# BenchSight Quick Start Guide

**Get up and running in 5 minutes**

Last Updated: 2026-01-13

---

## Prerequisites Check

```bash
# Verify Python version
python --version  # Should be 3.11+

# Check if dependencies installed
python -c "import pandas; print('Ready!')"
```

If not set up, see [SETUP.md](SETUP.md) first.

---

## Quick Start (5 Steps)

### Step 1: Verify Data Files

```bash
# Check master data exists
ls data/raw/BLB_Tables.xlsx

# Check game data exists
ls data/raw/games/
```

### Step 2: Run ETL

```bash
# Generate all 139 tables
python run_etl.py
```

**Expected output:**
```
✓ Extracted data from 4 games
✓ Built 55 dimension tables
✓ Built 71 fact tables
✓ Built 4 QA tables
✓ Generated 139 CSV files
```

### Step 3: Validate Output

```bash
# Quick validation
python validate.py --quick

# Full validation
python validate.py
```

**Should show:**
- ✓ 139 tables generated
- ✓ Goal counts verified (17 goals)
- ✓ No data integrity errors

### Step 4: View Results

```bash
# Check output directory
ls data/output/*.csv | wc -l  # Should show 139

# View a sample table
head -5 data/output/dim_player.csv
```

### Step 5: (Optional) Upload to Supabase

```bash
# Generate schema
python upload.py --schema

# Then in Supabase SQL Editor:
# 1. Run sql/reset_supabase.sql
# 2. Run sql/views/99_DEPLOY_ALL_VIEWS.sql

# Upload data
python upload.py
```

---

## Common Commands

### ETL Commands

```bash
# Full ETL (all games)
python run_etl.py

# Clean slate (delete output, then run)
python run_etl.py --wipe

# Specific games only
python run_etl.py --games 18969 18977

# Exclude games
python run_etl.py --exclude-games 18969

# Check status
python run_etl.py --status
```

### Validation Commands

```bash
# Quick check (counts only)
python validate.py --quick

# Full validation
python validate.py

# Check specific table
python validate.py --table dim_player
```

### Upload Commands

```bash
# Upload all tables
python upload.py

# Upload specific tables
python upload.py --tables dim_player fact_events

# Upload by pattern
python upload.py --pattern "fact_player*"

# Dry run (preview only)
python upload.py --dry-run

# List available tables
python upload.py --list
```

---

## What Gets Generated

### Output Structure

```
data/output/
├── dim_*.csv          # 55 dimension tables
├── fact_*.csv         # 71 fact tables
├── qa_*.csv           # 4 QA tables
└── lookup_*.csv       # Lookup tables
```

### Key Tables

| Table | Description | Rows (approx) |
|-------|-------------|---------------|
| `dim_player` | All players | ~50 |
| `dim_team` | All teams | ~10 |
| `dim_schedule` | All games | 4 |
| `fact_events` | All game events | ~2000 |
| `fact_player_game_stats` | Player stats per game | ~200 |
| `fact_team_game_stats` | Team stats per game | ~8 |

---

## Troubleshooting

### "No games found"

**Check:**
```bash
# List available games
python run_etl.py --list-games

# Verify game directories exist
ls data/raw/games/
```

### "Table count mismatch"

**Fix:**
```bash
# Clean and rebuild
python run_etl.py --wipe
python run_etl.py
```

### "Validation errors"

**Check:**
```bash
# See detailed errors
python validate.py

# Check specific validation
python validate.py --goals  # Goal counting
python validate.py --fk     # Foreign keys
```

---

## Next Steps

1. **Explore Data**: Open CSV files in Excel/Google Sheets
2. **Read Documentation**: 
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [ETL.md](ETL.md) - Pipeline details
   - [DATA_DICTIONARY.md](DATA_DICTIONARY.md) - Table definitions
   - [README.md](README.md) - Documentation index
3. **Set Up Dashboard**: See [NEXTJS_DASHBOARD_GUIDE.md](NEXTJS_DASHBOARD_GUIDE.md)
4. **Check TODO**: See [TODO.md](TODO.md) for current priorities
5. **Set Up Development**: See [SETUP.md](SETUP.md) for complete setup

---

## Quick Reference

| Task | Command |
|------|---------|
| Run ETL | `python run_etl.py` |
| Validate | `python validate.py` |
| Upload | `python upload.py` |
| List games | `python run_etl.py --list-games` |
| Clean rebuild | `python run_etl.py --wipe` |

---

*Last updated: 2026-01-13*
