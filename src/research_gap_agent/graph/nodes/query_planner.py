"""Query planner node: decompose query into search terms. Depth/search_config come from CLI state."""

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel

from research_gap_agent.models.output import QueryPlan
from research_gap_agent.models.state import AgentState
from research_gap_agent.prompts.templates import QUERY_DECOMPOSITION_PROMPT

logger = logging.getLogger(__name__)


def create_query_planner_node(llm: BaseChatModel):
    """Create the query planner node. Outputs refined_queries only; search_config from state (CLI depth)."""

    structured_llm = llm.with_structured_output(QueryPlan)

    def query_planner_node(state: AgentState) -> dict[str, Any]:
        query = state.get("query") or ""
        prompt = QUERY_DECOMPOSITION_PROMPT.format(query=query)
        plan = structured_llm.invoke(prompt)
        depth_label = state.get("depth") or "standard"
        logger.info(
            "Query plan: %s queries, depth=%s",
            len(plan.refined_queries),
            depth_label,
        )
        return {"refined_queries": plan.refined_queries}

    return query_planner_node
