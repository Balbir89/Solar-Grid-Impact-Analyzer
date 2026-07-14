```sql
-- Solar Grid Impact Analyzer
-- PostgreSQL Portfolio Example
-- Purpose: Analyze renewable generation, grid load, price behavior, and operational KPIs.
-- Skills shown: CTEs, aggregation, KPI modelling, window functions, anomaly detection, ranking.

DROP TABLE IF EXISTS solar_grid_hourly;

CREATE TABLE solar_grid_hourly (
    reading_time TIMESTAMP,
    region TEXT,
    solar_generation_mwh NUMERIC,
    wind_generation_mwh NUMERIC,
    hydro_generation_mwh NUMERIC,
    fossil_generation_mwh NUMERIC,
    grid_load_mwh NUMERIC,
    electricity_price_eur_mwh NUMERIC
);

INSERT INTO solar_grid_hourly VALUES
('2026-06-01 08:00', 'North', 120, 210, 45, 300, 620, 82),
('2026-06-01 12:00', 'North', 360, 180, 40, 220, 690, 76),
('2026-06-01 18:00', 'North', 90, 260, 42, 410, 780, 118),
('2026-06-02 08:00', 'North', 140, 230, 47, 290, 640, 80),
('2026-06-02 12:00', 'North', 390, 170, 43, 210, 700, 74),
('2026-06-02 18:00', 'North', 70, 280, 41, 450, 820, 132),

('2026-06-01 08:00', 'South', 180, 120, 60, 360, 710, 90),
('2026-06-01 12:00', 'South', 480, 100, 58, 250, 760, 78),
('2026-06-01 18:00', 'South', 110, 130, 62, 520, 880, 145),
('2026-06-02 08:00', 'South', 200, 115, 63, 340, 720, 88),
('2026-06-02 12:00', 'South', 510, 95, 61, 230, 770, 75),
('2026-06-02 18:00', 'South', 95, 145, 60, 550, 910, 152);


-- 1. Data quality check
-- Checks missing values and validates that generation/load values are positive.

SELECT
    COUNT(*) AS total_records,
    COUNT(*) FILTER (WHERE reading_time IS NULL) AS missing_timestamps,
    COUNT(*) FILTER (WHERE region IS NULL) AS missing_regions,
    COUNT(*) FILTER (WHERE grid_load_mwh <= 0) AS invalid_grid_load_records,
    COUNT(*) FILTER (WHERE electricity_price_eur_mwh < 0) AS invalid_price_records
FROM solar_grid_hourly;


-- 2. Executive KPI summary by region
-- Calculates renewable generation, total generation, renewable share, fossil dependency, and average market price.

WITH hourly_metrics AS (
    SELECT
        reading_time,
        region,
        solar_generation_mwh,
        wind_generation_mwh,
        hydro_generation_mwh,
        fossil_generation_mwh,
        grid_load_mwh,
        electricity_price_eur_mwh,
        solar_generation_mwh + wind_generation_mwh + hydro_generation_mwh AS renewable_generation_mwh,
        solar_generation_mwh + wind_generation_mwh + hydro_generation_mwh + fossil_generation_mwh AS total_generation_mwh
    FROM solar_grid_hourly
)

SELECT
    region,
    ROUND(SUM(renewable_generation_mwh), 2) AS total_renewable_generation_mwh,
    ROUND(SUM(total_generation_mwh), 2) AS total_generation_mwh,
    ROUND(SUM(grid_load_mwh), 2) AS total_grid_load_mwh,
    ROUND(SUM(renewable_generation_mwh) * 100.0 / NULLIF(SUM(total_generation_mwh), 0), 2) AS renewable_share_percent,
    ROUND(SUM(fossil_generation_mwh) * 100.0 / NULLIF(SUM(total_generation_mwh), 0), 2) AS fossil_share_percent,
    ROUND(AVG(electricity_price_eur_mwh), 2) AS average_price_eur_mwh
FROM hourly_metrics
GROUP BY region
ORDER BY renewable_share_percent DESC;


-- 3. Peak load analysis
-- Finds the highest demand hours per region using window functions.

WITH ranked_load AS (
    SELECT
        reading_time,
        region,
        grid_load_mwh,
        electricity_price_eur_mwh,
        RANK() OVER (
            PARTITION BY region
            ORDER BY grid_load_mwh DESC
        ) AS load_rank
    FROM solar_grid_hourly
)

SELECT
    region,
    reading_time,
    grid_load_mwh,
    electricity_price_eur_mwh,
    load_rank
FROM ranked_load
WHERE load_rank <= 2
ORDER BY region, load_rank;


-- 4. Renewable generation trend
-- Tracks renewable output changes compared with the previous time period.

WITH renewable_trend AS (
    SELECT
        reading_time,
        region,
        solar_generation_mwh + wind_generation_mwh + hydro_generation_mwh AS renewable_generation_mwh
    FROM solar_grid_hourly
),

trend_with_lag AS (
    SELECT
        reading_time,
        region,
        renewable_generation_mwh,
        LAG(renewable_generation_mwh) OVER (
            PARTITION BY region
            ORDER BY reading_time
        ) AS previous_renewable_generation_mwh
    FROM renewable_trend
)

SELECT
    reading_time,
    region,
    renewable_generation_mwh,
    previous_renewable_generation_mwh,
    ROUND(
        (renewable_generation_mwh - previous_renewable_generation_mwh) * 100.0
        / NULLIF(previous_renewable_generation_mwh, 0),
        2
    ) AS renewable_change_percent
FROM trend_with_lag
ORDER BY region, reading_time;


-- 5. Price anomaly detection
-- Flags hours where electricity price is unusually high compared with regional baseline.

WITH regional_baseline AS (
    SELECT
        region,
        AVG(electricity_price_eur_mwh) AS avg_price,
        STDDEV_POP(electricity_price_eur_mwh) AS price_stddev
    FROM solar_grid_hourly
    GROUP BY region
),

price_scoring AS (
    SELECT
        s.reading_time,
        s.region,
        s.electricity_price_eur_mwh,
        b.avg_price,
        b.price_stddev,
        CASE
            WHEN s.electricity_price_eur_mwh > b.avg_price + b.price_stddev THEN 'High price signal'
            ELSE 'Normal price range'
        END AS price_status
    FROM solar_grid_hourly s
    JOIN regional_baseline b
        ON s.region = b.region
)

SELECT
    reading_time,
    region,
    electricity_price_eur_mwh,
    ROUND(avg_price, 2) AS regional_average_price,
    ROUND(price_stddev, 2) AS regional_price_stddev,
    price_status
FROM price_scoring
ORDER BY region, reading_time;


-- 6. Business recommendation logic
-- Converts technical KPIs into simple management actions.

WITH kpi_summary AS (
    SELECT
        region,
        SUM(solar_generation_mwh + wind_generation_mwh + hydro_generation_mwh) AS renewable_generation_mwh,
        SUM(solar_generation_mwh + wind_generation_mwh + hydro_generation_mwh + fossil_generation_mwh) AS total_generation_mwh,
        AVG(electricity_price_eur_mwh) AS avg_price
    FROM solar_grid_hourly
    GROUP BY region
)

SELECT
    region,
    ROUND(renewable_generation_mwh * 100.0 / NULLIF(total_generation_mwh, 0), 2) AS renewable_share_percent,
    ROUND(avg_price, 2) AS average_price_eur_mwh,
    CASE
        WHEN renewable_generation_mwh * 100.0 / NULLIF(total_generation_mwh, 0) >= 60
            THEN 'Strong renewable performance - maintain investment and monitor storage capacity'
        WHEN renewable_generation_mwh * 100.0 / NULLIF(total_generation_mwh, 0) BETWEEN 45 AND 59.99
            THEN 'Moderate renewable performance - improve solar/wind integration'
        ELSE
            'Low renewable performance - investigate fossil dependency and grid constraints'
    END AS management_recommendation
FROM kpi_summary
ORDER BY renewable_share_percent DESC;
```
