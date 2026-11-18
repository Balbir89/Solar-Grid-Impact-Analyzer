-- kW * one-hour timestep = kWh. All hours are UTC; no DST ambiguity.
SELECT substr(timestamp, 1, 7) AS month, COUNT(*) AS observed_hours,
       SUM(demand_kw) AS demand_kwh, SUM(solar_kw) AS solar_kwh,
       SUM(grid_import_kw) AS solar_only_import_kwh,
       SUM(grid_export_kw) AS solar_only_export_kwh,
       SUM(solar_only_cost_eur) AS solar_only_cost_eur,
       MAX(grid_import_kw) AS peak_import_kw,
       100.0 * SUM(MIN(demand_kw, solar_kw)) / NULLIF(SUM(solar_kw), 0) AS solar_self_consumption_pct
FROM hourly_metrics GROUP BY month ORDER BY month;
