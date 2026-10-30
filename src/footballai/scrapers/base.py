from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import MatchResult


class BaseScraper(ABC):
    """Every data source implements these two calls; the pipeline does not care which."""

    @abstractmethod
    def team_results(self, team: str) -> list[MatchResult]:
        """Recent results for one team (any order)."""

    @abstractmethod
    def head_to_head(self, home: str, away: str) -> list[MatchResult]:
        """Previous meetings between the two teams (any order)."""
