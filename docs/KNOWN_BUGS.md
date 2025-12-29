# 🐛 KNOWN BUGS - FIX BEFORE PROCEEDING

## BUG-001: ETL Scripts Strip Columns (CRITICAL)

**Status:** 🔴 OPEN - MUST FIX BEFORE RUNNING ETL

**Problem:**
Running the ETL pipeline strips columns from fact_player_game_stats:
- Before ETL: 317 columns
- After ETL: 224 columns
- Lost: 93 columns including critical FKs

**Lost Columns Include:**
- home_team_id
- away_team_id  
- venue_id
- team_id
- game_score
- game_score_per_60
- clutch_goals
- odd_man_rushes
- breakaway_attempts
- And 84 more...

**Affected Scripts:**
- `etl.py`
- `src/etl_orchestrator.py`
- `src/enhance_all_stats.py` (likely culprit)

**Current Workaround:**
DO NOT RUN ETL. The data in `data/output/` is correct with 317 columns.

**To Fix:**
1. Audit `src/enhance_all_stats.py` for column dropping logic
2. Check for any `df = df[columns]` or similar filtering
3. Ensure all original columns pass through
4. Test on copy of data first

**To Restore if ETL Run Accidentally:**
Restore `data/output/` from `benchsight_combined_6.zip` backup

---

## BUG-002: Game 18977 Galen Wood Scorer (RESOLVED)

**Status:** ✅ FIXED

**Problem:** Galen Wood was listed as event_team_player_2 (assister) instead of event_team_player_1 (scorer)

**Resolution:** Fixed in tracking file and stats updated. Goals now 6/6.

---

## Open Issues (Not Bugs)

### 3 Untracked Games
Games 18965, 18991, 19032 have template files but no tracking data.
**Resolution:** Need to be tracked using game tracker.

### Missing Assists in 2 Games
Games 18977 and 18981 don't have assist data.
**Resolution:** Source data limitation - tracker didn't record assists.

### 48 Zero Columns
48 columns are always zero (XY coords, score state, PP tags).
**Resolution:** Source data doesn't capture this info.
