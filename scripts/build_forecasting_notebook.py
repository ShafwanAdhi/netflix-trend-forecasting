"""Execute project-owned analysis cells against frozen model results."""

import contextlib
import io

import nbformat
from netflix_ml.shared.io import root

sources = [
    """from netflix_ml.tasks.task_05.service import load_forecasting
service = load_forecasting()
result = service.results
print('Run:', result['run_id'])
print('Snapshot:', result['snapshot_date'])
print('Entities:', result['audit']['entity_rows'])
print('Date anomalies retained:', len(result['audit']['date_anomalies']))
print('Excluded 2021 release-year cohort:', result['audit']['annual_excluded_2021'])
print('Excluded September additions:', result['audit']['monthly_excluded_september_2021'])
""",
    """import pandas as pd
for row in result['series']:
    print(row['target'], row['group'], 'selected', row['model'])
    print('Test metrics:', row['test_metrics'])
    print(pd.DataFrame([{'model':c['model'],'cv_mae':c['cv_mae'],'test_mae':c['test_metrics']['mae']} for c in row['comparison']]).to_string(index=False))
""",
    """for row in result['series']:
    print(row['target'],row['group'],'origin',row['forecast_origin'])
    print(pd.DataFrame(row['forecast']).to_string(index=False))
    print('Empirical CV band errors:',row['band_residual_count'],'test coverage:',row['test_band_coverage'])
""",
]
cells = [
    nbformat.v4.new_markdown_cell("""# Historical trend forecasting

This executed notebook reads frozen experimental outputs. Annual release-year cohorts are the primary analysis; monthly date-added cohorts are a distinct supplementary target. Neither is a complete Netflix release pipeline. Projections are relative to completed historical periods, not the current calendar date. The snapshot ends September 25, 2021; 2021 release cohorts and September additions are excluded from modeling.

Selection uses expanding chronological CV before the final test. There are no shuffled splits or future observed lag values. Final projections refit the selected model on all completed periods after evaluation. Test results remain frozen and must not be used to change the selected model.
""")
]
namespace = {}
for index, source in enumerate(sources, 1):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(source, "<project-owned-forecast-analysis>", "exec"), namespace)  # noqa: S102
    cells.append(
        nbformat.v4.new_code_cell(
            source,
            execution_count=index,
            outputs=[nbformat.v4.new_output("stream", name="stdout", text=output.getvalue())],
        )
    )
cells.append(
    nbformat.v4.new_markdown_cell("""## Interpretation and limitations

Compare each CV-selected model with last-value, drift/mean and (monthly) seasonal-naive baselines on the untouched test. A worse test result is a failure of generalization, not a reason to reselect from test scores. Annual cohorts show rapid growth followed by flattening; recursive extrapolation can amplify errors across that change. Sparse annual history and overlapping validation origins limit evidence.

The pooled 80th-percentile absolute CV residual forms an exploratory error band. It is not a calibrated interval; annual validation is two steps whereas test/projection are longer. Coverage on the independent test must be disclosed. Snapshot survivorship and retrospective backfills mean these are not true point-in-time historical archives. Separate content-type models are not reconciled and their forecasts need not sum.
""")
)
for target in ["releases", "additions"]:
    cells.append(
        nbformat.v4.new_markdown_cell(
            f"![{target} historical as-of projection](../../reports/task-05/figures/{target}-all.png)"
        )
    )
notebook = nbformat.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
        "language_info": {"name": "python", "version": "3.11"},
    },
)
path = root() / "notebooks/task-05/01_forecasting.ipynb"
path.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(notebook, path)
print(f"Executed forecast notebook: {path}")
