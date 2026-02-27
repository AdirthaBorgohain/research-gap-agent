"""Build the research gap agent LangGraph."""

from langgraph.graph import END, START, StateGraph

from research_gap_agent.config import RuntimeConfig, get_runtime_config, Settings
from research_gap_agent.graph.nodes.deep_analysis import (
    create_analyze_cluster_node,
    fan_out_analyze_edges,
)
from research_gap_agent.graph.nodes.gap_finder import create_gap_finder_node
from research_gap_agent.graph.nodes.hypothesis_gen import create_hypothesis_gen_node
from research_gap_agent.graph.nodes.literature_search import (
    create_search_api_node,
    fan_out_search_edges,
)
from research_gap_agent.graph.nodes.paper_processor import create_paper_processor_node
from research_gap_agent.graph.nodes.query_planner import create_query_planner_node
from research_gap_agent.graph.nodes.refine_queries import refine_queries_node
from research_gap_agent.graph.nodes.report_writer import create_report_writer_node
from research_gap_agent.graph.nodes.topic_clustering import create_topic_clustering_node
from research_gap_agent.llm import get_llm
from research_gap_agent.models.state import AgentState
from research_gap_agent.tools.arxiv import ArxivClient
from research_gap_agent.tools.openalex import OpenAlexClient
from research_gap_agent.tools.semantic_scholar import SemanticScholarClient


def _coverage_route(state: AgentState) -> str:
    """Route after paper_processor: refine_queries or topic_clustering."""
    config = state.get("search_config") or {}
    min_papers = config.get("min_papers", 30)
    max_iterations = config.get("max_search_iterations", 2)
    iteration = state.get("search_iteration") or 0
    filtered = state.get("filtered_papers") or []
    if len(filtered) < min_papers and iteration < max_iterations:
        return "refine_queries"
    return "topic_clustering"


def build_graph(runtime_config: RuntimeConfig | None = None):
    """Build and compile the research gap agent graph."""
    rc = runtime_config or get_runtime_config(settings=Settings())
    llm = get_llm(rc)
    enabled_clients: dict[str, SemanticScholarClient | OpenAlexClient | ArxivClient] = {}
    if "semantic_scholar" in rc.literature_apis:
        enabled_clients["semantic_scholar"] = SemanticScholarClient(
            api_key=rc.semantic_scholar_api_key,
            rate_limit_delay=0.01 if rc.semantic_scholar_api_key else 1.0,
        )
    if "openalex" in rc.literature_apis:
        enabled_clients["openalex"] = OpenAlexClient(api_key=rc.openalex_api_key)
    if "arxiv" in rc.literature_apis:
        enabled_clients["arxiv"] = ArxivClient(rate_limit_delay=3.0)

    query_planner = create_query_planner_node(llm)
    search_api = create_search_api_node(enabled_clients=enabled_clients)
    paper_processor = create_paper_processor_node(llm)
    topic_clustering = create_topic_clustering_node(llm)
    analyze_cluster = create_analyze_cluster_node(llm)
    gap_finder = create_gap_finder_node(llm)
    hypothesis_gen = create_hypothesis_gen_node(
        llm, hypothesis_temperature=rc.hypothesis_temperature
    )
    report_writer = create_report_writer_node(llm)

    def literature_search_progress(state: AgentState) -> dict:
        """Return progress payload for CLI; no state change for graph logic."""
        apis = state.get("literature_apis") or []
        queries = state.get("refined_queries") or []
        return {
            "_progress": {
                "phase": "literature_search",
                "apis": list(apis),
                "n_queries": len(queries),
            }
        }

    builder = StateGraph(AgentState)

    builder.add_node("query_planner", query_planner)
    builder.add_node("literature_search", literature_search_progress)
    builder.add_node("search_api", search_api)
    builder.add_node("paper_processor", paper_processor)
    builder.add_node("refine_queries", refine_queries_node)
    builder.add_node("topic_clustering", topic_clustering)
    builder.add_node("analyze_cluster", analyze_cluster)
    builder.add_node("gap_finder", gap_finder)
    builder.add_node("hypothesis_gen", hypothesis_gen)
    builder.add_node("report_writer", report_writer)

    builder.add_edge(START, "query_planner")
    builder.add_edge("query_planner", "literature_search")
    builder.add_conditional_edges("literature_search", fan_out_search_edges)
    builder.add_edge("search_api", "paper_processor")
    builder.add_conditional_edges(
        "paper_processor",
        _coverage_route,
        {"refine_queries": "refine_queries", "topic_clustering": "topic_clustering"},
    )
    builder.add_edge("refine_queries", "literature_search")
    builder.add_conditional_edges("topic_clustering", fan_out_analyze_edges)
    builder.add_edge("analyze_cluster", "gap_finder")
    builder.add_edge("gap_finder", "hypothesis_gen")
    builder.add_edge("hypothesis_gen", "report_writer")
    builder.add_edge("report_writer", END)

    return builder.compile()
