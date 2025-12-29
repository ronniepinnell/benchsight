# 🚨🚨🚨 STOP - READ THIS FIRST 🚨🚨🚨

## CRITICAL BUG: DO NOT RUN ETL SCRIPTS

**The ETL scripts (etl.py, etl_orchestrator.py, enhance_all_stats.py) have a bug that DESTROYS your data.**

| Before ETL | After ETL | Lost |
|------------|-----------|------|
| 317 columns | 224 columns | 93 columns |
| All FKs ✅ | FKs GONE ❌ | home_team_id, away_team_id, etc. |

### ⚠️ STEP 1 FOR NEW SESSION: FIX THIS BUG

See `docs/KNOWN_BUGS.md` for full details.

**Your current data in `data/output/` is CORRECT. Don't run ETL until bug is fixed.**

---

# 📚 BenchSight Master Guide

## Session Rules (MUST FOLLOW)

1. **At 50% capacity** - Notify how much remains
2. **At 90% capacity** - Package everything with updated docs
3. **When packaging** - Include full project, docs, handoffs, visuals
4. **Never remove** - Only append/update
5. **Ask first** - Summarize and share plan before starting
6. **Keep logs** - Requests, summaries, requirements, changes
7. **Verify goals** - Must match noradhockey.com
8. **Run verify_delivery.py** before packaging

## BenchSight Rules
- `event_team_player_1` = scorer (first row per event_index)
- Goals: `event_type == 'Goal'` OR `event_detail contains 'Shot Goal'`
- 's' = successful, 'u' = unsuccessful
- 12-character primary keys

---

## 📖 READING ORDER

| Step | File | Purpose |
|------|------|---------|
| 1 | `docs/KNOWN_BUGS.md` | **FIX BUG FIRST** |
| 2 | `docs/handoff/COMPLETE_HANDOFF.md` | Full context |
| 3 | `docs/DOCUMENTATION_HUB.html` | **OPEN IN BROWSER** |
| 4 | `docs/SUPABASE_DEPLOYMENT.md` | Deploy after bug fixed |

---

## 🚀 AFTER BUG IS FIXED: Supabase Commands

```bash
# Test connection
python scripts/supabase_test_connection.py

# Full rebuild
python scripts/supabase_loader.py --rebuild

# Upload options
--all / --dims / --facts / --qa
--tables x,y
--games 18969
--mode append / --mode replace
--teardown / --verify / --dry-run
```

---

## ✅ CURRENT STATUS

| Item | Status |
|------|--------|
| Data columns | 317 ✅ (don't run ETL!) |
| Goals verified | 17/17 ✅ |
| FKs present | All ✅ |
| Tests passing | 131 ✅ |
| ETL Bug | 🔴 OPEN - FIX FIRST |
| Supabase | ⏳ After bug fix |
