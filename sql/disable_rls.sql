-- BenchSight: Disable RLS for All Tables
-- Run this AFTER reset_supabase.sql to allow public access
-- For development/testing only - add proper policies for production

-- ============================================================
-- OPTION 1: Disable RLS entirely (simplest for development)
-- ============================================================

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE 'ALTER TABLE public.' || quote_ident(r.tablename) || ' DISABLE ROW LEVEL SECURITY';
    END LOOP;
END $$;

-- ============================================================
-- OPTION 2: Enable RLS with public read access (for dashboard)
-- Only use this if you want some security
-- ============================================================

-- Uncomment below to enable RLS with public read:

/*
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        -- Enable RLS
        EXECUTE 'ALTER TABLE public.' || quote_ident(r.tablename) || ' ENABLE ROW LEVEL SECURITY';
        
        -- Create public read policy
        EXECUTE 'DROP POLICY IF EXISTS "Public read" ON public.' || quote_ident(r.tablename);
        EXECUTE 'CREATE POLICY "Public read" ON public.' || quote_ident(r.tablename) || ' FOR SELECT USING (true)';
        
        -- Create public insert policy (for tracker)
        EXECUTE 'DROP POLICY IF EXISTS "Public insert" ON public.' || quote_ident(r.tablename);
        EXECUTE 'CREATE POLICY "Public insert" ON public.' || quote_ident(r.tablename) || ' FOR INSERT WITH CHECK (true)';
        
        -- Create public update policy
        EXECUTE 'DROP POLICY IF EXISTS "Public update" ON public.' || quote_ident(r.tablename);
        EXECUTE 'CREATE POLICY "Public update" ON public.' || quote_ident(r.tablename) || ' FOR UPDATE USING (true) WITH CHECK (true)';
        
        -- Create public delete policy
        EXECUTE 'DROP POLICY IF EXISTS "Public delete" ON public.' || quote_ident(r.tablename);
        EXECUTE 'CREATE POLICY "Public delete" ON public.' || quote_ident(r.tablename) || ' FOR DELETE USING (true)';
    END LOOP;
END $$;
*/

-- ============================================================
-- Verify RLS status
-- ============================================================

SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
