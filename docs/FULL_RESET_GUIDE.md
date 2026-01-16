# Complete ETL + Supabase Reset Guide

This guide walks you through the complete process of:
1. Running full ETL
2. Wiping Supabase
3. Recreating schema
4. Uploading all data

---

## Step 1: Run Full ETL

Run the complete ETL pipeline to generate all CSV files in `data/output/`:

```bash
# Option A: Clean slate (recommended for fresh start)
python run_etl.py --wipe

# Option B: Standard run (keeps existing files)
python run_etl.py
```

**Expected output:**
- ~139 tables created in `data/output/`
- Duration: ~80 seconds
- All tables should be CSV files

**Verify ETL completed:**
```bash
python run_etl.py --validate
```

---

## Step 2: Wipe Supabase (SQL Editor)

Open your Supabase project → SQL Editor and run this script to drop all views and tables:

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

**Expected result:** Both counts should be 0.

---

## Step 3: Generate Schema SQL

Generate the CREATE TABLE statements from your ETL output:

```bash
python upload.py --schema
```

This creates/updates `sql/reset_supabase.sql` with:
- DROP TABLE statements (for safety)
- CREATE TABLE statements with proper data types

**Expected output:**
```
Generated sql/reset_supabase.sql
Tables: 139
```

---

## Step 4: Create Schema in Supabase (SQL Editor)

1. Open `sql/reset_supabase.sql` in your editor
2. Copy the entire contents
3. Paste into Supabase SQL Editor
4. Execute

**Note:** The file contains both DROP and CREATE statements, so it's safe to run even if tables exist.

**Expected result:** 139 tables created (verify with table count query if needed)

---

## Step 5: Upload Data to Supabase

Upload all CSV files from `data/output/` to Supabase:

```bash
# Upload all tables (recommended)
python upload.py
```

**Alternative: Batch upload** (if you encounter timeout issues):

```bash
python upload.py --dims      # Dimension tables first (~40 tables)
python upload.py --facts     # Fact tables next (~95 tables)
python upload.py --qa        # QA/lookup tables last (~4 tables)
```

**Expected output:**
```
Success: 139/139
Failed:  0
Rows:    [varies based on data]
✓ Upload complete!
```

---

## Step 6: (Optional) Deploy Views

If you have views defined, deploy them:

1. Open Supabase SQL Editor
2. Run `sql/views/99_DEPLOY_ALL_VIEWS.sql` (or individual view files)

---

## Step 7: Verify Everything

Run verification queries in Supabase SQL Editor:

```sql
-- Check table count (should be 139)
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- Check view count (if views deployed)
SELECT COUNT(*) as view_count 
FROM information_schema.views 
WHERE table_schema = 'public';

-- Test a key table
SELECT COUNT(*) FROM dim_player;
SELECT COUNT(*) FROM fact_events;

-- Verify goal count (should match your data)
SELECT COUNT(*) as total_goals 
FROM fact_events 
WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored';
```

---

## Quick Reference: All Commands

```bash
# 1. Run ETL
python run_etl.py --wipe

# 2. Generate schema
python upload.py --schema

# 3. (In Supabase SQL Editor) Run wipe script, then sql/reset_supabase.sql

# 4. Upload data
python upload.py

# 5. (Optional) Deploy views in SQL Editor
```

---

## Troubleshooting

### ETL fails
- Check `data/raw/` has game data
- Verify `config/config.ini` is configured
- Run `python run_etl.py --status` to check current state

### Upload fails with timeout
- Use batch upload: `--dims`, then `--facts`, then `--qa`
- Check Supabase connection in `config/config_local.ini`
- Verify network connection

### Schema generation fails
- Ensure ETL completed successfully
- Check `data/output/` has CSV files
- Verify at least one table exists

### Wrong table count
- Re-run wipe script in SQL Editor
- Re-generate schema: `python upload.py --schema`
- Re-run `sql/reset_supabase.sql`
- Re-upload: `python upload.py`

---

## Expected Final State

| Item | Expected Count |
|------|----------------|
| ETL Tables (CSV) | 139 |
| Supabase Tables | 139 |
| Views (if deployed) | ~20 |
| Goals in fact_events | Varies by data |

---

## One-Line Script (All Steps)

For convenience, you can also use the combined script:

```bash
python run_etl_and_upload.py
```

**Note:** This runs ETL + Upload, but you still need to:
1. Wipe Supabase (Step 2)
2. Generate and run schema (Steps 3-4)

---

## Related Documentation

- `docs/archive/SUPABASE_COMPLETE_RESET.md` - Detailed reset guide
- `docs/SUPABASE.md` - Supabase configuration
- `run_etl.py` - ETL script documentation
- `upload.py` - Upload script documentation
