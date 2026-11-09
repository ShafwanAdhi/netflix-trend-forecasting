# Trend Forecasting: dataset card

Source: historical `Dataset.csv`, SHA-256 `90b02beeb554921f81d3b9a774d0f7766f6a65240162565f6b4082165dc2a1d3`. The audited ten-column schema is validated before preparation. The raw file is preserved. No external dataset is joined.

8,790 rows become **8,783 entities** after retaining the first row for each trimmed/casefolded title + type + release year. The seven removed-to-retained ID mappings are in [data_audit.json](../../reports/task-05/data_audit.json). Same-title/type/year collisions and unrecognized alternate spellings remain limitations.

## Two clocks

`release_year` describes the source's release cohort, not its Netflix addition date. `date_added` describes the observed catalog-entry date, not original release. Date-added spans January 2008 through **September 25, 2021**. Fourteen deduplicated records have an addition year earlier than release year; some may describe a later season. The audit lists them all. Preserve dates without inventing corrections; release-year and addition-month aggregations remain independent.

Annual modeling: **2000–2020**, 21 periods. Exclude the incomplete **2021** release cohort (592 titles). The predeclared 2000 start avoids extrapolating a modern process from sparse early film years. Full available release-year counts remain in the audit, including excluded 2021 marked partial.

Monthly modeling: **2015-01–2021-08**, 80 periods. Exclude **2021-09** (183 additions) because the source ends mid-month. Years before 2015 have sparse catalog additions and are excluded by the predeclared window. No September actual values are fed into fitting or scoring, even though the raw source contains partial observations.

Reindex to contiguous periods; absent periods become zero **observed snapshot titles**, not proof of zero actual platform activity. Sum of Movie and TV observed counts equals All Titles. Independent forecast models need not sum.

## Bias and target limitations

This is one retrospective snapshot, not archived catalog states at each backtest origin. Removed titles are absent, later backfills may change earlier cohorts, and recent releases have less observation time. Excluding partial periods does not remove survivorship/right-censoring bias. Earlier periods are not guaranteed complete. Historical-origin forecasts are experiments on this snapshot, not reconstructions of information actually available at each historical origin.

There is no release month/date, viewer demand, views, engagement, revenue or future verified release schedule. Annual observed release cohorts describe catalog composition within these bounds; additions are labelled supplementary. Forecasts beyond the historical data are unverified model outputs, never actual future counts or current-year predictions. The final test evaluates retrospective completed cohorts only.

Prepared aggregates are written to `data/processed/task-05/series.csv`; their hash is recorded in metadata and the audit. The immutable bundle contains a serving copy. Raw source CSVs are excluded from version control. Original data provenance and redistribution rights remain unverified.

## Provenance and reproduction boundary

The structured [provenance record](../../data/provenance.json) is bound to the audited source SHA-256 and is included in the generated dataset profile. **Upstream source unverified. Redistribution permission unverified.** Public candidate datasets were reviewed on 9 November 2026; none established the exact byte lineage and transformation history of this input. No upstream license is attributed to the supplied CSV.

Observed release years are 1925–2021; date-added values span 2008-01-01 through 2021-09-25. The maximum date-added value is not a known acquisition date. Acquisition date and upstream version remain unknown.

**Artifact inference** works with the bundled model without raw data. **Training reproduction** requires the exact supplied CSV with the documented hash; there is no verified public download instruction for that input. Raw CSV remains excluded from Git. Run `uv run python scripts/refresh_dataset.py` after changing an active run; the generator checks the provenance hash before emitting the profile.
