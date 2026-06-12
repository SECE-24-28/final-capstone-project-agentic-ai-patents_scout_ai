import os
import sys
import unittest
from backend.agents.patent_agent import patent_agent
from backend.pipeline import AgentState

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.embedder import CHROMA_AVAILABLE, chroma_client, pure_db

class TestPatentAgentLive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Ensure that the local vector database has patents loaded."""
        print("\n" + "=" * 60)
        print("SETTING UP PATENT AGENT LIVE TEST ENVIRONMENT")
        print("=" * 60)
        
        # Check if collection 'patent_global' is already populated
        populated = False
        if CHROMA_AVAILABLE and chroma_client is not None:
            try:
                col = chroma_client.get_collection("patent_global")
                count = col.count()
                print(f"[SetUp] ChromaDB 'patent_global' has {count} documents.")
                if count > 0:
                    populated = True
            except Exception:
                print("[SetUp] ChromaDB collection 'patent_global' not found.")
        elif pure_db is not None:
            if "patent_global" in pure_db.data:
                count = len(pure_db.data["patent_global"])
                print(f"[SetUp] PurePythonDB 'patent_global' has {count} documents.")
                if count > 0:
                    populated = True
                    
        if not populated:
            print("[SetUp] 'patent_global' is empty. Ingesting a 300-record sample of raw patents for speed...")
            import pandas as pd
            from backend.data_pipeline.patent_ingestion import ingest_raw_patents
            
            csv_path = "data/raw_patents/raw_patents.csv"
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"Missing required raw patents CSV file at: {csv_path}")
                
            # Create a small temporary subset of 300 rows to speed up test execution
            temp_csv = "data/raw_patents/raw_patents_temp.csv"
            try:
                df = pd.read_csv(csv_path)
                df.head(300).to_csv(temp_csv, index=False, encoding="utf-8")
                success = ingest_raw_patents(temp_csv)
                if not success:
                    raise RuntimeError("Failed to ingest raw patents into database.")
            finally:
                if os.path.exists(temp_csv):
                    os.remove(temp_csv)
        else:
            print("[SetUp] Vector database is already populated. Skipping ingestion step.")
        print("=" * 60 + "\n")

    def test_patent_agent_live_execution(self):
        """
        Runs the Patent Agent with domain 'Artificial Intelligence':
        1. Retrieves patents from the local knowledge base.
        2. Retrieves top 15 matches from local ChromaDB.
        3. Formulates LLM context and triggers Gemini clustering.
        4. Validates output structure against PatentCluster schema.
        """
        print("\nExecuting live Patent Agent execution for 'Artificial Intelligence'...")
        
        # Setup initial state
        state: AgentState = {
            "domain": "Artificial Intelligence",
            "research_topics": [],
            "patent_clusters": [],
            "gap_matrix": [],
            "innovation_ideas": [],
            "patentability_scores": [],
            "report_markdown": "",
            "top_recommendation": {},
            "error": None
        }

        # Run the agent
        final_state = patent_agent(state)

        # Assertions
        self.assertIsNone(final_state.get("error"), f"Patent Agent execution failed: {final_state.get('error')}")
        
        clusters = final_state.get("patent_clusters", [])
        self.assertIsInstance(clusters, list)
        self.assertTrue(len(clusters) > 0, "No patent clusters were populated in the final state.")

        print(f"\n[SUCCESS] Live Test Succeeded. Identified {len(clusters)} validated patent clusters:")
        for i, cluster in enumerate(clusters):
            self.assertIn("category", cluster)
            self.assertIn("description", cluster)
            self.assertIn("saturation", cluster)
            self.assertIn("major_assignees", cluster)
            
            print(f"  Cluster #{i+1}:")
            print(f"    - Category: {cluster['category']}".encode('ascii', 'replace').decode('ascii'))
            print(f"    - Saturation: {cluster['saturation']}".encode('ascii', 'replace').decode('ascii'))
            print(f"    - Assignees: {', '.join(cluster['major_assignees'])}".encode('ascii', 'replace').decode('ascii'))

if __name__ == "__main__":
    unittest.main()
