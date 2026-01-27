-- ============================================================================
-- BASELINE MIGRATION
-- This marks the initial schema as "already applied"
-- All tables created via reset_supabase.sql are considered baseline
-- ============================================================================

-- This migration is intentionally empty.
-- It serves as a marker that the initial schema (from reset_supabase.sql)
-- has been applied to both dev and prod databases.

-- Future migrations will contain only INCREMENTAL changes:
-- - ALTER TABLE ADD COLUMN
-- - CREATE TABLE IF NOT EXISTS (for new tables)
-- - CREATE OR REPLACE VIEW (for view updates)

-- DO NOT put DROP statements in migrations unless absolutely necessary
-- and you've backed up the data.

SELECT 'Baseline migration applied' AS status;
