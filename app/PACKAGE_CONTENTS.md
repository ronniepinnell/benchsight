# BenchSight Complete Package Contents

## Source Code
- `src/etl/extract.py` - Data extraction from Excel
- `src/etl/transform.py` - Stage/Intermediate/Mart transformations
- `src/etl/orchestrator.py` - ETL pipeline runner

## SQL
- `sql/create_schema.sql` - Complete PostgreSQL schema (56+ tables)

## Portal
- `portal/index.html` - Full interactive dashboard with:
  - Game selector (all 9 games)
  - Score display with team logos
  - Period filters (P1/P2/P3)
  - Scrollable event/shift logs
  - Admin ETL runner
  - Documentation viewer
  - Privacy mode toggle

## Data
- `data/raw/master/BenchSight_Tables.xlsx` - Master dimension tables
- `data/raw/games/` - 9 game folders with tracking data
- `data/processed/stage/` - Stage layer CSVs (generated)
- `data/processed/mart/` - Mart layer CSVs (generated)

## Documentation
- `docs/BENCHSIGHT_MASTER_STATUS.md` - Complete project status & triage
- `docs/llm/LLM_CONSULTATION_GUIDE.md` - Guide for GPT/Gemini
- `docs/catalogs/` - Stats and table catalogs

## Configuration
- `config/settings.py` - Project configuration
- `README.md` - Quick start guide

## Total Files: 100+
## Total Code Lines: 3,000+
## Total Documentation: 1,500+ lines
