"""Deduplication helpers: title normalization and fuzzy matching."""

import re
from difflib import SequenceMatcher


def normalize_title(title: str) -> str:
    """Normalize a paper title for comparison: lowercase, collapse whitespace, remove punctuation."""
    if not title or not isinstance(title, str):
        return ""
    s = title.lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s]", "", s)
    return s.strip()


def title_similarity(a: str, b: str) -> float:
    """Return similarity between two titles in [0, 1] using normalized text."""
    na, nb = normalize_title(a), normalize_title(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def is_duplicate_title(title_a: str, title_b: str, threshold: float = 0.9) -> bool:
    """Return True if the two titles are likely the same paper (above threshold)."""
    return title_similarity(title_a, title_b) >= threshold
