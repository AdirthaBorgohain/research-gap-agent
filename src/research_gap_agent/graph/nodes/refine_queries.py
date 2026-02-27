"""Refine queries node: increment search iteration for coverage loop."""

from typing import Any

from research_gap_agent.models.state import AgentState


def refine_queries_node(state: AgentState) -> dict[str, Any]:
    """Increment search iteration; refined_queries stay the same for retry."""
    current = state.get("search_iteration") or 0
    return {"search_iteration": current + 1}
