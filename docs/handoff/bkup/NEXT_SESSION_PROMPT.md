# BenchSight - Next Session Prompt

Copy and paste this entire prompt at the start of your next Claude session:

---

## PROMPT START

I'm continuing work on BenchSight, a hockey analytics ETL pipeline. Please read the handoff documentation to understand the project state.

**First, read these files in order:**
1. `docs/handoff/HANDOFF_COMPLETE_V2.md` - Overview and quick start
2. `docs/handoff/HONEST_ASSESSMENT_V2.md` - Current status and limitations
3. `docs/handoff/GAP_ANALYSIS_V2.md` - What's done vs what's needed
4. `docs/handoff/IMPLEMENTATION_PHASES_V2.md` - Where we are in the build

**Key Context:**
- Project: BenchSight hockey analytics for NORAD recreational league
- Status: ~75% complete, Phase 3 (Deployment) in progress
- Current: 77 CSV tables (40 dim + 37 fact), all validations passing
- Next step: Deploy to Supabase

**My immediate goal is:** [USER FILLS IN THEIR GOAL]

**Technical notes:**
- ETL: `python -m src.etl_orchestrator`
- FK Population: `python src/populate_all_fks_v2.py`
- Validations: `python scripts/test_validations.py`
- 4 test games: 18969, 18977, 18987, 18981
- Goals: event_type="Goal" OR event_detail contains "Shot Goal"

**Important memory:**
- User is Ronnie (SQL Server expert)
- Always provide complete project zip with updated docs
- event_player_1 = primary player, 's'=success, 'u'=unsuccessful
- Run verify_delivery.py before packaging
- Verify goals match noradhockey.com

## PROMPT END

---

## Quick Reference Commands

```bash
# Navigate to project
cd benchsight_combined

# Run ETL (regenerates all fact tables)
python -m src.etl_orchestrator

# Populate foreign keys
python src/populate_all_fks_v2.py

# Fix line combos (if needed)
python src/fix_line_combos.py

# Run all validations
python scripts/test_validations.py

# Check table row counts
wc -l data/output/*.csv

# View specific table schema
head -1 data/output/fact_events.csv

# Create delivery package
zip -r benchsight_combined.zip benchsight_combined -x "*.pyc" -x "*__pycache__*"
```

---

## Common Tasks for Next Session

### Task 1: Deploy to Supabase
```
Goal: Execute Supabase DDL and upload all CSVs

Steps:
1. Run sql/01_create_tables_generated.sql in Supabase SQL editor
2. Execute python src/supabase_upload_v3.py
3. Verify row counts in Supabase match local CSVs
4. Test a few FK relationships
```

### Task 2: Add New Test Game
```
Goal: Process game XXXXX

Steps:
1. Create folder data/raw/games/XXXXX
2. Add XXXXX_tracking.xlsx
3. Run python -m src.etl_orchestrator
4. Run python src/populate_all_fks_v2.py
5. Verify with python scripts/test_validations.py
```

### Task 3: Modify Dimension Table
```
Goal: Add new values to dim_X

Steps:
1. Edit data/output/dim_X.csv
2. Add potential_values or old_equiv for fuzzy matching
3. Run python src/populate_all_fks_v2.py
4. Check fill rates in output
```

### Task 4: Implement xG Model
```
Goal: Add expected goals calculation

Steps:
1. Design shot quality factors (distance, angle, type)
2. Create dim_xg_factors.csv
3. Add xG column to fact_shot_xy
4. Aggregate to fact_player_game_stats
5. Validate against actual goal totals
```

---

## File Locations Quick Reference

| What You Need | Location |
|---------------|----------|
| Main ETL code | src/etl_orchestrator.py |
| FK population | src/populate_all_fks_v2.py |
| Validations | scripts/test_validations.py |
| Dimension tables | data/output/dim_*.csv |
| Fact tables | data/output/fact_*.csv |
| Raw tracking | data/raw/games/XXXXX/ |
| Schema docs | docs/SCHEMA.md |
| Stat definitions | docs/STAT_DEFINITIONS.md |
| Supabase DDL | sql/01_create_tables_generated.sql |
| Upload script | src/supabase_upload_v3.py |

---

## Troubleshooting

### "FK fill rate is low"
- Check if source column has values: `df['column'].value_counts()`
- Add mapping to dim table's potential_values or old_equiv
- Re-run populate_all_fks_v2.py

### "Validation failing"
- Read the specific test in scripts/test_validations.py
- Check if source data has changed
- Verify official data at noradhockey.com

### "ETL error"
- Check data/raw/games/XXXXX/ has required files
- Verify Excel format matches expected schema
- Look for null/missing required columns

---

*Last Updated: December 29, 2024*
