-- At target hour t, only meter readings through t-1 are available.
-- Python checks hourly continuity before loading: ROWS therefore means hours.
WITH history AS (
 SELECT timestamp, net_load_kw AS target_kw,
        CAST(strftime('%H', timestamp) AS INTEGER) AS hour,
        CAST(strftime('%w', timestamp) AS INTEGER) AS weekday,
        CAST(strftime('%j', timestamp) AS INTEGER) AS day_of_year,
        LAG(net_load_kw, 1) OVER w AS net_lag_1,
        LAG(net_load_kw, 24) OVER w AS net_lag_24,
        LAG(net_load_kw, 168) OVER w AS net_lag_168,
        LAG(demand_kw, 1) OVER w AS demand_lag_1,
        LAG(solar_kw, 1) OVER w AS solar_lag_1,
        LAG(solar_kw, 24) OVER w AS solar_lag_24,
        AVG(net_load_kw) OVER (ORDER BY timestamp ROWS BETWEEN 24 PRECEDING AND 1 PRECEDING) AS net_mean_24,
        MIN(net_load_kw) OVER (ORDER BY timestamp ROWS BETWEEN 24 PRECEDING AND 1 PRECEDING) AS net_min_24,
        MAX(net_load_kw) OVER (ORDER BY timestamp ROWS BETWEEN 24 PRECEDING AND 1 PRECEDING) AS net_max_24
 FROM hourly_metrics WINDOW w AS (ORDER BY timestamp)
)
SELECT * FROM history WHERE net_lag_168 IS NOT NULL ORDER BY timestamp;
