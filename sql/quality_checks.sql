SELECT COUNT(*) AS rows_checked, COUNT(DISTINCT timestamp) AS unique_timestamps,
       SUM(CASE WHEN ABS(net_load_kw - (demand_kw - solar_kw)) > 0.000001 THEN 1 ELSE 0 END) AS balance_failures,
       SUM(CASE WHEN grid_import_kw > 0 AND grid_export_kw > 0 THEN 1 ELSE 0 END) AS simultaneous_import_export
FROM hourly_metrics;
