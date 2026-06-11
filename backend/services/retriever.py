from typing import List, Dict, Any
from backend.services.embedder import (
    CHROMA_AVAILABLE, chroma_client, pure_db, get_embeddings
)

def retrieve(query: str, collection_name: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve top-k documents matching the query from the specified collection.
    Automatically routes to ChromaDB or Pure-Python fallback vector search.
    Returns:
        List of dicts, each with:
            - id: Unique ID of the record
            - document: Text content of the document
            - metadata: Associated metadata dictionary
            - score: Vector similarity score (1 - cosine distance)
    """
    print(f"[Retriever] Searching for: '{query}' in collection: '{collection_name}'...")
    
    # 1. Generate query embedding
    try:
        query_vectors = get_embeddings([query])
        query_vector = query_vectors[0]
    except Exception as e:
        print(f"[Retriever] Error generating query embedding: {e}")
        return []
        
    results = []
    
    # 2. Query appropriate database engine
    if CHROMA_AVAILABLE and chroma_client is not None:
        try:
            collection = chroma_client.get_collection(name=collection_name)
            response = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k
            )
            
            # Format ChromaDB response
            ids = response.get("ids", [[]])[0]
            documents = response.get("documents", [[]])[0]
            metadatas = response.get("metadatas", [[]])[0]
            distances = response.get("distances", [[]])[0]
            
            for i in range(len(ids)):
                # Convert distance (L2 or Cosine distance) to a normalized similarity score
                # For cosine distance, distance = 1 - cosine_sim, so sim = 1 - distance
                dist = distances[i] if i < len(distances) else 0.0
                score = round(max(0.0, 1.0 - dist), 4)
                
                results.append({
                    "id": ids[i],
                    "document": documents[i],
                    "metadata": metadatas[i] or {},
                    "score": score
                })
        except Exception as e:
            print(f"[Retriever] ChromaDB query error: {e}. Falling back to Pure-Python search.")
            # Route query fallback to pure db
            results = _query_pure_db(collection_name, query_vector, top_k)
    else:
        # Route query directly to pure db fallback
        results = _query_pure_db(collection_name, query_vector, top_k)
        
    print(f"[Retriever] Found {len(results)} matches.")
    return results

def _query_pure_db(collection_name: str, query_vector: List[float], top_k: int) -> List[Dict[str, Any]]:
    """Helper method to execute query in the pure-python numpy vector store."""
    if pure_db is None:
        print("[Retriever] Pure-Python fallback store is not initialized.")
        return []
        
    response = pure_db.query(collection_name, query_vector, n_results=top_k)
    
    ids = response.get("ids", [[]])[0]
    documents = response.get("documents", [[]])[0]
    metadatas = response.get("metadatas", [[]])[0]
    distances = response.get("distances", [[]])[0]
    
    results = []
    for i in range(len(ids)):
        dist = distances[i]
        score = round(max(0.0, 1.0 - dist), 4)
        results.append({
            "id": ids[i],
            "document": documents[i],
            "metadata": metadatas[i],
            "score": score
        })
    return results
