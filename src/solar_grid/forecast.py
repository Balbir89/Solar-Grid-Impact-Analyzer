"""Chronological selection and untouched holdout; observed past lags only."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from solar_grid.config import Config
from solar_grid.warehouse import FEATURES


def scores(actual, predicted) -> dict:
    return {
        "mae_kw": float(mean_absolute_error(actual, predicted)),
        "rmse_kw": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)),
    }


def fit_model(frame, config, leaf):
    model = RandomForestRegressor(
        n_estimators=config.n_estimators,
        max_depth=16,
        min_samples_leaf=leaf,
        random_state=config.seed,
        n_jobs=2,
    )
    model.fit(frame[FEATURES], frame.target_kw)
    return model


def evaluate(frame: pd.DataFrame, config: Config):
    train = frame[frame.timestamp < pd.Timestamp(config.train_end, tz="UTC")]
    validation = frame[
        (frame.timestamp >= pd.Timestamp(config.train_end, tz="UTC"))
        & (frame.timestamp < pd.Timestamp(config.test_start, tz="UTC"))
    ]
    test = frame[frame.timestamp >= pd.Timestamp(config.test_start, tz="UTC")]
    if min(len(train), len(validation), len(test)) < 168:
        raise ValueError("Each temporal partition requires at least one week")
    candidates = []
    for leaf in (4, 12):
        model = fit_model(train, config, leaf)
        candidates.append(
            {
                "min_samples_leaf": leaf,
                **scores(validation.target_kw, model.predict(validation[FEATURES])),
            }
        )
    chosen = min(candidates, key=lambda r: r["mae_kw"])["min_samples_leaf"]
    development = frame[frame.timestamp < pd.Timestamp(config.test_start, tz="UTC")]
    model = fit_model(development, config, chosen)
    predictions = test[["timestamp", "target_kw"]].copy()
    predictions["random_forest_kw"] = model.predict(test[FEATURES])
    predictions["previous_hour_kw"] = test.net_lag_1
    predictions["previous_day_kw"] = test.net_lag_24
    predictions["previous_week_kw"] = test.net_lag_168
    metrics = {
        name.removesuffix("_kw"): scores(test.target_kw, predictions[name])
        for name in ("random_forest_kw", "previous_hour_kw", "previous_day_kw", "previous_week_kw")
    }
    backtests = []
    for fraction in (0.55, 0.70, 0.85):
        cut = int(len(development) * fraction)
        end = min(cut + 24 * 30, len(development))
        fold_train, fold_test = development.iloc[:cut], development.iloc[cut:end]
        fold_model = fit_model(fold_train, config, 4)
        backtests.append(
            {
                "train_last": str(fold_train.timestamp.iloc[-1]),
                "test_first": str(fold_test.timestamp.iloc[0]),
                "test_last": str(fold_test.timestamp.iloc[-1]),
                "rows": len(fold_test),
                "random_forest": scores(
                    fold_test.target_kw, fold_model.predict(fold_test[FEATURES])
                ),
                "previous_day": scores(fold_test.target_kw, fold_test.net_lag_24),
            }
        )
    validation_preds = fit_model(train, config, chosen).predict(validation[FEATURES])
    radius = float(np.quantile(np.abs(validation.target_kw - validation_preds), 0.9))
    predictions["lower_kw"] = predictions.random_forest_kw - radius
    predictions["upper_kw"] = predictions.random_forest_kw + radius
    coverage = float(
        (
            (predictions.target_kw >= predictions.lower_kw)
            & (predictions.target_kw <= predictions.upper_kw)
        ).mean()
    )
    report = {
        "horizon_hours": 1,
        "feature_count": len(FEATURES),
        "train_rows": len(train),
        "validation_rows": len(validation),
        "test_rows": len(test),
        "test_start": str(test.timestamp.iloc[0]),
        "test_end": str(test.timestamp.iloc[-1]),
        "validation_candidates": candidates,
        "selected_min_samples_leaf": chosen,
        "test_metrics": metrics,
        "development_backtests": backtests,
        "diagnostic_interval": {
            "validation_abs_error_p90_kw": radius,
            "test_coverage": coverage,
            "note": "Empirical diagnostic band; no future coverage guarantee.",
        },
        "feature_importance": dict(zip(FEATURES, model.feature_importances_.tolist())),
    }
    return report, predictions
