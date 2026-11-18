"""Guard published claims against the freshly generated audit report."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
actual = json.loads((root / "artifacts/metrics.json").read_text())
expected = json.loads((root / "reports/metrics.json").read_text())
assert actual["input_rows"] == expected["input_rows"] == 17544
assert actual["input_sha256"] == expected["input_sha256"]
assert actual["source_sha256"] == expected["source_sha256"]
assert actual["quality"]["balance_failures"] == 0
assert actual["quality"]["simultaneous_import_export"] == 0
forecast = pd.read_csv(root / "artifacts/forecast_test.csv")
for model in ("random_forest", "previous_hour", "previous_day", "previous_week"):
    mae = float(np.abs(forecast.target_kw - forecast[f"{model}_kw"]).mean())
    assert np.isclose(mae, actual["forecast"]["test_metrics"][model]["mae_kw"], atol=1e-6)
    assert np.isclose(mae, expected["forecast"]["test_metrics"][model]["mae_kw"], atol=1e-4)
dispatch = pd.read_csv(root / "artifacts/dispatch.csv")
e = actual["economics"]
assert np.isclose(
    dispatch.operating_savings_eur.sum() * e["annualization_factor"] - e["annual_opex_eur"],
    e["annual_net_savings_eur"],
    atol=1e-5,
)
for field in ("annual_net_savings_eur", "npv_eur"):
    assert np.isclose(e[field], expected["economics"][field], atol=0.01)
print("Input hash, all model MAEs and battery cash flows reconcile.")
