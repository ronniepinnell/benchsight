# BenchSight Database Schema ERD

**Entity-Relationship Diagrams for all tables and relationships**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document provides Entity-Relationship Diagrams (ERDs) for the BenchSight database schema, showing table relationships, primary keys, and foreign keys.

**Total Tables:** 132-139 tables  
**Core Tables:** ~20 essential tables  
**Derived Tables:** ~100+ calculated/aggregated tables

---

## Core Schema ERD

### Essential Tables and Relationships

```mermaid
erDiagram
    dim_player ||--o{ fact_events : "event_player_1"
    dim_player ||--o{ fact_shifts : "player_id"
    dim_player ||--o{ fact_player_game_stats : "player_id"
    dim_player ||--o{ fact_gameroster : "player_id"
    
    dim_team ||--o{ dim_player : "team_id"
    dim_team ||--o{ fact_team_game_stats : "team_id"
    dim_team ||--o{ fact_gameroster : "team_id"
    
    dim_schedule ||--o{ fact_events : "game_id"
    dim_schedule ||--o{ fact_shifts : "game_id"
    dim_schedule ||--o{ fact_player_game_stats : "game_id"
    dim_schedule ||--o{ fact_team_game_stats : "game_id"
    dim_schedule ||--o{ fact_gameroster : "game_id"
    
    dim_season ||--o{ dim_schedule : "season_id"
    dim_season ||--o{ fact_player_season_stats : "season_id"
    
    dim_league ||--o{ dim_team : "league_id"
    dim_league ||--o{ dim_season : "league_id"
    
    fact_events ||--o{ fact_event_players : "event_id"
    fact_events ||--o{ fact_scoring_chances : "event_id"
    fact_events ||--o{ fact_shots : "event_id"
    fact_events ||--o{ fact_goals : "event_id"
    
    fact_shifts ||--o{ fact_shift_players : "shift_id"
    fact_shifts ||--o{ fact_shift_quality : "shift_id"
    
    fact_player_game_stats ||--o{ fact_player_season_stats : "player_game_key"
    fact_player_season_stats ||--o{ fact_player_career_stats : "player_season_key"
    
    fact_team_game_stats ||--o{ fact_team_season_stats : "team_game_key"
    
    dim_event_type ||--o{ fact_events : "event_type"
    dim_event_detail ||--o{ fact_events : "event_detail"
    dim_zone ||--o{ fact_events : "zone"
    dim_danger_level ||--o{ fact_events : "danger_level"
    
    dim_player {
        string player_id PK
        string player_full_name
        string team_id FK
        string position
        int jersey_number
        decimal skill_rating
    }
    
    dim_team {
        string team_id PK
        string team_name
        string league_id FK
        string division
    }
    
    dim_schedule {
        int game_id PK
        string season_id FK
        date game_date
        string home_team_id FK
        string away_team_id FK
    }
    
    dim_season {
        string season_id PK
        string league_id FK
        string season_name
        date start_date
        date end_date
    }
    
    dim_league {
        string league_id PK
        string league_name
    }
    
    fact_events {
        string event_id PK
        int game_id FK
        string event_type FK
        string event_detail FK
        string event_player_1 FK
        string zone FK
        string danger_level FK
        int time_start_total_seconds
    }
    
    fact_shifts {
        string shift_id PK
        int game_id FK
        string player_id FK
        int shift_start
        int shift_end
        int shift_duration
    }
    
    fact_player_game_stats {
        string player_game_key PK
        int game_id FK
        string player_id FK
        string team_id FK
        int goals
        int assists
        int points
        int shots
        int sog
        decimal shooting_pct
        decimal xg_for
        decimal war
        decimal gar_total
    }
    
    fact_team_game_stats {
        string team_game_key PK
        int game_id FK
        string team_id FK
        int goals
        int shots
        decimal cf_pct
    }
    
    fact_gameroster {
        string player_game_id PK
        int game_id FK
        string player_id FK
        string team_id FK
        int goals
        int assists
    }
```

---

## Complete Schema ERD (Simplified)

### All Table Categories

```mermaid
graph TB
    subgraph Dimensions["Dimension Tables (50 tables)"]
        D1[dim_player]
        D2[dim_team]
        D3[dim_schedule]
        D4[dim_season]
        D5[dim_league]
        D6[dim_event_type]
        D7[dim_event_detail]
        D8[dim_zone]
        D9[dim_danger_level]
        D10[dim_period]
        D11[dim_strength]
        D12[dim_situation]
        D13[Other Dimensions...]
    end
    
    subgraph CoreFacts["Core Fact Tables (10 tables)"]
        F1[fact_events]
        F2[fact_shifts]
        F3[fact_event_players]
        F4[fact_shift_players]
        F5[fact_gameroster]
        F6[fact_player_game_stats]
        F7[fact_team_game_stats]
        F8[fact_goalie_game_stats]
        F9[fact_tracking]
        F10[fact_registration]
    end
    
    subgraph DerivedFacts["Derived Fact Tables (70+ tables)"]
        DF1[fact_player_season_stats]
        DF2[fact_player_career_stats]
        DF3[fact_scoring_chances]
        DF4[fact_shots]
        DF5[fact_goals]
        DF6[fact_sequences]
        DF7[fact_plays]
        DF8[fact_shift_quality]
        DF9[fact_line_combos]
        DF10[Other Derived...]
    end
    
    subgraph XY["XY/Spatial Tables (8 tables)"]
        XY1[fact_puck_xy_wide]
        XY2[fact_puck_xy_long]
        XY3[fact_player_xy_wide]
        XY4[fact_player_xy_long]
        XY5[fact_shot_xy]
        XY6[Other XY...]
    end
    
    subgraph QA["QA Tables (4 tables)"]
        QA1[qa_goal_verification]
        QA2[qa_data_completeness]
        QA3[qa_suspicious_stats]
        QA4[Other QA...]
    end
    
    D1 --> F1
    D1 --> F2
    D1 --> F6
    D2 --> F6
    D2 --> F7
    D3 --> F1
    D3 --> F2
    D3 --> F6
    D3 --> F7
    
    F1 --> F6
    F2 --> F6
    F6 --> DF1
    DF1 --> DF2
    F6 --> F7
    
    F1 --> DF3
    F1 --> DF4
    F1 --> DF5
    F1 --> DF6
    F1 --> XY1
    F1 --> XY3
    
    F6 --> QA1
    
    style D1 fill:#00d4ff
    style D2 fill:#00d4ff
    style D3 fill:#00d4ff
    style F1 fill:#ff8800
    style F2 fill:#ff8800
    style F6 fill:#00ff88
    style F7 fill:#00ff88
    style DF1 fill:#aa66ff
    style DF2 fill:#aa66ff
    style QA1 fill:#ff4444
```

---

## Detailed Table Relationships

### Player Statistics Hierarchy

```mermaid
erDiagram
    dim_player ||--o{ fact_player_game_stats : "player_id"
    fact_player_game_stats ||--o{ fact_player_season_stats : "aggregates"
    fact_player_season_stats ||--o{ fact_player_career_stats : "aggregates"
    
    fact_player_game_stats ||--o{ fact_player_period_stats : "splits by period"
    fact_player_game_stats ||--o{ fact_player_situation_stats : "splits by situation"
    fact_player_game_stats ||--o{ fact_player_micro_stats : "micro statistics"
    
    dim_player {
        string player_id PK
        string player_full_name
        string team_id FK
    }
    
    fact_player_game_stats {
        string player_game_key PK
        string player_id FK
        int game_id FK
        int goals
        int assists
        decimal xg_for
        decimal war
    }
    
    fact_player_season_stats {
        string player_season_key PK
        string player_id FK
        string season_id FK
        int goals
        int assists
        decimal xg_for
        decimal war
    }
    
    fact_player_career_stats {
        string player_career_key PK
        string player_id FK
        int goals
        int assists
        decimal xg_for
        decimal war
    }
```

### Event and Shift Relationships

```mermaid
erDiagram
    fact_events ||--o{ fact_event_players : "event_id"
    fact_events ||--o{ fact_scoring_chances : "event_id"
    fact_events ||--o{ fact_shots : "event_id"
    fact_events ||--o{ fact_goals : "event_id"
    fact_events ||--o{ fact_sequences : "event_id"
    
    fact_shifts ||--o{ fact_shift_players : "shift_id"
    fact_shifts ||--o{ fact_shift_quality : "shift_id"
    fact_shifts ||--o{ fact_line_combos : "shift_id"
    
    dim_player ||--o{ fact_event_players : "player_id"
    dim_player ||--o{ fact_shift_players : "player_id"
    
    fact_events {
        string event_id PK
        int game_id FK
        string event_player_1 FK
        string event_type
    }
    
    fact_event_players {
        string event_player_id PK
        string event_id FK
        string player_id FK
        string player_role
    }
    
    fact_shifts {
        string shift_id PK
        int game_id FK
        string player_id FK
        int shift_duration
    }
    
    fact_shift_players {
        string shift_player_id PK
        string shift_id FK
        string player_id FK
    }
```

### Team Statistics Hierarchy

```mermaid
erDiagram
    dim_team ||--o{ fact_team_game_stats : "team_id"
    fact_team_game_stats ||--o{ fact_team_season_stats : "aggregates"
    fact_team_season_stats ||--o{ fact_team_standings_snapshot : "snapshot"
    
    fact_player_game_stats ||--o{ fact_team_game_stats : "aggregates by team"
    
    dim_team {
        string team_id PK
        string team_name
        string league_id FK
    }
    
    fact_team_game_stats {
        string team_game_key PK
        string team_id FK
        int game_id FK
        int goals
        int shots
        decimal cf_pct
    }
    
    fact_team_season_stats {
        string team_season_key PK
        string team_id FK
        string season_id FK
        int goals
        int shots
        decimal cf_pct
    }
```

---

## Foreign Key Relationships

### Primary Foreign Key Paths

```mermaid
graph TD
    A[dim_league] --> B[dim_season]
    A --> C[dim_team]
    
    B --> D[dim_schedule]
    
    C --> E[dim_player]
    C --> F[fact_team_game_stats]
    
    D --> G[fact_events]
    D --> H[fact_shifts]
    D --> I[fact_player_game_stats]
    D --> J[fact_team_game_stats]
    D --> K[fact_gameroster]
    
    E --> G
    E --> H
    E --> I
    E --> K
    
    G --> L[fact_event_players]
    G --> M[fact_scoring_chances]
    G --> N[fact_shots]
    G --> O[fact_goals]
    
    H --> P[fact_shift_players]
    H --> Q[fact_shift_quality]
    
    I --> R[fact_player_season_stats]
    R --> S[fact_player_career_stats]
    
    F --> T[fact_team_season_stats]
    
    style A fill:#00d4ff
    style B fill:#00d4ff
    style C fill:#00d4ff
    style D fill:#00d4ff
    style E fill:#00d4ff
    style G fill:#ff8800
    style H fill:#ff8800
    style I fill:#00ff88
    style F fill:#00ff88
```

---

## Table Categories Overview

### Dimension Tables (50 tables)

```mermaid
graph LR
    subgraph BLB["BLB Dimensions (16-17)"]
        D1[dim_player]
        D2[dim_team]
        D3[dim_schedule]
        D4[dim_season]
        D5[dim_league]
        D6[Other BLB...]
    end
    
    subgraph Static["Static Dimensions (19-25)"]
        S1[dim_period]
        S2[dim_zone]
        S3[dim_danger_level]
        S4[dim_strength]
        S5[dim_situation]
        S6[Other Static...]
    end
    
    subgraph Dynamic["Dynamic Dimensions (15+)"]
        DY1[dim_comparison_type]
        DY2[dim_competition_tier]
        DY3[dim_rink_zone]
        DY4[Other Dynamic...]
    end
    
    style D1 fill:#00d4ff
    style D2 fill:#00d4ff
    style D3 fill:#00d4ff
    style S1 fill:#aa66ff
    style S2 fill:#aa66ff
    style S3 fill:#aa66ff
```

### Fact Tables (81 tables)

```mermaid
graph LR
    subgraph Core["Core Facts (10)"]
        C1[fact_events]
        C2[fact_shifts]
        C3[fact_player_game_stats]
        C4[fact_team_game_stats]
        C5[fact_goalie_game_stats]
        C6[Other Core...]
    end
    
    subgraph Derived["Derived Facts (60+)"]
        D1[fact_player_season_stats]
        D2[fact_player_career_stats]
        D3[fact_scoring_chances]
        D4[fact_sequences]
        D5[fact_shift_quality]
        D6[Other Derived...]
    end
    
    subgraph XY["XY Facts (8)"]
        X1[fact_puck_xy_wide]
        X2[fact_player_xy_wide]
        X3[fact_shot_xy]
        X4[Other XY...]
    end
    
    subgraph QA["QA Facts (4)"]
        Q1[qa_goal_verification]
        Q2[qa_data_completeness]
        Q3[Other QA...]
    end
    
    style C1 fill:#ff8800
    style C2 fill:#ff8800
    style C3 fill:#00ff88
    style D1 fill:#aa66ff
    style D2 fill:#aa66ff
    style X1 fill:#00d4ff
    style Q1 fill:#ff4444
```

---

## Data Lineage Diagram

### Source to Final Output

```mermaid
graph TD
    subgraph Sources["Data Sources"]
        S1[BLB_Tables.xlsx]
        S2[Tracking Files]
    end
    
    subgraph Extract["Extract Layer"]
        S1 --> E1[dim_player]
        S1 --> E2[dim_team]
        S1 --> E3[dim_schedule]
        S2 --> E4[fact_events]
        S2 --> E5[fact_shifts]
    end
    
    subgraph Transform["Transform Layer"]
        E4 --> T1[fact_event_players]
        E5 --> T2[fact_shift_players]
        E4 --> T3[fact_scoring_chances]
        E4 --> T4[fact_shots]
        E4 --> T5[fact_goals]
    end
    
    subgraph Calculate["Calculate Layer"]
        E1 --> C1[fact_player_game_stats]
        E3 --> C1
        E4 --> C1
        E5 --> C1
        T1 --> C1
        T2 --> C1
        
        C1 --> C2[fact_player_season_stats]
        C1 --> C3[fact_team_game_stats]
        C2 --> C4[fact_player_career_stats]
        C3 --> C5[fact_team_season_stats]
    end
    
    subgraph Output["Output Layer"]
        C1 --> O1[Dashboard]
        C2 --> O1
        C3 --> O1
        C4 --> O1
        C5 --> O1
    end
    
    style S1 fill:#00d4ff
    style S2 fill:#00d4ff
    style E4 fill:#ff8800
    style E5 fill:#ff8800
    style C1 fill:#00ff88
    style O1 fill:#00ff88
```

---

## Multi-Tenant Schema ERD (Future)

### With Tenant Isolation

```mermaid
erDiagram
    dim_tenant ||--o{ dim_player : "tenant_id"
    dim_tenant ||--o{ dim_team : "tenant_id"
    dim_tenant ||--o{ dim_schedule : "tenant_id"
    dim_tenant ||--o{ fact_events : "tenant_id"
    dim_tenant ||--o{ fact_shifts : "tenant_id"
    dim_tenant ||--o{ fact_player_game_stats : "tenant_id"
    
    dim_tenant {
        string tenant_id PK
        string tenant_name
        string subscription_tier
        string subscription_status
    }
    
    dim_player {
        string tenant_id PK
        string player_id PK
        string player_full_name
    }
    
    fact_events {
        string tenant_id PK
        string event_id PK
        int game_id FK
        string event_player_1 FK
    }
    
    fact_player_game_stats {
        string tenant_id PK
        string player_game_key PK
        string player_id FK
        int game_id FK
    }
```

**Note:** In multi-tenant schema, all primary keys become composite (tenant_id, original_key) and all foreign keys include tenant_id.

---

## Related Documentation

- [DATA_DICTIONARY.md](DATA_DICTIONARY.md) - Complete table and column documentation
- [SCHEMA_SCALABILITY_DESIGN.md](SCHEMA_SCALABILITY_DESIGN.md) - Multi-tenant schema design
- [ETL_FLOW_DIAGRAMS.md](../etl/ETL_FLOW_DIAGRAMS.md) - ETL process diagrams

---

*Last Updated: 2026-01-15*
