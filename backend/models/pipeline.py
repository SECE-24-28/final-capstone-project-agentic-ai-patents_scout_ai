from typing import TypedDict, List
from backend.models.pydantic_models import (
    Paper, Patent, Gap, InnovationOpportunity, PatentabilityResult, FinalReport
)

class AgentState(TypedDict):
    domain: str
    papers: List[Paper]
    patents: List[Patent]
    research_summary: str
    patent_summary: str
    gaps: List[Gap]
    opportunities: List[InnovationOpportunity]
    patentability_score: List[PatentabilityResult]
    final_report: str
