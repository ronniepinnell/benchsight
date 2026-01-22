# Tracker Export Format

**Complete export data structure and format specification**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

The tracker exports game data to Excel format for ETL processing. This document details the export data structure and format.

**Export Format:** Excel (.xlsx)  
**Export Sheets:** `events`, `shifts`  
**Export Location:** `data/raw/games/{game_id}/{game_id}_tracking.xlsx`

---

## Export Data Structure

### Events Sheet

**Columns:**
- `tracking_event_index` (or `event_index`) - Event sequence number
- `period` - Period number (1, 2, 3, OT)
- `time` - Time in period (MM:SS format)
- `Type` - Event type (Faceoff, Shot, Pass, Goal, etc.)
- `Detail` - Event detail (subtype)
- `Detail_2` - Secondary detail
- `Play_Detail` - Play context
- `Play_Detail_2` - Secondary play context
- `event_player_1` - Primary player (shooter, passer, etc.)
- `event_player_2` - Secondary player (assist, faceoff opponent, etc.)
- `event_player_3` - Tertiary player (second assist, etc.)
- `puck_x` - Puck X coordinate (rink coordinates)
- `puck_y` - Puck Y coordinate (rink coordinates)
- `net_x` - Net X coordinate (if applicable)
- `net_y` - Net Y coordinate (if applicable)
- `team` - Team (Home/Away)
- `strength` - Game strength (5v5, PP, PK, etc.)
- `zone` - Zone (Offensive, Neutral, Defensive)
- Additional fields as needed

**Example Row:**
```
tracking_event_index: 1
period: 1
time: 15:30
Type: Shot
Detail: Shot_Attempt
Detail_2: Wrist_Shot
Play_Detail: Rush
event_player_1: P100001
puck_x: 45.2
puck_y: 12.5
team: Home
strength: 5v5
zone: Offensive
```

### Shifts Sheet

**Columns:**
- `shift_index` - Shift sequence number
- `Period` - Period number
- `shift_start` - Shift start time (MM:SS)
- `shift_end` - Shift end time (MM:SS)
- `player_id` - Player ID
- `player_number` - Jersey number
- `team` - Team (Home/Away)
- `shift_start_type` - How shift started (Faceoff, Line_Change, etc.)
- `shift_end_type` - How shift ended (Line_Change, Period_End, etc.)
- `duration_seconds` - Shift duration in seconds
- Additional fields as needed

**Example Row:**
```
shift_index: 1
Period: 1
shift_start: 18:00
shift_end: 16:45
player_id: P100001
player_number: 10
team: Home
shift_start_type: Faceoff
shift_end_type: Line_Change
duration_seconds: 75
```

---

## Export Process

### Export to Excel

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

## Export Validation

### Validate Export Data

```typescript
function validateExportData(): ValidationResult {
  const errors: string[] = []
  
  // Validate events
  S.events.forEach((event, idx) => {
    if (!event.event_type) {
      errors.push(`Event ${idx}: Missing event_type`)
    }
    if (!event.period) {
      errors.push(`Event ${idx}: Missing period`)
    }
    if (!event.time) {
      errors.push(`Event ${idx}: Missing time`)
    }
  })
  
  // Validate shifts
  S.shifts.forEach((shift, idx) => {
    if (!shift.playerId) {
      errors.push(`Shift ${idx}: Missing player_id`)
    }
    if (!shift.startTime) {
      errors.push(`Shift ${idx}: Missing start_time`)
    }
  })
  
  return {
    valid: errors.length === 0,
    errors
  }
}
```

---

## Export File Naming

### File Naming Convention

```
{game_id}_tracking.xlsx
```

**Example:**
- `18969_tracking.xlsx`
- `18977_tracking.xlsx`

### File Location

```
data/raw/games/{game_id}/{game_id}_tracking.xlsx
```

---

## Import Compatibility

### ETL Import Requirements

The export format must match ETL import expectations:

1. **Sheet Names:** Must be `events` and `shifts`
2. **Column Names:** Must match ETL column expectations
3. **Data Types:** Must be correct types (strings, numbers, etc.)
4. **Required Fields:** Must have all required fields

### ETL Column Mapping

```
Export Column → ETL Column
tracking_event_index → tracking_event_index
Type → event_type
Detail → event_detail
Detail_2 → event_detail_2
Play_Detail → play_detail
Play_Detail_2 → play_detail_2
event_player_1 → event_player_1
event_player_2 → event_player_2
event_player_3 → event_player_3
puck_x → puck_x
puck_y → puck_y
```

---

## Related Documentation

- [TRACKER_COMPLETE_LOGIC.md](TRACKER_COMPLETE_LOGIC.md) - Function reference
- [TRACKER_STATE_MANAGEMENT.md](TRACKER_STATE_MANAGEMENT.md) - State management
- [TRACKER_EVENT_FLOW.md](TRACKER_EVENT_FLOW.md) - Event workflow
- [TRACKER_CONVERSION_SPEC.md](TRACKER_CONVERSION_SPEC.md) - Conversion specification

---

*Last Updated: 2026-01-15*
