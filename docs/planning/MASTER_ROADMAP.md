# BenchSight Master Roadmap

**Unified roadmap for all components: ETL, Dashboard, Tracker, Portal, and ML/CV**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document consolidates all roadmaps into a single, unified view. It covers ETL, Dashboard, Tracker, Portal, and future ML/CV integration.

**Timeline:** 16-week strategic roadmap (MVP) → 48-week commercial roadmap  
**Current Phase:** Pre-Deployment & Data Collection  
**Next Phase:** Advanced Analytics & ML Integration  
**Commercial Goal:** SaaS platform for high-level youth, junior, and college hockey (rec league is the prototype/pilot)

---

## Project Vision

### End Goal

**Commercial SaaS Platform** for hockey analytics and game tracking, targeting:

- **Primary Market:** High-level youth hockey teams and leagues
- **Secondary Market:** Junior hockey programs
- **Tertiary Market:** College club hockey teams
- **Prototype/Pilot:** Personal rec league (initial data source and validation cohort)
- **Value Proposition:** Affordable, comprehensive alternative to expensive professional platforms (Sportlogiq, InStat, Synergy Sports)

### MVP Definition

**MVP = Better Working Version of Current Prototype**

The MVP is a polished, production-ready version of the current functional prototype, including:

- [YES] All current ETL functionality (139 tables, advanced metrics)
- [YES] All current Dashboard functionality (50+ pages, analytics)
- [YES] All current Tracker functionality (event/shift tracking, video sync)
- [YES] Portal with full API integration
- [YES] Multi-tenant architecture (single-tenant → multi-tenant)
- [YES] User authentication and authorization
- [YES] Production deployment and monitoring
- [YES] Performance optimization and scalability

**MVP Success Criteria:**
- Can support 10+ teams simultaneously
- Can process 100+ games per season
- Dashboard loads in < 2 seconds
- ETL completes in < 90 seconds for 4 games
- 99.9% uptime
- User-friendly onboarding

### Market Context

**Target Customer Segments:**

1. **Teams & Coaches:**
   - Need game tracking and analytics
   - Want affordable alternative to pro platforms
   - Value ease of use and comprehensive stats

2. **Players:**
   - Want to see their performance data
   - Track progress over time
   - Compare to teammates/league

3. **League Administrators:**
   - Need league-wide analytics
   - Standings and leaderboards
   - Player/team management

**Pilot Cohort (Prototype):**
- Personal rec league to validate workflows, tracking, and pricing sensitivity before junior/college rollout

**Competitive Positioning:**
- **Lower price point** than professional platforms
- **Easier to use** than complex analytics tools
- **More comprehensive** than basic stat trackers
- **Better value** for youth/junior/college market

**Pricing Strategy Overview:**
- Free tier (limited features)
- Team tier ($X/month per team)
- Pro tier ($Y/month per team, advanced features)
- Enterprise tier (custom pricing, multi-league)

*Detailed pricing in [MONETIZATION_STRATEGY.md](commercial/MONETIZATION_STRATEGY.md)*

**Related Documentation:**
- [MASTER_IMPLEMENTATION_PLAN.md](MASTER_IMPLEMENTATION_PLAN.md) - Detailed phased implementation plan
- [TECH_STACK_ROADMAP.md](TECH_STACK_ROADMAP.md) - Tech stack requirements and migration paths
- [commercial/COMPETITOR_ANALYSIS.md](commercial/COMPETITOR_ANALYSIS.md) - Competitor research
- [commercial/GAP_ANALYSIS.md](commercial/GAP_ANALYSIS.md) - Gap analysis
- [commercial/MONETIZATION_STRATEGY.md](commercial/MONETIZATION_STRATEGY.md) - Monetization strategy
- [commercial/COMMERCIAL_ROADMAP_VISUALS.md](commercial/COMMERCIAL_ROADMAP_VISUALS.md) - Commercial roadmap visuals

### Commercial Roadmap

**MVP to Commercial Timeline:**

**Phase 1-4 (Weeks 1-16): MVP Development**
- Complete all MVP features
- Multi-tenant architecture
- Production deployment
- Beta testing with 3-5 teams

**Phase 5-6 (Weeks 17-32): Commercial Preparation**
- Payment integration
- Subscription management
- Onboarding flows
- Marketing site
- Customer support system

**Phase 7-8 (Weeks 33-48): Commercial Launch**
- Public launch
- Customer acquisition
- Feature expansion based on feedback
- Multi-league support

**Feature Prioritization for Market Readiness:**

**Must-Have for MVP:**
- Core analytics (current functionality)
- Game tracking (current tracker)
- Multi-tenant support
- User authentication
- Payment processing

**Should-Have for Launch:**
- Mobile optimization
- Advanced analytics (xG, WAR/GAR)
- Export functionality
- Custom reports

**Nice-to-Have for Future:**
- ML/CV integration
- Mobile apps
- Real-time collaboration
- Advanced predictive analytics

**Multi-Tenant Architecture Requirements:**
- Schema redesign for tenant isolation
- Row-level security (RLS)
- Data isolation per tenant
- Performance at scale (100+ teams)
- Billing and subscription management

**Scalability Considerations:**
- Horizontal scaling (read replicas)
- Caching strategies (Redis)
- CDN for static assets
- Database optimization (indexing, partitioning)
- API rate limiting

---

## Current State Summary

### ETL Pipeline
- **Status:** [YES] Functional (139 tables)
- **Completion:** ~90%
- **Remaining:** Cleanup, refactoring, optimization

### Dashboard
- **Status:** [YES] Functional (50+ pages)
- **Completion:** ~85%
- **Remaining:** Polish, enhanced visualizations, mobile optimization

### Tracker
- **Status:** [YES] Functional (HTML/JS)
- **Completion:** 100% (current version)
- **Remaining:** Rust/Next.js conversion (planned)

### Portal
- **Status:** [IN_PROGRESS] UI mockup only
- **Completion:** ~10%
- **Remaining:** API integration, full functionality

### API
- **Status:** [YES] Functional
- **Completion:** ~80%
- **Remaining:** Game management endpoints, data browser endpoints

---

## Unified Roadmap

### Phase 1: Foundation (COMPLETE [YES])

**Timeline:** Weeks 1-4  
**Status:** [YES] Complete

**ETL:**
- [YES] Core ETL pipeline (139 tables)
- [YES] Data validation
- [YES] Supabase integration

**Dashboard:**
- [YES] Core pages (players, teams, games, goalies)
- [YES] Basic analytics
- [YES] Data visualization

**Tracker:**
- [YES] HTML tracker functional
- [YES] Event/shift tracking
- [YES] Video integration
- [YES] Export functionality

**API:**
- [YES] ETL endpoints
- [YES] Upload endpoints
- [YES] Staging endpoints

---

### Phase 2: Pre-Deployment & Data Collection (CURRENT [IN_PROGRESS])

**Timeline:** Weeks 5-8
**Status:** [IN_PROGRESS] In Progress

**ETL:**
- [IN_PROGRESS] Code cleanup and refactoring
- [IN_PROGRESS] Table verification
- [IN_PROGRESS] Performance optimization
- [YES] Documentation consolidation (Review folder cleaned, reference materials organized)

**Schema Optimization (NEW):**
- [PLANNED] Remove 20 empty/duplicate tables (see [COMMERCIAL_SCHEMA_DESIGN.md](data/COMMERCIAL_SCHEMA_DESIGN.md))
- [PLANNED] Remove 8 null columns from fact_events
- [PLANNED] Archive 7 development-only tables
- [PLANNED] Document schema changes in CHANGELOG

**Dashboard:**
- [IN_PROGRESS] Enhanced visualizations
- [IN_PROGRESS] Search and filter integration
- [IN_PROGRESS] Export functionality expansion
- [PLANNED] Mobile optimization

**Portal:**
- [IN_PROGRESS] API integration
- [IN_PROGRESS] ETL control functionality
- [IN_PROGRESS] Data display
- [PLANNED] Game management

**API:**
- [IN_PROGRESS] Game management endpoints
- [IN_PROGRESS] Data browser endpoints
- [PLANNED] Authentication

---

### Phase 3: Advanced Analytics (PLANNED [PLANNED])

**Timeline:** Weeks 9-12
**Status:** [PLANNED] Planned

**Schema Consolidation:**
- [PLANNED] Consolidate 6 H2H/matchup tables → 2 tables
- [PLANNED] Consolidate 6 zone entry/exit tables → 2 tables
- [PLANNED] Consolidate 6 shot/scoring tables → 2 tables
- [PLANNED] Update ETL builders for consolidated tables
- [PLANNED] Update dashboard queries

**Schema Normalization:**
- [PLANNED] Normalize fact_events (200 → 25 columns)
- [PLANNED] Create fact_event_participants junction table
- [PLANNED] Create backward-compatible views
- [PLANNED] Update all queries to use normalized schema
- [PLANNED] Performance testing and optimization

**ETL:**
- [PLANNED] Spatial xG (GBM with distance/angle/royal-road/rush/rebound/flurry/shooter-talent)
- [PLANNED] RAPM/WAR rebuild (stints, RidgeCV, replacement level, daisy-chain priors)
- [PLANNED] Microstats: WDBE faceoffs, gap control, entry/exit value, xT grid spec
- [PLANNED] ML feature engineering
- [PLANNED] Real-time data processing

**Dashboard:**
- [PLANNED] xG layers (shot maps, flurry view, shooter talent)
- [PLANNED] WAR/RAPM components and leaderboards
- [PLANNED] Microstat surfaces (WDBE, gap, entry/exit value, rush vs cycle)
- [PLANNED] Predictive analytics

**Portal:**
- [PLANNED] Advanced data management
- [PLANNED] Batch operations
- [PLANNED] Data quality monitoring

**ML/CV:**
- [PLANNED] Goal detection
- [PLANNED] Player tracking
- [PLANNED] Event classification

---

### Phase 4: Production & Scale (PLANNED [PLANNED])

**Timeline:** Weeks 13-16
**Status:** [PLANNED] Planned

**Multi-Tenant Schema:**
- [PLANNED] Add tenant_id to all tables (see [SCHEMA_SCALABILITY_DESIGN.md](data/SCHEMA_SCALABILITY_DESIGN.md))
- [PLANNED] Implement Row-Level Security (RLS)
- [PLANNED] Update foreign keys to include tenant_id
- [PLANNED] Create composite indexes for tenant queries
- [PLANNED] Test tenant isolation

**All Components:**
- [PLANNED] Production deployment
- [PLANNED] Performance optimization
- [PLANNED] Scalability improvements
- [PLANNED] Monitoring and alerting

**Tracker:**
- [PLANNED] Rust/Next.js conversion
- [PLANNED] Real-time collaboration
- [PLANNED] Mobile app

---

## Component-Specific Roadmaps

### ETL Roadmap

**Current State:** [YES] Functional, needs cleanup

**Immediate (Weeks 1-2):**
- [ ] Code cleanup and refactoring
- [ ] Table verification
- [ ] Performance optimization
- [ ] Documentation consolidation
- [ ] **Schema Cleanup:** Remove 20 empty/duplicate tables
- [ ] **Schema Cleanup:** Remove 8 null columns from fact tables
- [ ] **Schema Cleanup:** Archive 7 development-only tables

**Short-term (Weeks 3-4):**
- [ ] Module refactoring (split base_etl.py)
- [ ] Vectorization improvements
- [ ] Parallel processing
- [ ] Enhanced validation
- [ ] **Schema Consolidation:** Merge H2H tables (6 → 2)
- [ ] **Schema Consolidation:** Merge zone tables (6 → 2)
- [ ] **Schema Consolidation:** Merge shot tables (6 → 2)

**Medium-term (Weeks 5-8):**
- [ ] **Schema Normalization:** Normalize fact_events (200 → 25 cols)
- [ ] **Schema Normalization:** Create fact_event_participants
- [ ] **Schema Normalization:** Create backward-compatible views
- [ ] Advanced stat calculations (GBM xG, flurry, shooter talent)
- [ ] ML feature engineering
- [ ] Real-time processing support

**Long-term (Weeks 9-16):**
- [ ] **Multi-Tenant:** Add tenant_id to all tables
- [ ] **Multi-Tenant:** Implement Row-Level Security
- [ ] RAPM/WAR rebuild with replacement level
- [ ] xT / possession value, WDBE, gap control
- [ ] ML / computer vision integration
- [ ] Automated data quality

---

### Dashboard Roadmap

**Current State:** [YES] Functional, needs polish

**Immediate (Weeks 1-2):**
- [ ] Enhanced visualizations
- [ ] Search and filter integration
- [ ] Export expansion
- [ ] Mobile optimization

**Short-term (Weeks 3-4):**
- [ ] Complete xG analysis page
- [ ] Complete WAR/GAR analysis page
- [ ] Enhanced player comparison
- [ ] UI polish

**Medium-term (Weeks 5-8):**
- [ ] RAPM analysis
- [ ] Predictive analytics
- [ ] Real-time updates
- [ ] User preferences

**Long-term (Weeks 9-16):**
- [ ] AI-powered insights
- [ ] Custom report builder
- [ ] Advanced visualizations

---

### Tracker Roadmap

**Current State:** [YES] Functional (HTML/JS)

**Immediate (Weeks 1-2):**
- [ ] Complete logic documentation [YES]
- [ ] Conversion planning [YES]

**Short-term (Weeks 3-6):**
- [ ] Rust backend development
- [ ] Next.js frontend development
- [ ] Feature parity testing

**Medium-term (Weeks 7-10):**
- [ ] Performance optimization
- [ ] Real-time collaboration
- [ ] Mobile support

**Long-term (Weeks 11-16):**
- [ ] Mobile app
- [ ] Advanced features
- [ ] ML integration

---

### Portal Roadmap

**Current State:** [IN_PROGRESS] UI mockup only

**Immediate (Weeks 1-2):**
- [ ] API integration
- [ ] ETL trigger functionality
- [ ] Status polling

**Short-term (Weeks 3-4):**
- [ ] Upload functionality
- [ ] Game list display
- [ ] Data browser

**Medium-term (Weeks 5-8):**
- [ ] Game management
- [ ] Staging data upload
- [ ] Settings management

**Long-term (Weeks 9-16):**
- [ ] Advanced features
- [ ] User management
- [ ] Role-based access

---

### API Roadmap

**Current State:** [YES] Functional, needs expansion

**Immediate (Weeks 1-2):**
- [ ] Game management endpoints
- [ ] Data browser endpoints
- [ ] Error handling improvements

**Short-term (Weeks 3-4):**
- [ ] Authentication
- [ ] Rate limiting
- [ ] API documentation

**Medium-term (Weeks 5-8):**
- [ ] WebSocket support
- [ ] Real-time updates
- [ ] Job queue (Redis)

**Long-term (Weeks 9-16):**
- [ ] ML endpoints
- [ ] Advanced features
- [ ] Performance optimization

---

## ML/CV Roadmap (Future)

**Timeline:** Weeks 9-16+  
**Status:** [PLANNED] Planned

**Phase 1: Goal Detection**
- [PLANNED] Computer vision model
- [PLANNED] Goal detection API
- [PLANNED] Integration with tracker

**Phase 2: Player Tracking**
- [PLANNED] Player identification
- [PLANNED] Position tracking
- [PLANNED] Movement analysis

**Phase 3: Event Classification**
- [PLANNED] Automatic event detection
- [PLANNED] Event type classification
- [PLANNED] Quality scoring

---

## AI Coaching & Analysis Roadmap (Commercial Features)

**Timeline:** Weeks 33-48+  
**Status:** [PLANNED] Planned  
**Priority:** High (differentiator for commercial launch)

**Overview:** Transform BenchSight into an intelligent coaching assistant with AI-powered video analysis, natural language queries, and specialized coaching modes.

**Related PRD:** [AI_COACHING_FEATURES.md](prds/AI_COACHING_FEATURES.md)

### Phase 9: AI Coach Foundation (Weeks 33-36)

**Goal:** Basic AI coach functionality with video review

**Features:**
- Video upload and storage infrastructure
- Video player component with AI annotations
- Basic Q&A system (LLM integration)
- Video-event synchronization
- Simple text-based queries

**Dependencies:**
- Multi-tenant architecture (Phase 7)
- Video upload infrastructure
- ML/CV models (Phase 6)

### Phase 10: Natural Language Queries (Weeks 37-40)

**Goal:** Full natural language query system

**Features:**
- Natural language understanding system
- SQL query generation from natural language
- Response visualization engine
- Query caching and optimization
- Voice input (future enhancement)

**Dependencies:**
- Phase 9 completion
- LLM integration (OpenAI/Anthropic)

### Phase 11: Coach Modes (Weeks 41-44)

**Goal:** Complete coach mode features

**Features:**
- **Game Plan Generator:** AI-powered game plan creation based on opponent analysis
- **Practice Planner:** AI-suggested practice drills based on game performance
- **Scout Mode:** Player comparison, talent identification, scouting reports
- **Game Prep Mode:** Pre-game analysis and preparation tools

**Dependencies:**
- Phase 10 completion
- Advanced analytics models
- Recommendation engine

### Phase 12: GM Mode & Advanced Features (Weeks 45-48)

**Goal:** GM mode and advanced analytics

**Features:**
- **Team Builder:** AI-powered roster optimization and player acquisition
- **Advanced Analytics Dashboard:** GM-focused analytics with AI insights
- **Trade Evaluation:** AI-powered trade analysis
- **Draft Analysis:** Prospect evaluation and draft strategy
- **Moneyball Draft Board:** Rating-cap-aware optimizer with keepers, opponent-pick sims, and human/vibes overlays

**Moneyball Draft Board - Data Inputs (prep before Phase 12)**
- Draft history: last season draft order and picks (`team_id`, `pick_number`, `player_id`, `rating`, `position`).
- Keepers: per-team kept players (`team_id`, `player_id`, `rating`, `position`, `captain_flag`), consumed rating slots.
- Player pool: unified value outputs (rich/sparse/new routes) with offense/defense splits and confidence, human/vibes notes (optional tags).
- Team rules: rating cap template, role needs (PP/PK/transition/faceoff/defense), attendance/reliability flags if available.
- Opponent tendencies: optional heuristics from last-year picks (offense/defense bias, positional runs).

**Dependencies:**
- Phase 11 completion
- Player valuation models
- Roster optimization algorithms

---

## Roadmap Visualizations

### Timeline Gantt Chart

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

    section Phase 9-12: AI Coaching
    AI Coach Foundation    :p9-ai, 2026-09-01, 4w
    Natural Language Query :p10-nl, 2026-10-01, 4w
    Coach Modes            :p11-coach, 2026-11-01, 4w
    GM Mode & Advanced     :p12-gm, 2026-12-01, 4w

    section NHL Data & Training (Parallel)
    Multi-League Schema    :nhl-schema, 2026-02-15, 4w
    NHL Data Loaders       :nhl-load, 2026-03-01, 4w
    Benchmarking Views     :nhl-bench, 2026-03-15, 4w
    xG Model Training      :nhl-xg, 2026-06-01, 6w
    Training Schema Merge  :train-schema, 2026-07-15, 4w
    Athlete Portal MVP     :train-portal, 2026-08-01, 6w
    CV Coach Migration     :cv-migrate, 2026-09-01, 4w
    Performance Correlation:train-corr, 2026-10-01, 4w
    NHL Exploration Dash   :nhl-explore, 2026-10-15, 6w
```

### Component Dependency Graph

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

### Feature Roadmap

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

    subgraph Expansion["NHL Data & Training (Parallel)"]
        EXP1[Multi-League Schema]
        EXP2[NHL Benchmarking]
        EXP3[xG Model Training]
        EXP4[Athlete Portal]
        EXP5[CV Coach Enhancement]
        EXP6[NHL Explorer]
    end

    MVP --> Commercial
    Commercial --> Future
    MVP --> Expansion
    Expansion --> Future

    style MVP fill:#00ff88
    style Commercial fill:#00d4ff
    style Future fill:#aa66ff
    style Expansion fill:#ff8800
```

## Dependencies

### Critical Path

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

### Parallel Work

- **Dashboard polish** can happen in parallel with **ETL cleanup**
- **Portal development** can happen in parallel with **Tracker conversion planning**
- **API expansion** can happen in parallel with all other work
- **Multi-tenant design** can start in parallel with **Advanced Analytics**

---

## Success Metrics

### Phase 2 (Current)

**Technical:**
- [ ] All documentation consolidated
- [ ] ETL code cleaned and refactored
- [ ] Portal fully functional
- [ ] Dashboard polished
- [ ] Tracker conversion plan complete

**Commercial:**
- [ ] MVP feature list finalized
- [ ] Multi-tenant architecture designed
- [ ] Pricing strategy defined

### Phase 3

**Technical:**
- [ ] Advanced analytics complete
- [ ] ML features integrated
- [ ] Real-time updates working
- [ ] Performance optimized

**Commercial:**
- [ ] Beta program launched (3-5 teams)
- [ ] User feedback collected
- [ ] Feature prioritization updated

### Phase 4

**Technical:**
- [ ] Production deployment
- [ ] Scalability proven
- [ ] Monitoring in place
- [ ] User feedback positive

**Commercial:**
- [ ] MVP launched
- [ ] 10+ teams onboarded
- [ ] Payment processing working
- [ ] Customer support operational

### Commercial Metrics (Post-MVP)

**User Acquisition:**
- Target: 50 teams in first 6 months
- Target: 200 teams in first year
- Customer acquisition cost (CAC) < $X
- Conversion rate (free → paid) > Y%

**Retention:**
- Monthly churn rate < 5%
- Annual retention rate > 80%
- Net Promoter Score (NPS) > 50

**Revenue:**
- Monthly Recurring Revenue (MRR) growth > 20% month-over-month
- Average Revenue Per User (ARPU) > $X
- Lifetime Value (LTV) > 3x CAC

**Product:**
- Feature adoption rate > 60%
- Daily Active Users (DAU) / Monthly Active Users (MAU) > 30%
- User satisfaction score > 4.0/5.0

---

## GitHub Issues Mapping (30 Open Issues)

### Phase 2: Current ETL Work (18 Issues)

**P0 - Critical (4 issues):**
| # | Title | Type |
|---|-------|------|
| #3 | ✅ ETL-001: Modularize base_etl.py | COMPLETED |
| #5 | ETL-003: Replace .iterrows() with vectorized | Perf |
| #13 | ETL-011: Verify goal counting matches official | Test |
| #31 | Investigate missing 7 tables (132 vs 139) | Bug |

**P1 - High Priority (9 issues):**
| # | Title | Type |
|---|-------|------|
| #4 | ETL-002: Profile ETL and identify bottlenecks | Chore |
| #6 | ETL-004: Create table verification script | Test |
| #7 | ETL-005: Verify all 139 tables have data | Test |
| #8 | ETL-006: Validate foreign key relationships | Test |
| #25 | Vectorize goal-shift matching in shift_enhancers | Perf |
| #26 | Vectorize player/roster loops in shift_enhancers | Perf |
| #27 | Vectorize pressure calculation in derived_columns | Perf |
| #28 | Vectorize zone inference in event_enhancers | Perf |
| #29 | Vectorize cycle detection in event_enhancers | Perf |

**P2 - Medium Priority (5 issues):**
| # | Title | Type |
|---|-------|------|
| #9 | ETL-007: Identify and document unused tables | Docs |
| #16 | Remove all dead code from / and /src | Cleanup |
| #30 | Remove data_loader.py wrapper - CLAUDE.md violation | Cleanup |
| #32 | Add type hints to etl_phases module | Quality |
| #33 | Split long functions in event_enhancers.py | Refactor |
| #34 | Address pandas FutureWarnings | Quality |

### Phase 3: Advanced Analytics (12 Issues)

**P1 - Analytics Validation (3 issues):**
| # | Title | Type |
|---|-------|------|
| #10 | ETL-008: Validate xG calculations | Test |
| #11 | ETL-009: Validate WAR/GAR calculations | Test |
| #12 | ETL-010: Validate Corsi/Fenwick calculations | Test |

**P2 - CI/CD & Debug Infrastructure (8 issues):**
| # | Title | Type |
|---|-------|------|
| #14 | ETL-012: Add verification tests to CI | Chore |
| #17 | ETL Debug: Docker PostgreSQL Infrastructure | Enhancement |
| #18 | ETL Debug: PostgreSQL Manager Module | Enhancement |
| #19 | ETL Debug: State Manager Module | Enhancement |
| #20 | ETL Debug: Phase Executor Module | Enhancement |
| #21 | ETL Debug: Data Comparator Module | Enhancement |
| #22 | ETL Debug: Integrate Debug Mode into run_etl.py | Enhancement |
| #23 | ETL Debug: Add Debug Commands to benchsight.sh | Enhancement |

### Issue Priority Summary

| Priority | Count | Phase |
|----------|-------|-------|
| P0 (Critical) | 4 | Phase 2 |
| P1 (High) | 12 | Phase 2-3 |
| P2 (Medium) | 14 | Phase 2-3 |
| **Total** | **30** | |

---

## NHL Data & Training Integration Roadmap (Parallel Track)

**Status:** [PLANNED] Planned
**Priority:** Medium-High (strategic expansion)
**Timeline:** Runs parallel to Phases 3-12

**Overview:** Expand BenchSight from a NORAD-focused platform into a comprehensive hockey intelligence hub with NHL benchmarking, ML models trained on pro data, and personal training integration.

**Data Sources Available (9.9 GB):**
| Source | Records | Location |
|--------|---------|----------|
| MoneyPuck Shots | 1.9M (2007-2023) | `data/hockey_data/NHL_Project/MoneyPuckData/Shots/` |
| MoneyPuck Skaters | 17 seasons | `data/hockey_data/NHL_Project/MoneyPuckData/Skaters/` |
| MoneyPuck Lines | 17 seasons | `data/hockey_data/NHL_Project/MoneyPuckData/Lines/` |
| NHL Event Data | 8M+ events | `data/hockey_data/HockeyDataReference/Hockey_Statistics/NHL/` |
| NHL Shifts | 5.7M shifts | `data/hockey_data/HockeyDataReference/Hockey_Statistics/NHL/` |
| PWHL | 2024-25 season | `data/hockey_data/HockeyDataReference/Hockey_Statistics/PWHL/` |
| Big Data Cup | 3 games + tracking | `data/hockey_data/HockeyDataReference/Hockey_Statistics/Big-Data-Cup-2025-Data/` |

**Training App Source:** `data/hockey_training/master/` (Vanilla JS PWA + Supabase + Python workers)

---

### Track A: Multi-League Data Foundation (Parallel to Phase 3)

**Goal:** Abstract BenchSight to support multiple leagues with consistent schemas.

**New Tables:**
```
dim_leagues              -- NORAD, NHL, PWHL, AHL, etc.
dim_nhl_players          -- NHL player master (3,200+ players)
dim_nhl_teams            -- 32 NHL teams + historical
dim_nhl_seasons          -- Season metadata (2007-2025)
fact_nhl_shots           -- 1.9M shot records with xG
fact_nhl_player_games    -- Per-player per-game stats
fact_nhl_shifts          -- Shift-level data
fact_nhl_lines           -- Line combination stats
```

**Schema Changes:**
- [ ] Add `league_id` to relevant dim/fact tables
- [ ] Create `dim_leagues` table
- [ ] Create NHL data loaders in `src/loaders/`
- [ ] Add `--source nhl|pwhl|bdc` flag to ETL
- [ ] Update dashboard queries to filter by league context

**ETL Approach:**
- Store raw CSVs in `data/external/` (gitignored)
- One-time bulk load + incremental updates for current season
- Separate ETL run modes: `./benchsight.sh etl run --source norad` vs `--source nhl`

---

### Track B: NHL Benchmarking (Parallel to Phase 3-4)

**Goal:** Compare NORAD players/teams against NHL percentiles.

**Features:**
- [ ] Percentile rankings (e.g., "Your Corsi% is 65th percentile of NHL forwards")
- [ ] Position-adjusted comparisons (F vs F, D vs D, G vs G)
- [ ] Stat radar charts overlaying player vs NHL median/elite
- [ ] "NHL Comparable" finder (which NHL player has similar profile?)
- [ ] Team benchmarking (shot quality, possession, special teams vs NHL)

**New Views:**
```sql
v_nhl_percentiles_skaters    -- Pre-computed percentiles by position
v_nhl_percentiles_goalies    -- Goalie-specific percentiles
v_player_nhl_comparison      -- Join NORAD player stats to NHL benchmarks
```

**Dashboard Pages:**
- [ ] `/players/[id]/benchmark` - NHL comparison for individual player
- [ ] `/teams/[id]/benchmark` - Team vs NHL baselines
- [ ] `/nhl/percentiles` - League-wide percentile explorer

---

### Track C: xG Model Training (Parallel to Phase 6 ML/CV)

**Goal:** Train expected goals model on NHL shots, apply to NORAD.

**Training Data:** MoneyPuck shots (1.9M records)
- Shot location (x, y coordinates)
- Shot type (wrist, slap, backhand, etc.)
- Game state (score, period, strength)
- Rush/rebound indicators
- Shooter angle and distance

**Model Approach:**
- [ ] Train gradient boosting model on NHL data
- [ ] Validate against MoneyPuck's published xG values
- [ ] Apply to NORAD shots with coordinate mapping
- [ ] Store model in `models/xg/` with versioning

**New Tables:**
```
ml_xg_models             -- Model metadata, version, accuracy
fact_shots.xg_predicted  -- Add xG column to existing shot facts
```

**Additional Models (Future):**
- [ ] Win Probability Model (score, time, strength, Corsi)
- [ ] Player Similarity Model (cosine similarity clustering)

---

### Track D: Athlete Portal & Training Integration (Parallel to Phase 7-8)

**Goal:** Merge hockey_training app into BenchSight with authenticated Athlete Portal.

**Tables to Port from hockey_training:**
```
-- Planning
plan_sessions           → fact_training_sessions
plan_settings           → dim_athlete_settings
events                  → dim_training_events

-- Logging
actual_sessions         → fact_training_actuals
actual_lift_sets        → fact_lift_sets
workout_notes           → fact_training_notes
journal_entries         → fact_journal_entries
food_logs               → fact_nutrition_logs

-- Recovery
recovery_daily          → fact_recovery_daily
body_comp_daily         → fact_body_comp

-- Hockey-specific
helios_player_sessions  → fact_helios_sessions
helios_player_shifts    → fact_helios_shifts
cv_jobs                 → fact_cv_jobs
cv_sessions             → fact_cv_sessions
```

**Athlete Portal Pages:**
- [ ] `/athlete/today` - Daily training plan + readiness
- [ ] `/athlete/week` - Weekly overview with hockey games highlighted
- [ ] `/athlete/dashboard` - Training load trends, recovery metrics
- [ ] `/athlete/cv-coach` - Shot/stickhandling video analysis
- [ ] `/athlete/nutrition` - Meal logging and macro tracking
- [ ] `/athlete/recovery` - Oura/Apple Health data visualization

**External Integrations (Port from hockey_training):**
| Service | Data | Status in hockey_training |
|---------|------|---------------------------|
| Strava | Runs, rides, activities | ✅ Implemented |
| Oura | Sleep, HRV, readiness | ✅ Implemented |
| Helios | Game tracking, shifts | ✅ Implemented |
| Apple Health | HR, sleep, workouts | ✅ Implemented |
| Strong | Lift sessions | ✅ Implemented |
| Withings | Body composition | 📋 Planned |

**Worker Architecture:**
- Port Python workers from `data/hockey_training/master/worker/` to `api/workers/`
- Run via GitHub Actions or migrate to Railway
- Store sync state in `ingest_state` table

**Auth Consideration:**
- Athlete portal requires Supabase Auth
- Personal data isolated via RLS (user_id = auth.uid())
- Public BenchSight dashboard remains open

---

### Track E: Performance Correlation Engine (Parallel to Phase 9-12)

**Goal:** Connect training load to game performance.

**Analyses:**
- [ ] Does readiness score predict points/game?
- [ ] Training volume vs. ice time correlation
- [ ] Recovery metrics vs. Corsi differential
- [ ] Pre-game nutrition impact on performance

**New Views:**
```sql
v_training_game_correlation  -- Join training metrics to game stats
v_readiness_performance      -- Readiness score vs game outcomes
```

**Dashboard Pages:**
- [ ] `/athlete/correlations` - Training-performance insights
- [ ] `/athlete/predictions` - AI-suggested training adjustments

---

### Track F: CV Coach Enhancement (Parallel to Phase 9-12)

**Goal:** Enhance video analysis using NHL tracking data patterns.

**Current State (from hockey_training):**
- ✅ ArUco marker-based net calibration
- ✅ Shot placement heatmaps
- ✅ Stickhandling cadence scoring
- 🚧 Basic form analysis (MediaPipe foundation)

**Enhancements Using NHL Tracking Data:**
- [ ] Learn optimal skating patterns from Big Data Cup tracking
- [ ] Compare user's movement patterns to professional benchmarks
- [ ] Enhance shot release point detection
- [ ] Stride length/cadence analysis against NHL baselines

**Advanced Form Analysis:**
- [ ] Skating stride analysis (crossovers, edges, transitions)
- [ ] Shot mechanics breakdown (weight transfer, follow-through)
- [ ] Comparison overlays with "ideal" form
- [ ] Progress tracking over time

---

### Track G: NHL Exploration Dashboard (Parallel to Phase 9-12)

**Goal:** Separate section for exploring professional hockey data.

**Dashboard Pages:**
- [ ] `/nhl/players` - Player search with advanced filters
- [ ] `/nhl/teams` - Team comparisons and rankings
- [ ] `/nhl/games` - Game analysis with shot maps
- [ ] `/nhl/trends` - League-wide trends over time
- [ ] `/nhl/xg-explorer` - Interactive xG visualization

**Research Tools:**
- [ ] Custom query builder for stat exploration
- [ ] Export capabilities for further analysis
- [ ] Saved queries and dashboards

---

### Implementation Priority (Suggested Order)

**Immediate (During Phase 3):**
1. Multi-league schema changes (`league_id`, `dim_leagues`)
2. MoneyPuck shots loader (cleanest data, highest value)
3. Basic percentile benchmarking view

**Short-term (During Phase 4-6):**
4. xG model training pipeline
5. Player benchmarking dashboard page
6. NHL player search/exploration

**Medium-term (During Phase 7-8):**
7. Migrate training schema to BenchSight
8. Athlete portal MVP (today, week views)
9. Strava/Oura worker integration

**Long-term (During Phase 9-12):**
10. CV Coach migration and enhancement
11. Win probability model
12. Performance correlation engine
13. Full NHL exploration dashboard

---

### Success Metrics

| Metric | Target |
|--------|--------|
| Benchmarking | Any NORAD player can see NHL percentile rankings |
| xG Model | Model achieves <0.05 MAE vs MoneyPuck baseline |
| Training Integration | Full workout logging through BenchSight dashboard |
| Correlation Insights | 3+ statistically significant training-performance correlations |
| CV Coach | Shot accuracy trends visible over 10+ sessions |

---

### Technical Considerations

**Storage:**
- External data stays in `data/external/` (gitignored)
- Document download/setup instructions in README
- Consider Supabase Storage for large files

**Performance:**
- NHL data is large - pre-aggregate common queries
- Create materialized views for percentiles
- Index on league_id, season, player_id

**Deployment:**
- Workers can run on Railway (FastAPI already there)
- Consider scheduled jobs for API syncs
- CV processing may need GPU (future)

---

## Related Documentation

- [dashboard/DASHBOARD_ROADMAP.md](dashboard/DASHBOARD_ROADMAP.md) - Dashboard-specific roadmap
- [tracker/TRACKER_CONVERSION.md](tracker/TRACKER_CONVERSION.md) - Tracker conversion plan
- [portal/PORTAL.md](portal/PORTAL.md) - Portal development plan
- [commercial/GAP_ANALYSIS.md](commercial/GAP_ANALYSIS.md) - Strategic assessment (gap analysis)
- [GITHUB_ISSUES_BACKLOG.md](GITHUB_ISSUES_BACKLOG.md) - Detailed issue descriptions
- [archive/COMPREHENSIVE_FUTURE_ROADMAP.md](archive/COMPREHENSIVE_FUTURE_ROADMAP.md) - Future roadmap (archived)
- **[NEW]** [NHL_TRAINING_EXPANSION.md](NHL_TRAINING_EXPANSION.md) - Detailed NHL data + training integration plan

---

*Last Updated: 2026-01-23*
