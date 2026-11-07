# Task 5 model card

Run `20261106T122211417836Z`; source snapshot through September 25, 2021. Six independently fitted forecasting pipelines use the shared [protocol](methodology.md). Saved final models are refitted after evaluation; reported test metrics come from development-only fits. sklearn/Python versions and exact configuration are in the bundle.

| Target / scope | CV-selected model | Test MAE (titles/period) | Last-value test MAE |
| --- | --- | ---: | ---: |
| Annual / All | Ridge alpha=1 | 2,395.37 | 137.75 |
| Annual / Movies | Ridge alpha=1 | 1,801.70 | 95.50 |
| Annual / TV | Ridge alpha=1 | 527.58 | 125.75 |
| Monthly / All | Ridge alpha=100 | 48.11 | 70.00 |
| Monthly / Movies | Ridge alpha=100 | 28.51 | 54.00 |
| Monthly / TV | Shallow Random Forest | 19.33 | 20.33 |

**Annual generalization failed.** The large errors are retained in reports/UI rather than selecting a new winner from test. Monthly models beat last value in this short test, but seasonal naive is better for All/Movies (45.33/24.50 MAE); several TV alternatives also have lower test error. Selection remains frozen to prevent test-driven optimization.

Intended use: educational exploration of snapshot release cohorts, additions and chronological validation. Annual projections cover 2021–2023 from a 2020 fitting endpoint; monthly projections cover 2021-09–2022-02 from 2021-08. Neither is a current forecast or actual verified future outcome. Snapshot data was collected later than some retrospective fitting endpoints, so no true point-in-time archive is claimed.

The API serves precomputed bounded horizons and a real pipeline bundle. It does not accept uploads, trigger training or expose arbitrary current/far-future projections. Negative count projections are clipped at zero; fractional point forecasts are expected counts, not literal partial titles. Independent scope forecasts are not hierarchically reconciled.

Exploratory bands use CV absolute errors; test coverage and its limitations are visible. They are not calibrated confidence. Structural breaks, small annual samples, partial recent cohorts, survivorship, backfills, retained date discrepancies and source taxonomy all limit reliability. There is no evidence for audience demand, revenue or full Netflix release schedules.

Verified evidence is in the [submission guide](../../../submissions/task-05/README.md): chronological manifests, feature alignment, saved-model parity, reproduced test predictions/metrics, API limits/independent readiness, responsive UI and Tasks 3/4 regressions. Expanded studies, public hosting, external portal submission and video recording are not claimed.
