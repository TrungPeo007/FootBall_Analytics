from __future__ import annotations

import argparse
import logging
import sys

from dotenv import load_dotenv

from .config import Settings
from .pipeline import run_pipeline
from .scrapers import HtmlScraper, HttpClient, SampleScraper


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="football-ai",
        description="Scrape football data and generate an AI match preview.",
    )
    p.add_argument("--home", required=True, help="Home team name, exactly as in the data source")
    p.add_argument("--away", required=True, help="Away team name")
    p.add_argument("--competition", default="League", help="Competition name (default: League)")
    p.add_argument("--kickoff", default="TBD", help="Kickoff date/time text")
    p.add_argument("--provider", choices=["sample", "html"], default="sample")
    p.add_argument("--fixtures", default="data/sample/fixtures.json", help="JSON file for --provider sample")
    p.add_argument("--sources", default="config/sources.json", help="Selector config for --provider html")
    p.add_argument("--dry-run", action="store_true", help="Scrape + build prompt, skip the LLM call")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    settings = Settings.from_env()

    if args.provider == "sample":
        scraper = SampleScraper(args.fixtures)
    else:
        http = HttpClient(settings.user_agent, settings.request_delay, settings.cache_dir)
        scraper = HtmlScraper.from_file(http, args.sources)

    try:
        out_dir = run_pipeline(
            args.home, args.away, args.competition, args.kickoff, scraper, settings, args.dry_run
        )
    except (RuntimeError, ValueError, PermissionError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Done -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
