# България, 1989–2026 · Дългата промяна

> **Генерирано от изкуствен интелект.** Проучването, текстът, оценките, графиките и кодът са създадени от Claude (Anthropic) чрез Claude Code. Промптът е показан на самата страница, в раздела „Как е създаден този сайт“.

The page itself is in Bulgarian. It is fully AI-generated, says so in the header, the hero and the footer, and shows its prompt in its own section.

A long, scrollable, parallax history of Bulgaria from the Revival Process (1984) to the euro and the Radev government (2026), written as if by a historian in 2050.

## What the site does

The site is written from the prompt in `prompts/second-edition.md`. It:

- benchmarks Bulgaria against Romania, Croatia, Serbia, Slovakia, Poland and the EU, with country toggles on every comparison chart;
- scores every elected government on five separate dimensions (everyday life, economic foundations, geopolitics, institutions, society and demography), each with an in-term and a legacy mark, and lets the reader set the weights;
- shows "Bulgaria minus peers" for each government, with and without a one-year lag;
- adds a 1984–89 prologue, a decisions ledger (alternatives at the time and consequences), non-elected actors, survey voices, open questions from 2026, an adversarial review log and numbered citations;
- offers the chart data as JSON and CSV downloads.

## Какво ако?

`what-if/` is a counterfactual experiment: five alternative paths Bulgaria could have taken after 1989 (Baltic, Central European, Romanian, neutral Balkan, Eurasian), each anchored at a real decision point and measured with real proxy countries (Estonia, Latvia, Lithuania; Poland, Slovakia; Romania; Serbia, North Macedonia; Belarus, Armenia). Income is projected by the share of the gap to the EU each proxy closed, shown as a range across proxies and two base years. Each scenario is rated against reality on the same five dimensions as the main page, with a separate plausibility score, and can be compared with reality side by side.

## Structure

- `index.html` — the built main page (data inlined).
- `what-if/index.html` — the built "Какво ако?" page.
- `src/page.html`, `src/what-if.html` — page sources; `__DATA__`, `__PEERS__`, `__REVIEW__` and `__WHATIF__` are replaced at build time.
- `src/styles.css`, `src/charts.js` — styles and chart code shared by the main page and "Какво ако?".
- `data/data.json` — Bulgaria series.
- `data/peers.json` — cleaned peer-comparison series; `data/peers_raw.json` is the raw API extract (September 2026).
- `data/whatif.json` — cleaned proxy-country series; `data/whatif_raw.json` is the raw World Bank extract (`scripts/fetch_whatif.py`, `scripts/build_whatif.py`).
- `data/review.json` — the adversarial review and fact-check log shown on the page.
- `scripts/fetch_peers.py` — pulls the Eurostat and World Bank series; `scripts/build_peers.py` cleans them and adds the hand-collected RSF, CPI and turnout series.
- `scripts/build.py` — inlines the data and writes both pages.
- `prompts/` — the second-edition prompt and the research plan.

Rebuild after editing: `python3 scripts/build.py` (refresh data first with `python3 scripts/fetch_peers.py && python3 scripts/build_peers.py`).

## Sources

Eurostat, the National Statistical Institute of Bulgaria (nsi.bg), World Bank WDI and WGI, Reporters Without Borders, Transparency International, Pew Research Center, and Central Election Commission results as compiled on Wikipedia. The page lists every source with a link.
