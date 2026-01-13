# BenchSight Changelog

## v29.0 (Current) - Game Type Aggregator & Code Refactor

### Summary
- **Created `game_type_aggregator.py`** - Single source of truth for game_type splits
- **6 season stats tables** refactored to use shared utility
- **Eliminated code duplication** - GAME_TYPE_SPLITS now defined once

### Architecture Change: game_type_aggregator

New utility module at `src/utils/game_type_aggregator.py` provides:

| Function/Constant | Purpose |
|-------------------|---------|
| `GAME_TYPE_SPLITS` | `['Regular', 'Playoffs', 'All']` - THE canonical list |
| `add_game_type_to_df()` | Adds game_type column via schedule join |
| `get_team_record_from_schedule()` | Calculate W-L-T-Pts from schedule |
| `get_goalie_record_from_games()` | Calculate goalie W-L-T from game data |

### Tables Using game_type_aggregator

All 6 season stats tables now import from the shared utility:

| Table | File |
|-------|------|
| fact_team_season_stats_basic | macro_stats.py |
| fact_player_season_stats_basic | macro_stats.py |
| fact_goalie_season_stats_basic | macro_stats.py |
| fact_goalie_season_stats | macro_stats.py |
| fact_player_season_stats | remaining_facts.py |
| fact_team_season_stats | remaining_facts.py |

### Row Counts (unchanged from initial implementation)

| Table | Rows | Regular | Playoffs | All |
|-------|------|---------|----------|-----|
| fact_team_season_stats_basic | 123 | 45 | 33 | 45 |
| fact_player_season_stats_basic | 1,972 | 750 | 472 | 750 |
| fact_goalie_season_stats_basic | 195 | 78 | 38 | 79 |
| fact_team_season_stats | 10 | 5 | 0 | 5 |
| fact_player_season_stats | 126 | 63 | 0 | 63 |
| fact_goalie_season_stats | 10 | 5 | 0 | 5 |

### Code Quality Improvements

**Before (patchwork):**
```python
# Duplicated in 6 different functions across 2 files
GAME_TYPES = ['Regular', 'Playoffs', 'All']
df = df.merge(schedule[['game_id', 'game_type']], ...)
df['game_type'] = df['game_type'].fillna('Regular')
```

**After (single source of truth):**
```python
from src.utils.game_type_aggregator import GAME_TYPE_SPLITS, add_game_type_to_df

df = add_game_type_to_df(df, schedule)
for game_type in GAME_TYPE_SPLITS:
    ...
```

### Bug Fixes from v28.7
- Fixed season_id mapping for scrimmage games (N2025S)
- Fixed games_played counting all seasons instead of per-season
- Added ties tracking from schedule home_team_t/away_team_t columns
- Fixed points calculation (wins×2 + ties×1)

---

## v28.3 (Previous) - View Layer, Dashboard Integration & ETL Cleanup

### SQL Views
- Created 26 SQL views for dashboard queries
- Views organized by function: leaderboards, standings, rankings, etc.

### Dashboard Integration
- Next.js dashboard components integrated
- Supabase connection established

### ETL Cleanup
- Deprecated 3 snapshot tables (replaced by views)
- Cleaned up unused code paths

### View Updates (v29.0)

**New/Updated Views:**
- Added `ties` column to all standings views
- Added `game_type` filter to all leaderboard and standings views
- New views: `v_standings_current_regular`, `v_standings_current_playoffs`, `v_standings_by_game_type`
- New views: `v_leaderboard_points_by_game_type`, `v_leaderboard_goalie_wins_by_game_type`
- New view: `v_leaderboard_goalie_record` (W-L-T record summary)

**New Scripts:**
- `scripts/deploy_views.py` - Deploy SQL views to Supabase
- `scripts/sync_views_to_schema.py` - Check view/table schema drift

**Usage:**
```bash
# List all views
python scripts/deploy_views.py --list

# Generate combined SQL script
python scripts/deploy_views.py --generate

# Deploy to Supabase
python scripts/deploy_views.py

# Check schema drift
python scripts/sync_views_to_schema.py
```
