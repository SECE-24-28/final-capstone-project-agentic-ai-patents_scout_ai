import unittest
from backend.agents.patent_agent import patent_agent
from backend.pipeline import AgentState

class TestPatentAgentLive(unittest.TestCase):
    def test_patent_agent_live_execution(self):
        """
        Live integration test for Patent Agent:
        1. Queries Google Patents for 'Smart Cities'.
        2. Filters out non-English patents.
        3. Indexes patents into ChromaDB.
        4. Performs similarity retrieval.
        5. Queries Gemini to cluster patents.
        6. Validates clusters against PatentCluster.
        """
        # Setup initial state
        state: AgentState = {
            "domain": "Smart Cities",
            "research_topics": [],
            "patent_clusters": [],
            "gap_matrix": [],
            "innovation_ideas": [],
            "patentability_scores": [],
            "report_markdown": "",
            "top_recommendation": {},
            "error": None
        }

        # Execute the agent
        print("\nExecuting live Patent Agent execution for 'Smart Cities'...")
        final_state = patent_agent(state)

        # Verify results
        self.assertIsNone(final_state.get("error"), f"Patent Agent execution failed: {final_state.get('error')}")
        
        clusters = final_state.get("patent_clusters", [])
        self.assertIsInstance(clusters, list)
        self.assertTrue(len(clusters) > 0, "No patent clusters were populated in the final state.")

        print(f"\n[SUCCESS] Live Test Succeeded. Identified {len(clusters)} validated patent clusters:")
        for i, cluster in enumerate(clusters):
            self.assertIn("category", cluster)
            self.assertIn("description", cluster)
            self.assertIn("saturation", cluster)
            self.assertIn("major_assignees", cluster)
            
            print(f"  Cluster #{i+1}:")
            print(f"    - Category: {cluster['category']}")
            print(f"    - Saturation: {cluster['saturation']}")
            print(f"    - Assignees: {', '.join(cluster['major_assignees'])}")

if __name__ == "__main__":
    unittest.main()
