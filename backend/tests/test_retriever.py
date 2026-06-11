import unittest
from backend.services.embedder import embed_and_store
from backend.services.retriever import retrieve
from backend.models.pydantic_models import Paper

class TestRetriever(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Seed a test collection with unique keywords
        cls.collection_name = "test_retrieval_collection"
        cls.items = [
            Paper(
                title="Hydroponics nutrient monitoring system",
                abstract="Specifies a low-cost IoT device for tracking liquid nutrients in tomato greenhouse agriculture.",
                authors=["Scientist A"],
                year=2023,
                source="arXiv",
                url="http://arxiv.org/hydroponics"
            ),
            Paper(
                title="Deep learning for computer vision in medical imaging",
                abstract="Discusses convolutional neural networks for tumor detection in MRI brain scans.",
                authors=["Scientist B"],
                year=2022,
                source="Semantic Scholar",
                url="http://semantic/medical"
            )
        ]
        embed_and_store(cls.collection_name, cls.items)

    def test_retrieve_agriculture_query(self):
        """Test retrieving relevant tomato/agriculture documents, matching hydroponics paper."""
        results = retrieve("tomato hydroponics IoT sensor", self.collection_name, top_k=1)
        self.assertEqual(len(results), 1)
        
        top_match = results[0]
        self.assertEqual(top_match["metadata"]["title"], "Hydroponics nutrient monitoring system")
        self.assertTrue(top_match["score"] > 0.0)
        self.assertIn("document", top_match)
        self.assertIn("id", top_match)

    def test_retrieve_medical_query(self):
        """Test retrieving relevant medical documents, matching the medical imaging paper."""
        results = retrieve("mri brain scan tumors cnn", self.collection_name, top_k=1)
        self.assertEqual(len(results), 1)
        
        top_match = results[0]
        self.assertEqual(top_match["metadata"]["title"], "Deep learning for computer vision in medical imaging")

if __name__ == "__main__":
    unittest.main()
