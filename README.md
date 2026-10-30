# Football Data Scraper & AI Match Analysis Pipeline

[![CI](https://github.com/<your-username>/football-ai-analyst/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-username>/football-ai-analyst/actions)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

An automated pipeline that scrapes match data (recent results, head-to-head records, team momentum), turns it into verified statistics and a transparent probability model, and uses the **Gemini API** with structured system prompts to write 500-1,000 word match previews with tactical summaries and risk-rated predictions.

**Tech:** Python · BeautifulSoup · pandas · Gemini API · Prompt Engineering · Git

## How it works

```
 data source ──▶ scraper ──▶ features ──▶ prompt builder ──▶ Gemini ──▶ validator ──▶ report.md
 (HTML pages)   (bs4)       (form, H2H,   (system prompt +    (LLM)      (length +      + context.json
                             Poisson       JSON context)                 sections,      + stats.csv
                             model, risk)                                1 auto-retry)
```

1. **Scrape** – a polite HTTP client (robots.txt check, rate limit, retry/backoff, disk cache) feeds a config-driven BeautifulSoup scraper. URLs and CSS selectors live in a JSON file, so supporting a new site means editing config, not code.
2. **Features** – last-5 form (W/D/L, points, goals), recency-weighted *momentum* score, head-to-head summary, and a small Poisson model that outputs 1X2 probabilities, expected goals and an uncertainty-based **risk rating** (Low / Medium / High).
3. **Prompting** – the LLM receives only a verified JSON context. The system prompt forbids inventing facts, requires every claim to cite a number, fixes the probabilities and risk rating, and labels tactical commentary as inference.
4. **Validation** – output must be 500-1,000 words and contain all required sections; otherwise the pipeline sends one automatic revision request with the exact problems listed.

## Quick start

```bash
git clone https://github.com/<your-username>/football-ai-analyst.git
cd football-ai-analyst
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env                                  # add your GEMINI_API_KEY
```

Try it offline with the bundled **synthetic** demo data:

```bash
# No API key needed: scrapes, computes stats, writes the prompt
python -m footballai --home "Riverside FC" --away "Northgate United" --competition "Demo League" --dry-run

# With a Gemini key: full AI match preview
python -m footballai --home "Riverside FC" --away "Northgate United" --competition "Demo League"
```

Output goes to `outputs/<home>-vs-<away>/`:

| File | Content |
|---|---|
| `report.md` | The generated match preview |
| `context.json` | Exact data the LLM was given |
| `stats.csv` | Side-by-side team stats (pandas) |
| `prompt.md` | Full system + user prompt, for auditing |

See [`examples/`](examples) for a sample context, stats table and prompt.

## Using a real data source

```bash
cp config/sources.example.json config/sources.json   # edit URLs + CSS selectors
python -m footballai --provider html --home "Team A" --away "Team B"
```

> **Scrape responsibly.** Only scrape sites whose Terms of Service allow it, respect `robots.txt` (enforced by the client), keep the default delay, and prefer official APIs where available. Selectors in `sources.example.json` are placeholders.

Adding a new source with different structure? Subclass `BaseScraper` (two methods: `team_results`, `head_to_head`).

## Prompt engineering notes

- **Grounding first**: the model may only use numbers present in the JSON; missing data must be stated as unavailable.
- **Separation of concerns**: probabilities and risk are computed in Python, not by the LLM. The LLM explains, it does not invent.
- **Structured output**: fixed H1/H2 layout makes reports comparable and machine-checkable.
- **Objective tone**: no hype, no betting tips, uncertainty acknowledged explicitly.
- **Self-repair loop**: automatic validation + single targeted revision prompt.

Prompt templates are plain Markdown in [`src/footballai/prompts/`](src/footballai/prompts) so they can be versioned and diffed in Git.

## Tests

```bash
pytest -q
```

Covers form/momentum maths, probability model, HTML parsing (offline, no network), prompt validation, and the full pipeline with a fake LLM.

## Project structure

```
src/footballai/
├── scrapers/        # http client, base class, HTML scraper, offline sample scraper
├── prompts/         # system prompt + match preview template (Markdown)
├── features.py      # form, momentum, H2H, Poisson model, risk rating
├── prompts.py       # prompt building + output validation
├── gemini_client.py # Gemini API wrapper with retry
├── pipeline.py      # orchestration
└── cli.py           # command line interface
tests/  data/sample/  config/  examples/
```

## Roadmap

- League table / xG features from additional sources
- Batch mode for a whole matchday
- Backtesting predicted probabilities (Brier score) against real results

## Disclaimer

Statistical analysis for information only. Not betting advice. Demo data in `data/sample` is synthetic.

## License

MIT
