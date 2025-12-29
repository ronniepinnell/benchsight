# 🚀 BenchSight Supabase Deployment Guide

## Complete Instructions for Database Deployment

---

## Prerequisites

1. **Python packages:**
   ```bash
   pip install supabase pandas
   ```

2. **Supabase project:**
   - Go to https://supabase.com
   - Create a new project
   - Note your Project URL and anon key (Settings > API)

3. **Local data:**
   - Run full ETL first: `python etl.py && python src/etl_orchestrator.py --all`
   - Verify CSVs exist in `data/output/`

---

## Step 1: Configure Credentials

### Option A: Environment Variables
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

### Option B: Config File
Edit `config/config_local.ini`:
```ini
[supabase]
url = https://your-project.supabase.co
key = your-anon-key
```

---

## Step 2: Test Connection

```bash
python scripts/supabase_test_connection.py
```

Expected output:
```
✓ supabase package installed
✓ Credentials loaded
✓ Client created successfully
✓ Connection is working!
```

---

## Step 3: Choose Your Deployment Method

### Method A: Full Rebuild (Recommended for First Time)
Drops all tables, recreates schema, uploads all data:
```bash
python scripts/supabase_loader.py --rebuild
```

### Method B: Create Tables Only
Create schema without uploading data:
```bash
python scripts/supabase_loader.py --create-only
```

### Method C: Upload All Data
Upload all tables (tables must exist):
```bash
python scripts/supabase_loader.py --all
```

### Method D: Upload Specific Tables
```bash
# Only dimension tables
python scripts/supabase_loader.py --dims

# Only fact tables
python scripts/supabase_loader.py --facts

# Specific tables
python scripts/supabase_loader.py --tables dim_player,dim_team,fact_player_game_stats
```

### Method E: Upload Specific Games
```bash
# Only data for specific games
python scripts/supabase_loader.py --all --games 18969,18977
```

---

## Step 4: Choose Upload Mode

### Replace Mode (Default)
Truncates existing data before inserting:
```bash
python scripts/supabase_loader.py --all --mode replace
```

### Append Mode
Adds to existing data (useful for incremental updates):
```bash
python scripts/supabase_loader.py --all --mode append
```

---

## Step 5: Verify Deployment

### Automatic Verification
```bash
python scripts/supabase_loader.py --verify
```

### Manual Verification in Supabase
1. Go to Table Editor in Supabase dashboard
2. Check each table has correct row counts:

| Table | Expected Rows |
|-------|---------------|
| dim_player | ~298 |
| dim_team | ~15 |
| dim_schedule | ~562 |
| fact_player_game_stats | ~107 |
| fact_events_player | ~11,635 |
| fact_shifts_player | ~4,626 |

---

## Teardown (Reset Everything)

To completely remove all BenchSight tables:

### Option A: Using Loader
```bash
python scripts/supabase_loader.py --teardown
```

### Option B: Using SQL Editor
1. Go to Supabase SQL Editor
2. Copy contents of `sql/00_drop_all_tables.sql`
3. Execute

---

## Troubleshooting

### "Connection failed"
- Check URL and key are correct
- Check project is active (not paused)
- Check network connectivity

### "Table does not exist"
- Run `--create-only` first
- Or use `--rebuild` for full setup

### "Permission denied"
- Check you're using correct key (anon vs service role)
- Check RLS policies aren't blocking inserts

### "Duplicate key"
- Use `--mode replace` to clear existing data first
- Or use `--teardown` then `--rebuild`

### "Rate limited"
- Wait a few minutes and retry
- Reduce batch size in `supabase_loader.py`

---

## Common Workflows

### First-Time Setup
```bash
# 1. Test connection
python scripts/supabase_test_connection.py

# 2. Full rebuild
python scripts/supabase_loader.py --rebuild

# 3. Verify
python scripts/supabase_loader.py --verify
```

### Adding New Game Data
```bash
# 1. Run ETL for new game
python etl.py

# 2. Upload new data (append mode)
python scripts/supabase_loader.py --facts --mode append
```

### Refreshing All Data
```bash
# Replace all fact tables, keep dims
python scripts/supabase_loader.py --facts --mode replace
```

### Complete Reset
```bash
# Drop everything and start fresh
python scripts/supabase_loader.py --rebuild
```

---

## Log Files

All uploads are logged to `logs/supabase_upload_YYYYMMDD_HHMMSS.log`

Log includes:
- Tables processed
- Row counts
- Errors
- Verification results

---

## Security Notes

1. **Never commit credentials** - Use environment variables or .gitignore config_local.ini
2. **Use anon key for uploads** - Service role key has more permissions than needed
3. **Enable RLS** - Row Level Security for production use
4. **Backup before teardown** - Export data before dropping tables

---

## Quick Reference

```bash
# Test connection
python scripts/supabase_test_connection.py

# Full rebuild (drop + create + upload)
python scripts/supabase_loader.py --rebuild

# Upload all tables
python scripts/supabase_loader.py --all

# Upload dims only
python scripts/supabase_loader.py --dims

# Upload facts only
python scripts/supabase_loader.py --facts

# Upload specific tables
python scripts/supabase_loader.py --tables dim_player,dim_team

# Upload specific games
python scripts/supabase_loader.py --all --games 18969,18977

# Append mode (don't delete existing)
python scripts/supabase_loader.py --all --mode append

# Replace mode (delete then insert)
python scripts/supabase_loader.py --all --mode replace

# Verify upload
python scripts/supabase_loader.py --verify

# Teardown (drop all)
python scripts/supabase_loader.py --teardown

# Create tables only
python scripts/supabase_loader.py --create-only

# Dry run (see what would happen)
python scripts/supabase_loader.py --all --dry-run
```
