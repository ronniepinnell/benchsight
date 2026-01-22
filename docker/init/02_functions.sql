-- BenchSight ETL Debug: Helper Functions
-- =======================================

-- Function: Get row counts for all tables in a schema
CREATE OR REPLACE FUNCTION get_table_counts(schema_name text)
RETURNS TABLE(table_name text, row_count bigint) AS $$
DECLARE
    rec RECORD;
    cnt bigint;
BEGIN
    FOR rec IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = schema_name
        ORDER BY tablename
    LOOP
        EXECUTE format('SELECT count(*) FROM %I.%I', schema_name, rec.tablename) INTO cnt;
        table_name := rec.tablename;
        row_count := cnt;
        RETURN NEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function: Get total row count for a schema
CREATE OR REPLACE FUNCTION get_schema_total(schema_name text)
RETURNS bigint AS $$
DECLARE
    total bigint := 0;
BEGIN
    SELECT COALESCE(SUM(row_count), 0) INTO total
    FROM get_table_counts(schema_name);
    RETURN total;
END;
$$ LANGUAGE plpgsql;

-- Function: Compare row counts between two schemas
CREATE OR REPLACE FUNCTION compare_schemas(schema1 text, schema2 text)
RETURNS TABLE(
    table_name text,
    schema1_count bigint,
    schema2_count bigint,
    diff bigint,
    pct_diff numeric
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(s1.table_name, s2.table_name),
        COALESCE(s1.row_count, 0),
        COALESCE(s2.row_count, 0),
        COALESCE(s1.row_count, 0) - COALESCE(s2.row_count, 0),
        CASE
            WHEN COALESCE(s2.row_count, 0) = 0 THEN NULL
            ELSE ROUND(((COALESCE(s1.row_count, 0) - COALESCE(s2.row_count, 0))::numeric / s2.row_count * 100), 2)
        END
    FROM get_table_counts(schema1) s1
    FULL OUTER JOIN get_table_counts(schema2) s2 USING (table_name)
    ORDER BY ABS(COALESCE(s1.row_count, 0) - COALESCE(s2.row_count, 0)) DESC;
END;
$$ LANGUAGE plpgsql;

-- Function: Get summary of all schemas
CREATE OR REPLACE FUNCTION schema_summary()
RETURNS TABLE(
    schema_name text,
    table_count integer,
    total_rows bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.nspname::text,
        COUNT(t.tablename)::integer,
        COALESCE((SELECT SUM(row_count) FROM get_table_counts(s.nspname)), 0)
    FROM pg_namespace s
    LEFT JOIN pg_tables t ON t.schemaname = s.nspname
    WHERE s.nspname IN ('raw', 'stage', 'intermediate', 'datamart')
    GROUP BY s.nspname
    ORDER BY
        CASE s.nspname
            WHEN 'raw' THEN 1
            WHEN 'stage' THEN 2
            WHEN 'intermediate' THEN 3
            WHEN 'datamart' THEN 4
        END;
END;
$$ LANGUAGE plpgsql;

-- Function: Find tables with high null percentages
CREATE OR REPLACE FUNCTION find_high_null_tables(schema_name text, threshold numeric DEFAULT 20.0)
RETURNS TABLE(
    table_name text,
    column_name text,
    null_count bigint,
    total_count bigint,
    null_pct numeric
) AS $$
DECLARE
    rec RECORD;
    col RECORD;
    null_cnt bigint;
    total_cnt bigint;
    pct numeric;
BEGIN
    FOR rec IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = schema_name
    LOOP
        -- Get total count for table
        EXECUTE format('SELECT count(*) FROM %I.%I', schema_name, rec.tablename) INTO total_cnt;

        IF total_cnt > 0 THEN
            -- Check each column
            FOR col IN
                SELECT column_name as colname
                FROM information_schema.columns
                WHERE table_schema = schema_name AND table_name = rec.tablename
            LOOP
                EXECUTE format('SELECT count(*) FROM %I.%I WHERE %I IS NULL',
                    schema_name, rec.tablename, col.colname) INTO null_cnt;

                pct := ROUND((null_cnt::numeric / total_cnt * 100), 2);

                IF pct >= threshold THEN
                    table_name := rec.tablename;
                    column_name := col.colname;
                    null_count := null_cnt;
                    total_count := total_cnt;
                    null_pct := pct;
                    RETURN NEXT;
                END IF;
            END LOOP;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function: Get phase completion status
CREATE OR REPLACE FUNCTION get_phase_status(p_run_id text DEFAULT NULL)
RETURNS TABLE(
    run_id text,
    phase_id text,
    phase_name text,
    status text,
    tables_created integer,
    duration interval
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pl.run_id::text,
        pl.phase_id::text,
        pl.phase_name::text,
        pl.status::text,
        pl.tables_created,
        pl.completed_at - pl.started_at
    FROM public.phase_log pl
    WHERE (p_run_id IS NULL OR pl.run_id = p_run_id)
    ORDER BY pl.started_at;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION get_table_counts(text) TO PUBLIC;
GRANT EXECUTE ON FUNCTION get_schema_total(text) TO PUBLIC;
GRANT EXECUTE ON FUNCTION compare_schemas(text, text) TO PUBLIC;
GRANT EXECUTE ON FUNCTION schema_summary() TO PUBLIC;
GRANT EXECUTE ON FUNCTION find_high_null_tables(text, numeric) TO PUBLIC;
GRANT EXECUTE ON FUNCTION get_phase_status(text) TO PUBLIC;
