from __future__ import annotations

import json
import re
from pathlib import Path
from string import Template

from .models import MatchContext

PROMPT_DIR = Path(__file__).parent / "prompts"
MIN_WORDS, MAX_WORDS = 500, 1000
REQUIRED_SECTIONS = (
    "Overview",
    "Form & Momentum",
    "Head-to-Head",
    "Tactical Summary",
    "Probability Assessment",
    "Risk Rating",
)


def load_system_prompt() -> str:
    return (PROMPT_DIR / "system_prompt.md").read_text(encoding="utf-8")


def build_user_prompt(ctx: MatchContext) -> str:
    template = Template((PROMPT_DIR / "match_preview.md").read_text(encoding="utf-8"))
    return template.substitute(
        competition=ctx.competition,
        kickoff=ctx.kickoff,
        home=ctx.home,
        away=ctx.away,
        context_json=json.dumps(ctx.to_dict(), indent=2, ensure_ascii=False, default=str),
    )


def validate_report(text: str, min_words: int = MIN_WORDS, max_words: int = MAX_WORDS) -> list[str]:
    """Return a list of problems; empty list means the report passes."""
    issues: list[str] = []
    words = len(text.split())
    if words < min_words:
        issues.append(f"Too short: {words} words (minimum {min_words}).")
    if words > max_words:
        issues.append(f"Too long: {words} words (maximum {max_words}).")
    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^#+\s.*{re.escape(section)}", text, re.IGNORECASE | re.MULTILINE):
            issues.append(f"Missing section heading: '{section}'.")
    return issues


def build_revision_prompt(user_prompt: str, draft: str, issues: list[str]) -> str:
    problems = "\n".join(f"- {i}" for i in issues)
    return (
        f"{user_prompt}\n\n---\n"
        f"Your previous draft failed validation:\n{problems}\n\n"
        f"Previous draft:\n{draft}\n\n"
        "Rewrite the complete report so every issue is fixed. Keep all facts grounded in the data. "
        "Output only the final report."
    )
