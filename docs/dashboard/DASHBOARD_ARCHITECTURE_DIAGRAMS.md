# BenchSight Dashboard Architecture Diagrams

**Visual representation of dashboard architecture, component structure, and data flow**

Last Updated: 2026-01-15  
Version: 1.0

---

## Overview

This document provides visual diagrams of the BenchSight Dashboard architecture, including component structure, data flow, and user journey flows.

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Recharts, Supabase

---

## Component Architecture

### Page Structure

```mermaid
graph TD
    A[Dashboard Root<br/>app/] --> B[Players Pages]
    A --> C[Teams Pages]
    A --> D[Games Pages]
    A --> E[Goalies Pages]
    A --> F[Standings Pages]
    A --> G[Leaders Pages]
    A --> H[Analytics Pages]
    
    B --> B1[app/players/page.tsx<br/>Player List]
    B --> B2[app/players/[id]/page.tsx<br/>Player Detail]
    B --> B3[app/players/[id]/stats/page.tsx<br/>Player Stats]
    B --> B4[app/players/[id]/games/page.tsx<br/>Player Games]
    
    C --> C1[app/teams/page.tsx<br/>Team List]
    C --> C2[app/teams/[id]/page.tsx<br/>Team Detail]
    C --> C3[app/teams/[id]/stats/page.tsx<br/>Team Stats]
    C --> C4[app/teams/[id]/games/page.tsx<br/>Team Games]
    
    D --> D1[app/games/page.tsx<br/>Game List]
    D --> D2[app/games/[id]/page.tsx<br/>Game Detail]
    D --> D3[app/games/[id]/boxscore/page.tsx<br/>Boxscore]
    
    E --> E1[app/goalies/page.tsx<br/>Goalie List]
    E --> E2[app/goalies/[id]/page.tsx<br/>Goalie Detail]
    
    F --> F1[app/standings/page.tsx<br/>Standings Table]
    
    G --> G1[app/leaders/page.tsx<br/>League Leaders]
    
    H --> H1[app/analytics/page.tsx<br/>Analytics Dashboard]
    H --> H2[app/analytics/xg/page.tsx<br/>xG Analysis]
    H --> H3[app/analytics/war/page.tsx<br/>WAR/GAR Analysis]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#ff8800
    style G fill:#ff8800
    style H fill:#ff8800
```

### Component Hierarchy

```mermaid
graph TD
    A[Page Component<br/>app/players/[id]/page.tsx] --> B[Layout Component<br/>components/layout/]
    A --> C[Player Detail Component<br/>components/players/PlayerDetail.tsx]
    
    B --> B1[Header<br/>components/layout/Header.tsx]
    B --> B2[Navigation<br/>components/layout/Navigation.tsx]
    B --> B3[Footer<br/>components/layout/Footer.tsx]
    
    C --> C1[Player Stats Table<br/>components/tables/StatsTable.tsx]
    C --> C2[Player Charts<br/>components/charts/PlayerCharts.tsx]
    C --> C3[Player Info Card<br/>components/cards/PlayerInfo.tsx]
    
    C1 --> D1[Data Table<br/>components/ui/data-table.tsx]
    C2 --> D2[Recharts Components<br/>components/charts/]
    C3 --> D3[Card Component<br/>components/ui/card.tsx]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D1 fill:#aa66ff
    style D2 fill:#aa66ff
    style D3 fill:#aa66ff
```

---

## Data Flow Diagram

### Supabase → Dashboard Flow

```mermaid
sequenceDiagram
    participant User
    participant Page as Next.js Page
    participant Component as React Component
    participant Supabase as Supabase Client
    participant DB as Supabase Database
    
    User->>Page: Navigate to /players/123
    Page->>Component: Render PlayerDetail
    Component->>Supabase: Query fact_player_game_stats
    Supabase->>DB: SELECT * FROM fact_player_game_stats<br/>WHERE player_id = '123'
    DB-->>Supabase: Return player stats
    Supabase-->>Component: Player stats data
    Component->>Component: Process data
    Component-->>Page: Render stats table
    Page-->>User: Display player page
    
    User->>Page: Filter by season
    Page->>Component: Update season filter
    Component->>Supabase: Query with season filter
    Supabase->>DB: SELECT * FROM fact_player_game_stats<br/>WHERE player_id = '123'<br/>AND season_id = 'S2024'
    DB-->>Supabase: Filtered data
    Supabase-->>Component: Updated stats
    Component-->>Page: Re-render with new data
    Page-->>User: Updated display
```

### Data Flow Architecture

```mermaid
graph LR
    A[(Supabase Database)] --> B[Supabase Client<br/>@supabase/supabase-js]
    B --> C[API Routes<br/>app/api/]
    B --> D[Server Components<br/>app/**/page.tsx]
    B --> E[Client Components<br/>components/**]
    
    C --> F[Data Fetching<br/>Server-side]
    D --> G[Data Fetching<br/>Server-side]
    E --> H[Data Fetching<br/>Client-side]
    
    F --> I[React Components]
    G --> I
    H --> I
    
    I --> J[UI Rendering<br/>Tables, Charts, Cards]
    
    K[User Actions] --> L[State Updates]
    L --> E
    E --> B
    B --> A
    
    style A fill:#00ff88
    style B fill:#00d4ff
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style I fill:#aa66ff
    style J fill:#00ff88
```

### Real-Time Update Flow (Future)

```mermaid
graph TD
    A[ETL Completes] --> B[Supabase Database Updated]
    B --> C[Supabase Realtime<br/>PostgreSQL Changes]
    C --> D[Supabase Client<br/>Subscription]
    D --> E[React Component<br/>useEffect Hook]
    E --> F[Update State]
    F --> G[Re-render Component]
    G --> H[User Sees Updated Data]
    
    style A fill:#00d4ff
    style B fill:#00ff88
    style C fill:#00d4ff
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#aa66ff
    style G fill:#aa66ff
    style H fill:#00ff88
```

---

## User Journey Flow

### Navigation Paths

```mermaid
graph TD
    A[Home/Dashboard] --> B[Players]
    A --> C[Teams]
    A --> D[Games]
    A --> E[Goalies]
    A --> F[Standings]
    A --> G[Leaders]
    A --> H[Analytics]
    
    B --> B1[Player List]
    B1 --> B2[Player Detail]
    B2 --> B3[Player Stats]
    B2 --> B4[Player Games]
    B2 --> B5[Player Comparison]
    
    C --> C1[Team List]
    C1 --> C2[Team Detail]
    C2 --> C3[Team Stats]
    C2 --> C4[Team Games]
    C2 --> C5[Team Roster]
    
    D --> D1[Game List]
    D1 --> D2[Game Detail]
    D2 --> D3[Boxscore]
    D2 --> D4[Game Events]
    D2 --> D5[Game Charts]
    
    E --> E1[Goalie List]
    E1 --> E2[Goalie Detail]
    E2 --> E3[Goalie Stats]
    
    F --> F1[Standings Table]
    F1 --> F2[Team Detail]
    
    G --> G1[League Leaders]
    G1 --> G2[Player Detail]
    
    H --> H1[Analytics Dashboard]
    H1 --> H2[xG Analysis]
    H1 --> H3[WAR/GAR Analysis]
    H1 --> H4[RAPM Analysis]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#ff8800
    style G fill:#ff8800
    style H fill:#ff8800
```

### Feature Access Flow

```mermaid
graph TD
    A[User Lands on Page] --> B{Page Type?}
    
    B -->|List Page| C[Display Table/List]
    B -->|Detail Page| D[Display Detail View]
    B -->|Analytics Page| E[Display Analytics]
    
    C --> F[User Clicks Item]
    F --> G[Navigate to Detail]
    
    D --> H[User Interacts]
    H --> I{Action Type?}
    
    I -->|Filter| J[Apply Filter]
    I -->|Sort| K[Sort Table]
    I -->|Search| L[Search Results]
    I -->|Export| M[Export Data]
    I -->|View Stats| N[Navigate to Stats Page]
    
    J --> O[Update Query]
    K --> O
    L --> O
    O --> P[Fetch New Data]
    P --> Q[Re-render Component]
    
    E --> R[User Selects Metric]
    R --> S[Update Chart]
    S --> T[Display Visualization]
    
    style A fill:#00d4ff
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style O fill:#aa66ff
    style P fill:#00d4ff
    style Q fill:#00ff88
```

---

## Component Data Flow

### Player Detail Page Flow

```mermaid
graph TD
    A[Player Detail Page<br/>app/players/[id]/page.tsx] --> B[Fetch Player Data]
    
    B --> B1[Supabase Query<br/>fact_player_game_stats<br/>WHERE player_id = id]
    B --> B2[Supabase Query<br/>dim_player<br/>WHERE player_id = id]
    B --> B3[Supabase Query<br/>fact_player_season_stats<br/>WHERE player_id = id]
    
    B1 --> C[Process Data]
    B2 --> C
    B3 --> C
    
    C --> D[Player Detail Component]
    D --> D1[Player Info Card<br/>Name, Team, Position]
    D --> D2[Player Stats Table<br/>Game-by-game stats]
    D --> D3[Player Charts<br/>Trends, comparisons]
    D --> D4[Season Summary<br/>Season totals]
    
    D1 --> E[Render UI]
    D2 --> E
    D3 --> E
    D4 --> E
    
    E --> F[User Sees Player Page]
    
    F --> G{User Action?}
    G -->|Filter Season| H[Update Query]
    G -->|Sort Stats| I[Sort Data]
    G -->|Export| J[Export CSV]
    G -->|View Game| K[Navigate to Game]
    
    H --> B1
    I --> D2
    J --> L[Download CSV]
    K --> M[Game Detail Page]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#aa66ff
    style D fill:#ff8800
    style E fill:#00ff88
    style F fill:#00ff88
```

### Caching Strategy

```mermaid
graph TD
    A[Data Request] --> B{Cache Check}
    
    B -->|Cache Hit| C[Return Cached Data]
    B -->|Cache Miss| D[Fetch from Supabase]
    
    D --> E[Store in Cache]
    E --> F[Return Data]
    
    C --> G[Render Component]
    F --> G
    
    H[Cache Invalidation] --> I{Trigger?}
    I -->|ETL Complete| J[Clear Cache]
    I -->|Time Expired| J
    I -->|Manual Refresh| J
    
    J --> K[Next Request Fetches Fresh]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#00ff88
    style D fill:#ff8800
    style E fill:#aa66ff
    style G fill:#00ff88
    style H fill:#ff4444
    style J fill:#ff4444
```

---

## Component Library Structure

### Reusable Components

```mermaid
graph TD
    A[Component Library<br/>components/] --> B[UI Components<br/>components/ui/]
    A --> C[Feature Components<br/>components/players/]
    A --> D[Layout Components<br/>components/layout/]
    A --> E[Chart Components<br/>components/charts/]
    A --> F[Table Components<br/>components/tables/]
    
    B --> B1[Button<br/>components/ui/button.tsx]
    B --> B2[Card<br/>components/ui/card.tsx]
    B --> B3[Input<br/>components/ui/input.tsx]
    B --> B4[Select<br/>components/ui/select.tsx]
    B --> B5[Data Table<br/>components/ui/data-table.tsx]
    
    C --> C1[PlayerDetail<br/>components/players/PlayerDetail.tsx]
    C --> C2[PlayerStats<br/>components/players/PlayerStats.tsx]
    C --> C3[PlayerCharts<br/>components/players/PlayerCharts.tsx]
    
    D --> D1[Header<br/>components/layout/Header.tsx]
    D --> D2[Navigation<br/>components/layout/Navigation.tsx]
    D --> D3[Footer<br/>components/layout/Footer.tsx]
    
    E --> E1[LineChart<br/>components/charts/LineChart.tsx]
    E --> E2[BarChart<br/>components/charts/BarChart.tsx]
    E --> E3[ShotMap<br/>components/charts/ShotMap.tsx]
    
    F --> F1[StatsTable<br/>components/tables/StatsTable.tsx]
    F --> F2[StandingsTable<br/>components/tables/StandingsTable.tsx]
    
    style A fill:#00d4ff
    style B fill:#aa66ff
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#ff8800
```

---

## State Management Flow

### Client-Side State

```mermaid
graph TD
    A[Page Component] --> B[React State<br/>useState]
    A --> C[URL State<br/>searchParams]
    A --> D[Server State<br/>Server Components]
    
    B --> E[Local UI State<br/>Filters, Sort, Search]
    C --> F[Route State<br/>Season, Game Type]
    D --> G[Data State<br/>Player/Team/Game Data]
    
    E --> H[Component Re-render]
    F --> H
    G --> H
    
    I[User Action] --> J{Action Type?}
    J -->|Filter Change| E
    J -->|Navigation| C
    J -->|Data Refresh| D
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#aa66ff
    style F fill:#aa66ff
    style G fill:#aa66ff
    style H fill:#00ff88
```

---

## Related Documentation

- [DASHBOARD_ROADMAP.md](DASHBOARD_ROADMAP.md) - Dashboard roadmap
- [API.md](../api/API.md) - API documentation
- [DATA_DICTIONARY.md](../data/DATA_DICTIONARY.md) - Data dictionary

---

*Last Updated: 2026-01-15*
