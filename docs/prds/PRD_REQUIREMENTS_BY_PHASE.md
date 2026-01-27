# PRD Requirements by Phase

**What PRDs are needed before each phase begins**

Last Updated: 2025-01-22

---

## Overview

PRDs (Product Requirements Documents) should be created BEFORE implementation begins. This document outlines what PRDs are needed for each phase of the BenchSight roadmap.

**PRD Location:** `docs/prds/`
**PRD Template:** `docs/templates/prd-template.md`

---

## Phase 2: ETL Optimization (CURRENT)

**Status:** In Progress - Some PRDs needed

### Required PRDs

| PRD | Status | Priority | Description |
|-----|--------|----------|-------------|
| `etl/ETL_VERIFICATION_FRAMEWORK.md` | NEEDED | P0 | Framework for verifying all 139 tables |
| `etl/ETL_VECTORIZATION.md` | NEEDED | P0 | Plan for replacing .iterrows() |
| `etl/ETL_DEBUG_INFRASTRUCTURE.md` | NEEDED | P1 | PostgreSQL debugging setup |
| `etl/ETL_PERFORMANCE_OPTIMIZATION.md` | NEEDED | P1 | Performance profiling and optimization |

### PRD Contents Needed

**ETL_VERIFICATION_FRAMEWORK.md:**
- Table verification approach
- Column validation rules
- Primary/foreign key verification
- Business rule validation
- CI integration plan

**ETL_VECTORIZATION.md:**
- Current .iterrows() locations
- Replacement strategy for each
- Performance benchmarks
- Testing approach

---

## Phase 3: Dashboard Enhancement

**Status:** Planned - PRDs needed before starting

### Required PRDs

| PRD | Status | Priority | Description |
|-----|--------|----------|-------------|
| `dashboard/ENHANCED_VISUALIZATIONS.md` | NEEDED | P1 | xG, WAR, microstat visualizations |
| `dashboard/MOBILE_OPTIMIZATION.md` | NEEDED | P1 | Responsive design implementation |
| `dashboard/SEARCH_FILTER.md` | NEEDED | P1 | Search and filter functionality |
| `dashboard/EXPORT_EXPANSION.md` | NEEDED | P2 | Export to CSV, PDF, image |
| `dashboard/PLAYER_COMPARISON.md` | EXISTS | P1 | Already created |

### PRD Contents Needed

**ENHANCED_VISUALIZATIONS.md:**
- xG shot maps and surfaces
- WAR/GAR component charts
- Microstat visualizations
- Design mockups
- Data requirements

**MOBILE_OPTIMIZATION.md:**
- Breakpoint strategy
- Component adaptations
- Touch interactions
- Performance targets

---

## Phase 4: Portal Development

**Status:** Planned - PRDs needed before starting

### Required PRDs

| PRD | Status | Priority | Description |
|-----|--------|----------|-------------|
| `portal/API_INTEGRATION.md` | NEEDED | P0 | Full API integration plan |
| `portal/GAME_MANAGEMENT.md` | NEEDED | P1 | Game CRUD operations |
| `portal/ETL_CONTROL.md` | NEEDED | P1 | ETL trigger and monitoring |
| `portal/DATA_BROWSER.md` | NEEDED | P2 | Browse and query data |
| `portal/SETTINGS_MANAGEMENT.md` | NEEDED | P2 | Configuration management |

### PRD Contents Needed

**API_INTEGRATION.md:**
- API endpoint mapping
- Authentication flow
- Error handling
- State management
- Loading states

---

## Phase 5: Tracker Conversion

**Status:** Planned - PRDs needed before starting

### Required PRDs

| PRD | Status | Priority | Description |
|-----|--------|----------|-------------|
| `tracker/RUST_BACKEND.md` | NEEDED | P0 | Rust backend architecture |
| `tracker/NEXTJS_FRONTEND.md` | NEEDED | P0 | Next.js frontend design |
| `tracker/MIGRATION_STRATEGY.md` | NEEDED | P0 | JS to Rust migration approach |
| `tracker/FEATURE_PARITY.md` | NEEDED | P1 | Ensure all 722 functions preserved |
| `tracker/REAL_TIME_COLLAB.md` | NEEDED | P2 | Real-time collaboration features |

### PRD Contents Needed

**RUST_BACKEND.md:**
- Architecture design
- Module structure
- API design
- State management
- Performance targets

**MIGRATION_STRATEGY.md:**
- Function mapping
- Phase-by-phase migration
- Testing strategy
- Rollback plan

---

## Phase 6: ML/CV + Advanced Analytics

**Status:** Planned - PRDs needed before starting

### Required PRDs

| PRD | Status | Priority | Description |
|-----|--------|----------|-------------|
| `ml/XG_MODEL_V2.md` | NEEDED | P0 | Enhanced xG with features |
| `ml/WAR_GAR_REBUILD.md` | NEEDED | P1 | RAPM-based WAR/GAR |
| `ml/MICROSTAT_SURFACES.md` | NEEDED | P1 | Microstat visualization |
| `cv/GOAL_DETECTION.md` | NEEDED | P2 | CV goal detection |
| `cv/PLAYER_TRACKING.md` | NEEDED | P2 | CV player tracking |
| `cv/EVENT_CLASSIFICATION.md` | NEEDED | P3 | CV event classification |

### PRD Contents Needed

**XG_MODEL_V2.md:**
- Feature engineering
- Model architecture (GBM)
- Training data requirements
- Evaluation metrics
- Integration plan

---

## Phase 7: Multi-Tenancy & Scalability

**Status:** Planned - PRDs needed before starting

### Required PRDs

| PRD | Status | Priority | Description |
|-----|--------|----------|-------------|
| `infrastructure/MULTI_TENANT_ARCHITECTURE.md` | NEEDED | P0 | Tenant isolation design |
| `infrastructure/RLS_POLICIES.md` | NEEDED | P0 | Row-level security |
| `infrastructure/SCALABILITY_DESIGN.md` | NEEDED | P1 | Horizontal scaling |
| `infrastructure/CACHING_STRATEGY.md` | NEEDED | P1 | Redis caching |

### PRD Contents Needed

**MULTI_TENANT_ARCHITECTURE.md:**
- tenant_id implementation
- Data isolation approach
- Schema changes
- Migration plan
- Testing strategy

---

## Phase 8: Commercial Launch

**Status:** Planned - PRDs needed before starting

### Required PRDs

| PRD | Status | Priority | Description |
|-----|--------|----------|-------------|
| `commercial/PAYMENT_INTEGRATION.md` | NEEDED | P0 | Stripe integration |
| `commercial/SUBSCRIPTION_MANAGEMENT.md` | NEEDED | P0 | Tiers, billing cycles |
| `commercial/ONBOARDING_FLOW.md` | NEEDED | P1 | New user onboarding |
| `commercial/MARKETING_SITE.md` | NEEDED | P1 | Public website |
| `commercial/CUSTOMER_SUPPORT.md` | NEEDED | P2 | Support system |

### PRD Contents Needed

**PAYMENT_INTEGRATION.md:**
- Stripe setup
- Webhook handling
- Subscription lifecycle
- Invoice management
- Error handling

---

## Phase 9-12: AI Coaching & Analysis

**Status:** Planned - PRDs needed before starting

### Required PRDs

| PRD | Status | Priority | Description |
|-----|--------|----------|-------------|
| `ai/AI_COACH_FOUNDATION.md` | EXISTS | P1 | Basic AI coach (AI_COACHING_FEATURES.md) |
| `ai/VIDEO_UPLOAD_INFRASTRUCTURE.md` | NEEDED | P1 | Video storage and processing |
| `ai/NATURAL_LANGUAGE_QUERIES.md` | NEEDED | P1 | Text-to-SQL system |
| `ai/COACH_MODES.md` | NEEDED | P2 | Game plan, practice, scout modes |
| `ai/GM_MODE.md` | NEEDED | P2 | Team builder, trade analysis |

### PRD Contents Needed

**NATURAL_LANGUAGE_QUERIES.md:**
- NL understanding system
- SQL generation approach
- Response visualization
- Query caching
- Voice input (future)

---

## PRD Priority Summary

### P0 PRDs Needed (Block Progress)

1. `etl/ETL_VERIFICATION_FRAMEWORK.md` - Phase 2
2. `etl/ETL_VECTORIZATION.md` - Phase 2
3. `portal/API_INTEGRATION.md` - Phase 4
4. `tracker/RUST_BACKEND.md` - Phase 5
5. `tracker/NEXTJS_FRONTEND.md` - Phase 5
6. `tracker/MIGRATION_STRATEGY.md` - Phase 5
7. `ml/XG_MODEL_V2.md` - Phase 6
8. `infrastructure/MULTI_TENANT_ARCHITECTURE.md` - Phase 7
9. `infrastructure/RLS_POLICIES.md` - Phase 7
10. `commercial/PAYMENT_INTEGRATION.md` - Phase 8
11. `commercial/SUBSCRIPTION_MANAGEMENT.md` - Phase 8

### P1 PRDs Needed (Important)

1. `etl/ETL_DEBUG_INFRASTRUCTURE.md` - Phase 2
2. `etl/ETL_PERFORMANCE_OPTIMIZATION.md` - Phase 2
3. `dashboard/ENHANCED_VISUALIZATIONS.md` - Phase 3
4. `dashboard/MOBILE_OPTIMIZATION.md` - Phase 3
5. `portal/GAME_MANAGEMENT.md` - Phase 4
6. `tracker/FEATURE_PARITY.md` - Phase 5
7. `ml/WAR_GAR_REBUILD.md` - Phase 6
8. `infrastructure/SCALABILITY_DESIGN.md` - Phase 7
9. `commercial/ONBOARDING_FLOW.md` - Phase 8
10. `ai/VIDEO_UPLOAD_INFRASTRUCTURE.md` - Phase 9
11. `ai/NATURAL_LANGUAGE_QUERIES.md` - Phase 10

---

## PRD Creation Workflow

### When to Create

Create PRD **BEFORE** starting implementation:

1. When phase is about to start
2. When planning a significant feature
3. When architecture decisions needed
4. When multiple approaches possible

### How to Create

1. Copy template: `cp docs/templates/prd-template.md docs/prds/[category]/[name].md`
2. Fill out all sections
3. Get review (peer or Claude)
4. Finalize before implementing

### Template Sections

```markdown
# Feature Name PRD

## Overview
What and why

## Goals
Success criteria

## Non-Goals
Out of scope

## Requirements
Functional and non-functional

## Technical Design
Architecture and approach

## Implementation Plan
Phases and milestones

## Testing Strategy
How to verify

## Risks
What could go wrong

## Open Questions
Decisions needed
```

---

## Related Documentation

- [docs/MASTER_ROADMAP.md](../MASTER_ROADMAP.md) - Phase definitions
- [docs/MASTER_IMPLEMENTATION_PLAN.md](../MASTER_IMPLEMENTATION_PLAN.md) - Detailed tasks
- [docs/templates/prd-template.md](../templates/prd-template.md) - PRD template

---

*Last Updated: 2025-01-22*
