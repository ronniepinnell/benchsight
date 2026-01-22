# BenchSight GitHub Issues Backlog

**Comprehensive phased backlog covering the entire project roadmap from MVP to commercial launch.**

Last Updated: 2026-01-22
Total Issues: ~211
Source: [MASTER_IMPLEMENTATION_PLAN.md](MASTER_IMPLEMENTATION_PLAN.md)

---

## Table of Contents

1. [Label Taxonomy](#label-taxonomy)
2. [Milestones](#milestones)
3. [Phase 2: ETL Optimization](#phase-2-etl-optimization-current) (12 issues)
4. [Phase 3: Dashboard Enhancement](#phase-3-dashboard-enhancement) (16 issues)
5. [Phase 4: Portal Development](#phase-4-portal-development) (16 issues)
6. [Phase 5: Tracker Conversion](#phase-5-tracker-conversion) (12 issues)
7. [Phase 6: ML/CV + Advanced Analytics](#phase-6-mlcv--advanced-analytics) (20 issues)
8. [Phase 7: Multi-Tenancy & Scalability](#phase-7-multi-tenancy--scalability) (12 issues)
9. [Phase 8: Commercial Launch](#phase-8-commercial-launch) (12 issues)
10. [Phase 9-12: AI Coaching & Analysis](#phase-9-12-ai-coaching--analysis) (20 issues)
11. [Foundation & Workflow](#foundation--workflow) (13 issues)

---

## Label Taxonomy

### Type Labels
| Label | Description |
|-------|-------------|
| `type:feature` | New functionality |
| `type:enhancement` | Improvement to existing feature |
| `type:fix` | Bug fix |
| `type:refactor` | Code restructuring without behavior change |
| `type:docs` | Documentation only |
| `type:test` | Testing infrastructure |
| `type:chore` | Maintenance tasks |
| `type:design` | Architecture/design decisions |
| `type:research` | Investigation/spike |
| `type:perf` | Performance optimization |

### Area Labels
| Label | Description |
|-------|-------------|
| `area:etl` | ETL pipeline (`src/`, `run_etl.py`) |
| `area:dashboard` | Next.js dashboard (`ui/dashboard/`) |
| `area:tracker` | Game tracker (`ui/tracker/`) |
| `area:portal` | Admin portal (`ui/portal/`) |
| `area:api` | FastAPI backend (`api/`) |
| `area:data` | Database schema, migrations |
| `area:infra` | Infrastructure, deployment |
| `area:docs` | Documentation |
| `area:commercial` | Business/monetization |
| `area:workflow` | Development workflow |
| `area:analytics` | Advanced analytics/ML |

### Priority Labels
| Label | Description |
|-------|-------------|
| `priority:p0` | Critical/blocking - do first |
| `priority:p1` | High priority - core functionality |
| `priority:p2` | Medium priority - important but not blocking |
| `priority:p3` | Low priority - nice to have |

### Phase Labels
| Label | Phase | Status |
|-------|-------|--------|
| `phase:1` | Foundation & Documentation | [YES] COMPLETE |
| `phase:2` | ETL Optimization | [IN_PROGRESS] CURRENT |
| `phase:3` | Dashboard Enhancement | [PLANNED] PLANNED |
| `phase:4` | Portal Development | [PLANNED] PLANNED |
| `phase:5` | Tracker Conversion | [PLANNED] PLANNED |
| `phase:6` | ML/CV Integration | [PLANNED] PLANNED |
| `phase:7` | Multi-Tenancy | [PLANNED] PLANNED |
| `phase:8` | Commercial Launch | [PLANNED] PLANNED |
| `phase:9` | AI Coach Foundation | [PLANNED] PLANNED |
| `phase:10` | Natural Language Queries | [PLANNED] PLANNED |
| `phase:11` | Coach Modes | [PLANNED] PLANNED |
| `phase:12` | GM Mode & Advanced | [PLANNED] PLANNED |

---

## Milestones

| Milestone | Phases | Description | Target |
|-----------|--------|-------------|--------|
| **M1: MVP Foundation** | 1-4 | Core platform functional | Week 16 |
| **M2: Tracker Modernization** | 5 | Rust/Next.js tracker | Week 24 |
| **M3: ML/CV Integration** | 6 | Automated tracking | Week 32 |
| **M4: Commercial Ready** | 7-8 | Multi-tenant, payments | Week 48 |
| **M5: AI Coaching Platform** | 9-12 | AI coach, NL queries, coach/GM modes | Week 48+ |

---

## Phase 2: ETL Optimization (CURRENT)

**Status:** [IN_PROGRESS] IN PROGRESS
**Timeline:** Weeks 5-8
**Objective:** Clean up ETL code, optimize performance, verify tables, add debugging infrastructure, bulletproof code

### Issues

#### ETL-001: Modularize base_etl.py
- **Labels:** `type:refactor`, `area:etl`, `priority:p0`, `phase:2`
- **Description:** Split `src/core/base_etl.py` (4,400 lines) into smaller modules (<500 lines each)
- **Acceptance Criteria:**
  - [ ] Create `src/core/etl_phases/` directory
  - [ ] Extract Phase 1 logic → `phase1_blb_loader.py`
  - [ ] Extract Phase 3 logic → `phase3_tracking_processor.py`
  - [ ] Extract derived columns → `derived_columns.py`
  - [ ] Extract validation → `validation.py`
  - [ ] `base_etl.py` reduced to orchestration only
  - [ ] All 139 tables still generated
  - [ ] All tests pass

#### ETL-002: Profile ETL and identify bottlenecks
- **Labels:** `type:chore`, `area:etl`, `priority:p1`, `phase:2`
- **Description:** Profile ETL execution to identify slow operations
- **Acceptance Criteria:**
  - [ ] Add timing instrumentation to each phase
  - [ ] Identify top 10 slowest operations
  - [ ] Document bottlenecks in `docs/etl/ETL_PERFORMANCE.md`
  - [ ] Find all `.iterrows()` usage

#### ETL-003: Replace .iterrows() with vectorized operations
- **Labels:** `type:perf`, `area:etl`, `priority:p0`, `phase:2`
- **Depends On:** ETL-002
- **Description:** Remove all `.iterrows()` calls and replace with vectorized pandas operations
- **Acceptance Criteria:**
  - [ ] Zero `.iterrows()` usage in codebase
  - [ ] Use `.groupby()` and `.apply()` instead
  - [ ] Data integrity maintained
  - [ ] Performance improved

#### ETL-004: Create table verification script
- **Labels:** `type:test`, `area:etl`, `priority:p0`, `phase:2`
- **Description:** Create automated script to verify all tables have data
- **Acceptance Criteria:**
  - [ ] Script checks all 139 tables exist
  - [ ] Script checks row counts > 0 for active tables
  - [ ] Script validates column schemas
  - [ ] Output report in markdown format

#### ETL-005: Verify all 139 tables have data
- **Labels:** `type:test`, `area:etl`, `priority:p0`, `phase:2`
- **Depends On:** ETL-004
- **Description:** Run verification to confirm all tables populated correctly
- **Acceptance Criteria:**
  - [ ] All dimension tables populated
  - [ ] All fact tables populated
  - [ ] All QA tables populated
  - [ ] Document any empty/unused tables

#### ETL-006: Validate foreign key relationships
- **Labels:** `type:test`, `area:etl`, `priority:p0`, `phase:2`
- **Depends On:** ETL-004
- **Description:** Verify referential integrity across all tables
- **Acceptance Criteria:**
  - [ ] All foreign keys resolve
  - [ ] No orphaned records
  - [ ] Document relationship graph

#### ETL-007: Identify and document unused tables
- **Labels:** `type:docs`, `area:etl`, `priority:p2`, `phase:2`
- **Depends On:** ETL-005
- **Description:** Find tables that aren't used by dashboard or downstream processes
- **Acceptance Criteria:**
  - [ ] List all unused tables
  - [ ] Recommendation: keep, archive, or delete
  - [ ] Update DATA_DICTIONARY.md

#### ETL-008: Validate xG calculations
- **Labels:** `type:test`, `area:etl`, `priority:p1`, `phase:2`
- **Description:** Verify expected goals calculation accuracy
- **Acceptance Criteria:**
  - [ ] xG values within expected ranges (0-1)
  - [ ] xG sums match reasonable goals-per-game
  - [ ] Compare against known benchmarks
  - [ ] Add regression tests

#### ETL-009: Validate WAR/GAR calculations
- **Labels:** `type:test`, `area:etl`, `priority:p1`, `phase:2`
- **Description:** Verify Wins Above Replacement calculation accuracy
- **Acceptance Criteria:**
  - [ ] WAR values within expected ranges
  - [ ] Component breakdowns sum correctly
  - [ ] Add regression tests

#### ETL-010: Validate Corsi/Fenwick calculations
- **Labels:** `type:test`, `area:etl`, `priority:p1`, `phase:2`
- **Description:** Verify shot attempt metrics accuracy
- **Acceptance Criteria:**
  - [ ] Corsi = shots + missed + blocked
  - [ ] Fenwick = shots + missed
  - [ ] CF% + CA% = 100%
  - [ ] Add regression tests

#### ETL-011: Verify goal counting matches official counts
- **Labels:** `type:test`, `area:etl`, `priority:p0`, `phase:2`
- **Description:** Critical test - ensure goals counted correctly
- **Acceptance Criteria:**
  - [ ] Goals ONLY counted when `event_type == 'Goal' AND event_detail == 'Goal_Scored'`
  - [ ] Match official game scores for all test games
  - [ ] Document goal counting rules
  - [ ] Add regression tests

#### ETL-012: Add verification tests to CI
- **Labels:** `type:chore`, `area:etl`, `priority:p1`, `phase:2`
- **Depends On:** ETL-004, ETL-005, ETL-006
- **Description:** Integrate table verification into CI pipeline
- **Acceptance Criteria:**
  - [ ] GitHub Action runs verification on PR
  - [ ] Fails on missing tables
  - [ ] Fails on broken foreign keys
  - [ ] Reports results in PR comment

#### ETL-013: Comprehensive table verification framework
- **Labels:** `type:test`, `area:etl`, `priority:p0`, `phase:2`
- **Execution Order:** 1
- **Description:** Create framework to verify all 139 tables: existence, row counts, column schemas, data types, null percentages, value ranges
- **Acceptance Criteria:**
  - [ ] Framework checks table existence
  - [ ] Framework validates column schemas (names, types, nullability)
  - [ ] Framework calculates null percentages per column
  - [ ] Framework validates value ranges (min/max for numeric, enum values for categorical)
  - [ ] Framework validates primary keys
  - [ ] Framework validates foreign keys
  - [ ] Outputs comprehensive verification report

#### ETL-014: Phase-by-phase table verification
- **Labels:** `type:test`, `area:etl`, `priority:p0`, `phase:2`
- **Execution Order:** 2
- **Depends On:** ETL-013
- **Description:** Verify tables after each ETL phase (Phase 1, 3B, 4, 4B, 4C, 4D, 4E, 5, 6, 7, 8, 9, 10, 10B, 11)
- **Acceptance Criteria:**
  - [ ] Verification runs after Phase 1 (base ETL)
  - [ ] Verification runs after Phase 3B (dimension tables)
  - [ ] Verification runs after each Phase 4 sub-phase
  - [ ] Verification runs after Phases 5-11
  - [ ] Phase-specific verification rules defined
  - [ ] Phase-by-phase verification report generated

#### ETL-015: Column-level verification for all tables
- **Labels:** `type:test`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 3
- **Depends On:** ETL-013
- **Description:** Verify each column in each table: data type, null percentage, value ranges, business rules
- **Acceptance Criteria:**
  - [ ] All 139 tables have column verification
  - [ ] Data type validation (int, float, string, date, etc.)
  - [ ] Null percentage calculated and flagged if > threshold
  - [ ] Value range validation (e.g., goals >= 0, percentages 0-100)
  - [ ] Business rule validation (e.g., CF% + CA% = 100%)
  - [ ] Column verification report generated

#### ETL-016: Review table generation code and logic
- **Labels:** `type:docs`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 4
- **Description:** Review code that generates each table, document logic, verify calculations
- **Acceptance Criteria:**
  - [ ] All table generation code reviewed
  - [ ] Logic documented for each table
  - [ ] Calculations verified against formulas
  - [ ] Code review checklist completed
  - [ ] Issues identified and documented

#### ETL-017: Validate table structure against data dictionary
- **Labels:** `type:test`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 5
- **Depends On:** ETL-015, ETL-016
- **Description:** Compare actual table structures against DATA_DICTIONARY.md, identify discrepancies
- **Acceptance Criteria:**
  - [ ] All tables compared to data dictionary
  - [ ] Column name mismatches identified
  - [ ] Column type mismatches identified
  - [ ] Missing columns identified
  - [ ] Extra columns identified
  - [ ] Data dictionary updated with discrepancies

#### ETL-018: Verify primary keys for all tables
- **Labels:** `type:test`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 6
- **Depends On:** ETL-013
- **Description:** Verify all tables have correct primary keys, no duplicates, proper key format
- **Acceptance Criteria:**
  - [ ] All tables have primary keys defined
  - [ ] Primary key format validated ({XX}{ID}{5D} format)
  - [ ] No duplicate primary keys found
  - [ ] Primary key uniqueness verified
  - [ ] Primary key report generated

#### ETL-019: Verify foreign keys for all tables
- **Labels:** `type:test`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 7
- **Depends On:** ETL-013, ETL-018
- **Description:** Verify all foreign keys resolve correctly, no orphaned records
- **Acceptance Criteria:**
  - [ ] All foreign keys identified
  - [ ] Foreign key relationships validated
  - [ ] No orphaned records found
  - [ ] Foreign key referential integrity verified
  - [ ] Foreign key report generated

#### ETL-020: Create table verification CI integration
- **Labels:** `type:chore`, `area:etl`, `priority:p2`, `phase:2`
- **Execution Order:** 8
- **Depends On:** ETL-013, ETL-014, ETL-015
- **Description:** Integrate table verification into CI pipeline, run on every PR
- **Acceptance Criteria:**
  - [ ] GitHub Action runs verification on PR
  - [ ] Fails on table/column verification failures
  - [ ] Reports results in PR comment
  - [ ] Verification report artifact uploaded

#### ETL-021: Set up local Docker PostgreSQL environment
- **Labels:** `type:infra`, `area:etl`, `priority:p0`, `phase:2`
- **Execution Order:** 9
- **Description:** Create Docker Compose setup for local PostgreSQL with 4-schema architecture (raw, stage, intermediate, datamart)
- **Acceptance Criteria:**
  - [ ] Docker Compose file created
  - [ ] PostgreSQL container configured
  - [ ] 4 schemas created: raw, stage, intermediate, datamart
  - [ ] Connection configuration documented
  - [ ] Setup script created
  - [ ] Documentation in `docs/etl/POSTGRES_DEBUG_SETUP.md`

#### ETL-022: Create PostgreSQL state manager for ETL phases
- **Labels:** `type:feature`, `area:etl`, `priority:p0`, `phase:2`
- **Execution Order:** 10
- **Depends On:** ETL-021
- **Description:** Create state manager to save/restore PostgreSQL state at each ETL phase for debugging
- **Acceptance Criteria:**
  - [ ] State manager saves PostgreSQL state after each phase
  - [ ] State manager can restore to any phase
  - [ ] State includes all tables in appropriate schemas
  - [ ] State manager API documented
  - [ ] Integration with ETL pipeline

#### ETL-023: Create phase-by-phase ETL executor with PostgreSQL storage
- **Labels:** `type:feature`, `area:etl`, `priority:p0`, `phase:2`
- **Execution Order:** 11
- **Depends On:** ETL-021, ETL-022
- **Description:** Create executor that runs ETL phases one at a time, storing results in PostgreSQL for inspection
- **Acceptance Criteria:**
  - [ ] Executor runs single phase or phase range
  - [ ] Results stored in PostgreSQL after each phase
  - [ ] Phase execution can be paused/resumed
  - [ ] Phase execution logs stored
  - [ ] Integration with existing ETL pipeline

#### ETL-024: Create data comparison tools for PostgreSQL debugging
- **Labels:** `type:feature`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 12
- **Depends On:** ETL-021, ETL-023
- **Description:** Create tools to compare data between phases, identify differences, validate transformations
- **Acceptance Criteria:**
  - [ ] Tool compares tables between phases
  - [ ] Tool identifies row count differences
  - [ ] Tool identifies column value differences
  - [ ] Tool validates transformations
  - [ ] Comparison reports generated

#### ETL-025: Create PostgreSQL debugging CLI interface
- **Labels:** `type:feature`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 13
- **Depends On:** ETL-021, ETL-022, ETL-023
- **Description:** Create CLI interface for PostgreSQL debugging: query tables, compare phases, inspect data
- **Acceptance Criteria:**
  - [ ] CLI command to list tables in schema
  - [ ] CLI command to query table data
  - [ ] CLI command to compare phases
  - [ ] CLI command to restore state
  - [ ] CLI documentation

#### ETL-026: Audit and identify dead code
- **Labels:** `type:refactor`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 14
- **Description:** Identify unused functions, imports, files, and code paths in ETL codebase
- **Acceptance Criteria:**
  - [ ] Script identifies unused functions
  - [ ] Script identifies unused imports
  - [ ] Script identifies unused files
  - [ ] Script identifies unreachable code
  - [ ] Dead code report generated
  - [ ] Dead code categorized (safe to delete, needs review, etc.)

#### ETL-027: Remove dead code from ETL codebase
- **Labels:** `type:refactor`, `area:etl`, `priority:p2`, `phase:2`
- **Execution Order:** 15
- **Depends On:** ETL-026
- **Description:** Remove identified dead code, organize archive directories
- **Acceptance Criteria:**
  - [ ] Dead functions removed
  - [ ] Dead imports removed
  - [ ] Dead files moved to archive or deleted
  - [ ] Archive directories organized
  - [ ] All tests still pass
  - [ ] ETL still generates 139 tables

#### ETL-028: Clean up archive directories
- **Labels:** `type:chore`, `area:etl`, `priority:p3`, `phase:2`
- **Execution Order:** 16
- **Depends On:** ETL-027
- **Description:** Organize and document archive directories, remove truly obsolete code
- **Acceptance Criteria:**
  - [ ] Archive directories organized
  - [ ] Archive contents documented
  - [ ] Obsolete code removed
  - [ ] Archive structure documented

#### ETL-029: Create comprehensive code walkthrough documentation
- **Labels:** `type:docs`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 17
- **Description:** Document code flow, logic, and architecture for ETL pipeline
- **Acceptance Criteria:**
  - [ ] Document main ETL flow (run_etl.py → base_etl.py → phases)
  - [ ] Document each phase's purpose and logic
  - [ ] Document table generation flow
  - [ ] Document calculation flow
  - [ ] Document data transformation flow
  - [ ] Code walkthrough guide created in `docs/etl/CODE_WALKTHROUGH.md`

#### ETL-030: Document table generation logic for all 139 tables
- **Labels:** `type:docs`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 18
- **Depends On:** ETL-029
- **Description:** Document how each of the 139 tables is generated, including source data, transformations, and calculations
- **Acceptance Criteria:**
  - [ ] All 139 tables documented
  - [ ] Source data identified for each table
  - [ ] Transformations documented
  - [ ] Calculations documented
  - [ ] Dependencies documented
  - [ ] Table generation guide created

#### ETL-031: Create architecture diagrams for ETL pipeline
- **Labels:** `type:docs`, `area:etl`, `priority:p2`, `phase:2`
- **Execution Order:** 19
- **Depends On:** ETL-029
- **Description:** Create visual diagrams showing ETL architecture, data flow, and phase dependencies
- **Acceptance Criteria:**
  - [ ] ETL architecture diagram created
  - [ ] Data flow diagram created
  - [ ] Phase dependency diagram created
  - [ ] Table dependency diagram created
  - [ ] Diagrams in `docs/etl/ARCHITECTURE_DIAGRAMS.md`

#### ETL-032: Add comprehensive error handling throughout ETL
- **Labels:** `type:fix`, `area:etl`, `priority:p0`, `phase:2`
- **Execution Order:** 20
- **Description:** Add try/except blocks, error logging, and graceful error handling throughout ETL pipeline
- **Acceptance Criteria:**
  - [ ] Error handling added to all major functions
  - [ ] Error logging implemented
  - [ ] Graceful error recovery where possible
  - [ ] Error messages are clear and actionable
  - [ ] Error handling tested

#### ETL-033: Add type hints to all ETL code
- **Labels:** `type:refactor`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 21
- **Description:** Add Python type hints to all functions, methods, and class attributes in ETL codebase
- **Acceptance Criteria:**
  - [ ] All functions have type hints
  - [ ] All methods have type hints
  - [ ] All class attributes have type hints
  - [ ] Type hints validated with mypy
  - [ ] Type hints documented

#### ETL-034: Add data validation at each ETL phase
- **Labels:** `type:test`, `area:etl`, `priority:p0`, `phase:2`
- **Execution Order:** 22
- **Description:** Add validation checks at each ETL phase to catch data quality issues early
- **Acceptance Criteria:**
  - [ ] Validation added to Phase 1 (data loading)
  - [ ] Validation added to Phase 3B (dimension tables)
  - [ ] Validation added to each Phase 4 sub-phase
  - [ ] Validation added to Phases 5-11
  - [ ] Validation failures logged and reported
  - [ ] Validation rules documented

#### ETL-035: Create unit tests for critical calculations
- **Labels:** `type:test`, `area:etl`, `priority:p0`, `phase:2`
- **Execution Order:** 23
- **Description:** Create unit tests for goals, xG, WAR/GAR, Corsi, and other critical calculations
- **Acceptance Criteria:**
  - [ ] Unit tests for goal counting
  - [ ] Unit tests for xG calculations
  - [ ] Unit tests for WAR/GAR calculations
  - [ ] Unit tests for Corsi/Fenwick calculations
  - [ ] Unit tests for other critical calculations
  - [ ] Test coverage > 80% for calculations

#### ETL-036: Create integration tests for ETL phases
- **Labels:** `type:test`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 24
- **Depends On:** ETL-035
- **Description:** Create integration tests that run entire ETL phases and validate outputs
- **Acceptance Criteria:**
  - [ ] Integration test for Phase 1
  - [ ] Integration test for Phase 3B
  - [ ] Integration test for each Phase 4 sub-phase
  - [ ] Integration test for Phases 5-11
  - [ ] Integration tests validate table outputs
  - [ ] Integration tests run in CI

#### ETL-037: Add edge case handling throughout ETL
- **Labels:** `type:fix`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 25
- **Description:** Add handling for edge cases: empty data, missing columns, invalid values, null handling
- **Acceptance Criteria:**
  - [ ] Edge cases identified for each phase
  - [ ] Edge case handling implemented
  - [ ] Edge case handling tested
  - [ ] Edge cases documented
  - [ ] Graceful degradation for edge cases

#### ETL-038: Create regression test suite
- **Labels:** `type:test`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 26
- **Depends On:** ETL-035, ETL-036
- **Description:** Create regression tests to prevent unintended side effects from code changes
- **Acceptance Criteria:**
  - [ ] Regression tests for all 139 tables
  - [ ] Regression tests for critical calculations
  - [ ] Regression tests for data transformations
  - [ ] Regression test baseline established
  - [ ] Regression tests run in CI

#### ETL-039: Add input validation for all ETL functions
- **Labels:** `type:fix`, `area:etl`, `priority:p1`, `phase:2`
- **Execution Order:** 27
- **Description:** Add input validation (type checking, value ranges, required fields) to all ETL functions
- **Acceptance Criteria:**
  - [ ] Input validation added to all public functions
  - [ ] Input validation for data types
  - [ ] Input validation for value ranges
  - [ ] Input validation for required fields
  - [ ] Validation errors are clear and actionable

#### ETL-040: Add comprehensive logging throughout ETL
- **Labels:** `type:chore`, `area:etl`, `priority:p2`, `phase:2`
- **Execution Order:** 28
- **Description:** Add structured logging throughout ETL pipeline for debugging and monitoring
- **Acceptance Criteria:**
  - [ ] Logging added to all major functions
  - [ ] Log levels appropriate (DEBUG, INFO, WARNING, ERROR)
  - [ ] Logging includes context (phase, table, function)
  - [ ] Logging output is structured and parseable
  - [ ] Logging configuration documented

### Execution Order

**Phase 2 issues should be executed in this order for optimal workflow:**

1. **ETL-013**: Comprehensive table verification framework (foundation)
2. **ETL-014**: Phase-by-phase table verification (builds on framework)
3. **ETL-015**: Column-level verification (detailed validation)
4. **ETL-016**: Review table generation code (understand before verifying)
5. **ETL-017**: Validate table structure (compare to dictionary)
6. **ETL-018**: Verify primary keys (data integrity)
7. **ETL-019**: Verify foreign keys (referential integrity)
8. **ETL-020**: Create table verification CI (automation)
9. **ETL-021**: Set up local Docker PostgreSQL (debugging infrastructure)
10. **ETL-022**: Create PostgreSQL state manager (debugging tool)
11. **ETL-023**: Create phase-by-phase executor (debugging tool)
12. **ETL-024**: Create data comparison tools (debugging tool)
13. **ETL-025**: Create PostgreSQL debugging CLI (debugging interface)
14. **ETL-026**: Audit dead code (identify before removing)
15. **ETL-027**: Remove dead code (cleanup)
16. **ETL-028**: Clean up archive directories (organization)
17. **ETL-029**: Create code walkthrough documentation (understanding)
18. **ETL-030**: Document table generation logic (detailed docs)
19. **ETL-031**: Create architecture diagrams (visual docs)
20. **ETL-032**: Add error handling (bulletproofing)
21. **ETL-033**: Add type hints (code quality)
22. **ETL-034**: Add data validation (bulletproofing)
23. **ETL-035**: Create unit tests (testing foundation)
24. **ETL-036**: Create integration tests (testing coverage)
25. **ETL-037**: Add edge case handling (bulletproofing)
26. **ETL-038**: Create regression test suite (prevent regressions)
27. **ETL-039**: Add input validation (bulletproofing)
28. **ETL-040**: Add comprehensive logging (observability)

**Existing issues execution order:**
- **ETL-001**: Modularize base_etl.py (can run in parallel with verification)
- **ETL-002**: Profile ETL (can run early, informs optimization)
- **ETL-003**: Replace iterrows (depends on ETL-002, can run after profiling)
- **ETL-004**: Create verification script (superseded by ETL-013, can be merged)
- **ETL-005**: Verify 139 tables (superseded by ETL-014, can be merged)
- **ETL-006**: Validate foreign keys (superseded by ETL-019, can be merged)
- **ETL-007**: Identify unused tables (can run after ETL-026 dead code audit)
- **ETL-008**: Validate xG (can run after ETL-035 unit tests)
- **ETL-009**: Validate WAR/GAR (can run after ETL-035 unit tests)
- **ETL-010**: Validate Corsi/Fenwick (can run after ETL-035 unit tests)
- **ETL-011**: Verify goal counting (critical, should run early - execution order 0.5)
- **ETL-012**: Add verification to CI (depends on ETL-020, can run after)

---

## Phase 3: Dashboard Enhancement

**Status:** [PLANNED] PLANNED
**Timeline:** Weeks 9-12
**Objective:** Enhance UI/UX, add advanced analytics pages, optimize performance

### Issues

#### DASH-001: Add trend line charts to player pages
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Description:** Add performance trend visualizations to player detail pages
- **Acceptance Criteria:**
  - [ ] Line charts showing stats over time
  - [ ] Multiple stat selection
  - [ ] Responsive design

#### DASH-002: Enhance shot map visualization
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Description:** Improve shot location visualizations with better UX
- **Acceptance Criteria:**
  - [ ] Color coding by outcome (goal, save, miss, block)
  - [ ] xG overlay option
  - [ ] Filter by period, strength, shooter
  - [ ] Hover tooltips with details

#### DASH-003: Add heatmap visualizations
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Description:** Add ice surface heatmaps for various metrics
- **Acceptance Criteria:**
  - [ ] Shot location heatmaps
  - [ ] Zone time heatmaps
  - [ ] Player positioning heatmaps

#### DASH-004: Improve leaderboard design
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Description:** Redesign leaderboard tables for better UX
- **Acceptance Criteria:**
  - [ ] Sortable columns
  - [ ] Sparkline mini-charts
  - [ ] Highlight above/below average
  - [ ] Player photos/avatars

#### DASH-005: Mobile-responsive navigation
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Description:** Add responsive navigation for mobile devices
- **Acceptance Criteria:**
  - [ ] Hamburger menu on mobile
  - [ ] Touch-friendly navigation
  - [ ] Collapsible sidebar

#### DASH-006: Optimize mobile table layouts
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Depends On:** DASH-005
- **Description:** Make data tables work well on mobile
- **Acceptance Criteria:**
  - [ ] Horizontal scroll for wide tables
  - [ ] Card view option for narrow screens
  - [ ] Priority column visibility

#### DASH-007: Create xG analysis page
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Description:** New page dedicated to expected goals analysis
- **Acceptance Criteria:**
  - [ ] xG vs actual goals comparison
  - [ ] xG quality visualization
  - [ ] Finishing skill metrics
  - [ ] Team and player views

#### DASH-008: Create WAR/GAR analysis page
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Description:** New page for Wins Above Replacement analysis
- **Acceptance Criteria:**
  - [ ] GAR component breakdown charts
  - [ ] WAR rankings table
  - [ ] WAR trend visualizations
  - [ ] Player comparison tool

#### DASH-009: Add RAPM analysis section
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Depends On:** DASH-008
- **Description:** Add Regularized Adjusted Plus-Minus to WAR page
- **Acceptance Criteria:**
  - [ ] RAPM component display
  - [ ] Comparison to raw +/-
  - [ ] Confidence intervals

#### DASH-010: Create reusable search component
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Description:** Build standardized search component for all pages
- **Acceptance Criteria:**
  - [ ] Autocomplete suggestions
  - [ ] Recent searches
  - [ ] Keyboard navigation
  - [ ] Debounced input

#### DASH-011: Add search to all pages
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Depends On:** DASH-010
- **Description:** Integrate search component across all pages
- **Acceptance Criteria:**
  - [ ] Search on player pages
  - [ ] Search on team pages
  - [ ] Search on game pages
  - [ ] Global search option

#### DASH-012: Add filter persistence (localStorage)
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Depends On:** DASH-010
- **Description:** Remember user filter selections between sessions
- **Acceptance Criteria:**
  - [ ] Filters saved to localStorage
  - [ ] Restored on page load
  - [ ] Clear filters option
  - [ ] Per-page filter memory

#### DASH-013: Add CSV export to all pages
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Description:** Enable CSV export from any data table
- **Acceptance Criteria:**
  - [ ] Export button on all tables
  - [ ] Includes filtered data only
  - [ ] Proper column headers
  - [ ] Date-stamped filename

#### DASH-014: Add Excel export option
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Depends On:** DASH-013
- **Description:** Add Excel (.xlsx) export alongside CSV
- **Acceptance Criteria:**
  - [ ] Excel format option
  - [ ] Formatted cells
  - [ ] Multiple sheets for related data

#### DASH-015: Add PDF export for reports
- **Labels:** `type:feature`, `area:dashboard`, `priority:p3`, `phase:3`
- **Description:** Generate PDF reports from dashboard pages
- **Acceptance Criteria:**
  - [ ] Player report PDF
  - [ ] Team report PDF
  - [ ] Game summary PDF
  - [ ] Include visualizations

#### DASH-016: Create reusable export component
- **Labels:** `type:refactor`, `area:dashboard`, `priority:p1`, `phase:3`
- **Depends On:** DASH-013
- **Description:** Standardize export functionality across pages
- **Acceptance Criteria:**
  - [ ] Single export component
  - [ ] Format selector (CSV, Excel, PDF)
  - [ ] Progress indicator for large exports

### Existing Dashboard Pages - Enhancements

#### DASH-017: Standings Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/standings`
- **Description:** Enhance standings page with additional features
- **Acceptance Criteria:**
  - [ ] Add team logos to standings
  - [ ] Add win/loss streak indicators
  - [ ] Add goal differential visualization
  - [ ] Add conference/division grouping
  - [ ] Add historical standings comparison
  - [ ] Add playoff race visualization
  - [ ] Add export functionality

#### DASH-018: Players Directory Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players`
- **Description:** Enhance player directory with better filtering and display
- **Acceptance Criteria:**
  - [ ] Add advanced filters (position, team, min GP, age range)
  - [ ] Add player photos to table
  - [ ] Add quick stat cards (leaders)
  - [ ] Add export functionality
  - [ ] Add sorting by advanced metrics
  - [ ] Add player search with autocomplete

#### DASH-019: Player Profile Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/players/[playerId]`
- **Description:** Enhance player profile with Z-scores, heatmaps, and visualizations
- **Acceptance Criteria:**
  - [ ] Add Z-score visualization (from wireframes)
  - [ ] Add player photo to header
  - [ ] Add collapsible accordion sections for advanced stats
  - [ ] Add shot density heatmap (from wireframes)
  - [ ] Add player position heatmap (if tracking data available)
  - [ ] Add career trajectory visualization
  - [ ] Add similar players suggestion
  - [ ] Add export functionality

#### DASH-020: Player Trends Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players/[playerId]/trends`
- **Description:** Enhance trends page with more metrics and analysis
- **Acceptance Criteria:**
  - [ ] Add more trend metrics (CF%, xG%, WAR trend)
  - [ ] Add streak analysis (hot/cold streaks)
  - [ ] Add performance vs rating comparison
  - [ ] Add rolling average customization (5-game, 10-game, 20-game)
  - [ ] Add export functionality

#### DASH-021: Player Game Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players/[playerId]/games/[gameId]`
- **Description:** Enhance player game page with shift timeline and video
- **Acceptance Criteria:**
  - [ ] Add shift timeline visualization
  - [ ] Add event timeline for player
  - [ ] Add video integration (if available)
  - [ ] Add shot map for this game
  - [ ] Add comparison to season averages
  - [ ] Add export functionality

#### DASH-022: Player Comparison Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players/compare`
- **Description:** Enhance comparison with radar charts and advanced metrics
- **Acceptance Criteria:**
  - [ ] Add radar chart for multi-player comparison (from wireframes)
  - [ ] Add trend comparison charts
  - [ ] Add micro stats comparison
  - [ ] Add head-to-head matchup stats
  - [ ] Add export functionality

#### DASH-023: Goalies Directory Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/goalies`
- **Description:** Enhance goalie directory with photos and advanced filters
- **Acceptance Criteria:**
  - [ ] Add goalie photos to table
  - [ ] Add advanced filters
  - [ ] Add quick stat cards
  - [ ] Add export functionality
  - [ ] Add GSAx (Goals Saved Above Expected) leaders

#### DASH-024: Goalie Profile Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/goalies/[goalieId]`
- **Description:** Enhance goalie profile with save heatmaps and advanced visualizations
- **Acceptance Criteria:**
  - [ ] Add save location heatmap (from wireframes)
  - [ ] Add save type distribution chart
  - [ ] Add danger zone save breakdown
  - [ ] Add rebound control metrics visualization
  - [ ] Add goalie photo to header
  - [ ] Add export functionality

#### DASH-025: Goalie Comparison Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/goalies/compare`
- **Description:** Enhance goalie comparison with radar charts
- **Acceptance Criteria:**
  - [ ] Add radar chart comparison
  - [ ] Add save type distribution comparison
  - [ ] Add GSAx comparison
  - [ ] Add export functionality

#### DASH-026: Teams Directory Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/teams`
- **Description:** Enhance team directory with logos and quick stats
- **Acceptance Criteria:**
  - [ ] Add team logos to table
  - [ ] Add quick stat cards
  - [ ] Add filters
  - [ ] Add export functionality

#### DASH-027: Team Profile Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/team/[teamName]` or `/norad/teams/[teamId]`
- **Description:** Enhance team profile with passing grids and presence charts
- **Acceptance Criteria:**
  - [ ] Add passing grid matrix (from wireframes)
  - [ ] Add presence & importance charts (from wireframes)
  - [ ] Add team shot charts
  - [ ] Add zone time heatmaps
  - [ ] Add export functionality

#### DASH-028: Team Comparison Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/teams/compare`
- **Description:** Enhance team comparison with visualizations
- **Acceptance Criteria:**
  - [ ] Add radar chart comparison
  - [ ] Add head-to-head record visualization
  - [ ] Add export functionality

#### DASH-029: Games List Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/games`
- **Description:** Enhance games list with preview cards and predictions
- **Acceptance Criteria:**
  - [ ] Add game preview cards with key stats
  - [ ] Add win probability predictions (if ML available)
  - [ ] Add filters (season, team, game type, date range)
  - [ ] Add export functionality

#### DASH-030: Game Detail Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/games/[gameId]`
- **Description:** Enhance game detail with win probability, cumulative charts, and video
- **Acceptance Criteria:**
  - [ ] Add win probability chart (from wireframes)
  - [ ] Add cumulative Corsi/xG flow charts (from wireframes)
  - [ ] Add quadrant scatter plots (CF% vs xGF%) (from wireframes)
  - [ ] Add video integration (from wireframes)
  - [ ] Add shift timeline with video (from wireframes)
  - [ ] Add game flow visualization
  - [ ] Add momentum chart
  - [ ] Add export functionality

#### DASH-031: Shot Maps Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/games/shots`
- **Description:** Enhance shot maps with density heatmaps
- **Acceptance Criteria:**
  - [ ] Add shot density heatmap (from wireframes)
  - [ ] Add period-by-period shot maps
  - [ ] Add player-specific shot maps
  - [ ] Add strength situation filters
  - [ ] Add export functionality

#### DASH-032: Schedule Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/schedule`
- **Description:** Enhance schedule with calendar view and predictions
- **Acceptance Criteria:**
  - [ ] Add calendar view
  - [ ] Add win probability predictions
  - [ ] Add matchup analysis
  - [ ] Add filters
  - [ ] Add export functionality

#### DASH-033: Leaders Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/leaders`
- **Description:** Enhance leaders page with more categories and features
- **Acceptance Criteria:**
  - [ ] Add more leader categories (WAR, xG, CF%, etc.)
  - [ ] Add player photos
  - [ ] Add filters
  - [ ] Add export functionality

#### DASH-034: Analytics Overview Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/overview`
- **Description:** Enhance analytics overview with widgets and quick links
- **Acceptance Criteria:**
  - [ ] Add league summary cards
  - [ ] Add recent games widget
  - [ ] Add analytics tools grid (from wireframes)
  - [ ] Add quick links to all analytics pages

#### DASH-035: Analytics Statistics Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/statistics`
- **Description:** Enhance statistics page with comprehensive filters and tables
- **Acceptance Criteria:**
  - [ ] Add comprehensive stats tables with filters (from wireframes)
  - [ ] Add column selection
  - [ ] Add export functionality
  - [ ] Add advanced filtering (position, age, draft year, etc.)

#### DASH-036: Analytics Trends Page Implementation
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/trends`
- **Description:** Implement trends page (currently shows "Coming Soon")
- **Acceptance Criteria:**
  - [ ] Implement team statistics trends
  - [ ] Add goals per game trends
  - [ ] Add player scoring trends
  - [ ] Add multi-season comparison
  - [ ] Add export functionality

#### DASH-037: Analytics Teams Comparison Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/teams`
- **Description:** Enhance team comparison with quadrant charts
- **Acceptance Criteria:**
  - [ ] Add quadrant scatter plots
  - [ ] Add radar chart comparison
  - [ ] Add export functionality

#### DASH-038: Analytics Shifts Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/shifts`
- **Description:** Enhance shift viewer with timeline visualization
- **Acceptance Criteria:**
  - [ ] Add shift timeline visualization (from wireframes)
  - [ ] Add line combination grouping
  - [ ] Add shift quality metrics
  - [ ] Add export functionality

#### DASH-039: Analytics xG Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/analytics/xg`
- **Description:** Enhance xG page with timeline and flurry analysis
- **Acceptance Criteria:**
  - [ ] Add xG timeline (game flow) (from wireframes)
  - [ ] Add shot quality analysis
  - [ ] Add flurry-adjusted xG visualization
  - [ ] Add export functionality

#### DASH-040: Analytics WAR Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/analytics/war`
- **Description:** Enhance WAR page with component breakdown and trends
- **Acceptance Criteria:**
  - [ ] Add GAR component breakdown (from wireframes)
  - [ ] Add WAR trends over time
  - [ ] Add WAR by position visualization
  - [ ] Add export functionality

#### DASH-041: Analytics Micro Stats Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/micro-stats`
- **Description:** Enhance micro stats with interactive breakdowns
- **Acceptance Criteria:**
  - [ ] Add interactive micro stats breakdown
  - [ ] Add success rate visualizations
  - [ ] Add detailed micro stat breakdowns
  - [ ] Add export functionality

#### DASH-042: Analytics Zone Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/zone`
- **Description:** Enhance zone analytics with heatmaps and flow diagrams
- **Acceptance Criteria:**
  - [ ] Add zone time heatmaps (from wireframes)
  - [ ] Add zone entry/exit success rate visualizations
  - [ ] Add zone entry/exit flow diagrams
  - [ ] Add export functionality

#### DASH-043: Analytics Rushes Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/rushes`
- **Description:** Enhance rush analysis with visualizations
- **Acceptance Criteria:**
  - [ ] Add rush success rate visualizations
  - [ ] Add breakaway analysis
  - [ ] Add odd-man rush analysis
  - [ ] Add rush xG analysis
  - [ ] Add export functionality

#### DASH-044: Analytics Faceoffs Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/faceoffs`
- **Description:** Enhance faceoff analysis with WDBE and zone breakdowns
- **Acceptance Criteria:**
  - [ ] Add WDBE (Win/Draw/Back/Exit) faceoff analysis
  - [ ] Add faceoff win % by zone visualization
  - [ ] Add faceoff outcomes breakdown
  - [ ] Add export functionality

#### DASH-045: Analytics Lines Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/lines`
- **Description:** Enhance line combinations with WOWY analysis
- **Acceptance Criteria:**
  - [ ] Add WOWY (With Or Without You) analysis visualization
  - [ ] Add optimal line suggestions
  - [ ] Add line chemistry scoring
  - [ ] Add export functionality

#### DASH-046: Analytics Shot Chains Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/shot-chains`
- **Description:** Enhance shot chains with sequence visualization
- **Acceptance Criteria:**
  - [ ] Add shot sequence visualization
  - [ ] Add pattern recognition
  - [ ] Add flurry detection visualization
  - [ ] Add export functionality

#### DASH-047: Tracker Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/tracker`
- **Description:** Enhance tracker page with better interface
- **Acceptance Criteria:**
  - [ ] Add game selection interface
  - [ ] Add tracking status indicators
  - [ ] Add export functionality

#### DASH-048: Tracker Videos Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/tracker/videos`
- **Description:** Enhance video management with preview and sync
- **Acceptance Criteria:**
  - [ ] Add video preview thumbnails
  - [ ] Add video player integration
  - [ ] Add video-event synchronization
  - [ ] Add export functionality

#### DASH-049: Player Matchups Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players/matchups`
- **Description:** Enhance matchups with visualizations
- **Acceptance Criteria:**
  - [ ] Add head-to-head visualization
  - [ ] Add common games analysis
  - [ ] Add export functionality

#### DASH-050: Teams Free Agents Page Enhancement
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p3`, `phase:3`
- **Path:** `/norad/teams/free-agents`
- **Description:** Enhance free agents page with valuation
- **Acceptance Criteria:**
  - [ ] Add player valuation
  - [ ] Add contract value predictions
  - [ ] Add export functionality

### New Dashboard Pages from Wireframes

#### DASH-051: Game Win Probability Chart
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/games/[gameId]` (new tab)
- **Description:** Add win probability chart showing game flow (from wireframes)
- **Acceptance Criteria:**
  - [ ] Win probability line chart over game time
  - [ ] Goal markers on timeline
  - [ ] Power play indicators
  - [ ] Period breaks
  - [ ] Interactive tooltips
- **Data Source:** `fact_events`, calculated win probability

#### DASH-052: Game Cumulative Charts (Corsi/xG Flow)
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/games/[gameId]` (new tab)
- **Description:** Add cumulative Corsi and xG flow charts (from wireframes)
- **Acceptance Criteria:**
  - [ ] Cumulative shot attempts chart
  - [ ] Cumulative xG chart
  - [ ] Period breaks
  - [ ] Goal markers
  - [ ] Power play indicators
  - [ ] Score adjustment toggle
- **Data Source:** `fact_events`, `fact_shot_xy`

#### DASH-053: Game Skater Quadrant Charts
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/games/[gameId]` (new tab)
- **Description:** Add quadrant scatter plots for skaters (CF% vs xGF%) (from wireframes)
- **Acceptance Criteria:**
  - [ ] Quadrant scatter plot (CF/CA per 60)
  - [ ] Quadrant scatter plot (xGF/xGA per 60)
  - [ ] TOI indicated by dot size
  - [ ] Team coloring
  - [ ] Interactive tooltips
- **Data Source:** `fact_player_game_stats`

#### DASH-054: Game Player Tables (Enhanced Box Score)
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/games/[gameId]` (enhance existing)
- **Description:** Enhance box score with advanced metrics (from wireframes)
- **Acceptance Criteria:**
  - [ ] Add ISF, iFF, ICF, ixG columns
  - [ ] Add Sh%, FSh% columns
  - [ ] Add iSCF, iHDCF columns
  - [ ] Add iBLK, iHA columns
  - [ ] Add GIVE, TAKE columns
  - [ ] Add PENT, PEND columns
  - [ ] Add FO% column
- **Data Source:** `fact_player_game_stats`

#### DASH-055: Player Shot Chart with Density Heatmap
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/players/[playerId]` (new tab or enhance existing)
- **Description:** Add shot density heatmap overlay (from wireframes)
- **Acceptance Criteria:**
  - [ ] Shot location map with markers
  - [ ] Density heatmap overlay toggle
  - [ ] Zone breakdown (High/Medium/Low danger)
  - [ ] Shot stats sidebar
  - [ ] Filters (season, strength, shot type)
- **Data Source:** `fact_shot_xy`

#### DASH-056: Player Z-Score Card
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/players/[playerId]` (new section in Advanced tab)
- **Description:** Add Z-score visualization vs league average (from wireframes)
- **Acceptance Criteria:**
  - [ ] Horizontal bar charts for each metric
  - [ ] Z-score values
  - [ ] League average indicator
  - [ ] Categories: General Offense, Passing, Offensive Types, Zone Entries, Zone Exits, Forechecking
- **Data Source:** `fact_player_season_stats`, league averages

#### DASH-057: Player Position Heatmap
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players/[playerId]` (new tab)
- **Description:** Add player position heatmap showing time in each zone (from wireframes)
- **Acceptance Criteria:**
  - [ ] Zone-based heatmap (O-zone, N-zone, D-zone)
  - [ ] Time in zone percentages
  - [ ] Filters (season, strength, game type)
- **Data Source:** `fact_tracking` (if available), `fact_shifts`

#### DASH-058: Player Career Dashboard View
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/players/[playerId]` (enhance Career tab)
- **Description:** Add comprehensive career dashboard (from wireframes)
- **Acceptance Criteria:**
  - [ ] Season-by-season breakdown table
  - [ ] Career totals
  - [ ] Era-adjusted stats
  - [ ] Career trajectory chart
  - [ ] Milestone tracking
- **Data Source:** `fact_player_season_stats`, `fact_player_career_stats`

#### DASH-059: Team Passing Grid Matrix
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/teams/[teamId]` (new section in Analytics tab)
- **Description:** Add passing connection matrix (from wireframes)
- **Acceptance Criteria:**
  - [ ] Player-to-player passing grid
  - [ ] Color-coded by pass count
  - [ ] Interactive tooltips
  - [ ] Filters (game, season, strength)
- **Data Source:** `fact_events` (Pass events)

#### DASH-060: Team Presence & Importance Charts
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/teams/[teamId]` (new section in Analytics tab)
- **Description:** Add presence and importance visualization by position group (from wireframes)
- **Acceptance Criteria:**
  - [ ] Bar charts by position group (Forwards, Defense, Goalies)
  - [ ] Power play presence
  - [ ] Penalty kill presence
  - [ ] Bar height = ice time (presence)
  - [ ] Bar color intensity = impact (importance)
- **Data Source:** `fact_shifts`, `fact_player_game_stats`

#### DASH-061: Team Line Combinations Analysis
- **Labels:** `type:enhancement`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/teams/[teamId]` (enhance Lines tab)
- **Description:** Enhance line combinations with WOWY analysis (from wireframes)
- **Acceptance Criteria:**
  - [ ] Line performance cards
  - [ ] WOWY (With Or Without You) analysis
  - [ ] Optimal line suggestions
  - [ ] Line chemistry scoring
  - [ ] Visual line combination display
- **Data Source:** `fact_line_combos`, `fact_wowy`

#### DASH-062: Advanced Stats Leaderboard Table
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:3`
- **Path:** `/norad/analytics/statistics` (enhance existing)
- **Description:** Add comprehensive stats table with advanced filtering (from wireframes)
- **Acceptance Criteria:**
  - [ ] Multi-level filters (team, position, season, age, draft year, min TOI)
  - [ ] Column selection
  - [ ] Sortable columns
  - [ ] Search functionality
  - [ ] Pagination
  - [ ] Export functionality
- **Data Source:** `fact_player_season_stats`, `fact_goalie_season_stats`

#### DASH-063: Microstat Game Score Dashboard
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/micro-stats` (new view)
- **Description:** Add microstat game score visualization by game (from wireframes)
- **Acceptance Criteria:**
  - [ ] Time series chart of microstat game score
  - [ ] Team coloring
  - [ ] Game-by-game breakdown
  - [ ] Player highlighting
  - [ ] Filters (team, player, season)
- **Data Source:** `fact_player_micro_stats`

#### DASH-064: Zone Entry/Exit Flow Diagrams
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/zone` (new section)
- **Description:** Add zone entry/exit flow visualization (from wireframes)
- **Acceptance Criteria:**
  - [ ] Flow diagrams showing entry/exit patterns
  - [ ] Success rate visualization
  - [ ] Entry/exit type breakdown
  - [ ] Team comparison
- **Data Source:** `fact_zone_entries`, `fact_zone_exits`

#### DASH-065: Shot Danger Breakdown Dashboard
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/analytics/xg` (new section)
- **Description:** Add shot danger breakdown visualization (from wireframes)
- **Acceptance Criteria:**
  - [ ] High/Medium/Low danger breakdown
  - [ ] xG by danger zone
  - [ ] Team comparison
  - [ ] Player comparison
- **Data Source:** `fact_shot_xy`, `fact_events`

#### DASH-066: Momentum Chart
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:3`
- **Path:** `/norad/games/[gameId]` (new section)
- **Description:** Add momentum chart showing game flow (from wireframes)
- **Acceptance Criteria:**
  - [ ] Rolling 5-minute Corsi chart
  - [ ] Momentum score visualization
  - [ ] Goal markers
  - [ ] Period breaks
- **Data Source:** `fact_events`, calculated momentum

---

## Phase 4: Portal Development

**Status:** [PLANNED] PLANNED
**Timeline:** Weeks 13-16
**Objective:** Complete portal API integration, add game management, data browser

### Issues

#### PORT-001: Connect ETL trigger button to API
- **Labels:** `type:feature`, `area:portal`, `priority:p0`, `phase:4`
- **Description:** Replace placeholder ETL trigger with real API call
- **Acceptance Criteria:**
  - [ ] Button calls `/api/etl/run` endpoint
  - [ ] Handles authentication
  - [ ] Shows loading state
  - [ ] Handles errors gracefully

#### PORT-002: Implement ETL status polling
- **Labels:** `type:feature`, `area:portal`, `priority:p0`, `phase:4`
- **Depends On:** PORT-001
- **Description:** Poll API for ETL run status updates
- **Acceptance Criteria:**
  - [ ] Poll every 2 seconds during run
  - [ ] Display current phase
  - [ ] Stop polling on completion/error

#### PORT-003: Add ETL progress bar
- **Labels:** `type:feature`, `area:portal`, `priority:p1`, `phase:4`
- **Depends On:** PORT-002
- **Description:** Visual progress indicator for ETL runs
- **Acceptance Criteria:**
  - [ ] Progress bar component
  - [ ] Percentage complete
  - [ ] Estimated time remaining
  - [ ] Phase indicators

#### PORT-004: Connect upload to Supabase API
- **Labels:** `type:feature`, `area:portal`, `priority:p1`, `phase:4`
- **Description:** Implement file upload to Supabase storage
- **Acceptance Criteria:**
  - [ ] Upload Excel/CSV files
  - [ ] Validate file format
  - [ ] Store in Supabase storage
  - [ ] Update game records

#### PORT-005: Add upload progress tracking
- **Labels:** `type:feature`, `area:portal`, `priority:p1`, `phase:4`
- **Depends On:** PORT-004
- **Description:** Show upload progress to user
- **Acceptance Criteria:**
  - [ ] Progress bar during upload
  - [ ] File size display
  - [ ] Cancel upload option

#### PORT-006: Create game list endpoint
- **Labels:** `type:feature`, `area:api`, `priority:p1`, `phase:4`
- **Description:** API endpoint to list all games
- **Acceptance Criteria:**
  - [ ] `GET /api/games` endpoint
  - [ ] Pagination support
  - [ ] Filter by season, team, date
  - [ ] Sort options

#### PORT-007: Display game list in portal
- **Labels:** `type:feature`, `area:portal`, `priority:p1`, `phase:4`
- **Depends On:** PORT-006
- **Description:** Show games in portal UI
- **Acceptance Criteria:**
  - [ ] Table with game data
  - [ ] Pagination controls
  - [ ] Click to view details

#### PORT-008: Add game filters and search
- **Labels:** `type:feature`, `area:portal`, `priority:p2`, `phase:4`
- **Depends On:** PORT-007
- **Description:** Filter and search game list
- **Acceptance Criteria:**
  - [ ] Filter by team
  - [ ] Filter by date range
  - [ ] Search by opponent
  - [ ] Filter by processing status

#### PORT-009: Create game CRUD endpoints
- **Labels:** `type:feature`, `area:api`, `priority:p1`, `phase:4`
- **Depends On:** PORT-006
- **Description:** Create, read, update, delete game records
- **Acceptance Criteria:**
  - [ ] `POST /api/games` - create
  - [ ] `GET /api/games/{id}` - read
  - [ ] `PUT /api/games/{id}` - update
  - [ ] `DELETE /api/games/{id}` - delete

#### PORT-010: Implement game creation form
- **Labels:** `type:feature`, `area:portal`, `priority:p1`, `phase:4`
- **Depends On:** PORT-009
- **Description:** Form to create new game records
- **Acceptance Criteria:**
  - [ ] Date picker
  - [ ] Team selectors
  - [ ] Score inputs
  - [ ] Validation
  - [ ] Submit to API

#### PORT-011: Implement game edit form
- **Labels:** `type:feature`, `area:portal`, `priority:p1`, `phase:4`
- **Depends On:** PORT-009
- **Description:** Form to edit existing game records
- **Acceptance Criteria:**
  - [ ] Pre-populated fields
  - [ ] Validation
  - [ ] Save changes
  - [ ] Cancel option

#### PORT-012: Create table list component
- **Labels:** `type:feature`, `area:portal`, `priority:p2`, `phase:4`
- **Description:** Display list of all database tables
- **Acceptance Criteria:**
  - [ ] List all 139 tables
  - [ ] Show row counts
  - [ ] Show last updated
  - [ ] Group by type (dim/fact/qa)

#### PORT-013: Create data browser component
- **Labels:** `type:feature`, `area:portal`, `priority:p2`, `phase:4`
- **Depends On:** PORT-012
- **Description:** Browse table data in portal
- **Acceptance Criteria:**
  - [ ] Select table from list
  - [ ] View table data
  - [ ] Column sorting
  - [ ] Basic filtering

#### PORT-014: Add table data pagination
- **Labels:** `type:feature`, `area:portal`, `priority:p2`, `phase:4`
- **Depends On:** PORT-013
- **Description:** Paginate large tables
- **Acceptance Criteria:**
  - [ ] Page size selector
  - [ ] Page navigation
  - [ ] Row count display

#### PORT-015: Create settings page
- **Labels:** `type:feature`, `area:portal`, `priority:p2`, `phase:4`
- **Description:** Portal settings and configuration
- **Acceptance Criteria:**
  - [ ] API URL configuration
  - [ ] Default filters
  - [ ] Theme preference
  - [ ] Persist to localStorage

#### PORT-016: Add toast notification system
- **Labels:** `type:feature`, `area:portal`, `priority:p2`, `phase:4`
- **Description:** User feedback notifications
- **Acceptance Criteria:**
  - [ ] Success toasts
  - [ ] Error toasts
  - [ ] Auto-dismiss
  - [ ] Action buttons

---

## Phase 5: Tracker Conversion

**Status:** [PLANNED] PLANNED
**Timeline:** Weeks 17-24
**Objective:** Convert HTML tracker to Rust/Next.js, maintain feature parity

### Issues

#### TRACK-001: Initialize Rust backend project
- **Labels:** `type:feature`, `area:tracker`, `priority:p1`, `phase:5`
- **Description:** Set up Rust project with Actix web framework
- **Acceptance Criteria:**
  - [ ] Cargo project initialized
  - [ ] Actix web framework configured
  - [ ] SQLx database connection
  - [ ] Basic health endpoint

#### TRACK-002: Create Event data model (Rust)
- **Labels:** `type:feature`, `area:tracker`, `priority:p1`, `phase:5`
- **Depends On:** TRACK-001
- **Description:** Define Event struct matching tracker schema
- **Acceptance Criteria:**
  - [ ] Event struct defined
  - [ ] All event types supported
  - [ ] Serialization/deserialization
  - [ ] Database mapping

#### TRACK-003: Create Shift data model (Rust)
- **Labels:** `type:feature`, `area:tracker`, `priority:p1`, `phase:5`
- **Depends On:** TRACK-001
- **Description:** Define Shift struct for player shifts
- **Acceptance Criteria:**
  - [ ] Shift struct defined
  - [ ] Player associations
  - [ ] Duration calculation
  - [ ] Database mapping

#### TRACK-004: Implement event tracking API
- **Labels:** `type:feature`, `area:tracker`, `priority:p1`, `phase:5`
- **Depends On:** TRACK-002
- **Description:** REST API for event CRUD operations
- **Acceptance Criteria:**
  - [ ] `POST /api/events` - create
  - [ ] `GET /api/events` - list with filters
  - [ ] `PUT /api/events/{id}` - update
  - [ ] `DELETE /api/events/{id}` - delete
  - [ ] Validation middleware

#### TRACK-005: Implement shift tracking API
- **Labels:** `type:feature`, `area:tracker`, `priority:p1`, `phase:5`
- **Depends On:** TRACK-003
- **Description:** REST API for shift CRUD operations
- **Acceptance Criteria:**
  - [ ] `POST /api/shifts` - create
  - [ ] `GET /api/shifts` - list with filters
  - [ ] `PUT /api/shifts/{id}` - update
  - [ ] `DELETE /api/shifts/{id}` - delete

#### TRACK-006: Initialize Next.js frontend project
- **Labels:** `type:feature`, `area:tracker`, `priority:p1`, `phase:5`
- **Description:** Set up Next.js project for tracker UI
- **Acceptance Criteria:**
  - [ ] Next.js 14 with App Router
  - [ ] TypeScript strict mode
  - [ ] Tailwind CSS
  - [ ] API client setup

#### TRACK-007: Create event capture UI component
- **Labels:** `type:feature`, `area:tracker`, `priority:p1`, `phase:5`
- **Depends On:** TRACK-006
- **Description:** UI for capturing game events
- **Acceptance Criteria:**
  - [ ] Event type selector
  - [ ] Player selectors
  - [ ] Keyboard shortcuts
  - [ ] Quick entry mode

#### TRACK-008: Create shift tracking UI component
- **Labels:** `type:feature`, `area:tracker`, `priority:p1`, `phase:5`
- **Depends On:** TRACK-006
- **Description:** UI for tracking player shifts
- **Acceptance Criteria:**
  - [ ] Line display
  - [ ] On/off ice toggle
  - [ ] Shift timer
  - [ ] Auto line changes

#### TRACK-009: Create rink visualization component
- **Labels:** `type:feature`, `area:tracker`, `priority:p1`, `phase:5`
- **Depends On:** TRACK-006
- **Description:** Interactive rink diagram for XY positioning
- **Acceptance Criteria:**
  - [ ] SVG rink graphic
  - [ ] Click to set position
  - [ ] Zone highlighting
  - [ ] Event markers

#### TRACK-010: Feature parity testing
- **Labels:** `type:test`, `area:tracker`, `priority:p0`, `phase:5`
- **Depends On:** TRACK-004, TRACK-005, TRACK-007, TRACK-008, TRACK-009
- **Description:** Verify new tracker matches HTML tracker functionality
- **Acceptance Criteria:**
  - [ ] All event types work
  - [ ] Shift tracking works
  - [ ] Video integration works
  - [ ] XY positioning works
  - [ ] Export produces same format

#### TRACK-011: Backend performance optimization
- **Labels:** `type:perf`, `area:tracker`, `priority:p1`, `phase:5`
- **Depends On:** TRACK-010
- **Description:** Optimize Rust backend performance
- **Acceptance Criteria:**
  - [ ] Connection pooling
  - [ ] Response caching
  - [ ] Query optimization
  - [ ] < 50ms response time

#### TRACK-012: Frontend bundle optimization
- **Labels:** `type:perf`, `area:tracker`, `priority:p2`, `phase:5`
- **Depends On:** TRACK-010
- **Description:** Optimize Next.js bundle size
- **Acceptance Criteria:**
  - [ ] Code splitting
  - [ ] Tree shaking
  - [ ] < 200KB initial bundle
  - [ ] Lazy loading for heavy components

---

## Phase 6: ML/CV + Advanced Analytics

**Status:** [PLANNED] PLANNED
**Timeline:** Weeks 25-32
**Objective:** Integrate ML/CV for automated tracking, achieve analytics parity with NHL Edge/Sportlogiq

### ML/CV Infrastructure Issues

#### ML-001: Set up video processing service (FFmpeg)
- **Labels:** `type:feature`, `area:analytics`, `priority:p1`, `phase:6`
- **Description:** Infrastructure for video processing
- **Acceptance Criteria:**
  - [ ] FFmpeg container configured
  - [ ] Video format conversion
  - [ ] Frame extraction
  - [ ] Thumbnail generation

#### ML-002: Implement video upload API
- **Labels:** `type:feature`, `area:api`, `priority:p1`, `phase:6`
- **Depends On:** ML-001
- **Description:** API endpoint for video uploads
- **Acceptance Criteria:**
  - [ ] Large file upload support
  - [ ] Progress tracking
  - [ ] S3/Cloudflare storage
  - [ ] Processing queue

#### ML-003: Train goal detection model (YOLO)
- **Labels:** `type:feature`, `area:analytics`, `priority:p1`, `phase:6`
- **Depends On:** ML-001
- **Description:** Train model to detect goals in video
- **Acceptance Criteria:**
  - [ ] Training data collection
  - [ ] YOLO model training
  - [ ] > 90% accuracy
  - [ ] Inference < 100ms

#### ML-004: Integrate goal detection with tracker
- **Labels:** `type:feature`, `area:tracker`, `priority:p1`, `phase:6`
- **Depends On:** ML-003
- **Description:** Connect goal detection to tracker UI
- **Acceptance Criteria:**
  - [ ] Auto-detect goals during playback
  - [ ] Manual override option
  - [ ] Confidence score display

### Advanced Analytics Issues (P0 - Immediate)

#### ANALYTICS-001: Implement flurry-adjusted xG
- **Labels:** `type:feature`, `area:analytics`, `priority:p0`, `phase:6`
- **Description:** Group shots by possession; compute 1 - Π(1 - xG_i)
- **Acceptance Criteria:**
  - [ ] Shots grouped by possession/stoppage
  - [ ] Flurry xG computed correctly
  - [ ] Stored on shot chains/scoring chances
  - [ ] Unit tests for sequences and caps

#### ANALYTICS-002: WDBE v1 (faceoff value)
- **Labels:** `type:feature`, `area:analytics`, `priority:p0`, `phase:6`
- **Description:** Win/Draw/Back/Exit faceoff classification with value
- **Acceptance Criteria:**
  - [ ] Tag clean vs scrum
  - [ ] Approximate direction from event detail
  - [ ] Compute expected next-event value
  - [ ] Expose per player/zone
  - [ ] QA checks on sample games

#### ANALYTICS-003: Stint table & RAPM design matrix spec
- **Labels:** `type:design`, `area:analytics`, `priority:p0`, `phase:6`
- **Description:** Design specification for RAPM implementation
- **Acceptance Criteria:**
  - [ ] Derive stints from shifts/events
  - [ ] Encode players +/- in sparse matrix
  - [ ] Include zone start, score state, strength
  - [ ] Write schema and builder plan

#### ANALYTICS-004: WAR baseline update plan
- **Labels:** `type:design`, `area:analytics`, `priority:p0`, `phase:6`
- **Description:** Define WAR calculation methodology
- **Acceptance Criteria:**
  - [ ] Define replacement level (outside top 13F/7D by TOI)
  - [ ] Goals-per-win = 6
  - [ ] Outline daisy-chain priors across seasons

### Advanced Analytics Issues (P1 - Post-XY Ingestion)

#### ANALYTICS-005: Coordinate normalization + speed features
- **Labels:** `type:feature`, `area:analytics`, `priority:p1`, `phase:6`
- **Description:** Standardize XY coordinates and compute speeds
- **Acceptance Criteria:**
  - [ ] Standardize to offensive net at x=89
  - [ ] Flip per period/attacking side
  - [ ] Compute shot/puck/player speed features
  - [ ] Persist in database

#### ANALYTICS-006: GBM xG (LightGBM/XGBoost)
- **Labels:** `type:feature`, `area:analytics`, `priority:p1`, `phase:6`
- **Depends On:** ANALYTICS-005
- **Description:** Machine learning xG model
- **Acceptance Criteria:**
  - [ ] Features: distance, angle, shot type, rush, rebound, royal road, speed
  - [ ] Train LightGBM/XGBoost model
  - [ ] Calibration validation
  - [ ] Monitoring dashboard

#### ANALYTICS-007: Royal road + pre-shot movement detection
- **Labels:** `type:feature`, `area:analytics`, `priority:p1`, `phase:6`
- **Depends On:** ANALYTICS-005
- **Description:** Detect dangerous cross-ice passes
- **Acceptance Criteria:**
  - [ ] Detect y=0 crossings within 3s before shot
  - [ ] Angle-change feature
  - [ ] Tag east-west passes

#### ANALYTICS-008: Gap control metrics
- **Labels:** `type:feature`, `area:analytics`, `priority:p1`, `phase:6`
- **Depends On:** ANALYTICS-005
- **Description:** Defensive positioning metrics
- **Acceptance Criteria:**
  - [ ] Compute static/effective gap at blue line
  - [ ] Use player/puck XY + velocity
  - [ ] Correlate with entry outcomes
  - [ ] Store per defender

#### ANALYTICS-009: Entry/exit expected value models
- **Labels:** `type:feature`, `area:analytics`, `priority:p1`, `phase:6`
- **Depends On:** ANALYTICS-005
- **Description:** Value models for zone transitions
- **Acceptance Criteria:**
  - [ ] Estimate shot/goal probability uplift by entry type
  - [ ] Same for exit type/direction
  - [ ] Surface per player/team

### Advanced Analytics Issues (P2 - Model Rebuilds)

#### ANALYTICS-010: RAPM (6 components) + WAR recalculation
- **Labels:** `type:feature`, `area:analytics`, `priority:p2`, `phase:6`
- **Depends On:** ANALYTICS-003, ANALYTICS-004
- **Description:** Full RAPM implementation
- **Acceptance Criteria:**
  - [ ] Build sparse design matrix
  - [ ] RidgeCV for: EV off/def, PP off, PK def, Penalties, Finishing
  - [ ] Apply replacement level and priors
  - [ ] Recompute WAR

#### ANALYTICS-011: Shooting talent adjustment
- **Labels:** `type:feature`, `area:analytics`, `priority:p2`, `phase:6`
- **Depends On:** ANALYTICS-006
- **Description:** Bayesian adjustment for shooting skill
- **Acceptance Criteria:**
  - [ ] Bayesian shrinkage on (Goals - xG)
  - [ ] Volume prior
  - [ ] Integrate into player finishing component

#### ANALYTICS-012: xT grid model
- **Labels:** `type:feature`, `area:analytics`, `priority:p2`, `phase:6`
- **Depends On:** ANALYTICS-005
- **Description:** Expected Threat possession value model
- **Acceptance Criteria:**
  - [ ] Define 16×12 grid
  - [ ] Estimate transition matrix
  - [ ] Shot-to-goal probability per cell
  - [ ] Solve xT values
  - [ ] Credit passes/entries/exits

#### ANALYTICS-013: WDBE v2 (directional vectors)
- **Labels:** `type:feature`, `area:analytics`, `priority:p2`, `phase:6`
- **Depends On:** ANALYTICS-002, ANALYTICS-005
- **Description:** Enhanced faceoff value with XY data
- **Acceptance Criteria:**
  - [ ] Use faceoff XY to classify direction buckets
  - [ ] Compute EV from empirical next events
  - [ ] Add dashboards

#### ANALYTICS-014: Defensive microstats suite
- **Labels:** `type:feature`, `area:analytics`, `priority:p2`, `phase:6`
- **Description:** Comprehensive defensive metrics
- **Acceptance Criteria:**
  - [ ] Board/loose-puck battles
  - [ ] Pressures/retrievals
  - [ ] Lane blocks
  - [ ] Tagging rules defined
  - [ ] Data model and QA plan

### Advanced Analytics Issues (P3 - Dashboards & QA)

#### ANALYTICS-015: Dashboard surfacing of advanced layers
- **Labels:** `type:feature`, `area:dashboard`, `priority:p3`, `phase:6`
- **Depends On:** ANALYTICS-006, ANALYTICS-010, ANALYTICS-012
- **Description:** Display advanced analytics in dashboard
- **Acceptance Criteria:**
  - [ ] xG maps (flurry, royal road, shooter talent)
  - [ ] WAR/RAPM leaderboards
  - [ ] WDBE display
  - [ ] Gap control viz
  - [ ] Entry/exit value
  - [ ] xT overlays

#### ANALYTICS-016: Validation harness & monitoring
- **Labels:** `type:test`, `area:analytics`, `priority:p3`, `phase:6`
- **Depends On:** ANALYTICS-006, ANALYTICS-010
- **Description:** Ongoing validation of analytics
- **Acceptance Criteria:**
  - [ ] Reliability curves for xG
  - [ ] Cross-validation for RAPM
  - [ ] Stability dashboards
  - [ ] Drift alerts
  - [ ] Sample replay tests

---

## Phase 7: Multi-Tenancy & Scalability

**Status:** [PLANNED] PLANNED
**Timeline:** Weeks 33-40
**Objective:** Redesign schema for multi-tenant, implement authentication, ensure scalability

### Issues

#### MT-001: Design multi-tenant schema strategy
- **Labels:** `type:design`, `area:data`, `priority:p0`, `phase:7`
- **Description:** Architectural design for tenant isolation
- **Acceptance Criteria:**
  - [ ] Tenant isolation strategy (shared schema with RLS)
  - [ ] tenant_id column design
  - [ ] RLS policy templates
  - [ ] Migration approach

#### MT-002: Add tenant_id to all tables
- **Labels:** `type:feature`, `area:data`, `priority:p0`, `phase:7`
- **Depends On:** MT-001
- **Description:** Add tenant identification to schema
- **Acceptance Criteria:**
  - [ ] tenant_id column on all 139 tables
  - [ ] Foreign keys updated
  - [ ] Indexes added
  - [ ] Default tenant for existing data

#### MT-003: Implement Row-Level Security (RLS)
- **Labels:** `type:feature`, `area:data`, `priority:p0`, `phase:7`
- **Depends On:** MT-002
- **Description:** Supabase RLS for data isolation
- **Acceptance Criteria:**
  - [ ] RLS policies on all tables
  - [ ] Test isolation between tenants
  - [ ] Service role bypass for ETL

#### MT-004: Create migration scripts
- **Labels:** `type:chore`, `area:data`, `priority:p1`, `phase:7`
- **Depends On:** MT-002
- **Description:** Scripts to migrate existing data
- **Acceptance Criteria:**
  - [ ] Migration tested on dev
  - [ ] Rollback capability
  - [ ] Data integrity verification

#### MT-005: Set up Supabase Auth
- **Labels:** `type:feature`, `area:infra`, `priority:p0`, `phase:7`
- **Description:** User authentication with Supabase
- **Acceptance Criteria:**
  - [ ] Email/password auth
  - [ ] OAuth providers (Google, GitHub)
  - [ ] JWT token handling
  - [ ] Session management

#### MT-006: Create login/signup pages
- **Labels:** `type:feature`, `area:dashboard`, `priority:p0`, `phase:7`
- **Depends On:** MT-005
- **Description:** Authentication UI
- **Acceptance Criteria:**
  - [ ] Login page
  - [ ] Signup page
  - [ ] Password reset
  - [ ] Email verification

#### MT-007: Implement RBAC middleware
- **Labels:** `type:feature`, `area:api`, `priority:p1`, `phase:7`
- **Depends On:** MT-005
- **Description:** Role-based access control
- **Acceptance Criteria:**
  - [ ] Role definitions (admin, coach, player, viewer)
  - [ ] Permission checks
  - [ ] Protected endpoints
  - [ ] Role assignment

#### MT-008: Add indexes for tenant_id queries
- **Labels:** `type:perf`, `area:data`, `priority:p1`, `phase:7`
- **Depends On:** MT-002
- **Description:** Optimize multi-tenant query performance
- **Acceptance Criteria:**
  - [ ] Composite indexes (tenant_id + common filters)
  - [ ] Query plan analysis
  - [ ] Benchmark results

#### MT-009: Set up Redis cache
- **Labels:** `type:feature`, `area:infra`, `priority:p1`, `phase:7`
- **Description:** Caching layer for performance
- **Acceptance Criteria:**
  - [ ] Redis instance configured
  - [ ] Cache player stats queries
  - [ ] Cache team stats queries
  - [ ] Cache invalidation strategy

#### MT-010: Set up Prometheus metrics
- **Labels:** `type:feature`, `area:infra`, `priority:p2`, `phase:7`
- **Description:** Application monitoring metrics
- **Acceptance Criteria:**
  - [ ] Prometheus configured
  - [ ] Custom application metrics
  - [ ] Database metrics
  - [ ] API response time metrics

#### MT-011: Set up Grafana dashboards
- **Labels:** `type:feature`, `area:infra`, `priority:p2`, `phase:7`
- **Depends On:** MT-010
- **Description:** Monitoring visualization
- **Acceptance Criteria:**
  - [ ] Application dashboard
  - [ ] Database dashboard
  - [ ] API performance dashboard
  - [ ] Alert thresholds

#### MT-012: Integrate Sentry for error tracking
- **Labels:** `type:feature`, `area:infra`, `priority:p2`, `phase:7`
- **Description:** Error monitoring and alerting
- **Acceptance Criteria:**
  - [ ] Sentry SDK integrated
  - [ ] Dashboard configured
  - [ ] API errors captured
  - [ ] Alert notifications

---

## Phase 8: Commercial Launch

**Status:** [PLANNED] PLANNED
**Timeline:** Weeks 41-48
**Objective:** Payment integration, subscription management, onboarding, marketing

### Issues

#### COMM-001: Integrate Stripe payments
- **Labels:** `type:feature`, `area:commercial`, `priority:p0`, `phase:8`
- **Description:** Payment processing with Stripe
- **Acceptance Criteria:**
  - [ ] Stripe API integrated
  - [ ] Payment methods supported
  - [ ] Webhook handling
  - [ ] Test mode verified

#### COMM-002: Create subscription service
- **Labels:** `type:feature`, `area:commercial`, `priority:p0`, `phase:8`
- **Depends On:** COMM-001
- **Description:** Subscription management backend
- **Acceptance Criteria:**
  - [ ] Plan definitions
  - [ ] Status tracking
  - [ ] Renewal handling
  - [ ] Cancellation flow

#### COMM-003: Implement checkout flow
- **Labels:** `type:feature`, `area:dashboard`, `priority:p0`, `phase:8`
- **Depends On:** COMM-001
- **Description:** User-facing payment flow
- **Acceptance Criteria:**
  - [ ] Plan selection page
  - [ ] Stripe checkout integration
  - [ ] Success/failure handling
  - [ ] Receipt display

#### COMM-004: Create onboarding wizard
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:8`
- **Description:** New user onboarding flow
- **Acceptance Criteria:**
  - [ ] Multi-step wizard
  - [ ] Progress indicator
  - [ ] Skip option
  - [ ] Completion tracking

#### COMM-005: Add team creation step
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:8`
- **Depends On:** COMM-004
- **Description:** Team setup in onboarding
- **Acceptance Criteria:**
  - [ ] Team name/details
  - [ ] Logo upload
  - [ ] Season configuration
  - [ ] Roster import

#### COMM-006: Create user invitation system
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:8`
- **Depends On:** MT-006
- **Description:** Invite users to team
- **Acceptance Criteria:**
  - [ ] Email invitations
  - [ ] Invite links
  - [ ] Role assignment
  - [ ] Expiration handling

#### COMM-007: Create marketing landing page
- **Labels:** `type:feature`, `area:commercial`, `priority:p1`, `phase:8`
- **Description:** Public marketing website
- **Acceptance Criteria:**
  - [ ] Hero section
  - [ ] Feature highlights
  - [ ] Social proof
  - [ ] CTA buttons

#### COMM-008: Create pricing page
- **Labels:** `type:feature`, `area:commercial`, `priority:p1`, `phase:8`
- **Depends On:** COMM-007
- **Description:** Public pricing display
- **Acceptance Criteria:**
  - [ ] Plan comparison table
  - [ ] Feature matrix
  - [ ] FAQ section
  - [ ] Sign up CTAs

#### COMM-009: Complete end-to-end testing
- **Labels:** `type:test`, `area:commercial`, `priority:p0`, `phase:8`
- **Description:** Full platform testing
- **Acceptance Criteria:**
  - [ ] User journeys tested
  - [ ] Payment flows tested
  - [ ] Edge cases handled
  - [ ] Cross-browser testing

#### COMM-010: Perform load testing (100+ teams)
- **Labels:** `type:test`, `area:infra`, `priority:p1`, `phase:8`
- **Depends On:** MT-008, MT-009
- **Description:** Performance at scale
- **Acceptance Criteria:**
  - [ ] Simulate 100+ concurrent teams
  - [ ] Response times < 200ms
  - [ ] No errors under load
  - [ ] Auto-scaling verified

#### COMM-011: Complete user documentation
- **Labels:** `type:docs`, `area:commercial`, `priority:p1`, `phase:8`
- **Description:** End-user documentation
- **Acceptance Criteria:**
  - [ ] Getting started guide
  - [ ] Feature documentation
  - [ ] Video tutorials
  - [ ] FAQ

#### COMM-012: Set up customer support system
- **Labels:** `type:feature`, `area:commercial`, `priority:p1`, `phase:8`
- **Description:** Support infrastructure
- **Acceptance Criteria:**
  - [ ] Help center/knowledge base
  - [ ] Contact form
  - [ ] Email support setup
  - [ ] SLA defined

---

## Phase 9-12: AI Coaching & Analysis

**Status:** [PLANNED] PLANNED
**Timeline:** Weeks 33-48
**Objective:** Transform BenchSight into an intelligent coaching assistant with AI-powered video analysis, natural language queries, and specialized coaching modes

**Related PRD:** [AI_COACHING_FEATURES.md](../prds/AI_COACHING_FEATURES.md)

### Phase 9: AI Coach Foundation (Weeks 33-36)

#### AI-COACH-001: Video upload and storage infrastructure
- **Labels:** `type:feature`, `area:api`, `priority:p0`, `phase:9`
- **Description:** Infrastructure for video upload, storage, and management
- **Acceptance Criteria:**
  - [ ] Cloudflare R2 or AWS S3 bucket configured
  - [ ] Video upload API endpoint (POST /api/video/upload)
  - [ ] Large file upload support (chunked uploads)
  - [ ] Video metadata storage in database
  - [ ] Video format validation
  - [ ] Progress tracking for uploads

#### AI-COACH-002: Video player component with AI annotations
- **Labels:** `type:feature`, `area:dashboard`, `priority:p0`, `phase:9`
- **Depends On:** AI-COACH-001
- **Description:** Video player with AI-generated annotations and event markers
- **Acceptance Criteria:**
  - [ ] Video player component (React/Next.js)
  - [ ] YouTube and local video support
  - [ ] AI annotation overlay system
  - [ ] Event timestamp markers
  - [ ] Play/pause/skip controls
  - [ ] Annotation display on timeline

#### AI-COACH-003: Basic Q&A system (LLM integration)
- **Labels:** `type:feature`, `area:api`, `priority:p0`, `phase:9`
- **Description:** Basic question-answering system using LLM (OpenAI/Anthropic)
- **Acceptance Criteria:**
  - [ ] LLM integration (OpenAI GPT-4 or Anthropic Claude)
  - [ ] Q&A API endpoint (POST /api/ai/ask)
  - [ ] Context management (game data, player stats)
  - [ ] Response generation with citations
  - [ ] Error handling and rate limiting
  - [ ] Cost tracking and optimization

#### AI-COACH-004: Video-event synchronization
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:9`
- **Depends On:** AI-COACH-002
- **Description:** Sync video playback with game events from tracking data
- **Acceptance Criteria:**
  - [ ] Event-to-video timestamp mapping
  - [ ] Auto-jump to event on click
  - [ ] Event highlighting during playback
  - [ ] Shift boundaries marked in video
  - [ ] Goal/penalty/shot markers

### Phase 10: Natural Language Queries (Weeks 37-40)

#### AI-QUERY-001: Natural language understanding system
- **Labels:** `type:feature`, `area:api`, `priority:p0`, `phase:10`
- **Description:** NLU system to understand user queries and convert to database queries
- **Acceptance Criteria:**
  - [ ] Query intent classification
  - [ ] Entity extraction (player names, teams, dates)
  - [ ] Query type detection (statistical, comparative, analytical)
  - [ ] Query validation and error handling
  - [ ] Support for complex multi-part queries

#### AI-QUERY-002: SQL query generation from natural language
- **Labels:** `type:feature`, `area:api`, `priority:p0`, `phase:10`
- **Depends On:** AI-QUERY-001
- **Description:** Generate SQL queries from natural language using LLM
- **Acceptance Criteria:**
  - [ ] SQL generation from NL queries
  - [ ] Query optimization and validation
  - [ ] Support for aggregations, filters, joins
  - [ ] Query safety checks (prevent SQL injection)
  - [ ] Query caching for common patterns

#### AI-QUERY-003: Response visualization engine
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:10`
- **Depends On:** AI-QUERY-002
- **Description:** Automatically generate visualizations for query results
- **Acceptance Criteria:**
  - [ ] Chart type selection (bar, line, scatter, etc.)
  - [ ] Data visualization generation
  - [ ] Interactive charts (Recharts integration)
  - [ ] Export options (PNG, CSV)
  - [ ] Responsive design

#### AI-QUERY-004: Query caching and optimization
- **Labels:** `type:enhancement`, `area:api`, `priority:p2`, `phase:10`
- **Depends On:** AI-QUERY-002
- **Description:** Cache query results and optimize performance
- **Acceptance Criteria:**
  - [ ] Redis caching for query results
  - [ ] Cache invalidation strategy
  - [ ] Query result deduplication
  - [ ] Performance monitoring
  - [ ] Cost tracking for LLM calls

### Phase 11: Coach Modes (Weeks 41-44)

#### COACH-001: Game plan generation engine
- **Labels:** `type:feature`, `area:analytics`, `priority:p1`, `phase:11`
- **Description:** AI-powered game plan generator based on opponent analysis
- **Acceptance Criteria:**
  - [ ] Opponent analysis (strengths/weaknesses)
  - [ ] Game plan generation (offensive/defensive strategies)
  - [ ] Lineup optimization suggestions
  - [ ] Special teams recommendations
  - [ ] Export game plan as PDF/document

#### COACH-002: Practice drill database and recommendations
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:11`
- **Description:** Practice drill library with AI recommendations based on game performance
- **Acceptance Criteria:**
  - [ ] Drill database (100+ drills)
  - [ ] Drill categorization (offensive, defensive, special teams)
  - [ ] AI recommendations based on game data
  - [ ] Practice plan generation
  - [ ] Drill effectiveness tracking

#### COACH-003: Scout mode player comparison tools
- **Labels:** `type:feature`, `area:dashboard`, `priority:p1`, `phase:11`
- **Description:** Advanced player comparison and scouting tools
- **Acceptance Criteria:**
  - [ ] Side-by-side player comparison
  - [ ] Similar player finder (ML-based)
  - [ ] Scouting report generation
  - [ ] Player projection analysis
  - [ ] Export scouting reports

#### COACH-004: Game prep content generation
- **Labels:** `type:feature`, `area:dashboard`, `priority:p2`, `phase:11`
- **Description:** AI-generated game preparation content for coaches and players
- **Acceptance Criteria:**
  - [ ] Game preview generation
  - [ ] Opponent scouting summary
  - [ ] Player-specific focus areas
  - [ ] Team talking points
  - [ ] Pre-game motivation insights

### Phase 12: GM Mode & Advanced Features (Weeks 45-48)

#### GM-001: Team builder optimization engine
- **Labels:** `type:feature`, `area:analytics`, `priority:p1`, `phase:12`
- **Description:** AI-powered team building and roster optimization
- **Acceptance Criteria:**
  - [ ] Roster analysis (strengths/weaknesses)
  - [ ] Position depth analysis
  - [ ] Optimal lineup suggestions
  - [ ] Chemistry analysis
  - [ ] Salary cap optimization

#### GM-002: Player valuation models
- **Labels:** `type:feature`, `area:analytics`, `priority:p1`, `phase:12`
- **Description:** Advanced player valuation using WAR/GAR and market analysis
- **Acceptance Criteria:**
  - [ ] Player value calculations (WAR-based)
  - [ ] Contract value analysis
  - [ ] Performance vs salary comparisons
  - [ ] Trade value estimates
  - [ ] Free agent value projections

#### GM-003: Trade evaluation system
- **Labels:** `type:feature`, `area:analytics`, `priority:p2`, `phase:12`
- **Description:** AI-powered trade analysis and evaluation
- **Acceptance Criteria:**
  - [ ] Trade proposal evaluation
  - [ ] Value comparison (WAR, salary, age)
  - [ ] Trade impact projections
  - [ ] Trade history analysis
  - [ ] Trade recommendation engine

#### GM-004: Draft analysis tools
- **Labels:** `type:feature`, `area:analytics`, `priority:p2`, `phase:12`
- **Description:** Draft pick value and prospect evaluation tools
- **Acceptance Criteria:**
  - [ ] Draft pick value calculator
  - [ ] Prospect rankings
  - [ ] Draft strategy recommendations
  - [ ] Historical draft analysis
  - [ ] Prospect projection models

---

## Foundation & Workflow

**Status:** [ONGOING] ONGOING
**Description:** Infrastructure and workflow improvements that can be done anytime

### Issues

#### FW-001: Define issue and PR templates
- **Labels:** `type:docs`, `area:workflow`, `priority:p1`
- **Description:** Standardize GitHub templates
- **Acceptance Criteria:**
  - [ ] Issue template with type/area
  - [ ] PR template with checklist
  - [ ] Bug report template
  - [ ] Feature request template

#### FW-002: Codify project workflow (Cursor + Claude + CodeRabbit)
- **Labels:** `type:docs`, `area:workflow`, `priority:p1`
- **Description:** Document development workflow
- **Acceptance Criteria:**
  - [ ] Agent usage guidelines
  - [ ] Subagent review process
  - [ ] Skills documentation
  - [ ] PR review workflow

#### FW-003: Establish docs update policy
- **Labels:** `type:docs`, `area:workflow`, `priority:p1`
- **Description:** Rules for documentation updates
- **Acceptance Criteria:**
  - [ ] When to update PROJECT_STATUS
  - [ ] When to update MASTER_INDEX
  - [ ] Component docs requirements

#### FW-004: Docs link check automation
- **Labels:** `type:chore`, `area:docs`, `priority:p1`
- **Description:** Automated link validation
- **Acceptance Criteria:**
  - [ ] `scripts/docs-check.sh` in CI
  - [ ] Pre-commit hook option
  - [ ] Report broken links

#### FW-005: Pre-commit hooks baseline
- **Labels:** `type:chore`, `area:workflow`, `priority:p1`
- **Description:** Consistent code quality checks
- **Acceptance Criteria:**
  - [ ] Python formatting (black/ruff)
  - [ ] TypeScript linting
  - [ ] Commit message validation

#### FW-006: CodeRabbit configuration tuning
- **Labels:** `type:chore`, `area:workflow`, `priority:p2`
- **Description:** Optimize AI code review
- **Acceptance Criteria:**
  - [ ] Calibrate .coderabbit.yaml
  - [ ] Project-specific rules
  - [ ] Ignore patterns

#### FW-007: Supabase dev/prod environment separation
- **Labels:** `type:infra`, `area:infra`, `priority:p1`
- **Description:** Environment isolation
- **Acceptance Criteria:**
  - [ ] Separate Supabase projects
  - [ ] RLS policy parity
  - [ ] Migration workflow

#### FW-008: Vercel dev/prod projects and envs
- **Labels:** `type:infra`, `area:infra`, `priority:p1`
- **Description:** Deployment environment setup
- **Acceptance Criteria:**
  - [ ] Environment variables locked
  - [ ] Preview deployment strategy
  - [ ] Release guardrails

#### FW-009: Multi-tenant architecture plan
- **Labels:** `type:design`, `area:data`, `priority:p0`
- **Description:** Foundation for multi-tenancy (pre-Phase 7)
- **Acceptance Criteria:**
  - [ ] Data isolation design
  - [ ] RLS policy plan
  - [ ] Migration approach

#### FW-010: Pilot case study buildout
- **Labels:** `type:docs`, `area:commercial`, `priority:p1`
- **Description:** Customer success documentation
- **Acceptance Criteria:**
  - [ ] Template populated
  - [ ] Metrics defined
  - [ ] Story drafted

#### FW-011: Pricing validation plan
- **Labels:** `type:research`, `area:commercial`, `priority:p2`
- **Description:** Pricing strategy research
- **Acceptance Criteria:**
  - [ ] Pilot pricing experiments
  - [ ] Success metrics
  - [ ] Competitor analysis

#### FW-012: Update Tracker docs from v23.5 to v27.0
- **Labels:** `type:docs`, `area:tracker`, `priority:p1`
- **Description:** Documentation version update
- **Acceptance Criteria:**
  - [ ] TRACKER_REFERENCE.md updated
  - [ ] Function inventory verified
  - [ ] New features documented

#### FW-013: Fix Gantt chart dates (2025 → 2026)
- **Labels:** `type:docs`, `area:docs`, `priority:p1`
- **Description:** Correct timeline dates
- **Acceptance Criteria:**
  - [ ] MASTER_ROADMAP.md dates fixed
  - [ ] roadmap-visuals.md dates fixed

---

## Quick Reference: Issue Counts by Phase

| Phase | Status | Issues | Priority Breakdown |
|-------|--------|--------|-------------------|
| Phase 2: ETL | [IN_PROGRESS] CURRENT | 40 | P0:10, P1:22, P2:7, P3:1 |
| Phase 3: Dashboard | [PLANNED] PLANNED | 66 | P0:0, P1:18, P2:44, P3:4 |
| Phase 4: Portal | [PLANNED] PLANNED | 16 | P0:2, P1:9, P2:5 |
| Phase 5: Tracker | [PLANNED] PLANNED | 12 | P0:1, P1:9, P2:2 |
| Phase 6: ML/CV | [PLANNED] PLANNED | 20 | P0:4, P1:8, P2:6, P3:2 |
| Phase 7: Multi-Tenant | [PLANNED] PLANNED | 12 | P0:3, P1:5, P2:4 |
| Phase 8: Commercial | [PLANNED] PLANNED | 12 | P0:3, P1:7, P2:2 |
| Phase 9-12: AI Coaching | [PLANNED] PLANNED | 20 | P0:4, P1:10, P2:6 |
| Foundation | [ONGOING] ONGOING | 13 | P0:1, P1:10, P2:2 |
| **Total** | - | **161** | - |

---

## Creating Issues in GitHub

To create these issues in GitHub:

1. **Manual Creation:** Copy each issue's title, labels, description, and acceptance criteria into GitHub's issue form.

2. **Bulk Import:** Use the GitHub CLI:
   ```bash
   gh issue create --title "ETL-001: Modularize base_etl.py" \
     --label "type:refactor,area:etl,priority:p0,phase:2" \
     --body "Description and acceptance criteria here"
   ```

3. **Project Board:** Create a GitHub Project board with columns for each phase or status (Backlog, In Progress, Review, Done).

---

*Last Updated: 2026-01-22*
