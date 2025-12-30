# BenchSight Database Schema

## Entity Relationship Diagram

```mermaid
erDiagram
    dim_league ||--o{ dim_season : contains
    dim_league ||--o{ dim_team : contains
    
    dim_season ||--o{ dim_schedule : has_games
    dim_season ||--o{ fact_registration : has_registrations
    dim_season ||--o{ fact_draft : has_draft
    dim_season ||--o{ fact_leadership : has_leaders
    
    dim_team ||--o{ dim_schedule : home_team
    dim_team ||--o{ dim_schedule : away_team
    dim_team ||--o{ fact_gameroster : team
    dim_team ||--o{ fact_draft : drafted_by
    
    dim_player ||--o{ fact_gameroster : plays_in
    dim_player ||--o{ fact_registration : registers
    dim_player ||--o{ fact_draft : drafted
    dim_player ||--o{ fact_event_players_tracking : involved_in
    
    dim_schedule ||--o{ fact_gameroster : game
    dim_schedule ||--o{ fact_events_tracking : game_events
    dim_schedule ||--o{ fact_shifts_tracking : game_shifts
    
    dim_event_type ||--o{ fact_events_tracking : event_type
    dim_event_detail ||--o{ fact_events_tracking : event_detail
    
    fact_shifts_tracking ||--o{ fact_shift_players_tracking : players_on_ice
    fact_events_tracking ||--o{ fact_event_players_tracking : players_involved
```

## Table Categories

### Core Dimensions
```
dim_league ─────► dim_season ─────► dim_schedule
     │                │
     └────► dim_team ─┘
              │
         dim_player
```

### Event Tracking
```
dim_event_type ──┐
                 ├──► fact_events_tracking ──► fact_event_players_tracking
dim_event_detail ┘           │
                             └──► fact_linked_events_tracking
                             └──► fact_sequences_tracking
                             └──► fact_plays_tracking
```

### Shift Tracking
```
fact_shifts_tracking ──► fact_shift_players_tracking
         │
    dim_strength
    dim_situation
```

### Rink Coordinates
```
dim_rinkboxcoord ──► dim_rinkcoordzones
         │
dim_danger_zone ────► fact_event_coordinates
```

### Stats Reference
```
dim_stat ──────► (calculated stats)
dim_shot_type
dim_pass_type
dim_turnover_type
dim_play_detail
dim_net_location
```

## Table Counts

| Category | Count |
|----------|-------|
| Dimension Tables | 30 |
| Fact Tables | 21 |
| **Total** | **51** |

## Data Volumes

| Table | Est. Rows |
|-------|-----------|
| fact_events_tracking | 24,089 |
| fact_events_long | 22,333 |
| fact_gameroster | 14,473 |
| fact_playergames | 3,010 |
| fact_event_players_tracking | 3,132 |
| fact_shift_players_tracking | 1,136 |
| fact_shifts_tracking | 770 |
| dim_schedule | 562 |
| dim_playerurlref | 548 |
| dim_randomnames | 486 |
| dim_player | 337 |
| dim_rinkcoordzones | 202 |
| fact_draft | 160 |
| fact_registration | 191 |
| Other tables | <100 each |
