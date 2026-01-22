# BenchSight GitHub Issues Backlog

**Comprehensive phased backlog covering the entire project roadmap from MVP to commercial launch.**

Last Updated: 2026-01-21
Total Issues: ~113
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
10. [Foundation & Workflow](#foundation--workflow) (13 issues)

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
| `phase:1` | Foundation & Documentation | ✅ COMPLETE |
| `phase:2` | ETL Optimization | 🚧 CURRENT |
| `phase:3` | Dashboard Enhancement | 📋 PLANNED |
| `phase:4` | Portal Development | 📋 PLANNED |
| `phase:5` | Tracker Conversion | 📋 PLANNED |
| `phase:6` | ML/CV Integration | 📋 PLANNED |
| `phase:7` | Multi-Tenancy | 📋 PLANNED |
| `phase:8` | Commercial Launch | 📋 PLANNED |

---

## Milestones

| Milestone | Phases | Description | Target |
|-----------|--------|-------------|--------|
| **M1: MVP Foundation** | 1-4 | Core platform functional | Week 16 |
| **M2: Tracker Modernization** | 5 | Rust/Next.js tracker | Week 24 |
| **M3: ML/CV Integration** | 6 | Automated tracking | Week 32 |
| **M4: Commercial Ready** | 7-8 | Multi-tenant, payments | Week 48 |

---

## Phase 2: ETL Optimization (CURRENT)

**Status:** 🚧 IN PROGRESS
**Timeline:** Weeks 5-8
**Objective:** Clean up ETL code, optimize performance, verify tables

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
- **Labels:** `type:test`, `area:etl`, `priority:p1`, `phase:2`
- **Description:** Create automated script to verify all tables have data
- **Acceptance Criteria:**
  - [ ] Script checks all 139 tables exist
  - [ ] Script checks row counts > 0 for active tables
  - [ ] Script validates column schemas
  - [ ] Output report in markdown format

#### ETL-005: Verify all 139 tables have data
- **Labels:** `type:test`, `area:etl`, `priority:p1`, `phase:2`
- **Depends On:** ETL-004
- **Description:** Run verification to confirm all tables populated correctly
- **Acceptance Criteria:**
  - [ ] All dimension tables populated
  - [ ] All fact tables populated
  - [ ] All QA tables populated
  - [ ] Document any empty/unused tables

#### ETL-006: Validate foreign key relationships
- **Labels:** `type:test`, `area:etl`, `priority:p1`, `phase:2`
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
- **Labels:** `type:chore`, `area:etl`, `priority:p2`, `phase:2`
- **Depends On:** ETL-004, ETL-005, ETL-006
- **Description:** Integrate table verification into CI pipeline
- **Acceptance Criteria:**
  - [ ] GitHub Action runs verification on PR
  - [ ] Fails on missing tables
  - [ ] Fails on broken foreign keys
  - [ ] Reports results in PR comment

---

## Phase 3: Dashboard Enhancement

**Status:** 📋 PLANNED
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

---

## Phase 4: Portal Development

**Status:** 📋 PLANNED
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

**Status:** 📋 PLANNED
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

**Status:** 📋 PLANNED
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

**Status:** 📋 PLANNED
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

**Status:** 📋 PLANNED
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

## Foundation & Workflow

**Status:** 🔄 ONGOING
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
| Phase 2: ETL | 🚧 CURRENT | 12 | P0:3, P1:7, P2:2 |
| Phase 3: Dashboard | 📋 PLANNED | 16 | P1:10, P2:4, P3:2 |
| Phase 4: Portal | 📋 PLANNED | 16 | P0:2, P1:9, P2:5 |
| Phase 5: Tracker | 📋 PLANNED | 12 | P0:1, P1:9, P2:2 |
| Phase 6: ML/CV | 📋 PLANNED | 20 | P0:4, P1:8, P2:6, P3:2 |
| Phase 7: Multi-Tenant | 📋 PLANNED | 12 | P0:3, P1:5, P2:4 |
| Phase 8: Commercial | 📋 PLANNED | 12 | P0:3, P1:7, P2:2 |
| Foundation | 🔄 ONGOING | 13 | P0:1, P1:10, P2:2 |
| **Total** | | **113** | |

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

*Last Updated: 2026-01-21*
