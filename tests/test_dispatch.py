from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from solar_grid.config import Config
from solar_grid.data import simulate
from solar_grid.dispatch import dispatch, economics, verify_dispatch


def tiny_day():
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-07-01", periods=24, freq="h", tz="UTC"),
            "demand_kw": [10.0] * 24,
            "solar_kw": [0.0] * 10 + [50.0] * 5 + [0.0] * 9,
            "import_eur_kwh": [0.3] * 24,
            "export_eur_kwh": [0.05] * 24,
        }
    )


def test_energy_balance_and_limits():
    config = replace(Config(), battery_capacity_kwh=50, battery_power_kw=20)
    result = dispatch(tiny_day(), config)
    assert result.soc_kwh.max() <= 50 + 1e-7
    assert result.charge_kw.max() <= 20 + 1e-7
    assert result.discharge_kw.max() <= 20 + 1e-7
    assert result.charge_kw.sum() - result.discharge_kw.sum() == pytest.approx(
        result.loss_kwh.sum() + result.soc_kwh.iloc[-1]
    )
    assert result.loc[result.timestamp.dt.hour < 17, "discharge_kw"].sum() == 0


def test_zero_battery_matches_baseline():
    config = replace(Config(), battery_capacity_kwh=0)
    result = dispatch(tiny_day(), config)
    assert result.charge_kw.sum() == result.discharge_kw.sum() == 0
    assert result.operating_savings_eur.sum() == pytest.approx(0)
    assert economics(result, config)["npv_eur"] == pytest.approx(0)


def test_battery_has_no_free_initial_energy():
    data = tiny_day()
    data["solar_kw"] = 0.0
    result = dispatch(data, Config())
    assert result.discharge_kw.sum() == 0


def test_charge_cannot_use_grid_power():
    data = tiny_day()
    result = dispatch(data, Config())
    assert np.all(result.charge_kw <= (data.solar_kw - data.demand_kw).clip(lower=0) + 1e-7)


def test_tampered_balance_is_rejected():
    result = dispatch(tiny_day(), Config())
    result.loc[5, "grid_import_kw"] += 1
    with pytest.raises(ValueError, match="conservation"):
        verify_dispatch(result, Config())


def test_terminal_soc_has_no_revenue_credit():
    data = tiny_day().iloc[:16]
    config = Config()
    result = dispatch(data, config)
    report = economics(result, config)
    assert report["end_soc_kwh"] > 0
    assert report["annual_operating_savings_eur"] < 0
    assert report["simple_payback_years"] is None


def test_carbon_accounts_for_lost_export():
    config = Config()
    result = dispatch(tiny_day(), config)
    report = economics(result, config)
    assert report["site_import_emissions_reduction_tonnes"] > 0
    assert report["net_emissions_reduction_with_export_credit_tonnes"] < 0


def test_full_year_dispatch_conserves_energy():
    config = Config()
    frame = simulate(config)
    result = dispatch(frame[frame.timestamp.dt.year == 2024], config)
    assert len(result) == 8784
    assert result.charge_kw.sum() == pytest.approx(
        result.discharge_kw.sum() + result.loss_kwh.sum() + result.soc_kwh.iloc[-1]
    )
