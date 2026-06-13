import sys
import json
import logging
from backend.pipeline import AgentState
from backend.agents.research_agent import research_agent
from backend.agents.patent_agent import patent_agent
from backend.agents.gap_analysis_agent import gap_analysis_agent
from backend.agents.innovation_agent import innovation_agent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("VerifyInnovationAgentLive")


def evaluate_idea_quality(idea: dict) -> dict:
    """
    Evaluates the quality of a single innovation idea against 6 defined accuracy criteria.
    Returns a score report for that idea.
    """
    checks = {}

    # 1. Title is present and meaningful (> 5 chars, not generic)
    title = idea.get("title", "")
    checks["has_meaningful_title"] = len(title) > 5 and title not in ["", "Unknown", "Innovation"]

    # 2. Description is detailed (> 50 chars)
    description = idea.get("description", "")
    checks["has_detailed_description"] = len(description) > 50

    # 3. Core technology is specified
    core_tech = idea.get("core_technology", "")
    checks["has_core_technology"] = len(core_tech) > 10

    # 4. Target market is specified
    target_market = idea.get("target_market", "")
    checks["has_target_market"] = len(target_market) > 5

    # 5. Potential benefits is a non-empty list with at least 2 items
    benefits = idea.get("potential_benefits", [])
    checks["has_benefits_list"] = isinstance(benefits, list) and len(benefits) >= 2

    # 6. Novelty score is a valid integer between 0 and 100
    novelty_score = idea.get("novelty_score", None)
    checks["has_valid_novelty_score"] = isinstance(novelty_score, int) and 0 <= novelty_score <= 100

    # 7. Market potential is a valid string
    market_potential = idea.get("market_potential", "")
    checks["has_valid_market_potential"] = market_potential in ["High", "Medium", "Low"]

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    idea_accuracy = round((passed / total) * 100, 1)

    return {
        "title": title,
        "checks": checks,
        "passed": passed,
        "total": total,
        "accuracy_pct": idea_accuracy,
    }


def run_live_verification():
    print("=" * 70)
    print("  PatentScout AI — Innovation Agent Live Verification Run")
    print("=" * 70)

    # 1. Ask user for domain input
    print("\nSupported domains: Artificial Intelligence, Electric Vehicles, Cybersecurity,")
    print("                   Renewable Energy, Healthcare, Smart Cities, Biotechnology")
    domain = input("\nEnter technology domain to analyze (default: Electric Vehicles): ").strip()
    if not domain:
        domain = "Electric Vehicles"

    print(f"\n[Config] Target Domain: {domain}")

    state: AgentState = {
        "domain": domain,
        "research_topics": [],
        "patent_clusters": [],
        "gap_matrix": [],
        "innovation_ideas": [],
        "patentability_scores": [],
        "report_markdown": "",
        "top_recommendation": {},
        "error": None,
    }

    # ─── Step 1: Research Agent ───────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("[Step 1/4] Executing Research Agent...")
    state = research_agent(state)
    if state.get("error"):
        print(f"\n[ERROR] Research Agent Failed: {state['error']}")
        return False
    research_count = len(state.get("research_topics", []))
    print(f"[✓] Research Agent: identified {research_count} research topics.")

    # ─── Step 2: Patent Agent ─────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("[Step 2/4] Executing Patent Agent...")
    state = patent_agent(state)
    if state.get("error"):
        print(f"\n[ERROR] Patent Agent Failed: {state['error']}")
        return False
    patent_count = len(state.get("patent_clusters", []))
    print(f"[✓] Patent Agent: identified {patent_count} patent clusters.")

    # ─── Step 3: Gap Analysis Agent ───────────────────────────────────────────
    print("\n" + "─" * 70)
    print("[Step 3/4] Executing Gap Analysis Agent...")
    state = gap_analysis_agent(state)
    if state.get("error"):
        print(f"\n[ERROR] Gap Analysis Agent Failed: {state['error']}")
        return False
    gaps = state.get("gap_matrix", [])
    print(f"[✓] Gap Analysis Agent: identified {len(gaps)} technology gaps.")

    # ─── Step 4: Innovation Agent ─────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("[Step 4/4] Executing Innovation Agent...")
    state = innovation_agent(state)
    if state.get("error"):
        print(f"\n[ERROR] Innovation Agent Failed: {state['error']}")
        return False

    ideas = state.get("innovation_ideas", [])
    print(f"[✓] Innovation Agent: generated {len(ideas)} innovation ideas.")

    if not ideas:
        print("\n[FAIL] No innovation ideas were produced. Check LLM configuration.")
        return False

    # ─── Accuracy Evaluation ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  INNOVATION AGENT ACCURACY EVALUATION REPORT")
    print("=" * 70)

    total_checks = 0
    total_passed = 0
    idea_reports = []

    for idx, idea in enumerate(ideas):
        report = evaluate_idea_quality(idea)
        idea_reports.append(report)
        total_checks += report["total"]
        total_passed += report["passed"]

        print(f"\n  Idea #{idx + 1}: {report['title']}")
        print(f"  {'─' * 60}")
        for criterion, result in report["checks"].items():
            icon = "✓" if result else "✗"
            print(f"    [{icon}] {criterion.replace('_', ' ').title()}")
        print(f"\n  Idea Accuracy: {report['accuracy_pct']}% ({report['passed']}/{report['total']} checks passed)")

    # ─── Overall Score ────────────────────────────────────────────────────────
    overall_accuracy = round((total_passed / total_checks) * 100, 1) if total_checks > 0 else 0.0

    print("\n" + "=" * 70)
    print("  FINAL ACCURACY SUMMARY")
    print("=" * 70)
    print(f"  Target Domain       : {domain}")
    print(f"  Research Topics     : {research_count}")
    print(f"  Patent Clusters     : {patent_count}")
    print(f"  Technology Gaps     : {len(gaps)}")
    print(f"  Innovation Ideas    : {len(ideas)}")
    print(f"  Total Quality Checks: {total_checks}")
    print(f"  Checks Passed       : {total_passed}")
    print(f"\n  ┌──────────────────────────────────────────────────┐")
    print(f"  │  Innovation Agent Overall Accuracy: {overall_accuracy:>5}%        │")
    print(f"  └──────────────────────────────────────────────────┘")

    # Quality grade
    if overall_accuracy >= 90:
        grade = "EXCELLENT ✅"
    elif overall_accuracy >= 75:
        grade = "GOOD ✅"
    elif overall_accuracy >= 60:
        grade = "ACCEPTABLE ⚠️"
    else:
        grade = "NEEDS IMPROVEMENT ❌"
    print(f"\n  Quality Grade: {grade}")

    # ─── Print generated ideas in full ───────────────────────────────────────
    print("\n" + "=" * 70)
    print("  GENERATED INNOVATION IDEAS (Full Detail)")
    print("=" * 70)
    print(json.dumps(ideas, indent=2))
    print("=" * 70 + "\n")

    return True


if __name__ == "__main__":
    success = run_live_verification()
    sys.exit(0 if success else 1)
