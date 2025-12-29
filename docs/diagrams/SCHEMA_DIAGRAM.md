# BenchSight Database Schema Diagram

## Entity Relationship Diagram (Mermaid)

```mermaid
erDiagram
    %% DIMENSION TABLES
    dim_player {
        string player_id PK "P100XXX"
        string player_full_name
        string player_primary_position
        int current_skill_rating
        string player_norad_current_team
        string player_url
    }
    
    dim_team {
        string team_id PK "N100XX"
        string team_name
        string team_abrev
        string league_id FK
    }
    
    dim_schedule {
        int game_id PK
        date date
        string home_team_name
        string away_team_name
        string home_team_id FK
        string away_team_id FK
        int home_total_goals
        int away_total_goals
        string game_url
        string video_url
    }
    
    dim_league {
        string league_id PK
        string league_name
    }
    
    dim_season {
        string season_id PK
        string season_name
        date start_date
        date end_date
    }

    %% FACT TABLES - CORE
    fact_player_game_stats {
        string player_game_key PK
        int game_id FK
        string player_id FK
        int goals
        int assists
        int points
        int shots
        float toi_seconds
        int plus_minus_ev
        float cf_pct
        float game_score
    }
    
    fact_events_player {
        string event_player_key PK
        string event_key FK
        int game_id FK
        string player_id FK
        int event_index
        string player_role
        string event_type
    }
    
    fact_shifts_player {
        string shift_player_key PK
        string shift_key FK
        int game_id FK
        string player_id FK
        int shift_index
        string slot
        float shift_duration
        string situation
    }
    
    fact_gameroster {
        string player_game_id PK
        int game_id FK
        string player_id FK
        string team_name
        int player_game_number
    }

    %% FACT TABLES - ADVANCED
    fact_h2h {
        string h2h_key PK
        int game_id FK
        string player_id FK
        string opponent_id FK
        int shifts_against
        float toi_against
        int cf_against
    }
    
    fact_wowy {
        string wowy_key PK
        int game_id FK
        string player_1_id FK
        string player_2_id FK
        int shifts_together
        float toi_together
        float cf_pct_together
    }
    
    fact_line_combos {
        string combo_key PK
        int game_id FK
        string player_1_id FK
        string player_2_id FK
        string player_3_id FK
        int shifts_together
        float goals_for
    }
    
    fact_goalie_game_stats {
        string goalie_game_key PK
        int game_id FK
        string player_id FK
        int shots_faced
        int saves
        int goals_against
        float save_pct
    }

    %% QA TABLES
    fact_game_status {
        int game_id PK
        string tracking_status
        float tracking_pct
        boolean is_loaded
        boolean goal_match
        string issues
    }
    
    fact_suspicious_stats {
        int id PK
        int game_id FK
        string player_id FK
        string stat_name
        float stat_value
        string category
        string severity
    }

    %% RELATIONSHIPS
    dim_player ||--o{ fact_player_game_stats : "plays in"
    dim_schedule ||--o{ fact_player_game_stats : "has"
    dim_player ||--o{ fact_events_player : "participates"
    dim_schedule ||--o{ fact_events_player : "contains"
    dim_player ||--o{ fact_shifts_player : "takes"
    dim_schedule ||--o{ fact_shifts_player : "contains"
    dim_player ||--o{ fact_gameroster : "rostered"
    dim_schedule ||--o{ fact_gameroster : "roster for"
    dim_team ||--o{ dim_schedule : "plays home"
    dim_team ||--o{ dim_schedule : "plays away"
    dim_league ||--o{ dim_team : "contains"
    dim_player ||--o{ fact_h2h : "faces"
    dim_player ||--o{ fact_wowy : "plays with"
    dim_player ||--o{ fact_goalie_game_stats : "goalies"
    dim_schedule ||--o{ fact_game_status : "status"
```

## Table Categories

### Dimension Tables (Master Data)
| Table | Records | Purpose |
|-------|---------|---------|
| dim_player | 298 | Player master data |
| dim_team | 15 | Team information |
| dim_schedule | 562 | Game schedule with official scores |
| dim_league | 2 | League definitions |
| dim_season | 8 | Season periods |
| dim_position | 5 | Position types |
| dim_venue | 2 | Home/Away |
| dim_period | 4 | Game periods |
| dim_player_role | 6 | Event roles |
| dim_composite_rating | 10 | Rating categories |

### Fact Tables (Transactional)
| Table | Records | Grain |
|-------|---------|-------|
| fact_player_game_stats | 107 | One row per player per game |
| fact_events_player | 11,635 | One row per player per event |
| fact_shifts_player | 4,626 | One row per player per shift |
| fact_gameroster | 107 | One row per player per game |
| fact_events | 4,388 | One row per event |
| fact_h2h | 684 | Player vs opponent matchups |
| fact_wowy | 641 | Player pair analysis |
| fact_line_combos | 332 | 3-player combinations |
| fact_goalie_game_stats | 8 | Goalie stats per game |
| fact_team_game_stats | 8 | Team totals per game |

### QA Tables (Monitoring)
| Table | Records | Purpose |
|-------|---------|---------|
| fact_game_status | 562 | Game completeness tracking |
| fact_suspicious_stats | 18 | Flagged outliers |
| fact_player_game_position | 105 | Dynamic positions |

## Primary Key Structure

All keys follow 12-character format for consistency:

```
Player ID:        P100XXX (7 chars)
Team ID:          N100XX (6 chars)  
Game ID:          5 digits
Event Key:        E{game:05d}{event:06d} = 12 chars
Shift Key:        S{game:05d}{shift:06d} = 12 chars
Player-Game Key:  {game_id}{player_id} = 12 chars
```

## Foreign Key Relationships

```
fact_player_game_stats.player_id → dim_player.player_id
fact_player_game_stats.game_id → dim_schedule.game_id
fact_events_player.player_id → dim_player.player_id
fact_events_player.game_id → dim_schedule.game_id
fact_shifts_player.player_id → dim_player.player_id
fact_shifts_player.game_id → dim_schedule.game_id
fact_gameroster.player_id → dim_player.player_id
fact_gameroster.game_id → dim_schedule.game_id
dim_team.league_id → dim_league.league_id
```
