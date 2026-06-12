import sys
import json
from backend.agents.patent_agent import patent_agent
from backend.pipeline import AgentState

def run_live_verification():
    print("Initializing Patent Agent live verification run...")
    
    # 1. Ask user for domain input
    domain = input("Enter technology domain to analyze (default: Electric Vehicles): ").strip()
    if not domain:
        domain = "Electric Vehicles"
        
    state: AgentState = {
        "domain": domain,
        "research_topics": [],
        "patent_clusters": [],
        "gap_matrix": [],
        "innovation_ideas": [],
        "patentability_scores": [],
        "report_markdown": "",
        "top_recommendation": {},
        "error": None
    }
    
    # 2. Run agent
    print("Executing patent_agent(state)...")
    final_state = patent_agent(state)
    
    # 3. Check results
    if final_state.get("error"):
        print(f"\n[ERROR] Patent Agent Live Run Failed with error: {final_state['error']}")
        return False
        
    clusters = final_state.get("patent_clusters", [])
    print(f"\n[SUCCESS] Patent Agent Live Run Succeeded! Identified {len(clusters)} patent clusters:")
    print(json.dumps(clusters, indent=2))
    
    from backend.services.embedder import CHROMA_AVAILABLE, chroma_client, pure_db
    collection_name = "patent_global"
    
    total_found = 0
    domains = {}
    if CHROMA_AVAILABLE and chroma_client is not None:
        try:
            col = chroma_client.get_collection(name=collection_name)
            res = col.get()
            total_found = len(res.get("ids", []))
            for meta in res.get("metadatas", []):
                dom = meta.get("domain", "Unknown")
                domains[dom] = domains.get(dom, 0) + 1
        except Exception as e:
            print(f"Error querying ChromaDB collection: {e}")
    elif pure_db is not None:
        items = pure_db.data.get(collection_name, [])
        total_found = len(items)
        for item in items:
            dom = item.get("metadata", {}).get("domain", "Unknown")
            domains[dom] = domains.get(dom, 0) + 1
            
    print(f"[Verification] Ingested patent domain distribution in vector store '{collection_name}' (Total: {total_found}):")
    if domains:
        for dom, count in domains.items():
            print(f"  - {dom}: {count} patents")
    else:
        print("  No patents found in vector collection.")
        
    return True

if __name__ == "__main__":
    success = run_live_verification()
    sys.exit(0 if success else 1)
