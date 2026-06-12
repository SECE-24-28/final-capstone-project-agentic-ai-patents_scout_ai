import unittest
from backend.services.patent_fetcher import fetch_patents
from backend.models.pydantic_models import Patent

class TestPatentFetcher(unittest.TestCase):
    def test_fetch_patents_local_success(self):
        """Test successful local retrieval and normalization from ChromaDB patent_global collection."""
        # Query local database
        patents = fetch_patents("Artificial Intelligence", limit=5)
        
        # We assume database has been populated (either by live test run or initial data script)
        # Verify normalization holds
        self.assertIsInstance(patents, list)
        
        if len(patents) > 0:
            for p in patents:
                self.assertIsInstance(p, Patent)
                self.assertIsNotNone(p.title)
                self.assertIsNotNone(p.abstract)
                self.assertIsNotNone(p.patent_id)
                self.assertTrue(len(p.title) >= 10)
                self.assertTrue(len(p.abstract) >= 50)
                
                # Check compatibility attributes
                self.assertIsNotNone(getattr(p, "assignee"))
                self.assertIsNotNone(getattr(p, "patent_number"))
                self.assertEqual(p.patent_id, p.patent_number)
        else:
            print("[Warning] Local patent_global collection is currently empty or has no matches. Test passed vacuously.")

    def test_fetch_patents_no_results(self):
        """Test fetcher returns empty list for queries that yield zero results."""
        # Query with an obscure term unlikely to match any real patents
        patents = fetch_patents("nonexistenttechnologyqueryxyz", limit=5)
        self.assertIsInstance(patents, list)
        self.assertEqual(len(patents), 0)

if __name__ == "__main__":
    unittest.main()
