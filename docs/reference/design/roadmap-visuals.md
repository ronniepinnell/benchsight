# BenchSight Roadmap Visuals

**Standalone visual reference for roadmap diagrams**

Last Updated: 2026-01-15

---

## Timeline Gantt Chart

```mermaid
gantt
    title BenchSight Development Roadmap
    dateFormat YYYY-MM-DD
    section Phase 1: Foundation
    ETL Pipeline           :done, p1-etl, 2025-09-01, 4w
    Dashboard Core         :done, p1-dash, 2025-09-01, 4w
    Tracker HTML           :done, p1-track, 2025-09-01, 4w
    API Foundation         :done, p1-api, 2025-09-01, 4w
    
    section Phase 2: Pre-Deployment
    Documentation          :done, p2-docs, 2025-10-01, 2w
    ETL Cleanup            :active, p2-etl, 2025-10-15, 3w
    Portal Integration     :active, p2-portal, 2025-10-15, 4w
    Dashboard Polish       :p2-dash, 2025-11-01, 3w
    
    section Phase 3: Advanced Analytics
    Advanced Stats         :p3-stats, 2025-11-15, 4w
    ML Feature Engineering :p3-ml, 2025-11-15, 4w
    Real-time Updates      :p3-realtime, 2025-12-01, 3w
    
    section Phase 4: Production
    Multi-Tenant           :p4-multi, 2025-12-15, 4w
    Production Deploy      :p4-deploy, 2026-01-15, 2w
    Tracker Conversion     :p4-track, 2026-01-15, 8w
```

---

## Component Dependency Graph

```mermaid
graph TD
    BLB[BLB Tables] --> ETL[ETL Pipeline]
    TRK[Tracking Files] --> ETL
    ETL --> DB[(Supabase Database)]
    DB --> API[FastAPI]
    DB --> DASH[Dashboard]
    API --> PORTAL[Admin Portal]
    TRK --> TRACKER[Tracker]
    TRACKER --> ETL
    
    ETL -.->|139 tables| DB
    API -.->|ETL Control| ETL
    PORTAL -.->|User Actions| API
    DASH -.->|Data Display| DB
    
    style ETL fill:#00d4ff
    style DB fill:#00ff88
    style API fill:#ff8800
    style DASH fill:#aa66ff
    style PORTAL fill:#ff4444
    style TRACKER fill:#00d4ff
```

---

## Feature Roadmap

```mermaid
graph LR
    subgraph MVP["MVP Features (Weeks 1-16)"]
        MVP1[Core Analytics]
        MVP2[Game Tracking]
        MVP3[Multi-Tenant]
        MVP4[Authentication]
        MVP5[Payment]
    end
    
    subgraph Commercial["Commercial Features (Weeks 17-32)"]
        COM1[Mobile Optimization]
        COM2[Advanced Analytics]
        COM3[Export/Reports]
        COM4[Onboarding]
        COM5[Support System]
    end
    
    subgraph Future["Future Features (Weeks 33+)"]
        FUT1[ML/CV Integration]
        FUT2[Mobile Apps]
        FUT3[Real-time Collab]
        FUT4[Predictive Analytics]
        FUT5[Multi-League]
    end
    
    MVP --> Commercial
    Commercial --> Future
    
    style MVP fill:#00ff88
    style Commercial fill:#00d4ff
    style Future fill:#aa66ff
```

---

## Critical Path Visualization

```mermaid
graph TD
    A[Documentation Consolidation<br/>Week 1-2] --> B[ETL Cleanup<br/>Week 2-3]
    B --> C[Portal API Integration<br/>Week 3-4]
    C --> D[Dashboard Polish<br/>Week 4-5]
    D --> E[Tracker Conversion Planning<br/>Week 5-6]
    E --> F[Advanced Analytics<br/>Week 7-12]
    F --> G[ML/CV Integration<br/>Week 9-16]
    
    H[Multi-Tenant Design<br/>Week 13-14] --> I[Production Deploy<br/>Week 15-16]
    I --> J[Commercial Launch<br/>Week 17+]
    
    style A fill:#00ff88
    style B fill:#00d4ff
    style C fill:#ff8800
    style D fill:#aa66ff
    style E fill:#00d4ff
    style F fill:#00ff88
    style G fill:#ff4444
    style H fill:#00d4ff
    style I fill:#00ff88
    style J fill:#aa66ff
```

---

## Commercial Roadmap Timeline

```mermaid
gantt
    title Commercial Roadmap
    dateFormat YYYY-MM-DD
    section MVP Development
    MVP Features           :mvp, 2025-09-01, 16w
    Multi-Tenant           :multi, 2025-12-15, 4w
    Beta Testing           :beta, 2026-01-01, 4w
    
    section Commercial Prep
    Payment Integration    :pay, 2026-01-15, 4w
    Onboarding Flows       :onboard, 2026-02-01, 4w
    Marketing Site         :marketing, 2026-02-15, 4w
    
    section Launch
    Public Launch          :launch, 2026-03-15, 2w
    Customer Acquisition   :acq, 2026-03-15, 12w
    Feature Expansion      :features, 2026-04-01, 12w
```

---

*Last Updated: 2026-01-15*
