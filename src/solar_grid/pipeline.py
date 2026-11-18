"""One command creates warehouse, model evaluation and static dashboard data."""

import hashlib
import importlib.metadata
import json
import platform
import sqlite3
import tempfile
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from solar_grid.config import Config
from solar_grid.data import simulate
from solar_grid.dispatch import dispatch, economics, sensitivity
from solar_grid.forecast import evaluate
from solar_grid.warehouse import ROOT, create_warehouse, features, query


def dump_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def csv_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(frame.to_csv(index=False, float_format="%.8f").encode()).hexdigest()


def run(config: Config, output: Path) -> dict:
    config.validate()
    output.mkdir(parents=True, exist_ok=True)
    frame = simulate(config)
    # Fresh temporary database: existing successful runs remain usable on failure.
    with tempfile.TemporaryDirectory(prefix="solar-grid-") as temp:
        database = Path(temp) / "solar.sqlite"
        conn = create_warehouse(frame, database)
        try:
            quality = query(conn, "quality_checks").iloc[0].to_dict()
            monthly = query(conn, "monthly_kpis")
            model_report, predictions = evaluate(features(conn), config)
            # Economics uses a complete final calendar year by default, not a partial season.
            economic_start = pd.Timestamp(config.end_exclusive, tz="UTC") - pd.DateOffset(years=1)
            economic_frame = frame[frame.timestamp >= economic_start]
            dispatch_frame = dispatch(economic_frame, config)
            dispatch_frame.assign(timestamp=dispatch_frame.timestamp.astype(str)).to_sql(
                "battery_dispatch", conn, index=False, if_exists="replace"
            )
            predictions.assign(timestamp=predictions.timestamp.astype(str)).to_sql(
                "forecast_test", conn, index=False, if_exists="replace"
            )
            conn.commit()
        finally:
            conn.close()
        (output / "solar.sqlite").write_bytes(database.read_bytes())
    frame.to_csv(output / "hourly_energy.csv", index=False, float_format="%.8f")
    predictions.to_csv(output / "forecast_test.csv", index=False, float_format="%.8f")
    dispatch_frame.to_csv(output / "dispatch.csv", index=False, float_format="%.8f")
    monthly.to_csv(output / "monthly_kpis.csv", index=False, float_format="%.8f")
    econ = economics(dispatch_frame, config)
    report = {
        "schema_version": 1,
        "scenario": "Synthetic commercial site; no measured client savings",
        "config": asdict(config),
        "input_rows": len(frame),
        "input_sha256": csv_hash(frame),
        "source_sha256": hashlib.sha256(
            b"".join(
                path.relative_to(ROOT).as_posix().encode() + path.read_bytes()
                for folder, pattern in (("src/solar_grid", "*.py"), ("sql", "*.sql"))
                for path in sorted((ROOT / folder).glob(pattern))
            )
        ).hexdigest(),
        "environment": {
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
            **{
                name: importlib.metadata.version(name)
                for name in ("numpy", "pandas", "scikit-learn")
            },
        },
        "quality": quality,
        "forecast": model_report,
        "economics_period": {
            "start": str(economic_frame.timestamp.iloc[0]),
            "end": str(economic_frame.timestamp.iloc[-1]),
        },
        "economics": econ,
        "sensitivity": sensitivity(economic_frame, config),
    }
    dump_json(output / "metrics.json", report)
    # Daily aggregations keep client payload small; raw hourly audit CSVs stay in artifacts.
    daily = (
        predictions.assign(date=predictions.timestamp.dt.strftime("%Y-%m-%d"))
        .groupby("date")[["target_kw", "random_forest_kw", "previous_day_kw"]]
        .mean()
        .reset_index()
    )
    battery_months = (
        dispatch_frame.assign(month=dispatch_frame.timestamp.dt.strftime("%Y-%m"))
        .groupby("month")[
            ["baseline_cost_eur", "energy_cost_eur", "wear_cost_eur", "operating_savings_eur"]
        ]
        .sum()
        .reset_index()
    )
    week = dispatch_frame.iloc[:168].copy()
    # Choose highest solar week for a useful, explicitly labeled dispatch illustration.
    if len(dispatch_frame) >= 168:
        start = int(dispatch_frame.solar_kw.rolling(168).sum().fillna(-1).to_numpy().argmax()) - 167
        start = max(0, start)
        week = dispatch_frame.iloc[start : start + 168].copy()
    week["timestamp"] = week.timestamp.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        **report,
        "daily_forecast": daily.to_dict("records"),
        "monthly_dispatch": battery_months.to_dict("records"),
        "dispatch_week": week.to_dict("records"),
        "monthly_energy": monthly.to_dict("records"),
    }
    dump_json(output / "dashboard-data.json", payload)
    return report


def publish_snapshot(output: Path) -> None:
    """Copy measured outputs into the reviewable, versioned static demo."""
    payload = json.loads((output / "dashboard-data.json").read_text())
    report = json.loads((output / "metrics.json").read_text())
    dump_json(ROOT / "docs" / "data.json", payload)
    dump_json(ROOT / "reports" / "metrics.json", report)
    for name in ("monthly_kpis.csv",):
        (ROOT / "reports" / name).write_bytes((output / name).read_bytes())
