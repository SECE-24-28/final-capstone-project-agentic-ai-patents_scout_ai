from typing import List, Any
from backend.services.embedder import embed_and_store

def store_documents(documents: List[Any], domain: str, collection_type: str) -> None:
    """
    Store documents in the database using the domain and collection type.
    Creates collections named: research_{domain_slug} or patents_{domain_slug}
    """
    domain_slug = domain.lower().strip().replace(" ", "_")
    
    # Map 'research' to 'research_{domain}' and other types to 'patents_{domain}' (or patents)
    if collection_type == "research":
        collection_name = f"research_{domain_slug}"
    else:
        collection_name = f"patents_{domain_slug}"
        
    embed_and_store(collection_name, documents)
