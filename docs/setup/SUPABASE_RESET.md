# BenchSight Supabase Reset Game Plan

## Overview

This document outlines the complete process to:
1. Wipe Supabase
2. Deploy new schema
3. Upload all data
4. Create views
5. Connect dashboard

---

## Phase 1: Identify Tables to Keep vs Drop

### KEEP (Core ETL Tables) - 139 tables

These tables contain validated, complex calculations that can't be efficiently computed as views:

| Category | Tables | Reason |
|----------|--------|--------|
| **Dimensions** | dim_* (40 tables) | Reference data, small |
| **Game-Level Facts** | fact_player_game_stats, fact_goalie_game_stats | 444/128 cols, micro-stats |
| **Event Facts** | fact_events, fact_event_players, fact_tracking | Raw event data |
| **Basic Stats** | fact_*_basic (5 tables) | Official league data |
| **Advanced Tracking** | fact_shifts, fact_zone_entries, fact_faceoffs, etc. | Event-level tracking |

### DROP (Replaced by Views) - 5 tables

| Table | Rows | Replaced By | Reason |
|-------|------|-------------|--------|
| fact_league_leaders_snapshot | 20 | v_leaderboard_* | Simple aggregation |
| fact_team_standings_snapshot | 5 | v_standings_current | Simple aggregation |
| fact_season_summary | 1 | v_summary_league | Simple aggregation |
| fact_player_career_stats | 63 | v_summary_player_career + fact_player_career_stats_basic | Redundant |
| fact_team_season_stats | 5 | v_compare_teams + fact_team_season_stats_basic | Redundant |

**New Table Count: 142 - 5 = 137 tables**

---

## Phase 2: Supabase Wipe Script

Run in Supabase SQL Editor:

```sql
-- ============================================================
-- STEP 1: Drop all views first (they depend on tables)
-- ============================================================
DO $$ 
DECLARE
    view_name TEXT;
BEGIN
    FOR view_name IN 
        SELECT table_name FROM information_schema.views 
        WHERE table_schema = 'public'
    LOOP
        EXECUTE 'DROP VIEW IF EXISTS ' || quote_ident(view_name) || ' CASCADE';
    END LOOP;
END $$;

-- ============================================================
-- STEP 2: Drop all tables
-- ============================================================
DO $$ 
DECLARE
    table_name TEXT;
BEGIN
    FOR table_name IN 
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(table_name) || ' CASCADE';
    END LOOP;
END $$;

-- ============================================================
-- STEP 3: Verify clean slate
-- ============================================================
SELECT 
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public') as tables,
    (SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'public') as views;
-- Should return: tables=0, views=0
```

---

## Phase 3: Deploy Schema & Data

### Option A: Python Upload Script

```bash
# From benchsight directory
cd /path/to/benchsight_v28

# Upload all tables (schema auto-created)
python upload.py

# Or specific groups
python upload.py --tables dim_*
python upload.py --tables fact_*_basic
python upload.py --tables fact_player_game_stats fact_goalie_game_stats
```

### Option B: Manual CSV Import

1. Go to Supabase Dashboard → Table Editor
2. Click "New Table" → "Import from CSV"
3. Upload CSVs in order:
   - dim_* tables first (reference data)
   - fact_* tables second

---

## Phase 4: Create Views

After tables are populated, run in SQL Editor:

```sql
-- Run the full view deployment script
-- File: sql/views/99_DEPLOY_ALL_VIEWS.sql
```

Or run individual view files:
1. `01_leaderboard_views.sql`
2. `02_standings_views.sql`
3. `03_rankings_views.sql`
4. `04_summary_views.sql`
5. `05_recent_views.sql`
6. `06_comparison_views.sql`
7. `07_detail_views.sql`
8. `08_tracking_advanced_views.sql`

---

## Phase 5: Verify Deployment

```sql
-- Count tables
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
-- Expected: ~137

-- Count views
SELECT COUNT(*) as view_count 
FROM information_schema.views 
WHERE table_schema = 'public';
-- Expected: ~30

-- Test a view
SELECT * FROM v_standings_current LIMIT 5;
SELECT * FROM v_leaderboard_points LIMIT 10;
```

---

## Phase 6: Dashboard Connection

See `docs/DASHBOARD_INTEGRATION.md` for full details.

Quick start:
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://YOUR_PROJECT.supabase.co',
  'YOUR_ANON_KEY'
)

// Query a view (same as table)
const { data } = await supabase
  .from('v_standings_current')
  .select('*')
```

---

## Checklist

### Pre-Deployment
- [ ] Run fresh ETL locally: `python run_etl.py`
- [ ] Verify 142 tables created
- [ ] Remove deprecated tables from ETL (optional)

### Supabase Wipe
- [ ] Run wipe script in SQL Editor
- [ ] Verify 0 tables, 0 views

### Data Upload
- [ ] Upload all CSV files via upload.py or UI
- [ ] Verify row counts match local

### View Creation
- [ ] Run 99_DEPLOY_ALL_VIEWS.sql
- [ ] Verify ~30 views created
- [ ] Test sample queries

### Dashboard
- [ ] Update supabase URL/key in dashboard
- [ ] Test each page loads data
- [ ] Verify filters work

---

## Rollback Plan

If something goes wrong:

```sql
-- Restore from backup (if you have one)
-- Or re-run ETL and re-upload

-- Quick fix for views
DROP VIEW IF EXISTS v_problematic_view CASCADE;
-- Fix and re-create
```

---

## Timeline

| Step | Duration | Notes |
|------|----------|-------|
| Wipe Supabase | 1 min | Run SQL script |
| Upload tables | 5-10 min | Depends on connection |
| Create views | 1 min | Run SQL script |
| Test | 5 min | Verify queries work |
| Dashboard update | 10 min | Update connection config |
| **Total** | **~20-30 min** | - |
