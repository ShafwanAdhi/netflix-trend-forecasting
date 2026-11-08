"""Source audit, predeclared rolling-origin comparison, frozen test and historical projections."""

import platform
from datetime import UTC, datetime

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from threadpoolctl import threadpool_limits

from netflix_ml.shared.dataset import validate
from netflix_ml.shared.io import digest, read_json, root, write_json
from netflix_ml.tasks.task_05.models import Forecaster, metrics

GROUPS = {"all": None, "movies": "Movie", "tv": "TV Show"}


def prepare(config):
    base = root()
    path = base / "data/raw/Dataset.csv"
    if digest(path) != config["source_sha256"]:
        raise ValueError("Source hash differs from reviewed snapshot")
    raw = pd.read_csv(path)
    validate(raw)
    raw["entity_key"] = (
        raw.title.str.strip().str.casefold() + "|" + raw.type + "|" + raw.release_year.astype(str)
    )
    seen, removed = {}, []
    for row in raw.itertuples():
        if row.entity_key in seen:
            removed.append({"removed_id": row.show_id, "retained_id": seen[row.entity_key]})
        else:
            seen[row.entity_key] = row.show_id
    frame = raw.drop_duplicates("entity_key").copy()
    dates = pd.to_datetime(frame.date_added.str.strip())
    frame["added_month"] = dates.dt.to_period("M").dt.to_timestamp()
    anomaly = frame.loc[
        dates.dt.year < frame.release_year, ["show_id", "title", "date_added", "release_year"]
    ]
    audit = {
        "source_sha256": digest(path),
        "raw_rows": len(raw),
        "entity_rows": len(frame),
        "duplicate_mapping": removed,
        "snapshot_date": dates.max().strftime("%Y-%m-%d"),
        "date_anomalies": anomaly.to_dict("records"),
        "anomaly_policy": "Retain source dates; release year may describe a later season. No chronological imputation or date correction.",
        "deduplication": "First source row per casefolded trimmed title/type/year; deterministic entity deduplication",
        "annual_excluded_2021": int(frame.release_year.eq(2021).sum()),
        "monthly_excluded_september_2021": int(frame.added_month.eq(pd.Timestamp("2021-09-01")).sum()),
    }
    series, history = {}, []
    for target, cfg in config["targets"].items():
        for group, content_type in GROUPS.items():
            subset = frame if content_type is None else frame.loc[frame.type == content_type]
            if target == "releases":
                counts = subset.groupby("release_year").size()
                index = pd.date_range(cfg["start"], cfg["end"], freq=cfg["frequency"])
                values = [int(counts.get(t.year, 0)) for t in index]
            else:
                counts = subset.groupby("added_month").size()
                index = pd.date_range(cfg["start"], cfg["end"], freq=cfg["frequency"])
                values = [int(counts.get(t, 0)) for t in index]
            value = pd.Series(values, index=index, dtype=float)
            series[f"{target}:{group}"] = value
            history.extend(
                {"target": target, "group": group, "period": t.strftime("%Y-%m-%d"), "value": int(y)}
                for t, y in value.items()
            )
    folder = base / "data/processed/task-05"
    folder.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(history).to_csv(folder / "series.csv", index=False)
    audit["series_sha256"] = digest(folder / "series.csv")
    annual = frame.groupby(["release_year", "type"]).size().unstack(fill_value=0)
    audit["release_history"] = [
        {
            "year": int(year),
            "movies": int(row.get("Movie", 0)),
            "tv": int(row.get("TV Show", 0)),
            "partial": bool(year == 2021),
        }
        for year, row in annual.iterrows()
    ]
    write_json(base / "reports/task-05/data_audit.json", audit)
    return series, audit


def points(series):
    return [{"period": t.strftime("%Y-%m-%d"), "value": float(y)} for t, y in series.items()]


def candidates(monthly):
    return (
        ["last_value", "mean_3", "drift"]
        + (["seasonal_naive"] if monthly else [])
        + ["ridge_1", "ridge_10", "ridge_100", "forest_shallow", "forest_full"]
    )


def train():
    base = root()
    config = read_json(base / "configs/task-05/experiment.json")
    series_map, audit = prepare(config)
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    bundle = base / "artifacts/task-05" / run_id
    bundle.mkdir(parents=True, exist_ok=False)
    results, selections, models, membership = [], {}, {}, []
    with threadpool_limits(limits=1):
        for key, series in series_map.items():
            target, group = key.split(":")
            cfg = config["targets"][target]
            monthly = target == "additions"
            development, test = series.iloc[: -cfg["test_size"]], series.iloc[-cfg["test_size"] :]
            comparison, residuals = [], {}
            for name in candidates(monthly):
                fold_scores, errors = [], []
                for origin in cfg["cv_origins"]:
                    fit = development.loc[:origin]
                    validation = development.loc[development.index > pd.Timestamp(origin)].iloc[
                        : cfg["cv_horizon"]
                    ]
                    if len(validation) != cfg["cv_horizon"] or validation.index[-1] >= test.index[0]:
                        raise ValueError("CV horizon intersects test or lacks observations")
                    predicted = (
                        Forecaster(name, cfg["lags"], cfg["frequency"]).fit(fit).predict(len(validation))
                    )
                    if not predicted.index.equals(validation.index):
                        raise ValueError("Forecast dates are misaligned")
                    score = metrics(validation.values, predicted.values, fit.values, 12 if monthly else 1)
                    fold_scores.append(
                        {
                            "origin": origin,
                            "fit_end": fit.index[-1].strftime("%Y-%m-%d"),
                            "validation_start": validation.index[0].strftime("%Y-%m-%d"),
                            "validation_end": validation.index[-1].strftime("%Y-%m-%d"),
                            **score,
                        }
                    )
                    errors.extend(abs(validation.values - predicted.values).tolist())
                    if name == "last_value":
                        membership.extend(
                            {
                                "series": key,
                                "origin": origin,
                                "period": date.strftime("%Y-%m-%d"),
                                "role": "fit" if date <= pd.Timestamp(origin) else "validation",
                            }
                            for date in fit.index.union(validation.index)
                        )
                residuals[name] = errors
                comparison.append(
                    {
                        "model": name,
                        "cv_mae": float(np.mean([f["mae"] for f in fold_scores])),
                        "cv_rmse": float(np.mean([f["rmse"] for f in fold_scores])),
                        "folds": fold_scores,
                    }
                )
            selected = min(comparison, key=lambda row: row["cv_mae"])
            selected_at = datetime.now(UTC).isoformat()
            selections[key] = {
                "model": selected["model"],
                "selected_at": selected_at,
                "rule": config["selection"],
                "development_end": development.index[-1].strftime("%Y-%m-%d"),
                "test_start": test.index[0].strftime("%Y-%m-%d"),
            }
            # Persist the decision before evaluating any candidate on the frozen test window.
            write_json(bundle / "selection.json", selections)
            band = float(np.quantile(residuals[selected["model"]], config["band_quantile"], method="higher"))
            test_rows = []
            selected_test = None
            for row in comparison:
                predictor = Forecaster(row["model"], cfg["lags"], cfg["frequency"]).fit(development)
                predictions = predictor.predict(len(test))
                score = metrics(test.values, predictions.values, development.values, 12 if monthly else 1)
                row["test_metrics"] = score
                if row["model"] == selected["model"]:
                    selected_test = score
                    test_rows = [
                        {
                            "period": t.strftime("%Y-%m-%d"),
                            "actual": float(test.loc[t]),
                            "predicted": float(y),
                            "lower": max(0.0, float(y) - band),
                            "upper": float(y) + band,
                        }
                        for t, y in predictions.items()
                    ]
            evaluated_at = datetime.now(UTC).isoformat()
            model = Forecaster(selected["model"], cfg["lags"], cfg["frequency"]).fit(series)
            models[key] = model
            future = [
                {
                    "period": t.strftime("%Y-%m-%d"),
                    "predicted": float(y),
                    "lower": max(0.0, float(y) - band),
                    "upper": float(y) + band,
                }
                for t, y in model.predict(cfg["horizon"]).items()
            ]
            evaluation = {
                "target": target,
                "group": group,
                "frequency": cfg["frequency"],
                "model": selected["model"],
                "history": points(series),
                "development_end": development.index[-1].strftime("%Y-%m-%d"),
                "test_start": test.index[0].strftime("%Y-%m-%d"),
                "test_end": test.index[-1].strftime("%Y-%m-%d"),
                "test": test_rows,
                "test_metrics": selected_test,
                "comparison": comparison,
                "forecast": future,
                "forecast_origin": series.index[-1].strftime("%Y-%m-%d"),
                "band_width": band,
                "band_quantile": config["band_quantile"],
                "band_residual_count": len(residuals[selected["model"]]),
                "test_band_coverage": float(
                    np.mean([r["lower"] <= r["actual"] <= r["upper"] for r in test_rows])
                ),
                "selected_at": selected_at,
                "evaluated_at": evaluated_at,
                "refit_policy": "Final test uses development-only fit. Published projection refits selected model on all completed periods, including test, after evaluation; stored test scores are unchanged.",
            }
            results.append(evaluation)
            membership.extend(
                {
                    "series": key,
                    "origin": "final",
                    "period": date.strftime("%Y-%m-%d"),
                    "role": "development" if date in development.index else "test",
                }
                for date in series.index
            )
            print(
                f"{key}: selected {selected['model']}, CV MAE {selected['cv_mae']:.2f}, test MAE {selected_test['mae']:.2f}",
                flush=True,
            )
    metadata = {
        "run_id": run_id,
        "source_sha256": audit["source_sha256"],
        "series_sha256": audit["series_sha256"],
        "config": config,
        "sklearn": sklearn.__version__,
        "python": platform.python_version(),
    }
    result = {"run_id": run_id, "snapshot_date": audit["snapshot_date"], "audit": audit, "series": results}
    joblib.dump(models, bundle / "models.joblib", compress=3)
    write_json(bundle / "metadata.json", metadata)
    write_json(bundle / "results.json", result)
    pd.DataFrame(membership).to_csv(bundle / "temporal_manifest.csv", index=False)
    (bundle / "series.csv").write_bytes((base / "data/processed/task-05/series.csv").read_bytes())
    write_json(bundle / "checksums.json", {p.name: digest(p) for p in bundle.iterdir() if p.is_file()})
    # Validate before changing the active pointer. Serving never fits a model.
    from netflix_ml.tasks.task_05.service import Forecasting

    Forecasting(bundle)
    render_report(result)
    write_json(
        base / "artifacts/task-05/active.json",
        {"run_id": run_id, "checksums_sha256": digest(bundle / "checksums.json")},
    )
    print(f"Task 5 active run: {run_id}")
    return result


def render_report(result):
    folder = root() / "reports/task-05"
    (folder / "figures").mkdir(parents=True, exist_ok=True)
    text = f"# Historical trend forecasts\n\nRun `{result['run_id']}`; snapshot {result['snapshot_date']}. Projections are historical as-of estimates, not current forecasts.\n\n"
    text += "Annual target: observed snapshot titles grouped by release year; not all Netflix releases. Monthly target: observed date-added cohorts; not original release dates. Incomplete 2021 release year and September 2021 additions are excluded. Removed titles and future backfills are absent; even older periods are not proven complete.\n\n"
    for row in result["series"]:
        text += f"## {row['target']} / {row['group']}\n\nSelected **{row['model']}** using CV MAE. Held-out test {row['test_start']} to {row['test_end']}.\n\n"
        text += f"Test MAE **{row['test_metrics']['mae']:.2f}**, RMSE **{row['test_metrics']['rmse']:.2f}**, sMAPE **{row['test_metrics']['smape']:.2f}%**, MASE **{row['test_metrics']['mase']:.3f}**. Empirical error-band coverage: {row['test_band_coverage']:.1%}.\n\n"
        naive = next(c for c in row["comparison"] if c["model"] == "last_value")
        skill = 1 - row["test_metrics"]["mae"] / naive["test_metrics"]["mae"]
        text += f"Last-value test MAE **{naive['test_metrics']['mae']:.2f}**; selected-model relative MAE improvement **{skill:.1%}**. "
        if skill < 0:
            text += "**Held-out failure: the CV winner performs worse than last value.** Earlier growth-regime validation did not predict later flattening; recursive errors amplify across the longer annual test. Retain the failure, do not reselect on test. "
        text += "\n\n| Test period | Actual | Predicted | Absolute error |\n| --- | ---: | ---: | ---: |\n"
        for p in row["test"]:
            text += f"| {p['period']} | {p['actual']:.0f} | {p['predicted']:.1f} | {abs(p['actual'] - p['predicted']):.1f} |\n"
        text += "\n| Candidate | CV MAE | Test MAE | Test RMSE |\n| --- | ---: | ---: | ---: |\n"
        for c in row["comparison"]:
            text += f"| {c['model']} | {c['cv_mae']:.2f} | {c['test_metrics']['mae']:.2f} | {c['test_metrics']['rmse']:.2f} |\n"
        text += "\nTest scores are displayed for transparency after the selection record was frozen; they do not reselect the model.\n\n| Future period (historical as-of) | Projection | Lower | Upper |\n| --- | ---: | ---: | ---: |\n"
        for p in row["forecast"]:
            text += f"| {p['period']} | {p['predicted']:.1f} | {p['lower']:.1f} | {p['upper']:.1f} |\n"
        text += f"\nError band uses the 80th-percentile absolute CV residual ({row['band_residual_count']} pooled errors), fixed across horizons and clipped at zero. It is exploratory, not a calibrated confidence interval. Annual CV horizons are 2 years, while test is 4 and projection 3; longer-horizon uncertainty is not calibrated. {row['refit_policy']}\n\n"
        fig, ax = plt.subplots(figsize=(10, 4))
        history = row["history"]
        ax.plot(
            pd.to_datetime([p["period"] for p in history]),
            [p["value"] for p in history],
            color="#333333",
            label="Observed snapshot cohorts",
        )
        future = row["forecast"]
        x = pd.to_datetime([p["period"] for p in future])
        ax.plot(
            x,
            [p["predicted"] for p in future],
            color="#b22d36",
            marker="o",
            label="Historical as-of projection",
        )
        ax.fill_between(
            x,
            [p["lower"] for p in future],
            [p["upper"] for p in future],
            color="#b22d36",
            alpha=0.14,
            label="Empirical CV error band",
        )
        ax.set(
            title=f"{row['target']} / {row['group']} — historical snapshot",
            ylabel="Observed-title cohort count",
        )
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(folder / "figures" / f"{row['target']}-{row['group']}.png", dpi=150)
        plt.close(fig)
    text += "## Limitations and interpretation\n\nOnly 21 annual periods and 80 monthly periods are modeled. Annual validation folds overlap and errors are dependent. Recency/survivorship bias, source date anomalies, catalog churn, arbitrary start windows, structural growth and policy changes limit extrapolation. Independent Movie/TV/All fits are not hierarchically reconciled, so predictions need not sum. No country/genre-specific forecasts or current-year extrapolation are claimed. A baseline winning is reported honestly; negative skill relative to a baseline remains visible.\n"
    (folder / "final_report.md").write_text(text, encoding="utf-8")
