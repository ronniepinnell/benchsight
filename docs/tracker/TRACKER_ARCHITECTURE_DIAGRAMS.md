# BenchSight Tracker Architecture Diagrams

**Visual representation of tracker architecture, current HTML implementation, and future Rust/Next.js conversion**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document provides visual diagrams of the BenchSight Game Tracker architecture, including the current HTML implementation and the planned Rust/Next.js conversion.

**Current Stack:** HTML, JavaScript (vanilla), Supabase JS  
**Target Stack:** Rust (backend), Next.js (frontend), TypeScript, React

---

## Current Architecture (HTML Tracker)

### Component Structure

```mermaid
graph TD
    A[Tracker Root<br/>tracker_index_v23.5.html] --> B[Header Section]
    A --> C[Main Content]
    A --> D[Footer Section]
    
    B --> B1[Game Selector]
    B --> B2[Period Selector]
    B --> B3[Team Colors]
    B --> B4[Save Status]
    
    C --> E[Video Player Section]
    C --> F[Event Tracking Section]
    C --> G[Shift Tracking Section]
    C --> H[XY Positioning Section]
    
    E --> E1[Video Element]
    E --> E2[Playback Controls]
    E --> E3[Period Markers]
    E --> E4[Time Display]
    
    F --> F1[Event Type Selector]
    F --> F2[Player Selectors]
    F --> F3[Event Detail Forms]
    F --> F4[Event List Display]
    F --> F5[Event Chain Templates]
    
    G --> G1[Shift Start/End]
    G --> G2[Line Composition]
    G --> G3[Shift List Display]
    G --> G4[TOI Calculator]
    
    H --> H1[Rink Canvas]
    H --> H2[XY Coordinate Display]
    H --> H3[Position Selector]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style E fill:#aa66ff
    style F fill:#aa66ff
    style G fill:#aa66ff
    style H fill:#aa66ff
```

### State Management (Current)

```mermaid
graph TD
    A[Global State Object: S] --> B[Game State]
    A --> C[Event State]
    A --> D[Shift State]
    A --> E[Player State]
    A --> F[Video State]
    A --> G[UI State]
    
    B --> B1[game_id]
    B --> B2[game_date]
    B --> B3[home_team]
    B --> B4[away_team]
    
    C --> C1[events: Array]
    C --> C2[current_event]
    C --> C3[event_chain_templates]
    
    D --> D1[shifts: Array]
    D --> D2[current_shift]
    D --> D3[lines: Object]
    
    E --> E1[home_roster: Array]
    E --> E2[away_roster: Array]
    E --> E3[players_on_ice: Array]
    
    F --> F1[video_url]
    F --> F2[current_time]
    F --> F3[period_markers]
    
    G --> G1[active_section]
    G --> G2[selected_players]
    G --> G3[xy_position]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#ff8800
    style G fill:#ff8800
```

### Event Flow (Current)

```mermaid
sequenceDiagram
    participant User
    participant UI as Tracker UI
    participant State as Global State (S)
    participant SB as Supabase
    participant Video as Video Player
    
    User->>Video: Play/Pause Video
    Video->>UI: Time Update Event
    UI->>UI: Update Current Time Display
    
    User->>UI: Select Event Type
    UI->>UI: Show Event Form
    
    User->>UI: Select Players
    UI->>State: Update selected_players
    
    User->>UI: Click Rink for XY
    UI->>UI: Calculate XY from click
    UI->>State: Update xy_position
    
    User->>UI: Click "Log Event"
    UI->>State: createEvent()
    State->>State: Validate Event
    State->>State: Add to events array
    State->>UI: Render Event in List
    
    UI->>State: Auto-save (30s interval)
    State->>SB: Save to Supabase
    SB-->>State: Confirm Save
    
    Note over UI,State: Event Chain Templates (v23.9)
    State->>UI: Check for next event suggestion
    UI->>User: Show Auto-suggestion Modal
    User->>UI: Accept/Deny Suggestion
    UI->>State: Create Linked Event (if accepted)
```

### Function Categories (Current)

```mermaid
graph LR
    A[Tracker Functions<br/>200+ total] --> B[Event Management<br/>40+ functions]
    A --> C[Shift Management<br/>30+ functions]
    A --> D[Player Management<br/>20+ functions]
    A --> E[XY Positioning<br/>25+ functions]
    A --> F[Video Integration<br/>15+ functions]
    A --> G[Export/Import<br/>20+ functions]
    A --> H[UI Rendering<br/>30+ functions]
    A --> I[Validation<br/>15+ functions]
    A --> J[State Management<br/>10+ functions]
    
    B --> B1[createEvent]
    B --> B2[editEvent]
    B --> B3[deleteEvent]
    B --> B4[saveEvent]
    
    C --> C1[createShift]
    C --> C2[calculateTOI]
    C --> C3[calculateShiftStats]
    
    D --> D1[addPlayer]
    D --> D2[loadRoster]
    D --> D3[syncRoster]
    
    E --> E1[setXYPosition]
    E --> E2[getXYPosition]
    E --> E3[calculateXYFromClick]
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#ff8800
    style G fill:#ff8800
    style H fill:#ff8800
    style I fill:#ff8800
    style J fill:#ff8800
```

---

## Future Architecture (Rust/Next.js)

### High-Level Architecture

```mermaid
graph TD
    A[Next.js Frontend] --> B[React Components]
    A --> C[State Management<br/>Zustand]
    A --> D[API Client<br/>Fetch/Axios]
    
    B --> B1[Video Player Component]
    B --> B2[Event Form Component]
    B --> B3[Shift Form Component]
    B --> B4[Rink Canvas Component]
    B --> B5[Event List Component]
    
    C --> C1[Game Store]
    C --> C2[Event Store]
    C --> C3[Shift Store]
    C --> C4[Player Store]
    
    D --> E[Rust Backend API]
    
    E --> F[Event Service]
    E --> G[Shift Service]
    E --> H[Validation Service]
    E --> I[Export Service]
    E --> J[XY Calculation Service]
    
    F --> K[(Supabase<br/>PostgreSQL)]
    G --> K
    H --> K
    I --> K
    J --> K
    
    style A fill:#00d4ff
    style E fill:#ff8800
    style K fill:#00ff88
```

### Component Hierarchy (Future)

```mermaid
graph TD
    A[Tracker Page<br/>Next.js] --> B[Layout Component]
    A --> C[Header Component]
    A --> D[Main Content]
    
    B --> B1[Game Selector]
    B --> B2[Period Selector]
    B --> B3[Save Status]
    
    D --> E[Video Section]
    D --> F[Tracking Section]
    D --> G[Data Section]
    
    E --> E1[Video Player Component]
    E --> E2[Playback Controls]
    E --> E3[Period Markers]
    
    F --> F1[Event Tracker Component]
    F --> F2[Shift Tracker Component]
    F --> F3[XY Positioner Component]
    
    F1 --> F1A[Event Type Selector]
    F1 --> F1B[Player Selectors]
    F1 --> F1C[Event Detail Form]
    F1 --> F1D[Event Chain Templates]
    
    F2 --> F2A[Shift Start/End]
    F2 --> F2B[Line Composition]
    F2 --> F2C[TOI Display]
    
    F3 --> F3A[Rink Canvas Component]
    F3 --> F3B[XY Coordinate Display]
    
    G --> G1[Event List Component]
    G --> G2[Shift List Component]
    G --> G3[Export Component]
    
    style A fill:#00d4ff
    style E fill:#ff8800
    style F fill:#ff8800
    style G fill:#ff8800
```

### Data Flow (Future)

```mermaid
sequenceDiagram
    participant User
    participant React as React Component
    participant Store as Zustand Store
    participant API as Rust API
    participant DB as Supabase
    
    User->>React: Interact with UI
    React->>Store: Dispatch Action
    Store->>Store: Update Local State
    Store->>React: Trigger Re-render
    
    Store->>API: API Call (async)
    API->>API: Validate Request
    API->>API: Process Business Logic
    API->>DB: Database Operation
    DB-->>API: Return Data
    API-->>Store: Return Response
    Store->>Store: Update State with Response
    Store->>React: Trigger Re-render
    
    Note over Store,API: Optimistic Updates
    Store->>Store: Update UI Immediately
    Store->>API: Send Request in Background
    API-->>Store: Confirm or Rollback
```

### Rust Backend Services

```mermaid
graph TD
    A[Rust API Server] --> B[Event Service]
    A --> C[Shift Service]
    A --> D[Validation Service]
    A --> E[Export Service]
    A --> F[XY Service]
    A --> G[Import Service]
    
    B --> B1[POST /api/events]
    B --> B2[GET /api/events/{id}]
    B --> B3[PUT /api/events/{id}]
    B --> B4[DELETE /api/events/{id}]
    B --> B5[GET /api/events/game/{game_id}]
    
    C --> C1[POST /api/shifts]
    C --> C2[GET /api/shifts/player/{player_id}]
    C --> C3[PUT /api/shifts/{id}]
    C --> C4[DELETE /api/shifts/{id}]
    C --> C5[GET /api/shifts/game/{game_id}]
    
    D --> D1[validate_event]
    D --> D2[validate_shift]
    D --> D3[validate_xy]
    D --> D4[validate_time]
    
    E --> E1[export_events_csv]
    E --> E2[export_shifts_csv]
    E --> E3[export_game_json]
    
    F --> F1[calculate_xy_from_click]
    F --> F2[validate_xy_bounds]
    F --> F3[convert_xy_to_zone]
    
    G --> G1[import_events_csv]
    G --> G2[import_shifts_csv]
    G --> G3[import_game_json]
    
    B --> H[(Supabase)]
    C --> H
    D --> H
    E --> H
    F --> H
    G --> H
    
    style A fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
    style F fill:#ff8800
    style G fill:#ff8800
    style H fill:#00ff88
```

---

## Conversion Flow

### Migration Strategy

```mermaid
graph TD
    A[Current: HTML Tracker] --> B[Phase 1: Parallel Development]
    B --> C[Phase 2: Feature Parity]
    C --> D[Phase 3: Performance Optimization]
    D --> E[Phase 4: Advanced Features]
    E --> F[Future: Rust/Next.js Tracker]
    
    B --> B1[Extract Business Logic]
    B --> B2[Create Rust API]
    B --> B3[Build Next.js UI]
    B --> B4[Implement Core Features]
    
    C --> C1[Event Tracking]
    C --> C2[Shift Tracking]
    C --> C3[XY Positioning]
    C --> C4[Video Integration]
    C --> C5[Export/Import]
    
    D --> D1[Optimize API Calls]
    D --> D2[Implement Caching]
    D --> D3[WebAssembly for XY]
    D --> D4[Background Processing]
    
    E --> E1[Real-time Sync]
    E --> E2[Multi-user Support]
    E --> E3[Advanced Analytics]
    E --> E4[ML Integration]
    
    style A fill:#ff4444
    style F fill:#00d4ff
    style B fill:#ff8800
    style C fill:#ff8800
    style D fill:#ff8800
    style E fill:#ff8800
```

### Feature Mapping

```mermaid
graph LR
    subgraph Current["Current HTML Features"]
        A1[200+ JS Functions]
        A2[Global State Object]
        A3[Inline Event Handlers]
        A4[Direct DOM Manipulation]
        A5[Supabase JS Client]
    end
    
    subgraph Future["Future Rust/Next.js"]
        B1[Rust API Endpoints]
        B2[Zustand State Management]
        B3[React Event Handlers]
        B4[React Components]
        B5[API Client Layer]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B3
    A4 --> B4
    A5 --> B5
    
    style A1 fill:#ff4444
    style A2 fill:#ff4444
    style A3 fill:#ff4444
    style A4 fill:#ff4444
    style A5 fill:#ff4444
    style B1 fill:#00d4ff
    style B2 fill:#00d4ff
    style B3 fill:#00d4ff
    style B4 fill:#00d4ff
    style B5 fill:#00d4ff
```

---

## User Interaction Flow

### Complete Tracker Workflow

```mermaid
graph TD
    A[User Opens Tracker] --> B[Load Game]
    B --> C[Load Roster]
    C --> D[Load Video]
    D --> E[Set Period Markers]
    
    E --> F{User Action?}
    
    F -->|Track Event| G[Event Tracking Flow]
    F -->|Track Shift| H[Shift Tracking Flow]
    F -->|Export Data| I[Export Flow]
    F -->|Import Data| J[Import Flow]
    
    G --> G1[Play Video]
    G1 --> G2[Pause at Event]
    G2 --> G3[Select Event Type]
    G3 --> G4[Select Players]
    G4 --> G5[Click Rink for XY]
    G5 --> G6[Add Event Details]
    G6 --> G7[Log Event]
    G7 --> G8{Event Chain?}
    G8 -->|Yes| G9[Show Auto-suggestion]
    G8 -->|No| F
    G9 --> G10{Accept?}
    G10 -->|Yes| G11[Create Linked Event]
    G10 -->|No| F
    G11 --> F
    
    H --> H1[Start Shift]
    H1 --> H2[Select Line]
    H2 --> H3[Set Players]
    H3 --> H4[End Shift]
    H4 --> H5[Calculate TOI]
    H5 --> F
    
    I --> I1[Select Export Format]
    I1 --> I2[Generate Export]
    I2 --> I3[Download File]
    I3 --> F
    
    J --> J1[Select Import File]
    J1 --> J2[Parse File]
    J2 --> J3[Validate Data]
    J3 --> J4[Import to State]
    J4 --> F
    
    style A fill:#00d4ff
    style F fill:#aa66ff
    style G fill:#ff8800
    style H fill:#ff8800
    style I fill:#ff8800
    style J fill:#ff8800
```

---

## Related Documentation

- [TRACKER_REFERENCE.md](TRACKER_REFERENCE.md) - Complete function reference
- [TRACKER_CONVERSION.md](TRACKER_CONVERSION.md) - Detailed conversion plan
- [API_ARCHITECTURE_DIAGRAMS.md](../api/API_ARCHITECTURE_DIAGRAMS.md) - API architecture

---

*Last Updated: 2026-01-15*
