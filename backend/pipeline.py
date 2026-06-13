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

class InnovationIdea(BaseModel):
    name: str = Field(..., description="Short descriptive name of the product/startup idea")
    description: str = Field(..., description="Detailed description of the startup or product idea")
    target_user: str = Field(..., description="Target market and primary audience")
    type: str = Field(..., description="Type of innovation, e.g. product, startup, research")
    based_on_gap: str = Field(..., description="The technological gap this idea addresses")

class PatentabilityScore(BaseModel):
    innovation_name: str = Field(..., description="Title of the evaluated innovation opportunity")
    novelty_score: int = Field(..., description="Estimated novelty score (0-100)")
    competition_score: int = Field(..., description="Estimated competition score (0-100, lower is better)")
    feasibility_score: int = Field(..., description="Estimated feasibility score (0-100)")
    market_potential_score: int = Field(..., description="Estimated market potential score (0-100)")
    overall_score: int = Field(..., description="Calculated overall patentability score (0-100)")
    reasoning: str = Field(..., description="Detailed reasoning explaining the score calculations based on prior art")
    similar_patents: List[str] = Field(default_factory=list, description="Relevant prior-art patents found during search")

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
