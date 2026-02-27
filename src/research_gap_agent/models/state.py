"""LangGraph state and search config."""

import operator
from typing import Annotated

from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from research_gap_agent.models.output import (
    ClusterAnalysis,
    Hypothesis,
    ResearchGap,
    TopicCluster,
)
from research_gap_agent.models.paper import Paper


def _progress_reducer(current: dict | None, update: dict | None) -> dict:
    """Merge concurrent _progress updates; last write wins for CLI display."""
    return update if update else (current or {})


class SearchConfig(TypedDict, total=False):
    """Search depth and filtering parameters."""

    min_papers: int
    max_papers: int
    max_search_iterations: int
    relevance_threshold: float
    min_clusters: int
    max_clusters: int


class AgentState(TypedDict, total=False):
    """State for the research gap agent graph."""

    query: str
    depth: str  # CLI depth label (quick/standard/deep) for logging; search_config holds actual limits
    literature_apis: list[str]
    search_config: SearchConfig
    refined_queries: list[str]
    search_results: Annotated[list[Paper], operator.add]
    filtered_papers: list[Paper]
    topic_clusters: list[TopicCluster]
    cluster_analyses: Annotated[list[ClusterAnalysis], operator.add]
    research_gaps: list[ResearchGap]
    hypotheses: list[Hypothesis]
    report: str
    search_iteration: int
    messages: Annotated[list[BaseMessage], operator.add]
    # For Send() fan-out: current task for search_api or analyze_cluster
    _current_search_task: dict
    _current_cluster_payload: dict
    # Display-only progress for CLI; reducer required for concurrent search_api writes
    _progress: Annotated[dict, _progress_reducer]
