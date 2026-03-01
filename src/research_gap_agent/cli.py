"""CLI for the Research Gap Finding Agent."""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from research_gap_agent.config import LLMProvider, Settings, get_runtime_config
from research_gap_agent.graph.builder import build_graph

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logger = logging.getLogger(__name__)


def _configure_logging(log_path: Path) -> None:
    """Configure root logger with run-specific log file only (no console)."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Research Gap Finding Agent: identify research gaps from literature.",
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Research domain or question",
    )
    parser.add_argument(
        "--depth",
        "-d",
        choices=["quick", "standard", "deep"],
        default="standard",
        help="Search depth: quick (few papers), standard, deep (default: standard)",
    )
    parser.add_argument(
        "--provider",
        "-p",
        choices=["openai", "anthropic"],
        default=None,
        help="LLM provider (overrides config.yaml; openai or anthropic)",
    )
    parser.add_argument(
        "--config",
        "-c",
        metavar="PATH",
        default=os.environ.get("CONFIG_PATH", "config.yaml"),
        help="Path to config.yaml (default: config.yaml or CONFIG_PATH env)",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Do not write the JSON output file (default: JSON is written)",
    )
    return parser.parse_args()


def _slug_and_timestamp(query: str) -> tuple[str, str]:
    """Return (slug, timestamp) for this run (single source of truth)."""
    slug = (
        re.sub(r"[^\w\s-]", "", query.lower())[:40].strip().replace(" ", "_")
        or "report"
    )
    slug = re.sub(r"_+", "_", slug)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return slug, timestamp


def _paths_for_run(query: str, depth: str = "standard") -> tuple[Path, Path]:
    """Return (report_path, log_path) for this run with a single timestamp."""
    slug, timestamp = _slug_and_timestamp(query)
    Path("outputs").mkdir(parents=True, exist_ok=True)
    report_path = Path("outputs") / f"{depth}_report_{slug}_{timestamp}.md"
    log_path = Path("logs") / f"run_{slug}_{timestamp}.log"
    return report_path, log_path


def _dump_list_for_json(items: list[Any], /) -> list[Any]:
    """Serialize a list of Pydantic models or plain values to JSON-safe structures."""
    out: list[Any] = []
    for item in items:
        if hasattr(item, "model_dump"):
            out.append(item.model_dump(mode="json"))
        else:
            out.append(item)
    return out


def _build_report_export(state: dict[str, Any], report_path: Path) -> dict[str, Any]:
    """Build a JSON-serializable export dict from final agent state."""
    papers = state.get("filtered_papers") or []
    gaps = state.get("research_gaps") or []
    hypotheses = state.get("hypotheses") or []
    clusters = state.get("topic_clusters") or []
    analyses = state.get("cluster_analyses") or []
    refined = state.get("refined_queries") or []
    return {
        "meta": {
            "query": state.get("query") or "",
            "depth": state.get("depth") or "standard",
            "timestamp": datetime.now().isoformat(),
            "report_path": str(report_path) if report_path else "",
        },
        "papers": _dump_list_for_json(papers) if isinstance(papers, list) else [],
        "research_gaps": _dump_list_for_json(gaps) if isinstance(gaps, list) else [],
        "hypotheses": _dump_list_for_json(hypotheses)
        if isinstance(hypotheses, list)
        else [],
        "topic_clusters": (
            _dump_list_for_json(clusters) if isinstance(clusters, list) else []
        ),
        "cluster_analyses": (
            _dump_list_for_json(analyses) if isinstance(analyses, list) else []
        ),
        "refined_queries": refined if isinstance(refined, list) else [],
    }


def _print_config_banner(
    runtime_config: Any,
    search_config: dict,
    depth_label: str,
) -> None:
    """Print LLM, literature APIs, and depth to stdout."""
    provider = getattr(
        runtime_config.llm_provider, "value", str(runtime_config.llm_provider)
    )
    model = getattr(runtime_config, "llm_model", "")
    print(f"LLM: {provider} / {model}", flush=True)
    apis = getattr(runtime_config, "literature_apis", []) or []
    print(f"Literature APIs: {', '.join(apis)}", flush=True)
    min_p = search_config.get("min_papers", 0)
    max_p = search_config.get("max_papers", 0)
    max_iter = search_config.get("max_search_iterations", 0)
    min_c = search_config.get("min_clusters", 3)
    max_c = search_config.get("max_clusters", 7)
    rel = search_config.get("relevance_threshold", 0.4)
    print(
        f"Depth: {depth_label} ({min_p}–{max_p} papers, up to {max_iter} iterations, clusters: {min_c}–{max_c})",
        flush=True,
    )
    print(f"Relevance threshold: {rel}", flush=True)
    print(flush=True)


def _print_node_update(node_name: str, update: dict[str, Any]) -> None:
    """Print human-readable formatted section to stdout for selected nodes."""
    progress = update.get("_progress") or {}

    if (
        node_name == "literature_search"
        and progress.get("phase") == "literature_search"
    ):
        apis = progress.get("apis") or []
        n_queries = progress.get("n_queries", 0)
        print(
            f"Running literature search (APIs: {', '.join(apis)}; {n_queries} queries).",
            flush=True,
        )
        return
    if node_name == "search_api" and progress.get("phase") == "search_api":
        api = progress.get("api", "?")
        query = (progress.get("query") or "")[:100]
        count = progress.get("count", 0)
        print(f'  → {api}: {count} papers for "{query}"', flush=True)
        return
    if node_name == "refine_queries":
        it = update.get("search_iteration")
        if it is not None:
            print(f"Refining queries (iteration {it}).", flush=True)
        return
    if node_name == "analyze_cluster":
        analyses = update.get("cluster_analyses") or []
        if analyses:
            label = getattr(analyses[0], "cluster_label", str(analyses[0])[:100])
            print(f"  → Cluster analyzed: {label}", flush=True)
        return
    if node_name == "report_writer":
        report = update.get("report") or ""
        print(f"Report generated ({len(report)} chars).", flush=True)
        return

    if node_name == "query_planner":
        queries = update.get("refined_queries") or []
        if not queries:
            return
        print("\n--- Search queries ---", flush=True)
        print(f"Search queries generated ({len(queries)}):", flush=True)
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}", flush=True)
        return
    if node_name == "paper_processor":
        papers = update.get("filtered_papers") or []
        if not papers:
            return
        print("\n--- Papers loaded ---", flush=True)
        print(f"Papers loaded: {len(papers)} papers", flush=True)
        for i, p in enumerate(papers[:10], 1):
            title = getattr(p, "title", str(p))[:100]
            year = getattr(p, "year", None)
            yr = f" ({year})" if year else ""
            print(f"  {i}. {title}{yr}", flush=True)
        if len(papers) > 10:
            print(f"  ... and {len(papers) - 10} more", flush=True)
        return
    if node_name == "topic_clustering":
        clusters = update.get("topic_clusters") or []
        if not clusters:
            return
        print("\n--- Topic clusters ---", flush=True)
        print(f"Topic clusters ({len(clusters)}):", flush=True)
        for c in clusters:
            label = getattr(c, "label", str(c))
            desc = (getattr(c, "description", "") or "")[:100]
            print(f"  • {label}: {desc}", flush=True)
        return
    if node_name == "gap_finder":
        gaps = update.get("research_gaps") or []
        if not gaps:
            return
        print("\n--- Research gaps identified ---", flush=True)
        print(f"Research gaps identified ({len(gaps)}):", flush=True)
        for g in gaps:
            title = getattr(g, "title", str(g))[:100]
            gap_type = getattr(g, "gap_type", None)
            gt = gap_type.value if hasattr(gap_type, "value") else str(gap_type)
            desc = (getattr(g, "description", "") or "")[:100]
            print(f"  • {title} [{gt}]", flush=True)
            if desc:
                print(f"    {desc}", flush=True)
        return
    if node_name == "hypothesis_gen":
        hypotheses = update.get("hypotheses") or []
        if not hypotheses:
            return
        print("\n--- Hypotheses to explore ---", flush=True)
        print(f"Hypotheses to explore ({len(hypotheses)}):", flush=True)
        for h in hypotheses:
            title = getattr(h, "title", str(h))[:100]
            methodology = (getattr(h, "suggested_methodology", "") or "")[:100]
            print(f"  • {title}", flush=True)
            if methodology:
                print(f"    — {methodology}", flush=True)
        return
    print(f"Completed: {node_name}", flush=True)


def main() -> int:
    args = parse_args()
    query = (args.query or "").strip()
    if not query:
        print("Error: provide a query", file=sys.stderr)
        return 1

    settings = Settings()
    provider_override = (
        LLMProvider(args.provider) if args.provider is not None else None
    )
    runtime_config = get_runtime_config(
        config_path=args.config,
        settings=settings,
        llm_provider_override=provider_override,
    )

    out_path, log_path = _paths_for_run(query=query, depth=args.depth)
    _configure_logging(log_path=log_path)

    search_config = runtime_config.depth_presets[args.depth]
    initial_state = {
        "query": query,
        "depth": args.depth,
        "literature_apis": runtime_config.literature_apis,
        "search_config": search_config,
        "search_iteration": 0,
    }

    graph = build_graph(runtime_config=runtime_config)

    print("Research Gap Agent — Running for:", query, flush=True)
    print("─" * 50, flush=True)
    _print_config_banner(
        runtime_config=runtime_config,
        search_config=search_config,
        depth_label=args.depth,
    )
    logger.info("Running research gap agent...")
    final_state: dict[str, Any] = {}
    try:
        step = 0
        print("Running pipeline...", flush=True)
        for mode, chunk in graph.stream(
            initial_state,
            stream_mode=["updates", "values"],
        ):
            if mode == "updates":
                for node_name, update in chunk.items():
                    _print_node_update(node_name=node_name, update=update)
                continue

            if mode == "values":
                final_state = chunk
                step += 1
                logger.info("Completed step %s", step)
                continue
    except Exception as e:
        logger.error("Error: %s", e)
        return 1
    logger.info("Done.")

    report = final_state.get("report") or ""
    gaps = final_state.get("research_gaps") or []

    text = report or "# Research Gap Report\n\nNo report generated."
    out_path.write_text(text, encoding="utf-8")
    logger.info("Report written to %s", out_path)
    print("\nReport saved to:", out_path, flush=True)

    if not args.no_json:
        json_path = out_path.with_suffix(".json")
        export_data = _build_report_export(state=final_state, report_path=out_path)
        json_path.write_text(
            json.dumps(export_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("JSON written to %s", json_path)
        print("JSON saved to:", json_path, flush=True)

    for g in gaps[:15] if gaps else []:
        title = getattr(g, "title", str(g))
        gap_type = getattr(g, "gap_type", None)
        gt = gap_type.value if hasattr(gap_type, "value") else str(gap_type)
        n_papers = len(getattr(g, "supporting_paper_indices", []))
        logger.info(
            "Gap: %s | type=%s | papers=%s",
            title[:100] if isinstance(title, str) else title,
            gt,
            n_papers,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
