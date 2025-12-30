# Getting Started with BenchSight

## For All Roles

### 1. Understand the Project
- Read `README.md` for project overview
- Read `docs/HONEST_ASSESSMENT.md` for current status
- Browse `docs/html_docs/` for formatted documentation

### 2. Explore the Data
- `data/output/` contains 96 CSV files
- `docs/DATA_DICTIONARY.md` explains every table/column
- `docs/STATS_REFERENCE_COMPLETE.md` explains all 317 stats

### 3. View Prototypes
- `tracker/tracker_v19.html` - Event tracking interface
- `dashboard/dashboard.html` - Analytics dashboard

---

## For Developers

### Setup
```bash
# Clone/extract project
cd benchsight

# Install dependencies
pip install pandas supabase openpyxl

# Configure Supabase
cp config/config_local.ini.example config/config_local.ini
# Edit with your credentials
```

### Run ETL
```bash
./run_etl.sh --status           # Check status
./run_etl.sh --game 18969       # Process game
./run_etl.sh --export           # Export CSVs
```

### Deploy to Supabase
```bash
./run_deploy.sh                 # Deploy all
./run_deploy.sh --dry-run       # Preview
```

### Run Tests
```bash
python -m pytest tests/ -v
```

---

## For Dashboard Developers

1. Read `docs/handoffs/DASHBOARD_DEV_HANDOFF.md`
2. Study `dashboard/*.html` prototypes
3. Key tables:
   - `fact_player_game_stats` - All player stats
   - `fact_team_game_stats` - Team stats
   - `dim_player`, `dim_team` - Lookups

---

## For Tracker Developers

1. Read `docs/handoffs/TRACKER_DEV_HANDOFF.md`
2. Study `tracker/tracker_v19.html`
3. Key tables:
   - `fact_events` - All tracked events
   - `dim_event_type`, `dim_event_detail` - Event categories

---

## For Portal Developers

1. Read `docs/handoffs/PORTAL_DEV_HANDOFF.md`
2. Key tables:
   - `dim_player`, `dim_team` - Master data
   - `fact_registration` - Player registrations
   - `dim_schedule` - Game schedule

---

## For Supabase/Backend Developers

1. Read `docs/DEPLOYMENT_GUIDE.md`
2. Key files:
   - `sql/01_CREATE_ALL_TABLES.sql` - Create schema
   - `sql/02_TYPE_FIXES.sql` - Fix types
   - `scripts/flexible_loader.py` - Load data

---

## For Project Managers

1. Read `docs/handoffs/PROJECT_MANAGER_HANDOFF.md`
2. Read `docs/HONEST_ASSESSMENT.md`
3. Review `docs/FUTURE_IDEAS_BLUEPRINT.md`

---

## Quick Reference

| Task | Command/File |
|------|--------------|
| View all tables | `docs/DATA_DICTIONARY.md` |
| View all stats | `docs/STATS_REFERENCE_COMPLETE.md` |
| Deploy data | `./run_deploy.sh` |
| Run ETL | `./run_etl.sh` |
| Run tests | `pytest tests/ -v` |
| View HTML docs | `docs/html_docs/INDEX.html` |
