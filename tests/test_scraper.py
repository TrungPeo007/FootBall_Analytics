import datetime as dt

from footballai.scrapers import HtmlScraper

HTML = """
<table class="results"><tbody>
  <tr><th>Date</th><th>Home</th><th>Score</th><th>Away</th></tr>
  <tr><td class="date">2026-10-01</td><td class="home">Riverside FC</td>
      <td class="score">2 - 1</td><td class="away">Hillcrest FC</td><td class="comp">Demo League</td></tr>
  <tr><td class="date">2026-09-24</td><td class="home">Harbor City</td>
      <td class="score">postponed</td><td class="away">Riverside FC</td></tr>
</tbody></table>
"""

CONFIG = {
    "results_url": "https://example.test/{team_slug}",
    "h2h_url": "https://example.test/{home_slug}-{away_slug}",
    "selectors": {
        "row": "table.results tbody tr",
        "date": "td.date",
        "home": "td.home",
        "away": "td.away",
        "score": "td.score",
        "competition": "td.comp",
    },
}


class FakeHttp:
    def __init__(self):
        self.urls = []

    def get(self, url):
        self.urls.append(url)
        return HTML


def test_parses_valid_rows_and_skips_bad_ones():
    http = FakeHttp()
    results = HtmlScraper(http, CONFIG).team_results("Riverside FC")
    assert http.urls == ["https://example.test/riverside-fc"]
    assert len(results) == 1  # header row and "postponed" row skipped
    m = results[0]
    assert (m.home, m.away, m.home_goals, m.away_goals) == ("Riverside FC", "Hillcrest FC", 2, 1)
    assert m.date == dt.date(2026, 10, 1)
    assert m.competition == "Demo League"
