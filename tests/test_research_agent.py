import unittest
from unittest.mock import patch, MagicMock
from backend.agents.research_agent import research_agent
from backend.pipeline import AgentState
from backend.models.pydantic_models import Paper

class TestResearchAgent(unittest.TestCase):
    @patch('backend.agents.research_agent.fetch_papers')
    @patch('backend.agents.research_agent.store_documents')
    @patch('backend.agents.research_agent.retrieve')
    @patch('backend.agents.research_agent.generate_response')
    def test_research_agent_success(self, mock_generate, mock_retrieve, mock_store, mock_papers):
        # 1. Setup mock returns
        mock_papers.return_value = [
            Paper(title="Mock SS Paper", abstract="An abstract about EV battery aging.", authors=["Author A"], year=2024, source="Semantic Scholar", url="http://ss/1"),
            Paper(title="Mock arXiv Paper", abstract="Another abstract about battery cooling.", authors=["Author B"], year=2023, source="arXiv", url="http://arxiv/1")
        ]
        
        # mock retrieve returns formatted search documents
        mock_retrieve.return_value = [
            {
                "id": "http://ss/1",
                "document": "Title: Mock SS Paper\nAbstract: An abstract about EV battery aging.",
                "metadata": {"title": "Mock SS Paper", "year": 2024, "source": "Semantic Scholar"},
                "score": 0.95
            }
        ]
        
        # mock generate_response returns the expected JSON structure
        mock_generate.return_value = """
        [
            {
                "topic": "Battery Health Management",
                "description": "Predicting cell state of health using diagnostic telemetry.",
                "research_activity": "High",
                "citation_strength": 90
            },
            {
                "topic": "Thermal Optimization",
                "description": "Designing cooling circuits using high-efficiency fluid flows.",
                "research_activity": "Medium",
                "citation_strength": 75
            }
        ]
        """
        
        # 2. Execute node with initial state
        state: AgentState = {
            "domain": "Electric Vehicles",
            "research_topics": [],
            "patent_clusters": [],
            "gap_matrix": [],
            "innovation_ideas": [],
            "patentability_scores": [],
            "report_markdown": "",
            "top_recommendation": {},
            "error": None
        }
        
        updated_state = research_agent(state)
        
        # 3. Assertions
        self.assertIsNone(updated_state["error"])
        self.assertEqual(len(updated_state["research_topics"]), 2)
        
        first_topic = updated_state["research_topics"][0]
        self.assertEqual(first_topic["topic"], "Battery Health Management")
        self.assertEqual(first_topic["research_activity"], "High")
        self.assertEqual(first_topic["citation_strength"], 90)
        
        # Verify that sub-functions were called
        mock_papers.assert_called_once_with("Electric Vehicles", 50)
        mock_store.assert_called_once()
        mock_retrieve.assert_called_once()
        mock_generate.assert_called_once()

if __name__ == "__main__":
    unittest.main()
