import unittest
from unittest.mock import patch, MagicMock
from backend.services.patent_fetcher import fetch_patents
from backend.models.pydantic_models import Patent

class TestPatentFetcher(unittest.TestCase):
    @patch('backend.services.patent_fetcher.requests.get')
    @patch('backend.services.patent_fetcher.os.getenv')
    def test_fetch_patents_uspto_success(self, mock_getenv, mock_get):
        """Test successful retrieval from USPTO Open Data Portal."""
        mock_getenv.side_effect = lambda key: "uspto_mock_key" if "USPTO" in key or "PATENT" in key else None
        
        # Mock response from USPTO
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "patentApplicationSearchResults": [
                {
                    "applicationNumberText": "US20240123456A1",
                    "applicationMetaData": {
                        "inventionTitle": "Autonomous IoT Node for Smart Cities",
                        "abstractText": "A description of smart city sensor node structures.",
                        "filingDate": "2024-03-15",
                        "firstApplicantName": "Tesla Inc",
                        "patentNumber": "US11998877B2"
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        # Execute
        patents = fetch_patents("Smart Cities", limit=5)

        # Verification
        self.assertIsInstance(patents, list)
        self.assertEqual(len(patents), 1)
        
        p = patents[0]
        self.assertIsInstance(p, Patent)
        self.assertEqual(p.title, "Autonomous IoT Node for Smart Cities")
        self.assertEqual(p.abstract, "A description of smart city sensor node structures.")
        self.assertEqual(p.year, 2024)
        self.assertEqual(p.source, "USPTO")
        
        # Test custom dynamic attributes required by testing/compatibility requirements
        self.assertEqual(p.assignee, "Tesla Inc")
        self.assertEqual(p.patent_number, "US11998877B2")
        self.assertEqual(p.patent_id, "US11998877B2")

        # Verify USPTO was called and Lens was not
        mock_get.assert_called_once()

    @patch('backend.services.patent_fetcher.requests.post')
    @patch('backend.services.patent_fetcher.requests.get')
    @patch('backend.services.patent_fetcher.os.getenv')
    def test_fetch_patents_uspto_fails_lens_succeeds(self, mock_getenv, mock_get, mock_post):
        """Test fallback to Lens.org when USPTO retrieval fails."""
        mock_getenv.side_effect = lambda key: "lens_mock_key" if "LENS" in key else "uspto_mock_key"
        
        # USPTO fails (returns 500 error)
        mock_uspto_response = MagicMock()
        mock_uspto_response.status_code = 500
        mock_uspto_response.text = "Internal Server Error"
        mock_get.return_value = mock_uspto_response

        # Lens.org succeeds
        mock_lens_response = MagicMock()
        mock_lens_response.status_code = 200
        mock_lens_response.json.return_value = {
            "data": [
                {
                    "lens_id": "000-000-000-000-001",
                    "doc_number": "US11223344B1",
                    "date_published": "2023-10-12",
                    "biblio": {
                        "invention_title": [
                            {"text": "Smart Cities Dynamic Routing System", "lang": "en"}
                        ],
                        "publication_year": 2023,
                        "parties": {
                            "applicants": [
                                {"name": "Google LLC"}
                            ]
                        }
                    },
                    "abstract": [
                        {"text": "An abstract detailing dynamic routing algorithms.", "lang": "en"}
                    ]
                }
            ]
        }
        mock_post.return_value = mock_lens_response

        # Execute
        patents = fetch_patents("Smart Cities", limit=5)

        # Verification
        self.assertEqual(len(patents), 1)
        p = patents[0]
        self.assertEqual(p.title, "Smart Cities Dynamic Routing System")
        self.assertEqual(p.abstract, "An abstract detailing dynamic routing algorithms.")
        self.assertEqual(p.year, 2023)
        self.assertEqual(p.source, "Lens.org")
        self.assertEqual(p.assignee, "Google LLC")
        self.assertEqual(p.patent_number, "US11223344B1")
        self.assertEqual(p.patent_id, "US11223344B1")

        # Verify both endpoints were called in priority order
        mock_get.assert_called_once()
        mock_post.assert_called_once()

    @patch('backend.services.patent_fetcher.requests.post')
    @patch('backend.services.patent_fetcher.requests.get')
    @patch('backend.services.patent_fetcher.os.getenv')
    def test_fetch_patents_all_fail_raises_runtime_error(self, mock_getenv, mock_get, mock_post):
        """Test that failure on both sources raises a RuntimeError and does not generate mock data."""
        mock_getenv.return_value = "dummy_key"
        
        # Both APIs return error status codes
        mock_get.return_value.status_code = 500
        mock_post.return_value.status_code = 500

        with self.assertRaises(RuntimeError):
            fetch_patents("Smart Cities", limit=5)

if __name__ == "__main__":
    unittest.main()
