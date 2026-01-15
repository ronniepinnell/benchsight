# Data Sources Documentation

**Complete documentation of where each page gets its data**

Last Updated: 2026-01-15

---

## 📊 Page-by-Page Data Sources

### Player Pages

#### `/players` - Player Rankings
**Data Sources:**
- `v_rankings_players_current` - Current season player rankings
- **Columns Used**: `player_id`, `player_name`, `team_name`, `points_rank`, `games_played`, `goals`, `assists`, `points`, `points_per_game`, `pim`
- **Aggregation**: None (direct from view)
- **Filters**: Top 50 players by default

#### `/players/[playerId]` - Player Profile
**Data Sources:**
- `dim_player` - Player basic info (via `getPlayerById`)
- `fact_player_season_stats_basic` - Season stats
- `fact_player_game_stats` - Game-by-game stats
- `fact_player_qoc_summary` - Quality of Competition metrics
- **Advanced Stats Sources**:
  - `fact_player_game_stats` - Possession (CF, CA, FF, FA, xG)
  - `fact_player_game_stats` - Zone stats (zone_entries, zone_exits)
  - `fact_player_game_stats` - WAR/GAR (war, gar, game_score)
  - `fact_player_game_stats` - Physical (hits, blocks, takeaways, bad_giveaways)
  - `fact_player_game_stats` - Shooting (shots, sog, goals)
  - `fact_player_game_stats` - Per-60 rates
  - `fact_player_game_stats` - Faceoffs (fo_wins, fo_losses, fo_pct)
  - `fact_player_game_stats` - Passing (primary_assists, secondary_assists)
  - `fact_player_game_stats` - Situational (5v5, PP, PK stats)
  - `fact_player_game_stats` - Micro stats (dekes, drives, forechecks, etc.)
- **Aggregation**: In-memory aggregation from game-level to season-level
- **Filters**: By `season_id`, `game_type`, filtered by `game_id` from `dim_schedule`

#### `/players/matchups` - Player Matchups
**Data Sources:**
- `dim_player` - Player info (via `getPlayerById`)
- `fact_player_game_stats` - Game stats for both players
- **Logic**: Find common games, aggregate stats for those games only
- **Columns Used**: `game_id`, `player_id`, `goals`, `assists`, `points`, `shots`, `toi_seconds`

---

### Goalie Pages

#### `/goalies` - Goalie Leaderboards
**Data Sources:**
- `v_leaderboard_goalie_gaa` - GAA leaders (via `getGoalieGAALeaders`)
- `v_leaderboard_goalie_wins` - Wins leaders (via `getGoalieWinsLeaders`)
- `v_rankings_goalies_current` - Save % leaders
- **Columns Used**: `player_id`, `player_name`, `team_name`, `games_played`, `gaa`, `save_pct`, `wins`, `losses`, `saves`, `shots_against`

#### `/goalies/[goalieId]` - Goalie Profile
**Data Sources:**
- `dim_player` - Goalie basic info (via `getPlayerById`)
- `fact_goalie_season_stats_basic` - Season stats
- `fact_goalie_game_stats` - Game-by-game stats
- `fact_goalie_game_stats` - Advanced metrics (GSAx, WAR, GAR, HD Save %, Quality Starts)
- `fact_saves` - Save-by-save data (Saves tab)
- **Aggregation**: Rolling averages calculated in-memory from game stats
- **Trends**: Calculated from `fact_goalie_game_stats` with 5-game and 10-game rolling windows

---

### Team Pages

#### `/teams` - Team Directory
**Data Sources:**
- `fact_team_season_stats_basic` - Team season stats
- `dim_team` - Team info
- **Columns Used**: `team_id`, `team_name`, `wins`, `losses`, `points`, `goals_for`, `goals_against`

#### `/team/[teamName]` - Team Profile

**Overview Tab:**
- `fact_team_season_stats_basic` - Basic season stats
- `fact_team_game_stats` - Advanced team stats
- `dim_schedule` - Recent games
- `fact_player_season_stats_basic` - Roster stats
- `fact_goalie_season_stats_basic` - Goalie stats
- `v_rankings_players_current` - Current roster (if current season)

**Roster Tab:**
- Same as Overview tab roster section
- **Data Source**: `fact_player_season_stats_basic` or `v_rankings_players_current`
- **Advanced Stats**: `fact_player_game_stats` aggregated by player

**Lines Tab:**
- `fact_line_combos` - Line combination data
- **Columns Used**: `forward_combo` (comma-separated player IDs), `toi_together`, `goals_for`, `goals_against`, `corsi_for`, `corsi_against`
- **Filtering**: By `home_team_id`/`away_team_id` and `venue`
- **Aggregation**: Grouped by `forward_combo`, aggregated TOI, goals, Corsi
- **Player Names**: Looked up from `dim_player` using parsed player IDs

**Analytics Tab:**
- `fact_team_zone_time` - Zone time data
- **Columns Used**: `offensive_zone_events`, `neutral_zone_events`, `defensive_zone_events`
- **Filtering**: By `game_id` from `dim_schedule` filtered by team and season
- **Aggregation**: Sum of zone events, calculate percentages
- `fact_wowy` - WOWY (With Or Without You) data
- **Columns Used**: `player_1_id`, `player_2_id`, `player_1_name`, `player_2_name`, `toi_together`, `cf_pct_together`, `cf_pct_apart`, `cf_pct_delta`
- **Filtering**: By `game_id` and `home_team_id`/`away_team_id`

**Matchups Tab:**
- `dim_schedule` - All games for team in season
- **Columns Used**: `home_team_id`, `away_team_id`, `home_total_goals`, `away_total_goals`, `date`
- **Aggregation**: Group by opponent, calculate W-L-T record and goal differential
- **Team Info**: `dim_team` for opponent logos

---

### Game Pages

#### `/games` - Game List
**Data Sources:**
- `dim_schedule` - Game schedule and results
- `fact_game_status` - Official scores
- **Columns Used**: `game_id`, `date`, `home_team_name`, `away_team_name`, `home_total_goals`, `away_total_goals`
- **Filtering**: By `season_id`, `game_type`, team (via `home_team_id`/`away_team_id`)

#### `/games/[gameId]` - Game Detail
**Data Sources:**
- `dim_schedule` - Game basic info
- `fact_player_game_stats` - Player game stats (via `getGameRoster`)
- `fact_goalie_game_stats` - Goalie stats (via `getGameGoalieStats`)
- `fact_events` - Game events and highlights
- `fact_shot_xy` - Shot locations (via `getGameShots`)
- `fact_shifts` - Shift data
- **Columns Used**: 
  - Shifts: `player_id`, `period`, `shift_start_total_seconds`, `shift_end_total_seconds`, `shift_duration`
  - Events: `event_type`, `is_goal`, `is_highlight`, `time_start_total_seconds`
  - Shots: `x_coord`, `y_coord`, `is_goal`, `xg`, `danger_zone`

---

### Analytics Pages

#### `/analytics/overview` - Analytics Hub
**Data Sources:**
- `v_rankings_players_current` - Top players
- `v_leaderboard_goalie_gaa` - Top goalies
- `dim_schedule` - Recent games
- **Aggregation**: Top 5-10 by various metrics

#### `/analytics/rushes` - Rush Analysis
**Data Sources:**
- `fact_player_game_stats` - Rush metrics
- **Columns Used**: `rush_shots`, `rush_goals`, `rush_assists`, `rush_points`, `rush_xg`, `breakaway_goals`, `odd_man_rushes`, `rush_involvement`, `rush_off_success`, `rush_off_shot_generated`, `rush_off_goal_generated`
- **Aggregation**: Sum by player, calculate per-game rates and success percentages

#### `/analytics/faceoffs` - Faceoff Analysis
**Data Sources:**
- `fact_player_game_stats` - Faceoff metrics
- **Columns Used**: `fo_wins`, `fo_losses`, `fo_total`, `fo_pct`
- **Aggregation**: Sum by player, calculate win percentages

#### `/analytics/lines` - Line Combinations
**Data Sources:**
- `fact_line_combos` - Line combination data
- **Columns Used**: `forward_combo`, `defense_combo`, `toi_together`, `goals_for`, `goals_against`, `corsi_for`, `corsi_against`, `xg_for`, `xg_against`
- **Aggregation**: Group by forward combo, aggregate TOI, goals, Corsi, xG
- **Player Names**: `dim_player` lookup using parsed `forward_combo` player IDs
- **Team Logos**: `dim_team` lookup using `team_id`

#### `/analytics/shot-chains` - Shot Chains
**Data Sources:**
- `fact_events` - Event data
- **Columns Used**: `event_type` (filtered to 'Shot', 'Goal'), `game_id`, `time_start_total_seconds`, `is_goal`
- **Aggregation**: Group by game, count shots and goals
- **Note**: Currently shows summary stats, full chain visualization pending

---

### Comparison Pages

#### `/players/compare` - Player Comparison
**Data Sources:**
- `dim_player` - Player info (via `getPlayerById`)
- `v_rankings_players_current` - Current stats
- `fact_player_season_stats_basic` - Season stats
- **Aggregation**: Direct from views/tables

#### `/goalies/compare` - Goalie Comparison
**Data Sources:**
- `dim_player` - Goalie info (via `getPlayerById`)
- `v_rankings_goalies_current` - Current stats
- `fact_goalie_season_stats_basic` - Season stats
- `fact_goalie_game_stats` - Game stats for career summary
- **Aggregation**: Direct from views/tables

#### `/teams/compare` - Team Comparison
**Data Sources:**
- `dim_team` - Team info (via `getTeamById`)
- `fact_team_season_stats_basic` - Team season stats
- **Columns Used**: `games_played`, `wins`, `losses`, `points`, `goals_for`, `goals_against`

---

## 🔍 Data Quality Notes

### Known Schema Mismatches Fixed

1. **fact_team_zone_time**:
   - **Expected**: `offensive_zone_time`, `neutral_zone_time`, `defensive_zone_time`
   - **Actual**: `offensive_zone_events`, `neutral_zone_events`, `defensive_zone_events`
   - **Fix**: Updated to use `*_events` columns

2. **fact_line_combos**:
   - **Expected**: `forward_1`, `forward_2`, `forward_3` columns
   - **Actual**: `forward_combo` (comma-separated string)
   - **Fix**: Parse `forward_combo` string to extract player IDs

3. **fact_wowy**:
   - **Expected**: `team_id` column
   - **Actual**: `home_team_id`, `away_team_id` columns
   - **Fix**: Filter using `.or()` with both team ID columns

### Data Availability

**Tables with Good Data:**
- ✅ `dim_player` - Complete
- ✅ `dim_team` - Complete
- ✅ `dim_schedule` - Complete
- ✅ `fact_player_game_stats` - Good coverage
- ✅ `fact_goalie_game_stats` - Good coverage
- ✅ `fact_team_season_stats_basic` - Complete

**Tables with Limited Data:**
- ⚠️ `fact_line_combos` - 199 rows (may need more games tracked)
- ⚠️ `fact_team_zone_time` - 8 rows (may need more games tracked)
- ⚠️ `fact_wowy` - Limited rows (may need more games tracked)
- ⚠️ `fact_saves` - May be empty (save-by-save tracking)
- ⚠️ `fact_player_qoc_summary` - 105 rows (may need more games tracked)

**Tables That May Not Exist:**
- ❓ `fact_team_zone_time` - Check if table exists and has correct columns
- ❓ `fact_saves` - Check if table exists

---

## 📝 Query Patterns

### Common Patterns

1. **Season Filtering**:
   ```typescript
   // Get games for season
   const { data: scheduleGames } = await supabase
     .from('dim_schedule')
     .select('game_id')
     .eq('season_id', seasonId)
   
   // Filter stats by game_id
   const gameIds = scheduleGames.map(g => g.game_id)
   const { data: stats } = await supabase
     .from('fact_player_game_stats')
     .in('game_id', gameIds)
   ```

2. **Team Filtering**:
   ```typescript
   // For tables with team_id
   .eq('team_id', teamId)
   
   // For tables with home/away team IDs
   .or(`home_team_id.eq.${teamId},away_team_id.eq.${teamId}`)
   ```

3. **Aggregation**:
   ```typescript
   // In-memory aggregation
   const totals = data.reduce((acc, stat) => ({
     goals: acc.goals + (Number(stat.goals) || 0),
     // ...
   }), { goals: 0 })
   ```

---

## 🚨 Data Gaps to Address

1. **Zone Time Data**: ✅ FIXED - `fact_team_zone_time` uses `offensive_zone_events` (not `offensive_zone_time`), filtered by `game_id` → `dim_schedule` → venue
2. **WOWY Data**: ✅ FIXED - Filtered by `home_team_id`/`away_team_id` and `game_id`
3. **Shot Chains**: ✅ IMPROVED - Now builds chains using `linked_event_key`, `sequence_index`, `play_index`
4. **Saves Data**: ✅ FIXED - Falls back to `fact_goalie_game_stats` with save type breakdown
5. **Line Combos**: ✅ FIXED - Uses `forward_combo` (comma-separated string) instead of `forward_1`, `forward_2`, `forward_3`

## ✅ Schema Fixes Applied

### fact_team_zone_time
- **Wrong**: `offensive_zone_time`, `neutral_zone_time`, `defensive_zone_time`
- **Correct**: `offensive_zone_events`, `neutral_zone_events`, `defensive_zone_events`
- **Fix**: Updated queries to use `*_events` columns

### fact_line_combos
- **Wrong**: `forward_1`, `forward_2`, `forward_3` columns
- **Correct**: `forward_combo` (comma-separated string like "P12345,P67890,P11111")
- **Fix**: Parse `forward_combo` string to extract player IDs

### fact_wowy
- **Wrong**: `team_id` column
- **Correct**: `home_team_id`, `away_team_id` columns
- **Fix**: Filter using `.or()` with both team ID columns

### fact_saves
- **Issue**: Table may not exist or may not have `goalie_id` column
- **Fix**: Fallback to `fact_goalie_game_stats` with save type breakdown (`saves_butterfly`, `saves_pad`, etc.)

---

## ✅ Data Source Verification Checklist

For each page, verify:
- [ ] Table exists in database
- [ ] Columns match expected schema
- [ ] Data is being filtered correctly
- [ ] Aggregations are correct
- [ ] Fallbacks for missing data are in place
- [ ] Error handling for empty results
