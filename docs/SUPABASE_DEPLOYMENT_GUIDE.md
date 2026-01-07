# Supabase Deployment Guide

Complete guide for deploying BenchSight data to Supabase.

## Prerequisites

1. **Supabase Account**: Create project at supabase.com
2. **Python 3.8+**: With pandas installed
3. **Service Key**: From Supabase Dashboard > Settings > API

## Configuration

### Step 1: Create Config File
```bash
cp config/config_local.ini.template config/config_local.ini
```

### Step 2: Add Credentials
Edit `config/config_local.ini`:
```ini
[supabase]
url = https://your-project-id.supabase.co
service_key = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Finding Your Credentials:**
1. Go to Supabase Dashboard
2. Select your project
3. Settings > API
4. Copy "Project URL" and "service_role" key (not anon key)

### Alternative: Environment Variables
```bash
export SUPABASE_URL=https://your-project-id.supabase.co
export SUPABASE_SERVICE_KEY=eyJ...
```

## Database Setup

### Create Tables (First Time)
1. Open Supabase Dashboard > SQL Editor
2. Copy contents of `sql/create_all_tables.sql`
3. Run the query
4. Verify 111 tables created

### Reset Database (Start Over)
1. Run `sql/drop_all_tables.sql` in SQL Editor
2. Run `sql/create_all_tables.sql` in SQL Editor

### Clear Data Only (Keep Schema)
1. Run `sql/truncate_all_data.sql` in SQL Editor

## Deployment Commands

### Test Connection
```bash
python scripts/deploy_supabase.py --test
```
Expected output:
```
URL: https://xxx.supabase.co
✅ Connected!
   dim_player: 0 rows
   dim_team: 0 rows
   fact_events: 0 rows
```

### Full Deployment
```bash
# Default mode (upsert)
python scripts/deploy_supabase.py --all

# Fastest mode (after truncate)
python scripts/deploy_supabase.py --all --mode insert

# Replace mode (delete + insert)
python scripts/deploy_supabase.py --all --mode replace
```

### Selective Deployment
```bash
# Dimensions only
python scripts/deploy_supabase.py --dims

# Facts only
python scripts/deploy_supabase.py --facts

# Specific tables
python scripts/deploy_supabase.py --tables dim_player,dim_team,fact_events

# Exclude tables
python scripts/deploy_supabase.py --all --exclude fact_player_xy_long,fact_puck_xy_long
```

### Options
```bash
--dry-run       # Preview without uploading
--skip-errors   # Continue past errors
--list          # Show available tables
```

## Deployment Modes

| Mode | Best For | How It Works |
|------|----------|--------------|
| `insert` | Empty database | Plain INSERT, fails on duplicates |
| `upsert` | Incremental updates | INSERT or UPDATE on conflict |
| `replace` | Full refresh | DELETE all rows, then INSERT |

### Recommended Workflow

**Initial Load:**
```bash
# 1. Create schema (SQL Editor)
# 2. Deploy with insert mode
python scripts/deploy_supabase.py --all --mode insert
```

**Data Updates:**
```bash
python scripts/deploy_supabase.py --all --mode upsert
```

**Full Reset:**
```bash
# 1. Truncate data (SQL Editor)
# 2. Deploy with insert mode
python scripts/deploy_supabase.py --all --mode insert
```

## Troubleshooting

### Connection Failed
```
❌ Cannot connect to https://xxx.supabase.co
```
- Check URL in config file (no trailing slash)
- Verify service key is correct (not anon key)
- Check Supabase project is active

### Table Not Found
```
❌ Table not in Supabase
```
- Run `sql/create_all_tables.sql` first
- Check table name matches exactly

### Duplicate Key Error
```
Row 0: (409) duplicate key value
```
- Table has existing data
- Use `--mode upsert` or `--mode replace`
- Or truncate table first

### Data Type Error (22P02)
```
Row X: (400) {"code":"22P02"...
```
- Data type mismatch between CSV and schema
- Check column types in `sql/create_all_tables.sql`
- Regenerate schema with `python scripts/supabase_schema.py`

### Timeout Error
```
Row X: timed out
```
- Large table taking too long
- Increase batch size or timeout in script
- Try deploying in smaller chunks

## Verification

### Check Row Counts
```bash
python scripts/deploy_supabase.py --test
```

### Query in SQL Editor
```sql
SELECT 
    table_name,
    (xpath('/row/cnt/text()', xml_count))[1]::text::int as row_count
FROM (
    SELECT table_name, 
           query_to_xml(format('SELECT COUNT(*) as cnt FROM %I', table_name), false, true, '') as xml_count
    FROM information_schema.tables
    WHERE table_schema = 'public' 
      AND table_name LIKE 'dim_%'
    ORDER BY table_name
) t;
```

### List All Tables
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
```

## File Reference

| File | Purpose |
|------|---------|
| `scripts/deploy_supabase.py` | Main deployment script |
| `scripts/supabase_schema.py` | Schema generation |
| `sql/create_all_tables.sql` | Create all 111 tables |
| `sql/drop_all_tables.sql` | Drop all tables |
| `sql/truncate_all_data.sql` | Clear all data |
| `config/config_local.ini` | Credentials (create from template) |
| `data/output/*.csv` | 111 CSV files to deploy |

## Technical Details

### API Used
- PostgREST REST API (Supabase's auto-generated API)
- Batch uploads of 500 rows per request
- 120 second timeout per batch

### Upsert Implementation
```
POST /rest/v1/{table}?on_conflict={primary_key}
Header: Prefer: resolution=merge-duplicates
```

### Delete Implementation
```
DELETE /rest/v1/{table}?{primary_key}=not.is.null
```

### Data Type Conversion
- Float `1.0` → Integer `1` (for INTEGER columns)
- NaN → `null`
- All values JSON-serializable
