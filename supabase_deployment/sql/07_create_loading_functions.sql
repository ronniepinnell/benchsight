-- ================================================================
-- BenchSight Loading Functions
-- PostgreSQL functions for flexible data loading operations
-- ================================================================

-- ================================================================
-- FUNCTION: Get table row count
-- ================================================================
CREATE OR REPLACE FUNCTION get_table_count(p_table_name TEXT)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    EXECUTE format('SELECT COUNT(*) FROM %I', p_table_name) INTO v_count;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- FUNCTION: Get all table counts
-- ================================================================
CREATE OR REPLACE FUNCTION get_all_table_counts()
RETURNS TABLE(table_name TEXT, row_count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT 'dim_player'::TEXT, COUNT(*)::BIGINT FROM dim_player
    UNION ALL SELECT 'dim_team', COUNT(*) FROM dim_team
    UNION ALL SELECT 'dim_schedule', COUNT(*) FROM dim_schedule
    UNION ALL SELECT 'fact_shifts', COUNT(*) FROM fact_shifts
    UNION ALL SELECT 'fact_events', COUNT(*) FROM fact_events
    UNION ALL SELECT 'fact_events_player', COUNT(*) FROM fact_events_player
    UNION ALL SELECT 'fact_shifts_player', COUNT(*) FROM fact_shifts_player
    UNION ALL SELECT 'fact_player_game_stats', COUNT(*) FROM fact_player_game_stats
    UNION ALL SELECT 'fact_team_game_stats', COUNT(*) FROM fact_team_game_stats
    UNION ALL SELECT 'fact_goalie_game_stats', COUNT(*) FROM fact_goalie_game_stats
    UNION ALL SELECT 'fact_h2h', COUNT(*) FROM fact_h2h
    UNION ALL SELECT 'fact_wowy', COUNT(*) FROM fact_wowy
    UNION ALL SELECT 'staging_events', COUNT(*) FROM staging_events
    UNION ALL SELECT 'staging_shifts', COUNT(*) FROM staging_shifts
    ORDER BY 1;
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- FUNCTION: Delete game data from all tables
-- ================================================================
CREATE OR REPLACE FUNCTION delete_game_data(p_game_id INTEGER)
RETURNS JSON AS $$
DECLARE
    v_deleted_counts JSON;
    v_total INTEGER := 0;
    v_wowy INTEGER;
    v_h2h INTEGER;
    v_goalie INTEGER;
    v_team INTEGER;
    v_player INTEGER;
    v_shifts_player INTEGER;
    v_events_player INTEGER;
    v_events INTEGER;
    v_shifts INTEGER;
    v_staging_events INTEGER;
    v_staging_shifts INTEGER;
BEGIN
    -- Delete in reverse dependency order
    
    -- Analytics facts
    DELETE FROM fact_wowy WHERE game_id = p_game_id;
    GET DIAGNOSTICS v_wowy = ROW_COUNT;
    
    DELETE FROM fact_h2h WHERE game_id = p_game_id;
    GET DIAGNOSTICS v_h2h = ROW_COUNT;
    
    -- Stats facts
    DELETE FROM fact_goalie_game_stats WHERE game_id = p_game_id;
    GET DIAGNOSTICS v_goalie = ROW_COUNT;
    
    DELETE FROM fact_team_game_stats WHERE game_id = p_game_id;
    GET DIAGNOSTICS v_team = ROW_COUNT;
    
    DELETE FROM fact_player_game_stats WHERE game_id = p_game_id;
    GET DIAGNOSTICS v_player = ROW_COUNT;
    
    -- Long format facts
    DELETE FROM fact_shifts_player WHERE game_id = p_game_id;
    GET DIAGNOSTICS v_shifts_player = ROW_COUNT;
    
    DELETE FROM fact_events_player WHERE game_id = p_game_id;
    GET DIAGNOSTICS v_events_player = ROW_COUNT;
    
    -- Core facts
    DELETE FROM fact_events WHERE game_id = p_game_id;
    GET DIAGNOSTICS v_events = ROW_COUNT;
    
    DELETE FROM fact_shifts WHERE game_id = p_game_id;
    GET DIAGNOSTICS v_shifts = ROW_COUNT;
    
    -- Staging tables
    DELETE FROM staging_events WHERE game_id = p_game_id;
    GET DIAGNOSTICS v_staging_events = ROW_COUNT;
    
    DELETE FROM staging_shifts WHERE game_id = p_game_id;
    GET DIAGNOSTICS v_staging_shifts = ROW_COUNT;
    
    v_total := v_wowy + v_h2h + v_goalie + v_team + v_player + 
               v_shifts_player + v_events_player + v_events + v_shifts +
               v_staging_events + v_staging_shifts;
    
    -- Log the operation
    INSERT INTO load_history (
        table_name, category, game_id, operation, source,
        rows_affected, started_at, completed_at, status
    ) VALUES (
        'ALL', 'game_delete', p_game_id, 'delete', 'function',
        v_total, NOW(), NOW(), 'completed'
    );
    
    RETURN json_build_object(
        'success', true,
        'game_id', p_game_id,
        'total_deleted', v_total,
        'details', json_build_object(
            'fact_wowy', v_wowy,
            'fact_h2h', v_h2h,
            'fact_goalie_game_stats', v_goalie,
            'fact_team_game_stats', v_team,
            'fact_player_game_stats', v_player,
            'fact_shifts_player', v_shifts_player,
            'fact_events_player', v_events_player,
            'fact_events', v_events,
            'fact_shifts', v_shifts,
            'staging_events', v_staging_events,
            'staging_shifts', v_staging_shifts
        )
    );
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- FUNCTION: Truncate table(s) by category
-- ================================================================
CREATE OR REPLACE FUNCTION truncate_category(p_category TEXT)
RETURNS JSON AS $$
DECLARE
    v_tables TEXT[];
    v_table TEXT;
BEGIN
    -- Define categories
    CASE p_category
        WHEN 'dims' THEN
            v_tables := ARRAY['dim_player', 'dim_team', 'dim_schedule'];
        WHEN 'staging' THEN
            v_tables := ARRAY['staging_events', 'staging_shifts'];
        WHEN 'core_facts' THEN
            v_tables := ARRAY['fact_shifts', 'fact_events', 'fact_events_player', 'fact_shifts_player'];
        WHEN 'stats_facts' THEN
            v_tables := ARRAY['fact_player_game_stats', 'fact_team_game_stats', 'fact_goalie_game_stats'];
        WHEN 'analytics_facts' THEN
            v_tables := ARRAY['fact_h2h', 'fact_wowy'];
        WHEN 'all_facts' THEN
            v_tables := ARRAY[
                'fact_wowy', 'fact_h2h',
                'fact_goalie_game_stats', 'fact_team_game_stats', 'fact_player_game_stats',
                'fact_shifts_player', 'fact_events_player',
                'fact_events', 'fact_shifts'
            ];
        WHEN 'all' THEN
            v_tables := ARRAY[
                'fact_wowy', 'fact_h2h',
                'fact_goalie_game_stats', 'fact_team_game_stats', 'fact_player_game_stats',
                'fact_shifts_player', 'fact_events_player',
                'fact_events', 'fact_shifts',
                'staging_events', 'staging_shifts',
                'dim_schedule', 'dim_team', 'dim_player'
            ];
        ELSE
            RETURN json_build_object('success', false, 'error', 'Invalid category: ' || p_category);
    END CASE;
    
    -- Truncate in dependency order (reverse for facts)
    FOREACH v_table IN ARRAY v_tables LOOP
        EXECUTE format('TRUNCATE TABLE %I CASCADE', v_table);
    END LOOP;
    
    -- Log the operation
    INSERT INTO load_history (
        category, operation, source, started_at, completed_at, status, notes
    ) VALUES (
        p_category, 'truncate', 'function', NOW(), NOW(), 'completed',
        'Truncated tables: ' || array_to_string(v_tables, ', ')
    );
    
    RETURN json_build_object(
        'success', true,
        'category', p_category,
        'tables_truncated', v_tables
    );
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- FUNCTION: Get games list with tracking status
-- ================================================================
CREATE OR REPLACE FUNCTION get_games_with_status()
RETURNS TABLE(
    game_id INTEGER,
    game_date DATE,
    home_team VARCHAR,
    away_team VARCHAR,
    home_score INTEGER,
    away_score INTEGER,
    events_count BIGINT,
    shifts_count BIGINT,
    has_player_stats BOOLEAN,
    staging_events_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.game_id,
        s.date,
        s.home_team_name,
        s.away_team_name,
        s.home_total_goals,
        s.away_total_goals,
        COALESCE(e.cnt, 0)::BIGINT as events_count,
        COALESCE(sh.cnt, 0)::BIGINT as shifts_count,
        COALESCE(ps.cnt, 0) > 0 as has_player_stats,
        COALESCE(se.cnt, 0)::BIGINT as staging_events_count
    FROM dim_schedule s
    LEFT JOIN (SELECT game_id, COUNT(*) as cnt FROM fact_events GROUP BY game_id) e ON s.game_id = e.game_id
    LEFT JOIN (SELECT game_id, COUNT(*) as cnt FROM fact_shifts GROUP BY game_id) sh ON s.game_id = sh.game_id
    LEFT JOIN (SELECT game_id, COUNT(*) as cnt FROM fact_player_game_stats GROUP BY game_id) ps ON s.game_id = ps.game_id
    LEFT JOIN (SELECT game_id, COUNT(*) as cnt FROM staging_events GROUP BY game_id) se ON s.game_id = se.game_id
    ORDER BY s.date DESC, s.game_id DESC;
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- FUNCTION: Queue ETL job
-- ================================================================
CREATE OR REPLACE FUNCTION queue_etl_job(
    p_game_id INTEGER DEFAULT NULL,
    p_operation VARCHAR DEFAULT 'process_game',
    p_priority INTEGER DEFAULT 5,
    p_requested_by VARCHAR DEFAULT 'api'
)
RETURNS JSON AS $$
DECLARE
    v_queue_id INTEGER;
BEGIN
    INSERT INTO etl_queue (game_id, operation, priority, requested_by)
    VALUES (p_game_id, p_operation, p_priority, p_requested_by)
    RETURNING id INTO v_queue_id;
    
    RETURN json_build_object(
        'success', true,
        'queue_id', v_queue_id,
        'game_id', p_game_id,
        'operation', p_operation,
        'priority', p_priority
    );
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- FUNCTION: Get pending ETL jobs
-- ================================================================
CREATE OR REPLACE FUNCTION get_pending_etl_jobs()
RETURNS TABLE(
    id INTEGER,
    game_id INTEGER,
    operation VARCHAR,
    priority INTEGER,
    requested_at TIMESTAMP,
    requested_by VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        q.id,
        q.game_id,
        q.operation,
        q.priority,
        q.requested_at,
        q.requested_by
    FROM etl_queue q
    WHERE q.status = 'pending'
    ORDER BY q.priority DESC, q.requested_at ASC;
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- FUNCTION: Mark ETL job as processing
-- ================================================================
CREATE OR REPLACE FUNCTION start_etl_job(p_queue_id INTEGER, p_processor VARCHAR DEFAULT 'etl')
RETURNS JSON AS $$
DECLARE
    v_game_id INTEGER;
BEGIN
    UPDATE etl_queue 
    SET status = 'processing', 
        started_at = NOW(),
        processed_by = p_processor
    WHERE id = p_queue_id AND status = 'pending'
    RETURNING game_id INTO v_game_id;
    
    IF v_game_id IS NULL THEN
        RETURN json_build_object('success', false, 'error', 'Job not found or already processing');
    END IF;
    
    RETURN json_build_object('success', true, 'queue_id', p_queue_id, 'game_id', v_game_id);
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- FUNCTION: Complete ETL job
-- ================================================================
CREATE OR REPLACE FUNCTION complete_etl_job(
    p_queue_id INTEGER,
    p_rows_processed INTEGER DEFAULT 0,
    p_error_message TEXT DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
    v_status VARCHAR;
BEGIN
    v_status := CASE WHEN p_error_message IS NULL THEN 'completed' ELSE 'failed' END;
    
    UPDATE etl_queue 
    SET status = v_status, 
        completed_at = NOW(),
        rows_processed = p_rows_processed,
        error_message = p_error_message
    WHERE id = p_queue_id;
    
    RETURN json_build_object(
        'success', true, 
        'queue_id', p_queue_id, 
        'status', v_status,
        'rows_processed', p_rows_processed
    );
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- FUNCTION: Get recent load history
-- ================================================================
CREATE OR REPLACE FUNCTION get_load_history(p_limit INTEGER DEFAULT 20)
RETURNS TABLE(
    id INTEGER,
    table_name VARCHAR,
    category VARCHAR,
    game_id INTEGER,
    operation VARCHAR,
    rows_affected INTEGER,
    status VARCHAR,
    started_at TIMESTAMP,
    duration_ms INTEGER,
    initiated_by VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        h.id,
        h.table_name,
        h.category,
        h.game_id,
        h.operation,
        h.rows_affected,
        h.status,
        h.started_at,
        h.duration_ms,
        h.initiated_by
    FROM load_history h
    ORDER BY h.started_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- FUNCTION: Log a load operation
-- ================================================================
CREATE OR REPLACE FUNCTION log_load_operation(
    p_table_name VARCHAR,
    p_operation VARCHAR,
    p_game_id INTEGER DEFAULT NULL,
    p_rows_affected INTEGER DEFAULT 0,
    p_status VARCHAR DEFAULT 'completed',
    p_initiated_by VARCHAR DEFAULT 'api',
    p_error_message TEXT DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_id INTEGER;
BEGIN
    INSERT INTO load_history (
        table_name, operation, game_id, rows_affected, 
        started_at, completed_at, status, initiated_by, error_message
    ) VALUES (
        p_table_name, p_operation, p_game_id, p_rows_affected,
        NOW(), NOW(), p_status, p_initiated_by, p_error_message
    )
    RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- COMMENTS
-- ================================================================
COMMENT ON FUNCTION delete_game_data IS 'Delete all data for a specific game across all fact tables';
COMMENT ON FUNCTION truncate_category IS 'Truncate all tables in a category (dims, facts, all)';
COMMENT ON FUNCTION get_games_with_status IS 'Get all games with their tracking/processing status';
COMMENT ON FUNCTION queue_etl_job IS 'Add an ETL processing job to the queue';
COMMENT ON FUNCTION get_pending_etl_jobs IS 'Get all pending ETL jobs ordered by priority';
