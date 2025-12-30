# 🐛 KNOWN BUGS - FIX BEFORE PROCEEDING

## BUG-001: ETL Scripts Strip Columns (CRITICAL)

**Status:** ✅ FIXED (2025-12-29)

**Problem:**
Running the ETL pipeline was stripping columns from fact_player_game_stats:
- Before ETL: 317 columns
- After ETL: 224 columns
- Lost: 93 columns including critical FKs

**Root Cause:**
The `_build_fact_player_game_stats` method in `src/etl_orchestrator.py` was rebuilding
the DataFrame from scratch, overwriting enhanced columns from `enhance_all_stats.py`.

**Fix Applied:**
Modified `_build_fact_player_game_stats` to:
1. Load existing fact_player_game_stats.csv if it exists
2. Preserve enhanced columns that aren't recalculated
3. Merge new calculated stats with existing enhanced columns

**Verification:**
```bash
# Test that ETL preserves columns
python -c "
from src.etl_orchestrator import ETLOrchestrator
orchestrator = ETLOrchestrator()
orchestrator.run(tables=['fact_player_game_stats'])
import pandas as pd
df = pd.read_csv('data/output/fact_player_game_stats.csv')
print(f'Columns: {len(df.columns)} (should be 317)')
"
```

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
