"""Temporal leakage, snapshot coverage, saved forecast parity and HTTP behavior."""

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from netflix_api.main import create_app
from netflix_ml.shared.io import read_json, root
from netflix_ml.tasks.task_05.models import Forecaster, features, metrics
from netflix_ml.tasks.task_05.service import Forecasting, load_forecasting


@pytest.fixture(scope="module")
def service():
    return load_forecasting()


def test_temporal_manifest_and_selection(service):
    bundle = root() / "artifacts/task-05" / service.metadata["run_id"]
    manifest = pd.read_csv(bundle / "temporal_manifest.csv")
    selection = read_json(bundle / "selection.json")
    for row in service.results["series"]:
        key = f"{row['target']}:{row['group']}"
        assert selection[key]["model"] == row["model"]
        assert row["selected_at"] < row["evaluated_at"]
        assert row["model"] == min(row["comparison"], key=lambda c: c["cv_mae"])["model"]
        final = manifest[(manifest.series == key) & (manifest.origin == "final")]
        assert (
            final.loc[final.role == "development", "period"].max()
            < final.loc[final.role == "test", "period"].min()
        )
        for _, fold in manifest[(manifest.series == key) & (manifest.origin != "final")].groupby("origin"):
            assert (
                fold.loc[fold.role == "fit", "period"].max()
                < fold.loc[fold.role == "validation", "period"].min()
            )
            assert fold.period.max() < row["test_start"]


def test_partial_periods_and_scope_additivity(service):
    for target, end, count in [("releases", "2020-01-01", 21), ("additions", "2021-08-01", 80)]:
        rows = {r["group"]: r for r in service.results["series"] if r["target"] == target}
        for row in rows.values():
            assert len(row["history"]) == count and row["history"][-1]["period"] == end
            assert row["forecast"][0]["period"] > end
            assert all(
                p["predicted"] >= 0 and p["lower"] <= p["predicted"] <= p["upper"] for p in row["forecast"]
            )
        assert np.array_equal(
            [p["value"] for p in rows["all"]["history"]],
            np.array([p["value"] for p in rows["movies"]["history"]])
            + np.array([p["value"] for p in rows["tv"]["history"]]),
        )
    audit = service.results["audit"]
    assert audit["entity_rows"] == 8783 and len(audit["duplicate_mapping"]) == 7
    assert audit["annual_excluded_2021"] > 0 and audit["monthly_excluded_september_2021"] > 0


def test_recursive_forecast_saved_parity_and_test_reproduction(service):
    for row in service.results["series"]:
        key = f"{row['target']}:{row['group']}"
        history = pd.Series(
            [p["value"] for p in row["history"]], index=pd.to_datetime([p["period"] for p in row["history"]])
        )
        expected = [p["predicted"] for p in row["forecast"]]
        assert np.allclose(service.models[key].predict(len(expected)), expected)
        cfg = service.metadata["config"]["targets"][row["target"]]
        development = history.loc[: row["development_end"]]
        predicted = (
            Forecaster(row["model"], cfg["lags"], cfg["frequency"]).fit(development).predict(len(row["test"]))
        )
        assert np.allclose(predicted, [p["predicted"] for p in row["test"]])
        actual = [p["actual"] for p in row["test"]]
        score = metrics(
            actual, predicted.values, development.values, 12 if row["target"] == "additions" else 1
        )
        assert score == row["test_metrics"]
        # Altering future observations cannot enter a model already fitted on development.
        altered = history.copy()
        altered.loc[row["test_start"] :] = 1000000
        assert np.array_equal(development.values, altered.loc[: row["development_end"]].values)


def test_feature_alignment_and_metric_edges():
    history = np.arange(1, 25, dtype=float)
    row = features(history, pd.Timestamp("2020-01-01"), [1, 2, 3, 6, 12], True)
    assert row[:5] == [24, 23, 22, 19, 13]
    assert row[5] == 23 and row[6] == 24
    score = metrics([0, 0], [0, 0], [0, 0, 0], 1)
    assert score["mae"] == score["smape"] == 0 and score["mase"] is None and score["wape"] is None


def test_forecast_api_and_independent_readiness(service, monkeypatch):
    with TestClient(create_app()) as client:
        health = client.get("/api/v1/health").json()
        assert health["task_5_ready"]
        assert client.get("/api/v1/tasks").json()[0]["status"] == "ready"
        result = client.get("/api/v1/tasks/5/results").json()
        assert result["run_id"] == service.metadata["run_id"]
        for target, horizon in [("releases", 3), ("additions", 6)]:
            for group in ["all", "movies", "tv"]:
                response = client.get(
                    "/api/v1/tasks/5/forecast", params={"target": target, "group": group, "horizon": horizon}
                )
                assert response.status_code == 200 and len(response.json()["series"]["forecast"]) == horizon
        assert len(client.get("/api/v1/tasks/5/forecast?horizon=1").json()["series"]["forecast"]) == 1
        for query in [
            "target=bad",
            "group=bad",
            "horizon=0",
            "horizon=7",
            "horizon=1.5",
            "horizon=4&target=releases",
        ]:
            assert client.get(f"/api/v1/tasks/5/forecast?{query}").status_code == 422

    def unavailable():
        raise ValueError("Controlled incompatible Task 5 artifact")

    monkeypatch.setattr("netflix_api.main.load_forecasting", unavailable)
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/tasks/5/forecast").status_code == 503


def test_corrupt_forecast_bundle_refused(tmp_path):
    (tmp_path / "checksums.json").write_text('{"results.json":"invalid"}')
    (tmp_path / "results.json").write_text("{}")
    with pytest.raises(ValueError, match="integrity"):
        Forecasting(tmp_path)
