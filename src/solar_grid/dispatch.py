"""Hourly reactive dispatch with explicit energy conservation and economics."""

from dataclasses import replace

import numpy as np
import pandas as pd

from solar_grid.config import Config


def dispatch(frame: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Store surplus PV; discharge at 17:00–21:59 UTC into on-site demand only.

    Initial SOC is zero. No grid charging or battery export. Ending SOC is
    carried as unused energy with zero terminal revenue, never free cash.
    """
    config.validate()
    soc, records = 0.0, []
    for row in frame.itertuples(index=False):
        net = row.demand_kw - row.solar_kw
        charge = discharge = 0.0
        if net < 0:
            charge = max(
                0.0,
                min(
                    -net,
                    config.battery_power_kw,
                    (config.battery_capacity_kwh - soc) / config.charge_efficiency,
                ),
            )
        elif (
            17 <= row.timestamp.hour < 22
            and row.import_eur_kwh > config.throughput_cost_eur_per_kwh
        ):
            discharge = max(
                0.0, min(net, config.battery_power_kw, soc * config.discharge_efficiency)
            )
        soc += charge * config.charge_efficiency - discharge / config.discharge_efficiency
        grid_import = max(0.0, net - discharge)
        grid_export = max(0.0, -net - charge)
        baseline_cost = max(net, 0) * row.import_eur_kwh - max(-net, 0) * row.export_eur_kwh
        energy_cost = grid_import * row.import_eur_kwh - grid_export * row.export_eur_kwh
        wear = discharge * config.throughput_cost_eur_per_kwh
        loss = charge * (1 - config.charge_efficiency) + discharge * (
            1 / config.discharge_efficiency - 1
        )
        records.append(
            {
                "timestamp": row.timestamp,
                "demand_kw": row.demand_kw,
                "solar_kw": row.solar_kw,
                "charge_kw": charge,
                "discharge_kw": discharge,
                "soc_kwh": soc,
                "grid_import_kw": grid_import,
                "grid_export_kw": grid_export,
                "loss_kwh": loss,
                "baseline_cost_eur": baseline_cost,
                "energy_cost_eur": energy_cost,
                "wear_cost_eur": wear,
                "operating_savings_eur": baseline_cost - energy_cost - wear,
            }
        )
    result = pd.DataFrame(records)
    verify_dispatch(result, config)
    return result


def verify_dispatch(result: pd.DataFrame, config: Config) -> None:
    if result.empty:
        raise ValueError("Dispatch requires at least one hour")
    balance = (
        result.solar_kw
        + result.grid_import_kw
        + result.discharge_kw
        - (result.demand_kw + result.grid_export_kw + result.charge_kw)
    )
    soc_before = result.soc_kwh.shift(1, fill_value=0)
    soc_balance = (
        result.soc_kwh
        - soc_before
        - (
            result.charge_kw * config.charge_efficiency
            - result.discharge_kw / config.discharge_efficiency
        )
    )
    if not np.allclose(balance, 0, atol=1e-7) or not np.allclose(soc_balance, 0, atol=1e-7):
        raise ValueError("Energy conservation failed")
    if ((result.soc_kwh < -1e-7) | (result.soc_kwh > config.battery_capacity_kwh + 1e-7)).any():
        raise ValueError("Battery capacity exceeded")
    if (result[["charge_kw", "discharge_kw"]] > config.battery_power_kw + 1e-7).any().any():
        raise ValueError("Power limit exceeded")
    if ((result.charge_kw > 1e-7) & (result.discharge_kw > 1e-7)).any():
        raise ValueError("Simultaneous charge and discharge")


def economics(result: pd.DataFrame, config: Config) -> dict:
    # Annualize observed hours to a 365.25-day year; label this convention explicitly.
    factor = 365.25 * 24 / len(result)
    annual_operating_savings = float(result.operating_savings_eur.sum()) * factor
    capex = config.battery_capacity_kwh * config.battery_capex_eur_per_kwh
    annual_opex = capex * config.annual_opex_fraction
    annual_net = annual_operating_savings - annual_opex
    cashflows = [-capex] + [
        annual_operating_savings * (1 - config.annual_savings_decline) ** (year - 1) - annual_opex
        for year in range(1, config.project_years + 1)
    ]
    npv = sum(cash / (1 + config.discount_rate) ** year for year, cash in enumerate(cashflows))
    direct_import_avoided = float(result.discharge_kw.sum())
    # Export is credited with the SAME displacement factor as import. Lost export
    # must be deducted, otherwise storage carbon benefits would be overstated.
    credited_net_avoided = direct_import_avoided - float(result.charge_kw.sum())
    return {
        "observed_hours": len(result),
        "annualization_factor": factor,
        "baseline_cost_eur": float(result.baseline_cost_eur.sum()),
        "battery_energy_cost_eur": float(result.energy_cost_eur.sum()),
        "wear_cost_eur": float(result.wear_cost_eur.sum()),
        "annual_operating_savings_eur": annual_operating_savings,
        "annual_opex_eur": annual_opex,
        "annual_net_savings_eur": annual_net,
        "capex_eur": capex,
        "npv_eur": npv,
        "project_years": config.project_years,
        "simple_payback_years": capex / annual_net if annual_net > 0 and capex > 0 else None,
        "peak_import_kw": float(result.grid_import_kw.max()),
        "baseline_peak_import_kw": float(np.maximum(result.demand_kw - result.solar_kw, 0).max()),
        "charge_kwh": float(result.charge_kw.sum()),
        "discharge_kwh": direct_import_avoided,
        "loss_kwh": float(result.loss_kwh.sum()),
        "end_soc_kwh": float(result.soc_kwh.iloc[-1]),
        "site_import_emissions_reduction_tonnes": direct_import_avoided
        * config.grid_carbon_kg_per_kwh
        / 1000,
        "net_emissions_reduction_with_export_credit_tonnes": credited_net_avoided
        * config.grid_carbon_kg_per_kwh
        / 1000,
        "cashflows_eur": cashflows,
    }


def sensitivity(frame: pd.DataFrame, config: Config) -> list[dict]:
    rows = []
    for capacity in (0.0, 500.0, 1000.0, 2000.0):
        scenario = replace(config, battery_capacity_kwh=capacity)
        result = dispatch(frame, scenario)
        for capex_rate in (200.0, 350.0, 500.0):
            priced = replace(scenario, battery_capex_eur_per_kwh=capex_rate)
            e = economics(result, priced)
            rows.append(
                {
                    "capacity_kwh": capacity,
                    "capex_eur_kwh": capex_rate,
                    "annual_net_savings_eur": e["annual_net_savings_eur"],
                    "npv_eur": e["npv_eur"],
                    "simple_payback_years": e["simple_payback_years"],
                }
            )
    return rows
