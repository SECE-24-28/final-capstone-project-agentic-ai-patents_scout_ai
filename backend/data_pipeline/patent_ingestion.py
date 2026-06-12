import os
import sys
import pandas as pd
import logging

# Set up module path for backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.embedder import (
    CHROMA_AVAILABLE,
    chroma_client,
    pure_db,
    get_embeddings
)

# Set up logging
logger = logging.getLogger("PatentIngestion")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def ingest_raw_patents(csv_path: str = "data/raw_patents/raw_patents.csv") -> bool:
    """
    Loads raw_patents.csv, creates embeddings using the SentenceTransformer model,
    and stores all patents in ChromaDB (or PurePython DB) under collection 'patent_global'.
    """
    logger.info(f"Starting patent ingestion from: {csv_path}")
    
    if not os.path.exists(csv_path):
        logger.error(f"Raw patents CSV file not found at: {csv_path}")
        return False

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        logger.error(f"Failed to read CSV file: {e}")
        return False

    total_records = len(df)
    logger.info(f"Loaded {total_records} patents from CSV. Commencing ingestion...")

    # Drop any rows missing core elements
    df = df.dropna(subset=["patent_number", "title", "abstract"])
    df["assignee"] = df["assignee"].fillna("Unknown Assignee")
    df["year"] = df["year"].fillna(0).astype(int)
    
    records = df.to_dict(orient="records")
    
    collection_name = "patent_global"
    batch_size = 500
    
    # Process and store in batches
    for start_idx in range(0, len(records), batch_size):
        end_idx = min(start_idx + batch_size, len(records))
        batch = records[start_idx:end_idx]
        
        logger.info(f"Processing batch {start_idx // batch_size + 1}: records {start_idx} to {end_idx}...")
        
        ids = []
        documents = []
        metadatas = []
        
        for record in batch:
            patent_number = str(record["patent_number"]).strip()
            title = str(record["title"]).strip()
            abstract = str(record["abstract"]).strip()
            assignee = str(record["assignee"]).strip()
            year = int(record["year"])
            domain = str(record["domain"]).strip()
            
            # Formulate text: Title + Abstract
            doc_text = f"Title: {title}\nAbstract: {abstract}"
            
            # Construct metadata dict
            meta = {
                "patent_number": patent_number,
                "assignee": assignee,
                "year": year,
                "domain": domain,
                "title": title
            }
            
            ids.append(patent_number)
            documents.append(doc_text)
            metadatas.append(meta)
            
        try:
            # Generate embeddings for batch
            embeddings = get_embeddings(documents)
        except Exception as e:
            logger.error(f"Failed to generate embeddings for batch starting at {start_idx}: {e}")
            return False
            
        # Store in ChromaDB or fallback Pure-Python vector store
        if CHROMA_AVAILABLE and chroma_client is not None:
            try:
                collection = chroma_client.get_or_create_collection(name=collection_name)
                collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
            except Exception as e:
                logger.error(f"ChromaDB batch storage failed: {e}. Falling back to Pure-Python DB.")
                if pure_db is not None:
                    pure_db.add_documents(collection_name, ids, documents, metadatas, embeddings)
                else:
                    logger.error("Pure-Python fallback database is not initialized.")
                    return False
        else:
            if pure_db is not None:
                pure_db.add_documents(collection_name, ids, documents, metadatas, embeddings)
            else:
                logger.error("Vector database backend is unavailable.")
                return False

    logger.info(f"Ingestion completed! Successfully stored {total_records} patents in '{collection_name}' collection.")
    return True

if __name__ == "__main__":
    success = ingest_raw_patents()
    sys.exit(0 if success else 1)
