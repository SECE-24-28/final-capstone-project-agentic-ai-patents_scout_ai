import unittest
from unittest.mock import patch, MagicMock
from backend.agents.patent_agent import patent_agent
from backend.pipeline import AgentState
from backend.models.pydantic_models import Patent

class TestPatentAgent(unittest.TestCase):
    @patch('backend.agents.patent_agent.fetch_patents')
    @patch('backend.agents.patent_agent.store_documents')
    @patch('backend.agents.patent_agent.retrieve')
    @patch('backend.agents.patent_agent.generate_response')
    def test_patent_agent_success(self, mock_generate, mock_retrieve, mock_store, mock_fetch):
        # 1. Setup mock returns
        mock_fetch.return_value = [
            Patent(
                title="Mock Patent", 
                abstract="An abstract about battery fast charging.", 
                inventors=["Inventor A"], 
                year=2024, 
                patent_id="US1234567B2", 
                source="PatentsView"
            )
        ]
        
        # mock retrieve returns formatted search documents
        mock_retrieve.return_value = [
            {
                "id": "US1234567B2",
                "document": "Title: Mock Patent\nAbstract: An abstract about battery fast charging.",
                "metadata": {"title": "Mock Patent", "year": 2024, "source": "PatentsView"},
                "score": 0.95
            }
        ]
        
        # mock generate_response returns the expected JSON structure
        mock_generate.return_value = """
        [
            {
                "category": "Battery Management Systems",
                "description": "Monitoring and control of EV batteries",
                "saturation": "High",
                "major_assignees": ["Tesla", "LG Energy Solution"]
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
        
        updated_state = patent_agent(state)
        
        # 3. Assertions
        self.assertIsNone(updated_state["error"])
        self.assertEqual(len(updated_state["patent_clusters"]), 1)
        
        first_cluster = updated_state["patent_clusters"][0]
        self.assertEqual(first_cluster["category"], "Battery Management Systems")
        self.assertEqual(first_cluster["saturation"], "High")
        self.assertEqual(first_cluster["major_assignees"], ["Tesla", "LG Energy Solution"])
        
        # Verify that sub-functions were called
        mock_fetch.assert_called_once_with("Electric Vehicles", limit=60)
        mock_store.assert_called_once()
        mock_retrieve.assert_called_once()
        mock_generate.assert_called_once()

if __name__ == "__main__":
    unittest.main()
