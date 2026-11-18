from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from solar_grid.config import Config
from solar_grid.data import simulate
from solar_grid.forecast import evaluate
from solar_grid.warehouse import create_warehouse, features


@pytest.fixture(scope="module")
def built():
    config = replace(
        Config(),
        start="2023-01-01",
        train_end="2023-05-01",
        test_start="2023-06-01",
        end_exclusive="2023-07-01",
        n_estimators=4,
    )
    conn = create_warehouse(simulate(config))
    try:
        frame = features(conn)
    finally:
        conn.close()
    return config, frame


def test_partitioning_and_all_baselines(built):
    config, frame = built
    report, predictions = evaluate(frame, config)
    assert report["train_rows"] + report["validation_rows"] + report["test_rows"] == len(frame)
    assert predictions.timestamp.min() >= pd.Timestamp(config.test_start, tz="UTC")
    assert set(report["test_metrics"]) == {
        "random_forest",
        "previous_day",
        "previous_hour",
        "previous_week",
    }
    assert np.isfinite(predictions.select_dtypes("number")).all().all()
    for fold in report["development_backtests"]:
        assert pd.Timestamp(fold["train_last"]) < pd.Timestamp(fold["test_first"])
        assert pd.Timestamp(fold["test_last"]) < pd.Timestamp(config.test_start, tz="UTC")


def test_test_labels_cannot_change_selection_or_predictions(built):
    config, frame = built
    first, original = evaluate(frame, config)
    tampered = frame.copy()
    tampered.loc[tampered.timestamp >= pd.Timestamp(config.test_start, tz="UTC"), "target_kw"] += (
        10000
    )
    second, changed = evaluate(tampered, config)
    assert first["selected_min_samples_leaf"] == second["selected_min_samples_leaf"]
    np.testing.assert_allclose(original.random_forest_kw, changed.random_forest_kw)
