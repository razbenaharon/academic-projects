# MatchPoint — Football Tourism Accommodation Ranking

**Course:** Data Collection & Management Lab (00940290), Technion — Final Project

Rank Airbnb listings for football tourists, where "best" means *near the stadium on match day* rather than the generic price/quality trade-off booking platforms optimise for.

---

## Problem

Someone flying to a match cares about a different objective function than a general traveller: proximity to a specific stadium at a specific time dominates, with price and quality as secondary constraints. Booking platforms expose neither the fixture list nor stadium geography, so the search is manual — cross-referencing a match schedule against a map against a listings site, per candidate trip.

The project builds the missing join: fixtures × stadium geography × accommodation, ranked on a purpose-built objective.

## Pipeline

```text
scraping.ipynb            Wikipedia via Bright Data proxies
                          -> fixtures + stadium coordinates, 16 European leagues
                                        |
llm_enrichment.ipynb      Llama 3.3 70B (Databricks serving) via LangChain
                          -> per-stadium guides: food & drink, transit, tickets
                                        |
matchpoint_analysis.ipynb PySpark: join fixtures + guides + Airbnb listings
                          -> haversine distance, 50 km filter
                          -> value-for-money score, weighted ranking
                          -> MatchPoint_App.html (Leaflet, client-side)
```

**Ranking.** Final score is **60% proximity + 40% value-for-money**, where VFM combines rating, price, amenities and booking flexibility. Top 10 listings per fixture. The weighting encodes the premise: a football tourist trades quality for walking distance, and a ranker that does not say so by how much is just a generic search.

**Why scrape at all.** Fixture lists and stadium coordinates for 16 leagues are not available as one clean feed. Bright Data proxies with rate limiting and error handling were needed to collect them at that breadth.

**Why an LLM.** Stadium-area context — where to eat, how to get there, how tickets work — is the kind of knowledge that exists in prose across thousands of pages and in no structured source. Generating it per stadium was cheaper than building 16 more scrapers, and it is advisory content where an occasional inaccuracy is tolerable. It is not in the ranking path.

## Tech stack

| Layer | |
|---|---|
| Processing | PySpark, pandas, Databricks |
| Acquisition | BeautifulSoup, Bright Data residential proxies |
| Generation | Llama 3.3 70B via Databricks serving endpoints, LangChain |
| Output | Standalone HTML + Leaflet, no server |

## Running it

The notebooks execute in order — each writes artifacts the next reads:

| Step | Notebook | Output |
|---|---|---|
| 1 | `scraping.ipynb` | `Stadium_LLM_Enrichment.csv`, `Match_Schedule_All_Leagues.csv` |
| 2 | `llm_enrichment.ipynb` | `stadium_guides.json` |
| 3 | `matchpoint_analysis.ipynb` | `MatchPoint_App.html` |

Credentials are read from the environment (Databricks Secrets in the original setup); the notebooks reference `BRIGHTDATA_USER`, `BRIGHTDATA_PASSWORD`, `SAS_SUBMISSIONS` and `SAS_AIRBNB` by name only.

**This will not run as-is.** It targets Databricks with `/dbfs/FileStore` paths and a Llama serving endpoint, and the Airbnb dataset came from course-provided Azure storage. Preserved as a record of the work, with outputs intact.

## Notes on this copy

Migrated from a standalone repository during a portfolio cleanup:

- **The original repository committed a `.env` containing live Bright Data proxy credentials and two Azure SAS tokens.** It is not carried over, and no credential value appears anywhere in this repo — only variable names. See the portfolio report; the tokens still need rotating at source.
- `Final Project - MatchPoint.ipynb` → `matchpoint_analysis.ipynb` (spaces in filenames break tooling).
- Databricks mirrors each `display()` result a second time inside vendor metadata. Removing that duplicate took the main notebook from 9.0 MB to 0.3 MB, which is the difference between GitHub rendering it and refusing to. All 32 cells and every meaningful output are intact.
