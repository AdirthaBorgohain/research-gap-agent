"""Base API client with rate limiting and retry."""

import logging
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)


def _do_request_sync(
    method: str,
    url: str,
    rate_limit_delay: float,
    max_retries: int,
    timeout: float,
    **kwargs: Any,
) -> dict | list:
    """Sync request with rate limiting and retry (for use from sync nodes)."""
    time.sleep(rate_limit_delay)
    last_exc: Exception | None = None
    with httpx.Client(timeout=timeout) as client:
        for attempt in range(max_retries):
            try:
                response = client.request(method=method, url=url, **kwargs)
                if response.status_code == 429:
                    wait = 2**attempt * 5
                    logger.warning(
                        "Rate limited (429), retry in %s s (attempt %s/%s)",
                        wait,
                        attempt + 1,
                        max_retries,
                    )
                    time.sleep(wait)
                    continue
                if response.status_code >= 500:
                    wait = 2**attempt * 2
                    logger.warning(
                        "Server error %s, retry in %s s (attempt %s/%s)",
                        response.status_code,
                        wait,
                        attempt + 1,
                        max_retries,
                    )
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                last_exc = e
                if e.response.status_code in (429, 500, 502, 503, 504):
                    time.sleep(2**attempt * 2)
                    continue
                raise
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exc = e
                time.sleep(2**attempt * 2)
        if last_exc:
            raise last_exc
        return {}
    return {}


class BaseAPIClient:
    """HTTP client with rate limiting and retry."""

    def __init__(
        self,
        rate_limit_delay: float = 1.0,
        max_retries: int = 3,
        timeout: float = 30.0,
    ) -> None:
        self._rate_limit_delay = rate_limit_delay
        self._max_retries = max_retries
        self._timeout = timeout

    def _request_sync(self, method: str, url: str, **kwargs: Any) -> dict | list:
        """Sync request for use from sync graph nodes."""
        return _do_request_sync(
            method=method,
            url=url,
            rate_limit_delay=self._rate_limit_delay,
            max_retries=self._max_retries,
            timeout=self._timeout,
            **kwargs,
        )
