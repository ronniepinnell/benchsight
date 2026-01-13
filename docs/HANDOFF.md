# BenchSight Chat Handoff Document

Last Updated: 2026-01-12
Version: 24.3

## Purpose

This document ensures continuity between chat sessions. **Read this at the start of every new chat.**

---

## Quick Start for New Chat

```bash
# 1. Always read these first:
cat docs/MAINTENANCE.md      # Doc update checklist
cat docs/CHANGELOG.md        # Recent changes
cat docs/TODO.md             # Current tasks

# 2. Check current version
grep "##" docs/CHANGELOG.md | head -1
```

---

## Project Summary

**BenchSight** is a hockey analytics platform for the NORAD recreational hockey league.

| Component | Description |
|-----------|-------------|
| ETL Pipeline | Processes game tracking data → 120 table data warehouse |
| Data Warehouse | PostgreSQL/Supabase with dimensional model |
| Tracker | Game tracking application |
| Dashboard | Analytics UI (HTML/JS) |

---

## Critical Rules (NEVER FORGET)

### Goal Counting
```sql
-- Goals ONLY via this exact filter:
WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored'

-- Shot_Goal is the SHOT, not the goal!
-- event_player_1 is ALWAYS the primary player (scorer, shooter, etc.)
```

### Version Numbering
```
Format: benchsight_v{CHAT}.{OUTPUT}

Examples:
- v24.4 = Chat 24, Output 3
- New chat = increment CHAT (v25.0)
- New output in same chat = increment OUTPUT (v24.4)

IMPORTANT: Folder name must match zip name!
```

### Documentation Updates (EVERY OUTPUT)
```
□ CHANGELOG.md - Add entry for changes
□ TODO.md - Update task status
□ Timestamps - Update "Last Updated" dates
```

---

## Current State (v24.4)

### Completed
- [x] 120-table ETL pipeline (base_etl.py + table modules)
- [x] Complete fact_events with 129 columns + 43 context columns
- [x] Complete fact_shifts with team-specific event columns
- [x] Complete fact_shift_players with proper venue mapping
- [x] 29 validated flag columns in fact_events
- [x] FK relationships validated (competition_tier_id fixed)
- [x] Comprehensive documentation (20+ docs)

### v24.4 Key Fixes
- [x] fact_shift_players: cf/ca/ff/fa/sf/sa venue-mapped for away players
- [x] fact_shifts: Team-specific event columns (home_zone_entries, etc.)
- [x] fact_shifts: Added bad_giveaways columns
- [x] competition_tier_id: Fixed FK mismatch (CT→TI)

### Pending
- [ ] 3 flag columns need review (is_high_danger, is_highlight, is_scoring_chance)
- [ ] Taxonomy dimension sync (117 values)
- [ ] Phase 1: Supabase raw tables + live dashboard
- [ ] Phase 2: Deployment + auth

---

## Key File Locations

```
benchsight_v24.4/
├── src/
│   ├── core/base_etl.py    # Main ETL (52 tables)
│   └── tables/             # Additional table modules
│       ├── dimension_tables.py   # 21 dim tables
│       ├── core_facts.py         # 3 core fact tables
│       ├── event_analytics.py    # 5 event tables
│       ├── shift_analytics.py    # 5 shift tables
│       └── remaining_facts.py    # 34 remaining tables
├── data/
│   ├── raw/                # Source files
│   └── output/             # Generated CSVs (120 tables)
├── scripts/
│   ├── validate_tables.py  # Data integrity checks
│   └── generate_data_dictionary.py
├── docs/
│   ├── CHANGELOG.md        # Version history
│   ├── TODO.md             # Task tracking
│   ├── HANDOFF.md          # This file
│   ├── DATA_DICTIONARY.md  # Column definitions
│   └── ... (20+ docs)
└── dashboard/              # HTML dashboards
```

---

## Known Issues / Decisions

### Type Conversion (SOLVED in v21.4)
- `pd.DataFrame.iterrows()` converts np.int64 → Python int
- `_clean_value()` now handles: Python int, bool, numpy types, strings
- Null-like codes ('FA', 'IR', '-', etc.) → NULL

### Goal Attribution
- Primary player (scorer) = `event_player_1`
- Primary assist = `event_player_2`
- Secondary assist = `event_player_3`

### Data Quality Notes
- 17 goals expected, 16 tracked (1 missing in raw data)
- Some players have 'FA' (Free Agent) as jersey number → NULL

---

## Validation Status

### Not Yet Validated
All 131 tables need table-by-table validation. Priority order:

1. **Tier 1**: fact_events, dim_player, dim_game (source of truth)
2. **Tier 2**: fact_gameroster, fact_player_season_stats (aggregations)
3. **Tier 3**: fact_team_season_stats, fact_goalie_game_stats
4. **Tier 4**: All other tables

See `docs/VALIDATION_PLAN.md` for full approach.

---

## Next Steps (For Next Chat)

If this chat ends, the next chat should:

1. **Read this handoff doc first**
2. Check CHANGELOG.md for latest version
3. Continue with table-by-table validation (start with fact_events)
4. After validation: build automated sanity checks into ETL
5. Then proceed to Phase 1 of ROADMAP.md

---

## Commands Reference

```bash
# Generate all CSVs
python run_etl.py

# Validate data integrity
python validate.py

# Generate Supabase schema
python upload.py --schema

# Upload to Supabase
python upload.py

# Package for delivery
zip -r benchsight_vX.Y.zip benchsight_vX.Y -x "*.pyc" -x "*__pycache__*"
```

---

## Contact / Context

- **Project Owner**: Ronnie (SQL Server expert)
- **League**: NORAD recreational hockey
- **Official Stats**: noradhockey.com
- **Goal**: Reduce game tracking from 8 hours to 1 hour, provide comprehensive analytics

---

## Memory Reminders for Claude

The user has these stored in Claude's memory:
1. Always provide complete project zip with updated docs
2. Goals ONLY via event_type='Goal' AND event_detail='Goal_Scored'
3. BenchSight delivery checklist
4. Version format: benchsight_v{CHAT}.{OUTPUT}

If these memories aren't visible, ask the user to confirm them.

---

## Code Quality Standards (CRITICAL)

**Read CODE_STANDARDS.md for full details. Key points:**

### Root-Level Solutions (Not Patchwork)
```
❌ BAD: Quick fixes, workarounds, patches on patches
✅ GOOD: Fix actual problems, understand full data flow
```

### Single Source of Truth
```python
# ONE canonical implementation per calculation
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
```

### Documentation Requirements
Every column must have:
- Data type
- Description
- Calculation formula (if derived)
- Validation status

### Before Delivering Any Code
```
□ Does it solve the root problem?
□ Is there ONE implementation for each calculation?
□ Is DATA_DICTIONARY updated?
□ Is validation_tracker.csv updated?
□ Does validate.py catch errors?
```

---

## Validation Tracking

**Files:**
- `docs/DATA_DICTIONARY_FULL.md` - Auto-generated, 131 tables
- `docs/validation_tracker.csv` - 3249 columns, track status per column
- `scripts/generate_data_dictionary.py` - Regenerates docs

**To regenerate after changes:**
```bash
python scripts/generate_data_dictionary.py
```

**To mark column as validated:**
Edit validation_tracker.csv, set `validated=Yes`, add date and notes.
