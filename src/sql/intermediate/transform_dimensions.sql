-- =============================================================================
-- INTERMEDIATE: TRANSFORM SUPPLEMENTARY DIMENSIONS
-- =============================================================================
-- File: src/sql/intermediate/transform_dimensions.sql
--
-- PURPOSE:
--     Transform dim_dates and dim_seconds from stage to intermediate.
--     These enable rich time-based filtering in Power BI.
-- =============================================================================

-- =============================================================================
-- INT_DIM_DATES: Calendar dimension
-- =============================================================================
-- WHY: Standard date dimension for filtering games by weekday, month, season

DROP TABLE IF EXISTS int_dim_dates;

CREATE TABLE int_dim_dates AS
SELECT
    -- Primary key
    datekey AS date_key,
    
    -- Date value
    date AS full_date,
    
    -- Day components
    day AS day_of_month,
    daysuffix AS day_suffix,
    weekday AS day_of_week_num,
    weekdayname AS day_name,
    weekdayname_short AS day_name_short,
    dayofyear AS day_of_year,
    
    -- Week components
    weekofmonth AS week_of_month,
    weekofyear AS week_of_year,
    weekstartdate AS week_start_date,
    weekenddate AS week_end_date,
    
    -- Month components
    month AS month_num,
    monthname AS month_name,
    monthname_short AS month_name_short,
    mmyyyy AS month_year_key,
    monthyear AS month_year_label,
    
    -- Quarter/Year
    quarter AS quarter_num,
    quartername AS quarter_name,
    year AS year_num,
    
    -- Flags
    CASE WHEN isweekend = 1 THEN 1 ELSE 0 END AS is_weekend,
    CASE WHEN isholiday = 1 THEN 1 ELSE 0 END AS is_holiday,
    
    -- Four week periods (for scheduling)
    fourweekperiodstartdate AS four_week_start,
    fourweekperiodenddate AS four_week_end,
    
    -- Metadata
    datetime('now') AS _processed_timestamp,
    datetime('now') AS _updated_timestamp
    
FROM stg_dim_dates;

CREATE INDEX IF NOT EXISTS idx_int_dates_key ON int_dim_dates(date_key);
CREATE INDEX IF NOT EXISTS idx_int_dates_year ON int_dim_dates(year_num);
CREATE INDEX IF NOT EXISTS idx_int_dates_month ON int_dim_dates(year_num, month_num);

-- =============================================================================
-- INT_DIM_SECONDS: Time dimension for game analysis
-- =============================================================================
-- WHY: Enable second-by-second analysis of game events
--      Filter by period, time remaining, etc.

DROP TABLE IF EXISTS int_dim_seconds;

CREATE TABLE int_dim_seconds AS
SELECT
    time_key,
    period,
    period_name,
    period_type,
    
    -- Ascending time (clock up)
    minute_in_period,
    second_in_minute,
    total_seconds_in_period,
    time_elapsed_period_formatted,
    
    -- Descending time (clock down)
    time_remaining_period_seconds,
    time_remaining_period_formatted,
    minute_remaining_period,
    second_remaining_minute,
    
    -- Game-level time
    time_elapsed_game_seconds,
    time_elapsed_game_formatted,
    time_remaining_regulation_seconds,
    
    -- Flags
    is_first_minute,
    is_last_minute,
    is_regulation,
    is_overtime,
    
    -- Metadata
    datetime('now') AS _processed_timestamp,
    datetime('now') AS _updated_timestamp
    
FROM stg_dim_seconds;

CREATE INDEX IF NOT EXISTS idx_int_seconds_key ON int_dim_seconds(time_key);
CREATE INDEX IF NOT EXISTS idx_int_seconds_period ON int_dim_seconds(period);
