# ETL / Data Engineer Handoff

## Overview

You're taking over the BenchSight ETL pipeline - a hockey analytics data warehouse that processes game tracking data into a 98-table dimensional model with 317+ statistical columns.

## Your Responsibilities

1. **ETL Pipeline Maintenance** - Keep data flowing from tracking files to Supabase
2. **Data Quality** - Validate stats, fix anomalies, ensure accuracy
3. **Schema Evolution** - Add new tables/columns as needed
4. **Performance** - Optimize queries and data loading

---

## Quick Start

```bash
# 1. Test the pipeline works
./run_etl.sh --status

# 2. Process a game
./run_etl.sh --game 18969

# 3. Export to CSV
./run_etl.sh --export

# 4. Deploy to Supabase
./run_deploy.sh
```

---

## Architecture

### Data Flow
```
data/raw/games/{game_id}/BLB_*.xlsx   →   ETL Pipeline   →   data/output/*.csv   →   Supabase
         ↓                                     ↓                    ↓
    Tracking files              Stage → Intermediate → Datamart    98 tables
    (events, shifts)            (raw)    (transforms)  (star schema)
```

### Key Files

| File | Purpose |
|------|---------|
| `src/main.py` | ETL entry point / CLI |
| `src/pipeline/orchestrator.py` | Coordinates ETL layers |
| `src/ingestion/blb_loader.py` | Loads BLB_Tables.xlsx |
| `src/ingestion/game_loader.py` | Loads game tracking files |
| `src/ingestion/xy_loader.py` | Loads XY coordinate data |
| `scripts/flexible_loader.py` | Supabase deployment |

### Database Layers

| Layer | Purpose | Tables |
|-------|---------|--------|
| Stage | Raw data loading | `stg_*` |
| Intermediate | Transforms, joins | `int_*` |
| Datamart | Star schema (dims + facts) | `dim_*`, `fact_*` |

---

## Core Tables

### Dimensions (44 tables)
Reference/lookup tables:
- `dim_player` - Player master data
- `dim_team` - Team definitions
- `dim_schedule` - Game schedule
- `dim_event_type` - Event type codes
- `dim_stat` - Stat definitions

### Facts (51 tables)
Transactional/metric tables:
- `fact_events` - All tracked events (5,833 rows)
- `fact_shifts` - Player shifts (672 rows)
- `fact_player_game_stats` - **317 columns per player per game**
- `fact_team_game_stats` - Team-level stats
- `fact_h2h` - Head-to-head matchups
- `fact_wowy` - With Or Without You analysis
- `fact_line_combos` - Line combination stats

---

## Key ETL Rules

### Event Attribution
```
event_player_1 = PRIMARY player (first row per event_index)
event_player_2 = Secondary (assist 1, defender)
event_player_3 = Tertiary (assist 2)
```

### Success Codes
```
's' = successful
'u' = unsuccessful
```

### Goal Detection (CRITICAL)
Goals are tracked TWO ways - must check BOTH:
```sql
WHERE event_type = 'Goal'
   OR event_detail IN ('Shot Goal', 'Goal Scored')
```

---

## Common Tasks

### Add a New Game

```bash
# 1. Place tracking file
cp BLB_GameTracking_18999.xlsx data/raw/games/18999/

# 2. Run ETL
./run_etl.sh --game 18999

# 3. Verify
python scripts/validate_stats.py

# 4. Deploy
./run_deploy.sh --scope category --category all_facts --operation replace
```

### Reprocess All Games

```bash
./run_etl.sh --process-all --export
./run_deploy.sh
```

### Add a New Stat Column

1. Add to calculation in `src/analytics/`
2. Update `docs/STATS_REFERENCE_COMPLETE.md`
3. Add column to `sql/01_CREATE_ALL_TABLES.sql`
4. Add test to `tests/test_stats_calculations.py`
5. Run: `./run_etl.sh --export && ./run_deploy.sh`

### Fix Data Quality Issue

```bash
# 1. Identify issue
python scripts/qa_comprehensive.py

# 2. Fix in source or transform
# Edit relevant src/ file

# 3. Reprocess affected games
./run_etl.sh --games 18969,18977 --export

# 4. Validate
python scripts/validate_stats.py

# 5. Deploy
./run_deploy.sh
```

---

## Utility Scripts

Located in `scripts/utilities/`:

| Script | Purpose |
|--------|---------|
| `generate_schema.py` | Generate SQL from CSV headers |
| `schema_definition.py` | Schema definitions |
| `fix_data_accuracy.py` | Fix data accuracy issues |
| `fix_dim_mappings.py` | Fix dimension mappings |
| `populate_all_fks_v2.py` | Populate foreign keys |
| `add_all_fkeys.py` | Add FK constraints |
| `export_all_data.py` | Export all data to CSV |
| `validate_h2h_wowy.py` | Validate H2H/WOWY tables |

---

## Validation Scripts

| Script | Purpose |
|--------|---------|
| `scripts/validate_stats.py` | Validate stat calculations |
| `scripts/validate_against_ground_truth.py` | Compare to noradhockey.com |
| `scripts/qa_comprehensive.py` | Full QA sweep |
| `scripts/qa_dynamic.py` | Dynamic validation |
| `scripts/etl_validation.py` | Post-ETL checks |

---

## SQL Files

| File | Purpose |
|------|---------|
| `sql/01_CREATE_ALL_TABLES.sql` | Create all 98 tables |
| `sql/02_TYPE_FIXES.sql` | Fix column types |
| `sql/03_TRUNCATE_DATA.sql` | Truncate all data |
| `sql/utilities/drop_all_tables.sql` | Drop all tables |
| `sql/utilities/reset_supabase.sql` | Full reset |

---

## Configuration

### config/config_local.ini
```ini
[supabase]
url = https://YOUR_PROJECT.supabase.co
service_key = YOUR_SERVICE_ROLE_KEY

[loader]
batch_size = 500
verbose = true
```

### Environment Setup
```bash
pip install pandas supabase openpyxl python-dotenv
```

---

## Known Issues

See `docs/HONEST_ASSESSMENT.md` for full list:

1. **Shift data gaps** - Some games have incomplete shift tracking
2. **XY coordinate gaps** - Not all events have coordinates
3. **Period codes** - Some period fields have "OT", "SO" (text, not int)
4. **Player numbers** - Some have "FA" for free agent

---

## Performance Tips

1. **Batch inserts** - Use `batch_size=500` for Supabase
2. **Replace vs Append** - Use `replace` for clean loads, `append` for incremental
3. **Category loading** - Load dims first, then facts
4. **Parallel processing** - Games can be processed in parallel

---

## Monitoring

### Check Table Counts
```bash
python scripts/flexible_loader.py --scope full --dry-run
```

### Check Data Quality
```bash
python scripts/qa_comprehensive.py
```

### Verify Goals Match Official
```bash
python scripts/validate_against_ground_truth.py
```

---

## Contacts & Resources

- **Data Source**: NORAD Hockey League (noradhockey.com)
- **Ground Truth**: Official game box scores
- **Documentation**: `docs/INDEX.md`
- **Stats Reference**: `docs/STATS_REFERENCE_COMPLETE.md`

---

## First Week Checklist

- [ ] Run `./run_etl.sh --status` to verify pipeline works
- [ ] Review `docs/CODE_ARCHITECTURE.md` for code structure
- [ ] Review `docs/STATS_REFERENCE_COMPLETE.md` for all stats
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Deploy test: `./run_deploy.sh --dry-run`
- [ ] Review `docs/HONEST_ASSESSMENT.md` for known issues
- [ ] Process one game end-to-end
- [ ] Validate against noradhockey.com
