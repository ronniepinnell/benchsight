# Tracker Complete Reference

**Complete reference for BenchSight Tracker v27.0 - functions, state, workflows, and features**

Last Updated: 2026-01-21
Version: 3.00
Source: `ui/tracker/tracker_index_v27.0.html`

---

## Overview

The tracker is a comprehensive game tracking application with 700+ JavaScript functions managing events, shifts, video playback, XY positioning, and data export. This document provides complete reference for all tracker functionality.

**Total Functions:** 722 (verified 2026-01-21)
**Lines of Code:** 35,174 (doubled since v23.5)
**State Object:** `S` (global state management)
**Features:** 150+ features across 15 categories

### Version History
| Version | Lines | Functions | Key Changes |
|---------|-------|-----------|-------------|
| v23.5 | 16,162 | ~200 | Original documented version |
| v26.0 | ~28,000 | ~500 | Video management expansion |
| v27.0 | 35,174 | 722 | Full feature set, highlight videos, multi-source video |
| v28.0 | 35,008 | ~720 | Latest version (refinements) |

**Related Documentation:**
- [TRACKER_ARCHITECTURE_DIAGRAMS.md](TRACKER_ARCHITECTURE_DIAGRAMS.md) - **NEW** Visual tracker architecture diagrams (current HTML, future Rust/Next.js)
- [TRACKER_CONVERSION.md](TRACKER_CONVERSION.md) - Complete Rust/Next.js conversion plan

---

## Table of Contents

1. [Function Reference](#function-reference)
2. [State Management](#state-management)
3. [Event Flow](#event-flow)
4. [Video Integration](#video-integration)
5. [XY Positioning](#xy-positioning)
6. [Export/Import](#exportimport)
7. [Dropdown Mapping](#dropdown-mapping)
8. [Feature Inventory](#feature-inventory)

---

## Function Reference

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

## New Features in v27.0 (Since v23.5)

### Video System Expansion (100+ new functions)

The video system has been significantly expanded with multi-source support, highlight videos, and advanced scrubbing.

**Multi-Source Video Management:**
- `addVideoSource()` - Add video source with hotkey
- `switchVideoByHotkey()` - Switch sources via keyboard
- `switchVideoSource()` - Switch video source
- `setActiveVideoSource()` - Set active source
- `updateVideoSourcesUI()` - Update source list UI
- `renderVideoHotkeyBar()` - Render video hotkey bar
- `showVideoSourcesManager()` - Manage video sources
- `removeVideoSource()` - Remove video source
- `saveVideoSources()` / `loadVideoSources()` - Persistence

**Highlight Videos:**
- `openHighlightVideosModal()` / `closeHighlightVideosModal()` - Modal management
- `renderHighlightVideos()` - Render highlight list
- `addHighlightVideo()` - Add highlight video
- `removeHighlightVideo()` - Remove highlight video
- `updateHighlightVideoUrl()` - Update highlight URL

**Video Timing & Scrubbing:**
- `renderVideoScrubBar()` - Scrub bar visualization
- `handleScrubClick()` - Handle scrub interaction
- `calculateAdjustedVideoTime()` - Adjusted time calculation
- `calculateRunningVideoTime()` - Running time calculation
- `renderVideoTimeouts()` - Timeout markers
- `addVideoTimeout()` / `removeVideoTimeout()` - Timeout management

### Rink Visualization Enhancements (20+ new functions)

**Zoom Controls:**
- `rinkZoomIn()` / `rinkZoomOut()` / `rinkZoomReset()` - Zoom controls
- `toggleRinkZoomLock()` - Lock zoom level
- `updateRinkZoomLockUI()` - Update zoom UI
- `rinkZoomAtPoint()` - Zoom at cursor position
- `updateRinkViewBox()` - Update viewBox

### Settings & Configuration (15+ new functions)

- `loadSettings()` / `saveSettings()` - Settings persistence
- `openSettings()` / `closeSettings()` - Settings modal
- `openUserGuide()` - User guide access
- `openHelp()` / `closeHelp()` - Help system
- `updatePeriodLengthsFromUI()` - UI-driven period config
- `updatePenaltyLengthsFromUI()` - UI-driven penalty config

### Video Timing Modal (15+ new functions)

- `openVideoTimingModal()` / `closeVideoTimingModal()` - Modal management
- `syncPeriodLengthsFromVT()` - Sync period lengths
- `parseTimeToSeconds()` / `formatSecondsToTime()` - Time parsing
- `updateTimeoutFromGameTimes()` / `updateTimeoutFromVideoTimes()` - Timeout sync
- `calculateStopTime()` / `calculateDurationFromTimes()` - Duration calculations
- `saveVideoTiming()` / `updateVideoTimingPreview()` - Save and preview

---

## State Management

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

### State Initialization

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

### State Persistence

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

### Auto-Save

```typescript
function enableAutoSave() {
  S.saveTimer = setInterval(() => {
    if (S.connected && S.gameId) {
      syncToSupabase()
    }
  }, 30000) // Every 30 seconds
}
```

---

## Event Flow

### Event Creation Workflow

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

### Event Editing Workflow

```
User Clicks Edit on Event
    ↓
Load Event into Form
    ↓
Populate Form Fields
    ↓
User Modifies Fields
    ↓
Validate Changes
    ↓
Update Event in Array
    ↓
Save State
    ↓
Update UI
    ↓
Sync to Server
```

### Event Deletion Workflow

```
User Clicks Delete on Event
    ↓
Confirm Deletion
    ↓
Remove from Array
    ↓
Update Indices
    ↓
Save State
    ↓
Update UI
    ↓
Sync to Server
```

### Event Validation

**Required Fields:**
- `event_type` (required)
- `period` (required)
- `time` (required)
- `team` (required)

**Event-Specific:**
- **Shot/Goal:** `event_player_1` (shooter)
- **Pass:** `event_player_1` (passer), `event_player_2` (receiver)
- **Faceoff:** `event_player_1` (winner), `event_player_2` (loser)
- **Goal:** `event_detail` must be 'Goal_Scored'

### Event Storage Format

```typescript
interface Event {
  // Identification
  event_id: string
  event_index: number
  
  // Core fields
  event_type: string
  event_detail: string
  event_detail_2: string
  play_detail: string
  play_detail_2: string
  
  // Time/Period
  period: number
  time: string
  time_start_total_seconds: number
  
  // Team
  team: 'home' | 'away'
  team_venue: 'Home' | 'Away'
  
  // Players
  event_player_1: string | null  // Primary actor
  event_player_2: string | null  // Secondary
  event_player_3: string | null  // Tertiary
  
  // Position
  puckXY: [number, number] | null
  netXY: [number, number] | null
  zone: string | null
  
  // Context
  strength: string
  situation: string
  linked_event_id: string | null
  
  // Metadata
  created_at: Date
  updated_at: Date
}
```

---

## Video Integration

### Video Player State

```typescript
interface VideoPlayerState {
  sources: VideoSource[]
  currentSourceIdx: number
  isPlaying: boolean
  currentTime: number
  speed: number
  autoSync: boolean
  ytPlayer: YT.Player | null
  gameMarkers: GameMarkers
}

interface VideoTiming {
  videoStartOffset: number
  intermission1: number  // 15 min = 900 seconds
  intermission2: number   // 15 min = 900 seconds
  intermission3: number   // 5 min = 300 seconds
  timeouts: Timeout[]
  youtubeUrl: string
}
```

### Video Loading

**HTML5 Video:**
```typescript
function loadVideo(url: string) {
  const video = document.getElementById('video-player') as HTMLVideoElement
  video.src = url
  video.load()
  
  S.videoPlayer.sources = [{
    type: 'html5',
    url: url
  }]
  S.videoPlayer.currentSourceIdx = 0
}
```

**YouTube Video:**
```typescript
function loadYouTubeVideo(videoId: string) {
  S.videoTiming.youtubeUrl = `https://www.youtube.com/watch?v=${videoId}`
  
  if (!S.videoPlayer.ytPlayer) {
    initializeYouTubePlayer(videoId)
  } else {
    S.videoPlayer.ytPlayer.loadVideoById(videoId)
  }
}
```

### Video Synchronization

**Game Time to Video Time:**
```typescript
function calculateVideoTime(
  period: number,
  gameTime: string,
  videoStartOffset: number,
  intermissions: VideoTiming
): number {
  const [minutes, seconds] = gameTime.split(':').map(Number)
  const gameSeconds = minutes * 60 + seconds
  
  let videoTime = videoStartOffset
  
  if (period > 1) {
    videoTime += intermissions.intermission1
  }
  if (period > 2) {
    videoTime += intermissions.intermission2
  }
  if (period > 3) {
    videoTime += intermissions.intermission3
  }
  
  const periodStart = (period - 1) * periodLength
  videoTime += periodStart + gameSeconds
  
  return videoTime
}
```

**Auto-Sync:**
```typescript
function syncVideoToEvent(event: Event) {
  if (!S.videoPlayer.autoSync) return
  
  const videoTime = calculateVideoTime(
    event.period,
    event.time,
    S.videoTiming.videoStartOffset,
    S.videoTiming
  )
  
  if (S.videoPlayer.ytPlayer) {
    S.videoPlayer.ytPlayer.seekTo(videoTime, true)
  } else {
    const video = document.getElementById('video-player') as HTMLVideoElement
    video.currentTime = videoTime
  }
}
```

---

## XY Positioning

### Coordinate System

**Rink Dimensions:**
- Length: 200 feet (60.96 meters)
- Width: 85 feet (25.91 meters)
- Neutral zone: 50 feet (15.24 meters)
- End zones: 75 feet each (22.86 meters)

**Canvas Coordinate System:**
- Origin (0, 0): Top-left corner
- X-axis: Left to right (0 to canvas.width)
- Y-axis: Top to bottom (0 to canvas.height)
- Center: (canvas.width / 2, canvas.height / 2)

**Rink Coordinate System:**
- Origin (0, 0): Center ice
- X-axis: Left to right (-100 to +100 feet)
- Y-axis: Top to bottom (-42.5 to +42.5 feet)
- Center: (0, 0)

### Coordinate Conversion

**Canvas to Rink:**
```typescript
function convertCanvasToRink(
  canvasX: number,
  canvasY: number,
  canvasWidth: number,
  canvasHeight: number
): { x: number, y: number } {
  const rinkX = (canvasX / canvasWidth) * 200 - 100  // -100 to +100
  const rinkY = (canvasY / canvasHeight) * 85 - 42.5  // -42.5 to +42.5
  
  return { x: rinkX, y: rinkY }
}
```

**Period Direction Handling:**
```typescript
function adjustXYForPeriod(
  x: number,
  y: number,
  period: number,
  homeAttacksRightP1: boolean
): { x: number, y: number } {
  // In even periods, flip X coordinate
  if (period % 2 === 0) {
    x = -x  // Flip horizontally
  }
  
  // If home attacks left in P1, flip all periods
  if (!homeAttacksRightP1) {
    x = -x
  }
  
  return { x, y }
}
```

**Zone Determination:**
```typescript
function getZoneFromXY(
  x: number,
  y: number,
  period: number,
  team: 'home' | 'away',
  homeAttacksRightP1: boolean
): 'Offensive' | 'Neutral' | 'Defensive' {
  const adjusted = adjustXYForPeriod(x, y, period, homeAttacksRightP1)
  
  // Neutral zone: -25 to +25 feet
  // Offensive zone: +25 to +100 feet
  // Defensive zone: -100 to -25 feet
  
  if (adjusted.x > 25) {
    return team === 'home' ? 'Offensive' : 'Defensive'
  } else if (adjusted.x < -25) {
    return team === 'home' ? 'Defensive' : 'Offensive'
  } else {
    return 'Neutral'
  }
}
```

---

## Export/Import

### Export Format

**Export Location:** `data/raw/games/{game_id}/{game_id}_tracking.xlsx`

**Events Sheet Columns:**
- `tracking_event_index` - Event sequence number
- `period` - Period number (1, 2, 3, OT)
- `time` - Time in period (MM:SS format)
- `Type` - Event type (Faceoff, Shot, Pass, Goal, etc.)
- `Detail` - Event detail (subtype)
- `Detail_2` - Secondary detail
- `Play_Detail` - Play context
- `Play_Detail_2` - Secondary play context
- `event_player_1` - Primary player
- `event_player_2` - Secondary player
- `event_player_3` - Tertiary player
- `puck_x` - Puck X coordinate (rink coordinates)
- `puck_y` - Puck Y coordinate (rink coordinates)
- `net_x` - Net X coordinate (if applicable)
- `net_y` - Net Y coordinate (if applicable)
- `team` - Team (Home/Away)
- `strength` - Game strength (5v5, PP, PK, etc.)
- `zone` - Zone (Offensive, Neutral, Defensive)

**Shifts Sheet Columns:**
- `shift_index` - Shift sequence number
- `Period` - Period number
- `shift_start` - Shift start time (MM:SS)
- `shift_end` - Shift end time (MM:SS)
- `player_id` - Player ID
- `player_number` - Jersey number
- `team` - Team (Home/Away)
- `shift_start_type` - How shift started
- `shift_end_type` - How shift ended
- `duration_seconds` - Shift duration in seconds

### Export Process

```typescript
function exportToExcel() {
  // Prepare events data
  const eventsData = S.events.map(event => ({
    tracking_event_index: event.event_index,
    period: event.period,
    time: event.time,
    Type: event.event_type,
    Detail: event.event_detail,
    Detail_2: event.event_detail_2,
    Play_Detail: event.play_detail,
    Play_Detail_2: event.play_detail_2,
    event_player_1: event.event_player_1,
    event_player_2: event.event_player_2,
    event_player_3: event.event_player_3,
    puck_x: event.puckXY ? event.puckXY[0] : null,
    puck_y: event.puckXY ? event.puckXY[1] : null,
    net_x: event.netXY ? event.netXY[0] : null,
    net_y: event.netXY ? event.netXY[1] : null,
    team: event.team,
    strength: event.strength,
    zone: event.zone
  }))
  
  // Prepare shifts data
  const shiftsData = S.shifts.map(shift => ({
    shift_index: shift.shift_index,
    Period: shift.period,
    shift_start: shift.startTime,
    shift_end: shift.endTime,
    player_id: shift.playerId,
    player_number: shift.playerNumber,
    team: shift.team,
    shift_start_type: shift.startType,
    shift_end_type: shift.endType,
    duration_seconds: shift.durationSeconds
  }))
  
  // Create Excel workbook
  const workbook = XLSX.utils.book_new()
  
  // Add events sheet
  const eventsSheet = XLSX.utils.json_to_sheet(eventsData)
  XLSX.utils.book_append_sheet(workbook, eventsSheet, 'events')
  
  // Add shifts sheet
  const shiftsSheet = XLSX.utils.json_to_sheet(shiftsData)
  XLSX.utils.book_append_sheet(workbook, shiftsSheet, 'shifts')
  
  // Write file
  const filename = `${S.gameId}_tracking.xlsx`
  XLSX.writeFile(workbook, filename)
}
```

---

## Dropdown Mapping

### UI Element to Supabase Table Map

| Circle | UI Element | Field Name | Supabase Table | Column Used | Status |
|--------|------------|------------|----------------|-------------|--------|
| 🔘 Gray | Event Type Buttons | `event_type` | `dim_event_type` | `event_type_code` | ✅ Fixed in v22.1 |
| 🔵 Blue | DETAIL 1 | `event_detail` | `dim_event_detail` | `event_detail_name` | ✅ Working |
| 🟣 Pink | DETAIL 2 | `event_detail_2` | `dim_event_detail_2` | `event_detail_2_name` | ✅ Working |
| 🟢 Green | PLAY DETAIL 1 | `play_detail` | `dim_play_detail` | `play_detail_name` | ✅ Working |
| 🔴 Red | PLAY DETAIL 2 | `play_detail_2` | `dim_play_detail_2` | `play_detail_2_name` | ✅ Working |

### Supabase Table Structure

**dim_event_type (23 rows):**
- `event_type_id` - Primary key
- `event_type_code` - Code (Faceoff, Shot, etc.)
- `event_type_name` - Display name

**dim_event_detail (49 rows):**
- `event_detail_id` - Primary key
- `event_detail_code` - Code
- `event_detail_name` - Display name
- `event_type` - Related event type

**dim_event_detail_2 (176 rows):**
- `event_detail_2_id` - Primary key
- `event_detail_2_code` - Code
- `event_detail_2_name` - Display name

**dim_play_detail (111 rows):**
- `play_detail_id` - Primary key
- `play_detail_code` - Code
- `play_detail_name` - Display name
- `play_category` - Category

**dim_play_detail_2 (111 rows):**
- `play_detail_2_id` - Primary key
- `play_detail_2_code` - Code
- `play_detail_2_name` - Display name
- `play_category` - Category

---

## Feature Inventory

### Core Features (100+)

**1. Event Management**
- 15+ event types (Faceoff, Shot, Pass, Goal, Turnover, etc.)
- Create, edit, delete events
- Event validation
- Event linking
- Event search/filter

**2. Shift Management**
- Create, edit, delete shifts
- Shift duration calculation
- TOI calculation
- Line combination analysis

**3. Player Management**
- Load roster from Supabase
- Player selection
- On-ice slot assignment
- Player search/filter

**4. XY Positioning**
- Rink coordinate system
- Canvas to rink conversion
- Period direction handling
- Zone determination
- XY validation

**5. Video Integration**
- HTML5 video support
- YouTube video support
- Auto-sync video to event
- Period markers
- Intermission handling

**6. Time/Period Management**
- Period switching
- Time formatting
- Time validation
- Total seconds calculation

**7. Export/Import**
- Excel export (.xlsx)
- CSV export
- Export validation
- Import from Excel/CSV

**8. State Management**
- localStorage persistence
- Supabase sync
- Auto-save (30-second interval)
- State recovery

**9. UI/UX Features**
- Modal dialogs
- Toast notifications
- Form validation
- Keyboard shortcuts
- Responsive design

**10. Data Validation**
- Event validation
- Shift validation
- XY validation
- Time validation
- Export validation

**11. Supabase Integration**
- Connect to Supabase
- Load reference data
- Load rosters
- Save events/shifts
- State sync

**12. Game Management**
- Select game
- Load game data
- Create new game
- Game metadata

### Advanced Features

**13. Event Linking**
- Link shot to goal
- Link pass to shot
- Linked event navigation

**14. Shift Analytics**
- Line combination analysis
- Shift duration analysis
- TOI calculation
- Player usage

**15. Data Quality**
- Data completeness checks
- Data consistency checks
- Missing data detection

---

## Key Algorithms

### Event Time Calculation

```javascript
function calculateEventTime(period, timeString) {
  const periodStart = (period - 1) * periodLength
  const periodTime = parseTime(timeString)
  return periodStart + periodTime
}
```

### XY Coordinate Conversion

```javascript
function convertXYToRink(x, y, period, homeAttacksRight) {
  if (period % 2 === 0) {
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

*Last Updated: 2026-01-15*
