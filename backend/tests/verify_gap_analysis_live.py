import sys
import json
import logging
from backend.pipeline import AgentState
from backend.agents.research_agent import research_agent
from backend.agents.patent_agent import patent_agent
from backend.agents.gap_analysis_agent import gap_analysis_agent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("VerifyGapAnalysisLive")

def run_live_verification():
    print("=" * 65)
    print("Initializing Multi-Agent Gap Analysis Live Verification Run...")
    print("=" * 65)
    
    # 1. Ask user for domain input
    print("Supported domains: Artificial Intelligence, Biotechnology, Renewable Energy, Cybersecurity, Smart Cities")
    domain = input("Enter technology domain to analyze (default: Electric Vehicles): ").strip()
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
    
    # 2. Run Research Agent
    print("\n[Step 1/3] Executing Research Agent...")
    state = research_agent(state)
    if state.get("error"):
        print(f"\n[ERROR] Research Agent Failed: {state['error']}")
        return False
    print(f"[Success] Identified {len(state.get('research_topics', []))} research topics.")
    
    # 3. Run Patent Agent
    print("\n[Step 2/3] Executing Patent Agent...")
    state = patent_agent(state)
    if state.get("error"):
        print(f"\n[ERROR] Patent Agent Failed: {state['error']}")
        return False
    print(f"[Success] Identified {len(state.get('patent_clusters', []))} patent clusters.")
    
    # 4. Run Gap Analysis Agent
    print("\n[Step 3/3] Executing Gap Analysis Agent...")
    state = gap_analysis_agent(state)
    if state.get("error"):
        print(f"\n[ERROR] Gap Analysis Agent Failed: {state['error']}")
        return False
        
    gaps = state.get("gap_matrix", [])
    print(f"\n[SUCCESS] Integrated Multi-Agent Flow Completed! Identified {len(gaps)} Gap Opportunities:")
    print(json.dumps(gaps, indent=2))
    
    print("\n" + "=" * 65)
    print("Verification Summary:")
    print(f"  - Target Domain: {domain}")
    print(f"  - Research Topics: {len(state['research_topics'])}")
    print(f"  - Patent Clusters: {len(state['patent_clusters'])}")
    print(f"  - Gap Matrix Opportunities: {len(gaps)}")
    if gaps:
        print(f"  - Top Opportunity Identified: '{gaps[0].get('area')}' (Score: {gaps[0].get('opportunity_score')})")
    print("=" * 65 + "\n")
    return True

if __name__ == "__main__":
    success = run_live_verification()
    sys.exit(0 if success else 1)
