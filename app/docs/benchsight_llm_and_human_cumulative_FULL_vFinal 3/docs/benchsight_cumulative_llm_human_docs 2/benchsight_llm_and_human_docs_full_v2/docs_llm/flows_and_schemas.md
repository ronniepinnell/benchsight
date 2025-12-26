# Flows & Schemas (LLM-Focused)

This file gives you structural diagrams for the BenchSight / BLB project.

Use these diagrams when reasoning about:

- Where to put transformations.
- How tables join.
- How to design new features.

We use Mermaid syntax so humans can render them if desired.

---

## 1. End-to-End Pipeline

```mermaid
flowchart LR
    A[Raw Excel & CSV
BLB_Tables, tracking.xlsx,
XY, shots, video_times] --> B[Stage ETL
src/stage + sql/stage]
    B --> C[Postgres Staging Schema
blb_stage.*]
    C --> D[Intermediate Transforms
src/intermediate + sql/intermediate]
    D --> E[Intermediate Tables
( events_long, shifts_long,
chains, rating_context, xy_joined )]
    E --> F[Mart ETL
src/mart + sql/mart]
    F --> G[Datamart Schema
fact_* and dim_*]
    G --> H[Power BI
Reports & Dashboards]
    G --> I[Python Dash / Render
Interactive BenchSight UI]
    G --> J[ML / Notebooks
xG, microstats models]
```

---

## 2. Core Datamart Star Schema

High-level view (simplified):

```mermaid
erDiagram
    FACT_EVENTS {
        string event_id
        int game_id
        int event_index
        int period
        int team_id_for
        int team_id_against
        int player_id_main
        string event_type_id
        string zone_id
        float x_coord
        float y_coord
        float xg_value
        ...
    }

    FACT_SHIFTS {
        string shift_id
        int game_id
        int player_id
        int team_id
        int period
        int shift_number_in_game
        int shift_segment_count
        float toi_seconds
        float toi_excluding_stoppages
        ...
    }

    FACT_BOX_PLAYER {
        string box_id
        int game_id
        int player_id
        int team_id
        float goals
        float assists
        float shots
        float corsi_for
        float corsi_against
        ...
    }

    DIM_PLAYERS {
        int player_id
        string player_name
        int jersey_number
        int rating_1_to_6
        string handedness
        string primary_position
        ...
    }

    DIM_TEAMS {
        int team_id
        string team_name
        string short_name
        ...
    }

    DIM_GAMES {
        int game_id
        date game_date
        int home_team_id
        int away_team_id
        string league_id
        string game_tracking_status_id
        ...
    }

    DIM_DATES {
        date date_key
        int year
        int month
        int day
        int season
        ...
    }

    DIM_EVENT_TYPES {
        string event_type_id
        string event_group
        string description
        ...
    }

    FACT_EVENTS ||--o{ DIM_PLAYERS : "player_id_main"
    FACT_EVENTS ||--o{ DIM_TEAMS : "team_id_for, team_id_against"
    FACT_EVENTS }o--|| DIM_GAMES : "game_id"
    FACT_SHIFTS }o--|| DIM_PLAYERS : "player_id"
    FACT_SHIFTS }o--|| DIM_TEAMS : "team_id"
    FACT_SHIFTS }o--|| DIM_GAMES : "game_id"
    FACT_BOX_PLAYER }o--|| DIM_PLAYERS : "player_id"
    FACT_BOX_PLAYER }o--|| DIM_TEAMS : "team_id"
    FACT_BOX_PLAYER }o--|| DIM_GAMES : "game_id"
```

Use `table_catalog.csv` for the exact column lists and grain definitions.

---

## 3. Event / Shift / Chain Relationship

Conceptual graph:

```mermaid
flowchart TB
    subgraph Game
        G[Game (game_id)]
    end

    subgraph Shifts
        SL[Shifts Long
1 row = 1 player
for 1 logical shift]
        SW[Shifts Wide
1 row = 1 shift
all players as columns]
    end

    subgraph Events
        EL[Events Long
1 row = 1 player-role
for 1 event]
        EW[Events Wide
1 row = 1 event
players pivoted]
    end

    subgraph Chains
        CSEQ[Sequences
multi-event possessions]
        CPLAY[Plays
within sequences
same team & zone]
        CLINK[Linked Events
like shot + save + rebound]
    end

    G --> SL
    G --> SW
    G --> EL
    G --> EW

    SW --> SL
    EW --> EL

    EL --> CSEQ
    EL --> CPLAY
    EL --> CLINK
```

**Key idea:**

- Shifts and events are both anchored by `game_id`, `period`, and running time.
- Chains/sequences/plays are built on top of ordered events.
- XY and video links join via `linked_event_id` and running timestamps.

Use this mental model when the user asks for new metrics, chain rules,
or visualizations that need to combine these layers.
