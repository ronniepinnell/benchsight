# BenchSight Table Manifest

**Clean slate: 128 tables with known sources.**

Generated: 2026-01-10 (v22.0)

---

## Source Summary

| Source | Count | Description |
|--------|-------|-------------|
| 📊 BLB | 16 | Direct from BLB_Tables.xlsx |
| 🎮 TRK | 5 | From tracking Excel files |
| 📌 STATIC | 19 | Hardcoded constants |
| 🧮 CALC | 84 | Calculated/derived |
| 🔍 QA | 4 | Validation tables |
| **TOTAL** | **128** | |

---

## 📊 BLB Tables (Source of Truth)

| Table | Rows | Cols | Notes |
|-------|------|------|-------|
| `dim_event_detail` | 49 | 11 | |
| `dim_event_detail_2` | 176 | 12 | |
| `dim_event_type` | 23 | 7 | |
| `dim_league` | 2 | 2 | |
| `dim_play_detail` | 111 | 6 | |
| `dim_play_detail_2` | 111 | 6 | |
| `dim_player` | 337 | 27 | |
| `dim_playerurlref` | 550 | 3 | |
| `dim_randomnames` | 486 | 5 | |
| `dim_schedule` | 567 | 44 | |
| `dim_season` | 9 | 8 | |
| `dim_team` | 26 | 14 | |
| `fact_draft` | 160 | 14 | |
| `fact_gameroster` | 14,595 | 24 | |
| `fact_leadership` | 28 | 9 | |
| `fact_registration` | 190 | 18 | |

## 🎮 Tracking Tables

| Table | Rows | Cols | Notes |
|-------|------|------|-------|
| `fact_event_players` | 11,155 | 156 | |
| `fact_events` | 5,823 | 130 | |
| `fact_shift_players` | 4,613 | 86 | |
| `fact_shifts` | 399 | 132 | |
| `fact_tracking` | 5,823 | 22 | |

## 📌 Static Reference Tables

| Table | Rows | Cols | Notes |
|-------|------|------|-------|
| `dim_danger_level` | 3 | 4 | |
| `dim_giveaway_type` | 16 | 3 | |
| `dim_pass_type` | 8 | 4 | |
| `dim_period` | 5 | 5 | |
| `dim_player_role` | 14 | 5 | |
| `dim_position` | 6 | 4 | |
| `dim_shift_duration` | 5 | 7 | |
| `dim_shift_start_type` | 9 | 2 | |
| `dim_shift_stop_type` | 18 | 2 | |
| `dim_shot_type` | 6 | 4 | |
| `dim_situation` | 4 | 2 | |
| `dim_stoppage_type` | 4 | 3 | |
| `dim_strength` | 18 | 7 | |
| `dim_success` | 3 | 4 | |
| `dim_takeaway_type` | 2 | 3 | |
| `dim_venue` | 2 | 4 | |
| `dim_zone` | 3 | 4 | |
| `dim_zone_entry_type` | 12 | 3 | |
| `dim_zone_exit_type` | 10 | 3 | |

## 🧮 Calculated Tables

| Table | Rows | Cols | Category |
|-------|------|------|----------|
| `dim_assist_type` | 5 | 5 | Other |
| `dim_comparison_type` | 6 | 5 | Other |
| `dim_competition_tier` | 4 | 4 | Other |
| `dim_composite_rating` | 8 | 6 | Other |
| `dim_danger_zone` | 4 | 5 | Zone Analysis |
| `dim_game_state` | 6 | 6 | Other |
| `dim_micro_stat` | 22 | 4 | Other |
| `dim_net_location` | 10 | 5 | Other |
| `dim_pass_outcome` | 4 | 4 | Other |
| `dim_rating` | 5 | 3 | Other |
| `dim_rating_matchup` | 5 | 4 | Matchups |
| `dim_rink_zone` | 201 | 13 | Zone Analysis |
| `dim_save_outcome` | 3 | 4 | Other |
| `dim_shift_quality_tier` | 5 | 6 | Shift Analysis |
| `dim_shift_slot` | 7 | 3 | Shift Analysis |
| `dim_shot_outcome` | 5 | 8 | Shot/Scoring |
| `dim_stat` | 39 | 12 | Other |
| `dim_stat_category` | 13 | 4 | Other |
| `dim_stat_type` | 8 | 6 | Other |
| `dim_terminology_mapping` | 23 | 4 | Other |
| `dim_time_bucket` | 6 | 6 | Other |
| `dim_turnover_quality` | 3 | 5 | Other |
| `dim_turnover_type` | 12 | 10 | Other |
| `dim_zone_outcome` | 6 | 5 | Zone Analysis |
| `fact_breakouts` | 476 | 125 | Other |
| `fact_event_chains` | 11,155 | 9 | Other |
| `fact_faceoffs` | 169 | 122 | Other |
| `fact_game_status` | 567 | 27 | Other |
| `fact_goalie_game_stats` | 8 | 18 | Statistics |
| `fact_h2h` | 621 | 17 | Matchups |
| `fact_head_to_head` | 621 | 18 | Other |
| `fact_high_danger_chances` | 31 | 95 | Other |
| `fact_league_leaders_snapshot` | 20 | 8 | Shot/Scoring |
| `fact_line_combos` | 199 | 16 | Other |
| `fact_matchup_performance` | 621 | 33 | Matchups |
| `fact_matchup_summary` | 621 | 16 | Matchups |
| `fact_penalties` | 20 | 95 | Other |
| `fact_period_momentum` | 12 | 7 | Other |
| `fact_player_boxscore_all` | 105 | 71 | Other |
| `fact_player_career_stats` | 67 | 16 | Statistics |
| `fact_player_event_chains` | 105 | 6 | Other |
| `fact_player_game_position` | 105 | 8 | Other |
| `fact_player_game_stats` | 105 | 70 | Statistics |
| `fact_player_matchups_xy` | 2 | 23 | Spatial |
| `fact_player_micro_stats` | 105 | 12 | Statistics |
| `fact_player_pair_stats` | 621 | 16 | Statistics |
| `fact_player_period_stats` | 315 | 9 | Statistics |
| `fact_player_position_splits` | 67 | 65 | Other |
| `fact_player_puck_proximity` | 5 | 15 | Spatial |
| `fact_player_qoc_summary` | 105 | 8 | Other |
| `fact_player_season_stats` | 67 | 65 | Statistics |
| `fact_player_stats_by_competition_tier` | 67 | 65 | Statistics |
| `fact_player_stats_long` | 1,155 | 7 | Statistics |
| `fact_player_trends` | 105 | 11 | Other |
| `fact_player_xy_long` | 22 | 13 | Spatial |
| `fact_player_xy_wide` | 5 | 37 | Spatial |
| `fact_playergames` | 14,595 | 4 | Other |
| `fact_plays` | 2,202 | 39 | Other |
| `fact_puck_xy_long` | 12 | 9 | Spatial |
| `fact_puck_xy_wide` | 2 | 33 | Spatial |
| `fact_rushes` | 421 | 125 | Other |
| `fact_saves` | 213 | 121 | Other |
| `fact_scoring_chances_detailed` | 451 | 123 | Shot/Scoring |
| `fact_season_summary` | 1 | 10 | Other |
| `fact_sequences` | 521 | 38 | Other |
| `fact_shift_quality` | 4,551 | 9 | Shift Analysis |
| `fact_shift_quality_logical` | 105 | 19 | Shift Analysis |
| `fact_shot_event` | 451 | 23 | Shot/Scoring |
| `fact_shot_players` | 1,036 | 23 | Shot/Scoring |
| `fact_shot_xy` | 0 | 12 | Shot/Scoring |
| `fact_special_teams_summary` | 5 | 6 | Other |
| `fact_suspicious_stats` | 20 | 14 | Statistics |
| `fact_team_game_stats` | 8 | 39 | Statistics |
| `fact_team_season_stats` | 5 | 9 | Statistics |
| `fact_team_standings_snapshot` | 5 | 10 | Shot/Scoring |
| `fact_team_zone_time` | 8 | 8 | Zone Analysis |
| `fact_turnovers_detailed` | 744 | 98 | Other |
| `fact_video` | 0 | 8 | Other |
| `fact_wowy` | 621 | 23 | Matchups |
| `fact_zone_entries` | 510 | 125 | Zone Analysis |
| `fact_zone_entry_summary` | 67 | 5 | Zone Analysis |
| `fact_zone_exit_summary` | 67 | 5 | Zone Analysis |
| `fact_zone_exits` | 488 | 125 | Zone Analysis |
| `lookup_player_game_rating` | 105 | 6 | Other |

## 🔍 QA Tables

| Table | Rows | Purpose |
|-------|------|---------|
| `qa_data_completeness` | 4 | Validation |
| `qa_goal_accuracy` | 4 | Validation |
| `qa_scorer_comparison` | 4 | Validation |
| `qa_suspicious_stats` | 0 | Validation |

---

## ETL Pipeline

```
run_etl.py
├── Phase 1: base_etl.py (BLB + Tracking)
├── Phase 2: dimension_tables.py
├── Phase 3: core_facts.py (Player/Team stats)
├── Phase 4: shift_analytics.py
├── Phase 5: remaining_facts.py
├── Phase 6: add_all_fkeys.py
├── Phase 7: extended_tables.py
├── Phase 8: post_etl_processor.py
├── Phase 9: build_qa_facts.py
├── Phase 10: v11_enhancements.py
└── Phase 10B: xy_table_builder.py
```
