# Tracker Data Format Guide

## Overview

The Tracker writes to 4 main tables:
1. `fact_events` - Game events (shots, passes, goals, etc.)
2. `fact_shifts` - Player shift tracking
3. `fact_player_xy_*` / `fact_puck_xy_*` - XY coordinate tracking
4. `fact_video_highlights` - Video clip markers (future)

---

## 1. EVENTS TABLE: `fact_events`

### Primary Key
```
event_key = "{game_id}_{event_index}"
Example: "18969_1", "18969_2", "18969_3"
```

### Required Columns

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `event_key` | TEXT | ✅ | Primary key | "18969_1" |
| `game_id` | INTEGER | ✅ | FK to dim_schedule | 18969 |
| `event_index` | INTEGER | ✅ | Sequential within game | 1, 2, 3... |
| `period_number` | TEXT | ✅ | Period (1, 2, 3, OT, SO) | "1" |
| `game_time` | DECIMAL | ✅ | Seconds into period | 45.5 |
| `event_type` | TEXT | ✅ | Primary event category | "Shot" |
| `event_player_1` | INTEGER | ✅ | Primary player FK | 123 |
| `team_id` | INTEGER | ✅ | Team FK | 5 |

### Optional Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `event_detail` | TEXT | Specific event type | "Wrist Shot" |
| `event_detail_2` | TEXT | Secondary detail | "High" |
| `event_player_2` | INTEGER | Secondary player (assist 1) | 456 |
| `event_player_3` | INTEGER | Tertiary player (assist 2) | 789 |
| `success` | TEXT | 's' = success, 'u' = unsuccessful | "s" |
| `x_coord` | DECIMAL | X coordinate (0-100) | 75.5 |
| `y_coord` | DECIMAL | Y coordinate (0-42.5) | 22.0 |
| `zone` | TEXT | DZ, NZ, OZ | "OZ" |
| `strength` | TEXT | EV, PP, PK, 4v4, etc. | "EV" |
| `score_state` | TEXT | Leading, Tied, Trailing | "Tied" |
| `video_timestamp` | DECIMAL | Video time in seconds | 1234.5 |

### Event Types & Details

```javascript
const EVENT_TYPES = {
  // Scoring
  'Goal': ['Wrist Shot', 'Slap Shot', 'Snap Shot', 'Backhand', 'Tip-In', 'Deflection', 'Wrap Around'],
  'Shot': ['Wrist Shot', 'Slap Shot', 'Snap Shot', 'Backhand', 'Blocked', 'Missed'],
  
  // Passing
  'Pass': ['Complete', 'Incomplete', 'Intercepted', 'Saucer', 'Bank'],
  
  // Puck Control
  'Faceoff': ['Won', 'Lost'],
  'Takeaway': ['Stick Check', 'Poke Check', 'Body Position', 'Interception'],
  'Giveaway': ['Bad Pass', 'Lost Battle', 'Turnover'],
  
  // Physical
  'Hit': ['Body Check', 'Board', 'Open Ice'],
  'Block': ['Shot Block', 'Pass Block'],
  
  // Zone
  'Zone Entry': ['Carry', 'Dump', 'Pass'],
  'Zone Exit': ['Carry', 'Pass', 'Clear', 'Dump'],
  
  // Goalie
  'Save': ['Glove', 'Blocker', 'Pad', 'Body', 'Stick'],
  
  // Special
  'Penalty': ['Minor', 'Major', 'Misconduct'],
  'Stoppage': ['Icing', 'Offside', 'Puck Out', 'Goalie Freeze'],
}
```

### JavaScript: Insert Event

```javascript
async function insertEvent(eventData) {
  const event = {
    event_key: `${eventData.gameId}_${eventData.eventIndex}`,
    game_id: eventData.gameId,
    event_index: eventData.eventIndex,
    period_number: String(eventData.period),
    game_time: eventData.gameTime,
    event_type: eventData.eventType,
    event_detail: eventData.eventDetail || null,
    event_player_1: eventData.primaryPlayer,
    event_player_2: eventData.secondaryPlayer || null,
    event_player_3: eventData.tertiaryPlayer || null,
    team_id: eventData.teamId,
    success: eventData.success || null,  // 's' or 'u'
    x_coord: eventData.x || null,
    y_coord: eventData.y || null,
    zone: eventData.zone || null,
    strength: eventData.strength || 'EV',
  }
  
  const { data, error } = await supabase
    .from('fact_events')
    .insert(event)
  
  return { data, error }
}
```

### CRITICAL: Goal Detection
Goals are tracked TWO ways - BOTH must be recorded:
```javascript
// Method 1: event_type = 'Goal'
{ event_type: 'Goal', event_detail: 'Wrist Shot', ... }

// Method 2: event_detail contains goal indicator
{ event_type: 'Shot', event_detail: 'Shot Goal', ... }
// OR
{ event_type: 'Shot', event_detail: 'Goal Scored', ... }
```

---

## 2. SHIFTS TABLE: `fact_shifts`

### Primary Key
```
shift_key = "{game_id}_{player_id}_{shift_number}"
Example: "18969_123_1", "18969_123_2"
```

### Required Columns

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `shift_key` | TEXT | ✅ | Primary key | "18969_123_1" |
| `game_id` | INTEGER | ✅ | FK to dim_schedule | 18969 |
| `player_id` | INTEGER | ✅ | FK to dim_player | 123 |
| `shift_number` | INTEGER | ✅ | Sequential per player | 1, 2, 3... |
| `period_number` | TEXT | ✅ | Period | "1" |
| `start_time` | DECIMAL | ✅ | Shift start (period seconds) | 0.0 |
| `end_time` | DECIMAL | ✅ | Shift end (period seconds) | 45.5 |

### Optional Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `duration` | DECIMAL | Calculated duration | 45.5 |
| `team_id` | INTEGER | Team FK | 5 |
| `shift_start_type` | TEXT | How shift started | "Faceoff" |
| `shift_stop_type` | TEXT | How shift ended | "Change" |
| `is_penalty` | BOOLEAN | Penalty box time | false |

### JavaScript: Insert Shift

```javascript
async function insertShift(shiftData) {
  const shift = {
    shift_key: `${shiftData.gameId}_${shiftData.playerId}_${shiftData.shiftNumber}`,
    game_id: shiftData.gameId,
    player_id: shiftData.playerId,
    shift_number: shiftData.shiftNumber,
    period_number: String(shiftData.period),
    start_time: shiftData.startTime,
    end_time: shiftData.endTime,
    duration: shiftData.endTime - shiftData.startTime,
    team_id: shiftData.teamId,
  }
  
  const { data, error } = await supabase
    .from('fact_shifts')
    .insert(shift)
  
  return { data, error }
}
```

### Shift Tracking Logic

```javascript
// Track players currently on ice
const playersOnIce = {
  home: new Set(),  // Set of player_ids
  away: new Set()
}

// Track active shifts (not yet ended)
const activeShifts = new Map()  // player_id -> { startTime, period, shiftNumber }

function startShift(playerId, teamId, gameTime, period) {
  const shiftNumber = getNextShiftNumber(playerId)
  activeShifts.set(playerId, {
    startTime: gameTime,
    period: period,
    shiftNumber: shiftNumber,
    teamId: teamId
  })
  playersOnIce[teamId === homeTeamId ? 'home' : 'away'].add(playerId)
}

function endShift(playerId, gameTime) {
  const shift = activeShifts.get(playerId)
  if (shift) {
    insertShift({
      gameId: currentGameId,
      playerId: playerId,
      shiftNumber: shift.shiftNumber,
      period: shift.period,
      startTime: shift.startTime,
      endTime: gameTime,
      teamId: shift.teamId
    })
    activeShifts.delete(playerId)
    playersOnIce.home.delete(playerId)
    playersOnIce.away.delete(playerId)
  }
}
```

---

## 3. XY COORDINATES: `fact_player_xy_long`

### Primary Key
```
xy_long_key = "{game_id}_{timestamp}_{player_id}"
Example: "18969_45.5_123"
```

### Required Columns

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `xy_long_key` | TEXT | ✅ | Primary key | "18969_45.5_123" |
| `game_id` | INTEGER | ✅ | FK to dim_schedule | 18969 |
| `period_number` | TEXT | ✅ | Period | "1" |
| `game_time` | DECIMAL | ✅ | Seconds into period | 45.5 |
| `player_id` | INTEGER | ✅ | FK to dim_player | 123 |
| `x_coord` | DECIMAL | ✅ | X position (0-100) | 75.5 |
| `y_coord` | DECIMAL | ✅ | Y position (0-42.5) | 22.0 |

### Coordinate System

```
        0                    50                   100
        ├────────────────────┼────────────────────┤
   42.5 │                    │                    │
        │   DEFENSIVE ZONE   │    NEUTRAL ZONE    │   OFFENSIVE ZONE
        │                    │                    │
        │         ┌──────────┼──────────┐         │
   21.25│         │          │          │         │  ← CENTER ICE
        │         │   GOAL   │   GOAL   │         │
        │         └──────────┼──────────┘         │
        │                    │                    │
      0 │                    │                    │
        └────────────────────┴────────────────────┘
                 BLUE LINE        BLUE LINE
                   (25)             (75)
```

---

## 4. VIDEO HIGHLIGHTS: `fact_video_highlights`

### Primary Key
```
highlight_key = "{game_id}_{event_index}_{clip_number}"
Example: "18969_15_1"
```

### Required Columns

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `highlight_key` | TEXT | ✅ | Primary key | "18969_15_1" |
| `game_id` | INTEGER | ✅ | FK to dim_schedule | 18969 |
| `video_url` | TEXT | ✅ | Video source URL | "https://..." |
| `start_timestamp` | DECIMAL | ✅ | Start time (seconds) | 1234.5 |
| `end_timestamp` | DECIMAL | ✅ | End time (seconds) | 1240.0 |
| `highlight_type` | TEXT | ✅ | Type of highlight | "goal" |

### Optional Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `event_index` | INTEGER | Link to fact_events | 15 |
| `player_id` | INTEGER | Featured player | 123 |
| `team_id` | INTEGER | Featured team | 5 |
| `title` | TEXT | Display title | "Smith Goal" |
| `description` | TEXT | Longer description | "Nice snipe..." |
| `highlight_subtype` | TEXT | Specific type | "snipe" |
| `is_featured` | BOOLEAN | Featured on homepage | false |
| `is_approved` | BOOLEAN | Admin approved | false |

### Highlight Types

```javascript
const HIGHLIGHT_TYPES = [
  'goal',       // Goal scored
  'save',       // Great save
  'hit',        // Big hit
  'fight',      // Fight
  'penalty',    // Penalty call
  'skill',      // Deke, dangle
  'team_play',  // Nice passing
  'defensive',  // Block, stick check
  'other'       // Other notable
]
```

### JavaScript: Insert Highlight

```javascript
async function insertHighlight(highlightData) {
  const highlight = {
    highlight_key: `${highlightData.gameId}_${highlightData.eventIndex}_${highlightData.clipNumber}`,
    game_id: highlightData.gameId,
    event_index: highlightData.eventIndex || null,
    player_id: highlightData.playerId || null,
    team_id: highlightData.teamId || null,
    video_url: highlightData.videoUrl,
    start_timestamp: highlightData.startTime,
    end_timestamp: highlightData.endTime,
    highlight_type: highlightData.type,
    title: highlightData.title || null,
    description: highlightData.description || null,
    is_featured: false,
    is_approved: false,
  }
  
  const { data, error } = await supabase
    .from('fact_video_highlights')
    .insert(highlight)
  
  if (!error && highlightData.eventIndex) {
    // Update the event to mark it has a highlight
    await supabase
      .from('fact_events')
      .update({ 
        has_video_highlight: true,
        highlight_count: supabase.sql`highlight_count + 1`
      })
      .eq('game_id', highlightData.gameId)
      .eq('event_index', highlightData.eventIndex)
  }
  
  return { data, error }
}
```

---

## 5. REFERENCE DATA (Read-Only)

The Tracker should READ from these dimension tables:

### dim_player
```javascript
const { data: players } = await supabase
  .from('dim_player')
  .select('player_id, player_name, jersey_number, position')
  .eq('is_active', true)
  .order('player_name')
```

### dim_team
```javascript
const { data: teams } = await supabase
  .from('dim_team')
  .select('team_id, team_name, team_abbrev')
```

### dim_schedule (Get today's games)
```javascript
const today = new Date().toISOString().split('T')[0]
const { data: games } = await supabase
  .from('dim_schedule')
  .select(`
    game_id, game_date, game_time,
    home_team:dim_team!home_team_id(team_name),
    away_team:dim_team!away_team_id(team_name)
  `)
  .eq('game_date', today)
```

### dim_event_type / dim_event_detail
```javascript
const { data: eventTypes } = await supabase
  .from('dim_event_type')
  .select('event_type_id, event_type, description')

const { data: eventDetails } = await supabase
  .from('dim_event_detail')
  .select('event_detail_id, event_detail, event_type')
```

---

## 6. COMPLETE TRACKER WORKFLOW

```javascript
// 1. GAME SETUP
const game = await loadGame(gameId)
const homeRoster = await loadRoster(game.home_team_id)
const awayRoster = await loadRoster(game.away_team_id)

// 2. PERIOD START
startPeriod(periodNumber)
// Set initial lines on ice

// 3. DURING PLAY
// On each event:
function handleEvent(eventData) {
  // Insert event
  await insertEvent(eventData)
  
  // If goal, handle assists
  if (eventData.eventType === 'Goal') {
    // event_player_1 = goal scorer
    // event_player_2 = assist 1 (optional)
    // event_player_3 = assist 2 (optional)
  }
  
  // Track XY if available
  if (eventData.x && eventData.y) {
    // Coords recorded in event
  }
}

// 4. LINE CHANGES
function handleLineChange(playersOff, playersOn, gameTime) {
  playersOff.forEach(p => endShift(p, gameTime))
  playersOn.forEach(p => startShift(p.id, p.teamId, gameTime, currentPeriod))
}

// 5. PERIOD END
function endPeriod() {
  // End all active shifts
  activeShifts.forEach((shift, playerId) => {
    endShift(playerId, periodEndTime)
  })
}

// 6. GAME END
function endGame() {
  // Final shift cleanup
  // Save game status
  await supabase
    .from('fact_game_status')
    .upsert({
      game_id: gameId,
      status: 'complete',
      final_home_score: homeScore,
      final_away_score: awayScore,
      processed_at: new Date().toISOString()
    })
}
```

---

## 7. VALIDATION RULES

### Event Validation
```javascript
function validateEvent(event) {
  const errors = []
  
  if (!event.game_id) errors.push('game_id required')
  if (!event.event_index) errors.push('event_index required')
  if (!event.event_type) errors.push('event_type required')
  if (!event.event_player_1) errors.push('event_player_1 required')
  if (!event.period_number) errors.push('period_number required')
  if (event.game_time < 0 || event.game_time > 1200) errors.push('game_time invalid')
  if (event.success && !['s', 'u'].includes(event.success)) errors.push('success must be s or u')
  if (event.x_coord && (event.x_coord < 0 || event.x_coord > 100)) errors.push('x_coord out of range')
  if (event.y_coord && (event.y_coord < 0 || event.y_coord > 42.5)) errors.push('y_coord out of range')
  
  return errors
}
```

### Shift Validation
```javascript
function validateShift(shift) {
  const errors = []
  
  if (shift.end_time <= shift.start_time) errors.push('end_time must be after start_time')
  if (shift.duration > 300) errors.push('shift duration suspiciously long (>5 min)')
  
  return errors
}
```
