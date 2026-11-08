import { useSearchParams, Link } from "react-router";
import { DATA_COLORS } from "../../lib/dataColors";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Note, PageHeading, RunStamp, State } from "../../components/Shared";
import { useForecastResults, useForecast, modelName } from "../../lib/api";
import type { ForecastResults, ForecastSeries } from "../../lib/api";

const number = (value: number) =>
  value.toLocaleString("en-US", { maximumFractionDigits: 1 });
const period = (value: string, annual: boolean) =>
  value.slice(0, annual ? 4 : 7);
function validHorizon(value: string | null, limit: number) {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0
    ? Math.min(parsed, limit)
    : limit;
}
function useSelection() {
  const [params, setParams] = useSearchParams();
  const target =
    params.get("target") === "additions" ? "additions" : "releases";
  const group = ["movies", "tv"].includes(params.get("group") ?? "")
    ? params.get("group")!
    : "all";
  return { params, setParams, target, group };
}
function Controls({ horizonControl = false }: { horizonControl?: boolean }) {
  const { params, setParams, target, group } = useSelection();
  const limit = target === "releases" ? 3 : 6;
  const h = validHorizon(params.get("horizon"), limit);
  return (
    <div className="forecast-controls">
      <label htmlFor="forecast-target">Time target</label>
      <select
        id="forecast-target"
        value={target}
        onChange={(e) => setParams({ target: e.target.value, group })}
      >
        <option value="releases">Annual release-year cohorts</option>
        <option value="additions">Monthly catalog additions</option>
      </select>
      <label htmlFor="forecast-group">Content scope</label>
      <select
        id="forecast-group"
        value={group}
        onChange={(e) => setParams({ target, group: e.target.value })}
      >
        <option value="all">All titles</option>
        <option value="movies">Movies</option>
        <option value="tv">TV Shows</option>
      </select>
      {horizonControl && (
        <>
          <label htmlFor="forecast-horizon">Forecast horizon</label>
          <select
            id="forecast-horizon"
            value={Math.max(1, Math.min(limit, h))}
            onChange={(e) =>
              setParams({ target, group, horizon: e.target.value })
            }
          >
            {Array.from({ length: limit }, (_, i) => (
              <option key={i + 1} value={i + 1}>
                {i + 1} {target === "releases" ? "year" : "month"}
                {i > 0 ? "s" : ""}
              </option>
            ))}
          </select>
        </>
      )}
    </div>
  );
}
function TargetNote({ annual }: { annual: boolean }) {
  return (
    <Note>
      {annual
        ? "Release-year counts describe titles present in this snapshot, not the complete Netflix release pipeline. The incomplete 2021 cohort is excluded. Older cohorts also have survivorship and backfill bias."
        : "Date added measures entry into the observed catalog, not original release. September 2021 is excluded as incomplete. Removed titles and later backfills are absent from this snapshot."}{" "}
      All projections are historical as-of estimates, not current forecasts.
    </Note>
  );
}
function Chart({ row, test = false }: { row: ForecastSeries; test?: boolean }) {
  const annual = row.target === "releases";
  const hasProjection = test || row.forecast.length > 0;
  const data = test
    ? row.test.map((p) => ({
        date: period(p.period, annual),
        observed: p.actual,
        projection: p.predicted,
        band: [p.lower, p.upper],
      }))
    : [
        ...row.history.map((p, i) => ({
          date: period(p.period, annual),
          observed: p.value,
          projection: i === row.history.length - 1 ? p.value : undefined,
          band: undefined as number[] | undefined,
        })),
        ...row.forecast.map((p) => ({
          date: period(p.period, annual),
          observed: undefined,
          projection: p.predicted,
          band: [p.lower, p.upper],
        })),
      ];
  return (
    <div
      className="forecast-chart"
      data-motion-revision={`${row.target}-${row.group}-${row.forecast.length}-${test}`}
      role="img"
      aria-label={
        test
          ? "Chronological test: observed versus selected-model prediction"
          : hasProjection
            ? "Observed historical cohorts and historical as-of projections with empirical error band"
            : "Observed historical snapshot cohort counts"
      }
    >
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={data}
          margin={{ top: 20, right: 15, bottom: 20, left: 5 }}
        >
          <CartesianGrid
            stroke="#d0d0d0"
            strokeDasharray="3 4"
            vertical={false}
          />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} minTickGap={28} />
          <YAxis tick={{ fontSize: 12 }} width={50} />
          <Tooltip
            formatter={(value) =>
              Array.isArray(value)
                ? value.map((v) => number(Number(v))).join(" – ")
                : number(Number(value))
            }
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {hasProjection && (
            <Area
              dataKey="band"
              name="Empirical CV error band"
              stroke="none"
              fill={DATA_COLORS.band}
              fillOpacity={0.65}
              isAnimationActive={false}
            />
          )}
          <Line
            dataKey="observed"
            name="Observed snapshot cohort"
            stroke={DATA_COLORS.observed}
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
          {hasProjection && (
            <Line
              dataKey="projection"
              name={
                test
                  ? "Selected model, development fit"
                  : "Selected model, full-history refit"
              }
              stroke={DATA_COLORS.projected}
              strokeWidth={2.5}
              strokeDasharray="5 3"
              dot={{ r: 3 }}
              isAnimationActive={false}
            />
          )}
          {!test && hasProjection && (
            <ReferenceLine
              x={period(row.forecast_origin, annual)}
              stroke="#000000"
              strokeDasharray="3 4"
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
function ModelWarning({ row }: { row: ForecastSeries }) {
  const naive = row.comparison.find((c) => c.model === "last_value")!;
  const skill = 1 - row.test_metrics.mae / naive.test_metrics.mae;
  return (
    <aside
      className={`forecast-skill ${skill < 0 ? "forecast-failure" : ""}`}
      role="note"
    >
      <strong>
        {skill < 0
          ? "Held-out warning: worse than last-value baseline."
          : "Held-out comparison with last-value baseline."}
      </strong>
      <p>
        Selected-model MAE {number(row.test_metrics.mae)} titles; last-value MAE{" "}
        {number(naive.test_metrics.mae)}. Relative MAE improvement:{" "}
        {number(skill * 100)}%.{" "}
        {skill < 0
          ? "The CV winner did not generalize across the test regime. The model was not reselected from test scores; projections remain exploratory."
          : "This single short test window is limited evidence. Other baselines and complete scores remain visible in Evaluation."}
      </p>
    </aside>
  );
}
function selectRow(data: ForecastResults, target: string, group: string) {
  return data.series.find((r) => r.target === target && r.group === group)!;
}
export function ForecastOverview() {
  const { data, error, isPending } = useForecastResults();
  const { target, group } = useSelection();
  if (!data) return <State error={error} loading={isPending} />;
  const row = selectRow(data, target, group);
  const annual = target === "releases";
  return (
    <>
      <PageHeading
        eyebrow="TIME SERIES"
        title="Historical trends, explicit forecast limits."
        action={
          <Link className="button" to="/forecast">
            Explore forecasts
          </Link>
        }
      >
        Inspect release-year cohorts and catalog additions, then evaluate what
        the historical models could predict.
      </PageHeading>
      <Controls />
      <div className="summary-strip">
        <div>
          <span>OBSERVED ENTITIES</span>
          <strong>{data.audit.entity_rows.toLocaleString()}</strong>
          <small>
            {data.audit.raw_rows - data.audit.entity_rows} duplicate entities
            removed
          </small>
        </div>
        <div>
          <span>MODELED PERIODS</span>
          <strong>{row.history.length}</strong>
          <small>
            {annual ? "2000–2020, annual" : "2015-01–2021-08, monthly"}
          </small>
        </div>
        <div>
          <span>SNAPSHOT THROUGH</span>
          <strong className="date-value">{data.snapshot_date}</strong>
          <small>Not a current data feed</small>
        </div>
        <div>
          <span>EXCLUDED PARTIAL COHORT</span>
          <strong>
            {annual
              ? data.audit.annual_excluded_2021
              : data.audit.monthly_excluded_september_2021}
          </strong>
          <small>
            {annual ? "Titles released in 2021" : "Additions in September 2021"}
          </small>
        </div>
      </div>
      <section className="report-section">
        <p className="eyebrow">01 / HISTORICAL PATTERNS</p>
        <h2>
          {annual
            ? "Release-year cohorts in the snapshot"
            : "Monthly additions in the snapshot"}
        </h2>
        <Chart row={{ ...row, forecast: [] }} />
        <p className="section-description">
          {annual
            ? "Growth accelerates in the mid-2010s and then flattens. Counts reflect the observed catalog and its survival to the snapshot date."
            : "Monthly counts vary with catalog acquisition and reporting. Early sparse years are excluded by the predeclared 2015 start."}
        </p>
      </section>
      <section className="report-section">
        <p className="eyebrow">02 / SOURCE REVIEW</p>
        <h2>Coverage shapes the forecast.</h2>
        <div className="forecast-audit">
          <p>
            <strong>
              {data.audit.date_anomalies.length} date discrepancies retained.
            </strong>{" "}
            Some titles were added before their recorded release year,
            potentially reflecting later TV seasons. Source dates are preserved;
            no invented correction is applied.
          </p>
          <p>
            <strong>Two time concepts, independent targets.</strong> Release
            year is the primary analysis. Monthly date-added forecasts
            supplement it; they never stand in for original release dates.
          </p>
          <p>
            <strong>Snapshot backtest.</strong> Historical counts come from a
            2021 snapshot, not point-in-time catalog archives. No removed-title
            history or actual future outcomes is available.
          </p>
        </div>
      </section>
      <TargetNote annual={annual} />
      <RunStamp run={data.run_id} />
    </>
  );
}
function download(row: ForecastSeries, run: string) {
  const lines = [
    `run_id,target,group,period,predicted,lower,upper`,
    ...row.forecast.map((p) =>
      [
        run,
        row.target,
        row.group,
        p.period,
        p.predicted,
        p.lower,
        p.upper,
      ].join(","),
    ),
  ];
  const url = URL.createObjectURL(
    new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" }),
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = `trend-forecasting-${row.target}-${row.group}-${run}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}
export function ForecastWorkspace() {
  const { target, group, params } = useSelection();
  const max = target === "releases" ? 3 : 6;
  const horizon = validHorizon(params.get("horizon"), max);
  const { data, error, isPending } = useForecast(target, group, horizon);
  const row = data?.series;
  return (
    <>
      <PageHeading
        eyebrow="HISTORICAL PROJECTION"
        title="Project from a frozen historical origin."
      >
        Change the target, content scope and horizon. Each view serves a saved
        forecast; opening this page does not retrain a model.
      </PageHeading>
      <Controls horizonControl />
      {!row || !data ? (
        <State error={error} loading={isPending} />
      ) : (
        <>
          <div className="forecast-context">
            <span>
              Origin {period(row.forecast_origin, target === "releases")}
            </span>
            <span>{modelName(row.model)}</span>
            <span>{row.forecast.length} projected periods</span>
          </div>
          <Chart row={row} />
          <ModelWarning row={row} />
          <section className="report-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">FROZEN OUTPUT</p>
                <h2>Historical as-of projections</h2>
              </div>
              <button
                className="text-button"
                onClick={() => download(row, data.run_id)}
              >
                Export CSV
              </button>
            </div>
            <div
              className="table-scroll"
              tabIndex={0}
              role="region"
              aria-label="Scrollable results table"
            >
              <table className="forecast-output">
                <thead>
                  <tr>
                    <th>Period</th>
                    <th>Projected titles</th>
                    <th>Lower band</th>
                    <th>Upper band</th>
                  </tr>
                </thead>
                <tbody>
                  {row.forecast.map((p) => (
                    <tr key={p.period}>
                      <td>{period(p.period, target === "releases")}</td>
                      <td>{number(p.predicted)}</td>
                      <td>{number(p.lower)}</td>
                      <td>{number(p.upper)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          <Note>
            The shaded band is the 80th-percentile absolute CV error from{" "}
            {row.band_residual_count} pooled errors. It is exploratory, fixed
            across horizons, and clipped at zero; it is not a calibrated
            confidence interval.{" "}
            {target === "releases"
              ? "Annual CV covers two steps; the longer test and projection horizons have no calibrated uncertainty. "
              : ""}
            Independent scope models need not sum to the all-title forecast.
          </Note>
          <TargetNote annual={target === "releases"} />
          <RunStamp run={data.run_id} />
        </>
      )}
    </>
  );
}
export function ForecastEvaluation() {
  const { data, error, isPending } = useForecastResults();
  const { target, group } = useSelection();
  if (!data) return <State error={error} loading={isPending} />;
  const row = selectRow(data, target, group);
  const metric = row.test_metrics;
  return (
    <>
      <PageHeading
        eyebrow="CHRONOLOGICAL VALIDATION"
        title="Compare forecasts with what followed."
      >
        Selection uses expanding-window validation. The final test is evaluated
        once after selection, with no observed future values fed into recursive
        lags.
      </PageHeading>
      <Controls />
      <div className="selected-model">
        <span className="tag">CV-SELECTED MODEL</span>
        <strong>{modelName(row.model)}</strong>
        <span>
          Test {period(row.test_start, target === "releases")} to{" "}
          {period(row.test_end, target === "releases")}
        </span>
      </div>
      <div className="summary-strip">
        <div>
          <span>TEST MAE ↓</span>
          <strong>{number(metric.mae)}</strong>
          <small>Titles per period</small>
        </div>
        <div>
          <span>TEST RMSE ↓</span>
          <strong>{number(metric.rmse)}</strong>
          <small>Larger errors weigh more</small>
        </div>
        <div>
          <span>TEST sMAPE ↓</span>
          <strong>{number(metric.smape)}%</strong>
          <small>Symmetric percentage error</small>
        </div>
        <div>
          <span>TEST MASE ↓</span>
          <strong>
            {metric.mase === null ? "Undefined" : number(metric.mase)}
          </strong>
          <small>
            Scaled by development {target === "releases" ? "lag-1" : "lag-12"}{" "}
            error
          </small>
        </div>
      </div>
      <ModelWarning row={row} />
      <section className="report-section">
        <p className="eyebrow">01 / UNTOUCHED TEST WINDOW</p>
        <h2>Observed counts and recursive predictions</h2>
        <Chart row={row} test />
        <p className="section-description">
          Test band coverage: {number(row.test_band_coverage * 100)}% across{" "}
          {row.test.length} periods. WAPE:{" "}
          {metric.wape === null ? "undefined" : `${number(metric.wape * 100)}%`}
          . This short test is not evidence of current forecasting accuracy.
        </p>
      </section>
      <section className="report-section">
        <p className="eyebrow">02 / PREDECLARED COMPARISON</p>
        <h2>Validation chooses; test reveals limitations.</h2>
        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label="Scrollable results table"
        >
          <table className="forecast-comparison">
            <thead>
              <tr>
                <th>Candidate</th>
                <th>CV MAE</th>
                <th>CV RMSE</th>
                <th>Test MAE</th>
                <th>Test RMSE</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {row.comparison.map((c) => (
                <tr
                  key={c.model}
                  className={c.model === row.model ? "selected-row" : ""}
                >
                  <td>{modelName(c.model)}</td>
                  <td>{number(c.cv_mae)}</td>
                  <td>{number(c.cv_rmse)}</td>
                  <td>{number(c.test_metrics.mae)}</td>
                  <td>{number(c.test_metrics.rmse)}</td>
                  <td>
                    {c.model === row.model ? "Selected by CV" : "Comparison"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="section-description">
          All test comparisons are reported after freezing selection. A baseline
          may outperform the selected model on test; no retrospective
          reselection is performed.
        </p>
      </section>
      <section className="report-section">
        <p className="eyebrow">03 / EXPANDING WINDOWS</p>
        <h2>Every validation period follows its fitting history.</h2>
        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label="Scrollable results table"
        >
          <table>
            <thead>
              <tr>
                <th>Fit through</th>
                <th>Validation from</th>
                <th>Validation through</th>
                <th>Selected-model MAE</th>
              </tr>
            </thead>
            <tbody>
              {row.comparison
                .find((c) => c.model === row.model)!
                .folds.map((f) => (
                  <tr key={f.origin}>
                    <td>{period(f.fit_end, target === "releases")}</td>
                    <td>{period(f.validation_start, target === "releases")}</td>
                    <td>{period(f.validation_end, target === "releases")}</td>
                    <td>{number(f.mae)}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </section>
      <Note>
        The final projection refits the selected model on all completed periods
        after test evaluation. Test metrics above belong to the development-only
        fit, not that refitted model. Annual validation windows overlap; pooled
        CV residuals are dependent and uncertainty bands have no coverage
        guarantee.
      </Note>
      <RunStamp run={data.run_id} />
    </>
  );
}
export function ForecastMethodology() {
  const { data, error, isPending } = useForecastResults();
  if (!data) return <State error={error} loading={isPending} />;
  return (
    <>
      <PageHeading
        eyebrow="EXPERIMENT DESIGN"
        title="Respect time before fitting a trend."
      >
        The release-year target and the supplementary date-added
        target remain separate throughout preparation, validation and
        presentation.
      </PageHeading>
      <section className="method-grid">
        <div>
          <p className="eyebrow">THE WORKFLOW</p>
          <ol className="workflow">
            {[
              [
                "Audit the snapshot",
                "Verify source SHA-256, deduplicate normalized title/type/year, preserve source dates and record anomalies. Keep 2021 release cohorts and September 2021 additions out of modeling.",
              ],
              [
                "Build contiguous time series",
                "Annual observed release cohorts: 2000–2020. Monthly observed additions: 2015-01–2021-08. Reindex missing periods to zero observed snapshot titles; this does not establish a complete catalog.",
              ],
              [
                "Create strictly past-based features",
                "Annual lags 1/2/3; monthly lags 1/2/3/6/12. Trailing averages, time trend and monthly sine/cosine seasonality. Ridge scaling fits inside each origin; forest and baselines also fit past history only.",
              ],
              [
                "Compare on expanding windows",
                "Eight annual and nine monthly candidates per scope: last value, mean, drift, seasonal naive where applicable, Ridge alpha 1/10/100, shallow/full forests. Select lowest mean CV MAE; ties follow declared candidate order.",
              ],
              [
                "Freeze, test, then refit",
                "Record selection before evaluating the final four annual or six monthly periods. Recursively forecast without actual future lags. Publish errors even when a baseline wins on test; refit on completed history only afterward.",
              ],
              [
                "Explain uncertainty honestly",
                "Use pooled 80th-percentile absolute CV errors for an exploratory band. Report test coverage. Annual two-step CV does not calibrate longer horizons; dependent residuals and structural changes weaken uncertainty claims.",
              ],
            ].map(([heading, text], i) => (
              <li key={heading}>
                <span>0{i + 1}</span>
                <div>
                  <h2>{heading}</h2>
                  <p>{text}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
        <aside className="method-aside">
          <h2>A historical experiment.</h2>
          <p>
            The data ends {data.snapshot_date}. Annual projections begin in
            2021; monthly projections begin in September 2021. They are future
            relative to their fitting origins, not relative to today.
          </p>
          <h3>What is actually forecast?</h3>
          <p>
            Observed titles in the supplied snapshot, grouped by release year or
            catalog-entry month. Audience demand, revenue, original release
            schedules and total platform releases are unobserved.
          </p>
          <h3>Why can the annual model fail?</h3>
          <p>
            The short series grows rapidly before flattening. Earlier CV rewards
            extrapolation; the later test can reverse that ranking. Recursive
            forecasts compound errors. The failed annual backtest is retained
            visibly.
          </p>
          <h3>Can scope predictions be added?</h3>
          <p>
            All-title, Movie and TV models are independent and not reconciled.
            Their projected counts need not sum, although observed counts do.
          </p>
          <h3>Are these true historical archives?</h3>
          <p>
            No. Retrospective cohorts share the same 2021 snapshot. Backfills
            and removed titles prevent a point-in-time reconstruction;
            chronological splitting alone does not remove that bias.
          </p>
        </aside>
      </section>
      <RunStamp run={data.run_id} />
    </>
  );
}
