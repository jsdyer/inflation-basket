# Inflation Basket

[Open Inflation Basket](https://coolcode.ca/inflation-basket/)

<!-- coolcode:guide -->
Set every category except food to zero to isolate food inflation. In BC from October 2025 to October 2026 the food index rose 2.37% and the official all-items index rose 2.51%. The contribution table shows exactly which spending categories drive a custom result.
<!-- /coolcode:guide -->

Choose Canada or one of its ten provinces and two months from January 2002 onward. The calculator opens with the latest published reference-period basket weights for that geography. Enter your own monthly spending or percentages to customize the eight major components. The published preset bears its basket year and can be applied to historical periods as a hypothetical fixed spending mix. The equal-weight control assigns the same share to every category. Changing region keeps custom inputs. No personal spending is saved or sent to a server.

The custom index starts at 100. For each subsequent month it sums the eight ratios of current price index to starting price index, weighted by their normalized starting shares. Contributions are percentage points of price change. The all-items benchmark is independently rebased using the published official all-items series, which links changing baskets over time. Percentages use unrounded inputs. A missing component with positive weight makes the affected custom result unavailable. Entering zero for a category excludes it. Both series are unadjusted for seasonality.

[Statistics Canada monthly CPI, table 18-10-0004-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401) · [Basket weights, table 18-10-0007-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000701) · [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/reference/licence).

## Refresh and development

The committed edition builds offline. The scheduled workflow downloads the official archives, validates the edition, runs the browser checks, then commits the refreshed snapshot and deploys it. Source retrieval dates are separate from the observation periods. A failed refresh leaves the last published edition available.

Run `python3 scripts/refresh.py` to retrieve current source files, `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests` and `python3 scripts/build.py` to check and build. Preview using `python3 -m http.server --directory dist`. The interactive browser check is `python3 tests/browser_smoke.py` after installing the test-only Playwright dependency and its Chromium browser.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->
