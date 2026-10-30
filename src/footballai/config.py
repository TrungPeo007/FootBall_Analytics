from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_UA = "football-ai-analyst/0.1 (educational project)"


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    temperature: float = 0.4
    request_delay: float = 2.0
    user_agent: str = DEFAULT_UA
    cache_dir: Path = Path("data/cache")
    output_dir: Path = Path("outputs")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.4")),
            request_delay=float(os.getenv("SCRAPER_DELAY_SECONDS", "2.0")),
            user_agent=os.getenv("SCRAPER_USER_AGENT", DEFAULT_UA),
            cache_dir=Path(os.getenv("CACHE_DIR", "data/cache")),
            output_dir=Path(os.getenv("OUTPUT_DIR", "outputs")),
        )
