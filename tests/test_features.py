import datetime as dt

import pytest

from footballai.features import build_form, estimate_prediction, head_to_head_summary, risk_rating
from footballai.models import MatchResult


def mr(day, home, away, hg, ag):
    return MatchResult(dt.date(2026, 1, day), home, away, hg, ag)


def test_form_order_points_and_goals():
    results = [mr(1, "A", "B", 2, 0), mr(2, "C", "A", 1, 1), mr(3, "A", "D", 0, 1)]
    form = build_form("A", results)
    assert form.results == ["L", "D", "W"]  # most recent first
    assert form.points == 4
    assert (form.goals_for, form.goals_against) == (3, 2)


def test_momentum_bounds():
    wins = [mr(i, "A", "X", 1, 0) for i in range(1, 6)]
    losses = [mr(i, "A", "X", 0, 1) for i in range(1, 6)]
    assert build_form("A", wins).momentum == 1.0
    assert build_form("A", losses).momentum == 0.0


def test_unknown_team_raises():
    with pytest.raises(ValueError):
        build_form("Nobody", [mr(1, "A", "B", 1, 0)])


def test_head_to_head_counts():
    matches = [mr(1, "A", "B", 2, 0), mr(2, "B", "A", 1, 1), mr(3, "B", "A", 3, 0)]
    summary, _ = head_to_head_summary("A", "B", matches)
    assert (summary.home_wins, summary.draws, summary.away_wins) == (1, 1, 1)
    assert summary.avg_goals == 2.33


def test_probabilities_sum_to_100_and_favour_stronger_side():
    strong = build_form("A", [mr(i, "A", "X", 3, 0) for i in range(1, 6)])
    weak = build_form("B", [mr(i, "B", "Y", 0, 3) for i in range(1, 6)])
    p = estimate_prediction(strong, weak)
    assert abs(p.home_win + p.draw + p.away_win - 100) < 0.3
    assert p.home_win > p.away_win
    assert p.risk_rating in {"Low", "Medium", "High"}


def test_risk_rating_levels():
    assert risk_rating(70, 20, 10) == "Low"
    assert risk_rating(48, 28, 24) == "Medium"
    assert risk_rating(36, 33, 31) == "High"
