"""Configuration validation shared by CLI, tests and notebooks."""

import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Config:
    start: str = "2023-01-01"
    end_exclusive: str = "2025-01-01"
    seed: int = 42
    train_end: str = "2024-01-01"
    test_start: str = "2024-07-01"
    pv_capacity_kw: float = 1200.0
    battery_capacity_kwh: float = 1000.0
    battery_power_kw: float = 500.0
    charge_efficiency: float = 0.95
    discharge_efficiency: float = 0.95
    battery_capex_eur_per_kwh: float = 350.0
    annual_opex_fraction: float = 0.02
    throughput_cost_eur_per_kwh: float = 0.02
    discount_rate: float = 0.08
    project_years: int = 10
    annual_savings_decline: float = 0.02
    grid_carbon_kg_per_kwh: float = 0.35
    n_estimators: int = 64

    def validate(self):
        dates = [
            datetime.fromisoformat(getattr(self, k))
            for k in ("start", "train_end", "test_start", "end_exclusive")
        ]
        if any(d.tzinfo is not None or d.time().isoformat() != "00:00:00" for d in dates):
            raise ValueError("Use midnight dates without offsets; timestamps are UTC")
        if not all(a < b for a, b in zip(dates, dates[1:])):
            raise ValueError("Require start < train_end < test_start < end_exclusive")
        if (dates[1] - dates[0]).days < 90:
            raise ValueError("At least 90 days of training history are required")
        for key, value in asdict(self).items():
            if isinstance(value, (int, float)) and not math.isfinite(value):
                raise ValueError(f"{key} must be finite")
        for key in ("charge_efficiency", "discharge_efficiency"):
            if not 0 < getattr(self, key) <= 1:
                raise ValueError(f"{key} must be in (0, 1]")
        for key in ("annual_opex_fraction", "discount_rate", "annual_savings_decline"):
            if not 0 <= getattr(self, key) < 1:
                raise ValueError(f"{key} must be in [0, 1)")
        for key in (
            "pv_capacity_kw",
            "battery_capacity_kwh",
            "battery_power_kw",
            "battery_capex_eur_per_kwh",
            "throughput_cost_eur_per_kwh",
            "grid_carbon_kg_per_kwh",
        ):
            if getattr(self, key) < 0:
                raise ValueError(f"{key} cannot be negative")
        for key in ("n_estimators", "project_years"):
            if not isinstance(getattr(self, key), int) or getattr(self, key) < 1:
                raise ValueError(f"{key} must be a positive integer")
        if not isinstance(self.seed, int) or self.seed < 0:
            raise ValueError("seed must be a nonnegative integer")
        return self


def load_config(path: Path) -> Config:
    return Config(**json.loads(path.read_text())).validate()
