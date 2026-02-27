"""Citation helpers: build citation list text and references section from filtered_papers."""

from research_gap_agent.models.output import ClusterAnalysis
from research_gap_agent.models.paper import Paper


def citation_list_text(papers: list[Paper]) -> str:
    """Numbered list for prompts: '1. Title (Year)\\n2. Title (Year)\\n...'."""
    lines = []
    for i, p in enumerate(papers, start=1):
        year = p.year if p.year is not None else "n.d."
        lines.append(f"{i}. {p.title} ({year})")
    return "\n".join(lines)


def references_section_md(papers: list[Paper]) -> str:
    """Markdown references section: one line per paper with [key] Title (Year). URL or DOI."""
    lines = []
    for i, p in enumerate(papers, start=1):
        year = p.year if p.year is not None else "n.d."
        link = p.url or (f"https://doi.org/{p.doi}" if p.doi else "")
        suffix = f" {link}" if link else ""
        lines.append(f"- [{i}] {p.title} ({year}).{suffix}")
    return "\n".join(lines)


def validate_citation_keys(keys: list[int], n_papers: int) -> list[int]:
    """Return only keys in 1..n_papers, preserving order."""
    return [k for k in keys if 1 <= k <= n_papers]


def format_gap_citations(supporting_paper_indices: list[int], n_papers: int) -> str:
    """Format as 'Supporting citations: [1], [5], [12]' for prompts."""
    valid = validate_citation_keys(supporting_paper_indices, n_papers)
    if not valid:
        return "Supporting citations: (none)"
    return "Supporting citations: " + ", ".join(f"[{k}]" for k in sorted(valid))


def findings_citations_section(
    cluster_analyses: list[ClusterAnalysis], n_papers: int
) -> str:
    """Format findings with their citation keys for the report prompt (one line per finding)."""
    lines = []
    for analysis in cluster_analyses:
        label = analysis.cluster_label
        for f in analysis.findings:
            valid_keys = validate_citation_keys(f.paper_indices, n_papers)
            keys_str = ", ".join(f"[{k}]" for k in sorted(valid_keys)) if valid_keys else "(cluster-level)"
            lines.append(f'{label}: "{f.text[:200]}{"..." if len(f.text) > 200 else ""}" {keys_str}')
    return "\n".join(lines) if lines else "(No findings with citations)"
