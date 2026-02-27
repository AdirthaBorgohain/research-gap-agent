"""OpenAlex API client."""

import logging
import sys
from urllib.parse import urlencode

from research_gap_agent.models.paper import Paper
from research_gap_agent.tools.base import BaseAPIClient

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openalex.org"
WORKS_PATH = "/works"


class OpenAlexClient(BaseAPIClient):
    """Client for OpenAlex works search. Requires API key (free tier). Rate limit: 100 req/s."""

    def __init__(
        self,
        api_key: str | None = None,
        rate_limit_delay: float = 0.02,
        max_retries: int = 3,
    ) -> None:
        super().__init__(
            rate_limit_delay=rate_limit_delay,
            max_retries=max_retries,
        )
        self._api_key = api_key
        self._headers = {"User-Agent": "ResearchGapAgent/1.0"}
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

    def search_sync(
        self,
        query: str,
        per_page: int = 200,
        page: int = 1,
    ) -> list[Paper]:
        """Sync search for use from graph nodes. Returns [] on failure."""
        try:
            params = {
                "search": query,
                "per-page": min(per_page, 200),
                "page": page,
            }
            url = f"{BASE_URL}{WORKS_PATH}?{urlencode(params)}"
            result = self._request_sync(
                "GET",
                url,
                headers=self._headers,
            )
            if not isinstance(result, dict):
                return []
            results = result.get("results") or []
            return [self._to_paper(item) for item in results]
        except Exception as e:
            logger.exception("OpenAlex search failed: %s", e)
            return []

    async def search(
        self,
        query: str,
        per_page: int = 200,
        page: int = 1,
    ) -> list[Paper]:
        """Search works; returns normalized Paper list. Returns [] on failure."""
        try:
            params = {
                "search": query,
                "per-page": min(per_page, 200),
                "page": page,
            }
            url = f"{BASE_URL}{WORKS_PATH}?{urlencode(params)}"
            result = await self._request(
                "GET",
                url,
                headers=self._headers,
            )
            if not isinstance(result, dict):
                return []
            results = result.get("results") or []
            return [self._to_paper(item) for item in results]
        except Exception as e:
            logger.exception("OpenAlex search failed: %s", e)
            return []

    @staticmethod
    def _to_paper(item: dict) -> Paper:
        authors = []
        for a in item.get("authorships") or []:
            author = a.get("author") if isinstance(a, dict) else None
            if isinstance(author, dict):
                display = author.get("display_name")
                if display:
                    authors.append(display)
        year = item.get("publication_year")
        if isinstance(year, str) and year.isdigit():
            year = int(year)
        abstract = item.get("abstract")
        if abstract is None and item.get("abstract_inverted_index"):
            abstract = _inverted_index_to_text(item.get("abstract_inverted_index"))
        return Paper(
            id=item.get("id") or "",
            title=item.get("title") or "",
            abstract=abstract,
            authors=authors,
            year=year if isinstance(year, int) else None,
            citation_count=item.get("cited_by_count"),
            venue=(
            (item.get("primary_location") or {}).get("source") or {}
        ).get("display_name"),
            url=item.get("doi") and f"https://doi.org/{item.get('doi').replace('https://doi.org/', '')}"
            or item.get("id"),
            doi=item.get("doi") if isinstance(item.get("doi"), str) else None,
            source="openalex",
        )


def _inverted_index_to_text(inv: dict | None) -> str | None:
    """Convert OpenAlex abstract_inverted_index to plain text."""
    if not inv or not isinstance(inv, dict):
        return None
    pairs: list[tuple[int, str]] = []
    for word, positions in inv.items():
        for pos in positions:
            pairs.append((pos, word))
    pairs.sort(key=lambda x: x[0])
    return " ".join(p for _, p in pairs)


def main() -> int:
    """Run a quick OpenAlex search for standalone testing."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s %(message)s",
    )
    client = OpenAlexClient()
    papers = client.search_sync(query="machine learning", per_page=3, page=1)
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
