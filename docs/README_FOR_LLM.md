# BenchSight - LLM Context Guide

## What Is This Project?

BenchSight is a hockey analytics platform for NORAD recreational hockey league. It processes game tracking data into a 98-table data warehouse with 317+ statistical columns per player per game.

## Key Rules for LLM Assistants

### Event Attribution
- `event_player_1` = PRIMARY player (shooter, passer, etc.) - FIRST row per event_index
- `event_player_2` = Secondary player (assist 1, defender, etc.)
- `event_player_3` = Tertiary player (assist 2)
- Success: `'s'` = successful, `'u'` = unsuccessful

### Goals Detection
Goals are tracked TWO ways (must check both):
1. `event_type = 'Goal'`
2. `event_detail IN ('Shot Goal', 'Goal Scored')`

### Data Flow
```
data/raw/games/{game_id}/ → ETL → data/output/*.csv → Supabase
```

### Table Naming
- `dim_*` = Dimension/lookup tables (44 tables)
- `fact_*` = Fact/transactional tables (51 tables)
- `qa_*` = Quality assurance tables (1 table)

### Key Fact Tables
- `fact_player_game_stats` - 317 columns per player per game
- `fact_events` - Raw tracked events
- `fact_shifts` - Player shift data
- `fact_h2h` - Head-to-head matchups
- `fact_wowy` - With Or Without You analysis
- `fact_line_combos` - Line combination stats

### Before Packaging
Always run: `scripts/verify_delivery.py`
Verify goals match: noradhockey.com

### Stats Reference
See `docs/STATS_REFERENCE_COMPLETE.md` for all 317 columns with:
- Formulas
- Plain English descriptions
- Good/Bad benchmarks

## File Locations

| Path | Contents |
|------|----------|
| `data/output/` | 96 CSVs for Supabase |
| `data/raw/games/` | Source tracking files |
| `scripts/flexible_loader.py` | Supabase deployment |
| `sql/01_CREATE_ALL_TABLES.sql` | Create all tables |
| `src/main.py` | ETL entry point |
| `docs/` | All documentation |

## Quick Commands

```bash
# Deploy to Supabase
python scripts/flexible_loader.py --scope all --operation replace

# Run ETL
python src/main.py --games 18969 18977

# Validate
python scripts/verify_delivery.py
```
