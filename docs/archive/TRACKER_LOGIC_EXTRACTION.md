# Tracker Logic Extraction

**Complete extraction of all logic from tracker_index_v23.5.html**

Last Updated: 2026-01-21
Source: `ui/tracker/tracker_index_v23.5.html` (16,162 lines)  
Purpose: Document all logic for Next.js rebuild

---

## Overview

This document extracts ALL logic, functions, and patterns from the current tracker HTML file to inform the Next.js rebuild. The tracker has **16,162 lines** of code with approximately **200+ functions**.

---

## State Management (S Object)

### Global State Structure

```javascript
const S = {
  // Supabase connection
  sb: null,
  connected: false,
  
  // Game info
  gameId: null,
  games: [],
  homeTeam: 'Home',
  awayTeam: 'Away',
  homeColor: '#3b82f6',
  awayColor: '#ef4444',
  homeLogo: null,
  awayLogo: null,
  teams: {},
  
  // Reference data from Supabase
  playDetails1: [],      // dim_play_detail
  playDetails2: [],      // dim_play_detail_2
  eventDetails1: [],     // dim_event_detail
  eventDetails2: [],     // dim_event_detail_2
  eventTypesDB: [],      // dim_event_type
  showAllEventTypes: false,
  playerRoles: [],       // dim_player_role
  
  // Period/Time
  period: 1,
  evtTeam: 'home',
  periodLengths: { 1: 18, 2: 18, 3: 18, OT: 5 },
  periodLength: 18,      // Legacy - use getPeriodLength()
  homeAttacksRightP1: true,
  
  // On-ice slots
  slots: {
    home: { F1: null, F2: null, F3: null, D1: null, D2: null, G: null, X: null },
    away: { F1: null, F2: null, F3: null, D1: null, D2: null, G: null, X: null }
  },
  selectedSlot: null,
  
  // Events and shifts
  events: [],
  shifts: [],
  evtIdx: 0,
  shiftIdx: 0,
  
  // Current event being edited
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
  
  // XY positioning
  xyMode: 'puck',        // 'puck' or 'player'
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
    intermission1: 900,  // 15 min
    intermission2: 900,
    intermission3: 300,  // 5 min
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

## Reference Data (LISTS Object)

### Event Types

```javascript
const LISTS = {
  eventTypes: [
    'Faceoff', 'Shot', 'Pass', 'Goal', 'Turnover',
    'Zone_Entry_Exit', 'Penalty', 'Stoppage', 'Possession',
    'Save', 'Rebound', 'DeadIce', 'Play', 'Intermission',
    'Clockstop', 'Timeout'
  ],
  
  hotkeys: {
    Faceoff: 'F',
    Shot: 'S',
    Pass: 'P',
    Goal: 'G',
    Turnover: 'T',
    Zone_Entry_Exit: 'Z',
    Penalty: 'N',
    Stoppage: 'X',
    Possession: 'O',
    Save: 'V',
    Rebound: 'R',
    DeadIce: 'D',
    Play: 'Y',
    Intermission: 'I',
    Clockstop: 'C'
  },
  
  // Event details (detail1 and detail2 options per event type)
  details: {
    Shot: {
      d1: ['Shot_OnNetSaved', 'Shot_Missed', 'Shot_Blocked', 
           'Shot_BlockedSameTeam', 'Shot_Deflected', 'Shot_OnNetGoal'],
      d2: ['Shot-Wrist', 'Shot-Slap', 'Shot-Backhand', 'Shot-Snap',
           'Shot-WrapAround', 'Shot-Bat', 'Shot-Poke', 'Shot-OneTime',
           'Shot-Tip', 'Shot-Deflection', 'Shot-Other']
    },
    // ... (similar for all event types)
  },
  
  shiftStart: [
    'GameStart', 'PeriodStart', 'FaceoffAfterGoal',
    'FaceoffAfterPenalty', 'OtherFaceoff', 'Stoppage',
    'Intermission', 'OnTheFly'
  ],
  
  shiftStop: [
    '', 'OnTheFly', 'PeriodEnd', 'Period End',
    'GoalScored', 'Home Goal', 'Away Goal', 'Penalty',
    'Stoppage', 'OtherFaceoff', 'Intermission', 'GameEnd',
    // ... more
  ],
  
  nextEventSuggestions: {
    'Faceoff': ['Pass', 'Possession', 'Turnover'],
    'Pass': ['Shot', 'Pass', 'Turnover', 'Zone_Entry_Exit'],
    'Shot': ['Save', 'Goal', 'Rebound'],
    'Save': ['Rebound', 'Pass', 'Stoppage'],
    'Goal': ['Faceoff', 'Stoppage'],
    // ... more
  },
  
  linkedEvents: {
    'Shot': ['Pass', 'Rebound'],
    'Goal': ['Shot', 'Pass'],
    'Save': ['Shot'],
    'Rebound': ['Shot', 'Save']
  }
}
```

---

## Function Categories

### 1. Initialization & Setup

**Functions:**
- `init()` - Main initialization function
- `loadSettings()` - Load settings from localStorage
- `saveSettings()` - Save settings to localStorage
- `setupRinkEventListeners()` - Set up rink mouse handlers
- `tryConnect()` - Connect to Supabase
- `loadReferenceData()` - Load reference data from Supabase
- `buildUI()` - Build initial UI
- `loadFromStorage()` - Load saved game data from localStorage
- `setupKeys()` - Set up keyboard shortcuts
- `setupTimeInputs()` - Auto-format time inputs
- `startAutoSave()` - Start auto-save timer

**Key Logic:**
- Auto-loads last game from localStorage
- Connects to Supabase for reference data
- Sets up event listeners
- Initializes UI state

---

### 2. Period & Time Management

**Functions:**
- `getPeriodLength(period)` - Get period length in minutes
- `getPeriodLengthSeconds(period)` - Get period length in seconds
- `updatePeriodLengthsFromUI()` - Update period lengths from UI inputs
- `updatePeriodLengthIndicator()` - Update period length indicator in header
- `updatePeriodLengthsUI()` - Update UI inputs from periodLengths
- `getElapsedAtPeriodStart(period)` - Calculate elapsed time at period start (for video sync)
- `parseTime(timeStr)` - Parse time string "MM:SS" to seconds
- `formatTOI(seconds)` - Format time-on-ice as "MM:SS"
- `formatVideoTime(sec)` - Format video time as "HH:MM:SS"

**Key Logic:**
- Supports variable period lengths (P1, P2, P3, OT can differ)
- Calculates running time for video sync
- Handles period-specific time calculations

---

### 3. Video Player Integration

**Functions:**
- `loadVideo(url, name)` - Load video (YouTube or local)
- `extractYouTubeId(url)` - Extract YouTube ID from URL
- `loadYouTubeVideo(videoId)` - Load YouTube video
- `createYouTubePlayer(videoId)` - Create YouTube IFrame API player
- `onYouTubePlayerReady(event)` - YouTube player ready callback
- `onYouTubePlayerStateChange(event)` - YouTube player state change callback
- `loadLocalVideo(url)` - Load local video file
- `loadVideoFromFile(event)` - Handle file input for video
- `videoPlayPause()` - Toggle play/pause
- `videoSeek(deltaSec)` - Seek video by delta seconds
- `videoSeekTo(timeSec)` - Seek video to specific time
- `videoFrameStep(frames)` - Step video frame by frame
- `setVideoSpeed(speed)` - Set playback speed (0.25, 0.5, 1, 1.5, 2)
- `getVideoSpeed()` - Get current playback speed
- `getVideoCurrentTime()` - Get current video time in seconds
- `getVideoDuration()` - Get video duration in seconds
- `startVideoTimeUpdate()` - Start video time update loop
- `calculateGameTimeFromVideo(videoSec)` - Convert video time to game time
- `captureStartTime()` - Capture video time to start_time field
- `captureEndTime()` - Capture video time to end_time field
- `toggleVideoAutoSync()` - Toggle auto-sync mode
- `setGameMarker(markerName)` - Set period marker (P1Start, P1End, etc.)
- `jumpToMarker(markerName)` - Jump video to marker
- `addStoppageMarker()` - Add stoppage marker
- `setVideoZoom(zoom)` - Set video zoom level
- `addVideoSource(name, url, hotkey)` - Add video source
- `switchVideoSource()` - Switch active video source
- `saveVideoSources()` - Save video sources to localStorage
- `loadVideoSources()` - Load video sources from localStorage

**Key Logic:**
- Supports YouTube and local video files
- Video sync with game clock (handles intermissions, stoppages)
- Multiple video sources (camera angles)
- Period markers for video sync
- Auto-sync mode (auto-populate times from video)

---

### 4. Event Management

**Functions:**
- `addEvent()` - Add new event
- `editEvent(idx)` - Edit existing event
- `saveEditEvent()` - Save edited event
- `deleteEvent()` - Delete event
- `insertEventBefore()` - Insert event before current
- `logEvent()` - Log event with validation
- `validateEvent()` - Validate event data
- `setEvtType(type)` - Set event type
- `updateEventTypeUI()` - Update event type UI
- `renderEvents()` - Render event list
- `renderEventItem(evt, idx)` - Render single event row
- `selectEvent(idx)` - Select event for editing
- `updateLinkedEventsDropdown()` - Update linked events dropdown
- `applyLinkedEventData()` - Apply data from linked event
- `updateNextPlaySuggestions()` - Update suggested next events
- `selectNextEvent(type)` - Select suggested next event

**Key Logic:**
- Event validation before logging
- Event linking (Shot→Save, Pass→Shot, etc.)
- Event suggestions based on last event
- Event editing and deletion
- Event list rendering with filtering

---

### 5. Shift Management

**Functions:**
- `addShift()` - Add new shift
- `editShift(idx)` - Edit existing shift
- `saveEditShift()` - Save edited shift
- `deleteShift()` - Delete shift
- `insertShiftBefore()` - Insert shift before current
- `logShift()` - Log shift with validation
- `deriveShiftStopType()` - Auto-derive shift stop type from events
- `renderShiftLog()` - Render shift list
- `renderShiftItem(shift, idx)` - Render single shift row
- `selectShift(idx)` - Select shift for editing
- `editShiftPlayers(shiftIdx)` - Edit shift players
- `saveShiftPlayers()` - Save shift players
- `clearShiftPlayers()` - Clear shift players
- `calculateTOI()` - Calculate time-on-ice from shifts

**Key Logic:**
- Shift validation before logging
- Auto-derive shift stop type from last event
- Shift player management (on-ice roster)
- Time-on-ice calculation
- Shift editing and deletion

---

### 6. Player Management

**Functions:**
- `addPlayer(player)` - Add player to current event
- `removePlayer(player)` - Remove player from current event
- `selectPlayer(player)` - Select player
- `assignPlayerRole(player, role)` - Assign player role (E1, E2, O1, etc.)
- `addToRecentPlayers(player)` - Add to recent players list
- `renderRecentPlayers()` - Render recent players bar
- `quickAddRecentPlayer(num, team)` - Quick add recent player
- `loadRoster(team)` - Load roster from Supabase
- `renderRoster(team)` - Render roster display
- `searchPlayers(query)` - Search players in roster

**Key Logic:**
- Player role assignment (event_team_player_1, opponent_player_1, etc.)
- Recent players tracking
- Roster loading from Supabase
- Player search/filtering

---

### 7. XY Positioning (Rink)

**Functions:**
- `handleRinkClick(e)` - Handle rink click for XY positioning
- `handleRinkMouseDown(e)` - Handle rink mouse down
- `handleRinkMouseMove(e)` - Handle rink mouse move
- `handleRinkMouseUp(e)` - Handle rink mouse up
- `placeXY(x, y, mode)` - Place XY coordinate
- `clearXY()` - Clear XY coordinates
- `undoXY()` - Undo last XY placement
- `toggleXYMode()` - Toggle puck/player mode
- `calculateZone()` - Calculate zone from XY position
- `renderXYMarkers()` - Render XY markers on rink
- `updateXYControls()` - Update XY control UI
- `handleRinkHover(e)` - Handle rink hover for tooltip
- `showXYTooltip(x, y)` - Show XY tooltip
- `hideXYTooltip()` - Hide XY tooltip

**Key Logic:**
- Click rink to place XY coordinates
- Drag to create trajectory (shot, pass)
- Puck mode vs Player mode
- Zone calculation from XY (offensive, neutral, defensive)
- XY coordinate storage (array of {x, y})
- Net target positioning (for shots)

---

### 8. Slot Management (On-Ice Roster)

**Functions:**
- `renderSlots()` - Render on-ice slots
- `clearSlot(team, pos)` - Clear slot
- `fillSlot(team, pos, player)` - Fill slot with player
- `setupSlotDragDrop()` - Set up drag and drop for slots
- `handleSlotDragStart(e)` - Handle slot drag start
- `handleSlotDragOver(e)` - Handle slot drag over
- `handleSlotDrop(e)` - Handle slot drop
- `deriveStrength()` - Calculate game strength from slots (5v5, 5v4, etc.)

**Key Logic:**
- On-ice roster tracking (F1, F2, F3, D1, D2, G, X slots)
- Drag and drop for slot management
- Strength calculation (5v5, 5v4, 4v5, etc.)
- Empty net detection

---

### 9. Auto-Functions & Derivation

**Functions:**
- `autoZone()` - Auto-detect zone from XY
- `autoSuccess()` - Auto-derive success indicator
- `autoSideOfPuck()` - Auto-calculate side of puck
- `autoStrength()` - Auto-calculate game strength
- `deriveSuccess()` - Derive success from event type/detail
- `deriveStrength()` - Derive strength from slots
- `calculateZone()` - Calculate zone from XY position

**Key Logic:**
- Automatic field population
- Zone detection from XY coordinates
- Success derivation from event details
- Strength calculation from on-ice players

---

### 10. Data Export & Import

**Functions:**
- `exportData()` - Export to Excel format
- `importExcel(file)` - Import from Excel
- `exportSettings()` - Export settings to JSON
- `importSettings(file)` - Import settings from JSON
- `validateImportData(data)` - Validate imported data

**Key Logic:**
- Excel export matches ETL format (events, shifts, metadata sheets)
- LONG format export (one row per player per event)
- Import validation and mapping
- Settings import/export

---

### 11. UI Rendering

**Functions:**
- `buildUI()` - Build initial UI
- `renderEvents()` - Render event list
- `renderShiftLog()` - Render shift list
- `renderRoster(team)` - Render roster
- `renderQuickAdd()` - Render quick add buttons
- `renderMarkers()` - Render XY markers on rink
- `updateScores()` - Update score display
- `updateBoxScore()` - Update box score
- `updateClock()` - Update game clock
- `updateStrength()` - Update strength indicator
- `updateSaveIndicator()` - Update save status indicator

**Key Logic:**
- Event list rendering with filtering
- Shift list rendering
- Real-time UI updates
- Status indicators

---

### 12. Modal Management

**Functions:**
- `openSettings()` - Open settings modal
- `closeSettings()` - Close settings modal
- `openHelp()` - Open help modal
- `closeHelp()` - Close help modal
- `openVideoTimingModal()` - Open video timing modal
- `closeVideoTimingModal()` - Close video timing modal
- `openEditModal()` - Open event edit modal
- `closeEditModal()` - Close event edit modal
- `openEditShiftModal()` - Open shift edit modal
- `closeEditShiftModal()` - Close shift edit modal

**Key Logic:**
- Modal show/hide management
- Form data handling
- Validation before close

---

### 13. Keyboard Shortcuts

**Functions:**
- `setupKeys()` - Set up keyboard shortcuts
- `handleKeyPress(e)` - Handle key press
- `handleKeyDown(e)` - Handle key down
- `handleKeyUp(e)` - Handle key up

**Key Shortcuts:**
- Event types: `F` (Faceoff), `S` (Shot), `P` (Pass), `G` (Goal), etc.
- Zones: `Q` (Offensive), `W` (Neutral), `E` (Defensive)
- Video: `Space` (Play/Pause), `←→` (Seek), `↑↓` (Speed)
- Logging: `Enter` (Log event), `Escape` (Cancel)

**Key Logic:**
- Comprehensive keyboard shortcuts
- Hotkey support for video sources (1-9)
- Keyboard XY placement
- Modal keyboard handling

---

### 14. Persistence & Sync

**Functions:**
- `autoSave()` - Auto-save to localStorage
- `saveGameData()` - Manual save
- `loadFromStorage()` - Load from localStorage
- `saveToSupabase()` - Save to Supabase (future)
- `loadFromSupabase()` - Load from Supabase (future)

**Key Logic:**
- Auto-save every 30 seconds (configurable)
- localStorage key: `bs_{gameId}`
- Save format: JSON (events, shifts, state)
- Load on page load

---

### 15. Game Management

**Functions:**
- `loadGames()` - Load games from Supabase
- `selectGame(gameId)` - Select game
- `createGame()` - Create new game
- `deleteGame(gameId)` - Delete game
- `loadRosters()` - Load rosters for game
- `loadGameData()` - Load saved game data

**Key Logic:**
- Game selection from Supabase
- Roster loading per game
- Game state loading from localStorage
- Game creation/deletion

---

### 16. Validation & Error Handling

**Functions:**
- `validateEvent(evt)` - Validate event data
- `validateShift(shift)` - Validate shift data
- `showError(msg)` - Show error message
- `toast(msg, type)` - Show toast notification
- `confirmAction(msg)` - Confirm action

**Key Logic:**
- Event validation (required fields, data types)
- Shift validation (time ranges, players)
- Error messages and notifications
- Confirmation dialogs

---

## Key Business Rules

### Event Rules
1. **Event Types:** 16 event types (Faceoff, Shot, Pass, Goal, etc.)
2. **Event Details:** Each event type has detail1 and detail2 options
3. **Event Linking:** Events can link to each other (Shot→Save, Pass→Shot)
4. **Event Validation:** Type, time, team are required
5. **Event Indexing:** Events have sequential index (idx)

### Shift Rules
1. **Shift Structure:** Start time, end time, players on ice
2. **Shift Types:** Start type (OnTheFly, Faceoff, etc.) and stop type
3. **Shift Stop Type:** Auto-derived from last event in shift
4. **Time Validation:** End time must be after start time
5. **Player Slots:** F1, F2, F3, D1, D2, G, X positions

### XY Positioning Rules
1. **Puck Mode:** Click places puck trajectory points
2. **Player Mode:** Click places selected player position
3. **Zone Detection:** Zone (o/n/d) calculated from XY position
4. **Net Target:** Shots require net target XY
5. **Trajectory:** Drag creates trajectory (shot or pass)

### Video Sync Rules
1. **Period Markers:** Mark when each period starts/ends in video
2. **Time Conversion:** Video time → game time (accounts for intermissions)
3. **Auto-Sync:** Auto-populate times from video
4. **Stoppages:** Track stoppages that affect time sync

### Strength Calculation Rules
1. **Count Players:** Count players on ice per team
2. **Goalie Detection:** Detect if goalie is on ice
3. **Calculate Skaters:** Subtract goalie from total
4. **Format:** "5v5", "5v4", "4v5", etc.
5. **Empty Net:** "ENH" (home empty), "ENA" (away empty)

---

## Data Structures

### Event Object
```javascript
{
  idx: 0,                    // Event index
  eventId: 'EV1896901058',   // Unique ID
  period: 1,                 // Period (1, 2, 3, 4)
  start_time: '12:30',     // Start time (MM:SS)
  end_time: '12:35',        // End time (MM:SS)
  type: 'Shot',              // Event type
  detail1: 'Shot_OnNetSaved', // Primary detail
  detail2: 'Shot-Wrist',     // Secondary detail
  team: 'home',              // Team ('home' or 'away')
  zone: 'o',                 // Zone ('o', 'n', 'd')
  success: true,             // Success indicator
  strength: '5v5',           // Game strength
  players: [...],            // Array of Player objects
  puckXY: [{x: 50, y: 30}], // Puck trajectory
  netXY: {x: 89, y: 0},     // Net target
  isHighlight: false,        // Highlight flag
  linkedEventIdx: null,      // Linked event index
  videoTime: 125.5          // Video timestamp (seconds)
}
```

### Shift Object
```javascript
{
  idx: 0,                    // Shift index
  shiftId: 'SH123',          // Unique ID
  period: 1,                 // Period
  start_time: '12:00',       // Start time
  end_time: '14:30',         // End time
  start_type: 'OnTheFly',    // How shift started
  stop_type: 'OnTheFly',     // How shift ended
  strength: '5v5',           // Game strength
  home: {                    // Home lineup
    F1: {num: '10', name: 'Smith'},
    F2: {num: '20', name: 'Jones'},
    // ...
  },
  away: {                    // Away lineup
    // ...
  }
}
```

### Player Object
```javascript
{
  num: '10',                 // Jersey number
  name: 'John Smith',        // Player name
  team: 'home',              // Team
  role: 'event_team_player_1', // Role (E1, E2, O1, etc.)
  position: 'F',             // Position (F, D, G)
  xy: [{x: 50, y: 30}]       // Player XY positions
}
```

---

## Utility Functions

**Time Utilities:**
- `parseTime(timeStr)` - Parse "MM:SS" to seconds
- `formatTime(seconds)` - Format seconds to "MM:SS"
- `formatTOI(seconds)` - Format time-on-ice
- `calculateRunningTime(period, time)` - Calculate running time

**XY Utilities:**
- `calculateZone(x, y)` - Calculate zone from XY
- `normalizeXY(x, y, period)` - Normalize XY for period
- `distance(x1, y1, x2, y2)` - Calculate distance

**Validation Utilities:**
- `validateTime(timeStr)` - Validate time format
- `validateJersey(num)` - Validate jersey number
- `validatePeriod(period)` - Validate period (1-4)

**Data Utilities:**
- `generateEventId()` - Generate unique event ID
- `generateShiftId()` - Generate unique shift ID
- `deepClone(obj)` - Deep clone object
- `formatDate(date)` - Format date

---

## Next Steps for Rebuild

1. **Convert State to React State/Zustand**
   - Transform `S` object to React state or Zustand store
   - Handle state updates with React patterns

2. **Extract Functions to Modules**
   - Create `lib/tracker/events.ts` - Event functions
   - Create `lib/tracker/shifts.ts` - Shift functions
   - Create `lib/tracker/video.ts` - Video functions
   - Create `lib/tracker/xy.ts` - XY positioning functions
   - Create `lib/tracker/export.ts` - Export functions
   - Create `lib/tracker/utils.ts` - Utility functions

3. **Create React Components**
   - Convert UI rendering functions to React components
   - Use React hooks for state management
   - Use React patterns for event handling

4. **TypeScript Conversion**
   - Convert all functions to TypeScript
   - Add proper type annotations
   - Use extracted types from `types.ts`

5. **Testing**
   - Unit test utility functions
   - Integration test core logic
   - Component testing

---

*Document created: 2026-01-13*  
*This is a comprehensive extraction - will be updated as rebuild progresses*
