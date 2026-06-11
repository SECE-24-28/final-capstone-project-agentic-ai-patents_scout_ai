import unittest
from backend.services.research_fetcher import fetch_openalex_papers

class TestOpenAlexFetcher(unittest.TestCase):
    def test_fetch_openalex_papers_success(self):
        print("\n[Test] Running OpenAlex fetcher test for 'Biotechnology'...")
        papers = fetch_openalex_papers("Biotechnology", max_results=5)
        
        # Verify papers are returned
        self.assertIsNotNone(papers)
        self.assertTrue(len(papers) > 0, "No papers were returned from OpenAlex API.")
        
        # Verify max results limit is respected
        self.assertTrue(len(papers) <= 5)
        
        # Verify titles, abstracts, and URLs exist
        for i, paper in enumerate(papers):
            print(f"Paper #{i+1}:")
            print(f"  Title: {paper.title}")
            print(f"  Source: {paper.source}")
            print(f"  Year: {paper.year}")
            print(f"  URL: {paper.url}")
            print(f"  Abstract Length: {len(paper.abstract)} chars")
            
            self.assertTrue(bool(paper.title), "Paper title is missing or empty.")
            self.assertTrue(bool(paper.abstract), "Paper abstract was not reconstructed or is empty.")
            self.assertIsNotNone(paper.url, "Paper URL is missing.")

if __name__ == "__main__":
    unittest.main()
