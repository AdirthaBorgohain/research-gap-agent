"""Utility modules."""

from research_gap_agent.utils.citations import (
    citation_list_text,
    findings_citations_section,
    format_gap_citations,
    references_section_md,
    validate_citation_keys,
)
from research_gap_agent.utils.dedup import is_duplicate_title

__all__ = [
    "citation_list_text",
    "findings_citations_section",
    "format_gap_citations",
    "is_duplicate_title",
    "references_section_md",
    "validate_citation_keys",
]
