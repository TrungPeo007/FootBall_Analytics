from pathlib import Path

from footballai.config import Settings
from footballai.pipeline import run_pipeline
from footballai.prompts import REQUIRED_SECTIONS, validate_report
from footballai.scrapers import SampleScraper

FIXTURES = Path(__file__).resolve().parents[1] / "data" / "sample" / "fixtures.json"


def good_report() -> str:
    return "# Title\n" + "\n".join(f"## {s}\n" + "analysis " * 100 for s in REQUIRED_SECTIONS)


class FakeAnalyst:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0

    def generate(self, system_prompt, user_prompt):
        self.calls += 1
        return self.replies.pop(0)


def test_validate_report():
    assert validate_report(good_report()) == []
    issues = validate_report("## Overview\nshort")
    assert any("Too short" in i for i in issues)
    assert any("Missing section" in i for i in issues)


def test_dry_run_writes_data_and_prompt(tmp_path):
    out = run_pipeline(
        "Riverside FC", "Northgate United", "Demo League", "TBD",
        SampleScraper(FIXTURES), Settings(output_dir=tmp_path), dry_run=True,
    )
    assert (out / "context.json").exists()
    assert (out / "stats.csv").exists()
    assert "Riverside FC" in (out / "prompt.md").read_text(encoding="utf-8")
    assert not (out / "report.md").exists()


def test_full_run_with_fake_llm(tmp_path):
    analyst = FakeAnalyst([good_report()])
    out = run_pipeline(
        "Riverside FC", "Northgate United", "Demo League", "TBD",
        SampleScraper(FIXTURES), Settings(output_dir=tmp_path), analyst=analyst,
    )
    assert analyst.calls == 1
    assert (out / "report.md").exists()


def test_invalid_draft_triggers_one_revision(tmp_path):
    analyst = FakeAnalyst(["too short", good_report()])
    out = run_pipeline(
        "Riverside FC", "Northgate United", "Demo League", "TBD",
        SampleScraper(FIXTURES), Settings(output_dir=tmp_path), analyst=analyst,
    )
    assert analyst.calls == 2
    assert validate_report((out / "report.md").read_text(encoding="utf-8")) == []
