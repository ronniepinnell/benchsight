# BenchSight Quick Start Guide

**Get up and running in 5 minutes**

Last Updated: 2026-01-15

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
# Using unified CLI (recommended)
./benchsight.sh etl run

# Or using Python directly
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
# Using unified CLI (recommended)
./benchsight.sh etl validate

# Or using Python directly
python validate.py --quick  # Quick validation
python validate.py          # Full validation
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
# Using unified CLI (recommended)
./benchsight.sh db schema   # Generate schema
./benchsight.sh db upload  # Upload data

# Or using Python directly
python upload.py --schema   # Generate schema
python upload.py           # Upload data

# Then in Supabase SQL Editor:
# 1. Run sql/reset_supabase.sql
# 2. Run sql/views/99_DEPLOY_ALL_VIEWS.sql
```

---

## Common Commands

### Using Unified CLI (Recommended)

```bash
# ETL
./benchsight.sh etl run                    # Full ETL
./benchsight.sh etl run --wipe             # Clean rebuild
./benchsight.sh etl run --games 18969 18977 # Specific games
./benchsight.sh etl validate               # Validate output
./benchsight.sh etl status                 # Check status

# Dashboard
./benchsight.sh dashboard dev              # Start dev server
./benchsight.sh dashboard build            # Build for production

# Database
./benchsight.sh db upload                  # Upload to Supabase
./benchsight.sh db schema                  # Generate schema

# Environment
./benchsight.sh env switch dev             # Switch to dev
./benchsight.sh env status                 # Check environment

# Project
./benchsight.sh status                     # Project status
./benchsight.sh docs                       # Open documentation
./benchsight.sh help                       # Show help
```

**Complete Command Reference:** See [COMMANDS.md](COMMANDS.md)

### Direct Python Commands (Alternative)

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
   - [MASTER_INDEX.md](MASTER_INDEX.md) - Documentation index
   - [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current project status
   - [COMMANDS.md](COMMANDS.md) - Complete command reference
   - [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) - Development workflows
   - [PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md) - Pre-flight checklists
3. **Set Up Dashboard**: See [DEV_ENV_VERCEL.md](DEV_ENV_VERCEL.md) for Vercel setup
4. **Set Up Supabase**: See [DEV_ENV_SUPABASE.md](DEV_ENV_SUPABASE.md) for Supabase setup
5. **Set Up Development**: See [DEV_ENV_COMPLETE.md](DEV_ENV_COMPLETE.md) for complete setup
6. **Check Next Steps**: See [MASTER_NEXT_STEPS.md](MASTER_NEXT_STEPS.md) for current priorities

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

## Using the API

### Start the API Server

```bash
# Navigate to API directory
cd api

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Trigger ETL via API

```bash
# Trigger ETL job
curl -X POST http://localhost:8000/api/etl/trigger \
  -H "Content-Type: application/json" \
  -d '{"games": [18969, 18977]}'

# Check job status
curl http://localhost:8000/api/etl/status/{job_id}

# View job history
curl http://localhost:8000/api/etl/history
```

### API Documentation

- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

See [API_REFERENCE.md](API_REFERENCE.md) for complete API documentation.

---

## Dashboard Quick Start

### Local Development

```bash
# Navigate to dashboard directory
cd ui/dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Environment Setup

See [DEV_ENV_VERCEL.md](DEV_ENV_VERCEL.md) for Vercel setup and [DEV_ENV_SUPABASE.md](DEV_ENV_SUPABASE.md) for Supabase setup.

---

*Last updated: 2026-01-15*
