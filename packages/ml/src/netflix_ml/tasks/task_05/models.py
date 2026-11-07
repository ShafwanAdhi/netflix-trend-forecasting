"""Recursive forecasting: features at time t inspect observations strictly before t."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def features(history, date, lags, monthly):
    values = list(history)
    row = [values[-lag] for lag in lags]
    row += [np.mean(values[-3:]), len(values)]
    if monthly:
        row += [
            np.mean(values[-12:]),
            np.sin(2 * np.pi * date.month / 12),
            np.cos(2 * np.pi * date.month / 12),
        ]
    return row


class Forecaster:
    def __init__(self, name, lags, frequency):
        self.name, self.lags, self.frequency = name, lags, frequency

    def fit(self, series):
        self.history_ = series.to_numpy(dtype=float).tolist()
        self.last_date_ = series.index[-1]
        self.model_ = None
        if self.name.startswith(("ridge_", "forest_")):
            rows, labels = [], []
            for i in range(max(self.lags), len(series)):
                rows.append(
                    features(series.iloc[:i].values, series.index[i], self.lags, self.frequency == "MS")
                )
                labels.append(float(series.iloc[i]))
            if len(rows) < 3:
                raise ValueError("Insufficient chronological fitting rows")
            if self.name.startswith("ridge_"):
                self.model_ = make_pipeline(StandardScaler(), Ridge(alpha=float(self.name.split("_")[1])))
            else:
                depth = 3 if self.name == "forest_shallow" else None
                self.model_ = RandomForestRegressor(
                    n_estimators=120, max_depth=depth, min_samples_leaf=2, random_state=42, n_jobs=1
                )
            self.model_.fit(rows, labels)
        return self

    def predict(self, horizon):
        dates = pd.date_range(self.last_date_, periods=horizon + 1, freq=self.frequency)[1:]
        history, predictions = self.history_.copy(), []
        for i, date in enumerate(dates, 1):
            if self.model_ is not None:
                value = self.model_.predict([features(history, date, self.lags, self.frequency == "MS")])[0]
            elif self.name == "last_value":
                value = self.history_[-1]
            elif self.name == "mean_3":
                value = np.mean(self.history_[-3:])
            elif self.name == "drift":
                value = self.history_[-1] + i * (self.history_[-1] - self.history_[0]) / (
                    len(self.history_) - 1
                )
            elif self.name == "seasonal_naive":
                value = history[-12]
            else:
                raise ValueError("Unknown candidate")
            value = max(0.0, float(value))
            history.append(value)
            predictions.append(value)
        return pd.Series(predictions, index=dates)


def metrics(actual, predicted, training, seasonal_lag):
    actual, predicted = np.asarray(actual, dtype=float), np.asarray(predicted, dtype=float)
    errors = actual - predicted
    denominator = np.abs(actual) + np.abs(predicted)
    smape = np.divide(200 * np.abs(errors), denominator, out=np.zeros_like(errors), where=denominator > 0)
    scale = float(np.mean(np.abs(np.asarray(training)[seasonal_lag:] - np.asarray(training)[:-seasonal_lag])))
    return {
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(errors**2))),
        "smape": float(smape.mean()),
        "wape": float(np.abs(errors).sum() / np.abs(actual).sum()) if np.abs(actual).sum() else None,
        "mase": float(np.mean(np.abs(errors)) / scale) if scale else None,
    }
