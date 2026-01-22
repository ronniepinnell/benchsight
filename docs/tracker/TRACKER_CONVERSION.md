# Tracker Conversion Plan

**Complete plan for converting HTML tracker to Rust/Next.js**

Last Updated: 2026-01-21
Version: 2.00
Timeline: 6-8 weeks

---

## Overview

This document provides the complete conversion plan for transforming the HTML tracker (`tracker_index_v23.5.html`) into a Rust backend + Next.js frontend implementation.

**Source:** `ui/tracker/tracker_index_v23.5.html` (16,162 lines, 200+ functions)  
**Target:** Rust API + Next.js frontend  
**Goal:** Feature parity with improved performance, maintainability, and scalability

---

## Table of Contents

1. [Architecture](#architecture)
2. [Conversion Strategy](#conversion-strategy)
3. [Rust Implementation](#rust-implementation)
4. [Next.js Implementation](#nextjs-implementation)
5. [Database Schema](#database-schema)
6. [Conversion Roadmap](#conversion-roadmap)
7. [Feature Parity Requirements](#feature-parity-requirements)
8. [Performance Targets](#performance-targets)
9. [Testing Strategy](#testing-strategy)
10. [Migration Strategy](#migration-strategy)

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Frontend                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   React UI   │  │  State Mgmt  │  │  Video Player │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Rink Canvas  │  │ Event Forms  │  │ Shift Forms  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                        ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────┐
│                    Rust Backend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Event API   │  │  Shift API   │  │ Validation   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Export/Import│  │  XY Calc      │  │  Business    │ │
│  │              │  │              │  │  Logic       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                        ↕ SQL/PostgreSQL
┌─────────────────────────────────────────────────────────┐
│                    Supabase                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Events      │  │   Shifts     │  │  Reference   │ │
│  │  Table       │  │   Table      │  │  Data        │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Component Breakdown

**Frontend (Next.js):**
- React components for UI
- TypeScript for type safety
- State management (Zustand)
- Video player integration
- Rink canvas rendering

**Backend (Rust):**
- Event/shift CRUD operations
- Validation logic
- Export/import processing
- XY coordinate calculations
- Performance-critical operations

---

## Conversion Strategy

### Why Rust?

1. **Performance:** Critical calculations (XY, validation) benefit from Rust speed
2. **Safety:** Memory safety for data processing
3. **Concurrency:** Handle multiple games/trackers simultaneously
4. **Integration:** Can be compiled to WebAssembly for browser use

### Migration Phases

**Phase 1: Parallel Development**
- Build Rust backend alongside existing HTML tracker
- Create API endpoints
- Test API with existing tracker (optional integration)

**Phase 2: Next.js Frontend**
- Build Next.js components
- Integrate with Rust API
- Test feature parity

**Phase 3: Migration**
- Deploy Rust backend
- Deploy Next.js frontend
- Migrate existing game data
- Switch users to new tracker

**Phase 4: Deprecation**
- Archive HTML tracker
- Remove old code
- Update documentation

---

## Rust Implementation

### Project Structure

```
tracker-api/
├── Cargo.toml
├── .env.example
├── README.md
├── src/
│   ├── main.rs                       # Entry point
│   ├── lib.rs                        # Library root
│   │
│   ├── api/
│   │   ├── mod.rs
│   │   ├── events.rs                 # Event endpoints
│   │   ├── shifts.rs                 # Shift endpoints
│   │   ├── export.rs                 # Export endpoints
│   │   ├── validation.rs             # Validation endpoints
│   │   └── health.rs                 # Health check
│   │
│   ├── models/
│   │   ├── mod.rs
│   │   ├── event.rs                  # Event model
│   │   ├── shift.rs                  # Shift model
│   │   ├── game.rs                   # Game model
│   │   └── error.rs                  # Error types
│   │
│   ├── services/
│   │   ├── mod.rs
│   │   ├── event_service.rs          # Event business logic
│   │   ├── shift_service.rs         # Shift business logic
│   │   ├── validation_service.rs    # Validation logic
│   │   ├── export_service.rs        # Export logic
│   │   └── xy_service.rs            # XY calculations
│   │
│   ├── database/
│   │   ├── mod.rs
│   │   ├── connection.rs            # DB connection pool
│   │   ├── events.rs                # Event queries
│   │   ├── shifts.rs                # Shift queries
│   │   └── migrations.rs            # Database migrations
│   │
│   └── utils/
│       ├── mod.rs
│       ├── validation.rs             # Validation utilities
│       ├── xy.rs                     # XY utilities
│       └── time.rs                   # Time utilities
│
└── tests/
    ├── integration/
    │   ├── events_test.rs
    │   ├── shifts_test.rs
    │   └── export_test.rs
    └── unit/
        ├── validation_test.rs
        └── xy_test.rs
```

### Dependencies (Cargo.toml)

```toml
[package]
name = "tracker-api"
version = "0.1.0"
edition = "2021"

[dependencies]
# Web framework
axum = "0.7"
tower = "0.4"
tower-http = { version = "0.5", features = ["cors"] }
tokio = { version = "1", features = ["full"] }

# Database
sqlx = { version = "0.7", features = ["runtime-tokio-rustls", "postgres", "chrono", "uuid"] }
postgres = "0.19"

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Error handling
anyhow = "1.0"
thiserror = "1.0"

# Validation
validator = { version = "0.18", features = ["derive"] }

# Excel export
calamine = "0.24"
rust_xlsxwriter = "0.75"

# Time
chrono = "0.4"

# UUID
uuid = { version = "1.6", features = ["v4", "serde"] }

# Environment variables
dotenv = "0.15"

# Logging
tracing = "0.1"
tracing-subscriber = "0.3"

[dev-dependencies]
# Testing
tokio-test = "0.4"
mockall = "0.12"
```

### Core Models

**Event Model:**
```rust
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Event {
    pub id: Uuid,
    pub game_id: i32,
    pub event_index: i32,
    pub event_type: String,
    pub event_detail: Option<String>,
    pub event_detail_2: Option<String>,
    pub play_detail: Option<String>,
    pub play_detail_2: Option<String>,
    pub period: i32,
    pub time: String,
    pub time_start_total_seconds: Option<i32>,
    pub team: String,
    pub event_player_1: Option<String>,
    pub event_player_2: Option<String>,
    pub event_player_3: Option<String>,
    pub puck_x: Option<f64>,
    pub puck_y: Option<f64>,
    pub net_x: Option<f64>,
    pub net_y: Option<f64>,
    pub zone: Option<String>,
    pub strength: Option<String>,
    pub situation: Option<String>,
    pub linked_event_id: Option<Uuid>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}
```

**Shift Model:**
```rust
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Shift {
    pub id: Uuid,
    pub game_id: i32,
    pub shift_index: i32,
    pub player_id: String,
    pub player_number: Option<i32>,
    pub team: String,
    pub period: i32,
    pub start_time: String,
    pub end_time: Option<String>,
    pub start_total_seconds: i32,
    pub end_total_seconds: Option<i32>,
    pub duration_seconds: Option<i32>,
    pub start_type: Option<String>,
    pub end_type: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}
```

### API Endpoints

**Event Endpoints:**
- `POST /api/tracker/events` - Create event
- `GET /api/tracker/events/:id` - Get event
- `PUT /api/tracker/events/:id` - Update event
- `DELETE /api/tracker/events/:id` - Delete event
- `GET /api/tracker/events?game_id=:id` - List events for game

**Shift Endpoints:**
- `POST /api/tracker/shifts` - Create shift
- `GET /api/tracker/shifts/:id` - Get shift
- `PUT /api/tracker/shifts/:id` - Update shift
- `DELETE /api/tracker/shifts/:id` - Delete shift
- `GET /api/tracker/shifts?game_id=:id` - List shifts for game

**Export Endpoints:**
- `POST /api/tracker/export/excel` - Export to Excel
- `POST /api/tracker/export/csv` - Export to CSV

**Validation Endpoints:**
- `POST /api/tracker/validate/event` - Validate event
- `POST /api/tracker/validate/shift` - Validate shift

### XY Service

```rust
pub struct XYService;

impl XYService {
    pub fn convert_canvas_to_rink(
        x: f64,
        y: f64,
        period: i32,
        home_attacks_right_p1: bool
    ) -> (f64, f64) {
        // Convert canvas coordinates to rink coordinates
        // Handle period direction
        (x, y)
    }
    
    pub fn validate_xy_position(x: f64, y: f64) -> bool {
        // Validate XY is within rink bounds
        true
    }
    
    pub fn get_zone_from_xy(x: f64, y: f64) -> String {
        // Determine zone from XY position
        "Offensive".to_string()
    }
}
```

---

## Next.js Implementation

### Component Structure

```
ui/tracker/
├── src/
│   ├── app/
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Tracker list
│   │   └── [gameId]/
│   │       └── page.tsx               # Tracker page
│   │
│   ├── components/
│   │   ├── tracker/
│   │   │   ├── EventForm.tsx          # Event creation/edit form
│   │   │   ├── ShiftForm.tsx          # Shift creation/edit form
│   │   │   ├── EventList.tsx          # Event list display
│   │   │   ├── ShiftList.tsx          # Shift list display
│   │   │   ├── RinkCanvas.tsx         # Rink rendering & XY
│   │   │   ├── VideoPlayer.tsx        # Video player component
│   │   │   ├── OnIceSlots.tsx         # On-ice player slots
│   │   │   ├── PeriodClock.tsx         # Period/time display
│   │   │   ├── ScoreBoard.tsx         # Score display
│   │   │   └── PlayerSelect.tsx       # Player selection
│   │   │
│   │   ├── ui/                        # Shared UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Toast.tsx
│   │   │
│   │   └── layout/
│   │       ├── Sidebar.tsx
│   │       └── Topbar.tsx
│   │
│   ├── lib/
│   │   ├── tracker/
│   │   │   ├── store.ts               # Zustand store
│   │   │   ├── types.ts               # TypeScript types
│   │   │   ├── api.ts                 # API client
│   │   │   ├── validation.ts          # Client-side validation
│   │   │   └── utils.ts               # Utility functions
│   │   │
│   │   ├── supabase/
│   │   │   ├── client.ts              # Supabase client
│   │   │   └── server.ts              # Server client
│   │   │
│   │   └── utils.ts                   # General utilities
│   │
│   ├── hooks/
│   │   ├── useTracker.ts              # Tracker hook
│   │   ├── useGameState.ts            # Game state hook
│   │   ├── useKeyboardShortcuts.ts    # Keyboard shortcuts
│   │   ├── useAutoSave.ts             # Auto-save hook
│   │   └── useVideoSync.ts            # Video sync hook
│   │
│   └── styles/
│       └── globals.css                # Global styles
│
├── public/
│   ├── rink.svg                       # Rink SVG
│   └── assets/                        # Static assets
│
└── package.json
```

### State Management (Zustand)

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface TrackerStore {
  // Game state
  gameId: string | null
  games: Game[]
  homeTeam: string
  awayTeam: string
  
  // Events & shifts
  events: Event[]
  shifts: Shift[]
  evtIdx: number
  shiftIdx: number
  
  // Current editing
  editingEvtIdx: number | null
  editingShiftIdx: number | null
  curr: CurrentEvent
  
  // Period/Time
  period: number
  evtTeam: 'home' | 'away'
  
  // On-ice slots
  slots: OnIceSlots
  
  // Actions
  addEvent: (event: Event) => void
  updateEvent: (idx: number, event: Event) => void
  deleteEvent: (idx: number) => void
  addShift: (shift: Shift) => void
  updateShift: (idx: number, shift: Shift) => void
  deleteShift: (idx: number) => void
  setPeriod: (period: number) => void
  setEvtTeam: (team: 'home' | 'away') => void
}

export const useTrackerStore = create<TrackerStore>()(
  persist(
    (set) => ({
      // Initial state
      gameId: null,
      events: [],
      shifts: [],
      // ... more state
      
      // Actions
      addEvent: (event) => set((state) => ({
        events: [...state.events, event],
        evtIdx: state.events.length
      })),
      // ... more actions
    }),
    {
      name: 'tracker-storage',
      partialize: (state) => ({
        events: state.events,
        shifts: state.shifts,
        period: state.period,
        // ... persist only necessary fields
      })
    }
  )
)
```

### API Client

```typescript
class TrackerAPI {
  private baseUrl = '/api/tracker'
  
  async createEvent(event: Event): Promise<Event> {
    const res = await fetch(`${this.baseUrl}/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event)
    })
    return res.json()
  }
  
  async updateEvent(id: string, event: Event): Promise<Event> {
    const res = await fetch(`${this.baseUrl}/events/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event)
    })
    return res.json()
  }
  
  async deleteEvent(id: string): Promise<void> {
    await fetch(`${this.baseUrl}/events/${id}`, {
      method: 'DELETE'
    })
  }
  
  // ... more API methods
}

export const trackerAPI = new TrackerAPI()
```

---

## Database Schema

### Events Table

```sql
CREATE TABLE tracker_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id INTEGER NOT NULL REFERENCES dim_schedule(game_id),
  event_index INTEGER NOT NULL,
  event_type VARCHAR(50) NOT NULL,
  event_detail VARCHAR(100),
  event_detail_2 VARCHAR(100),
  play_detail VARCHAR(100),
  play_detail_2 VARCHAR(100),
  period INTEGER NOT NULL,
  time VARCHAR(10) NOT NULL,
  time_start_total_seconds INTEGER,
  team VARCHAR(10) NOT NULL,
  event_player_1 VARCHAR(20),
  event_player_2 VARCHAR(20),
  event_player_3 VARCHAR(20),
  puck_x DECIMAL(10, 2),
  puck_y DECIMAL(10, 2),
  net_x DECIMAL(10, 2),
  net_y DECIMAL(10, 2),
  zone VARCHAR(20),
  strength VARCHAR(10),
  situation VARCHAR(20),
  linked_event_id UUID,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(game_id, event_index)
);

CREATE INDEX idx_tracker_events_game_id ON tracker_events(game_id);
CREATE INDEX idx_tracker_events_period ON tracker_events(period);
CREATE INDEX idx_tracker_events_event_type ON tracker_events(event_type);
```

### Shifts Table

```sql
CREATE TABLE tracker_shifts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id INTEGER NOT NULL REFERENCES dim_schedule(game_id),
  shift_index INTEGER NOT NULL,
  player_id VARCHAR(20) NOT NULL REFERENCES dim_player(player_id),
  player_number INTEGER,
  team VARCHAR(10) NOT NULL,
  period INTEGER NOT NULL,
  start_time VARCHAR(10) NOT NULL,
  end_time VARCHAR(10),
  start_total_seconds INTEGER NOT NULL,
  end_total_seconds INTEGER,
  duration_seconds INTEGER,
  start_type VARCHAR(50),
  end_type VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(game_id, shift_index)
);

CREATE INDEX idx_tracker_shifts_game_id ON tracker_shifts(game_id);
CREATE INDEX idx_tracker_shifts_player_id ON tracker_shifts(player_id);
CREATE INDEX idx_tracker_shifts_period ON tracker_shifts(period);
```

---

## Conversion Roadmap

### Phase 1: Foundation Setup (Week 1)

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

**Database Setup:**
- [ ] Create `tracker_events` table
- [ ] Create `tracker_shifts` table
- [ ] Create indexes
- [ ] Set up migrations
- [ ] Test database connection

**Type Definitions:**
- [ ] Define TypeScript types for events, shifts, games
- [ ] Define Rust structs for events, shifts, games
- [ ] Create type conversion utilities
- [ ] Document type mappings

### Phase 2: Core Event Management (Week 2)

**Event CRUD (Rust Backend):**
- [ ] Implement `create_event` endpoint
- [ ] Implement `get_event` endpoint
- [ ] Implement `update_event` endpoint
- [ ] Implement `delete_event` endpoint
- [ ] Implement `list_events` endpoint
- [ ] Add event validation
- [ ] Add error handling
- [ ] Write unit tests

**Event UI (Next.js Frontend):**
- [ ] Create `EventForm` component
- [ ] Create `EventList` component
- [ ] Implement event creation UI
- [ ] Implement event editing UI
- [ ] Implement event deletion UI
- [ ] Add form validation
- [ ] Add error handling
- [ ] Connect to Rust API

**State Management:**
- [ ] Set up Zustand store
- [ ] Implement event state management
- [ ] Implement auto-save
- [ ] Implement state persistence
- [ ] Test state management

### Phase 3: Shift Management (Week 3)

**Shift CRUD (Rust Backend):**
- [ ] Implement `create_shift` endpoint
- [ ] Implement `get_shift` endpoint
- [ ] Implement `update_shift` endpoint
- [ ] Implement `delete_shift` endpoint
- [ ] Implement `list_shifts` endpoint
- [ ] Add shift validation
- [ ] Add shift duration calculation
- [ ] Write unit tests

**Shift UI (Next.js Frontend):**
- [ ] Create `ShiftForm` component
- [ ] Create `ShiftList` component
- [ ] Implement shift creation UI
- [ ] Implement shift editing UI
- [ ] Implement shift deletion UI
- [ ] Add form validation
- [ ] Connect to Rust API

**Shift State Management:**
- [ ] Add shift state to Zustand store
- [ ] Implement shift auto-save
- [ ] Test shift state management

### Phase 4: Player Management & On-Ice Slots (Week 4)

**Player Management:**
- [ ] Implement player loading from Supabase
- [ ] Create `PlayerSelect` component
- [ ] Implement player search/filter
- [ ] Add player assignment to events
- [ ] Add player assignment to shifts

**On-Ice Slots:**
- [ ] Create `OnIceSlots` component
- [ ] Implement slot assignment
- [ ] Implement slot clearing
- [ ] Add slot state management
- [ ] Connect slots to events/shifts

### Phase 5: XY Positioning & Rink Canvas (Week 5)

**XY Calculations (Rust Backend):**
- [ ] Implement XY coordinate conversion
- [ ] Implement zone determination
- [ ] Implement XY validation
- [ ] Add XY calculation endpoints
- [ ] Write unit tests

**Rink Canvas (Next.js Frontend):**
- [ ] Create `RinkCanvas` component
- [ ] Implement rink SVG rendering
- [ ] Implement click-to-set XY
- [ ] Implement drag-to-set XY
- [ ] Implement period direction handling
- [ ] Add zone visualization
- [ ] Connect to Rust API for calculations

### Phase 6: Time/Period Management (Week 5-6)

**Time Management:**
- [ ] Implement period management
- [ ] Implement time formatting
- [ ] Implement time validation
- [ ] Implement total seconds calculation
- [ ] Create `PeriodClock` component

**Period Management:**
- [ ] Implement period switching
- [ ] Implement period direction handling
- [ ] Add period state management
- [ ] Test period/time logic

### Phase 7: Video Integration (Week 6)

**Video Player:**
- [ ] Create `VideoPlayer` component
- [ ] Implement HTML5 video support
- [ ] Implement YouTube video support
- [ ] Add video controls
- [ ] Add playback speed control

**Video Sync:**
- [ ] Implement video-to-event sync
- [ ] Implement event-to-video sync
- [ ] Implement period markers
- [ ] Implement intermission handling
- [ ] Add auto-sync feature

### Phase 8: Export/Import (Week 7)

**Export (Rust Backend):**
- [ ] Implement Excel export
- [ ] Implement CSV export
- [ ] Add export validation
- [ ] Add export formatting
- [ ] Write unit tests

**Export UI (Next.js Frontend):**
- [ ] Create export UI
- [ ] Implement export button
- [ ] Add export options
- [ ] Add export progress
- [ ] Connect to Rust API

**Import:**
- [ ] Implement Excel import
- [ ] Implement CSV import
- [ ] Add import validation
- [ ] Add import UI
- [ ] Test import functionality

### Phase 9: Data Validation & Quality (Week 7-8)

**Validation (Rust Backend):**
- [ ] Implement event validation
- [ ] Implement shift validation
- [ ] Implement XY validation
- [ ] Implement time validation
- [ ] Add validation endpoints
- [ ] Write unit tests

**Validation UI (Next.js Frontend):**
- [ ] Add real-time validation
- [ ] Add validation error messages
- [ ] Add validation warnings
- [ ] Add data quality checks

### Phase 10: Testing & Polish (Week 8)

**Testing:**
- [ ] Write unit tests for Rust backend
- [ ] Write unit tests for Next.js frontend
- [ ] Write integration tests
- [ ] Write E2E tests
- [ ] Test all features
- [ ] Fix bugs

**Polish:**
- [ ] Improve error handling
- [ ] Improve loading states
- [ ] Improve UI/UX
- [ ] Add keyboard shortcuts
- [ ] Add accessibility features
- [ ] Optimize performance

**Documentation:**
- [ ] Document API endpoints
- [ ] Document component usage
- [ ] Document state management
- [ ] Create user guide
- [ ] Update conversion docs

---

## Feature Parity Requirements

### Core Features (Must Have)

1. **Event Management**
   - ✅ Create, edit, delete events
   - ✅ All 15+ event types
   - ✅ Player assignment
   - ✅ XY positioning
   - ✅ Validation

2. **Shift Management**
   - ✅ Create, edit, delete shifts
   - ✅ Shift timing
   - ✅ Player assignment
   - ✅ Line combinations

3. **Video Integration**
   - ✅ HTML5 video support
   - ✅ YouTube integration
   - ✅ Auto-sync
   - ✅ Period markers
   - ✅ Time conversion

4. **XY Positioning**
   - ✅ Rink coordinate system
   - ✅ Period direction handling
   - ✅ Zone determination
   - ✅ Canvas rendering

5. **Export/Import**
   - ✅ Excel export
   - ✅ CSV export
   - ✅ Import from Excel
   - ✅ Data validation

6. **State Management**
   - ✅ Local state
   - ✅ Cloud sync (Supabase)
   - ✅ Auto-save
   - ✅ Undo/redo

---

## Performance Targets

### Rust Backend
- Event creation: < 10ms
- Event validation: < 5ms
- Export processing: < 100ms for 1000 events
- XY calculations: < 1ms

### Next.js Frontend
- Page load: < 2 seconds
- Event creation UI: < 100ms
- Rink rendering: 60 FPS
- Video sync: < 50ms latency

---

## Testing Strategy

### Unit Tests
- Rust: Test each module independently
- TypeScript: Test React components

### Integration Tests
- Test API endpoints
- Test frontend-backend integration
- Test export/import

### E2E Tests
- Test complete event creation flow
- Test video sync
- Test export functionality

---

## Migration Strategy

### Phase 1: Parallel Development
- Build Rust backend alongside existing HTML tracker
- Build Next.js frontend alongside existing HTML tracker
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

## Related Documentation

- [TRACKER_REFERENCE.md](TRACKER_REFERENCE.md) - Complete function and feature reference
- [TRACKER_CONVERSION_SPEC.md](../archive/TRACKER_CONVERSION_SPEC.md) - Detailed conversion specification (archived)
- [TRACKER_CONVERSION_ROADMAP.md](../archive/TRACKER_CONVERSION_ROADMAP.md) - Detailed roadmap (archived)
- [TRACKER_RUST_PLAN.md](../archive/TRACKER_RUST_PLAN.md) - Detailed Rust plan (archived)
- [TRACKER_ARCHITECTURE_PLAN.md](../archive/TRACKER_ARCHITECTURE_PLAN.md) - Detailed architecture (archived)

---

*Last Updated: 2026-01-15*
