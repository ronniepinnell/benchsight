# BenchSight ETL - Complete Handoff Document

*Prepared: December 29, 2024*

## Executive Summary

BenchSight is a hockey analytics ETL pipeline that transforms game tracking data into a dimensional data warehouse. The system is approximately **70% complete** with core functionality working but several gaps remaining.

### Quick Stats
- **77 output tables** (dimensions + facts)
- **4 games processed** (test data)
- **54 validations passing**
- **11,635 events** extracted
- **4,626 shifts** tracked

---

## Project Structure

```
benchsight_combined/
├── data/
│   ├── raw/games/           # Source tracking files
│   ├── output/              # 77 CSV output tables
│   └── BLB_Tables.xlsx      # Master dimensions
├── src/
│   ├── etl_orchestrator.py  # Main entry point
│   ├── fix_dim_mappings.py  # FK application
│   ├── complete_chain_builder.py
│   ├── stats_builder.py
│   ├── xy_tables.py
│   └── pipeline/            # ETL stages
├── config/
│   └── settings.py          # Configuration
├── scripts/
│   ├── test_validations.py  # Stat validations
│   └── verify_delivery.py   # Package checker
├── docs/
│   ├── handoff/             # ← YOU ARE HERE
│   └── diagrams/            # Mermaid diagrams
├── sql/                      # PostgreSQL DDL
└── dashboard/               # HTML dashboards
```

---

## How to Run

### Full Pipeline
```bash
cd benchsight_combined

# 1. Run main ETL
python -m src.etl_orchestrator

# 2. Apply foreign keys
python src/fix_dim_mappings.py

# 3. Build play chains
python src/complete_chain_builder.py

# 4. Run validations
python scripts/test_validations.py
```

### Single Commands
```bash
# Check package completeness
python scripts/verify_delivery.py

# Create XY table schemas (no data yet)
python src/xy_tables.py
```

---

## Key Concepts

### Primary Keys
12-character format: `{prefix}{game_id:05d}{index:06d}`

| Table | Prefix | Example |
|-------|--------|---------|
| Events | E | E18969001234 |
| Shifts | S | S18969000042 |
| Sequences | SQ | SQ18969000001 |
| Plays | PL | PL18969000001 |
| Rushes | RU | RU18969001011 |
| Cycles | CY | CY18969001048 |

### Play Chains
Human-readable event sequences stored in `play_chain` column:
```
Faceoff > Pass > Possession > Pass > Shot > Save > Rebound
```

### Plus/Minus Versions
1. **Traditional**: EV only, +1 GF, -1 GA
2. **All Situations**: Includes PP/PK
3. **EN Adjusted**: Excludes empty net goals

---

## What Works

| Component | Status | Confidence |
|-----------|--------|------------|
| Event extraction | ✅ | High |
| Shift extraction | ✅ | High |
| Plus/minus (3 types) | ✅ | High (validated) |
| Video URL linking | ✅ | High |
| Sequence detection | ✅ | Medium |
| Rush detection | ✅ | Medium |
| H2H/WOWY | ⚠️ | Medium (needs validation) |
| Play chains | ✅ | High |
| Foreign keys | ⚠️ | Medium (some low fill rates) |

---

## What's Broken/Missing

| Issue | Severity | Notes |
|-------|----------|-------|
| Line combo stats | High | Calculation was wrong, stats removed |
| XY coordinates | Medium | Schema only, no data source yet |
| Zone data | Medium | Varies 0-87% by game |
| Supabase deployment | High | Not deployed |
| Unit tests | Medium | Only integration validations |

---

## Data Quality

| Metric | Best Game (18969) | Worst Game (18977) |
|--------|-------------------|-------------------|
| event_team_zone fill | 86.8% | 0% |
| Cycles detected | 9 | 0 |
| Zone entries | 285 | 337 |

The zone data quality is a **source data issue**, not an ETL bug.

---

## Diagrams

### Schema Overview
See: `docs/diagrams/schema_overview.mermaid`

Render at: https://mermaid.live or in VS Code with Mermaid extension

### Data Flow
See: `docs/diagrams/data_flow.mermaid`

---

## Files for Next Engineer

| Document | Purpose |
|----------|---------|
| `README_NEXT_ENGINEER.md` | Quick start (read first) |
| `HONEST_ASSESSMENT.md` | Real status, no sugar-coating |
| `GAP_ANALYSIS.md` | What's done vs what's needed |
| `IMPLEMENTATION_PHASES.md` | Roadmap with phases |
| `TABLE_INVENTORY.md` | All 77 tables listed |

---

## Immediate Next Steps

1. **Fix line combo stats** (2-4 hours)
   - File: `src/stats_builder.py`
   - Issue: Not filtering events by actual line combo players
   
2. **Validate H2H/WOWY manually** (1-2 hours)
   - Pick 2-3 player pairs
   - Verify shift counts against raw data

3. **Deploy to Supabase** (4-8 hours)
   - Review `sql/postgres/` DDL
   - Create project at supabase.com
   - Load dimension tables first, then facts

---

## Known Issues Log

| ID | Issue | Workaround |
|----|-------|------------|
| 1 | Zone data sparse in some games | Use game 18969 for testing |
| 2 | Line combo stats wrong | Stats removed from table |
| 3 | XY tables empty | Schema ready, awaiting data |
| 4 | Some FKs have low fill rates | Expected for optional fields |

---

## Contact Points

- **Project Owner**: Ronnie (NORAD hockey league)
- **Development History**: Claude AI sessions (see `/mnt/transcripts/`)
- **Documentation**: `docs/REQUEST_LOG.md` for feature requests

---

## Validation Summary

```
python scripts/test_validations.py

PASSED:   54
FAILED:   0
WARNINGS: 1 (no EN goals in test data)
```

All critical validations pass. The EN goal warning is expected given test data.
