"""Semantic Scholar API client."""

import logging
import sys
from urllib.parse import urlencode

from research_gap_agent.models.paper import Paper
from research_gap_agent.tools.base import BaseAPIClient

logger = logging.getLogger(__name__)

BASE_URL = "https://api.semanticscholar.org/graph/v1"
FIELDS = "paperId,title,abstract,year,authors,citationCount,externalIds,url"


class SemanticScholarClient(BaseAPIClient):
    """Client for Semantic Scholar paper search. Rate limit: 1 req/s without key, 100/s with key."""

    def __init__(
        self,
        api_key: str | None = None,
        rate_limit_delay: float = 1.0,
        max_retries: int = 3,
    ) -> None:
        super().__init__(
            rate_limit_delay=0.01 if api_key else rate_limit_delay,
            max_retries=max_retries,
        )
        self._api_key = api_key
        self._headers = {"x-api-key": api_key} if api_key else {}

    def search_sync(
        self,
        query: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Paper]:
        """Sync search for use from graph nodes. Returns [] on failure."""
        try:
            params = {
                "query": query,
                "limit": min(limit, 100),
                "offset": offset,
                "fields": FIELDS,
            }
            url = f"{BASE_URL}/paper/search?{urlencode(params)}"
            result = self._request_sync(
                "GET",
                url,
                headers=self._headers,
            )
            if not isinstance(result, dict):
                return []
            data = result.get("data") or []
            return [self._to_paper(item) for item in data]
        except Exception as e:
            logger.exception("Semantic Scholar search failed: %s", e)
            return []

    @staticmethod
    def _to_paper(item: dict) -> Paper:
        authors = []
        for a in item.get("authors") or []:
            if isinstance(a, dict) and "name" in a:
                authors.append(a["name"])
            elif isinstance(a, str):
                authors.append(a)
        external = item.get("externalIds") or {}
        doi = external.get("DOI") if isinstance(external, dict) else None
        if isinstance(doi, list):
            doi = doi[0] if doi else None
        return Paper(
            id=item.get("paperId") or "",
            title=item.get("title") or "",
            abstract=item.get("abstract") or None,
            authors=authors,
            year=item.get("year"),
            citation_count=item.get("citationCount"),
            venue=None,
            url=item.get("url"),
            doi=doi,
            source="semantic_scholar",
        )


def main() -> int:
    """Run a quick Semantic Scholar search for standalone testing."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s %(message)s",
    )
    client = SemanticScholarClient()
    papers = client.search_sync(query="machine learning", limit=3, offset=0)
    if not papers:
        print("No results or request failed.", file=sys.stderr)
        return 1
    for i, p in enumerate(papers, 1):
        print(f"{i}. [{p.id}] {p.title}")
        if p.year:
            print(f"   Year: {p.year}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
