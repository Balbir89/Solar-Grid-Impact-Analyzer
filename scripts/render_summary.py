"""Render the README figure from measured results (optional presentation extra)."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / "reports/metrics.json").read_text())
models = report["forecast"]["test_metrics"]
economics = report["economics"]
background, panel = "#091522", "#142537"
white, muted, teal, gold = "#eef5ff", "#a8bad0", "#68e0c1", "#f5c581"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
fig = plt.figure(figsize=(14, 8), facecolor=background)
fig.text(0.055, 0.93, "SOLAR GRID IMPACT / PYTHON + SQL", color=teal, weight="bold", size=12)
fig.text(
    0.055, 0.862, "Forecast the load. Question the investment.", color=white, size=25, weight="bold"
)
fig.text(
    0.055,
    0.81,
    "Synthetic commercial-site case study | 2023–2024 | Reproducible evidence",
    color=muted,
)

baseline = min(models[k]["mae_kw"] for k in models if k != "random_forest")
cards = [
    ("HOURLY RECORDS", f"{report['input_rows']:,}"),
    ("TEST FORECAST MAE", f"{models['random_forest']['mae_kw']:.2f} kW"),
    (
        "BASELINE ERROR REDUCTION",
        f"{(1 - models['random_forest']['mae_kw'] / baseline) * 100:.1f}%",
    ),
    ("10-YEAR BATTERY NPV", f"−€{abs(economics['npv_eur']):,.0f}"),
]
for i, (label, value) in enumerate(cards):
    x = 0.055 + i * 0.234
    fig.text(x, 0.725, label, color=muted, size=9, weight="bold")
    fig.text(x, 0.675, value, color=white if i < 3 else gold, size=23, weight="bold")

left = fig.add_axes([0.22, 0.22, 0.275, 0.32], facecolor=panel)
keys = ["random_forest", "previous_hour", "previous_day", "previous_week"]
labels = ["Random Forest", "Previous hour", "Same hour yesterday", "Same hour last week"]
values = [models[k]["mae_kw"] for k in keys]
left.barh(labels, values, color=[teal, muted, muted, muted], height=0.5)
left.invert_yaxis()
left.set_xlim(0, max(values) * 1.28)
for i, value in enumerate(values):
    left.text(value + 2, i, f"{value:.2f}", va="center", color=white, size=10)
left.set_xlabel("Final holdout MAE (kW) · lower is better", color=muted, labelpad=12)
fig.text(0.055, 0.585, "Forecast quality", color=white, size=16, weight="bold")

right = fig.add_axes([0.61, 0.22, 0.335, 0.32], facecolor=panel)
discount = report["config"]["discount_rate"]
cumulative, total = [], 0.0
for year, cash in enumerate(economics["cashflows_eur"]):
    total += cash / (1 + discount) ** year
    cumulative.append(total)
right.plot(range(len(cumulative)), cumulative, color=gold, marker="o", markersize=4, linewidth=2)
right.axhline(0, color=muted, linewidth=0.8, linestyle="--")
right.set_ylim(-economics["capex_eur"] * 1.12, economics["capex_eur"] * 0.08)
right.set_xlim(0, economics["project_years"])
right.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"€{value / 1000:,.0f}k"))
right.set_xlabel("Year · cumulative discounted cash flow", color=muted, labelpad=12)
fig.text(0.56, 0.585, "Investment case", color=white, size=16, weight="bold")
for ax in (left, right):
    ax.tick_params(colors=muted, labelsize=10, length=0, pad=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis="x" if ax is left else "y", alpha=0.10, color=white)

fig.text(0.055, 0.095, "DECISION", color=teal, size=10, weight="bold")
fig.text(
    0.145,
    0.095,
    "Revisit capital cost and dispatch before investing under these assumptions.",
    color=white,
    size=12,
)
fig.text(
    0.055,
    0.045,
    "All data and financial outcomes are simulated. Forecasting and battery dispatch are evaluated separately.",
    color=muted,
    size=10,
)
destination = ROOT / "docs/assets/case-study-summary.png"
destination.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(destination, dpi=160, facecolor=background)
plt.close(fig)
print(destination)
