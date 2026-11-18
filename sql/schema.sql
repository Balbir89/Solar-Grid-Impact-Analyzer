PRAGMA foreign_keys = ON;
CREATE TABLE hourly_energy (
    timestamp TEXT PRIMARY KEY NOT NULL,
    demand_kw REAL NOT NULL CHECK (demand_kw >= 0),
    solar_kw REAL NOT NULL CHECK (solar_kw >= 0),
    import_eur_kwh REAL NOT NULL,
    export_eur_kwh REAL NOT NULL
);
CREATE VIEW hourly_metrics AS
SELECT *, demand_kw - solar_kw AS net_load_kw,
       MAX(demand_kw - solar_kw, 0) AS grid_import_kw,
       MAX(solar_kw - demand_kw, 0) AS grid_export_kw,
       MAX(demand_kw - solar_kw, 0) * import_eur_kwh
       - MAX(solar_kw - demand_kw, 0) * export_eur_kwh AS solar_only_cost_eur
FROM hourly_energy;
