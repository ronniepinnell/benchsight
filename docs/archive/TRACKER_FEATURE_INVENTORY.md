# Tracker Feature Inventory

**Complete feature catalog for tracker conversion**

Last Updated: 2026-01-15  
Version: 23.5 → Target: Rust/Next.js

---

## Overview

This document catalogs all features in the HTML tracker (`tracker_index_v23.5.html`) that must be preserved in the Rust/Next.js conversion.

**Total Features:** 100+  
**Source:** `ui/tracker/tracker_index_v23.5.html` (16,162 lines)  
**Status:** Complete inventory for conversion planning

---

## Core Features

### 1. Event Management

**Event Types (15+):**
- ✅ Faceoff
- ✅ Shot (Shot_Attempt, Shot_On_Goal, Shot_Blocked, Shot_Missed)
- ✅ Goal (Goal_Scored)
- ✅ Pass (Pass_Attempt, Pass_Complete, Pass_Incomplete)
- ✅ Turnover (Turnover_Giveaway, Turnover_Takeaway)
- ✅ Hit
- ✅ Penalty
- ✅ Block
- ✅ Save
- ✅ Icing
- ✅ Offside
- ✅ Stoppage
- ✅ Timeout
- ✅ Challenge
- ✅ Other custom event types

**Event Operations:**
- ✅ Create event
- ✅ Edit event
- ✅ Delete event
- ✅ Duplicate event
- ✅ Link events (e.g., shot → goal)
- ✅ Event validation
- ✅ Event search/filter
- ✅ Event sorting

**Event Fields (20+):**
- Event type, detail, detail_2
- Play detail, play detail_2
- Period, time, total seconds
- Team (home/away)
- Event players (1, 2, 3)
- XY coordinates (puck, net)
- Zone, strength, situation
- Linked event ID

### 2. Shift Management

**Shift Operations:**
- ✅ Create shift
- ✅ Edit shift
- ✅ Delete shift
- ✅ End shift
- ✅ Auto-end shift (on event)
- ✅ Shift validation
- ✅ Shift search/filter

**Shift Fields:**
- Player ID, player number
- Team (home/away)
- Period
- Start time, end time
- Start type, end type
- Duration (calculated)
- Total seconds (start, end)

**Shift Calculations:**
- ✅ Calculate shift duration
- ✅ Calculate TOI (time on ice)
- ✅ Calculate line combinations
- ✅ Calculate shift statistics

### 3. Player Management

**Player Operations:**
- ✅ Load roster from Supabase
- ✅ Select player for event
- ✅ Select player for shift
- ✅ Assign player to on-ice slot
- ✅ Remove player from slot
- ✅ Player search/filter

**On-Ice Slots:**
- ✅ Home team slots (F1, F2, F3, D1, D2, G, X)
- ✅ Away team slots (F1, F2, F3, D1, D2, G, X)
- ✅ Slot selection
- ✅ Slot assignment
- ✅ Slot clearing

**Player Data:**
- Player ID, player number
- Player name
- Player position
- Team affiliation
- Roster status

### 4. XY Positioning

**XY Operations:**
- ✅ Set puck XY position
- ✅ Set net XY position
- ✅ Set player XY position
- ✅ Click-to-set XY
- ✅ Drag-to-set XY
- ✅ XY coordinate conversion (canvas ↔ rink)
- ✅ Zone determination from XY
- ✅ XY validation (rink bounds)

**XY Features:**
- ✅ Rink canvas rendering
- ✅ Period direction handling (home attacks right P1, left P2, etc.)
- ✅ Zone visualization
- ✅ XY history/undo
- ✅ XY snap to zone

**XY Coordinate System:**
- Canvas coordinates (0-100, 0-50)
- Rink coordinates (feet from center)
- Zone mapping (Offensive, Neutral, Defensive)

### 5. Video Integration

**Video Player:**
- ✅ HTML5 video support
- ✅ YouTube video support
- ✅ Video playback controls (play, pause, seek)
- ✅ Playback speed control
- ✅ Video time display
- ✅ Fullscreen mode

**Video Sync:**
- ✅ Auto-sync video to event
- ✅ Auto-sync event to video
- ✅ Manual sync
- ✅ Period markers (P1 start, P1 end, etc.)
- ✅ Intermission handling
- ✅ Timeout handling

**Video Timing:**
- ✅ Video start offset
- ✅ Period video times
- ✅ Intermission durations
- ✅ Game time ↔ video time conversion
- ✅ Video markers (period starts/ends, stoppages)

### 6. Time/Period Management

**Period Operations:**
- ✅ Set current period (1, 2, 3, OT)
- ✅ Period length configuration
- ✅ Period direction (home attacks right/left)
- ✅ Period time tracking
- ✅ Period end detection

**Time Operations:**
- ✅ Set event time
- ✅ Set shift time
- ✅ Time format (MM:SS)
- ✅ Time validation (within period)
- ✅ Total seconds calculation
- ✅ Time increment/decrement

**Time Features:**
- ✅ Period clock display
- ✅ Game clock display
- ✅ Time remaining calculation
- ✅ Time formatting

### 7. Export/Import

**Export Formats:**
- ✅ Excel export (.xlsx)
- ✅ CSV export
- ✅ Events-only export
- ✅ Shifts-only export
- ✅ Full game export

**Export Features:**
- ✅ Export validation
- ✅ Export formatting
- ✅ Export file naming
- ✅ Export location (data/raw/games/{game_id}/)

**Import Formats:**
- ✅ Excel import
- ✅ CSV import
- ✅ Import validation
- ✅ Import merge

### 8. State Management

**State Operations:**
- ✅ Save state to localStorage
- ✅ Load state from localStorage
- ✅ Clear state
- ✅ Reset state
- ✅ State sync to Supabase
- ✅ Auto-save (30-second interval)
- ✅ Manual save

**State Features:**
- ✅ State persistence
- ✅ State recovery (on crash)
- ✅ State versioning
- ✅ State validation

### 9. UI/UX Features

**UI Components:**
- ✅ Event form
- ✅ Shift form
- ✅ Event list
- ✅ Shift list
- ✅ Rink canvas
- ✅ Video player
- ✅ On-ice slots display
- ✅ Period/score display
- ✅ Player selection dropdowns

**UI Features:**
- ✅ Modal dialogs
- ✅ Toast notifications
- ✅ Form validation
- ✅ Error messages
- ✅ Loading indicators
- ✅ Responsive design

**Keyboard Shortcuts:**
- ✅ Quick event creation
- ✅ Quick player selection
- ✅ Quick time entry
- ✅ Navigation shortcuts

### 10. Data Validation

**Validation Rules:**
- ✅ Event validation (required fields, time, players)
- ✅ Shift validation (player, time, duration)
- ✅ XY validation (rink bounds)
- ✅ Time validation (within period)
- ✅ Player validation (on roster)
- ✅ Export validation

**Validation Features:**
- ✅ Real-time validation
- ✅ Validation error messages
- ✅ Validation warnings
- ✅ Data integrity checks

### 11. Supabase Integration

**Supabase Operations:**
- ✅ Connect to Supabase
- ✅ Load reference data (event types, play details, etc.)
- ✅ Load rosters
- ✅ Load game data
- ✅ Save events/shifts
- ✅ Sync state

**Supabase Features:**
- ✅ Authentication (future)
- ✅ Real-time sync (future)
- ✅ Multi-user support (future)
- ✅ Data backup

### 12. Game Management

**Game Operations:**
- ✅ Select game
- ✅ Load game data
- ✅ Create new game
- ✅ Game info (teams, date, etc.)
- ✅ Game settings

**Game Features:**
- ✅ Game list
- ✅ Game search
- ✅ Game metadata
- ✅ Team colors/logos

---

## Advanced Features

### 13. Event Linking

**Linking Features:**
- ✅ Link shot to goal
- ✅ Link pass to shot
- ✅ Link events in sequence
- ✅ Linked event navigation
- ✅ Linked event display

### 14. Shift Analytics

**Analytics Features:**
- ✅ Line combination analysis
- ✅ Shift duration analysis
- ✅ TOI calculation
- ✅ Shift statistics
- ✅ Player usage

### 15. Data Quality

**Quality Features:**
- ✅ Data completeness checks
- ✅ Data consistency checks
- ✅ Missing data detection
- ✅ Data quality reports

---

## Feature Priority

### Critical (Must Have)
1. Event management (create, edit, delete)
2. Shift management (create, edit, delete)
3. Player selection
4. XY positioning
5. Time/period management
6. Export to Excel
7. State persistence

### High Priority
8. Video integration
9. Video sync
10. Import from Excel
11. Data validation
12. Supabase integration

### Medium Priority
13. Event linking
14. Shift analytics
15. Advanced UI features
16. Keyboard shortcuts

### Low Priority (Future)
17. Real-time multi-user sync
18. Advanced analytics
19. Custom event types
20. Mobile support

---

## Feature Gaps (HTML → Next.js)

### Missing in HTML (To Add)
- [ ] Undo/redo functionality
- [ ] Event templates
- [ ] Bulk operations
- [ ] Advanced search/filter
- [ ] Data visualization
- [ ] Export templates
- [ ] Import validation UI
- [ ] Error recovery
- [ ] Offline mode
- [ ] Mobile responsive design

### To Improve
- [ ] Better error handling
- [ ] Better loading states
- [ ] Better validation feedback
- [ ] Better keyboard navigation
- [ ] Better accessibility
- [ ] Better performance (React optimization)
- [ ] Better state management (Zustand/Redux)

---

## Related Documentation

- [TRACKER_COMPLETE_LOGIC.md](TRACKER_COMPLETE_LOGIC.md) - Function reference
- [TRACKER_STATE_MANAGEMENT.md](TRACKER_STATE_MANAGEMENT.md) - State management
- [TRACKER_EVENT_FLOW.md](TRACKER_EVENT_FLOW.md) - Event workflow
- [TRACKER_VIDEO_INTEGRATION.md](TRACKER_VIDEO_INTEGRATION.md) - Video integration
- [TRACKER_XY_POSITIONING.md](TRACKER_XY_POSITIONING.md) - XY positioning
- [TRACKER_EXPORT_FORMAT.md](TRACKER_EXPORT_FORMAT.md) - Export format
- [TRACKER_CONVERSION_SPEC.md](TRACKER_CONVERSION_SPEC.md) - Conversion specification

---

*Last Updated: 2026-01-15*
