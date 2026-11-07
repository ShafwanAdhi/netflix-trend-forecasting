# Task 5 submission

Status: **prepared locally for private review, not externally submitted**. Active run `20261106T122211417836Z`. [Requirement matrix](../../docs/tasks/task-05/requirements.md), [report](../../reports/task-05/final_report.md), [model card](../../docs/tasks/task-05/model-card.md).

The package includes source, configs, both lockfiles, generated API contract/types, tests, actual experiment/model bundles, frozen chronology, report figures, executed notebook, seven real screenshots and recorded checks. It includes all three active task bundles so Tasks 3/4/5 work. Task 6 remains planned. Old Task 3/4 ZIPs are preserved unchanged as historical deliveries; the new verification applies to current source.

Raw/processed source CSVs, dependency folders, caches, builds, temporary output, other ZIPs and inactive runs are excluded. Aggregate series and Task 4 derived title assignments are included for serving; private review is intended, not public dataset redistribution. The bundled website needs setup/build but no raw CSV; rerunning training and the complete data-test suite needs the user's original CSV and Task 3 preparation.

## Replay, inspect and package

Start the production preview as documented at the root (`pnpm build`, then `uv run uvicorn netflix_api.main:app --host 127.0.0.1 --port 8000`). In another terminal:

```powershell
New-Item -ItemType Directory -Force output/playwright/task-05 | Out-Null
npx --yes --package @playwright/cli playwright-cli -s=trends open http://127.0.0.1:8000/tasks/5/overview --browser chrome
npx --yes --package @playwright/cli playwright-cli -s=trends run-code --filename=scripts/browser-check-forecasting.js --json | Out-File -Encoding utf8 output/playwright/task-05/browser-result.json
```

Visually inspect the seven generated PNGs before recording. The replay also downloads an actual scope/horizon forecast CSV. Then:

```powershell
uv run python scripts/verify_forecasting_submission.py --record-browser --checks --package
npx --yes --package @playwright/cli playwright-cli -s=trends close
```

The verifier refuses failed browser results, stale source hashes, missing screenshots, inconsistent model results or failed command checks. It copies actual screenshots/export, records their hashes, runs Ruff/pytest/Vitest/build, checks documentation/evidence and assembles `netflix-ml-lab-task-05.zip`. `--package` alone re-verifies existing evidence without rerunning tests. After a new training run, regenerate the notebook/report, restart the API, replay the browser and update documentation/screenshot captions with actual new results. Never invent successful evidence or simply relabel old screenshots.

## Demo sequence

1. Show Task 5 Overview, annual observed release-year trends, snapshot date, excluded partial periods and retained date discrepancies.
2. Open Forecast; explain the 2020 annual fitting endpoint, 2021–2023 historical projections and exploratory bands. Point out the annual held-out failure prominently.
3. Switch to monthly additions; explain the different target. Change Movies/TV/All and horizon, then export the actual CSV.
4. Open Evaluation. Show all candidates, CV/test separation, baseline comparisons, time windows and empirical band coverage. Monthly improvement over last value is not superiority over seasonal naive.
5. Open Methodology: past-only features, recursive forecast, selection freeze, post-test refit and retrospective snapshot bias.
6. Demonstrate mobile navigation and Tasks 3/4 regression. Task 6 is still planned.
7. Show report, notebook, model card and verification records. Predictions are neither current forecasts nor verified future outcomes.

## Portal checklist

Submit source ZIP and required completion screenshots once the official form/portal and file limits are supplied. GitHub URL is conditional and currently unavailable. Video is optional; no recording is claimed. Public hosting, external portal upload and a submission receipt have not been performed. Docker preparation includes all bundles; Engine was unavailable, so no built-container verification is claimed.
