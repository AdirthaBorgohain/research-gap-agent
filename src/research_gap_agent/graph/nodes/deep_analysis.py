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
    return [
        Send(
            "analyze_cluster",
            {
                "_current_cluster_payload": {
                    "cluster_label": c.label,
                    "description": c.description,
                    "paper_indices": c.paper_indices,
                }
            },
        )
        for c in clusters
    ]


def create_analyze_cluster_node(llm: BaseChatModel):
    """Create analyze_cluster node that closes over llm."""

    def analyze_cluster_node(state: AgentState) -> dict[str, Any]:
        payload = state.get("_current_cluster_payload") or {}
        papers: list[Paper] = state.get("filtered_papers") or []
        indices = payload.get("paper_indices") or []
        cluster_label = payload.get("cluster_label") or "Unknown"
        cluster_papers = [papers[i] for i in indices if 0 <= i < len(papers)]
        if not cluster_papers:
            return {
                "cluster_analyses": [
                    ClusterAnalysis(
                        cluster_label=cluster_label,
                        methodologies=[],
                        findings=[],
                        limitations=[],
                        trend="unknown",
                        contradictions=[],
                    )
                ]
            }
        lines = []
        for i, p in enumerate(cluster_papers, start=1):
            ab = (p.abstract or "")[:350]
            lines.append(f"Paper {i}: {p.title} ({p.year or 'n.d.'})\n  {ab}")
        papers_text = "\n\n".join(lines)
        prompt = DEEP_ANALYSIS_PROMPT.format(
            cluster_label=cluster_label,
            papers_text=papers_text,
        )
        n_cluster = len(cluster_papers)
        paper_indices_0based = indices[:n_cluster]
        analysis = _analyze_cluster_structured(
            llm=llm,
            prompt=prompt,
            cluster_label=cluster_label,
            paper_indices_0based=paper_indices_0based,
            n_global_papers=len(papers),
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
    """Run deep analysis with structured output; fallback to free-text parse if needed."""
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
            methodologies=methodologies[:15] or ["Not specified"],
            findings=cited_findings[:15] or [
                CitedFinding(text="Not specified", paper_indices=[]),
            ],
            limitations=limitations[:15] or [],
            trend=trend if trend in ("increasing", "stable", "decreasing", "unknown") else "unknown",
            contradictions=contradictions[:10],
        )
    except Exception as e:
        logger.warning("Structured deep analysis failed (%s), falling back to parse", e)
        resp = llm.invoke(prompt)
        content = getattr(resp, "content", str(resp))
        return _parse_cluster_analysis(
            content=content,
            cluster_label=cluster_label,
        )


def _parse_cluster_analysis(content: str, cluster_label: str) -> ClusterAnalysis:
    """Parse LLM response into ClusterAnalysis."""
    import re

    methodologies = []
    findings = []
    limitations = []
    contradictions = []
    trend = "unknown"
    lower = content.lower()
    for m in re.finditer(
        r"(?:methodolog|approach|method)s?\s*[:\-]\s*(.+?)(?=\n\n|\n\s*\d\.|\Z)",
        content,
        re.DOTALL | re.I,
    ):
        methodologies.extend(_bullet_lines(m.group(1)))
    for m in re.finditer(
        r"finding[s]?\s*[:\-]\s*(.+?)(?=\n\n|\n\s*\d\.|\Z)", content, re.DOTALL | re.I
    ):
        findings.extend(_bullet_lines(m.group(1)))
    for m in re.finditer(
        r"limitation[s]?\s*[:\-]\s*(.+?)(?=\n\n|\n\s*\d\.|\Z)",
        content,
        re.DOTALL | re.I,
    ):
        limitations.extend(_bullet_lines(m.group(1)))
    for m in re.finditer(
        r"contradiction[s]?\s*[:\-]\s*(.+?)(?=\n\n|\n\s*\d\.|\Z)",
        content,
        re.DOTALL | re.I,
    ):
        contradictions.extend(_bullet_lines(m.group(1)))
    if "increasing" in lower:
        trend = "increasing"
    elif "decreasing" in lower:
        trend = "decreasing"
    elif "stable" in lower:
        trend = "stable"
    cited_findings = [
        CitedFinding(text=s[:500], paper_indices=[])
        for s in (findings[:15] or ["Not specified"])
    ]
    return ClusterAnalysis(
        cluster_label=cluster_label,
        methodologies=methodologies[:15] or ["Not specified"],
        findings=cited_findings,
        limitations=limitations[:15] or [],
        trend=trend,
        contradictions=contradictions[:10],
    )


def _bullet_lines(block: str) -> list[str]:
    lines = [s.strip() for s in block.split("\n") if s.strip()]
    out = []
    for line in lines:
        line = line.lstrip("-*•· \t")
        if len(line) > 10:
            out.append(line[:500])
    return out[:20]
