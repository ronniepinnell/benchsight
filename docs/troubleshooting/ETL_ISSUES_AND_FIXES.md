# ETL Issues and Fixes

## Issues Found

### 1. Only 4 Games Processing (Not All Games)

**Problem:** Only 4 games are being processed instead of all available games.

**Root Cause:** 
- Games are being auto-excluded if they don't have proper tracking files
- The `discover_games()` function in `base_etl.py` validates each game and excludes those without:
  - Tracking Excel files (`*_tracking.xlsx`)
  - Required sheets ('events' and 'shifts')
  - Proper event_index columns
  - At least 5 rows of data

**Solution:**
1. Check which games have tracking files:
   ```bash
   ls -la data/raw/games/*/*_tracking.xlsx
   ```

2. If games are missing tracking files, they need to be added to `data/raw/games/{game_id}/`

3. To manually include games, remove them from `config/excluded_games.txt` (currently only has 3 games, but 14 are being excluded)

4. The auto-exclusion happens in `src/core/base_etl.py` lines 97-137. Games are excluded if:
   - No tracking file found
   - Missing 'events' or 'shifts' sheets
   - Missing event_index column
   - Less than 5 rows of data

### 2. Empty Tables (0 Rows)

**Problem:** Many tables have 0 rows because they're aggregations that require:
- More games (season/career stats need multiple games)
- Specific conditions (e.g., XY tables need coordinate data)
- event_player_1 filtering (some stats should only count for primary player)

**Tables with 0 rows:**
- `fact_player_career_stats` - Needs multiple games per player
- `fact_player_season_stats` - Needs multiple games per player-season
- `fact_team_season_stats` - Needs multiple games per team-season
- `fact_player_micro_stats` - May need specific event types
- `fact_player_position_splits` - Needs position data
- `fact_player_trends` - Needs time-series data
- `fact_player_stats_long` - Needs aggregated data
- `fact_player_boxscore_all` - May need specific calculation
- `fact_player_xy_long`, `fact_puck_xy_long` - Need XY coordinate data
- `fact_player_matchups_xy`, `fact_player_puck_proximity` - Need XY data
- `fact_shot_xy` - Needs shot coordinate data
- `qa_scorer_comparison`, `qa_suspicious_stats`, `fact_suspicious_stats` - Need validation data

**Solution:**
- These tables will populate as more games are added
- Some require specific data (XY coordinates) that may not be in all tracking files
- Ensure `event_player_1` filtering is applied (see issue #3)

### 3. event_player_1 Stats Only

**Problem:** User wants to ensure only `event_player_1` stats are included.

**Current Status:** 
- Most calculation functions already filter for `event_player_1` (PRIMARY_PLAYER role)
- Check functions like `calculate_zone_entry_exit_stats()` which explicitly filters:
  ```python
  pe_primary = pe[pe['player_role'].astype(str).str.lower() == PRIMARY_PLAYER]
  ```

**Action Needed:**
- Verify all stat calculations use `event_player_1` filtering
- Search for places where stats are calculated without role filtering

### 4. Error: 'int' object has no attribute 'notna'

**Problem:** Error in player stats calculation.

**Location:** `src/tables/core_facts.py` or `src/builders/player_stats.py`

**Likely Cause:** 
- Type mismatch: `game_id` might be int but compared to string column
- Or an integer value is being treated as a pandas Series

**Fix Needed:**
- Ensure `game_id` is consistently string type throughout
- Check `get_game_ids()` returns strings (it does: `events['game_id'].dropna().unique().tolist()`)
- Check `get_players_in_game()` expects string game_id, not int

### 5. Error: "No columns to parse from file"

**Problem:** Some tables fail to load because CSV files are empty or malformed.

**Affected Tables:**
- `fact_player_career_stats`
- V11 enhancements (likely `qa_suspicious_stats`)
- Macro stats (likely `fact_player_career_stats`)

**Solution:**
- These tables depend on `fact_player_game_stats` existing
- Since player stats failed, these dependent tables can't be built
- Fix the player stats error first, then these will work

### 6. Missing Columns: 'competition_tier_id', 'opp_team_rating_avg'

**Problem:** Some tables reference columns that don't exist.

**Solution:**
- Add checks for column existence before using them
- Provide default values if columns are missing

## Immediate Actions

1. **Fix game_id type consistency:**
   - Ensure all game_id comparisons use same type (string)
   - Check `get_players_in_game()` signature matches usage

2. **Fix player stats error:**
   - Find where `.notna()` is called on an int
   - Ensure all pandas operations use Series/DataFrame, not raw values

3. **Add more games:**
   - Check which games have tracking files
   - Add missing tracking files or remove games from exclusion

4. **Verify event_player_1 filtering:**
   - Search codebase for stat calculations
   - Ensure PRIMARY_PLAYER role is used

## Files to Check

- `src/builders/player_stats.py` - Player stats builder
- `src/tables/core_facts.py` - Core stat calculations
- `src/core/base_etl.py` - Game discovery logic
- `config/excluded_games.txt` - Excluded games list
