from __future__ import annotations

import datetime as dt
import json
import logging
import re
from pathlib import Path

from bs4 import BeautifulSoup

from ..models import MatchResult
from ..utils import slugify
from .base import BaseScraper

log = logging.getLogger(__name__)
SCORE_RE = re.compile(r"(\d+)\s*[-\u2013:]\s*(\d+)")


class HtmlScraper(BaseScraper):
    """Config-driven scraper: URLs and CSS selectors live in a JSON file (see config/)."""

    def __init__(self, http, config: dict) -> None:
        self.http = http
        self.cfg = config

    @classmethod
    def from_file(cls, http, path: str | Path) -> "HtmlScraper":
        return cls(http, json.loads(Path(path).read_text(encoding="utf-8")))

    def team_results(self, team: str) -> list[MatchResult]:
        url = self.cfg["results_url"].format(team_slug=slugify(team))
        return self._parse(self.http.get(url))

    def head_to_head(self, home: str, away: str) -> list[MatchResult]:
        url = self.cfg["h2h_url"].format(home_slug=slugify(home), away_slug=slugify(away))
        return self._parse(self.http.get(url))

    # -- parsing -----------------------------------------------------------------
    def _parse(self, html: str) -> list[MatchResult]:
        sel = self.cfg["selectors"]
        soup = BeautifulSoup(html, "lxml")
        results: list[MatchResult] = []
        for row in soup.select(sel["row"]):
            try:
                results.append(self._parse_row(row, sel))
            except (AttributeError, ValueError, KeyError) as exc:
                log.debug("Skipping row (%s)", exc)
        log.info("Parsed %d matches", len(results))
        return results

    def _parse_row(self, row, sel: dict) -> MatchResult:
        def text(key: str) -> str:
            return row.select_one(sel[key]).get_text(strip=True)  # AttributeError if missing

        score = SCORE_RE.search(text("score"))
        if not score:
            raise ValueError("no score in row")
        competition = ""
        if "competition" in sel:
            node = row.select_one(sel["competition"])
            competition = node.get_text(strip=True) if node else ""
        return MatchResult(
            date=dt.datetime.strptime(text("date"), self.cfg.get("date_format", "%Y-%m-%d")).date(),
            home=text("home"),
            away=text("away"),
            home_goals=int(score.group(1)),
            away_goals=int(score.group(2)),
            competition=competition,
        )
