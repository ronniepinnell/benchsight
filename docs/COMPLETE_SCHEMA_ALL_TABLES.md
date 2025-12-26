# Complete Schema - All 56 Tables with Columns

*Generated: 2025-12-20*

## Summary

| Layer | Count |
|-------|-------|
| Stage | 21 |
| Intermediate | 13 |
| Datamart | 20 |
| Metadata | 2 |
| **Total** | **56** |

---
## Stage Layer

### stg_dim_dates
**Rows**: 4,747

| Column | Type | PK |
|--------|------|-----|
| datekey | BIGINT |  |
| date | TEXT |  |
| day | BIGINT |  |
| daysuffix | TEXT |  |
| weekday | BIGINT |  |
| weekdayname | TEXT |  |
| weekdayname_short | TEXT |  |
| weekdayname_firstletter | TEXT |  |
| dowinmonth | BIGINT |  |
| dayofyear | BIGINT |  |
| weekofmonth | BIGINT |  |
| weekofyear | BIGINT |  |
| month | BIGINT |  |
| monthname | TEXT |  |
| monthname_short | TEXT |  |
| monthname_firstletter | TEXT |  |
| quarter | BIGINT |  |
| quartername | TEXT |  |
| year | BIGINT |  |
| mmyyyy | BIGINT |  |
| monthyear | TEXT |  |
| isweekend | BIGINT |  |
| isholiday | BIGINT |  |
| weekstartdate | TEXT |  |
| weekenddate | TEXT |  |
| fourweekperiodstartdate | TEXT |  |
| fourweekperiodenddate | TEXT |  |
| _load_timestamp | TEXT |  |
| _source_file | TEXT |  |

### stg_dim_league
**Rows**: 2

| Column | Type | PK |
|--------|------|-----|
| league_id | TEXT |  |
| league | TEXT |  |

### stg_dim_player
**Rows**: 335

| Column | Type | PK |
|--------|------|-----|
| player_first_name | TEXT |  |
| player_last_name | TEXT |  |
| player_full_name | TEXT |  |
| player_id | TEXT |  |
| player_primary_position | TEXT |  |
| current_skill_rating | BIGINT |  |
| player_hand | FLOAT |  |
| birth_year | FLOAT |  |
| player_gender | TEXT |  |
| highest_beer_league | TEXT |  |
| player_rating_ly | BIGINT |  |
| player_notes | FLOAT |  |
| player_leadership | TEXT |  |
| player_norad | TEXT |  |
| player_csaha | FLOAT |  |
| player_norad_primary_number | FLOAT |  |
| player_csah_primary_number | FLOAT |  |
| player_norad_current_team | TEXT |  |
| player_csah_current_team | FLOAT |  |
| player_norad_current_team_id | TEXT |  |
| player_csah_current_team_id | FLOAT |  |
| other_url | TEXT |  |
| player_url | TEXT |  |
| player_image | TEXT |  |
| random_player_first_name | TEXT |  |
| random_player_last_name | TEXT |  |
| random_player_full_name | TEXT |  |

### stg_dim_playerurlref
**Rows**: 543

| Column | Type | PK |
|--------|------|-----|
| n_player_url | TEXT |  |
| player_full_name | TEXT |  |
| n_player_id_2 | TEXT |  |

### stg_dim_randomnames
**Rows**: 486

| Column | Type | PK |
|--------|------|-----|
| random_full_name | TEXT |  |
| random_first_name | TEXT |  |
| random_last_name | TEXT |  |
| gender | TEXT |  |
| name_used | TEXT |  |

### stg_dim_rinkboxcoord
**Rows**: 50

| Column | Type | PK |
|--------|------|-----|
| box_id | TEXT |  |
| box_id_rev | TEXT |  |
| x_min | FLOAT |  |
| x_max | FLOAT |  |
| y_min | FLOAT |  |
| y_max | FLOAT |  |
| area | FLOAT |  |
| x_description | TEXT |  |
| y_description | TEXT |  |
| danger | TEXT |  |
| zone | TEXT |  |
| side | TEXT |  |

### stg_dim_rinkcoordzones
**Rows**: 297

| Column | Type | PK |
|--------|------|-----|
| box_id | TEXT |  |
| box_id_rev | TEXT |  |
| x_min | FLOAT |  |
| x_max | FLOAT |  |
| y_min | FLOAT |  |
| y_max | FLOAT |  |
| y_description | TEXT |  |
| x_description | TEXT |  |
| danger | TEXT |  |
| slot | TEXT |  |
| zone | TEXT |  |
| side | TEXT |  |
| dotside | TEXT |  |
| depth | TEXT |  |

### stg_dim_schedule
**Rows**: 552

| Column | Type | PK |
|--------|------|-----|
| index | BIGINT |  |
| game_id | BIGINT |  |
| season | BIGINT |  |
| season_id | TEXT |  |
| game_url | TEXT |  |
| home_team_game_id | TEXT |  |
| away_team_game_id | TEXT |  |
| date | TEXT |  |
| game_time | TEXT |  |
| home_team_name | TEXT |  |
| away_team_name | TEXT |  |
| home_team_id | TEXT |  |
| away_team_id | TEXT |  |
| head_to_head_id | TEXT |  |
| game_type | TEXT |  |
| playoff_round | TEXT |  |
| last_period_type | TEXT |  |
| period_length | TEXT |  |
| ot_period_length | TEXT |  |
| shootout_rounds | FLOAT |  |
| home_total_goals | BIGINT |  |
| away_total_goals | BIGINT |  |
| home_team_period1_goals | FLOAT |  |
| home_team_period2_goals | FLOAT |  |
| home_team_period3_goals | FLOAT |  |
| home_team_periodOT_goals | FLOAT |  |
| away_team_period1_goals | FLOAT |  |
| away_team_period2_goals | FLOAT |  |
| away_team_period3_goals | FLOAT |  |
| away_team_periodOT_goals | FLOAT |  |
| home_team_seeding | FLOAT |  |
| away_team_seeding | FLOAT |  |
| home_team_w | BIGINT |  |
| home_team_l | BIGINT |  |
| home_team_t | BIGINT |  |
| home_team_pts | BIGINT |  |
| away_team_w | BIGINT |  |
| away_team_l | BIGINT |  |
| away_team_t | BIGINT |  |
| away_team_pts | BIGINT |  |
| video_id | FLOAT |  |
| video_start_time | FLOAT |  |
| video_end_time | FLOAT |  |
| video_title | FLOAT |  |
| video_url | FLOAT |  |

### stg_dim_season
**Rows**: 9

| Column | Type | PK |
|--------|------|-----|
| index | BIGINT |  |
| season_id | TEXT |  |
| season | BIGINT |  |
| session | TEXT |  |
| norad | TEXT |  |
| csah | TEXT |  |
| league_id | TEXT |  |
| league | TEXT |  |
| start_date | TEXT |  |

### stg_dim_seconds
**Rows**: 4,800

| Column | Type | PK |
|--------|------|-----|
| time_key | BIGINT |  |
| period | BIGINT |  |
| period_name | TEXT |  |
| period_type | TEXT |  |
| minute_in_period | BIGINT |  |
| second_in_minute | BIGINT |  |
| total_seconds_in_period | BIGINT |  |
| time_elapsed_period_formatted | TEXT |  |
| time_remaining_period_seconds | BIGINT |  |
| time_remaining_period_formatted | TEXT |  |
| minute_remaining_period | BIGINT |  |
| second_remaining_minute | BIGINT |  |
| time_elapsed_game_seconds | BIGINT |  |
| time_elapsed_game_formatted | TEXT |  |
| time_remaining_regulation_seconds | BIGINT |  |
| is_first_minute | BOOLEAN |  |
| is_last_minute | BOOLEAN |  |
| is_regulation | BOOLEAN |  |
| is_overtime | BOOLEAN |  |
| _load_timestamp | TEXT |  |

### stg_dim_team
**Rows**: 26

| Column | Type | PK |
|--------|------|-----|
| team_name | TEXT |  |
| team_id | TEXT |  |
| norad_team | TEXT |  |
| csah_team | TEXT |  |
| league_id | TEXT |  |
| league | TEXT |  |
| long_team_name | TEXT |  |
| team_cd | TEXT |  |
| team_color1 | TEXT |  |
| team_color2 | TEXT |  |
| team_color3 | TEXT |  |
| team_color4 | TEXT |  |
| team_logo | TEXT |  |
| team_url | TEXT |  |

### stg_events_18969
**Rows**: 3,596

| Column | Type | PK |
|--------|------|-----|
| event_index_flag_ | TEXT |  |
| sequence_index_flag_ | TEXT |  |
| play_index_flag_ | TEXT |  |
| linked_event_index_flag_ | TEXT |  |
| event_start_min_ | FLOAT |  |
| event_start_sec_ | FLOAT |  |
| event_end_min_ | FLOAT |  |
| event_end_sec_ | FLOAT |  |
| player_game_number_ | FLOAT |  |
| event_team_zone_ | TEXT |  |
| event_type_ | TEXT |  |
| event_detail_ | TEXT |  |
| event_detail_2_ | TEXT |  |
| event_successful_ | TEXT |  |
| play_detail1_ | TEXT |  |
| play_detail2_ | TEXT |  |
| play_detail_successful_ | TEXT |  |
| pressured_pressurer_ | FLOAT |  |
| event_index_ | FLOAT |  |
| linked_event_index_ | FLOAT |  |
| sequence_index_ | FLOAT |  |
| play_index_ | FLOAT |  |
| team_ | TEXT |  |
| player_game_number | FLOAT |  |
| role_abrev_binary_ | TEXT |  |
| period | FLOAT |  |
| event_index | FLOAT |  |
| linked_event_index | FLOAT |  |
| tracking_event_index | FLOAT |  |
| event_start_min | FLOAT |  |
| event_start_sec | FLOAT |  |
| event_end_min | FLOAT |  |
| event_end_sec | FLOAT |  |
| role_abrev | TEXT |  |
| event_team_zone2_ | TEXT |  |
| event_team_zone | TEXT |  |
| home_team_zone_ | TEXT |  |
| away_team_zone_ | TEXT |  |
| team_venue_ | TEXT |  |
| team_venue_abv_ | TEXT |  |
| home_team_zone | TEXT |  |
| away_team_zone | TEXT |  |
| team_venue | TEXT |  |
| team_venue_abv | TEXT |  |
| side_of_puck | TEXT |  |
| sequence_index | FLOAT |  |
| play_index | FLOAT |  |
| play_detail1 | TEXT |  |
| play_detail_2 | TEXT |  |
| play_detail_successful | TEXT |  |
| pressured_pressurer | FLOAT |  |
| zone_change_index | FLOAT |  |
| game_id | FLOAT |  |
| home_team | TEXT |  |
| away_team | TEXT |  |
| Type | TEXT |  |
| event_detail | TEXT |  |
| event_detail_2 | TEXT |  |
| event_successful | TEXT |  |
| shift_index | FLOAT |  |
| duration | FLOAT |  |
| time_start_total_seconds | FLOAT |  |
| time_end_total_seconds | FLOAT |  |
| running_intermission_duration | FLOAT |  |
| period_start_total_running_seconds | FLOAT |  |
| running_video_time | FLOAT |  |
| event_running_start | FLOAT |  |
| event_running_end | FLOAT |  |
| player_role | TEXT |  |
| role_number | FLOAT |  |
| player_id | TEXT |  |
| player_team | TEXT |  |
| _game_id | BIGINT |  |
| _load_timestamp | TEXT |  |

### stg_fact_draft
**Rows**: 160

| Column | Type | PK |
|--------|------|-----|
| team_id | TEXT |  |
| skill_rating | BIGINT |  |
| round | BIGINT |  |
| player_full_name | TEXT |  |
| player_id | TEXT |  |
| team_name | TEXT |  |
| restricted | BOOLEAN |  |
| overall_draft_round | BIGINT |  |
| overall_draft_position | BIGINT |  |
| unrestricted_draft_position | BIGINT |  |
| season | BIGINT |  |
| season_id | TEXT |  |
| league | TEXT |  |
| player_draft_id | TEXT |  |

### stg_fact_gameroster
**Rows**: 14,239

| Column | Type | PK |
|--------|------|-----|
| index | FLOAT |  |
| game_id | BIGINT |  |
| team_game_id | TEXT |  |
| opp_team_game_id | TEXT |  |
| player_game_id | TEXT |  |
| team_venue | TEXT |  |
| team_name | TEXT |  |
| opp_team_name | TEXT |  |
| player_game_number | TEXT |  |
| n_player_url | TEXT |  |
| player_position | TEXT |  |
| games_played | TEXT |  |
| goals | FLOAT |  |
| assist | FLOAT |  |
| goals_against | FLOAT |  |
| pim | FLOAT |  |
| shutouts | FLOAT |  |
| team_id | TEXT |  |
| opp_team_id | TEXT |  |
| key | TEXT |  |
| player_full_name | TEXT |  |
| player_id | TEXT |  |
| date | TEXT |  |
| season | BIGINT |  |
| sub | FLOAT |  |
| current_team | TEXT |  |
| skill_rating | BIGINT |  |

### stg_fact_leadership
**Rows**: 28

| Column | Type | PK |
|--------|------|-----|
| player_full_name | TEXT |  |
| player_id | TEXT |  |
| leadership | TEXT |  |
| skill_rating | BIGINT |  |
| n_player_url | TEXT |  |
| team_name | TEXT |  |
| team_id | TEXT |  |
| season | BIGINT |  |
| season_id | TEXT |  |

### stg_fact_playergames
**Rows**: 3,010

| Column | Type | PK |
|--------|------|-----|
| ID | TEXT |  |
| Date | TEXT |  |
| Type | TEXT |  |
| Team | TEXT |  |
| Opp | TEXT |  |
| # | TEXT |  |
| Player | TEXT |  |
| Position | TEXT |  |
| GP | BIGINT |  |
| G | BIGINT |  |
| A | BIGINT |  |
| GA | BIGINT |  |
| PIM | BIGINT |  |
| SO | BIGINT |  |
| Rank | FLOAT |  |
| ID2 | TEXT |  |
| ID3 | TEXT |  |
| Season | TEXT |  |
| SeasonPlayerID | TEXT |  |

### stg_fact_registration
**Rows**: 191

| Column | Type | PK |
|--------|------|-----|
| player_full_name | TEXT |  |
| player_id | TEXT |  |
| season_id | TEXT |  |
| season | BIGINT |  |
| restricted | TEXT |  |
| email | TEXT |  |
| position | TEXT |  |
| norad_experience | TEXT |  |
| CAF | TEXT |  |
| highest_beer_league_played | TEXT |  |
| skill_rating | BIGINT |  |
| age | BIGINT |  |
| referred_by | TEXT |  |
| notes | TEXT |  |
| sub_yn | TEXT |  |
| drafted_team_name | TEXT |  |
| drafted_team_id | TEXT |  |
| player_season_registration_id | TEXT |  |

### stg_shifts_18969
**Rows**: 98

| Column | Type | PK |
|--------|------|-----|
| shift_index | BIGINT |  |
| Period | BIGINT |  |
| shift_start_min | FLOAT |  |
| shift_start_sec | FLOAT |  |
| shift_end_min | FLOAT |  |
| shift_end_sec | FLOAT |  |
| shift_start_type | TEXT |  |
| shift_stop_type | TEXT |  |
| home_forward_1 | FLOAT |  |
| home_forward_2 | FLOAT |  |
| home_forward_3 | FLOAT |  |
| home_defense_1 | FLOAT |  |
| home_defense_2 | FLOAT |  |
| home_xtra | FLOAT |  |
| home_goalie | FLOAT |  |
| away_forward_1 | FLOAT |  |
| away_forward_2 | FLOAT |  |
| away_forward_3 | FLOAT |  |
| away_defense_1 | FLOAT |  |
| away_defense_2 | FLOAT |  |
| away_xtra | FLOAT |  |
| away_goalie | FLOAT |  |
| stoppage_time | FLOAT |  |
| home_ozone_start | FLOAT |  |
| home_ozone_end | FLOAT |  |
| home_dzone_start | FLOAT |  |
| home_dzone_end | FLOAT |  |
| home_nzone_start | FLOAT |  |
| home_nzone_end | FLOAT |  |
| game_id | BIGINT |  |
| home_team | TEXT |  |
| away_team | TEXT |  |
| shift_start_total_seconds | FLOAT |  |
| shift_end_total_seconds | FLOAT |  |
| shift_duration | FLOAT |  |
| home_team_strength | FLOAT |  |
| away_team_strength | FLOAT |  |
| home_team_en | FLOAT |  |
| away_team_en | FLOAT |  |
| home_team_pk | FLOAT |  |
| home_team_pp | FLOAT |  |
| away_team_pp | FLOAT |  |
| away_team_pk | FLOAT |  |
| situation | TEXT |  |
| strength | TEXT |  |
| home_goals | BIGINT |  |
| away_goals | BIGINT |  |
| home_team_plus | FLOAT |  |
| home_team_minus | FLOAT |  |
| away_team_plus | FLOAT |  |
| away_team_minus | FLOAT |  |
| period_start_total_running_seconds | BIGINT |  |
| running_video_time | BIGINT |  |
| shift_start_running_time | BIGINT |  |
| shift_end_running_time | BIGINT |  |
| _game_id | BIGINT |  |
| _load_timestamp | TEXT |  |

### stg_video_18969
**Rows**: 11

| Column | Type | PK |
|--------|------|-----|
| video_index | BIGINT |  |
| video_key | TEXT |  |
| game_id | BIGINT |  |
| video_type | TEXT |  |
| video_category | TEXT |  |
| url_primary | TEXT |  |
| url_backup | TEXT |  |
| url_embed | TEXT |  |
| video_id | TEXT |  |
| extension | TEXT |  |
| description | TEXT |  |
| duration_seconds | BIGINT |  |
| start_offset | BIGINT |  |
| _load_timestamp | TEXT |  |
| event_index | FLOAT |  |
| event_key | TEXT |  |

### stg_xy_events_18969
**Rows**: 1,594

| Column | Type | PK |
|--------|------|-----|
| xy_event_index | BIGINT |  |
| xy_event_key | TEXT |  |
| event_index | BIGINT |  |
| event_key | TEXT |  |
| linked_event_index | FLOAT |  |
| linked_event_key | TEXT |  |
| game_id | BIGINT |  |
| x_coord | FLOAT |  |
| y_coord | FLOAT |  |
| rink_box_id | TEXT |  |
| rink_zone_id | TEXT |  |
| danger | TEXT |  |
| zone_name | TEXT |  |
| side | TEXT |  |
| _load_timestamp | TEXT |  |

### stg_xy_shots_18969
**Rows**: 181

| Column | Type | PK |
|--------|------|-----|
| xy_shot_index | BIGINT |  |
| xy_shot_key | TEXT |  |
| event_index | BIGINT |  |
| event_key | TEXT |  |
| linked_event_index | FLOAT |  |
| linked_event_key | TEXT |  |
| game_id | BIGINT |  |
| x_coord | FLOAT |  |
| y_coord | FLOAT |  |
| shot_distance | FLOAT |  |
| shot_angle | FLOAT |  |
| is_goal | BIGINT |  |
| rink_box_id | TEXT |  |
| rink_zone_id | TEXT |  |
| danger | TEXT |  |
| _load_timestamp | TEXT |  |

---
## Intermediate Layer

### int_dim_dates
**Rows**: 4,747

| Column | Type | PK |
|--------|------|-----|
| date_key | INT |  |
| full_date | TEXT |  |
| day_of_month | INT |  |
| day_suffix | TEXT |  |
| day_of_week_num | INT |  |
| day_name | TEXT |  |
| day_name_short | TEXT |  |
| day_of_year | INT |  |
| week_of_month | INT |  |
| week_of_year | INT |  |
| week_start_date | TEXT |  |
| week_end_date | TEXT |  |
| month_num | INT |  |
| month_name | TEXT |  |
| month_name_short | TEXT |  |
| month_year_key | INT |  |
| month_year_label | TEXT |  |
| quarter_num | INT |  |
| quarter_name | TEXT |  |
| year_num | INT |  |
| is_weekend | TEXT |  |
| is_holiday | TEXT |  |
| four_week_start | TEXT |  |
| four_week_end | TEXT |  |
| _processed_timestamp | TEXT |  |
| _updated_timestamp | TEXT |  |

### int_dim_player
**Rows**: 335

| Column | Type | PK |
|--------|------|-----|
| player_id | TEXT |  |
| player_full_name | TEXT |  |
| display_name | TEXT |  |
| primary_position | TEXT |  |
| skill_rating | REAL |  |
| player_hand | REAL |  |
| birth_year | REAL |  |
| _processed_timestamp | TEXT |  |
| _updated_timestamp | TEXT |  |

### int_dim_schedule
**Rows**: 552

| Column | Type | PK |
|--------|------|-----|
| game_id | INT |  |
| home_team | TEXT |  |
| away_team | TEXT |  |
| home_team_id | TEXT |  |
| away_team_id | TEXT |  |
| game_date | TEXT |  |
| season_id | TEXT |  |
| game_type | TEXT |  |
| playoff_round | TEXT |  |
| home_score | INT |  |
| away_score | INT |  |
| winner | TEXT |  |
| video_id | REAL |  |
| video_url | REAL |  |
| _processed_timestamp | TEXT |  |
| _updated_timestamp | TEXT |  |

### int_dim_seconds
**Rows**: 4,800

| Column | Type | PK |
|--------|------|-----|
| time_key | BIGINT |  |
| period | BIGINT |  |
| period_name | TEXT |  |
| period_type | TEXT |  |
| minute_in_period | BIGINT |  |
| second_in_minute | BIGINT |  |
| total_seconds_in_period | BIGINT |  |
| time_elapsed_period_formatted | TEXT |  |
| time_remaining_period_seconds | BIGINT |  |
| time_remaining_period_formatted | TEXT |  |
| minute_remaining_period | BIGINT |  |
| second_remaining_minute | BIGINT |  |
| time_elapsed_game_seconds | BIGINT |  |
| time_elapsed_game_formatted | TEXT |  |
| time_remaining_regulation_seconds | BIGINT |  |
| is_first_minute | BOOLEAN |  |
| is_last_minute | BOOLEAN |  |
| is_regulation | BOOLEAN |  |
| is_overtime | BOOLEAN |  |
| _load_timestamp | TEXT |  |
| _processed_timestamp | TEXT |  |
| _updated_timestamp | TEXT |  |

### int_dim_team
**Rows**: 26

| Column | Type | PK |
|--------|------|-----|
| team_id | TEXT |  |
| team_name | TEXT |  |
| team_abbr | TEXT |  |
| long_team_name | TEXT |  |
| league | TEXT |  |
| team_color1 | TEXT |  |
| team_color2 | TEXT |  |
| _processed_timestamp | TEXT |  |
| _updated_timestamp | TEXT |  |

### int_event_players_18969
**Rows**: 3,139

| Column | Type | PK |
|--------|------|-----|
| event_index | INT |  |
| event_key | TEXT |  |
| player_game_number | INT |  |
| player_id | TEXT |  |
| player_team | TEXT |  |
| player_game_key | TEXT |  |
| player_role | TEXT |  |
| play_detail1 | TEXT |  |
| play_detail_2 | TEXT |  |
| play_detail_successful | TEXT |  |
| is_primary_player | TEXT |  |
| is_event_team | TEXT |  |
| event_player_key | TEXT |  |
| game_id | TEXT |  |
| _processed_timestamp | TEXT |  |

### int_events_18969
**Rows**: 1,594

| Column | Type | PK |
|--------|------|-----|
| event_index | INT |  |
| event_key | TEXT |  |
| shift_index | INT |  |
| shift_key | TEXT |  |
| linked_event_index | INT |  |
| linked_event_key | TEXT |  |
| sequence_index | INT |  |
| sequence_key | TEXT |  |
| play_index | INT |  |
| play_key | TEXT |  |
| event_type | TEXT |  |
| event_detail | TEXT |  |
| event_detail_2 | TEXT |  |
| event_successful | TEXT |  |
| period | INT |  |
| event_start_min | REAL |  |
| event_start_sec | REAL |  |
| time_total_seconds | INT |  |
| duration | REAL |  |
| event_team_zone | TEXT |  |
| game_id | TEXT |  |
| _processed_timestamp | TEXT |  |

### int_fact_gameroster
**Rows**: 13,960

| Column | Type | PK |
|--------|------|-----|
| game_id | INT |  |
| player_id | TEXT |  |
| player_game_number | TEXT |  |
| player_full_name | TEXT |  |
| display_name | TEXT |  |
| team_name | TEXT |  |
| opp_team_name | TEXT |  |
| team_venue | TEXT |  |
| player_position | TEXT |  |
| goals | INT |  |
| assists | INT |  |
| points | INT |  |
| penalty_minutes | INT |  |
| goals_against | INT |  |
| skill_rating | REAL |  |
| player_game_key | TEXT |  |
| _processed_timestamp | TEXT |  |
| _updated_timestamp | TEXT |  |

### int_game_players_18969
**Rows**: 27

| Column | Type | PK |
|--------|------|-----|
| player_game_number | TEXT |  |
| player_id | TEXT |  |
| player_game_key | TEXT |  |
| player_full_name | TEXT |  |
| display_name | TEXT |  |
| player_team | TEXT |  |
| player_venue | TEXT |  |
| position | TEXT |  |
| skill_rating | REAL |  |
| game_id | TEXT |  |
| _processed_timestamp | TEXT |  |

### int_shifts_18969
**Rows**: 98

| Column | Type | PK |
|--------|------|-----|
| shift_index | INT |  |
| shift_key | TEXT |  |
| period | INT |  |
| shift_start_total_seconds | REAL |  |
| shift_end_total_seconds | REAL |  |
| shift_duration | REAL |  |
| shift_start_type | TEXT |  |
| shift_stop_type | TEXT |  |
| situation | TEXT |  |
| strength | TEXT |  |
| home_strength | INT |  |
| away_strength | INT |  |
| home_goals | INT |  |
| away_goals | INT |  |
| home_plus | INT |  |
| home_minus | INT |  |
| away_plus | INT |  |
| away_minus | INT |  |
| home_forward_1 | INT |  |
| home_forward_2 | INT |  |
| home_forward_3 | INT |  |
| home_defense_1 | INT |  |
| home_defense_2 | INT |  |
| home_goalie | INT |  |
| away_forward_1 | INT |  |
| away_forward_2 | INT |  |
| away_forward_3 | INT |  |
| away_defense_1 | INT |  |
| away_defense_2 | INT |  |
| away_goalie | INT |  |
| game_id | TEXT |  |
| _processed_timestamp | TEXT |  |

### int_video_18969
**Rows**: 11

| Column | Type | PK |
|--------|------|-----|
| video_index | BIGINT |  |
| video_key | TEXT |  |
| game_id | BIGINT |  |
| video_type | TEXT |  |
| video_category | TEXT |  |
| url_primary | TEXT |  |
| url_backup | TEXT |  |
| url_embed | TEXT |  |
| video_id | TEXT |  |
| extension | TEXT |  |
| description | TEXT |  |
| duration_seconds | BIGINT |  |
| start_offset | BIGINT |  |
| _load_timestamp | TEXT |  |
| event_index | FLOAT |  |
| event_key | TEXT |  |
| _processed_timestamp | TEXT |  |

### int_xy_events_18969
**Rows**: 1,594

| Column | Type | PK |
|--------|------|-----|
| xy_event_index | INT |  |
| xy_event_key | TEXT |  |
| event_index | INT |  |
| event_key | TEXT |  |
| linked_event_index | REAL |  |
| linked_event_key | TEXT |  |
| game_id | INT |  |
| x_coord | REAL |  |
| y_coord | REAL |  |
| rink_box_id | TEXT |  |
| rink_zone_id | TEXT |  |
| danger | TEXT |  |
| zone_name | TEXT |  |
| side | TEXT |  |
| event_type | TEXT |  |
| event_detail | TEXT |  |
| period | INT |  |
| time_total_seconds | INT |  |
| _processed_timestamp | TEXT |  |

### int_xy_shots_18969
**Rows**: 181

| Column | Type | PK |
|--------|------|-----|
| xy_shot_index | INT |  |
| xy_shot_key | TEXT |  |
| event_index | INT |  |
| event_key | TEXT |  |
| linked_event_index | REAL |  |
| linked_event_key | TEXT |  |
| game_id | INT |  |
| x_coord | REAL |  |
| y_coord | REAL |  |
| shot_distance | REAL |  |
| shot_angle | REAL |  |
| is_goal | INT |  |
| rink_box_id | TEXT |  |
| rink_zone_id | TEXT |  |
| danger | TEXT |  |
| event_type | TEXT |  |
| event_detail | TEXT |  |
| period | INT |  |
| time_total_seconds | INT |  |
| _processed_timestamp | TEXT |  |

---
## Datamart Layer

### dim_dates
**Rows**: 4,747

| Column | Type | PK |
|--------|------|-----|
| date_key | BIGINT |  |
| full_date | TEXT |  |
| day_of_month | BIGINT |  |
| day_suffix | TEXT |  |
| day_of_week_num | BIGINT |  |
| day_name | TEXT |  |
| day_name_short | TEXT |  |
| day_of_year | BIGINT |  |
| week_of_month | BIGINT |  |
| week_of_year | BIGINT |  |
| week_start_date | TEXT |  |
| week_end_date | TEXT |  |
| month_num | BIGINT |  |
| month_name | TEXT |  |
| month_name_short | TEXT |  |
| month_year_key | BIGINT |  |
| month_year_label | TEXT |  |
| quarter_num | BIGINT |  |
| quarter_name | TEXT |  |
| year_num | BIGINT |  |
| is_weekend | BIGINT |  |
| is_holiday | BIGINT |  |
| four_week_start | TEXT |  |
| four_week_end | TEXT |  |
| _processed_timestamp | TEXT |  |
| _updated_timestamp | TEXT |  |

### dim_event_type
**Rows**: 7

| Column | Type | PK |
|--------|------|-----|
| event_type | TEXT | ✓ |
| event_category | TEXT |  |
| is_shot | INTEGER |  |
| is_possession | INTEGER |  |
| is_turnover | INTEGER |  |
| is_penalty | INTEGER |  |
| sort_order | INTEGER |  |
| _updated_timestamp | TEXT |  |

### dim_period
**Rows**: 5

| Column | Type | PK |
|--------|------|-----|
| period_id | INTEGER | ✓ |
| period_name | TEXT |  |
| period_abbr | TEXT |  |
| is_overtime | INTEGER |  |
| is_shootout | INTEGER |  |
| sort_order | INTEGER |  |
| _updated_timestamp | TEXT |  |

### dim_player
**Rows**: 335

| Column | Type | PK |
|--------|------|-----|
| player_id | TEXT |  |
| player_full_name | TEXT |  |
| display_name | TEXT |  |
| primary_position | TEXT |  |
| skill_rating | FLOAT |  |
| player_hand | FLOAT |  |
| birth_year | FLOAT |  |
| _processed_timestamp | TEXT |  |
| _updated_timestamp | TEXT |  |

### dim_position
**Rows**: 8

| Column | Type | PK |
|--------|------|-----|
| position_code | TEXT | ✓ |
| position_name | TEXT |  |
| position_type | TEXT |  |
| is_forward | INTEGER |  |
| is_defense | INTEGER |  |
| is_goalie | INTEGER |  |
| _updated_timestamp | TEXT |  |

### dim_rink_box
**Rows**: 50

| Column | Type | PK |
|--------|------|-----|
| box_id | TEXT | ✓ |
| box_id_rev | TEXT |  |
| x_min | REAL |  |
| x_max | REAL |  |
| y_min | REAL |  |
| y_max | REAL |  |
| area | REAL |  |
| x_description | TEXT |  |
| y_description | TEXT |  |
| danger | TEXT |  |
| zone | TEXT |  |
| side | TEXT |  |
| _processed_timestamp | TEXT |  |

### dim_rink_zone
**Rows**: 297

| Column | Type | PK |
|--------|------|-----|
| box_id | TEXT | ✓ |
| box_id_rev | TEXT |  |
| x_min | REAL |  |
| x_max | REAL |  |
| y_min | REAL |  |
| y_max | REAL |  |
| y_description | TEXT |  |
| x_description | TEXT |  |
| danger | TEXT |  |
| slot | TEXT |  |
| zone | TEXT |  |
| side | TEXT |  |
| dotside | TEXT |  |
| depth | TEXT |  |
| _processed_timestamp | TEXT |  |

### dim_schedule
**Rows**: 552

| Column | Type | PK |
|--------|------|-----|
| game_id | BIGINT |  |
| home_team | TEXT |  |
| away_team | TEXT |  |
| home_team_id | TEXT |  |
| away_team_id | TEXT |  |
| game_date | TEXT |  |
| season_id | TEXT |  |
| game_type | TEXT |  |
| playoff_round | TEXT |  |
| home_score | BIGINT |  |
| away_score | BIGINT |  |
| winner | TEXT |  |
| video_id | FLOAT |  |
| video_url | FLOAT |  |
| _processed_timestamp | TEXT |  |
| _updated_timestamp | TEXT |  |

### dim_seconds
**Rows**: 4,800

| Column | Type | PK |
|--------|------|-----|
| time_key | BIGINT |  |
| period | BIGINT |  |
| period_name | TEXT |  |
| period_type | TEXT |  |
| minute_in_period | BIGINT |  |
| second_in_minute | BIGINT |  |
| total_seconds_in_period | BIGINT |  |
| time_elapsed_period_formatted | TEXT |  |
| time_remaining_period_seconds | BIGINT |  |
| time_remaining_period_formatted | TEXT |  |
| minute_remaining_period | BIGINT |  |
| second_remaining_minute | BIGINT |  |
| time_elapsed_game_seconds | BIGINT |  |
| time_elapsed_game_formatted | TEXT |  |
| time_remaining_regulation_seconds | BIGINT |  |
| is_first_minute | BOOLEAN |  |
| is_last_minute | BOOLEAN |  |
| is_regulation | BOOLEAN |  |
| is_overtime | BOOLEAN |  |
| _load_timestamp | TEXT |  |
| _processed_timestamp | TEXT |  |
| _updated_timestamp | TEXT |  |

### dim_skill_tier
**Rows**: 5

| Column | Type | PK |
|--------|------|-----|
| tier_id | INTEGER | ✓ |
| tier_name | TEXT |  |
| min_rating | REAL |  |
| max_rating | REAL |  |
| description | TEXT |  |
| _updated_timestamp | TEXT |  |

### dim_strength
**Rows**: 9

| Column | Type | PK |
|--------|------|-----|
| strength | TEXT | ✓ |
| home_players | INTEGER |  |
| away_players | INTEGER |  |
| is_even | INTEGER |  |
| is_powerplay | INTEGER |  |
| is_shorthanded | INTEGER |  |
| description | TEXT |  |
| _updated_timestamp | TEXT |  |

### dim_team
**Rows**: 26

| Column | Type | PK |
|--------|------|-----|
| team_id | TEXT |  |
| team_name | TEXT |  |
| team_abbr | TEXT |  |
| long_team_name | TEXT |  |
| league | TEXT |  |
| team_color1 | TEXT |  |
| team_color2 | TEXT |  |
| _processed_timestamp | TEXT |  |
| _updated_timestamp | TEXT |  |

### dim_venue
**Rows**: 2

| Column | Type | PK |
|--------|------|-----|
| venue_code | TEXT | ✓ |
| venue_name | TEXT |  |
| is_home | INTEGER |  |
| is_away | INTEGER |  |
| _updated_timestamp | TEXT |  |

### dim_video
**Rows**: 11

| Column | Type | PK |
|--------|------|-----|
| video_key | TEXT | ✓ |
| video_index | INTEGER |  |
| game_id | INTEGER |  |
| video_type | TEXT |  |
| video_category | TEXT |  |
| url_primary | TEXT |  |
| url_backup | TEXT |  |
| url_embed | TEXT |  |
| video_id | TEXT |  |
| extension | TEXT |  |
| description | TEXT |  |
| duration_seconds | INTEGER |  |
| start_offset | INTEGER |  |
| event_index | INTEGER |  |
| event_key | TEXT |  |
| _load_timestamp | TEXT |  |
| _processed_timestamp | TEXT |  |

### dim_zone
**Rows**: 3

| Column | Type | PK |
|--------|------|-----|
| zone_code | TEXT | ✓ |
| zone_name | TEXT |  |
| is_offensive | INTEGER |  |
| is_defensive | INTEGER |  |
| is_neutral | INTEGER |  |
| _updated_timestamp | TEXT |  |

### fact_box_score
**Rows**: 27

| Column | Type | PK |
|--------|------|-----|
| player_game_key | TEXT |  |
| player_game_number | BIGINT |  |
| player_id | TEXT |  |
| player_full_name | TEXT |  |
| display_name | TEXT |  |
| player_team | TEXT |  |
| player_venue | TEXT |  |
| position | TEXT |  |
| skill_rating | FLOAT |  |
| game_id | BIGINT |  |
| goals | BIGINT |  |
| assists_primary | BIGINT |  |
| assists_secondary | BIGINT |  |
| assists | BIGINT |  |
| points | BIGINT |  |
| shots | BIGINT |  |
| shots_on_goal | BIGINT |  |
| passes | BIGINT |  |
| passes_completed | BIGINT |  |
| giveaways | BIGINT |  |
| takeaways | BIGINT |  |
| faceoffs | BIGINT |  |
| faceoff_wins | BIGINT |  |
| stick_checks | BIGINT |  |
| poke_checks | BIGINT |  |
| blocked_shots | BIGINT |  |
| backchecks | BIGINT |  |
| dekes | BIGINT |  |
| puck_recoveries | BIGINT |  |
| is_tracked | BIGINT |  |
| _processed_timestamp | TEXT |  |
| toi_seconds | FLOAT |  |
| plus_minus | BIGINT |  |
| shifts | BIGINT |  |
| toi_formatted | TEXT |  |
| goals_per_60 | FLOAT |  |
| assists_per_60 | FLOAT |  |
| points_per_60 | FLOAT |  |
| shots_per_60 | FLOAT |  |

### fact_events
**Rows**: 1,594

| Column | Type | PK |
|--------|------|-----|
| event_index | FLOAT |  |
| event_key | TEXT |  |
| shift_index | FLOAT |  |
| shift_key | TEXT |  |
| linked_event_index | FLOAT |  |
| sequence_index | FLOAT |  |
| play_index | FLOAT |  |
| event_type | TEXT |  |
| event_detail | TEXT |  |
| event_detail_2 | TEXT |  |
| event_successful | TEXT |  |
| period | FLOAT |  |
| event_start_min | FLOAT |  |
| event_start_sec | FLOAT |  |
| time_total_seconds | FLOAT |  |
| duration | FLOAT |  |
| event_team_zone | TEXT |  |
| game_id | BIGINT |  |
| _processed_timestamp | TEXT |  |
| linked_event_key | TEXT |  |
| sequence_key | TEXT |  |
| play_key | TEXT |  |

### fact_gameroster
**Rows**: 13,960

| Column | Type | PK |
|--------|------|-----|
| game_id | BIGINT |  |
| player_id | TEXT |  |
| player_game_number | TEXT |  |
| player_full_name | TEXT |  |
| display_name | TEXT |  |
| team_name | TEXT |  |
| opp_team_name | TEXT |  |
| team_venue | TEXT |  |
| player_position | TEXT |  |
| goals | BIGINT |  |
| assists | BIGINT |  |
| points | BIGINT |  |
| penalty_minutes | BIGINT |  |
| goals_against | BIGINT |  |
| skill_rating | FLOAT |  |
| player_game_key | TEXT |  |
| _processed_timestamp | TEXT |  |
| _updated_timestamp | TEXT |  |

### fact_xy_events
**Rows**: 1,594

| Column | Type | PK |
|--------|------|-----|
| xy_event_key | TEXT | ✓ |
| xy_event_index | INTEGER |  |
| event_key | TEXT |  |
| event_index | INTEGER |  |
| linked_event_index | INTEGER |  |
| linked_event_key | TEXT |  |
| game_id | INTEGER |  |
| x_coord | REAL |  |
| y_coord | REAL |  |
| rink_box_id | TEXT |  |
| rink_zone_id | TEXT |  |
| danger | TEXT |  |
| zone_name | TEXT |  |
| side | TEXT |  |
| event_type | TEXT |  |
| event_detail | TEXT |  |
| period | INTEGER |  |
| time_total_seconds | REAL |  |
| _processed_timestamp | TEXT |  |

### fact_xy_shots
**Rows**: 181

| Column | Type | PK |
|--------|------|-----|
| xy_shot_key | TEXT | ✓ |
| xy_shot_index | INTEGER |  |
| event_key | TEXT |  |
| event_index | INTEGER |  |
| linked_event_index | INTEGER |  |
| linked_event_key | TEXT |  |
| game_id | INTEGER |  |
| x_coord | REAL |  |
| y_coord | REAL |  |
| shot_distance | REAL |  |
| shot_angle | REAL |  |
| is_goal | INTEGER |  |
| rink_box_id | TEXT |  |
| rink_zone_id | TEXT |  |
| danger | TEXT |  |
| event_type | TEXT |  |
| event_detail | TEXT |  |
| period | INTEGER |  |
| time_total_seconds | REAL |  |
| _processed_timestamp | TEXT |  |

---
## Metadata

### _blb_load_metadata
**Rows**: 2

| Column | Type | PK |
|--------|------|-----|
| load_id | INTEGER | ✓ |
| load_timestamp | TEXT |  |
| source_file | TEXT |  |
| tables_loaded | INTEGER |  |
| total_rows | INTEGER |  |

### _game_load_metadata
**Rows**: 2

| Column | Type | PK |
|--------|------|-----|
| load_id | INTEGER | ✓ |
| game_id | INTEGER |  |
| load_timestamp | TEXT |  |
| source_file | TEXT |  |
| events_rows | INTEGER |  |
| shifts_rows | INTEGER |  |
