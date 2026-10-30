from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

from .config import Settings
from .features import build_form, estimate_prediction, head_to_head_summary
from .models import MatchContext
from .prompts import (
    build_revision_prompt,
    build_user_prompt,
    load_system_prompt,
    validate_report,
)
from .scrapers.base import BaseScraper
from .utils import slugify

log = logging.getLogger(__name__)


def build_context(
    home: str, away: str, competition: str, kickoff: str, scraper: BaseScraper
) -> MatchContext:
    home_form = build_form(home, scraper.team_results(home))
    away_form = build_form(away, scraper.team_results(away))
    h2h, h2h_matches = head_to_head_summary(home, away, scraper.head_to_head(home, away))
    return MatchContext(
        home=home,
        away=away,
        competition=competition,
        kickoff=kickoff,
        home_form=home_form,
        away_form=away_form,
        h2h=h2h,
        h2h_matches=h2h_matches,
        prediction=estimate_prediction(home_form, away_form),
    )


def stats_frame(ctx: MatchContext) -> pd.DataFrame:
    rows = []
    for side, form in (("home", ctx.home_form), ("away", ctx.away_form)):
        rows.append(
            {
                "side": side,
                "team": form.team,
                "played": form.played,
                "form": "".join(form.results),
                "wins": form.wins,
                "draws": form.draws,
                "losses": form.losses,
                "points": form.points,
                "goals_for": form.goals_for,
                "goals_against": form.goals_against,
                "momentum": form.momentum,
            }
        )
    return pd.DataFrame(rows)


def run_pipeline(
    home: str,
    away: str,
    competition: str,
    kickoff: str,
    scraper: BaseScraper,
    settings: Settings,
    dry_run: bool = False,
    analyst=None,
) -> Path:
    """scrape -> features -> prompt -> LLM -> validate (+1 revision) -> files."""
    ctx = build_context(home, away, competition, kickoff, scraper)
    system_prompt = load_system_prompt()
    user_prompt = build_user_prompt(ctx)

    out_dir = Path(settings.output_dir) / f"{slugify(home)}-vs-{slugify(away)}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "context.json").write_text(
        json.dumps(ctx.to_dict(), indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    stats_frame(ctx).to_csv(out_dir / "stats.csv", index=False)
    (out_dir / "prompt.md").write_text(
        f"# System prompt\n\n{system_prompt}\n\n# User prompt\n\n{user_prompt}", encoding="utf-8"
    )
    if dry_run:
        log.info("Dry run: data + prompt written, LLM not called.")
        return out_dir

    if analyst is None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set (copy .env.example to .env), or use --dry-run.")
        from .gemini_client import GeminiAnalyst

        analyst = GeminiAnalyst(settings.gemini_api_key, settings.gemini_model, settings.temperature)

    report = analyst.generate(system_prompt, user_prompt)
    issues = validate_report(report)
    if issues:
        log.warning("Draft failed validation, requesting one revision: %s", issues)
        report = analyst.generate(system_prompt, build_revision_prompt(user_prompt, report, issues))
        issues = validate_report(report)
        if issues:
            log.warning("Revision still has issues: %s", issues)

    (out_dir / "report.md").write_text(report, encoding="utf-8")
    log.info("Report written (%d words)", len(report.split()))
    return out_dir
