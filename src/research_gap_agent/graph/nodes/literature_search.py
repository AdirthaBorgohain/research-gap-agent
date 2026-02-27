"""Literature search: fan-out edge and search_api node."""

import logging
from typing import Any

from langgraph.types import Send

from research_gap_agent.models.paper import Paper
from research_gap_agent.models.state import AgentState
from research_gap_agent.tools.arxiv import ArxivClient
from research_gap_agent.tools.openalex import OpenAlexClient
from research_gap_agent.tools.semantic_scholar import SemanticScholarClient

logger = logging.getLogger(__name__)

# Max papers per API per query to avoid huge responses
PER_QUERY_LIMIT = 50


def fan_out_search_edges(state: AgentState) -> list[Send]:
    """Return one Send per (api, query) for parallel search."""
    queries = state.get("refined_queries") or []
    config = state.get("search_config") or {}
    api_list = state.get("literature_apis") or []
    max_per_source = min(config.get("max_papers", 80) // max(len(queries), 1), 100)
    limit = min(max_per_source, PER_QUERY_LIMIT)
    sends = []
    for q in queries:
        for api_name in api_list:
            sends.append(
                Send(
                    "search_api",
                    {
                        "_current_search_task": {
                            "api": api_name,
                            "query": q,
                            "limit": limit,
                        }
                    },
                )
            )
    return sends


def create_search_api_node(
    enabled_clients: dict[str, SemanticScholarClient | OpenAlexClient | ArxivClient],
):
    """Create search_api node that closes over enabled API clients (sync)."""

    def search_api_node(state: AgentState) -> dict[str, Any]:
        task = state.get("_current_search_task") or {}
        api = task.get("api", "")
        query = task.get("query", "")
        limit = task.get("limit", PER_QUERY_LIMIT)
        papers: list[Paper] = []
        if api in enabled_clients:
            client = enabled_clients[api]
            if api == "semantic_scholar":
                papers = client.search_sync(query=query, limit=limit)
            elif api == "openalex":
                papers = client.search_sync(query=query, per_page=limit)
            elif api == "arxiv":
                papers = client.search_sync(query=query, max_results=limit)
        logger.info(
            "search_api %s: %s papers for query=%s", api, len(papers), query[:50]
        )
        return {
            "search_results": papers,
            "_progress": {
                "phase": "search_api",
                "api": api,
                "query": (query or "")[:60],
                "count": len(papers),
            },
        }

    return search_api_node
