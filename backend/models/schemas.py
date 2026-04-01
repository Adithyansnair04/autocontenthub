"""
Pydantic data models / schemas for the content factory pipeline.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ContentDomain(str, Enum):
    LINKEDIN = "linkedin"
    BLOG = "blog"
    TWEET = "tweet"
    EMAIL = "email"


class BrandStyle(BaseModel):
    """Brand voice and style extracted from website analysis."""
    brand_name: str = ""
    tone: str = "professional and clear"
    voice_characteristics: list[str] = Field(default_factory=list)
    vocabulary_patterns: list[str] = Field(default_factory=list)
    messaging_themes: list[str] = Field(default_factory=list)
    sample_phrases: list[str] = Field(default_factory=list)
    do_not_use: list[str] = Field(default_factory=list)
    raw_excerpts: str = ""


class FactSheet(BaseModel):
    """Structured facts extracted from source material."""
    product_name: str = ""
    value_proposition: str = ""
    core_features: list[str] = Field(default_factory=list)
    key_benefits: list[str] = Field(default_factory=list)
    technical_specs: list[str] = Field(default_factory=list)
    target_audience: str = ""
    ambiguous_statements: list[str] = Field(default_factory=list)
    raw_summary: str = ""


class ContentPiece(BaseModel):
    """A single piece of generated content."""
    domain: ContentDomain
    title: str = ""
    content: str = ""
    status: str = "draft"
    editor_notes: str = ""
    revision_count: int = 0


class AgentLog(BaseModel):
    """Log entry from an agent action."""
    agent: str
    action: str
    message: str
    timestamp: str = ""


class CampaignRequest(BaseModel):
    """Input request to run a content campaign."""
    source_text: str = ""
    source_url: Optional[str] = None
    brand_url: Optional[str] = None
    target_audience: str = "general professionals"
    selected_domains: list[ContentDomain] = Field(
        default_factory=lambda: [ContentDomain.LINKEDIN, ContentDomain.BLOG]
    )


class CampaignResult(BaseModel):
    """Output of a content campaign run."""
    status: str = "running"
    brand_style: Optional[BrandStyle] = None
    fact_sheet: Optional[FactSheet] = None
    content_pieces: list[ContentPiece] = Field(default_factory=list)
    agent_logs: list[AgentLog] = Field(default_factory=list)