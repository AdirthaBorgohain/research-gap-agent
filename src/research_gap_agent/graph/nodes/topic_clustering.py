"""Topic clustering node: group papers into thematic clusters via LLM."""

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel

from research_gap_agent.models.output import ClusteringOutput, TopicCluster
from research_gap_agent.models.state import AgentState
from research_gap_agent.prompts.templates import TOPIC_CLUSTERING_PROMPT

logger = logging.getLogger(__name__)


def create_topic_clustering_node(llm: BaseChatModel):
    """Create topic clustering node that closes over llm."""

    structured_llm = llm.with_structured_output(ClusteringOutput)

    def topic_clustering_node(state: AgentState) -> dict[str, Any]:
        papers = state.get("filtered_papers") or []
        if len(papers) < 2:
            return {
                "topic_clusters": [
                    TopicCluster(
                        label="All",
                        description="Single group",
                        paper_indices=list(range(len(papers))),
                    )
                ]
            }
        lines = []
        for i, p in enumerate(papers):
            ab = (p.abstract or "")[:400]
            lines.append(f"[{i}] {p.title}\n{ab}")
        papers_text = "\n\n".join(lines)
        search_config = state.get("search_config") or {}
        min_clusters = search_config.get("min_clusters", 3)
        max_clusters = search_config.get("max_clusters", 7)
        prompt = TOPIC_CLUSTERING_PROMPT.format(
            papers_text=papers_text,
            min_clusters=min_clusters,
            max_clusters=max_clusters,
        )
        try:
            out = structured_llm.invoke(prompt)
            clusters = out.clusters if hasattr(out, "clusters") else []
        except Exception as e:
            logger.warning("Structured clustering failed: %s", e)
            clusters = [
                TopicCluster(
                    label="General",
                    description="All papers",
                    paper_indices=list(range(len(papers))),
                )
            ]
        # Ensure all indices are valid
        n = len(papers)
        for c in clusters:
            c.paper_indices = [i for i in c.paper_indices if 0 <= i < n][:50]
        if not clusters:
            clusters = [
                TopicCluster(
                    label="General",
                    description="All papers",
                    paper_indices=list(range(len(papers))),
                )
            ]
        logger.info(
            "Topic clustering: target %s-%s clusters, got %s",
            min_clusters,
            max_clusters,
            len(clusters),
        )
        return {"topic_clusters": clusters}

    return topic_clustering_node
