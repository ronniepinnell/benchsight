# BenchSight Complete Stats Reference

**All 317 player game stats with formulas, context, and benchmarks**

---

## Scoring Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `assists` | Total assists (primary + secondary) | A1 + A2 | 1+/game | 0/game |
| `assists_per_60_playing` | Assists Per 60 Playing |  |  |  |
| `assists_rating_adj` | Assists Rating Adj |  |  |  |
| `breakaway_goals` | Breakaway Goals |  |  |  |
| `clutch_goals` | Clutch Goals |  |  |  |
| `def_goals_against` | Def Goals Against |  |  |  |
| `empty_net_goals_for` | Empty Net Goals For |  |  |  |
| `first_period_points` | First Period Points |  |  |  |
| `goals` | Goals scored by player | COUNT(Goal events where event_player_1 = player) | 1+/game | 0/game |
| `goals_leading` | Goals Leading |  |  |  |
| `goals_per_60_playing` | Goals Per 60 Playing |  |  |  |
| `goals_rating_adj` | Goals Rating Adj |  |  |  |
| `goals_tied` | Goals Tied |  |  |  |
| `goals_trailing` | Goals Trailing |  |  |  |
| `odd_man_rush_goals` | Odd Man Rush Goals |  |  |  |
| `points` | Total offensive production | goals + assists | 2+/game | 0/game |
| `points_per_60_playing` | Points Per 60 Playing |  |  |  |
| `points_rating_adj` | Points Rating Adj |  |  |  |
| `primary_assists` | Last pass before goal | COUNT where event_player_2 | 1+/game | 0 |
| `rush_goals` | Rush Goals |  |  |  |
| `second_period_points` | Second Period Points |  |  |  |
| `secondary_assists` | Second-to-last pass | COUNT where event_player_3 | 0.5+/game | 0 |
| `shorthanded_goals` | Shorthanded Goals |  |  |  |
| `third_period_points` | Third Period Points |  |  |  |

## Shooting Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `def_blocked_shots` | Def Blocked Shots |  |  |  |
| `def_shots_against` | Def Shots Against |  |  |  |
| `first_period_shots` | First Period Shots |  |  |  |
| `odd_man_rush_shots` | Odd Man Rush Shots |  |  |  |
| `rush_shots` | Rush Shots |  |  |  |
| `second_period_shots` | Second Period Shots |  |  |  |
| `shooting_pct` | Goal conversion rate | (goals / sog) * 100 | 12%+ | <8% |
| `shot_quality_avg` | Shot Quality Avg |  |  |  |
| `shot_success_rate` | Shot Success Rate |  |  |  |
| `shots` | All shot attempts | sog + shots_blocked + shots_missed | 5+/game | <2/game |
| `shots_blocked` | Shots stopped by defenders | COUNT(shots blocked by opponent) | N/A | N/A |
| `shots_leading` | Shots Leading |  |  |  |
| `shots_missed` | Shots that missed net | COUNT(shots off target) | Low ratio | High ratio |
| `shots_per_60_playing` | Shots Per 60 Playing |  |  |  |
| `shots_successful` | Shots Successful |  |  |  |
| `shots_tied` | Shots Tied |  |  |  |
| `shots_trailing` | Shots Trailing |  |  |  |
| `shots_unsuccessful` | Shots Unsuccessful |  |  |  |
| `sog` | Shots on net | COUNT(shots reaching goalie) | 4+/game | <2/game |
| `third_period_shots` | Third Period Shots |  |  |  |
| `times_targeted_shots` | Times Targeted Shots |  |  |  |
| `xg_per_shot` | Xg Per Shot |  |  |  |

## Passing Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `breakout_pass_attempts` | Breakout Pass Attempts |  |  |  |
| `cross_ice_passes_received` | Cross Ice Passes Received |  |  |  |
| `def_pass_deflected` | Def Pass Deflected |  |  |  |
| `def_pass_intercepted` | Def Pass Intercepted |  |  |  |
| `pass_attempts` | Total passes tried | COUNT(all passes) | 20+/game | <10/game |
| `pass_completed` | Passes that connected | COUNT(successful passes) | High volume | Low volume |
| `pass_for_tip` | Pass For Tip |  |  |  |
| `pass_pct` | Pass accuracy | (pass_completed / pass_attempts) * 100 | 75%+ | <60% |
| `pass_reception_rate` | Pass Reception Rate |  |  |  |
| `pass_success_rate` | Pass Success Rate |  |  |  |
| `passes_deflected` | Passes Deflected |  |  |  |
| `passes_intercepted` | Passes Intercepted |  |  |  |
| `passes_missed_target` | Passes Missed Target |  |  |  |
| `passes_received_successful` | Passes Received Successful |  |  |  |
| `passes_received_unsuccessful` | Passes Received Unsuccessful |  |  |  |
| `passes_successful` | Passes Successful |  |  |  |
| `passes_unsuccessful` | Passes Unsuccessful |  |  |  |
| `reverse_passes` | Reverse Passes |  |  |  |
| `slot_passes_received` | Slot Passes Received |  |  |  |
| `times_pass_target` | Times Pass Target |  |  |  |
| `times_targeted_passes` | Times Targeted Passes |  |  |  |
| `zone_exit_pass` | Zone Exit Pass |  |  |  |

## Faceoff Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `def_forced_turnovers` | Def Forced Turnovers |  |  |  |
| `fo_losses` | Draws lost | COUNT(faceoffs lost) | Low count | High count |
| `fo_losses_dz` | Fo Losses Dz |  |  |  |
| `fo_losses_nz` | Fo Losses Nz |  |  |  |
| `fo_losses_oz` | Fo Losses Oz |  |  |  |
| `fo_pct` | Draw win rate | (fo_wins / fo_total) * 100 | 55%+ | <45% |
| `fo_pct_dz` | Fo Pct Dz |  |  |  |
| `fo_pct_nz` | Fo Pct Nz |  |  |  |
| `fo_pct_oz` | Fo Pct Oz |  |  |  |
| `fo_total` | Total draws taken | fo_wins + fo_losses | N/A | N/A |
| `fo_wins` | Draws won | COUNT(faceoffs won) | High count | Low count |
| `fo_wins_dz` | Fo Wins Dz |  |  |  |
| `fo_wins_nz` | Fo Wins Nz |  |  |  |
| `fo_wins_oz` | Fo Wins Oz |  |  |  |
| `force_wide` | Force Wide |  |  |  |
| `late_game_performance` | Late Game Performance |  |  |  |
| `performance_index` | Performance Index |  |  |  |
| `rating_performance_delta` | Rating Performance Delta |  |  |  |

## Time on Ice Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `avg_playing_shift` | Avg Playing Shift |  |  |  |
| `avg_shift` | Average shift duration | toi_seconds / shift_count | 45-75 sec | >90 sec |
| `avg_shift_too_long` | Avg Shift Too Long |  |  |  |
| `def_times_beat_deke` | Def Times Beat Deke |  |  |  |
| `def_times_beat_speed` | Def Times Beat Speed |  |  |  |
| `def_times_beat_total` | Def Times Beat Total |  |  |  |
| `logical_shifts` | True shift changes (not period breaks) | COUNT(actual line changes) | N/A | N/A |
| `playing_toi_minutes` | Playing Toi Minutes |  |  |  |
| `playing_toi_seconds` | Active playing time | toi_seconds - stoppage_seconds | High % of TOI | Low % of TOI |
| `shift_count` | Number of shifts taken | COUNT(shifts) | N/A | N/A |
| `shift_length_warning` | Shift Length Warning |  |  |  |
| `times_attacked` | Times Attacked |  |  |  |
| `times_attacked_successfully` | Times Attacked Successfully |  |  |  |
| `times_attacked_unsuccessfully` | Times Attacked Unsuccessfully |  |  |  |
| `times_ep3` | Times Ep3 |  |  |  |
| `times_ep4` | Times Ep4 |  |  |  |
| `times_ep5` | Times Ep5 |  |  |  |
| `times_opp2` | Times Opp2 |  |  |  |
| `times_opp3` | Times Opp3 |  |  |  |
| `times_opp4` | Times Opp4 |  |  |  |
| `times_target_dz` | Times Target Dz |  |  |  |
| `times_target_nz` | Times Target Nz |  |  |  |
| `times_target_oz` | Times Target Oz |  |  |  |
| `times_targeted_as_defender` | Times Targeted As Defender |  |  |  |
| `times_targeted_by_opp` | Times Targeted By Opp |  |  |  |
| `times_targeted_entries` | Times Targeted Entries |  |  |  |
| `toi_minutes` | Total ice time in minutes | toi_seconds / 60 | 25+ | <10 |
| `toi_seconds` | Total ice time in seconds | SUM(shift durations) | 1500+ | <600 |
| `toi_vs_team_avg` | Toi Vs Team Avg |  |  |  |

## Per-60 Rate Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `assists_per_60` | Assist rate per 60 min | (assists / toi_minutes) * 60 | 2+ | 0 |
| `danger_creation_rate` | Danger Creation Rate |  |  |  |
| `defensive_success_rate` | Defensive Success Rate |  |  |  |
| `game_score_per_60` | Game Score Per 60 |  |  |  |
| `goals_per_60` | Goal rate per 60 min | (goals / toi_minutes) * 60 | 2+ | 0 |
| `involvement_rate` | Involvement Rate |  |  |  |
| `overall_success_rate` | Overall Success Rate |  |  |  |
| `play_success_rate` | Play Success Rate |  |  |  |
| `points_per_60` | Point rate per 60 min | (points / toi_minutes) * 60 | 3+ | <1 |
| `shots_per_60` | Shot rate per 60 min | (shots / toi_minutes) * 60 | 10+ | <5 |

## Zone Transition Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `ceded_exits` | Ceded Exits |  |  |  |
| `def_exits_denied` | Def Exits Denied |  |  |  |
| `def_zone_clears` | Def Zone Clears |  |  |  |
| `exits_successful` | Exits Successful |  |  |  |
| `exits_unsuccessful` | Exits Unsuccessful |  |  |  |
| `zone_entries` | Times entered O-zone | COUNT(offensive zone entries) | 5+/game | <2/game |
| `zone_entries_controlled` | Entries with possession | zone_entry_carry + zone_entry_pass | 70%+ | <50% |
| `zone_entries_uncontrolled` | Zone Entries Uncontrolled |  |  |  |
| `zone_entry_carry` | Controlled entries w/ puck | COUNT(zone entries via carry) | High % | Low % |
| `zone_entry_control_pct` | Controlled entry rate | (controlled / total) * 100 | 70%+ | <50% |
| `zone_entry_denials` | Zone Entry Denials |  |  |  |
| `zone_entry_denials_success` | Zone Entry Denials Success |  |  |  |
| `zone_entry_dump` | Uncontrolled entries | COUNT(dump and chase entries) | Low % | High % |
| `zone_entry_pass` | Entries via pass | COUNT(zone entries via pass) | N/A | N/A |
| `zone_entry_success_rate` | Zone Entry Success Rate |  |  |  |
| `zone_exit_carry` | Zone Exit Carry |  |  |  |
| `zone_exit_clear` | Zone Exit Clear |  |  |  |
| `zone_exit_control_pct` | Zone Exit Control Pct |  |  |  |
| `zone_exit_denials` | Zone Exit Denials |  |  |  |
| `zone_exit_dump` | Zone Exit Dump |  |  |  |
| `zone_exit_success_rate` | Zone Exit Success Rate |  |  |  |
| `zone_exits` | Times exited D-zone | COUNT(defensive zone exits) | 5+/game | <2/game |
| `zone_exits_controlled` | Zone Exits Controlled |  |  |  |
| `zone_exits_uncontrolled` | Zone Exits Uncontrolled |  |  |  |
| `zone_keepins` | Zone Keepins |  |  |  |
| `zone_starts_dz_pct` | Zone Starts Dz Pct |  |  |  |
| `zone_starts_oz_pct` | Zone Starts Oz Pct |  |  |  |

## Turnover Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `def_takeaways` | Def Takeaways |  |  |  |
| `give_and_go` | Give And Go |  |  |  |
| `giveaway_rate_per_60` | Giveaway Rate Per 60 |  |  |  |
| `giveaways` | Times lost puck to opponent | COUNT(turnovers committed) | <3/game | 5+/game |
| `giveaways_bad` | Turnovers leading to chances | COUNT(costly turnovers) | 0/game | 2+/game |
| `giveaways_good` | Giveaways Good |  |  |  |
| `giveaways_neutral` | Giveaways Neutral |  |  |  |
| `takeaway_rate_per_60` | Takeaway Rate Per 60 |  |  |  |
| `takeaways` | Times stole puck | COUNT(turnovers forced) | 3+/game | <1/game |
| `turnover_diff_adjusted` | Net turnover impact | takeaways - giveaways_bad | Positive | Negative |
| `turnover_recoveries` | Turnover Recoveries |  |  |  |
| `turnovers_dz` | Turnovers Dz |  |  |  |
| `turnovers_nz` | Turnovers Nz |  |  |  |
| `turnovers_oz` | Turnovers Oz |  |  |  |

## Possession Stats (Corsi/Fenwick)

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `cf_pct` | Share of shot attempts | (CF / (CF + CA)) * 100 | 55%+ | <45% |
| `cf_pct_rating_adj` | Cf Pct Rating Adj |  |  |  |
| `corsi_against` | Shot attempts against | opponent shot attempts while on ice | Low | High |
| `corsi_for` | Shot attempts for while on ice | sog + shots_blocked + shots_missed (team) | High | Low |
| `fenwick_against` | Unblocked attempts against | opponent unblocked attempts | Low | High |
| `fenwick_for` | Unblocked attempts for | sog + shots_missed (excludes blocked) | High | Low |
| `ff_pct` | Share of unblocked attempts | (FF / (FF + FA)) * 100 | 55%+ | <45% |

## Plus/Minus Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `minus_en_adj` | Minus En Adj |  |  |  |
| `minus_ev` | ES goals against | goals against at ES while on ice | Low | High |
| `minus_total` | Minus Total |  |  |  |
| `plus_en_adj` | Plus En Adj |  |  |  |
| `plus_ev` | ES goals for | goals for at ES while on ice | High | Low |
| `plus_minus_en_adj` | Plus Minus En Adj |  |  |  |
| `plus_minus_ev` | Plus Minus Ev |  |  |  |
| `plus_minus_rating_adj` | Plus Minus Rating Adj |  |  |  |
| `plus_minus_total` | Net goal differential | goals_for - goals_against (on ice) | Positive | Negative |
| `plus_total` | Plus Total |  |  |  |

## Expected Goals (xG) Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `expected_vs_rating` | Expected Vs Rating |  |  |  |
| `goals_above_expected` | Finishing vs expectation | actual_goals - xg_for | Positive | Negative |
| `xg_against` | Expected goals conceded | SUM(shot probabilities) against | Low | High |
| `xg_diff` | Net expected goal impact | xg_for - xg_against | Positive | Negative |
| `xg_for` | Expected goals from shot quality | SUM(shot probabilities) for team | High | Low |
| `xg_pct` | Xg Pct |  |  |  |

## Scoring Chance / Danger Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `high_danger_chances` | Best opportunities | shots from prime areas | 2+/game | 0/game |
| `scoring_chances` | Quality opportunities | high + medium danger shots | 5+/game | <2/game |
| `shots_high_danger` | Premium scoring chances | shots from slot/crease | 3+/game | 0/game |
| `shots_low_danger` | Low quality chances | shots from perimeter | N/A | N/A |
| `shots_medium_danger` | Moderate chances | shots from mid-range | N/A | N/A |

## Micro Stats (Detailed Play Tracking)

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `backchecks` | Defensive effort | COUNT(defensive hustle plays) | 3+/game | 0/game |
| `block_attempts` | Block Attempts |  |  |  |
| `blocked_shots_play` | Shots blocked by player | COUNT(blocked shots) | 2+/game (D) | N/A |
| `blocks` | Blocks |  |  |  |
| `box_outs` | Box Outs |  |  |  |
| `breakout_clear_attempts` | Breakout Clear Attempts |  |  |  |
| `breakout_rush_attempts` | Breakout Rush Attempts |  |  |  |
| `breakouts` | Successful DZ exits | COUNT(zone exit plays) | 5+/game (D) | <2/game |
| `breakouts_success` | Breakouts Success |  |  |  |
| `chips` | Chips |  |  |  |
| `contains` | Contains |  |  |  |
| `crash_net` | Crease presence | COUNT(drives to crease) | 2+/game | 0/game |
| `cycle_plays` | Sustained OZ pressure | COUNT(board cycle possessions) | 3+/game | 0/game |
| `deke_attempts` | Dekes attempted | COUNT(all deke tries) | N/A | N/A |
| `dekes_beat_defender` | Dekes Beat Defender |  |  |  |
| `dekes_successful` | Dekes that worked | COUNT(dekes beating defender) | 2+/game | 0/game |
| `drives_corner` | Drives Corner |  |  |  |
| `drives_corner_success` | Drives Corner Success |  |  |  |
| `drives_middle` | Drives Middle |  |  |  |
| `drives_middle_success` | Drives Middle Success |  |  |  |
| `drives_net` | Drives Net |  |  |  |
| `drives_wide` | Drives Wide |  |  |  |
| `drives_wide_success` | Drives Wide Success |  |  |  |
| `forechecks` | OZ pressure plays | COUNT(forecheck pressures) | 5+/game (F) | <2/game |
| `loose_puck_losses` | Loose Puck Losses |  |  |  |
| `loose_puck_wins` | Battle victories | COUNT(50/50 puck wins) | 3+/game | <1/game |
| `lost_puck` | Lost Puck |  |  |  |
| `poke_checks` | Defensive stick work | COUNT(stick pokes) | 2+/game | N/A |
| `pressures` | Pressures |  |  |  |
| `puck_battle_wins` | Puck Battle Wins |  |  |  |
| `puck_battles` | Puck Battles |  |  |  |
| `puck_possession_index` | Puck Possession Index |  |  |  |
| `puck_recoveries` | Retrieved loose pucks | COUNT(puck retrieval wins) | 3+/game | <1/game |
| `puck_retrievals` | Puck Retrievals |  |  |  |
| `puck_touches_estimated` | Puck Touches Estimated |  |  |  |
| `screens` | Blocked goalie vision | COUNT(net-front screens) | 2+/game | 0/game |
| `separate_from_puck` | Separate From Puck |  |  |  |
| `stick_checks` | Defensive disruption | COUNT(stick lifts/holds) | 2+/game | N/A |
| `stopped_deke` | Stopped Deke |  |  |  |
| `surf_plays` | Surf Plays |  |  |  |
| `tip_attempts` | Tip Attempts |  |  |  |

## Defensive Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `def_battles_lost` | Def Battles Lost |  |  |  |
| `def_battles_won` | Def Battles Won |  |  |  |
| `def_body_checks` | Def Body Checks |  |  |  |
| `def_coverage_assignments` | Def Coverage Assignments |  |  |  |
| `def_entries_allowed` | Def Entries Allowed |  |  |  |
| `def_interceptions` | Def Interceptions |  |  |  |
| `def_poke_checks` | Def Poke Checks |  |  |  |
| `def_stick_checks` | Def Stick Checks |  |  |  |

## Success Rate Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `entries_successful` | Entries Successful |  |  |  |
| `entries_unsuccessful` | Entries Unsuccessful |  |  |  |
| `plays_successful` | Plays Successful |  |  |  |
| `plays_unsuccessful` | Plays Unsuccessful |  |  |  |
| `total_successful_plays` | Total Successful Plays |  |  |  |
| `total_unsuccessful_plays` | Total Unsuccessful Plays |  |  |  |

## Situational Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `clutch_factor` | Clutch Factor |  |  |  |
| `period_3_dropoff` | Period 3 Dropoff |  |  |  |

## Composite Ratings

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `complete_player_score` | Complete Player Score |  |  |  |
| `defensive_rating` | Overall defensive impact | composite of D-stats | 7+/10 | <4/10 |
| `effective_game_rating` | Effective Game Rating |  |  |  |
| `efficiency_score` | Efficiency Score |  |  |  |
| `game_score` | Single-game performance | weighted sum per NHL formula | 2+ | <0 |
| `game_score_rating` | Game Score Rating |  |  |  |
| `hustle_rating` | Hustle Rating |  |  |  |
| `impact_score` | Total game impact | weighted composite of all stats | 8+ | <4 |
| `offensive_rating` | Overall offensive impact | composite of O-stats | 7+/10 | <4/10 |
| `physical_rating` | Physical Rating |  |  |  |
| `player_rating` | Player Rating |  |  |  |
| `playing_at_rating` | Playing At Rating |  |  |  |
| `playmaking_rating` | Playmaking Rating |  |  |  |
| `shooting_rating` | Shooting Rating |  |  |  |
| `sub_equity_score` | Sub Equity Score |  |  |  |
| `two_way_rating` | Overall player rating | (offensive + defensive) / 2 | 7+/10 | <4/10 |
| `war_estimate` | Value over replacement | estimated wins above replacement | 0.1+/game | Negative |

## Quality of Competition/Teammates

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `opp_avg_rating` | Quality of competition | AVG(opponent ratings faced) | N/A | N/A |
| `qoc_rating` | Difficulty of matchups | quality of competition index | High (if succeeding) | N/A |
| `qot_rating` | Linemate quality | quality of teammates index | N/A | N/A |

## Other Stats

| Column | Description | Formula | Good | Bad |
|--------|-------------|---------|------|-----|
| `2on0_rushes` | 2On0 Rushes |  |  |  |
| `2on1_rushes` | 2On1 Rushes |  |  |  |
| `3on2_rushes` | 3On2 Rushes |  |  |  |
| `away_team_id` | Away Team Id |  |  |  |
| `beat_middle` | Beat Middle |  |  |  |
| `beat_wide` | Beat Wide |  |  |  |
| `breakaway_attempts` | Breakaway Attempts |  |  |  |
| `ceded_entries` | Ceded Entries |  |  |  |
| `counter_attacks` | Counter Attacks |  |  |  |
| `cutbacks` | Cutbacks |  |  |  |
| `defensive_assignments` | Defensive Assignments |  |  |  |
| `defensive_contribution` | Defensive Contribution |  |  |  |
| `delays` | Delays |  |  |  |
| `dump_and_chase` | Dump And Chase |  |  |  |
| `dump_recoveries` | Dump Recoveries |  |  |  |
| `fatigue_indicator` | Fatigue Indicator |  |  |  |
| `front_of_net` | Front Of Net |  |  |  |
| `game_id` | Game Id |  |  |  |
| `got_beat_middle` | Got Beat Middle |  |  |  |
| `got_beat_wide` | Got Beat Wide |  |  |  |
| `hits` | Hits |  |  |  |
| `home_team_id` | Home Team Id |  |  |  |
| `in_lane` | In Lane |  |  |  |
| `man_on_man` | Man On Man |  |  |  |
| `odd_man_rushes` | Odd Man Rushes |  |  |  |
| `offensive_contribution` | Offensive Contribution |  |  |  |
| `on_ice_sh_pct` | On Ice Sh Pct |  |  |  |
| `on_ice_sv_pct` | On Ice Sv Pct |  |  |  |
| `pdo` | Pdo |  |  |  |
| `pdo_5v5` | Pdo 5V5 |  |  |  |
| `player_game_key` | Player Game Key |  |  |  |
| `player_id` | Player Id |  |  |  |
| `player_name` | Player Name |  |  |  |
| `quick_ups` | Quick Ups |  |  |  |
| `rebound_recoveries` | Rebound Recoveries |  |  |  |
| `retrievals` | Retrievals |  |  |  |
| `rush_entries` | Rush Entries |  |  |  |
| `second_touches` | Second Touches |  |  |  |
| `skill_diff` | Skill Diff |  |  |  |
| `stoppage_seconds` | Stoppage Seconds |  |  |  |
| `support_plays` | Support Plays |  |  |  |
| `total_on_ice_events` | Total On Ice Events |  |  |  |
| `transition_plays` | Transition Plays |  |  |  |

---

## Summary

**Total columns:** 317

| Category | Count |
|----------|-------|
| Scoring Stats | 24 |
| Shooting Stats | 22 |
| Passing Stats | 22 |
| Faceoff Stats | 18 |
| Time on Ice Stats | 29 |
| Per-60 Rate Stats | 10 |
| Zone Transition Stats | 27 |
| Turnover Stats | 14 |
| Possession Stats (Corsi/Fenwick) | 7 |
| Plus/Minus Stats | 10 |
| Expected Goals (xG) Stats | 6 |
| Scoring Chance / Danger Stats | 5 |
| Micro Stats (Detailed Play Tracking) | 41 |
| Defensive Stats | 8 |
| Success Rate Stats | 6 |
| Situational Stats | 2 |
| Composite Ratings | 17 |
| Quality of Competition/Teammates | 3 |
| Other Stats | 43 |
---

## Goalie Game Stats (`fact_goalie_game_stats`)

| Column | Description | Good | Bad |
|--------|-------------|------|-----|
| `goalie_game_key` | Primary key | - | - |
| `game_id` | Game identifier | - | - |
| `player_id` | Goalie player ID | - | - |
| `player_name` | Goalie name | - | - |
| `team_id` | Team ID | - | - |
| `shots_against` | Total shots faced | N/A | N/A |
| `goals_against` | Goals allowed | Low | High |
| `saves` | Shots stopped | High | Low |
| `save_pct` | Save percentage | 90%+ | <85% |
| `toi_seconds` | Time on ice | N/A | N/A |
| `toi_minutes` | Time on ice (min) | N/A | N/A |
| `gaa` | Goals against average | <3.0 | >5.0 |
| `wins` | Games won | High | Low |
| `losses` | Games lost | Low | High |
| `shutouts` | Clean sheets | Any | 0 |
| `high_danger_saves` | Saves from slot | High | Low |
| `high_danger_goals_against` | Goals from slot | Low | High |
| `high_danger_save_pct` | HD save % | 85%+ | <75% |
| `expected_goals_against` | xGA | N/A | N/A |
| `goals_saved_above_expected` | Performance vs xG | Positive | Negative |

---

## Team Game Stats (`fact_team_game_stats`)

| Column | Description | Good | Bad |
|--------|-------------|------|-----|
| `team_game_key` | Primary key | - | - |
| `game_id` | Game identifier | - | - |
| `team_id` | Team ID | - | - |
| `team_name` | Team name | - | - |
| `is_home` | Home team flag | - | - |
| `goals_for` | Goals scored | High | Low |
| `goals_against` | Goals allowed | Low | High |
| `shots_for` | Shots taken | High | Low |
| `shots_against` | Shots faced | Low | High |
| `shot_pct` | Team shooting % | 12%+ | <8% |
| `save_pct` | Team save % | 90%+ | <85% |
| `corsi_for` | Shot attempts for | High | Low |
| `corsi_against` | Shot attempts against | Low | High |
| `cf_pct` | Corsi % | 55%+ | <45% |
| `fenwick_for` | Unblocked attempts | High | Low |
| `fenwick_against` | Unblocked against | Low | High |
| `ff_pct` | Fenwick % | 55%+ | <45% |
| `faceoff_wins` | Faceoffs won | High | Low |
| `faceoff_losses` | Faceoffs lost | Low | High |
| `fo_pct` | Faceoff % | 55%+ | <45% |
| `power_play_goals` | PP goals | High | Low |
| `power_play_opportunities` | PP chances | N/A | N/A |
| `pp_pct` | Power play % | 25%+ | <15% |
| `penalty_kill_goals_against` | PK goals against | Low | High |
| `times_shorthanded` | Penalties taken | Low | High |
| `pk_pct` | Penalty kill % | 85%+ | <75% |
| `hits` | Total hits | Context | Context |
| `blocks` | Blocked shots | High | Low |
| `giveaways` | Turnovers | Low | High |
| `takeaways` | Forced turnovers | High | Low |
| `xg_for` | Expected goals | High | Low |
| `xg_against` | Expected goals against | Low | High |
| `xg_diff` | xG differential | Positive | Negative |
| `pdo` | SH% + SV% | 100 (luck neutral) | N/A |
