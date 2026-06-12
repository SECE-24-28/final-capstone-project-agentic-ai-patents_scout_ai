import logging
from typing import List, Optional
from backend.models.pydantic_models import Patent
from backend.services.retriever import retrieve

logger = logging.getLogger("PatentFetcher")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def fetch_patents(domain: str, limit: int = 60, max_results: Optional[int] = None) -> List[Patent]:
    """
    Offline local patent fetcher:
    1. Searches the 'patent_global' local database collection for the given domain query.
    2. Maps matches back into normalized, structured Patent objects.
    
    Args:
        domain (str): The search query or domain.
        limit (int): Maximum number of patents to retrieve. Defaults to 60.
        max_results (Optional[int]): Deprecated parameter for backward compatibility.
        
    Returns:
        List[Patent]: List of normalized Patent objects.
    """
    actual_limit = limit if max_results is None else max_results
    logger.info(f"Retrieving patents locally from 'patent_global' for: '{domain}' (limit: {actual_limit})")
    
    # Query ChromaDB (or the Pure-Python fallback)
    try:
        results = retrieve(
            query=domain,
            collection_name="patent_global",
            top_k=actual_limit
        )
    except Exception as e:
        logger.error(f"Local patent query failed: {e}")
        return []
        
    normalized_patents: List[Patent] = []
    
    for item in results:
        meta = item.get("metadata", {})
        doc_str = item.get("document", "")
        
        # Parse abstract back from the formatted document text
        if "Abstract: " in doc_str:
            abstract = doc_str.split("Abstract: ", 1)[1].strip()
        else:
            abstract = doc_str.strip()
            
        title = meta.get("title", "").strip()
        assignee = meta.get("assignee", "Unknown Assignee").strip()
        year = meta.get("year")
        patent_id = meta.get("patent_number") or item.get("id")
        
        # Build normalized Patent object
        p = Patent(
            title=title,
            abstract=abstract,
            inventors=[assignee],
            year=int(year) if year is not None else None,
            patent_id=str(patent_id),
            source="local_google_patents"
        )
        
        # Add dynamic attributes for backward compatibility
        object.__setattr__(p, 'assignee', assignee)
        object.__setattr__(p, 'patent_number', str(patent_id))
        
        normalized_patents.append(p)
        
    logger.info(f"Successfully returned {len(normalized_patents)} local patents.")
    return normalized_patents
