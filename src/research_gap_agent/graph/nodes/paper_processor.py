"""Paper processor: dedup, relevance scoring, filter."""

import json
import logging
from typing import Any

from langchain_core.language_models import BaseChatModel

from research_gap_agent.models.paper import Paper
from research_gap_agent.models.state import AgentState
from research_gap_agent.prompts.templates import RELEVANCE_SCORING_PROMPT
from research_gap_agent.utils.dedup import is_duplicate_title

logger = logging.getLogger(__name__)

# Batch size for LLM relevance scoring to avoid token limits
RELEVANCE_BATCH_SIZE = 20


def _deduplicate(papers: list[Paper]) -> list[Paper]:
    """Deduplicate by DOI first, then by fuzzy title match."""
    seen_dois: set[str] = set()
    seen_titles: list[tuple[str, int]] = []  # (normalized hint, index in result)
    result: list[Paper] = []
    for p in papers:
        if p.doi:
            d = (p.doi or "").lower().strip()
            if d and d in seen_dois:
                continue
            if d:
                seen_dois.add(d)
        keep = True
        for prev_title, _ in seen_titles:
            if is_duplicate_title(p.title, prev_title, threshold=0.9):
                keep = False
                break
        if not keep:
            continue
        if p.title:
            seen_titles.append((p.title, len(result)))
        result.append(p)
    return result


def create_paper_processor_node(llm: BaseChatModel):
    """Create paper processor node that closes over llm."""

    def paper_processor_node(state: AgentState) -> dict[str, Any]:
        query = state.get("query") or ""
        config = state.get("search_config") or {}
        max_papers = config.get("max_papers", 80)
        relevance_threshold = config.get("relevance_threshold", 0.4)
        raw = state.get("search_results") or []
        logger.info("Total papers from APIs: %s", len(raw))
        papers = _deduplicate(raw)
        logger.info("After dedup: %s papers (from %s)", len(papers), len(raw))
        if not papers:
            return {"filtered_papers": []}
        # Build text for relevance scoring in batches
        scored: list[Paper] = []
        for i in range(0, len(papers), RELEVANCE_BATCH_SIZE):
            batch = papers[i : i + RELEVANCE_BATCH_SIZE]
            lines = []
            for j, p in enumerate(batch):
                idx = i + j
                ab = (p.abstract or "")[:800]
                lines.append(f"{idx}. {p.title} | {ab}")
            papers_text = "\n".join(lines)
            prompt = RELEVANCE_SCORING_PROMPT.format(
                query=query,
                papers_text=papers_text,
            )
            try:
                resp = llm.invoke(prompt)
                content = resp.content if hasattr(resp, "content") else str(resp)
                if isinstance(content, str) and content.strip().startswith("{"):
                    scores = json.loads(content)
                else:
                    scores = {}
            except Exception as e:
                logger.warning("Relevance scoring failed: %s", e)
                scores = {str(k): 0.7 for k in range(i, min(i + len(batch), len(papers)))}
            for j, p in enumerate(batch):
                idx = i + j
                key = str(idx)
                score = float(scores.get(key, 0.5))
                p_copy = p.model_copy(update={"relevance_score": score})
                scored.append(p_copy)
        scored.sort(key=lambda x: (x.relevance_score or 0), reverse=True)
        filtered = [p for p in scored if (p.relevance_score or 0) >= relevance_threshold]
        filtered = filtered[:max_papers]
        logger.info("Filtered: %s papers (threshold=%.2f)", len(filtered), relevance_threshold)
        titles_preview = [p.title[:60] for p in filtered[:20]]
        logger.info("Papers kept (first %s): %s", len(titles_preview), titles_preview)
        return {"filtered_papers": filtered}

    return paper_processor_node
