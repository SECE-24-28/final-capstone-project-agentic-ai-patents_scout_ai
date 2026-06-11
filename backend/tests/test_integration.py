import unittest
from backend.services.research_fetcher import fetch_all_papers
from backend.services.patent_fetcher import fetch_patents
from backend.services.embedder import embed_and_store
from backend.services.retriever import retrieve

class TestFoundationIntegration(unittest.TestCase):
    def test_smart_agriculture_pipeline(self):
        """
        Runs the full foundational data lifecycle:
        1. Fetch papers for 'Smart Agriculture'
        2. Fetch patents for 'Smart Agriculture'
        3. Vectorize and store both in collections
        4. Query and retrieve items from both collections
        """
        domain = "Smart Agriculture"
        print(f"\n--- Starting Foundation Integration Test for domain: '{domain}' ---")
        
        # 1. Ingest papers
        papers = fetch_all_papers(domain, max_results=3)
        self.assertIsInstance(papers, list)
        print(f"[Integration] Fetched {len(papers)} papers.")
        
        # 2. Ingest patents
        patents = fetch_patents(domain, max_results=3)
        self.assertIsInstance(patents, list)
        print(f"[Integration] Fetched {len(patents)} patents.")
        
        # 3. Embed & Store
        papers_collection = "integration_research"
        patents_collection = "integration_patents"
        
        print(f"[Integration] Embedding and storing papers in '{papers_collection}'...")
        embed_and_store(papers_collection, papers)
        
        print(f"[Integration] Embedding and storing patents in '{patents_collection}'...")
        embed_and_store(patents_collection, patents)
        
        # 4. Retrieve and verify
        print("[Integration] Running retrieval queries...")
        retrieved_papers = retrieve("sensor irrigation precision crop monitoring", papers_collection, top_k=2)
        self.assertTrue(len(retrieved_papers) > 0)
        print(f"[Integration] Retrieved papers count: {len(retrieved_papers)}")
        for item in retrieved_papers:
            self.assertIn("title", item["metadata"])
            self.assertIn("score", item)
            print(f"  - Paper Match: {item['metadata']['title']} (Score: {item['score']})")
            
        retrieved_patents = retrieve("automated farming tracking control system", patents_collection, top_k=2)
        self.assertTrue(len(retrieved_patents) > 0)
        print(f"[Integration] Retrieved patents count: {len(retrieved_patents)}")
        for item in retrieved_patents:
            self.assertIn("title", item["metadata"])
            self.assertIn("score", item)
            print(f"  - Patent Match: {item['metadata']['title']} (Score: {item['score']})")
            
        print("--- Foundation Integration Test Passed! ---\n")

if __name__ == "__main__":
    unittest.main()
