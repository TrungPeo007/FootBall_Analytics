from __future__ import annotations

import datetime as dt
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class MatchResult:
    date: dt.date
    home: str
    away: str
    home_goals: int
    away_goals: int
    competition: str = ""

    def outcome_for(self, team: str) -> str:
        """Return 'W', 'D' or 'L' from the given team's point of view."""
        if self.home_goals == self.away_goals:
            return "D"
        home_won = self.home_goals > self.away_goals
        if team == self.home:
            return "W" if home_won else "L"
        if team == self.away:
            return "L" if home_won else "W"
        raise ValueError(f"{team!r} did not play in this match")

    def goals_for(self, team: str) -> int:
        return self.home_goals if team == self.home else self.away_goals

    def goals_against(self, team: str) -> int:
        return self.away_goals if team == self.home else self.home_goals


@dataclass
class TeamForm:
    team: str
    played: int
    results: list[str]  # most recent first, e.g. ["W", "D", "L"]
    wins: int
    draws: int
    losses: int
    points: int
    goals_for: int
    goals_against: int
    momentum: float  # 0..1, recency-weighted points share
    matches: list[MatchResult] = field(default_factory=list)


@dataclass
class H2HSummary:
    played: int
    home_wins: int
    away_wins: int
    draws: int
    avg_goals: float


@dataclass
class Prediction:
    home_win: float  # percent
    draw: float
    away_win: float
    expected_goals_home: float
    expected_goals_away: float
    risk_rating: str  # Low | Medium | High
    method: str


@dataclass
class MatchContext:
    home: str
    away: str
    competition: str
    kickoff: str
    home_form: TeamForm
    away_form: TeamForm
    h2h: H2HSummary
    h2h_matches: list[MatchResult]
    prediction: Prediction

    def to_dict(self) -> dict:
        return asdict(self)
