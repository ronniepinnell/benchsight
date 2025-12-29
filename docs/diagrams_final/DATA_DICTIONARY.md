# BenchSight Data Dictionary
## fact_player_game_stats - 317 Columns

Generated: December 29, 2024

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Columns | 317 |
| Total Rows | 107 |
| Populated Numeric | 263 |
| Zero Columns | 48 |

---

## Column Reference


### ⏱️ Time on Ice

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `toi_seconds` | float64 | 105/107 | ✅ |
| `toi_minutes` | float64 | 105/107 | ✅ |
| `playing_toi_seconds` | float64 | 105/107 | ✅ |
| `playing_toi_minutes` | float64 | 105/107 | ✅ |
| `shift_count` | int64 | 105/107 | ✅ |
| `logical_shifts` | int64 | 105/107 | ✅ |
| `avg_shift` | float64 | 105/107 | ✅ |
| `avg_playing_shift` | float64 | 105/107 | ✅ |
| `avg_shift_too_long` | float64 | 102/107 | ✅ |
| `shift_length_warning` | float64 | 102/107 | ✅ |
| `toi_vs_team_avg` | float64 | 105/107 | ✅ |

### ⚽ Expected Goals (xG)

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `xg_for` | float64 | 76/107 | ✅ |
| `xg_against` | float64 | 105/107 | ✅ |
| `xg_diff` | float64 | 105/107 | ✅ |
| `xg_pct` | float64 | 76/107 | ✅ |
| `xg_per_shot` | float64 | 76/107 | ✅ |

### ➕ Plus/Minus

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `plus_ev` | int64 | 55/107 | ✅ |
| `minus_ev` | int64 | 59/107 | ✅ |
| `plus_minus_ev` | int64 | 57/107 | ✅ |
| `plus_total` | int64 | 59/107 | ✅ |
| `minus_total` | int64 | 62/107 | ✅ |
| `plus_minus_total` | int64 | 65/107 | ✅ |
| `plus_en_adj` | int64 | 55/107 | ✅ |
| `minus_en_adj` | int64 | 59/107 | ✅ |
| `plus_minus_en_adj` | int64 | 57/107 | ✅ |

### 🎯 Passing

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `pass_attempts` | int64 | 103/107 | ✅ |
| `pass_completed` | int64 | 99/107 | ✅ |
| `pass_pct` | float64 | 99/107 | ✅ |
| `passes_missed_target` | int64 | 8/107 | ✅ |
| `pass_for_tip` | int64 | 4/107 | ✅ |
| `reverse_passes` | int64 | 7/107 | ✅ |
| `breakout_pass_attempts` | int64 | 13/107 | ✅ |
| `passes_intercepted` | int64 | 9/107 | ✅ |
| `def_pass_deflected` | int64 | 2/107 | ✅ |
| `def_pass_intercepted` | int64 | 7/107 | ✅ |
| `passes_deflected` | int64 | 14/107 | ✅ |
| `zone_entry_pass` | float64 | 99/107 | ✅ |
| `zone_exit_pass` | float64 | 62/107 | ✅ |
| `passes_successful` | float64 | 27/107 | ✅ |
| `passes_unsuccessful` | float64 | 27/107 | ✅ |
| `pass_success_rate` | float64 | 27/107 | ✅ |
| `times_pass_target` | float64 | 98/107 | ✅ |
| `passes_received_successful` | float64 | 25/107 | ✅ |
| `passes_received_unsuccessful` | float64 | 21/107 | ✅ |
| `pass_reception_rate` | float64 | 25/107 | ✅ |
| `slot_passes_received` | float64 | 0/107 | ⚠️ |
| `cross_ice_passes_received` | float64 | 0/107 | ⚠️ |
| `times_targeted_passes` | float64 | 100/107 | ✅ |

### 🎯 Shot Danger

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `shots_high_danger` | float64 | 93/107 | ✅ |
| `shots_medium_danger` | float64 | 64/107 | ✅ |
| `shots_low_danger` | float64 | 81/107 | ✅ |
| `scoring_chances` | float64 | 93/107 | ✅ |
| `high_danger_chances` | float64 | 93/107 | ✅ |
| `danger_creation_rate` | float64 | 93/107 | ✅ |

### 🏒 Faceoffs

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `fo_wins` | int64 | 19/107 | ✅ |
| `fo_losses` | int64 | 21/107 | ✅ |
| `fo_total` | int64 | 21/107 | ✅ |
| `fo_pct` | float64 | 19/107 | ✅ |
| `fo_wins_oz` | float64 | 18/107 | ✅ |
| `fo_wins_nz` | float64 | 18/107 | ✅ |
| `fo_wins_dz` | float64 | 19/107 | ✅ |
| `fo_losses_oz` | float64 | 17/107 | ✅ |
| `fo_losses_nz` | float64 | 19/107 | ✅ |
| `fo_losses_dz` | float64 | 21/107 | ✅ |
| `fo_pct_oz` | float64 | 18/107 | ✅ |
| `fo_pct_nz` | float64 | 18/107 | ✅ |
| `fo_pct_dz` | float64 | 19/107 | ✅ |

### 💨 Rush/Transition

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `breakout_rush_attempts` | int64 | 3/107 | ✅ |
| `odd_man_rushes` | int64 | 3/107 | ✅ |
| `odd_man_rush_goals` | int64 | 0/107 | ⚠️ |
| `odd_man_rush_shots` | int64 | 3/107 | ✅ |
| `breakaway_attempts` | int64 | 25/107 | ✅ |
| `breakaway_goals` | int64 | 2/107 | ✅ |
| `2on1_rushes` | int64 | 0/107 | ⚠️ |
| `3on2_rushes` | int64 | 0/107 | ⚠️ |
| `2on0_rushes` | int64 | 0/107 | ⚠️ |
| `rush_entries` | int64 | 74/107 | ✅ |
| `rush_shots` | int64 | 93/107 | ✅ |
| `rush_goals` | int64 | 0/107 | ⚠️ |

### 📈 Performance Metrics

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `opp_avg_rating` | float64 | 105/107 | ✅ |
| `player_rating` | float64 | 107/107 | ✅ |
| `goals_rating_adj` | float64 | 14/107 | ✅ |
| `assists_rating_adj` | float64 | 8/107 | ✅ |
| `points_rating_adj` | float64 | 20/107 | ✅ |
| `plus_minus_rating_adj` | float64 | 57/107 | ✅ |
| `cf_pct_rating_adj` | float64 | 0/107 | ⚠️ |
| `qoc_rating` | float64 | 105/107 | ✅ |
| `qot_rating` | float64 | 0/107 | ⚠️ |
| `expected_vs_rating` | float64 | 100/107 | ✅ |
| `offensive_rating` | float64 | 79/107 | ✅ |
| `defensive_rating` | float64 | 80/107 | ✅ |
| `hustle_rating` | float64 | 17/107 | ✅ |
| `playmaking_rating` | float64 | 99/107 | ✅ |
| `shooting_rating` | float64 | 76/107 | ✅ |
| `physical_rating` | float64 | 27/107 | ✅ |
| `late_game_performance` | float64 | 0/107 | ⚠️ |
| `game_score` | float64 | 107/107 | ✅ |
| `game_score_per_60` | float64 | 107/107 | ✅ |
| `game_score_rating` | float64 | 107/107 | ✅ |
| `effective_game_rating` | float64 | 107/107 | ✅ |
| `rating_performance_delta` | float64 | 106/107 | ✅ |
| `playing_above_rating` | int64 | 49/107 | ✅ |
| `playing_below_rating` | int64 | 38/107 | ✅ |
| `playing_at_rating` | int64 | 20/107 | ✅ |
| `performance_tier` | object | 107/107 | ✅ |
| `performance_index` | float64 | 107/107 | ✅ |
| `two_way_rating` | float64 | 93/107 | ✅ |

### 📉 Per-60 Rates

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `goals_per_60` | float64 | 14/107 | ✅ |
| `assists_per_60` | float64 | 8/107 | ✅ |
| `points_per_60` | float64 | 20/107 | ✅ |
| `shots_per_60` | float64 | 92/107 | ✅ |
| `goals_per_60_playing` | float64 | 14/107 | ✅ |
| `assists_per_60_playing` | float64 | 8/107 | ✅ |
| `points_per_60_playing` | float64 | 20/107 | ✅ |
| `shots_per_60_playing` | float64 | 92/107 | ✅ |

### 📊 Possession (Corsi/Fenwick)

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `cf_pct` | float64 | 105/107 | ✅ |
| `ff_pct` | float64 | 105/107 | ✅ |
| `skill_diff` | float64 | 98/107 | ✅ |
| `turnover_diff_adjusted` | float64 | 69/107 | ✅ |
| `period_3_dropoff` | float64 | 0/107 | ⚠️ |
| `offensive_contribution` | float64 | 84/107 | ✅ |
| `efficiency_score` | float64 | 107/107 | ✅ |

### 📋 Core Box Score

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `goals` | int64 | 14/107 | ✅ |
| `assists` | int64 | 8/107 | ✅ |
| `points` | int64 | 20/107 | ✅ |
| `sog` | int64 | 76/107 | ✅ |
| `shots_blocked` | int64 | 58/107 | ✅ |
| `shots_missed` | int64 | 57/107 | ✅ |

### 📌 Other

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `player_game_key` | object | 107/107 | ✅ |
| `player_name` | object | 107/107 | ✅ |
| `shots` | int64 | 94/107 | ✅ |
| `shooting_pct` | float64 | 14/107 | ✅ |
| `stoppage_seconds` | float64 | 78/107 | ✅ |
| `blocks` | int64 | 27/107 | ✅ |
| `hits` | int64 | 0/107 | ⚠️ |
| `puck_battles` | int64 | 20/107 | ✅ |
| `puck_battle_wins` | int64 | 10/107 | ✅ |
| `retrievals` | int64 | 50/107 | ✅ |
| `corsi_for` | int64 | 105/107 | ✅ |
| `corsi_against` | int64 | 105/107 | ✅ |
| `fenwick_for` | int64 | 105/107 | ✅ |
| `fenwick_against` | int64 | 105/107 | ✅ |
| `home_team_id` | object | 107/107 | ✅ |
| `away_team_id` | object | 107/107 | ✅ |
| `chips` | int64 | 2/107 | ✅ |
| `dekes_successful` | int64 | 12/107 | ✅ |
| `breakout_clear_attempts` | int64 | 14/107 | ✅ |
| `beat_middle` | int64 | 3/107 | ✅ |
| `beat_wide` | int64 | 3/107 | ✅ |
| `breakouts` | int64 | 14/107 | ✅ |
| `drives_corner` | int64 | 4/107 | ✅ |
| `tip_attempts` | int64 | 2/107 | ✅ |
| `cutbacks` | int64 | 7/107 | ✅ |
| `drives_middle` | int64 | 13/107 | ✅ |
| `poke_checks` | int64 | 20/107 | ✅ |
| `stick_checks` | int64 | 23/107 | ✅ |
| `got_beat_middle` | int64 | 5/107 | ✅ |
| `crash_net` | int64 | 3/107 | ✅ |
| `cycle_plays` | int64 | 2/107 | ✅ |
| `deke_attempts` | int64 | 3/107 | ✅ |
| `backchecks` | int64 | 7/107 | ✅ |
| `separate_from_puck` | int64 | 12/107 | ✅ |
| `rebound_recoveries` | int64 | 9/107 | ✅ |
| `block_attempts` | int64 | 3/107 | ✅ |
| `drives_net` | int64 | 1/107 | ✅ |
| `ceded_entries` | int64 | 1/107 | ✅ |
| `puck_retrievals` | int64 | 0/107 | ⚠️ |
| `stopped_deke` | int64 | 2/107 | ✅ |
| `dump_and_chase` | int64 | 9/107 | ✅ |
| `loose_puck_wins` | int64 | 9/107 | ✅ |
| `drives_wide` | int64 | 12/107 | ✅ |
| `puck_recoveries` | int64 | 0/107 | ⚠️ |
| `screens` | int64 | 2/107 | ✅ |
| `front_of_net` | int64 | 6/107 | ✅ |
| `secondary_assists` | int64 | 1/107 | ✅ |
| `in_lane` | int64 | 20/107 | ✅ |
| `quick_ups` | int64 | 2/107 | ✅ |
| `second_touches` | int64 | 23/107 | ✅ |
| `delays` | int64 | 12/107 | ✅ |
| `loose_puck_losses` | int64 | 8/107 | ✅ |
| `dump_recoveries` | int64 | 9/107 | ✅ |
| `pressures` | int64 | 5/107 | ✅ |
| `contains` | int64 | 2/107 | ✅ |
| `forechecks` | int64 | 1/107 | ✅ |
| `give_and_go` | int64 | 2/107 | ✅ |
| `lost_puck` | int64 | 15/107 | ✅ |
| `force_wide` | int64 | 5/107 | ✅ |
| `man_on_man` | int64 | 5/107 | ✅ |
| `dekes_beat_defender` | int64 | 11/107 | ✅ |
| `box_outs` | int64 | 2/107 | ✅ |
| `primary_assists` | int64 | 1/107 | ✅ |
| `got_beat_wide` | int64 | 3/107 | ✅ |
| `surf_plays` | int64 | 2/107 | ✅ |
| `blocked_shots_play` | int64 | 14/107 | ✅ |
| `drives_middle_success` | int64 | 10/107 | ✅ |
| `drives_wide_success` | int64 | 5/107 | ✅ |
| `drives_corner_success` | int64 | 3/107 | ✅ |
| `breakouts_success` | int64 | 13/107 | ✅ |
| `goals_above_expected` | float64 | 76/107 | ✅ |
| `shot_quality_avg` | float64 | 93/107 | ✅ |
| `impact_score` | float64 | 106/107 | ✅ |
| `war_estimate` | float64 | 92/107 | ✅ |
| `fatigue_indicator` | float64 | 0/107 | ⚠️ |
| `sub_equity_score` | float64 | 107/107 | ✅ |
| `on_ice_sh_pct` | float64 | 61/107 | ✅ |
| `on_ice_sv_pct` | float64 | 107/107 | ✅ |
| `pdo` | float64 | 107/107 | ✅ |
| `pdo_5v5` | float64 | 107/107 | ✅ |
| `shots_successful` | float64 | 27/107 | ✅ |
| `shots_unsuccessful` | float64 | 25/107 | ✅ |
| `plays_successful` | float64 | 51/107 | ✅ |
| `plays_unsuccessful` | float64 | 50/107 | ✅ |
| `entries_successful` | float64 | 26/107 | ✅ |
| `entries_unsuccessful` | float64 | 25/107 | ✅ |
| `total_successful_plays` | float64 | 52/107 | ✅ |
| `total_unsuccessful_plays` | float64 | 51/107 | ✅ |
| `overall_success_rate` | float64 | 52/107 | ✅ |
| `shot_success_rate` | float64 | 27/107 | ✅ |
| `play_success_rate` | float64 | 51/107 | ✅ |
| `times_target_oz` | float64 | 0/107 | ⚠️ |
| `times_target_nz` | float64 | 0/107 | ⚠️ |
| `times_target_dz` | float64 | 0/107 | ⚠️ |
| `counter_attacks` | int64 | 0/107 | ⚠️ |
| `transition_plays` | int64 | 43/107 | ✅ |
| `times_targeted_by_opp` | float64 | 107/107 | ✅ |
| `times_targeted_shots` | float64 | 90/107 | ✅ |
| `times_targeted_entries` | float64 | 93/107 | ✅ |
| `times_targeted_as_defender` | float64 | 107/107 | ✅ |
| `defensive_assignments` | float64 | 107/107 | ✅ |
| `times_attacked` | float64 | 27/107 | ✅ |
| `times_attacked_successfully` | float64 | 27/107 | ✅ |
| `times_attacked_unsuccessfully` | float64 | 27/107 | ✅ |
| `defensive_success_rate` | float64 | 27/107 | ✅ |
| `times_ep3` | float64 | 73/107 | ✅ |
| `times_ep4` | float64 | 19/107 | ✅ |
| `times_ep5` | float64 | 1/107 | ✅ |
| `times_opp2` | float64 | 96/107 | ✅ |
| `times_opp3` | float64 | 56/107 | ✅ |
| `times_opp4` | float64 | 10/107 | ✅ |
| `total_on_ice_events` | float64 | 107/107 | ✅ |
| `puck_touches_estimated` | float64 | 107/107 | ✅ |
| `involvement_rate` | float64 | 107/107 | ✅ |
| `support_plays` | float64 | 76/107 | ✅ |
| `goals_leading` | int64 | 0/107 | ⚠️ |
| `goals_trailing` | int64 | 0/107 | ⚠️ |
| `goals_tied` | int64 | 0/107 | ⚠️ |
| `shots_leading` | int64 | 0/107 | ⚠️ |
| `shots_trailing` | int64 | 0/107 | ⚠️ |
| `shots_tied` | int64 | 0/107 | ⚠️ |
| `first_period_points` | int64 | 5/107 | ✅ |
| `second_period_points` | int64 | 4/107 | ✅ |
| `third_period_points` | int64 | 7/107 | ✅ |
| `first_period_shots` | int64 | 66/107 | ✅ |
| `second_period_shots` | int64 | 64/107 | ✅ |
| `third_period_shots` | int64 | 71/107 | ✅ |
| `clutch_goals` | int64 | 0/107 | ⚠️ |
| `empty_net_goals_for` | int64 | 0/107 | ⚠️ |
| `shorthanded_goals` | int64 | 0/107 | ⚠️ |
| `defensive_contribution` | float64 | 75/107 | ✅ |
| `puck_possession_index` | float64 | 107/107 | ✅ |
| `clutch_factor` | float64 | 14/107 | ✅ |
| `complete_player_score` | float64 | 101/107 | ✅ |

### 🔄 Turnovers

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `giveaways` | int64 | 99/107 | ✅ |
| `takeaways` | int64 | 69/107 | ✅ |
| `turnover_recoveries` | int64 | 14/107 | ✅ |
| `def_takeaways` | int64 | 0/107 | ⚠️ |
| `def_forced_turnovers` | int64 | 0/107 | ⚠️ |
| `giveaways_bad` | float64 | 62/107 | ✅ |
| `giveaways_neutral` | float64 | 93/107 | ✅ |
| `giveaways_good` | float64 | 99/107 | ✅ |
| `turnovers_oz` | float64 | 99/107 | ✅ |
| `turnovers_nz` | float64 | 93/107 | ✅ |
| `turnovers_dz` | float64 | 62/107 | ✅ |
| `giveaway_rate_per_60` | float64 | 97/107 | ✅ |
| `takeaway_rate_per_60` | float64 | 68/107 | ✅ |

### 🔑 Keys

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `game_id` | int64 | 107/107 | ✅ |
| `player_id` | object | 107/107 | ✅ |

### 🚪 Zone Transitions

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `zone_entries` | int64 | 94/107 | ✅ |
| `zone_exits` | int64 | 94/107 | ✅ |
| `zone_keepins` | int64 | 4/107 | ✅ |
| `zone_exit_denials` | int64 | 1/107 | ✅ |
| `ceded_exits` | int64 | 1/107 | ✅ |
| `zone_entry_denials` | int64 | 2/107 | ✅ |
| `zone_entry_denials_success` | int64 | 1/107 | ✅ |
| `zone_entry_carry` | float64 | 82/107 | ✅ |
| `zone_entry_dump` | float64 | 93/107 | ✅ |
| `zone_exit_carry` | float64 | 43/107 | ✅ |
| `zone_exit_dump` | float64 | 0/107 | ⚠️ |
| `zone_exit_clear` | float64 | 85/107 | ✅ |
| `zone_entries_controlled` | float64 | 99/107 | ✅ |
| `zone_entries_uncontrolled` | float64 | 93/107 | ✅ |
| `zone_entry_success_rate` | float64 | 0/107 | ⚠️ |
| `zone_entry_control_pct` | float64 | 94/107 | ✅ |
| `zone_exits_controlled` | float64 | 62/107 | ✅ |
| `zone_exits_uncontrolled` | float64 | 40/107 | ✅ |
| `zone_exit_success_rate` | float64 | 0/107 | ⚠️ |
| `zone_exit_control_pct` | float64 | 60/107 | ✅ |
| `def_exits_denied` | int64 | 0/107 | ⚠️ |
| `def_zone_clears` | int64 | 0/107 | ⚠️ |
| `zone_starts_oz_pct` | float64 | 18/107 | ✅ |
| `zone_starts_dz_pct` | float64 | 21/107 | ✅ |
| `exits_successful` | float64 | 0/107 | ⚠️ |
| `exits_unsuccessful` | float64 | 0/107 | ⚠️ |

### 🛡️ Defensive

| Column | Type | Populated | Status |
|--------|------|-----------|--------|
| `def_shots_against` | int64 | 74/107 | ✅ |
| `def_goals_against` | int64 | 7/107 | ✅ |
| `def_entries_allowed` | int64 | 96/107 | ✅ |
| `def_times_beat_deke` | int64 | 0/107 | ⚠️ |
| `def_times_beat_speed` | int64 | 0/107 | ⚠️ |
| `def_times_beat_total` | int64 | 0/107 | ⚠️ |
| `def_blocked_shots` | int64 | 0/107 | ⚠️ |
| `def_interceptions` | int64 | 0/107 | ⚠️ |
| `def_stick_checks` | int64 | 0/107 | ⚠️ |
| `def_poke_checks` | int64 | 0/107 | ⚠️ |
| `def_body_checks` | int64 | 0/107 | ⚠️ |
| `def_coverage_assignments` | int64 | 0/107 | ⚠️ |
| `def_battles_won` | int64 | 0/107 | ⚠️ |
| `def_battles_lost` | int64 | 0/107 | ⚠️ |


---

## Table Inventory (88 Tables)

### Dimension Tables (44)

| Table | Rows | Primary Key |
|-------|------|-------------|
| `dim_comparison_type` | 6 | comparison_type_id |
| `dim_composite_rating` | 8 | rating_id |
| `dim_danger_zone` | 4 | danger_zone_id |
| `dim_event_detail` | 59 | event_detail_id |
| `dim_event_detail_2` | 97 | event_detail_2_id |
| `dim_event_type` | 20 | event_type_id |
| `dim_giveaway_type` | 12 | giveaway_type_id |
| `dim_league` | 2 | league_id |
| `dim_micro_stat` | 22 | micro_stat_id |
| `dim_net_location` | 10 | net_location_id |
| `dim_pass_type` | 16 | pass_type_id |
| `dim_period` | 5 | period_id |
| `dim_play_detail` | 154 | play_detail_id |
| `dim_play_detail_2` | 62 | play_detail_2_id |
| `dim_player` | 337 | index |
| `dim_player_role` | 14 | role_id |
| `dim_playerurlref` | 548 | n_player_url |
| `dim_position` | 7 | position_id |
| `dim_randomnames` | 486 | random_full_name |
| `dim_rink_coord` | 19 | rink_coord_id |
| `dim_rinkboxcoord` | 50 | box_id |
| `dim_rinkcoordzones` | 198 | box_id |
| `dim_schedule` | 562 | game_id |
| `dim_season` | 9 | index |
| `dim_shift_slot` | 7 | slot_id |
| `dim_shift_start_type` | 9 | shift_start_type_id |
| `dim_shift_stop_type` | 28 | shift_stop_type_id |
| `dim_shot_type` | 14 | shot_type_id |
| `dim_situation` | 5 | situation_id |
| `dim_stat` | 83 | stat_id |
| `dim_stat_category` | 13 | stat_category_id |
| `dim_stat_type` | 57 | stat_id |
| `dim_stoppage_type` | 10 | stoppage_type_id |
| `dim_strength` | 18 | strength_id |
| `dim_success` | 2 | success_id |
| `dim_takeaway_type` | 10 | takeaway_type_id |
| `dim_team` | 26 | index |
| `dim_terminology_mapping` | 84 | dimension |
| `dim_turnover_quality` | 3 | turnover_quality_id |
| `dim_turnover_type` | 21 | turnover_type_id |
| `dim_venue` | 2 | venue_id |
| `dim_zone` | 3 | zone_id |
| `dim_zone_entry_type` | 11 | zone_entry_type_id |
| `dim_zone_exit_type` | 10 | zone_exit_type_id |


### Fact Tables (44)

| Table | Rows | Primary Key |
|-------|------|-------------|
| `fact_cycle_events` | 9 | game_id |
| `fact_draft` | 160 | team_id |
| `fact_event_chains` | 295 | chain_id |
| `fact_events` | 5833 | event_key |
| `fact_events_long` | 11136 | event_player_key |
| `fact_events_player` | 11635 | event_player_key |
| `fact_gameroster` | 14471 | game_id |
| `fact_goalie_game_stats` | 4 | goalie_game_key |
| `fact_h2h` | 684 | game_id |
| `fact_head_to_head` | 572 | game_id |
| `fact_leadership` | 28 | player_full_name |
| `fact_league_leaders_snapshot` | 14473 | game_id |
| `fact_line_combos` | 332 | game_id |
| `fact_linked_events` | 473 | linked_event_key |
| `fact_matchup_summary` | 684 | game_id |
| `fact_player_boxscore_all` | 14473 | game_id |
| `fact_player_event_chains` | 5831 | event_chain_key |
| `fact_player_game_stats` | 107 | player_game_key |
| `fact_player_micro_stats` | 212 | micro_stat_key |
| `fact_player_pair_stats` | 475 | game_id |
| `fact_player_period_stats` | 321 | player_period_key |
| `fact_player_stats_long` | 7026 | player_stat_key |
| `fact_player_xy_long` | 0 | player_xy_key |
| `fact_player_xy_wide` | 0 | player_xy_key |
| `fact_playergames` | 3010 | ID |
| `fact_plays` | 2714 | play_id |
| `fact_possession_time` | 107 | possession_key |
| `fact_puck_xy_long` | 0 | puck_xy_key |
| `fact_puck_xy_wide` | 0 | puck_xy_key |
| `fact_registration` | 190 | player_full_name |
| `fact_rush_events` | 199 | game_id |
| `fact_scoring_chances` | 451 | scoring_chance_key |
| `fact_sequences` | 1088 | sequence_id |
| `fact_shift_quality` | 4626 | shift_quality_key |
| `fact_shifts` | 672 | shift_key |
| `fact_shifts_long` | 4336 | shift_player_key |
| `fact_shifts_player` | 4626 | shift_player_key |
| `fact_shot_danger` | 435 | shot_danger_key |
| `fact_shot_xy` | 0 | shot_xy_key |
| `fact_team_game_stats` | 8 | team_game_key |
| `fact_team_standings_snapshot` | 1124 | game_id |
| `fact_team_zone_time` | 8 | zone_time_key |
| `fact_video` | 10 | video_key |
| `fact_wowy` | 641 | game_id |


---

## XY Coordinate Mapping

### dim_rinkcoordzones (84 zones)

Used for mapping shot XY coordinates to danger zones.

| Field | Description |
|-------|-------------|
| `box_id` | Zone identifier (OZ01, OZ17, etc.) |
| `x_min`, `x_max` | X coordinate range |
| `y_min`, `y_max` | Y coordinate range |
| `danger` | 'low', 'mid', or 'high' |
| `zone` | 'offensive', 'neutral', 'defensive' |
| `slot` | 'inside', 'outside', 'outside low' |

### Danger Zone Examples

| Zone | X Range | Y Range | Danger |
|------|---------|---------|--------|
| OZ17 (Slot) | 69-89 | -8.5 to 8.5 | **high** |
| OZ13 | 69-89 | -25.5 to -8.5 | mid |
| OZ01 | 89-100 | -42.5 to -7.5 | low |

---

## Key Relationships

```
dim_player (1) ──────< (M) fact_player_game_stats
dim_schedule (1) ────< (M) fact_events
dim_schedule (1) ────< (M) fact_player_game_stats
dim_player (1) ──────< (M) fact_h2h (as player_1)
dim_player (1) ──────< (M) fact_h2h (as player_2)
dim_rinkcoordzones (1) ──< (M) fact_shot_xy
```

---

*Generated automatically from BenchSight data*
