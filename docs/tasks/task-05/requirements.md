# Task 5 requirements-to-evidence matrix

Document source: supplied assignment PDF, slide 10 (Task 5) and slide 12 (submission/evaluation). Requirements are distinguished from project decisions: annual release-year and supplementary monthly targets, chosen algorithms and validation/band designs are implementation choices. The PDF sets no required numeric accuracy or score weights.

| ID | Assignment requirement | Actual implementation and evidence |
| --- | --- | --- |
| T5-01 | Prepare time-based features | Source audit, contiguous series, lag/rolling/calendar features; alignment and chronology tests |
| T5-02 | Analyze historical release patterns | Annual release-year history, source coverage, observed growth/flattening, supplementary additions, notebook/report |
| T5-03 | Build forecasting models | Eight annual/nine monthly candidate specifications, baselines, Ridge/forest fits, frozen comparison and selection |
| T5-04 | Generate future predictions | Saved historical-origin projections, 3 years/6 months, four-page website, scope/horizon controls and CSV export |
| T5-05 | Evaluate forecasting accuracy | Expanding CV, untouched chronological test, MAE/RMSE/sMAPE/WAPE/MASE, baseline and per-period error analysis, band coverage |
| SUB-01 | Project source code | ZIP with ML/API/frontend, configs, tests, schema/types, lockfiles and all three active bundles |
| SUB-02 | Screenshots of completed tasks | Seven real browser captures with captions, run ID and hashes |
| SUB-03 | GitHub link if available | Not published; conditional item, not falsely completed |
| SUB-04 | Demonstration video optional | Written demo sequence; no recording claimed |
| SUB-05 | Separate form/portal | Local ZIP and manifest; official portal not provided or used |
| EVA-01 | Task Completion | T5-01 through T5-05, website and documented source limitations |
| EVA-02 | Code Quality | Task-owned modules, generated contracts, static checks, Python/frontend tests and build |
| EVA-03 | Website Responsiveness | Desktop 1440px, tablet 768px, mobile 390px; both targets across four routes |
| EVA-04 | User Interface Design | Labelled controls, real navigation/deep links, loading/error states, focus and reduced motion |
| EVA-05 | Creativity & Implementation | Separate time concepts, baseline/failure visibility, historical-origin labeling and scoped CSV export |
| EVA-06 | Professional Presentation | English report, executed notebook, dataset/model cards, indexed evidence and demo |
| EVA-07 | Project Functionality | Validated bundles, actual API forecasts, bounded inputs and Tasks 3/4 regression checks |

Implemented: all workflow steps, real results, tests and local packaging. Verified outcomes are recorded in submission JSON files, not inferred from this checklist. Annual model performance is a documented failure; task completion does not imply good predictive performance. Task 6 is independently implemented as historical catalog-entry analytics. Current forecasting, calibrated uncertainty, new data acquisition, GitHub/video/public hosting and portal submission remain outside this release.
