# Tracker State Management

**Complete state object structure and lifecycle management**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

The tracker uses a global `S` object for state management. This document details the complete state structure, lifecycle, and management patterns.

**State Object:** `S` (global)  
**State Size:** ~50 properties  
**Persistence:** localStorage + Supabase (optional)

---

## State Object Structure

### Complete State Interface

```typescript
interface TrackerState {
  // Supabase connection
  sb: SupabaseClient | null
  connected: boolean
  
  // Game info
  gameId: string | null
  games: Game[]
  homeTeam: string
  awayTeam: string
  homeColor: string
  awayColor: string
  homeLogo: string | null
  awayLogo: string | null
  teams: Record<string, Team>
  
  // Reference data from Supabase
  playDetails1: PlayDetail[]      // dim_play_detail
  playDetails2: PlayDetail[]      // dim_play_detail_2
  eventDetails1: EventDetail[]    // dim_event_detail
  eventDetails2: EventDetail[]    // dim_event_detail_2
  eventTypesDB: EventType[]        // dim_event_type
  showAllEventTypes: boolean
  playerRoles: PlayerRole[]        // dim_player_role
  
  // Period/Time
  period: number
  evtTeam: 'home' | 'away'
  periodLengths: Record<number, number>  // { 1: 18, 2: 18, 3: 18, OT: 5 }
  periodLength: number  // Legacy - use getPeriodLength()
  homeAttacksRightP1: boolean
  
  // On-ice slots
  slots: {
    home: OnIceSlots
    away: OnIceSlots
  }
  selectedSlot: string | null
  
  // Events and shifts
  events: Event[]
  shifts: Shift[]
  evtIdx: number
  shiftIdx: number
  
  // Current event being edited
  curr: {
    type: string | null
    players: string[]
    puckXY: number[]
    netXY: number[] | null
  }
  selectedPlayer: string | null
  editingEvtIdx: number | null
  editingShiftIdx: number | null
  lastEndTime: string
  
  // XY positioning
  xyMode: 'puck' | 'player'
  xySlot: number
  editingXYType: string | null
  editingXYIdx: number | null
  xyHistory: XYPosition[]
  
  // Sync
  lastSave: Date | null
  saveTimer: NodeJS.Timeout | null
  linkedEventIdx: number | null
  
  // Video
  videoTiming: VideoTiming
  videoPlayer: VideoPlayerState
  
  // Rosters
  rosters: {
    home: Player[]
    away: Player[]
  }
}
```

---

## State Initialization

### Initial State

```typescript
const S: TrackerState = {
  // Supabase
  sb: null,
  connected: false,
  
  // Game
  gameId: null,
  games: [],
  homeTeam: 'Home',
  awayTeam: 'Away',
  homeColor: '#3b82f6',
  awayColor: '#ef4444',
  homeLogo: null,
  awayLogo: null,
  teams: {},
  
  // Reference data
  playDetails1: [],
  playDetails2: [],
  eventDetails1: [],
  eventDetails2: [],
  eventTypesDB: [],
  showAllEventTypes: false,
  playerRoles: [],
  
  // Period/Time
  period: 1,
  evtTeam: 'home',
  periodLengths: { 1: 18, 2: 18, 3: 18, OT: 5 },
  periodLength: 18,
  homeAttacksRightP1: true,
  
  // Slots
  slots: {
    home: { F1: null, F2: null, F3: null, D1: null, D2: null, G: null, X: null },
    away: { F1: null, F2: null, F3: null, D1: null, D2: null, G: null, X: null }
  },
  selectedSlot: null,
  
  // Events/Shifts
  events: [],
  shifts: [],
  evtIdx: 0,
  shiftIdx: 0,
  
  // Current
  curr: {
    type: null,
    players: [],
    puckXY: [],
    netXY: null
  },
  selectedPlayer: null,
  editingEvtIdx: null,
  editingShiftIdx: null,
  lastEndTime: '18:00',
  
  // XY
  xyMode: 'puck',
  xySlot: 1,
  editingXYType: null,
  editingXYIdx: null,
  xyHistory: [],
  
  // Sync
  lastSave: null,
  saveTimer: null,
  linkedEventIdx: null,
  
  // Video
  videoTiming: {
    videoStartOffset: 0,
    intermission1: 900,
    intermission2: 900,
    intermission3: 300,
    timeouts: [],
    youtubeUrl: ''
  },
  videoPlayer: {
    sources: [],
    currentSourceIdx: 0,
    isPlaying: false,
    currentTime: 0,
    speed: 1,
    autoSync: true,
    ytPlayer: null,
    gameMarkers: {
      P1Start: null,
      P1End: null,
      P2Start: null,
      P2End: null,
      P3Start: null,
      P3End: null,
      OTStart: null,
      OTEnd: null,
      stoppages: []
    }
  },
  
  // Rosters
  rosters: {
    home: [],
    away: []
  }
}
```

---

## State Lifecycle

### 1. Initialization

```typescript
function initializeState() {
  // Load from localStorage if exists
  const saved = localStorage.getItem('tracker_state')
  if (saved) {
    Object.assign(S, JSON.parse(saved))
  }
  
  // Connect to Supabase
  connectSupabase()
  
  // Load reference data
  loadReferenceData()
  
  // Load rosters
  loadRosters()
}
```

### 2. State Updates

```typescript
function updateState(updates: Partial<TrackerState>) {
  Object.assign(S, updates)
  saveState()
  updateUI()
}
```

### 3. State Persistence

```typescript
function saveState() {
  // Save to localStorage
  localStorage.setItem('tracker_state', JSON.stringify(S))
  
  // Save to Supabase (if connected)
  if (S.connected && S.gameId) {
    syncToSupabase()
  }
  
  S.lastSave = new Date()
}
```

### 4. State Reset

```typescript
function resetState() {
  // Clear events and shifts
  S.events = []
  S.shifts = []
  S.evtIdx = 0
  S.shiftIdx = 0
  
  // Reset current
  S.curr = {
    type: null,
    players: [],
    puckXY: [],
    netXY: null
  }
  
  // Reset period
  S.period = 1
  S.lastEndTime = '18:00'
  
  // Save
  saveState()
}
```

---

## State Management Patterns

### Pattern 1: Event State

```typescript
// Creating event
function createEvent() {
  const event = {
    type: S.curr.type,
    players: S.curr.players,
    puckXY: S.curr.puckXY,
    period: S.period,
    time: getCurrentTime(),
    // ... other fields
  }
  
  S.events.push(event)
  S.evtIdx = S.events.length - 1
  saveState()
}
```

### Pattern 2: Shift State

```typescript
// Creating shift
function createShift() {
  const shift = {
    playerId: S.selectedPlayer,
    period: S.period,
    startTime: getCurrentTime(),
    endTime: null,
    // ... other fields
  }
  
  S.shifts.push(shift)
  S.shiftIdx = S.shifts.length - 1
  saveState()
}
```

### Pattern 3: XY State

```typescript
// Setting XY position
function setXYPosition(x: number, y: number) {
  if (S.xyMode === 'puck') {
    S.curr.puckXY = [x, y]
  } else {
    // Player XY
    const slot = S.slots[S.evtTeam][`F${S.xySlot}`]
    if (slot) {
      slot.xy = [x, y]
    }
  }
  
  S.xyHistory.push({ x, y, timestamp: Date.now() })
  saveState()
}
```

---

## State Synchronization

### Auto-Save

```typescript
function enableAutoSave() {
  S.saveTimer = setInterval(() => {
    if (S.connected && S.gameId) {
      syncToSupabase()
    }
  }, 30000) // Every 30 seconds
}

function disableAutoSave() {
  if (S.saveTimer) {
    clearInterval(S.saveTimer)
    S.saveTimer = null
  }
}
```

### Manual Save

```typescript
function manualSave() {
  saveState()
  if (S.connected) {
    syncToSupabase()
  }
  showToast('Saved successfully')
}
```

---

## Related Documentation

- [TRACKER_COMPLETE_LOGIC.md](TRACKER_COMPLETE_LOGIC.md) - Function reference
- [TRACKER_EVENT_FLOW.md](TRACKER_EVENT_FLOW.md) - Event workflow
- [TRACKER_VIDEO_INTEGRATION.md](TRACKER_VIDEO_INTEGRATION.md) - Video integration
- [TRACKER_XY_POSITIONING.md](TRACKER_XY_POSITIONING.md) - XY positioning

---

*Last Updated: 2026-01-15*
