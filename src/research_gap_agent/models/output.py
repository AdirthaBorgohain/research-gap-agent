"""Output models: research gaps, hypotheses, clusters, cluster analysis."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class QueryPlan(BaseModel):
    """Structured output from query planner: search queries only. Depth comes from CLI/config."""

    refined_queries: list[str] = Field(
        description="3-5 search query strings to run against literature APIs",
    )


class GapType(str, Enum):
    """Type of research gap."""

    TOPIC = "topic"  # Core questions, concepts, or subtopics that remain unexplored or underexplored
    METHODOLOGICAL = (
        "methodological"  # Limitations or missing methods, measures, or study designs
    )
    SCOPE = "scope"  # Gaps in populations, contexts, or settings that have not been adequately covered
    TEMPORAL = (
        "temporal"  # Outdated evidence or lack of longitudinal/recent work over time
    )
    CONTRADICTION = "contradiction"  # Conflicting findings, theories, or interpretations in the literature
    INTEGRATION = (
        "integration"  # Missing synthesis across fields, methods, or levels of analysis
    )


class ResearchGap(BaseModel):
    """Identified research gap with evidence."""

    title: str = Field(description="Short title for the gap")
    description: str = Field(description="Detailed description")
    gap_type: GapType = Field(description="Type of gap")
    evidence: list[str] = Field(
        default_factory=list, description="Supporting quotes or references"
    )
    supporting_paper_indices: list[int] = Field(
        default_factory=list,
        description="1-based indices into the canonical paper list (filtered_papers)",
    )


class Hypothesis(BaseModel):
    """Suggested follow-up hypothesis for a research gap."""

    title: str = Field(description="Short hypothesis title")
    description: str = Field(description="Detailed description")
    related_gap_title: str = Field(
        description="Title of the ResearchGap this addresses"
    )
    suggested_methodology: str = Field(description="Suggested methodology or approach")


class TopicCluster(BaseModel):
    """A cluster of papers grouped by topic."""

    label: str = Field(description="Short cluster label")
    description: str = Field(description="What this cluster represents")
    paper_indices: list[int] = Field(
        default_factory=list,
        description="Indices into the filtered_papers list",
    )


class ClusteringOutput(BaseModel):
    """Structured output for topic clustering."""

    clusters: list[TopicCluster] = Field(description="Thematic clusters of papers")


class ResearchGapList(BaseModel):
    """Wrapper for structured output of multiple research gaps."""

    gaps: list[ResearchGap] = Field(
        default_factory=list, description="List of research gaps"
    )


class HypothesisList(BaseModel):
    """Wrapper for structured output of multiple hypotheses."""

    hypotheses: list[Hypothesis] = Field(
        default_factory=list, description="List of hypotheses"
    )


class CitedFinding(BaseModel):
    """A single finding with optional paper-level attribution (1-based into filtered_papers)."""

    text: str = Field(description="The finding or claim text")
    paper_indices: list[int] = Field(
        default_factory=list,
        description="1-based indices into filtered_papers that support this finding; empty = cluster-level only",
    )


class FindingWithCitations(BaseModel):
    """LLM structured output: one finding with paper numbers 1-based within the cluster."""

    finding: str = Field(description="The finding or claim text")
    paper_numbers: list[int] = Field(
        default_factory=list,
        description="1-based indices within this cluster (1=first paper, 2=second, etc.) that support this finding",
    )


class ClusterAnalysisStructured(BaseModel):
    """Structured LLM output for deep analysis of one cluster (findings use cluster-relative paper numbers)."""

    methodologies: list[str] = Field(
        default_factory=list,
        description="Methods, frameworks, or approaches used across these papers",
    )
    findings: list[FindingWithCitations] = Field(
        default_factory=list,
        description="Key findings with supporting paper numbers (1-based within cluster)",
    )
    limitations: list[str] = Field(
        default_factory=list,
        description="Stated limitations across papers",
    )
    trend: Literal["increasing", "stable", "decreasing", "unknown"] = Field(
        description="Attention trend over time",
    )
    contradictions: list[str] = Field(
        default_factory=list,
        description="Conflicting findings or claims",
    )


class ClusterAnalysis(BaseModel):
    """Deep analysis output for one topic cluster."""

    cluster_label: str = Field(description="Label of the cluster analyzed")
    methodologies: list[str] = Field(
        default_factory=list,
        description="Methods used in this cluster",
    )
    findings: list[CitedFinding] = Field(
        default_factory=list,
        description="Key findings synthesized, each with optional supporting paper indices",
    )
    limitations: list[str] = Field(
        default_factory=list,
        description="Stated limitations across papers",
    )
    trend: Literal["increasing", "stable", "decreasing", "unknown"] = Field(
        description="Attention trend over time"
    )
    contradictions: list[str] = Field(
        default_factory=list,
        description="Conflicting findings or claims",
    )
