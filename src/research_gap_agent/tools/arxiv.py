"""arXiv API client (Atom XML)."""

import asyncio
import logging
import re
import sys
from urllib.parse import urlencode

import httpx

from research_gap_agent.models.paper import Paper
from research_gap_agent.tools.base import BaseAPIClient

logger = logging.getLogger(__name__)

ATOM_NS = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"
BASE_URL = "https://export.arxiv.org/api/query"


class ArxivClient(BaseAPIClient):
    """Client for arXiv API (Atom XML). Rate limit: ~1 req/3 sec."""

    def __init__(
        self,
        rate_limit_delay: float = 3.0,
        max_retries: int = 3,
    ) -> None:
        super().__init__(
            rate_limit_delay=rate_limit_delay,
            max_retries=max_retries,
        )

    def search_sync(
        self,
        query: str,
        start: int = 0,
        max_results: int = 100,
    ) -> list[Paper]:
        """Sync search for use from graph nodes. Returns [] on failure."""
        import time
        import xml.etree.ElementTree as ET

        try:
            time.sleep(self._rate_limit_delay)
            params = {
                "search_query": query,
                "start": start,
                "max_results": min(max_results, 200),
            }
            url = f"{BASE_URL}?{urlencode(params)}"
            with self._get_sync_client() as client:
                response = client.get(url)
                response.raise_for_status()
                root = ET.fromstring(response.text)
                papers = []
                for entry in root.findall(f".//{ATOM_NS}entry"):
                    p = self._entry_to_paper(entry, ATOM_NS, ARXIV_NS)
                    if p:
                        papers.append(p)
                return papers
        except Exception as e:
            logger.exception("arXiv search failed: %s", e)
            return []

    def _get_sync_client(self) -> httpx.Client:
        return httpx.Client(timeout=self._timeout, follow_redirects=True)

    async def search(
        self,
        query: str,
        start: int = 0,
        max_results: int = 100,
    ) -> list[Paper]:
        """Search arXiv; returns normalized Paper list. Returns [] on failure."""
        try:
            import xml.etree.ElementTree as ET
        except ImportError:
            logger.error("xml.etree not available")
            return []
        try:
            params = {
                "search_query": query,
                "start": start,
                "max_results": min(max_results, 200),
            }
            url = f"{BASE_URL}?{urlencode(params)}"
            client = await self._get_client()
            async with self._semaphore:
                await asyncio.sleep(self._rate_limit_delay)
            response = await client.get(url)
            response.raise_for_status()
            root = ET.fromstring(response.text)
            papers = []
            for entry in root.findall(f".//{ATOM_NS}entry"):
                p = self._entry_to_paper(entry, ATOM_NS, ARXIV_NS)
                if p:
                    papers.append(p)
            return papers
        except Exception as e:
            logger.exception("arXiv search failed: %s", e)
            return []

    @staticmethod
    def _entry_to_paper(entry, atom_ns: str, arxiv_ns: str) -> Paper | None:
        id_el = entry.find(f"{atom_ns}id")
        title_el = entry.find(f"{atom_ns}title")
        summary_el = entry.find(f"{atom_ns}summary")
        if id_el is None or id_el.text is None:
            return None
        raw_id = id_el.text.strip()
        arxiv_id = (
            raw_id.split("/abs/")[-1].split("/")[0] if "/abs/" in raw_id else raw_id
        )
        title = (
            title_el.text.strip().replace("\n", " ")
            if title_el is not None and title_el.text
            else ""
        )
        abstract = (
            summary_el.text.strip().replace("\n", " ")
            if summary_el is not None and summary_el.text
            else None
        )
        authors = []
        for author in entry.findall(f"{atom_ns}author"):
            name_el = author.find(f"{atom_ns}name")
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())
        published_el = entry.find(f"{atom_ns}published")
        year = None
        if published_el is not None and published_el.text:
            m = re.match(r"(\d{4})", published_el.text)
            if m:
                year = int(m.group(1))
        link_el = entry.find(f"{atom_ns}link[@title='pdf']")
        url = None
        if link_el is not None and link_el.get("href"):
            url = link_el.get("href")
        if not url:
            url = f"https://arxiv.org/abs/{arxiv_id}"
        return Paper(
            id=arxiv_id,
            title=title,
            abstract=abstract,
            authors=authors,
            year=year,
            citation_count=None,
            venue="arXiv",
            url=url,
            doi=None,
            source="arxiv",
        )


def main() -> int:
    """Run a quick arXiv search for standalone testing."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s %(message)s",
    )
    client = ArxivClient(rate_limit_delay=3.0)
    papers = client.search_sync(
        query="machine learning",
        start=0,
        max_results=3,
    )
    if not papers:
        print("No results or request failed.", file=sys.stderr)
        return 1
    for i, p in enumerate(papers, 1):
        print(f"{i}. [{p.id}] {p.title}")
        if p.year:
            print(f"   Year: {p.year}")
        if p.authors:
            print(f"   Authors: {', '.join(p.authors[:3])}{'...' if len(p.authors) > 3 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
