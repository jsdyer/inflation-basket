# Inflation Basket

[Open Inflation Basket](https://coolcode.ca/inflation-basket/)

<!-- coolcode:guide -->
Convert a historical Canadian dollar amount using all-items CPI, with complete annual averages from 1914 for Canada and separately labelled latest-month comparisons. The original spending-basket calculator still compares eight major categories from 2002 onward and shows their contributions. Both calculations use dated official observations; personal amounts stay local.
<!-- /coolcode:guide -->

Choose Canada or one of its ten provinces and two months from January 2002 onward. The calculator opens with the latest published reference-period basket weights for that geography. Enter your own monthly spending or percentages to customize the eight major components. The published preset bears its basket year and can be applied to historical periods as a hypothetical fixed spending mix. The equal-weight control assigns the same share to every category. Changing region keeps custom inputs. No personal spending is saved or sent to a server.

The custom index starts at 100. For each subsequent month it sums the eight ratios of current price index to starting price index, weighted by their normalized starting shares. Contributions are percentage points of price change. The all-items benchmark is independently rebased using the published official all-items series, which links changing baskets over time. Percentages use unrounded inputs. A missing component with positive weight makes the affected custom result unavailable. Entering zero for a category excludes it. Both series are unadjusted for seasonality.

[Statistics Canada monthly CPI, table 18-10-0004-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401) · [Basket weights, table 18-10-0007-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000701) · [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/reference/licence).


## Historical-dollar calculator

The separate historical-dollar panel uses all-items CPI before the eight-component basket's 2002 starting point. Canadian complete-year history begins in **1914**. Provincial histories begin where their actual source series allows. Choose a source year, another complete year or the latest published month, and any non-negative amount up to 10¹⁵ CAD.

Equivalent amount = original amount × target CPI ÷ source CPI. Each annual index is the arithmetic mean of **all twelve published monthly indexes**, retained at calculation precision. These derived means can differ slightly from rounded annual indexes published in another table. A missing month excludes that year; the current incomplete year is never treated as a complete annual average. The latest-month option states its exact YYYY-MM and uses that one monthly index. It does not claim to be today's price.

The JSON export records both endpoint indexes, period meanings, geography, source and check date. This is consumer purchasing-power context, not investment performance, a company valuation adjustment or a city-to-city cost comparison. No amount is uploaded or automatically saved.

### Expand or customize

The original basket remains in `web/app.mjs`; the historical panel is `web/dollars.mjs`. `scripts/history.py` defines the exact geography names and validates dates, units, positive indexes and complete years. To add coverage, use an actual geography in table 18-10-0004-01, update the documented coverage and validation, then refresh and review it. Do not label a city series as a territory.

Regular `scripts/refresh.py` updates both the basket and historical-dollar JSON from the same monthly CPI download, then publishes only after validation. To rebuild only the historical snapshot, run `python3 scripts/history.py`; `--source-dir DIRECTORY` accepts a previously downloaded official ZIP named `18100004` for reproducible source-layout testing. The committed `web/data/dollars.json` makes the new panel available immediately on an offline build. No extra schedule, key or Worker handler is needed.

## Refresh and development

The committed edition builds offline. The scheduled workflow downloads the official archives, validates the edition, runs the browser checks, then commits the refreshed snapshot and deploys it. Source retrieval dates are separate from the observation periods. A failed refresh leaves the last published edition available.

Run `python3 scripts/refresh.py` to retrieve current source files, `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests` and `python3 scripts/build.py` to check and build. Preview using `python3 -m http.server --directory dist`. The interactive browser check is `python3 tests/browser_smoke.py` after installing the test-only Playwright dependency and its Chromium browser.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

The schedule guard remains a mitigation, not a scheduling guarantee: scheduled runs can be delayed or dropped. The independent [CoolCode refresh watchdog](https://github.com/jsdyer/jsdyer.github.io/blob/main/services/refresh-watchdog/README.md) is maintained in GitHub and reads the centrally generated [workflow and freshness registry](https://github.com/jsdyer/jsdyer.github.io/tree/main/data/operations). An installed watchdog downloads registry updates; confirm its service report to verify that the private server has adopted them. The guard does not collect data, create dummy commits or change source/check timestamps. Successful collection and published data freshness remain separate from watchdog service health.
<!-- /schedule-reliability -->
