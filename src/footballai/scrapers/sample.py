from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from ..models import MatchResult
from .base import BaseScraper


class SampleScraper(BaseScraper):
    """Offline provider backed by a local JSON file (synthetic demo data)."""

    def __init__(self, path: str | Path) -> None:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        self.matches = [
            MatchResult(
                date=dt.date.fromisoformat(m["date"]),
                home=m["home"],
                away=m["away"],
                home_goals=m["home_goals"],
                away_goals=m["away_goals"],
                competition=m.get("competition", ""),
            )
            for m in raw["matches"]
        ]

    def team_results(self, team: str) -> list[MatchResult]:
        return [m for m in self.matches if team in (m.home, m.away)]

    def head_to_head(self, home: str, away: str) -> list[MatchResult]:
        return [m for m in self.matches if {m.home, m.away} == {home, away}]
