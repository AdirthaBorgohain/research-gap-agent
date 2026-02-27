"""Report writer node: compile markdown report."""

import logging
import re
from typing import Any

from langchain_core.language_models import BaseChatModel

from research_gap_agent.models.state import AgentState
from research_gap_agent.prompts.templates import REPORT_WRITING_PROMPT
from research_gap_agent.utils.citations import (
    citation_list_text,
    findings_citations_section,
    format_gap_citations,
    references_section_md,
)

logger = logging.getLogger(__name__)


def _inject_references_section(report: str, references_md: str) -> str:
    """Append section 5 Key References with programmatic references."""
    section5_header = "## 5. Key References"
    return report.rstrip() + "\n\n" + section5_header + "\n\n" + references_md + "\n"


def _strip_invalid_citations(report: str, n_papers: int) -> str:
    """Remove [n] where n is not in 1..n_papers."""

    def repl(m: re.Match) -> str:
        num = int(m.group(1))
        return "" if num < 1 or num > n_papers else m.group(0)

    return re.sub(r"\[\s*(\d+)\s*\]", repl, report)


def create_report_writer_node(llm: BaseChatModel):
    """Create report writer node that closes over llm."""

    def report_writer_node(state: AgentState) -> dict[str, Any]:
        query = state.get("query") or ""
        gaps = state.get("research_gaps") or []
        hypotheses = state.get("hypotheses") or []
        papers = state.get("filtered_papers") or []
        cluster_analyses = state.get("cluster_analyses") or []
        n_papers = len(papers)
        citation_list = citation_list_text(papers)
        findings_citations_text = findings_citations_section(
            cluster_analyses=cluster_analyses,
            n_papers=n_papers,
        )
        gap_lines = []
        for g in gaps:
            citations_str = format_gap_citations(g.supporting_paper_indices, n_papers)
            parts = [
                f"- **{g.title}** ({g.gap_type.value}): {g.description}",
                citations_str,
            ]
            gap_lines.append(" ".join(parts))
        gaps_text = "\n\n".join(gap_lines)
        hypotheses_text = "\n\n".join(
            f"- **{h.title}**: {h.description} — {h.suggested_methodology}"
            for h in hypotheses
        )
        prompt = REPORT_WRITING_PROMPT.format(
            query=query,
            citation_list=citation_list,
            findings_citations_text=findings_citations_text,
            gaps_text=gaps_text,
            hypotheses_text=hypotheses_text,
            n_papers=n_papers,
        )
        resp = llm.invoke(prompt)
        report = getattr(resp, "content", str(resp))
        references_md = references_section_md(papers)
        report = _inject_references_section(report=report, references_md=references_md)
        report = _strip_invalid_citations(report=report, n_papers=n_papers)
        logger.info("Report length: %s chars", len(report))
        return {"report": report}

    return report_writer_node
