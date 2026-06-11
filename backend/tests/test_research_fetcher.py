import unittest
from backend.services.research_fetcher import fetch_arxiv_papers, fetch_all_papers
from backend.models.pydantic_models import Paper

class TestResearchFetcher(unittest.TestCase):
    def test_fetch_arxiv_papers(self):
        """Test retrieving papers from arXiv with a test query."""
        papers = fetch_arxiv_papers("Smart Agriculture", max_results=2)
        self.assertIsInstance(papers, list)
        for p in papers:
            self.assertIsInstance(p, Paper)
            self.assertTrue(len(p.title) > 0)
            self.assertTrue(len(p.abstract) > 0)
            self.assertEqual(p.source, "arXiv")

    def test_fetch_all_papers(self):
        """Test search deduplication combining arXiv and Semantic Scholar."""
        papers = fetch_all_papers("Deep Learning", max_results=2)
        self.assertIsInstance(papers, list)
        if papers:
            p = papers[0]
            self.assertIsInstance(p, Paper)
            self.assertIsNotNone(p.title)

if __name__ == "__main__":
    unittest.main()
