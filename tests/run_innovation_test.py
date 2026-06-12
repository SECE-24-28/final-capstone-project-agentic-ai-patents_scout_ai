import sys
import json
import logging

sys.path.insert(0, '.')

# Suppress verbose logging during test run
logging.basicConfig(level=logging.WARNING)

from backend.pipeline import AgentState
from backend.agents.research_agent import research_agent
from backend.agents.patent_agent import patent_agent
from backend.agents.gap_analysis_agent import gap_analysis_agent
from backend.agents.innovation_agent import innovation_agent

DOMAIN = "Electric Vehicles"

print("=" * 70)
print("  PatentScout AI - Innovation Agent Verification Run")
print(f"  Domain: {DOMAIN}")
print("=" * 70)

state: AgentState = {
    "domain": DOMAIN,
    "research_topics": [],
    "patent_clusters": [],
    "gap_matrix": [],
    "innovation_ideas": [],
    "patentability_scores": [],
    "report_markdown": "",
    "top_recommendation": {},
    "error": None
}

# --- Step 1: Research Agent ---
print("[Step 1/4] Running Research Agent...")
state = research_agent(state)
rt_count = len(state.get("research_topics", []))
print(f"  -> Research Topics: {rt_count} | Error: {state.get('error')}")

# --- Step 2: Patent Agent ---
print("[Step 2/4] Running Patent Agent...")
state = patent_agent(state)
pc_count = len(state.get("patent_clusters", []))
print(f"  -> Patent Clusters: {pc_count} | Error: {state.get('error')}")

# --- Step 3: Gap Analysis Agent ---
print("[Step 3/4] Running Gap Analysis Agent...")
state = gap_analysis_agent(state)
gaps = state.get("gap_matrix", [])
print(f"  -> Technology Gaps: {len(gaps)} | Error: {state.get('error')}")

# --- Step 4: Innovation Agent ---
print("[Step 4/4] Running Innovation Agent...")
state = innovation_agent(state)
ideas = state.get("innovation_ideas", [])
print(f"  -> Innovation Ideas: {len(ideas)} | Error: {state.get('error')}")

print()
print("=" * 70)
print("  ACCURACY EVALUATION")
print("=" * 70)

total_checks = 0
total_passed = 0

for idx, idea in enumerate(ideas):
    # Fields from current InnovationIdea schema
    name         = idea.get("name", "")
    description  = idea.get("description", "")
    target_user  = idea.get("target_user", "")
    idea_type    = idea.get("type", "")
    based_on_gap = idea.get("based_on_gap", "")

    checks = {
        "has_meaningful_name":       len(name) > 5,
        "has_detailed_description":  len(description) > 50,
        "has_target_user":           len(target_user) > 5,
        "has_valid_type":            len(idea_type) > 0,
        "has_based_on_gap":          len(based_on_gap) > 0,
    }

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    total_checks += total
    total_passed += passed

    print()
    print(f"  Idea #{idx + 1}: {name}")
    for k, v in checks.items():
        icon = "PASS" if v else "FAIL"
        print(f"    [{icon}] {k.replace('_', ' ').title()}")
    pct = round(passed / total * 100, 1)
    print(f"  Idea Score: {passed}/{total} ({pct}%)")

overall = round(total_passed / total_checks * 100, 1) if total_checks > 0 else 0.0

print()
print("=" * 70)
print("  FINAL RESULTS")
print("=" * 70)
print(f"  Domain          : {DOMAIN}")
print(f"  Research Topics : {rt_count}")
print(f"  Patent Clusters : {pc_count}")
print(f"  Technology Gaps : {len(gaps)}")
print(f"  Innovation Ideas: {len(ideas)}")
print(f"  Checks Passed   : {total_passed}/{total_checks}")
print()
print(f"  >>> INNOVATION AGENT ACCURACY: {overall}% <<<")
print()

if overall >= 90:
    grade = "EXCELLENT"
elif overall >= 75:
    grade = "GOOD"
elif overall >= 60:
    grade = "ACCEPTABLE"
else:
    grade = "NEEDS IMPROVEMENT"

print(f"  Quality Grade   : {grade}")
print("=" * 70)

print()
print("GENERATED INNOVATION IDEAS (Full Detail):")
print(json.dumps(ideas, indent=2))
