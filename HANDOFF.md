# BenchSight Project Handoff

**Date**: January 1, 2026  
**Status**: Production Ready  
**Version**: 17.0 (Complete ETL Implementation)

---

## What Changed

**The ETL now generates ALL 111 tables from source data.**

Previously only ~15 tables were generated; the rest were static CSVs. Now you can run:

```bash
python -m src.etl_complete --all
```

And get all 111 tables regenerated from:
- BLB_Tables.xlsx (master data)
- Game tracking files in data/raw/games/

---

## Quick Start

### Generate All Tables
```bash
python -m src.etl_complete --all
```

### Generate Specific Games
```bash
python -m src.etl_complete --games 18969,18977,18981,18987
```

### Deploy to Supabase
```bash
python scripts/deploy_supabase.py --all
```

---

## Project Structure

```
benchsight/
├── src/
│   ├── etl_complete.py       # NEW: Complete ETL (generates all 111 tables)
│   ├── etl_orchestrator.py   # Legacy: Partial ETL
│   ├── api/server.py         # REST API
│   └── ...
├── data/
│   ├── BLB_Tables.xlsx       # Master data source
│   ├── raw/games/            # Game tracking files
│   └── output/               # Generated CSVs (111 tables)
├── sql/
│   ├── create_all_tables.sql
│   └── drop_all_tables.sql
├── scripts/
│   └── deploy_supabase.py
├── Dockerfile
└── docker-compose.yml
```

---

## ETL Pipeline

### Data Sources

1. **BLB_Tables.xlsx** - Master data
   - dim_player, dim_team, dim_season, dim_league
   - dim_schedule, fact_gameroster, fact_draft, etc.

2. **Game Tracking Files** (data/raw/games/{game_id}/{game_id}_tracking.xlsx)
   - events sheet: All game events with player IDs
   - shifts sheet: Shift data by period
   - game_rosters sheet: Per-game rosters

### What Gets Generated

| Category | Tables | Source |
|----------|--------|--------|
| BLB Dimensions | 9 | BLB_Tables.xlsx |
| Static Dimensions | 39 | Pre-defined lookups |
| Event Facts | 6 | Tracking files |
| Shift Facts | 6 | Tracking files |
| Player Stats | 17 | Calculated from events/shifts |
| Analytics | 20 | Derived from above |
| Support/QA | 14 | Generated |

### Key Tables

- `fact_events` - One row per unique event (5,833 rows for 4 games)
- `fact_events_player` - One row per player per event (11,635 rows)
- `fact_shifts_player` - Player shift records (4,559 rows)
- `fact_player_game_stats` - Per-game player statistics (107 rows)
- `fact_h2h` - Head-to-head matchup stats
- `fact_wowy` - With-or-without-you analysis
- `fact_line_combos` - Line combination tracking

---

## Docker

### Build and Run API
```bash
docker-compose up -d benchsight-api
```

### Run ETL
```bash
docker-compose --profile etl up benchsight-etl
```

### Build Only
```bash
docker build -t benchsight .
docker run -p 5000:5000 -v ./data:/app/data benchsight
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/health | GET | Health check |
| /api/status | GET | Pipeline status |
| /api/games | GET | List games |
| /api/games/{id}/process | POST | Process single game |
| /api/upload | POST | Upload tracking file |
| /api/tables/{name} | GET | Get table data |

---

## Adding New Games

1. Place tracking file in `data/raw/games/{game_id}/{game_id}_tracking.xlsx`
2. Run: `python -m src.etl_complete --games {game_id}`
3. Deploy: `python scripts/deploy_supabase.py --all --mode upsert`

---

## Deployment Checklist

### First Time
1. Create Supabase project
2. Copy `config/config_local.ini.template` → `config/config_local.ini`
3. Add Supabase URL and service key
4. Run `sql/create_all_tables.sql` in SQL Editor
5. Run `python -m src.etl_complete --all`
6. Run `python scripts/deploy_supabase.py --all`

### Updates
```bash
python -m src.etl_complete --all
python scripts/deploy_supabase.py --all --mode upsert
```

---

## Files Reference

### Critical
- `src/etl_complete.py` - Main ETL that generates everything
- `data/BLB_Tables.xlsx` - Master data (DO NOT LOSE)
- `scripts/deploy_supabase.py` - Supabase deployment

### Documentation
- `docs/TABLE_INVENTORY.csv` - All 111 tables listed
- `docs/DATA_DICTIONARY_COMPLETE.md` - Column definitions
- `docs/HONEST_ASSESSMENT.md` - Project status analysis

---

## Known Limitations

1. **Empty XY Tables** - 6 coordinate tables are placeholders for future tracking
2. **Batch Size** - 500 rows per Supabase API call
3. **Video Tables** - Placeholder for video integration

---

## Contact

NORAD Hockey League: https://noradhockey.com
