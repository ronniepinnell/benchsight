# Power BI Data Model Schema

## Overview

This document describes how to set up the data model in Power BI for the hockey analytics data mart.

---

## Star Schema Diagram

```
                                    ┌─────────────────┐
                                    │   dim_player    │
                                    │ (BLB Master)    │
                                    │                 │
                                    │ player_id (PK)  │
                                    │ skill_rating    │
                                    │ position        │
                                    └────────┬────────┘
                                             │
                                             │ 1
                                             │
                                             │ *
┌─────────────────┐                ┌─────────────────────┐                ┌─────────────────┐
│   dim_team      │                │  fact_gameroster    │                │  dim_schedule   │
│                 │                │  (BLB - ALL GAMES)  │                │                 │
│ team_id (PK)    │◄──────────────┤                     ├───────────────►│ game_id (PK)    │
│ team_name       │      *     1  │ game_id (FK)        │  1        *    │ home_team       │
│                 │                │ player_id (FK)      │                │ away_team       │
└─────────────────┘                │ team_id (FK)        │                │ game_date       │
                                   │ goals               │                └─────────────────┘
                                   │ assists             │
                                   │ plus_minus          │
                                   └─────────────────────┘
                                             │
                                             │ 
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
        ┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
        │ fact_box_score    │    │ fact_events       │    │ fact_shifts       │
        │ _tracking         │    │ _tracking         │    │ _tracking         │
        │                   │    │                   │    │                   │
        │ player_game_key   │    │ event_key (PK)    │    │ shift_key (PK)    │
        │ (PK)              │    │ game_id           │    │ game_id           │
        │ game_id           │    │ shift_key (FK)    │    │ period            │
        │ goals             │    │ Type              │    │ strength          │
        │ assists           │    │ event_detail      │    │ situation         │
        │ shots             │    │                   │    │                   │
        │ ... (64 cols)     │    └─────────┬─────────┘    └─────────┬─────────┘
        └───────────────────┘              │                        │
                    ▲                      │                        │
                    │                      ▼                        ▼
                    │          ┌───────────────────┐    ┌───────────────────┐
                    │          │ fact_event_       │    │ fact_shift_       │
                    │          │ players_tracking  │    │ players_tracking  │
                    │          │                   │    │                   │
                    └──────────┤ event_player_key  │    │ shift_player_key  │
                               │ event_key (FK)    │    │ shift_key (FK)    │
                               │ player_game_key   │    │ player_game_key   │
                               │ play_detail1      │    │ plus_minus        │
                               └───────────────────┘    └───────────────────┘
```

---

## Table Relationships

### Import Settings

When importing CSVs:
1. Import BLB tables first (master data)
2. Import dimension tables
3. Import fact tables last

### Relationship Definitions

#### Core Relationships (MUST HAVE)

| From Table | From Column | To Table | To Column | Cardinality | Cross-Filter |
|------------|-------------|----------|-----------|-------------|--------------|
| dim_player | player_id | fact_gameroster | player_id | 1:* | Single |
| dim_team | team_id | fact_gameroster | team_id | 1:* | Single |
| dim_schedule | game_id | fact_gameroster | game_id | 1:* | Single |
| dim_schedule | game_id | fact_events_tracking | game_id | 1:* | Single |
| dim_schedule | game_id | fact_shifts_tracking | game_id | 1:* | Single |
| dim_schedule | game_id | fact_box_score_tracking | game_id | 1:* | Single |

#### Event Relationships

| From Table | From Column | To Table | To Column | Cardinality |
|------------|-------------|----------|-----------|-------------|
| fact_events_tracking | event_key | fact_event_players_tracking | event_key | 1:* |
| dim_event_type | event_type | fact_events_tracking | Type | 1:* |
| dim_event_detail | event_detail | fact_events_tracking | event_detail | 1:* |
| dim_period | period_id | fact_events_tracking | period | 1:* |
| dim_time_bucket | time_bucket_id | fact_events_tracking | time_bucket_id | 1:* |

#### Shift Relationships

| From Table | From Column | To Table | To Column | Cardinality |
|------------|-------------|----------|-----------|-------------|
| fact_shifts_tracking | shift_key | fact_shift_players_tracking | shift_key | 1:* |
| dim_strength | strength_id | fact_shifts_tracking | strength | 1:* |
| dim_situation | situation_id | fact_shifts_tracking | situation | 1:* |

#### Player Relationships

| From Table | From Column | To Table | To Column | Cardinality |
|------------|-------------|----------|-----------|-------------|
| dim_game_players_tracking | player_game_key | fact_box_score_tracking | player_game_key | 1:1 |
| dim_game_players_tracking | player_game_key | fact_event_players_tracking | player_game_key | 1:* |
| dim_game_players_tracking | player_game_key | fact_shift_players_tracking | player_game_key | 1:* |

---

## Role-Playing Dimensions

### dim_team as Multiple Roles

The same `dim_team` table relates to multiple columns:

```
dim_schedule.home_team  ─── dim_team (as "Home Team")
dim_schedule.away_team  ─── dim_team (as "Away Team")
fact_gameroster.team_id ─── dim_team (as "Player Team")
```

**Solution:** Create inactive relationships or duplicate the dim_team table:
- dim_team_home
- dim_team_away

---

## Calculated Tables (Optional)

### Date Table

Create a proper date table for time intelligence:

```dax
DateTable = 
ADDCOLUMNS(
    CALENDAR(DATE(2020,1,1), DATE(2030,12,31)),
    "Year", YEAR([Date]),
    "Month", MONTH([Date]),
    "MonthName", FORMAT([Date], "MMMM"),
    "Quarter", "Q" & QUARTER([Date]),
    "DayOfWeek", WEEKDAY([Date]),
    "DayName", FORMAT([Date], "dddd"),
    "WeekNum", WEEKNUM([Date])
)
```

### Player Lookup Table

Combine dim_player with dim_randomnames:

```dax
PlayerLookup = 
SELECTCOLUMNS(
    NATURALLEFTOUTERJOIN(dim_player, dim_randomnames),
    "player_id", dim_player[player_id],
    "display_name", dim_randomnames[random_full_name],
    "real_name", dim_player[player_full_name],
    "skill_rating", dim_player[current_skill_rating],
    "position", dim_player[primary_position]
)
```

---

## Data Model View

In Power BI Model View, arrange tables like this:

```
┌─────────────────────────────────────────────────────────────────────┐
│                           DIMENSION LAYER                           │
│                                                                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐       │
│  │dim_player  │ │dim_team    │ │dim_schedule│ │dim_season  │       │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘       │
│                                                                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐       │
│  │dim_event_  │ │dim_strength│ │dim_situation│ │dim_period │       │
│  │type        │ │            │ │            │ │            │       │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            FACT LAYER                               │
│                                                                     │
│        ┌─────────────────┐                                         │
│        │ fact_gameroster │  ← ALL GAMES (tracked + non-tracked)    │
│        └─────────────────┘                                         │
│                 │                                                   │
│    ┌────────────┼────────────┬────────────┐                        │
│    ▼            ▼            ▼            ▼                        │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                   │
│ │fact_box_│ │fact_    │ │fact_    │ │fact_    │  ← TRACKED ONLY   │
│ │score    │ │events   │ │shifts   │ │linked   │                    │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘                   │
│      │           │            │                                    │
│      │           ▼            ▼                                    │
│      │    ┌───────────┐ ┌───────────┐                              │
│      │    │fact_event_│ │fact_shift_│  ← BRIDGE TABLES            │
│      │    │players    │ │players    │                              │
│      │    └───────────┘ └───────────┘                              │
│      │           │            │                                    │
│      └───────────┴────────────┘                                    │
│                  │                                                  │
│                  ▼                                                  │
│        ┌─────────────────┐                                         │
│        │dim_game_players │  ← Per-game player info                 │
│        └─────────────────┘                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Performance Tips

### 1. Remove Unused Columns

Before importing, exclude columns you won't use:
- `_source_file` from XY tables
- Intermediate calculation columns

### 2. Set Appropriate Data Types

| Column Type | Power BI Type |
|-------------|---------------|
| *_key | Text |
| *_id | Whole Number |
| *_seconds | Decimal |
| *_pct | Decimal (Percentage) |
| is_* | True/False |
| *_date | Date |

### 3. Create Aggregation Tables

For large datasets, create summary tables:

```dax
SeasonPlayerStats = 
SUMMARIZE(
    fact_box_score_tracking,
    fact_box_score_tracking[player_id],
    dim_season[season],
    "Total Games", COUNTROWS(fact_box_score_tracking),
    "Total Goals", SUM(fact_box_score_tracking[goals]),
    "Total Assists", SUM(fact_box_score_tracking[assists]),
    "Avg TOI", AVERAGE(fact_box_score_tracking[toi_seconds])
)
```
