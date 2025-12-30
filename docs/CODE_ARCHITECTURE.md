# BenchSight Code Architecture

## Directory Structure

```
benchsight/
├── src/                    # Core ETL code
│   ├── main.py            # CLI entry point
│   ├── pipeline/          # ETL orchestration
│   │   └── orchestrator.py
│   ├── ingestion/         # Data loading
│   │   ├── blb_loader.py  # BLB_Tables.xlsx loader
│   │   ├── game_loader.py # Game tracking loader
│   │   └── xy_loader.py   # XY coordinate loader
│   ├── transformation/    # Data transforms
│   ├── database/          # DB connections
│   ├── models/            # Data models
│   ├── loading/           # Data loading utilities
│   ├── analytics/         # Stats calculations
│   └── utils/             # Helpers
│       ├── logger.py
│       └── config_loader.py
│
├── scripts/               # Standalone scripts
│   ├── flexible_loader.py # Supabase deployment
│   ├── validate_*.py      # Validation scripts
│   ├── qa_*.py            # QA scripts
│   └── verify_delivery.py # Pre-package verification
│
├── sql/                   # SQL files
│   ├── 01_CREATE_ALL_TABLES.sql
│   ├── 02_TYPE_FIXES.sql
│   └── 03_TRUNCATE_DATA.sql
│
├── data/
│   ├── raw/games/         # Source tracking files
│   ├── output/            # Generated CSVs (98 tables)
│   └── BLB_Tables.xlsx    # Master reference data
│
├── config/
│   ├── config_local.ini   # Your credentials
│   └── *.example          # Example configs
│
├── tests/                 # Test suite
├── docs/                  # Documentation
├── tracker/               # Tracker HTML prototypes
├── dashboard/             # Dashboard HTML prototypes
└── developer_handoffs/    # Role-specific guides
```

## Data Flow

```
1. RAW DATA
   data/raw/games/{game_id}/BLB_*.xlsx
   data/BLB_Tables.xlsx
   
2. ETL PIPELINE (src/main.py)
   → Stage Layer (raw loading)
   → Intermediate Layer (transforms)
   → Datamart Layer (star schema)
   
3. OUTPUT
   data/output/*.csv (96 files)
   
4. DEPLOYMENT (scripts/flexible_loader.py)
   → Supabase tables
```

## Key Classes

### PipelineOrchestrator (src/pipeline/orchestrator.py)
Main ETL coordinator. Handles:
- Game processing order
- Layer dependencies
- Error handling

### BLBLoader (src/ingestion/blb_loader.py)
Loads BLB_Tables.xlsx reference data:
- Player registry
- Team definitions
- Schedule

### GameLoader (src/ingestion/game_loader.py)
Loads game tracking files:
- Events (shots, passes, etc.)
- Shifts (player ice time)

### FlexibleLoader (scripts/flexible_loader.py)
Deploys data to Supabase:
- Replace/Append/Upsert modes
- Category filtering
- Dry run support

## Configuration

### config/config_local.ini
```ini
[supabase]
url = https://YOUR_PROJECT.supabase.co
service_key = YOUR_SERVICE_ROLE_KEY

[loader]
batch_size = 500
```

## Logging

Uses structured logging via `src/utils/logger.py`:
```python
from src.utils.logger import get_logger
logger = get_logger(__name__)
logger.info("Processing game 18969")
```

## Error Handling

- ETL errors logged to console
- Failed games tracked in status
- Validation errors stored in reports

## Extending the Code

### Adding a New Stat
1. Add column to `fact_player_game_stats`
2. Add calculation to stats module
3. Add to `STATS_REFERENCE_COMPLETE.md`
4. Add test to `test_stats_calculations.py`
5. Run `sql/01_CREATE_ALL_TABLES.sql` to add column

### Adding a New Table
1. Create CSV in `data/output/`
2. Add CREATE TABLE to `sql/01_CREATE_ALL_TABLES.sql`
3. Add to `TABLE_CATEGORIES` in `flexible_loader.py`
4. Add to `DATA_DICTIONARY.md`
