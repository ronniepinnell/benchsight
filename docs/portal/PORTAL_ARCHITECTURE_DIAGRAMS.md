# BenchSight Portal Architecture Diagrams

**Visual representation of portal architecture, component structure, and data flow**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document provides visual diagrams of the BenchSight Admin Portal architecture, including component structure, data flow, and API integration patterns.

**Tech Stack:** HTML, JavaScript, FastAPI (API)

---

## Portal Component Structure

### UI Sections

```mermaid
graph TD
    A[Portal Root<br/>index.html] --> B[Header Section]
    A --> C[Main Content]
    A --> D[Footer Section]
    
    B --> B1[Logo/Branding]
    B --> B2[User Menu]
    B --> B3[Navigation]
    
    C --> E[ETL Control Section]
    C --> F[Game Management Section]
    C --> G[Data Browser Section]
    C --> H[Settings Section]
    
    E --> E1[Trigger ETL Button]
    E --> E2[ETL Status Display]
    E --> E3[ETL History Table]
    E --> E4[Progress Bar]
    
    F --> F1[Game List Table]
    F --> F2[Create Game Form]
    F --> F3[Edit Game Form]
    F --> F4[Delete Game Button]
    
    G --> G1[Table List]
    G --> G2[Table Data Browser]
    G --> G3[Table Schema Viewer]
    G --> G4[Export Button]
    
    H --> H1[User Preferences]
    H --> H2[API Configuration]
    H --> H3[Theme Settings]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style E fill:#aa66ff
    style F fill:#aa66ff
    style G fill:#aa66ff
    style H fill:#aa66ff
```

### Component Hierarchy

```mermaid
graph TD
    A[Portal App<br/>index.html] --> B[ETL Control Component]
    A --> C[Game Management Component]
    A --> D[Data Browser Component]
    A --> E[Settings Component]
    
    B --> B1[ETL Trigger Button]
    B --> B2[Status Poller]
    B --> B3[History Table]
    B --> B4[Progress Display]
    
    C --> C1[Game List Component]
    C --> C2[Game Form Component]
    C --> C3[Game Filters]
    
    D --> D1[Table List Component]
    D --> D2[Data Table Component]
    D --> D3[Pagination Component]
    D --> D4[Search/Filter Component]
    
    E --> E1[Settings Form]
    E --> E2[API Config Form]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
```

---

## Portal Data Flow

### ETL Control Flow

```mermaid
sequenceDiagram
    participant User
    participant Portal as Portal UI
    participant API as FastAPI
    participant JobMgr as Job Manager
    participant ETL as ETL Service
    participant DB as Supabase
    
    User->>Portal: Click "Trigger ETL"
    Portal->>API: POST /api/etl/trigger<br/>{mode: "full"}
    API->>JobMgr: Create job
    JobMgr->>DB: Store job record
    JobMgr-->>API: Return job_id
    API-->>Portal: {job_id, status: "pending"}
    
    Portal->>Portal: Store job_id
    Portal->>Portal: Start status polling
    
    loop Every 2 seconds
        Portal->>API: GET /api/etl/status/{job_id}
        API->>JobMgr: Get job status
        JobMgr->>DB: Query job
        DB-->>JobMgr: Job status
        JobMgr-->>API: Status response
        API-->>Portal: {status, progress, message}
        Portal->>Portal: Update UI
    end
    
    Note over ETL,DB: ETL runs in background
    ETL->>DB: Update job status
    DB-->>Portal: Status updates via polling
    
    ETL->>ETL: Complete
    ETL->>DB: Update status: "complete"
    Portal->>API: GET /api/etl/status/{job_id}
    API-->>Portal: {status: "complete"}
    Portal->>Portal: Stop polling
    Portal->>User: Show success message
```

### Game Management Flow

```mermaid
graph TD
    A[Portal: Game Management] --> B[Load Game List]
    B --> C[GET /api/games<br/>Fetch games from Supabase]
    C --> D[(Supabase Database)]
    D --> E[Return game list]
    E --> F[Display in table]
    
    F --> G{User Action?}
    G -->|Create Game| H[Show Create Form]
    G -->|Edit Game| I[Show Edit Form]
    G -->|Delete Game| J[Show Delete Confirmation]
    
    H --> K[POST /api/games<br/>Create game]
    K --> D
    D --> L[Return created game]
    L --> M[Update game list]
    
    I --> N[PUT /api/games/{id}<br/>Update game]
    N --> D
    D --> O[Return updated game]
    O --> M
    
    J --> P[DELETE /api/games/{id}<br/>Delete game]
    P --> D
    D --> Q[Return success]
    Q --> M
    
    M --> F
    
    style A fill:#00d4ff
    style C fill:#ff8800
    style D fill:#00ff88
    style K fill:#ff8800
    style N fill:#ff8800
    style P fill:#ff8800
```

### Data Browser Flow

```mermaid
graph TD
    A[Portal: Data Browser] --> B[Load Table List]
    B --> C[GET /api/tables<br/>List all tables]
    C --> D[(Supabase Database)]
    D --> E[Return table metadata]
    E --> F[Display table list]
    
    F --> G[User Selects Table]
    G --> H[Load Table Data]
    H --> I[GET /api/tables/{name}/data<br/>With pagination]
    I --> D
    D --> J[Return table data]
    J --> K[Display in data table]
    
    K --> L{User Action?}
    L -->|Search| M[Filter data]
    L -->|Sort| N[Sort data]
    L -->|Export| O[Export CSV]
    L -->|View Schema| P[Show schema]
    
    M --> I
    N --> I
    O --> Q[Download CSV]
    P --> R[Display schema info]
    
    style A fill:#00d4ff
    style C fill:#ff8800
    style D fill:#00ff88
    style I fill:#ff8800
    style K fill:#00ff88
```

---

## API Integration Patterns

### Current vs Future Integration

```mermaid
graph LR
    subgraph Current["Current (Placeholder)"]
        A1[Portal UI] --> B1[Placeholder Functions<br/>console.log]
        B1 --> C1[No API Calls]
    end
    
    subgraph Future["Future (Integrated)"]
        A2[Portal UI] --> B2[API Client<br/>fetch/axios]
        B2 --> C2[FastAPI Endpoints]
        C2 --> D2[ETL/Upload Services]
        D2 --> E2[(Supabase)]
    end
    
    style A1 fill:#ff4444
    style B1 fill:#ff4444
    style C1 fill:#ff4444
    style A2 fill:#00d4ff
    style B2 fill:#ff8800
    style C2 fill:#ff8800
    style D2 fill:#aa66ff
    style E2 fill:#00ff88
```

### Status Polling Pattern

```mermaid
graph TD
    A[User Triggers ETL] --> B[POST /api/etl/trigger]
    B --> C[Receive job_id]
    C --> D[Start Polling Timer]
    
    D --> E[Wait 2 seconds]
    E --> F[GET /api/etl/status/{job_id}]
    F --> G{Status?}
    
    G -->|pending/running| H[Update Progress Bar]
    G -->|processing| I[Update Status Message]
    G -->|complete| J[Stop Polling]
    G -->|failed| K[Stop Polling<br/>Show Error]
    
    H --> E
    I --> E
    J --> L[Show Success Message]
    K --> M[Show Error Message]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#aa66ff
    style D fill:#aa66ff
    style F fill:#ff8800
    style G fill:#aa66ff
    style J fill:#00ff88
    style K fill:#ff4444
```

---

## User Interaction Flow

### Complete User Journey

```mermaid
graph TD
    A[User Opens Portal] --> B[Portal Loads]
    B --> C[Display Dashboard]
    
    C --> D{User Action?}
    
    D -->|Trigger ETL| E[ETL Control Flow]
    D -->|Manage Games| F[Game Management Flow]
    D -->|Browse Data| G[Data Browser Flow]
    D -->|Settings| H[Settings Flow]
    
    E --> E1[Click Trigger Button]
    E1 --> E2[API Call: Trigger ETL]
    E2 --> E3[Start Status Polling]
    E3 --> E4[Display Progress]
    E4 --> E5[Show Completion]
    
    F --> F1[View Game List]
    F1 --> F2{Action?}
    F2 -->|Create| F3[Create Game Form]
    F2 -->|Edit| F4[Edit Game Form]
    F2 -->|Delete| F5[Delete Confirmation]
    F3 --> F6[API Call: Create]
    F4 --> F7[API Call: Update]
    F5 --> F8[API Call: Delete]
    
    G --> G1[View Table List]
    G1 --> G2[Select Table]
    G2 --> G3[View Table Data]
    G3 --> G4{Action?}
    G4 -->|Search| G5[Filter Data]
    G4 -->|Export| G6[Export CSV]
    G4 -->|View Schema| G7[Show Schema]
    
    H --> H1[View Settings]
    H1 --> H2[Update Preferences]
    H2 --> H3[Save to localStorage]
    
    style A fill:#00d4ff
    style C fill:#00ff88
    style E fill:#ff8800
    style F fill:#ff8800
    style G fill:#ff8800
    style H fill:#ff8800
```

---

## Related Documentation

- [PORTAL.md](PORTAL.md) - Complete portal documentation
- [API_ARCHITECTURE_DIAGRAMS.md](../api/API_ARCHITECTURE_DIAGRAMS.md) - API architecture
- [API.md](../api/API.md) - API reference

---

*Last Updated: 2026-01-15*
