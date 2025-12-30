-- ============================================================
-- BENCHSIGHT LOGGING TABLES FOR SUPABASE
-- ============================================================
-- This script creates tables to track:
-- - ETL runs and their status
-- - Individual table loads
-- - Errors and warnings
-- - Test results
-- - Change history
--
-- Run this AFTER the main schema is created
-- ============================================================

-- Drop existing logging tables if they exist
DROP TABLE IF EXISTS log_test_results CASCADE;
DROP TABLE IF EXISTS log_errors CASCADE;
DROP TABLE IF EXISTS log_etl_tables CASCADE;
DROP TABLE IF EXISTS log_etl_runs CASCADE;
DROP TABLE IF EXISTS log_data_changes CASCADE;

-- ============================================================
-- 1. ETL RUNS - Main run tracking
-- ============================================================
CREATE TABLE log_etl_runs (
    id BIGSERIAL PRIMARY KEY,
    run_id VARCHAR(100) UNIQUE NOT NULL,
    run_type VARCHAR(50) NOT NULL,  -- 'etl_run', 'supabase_load', 'test_run', etc.
    status VARCHAR(20) NOT NULL DEFAULT 'started',  -- 'started', 'in_progress', 'success', 'partial', 'failed'
    
    -- Timing
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_seconds DECIMAL(10,2),
    
    -- Counts
    tables_processed INTEGER DEFAULT 0,
    tables_success INTEGER DEFAULT 0,
    tables_failed INTEGER DEFAULT 0,
    total_rows_loaded INTEGER DEFAULT 0,
    
    -- Tests
    tests_passed INTEGER DEFAULT 0,
    tests_failed INTEGER DEFAULT 0,
    
    -- Errors/Warnings
    error_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    
    -- Environment
    environment JSONB,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for querying recent runs
CREATE INDEX idx_log_etl_runs_started_at ON log_etl_runs(started_at DESC);
CREATE INDEX idx_log_etl_runs_status ON log_etl_runs(status);
CREATE INDEX idx_log_etl_runs_run_type ON log_etl_runs(run_type);

-- ============================================================
-- 2. ETL TABLE LOADS - Per-table tracking
-- ============================================================
CREATE TABLE log_etl_tables (
    id BIGSERIAL PRIMARY KEY,
    run_id VARCHAR(100) NOT NULL REFERENCES log_etl_runs(run_id) ON DELETE CASCADE,
    
    -- Table info
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(50) NOT NULL,  -- 'insert', 'upsert', 'replace', 'delete'
    status VARCHAR(20) NOT NULL,  -- 'success', 'failed', 'skipped'
    
    -- Row counts
    rows_before INTEGER DEFAULT 0,
    rows_after INTEGER DEFAULT 0,
    rows_inserted INTEGER DEFAULT 0,
    rows_updated INTEGER DEFAULT 0,
    rows_deleted INTEGER DEFAULT 0,
    
    -- CSV info
    csv_rows INTEGER DEFAULT 0,
    csv_columns INTEGER DEFAULT 0,
    
    -- Timing
    duration_seconds DECIMAL(10,2),
    
    -- Errors
    error_message TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_log_etl_tables_run_id ON log_etl_tables(run_id);
CREATE INDEX idx_log_etl_tables_table_name ON log_etl_tables(table_name);
CREATE INDEX idx_log_etl_tables_status ON log_etl_tables(status);

-- ============================================================
-- 3. ERRORS - Detailed error tracking
-- ============================================================
CREATE TABLE log_errors (
    id BIGSERIAL PRIMARY KEY,
    run_id VARCHAR(100) REFERENCES log_etl_runs(run_id) ON DELETE SET NULL,
    
    -- Error details
    error_message TEXT NOT NULL,
    exception_type VARCHAR(100),
    exception_message TEXT,
    traceback TEXT,
    
    -- Context
    table_name VARCHAR(100),
    operation VARCHAR(50),
    context JSONB,
    
    -- Severity
    severity VARCHAR(20) DEFAULT 'error',  -- 'warning', 'error', 'critical'
    
    -- Resolution
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    resolved_by VARCHAR(100),
    resolution_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_log_errors_run_id ON log_errors(run_id);
CREATE INDEX idx_log_errors_severity ON log_errors(severity);
CREATE INDEX idx_log_errors_resolved ON log_errors(resolved);
CREATE INDEX idx_log_errors_created_at ON log_errors(created_at DESC);

-- ============================================================
-- 4. TEST RESULTS - Test tracking
-- ============================================================
CREATE TABLE log_test_results (
    id BIGSERIAL PRIMARY KEY,
    run_id VARCHAR(100) REFERENCES log_etl_runs(run_id) ON DELETE CASCADE,
    
    -- Test info
    test_file VARCHAR(200) NOT NULL,
    test_class VARCHAR(100),
    test_name VARCHAR(200) NOT NULL,
    
    -- Result
    status VARCHAR(20) NOT NULL,  -- 'passed', 'failed', 'skipped', 'error'
    duration_seconds DECIMAL(10,3),
    
    -- Failure info
    error_message TEXT,
    error_traceback TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_log_test_results_run_id ON log_test_results(run_id);
CREATE INDEX idx_log_test_results_status ON log_test_results(status);
CREATE INDEX idx_log_test_results_test_file ON log_test_results(test_file);

-- ============================================================
-- 5. DATA CHANGES - Track what changed
-- ============================================================
CREATE TABLE log_data_changes (
    id BIGSERIAL PRIMARY KEY,
    run_id VARCHAR(100) REFERENCES log_etl_runs(run_id) ON DELETE SET NULL,
    
    -- What changed
    table_name VARCHAR(100) NOT NULL,
    record_key VARCHAR(200),  -- Primary key value of changed record
    change_type VARCHAR(20) NOT NULL,  -- 'insert', 'update', 'delete'
    
    -- Change details
    old_values JSONB,
    new_values JSONB,
    changed_columns TEXT[],
    
    -- Context
    game_id INTEGER,
    player_id VARCHAR(20),
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_log_data_changes_run_id ON log_data_changes(run_id);
CREATE INDEX idx_log_data_changes_table_name ON log_data_changes(table_name);
CREATE INDEX idx_log_data_changes_change_type ON log_data_changes(change_type);
CREATE INDEX idx_log_data_changes_game_id ON log_data_changes(game_id);
CREATE INDEX idx_log_data_changes_created_at ON log_data_changes(created_at DESC);

-- ============================================================
-- VIEWS FOR REPORTING
-- ============================================================

-- Recent runs summary
CREATE OR REPLACE VIEW v_recent_runs AS
SELECT 
    run_id,
    run_type,
    status,
    started_at,
    completed_at,
    duration_seconds,
    tables_processed,
    tables_success,
    tables_failed,
    total_rows_loaded,
    tests_passed,
    tests_failed,
    error_count,
    warning_count
FROM log_etl_runs
ORDER BY started_at DESC
LIMIT 50;

-- Run statistics by day
CREATE OR REPLACE VIEW v_daily_run_stats AS
SELECT 
    DATE(started_at) as run_date,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_runs,
    SUM(total_rows_loaded) as total_rows_loaded,
    AVG(duration_seconds)::DECIMAL(10,2) as avg_duration_seconds,
    SUM(error_count) as total_errors
FROM log_etl_runs
GROUP BY DATE(started_at)
ORDER BY run_date DESC;

-- Table load statistics
CREATE OR REPLACE VIEW v_table_load_stats AS
SELECT 
    table_name,
    COUNT(*) as total_loads,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_loads,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_loads,
    SUM(rows_inserted) as total_rows_inserted,
    SUM(rows_updated) as total_rows_updated,
    AVG(duration_seconds)::DECIMAL(10,2) as avg_duration_seconds,
    MAX(created_at) as last_load_at
FROM log_etl_tables
GROUP BY table_name
ORDER BY table_name;

-- Unresolved errors
CREATE OR REPLACE VIEW v_unresolved_errors AS
SELECT 
    id,
    run_id,
    error_message,
    exception_type,
    table_name,
    severity,
    created_at
FROM log_errors
WHERE resolved = FALSE
ORDER BY created_at DESC;

-- Test pass rate by file
CREATE OR REPLACE VIEW v_test_pass_rate AS
SELECT 
    test_file,
    COUNT(*) as total_tests,
    SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
    SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) as skipped,
    ROUND(100.0 * SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) / COUNT(*), 1) as pass_rate
FROM log_test_results
GROUP BY test_file
ORDER BY test_file;

-- Recent data changes summary
CREATE OR REPLACE VIEW v_recent_changes AS
SELECT 
    DATE(created_at) as change_date,
    table_name,
    change_type,
    COUNT(*) as change_count
FROM log_data_changes
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at), table_name, change_type
ORDER BY change_date DESC, table_name;

-- ============================================================
-- FUNCTIONS FOR LOG MANAGEMENT
-- ============================================================

-- Function to clean up old logs (keep last N days)
CREATE OR REPLACE FUNCTION cleanup_old_logs(days_to_keep INTEGER DEFAULT 30)
RETURNS TABLE(table_name TEXT, rows_deleted BIGINT) AS $$
DECLARE
    cutoff_date TIMESTAMPTZ := NOW() - (days_to_keep || ' days')::INTERVAL;
    deleted_count BIGINT;
BEGIN
    -- Delete old test results
    DELETE FROM log_test_results WHERE created_at < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    table_name := 'log_test_results'; rows_deleted := deleted_count;
    RETURN NEXT;
    
    -- Delete old data changes
    DELETE FROM log_data_changes WHERE created_at < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    table_name := 'log_data_changes'; rows_deleted := deleted_count;
    RETURN NEXT;
    
    -- Delete old errors (keep unresolved)
    DELETE FROM log_errors WHERE created_at < cutoff_date AND resolved = TRUE;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    table_name := 'log_errors'; rows_deleted := deleted_count;
    RETURN NEXT;
    
    -- Delete old table logs
    DELETE FROM log_etl_tables WHERE created_at < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    table_name := 'log_etl_tables'; rows_deleted := deleted_count;
    RETURN NEXT;
    
    -- Delete old runs
    DELETE FROM log_etl_runs WHERE created_at < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    table_name := 'log_etl_runs'; rows_deleted := deleted_count;
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Function to get run summary
CREATE OR REPLACE FUNCTION get_run_summary(p_run_id VARCHAR)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'run', (SELECT row_to_json(r) FROM log_etl_runs r WHERE run_id = p_run_id),
        'tables', (SELECT jsonb_agg(row_to_json(t)) FROM log_etl_tables t WHERE run_id = p_run_id),
        'errors', (SELECT jsonb_agg(row_to_json(e)) FROM log_errors e WHERE run_id = p_run_id),
        'tests', (SELECT jsonb_agg(row_to_json(tr)) FROM log_test_results tr WHERE run_id = p_run_id)
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to mark error as resolved
CREATE OR REPLACE FUNCTION resolve_error(
    p_error_id BIGINT,
    p_resolved_by VARCHAR,
    p_notes TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE log_errors
    SET 
        resolved = TRUE,
        resolved_at = NOW(),
        resolved_by = p_resolved_by,
        resolution_notes = p_notes
    WHERE id = p_error_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- TRIGGERS FOR AUTO-UPDATE
-- ============================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_log_etl_runs_updated_at
    BEFORE UPDATE ON log_etl_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- SAMPLE QUERIES FOR MONITORING
-- ============================================================

/*
-- Get last 10 runs with status
SELECT * FROM v_recent_runs LIMIT 10;

-- Get today's run statistics
SELECT * FROM v_daily_run_stats WHERE run_date = CURRENT_DATE;

-- Get table load performance
SELECT * FROM v_table_load_stats;

-- Get unresolved errors
SELECT * FROM v_unresolved_errors;

-- Get test pass rates
SELECT * FROM v_test_pass_rate;

-- Get full run summary
SELECT get_run_summary('etl_run_20251230_123456_abc12345');

-- Clean up logs older than 30 days
SELECT * FROM cleanup_old_logs(30);

-- Mark error as resolved
SELECT resolve_error(123, 'ronnie', 'Fixed by updating CSV encoding');
*/

-- ============================================================
-- GRANT PERMISSIONS (uncomment as needed)
-- ============================================================

-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT INSERT, UPDATE ON log_etl_runs TO service_role;
-- GRANT INSERT ON log_etl_tables TO service_role;
-- GRANT INSERT, UPDATE ON log_errors TO service_role;
-- GRANT INSERT ON log_test_results TO service_role;
-- GRANT INSERT ON log_data_changes TO service_role;

COMMENT ON TABLE log_etl_runs IS 'Tracks all ETL and deployment runs';
COMMENT ON TABLE log_etl_tables IS 'Tracks individual table load operations within a run';
COMMENT ON TABLE log_errors IS 'Tracks errors with resolution tracking';
COMMENT ON TABLE log_test_results IS 'Tracks test execution results';
COMMENT ON TABLE log_data_changes IS 'Tracks data changes for audit purposes';
