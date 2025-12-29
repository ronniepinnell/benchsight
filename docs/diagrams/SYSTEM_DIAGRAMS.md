# BenchSight System Diagrams
## Mermaid Source Files

---

## 1. ETL Pipeline Flow

```mermaid
flowchart LR
    subgraph Sources["📁 Source Files"]
        TRACK[/"18969_tracking.xlsx"/]
        VIDEO[/"18969_video_times.xlsx"/]
        BLB[/"BLB_Tables.xlsx"/]
        ROSTER[/"roster.json"/]
    end
    
    subgraph ETL["🔄 ETL Pipeline"]
        ORCH[["etl_orchestrator.py"]]
        LOAD["Load Stage"]
        TRANS["Transform"]
        FK["FK Population"]
        VAL["Validation"]
    end
    
    subgraph Output["📊 Output"]
        DIM[("40 Dim Tables")]
        FACT[("37 Fact Tables")]
    end
    
    subgraph Target["☁️ Target"]
        SUPA[(Supabase)]
        PBI["Power BI"]
    end
    
    TRACK --> LOAD
    VIDEO --> LOAD
    BLB --> LOAD
    ROSTER --> LOAD
    
    LOAD --> ORCH
    ORCH --> TRANS
    TRANS --> FK
    FK --> VAL
    
    VAL --> DIM
    VAL --> FACT
    
    DIM --> SUPA
    FACT --> SUPA
    SUPA --> PBI
```

---

## 2. Data Model (Star Schema)

```mermaid
erDiagram
    dim_player ||--o{ fact_events_player : "player_id"
    dim_player ||--o{ fact_shifts_player : "player_id"
    dim_player ||--o{ fact_player_game_stats : "player_id"
    dim_player ||--o{ fact_h2h : "player_1_id"
    
    dim_schedule ||--o{ fact_events : "game_id"
    dim_schedule ||--o{ fact_shifts : "game_id"
    dim_schedule ||--o{ fact_player_game_stats : "game_id"
    
    dim_team ||--o{ fact_events : "home_team_id"
    dim_team ||--o{ fact_events : "away_team_id"
    dim_team ||--o{ fact_line_combos : "team_id"
    
    dim_event_type ||--o{ fact_events : "event_type_id"
    dim_event_detail ||--o{ fact_events : "event_detail_id"
    dim_period ||--o{ fact_events : "period_id"
    dim_venue ||--o{ fact_events : "venue_id"
    dim_zone ||--o{ fact_events : "zone_id"
    
    dim_strength ||--o{ fact_shifts_player : "strength_id"
    dim_situation ||--o{ fact_shifts_player : "situation_id"
    
    dim_player {
        string player_id PK
        string player_full_name
        string player_primary_position
        int skill_rating
    }
    
    dim_schedule {
        string game_id PK
        string season_id FK
        date date
        string home_team_id FK
        string away_team_id FK
    }
    
    dim_team {
        string team_id PK
        string team_name
        string league_id FK
    }
    
    fact_events {
        string event_key PK
        string game_id FK
        int event_index
        string event_type_id FK
        string player_id FK
    }
    
    fact_player_game_stats {
        string player_game_key PK
        string game_id FK
        string player_id FK
        int goals
        int assists
        int toi_seconds
    }
```

---

## 3. Fact Table Relationships

```mermaid
flowchart TB
    subgraph Events["Event Tables"]
        FE[fact_events]
        FEP[fact_events_player]
        FEL[fact_events_long]
        FLE[fact_linked_events]
    end
    
    subgraph Shifts["Shift Tables"]
        FS[fact_shifts]
        FSP[fact_shifts_player]
        FSL[fact_shifts_long]
    end
    
    subgraph Stats["Stats Tables"]
        PGS[fact_player_game_stats]
        GGS[fact_goalie_game_stats]
        TGS[fact_team_game_stats]
    end
    
    subgraph Analytics["Analytics Tables"]
        H2H[fact_h2h]
        WOWY[fact_wowy]
        LC[fact_line_combos]
        PPS[fact_player_pair_stats]
    end
    
    subgraph Sequences["Sequence Tables"]
        SEQ[fact_sequences]
        PLY[fact_plays]
        EC[fact_event_chains]
        RE[fact_rush_events]
    end
    
    FE --> FEP
    FE --> FEL
    FE --> FLE
    
    FS --> FSP
    FS --> FSL
    
    FEP --> PGS
    FSP --> PGS
    
    FSP --> H2H
    FSP --> WOWY
    FSP --> LC
    
    FE --> SEQ
    SEQ --> PLY
    FE --> EC
    EC --> RE
```

---

## 4. FK Population Flow

```mermaid
flowchart LR
    subgraph Source["Source Columns"]
        PERIOD["period (1,2,3)"]
        VENUE["venue (home/away)"]
        ETYPE["event_type"]
        SUCCESS["event_successful (s/u)"]
    end
    
    subgraph Matching["FK Matching"]
        DIRECT["Direct Match"]
        FUZZY["Fuzzy Match"]
        EQUIV["old_equiv Lookup"]
        POTVAL["potential_values"]
    end
    
    subgraph Dims["Dimension Lookups"]
        DP["dim_period"]
        DV["dim_venue"]
        DET["dim_event_type"]
        DS["dim_success"]
    end
    
    subgraph Output["FK Columns"]
        PID["period_id"]
        VID["venue_id"]
        ETID["event_type_id"]
        SID["success_id"]
    end
    
    PERIOD --> DIRECT
    VENUE --> FUZZY
    ETYPE --> DIRECT
    SUCCESS --> POTVAL
    
    DIRECT --> DP
    FUZZY --> DV
    DIRECT --> DET
    POTVAL --> DS
    
    DP --> PID
    DV --> VID
    DET --> ETID
    DS --> SID
```

---

## 5. Validation Pipeline

```mermaid
flowchart TB
    subgraph Tests["54 Validation Tests"]
        G["Goal Verification (8)"]
        T["TOI Calculations (6)"]
        P["Plus/Minus (4)"]
        F["FK Integrity (10)"]
        D["Data Quality (12)"]
        A["Aggregations (8)"]
        X["Cross-Table (6)"]
    end
    
    subgraph Sources["Validation Sources"]
        CSV["CSV Files"]
        NORAD["NORAD Official"]
        CALC["Calculations"]
    end
    
    subgraph Results["Results"]
        PASS["✅ PASS"]
        FAIL["❌ FAIL"]
        WARN["⚠️ WARNING"]
    end
    
    CSV --> G
    CSV --> T
    CSV --> P
    CSV --> F
    CSV --> D
    CSV --> A
    CSV --> X
    
    NORAD --> G
    CALC --> T
    CALC --> P
    
    G --> PASS
    T --> PASS
    P --> PASS
    F --> PASS
    D --> PASS
    A --> PASS
    X --> PASS
    
    G -.-> WARN
```

---

## 6. Implementation Phases

```mermaid
gantt
    title BenchSight Implementation Timeline
    dateFormat  YYYY-MM-DD
    
    section Phase 1
    Foundation Design      :done, p1a, 2024-12-01, 7d
    Dimension Tables       :done, p1b, after p1a, 5d
    Fact Tables           :done, p1c, after p1b, 5d
    ETL Pipeline          :done, p1d, after p1c, 7d
    
    section Phase 2
    Basic Stats           :done, p2a, after p1d, 5d
    Advanced Stats        :done, p2b, after p2a, 5d
    H2H/WOWY             :done, p2c, after p2b, 3d
    Line Combos          :done, p2d, after p2c, 2d
    FK Population        :done, p2e, after p2d, 2d
    Validation Suite     :done, p2f, after p2e, 3d
    
    section Phase 3
    Supabase DDL         :active, p3a, 2024-12-30, 1d
    Data Upload          :p3b, after p3a, 1d
    Verification         :p3c, after p3b, 1d
    Power BI             :p3d, after p3c, 2d
    
    section Phase 4
    xG Model             :p4a, after p3d, 7d
    WAR Calculation      :p4b, after p4a, 5d
    Advanced Metrics     :p4c, after p4b, 5d
    
    section Phase 5
    API Layer            :p5a, after p4c, 10d
    Real-time Backend    :p5b, after p5a, 10d
    Production           :p5c, after p5b, 14d
```

---

## 7. System Architecture

```mermaid
C4Context
    title BenchSight System Architecture
    
    Person(user, "Analyst", "Views dashboards and stats")
    Person(tracker, "Tracker", "Records game events")
    
    System_Boundary(benchsight, "BenchSight") {
        System(etl, "ETL Pipeline", "Python scripts")
        System(db, "Supabase", "PostgreSQL database")
        System(bi, "Power BI", "Dashboards")
        System(web, "Web Tracker", "HTML/JS app")
    }
    
    System_Ext(norad, "NORAD Website", "Official game data")
    System_Ext(excel, "Excel Files", "Tracking sheets")
    
    Rel(tracker, web, "Records events")
    Rel(web, excel, "Exports to")
    Rel(excel, etl, "Ingested by")
    Rel(etl, db, "Loads data to")
    Rel(db, bi, "Queries")
    Rel(user, bi, "Views")
    Rel(norad, etl, "Reference data")
```

---

## Usage

### View in Browser
Save each mermaid block as a `.mermaid` file and open in:
- Mermaid Live Editor: https://mermaid.live
- VS Code with Mermaid extension
- GitHub (renders automatically in markdown)

### Generate PNG
```bash
# Using mermaid-cli
npm install -g @mermaid-js/mermaid-cli
mmdc -i diagram.mermaid -o diagram.png

# Or use online tool
# https://mermaid.live → Export as PNG
```

---

*Generated: December 29, 2024*
