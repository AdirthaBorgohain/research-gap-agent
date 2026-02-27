"""Paper model for normalized literature results."""

from typing import Literal

from pydantic import BaseModel, Field


class Paper(BaseModel):
    """Normalized paper representation from any literature API."""

    id: str = Field(description="Unique identifier (API-specific or DOI)")
    title: str = Field(description="Paper title")
    abstract: str | None = Field(default=None, description="Abstract text")
    authors: list[str] = Field(default_factory=list, description="Author names")
    year: int | None = Field(default=None, description="Publication year")
    citation_count: int | None = Field(
        default=None, description="Citation count when available"
    )
    venue: str | None = Field(default=None, description="Venue or journal name")
    url: str | None = Field(default=None, description="URL to paper")
    doi: str | None = Field(default=None, description="DOI when available")
    source: Literal["semantic_scholar", "openalex", "arxiv"] = Field(
        description="Source API"
    )
    relevance_score: float | None = Field(
        default=None,
        description="Score 0-1 from relevance filter (set by PaperProcessor)",
    )
