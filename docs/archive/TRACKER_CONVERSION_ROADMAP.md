# Tracker Conversion Roadmap

**Step-by-step roadmap for converting HTML tracker to Rust/Next.js**

Last Updated: 2026-01-15  
Version: 23.5 → Target: Rust/Next.js  
Timeline: 6-8 weeks

---

## Overview

This roadmap outlines the complete conversion process from the HTML tracker to a Rust backend + Next.js frontend implementation.

**Source:** `ui/tracker/tracker_index_v23.5.html` (16,162 lines, 200+ functions)  
**Target:** Rust API + Next.js frontend  
**Goal:** Feature parity with improved performance and maintainability

---

## Phase 1: Foundation Setup (Week 1)

### 1.1 Project Setup

**Next.js Project:**
- [ ] Initialize Next.js 14 project with TypeScript
- [ ] Set up Tailwind CSS
- [ ] Set up shadcn/ui components
- [ ] Configure Supabase client
- [ ] Set up project structure

**Rust Project:**
- [ ] Initialize Rust project with Cargo
- [ ] Set up Axum web framework
- [ ] Configure database connection (PostgreSQL)
- [ ] Set up project structure
- [ ] Configure CORS

**Tasks:**
- [ ] Create `ui/tracker/` directory structure
- [ ] Create `tracker-api/` Rust project
- [ ] Set up development environment
- [ ] Configure build scripts
- [ ] Set up testing framework

### 1.2 Database Setup

- [ ] Create `tracker_events` table
- [ ] Create `tracker_shifts` table
- [ ] Create indexes
- [ ] Set up migrations
- [ ] Test database connection

### 1.3 Type Definitions

- [ ] Define TypeScript types for events, shifts, games
- [ ] Define Rust structs for events, shifts, games
- [ ] Create type conversion utilities
- [ ] Document type mappings

---

## Phase 2: Core Event Management (Week 2)

### 2.1 Event CRUD (Rust Backend)

- [ ] Implement `create_event` endpoint
- [ ] Implement `get_event` endpoint
- [ ] Implement `update_event` endpoint
- [ ] Implement `delete_event` endpoint
- [ ] Implement `list_events` endpoint
- [ ] Add event validation
- [ ] Add error handling
- [ ] Write unit tests

### 2.2 Event UI (Next.js Frontend)

- [ ] Create `EventForm` component
- [ ] Create `EventList` component
- [ ] Implement event creation UI
- [ ] Implement event editing UI
- [ ] Implement event deletion UI
- [ ] Add form validation
- [ ] Add error handling
- [ ] Connect to Rust API

### 2.3 State Management

- [ ] Set up Zustand store
- [ ] Implement event state management
- [ ] Implement auto-save
- [ ] Implement state persistence
- [ ] Test state management

---

## Phase 3: Shift Management (Week 3)

### 3.1 Shift CRUD (Rust Backend)

- [ ] Implement `create_shift` endpoint
- [ ] Implement `get_shift` endpoint
- [ ] Implement `update_shift` endpoint
- [ ] Implement `delete_shift` endpoint
- [ ] Implement `list_shifts` endpoint
- [ ] Add shift validation
- [ ] Add shift duration calculation
- [ ] Write unit tests

### 3.2 Shift UI (Next.js Frontend)

- [ ] Create `ShiftForm` component
- [ ] Create `ShiftList` component
- [ ] Implement shift creation UI
- [ ] Implement shift editing UI
- [ ] Implement shift deletion UI
- [ ] Add form validation
- [ ] Connect to Rust API

### 3.3 Shift State Management

- [ ] Add shift state to Zustand store
- [ ] Implement shift auto-save
- [ ] Test shift state management

---

## Phase 4: Player Management & On-Ice Slots (Week 4)

### 4.1 Player Management

- [ ] Implement player loading from Supabase
- [ ] Create `PlayerSelect` component
- [ ] Implement player search/filter
- [ ] Add player assignment to events
- [ ] Add player assignment to shifts

### 4.2 On-Ice Slots

- [ ] Create `OnIceSlots` component
- [ ] Implement slot assignment
- [ ] Implement slot clearing
- [ ] Add slot state management
- [ ] Connect slots to events/shifts

---

## Phase 5: XY Positioning & Rink Canvas (Week 5)

### 5.1 XY Calculations (Rust Backend)

- [ ] Implement XY coordinate conversion
- [ ] Implement zone determination
- [ ] Implement XY validation
- [ ] Add XY calculation endpoints
- [ ] Write unit tests

### 5.2 Rink Canvas (Next.js Frontend)

- [ ] Create `RinkCanvas` component
- [ ] Implement rink SVG rendering
- [ ] Implement click-to-set XY
- [ ] Implement drag-to-set XY
- [ ] Implement period direction handling
- [ ] Add zone visualization
- [ ] Connect to Rust API for calculations

---

## Phase 6: Time/Period Management (Week 5-6)

### 6.1 Time Management

- [ ] Implement period management
- [ ] Implement time formatting
- [ ] Implement time validation
- [ ] Implement total seconds calculation
- [ ] Create `PeriodClock` component

### 6.2 Period Management

- [ ] Implement period switching
- [ ] Implement period direction handling
- [ ] Add period state management
- [ ] Test period/time logic

---

## Phase 7: Video Integration (Week 6)

### 7.1 Video Player

- [ ] Create `VideoPlayer` component
- [ ] Implement HTML5 video support
- [ ] Implement YouTube video support
- [ ] Add video controls
- [ ] Add playback speed control

### 7.2 Video Sync

- [ ] Implement video-to-event sync
- [ ] Implement event-to-video sync
- [ ] Implement period markers
- [ ] Implement intermission handling
- [ ] Add auto-sync feature

---

## Phase 8: Export/Import (Week 7)

### 8.1 Export (Rust Backend)

- [ ] Implement Excel export
- [ ] Implement CSV export
- [ ] Add export validation
- [ ] Add export formatting
- [ ] Write unit tests

### 8.2 Export UI (Next.js Frontend)

- [ ] Create export UI
- [ ] Implement export button
- [ ] Add export options
- [ ] Add export progress
- [ ] Connect to Rust API

### 8.3 Import

- [ ] Implement Excel import
- [ ] Implement CSV import
- [ ] Add import validation
- [ ] Add import UI
- [ ] Test import functionality

---

## Phase 9: Data Validation & Quality (Week 7-8)

### 9.1 Validation (Rust Backend)

- [ ] Implement event validation
- [ ] Implement shift validation
- [ ] Implement XY validation
- [ ] Implement time validation
- [ ] Add validation endpoints
- [ ] Write unit tests

### 9.2 Validation UI (Next.js Frontend)

- [ ] Add real-time validation
- [ ] Add validation error messages
- [ ] Add validation warnings
- [ ] Add data quality checks

---

## Phase 10: Testing & Polish (Week 8)

### 10.1 Testing

- [ ] Write unit tests for Rust backend
- [ ] Write unit tests for Next.js frontend
- [ ] Write integration tests
- [ ] Write E2E tests
- [ ] Test all features
- [ ] Fix bugs

### 10.2 Polish

- [ ] Improve error handling
- [ ] Improve loading states
- [ ] Improve UI/UX
- [ ] Add keyboard shortcuts
- [ ] Add accessibility features
- [ ] Optimize performance

### 10.3 Documentation

- [ ] Document API endpoints
- [ ] Document component usage
- [ ] Document state management
- [ ] Create user guide
- [ ] Update conversion docs

---

## Migration Strategy

### Phase 1: Parallel Development
- Build Rust backend alongside HTML tracker
- Build Next.js frontend alongside HTML tracker
- Test API with existing tracker (optional)

### Phase 2: Feature Parity
- Match all HTML tracker features
- Test feature parity
- Fix any gaps

### Phase 3: Migration
- Deploy Rust backend
- Deploy Next.js frontend
- Migrate existing game data
- Test migration

### Phase 4: Cutover
- Switch users to new tracker
- Monitor for issues
- Archive HTML tracker
- Update documentation

---

## Success Criteria

### Functional Requirements
- [ ] All 15+ event types supported
- [ ] All shift operations working
- [ ] XY positioning accurate
- [ ] Video sync working
- [ ] Export format matches ETL expectations
- [ ] Import working correctly
- [ ] State persistence working
- [ ] Supabase integration working

### Performance Requirements
- [ ] Event creation: < 100ms
- [ ] Page load: < 2 seconds
- [ ] Rink rendering: 60 FPS
- [ ] Video sync: < 50ms latency

### Quality Requirements
- [ ] All tests passing
- [ ] No critical bugs
- [ ] Code coverage > 80%
- [ ] Documentation complete

---

## Risk Mitigation

### Technical Risks
- **Risk:** Rust learning curve
  - **Mitigation:** Start with simple endpoints, learn incrementally
- **Risk:** Performance issues
  - **Mitigation:** Profile early, optimize as needed
- **Risk:** Feature gaps
  - **Mitigation:** Comprehensive feature inventory, regular testing

### Timeline Risks
- **Risk:** Scope creep
  - **Mitigation:** Strict feature list, prioritize must-haves
- **Risk:** Integration issues
  - **Mitigation:** Test integration early, fix issues immediately

---

## Related Documentation

- [TRACKER_FEATURE_INVENTORY.md](TRACKER_FEATURE_INVENTORY.md) - Feature catalog
- [TRACKER_ARCHITECTURE_PLAN.md](TRACKER_ARCHITECTURE_PLAN.md) - Architecture design
- [TRACKER_CONVERSION_SPEC.md](TRACKER_CONVERSION_SPEC.md) - Conversion specification
- [TRACKER_RUST_PLAN.md](TRACKER_RUST_PLAN.md) - Rust implementation plan

---

*Last Updated: 2026-01-15*
