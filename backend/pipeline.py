from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field

class ResearchTopic(BaseModel):
    topic: str = Field(..., description="Short descriptive name of the topic")
    description: str = Field(..., description="Explanation of the research focus")
    research_activity: str = Field(..., description="Activity level, e.g. High, Medium, Low")
    citation_strength: int = Field(..., description="Average citations or relative volume score")

class AgentState(TypedDict):
    domain: str
    research_topics: List[dict]
    patent_clusters: List[dict]
    gap_matrix: List[dict]
    innovation_ideas: List[dict]
    patentability_scores: List[dict]
    report_markdown: str
    top_recommendation: dict
    error: Optional[str]
