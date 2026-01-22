# BenchSight ETL Flow Diagrams

**Visual representation of ETL phases, data flow, and calculation processes**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document provides visual diagrams of the ETL pipeline, including phase flow, data transformations, and calculation processes.

---

## ETL Phase Flow

### Complete Phase Flowchart

```mermaid
graph TD
    START[Start ETL] --> P1[Phase 1: Load BLB Tables]
    P1 --> P1A[Load dim_player]
    P1 --> P1B[Load dim_team]
    P1 --> P1C[Load dim_schedule]
    P1 --> P1D[Load fact_gameroster]
    P1A --> P1E[16-17 BLB Tables]
    P1B --> P1E
    P1C --> P1E
    P1D --> P1E
    
    P1E --> P2[Phase 2: Process Tracking Files]
    P2 --> P2A[Load events sheet]
    P2 --> P2B[Load shifts sheet]
    P2A --> P2C[Create fact_events]
    P2B --> P2D[Create fact_shifts]
    P2C --> P2E[Expand to fact_event_players]
    P2D --> P2F[Expand to fact_shift_players]
    
    P2E --> P3[Phase 3B: Create Dimension Tables]
    P2F --> P3
    P3 --> P3A[Create dim_period]
    P3 --> P3B[Create dim_zone]
    P3 --> P3C[Create dim_danger_level]
    P3 --> P3D[19-25 Static Dimensions]
    
    P3D --> P4[Phase 4: Core Player Stats]
    P4 --> P4A[fact_player_game_stats<br/>317 columns]
    P4 --> P4B[fact_team_game_stats]
    P4 --> P4C[fact_goalie_game_stats]
    
    P4A --> P4B[Phase 4B: Shift Analytics]
    P4B --> P4B1[fact_shift_quality]
    P4B --> P4B2[fact_line_combos]
    P4B --> P4B3[fact_player_pair_stats]
    
    P4B1 --> P4C[Phase 4C: Remaining Facts]
    P4C --> P4C1[fact_player_season_stats]
    P4C --> P4C2[fact_player_career_stats]
    P4C --> P4C3[30+ Derived Tables]
    
    P4C1 --> P4D[Phase 4D: Event Analytics]
    P4D --> P4D1[fact_sequences]
    P4D --> P4D2[fact_plays]
    P4D --> P4D3[fact_event_chains]
    
    P4D1 --> P5[Phase 5: Foreign Keys]
    P5 --> P5A[Add Foreign Keys]
    P5 --> P5B[Validate Relationships]
    
    P5A --> P6[Phase 6: Extended Tables]
    P6 --> P6A[fact_player_trends]
    P6 --> P6B[fact_player_boxscore_all]
    P6 --> P6C[10+ Extended Tables]
    
    P6A --> P7[Phase 7: Post Processing]
    P7 --> P7A[Add Names to Tables]
    P7 --> P7B[Remove Null Columns]
    P7 --> P7C[Validate Data]
    
    P7A --> P8[Phase 8: Event Time Context]
    P8 --> P8A[Add Time Context]
    P8 --> P8B[Calculate Durations]
    
    P8A --> P9[Phase 9: QA Tables]
    P9 --> P9A[qa_goal_verification]
    P9 --> P9B[qa_data_completeness]
    P9 --> P9C[qa_suspicious_stats]
    P9 --> P9D[4-6 QA Tables]
    
    P9A --> P10[Phase 10: V11 Enhancements]
    P10 --> P10A[fact_video]
    P10 --> P10B[fact_highlights]
    P10 --> P10C[5+ Enhancement Tables]
    
    P10A --> P10B[Phase 10B: XY Tables]
    P10B --> P10B1[fact_puck_xy_wide]
    P10B --> P10B2[fact_player_xy_wide]
    P10B --> P10B3[8+ XY Tables]
    
    P10B1 --> P11[Phase 11: Macro Stats]
    P11 --> P11A[fact_suspicious_stats]
    P11 --> P11B[Macro Analytics]
    
    P11A --> END[End ETL<br/>139 Tables Created]
    
    style START fill:#00ff88
    style P1 fill:#00d4ff
    style P2 fill:#00d4ff
    style P3 fill:#00d4ff
    style P4 fill:#ff8800
    style P4B fill:#ff8800
    style P4C fill:#ff8800
    style P4D fill:#ff8800
    style P5 fill:#aa66ff
    style P6 fill:#aa66ff
    style P7 fill:#aa66ff
    style P8 fill:#aa66ff
    style P9 fill:#ff4444
    style P10 fill:#aa66ff
    style P10B fill:#aa66ff
    style P11 fill:#aa66ff
    style END fill:#00ff88
```

---

## Data Source to Output Flow

### Source Data Flow

```mermaid
graph LR
    subgraph Sources["Data Sources"]
        BLB[BLB_Tables.xlsx<br/>16-17 sheets]
        TRK[Tracking Files<br/>{game_id}_tracking.xlsx]
    end
    
    subgraph Phase1["Phase 1: Extract"]
        BLB --> DIM1[dim_player<br/>dim_team<br/>dim_schedule<br/>...]
        BLB --> FACT1[fact_gameroster<br/>fact_leadership<br/>...]
    end
    
    subgraph Phase2["Phase 2-3: Transform"]
        TRK --> EVENTS[fact_events<br/>~5,800 rows]
        TRK --> SHIFTS[fact_shifts<br/>~400 rows]
        EVENTS --> EVPLAYERS[fact_event_players<br/>~11,000 rows]
        SHIFTS --> SHIFTPLAYERS[fact_shift_players<br/>~2,000 rows]
    end
    
    subgraph Phase3["Phase 3B: Dimensions"]
        STATIC[Static Constants] --> DIM2[dim_period<br/>dim_zone<br/>dim_danger_level<br/>...]
    end
    
    subgraph Phase4["Phase 4: Calculate"]
        EVENTS --> CALC1[fact_player_game_stats<br/>317 columns]
        SHIFTS --> CALC1
        CALC1 --> CALC2[fact_player_season_stats]
        CALC1 --> CALC3[fact_team_game_stats]
        CALC2 --> CALC4[fact_player_career_stats]
    end
    
    subgraph Output["Output"]
        DIM1 --> CSV[CSV Files<br/>data/output/]
        FACT1 --> CSV
        EVENTS --> CSV
        SHIFTS --> CSV
        DIM2 --> CSV
        CALC1 --> CSV
        CALC2 --> CSV
        CALC3 --> CSV
        CALC4 --> CSV
        CSV --> DB[(Supabase Database)]
    end
    
    style BLB fill:#00d4ff
    style TRK fill:#00d4ff
    style EVENTS fill:#ff8800
    style SHIFTS fill:#ff8800
    style CALC1 fill:#00ff88
    style CSV fill:#aa66ff
    style DB fill:#00ff88
```

---

## Calculation Flow

### fact_events → fact_player_game_stats

```mermaid
graph TD
    A[fact_events<br/>Raw event data] --> B[Filter by player<br/>event_player_1 = player_id]
    B --> C[Group by player + game]
    
    C --> D[Count Events]
    D --> D1[goals: COUNT WHERE<br/>event_type='Goal'<br/>AND event_detail='Goal_Scored']
    D --> D2[shots: COUNT WHERE<br/>event_type='Shot']
    D --> D3[passes: COUNT WHERE<br/>event_type='Pass']
    D --> D4[faceoffs: COUNT WHERE<br/>event_type='Faceoff']
    
    C --> E[Calculate Metrics]
    E --> E1[shooting_pct: goals / sog * 100]
    E --> E2[pass_pct: pass_completed / pass_attempts * 100]
    E --> E3[fo_pct: fo_wins / fo_total * 100]
    
    C --> F[Calculate Advanced]
    F --> F1[xG: SUM shot_xg<br/>with flurry adjustment]
    F --> F2[Corsi: COUNT corsi events]
    F --> F3[Fenwick: COUNT fenwick events]
    
    C --> G[Calculate WAR/GAR]
    G --> G1[GAR_offense: goals×1.0 + assists×0.7 + ...]
    G --> G2[GAR_defense: takeaways×0.05 + blocks×0.02 + ...]
    G --> G3[GAR_total: sum of components]
    G --> G4[WAR: GAR_total / 4.5]
    
    D1 --> H[fact_player_game_stats<br/>317 columns]
    D2 --> H
    D3 --> H
    D4 --> H
    E1 --> H
    E2 --> H
    E3 --> H
    F1 --> H
    F2 --> H
    F3 --> H
    G1 --> H
    G2 --> H
    G3 --> H
    G4 --> H
    
    I[fact_shifts<br/>TOI data] --> H
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#aa66ff
    style E fill:#aa66ff
    style F fill:#aa66ff
    style G fill:#aa66ff
    style H fill:#00ff88
    style I fill:#00d4ff
```

### Aggregation Hierarchy

```mermaid
graph TD
    A[fact_events<br/>Event-level data] --> B[fact_player_game_stats<br/>Player + Game level]
    B --> C[fact_player_season_stats<br/>Player + Season level]
    C --> D[fact_player_career_stats<br/>Player + Career level]
    
    B --> E[fact_team_game_stats<br/>Team + Game level]
    E --> F[fact_team_season_stats<br/>Team + Season level]
    
    B --> G[fact_goalie_game_stats<br/>Goalie + Game level]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#00ff88
    style D fill:#00ff88
    style E fill:#aa66ff
    style F fill:#aa66ff
    style G fill:#ff4444
```

---

## ETL Execution Flow

### Step-by-Step Execution

```mermaid
sequenceDiagram
    participant User
    participant ETL as ETL Pipeline
    participant BLB as BLB Loader
    participant TRK as Tracking Processor
    participant CALC as Calculation Engine
    participant VAL as Validator
    participant DB as Supabase
    
    User->>ETL: Run ETL (python run_etl.py)
    ETL->>BLB: Load BLB_Tables.xlsx
    BLB-->>ETL: 16-17 dimension/fact tables
    
    ETL->>TRK: Process tracking files
    TRK->>TRK: Load events sheet
    TRK->>TRK: Load shifts sheet
    TRK->>TRK: Create fact_events
    TRK->>TRK: Create fact_shifts
    TRK-->>ETL: Core tracking tables
    
    ETL->>CALC: Calculate player stats
    CALC->>CALC: Aggregate events by player
    CALC->>CALC: Calculate xG, WAR/GAR
    CALC->>CALC: Calculate Corsi/Fenwick
    CALC-->>ETL: fact_player_game_stats
    
    ETL->>CALC: Calculate team stats
    CALC->>CALC: Aggregate player stats
    CALC-->>ETL: fact_team_game_stats
    
    ETL->>VAL: Validate data
    VAL->>VAL: Check goal counts
    VAL->>VAL: Verify foreign keys
    VAL-->>ETL: Validation results
    
    ETL->>ETL: Save to CSV files
    ETL->>DB: Upload to Supabase
    DB-->>ETL: Upload complete
    ETL-->>User: ETL Complete (139 tables)
```

---

## Table Dependency Graph

### Core Dependencies

```mermaid
graph TD
    BLB[BLB_Tables.xlsx] --> DIM_PLAYER[dim_player]
    BLB --> DIM_TEAM[dim_team]
    BLB --> DIM_SCHEDULE[dim_schedule]
    BLB --> FACT_ROSTER[fact_gameroster]
    
    TRK[Tracking Files] --> FACT_EVENTS[fact_events]
    TRK --> FACT_SHIFTS[fact_shifts]
    
    FACT_EVENTS --> FACT_EV_PLAYERS[fact_event_players]
    FACT_SHIFTS --> FACT_SH_PLAYERS[fact_shift_players]
    
    DIM_PLAYER --> FACT_PLAYER_GAME[fact_player_game_stats]
    DIM_TEAM --> FACT_PLAYER_GAME
    DIM_SCHEDULE --> FACT_PLAYER_GAME
    FACT_EVENTS --> FACT_PLAYER_GAME
    FACT_SHIFTS --> FACT_PLAYER_GAME
    
    FACT_PLAYER_GAME --> FACT_PLAYER_SEASON[fact_player_season_stats]
    FACT_PLAYER_SEASON --> FACT_PLAYER_CAREER[fact_player_career_stats]
    
    FACT_PLAYER_GAME --> FACT_TEAM_GAME[fact_team_game_stats]
    FACT_TEAM_GAME --> FACT_TEAM_SEASON[fact_team_season_stats]
    
    FACT_EVENTS --> FACT_SHOTS[fact_shots]
    FACT_EVENTS --> FACT_GOALS[fact_goals]
    FACT_EVENTS --> FACT_SCORING[fact_scoring_chances]
    
    FACT_SHOTS --> FACT_SHOT_XY[fact_shot_xy]
    FACT_EVENTS --> FACT_PUCK_XY[fact_puck_xy_wide]
    
    FACT_PLAYER_GAME --> QA_GOALS[qa_goal_verification]
    FACT_GOALS --> QA_GOALS
    
    style BLB fill:#00d4ff
    style TRK fill:#00d4ff
    style FACT_EVENTS fill:#ff8800
    style FACT_SHIFTS fill:#ff8800
    style FACT_PLAYER_GAME fill:#00ff88
    style FACT_PLAYER_SEASON fill:#00ff88
    style FACT_TEAM_GAME fill:#aa66ff
    style QA_GOALS fill:#ff4444
```

---

## Calculation Process Flow

### xG Calculation Flow

```mermaid
graph TD
    A[Shot Event<br/>fact_events] --> B[Extract Shot Data]
    B --> B1[XY Coordinates]
    B --> B2[Event Detail]
    B --> B3[Event Detail 2]
    
    B1 --> C[Determine Danger Level]
    C --> C1[High Danger: XY in net area]
    C --> C2[Medium Danger: XY in slot]
    C --> C3[Low Danger: XY elsewhere]
    
    C1 --> D[Get Base xG Rate]
    C2 --> D
    C3 --> D
    D --> D1[High: 0.25]
    D --> D2[Medium: 0.08]
    D --> D3[Low: 0.03]
    
    B2 --> E[Check Rush Modifier]
    E --> E1[Is Rush: 1.3x]
    E --> E2[Is Rebound: 1.5x]
    E --> E3[Is One-Timer: 1.4x]
    E --> E4[Is Breakaway: 2.5x]
    E --> E5[Is Screened: 1.2x]
    E --> E6[Is Deflection: 1.3x]
    E --> E7[None: 1.0x]
    
    B3 --> F[Check Shot Type Modifier]
    F --> F1[Wrist: 1.0x]
    F --> F2[Slap: 0.95x]
    F --> F3[Snap: 1.05x]
    F --> F4[Backhand: 0.9x]
    F --> F5[Tip: 1.15x]
    F --> F6[Deflection: 1.1x]
    
    D1 --> G[Calculate Base xG]
    D2 --> G
    D3 --> G
    E1 --> G
    E2 --> G
    E3 --> G
    E4 --> G
    E5 --> G
    E6 --> G
    E7 --> G
    F1 --> G
    F2 --> G
    F3 --> G
    F4 --> G
    F5 --> G
    F6 --> G
    
    G --> H[Apply Modifiers<br/>base_rate × rush × shot_type]
    H --> I[Cap at 0.95]
    I --> J[Group Shots into Sequences<br/>Within 3 seconds]
    J --> K[Apply Flurry Adjustment<br/>P AtLeastOneGoal = 1 - ∏ 1-xG_i]
    K --> L[Final xG Value]
    
    style A fill:#00d4ff
    style C fill:#ff8800
    style D fill:#aa66ff
    style E fill:#aa66ff
    style F fill:#aa66ff
    style G fill:#ff8800
    style H fill:#ff8800
    style I fill:#ff8800
    style J fill:#aa66ff
    style K fill:#aa66ff
    style L fill:#00ff88
```

### WAR/GAR Calculation Flow

```mermaid
graph TD
    A[Player Stats<br/>fact_player_game_stats] --> B[GAR Components]
    
    B --> C[GAR Offense]
    C --> C1[goals × 1.0]
    C --> C2[primary_assists × 0.7]
    C --> C3[secondary_assists × 0.4]
    C --> C4[sog × 0.015]
    C --> C5[xg_for × 0.8]
    C --> C6[shot_assists × 0.3]
    C1 --> C7[Sum: GAR_offense]
    C2 --> C7
    C3 --> C7
    C4 --> C7
    C5 --> C7
    C6 --> C7
    
    B --> D[GAR Defense]
    D --> D1[takeaways × 0.05]
    D --> D2[blocks × 0.02]
    D --> D3[zone_exit_controlled × 0.03]
    D1 --> D4[Sum: GAR_defense]
    D2 --> D4
    D3 --> D4
    
    B --> E[GAR Possession]
    E --> E1[cf_pct - 50 / 100]
    E --> E2[× 0.02]
    E --> E3[× toi_hours]
    E --> E4[× 60]
    E1 --> E5[GAR_possession]
    E2 --> E5
    E3 --> E5
    E4 --> E5
    
    B --> F[GAR Transition]
    F --> F1[zone_entry_controlled × 0.04]
    F1 --> F2[GAR_transition]
    
    B --> G[GAR Poise]
    G --> G1[pressure_success_count × 0.02]
    G1 --> G2[GAR_poise]
    
    C7 --> H[GAR Total]
    D4 --> H
    E5 --> H
    F2 --> H
    G2 --> H
    
    H --> I[WAR Calculation]
    I --> I1[WAR = GAR_total / 4.5]
    I1 --> J[Final WAR Value]
    
    style A fill:#00d4ff
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#ff8800
    style G fill:#ff8800
    style H fill:#aa66ff
    style I fill:#aa66ff
    style J fill:#00ff88
```

### Corsi/Fenwick Calculation Flow

```mermaid
graph TD
    A[Event<br/>fact_events] --> B{Event Type?}
    
    B -->|Shot| C{Event Detail?}
    B -->|Other| Z[Not Corsi]
    
    C -->|Shot_OnNetSaved| D[SOG Event]
    C -->|Shot_OnNet| D
    C -->|Shot_Goal| D
    C -->|Shot_Missed| E[Missed Shot]
    C -->|Shot_MissedPost| E
    C -->|Blocked| F[Blocked Shot]
    C -->|Other| Z
    
    D --> G[Corsi Event]
    E --> G
    F --> G
    
    D --> H[Fenwick Event]
    E --> H
    F --> I[NOT Fenwick]
    
    G --> J[Count Corsi For<br/>Player's team]
    G --> K[Count Corsi Against<br/>Opponent team]
    
    H --> L[Count Fenwick For<br/>Player's team]
    H --> M[Count Fenwick Against<br/>Opponent team]
    
    J --> N[CF% = CF / CF+CA × 100]
    K --> N
    
    L --> O[FF% = FF / FF+FA × 100]
    M --> O
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#00ff88
    style E fill:#00ff88
    style F fill:#ff8800
    style G fill:#00ff88
    style H fill:#00ff88
    style J fill:#aa66ff
    style K fill:#aa66ff
    style L fill:#aa66ff
    style M fill:#aa66ff
    style N fill:#00ff88
    style O fill:#00ff88
```

---

## Data Transformation Pipeline

### End-to-End Data Flow

```mermaid
graph LR
    subgraph Input["Input Sources"]
        I1[BLB_Tables.xlsx<br/>Master Data]
        I2[Tracking Files<br/>Game Events]
    end
    
    subgraph Extract["Extract Phase"]
        I1 --> E1[Load Excel Sheets]
        I2 --> E2[Load Events/Shifts]
        E1 --> E3[16-17 BLB Tables]
        E2 --> E4[5 Tracking Tables]
    end
    
    subgraph Transform["Transform Phase"]
        E3 --> T1[Clean Data]
        E4 --> T2[Standardize Events]
        T1 --> T3[Calculate Derived Columns]
        T2 --> T3
        T3 --> T4[Create Dimensions]
        T4 --> T5[Create Core Facts]
    end
    
    subgraph Calculate["Calculate Phase"]
        T5 --> C1[Aggregate Player Stats]
        T5 --> C2[Calculate Advanced Metrics]
        C1 --> C3[317 Columns per Player]
        C2 --> C3
        C3 --> C4[Calculate Team Stats]
        C4 --> C5[Calculate Season Stats]
    end
    
    subgraph Validate["Validate Phase"]
        C5 --> V1[Goal Count Verification]
        C5 --> V2[Foreign Key Checks]
        C5 --> V3[Data Completeness]
        V1 --> V4[QA Tables]
        V2 --> V4
        V3 --> V4
    end
    
    subgraph Output["Output Phase"]
        V4 --> O1[Save to CSV]
        O1 --> O2[Upload to Supabase]
        O2 --> O3[139 Tables Complete]
    end
    
    style I1 fill:#00d4ff
    style I2 fill:#00d4ff
    style E3 fill:#ff8800
    style E4 fill:#ff8800
    style T5 fill:#ff8800
    style C3 fill:#00ff88
    style V4 fill:#ff4444
    style O3 fill:#00ff88
```

---

## Related Documentation

- [ETL.md](ETL.md) - ETL process documentation
- [DATA_DICTIONARY.md](../data/DATA_DICTIONARY.md) - Complete data dictionary
- [CALCULATION_FLOWS.md](../data/CALCULATION_FLOWS.md) - Calculation flow diagrams

---

*Last Updated: 2026-01-15*
