# Historical trend forecasts

Run `20261106T122211417836Z`; snapshot 2021-09-25. Projections are historical as-of estimates, not current forecasts.

Annual target: observed snapshot titles grouped by release year; not all Netflix releases. Monthly target: observed date-added cohorts; not original release dates. Incomplete 2021 release year and September 2021 additions are excluded. Removed titles and future backfills are absent; even older periods are not proven complete.

## releases / all

Selected **ridge_1** using CV MAE. Held-out test 2017-01-01 to 2020-01-01.

Test MAE **2395.37**, RMSE **3074.42**, sMAPE **89.07%**, MASE **42.966**. Empirical error-band coverage: 0.0%.

Last-value test MAE **137.75**; selected-model relative MAE improvement **-1638.9%**. **Held-out failure: the CV winner performs worse than last value.** Earlier growth-regime validation did not predict later flattening; recursive errors amplify across the longer annual test. Retain the failure, do not reselect on test. 

| Test period | Actual | Predicted | Absolute error |
| --- | ---: | ---: | ---: |
| 2017-01-01 | 1030 | 1376.2 | 346.2 |
| 2018-01-01 | 1143 | 2260.4 | 1117.4 |
| 2019-01-01 | 1029 | 3767.0 | 2738.0 |
| 2020-01-01 | 953 | 6332.9 | 5379.9 |

| Candidate | CV MAE | Test MAE | Test RMSE |
| --- | ---: | ---: | ---: |
| last_value | 145.60 | 137.75 | 153.54 |
| mean_3 | 181.00 | 436.42 | 441.65 |
| drift | 122.57 | 101.75 | 113.61 |
| ridge_1 | 109.23 | 2395.37 | 3074.42 |
| ridge_10 | 123.94 | 719.31 | 949.83 |
| ridge_100 | 209.76 | 377.85 | 385.76 |
| forest_shallow | 192.55 | 447.87 | 452.97 |
| forest_full | 192.55 | 447.87 | 452.97 |

Test scores are displayed for transparency after the selection record was frozen; they do not reselect the model.

| Future period (historical as-of) | Projection | Lower | Upper |
| --- | ---: | ---: | ---: |
| 2021-01-01 | 938.7 | 738.4 | 1139.1 |
| 2022-01-01 | 969.2 | 768.8 | 1169.5 |
| 2023-01-01 | 1032.2 | 831.8 | 1232.5 |

Error band uses the 80th-percentile absolute CV residual (10 pooled errors), fixed across horizons and clipped at zero. It is exploratory, not a calibrated confidence interval. Annual CV horizons are 2 years, while test is 4 and projection 3; longer-horizon uncertainty is not calibrated. Final test uses development-only fit. Published projection refits selected model on all completed periods, including test, after evaluation; stored test scores are unchanged.

## releases / movies

Selected **ridge_1** using CV MAE. Held-out test 2017-01-01 to 2020-01-01.

Test MAE **1801.70**, RMSE **2319.49**, sMAPE **95.16%**, MASE **44.011**. Empirical error-band coverage: 0.0%.

Last-value test MAE **95.50**; selected-model relative MAE improvement **-1786.6%**. **Held-out failure: the CV winner performs worse than last value.** Earlier growth-regime validation did not predict later flattening; recursive errors amplify across the longer annual test. Retain the failure, do not reselect on test. 

| Test period | Actual | Predicted | Absolute error |
| --- | ---: | ---: | ---: |
| 2017-01-01 | 765 | 987.2 | 222.2 |
| 2018-01-01 | 766 | 1619.8 | 853.8 |
| 2019-01-01 | 632 | 2710.3 | 2078.3 |
| 2020-01-01 | 517 | 4569.5 | 4052.5 |

| Candidate | CV MAE | Test MAE | Test RMSE |
| --- | ---: | ---: | ---: |
| last_value | 101.50 | 95.50 | 104.49 |
| mean_3 | 126.90 | 231.00 | 253.25 |
| drift | 84.96 | 134.56 | 169.09 |
| ridge_1 | 78.96 | 1801.70 | 2319.49 |
| ridge_10 | 89.02 | 567.47 | 739.13 |
| ridge_100 | 148.60 | 197.27 | 230.41 |
| forest_shallow | 134.77 | 238.43 | 260.04 |
| forest_full | 134.77 | 238.43 | 260.04 |

Test scores are displayed for transparency after the selection record was frozen; they do not reselect the model.

| Future period (historical as-of) | Projection | Lower | Upper |
| --- | ---: | ---: | ---: |
| 2021-01-01 | 477.2 | 344.8 | 609.6 |
| 2022-01-01 | 503.4 | 371.0 | 635.8 |
| 2023-01-01 | 578.6 | 446.2 | 711.0 |

Error band uses the 80th-percentile absolute CV residual (10 pooled errors), fixed across horizons and clipped at zero. It is exploratory, not a calibrated confidence interval. Annual CV horizons are 2 years, while test is 4 and projection 3; longer-horizon uncertainty is not calibrated. Final test uses development-only fit. Published projection refits selected model on all completed periods, including test, after evaluation; stored test scores are unchanged.

## releases / tv

Selected **ridge_1** using CV MAE. Held-out test 2017-01-01 to 2020-01-01.

Test MAE **527.58**, RMSE **672.09**, sMAPE **70.26%**, MASE **34.738**. Empirical error-band coverage: 0.0%.

Last-value test MAE **125.75**; selected-model relative MAE improvement **-319.5%**. **Held-out failure: the CV winner performs worse than last value.** Earlier growth-regime validation did not predict later flattening; recursive errors amplify across the longer annual test. Retain the failure, do not reselect on test. 

| Test period | Actual | Predicted | Absolute error |
| --- | ---: | ---: | ---: |
| 2017-01-01 | 265 | 371.9 | 106.9 |
| 2018-01-01 | 377 | 608.6 | 231.6 |
| 2019-01-01 | 397 | 989.5 | 592.5 |
| 2020-01-01 | 436 | 1615.3 | 1179.3 |

| Candidate | CV MAE | Test MAE | Test RMSE |
| --- | ---: | ---: | ---: |
| last_value | 44.70 | 125.75 | 140.89 |
| mean_3 | 54.10 | 205.42 | 215.02 |
| drift | 39.56 | 88.41 | 100.71 |
| ridge_1 | 32.49 | 527.58 | 672.09 |
| ridge_10 | 35.93 | 159.34 | 206.54 |
| ridge_100 | 61.11 | 181.70 | 188.76 |
| forest_shallow | 57.00 | 208.01 | 217.50 |
| forest_full | 57.00 | 208.01 | 217.50 |

Test scores are displayed for transparency after the selection record was frozen; they do not reselect the model.

| Future period (historical as-of) | Projection | Lower | Upper |
| --- | ---: | ---: | ---: |
| 2021-01-01 | 520.0 | 450.8 | 589.3 |
| 2022-01-01 | 585.1 | 515.8 | 654.3 |
| 2023-01-01 | 659.8 | 590.5 | 729.0 |

Error band uses the 80th-percentile absolute CV residual (10 pooled errors), fixed across horizons and clipped at zero. It is exploratory, not a calibrated confidence interval. Annual CV horizons are 2 years, while test is 4 and projection 3; longer-horizon uncertainty is not calibrated. Final test uses development-only fit. Published projection refits selected model on all completed periods, including test, after evaluation; stored test scores are unchanged.

## additions / all

Selected **ridge_100** using CV MAE. Held-out test 2021-03-01 to 2021-08-01.

Test MAE **48.11**, RMSE **57.81**, sMAPE **27.88%**, MASE **1.190**. Empirical error-band coverage: 50.0%.

Last-value test MAE **70.00**; selected-model relative MAE improvement **31.3%**. 

| Test period | Actual | Predicted | Absolute error |
| --- | ---: | ---: | ---: |
| 2021-03-01 | 112 | 143.0 | 31.0 |
| 2021-04-01 | 188 | 143.2 | 44.8 |
| 2021-05-01 | 132 | 141.4 | 9.4 |
| 2021-06-01 | 207 | 146.9 | 60.1 |
| 2021-07-01 | 257 | 145.9 | 111.1 |
| 2021-08-01 | 178 | 145.7 | 32.3 |

| Candidate | CV MAE | Test MAE | Test RMSE |
| --- | ---: | ---: | ---: |
| last_value | 35.04 | 70.00 | 84.70 |
| mean_3 | 34.35 | 52.11 | 63.77 |
| drift | 40.07 | 64.82 | 79.57 |
| seasonal_naive | 34.75 | 45.33 | 55.82 |
| ridge_1 | 36.04 | 69.73 | 84.00 |
| ridge_10 | 31.59 | 50.39 | 62.37 |
| ridge_100 | 23.20 | 48.11 | 57.81 |
| forest_shallow | 28.36 | 47.10 | 54.82 |
| forest_full | 28.39 | 47.48 | 56.28 |

Test scores are displayed for transparency after the selection record was frozen; they do not reselect the model.

| Future period (historical as-of) | Projection | Lower | Upper |
| --- | ---: | ---: | ---: |
| 2021-09-01 | 182.9 | 150.2 | 215.6 |
| 2021-10-01 | 187.6 | 154.9 | 220.3 |
| 2021-11-01 | 174.3 | 141.6 | 207.0 |
| 2021-12-01 | 179.8 | 147.1 | 212.5 |
| 2022-01-01 | 178.9 | 146.2 | 211.6 |
| 2022-02-01 | 167.9 | 135.2 | 200.6 |

Error band uses the 80th-percentile absolute CV residual (24 pooled errors), fixed across horizons and clipped at zero. It is exploratory, not a calibrated confidence interval. Annual CV horizons are 2 years, while test is 4 and projection 3; longer-horizon uncertainty is not calibrated. Final test uses development-only fit. Published projection refits selected model on all completed periods, including test, after evaluation; stored test scores are unchanged.

## additions / movies

Selected **ridge_100** using CV MAE. Held-out test 2021-03-01 to 2021-08-01.

Test MAE **28.51**, RMSE **35.21**, sMAPE **24.65%**, MASE **0.885**. Empirical error-band coverage: 66.7%.

Last-value test MAE **54.00**; selected-model relative MAE improvement **47.2%**. 

| Test period | Actual | Predicted | Absolute error |
| --- | ---: | ---: | ---: |
| 2021-03-01 | 75 | 96.1 | 21.1 |
| 2021-04-01 | 135 | 98.5 | 36.5 |
| 2021-05-01 | 94 | 95.8 | 1.8 |
| 2021-06-01 | 124 | 99.7 | 24.3 |
| 2021-07-01 | 169 | 100.3 | 68.7 |
| 2021-08-01 | 117 | 98.3 | 18.7 |

| Candidate | CV MAE | Test MAE | Test RMSE |
| --- | ---: | ---: | ---: |
| last_value | 29.25 | 54.00 | 61.70 |
| mean_3 | 28.78 | 35.78 | 43.52 |
| drift | 34.96 | 50.93 | 58.63 |
| seasonal_naive | 30.08 | 24.50 | 32.07 |
| ridge_1 | 34.59 | 50.45 | 59.66 |
| ridge_10 | 29.89 | 33.54 | 40.61 |
| ridge_100 | 20.30 | 28.51 | 35.21 |
| forest_shallow | 24.76 | 27.06 | 31.95 |
| forest_full | 24.71 | 29.79 | 34.58 |

Test scores are displayed for transparency after the selection record was frozen; they do not reselect the model.

| Future period (historical as-of) | Projection | Lower | Upper |
| --- | ---: | ---: | ---: |
| 2021-09-01 | 120.1 | 93.7 | 146.5 |
| 2021-10-01 | 126.0 | 99.6 | 152.4 |
| 2021-11-01 | 117.5 | 91.1 | 143.9 |
| 2021-12-01 | 119.0 | 92.6 | 145.4 |
| 2022-01-01 | 121.3 | 94.9 | 147.7 |
| 2022-02-01 | 112.9 | 86.4 | 139.3 |

Error band uses the 80th-percentile absolute CV residual (24 pooled errors), fixed across horizons and clipped at zero. It is exploratory, not a calibrated confidence interval. Annual CV horizons are 2 years, while test is 4 and projection 3; longer-horizon uncertainty is not calibrated. Final test uses development-only fit. Published projection refits selected model on all completed periods, including test, after evaluation; stored test scores are unchanged.

## additions / tv

Selected **forest_shallow** using CV MAE. Held-out test 2021-03-01 to 2021-08-01.

Test MAE **19.33**, RMSE **23.52**, sMAPE **33.17%**, MASE **1.458**. Empirical error-band coverage: 33.3%.

Last-value test MAE **20.33**; selected-model relative MAE improvement **4.9%**. 

| Test period | Actual | Predicted | Absolute error |
| --- | ---: | ---: | ---: |
| 2021-03-01 | 37 | 50.0 | 13.0 |
| 2021-04-01 | 53 | 47.9 | 5.1 |
| 2021-05-01 | 38 | 47.2 | 9.2 |
| 2021-06-01 | 83 | 47.6 | 35.4 |
| 2021-07-01 | 88 | 47.8 | 40.2 |
| 2021-08-01 | 61 | 47.8 | 13.2 |

| Candidate | CV MAE | Test MAE | Test RMSE |
| --- | ---: | ---: | ---: |
| last_value | 10.71 | 20.33 | 25.53 |
| mean_3 | 8.62 | 18.56 | 22.58 |
| drift | 11.29 | 19.03 | 23.73 |
| seasonal_naive | 14.58 | 20.83 | 26.58 |
| ridge_1 | 8.45 | 17.76 | 20.98 |
| ridge_10 | 8.04 | 18.85 | 22.53 |
| ridge_100 | 7.73 | 19.85 | 24.26 |
| forest_shallow | 7.18 | 19.33 | 23.52 |
| forest_full | 7.36 | 19.27 | 23.74 |

Test scores are displayed for transparency after the selection record was frozen; they do not reselect the model.

| Future period (historical as-of) | Projection | Lower | Upper |
| --- | ---: | ---: | ---: |
| 2021-09-01 | 68.0 | 55.3 | 80.6 |
| 2021-10-01 | 68.5 | 55.8 | 81.2 |
| 2021-11-01 | 69.8 | 57.1 | 82.5 |
| 2021-12-01 | 70.1 | 57.4 | 82.8 |
| 2022-01-01 | 67.6 | 54.9 | 80.3 |
| 2022-02-01 | 65.8 | 53.1 | 78.5 |

Error band uses the 80th-percentile absolute CV residual (24 pooled errors), fixed across horizons and clipped at zero. It is exploratory, not a calibrated confidence interval. Annual CV horizons are 2 years, while test is 4 and projection 3; longer-horizon uncertainty is not calibrated. Final test uses development-only fit. Published projection refits selected model on all completed periods, including test, after evaluation; stored test scores are unchanged.

## Limitations and interpretation

Only 21 annual periods and 80 monthly periods are modeled. Annual validation folds overlap and errors are dependent. Recency/survivorship bias, source date anomalies, catalog churn, arbitrary start windows, structural growth and policy changes limit extrapolation. Independent Movie/TV/All fits are not hierarchically reconciled, so predictions need not sum. No country/genre-specific forecasts or current-year extrapolation are claimed. A baseline winning is reported honestly; negative skill relative to a baseline remains visible.
