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
from backend.services.retriever import (
    retrieve as service_retrieve
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
    Patent Agent Node (Production):
    1. Reads domain from state["domain"].
    2. Fetches patents from the local knowledge base.
    3. Retrieves top 15 relevant patents from local ChromaDB.
    4. Formulates a prompt using patent_agent.txt.
    5. Invokes Gemini to classify and cluster patents.
    6. Validates clusters against PatentCluster schema.
    7. Stores clusters in state["patent_clusters"].
    """
    logger.info("Executing Patent Agent...")
    
    if "patent_clusters" not in state:
        state["patent_clusters"] = []

    try:
        # 1. Read domain
        domain = state["domain"]
        if not domain or not isinstance(domain, str):
            raise ValueError("Domain must be a non-empty string in AgentState.")
        
        logger.info(f"Target domain: {domain}")

        # 2. Fetch patents from local database (acts as validation/check)
        logger.info(f"Fetching local patents for domain: {domain}")
        patents = fetch_patents(domain, limit=60)
        logger.info(f"Fetched {len(patents)} local patents.")

        # 3. Retrieve the top 15 most relevant patents from the patent_global collection
        logger.info("Retrieving top 15 relevant patents from 'patent_global'...")
        retrieved_docs = service_retrieve(
            query=domain,
            collection_name="patent_global",
            top_k=15
        )
        logger.info(f"Retrieved {len(retrieved_docs)} relevant patents.")

        # 4. Format retrieved patents into a context string
        context_items = []
        for i, doc in enumerate(retrieved_docs):
            meta = doc.get("metadata", {})
            title = meta.get("title", "Unknown Title")
            year = meta.get("year") or "N/A"
            assignee = meta.get("assignee", "Unknown Assignee")
            
            doc_str = doc.get("document", "")
            if "Abstract: " in doc_str:
                abstract = doc_str.split("Abstract: ", 1)[1].strip()
            else:
                abstract = doc_str.strip()

            item_text = (
                f"Patent #{i+1}\n"
                f"Title: {title}\n"
                f"Year: {year}\n"
                f"Assignee: {assignee}\n"
                f"Abstract: {abstract}"
            )
            context_items.append(item_text)

        patent_context = "\n\n".join(context_items)

        # 5. Load prompt template
        prompt_path = Path("backend/prompts/patent_agent.txt")
        if not prompt_path.exists():
            prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "patent_agent.txt"
            
        logger.info(f"Loading prompt template from: {prompt_path}")
        prompt_template = prompt_path.read_text(encoding="utf-8")

        # 6. Build final prompt
        prompt = prompt_template.replace("{domain}", domain).replace("{patents}", patent_context)

        # 7. Generate response from Gemini
        logger.info("Generating response from LLM client...")
        response = generate_response(prompt)

        # 8. Clean and parse JSON safely
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
                logger.error(f"Failed to parse JSON response: {json_err}")
                raw_clusters = []

        if not isinstance(raw_clusters, list):
            logger.warning(f"Expected list of clusters, but got: {type(raw_clusters)}")
            raw_clusters = []

        # 9. Validate entries using PatentCluster Pydantic schema
        validated_clusters: List[Dict[str, Any]] = []
        for item in raw_clusters:
            try:
                cluster = PatentCluster(**item)
                validated_clusters.append(cluster.model_dump())
            except Exception as val_err:
                logger.warning(f"Skipping malformed patent cluster entry: {val_err}. Entry: {item}")

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
