import os
import json
import logging
from typing import List, Dict, Any

from backend.pipeline import AgentState, InnovationIdea
from backend.config import settings
from backend.rag.retriever import retrieve
from google import genai
from google.genai import types

# Configure structured logging
logger = logging.getLogger("InnovationAgent")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def innovation_agent(state: AgentState) -> AgentState:
    """
    Innovation Agent Node:
    1. Extracts 'domain', 'research_topics', 'patent_clusters', and 'gap_matrix' from the shared AgentState.
    2. If no gaps exist, returns state with an empty 'innovation_ideas' list.
    3. Selects only the top 3 gaps.
    4. Calls retrieve() to get supporting research papers for the domain.
    5. Formats upstream context: research topics, patent clusters, gap details, and research papers.
    6. Loads the prompt from backend/prompts/innovation_agent.txt.
    7. Configures google.genai client with settings.GOOGLE_API_KEY and invokes gemini-2.5-flash.
    8. Cleans, parses, and validates the output JSON array against the InnovationIdea model.
    9. Skips invalid entries, truncates to expected count, and writes valid ones to state['innovation_ideas'].
    10. Logs the number of generated ideas.
    11. Captures exceptions and writes error messages to state['error'] without crashing.
    """
    logger.info("Executing Innovation Agent...")
    
    if "innovation_ideas" not in state:
        state["innovation_ideas"] = []
        
    try:
        domain = state.get("domain", "")
        if not domain:
            raise ValueError("State must contain a non-empty 'domain' string.")
            
        gaps = state.get("gap_matrix", [])
        if not gaps:
            logger.warning("No gaps found in gap_matrix. Innovation ideas will be set to empty.")
            state["innovation_ideas"] = []
            state["error"] = None
            return state
            
        # Select only the top 3 gaps
        top_3_gaps = gaps[:3]
        expected_count = len(top_3_gaps)
        logger.info(f"Selected top {expected_count} gaps for innovation generation.")
        
        # Format research topics from upstream state
        raw_topics = state.get("research_topics", [])
        formatted_topics = []
        for t in raw_topics:
            if isinstance(t, dict):
                topic_name = t.get("topic") or t.get("name") or "Unknown Topic"
                desc = t.get("description") or ""
                desc_str = f" - {desc}" if desc else ""
                formatted_topics.append(f"* {topic_name}{desc_str}")
            elif isinstance(t, str):
                formatted_topics.append(f"* {t}")
        research_topics_context = "\n".join(formatted_topics) if formatted_topics else "No research topics available."
        
        # Format patent clusters from upstream state
        raw_clusters = state.get("patent_clusters", [])
        formatted_clusters = []
        for c in raw_clusters:
            if isinstance(c, dict):
                cat = c.get("category") or c.get("title") or c.get("name") or "Unknown Cluster"
                desc = c.get("description") or c.get("theme") or ""
                desc_str = f" - {desc}" if desc else ""
                formatted_clusters.append(f"* {cat}{desc_str}")
            elif isinstance(c, str):
                formatted_clusters.append(f"* {c}")
        patent_clusters_context = "\n".join(formatted_clusters) if formatted_clusters else "No patent clusters available."
        
        # Retrieve supporting research papers
        logger.info(f"Retrieving supporting research papers for domain '{domain}'...")
        retrieved_papers = retrieve(
            query=domain,
            domain=domain,
            collection_type="research",
            top_k=5
        )
        
        # Format research papers defensively
        formatted_papers = []
        for paper in retrieved_papers:
            title = (
                paper.get("title")
                or paper.get("metadata", {}).get("title")
                or "Unknown Title"
            )
            year = (
                paper.get("year")
                or paper.get("metadata", {}).get("year")
                or "N/A"
            )
            formatted_papers.append(f"* {title} ({year})")
        supporting_papers_context = "\n".join(formatted_papers) if formatted_papers else "No supporting papers found."
        
        # Format gap information
        formatted_gaps = []
        for index, gap in enumerate(top_3_gaps):
            area = gap.get("area", "Unknown Area")
            research_act = gap.get("research_activity", "Unknown")
            patent_act = gap.get("patent_activity", "Unknown")
            score = gap.get("opportunity_score", 0)
            rationale = gap.get("rationale", "No rationale provided.")
            
            gap_item = (
                f"Gap #{index+1}:\n"
                f"- Area: {area}\n"
                f"- Research Activity: {research_act}\n"
                f"- Patent Activity: {patent_act}\n"
                f"- Opportunity Score: {score}\n"
                f"- Rationale: {rationale}"
            )
            formatted_gaps.append(gap_item)
        gaps_context = "\n\n".join(formatted_gaps)
        
        # Read prompt template
        prompt_path = os.path.join("backend", "prompts", "innovation_agent.txt")
        if not os.path.exists(prompt_path):
            prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "prompts", "innovation_agent.txt"))
            
        logger.info(f"Loading prompt template from: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
            
        # Dynamically build allowed gap names list (Task 5)
        allowed_gap_list = []
        for index, gap in enumerate(top_3_gaps):
            area = gap.get("area", "Unknown Area")
            allowed_gap_list.append(f"{index+1}. {area}")
        allowed_gaps_str = "\n".join(allowed_gap_list)
        
        # Build extended prompt system context with upstream agent context and allowed gaps
        system_context = (
            f"Active Research Topics in this Domain:\n{research_topics_context}\n\n"
            f"Active Patent Clusters in this Domain:\n{patent_clusters_context}\n\n"
            f"Supporting Academic Literature:\n{supporting_papers_context}\n\n"
            f"Allowed gap names:\n{allowed_gaps_str}\n\n"
        )
        
        final_prompt = (
            f"{system_context}\n"
            f"{prompt_template.replace('{domain}', domain).replace('{gaps}', gaps_context)}"
        )
        
        # Invoke Gemini API using google-genai SDK (Task 1)
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not configured in environment variables or settings.")
            
        client = genai.Client(api_key=api_key)
        
        logger.info("Calling Gemini 2.5 Flash for innovation ideas...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=final_prompt,
        )
        response_text = response.text
        
        # Improve observability: log the raw response (Task 6)
        logger.info("Raw Gemini response:\n%s", response_text)
        
        # Parse JSON safely
        clean_json_str = response_text.strip()
        if clean_json_str.startswith("```json"):
            clean_json_str = clean_json_str[7:]
        elif clean_json_str.startswith("```"):
            clean_json_str = clean_json_str[3:]
        if clean_json_str.endswith("```"):
            clean_json_str = clean_json_str[:-3]
        clean_json_str = clean_json_str.strip()
        
        try:
            raw_ideas = json.loads(clean_json_str)
        except json.JSONDecodeError as json_err:
            logger.warning(f"Initial JSON parsing failed: {json_err}. Attempting fallback extraction...")
            # Attempt a single fallback extraction: find boundaries of first '[' and last ']'
            start_idx = clean_json_str.find("[")
            end_idx = clean_json_str.rfind("]")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                clean_json_str = clean_json_str[start_idx : end_idx + 1]
                try:
                    raw_ideas = json.loads(clean_json_str)
                except json.JSONDecodeError as retry_err:
                    raise ValueError(f"Invalid JSON returned by Gemini:\n{clean_json_str}") from retry_err
            else:
                raise ValueError(f"Invalid JSON returned by Gemini:\n{clean_json_str}") from json_err
                
        if not isinstance(raw_ideas, list):
            raise TypeError(f"Expected model response to parse as a JSON list, but got {type(raw_ideas)}")
            
        # Create validation set of areas
        valid_gap_names = {gap["area"] for gap in top_3_gaps}
        
        # Validate every generated idea using InnovationIdea
        validated_ideas: List[Dict[str, Any]] = []
        for index, item in enumerate(raw_ideas):
            try:
                # Map fields defensively from LLM JSON to InnovationIdea schema (No defaults/auto-fill)
                mapped_item = {
                    "name": item.get("name") or item.get("title"),
                    "description": item.get("description"),
                    "target_user": item.get("target_user") or item.get("target_market"),
                    "type": item.get("type"),
                    "based_on_gap": item.get("based_on_gap")
                }
                
                # Check based_on_gap validity (Task 7)
                bgap = mapped_item["based_on_gap"]
                if bgap not in valid_gap_names:
                    logger.warning(f"Skipping idea at index {index} because based_on_gap '{bgap}' is not in valid gaps: {valid_gap_names}")
                    continue
                    
                # Validate schema using InnovationIdea
                idea_model = InnovationIdea(**mapped_item)
                validated_ideas.append(idea_model.model_dump())
            except Exception as val_err:
                logger.warning(f"Skipping invalid innovation idea at index {index}: {val_err}. Item was: {item}")
                
        # Fix 2: Exact Idea Count Enforcement
        actual_count = len(validated_ideas)
        if actual_count > expected_count:
            logger.info(f"Truncating generated ideas count from {actual_count} to {expected_count}")
            validated_ideas = validated_ideas[:expected_count]
        elif actual_count < expected_count:
            logger.warning(
                "Expected %d ideas but validated %d",
                expected_count,
                actual_count
            )
            
        if not validated_ideas:
            raise ValueError("All generated ideas failed validation or mapping checks.")
            
        # Store valid entries
        state["innovation_ideas"] = validated_ideas
        state["error"] = None
        
        logger.info(f"[Innovation Agent] Generated {len(validated_ideas)} ideas")
        
    except Exception as e:
        logger.exception("An error occurred during Innovation Agent execution.")
        state["error"] = str(e)
        state["innovation_ideas"] = []
        
    return state
