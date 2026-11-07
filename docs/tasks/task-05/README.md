# Task 5 — Netflix Trend Forecasting Model

Status: **Implemented locally, with real chronological experiments and explicit failure analysis.** Source: assignment PDF slide 10; submission/evaluation criteria: slide 12. The assignment asks for time-based preparation, historical release analysis, forecasting, future predictions and evaluation. No accuracy threshold or required forecasting algorithm is specified.

## Targets and scope

The primary target is **annual observed release-year cohort size**, following the assignment's release-trend wording. A distinct supplementary target forecasts **monthly observed catalog additions** using `date_added`. Neither measures all Netflix releases, demand or popularity. All projections are future relative to historical fitting origins, not the current date. The source snapshot ends September 25, 2021.

Six series combine two targets with All Titles, Movies and TV Shows. Four website pages provide history/coverage, interactive frozen forecasts, full chronological evaluation and methodology. Models fit independently by scope; projected subtotals need not reconcile.

## Reproduce

Use the root [setup](../../../README.md). Place the supplied, hash-verified file at `data/raw/Dataset.csv`.

```powershell
uv run python scripts/train_forecasting.py
uv run python scripts/build_forecasting_notebook.py
pnpm dev
```

Training prepares the series, compares the predeclared candidates, freezes each selection before test evaluation, then refits selected models on completed history and activates a validated bundle. Restart the API after activation. No training happens through HTTP or page navigation. New runs have new IDs and require fresh checks/screenshots before submission.

Open `/tasks/5/overview`, `/tasks/5/forecast`, `/tasks/5/evaluation`, `/tasks/5/methodology`. Query parameters `target=releases|additions`, `group=all|movies|tv` and forecast `horizon` support direct links. The API bounds horizons to 3 annual or 6 monthly periods; the UI offers only those frozen outputs. Export CSV includes run ID, target, scope, period and empirical error bounds.

## Verified results and practical limits

Run `20261106T122211417836Z`. The annual All Titles CV winner is **Ridge alpha=1**; its four-period test MAE is **2,395.37 titles**, versus **137.75** for last value. **This is a held-out failure**, exposed in the UI and report, not hidden or repaired by reselecting on test. Recursive extrapolation from earlier growth performs poorly after growth flattens.

Monthly All Titles selects **Ridge alpha=100**, test MAE **48.11** titles versus **70.00** for last value. Seasonal naive achieves **45.33**, so beating last value does not mean beating every baseline. The six-period test and snapshot biases limit conclusions. Forecast bands use pooled CV errors and are not calibrated confidence intervals.

- [Dataset and coverage](dataset-card.md)
- [Methodology and frozen protocol](methodology.md)
- [Model card](model-card.md)
- [Requirements-to-evidence matrix](requirements.md)
- [Generated report and error analysis](../../../reports/task-05/final_report.md)
- [Executed notebook](../../../notebooks/task-05/01_forecasting.ipynb)
- [Submission and browser replay guide](../../../submissions/task-05/README.md)

Implemented behavior, actual check records and planned research are kept separate. Better annual modeling, longer-horizon validation, bootstrap/interval calibration, external point-in-time data and hierarchical reconciliation remain future work; no such outcomes are claimed.
