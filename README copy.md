# Hockey Analytics Data Pipeline

## Overview

A comprehensive data engineering project for hockey analytics, featuring:
- ETL pipeline for game tracking data
- Star/snowflake schema design
- Advanced statistics (Corsi, Fenwick, xG)
- Micro-statistics from play details
- Skill-adjusted metrics
- Power BI ready CSV exports

## Quick Start

```bash
# 1. Install dependencies
pip install pandas numpy openpyxl psycopg2-binary

# 2. Configure settings
cp config/config.ini config/config_local.ini
# Edit config_local.ini with your settings

# 3. Place data files
# - BLB_Tables.xlsx → data/raw/
# - Game tracking files → data/raw/games/{game_id}/

# 4. Run the pipeline
python main.py
```

## Project Structure

```
hockey_analytics_project/
├── main.py                    # Main orchestrator (run this)
├── config/
│   └── config.ini             # Configuration file
├── src/
│   ├── ingestion/             # Data loading modules
│   ├── transformation/        # Data transformation
│   ├── loading/               # Export modules
│   └── utils/                 # Utilities
├── sql/
│   └── ddl/                   # Table creation scripts
├── data/
│   ├── raw/                   # Input files
│   ├── processed/             # Intermediate files
│   └── output/                # CSV output (for Power BI)
├── docs/                      # Documentation
├── tests/                     # Unit tests
└── logs/                      # Log files
```

## Data Flow

1. **Ingest**: Load BLB_Tables.xlsx (reference data) and game tracking files
2. **Transform**: Create star schema tables with advanced stats
3. **Load**: Export to CSV for Power BI / PostgreSQL

## Schema Overview

### Dimension Tables
- `dim_player`: Player master data
- `dim_team`: Team information
- `dim_schedule`: Game schedule
- `dim_rink_zones`: Rink coordinates
- `dim_game_players`: Per-game player info

### Fact Tables
- `fact_events`: Game events with ML features
- `fact_event_players`: Player-event bridge
- `fact_shifts`: Shift data with skill aggregates
- `fact_shift_players`: Player-shift bridge
- `fact_box_score`: Comprehensive player stats
- `fact_linked_events`: Shot→Save chains
- `fact_sequences`: Possession chains
- `fact_plays`: Play-level chains

## Box Score Stats (125+ columns)

### Standard Stats
- Goals, Assists, Points, +/-
- Shots, SOG, Shooting %
- Passes, Completion %
- Faceoffs, Win %

### Advanced Stats
- Corsi For/Against
- Fenwick For/Against
- Zone entries/exits
- Possession time

### Micro-Stats
- Stick checks, Poke checks
- Dekes, Drives, Screens
- Breakouts, Puck recoveries
- Zone entry denials

### Skill Context
- Player skill rating
- Opponent skill faced
- Skill differential

## Configuration

Edit `config/config_local.ini`:

```ini
[database]
host = localhost
password = your_password

[paths]
blb_tables_file = data/raw/BLB_Tables.xlsx
```

## For Power BI

CSV files are exported to `data/output/` with UTF-8 BOM encoding.

Suggested relationships:
- dim_game_players → fact_box_score (1:1)
- dim_game_players → fact_event_players (1:N)
- dim_game_players → fact_shift_players (1:N)
- fact_shifts → fact_shift_players (1:N)
- fact_events → fact_event_players (1:N)

## Future Enhancements

- XY coordinate tracking
- Video link integration
- Expected goals model
- Computer vision analysis
- Real-time scoring prediction
