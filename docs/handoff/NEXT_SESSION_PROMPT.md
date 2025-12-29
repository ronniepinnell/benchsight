# BenchSight Next Session Prompt

## Copy this entire prompt to start your next conversation:

---

# CONTEXT: BenchSight Hockey Analytics Project

You are continuing work on BenchSight, a hockey analytics ETL pipeline for the NORAD recreational hockey league.

## 🚨 CRITICAL BUG - FIX FIRST

**PRIORITY 1: The ETL scripts have a bug that strips columns.**
- Original data: 317 columns with all FKs
- After running ETL: 224 columns - LOSES 93 columns including home_team_id, away_team_id, venue_id, team_id

**DO NOT run etl.py, etl_orchestrator.py, or enhance_all_stats.py until this is fixed.**

The current data in `data/output/` is CORRECT (317 columns). If ETL is run, it will destroy the data.

### Bug Fix Task:
1. Audit `src/enhance_all_stats.py` - this is likely where columns are being dropped
2. Ensure all 317 columns are preserved through the pipeline
3. Test on a COPY of data first
4. Only run on real data after verification

---

## AFTER BUG IS FIXED: Deploy to Supabase

Once ETL is safe, deploy using:
```bash
python scripts/supabase_test_connection.py
python scripts/supabase_loader.py --rebuild
python scripts/supabase_loader.py --verify
```

## PROJECT LOCATION
Extract zip and navigate to `benchsight_combined 6/`

## READ FIRST
1. `START_HERE.md` - Rules, reading order, critical warnings
2. `docs/handoff/COMPLETE_HANDOFF.md` - Full project overview
3. `docs/DOCUMENTATION_HUB.html` - Open in browser for visual docs

## CURRENT STATE
- ✅ 317 columns (CORRECT - do not run ETL)
- ✅ All FKs present (home_team_id, away_team_id, etc.)
- ✅ 17/17 goals verified against noradhockey.com
- ✅ 131 validation tests passing
- ❌ ETL BUG - strips columns when run
- ❌ Supabase not deployed yet

## RULES TO FOLLOW
- At 50% capacity, notify how much remains
- At 90% capacity, package everything with updated docs
- Never remove files, only append/update
- Ask questions before starting tasks
- Verify goals match noradhockey.com
- Run verify_delivery.py before packaging

## KNOWN BUGS
1. **ETL Column Stripping** - Running ETL drops 93 columns. FIX FIRST.
2. **3 Untracked Games** - 18965, 18991, 19032 are template only
3. **Missing Assists** - Games 18977, 18981 lack assist data

---

# END OF PROMPT
