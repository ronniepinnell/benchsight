# BenchSight Calculation Flow Diagrams

**Visual representation of calculation processes for xG, WAR/GAR, Corsi, Fenwick, and other metrics**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document provides visual flow diagrams for all major calculation processes in BenchSight, showing how raw data flows through transformations to produce final metrics.

---

## xG (Expected Goals) Calculation Flow

### Complete xG Calculation Process

```mermaid
graph TD
    A[Shot Event<br/>fact_events] --> B[Extract Shot Data]
    B --> B1[XY Coordinates<br/>x, y]
    B --> B2[Event Detail<br/>Shot type, outcome]
    B --> B3[Event Detail 2<br/>Shot type modifier]
    B --> B4[Is Rush Flag<br/>is_rush]
    B --> B5[Time Stamp<br/>time_start_total_seconds]
    
    B1 --> C[Calculate Danger Level]
    C --> C1{XY in High Danger Zone?<br/>Net area, close range}
    C --> C2{XY in Medium Danger Zone?<br/>Slot area}
    C --> C3{XY in Low Danger Zone?<br/>Elsewhere}
    
    C1 -->|Yes| D1[Base Rate: 0.25]
    C2 -->|Yes| D2[Base Rate: 0.08]
    C3 -->|Yes| D3[Base Rate: 0.03]
    C1 -->|No| D4[Base Rate: 0.06 default]
    C2 -->|No| D4
    C3 -->|No| D4
    
    D1 --> E[Apply Rush Modifier]
    D2 --> E
    D3 --> E
    D4 --> E
    
    B4 --> F{Is Rush?}
    F -->|Yes| F1[Modifier: 1.3x]
    F -->|No| F2[Modifier: 1.0x]
    
    B4 --> G{Is Rebound?}
    G -->|Yes| G1[Modifier: 1.5x]
    G -->|No| G2[Modifier: 1.0x]
    
    B4 --> H{Is One-Timer?}
    H -->|Yes| H1[Modifier: 1.4x]
    H -->|No| H2[Modifier: 1.0x]
    
    B4 --> I{Is Breakaway?}
    I -->|Yes| I1[Modifier: 2.5x]
    I -->|No| I2[Modifier: 1.0x]
    
    B4 --> J{Is Screened?}
    J -->|Yes| J1[Modifier: 1.2x]
    J -->|No| J2[Modifier: 1.0x]
    
    B4 --> K{Is Deflection?}
    K -->|Yes| K1[Modifier: 1.3x]
    K -->|No| K2[Modifier: 1.0x]
    
    E --> L[Calculate Base xG]
    F1 --> L
    F2 --> L
    G1 --> L
    G2 --> L
    H1 --> L
    H2 --> L
    I1 --> L
    I2 --> L
    J1 --> L
    J2 --> L
    K1 --> L
    K2 --> L
    
    L --> M[base_xg = base_rate × rush_modifier]
    
    B3 --> N[Apply Shot Type Modifier]
    N --> N1{Wrist Shot?}
    N --> N2{Slap Shot?}
    N --> N3{Snap Shot?}
    N --> N4{Backhand?}
    N --> N5{Tip?}
    N --> N6{Deflection?}
    
    N1 -->|Yes| O1[Modifier: 1.0x]
    N2 -->|Yes| O2[Modifier: 0.95x]
    N3 -->|Yes| O3[Modifier: 1.05x]
    N4 -->|Yes| O4[Modifier: 0.9x]
    N5 -->|Yes| O5[Modifier: 1.15x]
    N6 -->|Yes| O6[Modifier: 1.1x]
    N1 -->|No| O7[Modifier: 1.0x]
    
    M --> P[Apply Shot Type Modifier]
    O1 --> P
    O2 --> P
    O3 --> P
    O4 --> P
    O5 --> P
    O6 --> P
    O7 --> P
    
    P --> Q[xg_raw = base_xg × shot_type_modifier]
    Q --> R[Cap at 0.95<br/>xg = min xg_raw, 0.95]
    
    R --> S[Group Shots into Sequences<br/>Shots within 3 seconds]
    B5 --> S
    
    S --> T{Sequence Length?}
    T -->|Single Shot| U[No Adjustment<br/>xg_final = xg]
    T -->|Multiple Shots| V[Apply Flurry Adjustment]
    
    V --> V1[Calculate P No Goal<br/>P = ∏ 1-xG_i for all shots]
    V1 --> V2[Calculate P At Least One Goal<br/>P = 1 - P_no_goal]
    V2 --> V3[Cap at 0.99<br/>xg_flurry = min P, 0.99]
    
    U --> W[Sum All Shot xG]
    V3 --> W
    
    W --> X[xg_for = SUM xg_flurry<br/>Per player per game]
    
    style A fill:#00d4ff
    style C fill:#ff8800
    style E fill:#aa66ff
    style L fill:#ff8800
    style P fill:#aa66ff
    style R fill:#ff8800
    style S fill:#aa66ff
    style V fill:#aa66ff
    style W fill:#00ff88
    style X fill:#00ff88
```

### Flurry Adjustment Detail

```mermaid
graph TD
    A[Shot Sequence<br/>Multiple shots within 3 seconds] --> B[Extract xG Values<br/>xG_1, xG_2, xG_3, ...]
    
    B --> C[Calculate P No Goal<br/>P_no = 1-xG_1 × 1-xG_2 × ...]
    
    C --> D[Calculate P At Least One Goal<br/>P_goal = 1 - P_no]
    
    D --> E[Cap at 0.99<br/>xg_flurry = min P_goal, 0.99]
    
    E --> F[Use xg_flurry<br/>Instead of sum of individual xG]
    
    G[Single Shot<br/>No sequence] --> H[Use Raw xG<br/>No adjustment]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#aa66ff
    style D fill:#aa66ff
    style E fill:#ff8800
    style F fill:#00ff88
    style G fill:#00d4ff
    style H fill:#00ff88
```

---

## WAR/GAR Calculation Flow

### Complete WAR/GAR Calculation Process

```mermaid
graph TD
    A[Player Stats<br/>fact_player_game_stats] --> B[Extract Base Stats]
    
    B --> B1[goals, assists, sog]
    B --> B2[takeaways, blocks]
    B --> B3[cf_pct, toi_seconds]
    B --> B4[zone_entries, zone_exits]
    B --> B5[pressure_success_count]
    B --> B6[xg_for, shot_assists]
    
    B1 --> C[GAR Offense Calculation]
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
    
    B2 --> D[GAR Defense Calculation]
    D --> D1[takeaways × 0.05]
    D --> D2[blocks × 0.02]
    D --> D3[zone_exit_controlled × 0.03]
    
    D1 --> D4[Sum: GAR_defense]
    D2 --> D4
    D3 --> D4
    
    B3 --> E[GAR Possession Calculation]
    E --> E1[cf_pct - 50.0]
    E1 --> E2[Divide by 100]
    E2 --> E3[Multiply by 0.02]
    E3 --> E4[Multiply by toi_hours<br/>toi_seconds / 3600]
    E4 --> E5[Multiply by 60]
    E5 --> E6[GAR_possession]
    
    B4 --> F[GAR Transition Calculation]
    F --> F1[zone_entry_controlled × 0.04]
    F1 --> F2[GAR_transition]
    
    B5 --> G[GAR Poise Calculation]
    G --> G1[pressure_success_count × 0.02]
    G1 --> G2[GAR_poise]
    
    C7 --> H[GAR Total]
    D4 --> H
    E6 --> H
    F2 --> H
    G2 --> H
    
    H --> I[GAR_total = Sum of all components]
    
    I --> J[WAR Calculation]
    J --> J1[WAR = GAR_total / 4.5<br/>4.5 goals per win]
    J1 --> K[Final WAR Value]
    
    I --> L[WAR Pace Calculation]
    L --> L1[WAR_pace = WAR × 20<br/>20 games per season]
    L1 --> M[Season Projection]
    
    style A fill:#00d4ff
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#ff8800
    style G fill:#ff8800
    style H fill:#aa66ff
    style I fill:#00ff88
    style J fill:#aa66ff
    style K fill:#00ff88
    style L fill:#aa66ff
    style M fill:#00ff88
```

### GAR Component Breakdown

```mermaid
graph LR
    A[Player Performance] --> B[GAR Components]
    
    B --> C[Offense GAR<br/>Scoring, Playmaking]
    B --> D[Defense GAR<br/>Takeaways, Blocks]
    B --> E[Possession GAR<br/>CF% Impact]
    B --> F[Transition GAR<br/>Zone Entries]
    B --> G[Poise GAR<br/>Pressure Performance]
    
    C --> H[GAR Total]
    D --> H
    E --> H
    F --> H
    G --> H
    
    H --> I[WAR = GAR / 4.5]
    
    style A fill:#00d4ff
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#ff8800
    style G fill:#ff8800
    style H fill:#aa66ff
    style I fill:#00ff88
```

---

## Corsi/Fenwick Calculation Flow

### Corsi Event Identification

```mermaid
graph TD
    A[Event<br/>fact_events] --> B{Event Type = 'Shot'?}
    
    B -->|No| Z[Not Corsi]
    B -->|Yes| C{Event Detail?}
    
    C -->|Shot_OnNetSaved| D[SOG Event]
    C -->|Shot_OnNet| D
    C -->|Shot_Goal| D
    C -->|Shot_Missed| E[Missed Shot]
    C -->|Shot_MissedPost| E
    C -->|Blocked| F[Blocked Shot]
    C -->|Other| Z
    
    D --> G[Corsi Event ✅]
    E --> G
    F --> G
    
    D --> H[Fenwick Event ✅]
    E --> H
    F --> I[NOT Fenwick ❌]
    
    G --> J[Count Corsi For<br/>Player's team events]
    G --> K[Count Corsi Against<br/>Opponent team events<br/>Player on ice]
    
    H --> L[Count Fenwick For<br/>Player's team events]
    H --> M[Count Fenwick Against<br/>Opponent team events<br/>Player on ice]
    
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
    style I fill:#ff4444
    style J fill:#aa66ff
    style K fill:#aa66ff
    style L fill:#aa66ff
    style M fill:#aa66ff
    style N fill:#00ff88
    style O fill:#00ff88
```

### Corsi/Fenwick Aggregation

```mermaid
graph TD
    A[fact_events<br/>All game events] --> B[Filter: Player Events<br/>event_player_1 = player_id]
    
    B --> C[Identify Corsi Events<br/>is_corsi_event = True]
    B --> D[Identify Fenwick Events<br/>is_fenwick_event = True]
    
    C --> E[Filter: Player's Team<br/>team_id = player_team_id]
    C --> F[Filter: Opponent Team<br/>team_id = opponent_team_id<br/>AND player on ice]
    
    D --> G[Filter: Player's Team<br/>team_id = player_team_id]
    D --> H[Filter: Opponent Team<br/>team_id = opponent_team_id<br/>AND player on ice]
    
    E --> I[Count: Corsi For CF]
    F --> J[Count: Corsi Against CA]
    
    G --> K[Count: Fenwick For FF]
    H --> L[Count: Fenwick Against FA]
    
    I --> M[Calculate CF%<br/>CF / CF+CA × 100]
    J --> M
    
    K --> N[Calculate FF%<br/>FF / FF+FA × 100]
    L --> N
    
    M --> O[Store in fact_player_game_stats]
    N --> O
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#aa66ff
    style D fill:#aa66ff
    style E fill:#aa66ff
    style F fill:#aa66ff
    style G fill:#aa66ff
    style H fill:#aa66ff
    style I fill:#00ff88
    style J fill:#00ff88
    style K fill:#00ff88
    style L fill:#00ff88
    style M fill:#00ff88
    style N fill:#00ff88
    style O fill:#00ff88
```

---

## Game Score Calculation Flow

### Game Score Components

```mermaid
graph TD
    A[Player Stats<br/>fact_player_game_stats] --> B[Game Score Components]
    
    B --> C[Scoring Component]
    C --> C1[goals × 1.0]
    C --> C2[primary_assists × 0.8]
    C --> C3[secondary_assists × 0.5]
    C1 --> C4[gs_scoring]
    C2 --> C4
    C3 --> C4
    
    B --> D[Shots Component]
    D --> D1[sog × 0.1]
    D --> D2[shots_high_danger × 0.15]
    D1 --> D3[gs_shots]
    D2 --> D3
    
    B --> E[Playmaking Component]
    E --> E1[zone_ent_controlled × 0.08]
    E --> E2[second_touch × 0.02]
    E --> E3[shot_assists × 0.15]
    E1 --> E4[gs_playmaking]
    E2 --> E4
    E3 --> E4
    
    B --> F[Defense Component]
    F --> F1[takeaways × 0.15]
    F --> F2[blocks × 0.08]
    F --> F3[poke_checks × 0.05]
    F1 --> F4[gs_defense]
    F2 --> F4
    F3 --> F4
    
    B --> G[Hustle Component]
    G --> G1[fo_wins - fo_losses]
    G1 --> G2[× 0.03]
    G2 --> G3[gs_hustle]
    
    B --> H[Poise Component]
    H --> H1[poise_index × 0.2]
    H1 --> H2[gs_poise]
    
    B --> I[Penalty Component]
    I --> I1[giveaways × -0.08]
    I1 --> I2[gs_penalties]
    
    C4 --> J[Game Score Raw]
    D3 --> J
    E4 --> J
    F4 --> J
    G3 --> J
    H2 --> J
    I2 --> J
    
    J --> K[Game Score<br/>game_score = 2.0 + raw]
    
    K --> L[Offensive Game Score<br/>gs_scoring + gs_shots + gs_playmaking]
    K --> M[Defensive Game Score<br/>gs_defense + gs_hustle - giveaways×0.08]
    
    K --> N[Calculated Rating<br/>Map game_score to 2-6 scale]
    
    style A fill:#00d4ff
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#ff8800
    style G fill:#ff8800
    style H fill:#ff8800
    style I fill:#ff8800
    style J fill:#aa66ff
    style K fill:#00ff88
    style L fill:#00ff88
    style M fill:#00ff88
    style N fill:#00ff88
```

---

## Rate Stats Calculation Flow

### Per-60 Statistics

```mermaid
graph TD
    A[Player Stats<br/>fact_player_game_stats] --> B[Extract Stats]
    
    B --> B1[goals, assists, points]
    B --> B2[shots, sog]
    B --> B3[toi_seconds]
    
    B3 --> C[Calculate TOI Hours<br/>toi_hours = toi_seconds / 3600]
    
    B1 --> D[Calculate Per-60 Stats]
    B2 --> D
    
    D --> D1[goals_per_60 = goals / toi_hours × 60]
    D --> D2[assists_per_60 = assists / toi_hours × 60]
    D --> D3[points_per_60 = points / toi_hours × 60]
    D --> D4[shots_per_60 = shots / toi_hours × 60]
    D --> D5[sog_per_60 = sog / toi_hours × 60]
    
    C --> D1
    C --> D2
    C --> D3
    C --> D4
    C --> D5
    
    D1 --> E[Store in fact_player_game_stats]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#aa66ff
    style D fill:#aa66ff
    style E fill:#00ff88
```

---

## Related Documentation

- [DATA_DICTIONARY.md](DATA_DICTIONARY.md) - Complete data dictionary with formulas
- [ETL_FLOW_DIAGRAMS.md](../etl/ETL_FLOW_DIAGRAMS.md) - ETL process diagrams
- [ETL.md](../etl/ETL.md) - ETL documentation

---

*Last Updated: 2026-01-15*
