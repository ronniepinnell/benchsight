# BENCHSIGHT CHANGELOG

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
