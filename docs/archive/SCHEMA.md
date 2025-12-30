# BenchSight v5.0.0 - Data Schema

## Table Overview

### Dimension vs Fact Tables

**Dimension Tables (dim_)**: Reference data that describes the "what/who/where/when"
- Slowly changing or static
- Used for filtering, grouping, labeling
- Primary keys for joining to facts

**Fact Tables (fact_)**: Transactional data that measures the "how much/how many"
- Event-driven, grows over time
- Contains foreign keys to dimensions
- Contains measures (counts, durations, etc.)

---

## Table Relationships

### Wide vs Long Format

| Wide Table | Long Table | Relationship |
|------------|------------|--------------|
| fact_events | fact_events_long | 1 event → N player-event records |
| fact_shifts | fact_shifts_long | 1 shift → N player-shift records |

**Wide Format**: One row per event/shift with player info in columns
- Good for: Quick lookups, shift composition views
- Example: fact_shifts has home_forward_1, home_forward_2, etc.

**Long Format**: One row per player involvement
- Good for: Player-level analysis, aggregations, joins
- Example: fact_shifts_long has one row per player per shift

### Tracking Tables

| Table | Purpose |
|-------|---------|
| fact_events_tracking | Raw event data from Excel (all columns) |
| fact_events | Cleaned/normalized unique events |
| fact_events_long | Player-level event participation |

The _tracking tables preserve the original data. The derived tables are optimized for analysis.

---

## Entity Relationship Diagram

```mermaid
erDiagram
    %% DIMENSION TABLES
    dim_player {
        string player_id PK
        string player_full_name
        string player_first_name
        string player_last_name
    }
    
    dim_team {
        string team_id PK
        string team_name
        string league_id FK
    }
    
    dim_league {
        string league_id PK
        string league_name
    }
    
    dim_season {
        string season_id PK
        string season_name
        string league_id FK
    }
    
    dim_schedule {
        string game_id PK
        string season_id FK
        string home_team_id FK
        string away_team_id FK
        string game_date
    }
    
    dim_period {
        string period_id PK
        string period_number
        string period_name
        string period_type
    }
    
    dim_position {
        string position_id PK
        string position_code
        string position_name
        string position_type
    }
    
    dim_shift_slot {
        string slot_id PK
        string slot_code
        string slot_name
        string slot_type
    }
    
    dim_zone {
        string zone_id PK
        string zone_code
        string zone_name
    }
    
    dim_venue {
        string venue_id PK
        string venue_code
        string venue_name
    }
    
    dim_event_type {
        string event_type_id PK
        string event_type_code
        string event_type_name
        string event_category
    }
    
    dim_strength {
        string strength_id PK
        string strength_code
        string strength_name
        int home_skaters
        int away_skaters
    }
    
    dim_player_role {
        string role_id PK
        string role_code
        string role_name
        string role_type
    }
    
    %% FACT TABLES
    fact_gameroster {
        string player_game_id PK
        string game_id FK
        string player_id FK
        string team_id FK
        string player_game_number
        string player_position
    }
    
    fact_events {
        string event_id PK
        string game_id FK
        string event_type_id FK
        string period_id FK
        string event_index
    }
    
    fact_events_long {
        string event_player_id PK
        string event_id FK
        string game_id FK
        string player_id FK
        string event_type_id FK
        string period_id FK
        string player_role
    }
    
    fact_shifts {
        string shift_id PK
        string game_id FK
        string period_id FK
        string shift_index
    }
    
    fact_shifts_long {
        string shift_player_id PK
        string shift_id FK
        string game_id FK
        string player_id FK
        string slot_id FK
        string venue_id FK
        string period_id FK
    }
    
    %% RELATIONSHIPS
    dim_league ||--o{ dim_team : "has"
    dim_league ||--o{ dim_season : "has"
    dim_season ||--o{ dim_schedule : "contains"
    dim_team ||--o{ dim_schedule : "home_team"
    dim_team ||--o{ dim_schedule : "away_team"
    
    dim_schedule ||--o{ fact_gameroster : "game"
    dim_player ||--o{ fact_gameroster : "player"
    dim_team ||--o{ fact_gameroster : "team"
    
    dim_schedule ||--o{ fact_events : "game"
    dim_event_type ||--o{ fact_events : "type"
    dim_period ||--o{ fact_events : "period"
    
    fact_events ||--o{ fact_events_long : "event"
    dim_player ||--o{ fact_events_long : "player"
    dim_event_type ||--o{ fact_events_long : "type"
    dim_period ||--o{ fact_events_long : "period"
    
    dim_schedule ||--o{ fact_shifts : "game"
    dim_period ||--o{ fact_shifts : "period"
    
    fact_shifts ||--o{ fact_shifts_long : "shift"
    dim_player ||--o{ fact_shifts_long : "player"
    dim_shift_slot ||--o{ fact_shifts_long : "slot"
    dim_venue ||--o{ fact_shifts_long : "venue"
    dim_period ||--o{ fact_shifts_long : "period"
```

---

## Simplified View

```mermaid
flowchart TB
    subgraph Dimensions
        dim_player[dim_player<br/>337 players]
        dim_team[dim_team<br/>26 teams]
        dim_schedule[dim_schedule<br/>562 games]
        dim_event_type[dim_event_type<br/>20 types]
        dim_shift_slot[dim_shift_slot<br/>7 slots]
    end
    
    subgraph Facts
        fact_gameroster[fact_gameroster<br/>14,471 records]
        fact_events[fact_events<br/>5,411 events]
        fact_events_long[fact_events_long<br/>10,352 records]
        fact_shifts[fact_shifts<br/>476 shifts]
        fact_shifts_long[fact_shifts_long<br/>5,513 records]
    end
    
    dim_player --> fact_gameroster
    dim_player --> fact_events_long
    dim_player --> fact_shifts_long
    
    dim_schedule --> fact_gameroster
    dim_schedule --> fact_events
    dim_schedule --> fact_shifts
    
    dim_event_type --> fact_events
    dim_event_type --> fact_events_long
    
    dim_shift_slot --> fact_shifts_long
    
    fact_events --> fact_events_long
    fact_shifts --> fact_shifts_long
```

---

## Table Descriptions

### Dimension Tables (17 tables)

| Table | Rows | PK | Description |
|-------|------|-----|-------------|
| dim_player | 337 | player_id | All registered players |
| dim_team | 26 | team_id | All teams in league |
| dim_league | 2 | league_id | NORAD, CSAH |
| dim_season | 9 | season_id | Season definitions |
| dim_schedule | 562 | game_id | All scheduled games |
| dim_period | 5 | period_id | Game periods (1,2,3,OT,SO) |
| dim_position | 7 | position_id | Player positions (C,LW,RW,F,D,G,X) |
| dim_shift_slot | 7 | slot_id | Shift assignments (F1,F2,F3,D1,D2,G,X) |
| dim_zone | 3 | zone_id | Rink zones (O,D,N) |
| dim_venue | 2 | venue_id | Home/Away |
| dim_event_type | 20 | event_type_id | Event types from tracking |
| dim_strength | 10 | strength_id | Game situations (5v5, PP, PK, etc.) |
| dim_player_role | 14 | role_id | Player roles in events |
| dim_playerurlref | 548 | - | Player URL references |
| dim_rinkboxcoord | 50 | box_id | Rink coordinates |
| dim_rinkcoordzones | 198 | box_id | Rink zone mappings |
| dim_randomnames | 486 | - | Anonymization names |

### Fact Tables (11 tables)

| Table | Rows | PK | Description |
|-------|------|-----|-------------|
| fact_gameroster | 14,471 | player_game_id | Player-game assignments |
| fact_events | 5,411 | event_id | Unique events (wide) |
| fact_events_long | 10,352 | event_player_id | Player-event records |
| fact_events_tracking | 11,918 | event_id | Raw tracking data |
| fact_shifts | 476 | shift_id | Unique shifts (wide) |
| fact_shifts_long | 5,513 | shift_player_id | Player-shift records |
| fact_shifts_tracking | 476 | shift_id | Raw shift data |
| fact_playergames | 3,010 | player_game_id | Player game stats |
| fact_draft | 160 | player_draft_id | Draft history |
| fact_registration | 190 | player_season_registration_id | Season registrations |
| fact_leadership | 28 | - | Team leadership |

---

## Foreign Key Reference

### fact_events_long
- `game_id` → dim_schedule.game_id
- `player_id` → dim_player.player_id
- `event_type_id` → dim_event_type.event_type_id
- `period_id` → dim_period.period_id
- `event_id` → fact_events.event_id

### fact_shifts_long
- `game_id` → dim_schedule.game_id
- `player_id` → dim_player.player_id
- `slot_id` → dim_shift_slot.slot_id
- `venue_id` → dim_venue.venue_id
- `period_id` → dim_period.period_id
- `shift_id` → fact_shifts.shift_id

### fact_gameroster
- `game_id` → dim_schedule.game_id
- `player_id` → dim_player.player_id
- `team_id` → dim_team.team_id

