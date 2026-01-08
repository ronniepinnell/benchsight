=== MISSING TABLES WITH COLUMNS ===

**Version:** 16.08  
**Updated:** January 8, 2026


# Missing Tables (70 tables - no ETL source code)

These tables exist in backup but are NOT created by the current ETL.

## dim_comparison_type
Rows: 6 | Columns: 5
```
comparison_type_id
comparison_type_code
comparison_type_name
description
analysis_scope
```

## dim_competition_tier
Rows: 4 | Columns: 4
```
competition_tier_id
tier_name
min_rating
max_rating
```

## dim_composite_rating
Rows: 8 | Columns: 6
```
rating_id
rating_code
rating_name
description
scale_min
scale_max
```

## dim_danger_zone
Rows: 4 | Columns: 5
```
danger_zone_id
danger_zone_code
danger_zone_name
xg_base
description
```

## dim_micro_stat
Rows: 22 | Columns: 4
```
micro_stat_id
stat_code
stat_name
category
```

## dim_net_location
Rows: 10 | Columns: 5
```
net_location_id
net_location_code
net_location_name
x_pct
y_pct
```

## dim_pass_outcome
Rows: 4 | Columns: 4
```
pass_outcome_id
pass_outcome_code
pass_outcome_name
is_successful
```

## dim_rating
Rows: 5 | Columns: 3
```
rating_id
rating_value
rating_name
```

## dim_rating_matchup
Rows: 5 | Columns: 4
```
matchup_id
matchup_name
min_diff
max_diff
```

## dim_rink_zone
Rows: 267 | Columns: 13
```
rink_zone_id
zone_code
zone_name
granularity
x_min
x_max
y_min
y_max
zone
danger
side
x_description
y_description
```

## dim_save_outcome
Rows: 3 | Columns: 4
```
save_outcome_id
save_outcome_code
save_outcome_name
causes_stoppage
```

## dim_shift_slot
Rows: 7 | Columns: 3
```
slot_id
slot_code
slot_name
```

## dim_shot_outcome
Rows: 5 | Columns: 8
```
shot_outcome_id
shot_outcome_code
shot_outcome_name
is_goal
is_save
is_block
is_miss
xg_multiplier
```

## dim_stat
Rows: 83 | Columns: 12
```
stat_id
stat_code
stat_name
category
description
formula
player_role
computable_now
benchmark_elite
nhl_avg_per_game
nhl_elite_threshold
nhl_min_threshold
```

## dim_stat_category
Rows: 13 | Columns: 4
```
stat_category_id
category_code
category_name
description
```

## dim_stat_type
Rows: 57 | Columns: 6
```
stat_id
stat_name
stat_category
stat_level
computable_now
description
```

## dim_strength
Rows: 18 | Columns: 7
```
strength_id
strength_code
strength_name
situation_type
xg_multiplier
description
avg_toi_pct
```

## dim_terminology_mapping
Rows: 84 | Columns: 4
```
dimension
old_value
new_value
match_type
```

## dim_turnover_quality
Rows: 3 | Columns: 5
```
turnover_quality_id
turnover_quality_code
turnover_quality_name
description
counts_against
```

## dim_turnover_type
Rows: 21 | Columns: 10
```
turnover_type_id
turnover_type_code
turnover_type_name
category
quality
weight
description
zone_context
zone_danger_multiplier
old_equiv
```

## dim_zone_outcome
Rows: 6 | Columns: 5
```
zone_outcome_id
zone_outcome_code
zone_outcome_name
is_controlled
zone_type
```

## fact_event_chains
Rows: 227 | Columns: 32
```
chain_id
game_id
season_id
entry_event_key
shot_event_key
entry_event_index
shot_event_index
events_to_shot
entry_type
shot_result
is_goal
team_id
team_name
home_team_id
away_team_id
home_team_name
away_team_name
event_types_chain
event_details_chain
entry_player_id
entry_player_name
shot_player_id
shot_player_name
players_touched_count
sequence_key
play_key
zone_id
zone_entry_type_id
shot_result_detail_id
time_bucket_id
strength_id
shot_type_id
```

## fact_goalie_game_stats
Rows: 8 | Columns: 23
```
goalie_game_key
game_id
season_id
player_id
player_name
team_name
saves
goals_against
shots_against
save_pct
toi_seconds
empty_net_ga
saves_rebound
saves_freeze
saves_glove
saves_blocker
saves_left_pad
saves_right_pad
rebound_control_pct
total_save_events
team_id
home_team_id
away_team_id
```

## fact_h2h
Rows: 684 | Columns: 26
```
game_id
season_id
player_1_id
player_2_id
shifts_together
home_team_id
away_team_id
toi_together
goals_for
goals_against
plus_minus
corsi_for
corsi_against
cf_pct
fenwick_for
fenwick_against
ff_pct
xgf
xga
xg_diff
shots_for
shots_against
h2h_key
player_1_name
player_2_name
ozone_pct
```

## fact_head_to_head
Rows: 572 | Columns: 17
```
game_id
season_id
player_1_id
player_1_name
player_1_rating
player_1_venue
player_2_id
player_2_name
player_2_rating
player_2_venue
shifts_against
toi_against_seconds
rating_diff
home_team_id
away_team_id
player_1_venue_id
player_2_venue_id
```

## fact_league_leaders_snapshot
Rows: 14473 | Columns: 14
```
game_id
season_id
date
player_id
player_name
team_name
gp
goals
assists
pts
pim
gpg
ppg
team_id
```

## fact_line_combos
Rows: 332 | Columns: 42
```
line_combo_key
game_id
season_id
venue
forward_combo
defense_combo
shifts
toi_together
goals_for
goals_against
plus_minus
corsi_for
corsi_against
xgf
home_team_id
away_team_id
venue_id
team_id
fenwick_for
fenwick_against
ff_pct
xg_against
xg_diff
xg_pct
zone_entries
zone_exits
controlled_entry_pct
giveaways
takeaways
turnover_diff
avg_player_rating
opp_avg_rating
rating_diff
pdo
sh_pct
sv_pct
goals_per_60
goals_against_per_60
cf_per_60
ca_per_60
team_name
ozone_pct
```

## fact_linked_events
Rows: 473 | Columns: 51
```
linked_event_key
game_id
season_id
primary_event_index
event_count
event_1_index
event_1_type
event_1_detail
event_1_player_id
event_2_index
event_2_type
event_2_detail
event_2_player_id
event_3_index
event_3_type
event_3_detail
event_3_player_id
event_4_index
event_4_type
event_4_detail
event_4_player_id
event_5_index
event_5_type
event_5_detail
event_5_player_id
event_1_key
event_2_key
event_3_key
event_4_key
event_5_key
team_venue
team_id
play_chain
event_chain_indices
venue_id
video_time_start
video_time_end
event_1_type_id
event_2_type_id
event_3_type_id
event_4_type_id
event_5_type_id
event_1_detail_id
event_2_detail_id
event_3_detail_id
event_4_detail_id
event_5_detail_id
home_team_id
away_team_id
time_bucket_id
strength_id
```

## fact_matchup_performance
Rows: 265 | Columns: 22
```
game_id
season_id
player_id
player_name
team_id
matchup_id
toi_seconds
player_rating
rating_advantage
gf_all
ga_all
pm_all
gf_adj
ga_adj
pm_adj
cf
ca
shift_count
cf_pct
expected_cf_pct
cf_pct_vs_expected
matchup_perf_key
```

## fact_matchup_summary
Rows: 684 | Columns: 34
```
game_id
season_id
player_1_id
player_2_id
shifts_together
home_team_id
away_team_id
toi_together
goals_for
goals_against
plus_minus
corsi_for
corsi_against
cf_pct
fenwick_for
fenwick_against
ff_pct
xgf
xga
xg_diff
shots_for
shots_against
h2h_key
player_1_name
player_2_name
ozone_pct
p1_shifts_without_p2
p2_shifts_without_p1
cf_pct_together
cf_pct_apart
cf_pct_delta
matchup_key
synergy_score
is_positive_synergy
```

## fact_period_momentum
Rows: 12 | Columns: 7
```
momentum_key
game_id
period
events_count
goals
shots
passes
```

## fact_player_boxscore_all
Rows: 14473 | Columns: 23
```
game_id
player_id
player_name
player_number
player_position
team_venue
team_name
team_id
opp_team_name
date
season
gp
g
a
pts
ga
pim
so
skill_rating
venue_id
position_id
season_id
opp_team_id
```

## fact_player_career_stats
Rows: 68 | Columns: 16
```
player_career_key
player_id
games_played
career_goals
career_assists
career_points
career_shots
career_sog
career_pass_attempts
career_pass_completed
career_toi_seconds
career_shifts
career_ppg
career_shooting_pct
career_pass_pct
avg_toi_per_game
```

## fact_player_event_chains
Rows: 5117 | Columns: 20
```
event_chain_key
game_id
event_key
event_type
period
home_player_count
away_player_count
home_player_1
home_player_2
home_player_3
away_player_1
away_player_2
away_player_3
home_players
away_players
running_video_time
event_running_start
season_id
time_bucket_id
strength_id
```

## fact_player_game_stats
Rows: 107 | Columns: 342
```
player_game_id
player_game_key
game_id
season_id
player_id
player_name
goals
assists
points
shots
sog
shots_blocked
shots_missed
shooting_pct
pass_attempts
pass_completed
pass_pct
fo_wins
fo_losses
fo_total
fo_pct
zone_entries
zone_exits
giveaways
takeaways
toi_seconds
toi_minutes
playing_toi_seconds
playing_toi_minutes
stoppage_seconds
shift_count
logical_shifts
avg_shift
avg_playing_shift
goals_per_60
assists_per_60
points_per_60
shots_per_60
goals_per_60_playing
assists_per_60_playing
points_per_60_playing
shots_per_60_playing
blocks
hits
puck_battles
puck_battle_wins
retrievals
corsi_for
corsi_against
fenwick_for
fenwick_against
cf_pct
ff_pct
opp_avg_rating
skill_diff
plus_ev
minus_ev
plus_minus_ev
plus_total
minus_total
plus_minus_total
plus_en_adj
minus_en_adj
plus_minus_en_adj
player_rating
home_team_id
away_team_id
chips
breakout_rush_attempts
zone_keepins
dekes_successful
breakout_clear_attempts
beat_middle
beat_wide
zone_exit_denials
breakouts
passes_missed_target
drives_corner
tip_attempts
cutbacks
drives_middle
pass_for_tip
poke_checks
stick_checks
got_beat_middle
crash_net
cycle_plays
ceded_exits
reverse_passes
deke_attempts
breakout_pass_attempts
backchecks
separate_from_puck
rebound_recoveries
block_attempts
drives_net
ceded_entries
puck_retrievals
passes_intercepted
stopped_deke
dump_and_chase
def_pass_deflected
loose_puck_wins
drives_wide
puck_recoveries
def_pass_intercepted
screens
front_of_net
secondary_assists
in_lane
quick_ups
second_touches
delays
loose_puck_losses
turnover_recoveries
dump_recoveries
pressures
contains
forechecks
give_and_go
passes_deflected
lost_puck
force_wide
man_on_man
dekes_beat_defender
box_outs
primary_assists
got_beat_wide
zone_entry_denials
surf_plays
blocked_shots_play
drives_middle_success
drives_wide_success
drives_corner_success
zone_entry_denials_success
breakouts_success
zone_entry_carry
zone_entry_pass
zone_entry_dump
zone_exit_carry
zone_exit_pass
zone_exit_dump
zone_exit_clear
zone_entries_controlled
zone_entries_uncontrolled
zone_entry_success_rate
zone_entry_control_pct
zone_exits_controlled
zone_exits_uncontrolled
zone_exit_success_rate
zone_exit_control_pct
def_shots_against
def_goals_against
def_entries_allowed
def_exits_denied
def_times_beat_deke
def_times_beat_speed
def_times_beat_total
def_takeaways
def_forced_turnovers
def_zone_clears
def_blocked_shots
def_interceptions
def_stick_checks
def_poke_checks
def_body_checks
def_coverage_assignments
def_battles_won
def_battles_lost
giveaways_bad
giveaways_neutral
giveaways_good
turnover_diff_adjusted
turnovers_oz
turnovers_nz
turnovers_dz
giveaway_rate_per_60
takeaway_rate_per_60
goals_rating_adj
assists_rating_adj
points_rating_adj
plus_minus_rating_adj
cf_pct_rating_adj
qoc_rating
qot_rating
expected_vs_rating
xg_for
xg_against
xg_diff
xg_pct
goals_above_expected
shots_high_danger
shots_medium_danger
shots_low_danger
scoring_chances
high_danger_chances
xg_per_shot
shot_quality_avg
offensive_rating
defensive_rating
hustle_rating
playmaking_rating
shooting_rating
physical_rating
impact_score
war_estimate
avg_shift_too_long
shift_length_warning
fatigue_indicator
sub_equity_score
toi_vs_team_avg
period_3_dropoff
late_game_performance
on_ice_sh_pct
on_ice_sv_pct
pdo
pdo_5v5
fo_wins_oz
fo_wins_nz
fo_wins_dz
fo_losses_oz
fo_losses_nz
fo_losses_dz
fo_pct_oz
fo_pct_nz
fo_pct_dz
zone_starts_oz_pct
zone_starts_dz_pct
game_score
game_score_per_60
game_score_rating
effective_game_rating
rating_performance_delta
playing_above_rating
playing_below_rating
playing_at_rating
performance_tier
performance_index
shots_successful
shots_unsuccessful
passes_successful
passes_unsuccessful
plays_successful
plays_unsuccessful
entries_successful
entries_unsuccessful
exits_successful
exits_unsuccessful
total_successful_plays
total_unsuccessful_plays
overall_success_rate
shot_success_rate
pass_success_rate
play_success_rate
times_pass_target
passes_received_successful
passes_received_unsuccessful
pass_reception_rate
times_target_oz
times_target_nz
times_target_dz
slot_passes_received
cross_ice_passes_received
odd_man_rushes
odd_man_rush_goals
odd_man_rush_shots
breakaway_attempts
breakaway_goals
2on1_rushes
3on2_rushes
2on0_rushes
rush_entries
rush_shots
rush_goals
counter_attacks
transition_plays
times_targeted_by_opp
times_targeted_shots
times_targeted_entries
times_targeted_passes
times_targeted_as_defender
defensive_assignments
times_attacked
times_attacked_successfully
times_attacked_unsuccessfully
defensive_success_rate
times_ep3
times_ep4
times_ep5
times_opp2
times_opp3
times_opp4
total_on_ice_events
puck_touches_estimated
involvement_rate
support_plays
goals_leading
goals_trailing
goals_tied
shots_leading
shots_trailing
shots_tied
first_period_points
second_period_points
third_period_points
first_period_shots
second_period_shots
third_period_shots
clutch_goals
empty_net_goals_for
shorthanded_goals
offensive_contribution
defensive_contribution
two_way_rating
puck_possession_index
danger_creation_rate
efficiency_score
clutch_factor
complete_player_score
avg_opp_rating_precise
gf_all_shift
ga_all_shift
pm_all_shift
gf_adj
ga_adj
pm_adj
cf_shift
ca_shift
avg_shift_quality_score
qoc_precise
expected_pm
pm_vs_expected
performance_flag
avg_rating_advantage
cf_adj
ca_adj
cf_pct_adj
gf_adj_per_60
ga_adj_per_60
pm_adj_per_60
cf_adj_per_60
ca_adj_per_60
```

## fact_player_micro_stats
Rows: 212 | Columns: 6
```
micro_stat_key
player_game_key
game_id
player_id
micro_stat
count
```

## fact_player_pair_stats
Rows: 475 | Columns: 13
```
game_id
season_id
player_1_id
player_1_name
player_1_rating
player_2_id
player_2_name
player_2_rating
shifts_together
toi_together_seconds
combined_rating
home_team_id
away_team_id
```

## fact_player_period_stats
Rows: 321 | Columns: 11
```
player_period_key
game_id
season_id
player_id
period
events
shots
goals
passes
turnovers
period_id
```

## fact_player_position_splits
Rows: 3 | Columns: 8
```
position_split_key
position
player_count
avg_goals
avg_assists
avg_points
avg_shots
avg_toi_minutes
```

## fact_player_qoc_summary
Rows: 105 | Columns: 9
```
game_id
season_id
player_id
player_name
team_id
team_name
toi_seconds
player_rating
qoc
```

## fact_player_season_stats
Rows: 68 | Columns: 93
```
player_season_key
player_id
season_id
player_name
games_played
goals
assists
points
shots
sog
shots_blocked
shots_missed
pass_attempts
pass_completed
fo_wins
fo_losses
fo_total
zone_entries
zone_exits
giveaways
takeaways
toi_seconds
playing_toi_seconds
stoppage_seconds
shift_count
logical_shifts
corsi_for
corsi_against
fenwick_for
fenwick_against
blocks
hits
puck_battles
puck_battle_wins
retrievals
plus_ev
minus_ev
plus_total
minus_total
plus_en_adj
minus_en_adj
gf_all_shift
ga_all_shift
cf_shift
ca_shift
gf_adj
ga_adj
cf_adj
ca_adj
player_rating
avg_opp_rating_precise
qoc_precise
qoc_rating
qot_rating
avg_shift_quality_score
games_over
games_under
games_expected
expected_pm
pm_vs_expected
toi_minutes
toi_per_game_seconds
toi_per_game_minutes
plus_minus_total
plus_minus_ev
plus_minus_en_adj
pm_all_shift
pm_adj
shooting_pct
pass_pct
fo_pct
cf_pct
ff_pct
cf_pct_adj
avg_rating_advantage
goals_per_game
assists_per_game
points_per_game
shots_per_game
pm_adj_per_game
goals_per_60
assists_per_60
points_per_60
shots_per_60
corsi_for_per_60
corsi_against_per_60
gf_adj_per_60
ga_adj_per_60
pm_adj_per_60
cf_adj_per_60
ca_adj_per_60
over_pct
under_pct
```

## fact_player_stats_by_competition_tier
Rows: 240 | Columns: 31
```
game_id
season_id
player_id
player_name
team_id
team_name
competition_tier_id
toi_seconds
player_rating
opp_avg_rating
gf_all
ga_all
pm_all
gf_adj
ga_adj
pm_adj
cf
ca
cf_adj
ca_adj
scf
sca
hdf
hda
fo_won
fo_lost
shift_count
toi_minutes
cf_pct
cf_pct_adj
stats_by_tier_key
```

## fact_player_stats_long
Rows: 13884 | Columns: 6
```
player_stat_key
player_game_key
game_id
player_id
stat_name
stat_value
```

## fact_player_trends
Rows: 107 | Columns: 11
```
player_trend_key
player_id
game_id
game_number
points
cumulative_points
rolling_avg_points
goals
cumulative_goals
toi_minutes
trend_direction
```

## fact_player_xy_long
Rows: 0 | Columns: 15
```
player_xy_key
game_id
event_index
event_key
player_id
player_key
team_id
team_venue
point_number
x
y
timestamp
rink_coord_id
rink_coord_id_home
rink_coord_id_away
```

## fact_player_xy_wide
Rows: 0 | Columns: 49
```
player_xy_key
game_id
event_index
event_key
player_id
player_key
team_id
team_venue
point_count
x_1
y_1
timestamp_1
rink_coord_id_1
x_2
y_2
timestamp_2
rink_coord_id_2
x_3
y_3
timestamp_3
rink_coord_id_3
x_4
y_4
timestamp_4
rink_coord_id_4
x_5
y_5
timestamp_5
rink_coord_id_5
x_6
y_6
timestamp_6
rink_coord_id_6
x_7
y_7
timestamp_7
rink_coord_id_7
x_8
y_8
timestamp_8
rink_coord_id_8
x_9
y_9
timestamp_9
rink_coord_id_9
x_10
y_10
timestamp_10
rink_coord_id_10
```

## fact_playergames
Rows: 3010 | Columns: 20
```
ID
Date
Type
Team
Opp
#
Player
Position
GP
G
A
GA
PIM
SO
Rank
ID2
ID3
Season
SeasonPlayerID
player_game_id
```

## fact_possession_time
Rows: 107 | Columns: 15
```
possession_key
game_id
season_id
player_id
venue
zone_entries
zone_exits
ozone_entries
dzone_entries
possession_events
estimated_possession_seconds
venue_id
team_id
home_team_id
away_team_id
```

## fact_puck_xy_long
Rows: 0 | Columns: 12
```
puck_xy_key
game_id
event_index
event_key
point_number
x
y
z
timestamp
rink_coord_id
rink_coord_id_home
rink_coord_id_away
```

## fact_puck_xy_wide
Rows: 0 | Columns: 55
```
puck_xy_key
game_id
event_index
event_key
point_count
x_1
y_1
z_1
timestamp_1
rink_coord_id_1
x_2
y_2
z_2
timestamp_2
rink_coord_id_2
x_3
y_3
z_3
timestamp_3
rink_coord_id_3
x_4
y_4
z_4
timestamp_4
rink_coord_id_4
x_5
y_5
z_5
timestamp_5
rink_coord_id_5
x_6
y_6
z_6
timestamp_6
rink_coord_id_6
x_7
y_7
z_7
timestamp_7
rink_coord_id_7
x_8
y_8
z_8
timestamp_8
rink_coord_id_8
x_9
y_9
z_9
timestamp_9
rink_coord_id_9
x_10
y_10
z_10
timestamp_10
rink_coord_id_10
```

## fact_rush_events
Rows: 199 | Columns: 13
```
game_id
season_id
entry_event_index
shot_event_index
events_to_shot
is_rush
rush_type
is_goal
entry_type
zone_entry_type_id
rush_type_id
home_team_id
away_team_id
```

## fact_scoring_chances
Rows: 455 | Columns: 40
```
scoring_chance_key
game_id
event_id
period
is_goal
danger_level
is_rebound
is_rush
is_odd_man
event_detail
event_detail_2
time_bucket_id
strength_id
shot_type_id
time_to_next_event
time_from_last_event
time_to_next_goal_for
time_to_next_goal_against
time_from_last_goal_for
time_from_last_goal_against
time_to_next_stoppage
time_from_last_stoppage
event_player_1_toi
event_player_2_toi
event_player_3_toi
event_player_4_toi
event_player_5_toi
event_player_6_toi
opp_player_1_toi
opp_player_2_toi
opp_player_3_toi
opp_player_4_toi
opp_player_5_toi
opp_player_6_toi
team_on_ice_toi_avg
team_on_ice_toi_min
team_on_ice_toi_max
opp_on_ice_toi_avg
opp_on_ice_toi_min
opp_on_ice_toi_max
```

## fact_shift_quality
Rows: 4559 | Columns: 10
```
shift_quality_key
game_id
player_id
shift_index
shift_duration
shift_quality
quality_score
period
strength
situation
```

## fact_shift_quality_logical
Rows: 105 | Columns: 25
```
game_id
season_id
player_id
player_name
team_id
team_name
logical_shifts
toi_seconds
player_rating
avg_opp_rating
gf_all
ga_all
pm_all
gf_adj
ga_adj
pm_adj
cf
ca
avg_quality_score
toi_minutes
cf_pct
qoc
expected_pm
pm_vs_expected
performance
```

## fact_shift_players
Rows: 4559 | Columns: 32
```
shift_player_key
shift_key
game_id
season_id
shift_index
player_id
player_name
player_number
venue
slot
position
team_name
team_id
period
shift_duration
player_rating
opp_avg_rating
rating_advantage
gf_all
ga_all
pm_all
gf_adj
ga_adj
pm_adj
cf
ca
cf_pct
cf_adj
ca_adj
logical_shift_number
cumulative_duration
shift_duration_id
```

## fact_shot_danger
Rows: 435 | Columns: 11
```
shot_danger_key
game_id
season_id
event_index
danger_zone
xg
shot_distance
shot_angle
is_rebound
is_rush
is_one_timer
```

## fact_shot_xy
Rows: 0 | Columns: 28
```
shot_xy_key
game_id
event_index
event_key
player_id
player_key
team_id
team_venue
period
period_id
shot_x
shot_y
shot_rink_coord_id
shot_rink_coord_id_home
shot_rink_coord_id_away
shot_distance
shot_angle
target_x
target_y
net_location_id
shot_type
shot_result
is_goal
is_on_net
strength_id
goalie_player_id
xg
running_video_time
```

## fact_special_teams_summary
Rows: 5 | Columns: 9
```
special_teams_key
team_id
games_played
total_corsi_for
total_corsi_against
total_cf_pct
total_xg_for
total_xg_against
total_xg_diff
```

## fact_suspicious_stats
Rows: 18 | Columns: 14
```
game_id
player_id
player_name
position
stat_name
stat_value
threshold
threshold_direction
flag_type
severity
category
note
resolved
created_at
```

## fact_team_game_stats
Rows: 8 | Columns: 72
```
team_game_key
game_id
season_id
venue
goals
shots
fo_wins
giveaways
takeaways
zone_entries
zone_exits
pass_attempts
pass_completed
fo_losses
sog
fo_total
fo_pct
pass_pct
shooting_pct
venue_id
home_team_id
away_team_id
team_id
total_shots
total_sog
total_passes
total_pass_completed
team_pass_pct
total_zone_entries
total_zone_exits
controlled_entries
controlled_exits
entry_control_pct
total_giveaways
total_takeaways
turnover_diff
total_blocks
total_hits
total_fo_wins
total_fo_losses
corsi_for
corsi_against
cf_pct
xg_for
xg_against
xg_diff
avg_player_rating
total_dekes
total_screens
offensive_rating_avg
defensive_rating_avg
hustle_rating_avg
team_name
is_home
opponent_team_id
team_avg_rating
opponent_avg_rating
gf_adj
goals_against_raw
ga_adj
goal_diff_raw
goal_diff_adj
cf_adj
ca_adj
cf_pct_adj
rating_advantage
expected_goal_diff
goal_diff_vs_expected
performance_flag
win
loss
tie
```

## fact_team_season_stats
Rows: 5 | Columns: 9
```
team_season_key
team_id
games_played
season_goals
season_shots
season_sog
avg_goals_per_game
avg_shots_per_game
avg_sog_per_game
```

## fact_team_standings_snapshot
Rows: 1124 | Columns: 15
```
game_id
season_id
date
team_name
games_played
wins
losses
ties
points
goals_for
goals_against
goal_diff
gaa
gpg
team_id
```

## fact_team_zone_time
Rows: 8 | Columns: 19
```
zone_time_key
game_id
season_id
venue
ozone_events
dzone_events
nzone_events
total_events
ozone_pct
dzone_pct
nzone_pct
venue_id
home_team_id
away_team_id
team_id
oz_dominance
dz_pressure
territorial_index
team_name
```

## fact_video
Rows: 10 | Columns: 16
```
video_key
game_id
season_id
Index
Key
Game_ID
Video_Type
Video_Category
Url_1
Url_2
Url_3
Url_4
Video_ID
Extension
Embed_Url
Description
```

## fact_wowy
Rows: 641 | Columns: 35
```
game_id
season_id
player_1_id
player_2_id
venue
shifts_together
p1_shifts_without_p2
p2_shifts_without_p1
p1_logical_shifts
p2_logical_shifts
venue_id
home_team_id
away_team_id
toi_together
toi_apart
gf_pct_together
gf_pct_apart
gf_pct_delta
cf_pct_together
cf_pct_apart
cf_pct_delta
xgf_pct_together
xgf_pct_apart
xgf_pct_delta
relative_corsi
relative_fenwick
wowy_key
player_1_name
player_2_name
goals_for
goals_against
corsi_for
corsi_against
ozone_pct
xgf
```

## fact_zone_entry_summary
Rows: 68 | Columns: 5
```
zone_entry_key
player_id
games
total_entries
entries_per_game
```

## fact_zone_exit_summary
Rows: 68 | Columns: 5
```
zone_exit_key
player_id
games
total_exits
exits_per_game
```

## lookup_player_game_rating
Rows: 14471 | Columns: 3
```
game_id
player_id
skill_rating
```

## qa_scorer_comparison
Rows: 25 | Columns: 12
```
qa_key
game_id
player_name
team
norad_goals
norad_assists
events_goals
events_assists
goals_match
assists_match
source
check_date
```

## qa_suspicious_stats
Rows: 15 | Columns: 12
```
timestamp
game_id
season_id
player_id
player_name
category
stat
value
expected
severity
note
resolved
```

