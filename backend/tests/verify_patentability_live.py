"""
Live Verification Script — Patentability Agent (Agent 05)

Pipeline flow:
  Agent 01 (Research)  -->
                          |--> Agent 03 (Gap Analysis) --> [Stub Ideas] --> Agent 05 (Patentability) 
  Agent 02 (Patent)    -->

Since Agent 04 (Innovation Agent) is being built by a teammate,
innovation ideas are auto-generated from the top gaps as stubs,
allowing Agent 05 to be verified end-to-end with real API calls.
"""

import os
import sys
import json
import logging

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.pipeline import AgentState
from backend.agents.research_agent import research_agent
from backend.agents.patent_agent import patent_agent
from backend.agents.gap_analysis_agent import gap_analysis_agent
from backend.agents.patentability_agent import patentability_agent

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("VerifyPatentabilityLive")


def generate_stub_ideas_from_gaps(gaps: list, domain: str) -> list:
    """
    Auto-generates stub innovation ideas directly from the top 3 gaps.
    Used as a placeholder for Agent 04 (Innovation Agent) output.
    """
    stub_ideas = []
    type_cycle = ["product", "startup", "research"]
    
    for i, gap in enumerate(gaps[:3]):
        area = gap.get("area", "Unknown Area")
        rationale = gap.get("rationale", "")
        idea_name = area.replace("-", " ").replace("_", " ").title()
        
        stub_ideas.append({
            "name": f"{idea_name} Platform",
            "description": (
                f"An AI-powered platform that directly addresses the identified gap in '{area}'. "
                f"It leverages cutting-edge technology to bridge research and market needs: {rationale[:120]}..."
            ),
            "target_user": f"R&D teams, engineers, and startups operating in the {domain} sector",
            "type": type_cycle[i % len(type_cycle)],
            "based_on_gap": area
        })
    
    return stub_ideas


def run_live_verification():
    print("=" * 70)
    print("  PATENTABILITY AGENT (05) - LIVE VERIFICATION RUN")
    print("  Pipeline: Agent 01 + 02 -> Gap Analysis -> Stub Ideas -> Agent 05")
    print("=" * 70)

    # ── Select domain ──────────────────────────────────────────────────
    print("\nSupported domains: Electric Vehicles, Renewable Energy, Artificial Intelligence,")
    print("                   Cybersecurity, Healthcare Diagnostics, Smart Agriculture")
    domain = input("\nEnter technology domain (default: Electric Vehicles): ").strip()
    if not domain:
        domain = "Electric Vehicles"

    state: AgentState = {
        "domain": domain,
        "research_topics": [],
        "patent_clusters": [],
        "gap_matrix": [],
        "innovation_ideas": [],
        "patentability_scores": [],
        "report_markdown": "",
        "top_recommendation": {},
        "error": None
    }

    # ── Agent 01: Research Agent ───────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"[Step 1/4] Running Research Agent for domain: '{domain}'...")
    print(f"{'='*70}")
    state = research_agent(state)
    if state.get("error"):
        print(f"\n[ERROR] Research Agent failed: {state['error']}")
        return False
    topics = state.get("research_topics", [])
    print(f"[PASS] Identified {len(topics)} research topics.")
    for t in topics:
        print(f"    * {t.get('topic', t.get('name', 'N/A'))} "
              f"[Activity: {t.get('research_activity', 'N/A')}]")

    # ── Agent 02: Patent Agent ─────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"[Step 2/4] Running Patent Agent for domain: '{domain}'...")
    print(f"{'='*70}")
    state = patent_agent(state)
    if state.get("error"):
        print(f"\n[ERROR] Patent Agent failed: {state['error']}")
        return False
    clusters = state.get("patent_clusters", [])
    print(f"[PASS] Identified {len(clusters)} patent clusters.")
    for c in clusters:
        print(f"    * {c.get('category', 'N/A')} [Saturation: {c.get('saturation', 'N/A')}]")

    # ── Agent 03: Gap Analysis Agent ──────────────────────────────────
    print(f"\n{'='*70}")
    print(f"[Step 3/4] Running Gap Analysis Agent...")
    print(f"{'='*70}")
    state = gap_analysis_agent(state)
    if state.get("error"):
        print(f"\n[ERROR] Gap Analysis Agent failed: {state['error']}")
        return False
    gaps = state.get("gap_matrix", [])
    print(f"[PASS] Identified {len(gaps)} gap opportunities (sorted by score).")
    for g in gaps:
        print(f"    * [{g.get('opportunity_score')}/100] {g.get('area')} "
              f"- Research: {g.get('research_activity')} | Patents: {g.get('patent_activity')}")

    # ── Stub Innovation Ideas (Agent 04 placeholder) ───────────────────
    print(f"\n{'='*70}")
    print(f"[Stub] Generating innovation ideas from top gaps (Agent 04 placeholder)...")
    print(f"{'='*70}")
    stub_ideas = generate_stub_ideas_from_gaps(gaps, domain)
    state["innovation_ideas"] = stub_ideas
    print(f"[PASS] Generated {len(stub_ideas)} stub innovation ideas:")
    for idea in stub_ideas:
        print(f"    * [{idea['type'].upper()}] {idea['name']}")
        print(f"      Gap: {idea['based_on_gap']}")

    # ── Agent 05: Patentability Agent ─────────────────────────────────
    print(f"\n{'='*70}")
    print(f"[Step 4/4] Running Patentability Agent (real Gemini + ChromaDB)...")
    print(f"{'='*70}")
    state = patentability_agent(state)
    if state.get("error"):
        print(f"\n[ERROR] Patentability Agent failed: {state['error']}")
        return False
    scores = state.get("patentability_scores", [])

    # ── Print Results ──────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print(f"  PATENTABILITY EVALUATION RESULTS - {domain.upper()}")
    print(f"{'=' * 70}")

    for rank, score in enumerate(scores, 1):
        overall   = score.get("overall_score", 0)
        novelty   = score.get("novelty_score", 0)
        comp      = score.get("competition_score", 0)
        feasib    = score.get("feasibility_score", 0)
        market    = score.get("market_potential_score", 0)
        reasoning = score.get("reasoning", "")
        patents   = score.get("similar_patents", [])

        print(f"\n  Rank #{rank}: {score.get('innovation_name')}")
        print(f"  {'-'*60}")
        print(f"  Overall Score      : {overall}/100")
        print(f"  Novelty            : {novelty}/100")
        print(f"  Competition        : {comp}/100  (lower = less competition)")
        print(f"  Feasibility        : {feasib}/100")
        print(f"  Market Potential   : {market}/100")
        print(f"\n  Reasoning:")
        print(f"     {reasoning}")
        if patents:
            print(f"\n  Prior Art Citations:")
            for p in patents:
                print(f"     * {p}")
        else:
            print(f"\n  Prior Art Citations: None found in database")

    # Top recommendation
    if scores:
        top = scores[0]
        state["top_recommendation"] = top
        print(f"\n{'=' * 70}")
        print(f"  TOP RECOMMENDATION: {top.get('innovation_name')}")
        print(f"     Overall Patentability Score: {top.get('overall_score')}/100")
        print(f"{'=' * 70}")

    # Summary
    print(f"\n  VERIFICATION SUMMARY")
    print(f"  {'-'*50}")
    print(f"  Domain              : {domain}")
    print(f"  Research Topics     : {len(state['research_topics'])}")
    print(f"  Patent Clusters     : {len(state['patent_clusters'])}")
    print(f"  Gaps Identified     : {len(gaps)}")
    print(f"  Ideas Evaluated     : {len(stub_ideas)}")
    print(f"  Scores Computed     : {len(scores)}")
    print(f"  Errors              : {state.get('error') or 'None'}")
    print(f"\n  Setup and Execution completed successfully!\n")

    return True


if __name__ == "__main__":
    success = run_live_verification()
    sys.exit(0 if success else 1)
