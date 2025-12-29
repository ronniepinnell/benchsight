# BenchSight ETL - Quick Start for New Engineers

## What Is This Project?

BenchSight is a hockey analytics platform for the NORAD recreational league. It processes game tracking data (events, shifts, video) and produces a dimensional data warehouse for analytics and Power BI dashboards.

## 5-Minute Overview

```
Raw Tracking Files (Excel) 
    ↓
ETL Pipeline (Python)
    ↓
Dimensional Tables (CSV → Supabase PostgreSQL)
    ↓  
Power BI Dashboards
```

## Key Files to Read First

1. **This file** - You're here
2. `docs/handoff/HONEST_ASSESSMENT.md` - Real status, not sugar-coated
3. `docs/handoff/GAP_ANALYSIS.md` - What works vs what's broken
4. `docs/PROJECT_REQUIREMENTS.md` - Original requirements
5. `docs/HANDOFF.md` - Session summaries

## Quick Commands

```bash
# Run full ETL (4 test games)
python -m src.etl_orchestrator

# Fix dimension mappings + FKs
python src/fix_dim_mappings.py

# Build play chains
python src/complete_chain_builder.py

# Run all validations
python scripts/test_validations.py

# Verify delivery package
python scripts/verify_delivery.py
```

## Directory Structure

```
benchsight_combined/
├── data/
│   ├── raw/games/{game_id}/          # Source tracking files
│   ├── output/                        # Generated CSV tables (70+ files)
│   └── BLB_Tables.xlsx               # Master dimension tables
├── src/
│   ├── etl_orchestrator.py           # Main ETL entry point
│   ├── pipeline/                      # ETL stages
│   ├── ingestion/                     # Data loaders
│   ├── transformations/              # Core transforms
│   └── *.py                          # Utility scripts
├── config/
│   └── settings.py                   # Game IDs, paths, etc.
├── scripts/
│   ├── test_validations.py           # Stat validations
│   └── verify_delivery.py            # Package checker
├── docs/
│   ├── handoff/                      # This folder - key docs
│   └── *.md                          # Various documentation
└── dashboard/                         # HTML dashboards
```

## Current Test Data

4 games loaded: 18969, 18977, 18981, 18987

## What Works Well

- ✅ Event and shift extraction
- ✅ Plus/minus calculations (3 versions)
- ✅ Video URL linking
- ✅ 54 stat validations passing
- ✅ Primary/foreign key structure
- ✅ Play chain generation

## What Needs Work

- ⚠️ Line combo stats (broken - removed)
- ⚠️ XY coordinate tables (schema only, no data)
- ⚠️ Zone data quality (varies by game)
- ⚠️ Some FK fill rates <100%

## Key Concepts

### Primary Keys
All fact tables use 12-character keys:
- Events: `E{game_id:05d}{event_index:06d}` → `E18969001234`
- Shifts: `S{game_id:05d}{shift_index:06d}` → `S18969000042`
- Sequences: `SQ{game_id:05d}{seq_index:06d}` → `SQ18969000001`

### Play Chains
Human-readable event sequences:
- `Faceoff > Pass > Shot > Save > Rebound`
- Stored in `play_chain` column with `event_chain_indices` for joining

### Three Plus/Minus Types
1. **Traditional**: +1 for GF, -1 for GA (even strength only)
2. **All Situations**: Includes PP/PK
3. **EN Adjusted**: Excludes empty net situations

## Contact / History

This project has been developed across multiple Claude sessions. Check:
- `/mnt/transcripts/` for conversation history
- `docs/REQUEST_LOG.md` for feature requests
- `docs/VALIDATION_LOG.tsv` for validation history

## Next Steps (Priority Order)

1. Fix line combo stats calculation
2. Populate XY tables when coordinate data available
3. Test with more games
4. Deploy to Supabase
5. Build Power BI reports
