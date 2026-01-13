# Supabase Tables Inventory

## ✅ Complete Database Discovery

**Total Tables Found: 137**

The database explorer discovered all tables by:
1. Parsing SQL files in the `sql/` directory
2. Testing each table name against the live Supabase database
3. Verifying accessibility and row counts

## Table Breakdown

### Dimension Tables (41 tables)
Reference/lookup tables for the dimensional model:

- `dim_comparison_type` (6 rows)
- `dim_composite_rating` (8 rows)
- `dim_danger_zone` (4 rows)
- `dim_event_detail` (55 rows)
- `dim_event_detail_2` (176 rows)
- `dim_event_type` (23 rows)
- `dim_giveaway_type` (13 rows)
- `dim_league` (2 rows)
- `dim_micro_stat` (22 rows)
- `dim_net_location` (10 rows)
- `dim_pass_type` (8 rows)
- `dim_period` (5 rows)
- `dim_play_detail` (111 rows)
- `dim_play_detail_2` (111 rows)
- `dim_player` (337 rows)
- `dim_player_role` (14 rows)
- `dim_playerurlref` (550 rows)
- `dim_position` (6 rows)
- `dim_randomnames` (486 rows)
- `dim_schedule` (572 rows)
- `dim_season` (9 rows)
- `dim_shift_slot` (7 rows)
- `dim_shift_start_type` (9 rows)
- `dim_shift_stop_type` (18 rows)
- `dim_shot_type` (6 rows)
- `dim_situation` (4 rows)
- `dim_stat` (39 rows)
- `dim_stat_category` (13 rows)
- `dim_stat_type` (8 rows)
- `dim_stoppage_type` (4 rows)
- `dim_strength` (18 rows)
- `dim_success` (3 rows)
- `dim_takeaway_type` (8 rows)
- `dim_team` (17 rows)
- `dim_terminology_mapping` (23 rows)
- `dim_turnover_quality` (3 rows)
- `dim_turnover_type` (12 rows)
- `dim_venue` (2 rows)
- `dim_zone` (3 rows)
- `dim_zone_entry_type` (13 rows)
- `dim_zone_exit_type` (12 rows)

### Fact Tables (43 tables)
Transactional and measurement tables:

- `fact_cycle_events` (39 rows)
- `fact_draft` (160 rows)
- `fact_event_chains` (11,155 rows)
- `fact_events` (5,823 rows)
- `fact_game_status` (572 rows)
- `fact_gameroster` (14,724 rows)
- `fact_goalie_game_stats` (8 rows)
- `fact_h2h` (621 rows)
- `fact_head_to_head` (621 rows)
- `fact_leadership` (28 rows)
- `fact_line_combos` (199 rows)
- `fact_linked_events` (5,823 rows)
- `fact_matchup_summary` (621 rows)
- `fact_player_boxscore_all` (99 rows)
- `fact_player_event_chains` (107 rows)
- `fact_player_game_position` (107 rows)
- `fact_player_game_stats` (99 rows)
- `fact_player_micro_stats` (107 rows)
- `fact_player_pair_stats` (621 rows)
- `fact_player_period_stats` (321 rows)
- `fact_player_stats_long` (1,089 rows)
- `fact_player_xy_long` (22 rows)
- `fact_player_xy_wide` (5 rows)
- `fact_playergames` (14,724 rows)
- `fact_plays` (2,202 rows)
- `fact_possession_time` (107 rows)
- `fact_puck_xy_long` (12 rows)
- `fact_puck_xy_wide` (2 rows)
- `fact_registration` (190 rows)
- `fact_rush_events` (206 rows)
- `fact_scoring_chances` (451 rows)
- `fact_sequences` (521 rows)
- `fact_shift_players` (4,613 rows)
- `fact_shift_quality` (4,609 rows)
- `fact_shift_quality_logical` (107 rows)
- `fact_shifts` (399 rows)
- `fact_shot_danger` (451 rows)
- `fact_shot_xy` (0 rows)
- `fact_suspicious_stats` (11 rows)
- `fact_team_game_stats` (8 rows)
- `fact_team_zone_time` (8 rows)
- `fact_video` (0 rows)
- `fact_wowy` (621 rows)

### Views (53 tables)
Pre-aggregated views for dashboard and reporting:

- `v_compare_goalies` (195 rows)
- `v_compare_goalies_advanced` (10 rows)
- `v_compare_player_vs_league` (1,387 rows)
- `v_compare_players` (1,972 rows)
- `v_compare_teammates` (21,263 rows)
- `v_compare_teams` (111 rows)
- `v_detail_game_roster` (14,724 rows)
- `v_detail_goalie_game_log` (8 rows)
- `v_detail_goalie_periods` (8 rows)
- `v_detail_goalie_pressure` (8 rows)
- `v_detail_goalie_shot_context` (8 rows)
- `v_detail_player_game_log` (99 rows)
- `v_detail_player_periods` (99 rows)
- `v_detail_player_vs_opponent` (99 rows)
- `v_detail_team_game_log` (8 rows)
- `v_leaderboard_assists` (750 rows)
- `v_leaderboard_career_points` (295 rows)
- `v_leaderboard_goalie_gaa` (60 rows)
- `v_leaderboard_goalie_record` (79 rows)
- `v_leaderboard_goalie_wins` (79 rows)
- `v_leaderboard_goalie_wins_by_game_type` (195 rows)
- `v_leaderboard_goals` (750 rows)
- `v_leaderboard_pim` (750 rows)
- `v_leaderboard_points` (750 rows)
- `v_leaderboard_points_by_game_type` (1,972 rows)
- `v_leaderboard_ppg` (667 rows)
- `v_rankings_by_position` (1,972 rows)
- `v_rankings_career` (261 rows)
- `v_rankings_goalies_advanced` (10 rows)
- `v_rankings_goalies_career` (27 rows)
- `v_rankings_goalies_current` (32 rows)
- `v_rankings_players_current` (344 rows)
- `v_recent_games` (20 rows)
- `v_recent_goalie_games` (8 rows)
- `v_recent_high_scoring` (20 rows)
- `v_recent_hot_players` (10 rows)
- `v_recent_player_games` (99 rows)
- `v_recent_team_form` (13 rows)
- `v_standings_all_seasons` (45 rows)
- `v_standings_by_game_type` (123 rows)
- `v_standings_current` (10 rows)
- `v_standings_current_playoffs` (9 rows)
- `v_standings_current_regular` (10 rows)
- `v_standings_h2h` (97 rows)
- `v_standings_team_history` (13 rows)
- `v_summary_by_position` (13 rows)
- `v_summary_game` (572 rows)
- `v_summary_goalie_career` (33 rows)
- `v_summary_league` (6 rows)
- `v_summary_player_career` (295 rows)
- `v_summary_team_season` (111 rows)
- `v_tracking_event_summary` (71 rows)

### QA Tables (1 table)
Data quality tables:

- `qa_suspicious_stats` (0 rows)

## Key Statistics

- **Total Tables**: 137
- **Dimension Tables**: 41
- **Fact Tables**: 43
- **Views**: 53
- **QA Tables**: 1

## Largest Tables by Row Count

1. `v_compare_teammates` - 21,263 rows
2. `fact_gameroster` - 14,724 rows
3. `fact_playergames` - 14,724 rows
4. `v_detail_game_roster` - 14,724 rows
5. `fact_event_chains` - 11,155 rows
6. `v_compare_players` - 1,972 rows
7. `v_leaderboard_points_by_game_type` - 1,972 rows
8. `v_rankings_by_position` - 1,972 rows
9. `fact_player_stats_long` - 1,089 rows
10. `v_compare_player_vs_league` - 1,387 rows

## How to Explore

Run the database explorer script:

```bash
python3 scripts/explore_supabase.py
```

This will:
- Discover all tables from SQL files
- Test each table against the live database
- Show row counts and sample data
- Group tables by type (dim/fact/view)

## Dashboard Access

All 137 tables are accessible to dashboard developers via:

```typescript
import { createClient } from '@/lib/supabase/server'

const supabase = await createClient()
const { data } = await supabase.from('table_name').select('*')
```

Just ensure `.env.local` is configured with Supabase credentials.
