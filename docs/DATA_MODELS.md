# BenchSight Data Models

**Complete schema reference for all 111 tables**

---

## Table Categories

| Category | Count | Description |
|----------|-------|-------------|
| Dimension (dim_) | 48 | Reference/lookup tables |
| Fact (fact_) | 58 | Transactional/metric tables |
| ETL (etl_) | 2 | Pipeline tracking |
| QA (qa_) | 3 | Quality assurance |

---

## Core Dimension Tables

### dim_player
**Player master data**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| player_id | TEXT | **PK** | "P001" |
| player_full_name | TEXT | Full name | "John Smith" |
| first_name | TEXT | First name | "John" |
| last_name | TEXT | Last name | "Smith" |
| skill_rating | TEXT | 1-10 skill level | "7" |
| primary_position | TEXT | Main position | "C", "LW", "RW", "D", "G" |
| secondary_position | TEXT | Alternate position | "LW" |
| team_id | TEXT | Current team FK | "T001" |
| team_name | TEXT | Team name | "Ice Dogs" |
| jersey_number | TEXT | Jersey # | "19" |
| is_active | TEXT | Active flag | "1" or "0" |
| handedness | TEXT | Shoots/catches | "L" or "R" |
| birth_year | TEXT | Birth year | "1990" |

### dim_team
**Team information**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| team_id | TEXT | **PK** | "T001" |
| team_name | TEXT | Full name | "Ice Dogs" |
| team_short_name | TEXT | Abbreviation | "ICE" |
| division | TEXT | Division | "North" |
| conference | TEXT | Conference | "East" |
| is_active | TEXT | Active flag | "1" |
| primary_color | TEXT | Team color | "#FF0000" |
| secondary_color | TEXT | Secondary | "#FFFFFF" |

### dim_schedule
**Game schedule and results**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| game_id | TEXT | **PK** | "18969" |
| game_date_str | TEXT | Date string | "2025-01-15" |
| game_time | TEXT | Start time | "19:30" |
| season_id | TEXT | Season FK | "S2025" |
| home_team_id | TEXT | Home team FK | "T001" |
| away_team_id | TEXT | Away team FK | "T002" |
| home_team_name | TEXT | Home name | "Ice Dogs" |
| away_team_name | TEXT | Away name | "Polar Bears" |
| home_total_goals | TEXT | Home score | "5" |
| away_total_goals | TEXT | Away score | "3" |
| venue_id | TEXT | Venue FK | "V001" |
| venue_name | TEXT | Venue name | "Main Arena" |
| game_status | TEXT | Status | "completed", "scheduled", "in_progress" |
| period_count | TEXT | Periods played | "3" |
| overtime | TEXT | OT flag | "0" or "1" |
| shootout | TEXT | SO flag | "0" or "1" |

### dim_season
**Season definitions**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| season_id | TEXT | **PK** | "S2025" |
| season_name | TEXT | Display name | "2024-2025 Season" |
| start_date | TEXT | Season start | "2024-09-01" |
| end_date | TEXT | Season end | "2025-04-30" |
| is_current | TEXT | Current season | "1" |

### dim_event_type
**Event type lookup**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| event_type_id | TEXT | **PK** | "ET001" |
| event_type_name | TEXT | Type name | "Goal" |
| category | TEXT | Category | "scoring", "defensive", "faceoff" |
| description | TEXT | Details | "Goal scored" |

### dim_position
**Position definitions**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| position_id | TEXT | **PK** | "C" |
| position_name | TEXT | Full name | "Center" |
| position_type | TEXT | Type | "forward", "defense", "goalie" |

### dim_venue
**Rink/arena information**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| venue_id | TEXT | **PK** | "V001" |
| venue_name | TEXT | Name | "Main Arena" |
| city | TEXT | City | "Denver" |
| capacity | TEXT | Seating | "5000" |

### dim_zone
**Rink zones**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| zone_id | TEXT | **PK** | "OZ" |
| zone_name | TEXT | Name | "Offensive Zone" |
| zone_type | TEXT | Type | "offensive", "defensive", "neutral" |

---

## Core Fact Tables

### fact_events
**Play-by-play events**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| event_key | TEXT | **PK** | "EVT_18969_1_001" |
| game_id | TEXT | Game FK | "18969" |
| event_index | TEXT | Sequence # | "1" |
| period | TEXT | Period | "1", "2", "3", "OT" |
| event_time | TEXT | Time (MM:SS) | "12:34" |
| event_time_seconds | TEXT | Time in seconds | "754" |
| event_type | TEXT | Type | "Shot", "Goal", "Faceoff" |
| event_detail | TEXT | Detail | "Wrist Shot" |
| event_detail_2 | TEXT | Extra detail | "Top Corner" |
| team_id | TEXT | Team FK | "T001" |
| team_name | TEXT | Team name | "Ice Dogs" |
| zone | TEXT | Zone | "offensive" |
| x_coord | TEXT | X coordinate | "75" |
| y_coord | TEXT | Y coordinate | "25" |
| strength | TEXT | Strength state | "even", "pp", "pk" |
| is_goal | TEXT | Goal flag | "1" or "0" |
| is_shot | TEXT | Shot flag | "1" or "0" |
| video_time | TEXT | Video timestamp | "00:12:34" |

### fact_events_player
**Player involvement in events**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| event_player_key | TEXT | **PK** | "EPK_18969_1_001_P001" |
| event_key | TEXT | Event FK | "EVT_18969_1_001" |
| game_id | TEXT | Game FK | "18969" |
| event_index | TEXT | Event sequence | "1" |
| player_id | TEXT | Player FK | "P001" |
| player_name | TEXT | Player name | "John Smith" |
| player_role | TEXT | Role in event | "scorer", "assist1", "assist2", "goalie" |
| is_primary | TEXT | Primary player | "1" or "0" |
| team_id | TEXT | Player's team | "T001" |

### fact_player_game_stats
**Player stats per game**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| player_game_key | TEXT | **PK** | "PGK_18969_P001" |
| game_id | TEXT | Game FK | "18969" |
| player_id | TEXT | Player FK | "P001" |
| player_name | TEXT | Name | "John Smith" |
| team_id | TEXT | Team FK | "T001" |
| team_name | TEXT | Team | "Ice Dogs" |
| position | TEXT | Position played | "C" |
| goals | TEXT | Goals | "2" |
| assists | TEXT | Assists | "1" |
| points | TEXT | G+A | "3" |
| shots | TEXT | SOG | "5" |
| shots_missed | TEXT | Missed shots | "2" |
| blocked_shots | TEXT | Blocked | "1" |
| hits | TEXT | Hits | "3" |
| takeaways | TEXT | Takeaways | "2" |
| giveaways | TEXT | Giveaways | "1" |
| faceoff_wins | TEXT | FO wins | "8" |
| faceoff_losses | TEXT | FO losses | "4" |
| faceoff_pct | TEXT | FO% | "66.7" |
| toi_seconds | TEXT | TOI (sec) | "1110" |
| toi_minutes | TEXT | TOI (min) | "18.5" |
| plus_minus | TEXT | +/- | "+2" |
| pim | TEXT | PIM | "2" |
| pp_goals | TEXT | PPG | "1" |
| sh_goals | TEXT | SHG | "0" |
| gw_goals | TEXT | GWG | "0" |

### fact_shifts
**Player shifts**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| shift_key | TEXT | **PK** | "SHF_18969_P001_1" |
| game_id | TEXT | Game FK | "18969" |
| player_id | TEXT | Player FK | "P001" |
| player_name | TEXT | Name | "John Smith" |
| team_id | TEXT | Team FK | "T001" |
| period | TEXT | Period | "1" |
| shift_number | TEXT | Shift # | "1" |
| start_time | TEXT | Start (MM:SS) | "20:00" |
| end_time | TEXT | End (MM:SS) | "19:15" |
| start_time_seconds | TEXT | Start (sec) | "1200" |
| end_time_seconds | TEXT | End (sec) | "1155" |
| duration_seconds | TEXT | Duration | "45" |
| start_type | TEXT | How started | "period_start", "on_fly", "stoppage" |
| end_type | TEXT | How ended | "on_fly", "goal", "penalty" |

### fact_gameroster
**Game lineup**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| roster_key | TEXT | **PK** | "RST_18969_P001" |
| game_id | TEXT | Game FK | "18969" |
| player_id | TEXT | Player FK | "P001" |
| player_name | TEXT | Name | "John Smith" |
| team_id | TEXT | Team FK | "T001" |
| jersey_number | TEXT | Jersey # | "19" |
| position | TEXT | Position | "C" |
| line_number | TEXT | Line # | "1" |
| is_starter | TEXT | Started | "1" |
| is_scratch | TEXT | Scratched | "0" |

### fact_team_game_stats
**Team stats per game**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| team_game_key | TEXT | **PK** | "TGK_18969_T001" |
| game_id | TEXT | Game FK | "18969" |
| team_id | TEXT | Team FK | "T001" |
| team_name | TEXT | Name | "Ice Dogs" |
| goals | TEXT | Goals | "5" |
| shots | TEXT | Shots | "32" |
| shots_against | TEXT | SA | "28" |
| save_pct | TEXT | SV% | "0.893" |
| pp_goals | TEXT | PPG | "2" |
| pp_opportunities | TEXT | PP opp | "4" |
| pp_pct | TEXT | PP% | "50.0" |
| pk_goals_against | TEXT | PK GA | "1" |
| pk_opportunities | TEXT | Times shorthanded | "3" |
| pk_pct | TEXT | PK% | "66.7" |
| faceoff_wins | TEXT | FO wins | "28" |
| faceoff_pct | TEXT | FO% | "52.8" |
| hits | TEXT | Hits | "25" |
| blocked_shots | TEXT | Blocks | "12" |
| pim | TEXT | PIM | "8" |

### fact_goalie_game_stats
**Goalie stats per game**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| player_game_key | TEXT | **PK** | "GGK_18969_P050" |
| game_id | TEXT | Game FK | "18969" |
| player_id | TEXT | Player FK | "P050" |
| player_name | TEXT | Name | "Mike Johnson" |
| team_id | TEXT | Team FK | "T001" |
| shots_against | TEXT | SA | "28" |
| goals_against | TEXT | GA | "3" |
| saves | TEXT | Saves | "25" |
| save_pct | TEXT | SV% | "0.893" |
| toi_minutes | TEXT | TOI | "60" |
| win | TEXT | Win | "1" |
| loss | TEXT | Loss | "0" |
| shutout | TEXT | SO | "0" |

### fact_team_standings_snapshot
**Current standings**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| standings_key | TEXT | **PK** | "STD_S2025_T001" |
| season_id | TEXT | Season FK | "S2025" |
| team_id | TEXT | Team FK | "T001" |
| team_name | TEXT | Name | "Ice Dogs" |
| games_played | TEXT | GP | "20" |
| wins | TEXT | W | "12" |
| losses | TEXT | L | "6" |
| ties | TEXT | T | "2" |
| overtime_losses | TEXT | OTL | "0" |
| points | TEXT | Pts | "26" |
| goals_for | TEXT | GF | "65" |
| goals_against | TEXT | GA | "48" |
| goal_diff | TEXT | Diff | "+17" |
| win_pct | TEXT | Win% | "0.600" |

---

## Advanced Stat Tables

### fact_player_stats_core
**Season aggregates**

| Column | Type | Description |
|--------|------|-------------|
| player_stats_key | TEXT | **PK** |
| season_id | TEXT | Season FK |
| player_id | TEXT | Player FK |
| player_name | TEXT | Name |
| team_id | TEXT | Team FK |
| games_played | TEXT | GP |
| total_goals | TEXT | Total G |
| total_assists | TEXT | Total A |
| total_points | TEXT | Total P |
| total_shots | TEXT | Total SOG |
| shooting_pct | TEXT | SH% |
| total_toi_minutes | TEXT | Total TOI |
| avg_toi_minutes | TEXT | Avg TOI |
| total_plus_minus | TEXT | Total +/- |
| total_pim | TEXT | Total PIM |

### fact_player_stats_advanced
**Advanced analytics**

| Column | Type | Description |
|--------|------|-------------|
| player_stats_key | TEXT | **PK** |
| player_id | TEXT | Player FK |
| corsi_for | TEXT | CF |
| corsi_against | TEXT | CA |
| corsi_pct | TEXT | CF% |
| fenwick_for | TEXT | FF |
| fenwick_against | TEXT | FA |
| fenwick_pct | TEXT | FF% |
| expected_goals | TEXT | xG |
| goals_above_expected | TEXT | G-xG |
| zone_start_pct | TEXT | OZ Start% |

### fact_line_combos
**Line combination stats**

| Column | Type | Description |
|--------|------|-------------|
| combo_key | TEXT | **PK** |
| game_id | TEXT | Game FK |
| team_id | TEXT | Team FK |
| player_1_id | TEXT | Player 1 |
| player_2_id | TEXT | Player 2 |
| player_3_id | TEXT | Player 3 |
| toi_together | TEXT | TOI |
| goals_for | TEXT | GF |
| goals_against | TEXT | GA |
| shots_for | TEXT | SF |
| shots_against | TEXT | SA |

---

## Lookup/Reference Tables

### dim_event_detail
Event detail values (e.g., "Wrist Shot", "Slap Shot")

### dim_event_detail_2
Secondary event details (e.g., "Top Corner", "Five Hole")

### dim_shot_type
Shot type definitions

### dim_strength
Strength states (even, 5v4, 4v5, etc.)

### dim_period
Period definitions (1, 2, 3, OT, SO)

### dim_success
Success/failure codes

### dim_zone_entry_type
Zone entry types (carry, dump, pass)

### dim_zone_exit_type
Zone exit types (carry, clear, pass)

### dim_play_detail
Play detail codes

### dim_stoppage_type
Stoppage reasons (icing, offside, penalty, etc.)

---

## ETL Metadata Tables

### etl_run_log
Pipeline execution log

| Column | Type | Description |
|--------|------|-------------|
| run_id | TEXT | **PK** |
| start_time | TEXT | Start timestamp |
| end_time | TEXT | End timestamp |
| status | TEXT | success/failed |
| games_processed | TEXT | Game count |
| rows_processed | TEXT | Row count |
| errors | TEXT | Error messages |

### etl_table_log
Per-table processing log

| Column | Type | Description |
|--------|------|-------------|
| log_id | TEXT | **PK** |
| run_id | TEXT | Run FK |
| table_name | TEXT | Table name |
| rows_before | TEXT | Pre-count |
| rows_after | TEXT | Post-count |
| rows_inserted | TEXT | Inserted |
| rows_updated | TEXT | Updated |
| duration_seconds | TEXT | Time |

---

## QA Tables

### qa_goal_accuracy
Goal verification against official sources

| Column | Type | Description |
|--------|------|-------------|
| qa_key | TEXT | **PK** |
| game_id | TEXT | Game FK |
| official_home_goals | TEXT | Official home |
| official_away_goals | TEXT | Official away |
| calculated_home_goals | TEXT | Our home |
| calculated_away_goals | TEXT | Our away |
| match | TEXT | Matches? "1"/"0" |
| checked_at | TEXT | Check timestamp |

### qa_validation_log
Data validation results

| Column | Type | Description |
|--------|------|-------------|
| validation_id | TEXT | **PK** |
| table_name | TEXT | Table checked |
| check_type | TEXT | Check name |
| passed | TEXT | Pass? "1"/"0" |
| details | TEXT | Check details |
| checked_at | TEXT | Timestamp |

### qa_suspicious_stats
Flagged statistical anomalies

| Column | Type | Description |
|--------|------|-------------|
| flag_id | TEXT | **PK** |
| game_id | TEXT | Game FK |
| player_id | TEXT | Player FK |
| stat_name | TEXT | Stat flagged |
| stat_value | TEXT | Value |
| reason | TEXT | Why flagged |
| flagged_at | TEXT | Timestamp |

---

## Primary Key Conventions

All tables follow these PK patterns:

| Table Pattern | PK Format | Example |
|---------------|-----------|---------|
| dim_* | `{entity}_id` | player_id, team_id |
| fact_events | `event_key` | EVT_18969_1_001 |
| fact_*_stats | `{entity}_game_key` or `{entity}_stats_key` | PGK_18969_P001 |
| fact_shifts | `shift_key` | SHF_18969_P001_1 |

---

## Foreign Key Relationships

```
dim_player.player_id ─────┬────> fact_player_game_stats.player_id
                          ├────> fact_events_player.player_id
                          ├────> fact_shifts.player_id
                          └────> fact_gameroster.player_id

dim_team.team_id ─────────┬────> dim_player.team_id
                          ├────> dim_schedule.home_team_id
                          ├────> dim_schedule.away_team_id
                          └────> fact_team_game_stats.team_id

dim_schedule.game_id ─────┬────> fact_events.game_id
                          ├────> fact_player_game_stats.game_id
                          ├────> fact_shifts.game_id
                          └────> fact_gameroster.game_id
```

---

## Data Types

All columns are stored as TEXT in PostgreSQL for maximum flexibility. Convert as needed:

```javascript
// Convert to number
const goals = parseInt(player.goals) || 0
const pct = parseFloat(player.faceoff_pct) || 0

// Convert to boolean
const isActive = player.is_active === '1'

// Convert to date
const gameDate = new Date(game.game_date_str)
```
