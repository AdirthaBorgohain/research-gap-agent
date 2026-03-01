"""Deep analysis node: per-cluster methodology/findings/limitations/trends."""

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel

from research_gap_agent.models.output import (
    CitedFinding,
    ClusterAnalysis,
    ClusterAnalysisStructured,
)
from research_gap_agent.models.paper import Paper
from research_gap_agent.models.state import AgentState
from research_gap_agent.prompts.templates import DEEP_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


def fan_out_analyze_edges(state: AgentState) -> list:
    """Return one Send per topic cluster for parallel deep analysis."""
    from langgraph.types import Send

    clusters = state.get("topic_clusters") or []
    papers: list[Paper] = state.get("filtered_papers") or []
    n_global_papers = len(papers)
    sends = []
    for c in clusters:
        indices = [i for i in (c.paper_indices or []) if 0 <= i < n_global_papers]
        cluster_papers = [papers[i] for i in indices]
        lines = []
        for num, p in enumerate(cluster_papers, start=1):
            ab = (p.abstract or "")[:350]
            lines.append(f"Paper {num}: {p.title} ({p.year or 'n.d.'})\n  {ab}")
        papers_text = "\n\n".join(lines)
        sends.append(
            Send(
                "analyze_cluster",
                {
                    "_current_cluster_payload": {
                        "cluster_label": c.label,
                        "papers_text": papers_text,
                        "paper_indices_0based": indices,
                        "n_global_papers": n_global_papers,
                    }
                },
            )
        )
    return sends


def create_analyze_cluster_node(llm: BaseChatModel):
    """Create analyze_cluster node that closes over llm."""

    def analyze_cluster_node(state: AgentState) -> dict[str, Any]:
        payload = state.get("_current_cluster_payload") or {}
        cluster_label = payload.get("cluster_label") or "Unknown"
        papers_text = payload.get("papers_text") or ""
        paper_indices_0based = payload.get("paper_indices_0based") or []
        n_global_papers = payload.get("n_global_papers") or 0
        prompt = DEEP_ANALYSIS_PROMPT.format(
            cluster_label=cluster_label,
            papers_text=papers_text,
        )
        analysis = _analyze_cluster_structured(
            llm=llm,
            prompt=prompt,
            cluster_label=cluster_label,
            paper_indices_0based=paper_indices_0based,
            n_global_papers=n_global_papers,
        )
        return {"cluster_analyses": [analysis]}

    return analyze_cluster_node


def _cluster_to_global_indices(
    paper_numbers: list[int],
    paper_indices_0based: list[int],
    n_cluster: int,
) -> list[int]:
    """Map 1-based cluster-relative paper numbers to global 1-based indices. Invalid/out-of-range -> skip."""
    out = []
    for p in paper_numbers:
        if not (1 <= p <= n_cluster):
            continue
        idx_0based = paper_indices_0based[p - 1]
        out.append(idx_0based + 1)
    return sorted(set(out))


def _analyze_cluster_structured(
    llm: BaseChatModel,
    prompt: str,
    cluster_label: str,
    paper_indices_0based: list[int],
    n_global_papers: int,
) -> ClusterAnalysis:
    """Run deep analysis with structured output."""
    structured_llm = llm.with_structured_output(ClusterAnalysisStructured)
    n_cluster = len(paper_indices_0based)
    try:
        out = structured_llm.invoke(prompt)
        cited_findings = []
        for f in getattr(out, "findings", []) or []:
            text = getattr(f, "finding", "") or (f if isinstance(f, str) else "")
            if not text:
                continue
            paper_numbers = getattr(f, "paper_numbers", None) or []
            global_indices = _cluster_to_global_indices(
                paper_numbers=paper_numbers,
                paper_indices_0based=paper_indices_0based,
                n_cluster=n_cluster,
            )
            cited_findings.append(
                CitedFinding(text=text[:500], paper_indices=global_indices)
            )
        methodologies = getattr(out, "methodologies", None) or []
        limitations = getattr(out, "limitations", None) or []
        trend = getattr(out, "trend", None) or "unknown"
        contradictions = getattr(out, "contradictions", None) or []
        return ClusterAnalysis(
            cluster_label=cluster_label,
            methodologies=methodologies[:15],
            findings=cited_findings[:15],
            limitations=limitations[:15],
            trend=trend
            if trend in ("increasing", "stable", "decreasing", "unknown")
            else "unknown",
            contradictions=contradictions[:10],
        )
    except Exception as e:
        logger.warning("Structured deep analysis failed (%s), returning empty analysis", e)
        return ClusterAnalysis(
            cluster_label=cluster_label,
            methodologies=[],
            findings=[],
            limitations=[],
            trend="unknown",
            contradictions=[],
        )
