# BenchSight Tracker Logic Documentation

**Version:** v28.0  
**Last Updated:** 2026-01-22  
**Purpose:** Comprehensive documentation of all tracker logic, column definitions, calculations, and event handling

---

## Table of Contents

1. [Overview](#overview)
2. [Event Structure](#event-structure)
3. [Event Log Columns](#event-log-columns)
4. [Column Population Logic](#column-population-logic)
5. [Time Calculations](#time-calculations)
6. [XY Coordinate System](#xy-coordinate-system)
7. [Zone Calculations](#zone-calculations)
8. [Player Roles and Data](#player-roles-and-data)
9. [Event Types and Details](#event-types-and-details)
10. [Linked Events and Assists](#linked-events-and-assists)
11. [Export Format](#export-format)
12. [Shifts](#shifts)
13. [Video Timing](#video-timing)
14. [Event Handling Flow](#event-handling-flow)

---

## Overview

The BenchSight Tracker is a single-page HTML application for tracking hockey game events in real-time. It captures:

- **Events**: All on-ice actions (goals, shots, passes, faceoffs, etc.)
- **Shifts**: Player line changes and ice time
- **XY Coordinates**: Puck and player positions on the rink
- **Video Timing**: Synchronization with game video
- **Player Data**: Roles, play details, success flags, pressure, side of puck

The tracker exports data in Excel format with multiple sheets:
- `events`: One row per player per event (LONG format)
- `shifts`: One row per shift
- `xy_puck`: All puck XY coordinates
- `xy_player`: All player XY coordinates
- `video`: Video metadata
- `metadata`: Game configuration

---

## Event Structure

### Internal Event Object

Each event in `S.events[]` has the following structure:

```javascript
{
  idx: 0,                    // Event index (0-based, auto-incremented)
  game_id: "G18969",         // Game identifier
  period: 1,                 // Period number (1, 2, 3, OT, OT1, etc.)
  start_time: "18:00",       // Game time (MM:SS format, clock counts down)
  end_time: "17:45",         // End time (optional, defaults to start_time)
  team: "home",              // Event team: "home" or "away"
  type: "Goal",              // Event type (display name)
  typeCode: "G",             // Event type code (for export)
  typeId: 1,                 // Event type ID (from dim_event_type)
  detail1: "Goal_Scored",    // Event detail 1 (display name)
  detail1Code: "GS",         // Event detail 1 code (for export)
  detail1Id: 5,              // Event detail 1 ID (from dim_event_detail)
  detail2: "",               // Event detail 2 (display name)
  detail2Code: "",           // Event detail 2 code (for export)
  detail2Id: null,           // Event detail 2 ID (from dim_event_detail_2)
  zone: "o",                 // Zone: "o" (offensive), "d" (defensive), "n" (neutral)
  success: "Y",              // Success flag: "Y", "N", or ""
  strength: "5v5",           // Strength situation: "5v5", "5v4", "4v5", etc.
  linkedEventIdx: null,       // Index of linked event (for event chains)
  assistToGoalIdx: null,     // Index of goal this event assists (for Pass events)
  isHighlight: false,        // Whether this is a highlight event
  videoUrl: "",              // Individual highlight video URL (if isHighlight)
  adjustedVideoTime: 0,      // Adjusted video time for playback
  puckXY: [                  // Array of puck XY coordinates
    { x: 50, y: 20 }
  ],
  netXY: { x: 100, y: 0 },   // Net location (for shots/goals)
  players: [                 // Array of players involved
    {
      num: 12,               // Player jersey number
      name: "John Doe",      // Player name
      team: "home",          // Player team
      role: "event_team_player_1",  // Player role
      roleNum: 1,            // Role number (for sorting)
      playD1: "AssistPrimary",  // Play detail 1
      playD2: "",            // Play detail 2
      playSuccess: "Y",      // Play success flag
      pressure: "Pressured",  // Pressure status
      sideOfPuck: "Left",    // Side of puck
      xy: [                  // Array of player XY coordinates
        { x: 45, y: 15 }
      ]
    }
  ],
  shiftIdx: 0,               // Index of shift this event belongs to
  sequenceIdx: null,         // Sequence index (for multi-event sequences)
  playIdx: null,             // Play index (for multi-play sequences)
  event_id: null,            // Optional event ID (editable)
  sequence_key: null,        // Optional sequence key (editable)
  play_key: null             // Optional play key (editable)
}
```

---

## Event Log Columns

The event log displays events in a grid with the following columns (from left to right):

| Column | Width | Description | Source |
|--------|-------|-------------|--------|
| Up/Down | 30px | Move buttons (up/down) | UI only |
| # | 30px | Event index (1-based) | `evt.idx + 1` |
| Sh | 22px | Shift index | `evt.shiftIdx + 1` or empty |
| Lnk | 22px | Linked event index | `evt.linkedEventIdx + 1` or empty |
| Time | 20px | Game time (MM:SS) | `evt.start_time` |
| Adj | 48px | Adjusted video time | `evt.adjustedVideoTime` or calculated |
| VideoTime | 48px | Running video time | Calculated from period + time |
| T | 14px | Team (H/A) | `evt.team === 'home' ? 'H' : 'A'` |
| Type | 46px | Event type | `evt.type` |
| PIM | 30px | Penalty minutes | Calculated for Penalty events |
| Detail1 | 58px | Event detail 1 | `evt.detail1` |
| Detail2 | 58px | Event detail 2 | `evt.detail2` |
| Z | 14px | Zone (O/D/N) | `evt.zone` |
| S | 12px | Success (Y/N) | `evt.success` |
| EvtP | 30px | Event team players | `evt.players.filter(p => p.role.startsWith('event'))` |
| OppP | 30px | Opposing team players | `evt.players.filter(p => p.role.startsWith('opp'))` |
| PD1 | 46px | Play detail 1 | `evt.players[0]?.playD1` |
| PD2 | 46px | Play detail 2 | `evt.players[0]?.playD2` |
| PS | 12px | Play success | `evt.players[0]?.playSuccess` |
| XY | 12px | Has XY data (dot) | `evt.puckXY.length > 0` |
| Star | 12px | Highlight flag | `evt.isHighlight ? 'Star' : ''` |
| Notes | 12px | Notes indicator | UI only |
| Edit | 12px | Edit button | UI only |

---

## Column Population Logic

### Event Index (`event_index`, `event_index_flag_`)

**Calculation:**
- **Internal:** `evt.idx` (0-based, auto-incremented by `S.evtIdx++`)
- **Export (flag):** `i + 1` (1-based, where `i` is array index)
- **Export (ETL):** `1000 + i` (1000-based format for ETL)

**Logic:**
- Events are auto-sorted by time after creation (`sortAndReindexEvents()`)
- After sorting, `idx` values are reassigned sequentially
- Export uses array index `i`, not `evt.idx` (to ensure consistency)

### Sequence Index (`sequence_index_flag_`)

**Source:** `evt.sequenceIdx` (optional, manually set or from templates)

**Purpose:** Groups related events into sequences (e.g., a rush sequence)

### Play Index (`play_index_flag_`)

**Source:** `evt.playIdx` (optional, manually set or from templates)

**Purpose:** Groups related events into plays (e.g., a zone entry -> shot -> goal play)

### Linked Event Index (`linked_event_index`, `linked_event_index_flag_`)

**Source:** `evt.linkedEventIdx` (index of linked event, or `null`)

**Calculation:**
- **Export (flag):** `evt.linkedEventIdx !== null ? evt.linkedEventIdx + 1 : ''`
- **Export (ETL):** `evt.linkedEventIdx !== null ? 1000 + evt.linkedEventIdx : ''`

**Purpose:** Links related events (e.g., Pass -> Zone Entry -> Shot -> Goal)

**Logic:**
- When an event is linked, `linkedEventIdx` stores the **index** of the linked event
- Linked events can form chains (multiple events linked together)
- XY data can be propagated to all linked events

### Assist to Goal Index (`assist_to_goal_index`, `assist_to_goal_index_flag_`)

**Source:** `evt.assistToGoalIdx` (index of goal this event assists, or `null`)

**Calculation:**
- **Export (flag):** `(evt.assistToGoalIdx !== null && evt.assistToGoalIdx !== undefined) ? (parseInt(evt.assistToGoalIdx, 10) + 1) : ''`
- **Export (ETL):** `(evt.assistToGoalIdx !== null && evt.assistToGoalIdx !== undefined) ? (1000 + parseInt(evt.assistToGoalIdx, 10)) : ''`

**Purpose:** Links Pass events to Goal events they assist

**Logic:**
- Only Pass events can have `assistToGoalIdx` set
- Auto-detected when a Goal is created (finds Pass events within 15 seconds before goal)
- Can be manually set/removed via assist management UI

### Assist Primary/Secondary Event Index

**Calculation (for Goal events only):**
1. Find all Pass events where `assistToGoalIdx === goalEvent.idx`
2. Separate by assist type:
   - **Primary:** `playD1` or `playD2` contains "AssistPrimary"
   - **Secondary:** `playD1` or `playD2` contains "AssistSecondary"
   - **Untyped:** Contains "assist" but not "Primary" or "Secondary"
3. Assign:
   - **Primary:** First primary assist, or first untyped if no primary
   - **Secondary:** First secondary assist, or second untyped if no secondary

**Export:**
- `assist_primary_event_index_flag_`: 1-based index
- `assist_primary_event_index`: 1000-based index
- `assist_secondary_event_index_flag_`: 1-based index
- `assist_secondary_event_index`: 1000-based index

### Time Columns

#### Event Start/End Time (`event_start_min_`, `event_start_sec_`, `event_end_min_`, `event_end_sec_`)

**Source:** `evt.start_time` and `evt.end_time` (MM:SS format)

**Calculation:**
```javascript
const [startMin, startSec] = (evt.start_time || '').split(':');
const [endMin, endSec] = (evt.end_time || evt.start_time || '').split(':');
```

**Logic:**
- Clock counts **down** from period length (e.g., 18:00 -> 0:00)
- If `end_time` is missing, it defaults to `start_time`
- Times are stored as strings in "MM:SS" format

#### Time Start/End Total Seconds (`time_start_total_seconds`, `time_end_total_seconds`)

**Calculation:**
```javascript
const period = parseInt(evt.period) || 1;
const periodLengthMin = getPeriodLength(evt.period);  // e.g., 18 for 18-minute periods
const periodLengthSec = periodLengthMin * 60;
const startMinInt = parseInt(startMin) || 0;
const startSecInt = parseInt(startSec) || 0;
const startTotalSec = periodLengthSec - (startMinInt * 60 + startSecInt);
```

**Logic:**
- **Elapsed time** = period length - remaining time
- Example: Period 1, 18:00 length, time = 15:30
  - Remaining = 15*60 + 30 = 930 seconds
  - Elapsed = 18*60 - 930 = 1080 - 930 = 150 seconds

#### Running Time (`event_running_start`, `event_running_end`)

**Calculation:**
```javascript
let periodOffset = 0;
for (let p = 1; p < period; p++) {
  periodOffset += getPeriodLengthSeconds(p);
}
const eventRunningStart = periodOffset + startTotalSec;
const eventRunningEnd = periodOffset + endTotalSec;
```

**Logic:**
- Sums elapsed time from all previous periods
- Example: Event in Period 2 at 10:00 (18:00 period length)
  - Period 1 elapsed = 18*60 = 1080 seconds
  - Period 2 elapsed = 18*60 - (10*60 + 0) = 1080 - 600 = 480 seconds
  - Running start = 1080 + 480 = 1560 seconds

#### Running Video Time (`running_video_time`)

**Calculation:**
```javascript
const runningVideoTime = evt.videoTime || calculateRunningVideoTime(period, startTime);

function calculateRunningVideoTime(period, gameTime) {
  const offset = S.videoTiming?.videoStartOffset || 0;
  const int1 = S.videoTiming?.intermission1 || 900;  // 15 minutes default
  const int2 = S.videoTiming?.intermission2 || 900;
  
  // Calculate elapsed game time
  const periodLengthSec = getPeriodLengthSeconds(period);
  const [min, sec] = gameTime.split(':').map(Number);
  const remainingSec = (min || 0) * 60 + (sec || 0);
  const elapsedSec = periodLengthSec - remainingSec;
  
  // Sum previous periods
  let periodOffset = 0;
  for (let p = 1; p < period; p++) {
    periodOffset += getPeriodLengthSeconds(p);
  }
  
  // Add intermissions
  let intermissionDuration = 0;
  if (period >= 2) intermissionDuration += int1;
  if (period >= 3) intermissionDuration += int2;
  
  return offset + periodOffset + elapsedSec + intermissionDuration;
}
```

**Logic:**
- Includes video start offset (pre-game skip)
- Includes intermissions between periods
- Used for video synchronization

### Zone Columns

#### Event Team Zone (`event_team_zone_`, `event_team_zone`)

**Source:** `evt.zone` ("o", "d", or "n")

**Export:**
- `event_team_zone_`: "o", "d", or "n" (abbreviation)
- `event_team_zone`: "Offensive", "Defensive", or "Neutral" (full name)

**Logic:**
- Zone is from the **event team's perspective**
- "o" = offensive zone (attacking end)
- "d" = defensive zone (defending end)
- "n" = neutral zone (center ice)

**Auto-detection:**
- If `autoZoneEnabled` is true, zone is auto-set from puck X coordinate
- Uses `getZoneFromX(x, team, period)` function

#### Zone Change Index (`zone_change_index`)

**Calculation:**
```javascript
let lastZone = null;
let zoneChangeIdx = 0;

S.events.forEach((evt, i) => {
  const zoneAbbr = evt.zone || 'n';
  if (zoneAbbr !== lastZone) {
    zoneChangeIdx++;
    lastZone = zoneAbbr;
  }
  // Assign zoneChangeIdx to event
});
```

**Logic:**
- Increments each time zone changes between events
- Tracks zone transitions (e.g., neutral -> offensive -> defensive)

### Event Type/Detail Columns

#### Event Type (`event_type_`, `event_type_code`, `event_type_id`)

**Source:** `evt.type` (display name), `evt.typeCode` (code), `evt.typeId` (ID)

**Logic:**
- Loaded from `dim_event_type` table (Supabase)
- Display name is user-friendly (e.g., "Goal", "Shot", "Pass")
- Code is short identifier (e.g., "G", "S", "P")
- ID is database foreign key

**Lookup:**
```javascript
function getEventTypeCodeAndId(typeName) {
  const found = S.eventTypesDB?.find(e => e.name === typeName || e.code === typeName);
  return found ? { code: found.code || '', id: found.id || '' } : { code: typeName, id: '' };
}
```

#### Event Detail 1 (`event_detail_`, `event_detail_code`, `event_detail_id`)

**Source:** `evt.detail1` (display name), `evt.detail1Code` (code), `evt.detail1Id` (ID)

**Logic:**
- Loaded from `dim_event_detail` table (filtered by event type)
- Examples: "Goal_Scored", "Shot_On_Net", "Pass_Complete"

**Lookup:**
```javascript
function getEventDetailCodeAndId(detailName, eventType) {
  const found = S.eventDetails1?.find(e => 
    (e.name === detailName || e.code === detailName) && 
    (e.eventType === eventType || !eventType)
  );
  return found ? { code: found.code || '', id: found.id || '' } : { code: detailName, id: '' };
}
```

#### Event Detail 2 (`event_detail_2_`, `event_detail_2_code`, `event_detail_2_id`)

**Source:** `evt.detail2` (display name), `evt.detail2Code` (code), `evt.detail2Id` (ID)

**Logic:**
- Loaded from `dim_event_detail_2` table
- Optional second detail level
- Examples: "Backhand", "Forehand", "One_Timer"

### Success Flag (`event_successful_`, `event_successful`)

**Source:** `evt.success` ("Y", "N", or "")

**Logic:**
- "Y" = successful (e.g., pass complete, shot on net)
- "N" = unsuccessful (e.g., pass incomplete, shot wide)
- "" = not applicable (e.g., faceoff, stoppage)

**Auto-detection:**
- If `autoSuccessEnabled` is true, success is auto-detected based on event type and details
- Uses `autoDetectAllSuccess()` function

### Team Column (`team_`)

**Source:** `evt.team` ("home" or "away")

**Export:** "h" or "a" (abbreviated)

### Strength (`strength`)

**Source:** `evt.strength` (e.g., "5v5", "5v4", "4v5", "ENA", "ENH")

**Logic:**
- Auto-calculated from players on ice (slots)
- Format: `{homeSkaters}v{awaySkaters}`
- Empty net: "ENA" (away empty net) or "ENH" (home empty net)

**Calculation:**
```javascript
function deriveStrength() {
  const homeSkaters = ['F1','F2','F3','D1','D2','X'].filter(p => S.slots.home[p]?.num).length;
  const awaySkaters = ['F1','F2','F3','D1','D2','X'].filter(p => S.slots.away[p]?.num).length;
  const homeEN = S.slots.home?.G?.num ? 0 : 1;
  const awayEN = S.slots.away?.G?.num ? 0 : 1;
  
  if (homeEN || awayEN) {
    return homeEN ? 'ENA' : 'ENH';
  }
  return `${homeSkaters}v${awaySkaters}`;
}
```

### Penalty Minutes (`pim`)

**Calculation (for Penalty events only):**
```javascript
function calculateEventPIM(evt) {
  if (evt.type !== 'Penalty') return '';
  
  const penaltyLengths = {
    minor: 2,
    major: 5,
    misconduct: 10
  };
  
  const detail1Lower = (evt.detail1 || '').toLowerCase();
  if (detail1Lower.includes('major')) return penaltyLengths.major;
  if (detail1Lower.includes('misconduct')) return penaltyLengths.misconduct;
  if (detail1Lower.includes('minor')) return penaltyLengths.minor;
  
  return '';
}
```

**Logic:**
- Only calculated for events where `type === 'Penalty'`
- Extracts penalty length from `detail1` (e.g., "Minor", "Major", "Misconduct")
- Defaults: Minor = 2, Major = 5, Misconduct = 10

### Duration (`duration`)

**Calculation:**
```javascript
const duration = endTotalSec - startTotalSec;
```

**Logic:**
- Duration in seconds
- Negative if end time is before start time (shouldn't happen, but handled)

### Highlight Flag (`is_highlight`, `video_url`)

**Source:** `evt.isHighlight` (boolean)

**Export:**
- `is_highlight`: 1 if true, 0 if false
- `video_url`: Individual highlight video URL (if `isHighlight` is true)

**Logic:**
- User can mark events as highlights
- Highlight events can have individual video URLs
- Used for generating highlight reels

---

## Time Calculations

### Period Length

**Source:** `S.periodLength` (stored in game metadata, default 18 minutes)

**Function:**
```javascript
function getPeriodLength(period) {
  // Check for period-specific lengths
  if (S.periodLengths && S.periodLengths[period]) {
    return S.periodLengths[period];
  }
  // Default to S.periodLength or 18
  return S.periodLength || 18;
}

function getPeriodLengthSeconds(period) {
  return getPeriodLength(period) * 60;
}
```

### Clock Direction

**Important:** The clock counts **DOWN** from period length to 0:00.

- Period 1: 18:00 -> 0:00
- Period 2: 18:00 -> 0:00
- Overtime: 5:00 -> 0:00 (or custom length)

### Time Parsing

**Function:**
```javascript
function parseGameTime(timeStr) {
  if (!timeStr) return 0;
  const [min, sec] = timeStr.split(':').map(Number);
  return (min || 0) * 60 + (sec || 0);
}
```

**Returns:** Time in seconds (remaining time, not elapsed)

### Elapsed Time Calculation

**Formula:**
```
Elapsed Time = Period Length (seconds) - Remaining Time (seconds)
```

**Example:**
- Period: 1
- Period Length: 18:00 (1080 seconds)
- Game Time: 15:30
- Remaining: 15*60 + 30 = 930 seconds
- Elapsed: 1080 - 930 = 150 seconds (2:30 elapsed)

### Running Time Calculation

**Formula:**
```
Running Time = Sum of Previous Periods + Current Period Elapsed Time
```

**Example:**
- Event in Period 2 at 10:00
- Period 1: 18:00 length = 1080 seconds elapsed
- Period 2: 18:00 - 10:00 = 8:00 elapsed = 480 seconds
- Running Time: 1080 + 480 = 1560 seconds (26:00 total)

---

## XY Coordinate System

### Rink Dimensions

- **Width:** 200 units (feet)
- **Height:** 85 units (feet)
- **Center:** (0, 0)
- **X Range:** -100 to +100 (left to right)
- **Y Range:** -42.5 to +42.5 (bottom to top)

### Raw XY Coordinates

**Storage:**
- Puck XY: `evt.puckXY[]` (array of `{x, y}` objects)
- Player XY: `p.xy[]` (array of `{x, y}` objects per player)
- Net XY: `evt.netXY` (single `{x, y}` object)

**Coordinate System:**
- **Center-relative:** (0, 0) is center ice
- **X:** Negative = left side, Positive = right side
- **Y:** Negative = bottom (defensive end), Positive = top (offensive end)

### Adjusted XY Coordinates

**Purpose:** Standardize coordinates so offensive plays always have positive X, defensive plays always have negative X, regardless of which end teams attack.

**Calculation:**
```javascript
function calculateAdjustedXY(x, y, period, team, zone) {
  if (x === null || x === undefined || isNaN(x)) return { x: null, y };
  
  // Determine team's facing direction in this period
  const isOddPeriod = period === 1 || period === 3 || period === 'OT' || (parseInt(period) || 1) % 2 === 1;
  const homeOffensiveRight = isOddPeriod ? S.homeAttacksRightP1 : !S.homeAttacksRightP1;
  const isHome = team === 'home';
  const teamFacingRight = isHome ? homeOffensiveRight : !homeOffensiveRight;
  
  let adjustedX = x;
  
  if (zone === 'o') {
    // Offensive zone: always positive
    adjustedX = Math.abs(x);
  } else if (zone === 'd') {
    // Defensive zone: always negative
    adjustedX = -Math.abs(x);
  } else {
    // Neutral zone: adjust based on team's facing direction
    if (teamFacingRight) {
      adjustedX = x > 0 ? Math.abs(x) : -Math.abs(x);
    } else {
      adjustedX = x < 0 ? Math.abs(x) : -Math.abs(x);
    }
  }
  
  // Y inversion for even periods (teams switch ends)
  let adjustedY = y;
  if (!isOddPeriod) {
    adjustedY = y !== null && y !== undefined ? -y : y;
  }
  
  return { x: adjustedX, y: adjustedY };
}
```

**Logic:**
- **Offensive zone:** X is always positive (distance from center toward offensive end)
- **Defensive zone:** X is always negative (negative distance from center toward defensive end)
- **Neutral zone:** Adjusted based on team's facing direction
- **Y coordinate:** Inverted in even periods (teams switch ends)

**Export Columns:**
- `puck_x_start`, `puck_y_start`: Raw coordinates (first XY point)
- `puck_x_stop`, `puck_y_stop`: Raw coordinates (last XY point)
- `puck_x_start_adjusted`, `puck_y_start_adjusted`: Adjusted coordinates (first XY point)
- `puck_x_stop_adjusted`, `puck_y_stop_adjusted`: Adjusted coordinates (last XY point)
- `player_x_start`, `player_y_start`: Raw coordinates (first XY point)
- `player_x_stop`, `player_y_stop`: Raw coordinates (last XY point)
- `player_x_start_adjusted`, `player_y_start_adjusted`: Adjusted coordinates (first XY point)
- `player_x_stop_adjusted`, `player_y_stop_adjusted`: Adjusted coordinates (last XY point)

**Flags:**
- `is_xy_adjusted`: 1 if adjusted columns are present, 0 otherwise
- `needs_xy_adjustment`: 1 if even period (teams switched ends), 0 if odd period

---

## Zone Calculations

### Zone from X Coordinate

**Function:**
```javascript
function getZoneFromX(x, team, period) {
  if (x == null || x === undefined || isNaN(x)) return null;
  
  const isOddPeriod = period === 1 || period === 3 || period === 'OT' || (parseInt(period) || 1) % 2 === 1;
  const homeAttacksRightP1 = S.homeAttacksRightP1 !== false;
  const homeAttacksRight = isOddPeriod ? homeAttacksRightP1 : !homeAttacksRightP1;
  const teamAttacksRight = (team === 'home') ? homeAttacksRight : !homeAttacksRight;
  
  // Blue lines at x=75 and x=125 (NHL dimensions)
  // 0-75 = left zone, 75-125 = neutral, 125-200 = right zone
  
  if (teamAttacksRight) {
    // Team attacks right: Offensive = right (x > 125), Defensive = left (x < 75)
    if (x > 125) return 'o';
    if (x < 75) return 'd';
    return 'n';
  } else {
    // Team attacks left: Offensive = left (x < 75), Defensive = right (x > 125)
    if (x < 75) return 'o';
    if (x > 125) return 'd';
    return 'n';
  }
}
```

**Logic:**
- Blue lines at x=75 and x=125 (NHL standard)
- Zone depends on:
  1. Team (home/away)
  2. Period (odd/even - teams switch ends)
  3. Which end home attacks in Period 1 (`S.homeAttacksRightP1`)

**Auto-Zone Detection:**
- If `autoZoneEnabled` is true, zone is auto-set when puck XY is added
- Uses `getZoneFromX(puckXY[0].x, evt.team, evt.period)`

---

## Player Roles and Data

### Player Roles

**Format:** `{team}_{role}_{number}`

**Types:**
- `event_team_player_1`, `event_team_player_2`, etc. (players on event team)
- `opp_team_player_1`, `opp_team_player_2`, etc. (players on opposing team)

**Role Abbreviations:**
- `role_abrev`: "e1", "e2", "o1", "o2", etc. (e = event team, o = opposing team)
- `role_abrev_binary_`: "e" or "o" (just the prefix)

**Logic:**
- Event team players are numbered sequentially (1, 2, 3, ...)
- Opposing team players are numbered sequentially (1, 2, 3, ...)
- Roles are auto-assigned when players are added

### Player Game Number (`player_game_number_`, `player_game_number`)

**Source:** `p.num` (player jersey number)

**Export:** Same value in both columns (underscore and non-underscore versions)

### Player Name (`player_name`)

**Source:** `p.name` (player name from roster)

### Play Details

#### Play Detail 1 (`play_detail1_`, `play_detail1`)

**Source:** `p.playD1` (play detail 1)

**Examples:**
- "AssistPrimary" (primary assist)
- "AssistSecondary" (secondary assist)
- "Forced" (forced turnover)
- "Blocked" (shot blocked)

**Logic:**
- Loaded from `dim_play_detail` table
- User selects from dropdown or types manually
- Used for micro-stats and advanced analytics

#### Play Detail 2 (`play_detail2_`, `play_detail_2`)

**Source:** `p.playD2` (play detail 2)

**Examples:**
- "Backhand" (backhand pass/shot)
- "One_Timer" (one-timer shot)
- "Breakaway" (breakaway situation)

**Logic:**
- Loaded from `dim_play_detail_2` table
- Optional second level of detail

#### Play Detail Successful (`play_detail_successful_`, `play_detail_successful`)

**Source:** `p.playSuccess` ("Y", "N", or "")

**Logic:**
- Success flag for the specific play detail
- Different from event-level success (e.g., pass can be successful even if shot misses)

### Pressure (`pressured_pressurer_`, `pressured_pressurer`)

**Source:** `p.pressure` (pressure status)

**Examples:**
- "Pressured" (player was pressured)
- "Pressurer" (player applied pressure)
- "" (no pressure)

**Logic:**
- Auto-detected if `autoPressureEnabled` is true
- Uses `autoDetectAllPressure()` function

### Side of Puck (`side_of_puck_`, `side_of_puck`)

**Source:** `p.sideOfPuck` ("Left", "Right", or "")

**Logic:**
- Which side of the puck the player is on
- Auto-detected if `autoSideOfPuckEnabled` is true
- Uses `autoDetectAllSideOfPuck()` function

---

## Event Types and Details

### Event Types

Loaded from `dim_event_type` table (Supabase):

**Common Types:**
- Goal
- Shot
- Pass
- Faceoff
- Zone Entry
- Zone Exit
- Penalty
- Stoppage
- etc.

**Structure:**
```javascript
{
  id: 1,
  code: "G",
  name: "Goal",
  // ... other fields
}
```

### Event Details

Loaded from `dim_event_detail` table (filtered by event type):

**Goal Details:**
- Goal_Scored
- Goal_Own_Goal
- etc.

**Shot Details:**
- Shot_On_Net
- Shot_Wide
- Shot_Blocked
- Shot_Missed
- etc.

**Pass Details:**
- Pass_Complete
- Pass_Incomplete
- Pass_Intercepted
- etc.

### Event Detail 2

Loaded from `dim_event_detail_2` table:

**Examples:**
- Backhand
- Forehand
- One_Timer
- Slap_Shot
- Wrist_Shot
- etc.

---

## Linked Events and Assists

### Linked Events

**Purpose:** Connect related events (e.g., Pass -> Zone Entry -> Shot -> Goal)

**Storage:**
- `evt.linkedEventIdx`: Index of linked event (or `null`)

**Logic:**
- When event A is linked to event B, `A.linkedEventIdx = B.idx`
- Multiple events can form chains (A -> B -> C -> D)
- XY data can be propagated to all linked events

**Export:**
- `linked_event_index_flag_`: 1-based index (or empty)
- `linked_event_index`: 1000-based index (or empty)

### Assists

**Purpose:** Link Pass events to Goal events they assist

**Storage:**
- `evt.assistToGoalIdx`: Index of goal this event assists (for Pass events)

**Auto-Detection:**
```javascript
function detectAndLinkAssists(goalEvent) {
  // Find Pass events within 15 seconds before goal
  const recentPasses = S.events.filter(e => {
    if (e.type !== 'Pass') return false;
    if (e.period !== goalEvent.period) return false;
    if (e.team !== goalEvent.team) return false;
    if (e.idx >= goalEvent.idx) return false;  // Must be before goal
    
    const timeDiff = goalTime - passTime;
    return timeDiff >= 0 && timeDiff <= 15;  // Within 15 seconds
  });
  
  // Link passes that already have assist markers
  recentPasses.forEach(pass => {
    const hasAssist = pass.players?.some(p => {
      const pd1 = (p.playD1 || '').toLowerCase();
      const pd2 = (p.playD2 || '').toLowerCase();
      return pd1.includes('assist') || pd2.includes('assist');
    });
    
    if (hasAssist) {
      pass.assistToGoalIdx = goalEvent.idx;
    }
  });
}
```

**Assist Types:**
- **Primary (A1):** `playD1` or `playD2` contains "AssistPrimary"
- **Secondary (A2):** `playD1` or `playD2` contains "AssistSecondary"
- **Untyped:** Contains "assist" but not "Primary" or "Secondary"

**Export:**
- `assist_to_goal_index_flag_`: 1-based index (or empty)
- `assist_to_goal_index`: 1000-based index (or empty)
- `assist_primary_event_index_flag_`: 1-based index of primary assist (for Goal events)
- `assist_primary_event_index`: 1000-based index of primary assist (for Goal events)
- `assist_secondary_event_index_flag_`: 1-based index of secondary assist (for Goal events)
- `assist_secondary_event_index`: 1000-based index of secondary assist (for Goal events)

---

## Export Format

### Excel Workbook Structure

**Sheets:**
1. `metadata`: Game configuration
2. `events`: One row per player per event (LONG format)
3. `shifts`: One row per shift
4. `xy_puck`: All puck XY coordinates
5. `xy_player`: All player XY coordinates
6. `video`: Video metadata
7. `video_timing_config`: Video timing configuration

### Events Sheet Columns

**Input Columns (underscore suffix):**
- `event_index_flag_`: 1-based index
- `sequence_index_flag_`: Sequence index (optional)
- `play_index_flag_`: Play index (optional)
- `linked_event_index_flag_`: Linked event index (1-based)
- `assist_to_goal_index_flag_`: Assist to goal index (1-based)
- `assist_primary_event_index_flag_`: Primary assist index (1-based)
- `assist_secondary_event_index_flag_`: Secondary assist index (1-based)
- `event_start_min_`, `event_start_sec_`: Start time components
- `event_end_min_`, `event_end_sec_`: End time components
- `event_team_zone_`: Zone abbreviation (o/d/n)
- `event_type_`: Event type name
- `event_detail_`: Event detail 1 name
- `event_detail_2_`: Event detail 2 name
- `event_successful_`: Success flag
- `team_`: Team abbreviation (h/a)
- `player_game_number_`: Player jersey number
- `play_detail1_`, `play_detail2_`: Play details
- `play_detail_successful_`: Play success flag
- `pressured_pressurer_`: Pressure status
- `side_of_puck_`: Side of puck

**ETL Columns (1000-based indices):**
- `event_index`: 1000 + array index
- `linked_event_index`: 1000 + linked event index (or empty)
- `assist_to_goal_index`: 1000 + assist to goal index (or empty)
- `assist_primary_event_index`: 1000 + primary assist index (or empty)
- `assist_secondary_event_index`: 1000 + secondary assist index (or empty)

**Code/ID Columns:**
- `event_type_code`, `event_type_id`: Event type code and ID
- `event_detail_code`, `event_detail_id`: Event detail 1 code and ID
- `event_detail_2_code`, `event_detail_2_id`: Event detail 2 code and ID

**Calculated Columns:**
- `time_start_total_seconds`: Elapsed time in period (seconds)
- `time_end_total_seconds`: Elapsed time in period (seconds)
- `duration`: Event duration (seconds)
- `period_start_total_running_seconds`: Sum of previous periods (seconds)
- `running_video_time`: Running video time (seconds)
- `event_running_start`: Running game time (seconds)
- `event_running_end`: Running game time (seconds)
- `running_intermission_duration`: Intermission duration up to this point (seconds)
- `zone_change_index`: Zone change counter
- `shift_index`: Shift index (optional)
- `is_highlight`: Highlight flag (1/0)
- `video_url`: Highlight video URL
- `pim`: Penalty minutes (for Penalty events)

**XY Columns:**
- `puck_x_start`, `puck_y_start`: Raw puck XY (first point)
- `puck_x_stop`, `puck_y_stop`: Raw puck XY (last point)
- `puck_x_start_adjusted`, `puck_y_start_adjusted`: Adjusted puck XY (first point)
- `puck_x_stop_adjusted`, `puck_y_stop_adjusted`: Adjusted puck XY (last point)
- `player_x_start`, `player_y_start`: Raw player XY (first point)
- `player_x_stop`, `player_y_stop`: Raw player XY (last point)
- `player_x_start_adjusted`, `player_y_start_adjusted`: Adjusted player XY (first point)
- `player_x_stop_adjusted`, `player_y_stop_adjusted`: Adjusted player XY (last point)
- `net_x`, `net_y`: Net location (for shots/goals)
- `is_xy_adjusted`: Flag (1 if adjusted columns present)
- `needs_xy_adjustment`: Flag (1 if even period)

**Other Columns:**
- `game_id`: Game identifier
- `home_team`, `away_team`: Team names
- `period`: Period number
- `strength`: Strength situation
- `event_team_zone`: Zone full name
- `role_abrev`: Role abbreviation (e1, e2, o1, o2, etc.)
- `role_abrev_binary_`: Role prefix (e or o)
- `player_role`: Full role name
- `player_name`: Player name
- `Type`: Legacy uppercase event type (backward compatibility)

---

## Shifts

### Shift Structure

```javascript
{
  idx: 0,                    // Shift index (0-based)
  game_id: "G18969",         // Game identifier
  period: 1,                 // Period number
  start_time: "18:00",       // Shift start time (MM:SS)
  end_time: "17:30",         // Shift end time (MM:SS)
  start_type: "Faceoff",     // How shift started
  stop_type: "Whistle",      // How shift ended
  strength: "5v5",           // Strength situation
  home: {                    // Home team players on ice
    F1: { num: 12, name: "John Doe", pos: "F" },
    F2: { num: 23, name: "Jane Smith", pos: "F" },
    F3: { num: 34, name: "Bob Johnson", pos: "F" },
    D1: { num: 45, name: "Alice Brown", pos: "D" },
    D2: { num: 56, name: "Charlie Wilson", pos: "D" },
    G: { num: 1, name: "Goalie Name", pos: "G" },
    X: null                  // Extra skater (optional)
  },
  away: {                    // Away team players on ice
    // Same structure as home
  },
  stoppageTime: 15,          // Stoppage time during shift (seconds)
  duration: 30,              // Shift duration (seconds)
  shiftIdx: 0                // Index in shifts array
}
```

### Shift Export Columns

**Basic Columns:**
- `shift_index`: 1-based shift index
- `Period`: Period number
- `shift_start_min`, `shift_start_sec`: Start time components
- `shift_end_min`, `shift_end_sec`: End time components
- `shift_start_type`: How shift started
- `shift_stop_type`: How shift ended
- `shift_duration`: Duration (seconds)
- `stoppage_time`: Stoppage time during shift (seconds)

**Player Columns:**
- `home_forward_1`, `home_forward_2`, `home_forward_3`: Home forwards
- `home_defense_1`, `home_defense_2`: Home defensemen
- `home_goalie`: Home goalie
- `home_xtra`: Home extra skater
- `away_forward_1`, `away_forward_2`, `away_forward_3`: Away forwards
- `away_defense_1`, `away_defense_2`: Away defensemen
- `away_goalie`: Away goalie
- `away_xtra`: Away extra skater

**Calculated Columns:**
- `shift_start_total_seconds`: Elapsed time in period (seconds)
- `shift_end_total_seconds`: Elapsed time in period (seconds)
- `home_team_strength`: Home skaters on ice
- `away_team_strength`: Away skaters on ice
- `home_team_en`: Home empty net flag (1/0)
- `away_team_en`: Away empty net flag (1/0)
- `home_team_pk`: Home penalty kill flag (1/0)
- `home_team_pp`: Home power play flag (1/0)
- `away_team_pp`: Away power play flag (1/0)
- `away_team_pk`: Away penalty kill flag (1/0)
- `situation`: Strength situation (even, home_pp, away_pp, home_en, away_en)
- `home_goals`: Running home goals at shift start
- `away_goals`: Running away goals at shift start
- `home_team_plus`: Goals FOR home during shift (EV/SH only)
- `home_team_minus`: Goals AGAINST home during shift (EV/SH only)
- `away_team_plus`: Goals FOR away during shift (EV/SH only)
- `away_team_minus`: Goals AGAINST away during shift (EV/SH only)

**Zone Columns:**
- `home_ozone_start`, `home_ozone_end`: Home offensive zone flags (1/0)
- `home_dzone_start`, `home_dzone_end`: Home defensive zone flags (1/0)
- `home_nzone_start`, `home_nzone_end`: Home neutral zone flags (1/0)
- `away_ozone_start`, `away_ozone_end`: Away offensive zone flags (1/0)
- `away_dzone_start`, `away_dzone_end`: Away defensive zone flags (1/0)
- `away_nzone_start`, `away_nzone_end`: Away neutral zone flags (1/0)

**Puck XY Columns:**
- `puck_start_x`, `puck_start_y`: Puck location at shift start
- `puck_end_x`, `puck_end_y`: Puck location at shift end
- `needs_xy_adjustment`: Flag (1 if even period)

**Time Columns:**
- `period_start_total_running_seconds`: Sum of previous periods (seconds)
- `running_video_time`: Running video time (seconds)
- `shift_start_running_time`: Running game time at shift start (seconds)
- `shift_end_running_time`: Running game time at shift end (seconds)

### Stoppage Time Calculation

**Function:**
```javascript
function calculateShiftStoppageTime(shift) {
  let stoppageTotal = 0;
  
  S.events.forEach(evt => {
    if (evt.period !== shift.period) return;
    if (evt.type !== 'Stoppage' && evt.type !== 'Clockstop' && evt.type !== 'Timeout' && evt.type !== 'DeadIce') return;
    
    // Check if event falls within shift time window
    if (isTimeBetween(evt.start_time, shift.start_time, shift.end_time)) {
      // Get event duration
      let duration = 0;
      if (evt.end_time && evt.end_time !== evt.start_time) {
        duration = Math.abs(parseTime(evt.start_time) - parseTime(evt.end_time));
      }
      
      // Default durations by type
      if (duration > 0) {
        stoppageTotal += duration;
      } else {
        if (evt.type === 'Timeout') stoppageTotal += 60;
        else if (evt.type === 'DeadIce') {
          if (evt.detail1?.includes('Icing')) stoppageTotal += 15;
          else if (evt.detail1?.includes('Offside')) stoppageTotal += 10;
          else if (evt.detail1?.includes('PuckOut')) stoppageTotal += 10;
          else stoppageTotal += 5;
        } else if (evt.detail1?.includes('Icing')) stoppageTotal += 15;
        else if (evt.detail1?.includes('Offside')) stoppageTotal += 10;
        else if (evt.type === 'Clockstop') stoppageTotal += 30;
        else stoppageTotal += 5;
      }
    }
  });
  
  return stoppageTotal;
}
```

**Logic:**
- Finds all Stoppage/Clockstop/Timeout/DeadIce events within shift time window
- Sums their durations
- Uses default durations if event has no end time:
  - Timeout: 60 seconds
  - Icing: 15 seconds
  - Offside: 10 seconds
  - Clockstop: 30 seconds
  - Other: 5 seconds

### Shift Duration Calculation

**Function:**
```javascript
function calculateShiftDuration(shift) {
  const parseTime = (t) => {
    const [min, sec] = t.split(':').map(Number);
    return (min || 0) * 60 + (sec || 0);
  };
  
  // Clock counts down, so start > end
  return parseTime(shift.start_time) - parseTime(shift.end_time);
}
```

**Logic:**
- Duration = start time - end time (in seconds)
- Clock counts down, so start time is greater than end time

---

## Video Timing

### Video Start Offset

**Purpose:** Skip pre-game content (warmups, introductions, etc.)

**Storage:** `S.videoTiming.videoStartOffset` (seconds)

**Usage:** Added to all video time calculations

### Intermissions

**Storage:**
- `S.videoTiming.intermission1`: Duration between Period 1 and 2 (default 900 seconds = 15 minutes)
- `S.videoTiming.intermission2`: Duration between Period 2 and 3 (default 900 seconds)
- `S.videoTiming.intermission3`: Duration between Period 3 and OT (default 900 seconds)

**Usage:** Added to running video time calculations

### Running Video Time Calculation

**Function:**
```javascript
function calculateRunningVideoTime(period, gameTime) {
  const offset = S.videoTiming?.videoStartOffset || 0;
  const int1 = S.videoTiming?.intermission1 || 900;
  const int2 = S.videoTiming?.intermission2 || 900;
  
  // Calculate elapsed game time
  const periodLengthSec = getPeriodLengthSeconds(period);
  const [min, sec] = gameTime.split(':').map(Number);
  const remainingSec = (min || 0) * 60 + (sec || 0);
  const elapsedSec = periodLengthSec - remainingSec;
  
  // Sum previous periods
  let periodOffset = 0;
  for (let p = 1; p < period; p++) {
    periodOffset += getPeriodLengthSeconds(p);
  }
  
  // Add intermissions
  let intermissionDuration = 0;
  if (period >= 2) intermissionDuration += int1;
  if (period >= 3) intermissionDuration += int2;
  
  return offset + periodOffset + elapsedSec + intermissionDuration;
}
```

**Formula:**
```
Running Video Time = Video Start Offset + Sum of Previous Periods + Current Period Elapsed Time + Intermissions
```

**Example:**
- Video Start Offset: 30 seconds
- Period 1: 18:00 length, event at 15:00
  - Elapsed: 18*60 - 15*60 = 180 seconds
  - Running: 30 + 180 = 210 seconds
- Period 2: 18:00 length, event at 10:00
  - Period 1: 18*60 = 1080 seconds
  - Intermission 1: 900 seconds
  - Period 2 elapsed: 18*60 - 10*60 = 480 seconds
  - Running: 30 + 1080 + 900 + 480 = 2490 seconds

### Adjusted Video Time

**Purpose:** Adjust video time to go back a few seconds (for context) or to nearest faceoff

**Function:**
```javascript
function calculateAdjustedVideoTime(period, eventTime, eventType) {
  const runningTime = calculateRunningVideoTime(period, eventTime);
  
  // Go back up to 10 seconds for context
  const contextSeconds = 10;
  const adjustedTime = Math.max(0, runningTime - contextSeconds);
  
  // If event is a faceoff, try to find nearest faceoff in video
  // (simplified - actual implementation may be more complex)
  
  return adjustedTime;
}
```

**Storage:** `evt.adjustedVideoTime` (seconds)

---

## Event Handling Flow

### Creating an Event

1. **User Input:**
   - Select event type, detail, zone, success
   - Add players, set XY coordinates
   - Set time, team, strength

2. **Event Creation:**
   ```javascript
   function logEventDirect() {
     // Get current event data from UI
     const startTime = document.getElementById('evtStartTime').value;
     const endTime = document.getElementById('evtEndTime').value || startTime;
     const zone = document.getElementById('evtZone').value;
     const success = document.getElementById('evtSuccess').value;
     const strength = deriveStrength();
     
     // Create event object
     const evt = {
       idx: S.evtIdx++,
       game_id: S.gameId,
       period: S.period,
       start_time: startTime,
       end_time: endTime,
       team: S.evtTeam,
       type: S.curr.type,
       detail1: finalDetail1,
       detail2: finalDetail2,
       zone,
       success,
       strength,
       linkedEventIdx: S.linkedEventIdx,
       puckXY: [...S.curr.puckXY],
       netXY: S.curr.netXY,
       players: S.curr.players.map(p => ({...p, xy: [...(p.xy || [])]}))
     };
     
     // Add to events array
     S.events.push(evt);
     
     // Auto-sort and reindex
     sortAndReindexEvents();
     
     // Auto-detect assists (if Goal)
     if (evt.type === 'Goal') {
       detectAndLinkAssists(evt);
     }
     
     // Clear current event
     clearEvent();
     
     // Render updates
     renderEvents();
     updateScores();
     updateBoxScore();
     autoSave();
   }
   ```

3. **Auto-Sorting:**
   ```javascript
   function sortAndReindexEvents() {
     // Sort by period, then by time (descending - clock counts down)
     S.events.sort((a, b) => {
       if (a.period !== b.period) return a.period - b.period;
       const aTime = parseGameTime(a.start_time);
       const bTime = parseGameTime(b.start_time);
       return bTime - aTime;  // Descending (higher time = earlier in period)
     });
     
     // Reindex
     S.events.forEach((evt, i) => {
       evt.idx = i;
     });
   }
   ```

4. **Auto-Save:**
   - Saves to localStorage
   - Saves to Supabase (if connected)

### Editing an Event

1. **Open Edit Modal:**
   ```javascript
   function editEvent(idx) {
     S.editingEvtIdx = idx;
     const evt = S.events[idx];
     
     // Populate form fields
     document.getElementById('editType').value = evt.type;
     document.getElementById('editTeam').value = evt.team;
     document.getElementById('editStartTime').value = evt.start_time;
     // ... etc
     
     // Show modal
     document.getElementById('editModal').classList.add('show');
   }
   ```

2. **Save Changes:**
   ```javascript
   function saveEditEvent() {
     const evt = S.events[S.editingEvtIdx];
     
     // Update from form
     evt.type = document.getElementById('editType').value;
     evt.team = document.getElementById('editTeam').value;
     evt.start_time = document.getElementById('editStartTime').value;
     // ... etc
     
     // Re-sort and reindex
     sortAndReindexEvents();
     
     // Render updates
     renderEvents();
     updateScores();
     autoSave();
   }
   ```

### Deleting an Event

```javascript
function deleteEvent(idx) {
  if (!confirm('Delete this event?')) return;
  
  // Remove from array
  S.events.splice(idx, 1);
  
  // Re-sort and reindex
  sortAndReindexEvents();
  
  // Render updates
  renderEvents();
  updateScores();
  autoSave();
}
```

---

## Summary

This document provides a comprehensive overview of the BenchSight Tracker's logic, including:

- **Event Structure:** Internal event object and all fields
- **Column Definitions:** All export columns and their calculations
- **Time Calculations:** Elapsed time, running time, video time
- **XY Coordinates:** Raw and adjusted coordinate systems
- **Zone Calculations:** Zone detection from X coordinate
- **Player Data:** Roles, play details, pressure, side of puck
- **Linked Events:** Event chains and assist linking
- **Export Format:** Excel workbook structure and column mappings
- **Shifts:** Shift structure and calculations
- **Video Timing:** Video synchronization logic
- **Event Handling:** Create, edit, delete flow

For specific implementation details, refer to the source code in `ui/tracker/tracker_index_v28.html`.

---

**End of Document**
