# BenchSight Master Next Steps

**Prioritized next steps for all components**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document consolidates all "next steps" from various documentation into a single, prioritized list.

**Timeline:** 2-week focus (documentation priority)  
**Scope:** All components (ETL, Dashboard, Tracker, Portal, API)

---

## Immediate Next Steps (This Week)

### Priority 1: Documentation (Days 1-4)

**Status:** ✅ COMPLETE

- ✅ Complete code documentation
- ✅ ETL pipeline documentation
- ✅ Dashboard documentation
- ✅ Tracker documentation
- ✅ API documentation
- ✅ Portal documentation

### Priority 2: Documentation Consolidation (Days 5-7)

**Status:** 🚧 IN PROGRESS

- [ ] Create master documents
  - [x] MASTER_INDEX.md
  - [x] MASTER_ROADMAP.md
  - [x] MASTER_RULES.md
  - [x] MASTER_NEXT_STEPS.md
  - [ ] MASTER_PROJECT_MANAGEMENT.md
- [ ] Archive outdated documentation
- [ ] Review and consolidate all docs

---

## Short-Term Goals (Weeks 1-2)

### ETL

**Priority: HIGH**

1. **Code Cleanup**
   - [ ] Refactor `base_etl.py` (4,400 lines → smaller modules)
   - [ ] Remove duplicate code
   - [ ] Extract magic numbers to constants
   - [ ] Improve error handling

2. **Table Verification**
   - [ ] Verify all 139 tables have data
   - [ ] Identify empty/unused tables
   - [ ] Create cleanup plan
   - [ ] Verify stats accuracy

3. **Performance Optimization**
   - [ ] Vectorize pandas operations
   - [ ] Replace `iterrows()` with vectorized operations
   - [ ] Parallelize game processing
   - [ ] Cache intermediate results

### Dashboard

**Priority: MEDIUM**

1. **Search & Filters**
   - [ ] Integrate search into all pages
   - [ ] Add filter dropdowns
   - [ ] Add saved filter presets

2. **Export Expansion**
   - [ ] Add export to teams page
   - [ ] Add export to games page
   - [ ] Add export to standings page

3. **UI Polish**
   - [ ] Add breadcrumbs navigation
   - [ ] Enhance tooltips with formulas
   - [ ] Improve loading states
   - [ ] Improve error states

### Portal

**Priority: HIGH**

1. **API Integration**
   - [ ] Replace placeholder functions
   - [ ] Implement ETL trigger
   - [ ] Implement status polling
   - [ ] Implement upload functionality

2. **Data Display**
   - [ ] Connect to Supabase
   - [ ] Display game list
   - [ ] Display table list
   - [ ] Display data browser

### API

**Priority: MEDIUM**

1. **Missing Endpoints**
   - [ ] Game management endpoints
   - [ ] Data browser endpoints
   - [ ] Table schema endpoints

2. **Enhancements**
   - [ ] Better error handling
   - [ ] Rate limiting
   - [ ] API documentation

---

## Medium-Term Goals (Weeks 3-4)

### ETL

1. **Advanced Features**
   - [ ] Incremental ETL support
   - [ ] Real-time processing
   - [ ] Enhanced validation

2. **Testing**
   - [ ] Increase unit test coverage
   - [ ] Add integration tests
   - [ ] Add performance tests

### Dashboard

1. **Advanced Analytics**
   - [ ] Complete xG analysis page
   - [ ] Complete WAR/GAR analysis page
   - [ ] RAPM analysis

2. **Mobile Optimization**
   - [ ] Responsive tables
   - [ ] Mobile navigation
   - [ ] Touch-friendly interactions

### Tracker

1. **Conversion Planning**
   - [ ] Complete feature inventory
   - [ ] Architecture design
   - [ ] Conversion roadmap

### Portal

1. **Game Management**
   - [ ] Create game functionality
   - [ ] Edit game functionality
   - [ ] Delete game functionality

---

## Long-Term Goals (Months 2-3)

### ETL

1. **ML Integration**
   - [ ] ML feature engineering
   - [ ] Prediction models
   - [ ] Automated quality checks

### Dashboard

1. **Advanced Features**
   - [ ] Predictive analytics
   - [ ] AI-powered insights
   - [ ] Custom report builder

### Tracker

1. **Rust/Next.js Conversion**
   - [ ] Rust backend development
   - [ ] Next.js frontend development
   - [ ] Feature parity testing

### ML/CV

1. **Foundation**
   - [ ] Video processing pipeline
   - [ ] Object detection
   - [ ] Event classification

---

## Critical Path

### Week 1

1. ✅ Complete documentation (Days 1-4)
2. 🚧 Consolidate documentation (Days 5-7)
3. 📋 Review and archive outdated docs

### Week 2

1. 📋 ETL code cleanup
2. 📋 Portal API integration
3. 📋 Dashboard polish

### Weeks 3-4

1. 📋 ETL refactoring
2. 📋 Dashboard advanced features
3. 📋 Tracker conversion planning

---

## Blockers & Risks

### Current Blockers

**None** - All documentation complete, ready to proceed

### Risks

1. **Scope Creep** - Keep focus on documentation and cleanup
2. **Technical Debt** - Address incrementally
3. **Time Constraints** - Prioritize critical items

---

## Success Criteria

### Week 1

- [x] All code documented
- [x] All documentation consolidated
- [ ] Master documents complete
- [ ] Outdated docs archived

### Week 2

- [ ] ETL cleanup plan created
- [ ] Portal API integration started
- [ ] Dashboard polish started

### Month 1

- [ ] ETL refactored
- [ ] Portal functional
- [ ] Dashboard polished
- [ ] Tracker conversion plan complete

---

## Related Documentation

- [MASTER_ROADMAP.md](../MASTER_ROADMAP.md) - Unified roadmap
- [MASTER_RULES.md](../MASTER_RULES.md) - Rules and standards
- [MASTER_PROJECT_MANAGEMENT.md](MASTER_PROJECT_MANAGEMENT.md) - Project management

---

*Last Updated: 2026-01-15*
