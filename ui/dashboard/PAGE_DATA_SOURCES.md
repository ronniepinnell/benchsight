# Page Data Sources - Complete Reference

**For QC and Data Verification**

Last Updated: 2026-01-15

---

## 📋 Quick Reference by Page

### Player Pages

#### `/players` - Player Rankings
**Primary Table**: `v_rankings_players_current`  
**Columns**: `player_id`, `player_name`, `team_name`, `points_rank`, `games_played`, `goals`, `assists`, `points`, `points_per_game`, `pim`  
**Filter**: Top 50 by default  
**Aggregation**: None (direct from view)

#### `/players/[playerId]` - Player Profile

**Overview Tab:**
- **Player Info**: `dim_player` (via `getPlayerById`)
- **Current Stats**: `v_rankings_players_current` (via `getCurrentRankings`)
- **Game Log**: `fact_player_game_stats` aggregated by game
- **Career**: `fact_player_season_stats_basic` aggregated (via `getPlayerCareerSummary`)

**Season Tab:**
- **Game Stats**: `fact_player_game_stats` filtered by `season_id` and `game_id` from `dim_schedule`
- **Game Info**: `dim_schedule` joined via `game_id`

**Career Tab:**
- **Career Summary**: `fact_player_season_stats_basic` aggregated across all seasons
- **Per-Season Stats**: `fact_player_season_stats_basic` grouped by `season_id`

**Advanced Tab:**
- **Possession**: `fact_player_game_stats` → `corsi_for`, `corsi_against`, `fenwick_for`, `fenwick_against`, `xg_for`
- **Zone Stats**: `fact_player_game_stats` → `zone_entries`, `zone_entries_successful`, `zone_exits`, `zone_exits_successful`
- **WAR/GAR**: `fact_player_game_stats` → `war`, `gar`, `game_score`, `player_rating`
- **Physical**: `fact_player_game_stats` → `hits`, `blocks`, `takeaways`, `bad_giveaways`
- **Shooting**: `fact_player_game_stats` → `shots`, `sog`, `goals`
- **Per-60**: Calculated from `fact_player_game_stats` (TOI, goals, assists, etc.)
- **Faceoffs**: `fact_player_game_stats` → `fo_wins`, `fo_losses`, `fo_pct`
- **Passing**: `fact_player_game_stats` → `primary_assists`, `secondary_assists`
- **Situational**: `fact_player_game_stats` → 5v5, PP, PK stats
- **Micro Stats**: `fact_player_game_stats` → `dekes`, `drives_total`, `forechecks`, `backchecks`, `puck_battles_total`
- **QoC**: `fact_player_qoc_summary` → `avg_opp_rating`, `avg_own_rating`, `rating_diff`

**Data Flow**: 
1. Get `game_id`s from `dim_schedule` filtered by `season_id` and `game_type`
2. Filter `fact_player_game_stats` by `player_id` and `game_id`
3. Aggregate in-memory (sum, average, calculate percentages)

---

### Goalie Pages

#### `/goalies` - Goalie Leaderboards
**Primary Tables**: 
- `v_leaderboard_goalie_gaa` (via `getGoalieGAALeaders`)
- `v_leaderboard_goalie_wins` (via `getGoalieWinsLeaders`)
- `v_rankings_goalies_current` (Save % tab)

**Columns**: `player_id`, `player_name`, `team_name`, `games_played`, `gaa`, `save_pct`, `wins`, `losses`, `saves`, `shots_against`

#### `/goalies/[goalieId]` - Goalie Profile

**Overview Tab:**
- **Player Info**: `dim_player` (via `getPlayerById`)
- **Current Stats**: `fact_goalie_season_stats_basic` or `v_rankings_goalies_current`
- **Trends**: `fact_goalie_game_stats` with rolling averages (5-game, 10-game)
- **Recent Games**: `fact_goalie_game_stats` ordered by `game_id` desc

**Season Tab:**
- **Game Stats**: `fact_goalie_game_stats` filtered by `player_id`
- **Aggregation**: Sum by game, calculate season totals

**Career Tab:**
- **Career Summary**: `fact_goalie_season_stats_basic` aggregated (via `getGoalieCareerSummary`)

**Advanced Tab:**
- **GSAx**: `fact_goalie_game_stats` → `goalie_gsaa` or `goals_saved_above_avg`
- **WAR**: `fact_goalie_game_stats` → `goalie_war`
- **GAR**: `fact_goalie_game_stats` → `goalie_gar_total`
- **HD Save %**: `fact_goalie_game_stats` → `hd_saves`, `hd_shots_against`
- **Quality Starts**: `fact_goalie_game_stats` → `quality_start`

**Saves Tab:**
- **Primary**: `fact_saves` (if exists) filtered by `goalie_id` (may not exist)
- **Fallback**: `fact_goalie_game_stats` → `saves`, `shots_against`, `hd_saves`, `saves_butterfly`, `saves_pad`, `saves_glove`, `saves_blocker`, `saves_chest`, `saves_stick`, `saves_scramble`
- **Aggregation**: Group by game, show save type breakdown

---

### Team Pages

#### `/teams` - Team Directory
**Primary Table**: `fact_team_season_stats_basic`  
**Columns**: `team_id`, `team_name`, `wins`, `losses`, `points`, `goals_for`, `goals_against`  
**Filter**: Current season, `game_type='All'`

#### `/team/[teamName]` - Team Profile

**Overview Tab:**
- **Team Info**: `dim_team` (via `getTeamByName`)
- **Standings**: `fact_team_season_stats_basic` (via `getStandings`)
- **Roster**: `fact_player_season_stats_basic` or `v_rankings_players_current` filtered by `team_id`
- **Goalies**: `fact_goalie_season_stats_basic` or `v_leaderboard_goalie_gaa` filtered by `team_id`
- **Recent Games**: `dim_schedule` filtered by team and season
- **Advanced Stats**: `fact_team_game_stats` aggregated

**Roster Tab:**
- **Same as Overview** but shows full roster table

**Lines Tab:**
- **Primary Table**: `fact_line_combos`
- **Columns**: `forward_combo` (comma-separated player IDs), `toi_together`, `goals_for`, `goals_against`, `corsi_for`, `corsi_against`
- **Filtering**: 
  1. Get `game_id`s from `dim_schedule` where team is home or away
  2. Filter `fact_line_combos` by `game_id` and `combo_type='forward'`
  3. Filter by `venue` matching team's home/away status
- **Aggregation**: Group by `forward_combo`, sum TOI/goals/Corsi
- **Player Names**: Parse `forward_combo`, lookup from `dim_player`

**Analytics Tab:**
- **Zone Time**: 
  - **Table**: `fact_team_zone_time`
  - **Columns**: `offensive_zone_events`, `neutral_zone_events`, `defensive_zone_events`
  - **Filtering**: 
    1. Get `game_id`s from `dim_schedule` filtered by team and season
    2. Filter `fact_team_zone_time` by `game_id`
    3. Filter by `venue` matching team's home/away status
  - **Aggregation**: Sum events, calculate percentages
- **WOWY**:
  - **Table**: `fact_wowy`
  - **Columns**: `player_1_id`, `player_2_id`, `player_1_name`, `player_2_name`, `toi_together`, `cf_pct_together`, `cf_pct_apart`, `cf_pct_delta`
  - **Filtering**: By `game_id` and `home_team_id`/`away_team_id`

**Matchups Tab:**
- **Primary Table**: `dim_schedule`
- **Columns**: `home_team_id`, `away_team_id`, `home_total_goals`, `away_total_goals`, `date`
- **Filtering**: By `season_id` and team (home or away)
- **Aggregation**: Group by opponent, calculate W-L-T record and goal differential

---

### Game Pages

#### `/games` - Game List
**Primary Table**: `dim_schedule`  
**Columns**: `game_id`, `date`, `home_team_name`, `away_team_name`, `home_total_goals`, `away_total_goals`  
**Filtering**: By `season_id`, `game_type`, team (via `home_team_id`/`away_team_id`)  
**Fallback**: `fact_game_status` for official scores

#### `/games/[gameId]` - Game Detail
**Primary Tables**:
- `dim_schedule` - Game basic info
- `fact_player_game_stats` - Player stats (via `getGameRoster`)
- `fact_goalie_game_stats` - Goalie stats (via `getGameGoalieStats`)
- `fact_events` - Game events
- `fact_shot_xy` - Shot locations (via `getGameShots`)
- `fact_shifts` - Shift data

**Shift Chart**:
- **Table**: `fact_shifts`
- **Columns**: `player_id`, `period`, `shift_start_total_seconds`, `shift_end_total_seconds`, `shift_duration`
- **Aggregation**: Group by period, sum TOI and count shifts

---

### Analytics Pages

#### `/analytics/rushes` - Rush Analysis
**Primary Table**: `fact_player_game_stats`  
**Columns**: `rush_shots`, `rush_goals`, `rush_assists`, `rush_points`, `rush_xg`, `breakaway_goals`, `odd_man_rushes`, `rush_involvement`, `rush_off_success`, `rush_off_shot_generated`, `rush_off_goal_generated`  
**Aggregation**: Sum by player, calculate per-game rates

#### `/analytics/faceoffs` - Faceoff Analysis
**Primary Table**: `fact_player_game_stats`  
**Columns**: `fo_wins`, `fo_losses`, `fo_total`, `fo_pct`  
**Aggregation**: Sum by player, calculate win percentages

#### `/analytics/lines` - Line Combinations
**Primary Table**: `fact_line_combos`  
**Columns**: `forward_combo` (comma-separated), `toi_together`, `goals_for`, `goals_against`, `corsi_for`, `corsi_against`  
**Aggregation**: Group by `forward_combo`, sum stats  
**Player Lookup**: Parse `forward_combo`, lookup from `dim_player`

#### `/analytics/shot-chains` - Shot Chains
**Primary Table**: `fact_events`  
**Columns**: `event_type`, `game_id`, `time_start_total_seconds`, `is_goal`, `linked_event_key`, `sequence_index`, `play_index`  
**Logic**: 
1. Get all events and shots
2. For each shot, trace back using `linked_event_key`, `sequence_index`, or `play_index`
3. Build chains of events leading to shots
4. Analyze chain patterns

---

### Comparison Pages

#### `/players/compare` - Player Comparison
**Primary Tables**: 
- `dim_player` (via `getPlayerById`)
- `v_rankings_players_current` or `fact_player_season_stats_basic`

#### `/goalies/compare` - Goalie Comparison
**Primary Tables**:
- `dim_player` (via `getPlayerById`)
- `v_rankings_goalies_current` or `fact_goalie_season_stats_basic`
- `fact_goalie_game_stats` (for career summary)

#### `/teams/compare` - Team Comparison
**Primary Tables**:
- `dim_team` (via `getTeamById`)
- `fact_team_season_stats_basic`

---

## 🔍 Data Quality Checklist

For each page, verify:
1. ✅ Table exists in database
2. ✅ Columns match expected schema
3. ✅ Data is being filtered correctly
4. ✅ Aggregations are correct
5. ✅ Fallbacks for missing data are in place
6. ✅ Error handling for empty results

---

## 📊 Known Schema Mismatches (Fixed)

1. ✅ `fact_team_zone_time`: Uses `*_events` not `*_time`
2. ✅ `fact_line_combos`: Uses `forward_combo` (string) not `forward_1`, `forward_2`, `forward_3`
3. ✅ `fact_wowy`: Uses `home_team_id`/`away_team_id` not `team_id`
4. ✅ `fact_saves`: May not exist, fallback to `fact_goalie_game_stats`

---

## 🚨 Pages That May Show "No Data"

These pages will show "No data available" if:
- **Team Lines Tab**: No `fact_line_combos` data for team/season
- **Team Analytics Tab**: No `fact_team_zone_time` or `fact_wowy` data
- **Goalie Saves Tab**: No `fact_saves` or `fact_goalie_game_stats` data
- **Shot Chains**: No `fact_events` with shot/chain data
- **Player QoC**: No `fact_player_qoc_summary` data

**All pages have proper fallbacks and error messages.**
