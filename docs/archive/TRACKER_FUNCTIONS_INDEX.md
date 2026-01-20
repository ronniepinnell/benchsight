# Tracker Functions Index

**Complete index of all functions in tracker_index_v23.5.html**

Last Updated: 2026-01-13  
Source: `ui/tracker/tracker_index_v23.5.html` (16,162 lines)  
Total Functions: ~200+ functions

---

## Function Categories

This document indexes all functions by category. For detailed logic extraction, see `TRACKER_LOGIC_EXTRACTION.md`.

---

## 1. Initialization & Setup (12 functions)

1. `init()` - Main initialization function
2. `loadSettings()` - Load settings from localStorage
3. `saveSettings()` - Save settings to localStorage
4. `setupRinkEventListeners()` - Set up rink mouse handlers
5. `tryConnect()` - Connect to Supabase
6. `loadReferenceData()` - Load reference data from Supabase
7. `buildUI()` - Build initial UI
8. `loadFromStorage()` - Load saved game data
9. `setupKeys()` - Set up keyboard shortcuts
10. `setupTimeInputs()` - Auto-format time inputs
11. `startAutoSave()` - Start auto-save timer
12. `loadGames()` - Load games from Supabase

---

## 2. Period & Time Management (9 functions)

1. `getPeriodLength(period)` - Get period length in minutes
2. `getPeriodLengthSeconds(period)` - Get period length in seconds
3. `updatePeriodLengthsFromUI()` - Update period lengths from UI
4. `updatePeriodLengthIndicator()` - Update period length indicator
5. `updatePeriodLengthsUI()` - Update UI inputs from periodLengths
6. `getElapsedAtPeriodStart(period)` - Calculate elapsed time at period start
7. `parseTime(timeStr)` - Parse "MM:SS" to seconds
8. `formatTOI(seconds)` - Format time-on-ice as "MM:SS"
9. `formatVideoTime(sec)` - Format video time as "HH:MM:SS"

---

## 3. Video Player Integration (35+ functions)

1. `loadVideo(url, name)` - Load video (YouTube/local)
2. `extractYouTubeId(url)` - Extract YouTube ID from URL
3. `loadYouTubeVideo(videoId)` - Load YouTube video
4. `createYouTubePlayer(videoId)` - Create YouTube IFrame API player
5. `onYouTubePlayerReady(event)` - YouTube player ready callback
6. `onYouTubePlayerStateChange(event)` - YouTube player state change callback
7. `loadLocalVideo(url)` - Load local video file
8. `loadVideoFromFile(event)` - Handle file input for video
9. `videoPlayPause()` - Toggle play/pause
10. `videoSeek(deltaSec)` - Seek video by delta seconds
11. `videoSeekTo(timeSec)` - Seek video to specific time
12. `videoFrameStep(frames)` - Step video frame by frame
13. `setVideoSpeed(speed)` - Set playback speed
14. `getVideoSpeed()` - Get current playback speed
15. `getVideoCurrentTime()` - Get current video time
16. `getVideoDuration()` - Get video duration
17. `startVideoTimeUpdate()` - Start video time update loop
18. `calculateGameTimeFromVideo(videoSec)` - Convert video time to game time
19. `captureStartTime()` - Capture video time to start_time field
20. `captureEndTime()` - Capture video time to end_time field
21. `toggleVideoAutoSync()` - Toggle auto-sync mode
22. `setGameMarker(markerName)` - Set period marker
23. `jumpToMarker(markerName)` - Jump video to marker
24. `addStoppageMarker()` - Add stoppage marker
25. `setVideoZoom(zoom)` - Set video zoom level
26. `videoZoomIn()` - Zoom video in
27. `videoZoomOut()` - Zoom video out
28. `videoZoomReset()` - Reset video zoom
29. `addVideoSource(name, url, hotkey)` - Add video source
30. `switchVideoSource()` - Switch active video source
31. `saveVideoSources()` - Save video sources
32. `loadVideoSources()` - Load video sources
33. `calculateRunningVideoTime(period, gameTime)` - Calculate running video time
34. `updateVideoTimingPreview()` - Update video timing preview
35. `toggleVideoSection()` - Toggle video section visibility

---

## 4. Event Management (25+ functions)

1. `logEvent()` - Log event (with confirmation)
2. `logEventDirect()` - Log event directly (no confirmation)
3. `doLogEvent()` - Execute event logging (from confirmation modal)
4. `addEvent()` - Add new event (internal)
5. `editEvent(idx)` - Edit existing event
6. `saveEditEvent()` - Save edited event
7. `deleteEvent()` - Delete event
8. `insertEventBefore()` - Insert event before current
9. `validateEvent(evt)` - Validate event data
10. `setEvtType(type)` - Set event type
11. `updateEventTypeUI()` - Update event type UI
12. `renderEvents()` - Render event list
13. `renderEventItem(evt, idx)` - Render single event row
14. `selectEvent(idx)` - Select event for editing
15. `updateLinkedEventsDropdown()` - Update linked events dropdown
16. `applyLinkedEventData()` - Apply data from linked event
17. `updateNextPlaySuggestions()` - Update suggested next events
18. `selectNextEvent(type)` - Select suggested next event
19. `onLinkedEvtChange()` - Handle linked event change
20. `clearCurrentEvent()` - Clear current event form
21. `copyEventData(fromIdx, toIdx)` - Copy event data
22. `duplicateEvent(idx)` - Duplicate event
23. `moveEvent(idx, direction)` - Move event up/down
24. `filterEvents(criteria)` - Filter events
25. `sortEvents(criteria)` - Sort events

---

## 5. Shift Management (20+ functions)

1. `logShift()` - Log shift
2. `addShift()` - Add new shift (internal)
3. `editShift(idx)` - Edit existing shift
4. `saveEditShift()` - Save edited shift
5. `deleteShift()` - Delete shift
6. `insertShiftBefore()` - Insert shift before current
7. `validateShift(shift)` - Validate shift data
8. `deriveShiftStartType(idx)` - Auto-derive shift start type
9. `deriveShiftStopType()` - Auto-derive shift stop type
10. `renderShiftLog()` - Render shift list
11. `renderShiftItem(shift, idx)` - Render single shift row
12. `selectShift(idx)` - Select shift for editing
13. `editShiftPlayers(shiftIdx)` - Edit shift players
14. `saveShiftPlayers()` - Save shift players
15. `clearShiftPlayers()` - Clear shift players
16. `calculateTOI()` - Calculate time-on-ice from shifts
17. `calculateShiftDuration(shift)` - Calculate shift duration
18. `calculateShiftStoppageTime(shift)` - Calculate stoppage time
19. `updateShiftStrength(shift)` - Update shift strength
20. `getPlayersOnIce(shift)` - Get players on ice for shift

---

## 6. Player Management (15+ functions)

1. `addPlayer(player)` - Add player to current event
2. `removePlayer(player)` - Remove player from current event
3. `selectPlayer(player)` - Select player
4. `assignPlayerRole(player, role)` - Assign player role
5. `addToRecentPlayers(player)` - Add to recent players list
6. `renderRecentPlayers()` - Render recent players bar
7. `quickAddRecentPlayer(num, team)` - Quick add recent player
8. `loadRoster(team)` - Load roster from Supabase
9. `renderRoster(team)` - Render roster display
10. `searchPlayers(query)` - Search players in roster
11. `filterRoster(team, criteria)` - Filter roster
12. `getPlayerByNumber(num, team)` - Get player by jersey number
13. `getPlayerById(id, team)` - Get player by ID
14. `normalizePosition(pos)` - Normalize position (F/D/G)
15. `generateDemoRosters()` - Generate demo rosters

---

## 7. XY Positioning / Rink (20+ functions)

1. `handleRinkClick(e)` - Handle rink click for XY positioning
2. `handleRinkMouseDown(e)` - Handle rink mouse down
3. `handleRinkMouseMove(e)` - Handle rink mouse move
4. `handleRinkMouseUp(e)` - Handle rink mouse up
5. `handleRinkHover(e)` - Handle rink hover for tooltip
6. `placeXY(x, y, mode)` - Place XY coordinate
7. `handleXYPlacement(x, y)` - Handle XY placement logic
8. `clearXY()` - Clear XY coordinates
9. `undoXY()` - Undo last XY placement
10. `toggleXYMode()` - Toggle puck/player mode
11. `calculateZone()` - Calculate zone from XY position
12. `calculateZoneFromXY(x, y)` - Calculate zone from XY coordinates
13. `renderXYMarkers()` - Render XY markers on rink
14. `updateXYControls()` - Update XY control UI
15. `showXYTooltip(x, y)` - Show XY tooltip
16. `hideXYTooltip()` - Hide XY tooltip
17. `applyMirror(x, y)` - Apply mirror mode (period 2)
18. `normalizeXY(x, y, period)` - Normalize XY for period
19. `calculateDistance(x1, y1, x2, y2)` - Calculate distance
20. `toggleKeyboardXYMode()` - Toggle keyboard XY mode (WASD)

---

## 8. Slot Management (On-Ice Roster) (10+ functions)

1. `renderSlots()` - Render on-ice slots
2. `clearSlot(team, pos)` - Clear slot
3. `fillSlot(team, pos, player)` - Fill slot with player
4. `setupSlotDragDrop()` - Set up drag and drop for slots
5. `handleSlotDragStart(e)` - Handle slot drag start
6. `handleSlotDragOver(e)` - Handle slot drag over
7. `handleSlotDrop(e)` - Handle slot drop
8. `deriveStrength()` - Calculate game strength from slots
9. `updateStrengthFromSlots()` - Update strength indicator
10. `onSlotsChanged()` - Handle slot changes

---

## 9. Auto-Functions & Derivation (10+ functions)

1. `autoZone()` - Auto-detect zone from XY
2. `autoSuccess()` - Auto-derive success indicator
3. `autoSideOfPuck()` - Auto-calculate side of puck
4. `autoStrength()` - Auto-calculate game strength
5. `deriveSuccess()` - Derive success from event type/detail
6. `derivePlayerSuccess()` - Derive player success from event
7. `autoCalcPressure()` - Auto-calculate pressure
8. `detectPressure()` - Detect pressure for event players
9. `updatePlayD2()` - Update Play Detail 2 dropdown
10. `applySmartDefaults(type)` - Apply smart defaults from patterns

---

## 10. Data Export & Import (10+ functions)

1. `exportData()` - Export to Excel format
2. `importExcel(file)` - Import from Excel
3. `exportSettings()` - Export settings to JSON
4. `importSettings(file)` - Import settings from JSON
5. `validateImportData(data)` - Validate imported data
6. `parseExcelFile(file)` - Parse Excel file
7. `mapImportData(data)` - Map imported data to tracker format
8. `generateEventId()` - Generate unique event ID
9. `generateShiftId()` - Generate unique shift ID
10. `formatExportEvent(evt)` - Format event for export

---

## 11. UI Rendering (20+ functions)

1. `buildUI()` - Build initial UI
2. `renderEvents()` - Render event list
3. `renderShiftLog()` - Render shift list
4. `renderRoster(team)` - Render roster
5. `renderQuickAdd()` - Render quick add buttons
6. `renderMarkers()` - Render XY markers on rink
7. `updateScores()` - Update score display
8. `updateBoxScore()` - Update box score
9. `updateClock()` - Update game clock
10. `updateStrength()` - Update strength indicator
11. `updateSaveIndicator()` - Update save status indicator
12. `renderAll()` - Render all UI elements
13. `updateZoneDisplay()` - Update zone display
14. `updateZoneLabels()` - Update zone labels on rink
15. `updateTeamLogos()` - Update team logos
16. `updateQuickStats()` - Update quick stats display
17. `updatePeriodProgress()` - Update period progress ring
18. `updateProgressBar()` - Update progress bar
19. `renderShotChartOverlay()` - Render shot chart overlay
20. `refreshShotChartOverlay()` - Refresh shot chart overlay

---

## 12. Modal Management (15+ functions)

1. `openSettings()` - Open settings modal
2. `closeSettings()` - Close settings modal
3. `openHelp()` - Open help modal
4. `closeHelp()` - Close help modal
5. `openVideoTimingModal()` - Open video timing modal
6. `closeVideoTimingModal()` - Close video timing modal
7. `openEditModal()` - Open event edit modal
8. `closeEditModal()` - Close event edit modal
9. `openEditShiftModal()` - Open shift edit modal
10. `closeEditShiftModal()` - Close shift edit modal
11. `showModal(html)` - Show generic modal
12. `closeModal()` - Close generic modal
13. `showConfirmModal()` - Show confirmation modal
14. `closeConfirmModal()` - Close confirmation modal
15. `showEventQueueModal()` - Show event queue modal

---

## 13. Keyboard Shortcuts (5+ functions)

1. `setupKeys()` - Set up keyboard shortcuts
2. `handleKeyPress(e)` - Handle key press
3. `handleKeyDown(e)` - Handle key down
4. `handleKeyUp(e)` - Handle key up
5. `toggleKeyboardShortcuts()` - Toggle shortcuts on/off

---

## 14. Persistence & Sync (8+ functions)

1. `autoSave()` - Auto-save to localStorage
2. `saveGameData()` - Manual save
3. `loadFromStorage()` - Load from localStorage
4. `saveToSupabase()` - Save to Supabase (future)
5. `loadFromSupabase()` - Load from Supabase (future)
6. `clearStorage()` - Clear localStorage
7. `exportToFile()` - Export to file
8. `importFromFile()` - Import from file

---

## 15. Game Management (10+ functions)

1. `loadGames()` - Load games from Supabase
2. `selectGame(gameId)` - Select game
3. `createGame()` - Create new game
4. `deleteGame(gameId)` - Delete game
5. `loadRosters()` - Load rosters for game
6. `loadGameData(gid)` - Load saved game data
7. `saveGameData()` - Save game data
8. `switchGame(gameId)` - Switch to different game
9. `getGameInfo(gameId)` - Get game info
10. `updateGameInfo()` - Update game info

---

## 16. Validation & Error Handling (8+ functions)

1. `validateEvent(evt)` - Validate event data
2. `validateShift(shift)` - Validate shift data
3. `showError(msg)` - Show error message
4. `toast(msg, type)` - Show toast notification
5. `confirmAction(msg)` - Confirm action
6. `runConsistencyCheck()` - Run consistency check
7. `validateTime(timeStr)` - Validate time format
8. `validateJersey(num)` - Validate jersey number

---

## 17. Advanced Features (20+ functions)

1. `pushUndoState(action)` - Push state to undo stack
2. `undo()` - Undo last action
3. `updateUndoButton()` - Update undo button
4. `toggleBatchSelectMode()` - Toggle batch select mode
5. `applyBatchEdit()` - Apply batch edit
6. `startGoalReview(idx)` - Start goal review mode
7. `highlightGoalSequence(goalIdx)` - Highlight goal sequence
8. `quickQueueEvent(type)` - Queue event for later
9. `processQueuedEvent(idx)` - Process queued event
10. `clearEventQueue()` - Clear event queue
11. `toggleStatsOverlay()` - Toggle stats overlay
12. `toggleFloatingVideo()` - Toggle floating video
13. `toggleShotChartOverlay()` - Toggle shot chart overlay
14. `startRecordingMacro()` - Start recording macro
15. `stopRecordingMacro()` - Stop recording macro
16. `playMacro(macroIdx)` - Play macro
17. `getProgressEstimate()` - Get progress estimate
18. `updateProgressBar()` - Update progress bar
19. `runConsistencyCheck()` - Run consistency check
20. `toggleKeyboardXYMode()` - Toggle keyboard XY mode

---

## Function Dependencies

### Core Dependencies

**Event Management depends on:**
- Period & Time Management
- Player Management
- XY Positioning
- Slot Management
- Auto-Functions

**Shift Management depends on:**
- Period & Time Management
- Player Management
- Slot Management
- Event Management (for stop type derivation)

**Video Integration depends on:**
- Period & Time Management
- Event Management (for time capture)

**Export depends on:**
- Event Management
- Shift Management
- Period & Time Management

---

## Key Logic Patterns

### 1. Event Creation Pattern
```
1. Select event type
2. Add players
3. Set XY positions (optional)
4. Auto-derive zone, success, strength
5. Validate
6. Log event
7. Auto-save
8. Update UI
```

### 2. Shift Creation Pattern
```
1. Set start/end times
2. Fill on-ice slots
3. Auto-derive strength
4. Auto-derive stop type (from last event)
5. Validate
6. Log shift
7. Auto-save
8. Update UI
```

### 3. Video Sync Pattern
```
1. Set period markers (P1Start, P1End, etc.)
2. Calculate running video time
3. Convert video time → game time
4. Capture times to event fields
5. Auto-sync if enabled
```

### 4. XY Positioning Pattern
```
1. Select mode (puck or player)
2. Click rink to place XY
3. Auto-detect zone
4. Store XY coordinates
5. Render markers on rink
```

---

## Next Steps

This index provides a comprehensive overview of all functions. For detailed implementation, see:
- `TRACKER_LOGIC_EXTRACTION.md` - Detailed logic extraction
- `TRACKER_REBUILD_PLAN.md` - Rebuild implementation plan

Functions should be extracted and organized into TypeScript modules during the rebuild process.

---

*Index created: 2026-01-13*  
*Total functions indexed: ~200+*
