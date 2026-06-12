import os
import json
import numpy as np
from typing import List, Dict, Any, Union
from sentence_transformers import SentenceTransformer
from backend.config import settings

# Initialize the embedding model globally
print("[Embedder] Loading SentenceTransformer model ('all-MiniLM-L6-v2')...")
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("[Embedder] Embedding model loaded successfully.")
except Exception as e:
    print(f"[Embedder] Warning: Failed to load sentence-transformers model: {e}")
    model = None

# Try importing and initializing ChromaDB
CHROMA_AVAILABLE = False
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    print("[Embedder] ChromaDB library not found. Falling back to Pure-Python Vector Database.")

class PurePythonVectorDB:
    """
    A lightweight, pure-Python vector database that stores document metadata and 
    pre-computed embeddings in a persistent JSON file. Computes cosine similarity via NumPy.
    """
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        self.store_path = os.path.join(persist_dir, "pure_python_store.json")
        self.data: Dict[str, List[Dict[str, Any]]] = {}
        self.load()

    def load(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"[PurePythonDB] Error loading vector store: {e}")
                self.data = {}
        else:
            self.data = {}

    def save(self):
        try:
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[PurePythonDB] Error saving vector store: {e}")

    def add_documents(self, collection_name: str, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]):
        if collection_name not in self.data:
            self.data[collection_name] = []
            
        # Remove existing documents with duplicate IDs
        existing_ids = set(ids)
        self.data[collection_name] = [item for item in self.data[collection_name] if item["id"] not in existing_ids]
        
        # Add new items
        for i in range(len(ids)):
            self.data[collection_name].append({
                "id": ids[i],
                "document": documents[i],
                "metadata": metadatas[i],
                "embedding": embeddings[i]
            })
        self.save()

    def query(self, collection_name: str, query_embedding: List[float], n_results: int = 5) -> Dict[str, Any]:
        if collection_name not in self.data or not self.data[collection_name]:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
            
        items = self.data[collection_name]
        q_vec = np.array(query_embedding)
        
        results = []
        for item in items:
            item_vec = np.array(item["embedding"])
            # Compute cosine distance: 1 - cosine_similarity
            dot_product = np.dot(q_vec, item_vec)
            norm_q = np.linalg.norm(q_vec)
            norm_item = np.linalg.norm(item_vec)
            
            if norm_q > 0 and norm_item > 0:
                cosine_sim = dot_product / (norm_q * norm_item)
            else:
                cosine_sim = 0.0
                
            distance = float(1.0 - cosine_sim)
            results.append((distance, item))
            
        # Sort by distance ascending (closer embeddings have lower distance)
        results.sort(key=lambda x: x[0])
        top_results = results[:n_results]
        
        return {
            "ids": [[res[1]["id"] for res in top_results]],
            "documents": [[res[1]["document"] for res in top_results]],
            "metadatas": [[res[1]["metadata"] for res in top_results]],
            "distances": [[res[0] for res in top_results]]
        }

# Global DB handlers
chroma_client = None
pure_db = None

if CHROMA_AVAILABLE:
    try:
        # Initialize Persistent ChromaDB Client
        chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
        print(f"[Embedder] Persistent ChromaDB initialized at: {settings.CHROMA_DB_DIR}")
    except Exception as e:
        print(f"[Embedder] ChromaDB client initialization failed: {e}. Falling back to Pure-Python DB.")
        CHROMA_AVAILABLE = False
        pure_db = PurePythonVectorDB(settings.CHROMA_DB_DIR)
else:
    pure_db = PurePythonVectorDB(settings.CHROMA_DB_DIR)

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate vector embeddings for a list of strings using SentenceTransformers.
    """
    if model is None:
        raise ValueError("SentenceTransformer model is not loaded.")
    embeddings = model.encode(texts)
    return [e.tolist() for e in embeddings]

def embed_and_store(collection_name: str, items_list: List[Union[Any, Dict[str, Any]]]):
    """
    Generates embeddings for research papers or patents and stores them in the selected database collection.
    Accepts lists of Paper/Patent pydantic models or dictionaries.
    """
    if not items_list:
        print(f"[Embedder] No items provided to embed and store in collection: '{collection_name}'")
        return
        
    ids = []
    documents = []
    metadatas = []
    
    # Process each item based on its type
    for i, item in enumerate(items_list):
        # Determine attributes
        if hasattr(item, "dict"): # Pydantic model
            item_dict = item.dict()
        elif isinstance(item, dict):
            item_dict = item
        else:
            continue
            
        # Extract ID (patent number, URL, or generated index)
        item_id = item_dict.get("patent_id") or item_dict.get("url") or f"{collection_name}_{i}"
        
        # Formulate Document content block to index
        title = item_dict.get("title", "")
        abstract = item_dict.get("abstract", "")
        document_text = f"Title: {title}\nAbstract: {abstract}"
        
        # Meta dictionary
        meta = {
            "title": title,
            "year": item_dict.get("year") or 0,
            "source": item_dict.get("source", "")
        }
        
        ids.append(str(item_id))
        documents.append(document_text)
        metadatas.append(meta)
        
    if not documents:
        print("[Embedder] No content found to embed.")
        return
        
    # Generate vectors
    embeddings = get_embeddings(documents)
    
    if CHROMA_AVAILABLE and chroma_client is not None:
        try:
            # Add to ChromaDB
            collection = chroma_client.get_or_create_collection(name=collection_name)
            collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            print(f"[Embedder] Successfully stored {len(ids)} vectors in ChromaDB collection: '{collection_name}'")
        except Exception as e:
            print(f"[Embedder] Error storing in ChromaDB: {e}. Attempting storage in Pure-Python DB...")
            # Fall back to pure Python DB for this write operation
            if pure_db is None:
                globals()['pure_db'] = PurePythonVectorDB(settings.CHROMA_DB_DIR)
            pure_db.add_documents(collection_name, ids, documents, metadatas, embeddings)
            print(f"[Embedder] Stored {len(ids)} vectors in Pure-Python fallback collection: '{collection_name}'")
    else:
        # Pure Python fallback DB
        pure_db.add_documents(collection_name, ids, documents, metadatas, embeddings)
        print(f"[Embedder] Stored {len(ids)} vectors in Pure-Python collection: '{collection_name}'")
