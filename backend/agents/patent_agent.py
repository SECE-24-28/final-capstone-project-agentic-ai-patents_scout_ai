import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from backend.pipeline import AgentState, PatentCluster
from backend.services.patent_fetcher import fetch_patents
from backend.rag.embedder import store_documents
from backend.rag.retriever import retrieve
from backend.services.llm_client import generate_response

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PatentAgent")

def patent_agent(state: AgentState) -> AgentState:
    """
    Patent Agent Node:
    1. Reads domain from state["domain"]
    2. Fetches patents using fetch_patents(domain, limit=60)
    3. Stores all patents in ChromaDB using store_documents(documents=patents, domain=domain, collection_type="patent")
    4. Retrieves the most relevant patents using retrieve(query=domain, domain=domain, collection_type="patent", top_k=15)
    5. Formats retrieved patents into a context string (Patent ID, Title, Year, Assignee, Abstract)
    6. Loads the prompt template from backend/prompts/patent_agent.txt using pathlib.Path
    7. Formats the prompt with {domain} and {patents}
    8. Calls generate_response(prompt)
    9. Safely extracts and parses the JSON response
    10. Validates items using PatentCluster and updates state["patent_clusters"]
    """
    logger.info("Starting Patent Agent execution...")
    try:
        domain = state.get("domain")
        if not domain:
            raise ValueError("State must contain a non-empty 'domain' string.")
            
        logger.info(f"Target domain identified: '{domain}'")
        
        # 1. Fetch patents
        logger.info(f"Fetching patents for domain '{domain}'...")
        patents = fetch_patents(domain, limit=60)
        logger.info(f"[Patent Agent] Fetched {len(patents)} patents.")
        
        # 2. Store all patents in database
        logger.info(f"Vectorizing and indexing {len(patents)} patents...")
        store_documents(
            documents=patents,
            domain=domain,
            collection_type="patent"
        )
        logger.info(f"[Patent Agent] Stored {len(patents)} patents in vector database.")
        
        # 3. Retrieve top 15 relevant patents
        logger.info(f"Retrieving top 15 relevant patents for query: '{domain}'...")
        retrieved_docs = retrieve(
            query=domain,
            domain=domain,
            collection_type="patent",
            top_k=15
        )
        logger.info(f"[Patent Agent] Retrieved {len(retrieved_docs)} patents.")
        
        # 4. Format retrieved patents into a context string
        context_items = []
        for i, doc in enumerate(retrieved_docs):
            meta = doc.get("metadata", {})
            title = meta.get("title", "Unknown Title")
            year = meta.get("year") or "N/A"
            patent_id = doc.get("id", "Unknown Patent ID")
            abstract = doc.get("document", "").replace(f"Title: {title}\nAbstract: ", "")
            
            # Look up inventor names to use as assignee if possible
            assignee = "Unknown Assignee"
            for p in patents:
                if p.patent_id == patent_id:
                    if p.inventors:
                        assignee = ", ".join(p.inventors)
                    break
                    
            item_text = (
                f"Patent #{i+1}\n"
                f"Patent ID: {patent_id}\n"
                f"Title: {title}\n"
                f"Year: {year}\n"
                f"Assignee: {assignee}\n"
                f"Abstract: {abstract}\n"
                f"----------------------------------------"
            )
            context_items.append(item_text)
            
        patent_context = "\n".join(context_items)
        
        # 5. Load prompt template using pathlib.Path
        prompt_path = Path("backend") / "prompts" / "patent_agent.txt"
        if not prompt_path.exists():
            # Try workspace root resolution
            prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "patent_agent.txt"
            
        logger.info(f"Reading prompt template from: {prompt_path}")
        prompt_template = prompt_path.read_text(encoding="utf-8")
        
        # 6. Build final prompt
        final_prompt = prompt_template.replace("{domain}", domain).replace("{patents}", patent_context)
        
        # 7. Call model client
        logger.info("Executing Gemini model inference...")
        response_text = generate_response(final_prompt)
        
        # 8. Clean and parse JSON response array
        logger.info("Parsing model output JSON...")
        clean_json_str = response_text.strip()
        
        # Strip markdown code blocks if the model outputs them
        if clean_json_str.startswith("```json"):
            clean_json_str = clean_json_str[7:]
        if clean_json_str.startswith("```"):
            clean_json_str = clean_json_str[3:]
        if clean_json_str.endswith("```"):
            clean_json_str = clean_json_str[:-3]
        clean_json_str = clean_json_str.strip()
        
        if not clean_json_str:
            raw_clusters = []
        else:
            raw_clusters = json.loads(clean_json_str)
            
        if not isinstance(raw_clusters, list):
            raise TypeError(f"Expected model to return a JSON array list, got {type(raw_clusters)}")
            
        # 9. Validate JSON elements using Pydantic PatentCluster schema
        validated_clusters: List[Dict[str, Any]] = []
        for index, item in enumerate(raw_clusters):
            try:
                validated_item = PatentCluster(**item)
                validated_clusters.append(validated_item.model_dump())
            except Exception as item_err:
                logger.warning(f"Validation failed for patent cluster item at index {index}: {item_err}. Item was: {item}")
                
        logger.info(f"[Patent Agent] Validated {len(validated_clusters)} patent clusters.")
        
        # 10. Write back to shared state and return
        state["patent_clusters"] = validated_clusters
        state["error"] = None
        
    except Exception as e:
        logger.error(f"Patent Agent failed: {e}")
        state["error"] = str(e)
        if "patent_clusters" not in state:
            state["patent_clusters"] = []
            
    return state
