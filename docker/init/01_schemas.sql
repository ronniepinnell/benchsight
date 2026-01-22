-- BenchSight ETL Debug: 4-Schema Architecture
-- =============================================
-- This creates the layered data architecture for ETL debugging:
--   raw         - Original source data (BLB tables, tracking)
--   stage       - Intermediate transformations (enhanced events/shifts)
--   intermediate - Calculation-ready data (aggregated stats)
--   datamart    - Final tables (mirrors Supabase production)

-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS stage;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS datamart;

-- Grant full access to benchsight user
GRANT ALL ON SCHEMA raw TO benchsight;
GRANT ALL ON SCHEMA stage TO benchsight;
GRANT ALL ON SCHEMA intermediate TO benchsight;
GRANT ALL ON SCHEMA datamart TO benchsight;

-- Grant usage to public for easier querying
GRANT USAGE ON SCHEMA raw TO PUBLIC;
GRANT USAGE ON SCHEMA stage TO PUBLIC;
GRANT USAGE ON SCHEMA intermediate TO PUBLIC;
GRANT USAGE ON SCHEMA datamart TO PUBLIC;

-- Set default search path (datamart first for convenience)
ALTER DATABASE benchsight SET search_path TO datamart, intermediate, stage, raw, public;

-- Create etl_state table for tracking phase completion
CREATE TABLE IF NOT EXISTS public.etl_state (
    run_id VARCHAR(50) PRIMARY KEY,
    current_phase VARCHAR(10),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running',
    error_message TEXT
);

-- Create phase_log table for detailed tracking
CREATE TABLE IF NOT EXISTS public.phase_log (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(50) REFERENCES public.etl_state(run_id),
    phase_id VARCHAR(10) NOT NULL,
    phase_name VARCHAR(100),
    target_schema VARCHAR(20),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    tables_created INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'running',
    error_message TEXT
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_phase_log_run_id ON public.phase_log(run_id);
CREATE INDEX IF NOT EXISTS idx_phase_log_phase_id ON public.phase_log(phase_id);

COMMENT ON SCHEMA raw IS 'Original source data from BLB tables and tracking files';
COMMENT ON SCHEMA stage IS 'Intermediate transformations (enhanced events, shifts, lookups)';
COMMENT ON SCHEMA intermediate IS 'Calculation-ready aggregated data';
COMMENT ON SCHEMA datamart IS 'Final output tables (mirrors Supabase production)';
