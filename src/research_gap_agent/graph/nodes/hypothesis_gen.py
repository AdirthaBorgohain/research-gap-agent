"""Hypothesis generator node: per-gap hypotheses."""

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel

from research_gap_agent.models.output import HypothesisList
from research_gap_agent.models.state import AgentState
from research_gap_agent.prompts.templates import HYPOTHESIS_GENERATION_PROMPT

logger = logging.getLogger(__name__)


def create_hypothesis_gen_node(llm: BaseChatModel, hypothesis_temperature: float = 0.5):
    """Create hypothesis generator node that closes over llm. Uses higher temperature for more creative hypotheses."""

    structured_llm = llm.bind(
        temperature=hypothesis_temperature
    ).with_structured_output(HypothesisList)

    def hypothesis_gen_node(state: AgentState) -> dict[str, Any]:
        gaps = state.get("research_gaps") or []
        if not gaps:
            return {"hypotheses": []}
        gaps_text = "\n\n".join(
            f"- {g.title}: {g.description} (type={g.gap_type.value})" for g in gaps
        )
        prompt = HYPOTHESIS_GENERATION_PROMPT.format(gaps_text=gaps_text)
        try:
            out = structured_llm.invoke(prompt)
            hypotheses = getattr(out, "hypotheses", []) or []
        except Exception as e:
            logger.warning("Structured hypothesis generation failed: %s", e)
            hypotheses = []
        logger.info("Hypothesis gen: %s hypotheses", len(hypotheses))
        return {"hypotheses": hypotheses}

    return hypothesis_gen_node
