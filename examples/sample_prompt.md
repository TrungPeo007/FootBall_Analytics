# System prompt

You are a football analyst writing match previews for informed fans.

## Grounding rules (highest priority)
1. Use ONLY facts and numbers present in the JSON data supplied by the user. Never invent injuries, line-ups, managers, quotes, weather or stats.
2. If something useful is not in the data, state plainly that it is not available. Do not guess.
3. Quote the model's probabilities exactly as given (rounded to whole percent). Never change, re-derive or contradict them.
4. The risk rating in the data is final. Explain why it fits using the data (probability margin, form volatility, small sample).

## Analysis rules
5. Every claim about strength, weakness or momentum must be tied to a number from the data (e.g. "4 points from the last 5", "7 goals conceded in 5").
6. Tactical commentary must be framed as inference from goal patterns and results, and labelled as such ("the numbers suggest...").
7. Be objective and balanced. No hype, no guarantees, no betting tips, no certainty words such as "will definitely" or "lock".
8. Acknowledge uncertainty: football has high variance and form windows are small samples.

## Style
9. Write in clear English, active voice, analytical but readable.
10. Output Markdown only. Length: 500-1000 words. Follow the section structure requested by the user prompt exactly.


# User prompt

Write a match preview for this fixture.

## Fixture
- Competition: Demo League
- Kickoff: TBD
- Home: Riverside FC
- Away: Northgate United

## Verified data (the ONLY source of facts you may use)
```json
{
  "home": "Riverside FC",
  "away": "Northgate United",
  "competition": "Demo League",
  "kickoff": "TBD",
  "home_form": {
    "team": "Riverside FC",
    "played": 5,
    "results": [
      "W",
      "W",
      "D",
      "W",
      "L"
    ],
    "wins": 3,
    "draws": 1,
    "losses": 1,
    "points": 10,
    "goals_for": 8,
    "goals_against": 4,
    "momentum": 0.787,
    "matches": [
      {
        "date": "2026-10-24",
        "home": "Riverside FC",
        "away": "Lakeside Town",
        "home_goals": 2,
        "away_goals": 0,
        "competition": "Demo League"
      },
      {
        "date": "2026-10-17",
        "home": "Harbor City",
        "away": "Riverside FC",
        "home_goals": 1,
        "away_goals": 3,
        "competition": "Demo League"
      },
      {
        "date": "2026-10-10",
        "home": "Riverside FC",
        "away": "Westfield Rovers",
        "home_goals": 1,
        "away_goals": 1,
        "competition": "Demo League"
      },
      {
        "date": "2026-10-03",
        "home": "Eastvale Athletic",
        "away": "Riverside FC",
        "home_goals": 1,
        "away_goals": 2,
        "competition": "Demo League"
      },
      {
        "date": "2026-09-26",
        "home": "Riverside FC",
        "away": "Hillcrest FC",
        "home_goals": 0,
        "away_goals": 1,
        "competition": "Demo League"
      }
    ]
  },
  "away_form": {
    "team": "Northgate United",
    "played": 5,
    "results": [
      "L",
      "D",
      "W",
      "L",
      "W"
    ],
    "wins": 2,
    "draws": 1,
    "losses": 2,
    "points": 7,
    "goals_for": 5,
    "goals_against": 7,
    "momentum": 0.363,
    "matches": [
      {
        "date": "2026-10-25",
        "home": "Northgate United",
        "away": "Harbor City",
        "home_goals": 0,
        "away_goals": 2,
        "competition": "Demo League"
      },
      {
        "date": "2026-10-18",
        "home": "Oakwood Albion",
        "away": "Northgate United",
        "home_goals": 1,
        "away_goals": 1,
        "competition": "Demo League"
      },
      {
        "date": "2026-10-11",
        "home": "Northgate United",
        "away": "Hillcrest FC",
        "home_goals": 1,
        "away_goals": 0,
        "competition": "Demo League"
      },
      {
        "date": "2026-10-04",
        "home": "Lakeside Town",
        "away": "Northgate United",
        "home_goals": 3,
        "away_goals": 1,
        "competition": "Demo League"
      },
      {
        "date": "2026-09-27",
        "home": "Northgate United",
        "away": "Eastvale Athletic",
        "home_goals": 2,
        "away_goals": 1,
        "competition": "Demo League"
      }
    ]
  },
  "h2h": {
    "played": 6,
    "home_wins": 3,
    "away_wins": 2,
    "draws": 1,
    "avg_goals": 2.67
  },
  "h2h_matches": [
    {
      "date": "2026-03-14",
      "home": "Riverside FC",
      "away": "Northgate United",
      "home_goals": 2,
      "away_goals": 1,
      "competition": "Demo League"
    },
    {
      "date": "2025-10-05",
      "home": "Northgate United",
      "away": "Riverside FC",
      "home_goals": 1,
      "away_goals": 1,
      "competition": "Demo League"
    },
    {
      "date": "2025-03-02",
      "home": "Riverside FC",
      "away": "Northgate United",
      "home_goals": 0,
      "away_goals": 2,
      "competition": "Demo League"
    },
    {
      "date": "2024-11-10",
      "home": "Northgate United",
      "away": "Riverside FC",
      "home_goals": 2,
      "away_goals": 0,
      "competition": "Demo League"
    },
    {
      "date": "2024-04-20",
      "home": "Riverside FC",
      "away": "Northgate United",
      "home_goals": 3,
      "away_goals": 1,
      "competition": "Demo League"
    },
    {
      "date": "2023-12-09",
      "home": "Northgate United",
      "away": "Riverside FC",
      "home_goals": 1,
      "away_goals": 2,
      "competition": "Demo League"
    }
  ],
  "prediction": {
    "home_win": 60.6,
    "draw": 23.0,
    "away_win": 16.4,
    "expected_goals_home": 1.77,
    "expected_goals_away": 0.79,
    "risk_rating": "Low",
    "method": "Poisson goal model on last-5 form (shrunk toward league average of 1.35 goals), home advantage x1.1, momentum adjustment of +/-10%."
  }
}
```

## Required output
Start with a single H1 title: "Riverside FC vs Northgate United - Match Preview".
Then use exactly these H2 sections, in this order:

## Overview
Two or three sentences framing the fixture and what is at stake in the data.

## Form & Momentum
Compare both teams' last-5 results, points, goals scored/conceded and momentum score.

## Head-to-Head
Summarise previous meetings (wins, draws, average goals). Note the sample size.

## Tactical Summary
Inferred playing style and likely match shape from goal patterns. Label as inference.

## Probability Assessment
State home win / draw / away win percentages and expected goals exactly as given. Explain what drives each number using the data.

## Risk Rating
State the risk rating from the data (Low / Medium / High) and justify it in 2-4 sentences.

End with one italic line: *Statistical analysis for information only - not betting advice.*

Length: 500-1000 words in total.
