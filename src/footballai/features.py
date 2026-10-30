"""Turn raw match results into the numbers the LLM is allowed to talk about."""
from __future__ import annotations

import math

from .models import H2HSummary, MatchResult, Prediction, TeamForm

POINTS = {"W": 3, "D": 1, "L": 0}
# Recency weights, most recent match first. Sum is normalised away.
RECENCY_WEIGHTS = (0.35, 0.25, 0.20, 0.12, 0.08)
PRIOR_GAMES = 4  # pseudo-games at league average to shrink small samples


def build_form(team: str, results: list[MatchResult], n: int = 5) -> TeamForm:
    n = min(n, len(RECENCY_WEIGHTS))
    recent = sorted(
        (r for r in results if team in (r.home, r.away)),
        key=lambda r: r.date,
        reverse=True,
    )[:n]
    if not recent:
        raise ValueError(f"No results found for team {team!r}")

    outcomes = [r.outcome_for(team) for r in recent]
    weights = RECENCY_WEIGHTS[: len(outcomes)]
    momentum = sum(w * POINTS[o] for w, o in zip(weights, outcomes)) / (3 * sum(weights))

    return TeamForm(
        team=team,
        played=len(recent),
        results=outcomes,
        wins=outcomes.count("W"),
        draws=outcomes.count("D"),
        losses=outcomes.count("L"),
        points=sum(POINTS[o] for o in outcomes),
        goals_for=sum(r.goals_for(team) for r in recent),
        goals_against=sum(r.goals_against(team) for r in recent),
        momentum=round(momentum, 3),
        matches=recent,
    )


def head_to_head_summary(
    home: str, away: str, matches: list[MatchResult], n: int = 6
) -> tuple[H2HSummary, list[MatchResult]]:
    recent = sorted(matches, key=lambda m: m.date, reverse=True)[:n]
    home_wins = away_wins = draws = goals = 0
    for m in recent:
        outcome = m.outcome_for(home)
        if outcome == "W":
            home_wins += 1
        elif outcome == "L":
            away_wins += 1
        else:
            draws += 1
        goals += m.home_goals + m.away_goals
    avg = round(goals / len(recent), 2) if recent else 0.0
    return H2HSummary(len(recent), home_wins, away_wins, draws, avg), recent


def _poisson(k: int, lam: float) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def _strength(goals: int, played: int, league_avg: float) -> float:
    """Shrunk per-game goal rate relative to league average."""
    return ((goals + PRIOR_GAMES * league_avg) / (played + PRIOR_GAMES)) / league_avg


def risk_rating(home_win: float, draw: float, away_win: float) -> str:
    """How uncertain the prediction is (not how risky a bet is)."""
    ordered = sorted((home_win, draw, away_win), reverse=True)
    top, margin = ordered[0], ordered[0] - ordered[1]
    if top >= 55 and margin >= 25:
        return "Low"
    if top >= 42 and margin >= 12:
        return "Medium"
    return "High"


def estimate_prediction(
    home: TeamForm,
    away: TeamForm,
    league_avg_goals: float = 1.35,
    home_advantage: float = 1.1,
    max_goals: int = 12,
) -> Prediction:
    """Small Poisson model: attack x opposing defence x home edge x momentum.

    Deliberately simple and transparent so the LLM can explain it from the data.
    """
    h_att = _strength(home.goals_for, home.played, league_avg_goals)
    h_def = _strength(home.goals_against, home.played, league_avg_goals)
    a_att = _strength(away.goals_for, away.played, league_avg_goals)
    a_def = _strength(away.goals_against, away.played, league_avg_goals)

    lam_home = league_avg_goals * h_att * a_def * home_advantage * (0.9 + 0.2 * home.momentum)
    lam_away = league_avg_goals * a_att * h_def / home_advantage * (0.9 + 0.2 * away.momentum)

    p_home = p_draw = p_away = 0.0
    for i in range(max_goals + 1):
        pi = _poisson(i, lam_home)
        for j in range(max_goals + 1):
            p = pi * _poisson(j, lam_away)
            if i > j:
                p_home += p
            elif i == j:
                p_draw += p
            else:
                p_away += p
    total = p_home + p_draw + p_away
    hw, dr, aw = (round(100 * x / total, 1) for x in (p_home, p_draw, p_away))

    return Prediction(
        home_win=hw,
        draw=dr,
        away_win=aw,
        expected_goals_home=round(lam_home, 2),
        expected_goals_away=round(lam_away, 2),
        risk_rating=risk_rating(hw, dr, aw),
        method=(
            "Poisson goal model on last-5 form (shrunk toward league average of "
            f"{league_avg_goals} goals), home advantage x{home_advantage}, "
            "momentum adjustment of +/-10%."
        ),
    )
