import unittest
from unittest.mock import patch, MagicMock
from backend.services.patent_fetcher import fetch_patents, is_english
from backend.models.pydantic_models import Patent

class TestPatentFetcher(unittest.TestCase):
    def test_language_detection(self):
        """Test English-only detection logic (rejecting CJK and non-English)."""
        # English cases
        self.assertTrue(is_english("Dynamic routing in smart cities", "A system for traffic routing."))
        self.assertTrue(is_english("Autonomous Vehicles", ""))
        
        # CJK cases (Chinese character detection)
        self.assertFalse(is_english("Personal parking system based on IC card 聂刚", ""))
        self.assertFalse(is_english("Personal parking system", "安徽省新方尊铸造科技有限公司"))
        
        # Non-English text cases (detected by langdetect)
        self.assertFalse(is_english("Sistema de estacionamiento personal", "Un sistema para estacionar autos."))

    @patch('backend.services.patent_fetcher.requests.get')
    def test_fetch_patents_google_success(self, mock_get):
        """Test successful retrieval and normalization from Google Patents XHR."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": {
                "total_num_results": 100,
                "cluster": [
                    {
                        "result": [
                            {
                                "patent": {
                                    "title": "Smart City Routing System",
                                    "snippet": "A routing system designed for smart cities.",
                                    "publication_number": "US1234567A1",
                                    "assignee": "Google LLC",
                                    "publication_date": "2024-05-10"
                                }
                            },
                            {
                                "patent": {
                                    "title": "个人停车位系统 (Personal parking system)",
                                    "snippet": "An abstract containing Chinese characters 安徽省新方尊",
                                    "publication_number": "CN104504784A",
                                    "assignee": "Chinese Tech Inc",
                                    "publication_date": "2015-04-08"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        # Execute
        patents = fetch_patents("Smart Cities", limit=5)

        # Verification
        self.assertIsInstance(patents, list)
        self.assertEqual(len(patents), 1)  # Only 1 English patent remains after filtering out Chinese one
        
        p = patents[0]
        self.assertIsInstance(p, Patent)
        self.assertEqual(p.title, "Smart City Routing System")
        self.assertEqual(p.abstract, "A routing system designed for smart cities.")
        self.assertEqual(p.year, 2024)
        self.assertEqual(p.source, "google_patents")
        
        # Test dynamic attributes populated for compatibility
        self.assertEqual(p.assignee, "Google LLC")
        self.assertEqual(p.patent_number, "US1234567A1")
        self.assertEqual(p.patent_id, "US1234567A1")

if __name__ == "__main__":
    unittest.main()
