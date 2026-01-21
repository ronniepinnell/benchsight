# BenchSight API Architecture Diagrams

**Visual representation of API architecture, endpoints, and integration flows**

Last Updated: 2026-01-15  
Version: 1.0

---

## Overview

This document provides visual diagrams of the BenchSight API architecture, including endpoint maps, job processing flows, and integration patterns.

**Tech Stack:** FastAPI, Python 3.11+, Supabase, Background Tasks

---

## API Endpoint Map

### Complete Endpoint Structure

```mermaid
graph TD
    A[FastAPI Application<br/>api/main.py] --> B[ETL Routes<br/>/api/etl/]
    A --> C[Upload Routes<br/>/api/upload/]
    A --> D[Staging Routes<br/>/api/staging/]
    A --> E[ML Routes<br/>/api/ml/]
    A --> F[Health Routes<br/>/api/health/]
    A --> G[Job Routes<br/>/api/jobs/]
    
    B --> B1[POST /api/etl/trigger<br/>Trigger ETL job]
    B --> B2[GET /api/etl/status<br/>Get ETL status]
    B --> B3[GET /api/etl/history<br/>Get ETL history]
    B --> B4[POST /api/etl/validate<br/>Validate ETL]
    
    C --> C1[POST /api/upload/tables<br/>Upload CSV tables]
    C --> C2[POST /api/upload/schema<br/>Upload schema]
    C --> C3[POST /api/upload/tracking<br/>Upload tracking file]
    
    D --> D1[POST /api/staging/blb<br/>Upload BLB data]
    D --> D2[POST /api/staging/tracking<br/>Upload tracking data]
    D --> D3[GET /api/staging/status<br/>Get staging status]
    
    E --> E1[POST /api/ml/predict<br/>ML predictions]
    E --> E2[GET /api/ml/models<br/>List models]
    
    F --> F1[GET /api/health<br/>Health check]
    F --> F2[GET /api/health/db<br/>Database health]
    
    G --> G1[GET /api/jobs/{job_id}<br/>Get job status]
    G --> G2[GET /api/jobs<br/>List jobs]
    G --> G3[DELETE /api/jobs/{job_id}<br/>Cancel job]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#00ff88
    style G fill:#aa66ff
```

### Endpoint Categories

```mermaid
graph LR
    A[API Endpoints] --> B[ETL Endpoints<br/>4 endpoints]
    A --> C[Upload Endpoints<br/>3 endpoints]
    A --> D[Staging Endpoints<br/>3 endpoints]
    A --> E[ML Endpoints<br/>2 endpoints]
    A --> F[Health Endpoints<br/>2 endpoints]
    A --> G[Job Endpoints<br/>3 endpoints]
    
    B --> B1[Trigger ETL]
    B --> B2[Status Check]
    B --> B3[History]
    B --> B4[Validation]
    
    C --> C1[Upload Tables]
    C --> C2[Upload Schema]
    C --> C3[Upload Tracking]
    
    D --> D1[Upload BLB]
    D --> D2[Upload Tracking]
    D --> D3[Status Check]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#aa66ff
    style F fill:#00ff88
    style G fill:#aa66ff
```

---

## Job Processing Flow

### ETL Job Processing

```mermaid
sequenceDiagram
    participant Portal
    participant API as FastAPI
    participant JobMgr as Job Manager
    participant ETL as ETL Service
    participant DB as Supabase
    
    Portal->>API: POST /api/etl/trigger
    API->>JobMgr: Create ETL job
    JobMgr->>DB: Store job record
    JobMgr-->>API: Return job_id
    API-->>Portal: Job created (job_id)
    
    API->>ETL: Start background task
    ETL->>ETL: Run ETL pipeline
    ETL->>DB: Update job status (running)
    ETL->>ETL: Process games
    ETL->>DB: Update job status (processing)
    ETL->>DB: Upload tables
    ETL->>DB: Update job status (complete)
    
    Portal->>API: GET /api/etl/status/{job_id}
    API->>DB: Query job status
    DB-->>API: Job status
    API-->>Portal: Status response
    
    Note over Portal,DB: Portal polls status every 2 seconds
```

### Job State Machine

```mermaid
stateDiagram-v2
    [*] --> Pending: Create Job
    Pending --> Running: Start ETL
    Running --> Processing: ETL Started
    Processing --> Uploading: Tables Created
    Uploading --> Complete: Upload Success
    Processing --> Failed: Error
    Uploading --> Failed: Upload Error
    Running --> Failed: ETL Error
    Failed --> [*]
    Complete --> [*]
    
    note right of Pending
        Job created,
        waiting to start
    end note
    
    note right of Running
        ETL process started
    end note
    
    note right of Processing
        Creating tables,
        calculating stats
    end note
    
    note right of Uploading
        Uploading to Supabase
    end note
    
    note right of Complete
        Job successful,
        tables available
    end note
    
    note right of Failed
        Error occurred,
        check logs
    end note
```

---

## Integration Architecture

### Portal → API → ETL Flow

```mermaid
graph TD
    A[Admin Portal<br/>UI] --> B[FastAPI<br/>api/main.py]
    B --> C[ETL Service<br/>services/etl_service.py]
    C --> D[ETL Pipeline<br/>run_etl.py]
    D --> E[CSV Files<br/>data/output/]
    E --> F[Upload Service<br/>services/upload_service.py]
    F --> G[(Supabase Database)]
    
    B --> H[Job Manager<br/>services/job_manager.py]
    H --> I[(Job Status DB)]
    
    A --> J[Status Polling<br/>Every 2 seconds]
    J --> B
    B --> I
    I --> A
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#aa66ff
    style E fill:#aa66ff
    style F fill:#ff8800
    style G fill:#00ff88
    style H fill:#aa66ff
    style I fill:#00ff88
```

### Dashboard → API → Supabase Flow

```mermaid
graph LR
    A[Dashboard<br/>Next.js] --> B[Supabase Client<br/>Direct Connection]
    B --> C[(Supabase Database)]
    
    A --> D[API Routes<br/>app/api/]
    D --> E[Supabase Client<br/>Server-side]
    E --> C
    
    F[Future: API Gateway] --> G[FastAPI<br/>api/main.py]
    G --> C
    
    A -.->|Future| F
    
    style A fill:#00d4ff
    style B fill:#00ff88
    style C fill:#00ff88
    style D fill:#ff8800
    style E fill:#00ff88
    style F fill:#aa66ff
    style G fill:#ff8800
```

---

## Request/Response Flow

### ETL Trigger Request Flow

```mermaid
graph TD
    A[Portal: Click Trigger ETL] --> B[POST /api/etl/trigger<br/>Request Body: game_ids]
    
    B --> C[API: Validate Request]
    C --> D{Valid?}
    D -->|No| E[Return 400 Error]
    D -->|Yes| F[Create Job Record]
    
    F --> G[Start Background Task]
    G --> H[Return job_id]
    H --> I[Portal: Store job_id]
    
    G --> J[ETL Service: Run Pipeline]
    J --> K[Update Job Status: Running]
    K --> L[Process Games]
    L --> M[Update Job Status: Processing]
    M --> N[Create Tables]
    N --> O[Update Job Status: Uploading]
    O --> P[Upload to Supabase]
    P --> Q[Update Job Status: Complete]
    
    I --> R[Portal: Poll Status]
    R --> S[GET /api/etl/status/{job_id}]
    S --> T[Return Current Status]
    T --> R
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#aa66ff
    style F fill:#aa66ff
    style G fill:#ff8800
    style J fill:#aa66ff
    style Q fill:#00ff88
    style R fill:#00d4ff
```

### Upload Request Flow

```mermaid
graph TD
    A[Portal: Upload File] --> B[POST /api/upload/tables<br/>Multipart Form Data]
    
    B --> C[API: Validate File]
    C --> D{Valid?}
    D -->|No| E[Return 400 Error]
    D -->|Yes| F[Upload Service: Process File]
    
    F --> G[Parse CSV]
    G --> H[Validate Schema]
    H --> I{Valid Schema?}
    I -->|No| J[Return 422 Error]
    I -->|Yes| K[Upload to Supabase]
    
    K --> L[Return Success]
    L --> M[Portal: Show Success Message]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#aa66ff
    style F fill:#ff8800
    style K fill:#00ff88
    style L fill:#00ff88
```

---

## Service Architecture

### Service Layer Structure

```mermaid
graph TD
    A[API Routes<br/>routes/] --> B[ETL Service<br/>services/etl_service.py]
    A --> C[Upload Service<br/>services/upload_service.py]
    A --> D[Staging Service<br/>services/staging_service.py]
    A --> E[ML Service<br/>services/ml_service.py]
    A --> F[Job Manager<br/>services/job_manager.py]
    
    B --> G[ETL Pipeline<br/>run_etl.py]
    B --> H[Table Store<br/>src/core/table_store.py]
    
    C --> I[Supabase Client<br/>Upload Tables]
    C --> J[File Parser<br/>CSV Processing]
    
    D --> K[Staging Tables<br/>Supabase]
    D --> L[Data Validation]
    
    E --> M[ML Models<br/>Future]
    E --> N[Prediction Engine<br/>Future]
    
    F --> O[Job Status DB<br/>Supabase]
    F --> P[Background Tasks<br/>FastAPI BackgroundTasks]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#aa66ff
    style F fill:#aa66ff
    style G fill:#aa66ff
    style H fill:#aa66ff
    style I fill:#00ff88
    style O fill:#00ff88
```

### Background Task Processing

```mermaid
graph TD
    A[API Endpoint] --> B[Create Background Task]
    B --> C[FastAPI BackgroundTasks]
    C --> D[Task Queue]
    
    D --> E[Task 1: ETL Job]
    D --> F[Task 2: Upload Job]
    D --> G[Task 3: ML Job]
    
    E --> E1[ETL Service]
    E1 --> E2[Update Job Status]
    E2 --> E3[Run ETL]
    E3 --> E4[Upload Results]
    E4 --> E5[Complete Job]
    
    F --> F1[Upload Service]
    F1 --> F2[Process File]
    F2 --> F3[Upload to DB]
    F3 --> F4[Complete Job]
    
    G --> G1[ML Service]
    G1 --> G2[Load Model]
    G2 --> G3[Run Prediction]
    G3 --> G4[Return Results]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#aa66ff
    style D fill:#aa66ff
    style E1 fill:#ff8800
    style F1 fill:#ff8800
    style G1 fill:#aa66ff
```

---

## Error Handling Flow

### Error Response Flow

```mermaid
graph TD
    A[Request] --> B[API Endpoint]
    B --> C{Validation}
    C -->|Invalid| D[400 Bad Request]
    C -->|Valid| E[Service Call]
    
    E --> F{Service Success?}
    F -->|No| G{Error Type?}
    F -->|Yes| H[200 Success]
    
    G -->|Validation Error| I[422 Unprocessable Entity]
    G -->|Not Found| J[404 Not Found]
    G -->|Server Error| K[500 Internal Server Error]
    G -->|ETL Error| L[500 + Error Details]
    
    D --> M[Error Response<br/>message, details]
    I --> M
    J --> M
    K --> M
    L --> M
    
    M --> N[Client Receives Error]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#aa66ff
    style D fill:#ff4444
    style E fill:#ff8800
    style F fill:#aa66ff
    style H fill:#00ff88
    style M fill:#ff4444
```

---

## Authentication Flow (Future)

### JWT Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Auth as Supabase Auth
    participant DB as Supabase
    
    Client->>API: POST /api/auth/login<br/>email, password
    API->>Auth: Authenticate user
    Auth->>DB: Verify credentials
    DB-->>Auth: User data
    Auth-->>API: JWT token
    API-->>Client: Return token
    
    Client->>API: GET /api/etl/status<br/>Authorization: Bearer token
    API->>API: Verify JWT token
    API->>API: Extract tenant_id
    API->>DB: Query with tenant_id filter
    DB-->>API: Filtered data
    API-->>Client: Return data
```

---

## Related Documentation

- [API.md](API.md) - Complete API documentation
- [ETL.md](../etl/ETL.md) - ETL process documentation
- [PORTAL.md](../portal/PORTAL.md) - Portal documentation

---

*Last Updated: 2026-01-15*
