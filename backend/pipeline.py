from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field

class ResearchTopic(BaseModel):
    topic: str = Field(..., description="Short descriptive name of the topic")
    description: str = Field(..., description="Explanation of the research focus")
    research_activity: str = Field(..., description="Activity level, e.g. High, Medium, Low")
    citation_strength: int = Field(..., description="Average citations or relative volume score")

class PatentCluster(BaseModel):
    category: str = Field(..., description="Name of the patent category")
    description: str = Field(..., description="Detailed explanation of the patent cluster focus")
    saturation: str = Field(..., description="Patent density/saturation level (High, Medium, Low)")
    major_assignees: List[str] = Field(default_factory=list, description="Top companies or institutions holding patents in this area")

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
