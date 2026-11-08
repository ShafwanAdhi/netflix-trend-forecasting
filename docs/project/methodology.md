# forecasting protocol

Configuration: `configs/task-05/experiment.json`. All choices below were declared before scoring the held-out test. Changing them after inspecting results requires a new experiment and a genuinely new evaluation period; do not report the old test as untouched after iterative tuning.

## Features and models

Annual lags 1, 2, 3; monthly lags 1, 2, 3, 6, 12. Include trailing-three mean and sequential time index. Monthly models additionally use trailing-twelve mean and sine/cosine month seasonality. At period t every lag/rolling value comes strictly from periods before t; feature rows never include t's target. No rating, title, ID, country, genre or director enters the aggregated model.

Candidates in tie-break order: last value, mean of last three, drift, monthly seasonal naive, Ridge alpha 1/10/100, forest max_depth=3 and unlimited. Forests use 120 estimators, min_samples_leaf=2, seed 42, n_jobs=1. Ridge uses StandardScaler fitted inside each chronological origin's pipeline. Forests and baseline parameters also fit only that origin's past. Predictions are recursively fed back for multi-step lags; future observations are never injected. Clip point predictions to zero before recursive feedback; retain fractional expected counts, rounding for display only.

There are 8 annual and 9 monthly candidates, each across three scopes: **51 candidate-series comparisons**. Five annual and four monthly folds give **228 CV fits**, followed by 51 test-comparison fits and 6 final selected-model refits (including baseline fits in these counts). No random split, grid search on the final test, or post-test winner change is used.

## Chronological windows

| Target | Fitting window for final test | Final test | Expanding CV origins | CV horizon | Published horizon |
| --- | --- | --- | --- | --- | --- |
| Annual releases | 2000–2016 | 2017–2020 (4) | 2010, 2011, 2012, 2013, 2014 | 2 years | 2021–2023 (3) |
| Monthly additions | 2015-01–2021-02 | 2021-03–2021-08 (6) | 2018-12, 2019-06, 2019-12, 2020-06 | 6 months | 2021-09–2022-02 (6) |

Each origin uses all prior modeled observations. Annual validation windows overlap and errors are dependent; monthly validation blocks are consecutive nonoverlapping blocks, though training histories overlap. The temporal manifest records actual membership. All CV validation dates precede the final test. Annual CV does not validate the full 3-/4-step deployment/test horizon; this mismatch is an explicit limitation, not evidence of reliable longer-range forecasting.

Select the smallest mean CV MAE across folds, breaking exact ties by declared candidate order. Freeze `selection.json` before any candidate test scores for that series. Test comparisons are displayed transparently afterward and do not reselect. The final published model refits the CV-selected specification on all completed periods, including the test window, only after evaluating the development-only model. Test metrics remain associated with that earlier fit. Save the final models, metadata, selections, results, aggregate series and membership, validate checksums and compatibility, then activate the pointer. API startup only reads validated trusted artifacts.

## Metrics and exploratory error bands

MAE is mean absolute error in titles/period; RMSE emphasizes large errors. sMAPE is mean `200*abs(y-p)/(abs(y)+abs(p))`, using zero when both are zero. WAPE is summed absolute error divided by summed absolute actuals, null if the denominator is zero. MASE divides MAE by mean absolute development differences at lag 1 annually or 12 monthly, null for zero scale. MASE is not identical to skill against the final-test last-value forecast. Report the last-value comparison separately and show every candidate's scores.

Pool absolute errors from the selected specification's CV predictions; take the empirical 80th percentile with NumPy `method=higher`. Subtract/add this constant around each point forecast and clip the lower bound at zero. Annual series have 10 residuals, monthly 24. These residuals are small, dependent and influenced by model selection. The band is **not a calibrated 80% prediction interval**, not horizon-dependent, and does not guarantee coverage. Report actual final-test coverage. No test residuals set the band width. Uncertainty will often be understated after structural shifts or for longer horizons.

## Failure analysis and future research

Annual growth through the mid-2010s is followed by flattening. Early-origin CV favors weakly regularized recursive Ridge; the long untouched test exposes explosive extrapolation and worse performance than simple baselines. Keep and explain this outcome. Monthly Ridge improves on last value for All Titles but loses to seasonal naive on test; do not claim universal baseline superiority. Next research could use horizon-matched nested validation, stronger stability constraints, external point-in-time observations and interval calibration, each under a fresh evaluation protocol. These are planned, not verified improvements.
