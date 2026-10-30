from __future__ import annotations

import hashlib
import logging
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

log = logging.getLogger(__name__)


class HttpClient:
    """Polite HTTP client: robots.txt check, rate limit, retry with backoff, disk cache."""

    def __init__(
        self,
        user_agent: str,
        delay: float = 2.0,
        cache_dir: Path | None = None,
        timeout: int = 15,
        max_retries: int = 3,
    ) -> None:
        self.user_agent = user_agent
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self._robots: dict[str, RobotFileParser | None] = {}
        self._last_request = 0.0

    def allowed(self, url: str) -> bool:
        parts = urlparse(url)
        base = f"{parts.scheme}://{parts.netloc}"
        if base not in self._robots:
            parser = RobotFileParser(f"{base}/robots.txt")
            try:
                parser.read()
                self._robots[base] = parser
            except Exception as exc:  # network problem reading robots.txt
                log.warning("Could not read robots.txt for %s (%s)", base, exc)
                self._robots[base] = None
        parser = self._robots[base]
        return True if parser is None else parser.can_fetch(self.user_agent, url)

    def _cache_path(self, url: str) -> Path | None:
        if not self.cache_dir:
            return None
        return self.cache_dir / f"{hashlib.sha1(url.encode()).hexdigest()}.html"

    def _throttle(self) -> None:
        wait = self.delay - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()

    def get(self, url: str) -> str:
        cached = self._cache_path(url)
        if cached and cached.exists():
            log.debug("Cache hit: %s", url)
            return cached.read_text(encoding="utf-8")

        if not self.allowed(url):
            raise PermissionError(f"robots.txt disallows fetching {url}")

        for attempt in range(1, self.max_retries + 1):
            self._throttle()
            try:
                resp = self.session.get(url, timeout=self.timeout)
                resp.raise_for_status()
                break
            except requests.RequestException as exc:
                log.warning("GET %s failed (attempt %d/%d): %s", url, attempt, self.max_retries, exc)
                if attempt == self.max_retries:
                    raise
                time.sleep(2**attempt)

        if cached:
            cached.write_text(resp.text, encoding="utf-8")
        return resp.text
