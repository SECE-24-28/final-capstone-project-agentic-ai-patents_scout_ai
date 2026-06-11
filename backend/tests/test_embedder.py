import unittest
from backend.services.embedder import get_embeddings, embed_and_store, CHROMA_AVAILABLE
from backend.models.pydantic_models import Paper

class TestEmbedder(unittest.TestCase):
    def test_get_embeddings(self):
        """Test that get_embeddings returns a list of float arrays with dimension 384 (Minilm-L6-v2 dimension)."""
        texts = ["Artificial Intelligence in farming", "Drones for automated crop inspection"]
        vectors = get_embeddings(texts)
        
        self.assertEqual(len(vectors), 2)
        self.assertEqual(len(vectors[0]), 384)
        self.assertIsInstance(vectors[0][0], float)

    def test_embed_and_store(self):
        """Test creating and saving embeddings for paper models."""
        test_papers = [
            Paper(
                title="AI Irrigation Control",
                abstract="A deep reinforcement learning framework for precision water scheduling.",
                authors=["Alice Cooper"],
                year=2024,
                source="arXiv",
                url="http://arxiv.org/example"
            )
        ]
        
        # This will write to either ChromaDB or Pure-Python DB depending on compiler context
        # It should run without raising errors
        try:
            embed_and_store("test_research_collection", test_papers)
            success = True
        except Exception as e:
            print(f"Failed to embed and store: {e}")
            success = False
            
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()
