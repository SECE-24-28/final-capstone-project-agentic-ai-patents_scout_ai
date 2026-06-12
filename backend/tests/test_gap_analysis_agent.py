import os
import sys
import unittest

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.pipeline import AgentState
from backend.agents.gap_analysis_agent import gap_analysis_agent, GapEntry, GapMatrix

class TestGapAnalysisAgent(unittest.TestCase):
    def test_gap_analysis_agent_standalone(self):
        """
        Tests the Gap Analysis Agent node in isolation using mock input data.
        Verifies:
        1. Executing the agent updates the state with a validated gap_matrix list.
        2. Items in the list match the GapEntry schema.
        3. Results are sorted by opportunity_score in descending order.
        """
        print("\n" + "=" * 60)
        print("RUNNING STANDALONE GAP ANALYSIS AGENT UNIT TEST")
        print("=" * 60)

        # 1. Setup mock state
        state: AgentState = {
            "domain": "Renewable Energy",
            "research_topics": [
                {
                    "topic": "Solid-State Photovoltaic Interfaces",
                    "description": "Scholarly publications on solid electrolyte solar battery interfaces.",
                    "research_activity": "High",
                    "citation_strength": 94
                },
                {
                    "topic": "Microclimate Solar Prediction Models",
                    "description": "Deep learning weather forecasting at localized grid nodes.",
                    "research_activity": "Medium",
                    "citation_strength": 72
                }
            ],
            "patent_clusters": [
                {
                    "category": "Liquid Solar Cell Storage Packs",
                    "description": "Patents covering traditional liquid acid batteries for home solar grids.",
                    "saturation": "High",
                    "major_assignees": ["Tesla", "Panasonic", "BYD"]
                },
                {
                    "category": "High-Efficiency Solar Converters",
                    "description": "Standard silicon PV micro-inverters and safety cutouts.",
                    "saturation": "High",
                    "major_assignees": ["Enphase Energy", "SMA Solar", "Huawei"]
                }
            ],
            "gap_matrix": [],
            "innovation_ideas": [],
            "patentability_scores": [],
            "report_markdown": "",
            "top_recommendation": {},
            "error": None
        }

        # 2. Execute agent
        final_state = gap_analysis_agent(state)

        # 3. Assertions & Validation
        self.assertIsNone(final_state.get("error"), f"Agent failed with error: {final_state.get('error')}")
        
        gaps = final_state.get("gap_matrix", [])
        self.assertIsInstance(gaps, list)
        self.assertTrue(len(gaps) > 0, "No gaps were identified by the agent.")

        print(f"\n[Success] Found {len(gaps)} gap opportunities.")
        
        # Verify schema mapping and sort order
        last_score = 101
        for index, item in enumerate(gaps):
            # Verify pydantic schema validation
            entry = GapEntry(**item)
            self.assertIsInstance(entry.opportunity_score, int)
            self.assertTrue(0 <= entry.opportunity_score <= 100)
            self.assertIsNotNone(entry.area)
            self.assertIsNotNone(entry.rationale)
            
            # Verify sorting order (descending by opportunity score)
            self.assertTrue(entry.opportunity_score <= last_score, f"Sorting error at index {index}: {entry.opportunity_score} > {last_score}")
            last_score = entry.opportunity_score
            
            print(f"  Opportunity #{index+1}:")
            print(f"    - Area: {entry.area}")
            print(f"    - Research Activity: {entry.research_activity}")
            print(f"    - Patent Activity: {entry.patent_activity}")
            print(f"    - Opportunity Score: {entry.opportunity_score}")
            print(f"    - Rationale: {entry.rationale}")

        # Print metrics
        print("\n--- TEST METRICS SUMMARY ---")
        print(f"Gap Count: {len(gaps)}")
        print(f"Top Opportunity: {gaps[0]['area']}")
        print(f"Top Opportunity Score: {gaps[0]['opportunity_score']}")
        print("=" * 60 + "\n")

    def test_gap_analysis_agent_integration(self):
        """
        Runs the full integration flow:
        state = research_agent(state)
        state = patent_agent(state)
        state = gap_analysis_agent(state)
        
        Verifies all three data layers are generated successfully.
        """
        print("\n" + "=" * 60)
        print("RUNNING MULTI-AGENT GAP ANALYSIS INTEGRATION TEST")
        print("=" * 60)
        
        from backend.agents.research_agent import research_agent
        from backend.agents.patent_agent import patent_agent
        
        state: AgentState = {
            "domain": "Renewable Energy",
            "research_topics": [],
            "patent_clusters": [],
            "gap_matrix": [],
            "innovation_ideas": [],
            "patentability_scores": [],
            "report_markdown": "",
            "top_recommendation": {},
            "error": None
        }
        
        # 1. Run Research Agent
        print("Executing Research Agent...")
        state = research_agent(state)
        self.assertIsNone(state.get("error"), f"Research Agent failed: {state.get('error')}")
        self.assertTrue(len(state.get("research_topics", [])) > 0)
        
        # 2. Run Patent Agent
        print("Executing Patent Agent...")
        state = patent_agent(state)
        self.assertIsNone(state.get("error"), f"Patent Agent failed: {state.get('error')}")
        self.assertTrue(len(state.get("patent_clusters", [])) > 0)
        
        # 3. Run Gap Analysis Agent
        print("Executing Gap Analysis Agent...")
        state = gap_analysis_agent(state)
        self.assertIsNone(state.get("error"), f"Gap Analysis Agent failed: {state.get('error')}")
        
        gaps = state.get("gap_matrix", [])
        self.assertTrue(len(gaps) > 0, "No gaps were populated in the final integrated state.")
        
        print("\n[SUCCESS] Integrated Multi-Agent Run completed successfully!")
        print(f"  - Research Topics Found: {len(state['research_topics'])}")
        print(f"  - Patent Clusters Found: {len(state['patent_clusters'])}")
        print(f"  - Gap Analysis Opportunities Found: {len(gaps)}")
        print("=" * 60 + "\n")

if __name__ == "__main__":
    unittest.main()
