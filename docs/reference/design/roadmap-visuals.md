# BenchSight Roadmap Visuals

**Standalone visual reference for roadmap diagrams**

Last Updated: 2026-01-21

---

## Timeline Gantt Chart

```mermaid
gantt
    title BenchSight Development Roadmap
    dateFormat YYYY-MM-DD
    section Phase 1: Foundation (COMPLETE)
    ETL Pipeline           :done, p1-etl, 2025-09-01, 4w
    Dashboard Core         :done, p1-dash, 2025-09-01, 4w
    Tracker HTML           :done, p1-track, 2025-09-01, 4w
    API Foundation         :done, p1-api, 2025-09-01, 4w
    Documentation          :done, p1-docs, 2025-12-15, 4w

    section Phase 2: ETL Optimization (CURRENT)
    ETL Cleanup            :active, p2-etl, 2026-01-15, 4w
    Table Verification     :active, p2-verify, 2026-01-21, 2w
    Performance Tuning     :p2-perf, 2026-02-01, 2w

    section Phase 3: Dashboard Enhancement
    Dashboard Polish       :p3-dash, 2026-02-15, 4w
    Advanced Analytics UI  :p3-analytics, 2026-03-01, 4w

    section Phase 4: Portal Development
    Portal Integration     :p4-portal, 2026-03-15, 4w
    Game Management        :p4-games, 2026-04-01, 2w

    section Phase 5: Tracker Conversion
    Rust Backend           :p5-rust, 2026-04-15, 4w
    Next.js Frontend       :p5-nextjs, 2026-05-01, 4w

    section Phase 6: ML/CV
    Video Processing       :p6-video, 2026-06-01, 4w
    Advanced Analytics     :p6-ml, 2026-06-15, 4w

    section Phase 7-8: Commercial
    Multi-Tenant           :p7-multi, 2026-07-15, 4w
    Payments & Launch      :p8-launch, 2026-08-15, 4w
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
    MVP Features           :done, mvp, 2025-09-01, 16w
    ETL Optimization       :active, etl, 2026-01-15, 4w
    Dashboard Enhancement  :dash, 2026-02-15, 4w
    Portal Development     :portal, 2026-03-15, 4w

    section Tracker Conversion
    Rust Backend           :rust, 2026-04-15, 4w
    Next.js Frontend       :nextjs, 2026-05-01, 4w

    section ML/CV & Multi-Tenant
    ML/CV Integration      :ml, 2026-06-01, 8w
    Multi-Tenant           :multi, 2026-07-15, 4w

    section Commercial Prep
    Payment Integration    :pay, 2026-08-15, 4w
    Onboarding Flows       :onboard, 2026-09-01, 4w
    Marketing Site         :marketing, 2026-09-15, 4w

    section Launch
    Public Launch          :launch, 2026-10-15, 2w
    Customer Acquisition   :acq, 2026-10-15, 12w
```

---

*Last Updated: 2026-01-21*
