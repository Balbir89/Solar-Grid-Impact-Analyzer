"""Reproducible, simplified commercial-site scenario; all data are synthetic."""

import numpy as np
import pandas as pd

from solar_grid.config import Config

NUMERIC_COLUMNS = ["demand_kw", "solar_kw", "import_eur_kwh", "export_eur_kwh"]


def simulate(config: Config) -> pd.DataFrame:
    config.validate()
    index = pd.date_range(config.start, config.end_exclusive, freq="h", inclusive="left", tz="UTC")
    rng = np.random.default_rng(config.seed)
    hour, day = index.hour.to_numpy(), index.dayofyear.to_numpy()
    weekend = index.dayofweek.to_numpy() >= 5
    season = np.sin(2 * np.pi * (day - 80) / 365.25)
    daylight = 12 + 3.5 * season
    sun = np.maximum(0, np.sin(np.pi * (hour - (12 - daylight / 2)) / daylight))
    sun[(hour < 12 - daylight / 2) | (hour > 12 + daylight / 2)] = 0
    daily_cloud = rng.beta(5, 2, len(index.normalize().unique()))
    cloud = np.repeat(daily_cloud, 24)[: len(index)]
    cloud = np.clip(cloud + rng.normal(0, 0.06, len(index)), 0.1, 1)
    solar = config.pv_capacity_kw * sun * (0.75 + 0.25 * season) * cloud
    business = ((hour >= 8) & (hour < 18)).astype(float)
    evening = np.exp(-(((hour - 19) / 2.8) ** 2))
    demand = 420 + 290 * business + 150 * evening + 85 * (1 - season) / 2
    demand = np.maximum(100, demand * np.where(weekend, 0.76, 1) + rng.normal(0, 32, len(index)))
    tariff = np.where((hour >= 17) & (hour < 22), 0.34, np.where(hour < 6, 0.12, 0.21))
    return pd.DataFrame(
        {
            "timestamp": index,
            "demand_kw": demand,
            "solar_kw": solar,
            "import_eur_kwh": tariff,
            "export_eur_kwh": 0.065,
        }
    )


def validate_data(frame: pd.DataFrame) -> None:
    if set(frame.columns) != {"timestamp", *NUMERIC_COLUMNS}:
        raise ValueError("Unexpected input columns")
    if len(frame) < 169:
        raise ValueError("At least 169 hourly observations are required")
    if frame.timestamp.isna().any() or frame.timestamp.duplicated().any():
        raise ValueError("Timestamps must be present and unique")
    if not frame.timestamp.is_monotonic_increasing:
        raise ValueError("Timestamps must be ordered")
    if not frame.timestamp.diff().dropna().eq(pd.Timedelta(hours=1)).all():
        raise ValueError("Hourly observations must be contiguous")
    if str(frame.timestamp.dt.tz) != "UTC":
        raise ValueError("Timestamps must use UTC")
    if not np.isfinite(frame[NUMERIC_COLUMNS].to_numpy(dtype=float)).all():
        raise ValueError("Numeric values must be finite")
    if (frame[["demand_kw", "solar_kw"]] < 0).any().any():
        raise ValueError("Demand and generation cannot be negative")
    # Negative electricity prices are legitimate; do not discard them.
