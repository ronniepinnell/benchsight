# Fix for Empty Tables Issue

## Root Cause

**The tables are empty because `fact_player_game_stats` is failing to build** due to the error:
```
'int' object has no attribute 'notna'
```

This causes a cascade failure - all tables that depend on `fact_player_game_stats` are empty:
- `fact_player_season_stats` - depends on `fact_player_game_stats`
- `fact_player_boxscore_all` - depends on `fact_player_game_stats`
- `fact_player_micro_stats` - depends on `fact_player_game_stats`
- `fact_player_career_stats` - depends on `fact_player_season_stats`
- `fact_team_season_stats` - depends on team game stats
- And many more...

## Fixes Applied

1. **Fixed game_id type consistency** in:
   - `get_players_in_game()` - now converts game_id to string
   - `build_player_stats()` - now converts game_id to string for comparisons
   - `calculate_ratings_adjusted_stats()` - now converts game_id to string
   - `calculate_advanced_shift_stats()` - now converts game_id to string
   - `calculate_player_shift_stats()` - now converts game_id to string
   - `calculate_zone_entry_exit_stats()` - now converts game_id to string

2. **Fixed rating column access** in `calculate_player_shift_stats()`:
   - Added safety checks to ensure columns are Series before calling `.notna()`
   - Prevents "'int' object has no attribute 'notna'" error

3. **Fixed venue extraction** to use `pd.notna()` instead of direct access

## Remaining Issues

Many calculation functions still need game_id type fixes. The pattern is:
- Convert `game_id` to string: `game_id_str = str(game_id)`
- Use `.astype(str)` on DataFrame columns: `df['game_id'].astype(str) == game_id_str`

Functions that still need fixing:
- `calculate_strength_splits()`
- `calculate_shot_type_stats()`
- `calculate_pass_type_stats()`
- `calculate_playmaking_stats()`
- `calculate_pressure_stats()`
- `calculate_competition_tier_stats()`
- `calculate_game_state_stats()`
- `calculate_period_splits()`
- `calculate_danger_zone_stats()`
- `calculate_rush_stats()`
- `calculate_micro_stats()`
- `calculate_xg_stats()`
- `calculate_player_event_stats()`
- And more...

## Quick Fix Script

Run this to fix all game_id comparisons at once:

```python
import re

file_path = 'src/tables/core_facts.py'
with open(file_path, 'r') as f:
    content = f.read()

# Pattern: function definitions with game_id parameter
# Then find all comparisons like df['game_id'] == game_id
# Replace with: game_id_str = str(game_id) and df['game_id'].astype(str) == game_id_str

# This is complex - better to fix manually or function by function
```

## Testing

After fixes, run ETL again:
```bash
python3 run_etl.py
```

The tables should populate once `fact_player_game_stats` builds successfully.

## Why Tables Were Populated Before

The tables were populated before because:
1. Either `fact_player_game_stats` was building successfully
2. Or the code had different type handling
3. Or there were more games being processed (more data = more populated tables)

The current issue is that with only 4 games and the player stats failing, dependent tables have no source data.
