# BenchSight ETL Architecture

## Overview

The ETL pipeline transforms raw hockey data into a dimensional data warehouse suitable for analytics and Supabase deployment.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  RAW DATA       │────▶│  STAGE          │────▶│  INTERMEDIATE   │────▶│  DATAMART       │
│                 │     │                 │     │                 │     │                 │
│ • BLB_Tables.xlsx│    │ • stg_player    │     │ • int_player    │     │ • dim_player    │
│ • Game tracking │     │ • stg_team      │     │ • int_team      │     │ • dim_team      │
│   files         │     │ • stg_events    │     │ • int_events    │     │ • fact_events   │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
                                                                               │
                                                                               ▼
                                                                        ┌─────────────────┐
                                                                        │  CSV EXPORT     │
                                                                        │                 │
                                                                        │ data/output/    │
                                                                        │ (111 tables)    │
                                                                        └─────────────────┘
```

## Pipeline Stages

### Stage 1: Load BLB Tables
**Location:** `src/pipeline/stage/load_blb_tables.py`

Reads `BLB_Tables.xlsx` (reference data) and loads into SQLite staging tables:
- Player master data
- Team definitions
- Schedule/game metadata
- Season information

### Stage 2: Load Game Tracking
**Location:** `src/pipeline/stage/load_game_tracking.py`

Reads individual game files and loads tracking data:
- Event-by-event game data
- Shift data (who was on ice)
- Player assignments

### Stage 3: Transform BLB
**Location:** `src/pipeline/intermediate/transform_blb.py`

Normalizes BLB data:
- Generates surrogate keys
- Standardizes naming conventions
- Creates dimension table structures

### Stage 4: Transform Games
**Location:** `src/pipeline/intermediate/transform_game.py`

Transforms raw game data:
- Links events to players
- Calculates derived fields (duration, zones, etc.)
- Joins with dimension tables

### Stage 5: Build Datamart
**Location:** `src/pipeline/datamart/`

Builds final analytical tables:
- `publish_dimensions.py` - Final dimension tables
- `build_events.py` - Event fact tables
- `build_box_score.py` - Game statistics
- `build_enhanced_data.py` - Advanced analytics

### Stage 6: Export
**Location:** `src/pipeline/datamart/export_to_csv.py`

Exports all tables to CSV files in `data/output/`.

## Entry Points

### Interactive CLI
```bash
python src/main.py
```
Provides menu-driven interface for all operations.

### Command Line
```bash
python src/main.py --game 18969           # Process single game
python src/main.py --games 18969,18970    # Multiple games
python src/main.py --process-all          # All unprocessed games
python src/main.py --export               # Export to CSV
python src/main.py --status               # Show status
```

### Programmatic
```python
from src.pipeline.orchestrator import PipelineOrchestrator

orchestrator = PipelineOrchestrator()
results = orchestrator.run_full_pipeline(game_ids=[18969, 18970])
```

## Database

SQLite database at `data/hockey_analytics.db` stores all intermediate data.

Tables are organized by layer prefix:
- `stg_*` - Staging tables (raw load)
- `int_*` - Intermediate tables (transformed)
- `dm_*` or `dim_*/fact_*` - Datamart tables (final)

## Key Files

| File | Purpose |
|------|---------|
| `src/pipeline/orchestrator.py` | Main pipeline coordinator |
| `src/database/connection.py` | SQLite connection management |
| `src/database/table_operations.py` | Table read/write operations |
| `src/utils/logger.py` | Logging configuration |
| `src/etl/builders/` | Table-specific transformation logic |

## Data Flow Example: Player Stats

1. **BLB_Tables.xlsx** → Player sheet contains master player list
2. **load_blb_tables.py** → Loads to `stg_player`
3. **transform_blb.py** → Creates `int_player` with `player_id` keys
4. **Game tracking files** → Event data loaded to `stg_events`
5. **transform_game.py** → Links events to players
6. **build_box_score.py** → Aggregates stats per player per game
7. **export_to_csv.py** → Exports `fact_player_game_stats.csv`

## Configuration

Database and paths configured in:
- `src/database/connection.py` - DB path
- `src/pipeline/orchestrator.py` - Default directories

## Error Handling

- Pipeline logs to console with timestamps
- Errors captured in result dictionary
- Individual game failures don't stop batch processing
- Export verifies row counts match source

## Adding New Tables

1. Add transformation logic in appropriate `src/pipeline/` module
2. Register table in `src/pipeline/datamart/export_to_csv.py`
3. Run `python scripts/supabase_schema.py` to regenerate SQL
4. Add tests in `tests/test_integration_etl.py`
