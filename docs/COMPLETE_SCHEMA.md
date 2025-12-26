# Complete Database Schema - All Tables and Columns

## Summary

| Layer | Tables | Description |
|-------|--------|-------------|
| Stage | 18 | Raw data from source files |
| Intermediate | 10 | Cleaned, enriched data |
| Datamart | 15 | Final analytical tables |
| Metadata | 2 | ETL tracking |
| **Total** | **45** | |

---
## Stage Layer (stg_*)

Raw data loaded from source files with minimal transformation.

### stg_dim_dates
**Rows**: 4,747

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | datekey | BIGINT |  |
| 1 | date | TEXT |  |
| 2 | day | BIGINT |  |
| 3 | daysuffix | TEXT |  |
| 4 | weekday | BIGINT |  |
| 5 | weekdayname | TEXT |  |
| 6 | weekdayname_short | TEXT |  |
| 7 | weekdayname_firstletter | TEXT |  |
| 8 | dowinmonth | BIGINT |  |
| 9 | dayofyear | BIGINT |  |
| 10 | weekofmonth | BIGINT |  |
| 11 | weekofyear | BIGINT |  |
| 12 | month | BIGINT |  |
| 13 | monthname | TEXT |  |
| 14 | monthname_short | TEXT |  |
| 15 | monthname_firstletter | TEXT |  |
| 16 | quarter | BIGINT |  |
| 17 | quartername | TEXT |  |
| 18 | year | BIGINT |  |
| 19 | mmyyyy | BIGINT |  |
| 20 | monthyear | TEXT |  |
| 21 | isweekend | BIGINT |  |
| 22 | isholiday | BIGINT |  |
| 23 | weekstartdate | TEXT |  |
| 24 | weekenddate | TEXT |  |
| 25 | fourweekperiodstartdate | TEXT |  |
| 26 | fourweekperiodenddate | TEXT |  |
| 27 | _load_timestamp | TEXT |  |
| 28 | _source_file | TEXT |  |

### stg_dim_league
**Rows**: 2

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | league_id | TEXT |  |
| 1 | league | TEXT |  |

### stg_dim_player
**Rows**: 335

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | player_first_name | TEXT |  |
| 1 | player_last_name | TEXT |  |
| 2 | player_full_name | TEXT |  |
| 3 | player_id | TEXT |  |
| 4 | player_primary_position | TEXT |  |
| 5 | current_skill_rating | BIGINT |  |
| 6 | player_hand | FLOAT |  |
| 7 | birth_year | FLOAT |  |
| 8 | player_gender | TEXT |  |
| 9 | highest_beer_league | TEXT |  |
| 10 | player_rating_ly | BIGINT |  |
| 11 | player_notes | FLOAT |  |
| 12 | player_leadership | TEXT |  |
| 13 | player_norad | TEXT |  |
| 14 | player_csaha | FLOAT |  |
| 15 | player_norad_primary_number | FLOAT |  |
| 16 | player_csah_primary_number | FLOAT |  |
| 17 | player_norad_current_team | TEXT |  |
| 18 | player_csah_current_team | FLOAT |  |
| 19 | player_norad_current_team_id | TEXT |  |
| 20 | player_csah_current_team_id | FLOAT |  |
| 21 | other_url | TEXT |  |
| 22 | player_url | TEXT |  |
| 23 | player_image | TEXT |  |
| 24 | random_player_first_name | TEXT |  |
| 25 | random_player_last_name | TEXT |  |
| 26 | random_player_full_name | TEXT |  |

### stg_dim_playerurlref
**Rows**: 543

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | n_player_url | TEXT |  |
| 1 | player_full_name | TEXT |  |
| 2 | n_player_id_2 | TEXT |  |

### stg_dim_randomnames
**Rows**: 486

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | random_full_name | TEXT |  |
| 1 | random_first_name | TEXT |  |
| 2 | random_last_name | TEXT |  |
| 3 | gender | TEXT |  |
| 4 | name_used | TEXT |  |

### stg_dim_rinkboxcoord
**Rows**: 50

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | box_id | TEXT |  |
| 1 | box_id_rev | TEXT |  |
| 2 | x_min | FLOAT |  |
| 3 | x_max | FLOAT |  |
| 4 | y_min | FLOAT |  |
| 5 | y_max | FLOAT |  |
| 6 | area | FLOAT |  |
| 7 | x_description | TEXT |  |
| 8 | y_description | TEXT |  |
| 9 | danger | TEXT |  |
| 10 | zone | TEXT |  |
| 11 | side | TEXT |  |

### stg_dim_rinkcoordzones
**Rows**: 297

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | box_id | TEXT |  |
| 1 | box_id_rev | TEXT |  |
| 2 | x_min | FLOAT |  |
| 3 | x_max | FLOAT |  |
| 4 | y_min | FLOAT |  |
| 5 | y_max | FLOAT |  |
| 6 | y_description | TEXT |  |
| 7 | x_description | TEXT |  |
| 8 | danger | TEXT |  |
| 9 | slot | TEXT |  |
| 10 | zone | TEXT |  |
| 11 | side | TEXT |  |
| 12 | dotside | TEXT |  |
| 13 | depth | TEXT |  |

### stg_dim_schedule
**Rows**: 552

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | index | BIGINT |  |
| 1 | game_id | BIGINT |  |
| 2 | season | BIGINT |  |
| 3 | season_id | TEXT |  |
| 4 | game_url | TEXT |  |
| 5 | home_team_game_id | TEXT |  |
| 6 | away_team_game_id | TEXT |  |
| 7 | date | TEXT |  |
| 8 | game_time | TEXT |  |
| 9 | home_team_name | TEXT |  |
| 10 | away_team_name | TEXT |  |
| 11 | home_team_id | TEXT |  |
| 12 | away_team_id | TEXT |  |
| 13 | head_to_head_id | TEXT |  |
| 14 | game_type | TEXT |  |
| 15 | playoff_round | TEXT |  |
| 16 | last_period_type | TEXT |  |
| 17 | period_length | TEXT |  |
| 18 | ot_period_length | TEXT |  |
| 19 | shootout_rounds | FLOAT |  |
| 20 | home_total_goals | BIGINT |  |
| 21 | away_total_goals | BIGINT |  |
| 22 | home_team_period1_goals | FLOAT |  |
| 23 | home_team_period2_goals | FLOAT |  |
| 24 | home_team_period3_goals | FLOAT |  |
| 25 | home_team_periodOT_goals | FLOAT |  |
| 26 | away_team_period1_goals | FLOAT |  |
| 27 | away_team_period2_goals | FLOAT |  |
| 28 | away_team_period3_goals | FLOAT |  |
| 29 | away_team_periodOT_goals | FLOAT |  |
| 30 | home_team_seeding | FLOAT |  |
| 31 | away_team_seeding | FLOAT |  |
| 32 | home_team_w | BIGINT |  |
| 33 | home_team_l | BIGINT |  |
| 34 | home_team_t | BIGINT |  |
| 35 | home_team_pts | BIGINT |  |
| 36 | away_team_w | BIGINT |  |
| 37 | away_team_l | BIGINT |  |
| 38 | away_team_t | BIGINT |  |
| 39 | away_team_pts | BIGINT |  |
| 40 | video_id | FLOAT |  |
| 41 | video_start_time | FLOAT |  |
| 42 | video_end_time | FLOAT |  |
| 43 | video_title | FLOAT |  |
| 44 | video_url | FLOAT |  |

### stg_dim_season
**Rows**: 9

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | index | BIGINT |  |
| 1 | season_id | TEXT |  |
| 2 | season | BIGINT |  |
| 3 | session | TEXT |  |
| 4 | norad | TEXT |  |
| 5 | csah | TEXT |  |
| 6 | league_id | TEXT |  |
| 7 | league | TEXT |  |
| 8 | start_date | TEXT |  |

### stg_dim_seconds
**Rows**: 4,800

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | time_key | BIGINT |  |
| 1 | period | BIGINT |  |
| 2 | period_name | TEXT |  |
| 3 | period_type | TEXT |  |
| 4 | minute_in_period | BIGINT |  |
| 5 | second_in_minute | BIGINT |  |
| 6 | total_seconds_in_period | BIGINT |  |
| 7 | time_elapsed_period_formatted | TEXT |  |
| 8 | time_remaining_period_seconds | BIGINT |  |
| 9 | time_remaining_period_formatted | TEXT |  |
| 10 | minute_remaining_period | BIGINT |  |
| 11 | second_remaining_minute | BIGINT |  |
| 12 | time_elapsed_game_seconds | BIGINT |  |
| 13 | time_elapsed_game_formatted | TEXT |  |
| 14 | time_remaining_regulation_seconds | BIGINT |  |
| 15 | is_first_minute | BOOLEAN |  |
| 16 | is_last_minute | BOOLEAN |  |
| 17 | is_regulation | BOOLEAN |  |
| 18 | is_overtime | BOOLEAN |  |
| 19 | _load_timestamp | TEXT |  |

### stg_dim_team
**Rows**: 26

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | team_name | TEXT |  |
| 1 | team_id | TEXT |  |
| 2 | norad_team | TEXT |  |
| 3 | csah_team | TEXT |  |
| 4 | league_id | TEXT |  |
| 5 | league | TEXT |  |
| 6 | long_team_name | TEXT |  |
| 7 | team_cd | TEXT |  |
| 8 | team_color1 | TEXT |  |
| 9 | team_color2 | TEXT |  |
| 10 | team_color3 | TEXT |  |
| 11 | team_color4 | TEXT |  |
| 12 | team_logo | TEXT |  |
| 13 | team_url | TEXT |  |

### stg_events_18969
**Rows**: 3,596

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | event_index_flag_ | TEXT |  |
| 1 | sequence_index_flag_ | TEXT |  |
| 2 | play_index_flag_ | TEXT |  |
| 3 | linked_event_index_flag_ | TEXT |  |
| 4 | event_start_min_ | FLOAT |  |
| 5 | event_start_sec_ | FLOAT |  |
| 6 | event_end_min_ | FLOAT |  |
| 7 | event_end_sec_ | FLOAT |  |
| 8 | player_game_number_ | FLOAT |  |
| 9 | event_team_zone_ | TEXT |  |
| 10 | event_type_ | TEXT |  |
| 11 | event_detail_ | TEXT |  |
| 12 | event_detail_2_ | TEXT |  |
| 13 | event_successful_ | TEXT |  |
| 14 | play_detail1_ | TEXT |  |
| 15 | play_detail2_ | TEXT |  |
| 16 | play_detail_successful_ | TEXT |  |
| 17 | pressured_pressurer_ | FLOAT |  |
| 18 | event_index_ | FLOAT |  |
| 19 | linked_event_index_ | FLOAT |  |
| 20 | sequence_index_ | FLOAT |  |
| 21 | play_index_ | FLOAT |  |
| 22 | team_ | TEXT |  |
| 23 | player_game_number | FLOAT |  |
| 24 | role_abrev_binary_ | TEXT |  |
| 25 | period | FLOAT |  |
| 26 | event_index | FLOAT |  |
| 27 | linked_event_index | FLOAT |  |
| 28 | tracking_event_index | FLOAT |  |
| 29 | event_start_min | FLOAT |  |
| 30 | event_start_sec | FLOAT |  |
| 31 | event_end_min | FLOAT |  |
| 32 | event_end_sec | FLOAT |  |
| 33 | role_abrev | TEXT |  |
| 34 | event_team_zone2_ | TEXT |  |
| 35 | event_team_zone | TEXT |  |
| 36 | home_team_zone_ | TEXT |  |
| 37 | away_team_zone_ | TEXT |  |
| 38 | team_venue_ | TEXT |  |
| 39 | team_venue_abv_ | TEXT |  |
| 40 | home_team_zone | TEXT |  |
| 41 | away_team_zone | TEXT |  |
| 42 | team_venue | TEXT |  |
| 43 | team_venue_abv | TEXT |  |
| 44 | side_of_puck | TEXT |  |
| 45 | sequence_index | FLOAT |  |
| 46 | play_index | FLOAT |  |
| 47 | play_detail1 | TEXT |  |
| 48 | play_detail_2 | TEXT |  |
| 49 | play_detail_successful | TEXT |  |
| 50 | pressured_pressurer | FLOAT |  |
| 51 | zone_change_index | FLOAT |  |
| 52 | game_id | FLOAT |  |
| 53 | home_team | TEXT |  |
| 54 | away_team | TEXT |  |
| 55 | Type | TEXT |  |
| 56 | event_detail | TEXT |  |
| 57 | event_detail_2 | TEXT |  |
| 58 | event_successful | TEXT |  |
| 59 | shift_index | FLOAT |  |
| 60 | duration | FLOAT |  |
| 61 | time_start_total_seconds | FLOAT |  |
| 62 | time_end_total_seconds | FLOAT |  |
| 63 | running_intermission_duration | FLOAT |  |
| 64 | period_start_total_running_seconds | FLOAT |  |
| 65 | running_video_time | FLOAT |  |
| 66 | event_running_start | FLOAT |  |
| 67 | event_running_end | FLOAT |  |
| 68 | player_role | TEXT |  |
| 69 | role_number | FLOAT |  |
| 70 | player_id | TEXT |  |
| 71 | player_team | TEXT |  |
| 72 | _game_id | BIGINT |  |
| 73 | _load_timestamp | TEXT |  |

### stg_fact_draft
**Rows**: 160

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | team_id | TEXT |  |
| 1 | skill_rating | BIGINT |  |
| 2 | round | BIGINT |  |
| 3 | player_full_name | TEXT |  |
| 4 | player_id | TEXT |  |
| 5 | team_name | TEXT |  |
| 6 | restricted | BOOLEAN |  |
| 7 | overall_draft_round | BIGINT |  |
| 8 | overall_draft_position | BIGINT |  |
| 9 | unrestricted_draft_position | BIGINT |  |
| 10 | season | BIGINT |  |
| 11 | season_id | TEXT |  |
| 12 | league | TEXT |  |
| 13 | player_draft_id | TEXT |  |

### stg_fact_gameroster
**Rows**: 14,239

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | index | FLOAT |  |
| 1 | game_id | BIGINT |  |
| 2 | team_game_id | TEXT |  |
| 3 | opp_team_game_id | TEXT |  |
| 4 | player_game_id | TEXT |  |
| 5 | team_venue | TEXT |  |
| 6 | team_name | TEXT |  |
| 7 | opp_team_name | TEXT |  |
| 8 | player_game_number | TEXT |  |
| 9 | n_player_url | TEXT |  |
| 10 | player_position | TEXT |  |
| 11 | games_played | TEXT |  |
| 12 | goals | FLOAT |  |
| 13 | assist | FLOAT |  |
| 14 | goals_against | FLOAT |  |
| 15 | pim | FLOAT |  |
| 16 | shutouts | FLOAT |  |
| 17 | team_id | TEXT |  |
| 18 | opp_team_id | TEXT |  |
| 19 | key | TEXT |  |
| 20 | player_full_name | TEXT |  |
| 21 | player_id | TEXT |  |
| 22 | date | TEXT |  |
| 23 | season | BIGINT |  |
| 24 | sub | FLOAT |  |
| 25 | current_team | TEXT |  |
| 26 | skill_rating | BIGINT |  |

### stg_fact_leadership
**Rows**: 28

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | player_full_name | TEXT |  |
| 1 | player_id | TEXT |  |
| 2 | leadership | TEXT |  |
| 3 | skill_rating | BIGINT |  |
| 4 | n_player_url | TEXT |  |
| 5 | team_name | TEXT |  |
| 6 | team_id | TEXT |  |
| 7 | season | BIGINT |  |
| 8 | season_id | TEXT |  |

### stg_fact_playergames
**Rows**: 3,010

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | ID | TEXT |  |
| 1 | Date | TEXT |  |
| 2 | Type | TEXT |  |
| 3 | Team | TEXT |  |
| 4 | Opp | TEXT |  |
| 5 | # | TEXT |  |
| 6 | Player | TEXT |  |
| 7 | Position | TEXT |  |
| 8 | GP | BIGINT |  |
| 9 | G | BIGINT |  |
| 10 | A | BIGINT |  |
| 11 | GA | BIGINT |  |
| 12 | PIM | BIGINT |  |
| 13 | SO | BIGINT |  |
| 14 | Rank | FLOAT |  |
| 15 | ID2 | TEXT |  |
| 16 | ID3 | TEXT |  |
| 17 | Season | TEXT |  |
| 18 | SeasonPlayerID | TEXT |  |

### stg_fact_registration
**Rows**: 191

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | player_full_name | TEXT |  |
| 1 | player_id | TEXT |  |
| 2 | season_id | TEXT |  |
| 3 | season | BIGINT |  |
| 4 | restricted | TEXT |  |
| 5 | email | TEXT |  |
| 6 | position | TEXT |  |
| 7 | norad_experience | TEXT |  |
| 8 | CAF | TEXT |  |
| 9 | highest_beer_league_played | TEXT |  |
| 10 | skill_rating | BIGINT |  |
| 11 | age | BIGINT |  |
| 12 | referred_by | TEXT |  |
| 13 | notes | TEXT |  |
| 14 | sub_yn | TEXT |  |
| 15 | drafted_team_name | TEXT |  |
| 16 | drafted_team_id | TEXT |  |
| 17 | player_season_registration_id | TEXT |  |

### stg_shifts_18969
**Rows**: 98

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | shift_index | BIGINT |  |
| 1 | Period | BIGINT |  |
| 2 | shift_start_min | FLOAT |  |
| 3 | shift_start_sec | FLOAT |  |
| 4 | shift_end_min | FLOAT |  |
| 5 | shift_end_sec | FLOAT |  |
| 6 | shift_start_type | TEXT |  |
| 7 | shift_stop_type | TEXT |  |
| 8 | home_forward_1 | FLOAT |  |
| 9 | home_forward_2 | FLOAT |  |
| 10 | home_forward_3 | FLOAT |  |
| 11 | home_defense_1 | FLOAT |  |
| 12 | home_defense_2 | FLOAT |  |
| 13 | home_xtra | FLOAT |  |
| 14 | home_goalie | FLOAT |  |
| 15 | away_forward_1 | FLOAT |  |
| 16 | away_forward_2 | FLOAT |  |
| 17 | away_forward_3 | FLOAT |  |
| 18 | away_defense_1 | FLOAT |  |
| 19 | away_defense_2 | FLOAT |  |
| 20 | away_xtra | FLOAT |  |
| 21 | away_goalie | FLOAT |  |
| 22 | stoppage_time | FLOAT |  |
| 23 | home_ozone_start | FLOAT |  |
| 24 | home_ozone_end | FLOAT |  |
| 25 | home_dzone_start | FLOAT |  |
| 26 | home_dzone_end | FLOAT |  |
| 27 | home_nzone_start | FLOAT |  |
| 28 | home_nzone_end | FLOAT |  |
| 29 | game_id | BIGINT |  |
| 30 | home_team | TEXT |  |
| 31 | away_team | TEXT |  |
| 32 | shift_start_total_seconds | FLOAT |  |
| 33 | shift_end_total_seconds | FLOAT |  |
| 34 | shift_duration | FLOAT |  |
| 35 | home_team_strength | FLOAT |  |
| 36 | away_team_strength | FLOAT |  |
| 37 | home_team_en | FLOAT |  |
| 38 | away_team_en | FLOAT |  |
| 39 | home_team_pk | FLOAT |  |
| 40 | home_team_pp | FLOAT |  |
| 41 | away_team_pp | FLOAT |  |
| 42 | away_team_pk | FLOAT |  |
| 43 | situation | TEXT |  |
| 44 | strength | TEXT |  |
| 45 | home_goals | BIGINT |  |
| 46 | away_goals | BIGINT |  |
| 47 | home_team_plus | FLOAT |  |
| 48 | home_team_minus | FLOAT |  |
| 49 | away_team_plus | FLOAT |  |
| 50 | away_team_minus | FLOAT |  |
| 51 | period_start_total_running_seconds | BIGINT |  |
| 52 | running_video_time | BIGINT |  |
| 53 | shift_start_running_time | BIGINT |  |
| 54 | shift_end_running_time | BIGINT |  |
| 55 | _game_id | BIGINT |  |
| 56 | _load_timestamp | TEXT |  |

---
## Intermediate Layer (int_*)

Cleaned, enriched, and transformed data.

### int_dim_dates
**Rows**: 4,747

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | date_key | INT |  |
| 1 | full_date | TEXT |  |
| 2 | day_of_month | INT |  |
| 3 | day_suffix | TEXT |  |
| 4 | day_of_week_num | INT |  |
| 5 | day_name | TEXT |  |
| 6 | day_name_short | TEXT |  |
| 7 | day_of_year | INT |  |
| 8 | week_of_month | INT |  |
| 9 | week_of_year | INT |  |
| 10 | week_start_date | TEXT |  |
| 11 | week_end_date | TEXT |  |
| 12 | month_num | INT |  |
| 13 | month_name | TEXT |  |
| 14 | month_name_short | TEXT |  |
| 15 | month_year_key | INT |  |
| 16 | month_year_label | TEXT |  |
| 17 | quarter_num | INT |  |
| 18 | quarter_name | TEXT |  |
| 19 | year_num | INT |  |
| 20 | is_weekend | TEXT |  |
| 21 | is_holiday | TEXT |  |
| 22 | four_week_start | TEXT |  |
| 23 | four_week_end | TEXT |  |
| 24 | _processed_timestamp | TEXT |  |
| 25 | _updated_timestamp | TEXT |  |

### int_dim_player
**Rows**: 335

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | player_id | TEXT |  |
| 1 | player_full_name | TEXT |  |
| 2 | display_name | TEXT |  |
| 3 | primary_position | TEXT |  |
| 4 | skill_rating | REAL |  |
| 5 | player_hand | REAL |  |
| 6 | birth_year | REAL |  |
| 7 | _processed_timestamp | TEXT |  |
| 8 | _updated_timestamp | TEXT |  |

### int_dim_schedule
**Rows**: 552

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | game_id | INT |  |
| 1 | home_team | TEXT |  |
| 2 | away_team | TEXT |  |
| 3 | home_team_id | TEXT |  |
| 4 | away_team_id | TEXT |  |
| 5 | game_date | TEXT |  |
| 6 | season_id | TEXT |  |
| 7 | game_type | TEXT |  |
| 8 | playoff_round | TEXT |  |
| 9 | home_score | INT |  |
| 10 | away_score | INT |  |
| 11 | winner | TEXT |  |
| 12 | video_id | REAL |  |
| 13 | video_url | REAL |  |
| 14 | _processed_timestamp | TEXT |  |
| 15 | _updated_timestamp | TEXT |  |

### int_dim_seconds
**Rows**: 4,800

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | time_key | BIGINT |  |
| 1 | period | BIGINT |  |
| 2 | period_name | TEXT |  |
| 3 | period_type | TEXT |  |
| 4 | minute_in_period | BIGINT |  |
| 5 | second_in_minute | BIGINT |  |
| 6 | total_seconds_in_period | BIGINT |  |
| 7 | time_elapsed_period_formatted | TEXT |  |
| 8 | time_remaining_period_seconds | BIGINT |  |
| 9 | time_remaining_period_formatted | TEXT |  |
| 10 | minute_remaining_period | BIGINT |  |
| 11 | second_remaining_minute | BIGINT |  |
| 12 | time_elapsed_game_seconds | BIGINT |  |
| 13 | time_elapsed_game_formatted | TEXT |  |
| 14 | time_remaining_regulation_seconds | BIGINT |  |
| 15 | is_first_minute | BOOLEAN |  |
| 16 | is_last_minute | BOOLEAN |  |
| 17 | is_regulation | BOOLEAN |  |
| 18 | is_overtime | BOOLEAN |  |
| 19 | _load_timestamp | TEXT |  |
| 20 | _processed_timestamp | TEXT |  |
| 21 | _updated_timestamp | TEXT |  |

### int_dim_team
**Rows**: 26

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | team_id | TEXT |  |
| 1 | team_name | TEXT |  |
| 2 | team_abbr | TEXT |  |
| 3 | long_team_name | TEXT |  |
| 4 | league | TEXT |  |
| 5 | team_color1 | TEXT |  |
| 6 | team_color2 | TEXT |  |
| 7 | _processed_timestamp | TEXT |  |
| 8 | _updated_timestamp | TEXT |  |

### int_event_players_18969
**Rows**: 3,139

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | event_index | REAL |  |
| 1 | event_key | TEXT |  |
| 2 | player_game_number | REAL |  |
| 3 | player_id | TEXT |  |
| 4 | player_team | TEXT |  |
| 5 | player_game_key | TEXT |  |
| 6 | player_role | TEXT |  |
| 7 | play_detail1 | TEXT |  |
| 8 | play_detail_2 | TEXT |  |
| 9 | play_detail_successful | TEXT |  |
| 10 | is_primary_player | TEXT |  |
| 11 | is_event_team | TEXT |  |
| 12 | event_player_key | TEXT |  |
| 13 | game_id | TEXT |  |
| 14 | _processed_timestamp | TEXT |  |

### int_events_18969
**Rows**: 1,594

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | event_index | REAL |  |
| 1 | event_key | TEXT |  |
| 2 | shift_index | REAL |  |
| 3 | shift_key | TEXT |  |
| 4 | linked_event_index | REAL |  |
| 5 | sequence_index | REAL |  |
| 6 | play_index | REAL |  |
| 7 | event_type | TEXT |  |
| 8 | event_detail | TEXT |  |
| 9 | event_detail_2 | TEXT |  |
| 10 | event_successful | TEXT |  |
| 11 | period | REAL |  |
| 12 | event_start_min | REAL |  |
| 13 | event_start_sec | REAL |  |
| 14 | time_total_seconds | REAL |  |
| 15 | duration | REAL |  |
| 16 | event_team_zone | TEXT |  |
| 17 | game_id | TEXT |  |
| 18 | _processed_timestamp | TEXT |  |

### int_fact_gameroster
**Rows**: 13,960

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | game_id | INT |  |
| 1 | player_id | TEXT |  |
| 2 | player_game_number | TEXT |  |
| 3 | player_full_name | TEXT |  |
| 4 | display_name | TEXT |  |
| 5 | team_name | TEXT |  |
| 6 | opp_team_name | TEXT |  |
| 7 | team_venue | TEXT |  |
| 8 | player_position | TEXT |  |
| 9 | goals | INT |  |
| 10 | assists | INT |  |
| 11 | points | INT |  |
| 12 | penalty_minutes | INT |  |
| 13 | goals_against | INT |  |
| 14 | skill_rating | REAL |  |
| 15 | player_game_key | TEXT |  |
| 16 | _processed_timestamp | TEXT |  |
| 17 | _updated_timestamp | TEXT |  |

### int_game_players_18969
**Rows**: 27

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | player_game_number | TEXT |  |
| 1 | player_id | TEXT |  |
| 2 | player_game_key | TEXT |  |
| 3 | player_full_name | TEXT |  |
| 4 | display_name | TEXT |  |
| 5 | player_team | TEXT |  |
| 6 | player_venue | TEXT |  |
| 7 | position | TEXT |  |
| 8 | skill_rating | REAL |  |
| 9 | game_id | TEXT |  |
| 10 | _processed_timestamp | TEXT |  |

### int_shifts_18969
**Rows**: 98

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | shift_index | INT |  |
| 1 | shift_key | TEXT |  |
| 2 | period | INT |  |
| 3 | shift_start_total_seconds | REAL |  |
| 4 | shift_end_total_seconds | REAL |  |
| 5 | shift_duration | REAL |  |
| 6 | shift_start_type | TEXT |  |
| 7 | shift_stop_type | TEXT |  |
| 8 | situation | TEXT |  |
| 9 | strength | TEXT |  |
| 10 | home_strength | INT |  |
| 11 | away_strength | INT |  |
| 12 | home_goals | INT |  |
| 13 | away_goals | INT |  |
| 14 | home_plus | INT |  |
| 15 | home_minus | INT |  |
| 16 | away_plus | INT |  |
| 17 | away_minus | INT |  |
| 18 | home_forward_1 | REAL |  |
| 19 | home_forward_2 | REAL |  |
| 20 | home_forward_3 | REAL |  |
| 21 | home_defense_1 | REAL |  |
| 22 | home_defense_2 | REAL |  |
| 23 | home_goalie | REAL |  |
| 24 | away_forward_1 | REAL |  |
| 25 | away_forward_2 | REAL |  |
| 26 | away_forward_3 | REAL |  |
| 27 | away_defense_1 | REAL |  |
| 28 | away_defense_2 | REAL |  |
| 29 | away_goalie | REAL |  |
| 30 | game_id | TEXT |  |
| 31 | _processed_timestamp | TEXT |  |

---
## Datamart Layer

Final analytical tables for Power BI consumption.

### dim_dates
**Rows**: 4,747

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | date_key | BIGINT |  |
| 1 | full_date | TEXT |  |
| 2 | day_of_month | BIGINT |  |
| 3 | day_suffix | TEXT |  |
| 4 | day_of_week_num | BIGINT |  |
| 5 | day_name | TEXT |  |
| 6 | day_name_short | TEXT |  |
| 7 | day_of_year | BIGINT |  |
| 8 | week_of_month | BIGINT |  |
| 9 | week_of_year | BIGINT |  |
| 10 | week_start_date | TEXT |  |
| 11 | week_end_date | TEXT |  |
| 12 | month_num | BIGINT |  |
| 13 | month_name | TEXT |  |
| 14 | month_name_short | TEXT |  |
| 15 | month_year_key | BIGINT |  |
| 16 | month_year_label | TEXT |  |
| 17 | quarter_num | BIGINT |  |
| 18 | quarter_name | TEXT |  |
| 19 | year_num | BIGINT |  |
| 20 | is_weekend | BIGINT |  |
| 21 | is_holiday | BIGINT |  |
| 22 | four_week_start | TEXT |  |
| 23 | four_week_end | TEXT |  |
| 24 | _processed_timestamp | TEXT |  |
| 25 | _updated_timestamp | TEXT |  |

### dim_event_type
**Rows**: 7

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | event_type | TEXT | ✓ |
| 1 | event_category | TEXT |  |
| 2 | is_shot | INTEGER |  |
| 3 | is_possession | INTEGER |  |
| 4 | is_turnover | INTEGER |  |
| 5 | is_penalty | INTEGER |  |
| 6 | sort_order | INTEGER |  |
| 7 | _updated_timestamp | TEXT |  |

### dim_period
**Rows**: 5

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | period_id | INTEGER | ✓ |
| 1 | period_name | TEXT |  |
| 2 | period_abbr | TEXT |  |
| 3 | is_overtime | INTEGER |  |
| 4 | is_shootout | INTEGER |  |
| 5 | sort_order | INTEGER |  |
| 6 | _updated_timestamp | TEXT |  |

### dim_player
**Rows**: 335

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | player_id | TEXT |  |
| 1 | player_full_name | TEXT |  |
| 2 | display_name | TEXT |  |
| 3 | primary_position | TEXT |  |
| 4 | skill_rating | FLOAT |  |
| 5 | player_hand | FLOAT |  |
| 6 | birth_year | FLOAT |  |
| 7 | _processed_timestamp | TEXT |  |
| 8 | _updated_timestamp | TEXT |  |

### dim_position
**Rows**: 8

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | position_code | TEXT | ✓ |
| 1 | position_name | TEXT |  |
| 2 | position_type | TEXT |  |
| 3 | is_forward | INTEGER |  |
| 4 | is_defense | INTEGER |  |
| 5 | is_goalie | INTEGER |  |
| 6 | _updated_timestamp | TEXT |  |

### dim_schedule
**Rows**: 552

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | game_id | BIGINT |  |
| 1 | home_team | TEXT |  |
| 2 | away_team | TEXT |  |
| 3 | home_team_id | TEXT |  |
| 4 | away_team_id | TEXT |  |
| 5 | game_date | TEXT |  |
| 6 | season_id | TEXT |  |
| 7 | game_type | TEXT |  |
| 8 | playoff_round | TEXT |  |
| 9 | home_score | BIGINT |  |
| 10 | away_score | BIGINT |  |
| 11 | winner | TEXT |  |
| 12 | video_id | FLOAT |  |
| 13 | video_url | FLOAT |  |
| 14 | _processed_timestamp | TEXT |  |
| 15 | _updated_timestamp | TEXT |  |

### dim_seconds
**Rows**: 4,800

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | time_key | BIGINT |  |
| 1 | period | BIGINT |  |
| 2 | period_name | TEXT |  |
| 3 | period_type | TEXT |  |
| 4 | minute_in_period | BIGINT |  |
| 5 | second_in_minute | BIGINT |  |
| 6 | total_seconds_in_period | BIGINT |  |
| 7 | time_elapsed_period_formatted | TEXT |  |
| 8 | time_remaining_period_seconds | BIGINT |  |
| 9 | time_remaining_period_formatted | TEXT |  |
| 10 | minute_remaining_period | BIGINT |  |
| 11 | second_remaining_minute | BIGINT |  |
| 12 | time_elapsed_game_seconds | BIGINT |  |
| 13 | time_elapsed_game_formatted | TEXT |  |
| 14 | time_remaining_regulation_seconds | BIGINT |  |
| 15 | is_first_minute | BOOLEAN |  |
| 16 | is_last_minute | BOOLEAN |  |
| 17 | is_regulation | BOOLEAN |  |
| 18 | is_overtime | BOOLEAN |  |
| 19 | _load_timestamp | TEXT |  |
| 20 | _processed_timestamp | TEXT |  |
| 21 | _updated_timestamp | TEXT |  |

### dim_skill_tier
**Rows**: 5

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | tier_id | INTEGER | ✓ |
| 1 | tier_name | TEXT |  |
| 2 | min_rating | REAL |  |
| 3 | max_rating | REAL |  |
| 4 | description | TEXT |  |
| 5 | _updated_timestamp | TEXT |  |

### dim_strength
**Rows**: 9

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | strength | TEXT | ✓ |
| 1 | home_players | INTEGER |  |
| 2 | away_players | INTEGER |  |
| 3 | is_even | INTEGER |  |
| 4 | is_powerplay | INTEGER |  |
| 5 | is_shorthanded | INTEGER |  |
| 6 | description | TEXT |  |
| 7 | _updated_timestamp | TEXT |  |

### dim_team
**Rows**: 26

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | team_id | TEXT |  |
| 1 | team_name | TEXT |  |
| 2 | team_abbr | TEXT |  |
| 3 | long_team_name | TEXT |  |
| 4 | league | TEXT |  |
| 5 | team_color1 | TEXT |  |
| 6 | team_color2 | TEXT |  |
| 7 | _processed_timestamp | TEXT |  |
| 8 | _updated_timestamp | TEXT |  |

### dim_venue
**Rows**: 2

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | venue_code | TEXT | ✓ |
| 1 | venue_name | TEXT |  |
| 2 | is_home | INTEGER |  |
| 3 | is_away | INTEGER |  |
| 4 | _updated_timestamp | TEXT |  |

### dim_zone
**Rows**: 3

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | zone_code | TEXT | ✓ |
| 1 | zone_name | TEXT |  |
| 2 | is_offensive | INTEGER |  |
| 3 | is_defensive | INTEGER |  |
| 4 | is_neutral | INTEGER |  |
| 5 | _updated_timestamp | TEXT |  |

### fact_box_score
**Rows**: 27

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | player_game_key | TEXT |  |
| 1 | player_game_number | BIGINT |  |
| 2 | player_id | TEXT |  |
| 3 | player_full_name | TEXT |  |
| 4 | display_name | TEXT |  |
| 5 | player_team | TEXT |  |
| 6 | player_venue | TEXT |  |
| 7 | position | TEXT |  |
| 8 | skill_rating | FLOAT |  |
| 9 | game_id | BIGINT |  |
| 10 | goals | BIGINT |  |
| 11 | assists_primary | BIGINT |  |
| 12 | assists_secondary | BIGINT |  |
| 13 | assists | BIGINT |  |
| 14 | points | BIGINT |  |
| 15 | shots | BIGINT |  |
| 16 | shots_on_goal | BIGINT |  |
| 17 | passes | BIGINT |  |
| 18 | passes_completed | BIGINT |  |
| 19 | giveaways | BIGINT |  |
| 20 | takeaways | BIGINT |  |
| 21 | faceoffs | BIGINT |  |
| 22 | faceoff_wins | BIGINT |  |
| 23 | stick_checks | BIGINT |  |
| 24 | poke_checks | BIGINT |  |
| 25 | blocked_shots | BIGINT |  |
| 26 | backchecks | BIGINT |  |
| 27 | dekes | BIGINT |  |
| 28 | puck_recoveries | BIGINT |  |
| 29 | is_tracked | BIGINT |  |
| 30 | _processed_timestamp | TEXT |  |
| 31 | toi_seconds | FLOAT |  |
| 32 | plus_minus | BIGINT |  |
| 33 | shifts | BIGINT |  |
| 34 | toi_formatted | TEXT |  |
| 35 | goals_per_60 | FLOAT |  |
| 36 | assists_per_60 | FLOAT |  |
| 37 | points_per_60 | FLOAT |  |
| 38 | shots_per_60 | FLOAT |  |

### fact_events
**Rows**: 1,594

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | event_index | FLOAT |  |
| 1 | event_key | TEXT |  |
| 2 | shift_index | FLOAT |  |
| 3 | shift_key | TEXT |  |
| 4 | linked_event_index | FLOAT |  |
| 5 | sequence_index | FLOAT |  |
| 6 | play_index | FLOAT |  |
| 7 | event_type | TEXT |  |
| 8 | event_detail | TEXT |  |
| 9 | event_detail_2 | TEXT |  |
| 10 | event_successful | TEXT |  |
| 11 | period | FLOAT |  |
| 12 | event_start_min | FLOAT |  |
| 13 | event_start_sec | FLOAT |  |
| 14 | time_total_seconds | FLOAT |  |
| 15 | duration | FLOAT |  |
| 16 | event_team_zone | TEXT |  |
| 17 | game_id | BIGINT |  |
| 18 | _processed_timestamp | TEXT |  |

### fact_gameroster
**Rows**: 13,960

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | game_id | BIGINT |  |
| 1 | player_id | TEXT |  |
| 2 | player_game_number | TEXT |  |
| 3 | player_full_name | TEXT |  |
| 4 | display_name | TEXT |  |
| 5 | team_name | TEXT |  |
| 6 | opp_team_name | TEXT |  |
| 7 | team_venue | TEXT |  |
| 8 | player_position | TEXT |  |
| 9 | goals | BIGINT |  |
| 10 | assists | BIGINT |  |
| 11 | points | BIGINT |  |
| 12 | penalty_minutes | BIGINT |  |
| 13 | goals_against | BIGINT |  |
| 14 | skill_rating | FLOAT |  |
| 15 | player_game_key | TEXT |  |
| 16 | _processed_timestamp | TEXT |  |
| 17 | _updated_timestamp | TEXT |  |

---
## Metadata Tables

Internal ETL tracking tables.

### _blb_load_metadata
**Rows**: 1

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | load_id | INTEGER | ✓ |
| 1 | load_timestamp | TEXT |  |
| 2 | source_file | TEXT |  |
| 3 | tables_loaded | INTEGER |  |
| 4 | total_rows | INTEGER |  |

### _game_load_metadata
**Rows**: 1

| # | Column | Data Type | PK |
|---|--------|-----------|-----|
| 0 | load_id | INTEGER | ✓ |
| 1 | game_id | INTEGER |  |
| 2 | load_timestamp | TEXT |  |
| 3 | source_file | TEXT |  |
| 4 | events_rows | INTEGER |  |
| 5 | shifts_rows | INTEGER |  |
