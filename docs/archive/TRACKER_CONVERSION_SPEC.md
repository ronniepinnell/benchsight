# Tracker Conversion Specification

**Complete specification for converting HTML tracker to Rust/Next.js**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document specifies the complete conversion of the HTML tracker (`tracker_index_v23.5.html`) to a Rust/Next.js implementation.

**Source:** `ui/tracker/tracker_index_v23.5.html` (16,162 lines, 200+ functions)  
**Target:** Rust backend + Next.js frontend  
**Goal:** Feature parity with improved performance and maintainability

---

## Conversion Strategy

### Architecture

```
Next.js Frontend (React/TypeScript)
    ↓
Rust Backend (API)
    ↓
Supabase (Database)
```

### Component Breakdown

**Frontend (Next.js):**
- React components for UI
- TypeScript for type safety
- State management (React hooks or Zustand)
- Video player integration
- Rink canvas rendering

**Backend (Rust):**
- Event/shift CRUD operations
- Validation logic
- Export/import processing
- XY coordinate calculations
- Performance-critical operations

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

## Rust Implementation Plan

### Why Rust?

1. **Performance:** Critical calculations (XY, validation) benefit from Rust speed
2. **Safety:** Memory safety for data processing
3. **Concurrency:** Handle multiple games/trackers simultaneously
4. **Integration:** Can be compiled to WebAssembly for browser use

### Rust Modules

```
src/
├── events.rs          # Event CRUD operations
├── shifts.rs          # Shift CRUD operations
├── validation.rs      # Validation logic
├── xy.rs              # XY calculations
├── export.rs          # Export processing
├── import.rs           # Import processing
└── api.rs             # API endpoints
```

### Rust API Endpoints

```rust
// Event endpoints
POST   /api/events           # Create event
GET    /api/events/{id}      # Get event
PUT    /api/events/{id}      # Update event
DELETE /api/events/{id}       # Delete event

// Shift endpoints
POST   /api/shifts            # Create shift
GET    /api/shifts/{id}       # Get shift
PUT    /api/shifts/{id}       # Update shift
DELETE /api/shifts/{id}       # Delete shift

// Export endpoints
POST   /api/export/excel      # Export to Excel
POST   /api/export/csv        # Export to CSV

// Validation endpoints
POST   /api/validate/event    # Validate event
POST   /api/validate/shift    # Validate shift
```

---

## Next.js Implementation Plan

### Component Structure

```
src/app/tracker/
├── [gameId]/
│   └── page.tsx              # Tracker page
├── page.tsx                  # Tracker list
└── videos/
    └── page.tsx              # Video management

src/components/tracker/
├── EventForm.tsx             # Event creation form
├── ShiftForm.tsx             # Shift creation form
├── RinkCanvas.tsx            # Rink rendering
├── VideoPlayer.tsx           # Video player
├── EventList.tsx             # Event list
├── ShiftList.tsx            # Shift list
└── OnIceSlots.tsx           # On-ice player slots
```

### State Management

**Option 1: React Context + Hooks**
```typescript
const TrackerContext = createContext<TrackerState>()

export function useTracker() {
  return useContext(TrackerContext)
}
```

**Option 2: Zustand**
```typescript
interface TrackerStore {
  events: Event[]
  shifts: Shift[]
  addEvent: (event: Event) => void
  updateEvent: (id: string, event: Event) => void
  deleteEvent: (id: string) => void
}

export const useTrackerStore = create<TrackerStore>((set) => ({
  events: [],
  shifts: [],
  addEvent: (event) => set((state) => ({ events: [...state.events, event] })),
  // ...
}))
```

---

## Data Model

### Event Model (TypeScript)

```typescript
interface Event {
  id: string
  gameId: string
  eventIndex: number
  eventType: string
  eventDetail: string
  eventDetail2: string | null
  playDetail: string | null
  playDetail2: string | null
  period: number
  time: string
  timeStartTotalSeconds: number
  team: 'home' | 'away'
  eventPlayer1: string | null
  eventPlayer2: string | null
  eventPlayer3: string | null
  puckXY: [number, number] | null
  netXY: [number, number] | null
  zone: string | null
  strength: string
  situation: string
  linkedEventId: string | null
  createdAt: Date
  updatedAt: Date
}
```

### Shift Model (TypeScript)

```typescript
interface Shift {
  id: string
  gameId: string
  shiftIndex: number
  playerId: string
  playerNumber: number
  team: 'home' | 'away'
  period: number
  startTime: string
  endTime: string | null
  startTotalSeconds: number
  endTotalSeconds: number | null
  durationSeconds: number | null
  startType: string
  endType: string | null
  createdAt: Date
  updatedAt: Date
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
```

---

## Migration Strategy

### Phase 1: Parallel Development

1. Build Rust backend alongside existing HTML tracker
2. Create API endpoints
3. Test API with existing tracker (optional integration)

### Phase 2: Next.js Frontend

1. Build Next.js components
2. Integrate with Rust API
3. Test feature parity

### Phase 3: Migration

1. Deploy Rust backend
2. Deploy Next.js frontend
3. Migrate existing game data
4. Switch users to new tracker

### Phase 4: Deprecation

1. Archive HTML tracker
2. Remove old code
3. Update documentation

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

## Related Documentation

- [TRACKER_COMPLETE_LOGIC.md](TRACKER_COMPLETE_LOGIC.md) - Function reference
- [TRACKER_STATE_MANAGEMENT.md](TRACKER_STATE_MANAGEMENT.md) - State management
- [TRACKER_EVENT_FLOW.md](TRACKER_EVENT_FLOW.md) - Event workflow
- [TRACKER_VIDEO_INTEGRATION.md](TRACKER_VIDEO_INTEGRATION.md) - Video integration
- [TRACKER_XY_POSITIONING.md](TRACKER_XY_POSITIONING.md) - XY positioning
- [TRACKER_EXPORT_FORMAT.md](TRACKER_EXPORT_FORMAT.md) - Export format

---

*Last Updated: 2026-01-15*
