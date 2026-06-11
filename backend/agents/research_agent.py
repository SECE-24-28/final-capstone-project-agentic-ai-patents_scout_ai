import os
import json
import logging
from typing import List, Dict, Any

from backend.pipeline import AgentState, ResearchTopic
from backend.rag.research_fetcher import (
    fetch_papers
)
from backend.rag.embedder import store_documents
from backend.rag.retriever import retrieve
from backend.services.llm_client import generate_response

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ResearchAgent")

def research_agent(state: AgentState) -> AgentState:
    """
    Research Agent Node:
    1. Fetches academic papers from arXiv and Semantic Scholar.
    2. Embeds and indexes them into the vector database.
    3. Retrieves top matches to formulate the landscape context.
    4. Sends queries to Gemini 2.5 Flash via llm_client to extract research topics.
    5. Validates and stores output topics in the global state object.
    """
    logger.info("Starting Research Agent execution...")
    try:
        domain = state.get("domain")
        if not domain:
            raise ValueError("State must contain a non-empty 'domain' string.")
            
        logger.info(f"Target domain identified: '{domain}'")
        
        # 1. Fetch papers from all research sources (Semantic Scholar, arXiv, OpenAlex)
        logger.info(f"Fetching research papers for domain '{domain}'...")
        all_papers = fetch_papers(domain, 50)
        logger.info(f"Total unique papers retrieved: {len(all_papers)}")
        
        # 3. Store papers in vector database (ChromaDB or local fallback)
        logger.info(f"Vectorizing and indexing {len(all_papers)} papers into ChromaDB...")
        store_documents(
            documents=all_papers,
            domain=domain,
            collection_type="research"
        )
        
        # 4. Retrieve most relevant papers for prompt synthesis context
        logger.info(f"Retrieving top 15 relevant research documents for query: '{domain}'...")
        retrieved_docs = retrieve(
            query=domain,
            domain=domain,
            collection_type="research",
            top_k=15
        )
        
        # 5. Format retrieved documents into clean context text
        context_items = []
        for i, doc in enumerate(retrieved_docs):
            meta = doc.get("metadata", {})
            title = meta.get("title", "Unknown Title")
            year = meta.get("year") or "N/A"
            source = meta.get("source", "Unknown Source")
            abstract = doc.get("document", "").replace(f"Title: {title}\nAbstract: ", "")
            
            item_text = (
                f"Paper #{i+1}\n"
                f"Title: {title}\n"
                f"Year: {year}\n"
                f"Source: {source}\n"
                f"Abstract: {abstract}\n"
                f"----------------------------------------"
            )
            context_items.append(item_text)
            
        research_context = "\n".join(context_items)
        logger.info(f"Formatted research context size: {len(research_context)} characters.")
        
        # 6. Load prompt template from prompts directory
        prompt_path = os.path.join("backend", "prompts", "research_agent.txt")
        if not os.path.exists(prompt_path):
            # Try workspace root resolution
            prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "prompts", "research_agent.txt"))
            
        logger.info(f"Reading prompt template from: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
            
        # 7. Construct final prompt safely without curly brace formatting issues
        final_prompt = prompt_template.replace("{domain}", domain).replace("{abstracts}", research_context)
        
        # 8. Call model client to generate response
        logger.info("Executing Gemini model inference...")
        response_text = generate_response(final_prompt)
        
        # 9. Clean and parse JSON response array
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
        
        raw_topics = json.loads(clean_json_str)
        if not isinstance(raw_topics, list):
            raise TypeError(f"Expected model to return a JSON array list, got {type(raw_topics)}")
            
        # 10. Validate JSON elements using Pydantic ResearchTopic schema
        validated_topics: List[Dict[str, Any]] = []
        for index, item in enumerate(raw_topics):
            try:
                # Validate using ResearchTopic
                validated_item = ResearchTopic(**item)
                # Convert back to dict for shared TypedDict state storage
                validated_topics.append(validated_item.model_dump())
            except Exception as item_err:
                logger.warning(f"Validation failed for topic item at index {index}: {item_err}. Item was: {item}")
                
        logger.info(f"Successfully validated {len(validated_topics)} research topics.")
        
        # 11. Write back to shared state and return
        state["research_topics"] = validated_topics
        state["error"] = None
        
    except Exception as e:
        logger.error(f"Research Agent failed: {e}")
        state["error"] = str(e)
        if "research_topics" not in state:
            state["research_topics"] = []
            
    return state
