from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from solar_grid.config import Config
from solar_grid.data import simulate, validate_data
from solar_grid.warehouse import FEATURES, create_warehouse, features, query


@pytest.fixture
def data():
    return simulate(Config()).iloc[:240].copy()


def test_deterministic_simulation():
    pd.testing.assert_frame_equal(simulate(Config()), simulate(Config()))
    assert len(simulate(Config())) == 17544


@pytest.mark.parametrize("change", ["duplicate", "gap", "nan", "negative", "unsorted", "naive"])
def test_invalid_input_is_rejected(data, change):
    if change == "duplicate":
        data.loc[1, "timestamp"] = data.loc[0, "timestamp"]
    elif change == "gap":
        data = data.drop(index=10)
    elif change == "nan":
        data.loc[5, "demand_kw"] = np.nan
    elif change == "negative":
        data.loc[5, "solar_kw"] = -1
    elif change == "unsorted":
        data = data.iloc[::-1]
    else:
        data["timestamp"] = data.timestamp.dt.tz_localize(None)
    with pytest.raises(ValueError):
        validate_data(data)


def test_negative_prices_are_valid(data):
    data.loc[10, "import_eur_kwh"] = -0.1
    validate_data(data)


def test_sql_kpis_reconcile(data):
    conn = create_warehouse(data)
    try:
        quality = query(conn, "quality_checks").iloc[0]
        assert quality.rows_checked == len(data)
        assert quality.balance_failures == quality.simultaneous_import_export == 0
        monthly = query(conn, "monthly_kpis")
        net = data.demand_kw - data.solar_kw
        assert monthly.solar_only_import_kwh.sum() == pytest.approx(net.clip(lower=0).sum())
        assert monthly.solar_only_cost_eur.sum() == pytest.approx(
            (
                net.clip(lower=0) * data.import_eur_kwh - (-net).clip(lower=0) * data.export_eur_kwh
            ).sum()
        )
    finally:
        conn.close()


def feature_frame(data):
    conn = create_warehouse(data)
    try:
        return features(conn)
    finally:
        conn.close()


def test_features_do_not_read_target_or_future(data):
    before = feature_frame(data)
    target_time = data.timestamp.iloc[200]
    altered = data.copy()
    altered.loc[altered.timestamp >= target_time, "demand_kw"] += 10000
    after = feature_frame(altered)
    row = before.timestamp == target_time
    pd.testing.assert_frame_equal(before.loc[row, FEATURES], after.loc[row, FEATURES])
    assert after.loc[row, "target_kw"].iloc[0] != before.loc[row, "target_kw"].iloc[0]


def test_lag_and_rolling_boundaries(data):
    built = feature_frame(data).iloc[0]
    net = data.demand_kw - data.solar_kw
    assert built.net_lag_1 == pytest.approx(net.iloc[167])
    assert built.net_lag_168 == pytest.approx(net.iloc[0])
    assert built.net_mean_24 == pytest.approx(net.iloc[144:168].mean())


@pytest.mark.parametrize(
    "changes",
    [
        {"charge_efficiency": 0},
        {"discharge_efficiency": 1.2},
        {"battery_capacity_kwh": -1},
        {"discount_rate": float("nan")},
        {"test_start": "2022-01-01"},
        {"n_estimators": 0},
        {"seed": -1},
    ],
)
def test_invalid_configuration(changes):
    with pytest.raises(ValueError):
        replace(Config(), **changes).validate()
