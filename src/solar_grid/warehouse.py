"""SQLite is the executed feature and KPI layer."""

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from solar_grid.data import validate_data

ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = ROOT / "sql"
FEATURES = [
    "hour_sin",
    "hour_cos",
    "day_sin",
    "day_cos",
    "weekday",
    "net_lag_1",
    "net_lag_24",
    "net_lag_168",
    "demand_lag_1",
    "solar_lag_1",
    "solar_lag_24",
    "net_mean_24",
    "net_min_24",
    "net_max_24",
]


def create_warehouse(frame: pd.DataFrame, path: Path | str = ":memory:") -> sqlite3.Connection:
    validate_data(frame)
    conn = sqlite3.connect(path)
    try:
        conn.executescript((SQL_DIR / "schema.sql").read_text())
        records = frame.copy()
        records["timestamp"] = records.timestamp.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        records.to_sql("hourly_energy", conn, if_exists="append", index=False)
        conn.commit()
        return conn
    except Exception:
        conn.close()
        raise


def query(conn: sqlite3.Connection, name: str) -> pd.DataFrame:
    if name not in {"features", "monthly_kpis", "quality_checks"}:
        raise ValueError("Unknown SQL report")
    return pd.read_sql_query((SQL_DIR / f"{name}.sql").read_text(), conn)


def features(conn: sqlite3.Connection) -> pd.DataFrame:
    frame = query(conn, "features")
    frame["timestamp"] = pd.to_datetime(frame.timestamp, utc=True)
    frame["hour_sin"] = np.sin(2 * np.pi * frame.hour / 24)
    frame["hour_cos"] = np.cos(2 * np.pi * frame.hour / 24)
    frame["day_sin"] = np.sin(2 * np.pi * frame.day_of_year / 365.25)
    frame["day_cos"] = np.cos(2 * np.pi * frame.day_of_year / 365.25)
    return frame
