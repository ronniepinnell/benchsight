# BENCHSIGHT CHANGELOG

## [2.1.0] - 2025-12-28

### CRITICAL: Schema-Driven ETL Overhaul

This release fixes fundamental schema mismatches that were causing upload failures.

### Added
- `config/supabase_schema.json` - **SOURCE OF TRUTH** for Supabase columns (50 tables)
- `PRODUCTION_ETL.py` - New production-ready upload script with schema validation
- `tests/test_schema_compliance.py` - 25 schema validation tests (must pass before upload)
- `UPLOAD_GUIDE.md` - Step-by-step upload instructions
- `html/validation_report.html` - Visual validation status

### Fixed
- **fact_gameroster**: `assists`→`assist`, `game_date`→`date`, `roster_key`→`key`
- **fact_events_tracking**: `event_type`→`Type` (case-sensitive!)
- **fact_playergames**: Reverted to original Excel column names (`ID`, `Date`, `G`, `A`, etc.)
- **dim_schedule**: `game_date`→`date`, fixed OT goals column case
- **fact_registration**: `caf`→`CAF` (case-sensitive)
- **dim_rinkboxcoord**: Removed 5 extra columns not in schema
- **dim_video**: Removed extra `Index` column

### Workflow Change
**BEFORE EVERY UPLOAD:**
```bash
pytest tests/test_schema_compliance.py -v  # Must pass 25/25
python PRODUCTION_ETL.py --dry-run         # Preview upload
python PRODUCTION_ETL.py                   # Upload
```

### Test Results
- 54 total tests passing
- 25 schema compliance tests
- 29 ETL data cleaning tests

---

## [2.0.0] - 2025-12-27

### Added
- Complete Supabase PostgreSQL schema (36 tables)
- Data Dictionary with full column documentation
- Schema diagrams (Mermaid format)
- Supabase upload script (`src/supabase_upload.py`)
- `dim_video` table for video links
- `fact_event_coordinates` table for XY tracking
- `dim_position` now includes X (Extra) for empty net situations
- All 16 lookup dimension tables

### Changed
- Renamed `fact_gameroster_blb` to `fact_gameroster`
- ETL now combines ALL tracking files from game folders
- `fact_events_tracking`: 1,597 → 24,089 rows (fixed)
- `fact_shifts_tracking`: 99 → 770 rows (fixed)

### Removed
- `dim_dates` (use Power BI DAX instead)
- `dim_seconds` (unnecessary)
- `dim_randomnames` (anonymization data)
- `fact_game_rosters` (was Excel formulas, not data)

### Database Schema
- 8 Core Dimension tables
- 16 Lookup Dimension tables
- 12 Fact tables
- Total: 36 tables, ~43,400 rows

## [1.4.0] - 2025-12-27

### Added
- Tracker v18/v19 with embedded game data
- BLB schedule picker (552 games)
- QUICKSTART.md guide

### Fixed
- Player names showing "Unknown" → now shows real names
- Games dropdown empty → now populated from embedded data

## [1.3.0] - 2025-12-27

### Added
- Tracker v17 with 7 bug fixes
- Complete project documentation

## [1.0.0] - 2025-12-20

### Added
- Initial ETL pipeline
- BLB_Tables.xlsx processing
- Basic HTML dashboards
- Tracker v1-v16 development
