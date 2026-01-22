# Tracker Architecture Plan

**Architecture design for Rust/Next.js tracker conversion**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document outlines the architecture for converting the HTML tracker to a Rust backend + Next.js frontend implementation.

**Source:** `ui/tracker/tracker_index_v23.5.html` (16,162 lines)  
**Target:** Rust API + Next.js frontend  
**Goal:** Feature parity with improved performance, maintainability, and scalability

---

## Architecture Overview

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

---

## Frontend Architecture (Next.js)

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

### State Management

**Option: Zustand Store**

```typescript
// lib/tracker/store.ts
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
  // ... more actions
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
// lib/tracker/api.ts
import { TrackerApiClient } from '@/lib/tracker/types'

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

## Backend Architecture (Rust)

### Project Structure

```
tracker-api/
├── src/
│   ├── main.rs                       # Entry point
│   ├── api/
│   │   ├── mod.rs
│   │   ├── events.rs                  # Event endpoints
│   │   ├── shifts.rs                 # Shift endpoints
│   │   ├── export.rs                 # Export endpoints
│   │   └── validation.rs             # Validation endpoints
│   │
│   ├── models/
│   │   ├── mod.rs
│   │   ├── event.rs                  # Event model
│   │   ├── shift.rs                  # Shift model
│   │   └── game.rs                   # Game model
│   │
│   ├── services/
│   │   ├── mod.rs
│   │   ├── event_service.rs          # Event business logic
│   │   ├── shift_service.rs          # Shift business logic
│   │   ├── validation_service.rs     # Validation logic
│   │   ├── export_service.rs         # Export logic
│   │   └── xy_service.rs             # XY calculations
│   │
│   ├── database/
│   │   ├── mod.rs
│   │   ├── connection.rs             # DB connection
│   │   └── queries.rs                # SQL queries
│   │
│   └── utils/
│       ├── mod.rs
│       ├── validation.rs              # Validation utilities
│       └── xy.rs                      # XY utilities
│
├── Cargo.toml
└── README.md
```

### API Framework: Axum

```rust
// src/main.rs
use axum::{
    routing::{get, post, put, delete},
    Router,
};

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/api/tracker/events", post(create_event))
        .route("/api/tracker/events/:id", get(get_event))
        .route("/api/tracker/events/:id", put(update_event))
        .route("/api/tracker/events/:id", delete(delete_event))
        .route("/api/tracker/shifts", post(create_shift))
        .route("/api/tracker/shifts/:id", get(get_shift))
        .route("/api/tracker/shifts/:id", put(update_shift))
        .route("/api/tracker/shifts/:id", delete(delete_shift))
        .route("/api/tracker/export/excel", post(export_excel))
        .route("/api/tracker/validate/event", post(validate_event));
    
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3001").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

### Event Service

```rust
// src/services/event_service.rs
use crate::models::event::Event;
use crate::database::queries;

pub struct EventService;

impl EventService {
    pub async fn create_event(event: Event) -> Result<Event, ServiceError> {
        // Validate
        Self::validate_event(&event)?;
        
        // Calculate derived fields
        let event = Self::calculate_derived_fields(event)?;
        
        // Save to database
        let event = queries::insert_event(event).await?;
        
        Ok(event)
    }
    
    pub async fn update_event(id: String, event: Event) -> Result<Event, ServiceError> {
        // Validate
        Self::validate_event(&event)?;
        
        // Update in database
        let event = queries::update_event(id, event).await?;
        
        Ok(event)
    }
    
    pub async fn delete_event(id: String) -> Result<(), ServiceError> {
        queries::delete_event(id).await?;
        Ok(())
    }
    
    fn validate_event(event: &Event) -> Result<(), ValidationError> {
        // Validation logic
        Ok(())
    }
    
    fn calculate_derived_fields(event: Event) -> Result<Event, ServiceError> {
        // Calculate time_start_total_seconds, zone, etc.
        Ok(event)
    }
}
```

### XY Service

```rust
// src/services/xy_service.rs
pub struct XYService;

impl XYService {
    pub fn convert_canvas_to_rink(
        x: f64,
        y: f64,
        period: i32,
        home_attacks_right_p1: bool
    ) -> (f64, f64, String) {
        // Convert canvas coordinates to rink coordinates
        // Handle period direction
        // Determine zone
        (x, y, "Offensive".to_string())
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

## API Endpoints

### Event Endpoints

```
POST   /api/tracker/events              # Create event
GET    /api/tracker/events/:id          # Get event
PUT    /api/tracker/events/:id          # Update event
DELETE /api/tracker/events/:id          # Delete event
GET    /api/tracker/events?game_id=:id  # List events for game
```

### Shift Endpoints

```
POST   /api/tracker/shifts              # Create shift
GET    /api/tracker/shifts/:id          # Get shift
PUT    /api/tracker/shifts/:id          # Update shift
DELETE /api/tracker/shifts/:id          # Delete shift
GET    /api/tracker/shifts?game_id=:id  # List shifts for game
```

### Export Endpoints

```
POST   /api/tracker/export/excel        # Export to Excel
POST   /api/tracker/export/csv         # Export to CSV
```

### Validation Endpoints

```
POST   /api/tracker/validate/event     # Validate event
POST   /api/tracker/validate/shift     # Validate shift
```

---

## Performance Considerations

### Frontend Optimization
- React.memo for expensive components
- useMemo for calculated values
- useCallback for event handlers
- Code splitting for routes
- Lazy loading for video player

### Backend Optimization
- Async/await for I/O operations
- Connection pooling for database
- Caching for reference data
- Batch operations for bulk updates

### Database Optimization
- Indexes on frequently queried columns
- Partitioning for large tables (future)
- Query optimization
- Connection pooling

---

## Security Considerations

### Authentication
- JWT tokens for API authentication
- Supabase Auth integration
- Role-based access control (future)

### Validation
- Input validation on both frontend and backend
- SQL injection prevention (parameterized queries)
- XSS prevention (React auto-escaping)
- CSRF protection

### Data Privacy
- Encrypted connections (HTTPS)
- Secure storage of credentials
- Data access controls

---

## Deployment

### Frontend (Vercel)
- Next.js deployment
- Environment variables
- Build optimization

### Backend (Railway/Render)
- Rust binary deployment
- Environment variables
- Database connection
- Health check endpoint

### Database (Supabase)
- Production database
- Backup strategy
- Migration management

---

## Related Documentation

- [TRACKER_FEATURE_INVENTORY.md](TRACKER_FEATURE_INVENTORY.md) - Feature catalog
- [TRACKER_CONVERSION_SPEC.md](TRACKER_CONVERSION_SPEC.md) - Conversion specification
- [TRACKER_CONVERSION_ROADMAP.md](TRACKER_CONVERSION_ROADMAP.md) - Conversion roadmap
- [TRACKER_RUST_PLAN.md](TRACKER_RUST_PLAN.md) - Rust implementation plan

---

*Last Updated: 2026-01-15*
