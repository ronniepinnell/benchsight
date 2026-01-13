# BenchSight Supabase Setup

**Database Configuration and Upload Guide**

Updated: 2026-01-10

---

## Quick Start

```bash
# 1. Generate schema SQL
python upload.py --schema

# 2. In Supabase SQL Editor: paste and run sql/reset_supabase.sql

# 3. Upload data
python upload.py
```

---

## Prerequisites

1. **Supabase Account** - Free at [supabase.com](https://supabase.com)
2. **Project Created** - Note your project URL and service key
3. **ETL Complete** - Run `python run_etl.py` first

---

## Configuration

### Create config/config_local.ini

```ini
[supabase]
url = https://your-project-id.supabase.co
service_key = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

[etl]
batch_size = 500
```

### Find Your Credentials

1. Go to Supabase Dashboard
2. Select your project
3. Go to **Settings** → **API**
4. Copy:
   - **Project URL** → `url`
   - **service_role key** (not anon key) → `service_key`

⚠️ **Never commit config_local.ini to git** - it contains secrets!

---

## Initial Setup

### Step 1: Generate Schema

```bash
python upload.py --schema
```

This creates `sql/reset_supabase.sql` with:
- DROP TABLE statements (131 tables)
- CREATE TABLE statements with proper types
- Type inference from actual data

### Step 2: Create Tables in Supabase

1. Go to Supabase Dashboard
2. Open **SQL Editor**
3. Click **New Query**
4. Paste contents of `sql/reset_supabase.sql`
5. Click **Run**

You should see "Success. No rows returned" - that's correct.

### Step 3: Upload Data

```bash
python upload.py
```

Expected output:
```
BENCHSIGHT SUPABASE UPLOAD
============================================================
Tables to upload: 131

  ✓ dim_danger_zone: 6 rows
  ✓ dim_event_detail: 45 rows
  ...
  ✓ fact_player_game_stats: 200 rows

============================================================
SUMMARY
============================================================
Success: 131/131
Failed:  0
Rows:    50,000

✓ Upload complete!
```

---

## Upload Options

```bash
# Upload all tables
python upload.py

# Upload single table
python upload.py --table dim_player

# Upload dimensions only
python upload.py --dims

# Upload facts only
python upload.py --facts

# Regenerate schema only
python upload.py --schema

# Verbose output
python upload.py --verbose
```

---

## Verifying Upload

### In Supabase Dashboard

1. Go to **Table Editor**
2. Check table count (should be 131)
3. Click a table to view data

### Via SQL

```sql
-- Count all tables
SELECT COUNT(*) 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check specific table
SELECT COUNT(*) FROM fact_player_game_stats;

-- Verify goals
SELECT COUNT(*) 
FROM fact_events 
WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored';
```

---

## Table Categories

| Prefix | Count | Description |
|--------|-------|-------------|
| `dim_` | 55 | Dimension tables |
| `fact_` | 71 | Fact tables |
| `qa_` | 4 | Quality assurance |

---

## Data Types

The upload script infers PostgreSQL types from data:

| Python/Pandas | PostgreSQL |
|---------------|------------|
| int64 | BIGINT |
| float64 | DOUBLE PRECISION |
| bool | BOOLEAN |
| datetime | TIMESTAMPTZ |
| object/string | TEXT |

---

## Troubleshooting

### "relation does not exist"

Tables not created. Run the schema SQL first:
```bash
python upload.py --schema
# Then run SQL in Supabase Editor
```

### "permission denied"

Using wrong key. Make sure you're using `service_role` key, not `anon` key.

### "duplicate key value"

Data already exists. Options:
1. Run schema SQL again (drops all tables)
2. Or truncate specific table in SQL Editor

### "connection refused"

Check your URL in config. It should be:
```
https://your-project-id.supabase.co
```
Not the pooler URL or any other variant.

### Upload is slow

Normal for large tables. Upload runs in batches of 500 rows.
For 50,000 rows = 100 batches = ~2 minutes.

---

## Row Level Security (RLS)

By default, Supabase enables RLS which blocks all queries. For development, disable it:

### Disable RLS (Recommended for Development)

Run this in SQL Editor after uploading data:

```sql
-- Disable RLS on all tables
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE 'ALTER TABLE public.' || quote_ident(r.tablename) || ' DISABLE ROW LEVEL SECURITY';
    END LOOP;
END $$;
```

Or run the included script:
```bash
# In Supabase SQL Editor, paste contents of:
sql/disable_rls.sql
```

### For Production

Add proper policies per table. See `sql/fix_rls_policies.sql` for examples.

---

## Tracker Setup

The BenchSight Tracker (`ui/tracker/index.html`) connects to Supabase to:
1. Load game schedule (dropdown)
2. Load rosters for selected game
3. Load reference data (event types, play details)

### Required Tables for Tracker

| Table | Purpose |
|-------|---------|
| `dim_schedule` | Game list for dropdown |
| `fact_gameroster` | Player rosters per game |
| `dim_team` | Team colors/logos |
| `dim_play_detail` | Play detail dropdown |
| `dim_play_detail_2` | Play detail 2 dropdown |
| `dim_event_detail` | Event detail dropdown |
| `dim_event_detail_2` | Event detail 2 dropdown |
| `dim_player_role` | Player role codes |

### Tracker Configuration

1. Open tracker: `ui/tracker/index.html`
2. Click **⚙️ Settings**
3. Enter:
   - **Supabase URL**: `https://your-project.supabase.co`
   - **Supabase Anon Key**: Your `anon` public key (NOT service_role)
4. Click **Test Connection**
5. Click **Save**

### Troubleshooting Tracker

**"OFFLINE" status / Connection fails:**
- Check URL format: `https://xxx.supabase.co` (no trailing slash)
- Use `anon` key (public), not `service_role`
- Ensure RLS is disabled or policies allow SELECT

**Games dropdown empty:**
- Check `dim_schedule` has data
- Check RLS disabled: `SELECT COUNT(*) FROM dim_schedule;`

**Roster doesn't load:**
- Check `fact_gameroster` has data for that game_id
- Check column names match: `player_id`, `player_full_name`, `team_venue`

**Console errors (F12 to view):**
- Look for specific column not found errors
- Verify schema matches current CSVs

---

## Querying from Dashboard

### JavaScript (Supabase Client)

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://your-project.supabase.co',
  'your-anon-key'
)

// Get player stats
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('*')
  .eq('player_id', 42)

// Get top scorers
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('player_id, goals')
  .order('goals', { ascending: false })
  .limit(10)
```

### SQL (Direct)

```sql
-- Top scorers
SELECT 
  p.player_name,
  SUM(s.goals) as total_goals
FROM fact_player_game_stats s
JOIN dim_player p ON s.player_id = p.player_id
GROUP BY p.player_name
ORDER BY total_goals DESC
LIMIT 10;
```

---

## Resetting Data

To completely reset:

```bash
# Regenerate schema
python upload.py --schema

# Run SQL in Supabase (drops all tables, recreates empty)
# Then upload
python upload.py
```

To reset single table:

```sql
-- In Supabase SQL Editor
TRUNCATE TABLE fact_player_game_stats;
```

Then:
```bash
python upload.py --table fact_player_game_stats
```

---

## Backup

### Export from Supabase

Dashboard → Settings → Database → Backups

### Export via pg_dump

```bash
pg_dump -h db.your-project.supabase.co -U postgres -d postgres > backup.sql
```

### Local Backup

Your CSVs in `data/output/` are already a backup!

---

*Last updated: 2026-01-10*
