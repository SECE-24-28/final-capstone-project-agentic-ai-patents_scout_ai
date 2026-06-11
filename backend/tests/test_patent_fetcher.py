import unittest
from backend.services.patent_fetcher import fetch_patents, get_mock_patents
from backend.models.pydantic_models import Patent

class TestPatentFetcher(unittest.TestCase):
    def test_fetch_patents(self):
        """Test retrieving patents with a standard query."""
        patents = fetch_patents("Smart Agriculture", max_results=3)
        self.assertIsInstance(patents, list)
        self.assertTrue(len(patents) > 0)
        for p in patents:
            self.assertIsInstance(p, Patent)
            self.assertTrue(len(p.title) > 0)
            self.assertTrue(len(p.patent_id) > 0)
            self.assertIsNotNone(p.abstract)

    def test_mock_patents_generation(self):
        """Test that get_mock_patents creates required count and valid fields."""
        patents = get_mock_patents("Quantum Computing", count=5)
        self.assertEqual(len(patents), 5)
        for p in patents:
            self.assertTrue("Quantum Computing" in p.title or "Quantum Computing" in p.abstract)
            self.assertTrue(p.patent_id.startswith("US"))

if __name__ == "__main__":
    unittest.main()
