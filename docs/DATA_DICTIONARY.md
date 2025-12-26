# Data Dictionary

## Overview

This document describes all tables, columns, and their meanings in the hockey analytics data mart.

---

## dim_player

**Description**: Master player dimension table containing persistent player attributes.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| player_id | VARCHAR(20) | Unique player identifier | P100001 |
| player_full_name | VARCHAR(200) | Full player name | Sam Downs |
| display_name | VARCHAR(200) | Anonymized display name | Joshua Walton |
| player_primary_position | VARCHAR(20) | Primary position | Forward, Defense, Goalie |
| current_skill_rating | DECIMAL(3,1) | Skill rating (2-6) | 5 |
| player_hand | VARCHAR(10) | Dominant hand | L, R |
| birth_year | INTEGER | Year of birth | 1986 |
| player_gender | CHAR(1) | Gender | M, F |

---

## dim_team

**Description**: Team reference data.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| team_id | VARCHAR(20) | Unique team identifier | N10001 |
| team_name | VARCHAR(100) | Short team name | Amos |
| long_team_name | VARCHAR(200) | Full team name | AMOS |
| team_color1 | VARCHAR(20) | Primary color hex | #641C28 |
| league_id | VARCHAR(10) | League identifier | N |
| league | VARCHAR(50) | League name | NORAD |

---

## dim_game_players

**Description**: Players in each game with game-specific attributes.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| player_game_key | VARCHAR(30) | PK: game_id + player_number | 18969_45 |
| game_id | INTEGER | Game identifier | 18969 |
| player_game_number | INTEGER | Jersey number | 45 |
| player_id | VARCHAR(20) | FK to dim_player | P100001 |
| player_team | VARCHAR(100) | Team in this game | Platinum |
| player_venue | VARCHAR(10) | Home or away | home, away |
| position | VARCHAR(20) | Position this game | forward |
| skill_rating | DECIMAL(3,1) | Skill rating | 6 |

---

## fact_events

**Description**: Game events with skill context and ML features.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| event_key | VARCHAR(30) | PK: game_id + event_index | 18969_1189 |
| event_index | INTEGER | Event sequence number | 1189 |
| Type | VARCHAR(50) | Event type | Shot, Pass, Faceoff |
| event_detail | VARCHAR(100) | Event detail | Shot_OnNetSaved |
| event_detail_2 | VARCHAR(100) | Secondary detail | Shot-Wrist |
| event_successful | CHAR(1) | Success indicator | s, u |
| event_team | VARCHAR(100) | Team making event | Platinum |
| event_player_1_skill | DECIMAL(3,1) | Primary player skill | 6 |
| opp_player_1_skill | DECIMAL(3,1) | Opponent player skill | 4 |
| player_skill_differential | DECIMAL(3,1) | Skill diff (player - opp) | 2 |
| linked_event_index | INTEGER | Chain ID for linked events | 9004 |
| sequence_index | INTEGER | Possession sequence ID | 5001 |
| play_index | INTEGER | Play ID | 6001 |
| is_goal | INTEGER | Is this a goal? | 0, 1 |
| is_goal_sequence | INTEGER | Within 5 events of goal? | 0, 1 |
| events_to_next_goal | INTEGER | Events until next goal | 15 |

---

## fact_event_players

**Description**: Players involved in each event with roles and play details.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| event_player_key | VARCHAR(50) | PK | 18969_1189_45 |
| player_role | VARCHAR(30) | Role in event | event_team_player_1 |
| play_detail1 | VARCHAR(100) | Play detail | StickCheck, Deke |
| play_detail_2 | VARCHAR(100) | Secondary detail | Forehand |
| play_detail_successful | CHAR(1) | Play success | s, u |
| is_primary_player | INTEGER | Primary player flag | 0, 1 |
| is_event_team | INTEGER | On event team | 0, 1 |
| is_opp_team | INTEGER | On opposing team | 0, 1 |
| skill_rating | DECIMAL(3,1) | Player skill | 5 |

---

## fact_shifts

**Description**: Shift data with team skill aggregates.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| shift_key | VARCHAR(30) | PK | 18969_11 |
| shift_index | INTEGER | Shift number | 11 |
| shift_duration | INTEGER | Duration in seconds | 45 |
| situation | VARCHAR(20) | Game situation | even, pp, pk |
| strength | VARCHAR(20) | Strength situation | 5v5, 5v4 |
| home_goals | INTEGER | Home score | 2 |
| away_goals | INTEGER | Away score | 1 |
| home_skill_avg | DECIMAL(4,2) | Avg home skill on ice | 4.33 |
| away_skill_avg | DECIMAL(4,2) | Avg away skill on ice | 4.17 |
| skill_differential | DECIMAL(4,2) | Home - Away skill | 0.16 |

---

## fact_box_score

**Description**: Comprehensive player statistics (125+ columns).

### Identity Columns
| Column | Description |
|--------|-------------|
| player_game_key | Primary key |
| player_game_number | Jersey number |
| player_team | Team name |
| position | Position |
| skill_rating | Player skill |

### Ice Time
| Column | Description |
|--------|-------------|
| toi_seconds | Time on ice (seconds) |
| toi_formatted | TOI as MM:SS |
| shifts | Number of shifts |
| plus_minus | +/- |

### Scoring
| Column | Description |
|--------|-------------|
| goals | Goals scored |
| assists | Total assists |
| assists_primary | Primary assists |
| assists_secondary | Secondary assists |
| points | Goals + assists |

### Shooting
| Column | Description |
|--------|-------------|
| shots | All shot attempts |
| shots_on_goal | SOG |
| shots_missed | Missed shots |
| shots_blocked | Blocked shots |
| shooting_pct | Goals / SOG * 100 |
| shots_successful | Successful shots |
| shots_unsuccessful | Unsuccessful shots |

### Passing
| Column | Description |
|--------|-------------|
| passes | Pass attempts |
| passes_completed | Completed passes |
| passes_failed | Failed passes |
| pass_pct | Completion % |
| times_pass_target | Times targeted with pass |

### Turnovers
| Column | Description |
|--------|-------------|
| giveaways | Puck losses |
| takeaways | Puck steals |
| turnover_differential | Takeaways - giveaways |

### Faceoffs
| Column | Description |
|--------|-------------|
| faceoffs | Total faceoffs |
| faceoff_wins | Faceoffs won |
| faceoff_pct | Win % |

### Zone Play
| Column | Description |
|--------|-------------|
| zone_entries | Zone entry attempts |
| zone_entries_successful | Successful entries |
| zone_exits | Zone exit attempts |
| zone_entry_targets | Times targeted in entry |

### Micro-Stats (Defensive)
| Column | Description |
|--------|-------------|
| stick_checks | Stick check plays |
| poke_checks | Poke check plays |
| blocked_shots_play | Shot blocks |
| in_shot_pass_lane | In passing lane |
| separate_from_puck | Separated player from puck |
| backchecks | Backcheck plays |
| zone_entry_denials | Entry denials |
| zone_exit_denials | Exit denials |

### Micro-Stats (Offensive)
| Column | Description |
|--------|-------------|
| dekes | Deke attempts |
| dekes_successful | Successful dekes |
| screens | Screen attempts |
| dump_and_chase | Dump and chase plays |
| drives | Drive attempts |
| drives_successful | Successful drives |
| breakouts | Breakout plays |
| puck_recoveries | Puck recoveries |

### Goalie Stats
| Column | Description |
|--------|-------------|
| saves | Saves made |
| goals_against | Goals allowed |
| save_pct | Save percentage |

### Skill Context
| Column | Description |
|--------|-------------|
| avg_opp_skill_faced | Avg opponent skill |
| skill_vs_opponents | Own skill - opp skill |

### Per-60 Rates
| Column | Description |
|--------|-------------|
| goals_per_60 | Goals per 60 min |
| assists_per_60 | Assists per 60 min |
| points_per_60 | Points per 60 min |
| shots_per_60 | Shots per 60 min |

---

## fact_linked_events

**Description**: Linked event chains (shot→save→rebound).

| Column | Type | Description |
|--------|------|-------------|
| chain_id | VARCHAR(40) | PK |
| linked_event_index | INTEGER | Original link index |
| first_event | INTEGER | First event in chain |
| last_event | INTEGER | Last event in chain |
| event_count | INTEGER | Events in chain |
| chain_type | VARCHAR(30) | Type: shot_sequence, turnover_sequence |
| event_types | TEXT | List of event types |
| event_details | TEXT | List of event details |

---

## fact_sequences

**Description**: Possession sequence chains.

| Column | Type | Description |
|--------|------|-------------|
| sequence_key | VARCHAR(40) | PK |
| sequence_index | INTEGER | Sequence number |
| first_event | INTEGER | First event |
| last_event | INTEGER | Last event |
| event_count | INTEGER | Events in sequence |
| shift_index | INTEGER | Shift reference |

---

## fact_plays

**Description**: Play-level chains.

| Column | Type | Description |
|--------|------|-------------|
| play_key | VARCHAR(40) | PK |
| play_index | INTEGER | Play number |
| first_event | INTEGER | First event |
| last_event | INTEGER | Last event |
| event_count | INTEGER | Events in play |
