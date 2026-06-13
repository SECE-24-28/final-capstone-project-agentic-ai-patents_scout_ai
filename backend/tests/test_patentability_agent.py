import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.pipeline import AgentState, PatentabilityScore
from backend.agents.patentability_agent import patentability_agent


class TestPatentabilityAgent(unittest.TestCase):
    """
    Unit tests for Agent 05 — Patentability Agent.
    All external calls (LLM, ChromaDB retriever) are mocked.
    Innovation ideas are stubbed as direct state input.
    """

    def setUp(self):
        """Base state with stubbed innovation_ideas simulating Agent 04 output."""
        self.base_state: AgentState = {
            "domain": "Renewable Energy",
            "research_topics": [],
            "patent_clusters": [],
            "gap_matrix": [],
            "innovation_ideas": [
                {
                    "name": "SolarCell Interface Pro",
                    "description": "An automated micro-engineered charge balancing layer that "
                                   "matches solid-state solar interfaces dynamically.",
                    "target_user": "Solar panel developers and battery manufacturing labs",
                    "type": "startup",
                    "based_on_gap": "Solid-State Photovoltaic Interfaces"
                }
            ],
            "patentability_scores": [],
            "report_markdown": "",
            "top_recommendation": {},
            "error": None
        }

    # ------------------------------------------------------------------ #
    # TEST 1: Successful evaluation with prior art from patent_global
    # ------------------------------------------------------------------ #
    @patch("backend.agents.patentability_agent.retrieve")
    @patch("backend.agents.patentability_agent.service_retrieve")
    @patch("backend.agents.patentability_agent.generate_response")
    def test_success_with_prior_art_from_global(
        self, mock_generate, mock_service_retrieve, mock_retrieve
    ):
        """
        Verifies that when the dynamic patents collection is empty,
        the agent falls back to 'patent_global', retrieves prior art,
        calls Gemini, computes the weighted score, and returns
        a valid PatentabilityScore object.
        """
        # Dynamic collection returns nothing → triggers fallback
        mock_retrieve.return_value = []

        # patent_global returns one matching patent
        mock_service_retrieve.return_value = [
            {
                "id": "US-12345-B2",
                "document": "Title: Solar Interface Balancing\nAbstract: Centralized optimization of charging.",
                "metadata": {
                    "title": "Solar Interface Balancing",
                    "patent_number": "US-12345-B2",
                    "year": 2022,
                    "assignee": "SolarCorp Inc."
                }
            }
        ]

        # Gemini returns scores as a JSON object
        mock_generate.return_value = """{
          "novelty_score": 80,
          "competition_score": 40,
          "feasibility_score": 90,
          "market_potential_score": 85,
          "reasoning": "Highly feasible and novel. Minor competition from SolarCorp patent, but claims differ."
        }"""

        final_state = patentability_agent(self.base_state)

        # No errors
        self.assertIsNone(final_state.get("error"))

        scores = final_state.get("patentability_scores", [])
        self.assertEqual(len(scores), 1)

        # Validate against Pydantic schema
        score = PatentabilityScore(**scores[0])
        self.assertEqual(score.innovation_name, "SolarCell Interface Pro")
        self.assertEqual(score.novelty_score, 80)
        self.assertEqual(score.competition_score, 40)
        self.assertEqual(score.feasibility_score, 90)
        self.assertEqual(score.market_potential_score, 85)

        # Verify weighted formula:
        # novelty*0.35 + (100-competition)*0.25 + feasibility*0.20 + market*0.20
        # 80*0.35=28  |  60*0.25=15  |  90*0.20=18  |  85*0.20=17  => 78
        self.assertEqual(score.overall_score, 78)

        # Prior-art citation should reference patent number
        self.assertTrue(len(score.similar_patents) > 0)
        self.assertIn("US-12345-B2", score.similar_patents[0])

        print(f"\n[PASS] test_success_with_prior_art_from_global")
        print(f"  Name: {score.innovation_name}")
        print(f"  Overall Score: {score.overall_score}/100")
        print(f"  Novelty: {score.novelty_score} | Competition: {score.competition_score} "
              f"| Feasibility: {score.feasibility_score} | Market: {score.market_potential_score}")
        print(f"  Cited Prior Art: {score.similar_patents}")

    # ------------------------------------------------------------------ #
    # TEST 2: Dynamic patent collection is populated (no fallback needed)
    # ------------------------------------------------------------------ #
    @patch("backend.agents.patentability_agent.retrieve")
    @patch("backend.agents.patentability_agent.generate_response")
    def test_success_with_dynamic_patent_collection(self, mock_generate, mock_retrieve):
        """
        Verifies that when the dynamic 'patents_{domain}' collection
        returns results, the agent uses them directly (no fallback).
        """
        # Dynamic collection returns results
        mock_retrieve.return_value = [
            {
                "id": "US-99999-A1",
                "document": "Title: Solid State PV\nAbstract: Novel interface techniques.",
                "metadata": {
                    "title": "Solid State PV Interface",
                    "patent_number": "US-99999-A1",
                    "year": 2023,
                    "assignee": "EnergyTech LLC"
                }
            }
        ]

        mock_generate.return_value = """{
          "novelty_score": 90,
          "competition_score": 20,
          "feasibility_score": 85,
          "market_potential_score": 92,
          "reasoning": "Highly novel — no direct claim overlap found in the retrieved prior art."
        }"""

        final_state = patentability_agent(self.base_state)

        self.assertIsNone(final_state.get("error"))
        scores = final_state.get("patentability_scores", [])
        self.assertEqual(len(scores), 1)

        score = PatentabilityScore(**scores[0])
        self.assertEqual(score.novelty_score, 90)

        # Formula: 90*0.35 + 80*0.25 + 85*0.20 + 92*0.20 = 31.5+20+17+18.4 = 86.9 → 87
        self.assertEqual(score.overall_score, 87)

        print(f"\n[PASS] test_success_with_dynamic_patent_collection")
        print(f"  Overall Score: {score.overall_score}/100")

    # ------------------------------------------------------------------ #
    # TEST 3: LLM returns invalid JSON → fallback scores kick in
    # ------------------------------------------------------------------ #
    @patch("backend.agents.patentability_agent.retrieve")
    @patch("backend.agents.patentability_agent.service_retrieve")
    @patch("backend.agents.patentability_agent.generate_response")
    def test_fallback_on_invalid_llm_json(
        self, mock_generate, mock_service_retrieve, mock_retrieve
    ):
        """
        Verifies the fallback scoring logic triggers safely when
        the LLM returns unparseable text.
        """
        mock_retrieve.return_value = []
        mock_service_retrieve.return_value = []
        mock_generate.return_value = "Sorry, I cannot evaluate this at the moment."

        final_state = patentability_agent(self.base_state)

        self.assertIsNone(final_state.get("error"))
        scores = final_state.get("patentability_scores", [])
        self.assertEqual(len(scores), 1)

        score = PatentabilityScore(**scores[0])
        # Fallback should produce valid non-zero scores
        self.assertGreater(score.overall_score, 0)
        self.assertLessEqual(score.overall_score, 100)
        self.assertTrue(len(score.reasoning) > 0)
        self.assertEqual(score.similar_patents, [])   # No prior art found

        print(f"\n[PASS] test_fallback_on_invalid_llm_json")
        print(f"  Fallback Overall Score: {score.overall_score}/100")

    # ------------------------------------------------------------------ #
    # TEST 4: Empty innovation_ideas list → agent exits cleanly
    # ------------------------------------------------------------------ #
    @patch("backend.agents.patentability_agent.generate_response")
    def test_empty_innovation_ideas(self, mock_generate):
        """
        Verifies that when innovation_ideas is empty,
        the agent sets an error message and returns an empty scores list.
        """
        state = self.base_state.copy()
        state["innovation_ideas"] = []

        final_state = patentability_agent(state)

        scores = final_state.get("patentability_scores", [])
        self.assertEqual(len(scores), 0)
        self.assertIsNotNone(final_state.get("error"))
        mock_generate.assert_not_called()

        print(f"\n[PASS] test_empty_innovation_ideas")
        print(f"  Error message: {final_state.get('error')}")

    # ------------------------------------------------------------------ #
    # TEST 5: Multiple ideas → sorted by overall_score descending
    # ------------------------------------------------------------------ #
    @patch("backend.agents.patentability_agent.retrieve")
    @patch("backend.agents.patentability_agent.service_retrieve")
    @patch("backend.agents.patentability_agent.generate_response")
    def test_multiple_ideas_sorted_descending(
        self, mock_generate, mock_service_retrieve, mock_retrieve
    ):
        """
        Verifies that when multiple ideas are evaluated,
        the final list is sorted by overall_score descending.
        """
        state = self.base_state.copy()
        state["innovation_ideas"] = [
            {
                "name": "Idea Alpha",
                "description": "First idea description.",
                "target_user": "Engineers",
                "type": "product",
                "based_on_gap": "Gap A"
            },
            {
                "name": "Idea Beta",
                "description": "Second idea description.",
                "target_user": "Startups",
                "type": "startup",
                "based_on_gap": "Gap B"
            }
        ]

        mock_retrieve.return_value = []
        mock_service_retrieve.return_value = []

        # Return different scores per call
        mock_generate.side_effect = [
            """{
              "novelty_score": 60,
              "competition_score": 50,
              "feasibility_score": 60,
              "market_potential_score": 60,
              "reasoning": "Moderate novelty for Alpha."
            }""",
            """{
              "novelty_score": 95,
              "competition_score": 10,
              "feasibility_score": 90,
              "market_potential_score": 95,
              "reasoning": "Extremely novel for Beta."
            }"""
        ]

        final_state = patentability_agent(state)

        self.assertIsNone(final_state.get("error"))
        scores = final_state.get("patentability_scores", [])
        self.assertEqual(len(scores), 2)

        # Beta should rank first (higher score)
        self.assertEqual(scores[0]["innovation_name"], "Idea Beta")
        self.assertGreater(scores[0]["overall_score"], scores[1]["overall_score"])

        print(f"\n[PASS] test_multiple_ideas_sorted_descending")
        print(f"  Rank #1: {scores[0]['innovation_name']} — Score: {scores[0]['overall_score']}")
        print(f"  Rank #2: {scores[1]['innovation_name']} — Score: {scores[1]['overall_score']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
