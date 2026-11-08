"""Typed Task 5 historical forecasting contracts; no runtime training."""

from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel


class HistoricalPoint(BaseModel):
    period: str
    value: float


class ForecastPoint(BaseModel):
    period: str
    predicted: float
    lower: float
    upper: float


class BacktestPoint(ForecastPoint):
    actual: float


class ForecastMetrics(BaseModel):
    mae: float
    rmse: float
    smape: float
    wape: float | None
    mase: float | None


class TemporalFold(ForecastMetrics):
    origin: str
    fit_end: str
    validation_start: str
    validation_end: str


class ForecastCandidate(BaseModel):
    model: str
    cv_mae: float
    cv_rmse: float
    folds: list[TemporalFold]
    test_metrics: ForecastMetrics


class ForecastSeries(BaseModel):
    target: Literal["releases", "additions"]
    group: Literal["all", "movies", "tv"]
    frequency: str
    model: str
    history: list[HistoricalPoint]
    development_end: str
    test_start: str
    test_end: str
    test: list[BacktestPoint]
    test_metrics: ForecastMetrics
    comparison: list[ForecastCandidate]
    forecast: list[ForecastPoint]
    forecast_origin: str
    band_width: float
    band_quantile: float
    band_residual_count: int
    test_band_coverage: float
    selected_at: str
    evaluated_at: str
    refit_policy: str


class DuplicatePair(BaseModel):
    removed_id: str
    retained_id: str


class DateAnomaly(BaseModel):
    show_id: str
    title: str
    date_added: str
    release_year: int


class ReleaseCohort(BaseModel):
    year: int
    movies: int
    tv: int
    partial: bool


class ForecastAudit(BaseModel):
    source_sha256: str
    raw_rows: int
    entity_rows: int
    duplicate_mapping: list[DuplicatePair]
    snapshot_date: str
    date_anomalies: list[DateAnomaly]
    anomaly_policy: str
    deduplication: str
    annual_excluded_2021: int
    monthly_excluded_september_2021: int
    series_sha256: str
    release_history: list[ReleaseCohort]


class ForecastResults(BaseModel):
    run_id: str
    snapshot_date: str
    audit: ForecastAudit
    series: list[ForecastSeries]


class ForecastResponse(BaseModel):
    run_id: str
    snapshot_date: str
    series: ForecastSeries


router = APIRouter(prefix="/api/v1/tasks/5", tags=["Forecasting"])


def service(request):
    value = getattr(request.app.state, "forecasting", None)
    if value is None:
        raise HTTPException(
            503, detail="Validated forecast artifacts are unavailable. Run train_forecasting.py first."
        )
    return value


@router.get("/results", response_model=ForecastResults)
def results(request: Request):
    return service(request).results


@router.get("/forecast", response_model=ForecastResponse)
def forecast(
    request: Request,
    target: Literal["releases", "additions"] = "releases",
    group: Literal["all", "movies", "tv"] = "all",
    horizon: int | None = Query(default=None, ge=1, le=6),
):
    value = service(request).results
    row = next(row for row in value["series"] if row["target"] == target and row["group"] == group)
    if horizon is not None and horizon > len(row["forecast"]):
        raise HTTPException(422, detail="Requested horizon exceeds the frozen forecast for this target")
    return {
        "run_id": value["run_id"],
        "snapshot_date": value["snapshot_date"],
        "series": {**row, "forecast": row["forecast"][:horizon] if horizon else row["forecast"]},
    }
