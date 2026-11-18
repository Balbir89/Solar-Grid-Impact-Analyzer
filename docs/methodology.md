# Methodology and decision boundaries

## Data and units

The default scenario is a fictional commercial site observed hourly in UTC from 2023-01-01 inclusive to 2025-01-01 exclusive: 17,544 records including leap day. Power is kW, stored energy is kWh, and tariffs are EUR/kWh. At a one-hour timestep, kW multiplied by one hour gives kWh. All calendar and tariff hours are UTC; no claim is made that they reproduce German local tariffs or daylight-saving behavior.

The seeded generator combines weekday operating demand, an evening load component, seasonal daylight, daily cloud variation and hourly noise. It is not calibrated to a real site. No real utility, weather provider or electricity exchange supplied these synthetic observations.

The earlier MW-scale CSV is retained in data/reference for provenance. It is not an input to this new commercial-site experiment. Do not mix the old metrics or dashboard screenshots with the new results.

## Feature availability contract

For target hour t, the forecast is issued immediately before t after the meter observation for t-1 has arrived. Features are calendar values for t, net load lags 1/24/168, lagged demand and solar, and a rolling history spanning t-24 through t-1. The first 168 observations are warm-up rows.

SQL computes lags and rolling features, then Python adds cyclical calendar encodings. Current-hour demand, current-hour generation and the current target never enter X. The regression test changes every observation at and after t and verifies that features for t stay unchanged.

This is rolling one-hour forecasting. During evaluation, earlier test-period actuals become available for later predictions. It is not a multi-hour open-loop forecast. A delayed meter feed would require an explicit additional lag and new evaluation.

## Model selection and evaluation

Train: 2023 (8,592 usable rows after warm-up). Validation: January–June 2024 (4,368 rows). Final test: July–December 2024 (4,416 rows).

Two predeclared Random Forest candidates use 64 trees, maximum depth 16 and minimum leaf sizes 4 or 12. Validation MAE chooses the leaf size; the selected model is refit on training plus validation once. The final test is not used for tuning. Three simple baselines use the previous hour, same hour yesterday and same hour last week.

Three expanding development backtests provide temporal diagnostics using a fixed leaf size of 4. They are not substitutes for the final holdout. Random Forest impurity importance is descriptive and is not a causal explanation. An empirical validation-error band is reported with observed test coverage; it is not a calibrated probabilistic forecast or a coverage guarantee.

No model is tuned to achieve a promised R². A high synthetic score does not establish real-site accuracy.

## Dispatch policy and physical accounting

Forecasting and battery economics are separate evaluated workstreams. The dispatch rule does not consume model predictions; there is no claim that the ML model caused the storage savings.

The battery starts empty, stores only surplus PV and serves on-site demand from 17:00 through 21:59 UTC. Charge and discharge are limited by state of charge, capacity and power. It cannot charge and discharge simultaneously, charge from the grid, or sell battery energy to the grid. The final SOC has zero salvage revenue. The rule has current-hour telemetry, not future load or prices.

Energy accounting:

- Site: PV + grid import + battery discharge = demand + grid export + battery charge.
- Storage: SOC(t) = SOC(t-1) + charge × charge efficiency − discharge / discharge efficiency.
- Charge efficiency and discharge efficiency are each 95%; round-trip efficiency is 90.25%.

This is a transparent heuristic benchmark, not an optimal dispatch solver. The fixed evening rule can miss the site's maximum import peak; the base result shows no reduction in the annual peak. Demand charges are not priced into the model.

## Incremental financial case

Compare solar plus battery with the same solar-equipped site without battery. The default economics window is all 8,784 hours of calendar 2024. Normalize operating savings to a 365.25-day year using 8,766 / observed hours. Forecast metrics use a different, explicitly stated six-month holdout.

Assumptions are examples, not market quotes:

| Assumption | Default |
|---|---:|
| PV capacity | 1,200 kW |
| Battery capacity / power | 1,000 kWh / 500 kW |
| Import tariff: off-peak / standard / evening | €0.12 / €0.21 / €0.34 per kWh |
| Solar export credit | €0.065 per kWh |
| Battery installed cost | €350 per kWh |
| Fixed annual battery OPEX | 2% of initial CAPEX |
| Variable throughput cost | €0.02 per discharged kWh |
| Evaluation horizon / discount rate | 10 years / 8% |
| Annual operating-savings decline | 2% |

Energy bill = imports × import tariff − exports × export credit.
Operating savings = baseline bill − battery bill − throughput cost.
Annual net benefit = annualized operating savings − fixed OPEX.
NPV discounts ten annual net cash flows and subtracts initial battery CAPEX.
Simple payback is CAPEX divided by first-year net benefit; it ignores discounting and later decline and can exceed the assumed project life. It is absent when net benefit is nonpositive.

PV CAPEX is already sunk in the comparator. Subsidies, taxes, financing, replacement, demand charges, ancillary revenues and residual value are excluded. Throughput cost and annual benefit decline are separate illustrative wear allowances; they are not a validated electrochemical degradation model.

The sensitivity grid varies battery capacity (0/500/1,000/2,000 kWh) and CAPEX (€200/€350/€500 per kWh), keeping power fixed. It explores 12 combinations, of which three represent the identical no-investment baseline. It does not optimize storage size.

## Carbon boundary

A fixed illustrative grid factor of 0.35 kg CO₂/kWh is used. Site-import reduction is reported separately from net avoided emissions after deducting foregone solar exports. With equal displacement factors at import and export times, storage losses produce negative net avoided emissions in this experiment. Actual time-varying marginal emissions could change the result; no verified carbon savings are claimed.

## Technical trade-offs

SQLite keeps an executed SQL layer portable without a managed database; it is appropriate for this small, single-writer portfolio workload. Production scale could require partitioned storage and a warehouse. SQL validation rejects gaps because row-based windows assume contiguous hourly observations.

Random Forest handles nonlinear calendar/lag relationships without scaling. Baselines expose whether its additional complexity is justified. No GPU, distributed framework or MLOps platform is required for 17,544 rows.

Static JSON/SVG avoids a dashboard backend and external JavaScript dependencies. The figures are batch snapshots and do not refresh from live meters. Docker uses a build stage for analytics and a small, non-root runtime to serve only public results.

## References

- [scikit-learn: lagged time-series features](https://scikit-learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html)
- [SQLite: window functions](https://www.sqlite.org/windowfunctions.html)
- [Docker: build best practices](https://docs.docker.com/build/building/best-practices/)
- [GitHub: custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

These references describe methods and tooling. They are not sources for the scenario's tariff, cost or carbon assumptions.
