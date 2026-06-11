from pydantic import BaseModel, Field
from typing import List, Optional

class Paper(BaseModel):
    title: str = Field(..., description="Title of the research paper")
    abstract: str = Field(..., description="Abstract of the research paper")
    authors: List[str] = Field(default_factory=list, description="List of author names")
    year: Optional[int] = Field(None, description="Publication year")
    source: str = Field("arXiv", description="Data source name (e.g. arXiv, Semantic Scholar)")
    url: Optional[str] = Field(None, description="Direct URL to the paper")

class Patent(BaseModel):
    title: str = Field(..., description="Title of the patent")
    abstract: str = Field(..., description="Abstract or summary of the patent description")
    inventors: List[str] = Field(default_factory=list, description="List of inventor names")
    year: Optional[int] = Field(None, description="Year of patent issue or publication")
    patent_id: str = Field(..., description="Unique patent number or document identifier")
    source: str = Field("PatentsView", description="Data source name (e.g. PatentsView)")

class ResearchSummary(BaseModel):
    domain: str = Field(..., description="The searched technology domain")
    key_themes: List[str] = Field(..., description="Key research themes discovered")
    summary: str = Field(..., description="Synthesized text summary of the research landscape")

class PatentSummary(BaseModel):
    domain: str = Field(..., description="The searched technology domain")
    key_clusters: List[str] = Field(..., description="Identified patent clusters or classification areas")
    saturation_level: str = Field(..., description="Saturaton status: High, Medium, or Low")
    summary: str = Field(..., description="Synthesized text summary of patent space")

class Gap(BaseModel):
    title: str = Field(..., description="Name or title of the technology gap")
    description: str = Field(..., description="Detailed explanation of the gap")
    research_interest: str = Field(..., description="Academic interest level (High, Medium, Low)")
    patent_saturation: str = Field(..., description="Patent density/saturation level (High, Medium, Low)")
    evidence: List[str] = Field(default_factory=list, description="Citations or notes supporting the gap discovery")

class InnovationOpportunity(BaseModel):
    title: str = Field(..., description="Name of the generated innovation opportunity")
    description: str = Field(..., description="Detailed description of the startup or product idea")
    core_technology: str = Field(..., description="Core underlying technology to build this product")
    target_market: str = Field(..., description="Target market and primary audience")
    potential_benefits: List[str] = Field(..., description="Benefits and advantages of this innovation")

class PatentabilityResult(BaseModel):
    title: str = Field(..., description="Title of the evaluated innovation opportunity")
    novelty_score: int = Field(..., description="Estimated novelty score (0-100)")
    market_potential: int = Field(..., description="Estimated market potential score (0-100)")
    patentability_score: int = Field(..., description="Calculated patentability score (0-100)")
    prior_art_citations: List[str] = Field(default_factory=list, description="Relevant prior art citations found during search")
    mitigation_strategy: str = Field(..., description="Recommended technical modification or strategy to avoid infringement")

class FinalReport(BaseModel):
    domain: str = Field(..., description="Analyzed technology domain")
    executive_summary: str = Field(..., description="Executive summary of research gaps and opportunities")
    gaps: List[Gap] = Field(default_factory=list)
    opportunities: List[InnovationOpportunity] = Field(default_factory=list)
    patentability_assessments: List[PatentabilityResult] = Field(default_factory=list)
    created_at: Optional[str] = Field(None, description="Timestamp of report generation")
