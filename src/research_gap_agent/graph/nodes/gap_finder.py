"""Gap finder node: cross-cluster synthesis into research gaps."""

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel

from research_gap_agent.models.output import ResearchGapList
from research_gap_agent.models.state import AgentState
from research_gap_agent.prompts.templates import GAP_FINDER_PROMPT
from research_gap_agent.utils.citations import citation_list_text

logger = logging.getLogger(__name__)


def create_gap_finder_node(llm: BaseChatModel):
    """Create gap finder node that closes over llm."""

    structured_llm = llm.with_structured_output(ResearchGapList)

    def gap_finder_node(state: AgentState) -> dict[str, Any]:
        analyses = state.get("cluster_analyses") or []
        query = state.get("query") or ""
        if not analyses:
            return {"research_gaps": []}
        lines = []
        for a in analyses:
            findings_str = "; ".join(f.text for f in a.findings[:5])
            lines.append(
                f"## {a.cluster_label}\n"
                f"Methodologies: {', '.join(a.methodologies[:5])}\n"
                f"Findings: {findings_str}\n"
                f"Limitations: {'; '.join(a.limitations[:5])}\n"
                f"Trend: {a.trend}; Contradictions: {'; '.join(a.contradictions[:3])}"
            )
        cluster_analyses_text = "\n\n".join(lines)
        papers = state.get("filtered_papers") or []
        citation_list = citation_list_text(papers)
        prompt = GAP_FINDER_PROMPT.format(
            cluster_analyses_text=cluster_analyses_text,
            citation_list=citation_list,
            query=query,
        )
        try:
            out = structured_llm.invoke(prompt)
            gaps = getattr(out, "gaps", []) or []
        except Exception as e:
            logger.warning("Structured gap finding failed: %s", e)
            gaps = []
        logger.info("Gap finder: %s gaps", len(gaps))
        return {"research_gaps": gaps}

    return gap_finder_node
