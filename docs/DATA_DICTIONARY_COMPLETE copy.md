# BENCHSIGHT DATA DICTIONARY

**Version:** 2.0.0  
**Last Updated:** December 27, 2025  
**Total Tables:** 36

---

## TABLE SUMMARY

| # | Table | Type | Rows | Description |
|---|-------|------|------|-------------|
| 1 | dim_player | Core Dim | 335 | Player master data |
| 2 | dim_team | Core Dim | 26 | Team master data |
| 3 | dim_schedule | Core Dim | 552 | All games scheduled |
| 4 | dim_season | Core Dim | 9 | Season definitions |
| 5 | dim_league | Core Dim | 2 | League definitions |
| 6 | dim_rinkboxcoord | Core Dim | 50 | Rink box coordinates |
| 7 | dim_rinkcoordzones | Core Dim | 297 | Rink zone coordinates |
| 8 | dim_video | Core Dim | 10 | Video links per game |
| 9 | dim_event_type | Lookup | 7 | Event type categories |
| 10 | dim_event_detail | Lookup | 59 | Event detail subtypes |
| 11 | dim_play_detail | Lookup | 81 | Play detail types |
| 12 | dim_strength | Lookup | 9 | Game strength situations |
| 13 | dim_situation | Lookup | 5 | PP/PK/EN situations |
| 14 | dim_position | Lookup | 9 | Player positions (incl. X=Extra) |
| 15 | dim_zone | Lookup | 3 | Ice zones (OZ/NZ/DZ) |
| 16 | dim_period | Lookup | 5 | Period definitions |
| 17 | dim_venue | Lookup | 2 | Home/Away |
| 18 | dim_shot_type | Lookup | 6 | Shot type categories |
| 19 | dim_pass_type | Lookup | 8 | Pass type categories |
| 20 | dim_shift_type | Lookup | 6 | Shift start/stop types |
| 21 | dim_skill_tier | Lookup | 5 | Skill rating tiers |
| 22 | dim_player_role | Lookup | 7 | Player roles in events |
| 23 | dim_danger_zone | Lookup | 3 | Shot danger zones |
| 24 | dim_time_bucket | Lookup | 4 | Time period buckets |
| 25 | fact_gameroster | Fact | 14,239 | Players in each game |
| 26 | fact_events_tracking | Fact | 24,089 | Events (wide format) |
| 27 | fact_events_long | Fact | 24,090 | Events (long format) |
| 28 | fact_event_players_tracking | Fact | 3,133 | Player-event junction |
| 29 | fact_shifts_tracking | Fact | 770 | Shifts (wide format) |
| 30 | fact_shift_players_tracking | Fact | 1,137 | Player-shift junction |
| 31 | fact_playergames | Fact | 3,010 | Player game stats |
| 32 | fact_box_score_tracking | Fact | 27 | Detailed box scores |
| 33 | fact_linked_events_tracking | Fact | 230 | Event chains |
| 34 | fact_sequences_tracking | Fact | 5 | Event sequences |
| 35 | fact_plays_tracking | Fact | 5 | Play groupings |
| 36 | fact_event_coordinates | Fact | 0 | XY coordinates (from tracker) |

---

## CORE DIMENSION TABLES

### dim_player (335 rows)
Player master data.

| Column | Type | Description |
|--------|------|-------------|
| player_id | text PK | Unique player identifier (e.g., P100001) |
| player_first_name | text | First name |
| player_last_name | text | Last name |
| player_full_name | text | Full name |
| player_primary_position | text | Primary position (F/D/G) |
| current_skill_rating | float | Skill rating 1-6 |
| player_hand | text | L/R |
| birth_year | int | Birth year |
| player_gender | text | M/F |

### dim_team (26 rows)
Team master data.

| Column | Type | Description |
|--------|------|-------------|
| team_id | text PK | Unique team identifier (e.g., N10001) |
| team_name | text | Short name (e.g., Velodrome) |
| long_team_name | text | Full team name |
| team_color1 | text | Primary color hex |
| team_color2 | text | Secondary color hex |
| league_id | text | FK to dim_league |

### dim_schedule (552 rows)
All scheduled games.

| Column | Type | Description |
|--------|------|-------------|
| game_id | int PK | Unique game identifier |
| date | date | Game date |
| home_team_name | text | Home team |
| away_team_name | text | Away team |
| home_total_goals | int | Final home score |
| away_total_goals | int | Final away score |
| video_url | text | YouTube link if available |

### dim_video (10 rows)
Video links per game.

| Column | Type | Description |
|--------|------|-------------|
| game_id | int | FK to dim_schedule |
| video_type | text | Full_Ice, Broadcast, etc. |
| url_1 | text | Primary video URL |
| video_id | text | YouTube video ID |

---

## LOOKUP DIMENSION TABLES

### dim_event_type (7 rows)
| event_type | event_category |
|------------|----------------|
| Shot | scoring |
| Pass | possession |
| Faceoff | possession |
| Turnover | possession |
| Zone | transition |
| Save | goaltending |
| Penalty | infraction |

### dim_position (9 rows)
| position_code | position_name | position_type |
|---------------|---------------|---------------|
| C | Center | Forward |
| LW | Left Wing | Forward |
| RW | Right Wing | Forward |
| F | Forward | Forward |
| D | Defense | Defense |
| LD | Left Defense | Defense |
| RD | Right Defense | Defense |
| G | Goalie | Goalie |
| X | Extra | Extra |

### dim_strength (9 rows)
| strength | description |
|----------|-------------|
| 5v5 | Even strength |
| 5v4 | Power play |
| 4v5 | Penalty kill |
| 4v4 | 4-on-4 |
| 3v3 | Overtime |
| 6v5 | Extra attacker |
| 5v6 | Pulled goalie against |

### dim_zone (3 rows)
| zone_code | zone_name |
|-----------|-----------|
| OZ | Offensive Zone |
| NZ | Neutral Zone |
| DZ | Defensive Zone |

---

## FACT TABLES

### fact_events_tracking (24,089 rows) - WIDE FORMAT
One row per event. Primary tracking table.

| Column | Type | Description |
|--------|------|-------------|
| id | serial PK | Auto-increment ID |
| game_id | int | FK to dim_schedule |
| event_index | int | Event number within game |
| shift_index | int | FK to fact_shifts_tracking |
| period | int | Period number (1-3, OT) |
| type | text | Event type (Shot, Pass, etc.) |
| event_detail | text | Detail 1 (e.g., OnNet, Missed) |
| event_detail_2 | text | Detail 2 (e.g., Wrist, Slap) |
| event_successful | text | Success flag |
| event_team_zone | text | Zone where event occurred |
| team_venue | text | home/away |
| player_game_number | text | Jersey number |
| time_start_total_seconds | int | Clock time in seconds |

### fact_shifts_tracking (770 rows) - WIDE FORMAT
One row per shift. Contains all on-ice players.

| Column | Type | Description |
|--------|------|-------------|
| id | serial PK | Auto-increment ID |
| game_id | int | FK to dim_schedule |
| shift_index | int | Shift number within game |
| period | int | Period number |
| shift_start_total_seconds | int | Start time |
| shift_end_total_seconds | int | End time |
| shift_duration | int | Duration in seconds |
| situation | text | Even/PP/PK |
| strength | text | 5v5, 5v4, etc. |
| home_forward_1 | text | Home F1 jersey # |
| home_forward_2 | text | Home F2 jersey # |
| home_forward_3 | text | Home F3 jersey # |
| home_defense_1 | text | Home D1 jersey # |
| home_defense_2 | text | Home D2 jersey # |
| home_goalie | text | Home G jersey # |
| home_xtra | text | Home extra attacker # |
| away_forward_1 | text | Away F1 jersey # |
| away_forward_2 | text | Away F2 jersey # |
| away_forward_3 | text | Away F3 jersey # |
| away_defense_1 | text | Away D1 jersey # |
| away_defense_2 | text | Away D2 jersey # |
| away_goalie | text | Away G jersey # |
| away_xtra | text | Away extra attacker # |

### fact_shift_players_tracking (1,137 rows) - LONG FORMAT
One row per player per shift.

| Column | Type | Description |
|--------|------|-------------|
| shift_index | int | FK to fact_shifts_tracking |
| player_game_number | text | Jersey number |
| player_venue | text | home/away |
| position_slot | text | F1, F2, F3, D1, D2, G, X |
| game_id | int | FK to dim_schedule |
| skill_rating | float | Player skill |

### fact_event_coordinates (0 rows) - NEW
XY tracking data from tracker UI.

| Column | Type | Description |
|--------|------|-------------|
| event_id | text | FK to fact_events_tracking |
| game_id | int | FK to dim_schedule |
| entity_type | text | event_player, opp_player, puck |
| entity_slot | int | 1-6 for players, 1 for puck |
| sequence | int | Point sequence (1, 2, 3...) |
| x | float | X coordinate (0-200) |
| y | float | Y coordinate (0-85) |

### fact_gameroster (14,239 rows)
Who played in each game.

| Column | Type | Description |
|--------|------|-------------|
| game_id | int | FK to dim_schedule |
| player_id | text | FK to dim_player |
| team_venue | text | home/away |
| player_game_number | text | Jersey number for this game |
| player_position | text | Position played |
| goals | int | Goals scored |
| assist | int | Assists |
| skill_rating | float | Skill rating |

### fact_linked_events_tracking (230 rows)
Event chains (related events).

| Column | Type | Description |
|--------|------|-------------|
| linked_event_index | int | Chain identifier |
| first_event | int | First event in chain |
| last_event | int | Last event in chain |
| event_count | int | Number of events |
| event_types | text | Comma-separated types |
| chain_type | text | Type of chain |
| game_id | int | FK to dim_schedule |

---

## RELATIONSHIPS

```
dim_player ──────────────┐
                         │
dim_team ────────────────┼──► fact_gameroster
                         │
dim_schedule ────────────┘
      │
      ├──► fact_events_tracking ──► fact_event_players_tracking
      │           │
      │           └──► fact_event_coordinates
      │
      ├──► fact_shifts_tracking ──► fact_shift_players_tracking
      │
      ├──► fact_linked_events_tracking
      │
      ├──► dim_video
      │
      └──► fact_box_score_tracking
```

---

## TRACKER UI OUTPUT

The tracker exports data matching these tables exactly:

| Tracker Export | Target Table |
|----------------|--------------|
| events sheet | fact_events_tracking |
| shifts sheet | fact_shifts_tracking |
| XY clicks | fact_event_coordinates |

---

*Generated: December 27, 2025*
