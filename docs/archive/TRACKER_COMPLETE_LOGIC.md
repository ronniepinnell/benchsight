# Tracker Complete Logic Reference

**Complete function reference for tracker_index_v23.5.html (200+ functions)**

Last Updated: 2026-01-21
Version: 2.00
Source: `ui/tracker/tracker_index_v23.5.html` (16,162 lines)

---

## Overview

The tracker is a comprehensive game tracking application with 200+ JavaScript functions managing events, shifts, video playback, XY positioning, and data export. This document catalogs all functions for the Rust/Next.js conversion.

**Total Functions:** 200+  
**Lines of Code:** 16,162  
**State Object:** `S` (global state management)

---

## Function Categories

### Event Management (40+ functions)

**Core Event Functions:**
- `createEvent()` - Create new event
- `editEvent()` - Edit existing event
- `deleteEvent()` - Delete event
- `saveEvent()` - Save event to state
- `loadEvent()` - Load event from state
- `getEvent()` - Get event by index
- `getEventsByType()` - Filter events by type
- `getEventsByPlayer()` - Filter events by player
- `getEventsByPeriod()` - Filter events by period

**Event Validation:**
- `validateEvent()` - Validate event data
- `checkEventRequiredFields()` - Check required fields
- `validateEventTime()` - Validate event time
- `validateEventPlayers()` - Validate player assignments

**Event Display:**
- `renderEvent()` - Render event in UI
- `renderEventList()` - Render event list
- `updateEventDisplay()` - Update event display
- `highlightEvent()` - Highlight event in UI

### Shift Management (30+ functions)

**Core Shift Functions:**
- `createShift()` - Create new shift
- `editShift()` - Edit existing shift
- `deleteShift()` - Delete shift
- `saveShift()` - Save shift to state
- `loadShift()` - Load shift from state
- `getShift()` - Get shift by index
- `getShiftsByPlayer()` - Filter shifts by player
- `getShiftsByPeriod()` - Filter shifts by period

**Shift Calculations:**
- `calculateShiftDuration()` - Calculate shift length
- `calculateTOI()` - Calculate time on ice
- `calculateShiftStats()` - Calculate shift statistics
- `calculateLineStats()` - Calculate line statistics

### Player Management (20+ functions)

**Player Functions:**
- `addPlayer()` - Add player to roster
- `removePlayer()` - Remove player from roster
- `getPlayer()` - Get player by ID
- `getPlayersByTeam()` - Get players for team
- `getPlayersOnIce()` - Get players currently on ice
- `updatePlayerPosition()` - Update player position
- `assignPlayerToSlot()` - Assign player to on-ice slot

**Roster Functions:**
- `loadRoster()` - Load roster from Supabase
- `saveRoster()` - Save roster to state
- `syncRoster()` - Sync roster with server

### XY Positioning (25+ functions)

**XY Functions:**
- `setXYPosition()` - Set XY position
- `getXYPosition()` - Get XY position
- `convertXYToRink()` - Convert XY to rink coordinates
- `convertRinkToXY()` - Convert rink to XY coordinates
- `validateXYPosition()` - Validate XY position
- `snapXYToZone()` - Snap XY to zone
- `getZoneFromXY()` - Get zone from XY position

**Rink Functions:**
- `drawRink()` - Draw rink canvas
- `updateRinkDisplay()` - Update rink display
- `handleRinkClick()` - Handle rink click
- `handleRinkDrag()` - Handle rink drag

### Video Integration (30+ functions)

**Video Player Functions:**
- `loadVideo()` - Load video source
- `playVideo()` - Play video
- `pauseVideo()` - Pause video
- `seekVideo()` - Seek to time
- `setVideoSpeed()` - Set playback speed
- `syncVideoToEvent()` - Sync video to event time
- `syncEventToVideo()` - Sync event to video time

**Video Timing Functions:**
- `calculateVideoTime()` - Calculate video time from game time
- `calculateGameTime()` - Calculate game time from video time
- `getPeriodVideoTime()` - Get period video time range
- `handleIntermission()` - Handle intermission timing

**YouTube Integration:**
- `loadYouTubeVideo()` - Load YouTube video
- `initializeYouTubePlayer()` - Initialize YouTube player
- `handleYouTubeStateChange()` - Handle YouTube state changes

### Export/Import (20+ functions)

**Export Functions:**
- `exportToExcel()` - Export to Excel
- `exportToCSV()` - Export to CSV
- `exportEvents()` - Export events only
- `exportShifts()` - Export shifts only
- `exportFull()` - Export full game data
- `formatExportData()` - Format data for export
- `validateExportData()` - Validate export data

**Import Functions:**
- `importFromExcel()` - Import from Excel
- `importFromCSV()` - Import from CSV
- `validateImportData()` - Validate import data
- `mergeImportData()` - Merge imported data

### State Management (15+ functions)

**State Functions:**
- `saveState()` - Save state to localStorage
- `loadState()` - Load state from localStorage
- `clearState()` - Clear state
- `resetState()` - Reset to initial state
- `syncState()` - Sync state with server
- `getState()` - Get current state
- `updateState()` - Update state

### Time/Period Management (15+ functions)

**Time Functions:**
- `setPeriod()` - Set current period
- `getPeriod()` - Get current period
- `getPeriodLength()` - Get period length
- `formatTime()` - Format time display
- `parseTime()` - Parse time string
- `calculateTimeRemaining()` - Calculate time remaining
- `incrementTime()` - Increment game time
- `decrementTime()` - Decrement game time

### UI Functions (20+ functions)

**UI Update Functions:**
- `updateUI()` - Update UI elements
- `refreshDisplay()` - Refresh display
- `showModal()` - Show modal dialog
- `hideModal()` - Hide modal dialog
- `showToast()` - Show toast notification
- `updateEventList()` - Update event list display
- `updateShiftList()` - Update shift list display

**Form Functions:**
- `populateEventForm()` - Populate event form
- `clearEventForm()` - Clear event form
- `validateForm()` - Validate form data
- `submitForm()` - Submit form

---

## Function Dependencies

### Event Creation Flow

```
User clicks "Add Event"
    ↓
createEvent()
    ↓
validateEvent()
    ↓
saveEvent()
    ↓
updateState()
    ↓
updateEventDisplay()
    ↓
syncState() (if auto-save enabled)
```

### Shift Creation Flow

```
User clicks "Add Shift"
    ↓
createShift()
    ↓
validateShift()
    ↓
calculateShiftDuration()
    ↓
saveShift()
    ↓
updateState()
    ↓
updateShiftDisplay()
    ↓
syncState()
```

### Export Flow

```
User clicks "Export"
    ↓
exportToExcel()
    ↓
formatExportData()
    ↓
validateExportData()
    ↓
generateExcelFile()
    ↓
downloadFile()
```

---

## State Object Structure

The tracker uses a global `S` object for state management:

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
  
  // Reference data
  playDetails1: PlayDetail[]
  playDetails2: PlayDetail[]
  eventDetails1: EventDetail[]
  eventDetails2: EventDetail[]
  eventTypesDB: EventType[]
  playerRoles: PlayerRole[]
  
  // Period/Time
  period: number
  evtTeam: 'home' | 'away'
  periodLengths: Record<number, number>
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

## Key Algorithms

### Event Time Calculation

```javascript
function calculateEventTime(period, timeString) {
  // Convert period time to total seconds
  const periodStart = (period - 1) * periodLength
  const periodTime = parseTime(timeString)
  return periodStart + periodTime
}
```

### XY Coordinate Conversion

```javascript
function convertXYToRink(x, y, period, homeAttacksRight) {
  // Convert canvas XY to rink coordinates
  // Handle period direction (home attacks right in P1, left in P2, etc.)
  if (period % 2 === 0) {
    // Even periods: flip X coordinate
    x = rinkWidth - x
  }
  return { x, y, zone: getZoneFromXY(x, y) }
}
```

### Video Sync Algorithm

```javascript
function syncVideoToEvent(event) {
  const videoTime = calculateVideoTime(
    event.period,
    event.time,
    videoTiming.videoStartOffset,
    videoTiming.intermissions
  )
  videoPlayer.seekTo(videoTime)
}
```

---

## Related Documentation

- [TRACKER_STATE_MANAGEMENT.md](TRACKER_STATE_MANAGEMENT.md) - State management details
- [TRACKER_EVENT_FLOW.md](TRACKER_EVENT_FLOW.md) - Event creation workflow
- [TRACKER_VIDEO_INTEGRATION.md](TRACKER_VIDEO_INTEGRATION.md) - Video player integration
- [TRACKER_XY_POSITIONING.md](TRACKER_XY_POSITIONING.md) - XY positioning system
- [TRACKER_EXPORT_FORMAT.md](TRACKER_EXPORT_FORMAT.md) - Export data format
- [TRACKER_CONVERSION_SPEC.md](TRACKER_CONVERSION_SPEC.md) - Conversion specification

---

*Last Updated: 2026-01-15*
