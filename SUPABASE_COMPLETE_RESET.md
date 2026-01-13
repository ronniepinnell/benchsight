# Supabase Complete Reset Guide

## Overview

This guide covers wiping Supabase, recreating schema, and uploading all data.

**Final State:**
- 139 ETL tables
- 30 Supabase views
- 169 total database objects

---

## Step 1: Wipe Supabase (Run in SQL Editor)

Copy and paste this entire block into Supabase SQL Editor and run:

```sql
-- ============================================================
-- COMPLETE SUPABASE WIPE - RUN THIS FIRST
-- ============================================================

-- 1. Drop all views
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT table_name FROM information_schema.views WHERE table_schema = 'public'
    LOOP
        EXECUTE 'DROP VIEW IF EXISTS ' || quote_ident(r.table_name) || ' CASCADE';
    END LOOP;
END $$;

-- 2. Drop all tables
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;

-- 3. Verify clean slate
SELECT 
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE') as tables,
    (SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'public') as views;
-- Should return: tables=0, views=0
```

---

## Step 2: Generate Schema (Terminal)

```bash
python upload.py --schema
```

This creates/updates `sql/reset_supabase.sql` with CREATE TABLE statements.

---

## Step 3: Create Tables (SQL Editor)

Run the contents of `sql/reset_supabase.sql` in Supabase SQL Editor.

---

## Step 4: Upload Data (Terminal)

```bash
# Upload all tables (recommended)
python upload.py

# Or upload in batches if timeout issues:
python upload.py --dims      # Dimension tables first
python upload.py --facts     # Then fact tables
python upload.py --qa        # Then QA/lookup tables
```

**Expected output:** 139 tables uploaded

---

## Step 5: Deploy Views (SQL Editor)

Run `sql/views/99_DEPLOY_ALL_VIEWS.sql` in Supabase SQL Editor.

---

## Step 6: Verify (SQL Editor)

```sql
-- Check table count (should be 139)
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- Check view count (should be ~20)
SELECT COUNT(*) as view_count 
FROM information_schema.views 
WHERE table_schema = 'public';

-- Test key views
SELECT * FROM v_standings_current LIMIT 5;
SELECT * FROM v_leaderboard_points LIMIT 10;

-- Verify goal count (should be 17)
SELECT COUNT(*) as total_goals 
FROM fact_events 
WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored';
```

---

## Upload Command Reference

| Command | Description |
|---------|-------------|
| `python upload.py` | Upload ALL tables |
| `python upload.py --dims` | Dimension tables only (dim_*) |
| `python upload.py --facts` | Fact tables only (fact_*) |
| `python upload.py --qa` | QA/lookup tables only |
| `python upload.py --basic` | Basic stats tables (*_basic) |
| `python upload.py --tables dim_player dim_team` | Specific tables |
| `python upload.py --pattern "fact_player*"` | Pattern matching |
| `python upload.py --list` | List all tables |
| `python upload.py --list --dims` | List dimension tables |
| `python upload.py --dry-run` | Preview without uploading |
| `python upload.py --schema` | Generate schema SQL |

---

## Troubleshooting

### Upload fails with timeout
- Use batch upload: `--dims`, then `--facts`, then `--qa`
- Check Supabase connection in config/config_local.ini

### View creation fails
- Ensure all tables uploaded first
- Check for typos in table names
- Run views one file at a time (01, 02, 03... then 99)

### Wrong table/view count
- Re-run wipe script
- Re-upload tables
- Re-deploy views

---

## Quick Reference

| Item | Expected Count |
|------|----------------|
| Tables | 139 |
| Views | ~20 |
| Goals | 17 |
| Tracked Games | 4 |
| Players in dim_player | 400+ |
| Teams in dim_team | 12 |
