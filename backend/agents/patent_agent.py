import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from backend.pipeline import (
    AgentState,
    PatentCluster
)
from backend.services.patent_fetcher import (
    fetch_patents
)
from backend.rag.embedder import (
    store_documents
)
from backend.rag.retriever import (
    retrieve
)
from backend.services.llm_client import (
    generate_response
)

# Configure structured logging
logger = logging.getLogger("PatentAgent")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def patent_agent(state: AgentState) -> AgentState:
    """
    Patent Agent Node:
    Retrieves patents related to a technology domain, analyzes them,
    identifies major patent categories, estimates patent saturation levels,
    and stores the structured results in AgentState.

    Args:
        state (AgentState): The current state of the agent execution.

    Returns:
        AgentState: The updated state containing patent clusters or error information.
    """
    logger.info("Executing Patent Agent...")
    
    # Initialize patent_clusters in state if not already present
    if "patent_clusters" not in state:
        state["patent_clusters"] = []

    try:
        # 1. Read domain from state["domain"]
        domain = state["domain"]
        if not domain or not isinstance(domain, str):
            raise ValueError("Domain must be a non-empty string in AgentState.")
        
        logger.info(f"Target domain: {domain}")

        # 2. Fetch patents using fetch_patents(state["domain"], limit=60)
        logger.info(f"Fetching patents for domain: {domain}")
        patents = fetch_patents(state["domain"], limit=60)
        logger.info(f"Fetched {len(patents)} patents.")

        # 3. Store all patents in ChromaDB using store_documents
        logger.info(f"Storing {len(patents)} patents in ChromaDB...")
        store_documents(
            documents=patents,
            domain=state["domain"],
            collection_type="patent"
        )
        logger.info(f"Stored {len(patents)} patents.")

        # 4. Retrieve the most relevant patents using retrieve
        logger.info("Retrieving top 15 relevant patents...")
        retrieved_docs = retrieve(
            query=state["domain"],
            domain=state["domain"],
            collection_type="patent",
            top_k=15
        )
        logger.info(f"Retrieved {len(retrieved_docs)} patents.")

        # 5. Format retrieved patents into a readable context string
        context_items = []
        for i, doc in enumerate(retrieved_docs):
            meta = doc.get("metadata", {})
            title = meta.get("title", "Unknown Title")
            year = meta.get("year") or "N/A"
            patent_id = doc.get("id", "Unknown ID")
            abstract = doc.get("document", "").replace(f"Title: {title}\nAbstract: ", "")
            
            # Map assignee from patent list matching patent_id if possible
            assignee = "Unknown Assignee"
            for p in patents:
                if p.patent_id == patent_id:
                    if p.inventors:
                        assignee = ", ".join(p.inventors)
                    break

            item_text = (
                f"Patent #{i+1}\n"
                f"Title: {title}\n"
                f"Year: {year}\n"
                f"Assignee: {assignee}\n"
                f"Abstract: {abstract}"
            )
            context_items.append(item_text)

        patent_context = "\n\n".join(context_items)

        # 6. Load prompt template using pathlib.Path
        # Use robust relative path fallback
        prompt_path = Path("backend/prompts/patent_agent.txt")
        if not prompt_path.exists():
            prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "patent_agent.txt"
            
        logger.info(f"Loading prompt template from: {prompt_path}")
        prompt_template = prompt_path.read_text(encoding="utf-8")

        # 7. Build final prompt by injecting domain and patents
        prompt = prompt_template.replace("{domain}", domain).replace("{patents}", patent_context)

        # 8. Generate response using generate_response
        logger.info("Generating response from LLM client...")
        response = generate_response(prompt)

        # 9. Clean and parse JSON safely
        logger.info("Parsing JSON response...")
        clean_json_str = response.strip()
        
        # Strip markdown code blocks
        if clean_json_str.startswith("```json"):
            clean_json_str = clean_json_str[7:]
        elif clean_json_str.startswith("```"):
            clean_json_str = clean_json_str[3:]
        if clean_json_str.endswith("```"):
            clean_json_str = clean_json_str[:-3]
        clean_json_str = clean_json_str.strip()

        # Robust extraction: find first '[' and last ']'
        start_idx = clean_json_str.find("[")
        end_idx = clean_json_str.rfind("]")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            clean_json_str = clean_json_str[start_idx : end_idx + 1]

        if not clean_json_str:
            raw_clusters = []
        else:
            try:
                raw_clusters = json.loads(clean_json_str)
            except json.JSONDecodeError as json_err:
                logger.error(f"Failed to parse JSON response. Raw string: {clean_json_str}. Error: {json_err}")
                raw_clusters = []

        if not isinstance(raw_clusters, list):
            logger.warning(f"Expected list of clusters, but received: {type(raw_clusters)}")
            raw_clusters = []

        # 10. Validate every item using PatentCluster and continue on malformed items
        validated_clusters: List[Dict[str, Any]] = []
        for item in raw_clusters:
            try:
                # Validate item with PatentCluster Pydantic model
                cluster = PatentCluster(**item)
                validated_clusters.append(cluster.model_dump())
            except Exception as val_err:
                logger.warning(f"Skipping malformed patent cluster entry due to validation error: {val_err}. Entry: {item}")

        logger.info(f"Validated {len(validated_clusters)} patent clusters.")

        # Store validated results in state
        state["patent_clusters"] = validated_clusters
        state["error"] = None

    except Exception as e:
        logger.exception("An error occurred during patent agent execution.")
        state["error"] = str(e)
        if "patent_clusters" not in state:
            state["patent_clusters"] = []

    return state
