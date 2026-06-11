from typing import List, Dict, Any
from backend.services.retriever import retrieve as service_retrieve

def retrieve(query: str, domain: str, collection_type: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve documents matching query from collection: research_{domain_slug} or patents_{domain_slug}
    """
    domain_slug = domain.lower().strip().replace(" ", "_")
    
    if collection_type == "research":
        collection_name = f"research_{domain_slug}"
    else:
        collection_name = f"patents_{domain_slug}"
        
    return service_retrieve(query, collection_name, top_k)
