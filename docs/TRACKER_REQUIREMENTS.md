# BenchSight Tracker - Requirements & Design Document

**Version:** Draft 2.0  
**Date:** 2026-01-07  
**Based on:** Analysis of 4 games, 11,181 event rows, 398 shifts, existing prototypes (v18/v19)

---

## Table of Contents

1. [Critical: ETL Alignment](#critical-etl-alignment)
2. [Database Architecture](#database-architecture)
3. [Current Workflow Summary](#current-workflow-summary)
4. [Data Analysis Findings](#data-analysis-findings)
5. [Requirements Summary](#requirements-summary)
6. [XY Coordinate System Design](#xy-coordinate-system-design)
7. [Linked Event Detection](#linked-event-detection)
8. [Automation Opportunities](#automation-opportunities)
9. [Technical Architecture](#technical-architecture)

---

## Critical: ETL Alignment

### ABSOLUTE REQUIREMENT
The tracker output MUST match the existing `{gameid}_tracking.xlsx` format 1000000%.

**Events Tab Output → fact_event_players (61 columns)**
```
event_id, game_id, player_id, player_game_number, sequence_key, play_key, 
shift_key, linked_event_key, event_chain_key, tracking_event_key, zone_change_key,
period_id, home_team_id, away_team_id, player_team_id, period, event_start_min,
event_start_sec, event_end_min, event_end_sec, event_team_zone, home_team_zone,
away_team_zone, team_venue, side_of_puck, play_detail1, play_detail_2,
play_detail_successful, pressured_pressurer, home_team, away_team, event_type,
event_detail, event_detail_2, event_successful, duration, time_start_total_seconds,
time_end_total_seconds, running_intermission_duration, period_start_total_running_seconds,
running_video_time, event_running_start, event_running_end, player_role, player_team,
is_goal, player_name, season_id, position_id, shot_type_id, zone_entry_type_id,
zone_exit_type_id, stoppage_type_id, giveaway_type_id, takeaway_type_id,
turnover_type_id, pass_type_id, time_bucket_id, strength_id, cycle_key, is_cycle
```

**Shifts Tab Output → fact_shifts (129 columns)**
```
shift_id, game_id, shift_index, period, shift_start_type, shift_stop_type,
shift_start_min, shift_start_sec, shift_end_min, shift_end_sec, home_team, away_team,
home_forward_1, home_forward_2, home_forward_3, home_defense_1, home_defense_2,
home_xtra, home_goalie, away_forward_1, away_forward_2, away_forward_3,
away_defense_1, away_defense_2, away_xtra, away_goalie, shift_start_total_seconds,
shift_end_total_seconds, shift_duration, home_team_strength, away_team_strength,
... (remaining 100+ columns calculated by ETL)
```

### New Columns to Add (Tracker-Specific)

**Events:**
- `is_highlight` (boolean) - User-flagged highlight
- `highlight_key` (varchar) - Links to dim_highlights
- `video_time_seconds` (int) - For YouTube deep links
- `puck_xy_1` through `puck_xy_10` (json: {x, y})
- `player_xy_1` through `player_xy_10` (json per player: {player_id, x, y})
- `shot_net_xy` (json: {x, y}) - Net location for shots

**Shifts:**
- `video_start_seconds` (int)
- `video_end_seconds` (int)

### New Tables Required

```sql
-- YouTube video links per game
CREATE TABLE dim_youtube_videos (
    video_id SERIAL PRIMARY KEY,
    game_id INT REFERENCES dim_games(game_id),
    angle_name VARCHAR(50),  -- 'Main', 'Alt1', 'Alt2'
    youtube_url VARCHAR(500),
    start_offset_seconds INT DEFAULT 0,  -- Offset from video start to game start
    created_at TIMESTAMP DEFAULT NOW()
);

-- Highlight clips
CREATE TABLE fact_highlights (
    highlight_id SERIAL PRIMARY KEY,
    game_id INT REFERENCES dim_games(game_id),
    event_id INT REFERENCES fact_event_players(event_id),
    highlight_type VARCHAR(50),  -- 'Goal', 'Save', 'Hit', 'Custom'
    video_start_seconds INT,
    video_end_seconds INT,
    title VARCHAR(200),
    description TEXT,
    tags VARCHAR(500),  -- Comma-separated
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Database Architecture

### Three-Tier Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TRACKER APPLICATION                               │
│  (Electron + React)                                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE (Local PostgreSQL)                                            │
│  ─────────────────────────                                           │
│  • Raw tracker input                                                 │
│  • Auto-save every 30 seconds                                        │
│  • JSON backups to filesystem                                        │
│  • Full undo/redo history                                            │
│  • Working copy for active editing                                   │
│                                                                      │
│  Tables:                                                             │
│  • stage_events (tracker input format)                               │
│  • stage_shifts (tracker input format)                               │
│  • stage_undo_history                                                │
│  • stage_session_state                                               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ ETL (existing Python scripts)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  INTERMEDIATE (Local PostgreSQL)                                     │
│  ───────────────────────────────                                     │
│  • Transformed/enriched data                                         │
│  • All calculated fields                                             │
│  • Foreign key relationships                                         │
│  • QA validation results                                             │
│                                                                      │
│  Tables:                                                             │
│  • All 111+ existing BenchSight tables                               │
│  • qa_validation_results                                             │
│  • etl_run_log                                                       │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Sync (verified data only)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  DATAMART (Supabase PostgreSQL)                                      │
│  ──────────────────────────────                                      │
│  • Production-ready data                                             │
│  • Dashboard queries                                                 │
│  • API access                                                        │
│  • Row-level security                                                │
│                                                                      │
│  Tables:                                                             │
│  • All fact/dim tables                                               │
│  • dim_youtube_videos (NEW)                                          │
│  • fact_highlights (NEW)                                             │
│  • Materialized views for dashboard                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### Auto-Save Strategy

```javascript
// Every 30 seconds → Local PostgreSQL
setInterval(async () => {
  await localPg.query(`
    INSERT INTO stage_events (game_id, event_data, saved_at)
    VALUES ($1, $2, NOW())
    ON CONFLICT (game_id) DO UPDATE SET event_data = $2, saved_at = NOW()
  `, [gameId, JSON.stringify(state.events)]);
}, 30000);

// Every 5 minutes → JSON backup file
setInterval(async () => {
  const backup = {
    game_id: state.gid,
    timestamp: new Date().toISOString(),
    events: state.events,
    shifts: state.shifts,
    undo_stack: state.undoStack
  };
  await fs.writeFile(
    `backups/${state.gid}_${Date.now()}.json`,
    JSON.stringify(backup, null, 2)
  );
}, 300000);
```

### Data Flow

```
1. TRACKING SESSION
   User tracks game in Tracker app
   → Auto-saves to stage_events/stage_shifts (local PG)
   → JSON backups every 5 min

2. GAME COMPLETE
   User clicks "Finalize Game"
   → Exports to {gameid}_tracking.xlsx format
   → Triggers existing ETL pipeline

3. ETL PROCESSING
   Existing Python ETL runs
   → Reads tracking Excel
   → Transforms to all 111+ tables
   → Writes to intermediate (local PG)
   → Runs QA validations

4. SYNC TO DATAMART
   After QA passes
   → Sync intermediate → Supabase
   → Dashboard sees new data
```

---

## XY Coordinate System Design

### Rink Visualization (Reference: shot-plotter.netlify.app)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RINK DIAGRAM                                 │
│  ViewBox: 0,0 → 200,85 (NHL proportions)                            │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  ●42      ●9                              ●70     ●84       │    │
│  │    ╲      ╱                                ╲     ╱          │    │
│  │     ╲    ╱                                  ╲   ╱           │    │
│  │      [⬤]───────────────────────────────────[⬤]            │    │
│  │       P1                                    P2              │    │
│  │                        ⬤ PUCK                               │    │
│  │  ●61                  (current)             ●22             │    │
│  │                                                             │    │
│  │  [G39]                                            [G99]     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  LEGEND:                                                             │
│  ● = Player (team color, jersey #)                                  │
│  ⬤ = Puck position                                                  │
│  ─── = Movement path (xy1 → xy2 → xy3)                              │
│  Older events = more transparent (0.3 → 0.6 → 1.0 opacity)          │
└─────────────────────────────────────────────────────────────────────┘
```

### Net Diagram (For Shots - Reference: shot-plotter.netlify.app/ice-hockey-net-nhl)

```
When event_type = 'Shot' or 'Goal', popup net diagram:

┌───────────────────────────────────────┐
│           NET LOCATION                │
│  ┌─────────────────────────────────┐  │
│  │ ┌───┬───┬───┬───┬───┬───┬───┐ │  │
│  │ │   │   │   │   │   │   │   │ │  │
│  │ │ TL│ TC│ TC│ TC│ TC│ TC│ TR│ │  │ ← Top shelf
│  │ ├───┼───┼───┼───┼───┼───┼───┤ │  │
│  │ │   │   │   │   │   │   │   │ │  │
│  │ │ ML│ MC│ MC│ MC│ MC│ MC│ MR│ │  │ ← Mid
│  │ ├───┼───┼───┼───┼───┼───┼───┤ │  │
│  │ │   │   │   │   │   │   │   │ │  │
│  │ │ BL│ BC│ BC│ BC│ BC│ BC│ BR│ │  │ ← Low (five hole center)
│  │ └───┴───┴───┴───┴───┴───┴───┘ │  │
│  │  │                           │  │  │
│  │  └───────────────────────────┘  │  │
│  │           Posts                  │  │
│  └─────────────────────────────────┘  │
│                                       │
│  Click to mark shot location          │
│  [Cancel]                             │
└───────────────────────────────────────┘
```

### XY Storage Format

```javascript
// Per-event XY data structure
{
  event_id: 'EV18969001',
  puck_xy: [
    { seq: 1, x: 45.2, y: 32.1 },  // Puck position 1
    { seq: 2, x: 62.8, y: 28.4 },  // Puck position 2 (movement)
  ],
  player_xy: [
    { player_id: 'P42', role: 'event_player_1', positions: [
      { seq: 1, x: 38.1, y: 40.2 },
      { seq: 2, x: 55.3, y: 35.1 }
    ]},
    { player_id: 'P9', role: 'event_player_2', positions: [
      { seq: 1, x: 42.0, y: 22.5 }
    ]},
    { player_id: 'P39', role: 'opp_player_1', positions: [
      { seq: 1, x: 12.0, y: 42.5 }  // Goalie
    ]}
  ],
  shot_net_xy: { x: 3, y: 4 }  // Grid position (only for shots)
}
```

### Visual History (Last N Events)

```javascript
// Show last 5 events on rink, with decreasing opacity
const EVENT_HISTORY_COUNT = 5;
const OPACITY_SCALE = [1.0, 0.7, 0.5, 0.35, 0.2];  // Current → oldest

function renderEventHistory(events) {
  const recent = events.slice(-EVENT_HISTORY_COUNT);
  
  recent.forEach((evt, idx) => {
    const opacity = OPACITY_SCALE[recent.length - 1 - idx];
    const teamColor = evt.team === 'home' ? homeColor : awayColor;
    
    // Draw player positions
    evt.player_xy.forEach(player => {
      player.positions.forEach((pos, posIdx) => {
        // Draw dot with team color, player #
        drawPlayerDot(pos.x, pos.y, player.player_id, teamColor, opacity);
        
        // Draw line to next position
        if (posIdx < player.positions.length - 1) {
          const next = player.positions[posIdx + 1];
          drawLine(pos.x, pos.y, next.x, next.y, teamColor, opacity);
        }
      });
    });
    
    // Draw puck
    evt.puck_xy.forEach((pos, posIdx) => {
      drawPuck(pos.x, pos.y, opacity);
      if (posIdx < evt.puck_xy.length - 1) {
        const next = evt.puck_xy[posIdx + 1];
        drawLine(pos.x, pos.y, next.x, next.y, '#000', opacity);
      }
    });
  });
}
```

---

## Linked Event Detection

### Always-Linked Event Pairs

These events ALWAYS create linked events automatically:

| Primary Event | Auto-Creates | Relationship |
|---------------|--------------|--------------|
| Stoppage | DeadIce | 1:1 always |
| Shot_OnNet | Save | 1:1 (unless goal) |
| Save_Rebound | Rebound | 1:1 always |
| Save_Freeze | Stoppage + DeadIce | 1:1:1 chain |
| Goal_Scored | Shot_Goal | 1:1 always |

### Smart Detection Rules

```javascript
const LINKED_EVENT_RULES = {
  // After a pass that crosses a line
  'Pass_Completed': {
    detect: (evt, context) => {
      const startZone = getZoneFromXY(evt.puck_xy[0]);
      const endZone = getZoneFromXY(evt.puck_xy[evt.puck_xy.length - 1]);
      if (startZone !== endZone) {
        return {
          suggest: true,
          linkedType: startZone === 'o' ? 'Zone_Exit' : 'Zone_Entry',
          confidence: 0.95,
          message: `Pass crossed ${startZone} → ${endZone} zone line`
        };
      }
    }
  },
  
  // After a turnover with zone change
  'Turnover_Giveaway': {
    detect: (evt, context) => {
      const prevZone = context.previousEvent?.zone;
      const currZone = evt.zone;
      if (prevZone && prevZone !== currZone) {
        return {
          suggest: true,
          linkedType: 'Zone_Entry',
          confidence: 0.85,
          message: `Possession change with zone transition`
        };
      }
    }
  },
  
  // Shot → Save chain
  'Shot_OnNetSaved': {
    detect: () => ({
      suggest: true,
      linkedType: 'Save',
      confidence: 0.99,
      autoCreate: true,  // Don't even ask, just do it
      message: 'Auto-creating Save event'
    })
  }
};
```

### Linked Event UI

```
┌─────────────────────────────────────────────────────────────────────┐
│  ⚡ LINKED EVENT DETECTED                                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Pass_Completed (Zone Exit detected)                                 │
│                                                                      │
│  Your pass crossed from offensive → neutral zone.                    │
│  Create linked Zone_Exit event?                                      │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ ✓ Copy all player XY positions                              │    │
│  │ ✓ Copy play details                                         │    │
│  │ ✓ Same timestamp                                            │    │
│  │ ○ Flip event/opp players (for opposing perspective)         │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  [Create Linked] [Skip] [Always Auto-Create]                         │
│   (Enter)        (Esc)  (Shift+Enter)                               │
└─────────────────────────────────────────────────────────────────────┘
```

### Shot → Save Player Flip Logic

```javascript
function createLinkedSaveEvent(shotEvent) {
  const saveEvent = {
    ...shotEvent,
    event_type: 'Save',
    event_detail: determineSaveType(shotEvent),  // Save_Rebound, Save_Freeze, etc.
    
    // FLIP players
    event_player_1: shotEvent.opp_player_1,      // Goalie becomes primary
    event_player_2: shotEvent.opp_player_2,      // Other defenders
    opp_player_1: shotEvent.event_player_1,      // Shooter becomes opponent
    opp_player_2: shotEvent.event_player_2,      // Other attackers
    
    // Copy XY but flip player assignments
    player_xy: shotEvent.player_xy.map(p => ({
      ...p,
      role: flipRole(p.role)  // event_player_1 → opp_player_1, etc.
    })),
    
    // Same puck position
    puck_xy: shotEvent.puck_xy
  };
  
  return saveEvent;
}
```

---

## Hotkey System (User-Editable)

### Default Hotkey Configuration

```javascript
// Stored in localStorage, editable via Settings modal
const DEFAULT_HOTKEYS = {
  // Video Controls
  'space': { action: 'togglePlay', label: 'Play/Pause' },
  'arrowleft': { action: 'frameBack', label: 'Frame Back' },
  'arrowright': { action: 'frameForward', label: 'Frame Forward' },
  'shift+arrowleft': { action: 'jumpBack5', label: 'Jump Back 5s' },
  'shift+arrowright': { action: 'jumpForward5', label: 'Jump Forward 5s' },
  '[': { action: 'slowDown', label: 'Slow Down' },
  ']': { action: 'speedUp', label: 'Speed Up' },
  '1': { action: 'angle1', label: 'Camera Angle 1' },
  '2': { action: 'angle2', label: 'Camera Angle 2' },
  '3': { action: 'angle3', label: 'Camera Angle 3' },
  
  // Event Types
  's': { action: 'evtShot', label: 'Shot' },
  'g': { action: 'evtGoal', label: 'Goal' },
  'p': { action: 'evtPass', label: 'Pass' },
  't': { action: 'evtTurnover', label: 'Turnover' },
  'f': { action: 'evtFaceoff', label: 'Faceoff' },
  'z': { action: 'evtZone', label: 'Zone Entry/Exit' },
  'o': { action: 'evtPossession', label: 'Possession' },
  'v': { action: 'evtSave', label: 'Save' },
  'r': { action: 'evtRebound', label: 'Rebound' },
  'd': { action: 'evtDeadIce', label: 'Dead Ice' },
  'x': { action: 'evtStoppage', label: 'Stoppage' },
  'n': { action: 'evtPenalty', label: 'Penalty' },
  'y': { action: 'evtPlay', label: 'Play (Off/Def)' },
  
  // Team Selection
  'h': { action: 'teamHome', label: 'Home Team' },
  'a': { action: 'teamAway', label: 'Away Team' },
  
  // XY Mode
  '`': { action: 'modePuck', label: 'Puck XY Mode' },
  'e': { action: 'modeEventPlayer', label: 'Event Player XY' },
  'w': { action: 'modeOppPlayer', label: 'Opp Player XY' },
  
  // Event Actions
  'enter': { action: 'logEvent', label: 'Log Event' },
  'escape': { action: 'clearForm', label: 'Clear Form' },
  'l': { action: 'createLinked', label: 'Create Linked Event' },
  'ctrl+z': { action: 'undo', label: 'Undo' },
  'ctrl+shift+z': { action: 'redo', label: 'Redo' },
  'ctrl+c': { action: 'copyLastEvent', label: 'Copy Last Event' },
  
  // Shift Actions
  'shift+n': { action: 'newShift', label: 'New Shift' },
  'shift+e': { action: 'endShift', label: 'End Current Shift' },
  'q': { action: 'quickSwap', label: 'Quick Swap Mode' },
  
  // Highlight
  'shift+h': { action: 'toggleHighlight', label: 'Toggle Highlight' },
  
  // Player Selection (Numpad)
  'numpad1': { action: 'selectEvtPlayer1', label: 'Event Player 1' },
  'numpad2': { action: 'selectEvtPlayer2', label: 'Event Player 2' },
  'numpad3': { action: 'selectEvtPlayer3', label: 'Event Player 3' },
  'numpad4': { action: 'selectOppPlayer1', label: 'Opp Player 1' },
  'numpad5': { action: 'selectOppPlayer2', label: 'Opp Player 2' },
  'numpad6': { action: 'selectOppPlayer3', label: 'Opp Player 3' },
};
```

### Hotkey Editor UI

```
┌─────────────────────────────────────────────────────────────────────┐
│  ⌨️ HOTKEY SETTINGS                                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Search: [________________]                                          │
│                                                                      │
│  ┌─ VIDEO ──────────────────────────────────────────────────────┐   │
│  │ Play/Pause        [Space     ] ← Click to rebind             │   │
│  │ Frame Back        [←         ]                               │   │
│  │ Frame Forward     [→         ]                               │   │
│  │ Slow Down         [[         ]                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─ EVENTS ─────────────────────────────────────────────────────┐   │
│  │ Shot              [S         ]                               │   │
│  │ Goal              [G         ]                               │   │
│  │ Pass              [P         ]                               │   │
│  │ ... (expandable)                                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  [Reset to Defaults] [Import] [Export]              [Save] [Cancel]  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ML Suggestion System

### Transition Matrix (From Data Analysis)

```javascript
// Pre-computed from 4 games of tracking data
const TRANSITION_MATRIX = {
  'Shot': {
    'Save': 0.487, 'Turnover': 0.170, 'Possession': 0.152,
    'Zone_Entry_Exit': 0.048, 'Stoppage': 0.039
  },
  'Pass': {
    'Zone_Entry_Exit': 0.329, 'Possession': 0.302, 'Turnover': 0.150,
    'Pass': 0.107, 'Shot': 0.092
  },
  'Save': {
    'Rebound': 0.642, 'Stoppage': 0.325, 'Possession': 0.009
  },
  'Turnover': {
    'Possession': 0.542, 'Zone_Entry_Exit': 0.279, 'Pass': 0.087
  },
  'Faceoff': {
    'Possession': 0.343, 'Pass': 0.195, 'Zone_Entry_Exit': 0.189,
    'Shot': 0.142, 'Turnover': 0.083
  },
  'Goal': {
    'Stoppage': 0.688, 'DeadIce': 0.312
  }
};

// Detail-level predictions
const DETAIL_TRANSITIONS = {
  'Shot_OnNetSaved': { 'Save_Rebound': 0.66, 'Save_Freeze': 0.32 },
  'Save_Rebound': { 'Rebound_TeamRecovered': 0.49, 'Rebound_OppTeamRecovered': 0.36 },
  'Save_Freeze': { 'Stoppage_Play': 0.91 }
};
```

### Suggestion Display

```
┌─────────────────────────────────────────────────────────────────────┐
│  After: Shot_OnNetSaved                                             │
├─────────────────────────────────────────────────────────────────────┤
│  SUGGESTED NEXT:                                                     │
│  [1] Save_Rebound  ████████████████░░░░ 66%   [Enter]               │
│  [2] Save_Freeze   ██████████░░░░░░░░░░ 32%   [2]                   │
│  [3] Other...                                  [3]                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Current Workflow Summary

### Video Setup
- Multiple camera angles for puck visibility
- Premiere Pro for playback, angle switching, scrubbing
- Watch-back tracking (not real-time)
- Video time ≠ Game time (intermissions create offset)

### Pain Points Identified
| Pain Point | Impact |
|------------|--------|
| Too many clicks | 10+ fields per event |
| Linked events = 2x work | Duplicate data entry |
| Excel is slow | 4k+ rows per game |
| No validation | Errors go undetected |
| Manual zone/team | Could be inferred from XY |
| No XY coordinates | Want spatial data |
| Shift player entry | Re-enter 12+ players when 1-3 change |
| No video integration | Must switch between apps |

### New Requirements
| Requirement | Details |
|-------------|---------|
| XY Coordinates | Up to 10 points per player per event |
| Puck XY | Up to 10 puck positions per event |
| Shot net location | 1 additional XY point for shots |
| Highlight flag | Boolean per event |
| Video time storage | Seconds for YouTube link generation |
| Player validation | Only on-ice players can be in events |
| Shift boundary validation | Events shouldn't span shift boundaries |
| Video integration | Easy switching, zooming, super scrub |
| ML suggestions | Predict next likely events |

---

## Data Analysis Findings

### Event Volume (Per Game Average)

| Event Type | Per Game | Notes |
|------------|----------|-------|
| Possession | 378 | Most frequent - puck retrievals, recoveries |
| Zone_Entry_Exit | 284 | Entries, exits, keep-ins |
| Pass | 255 | Completed, missed, deflected, intercepted |
| Turnover | 186 | Giveaways and takeaways |
| Shot | 109 | Various outcomes |
| Save | 53 | Follows 48.7% of shots |
| Faceoff | 42 | After stoppages, goals, penalties |
| Stoppage | 41 | Play stoppages |
| DeadIce | 39 | Dead puck situations |
| Rebound | 35 | Follows 64.2% of saves |
| Play | 19 | Offensive/defensive plays |
| Goal | 4 | Scoring events |

**Total: ~1,458 unique events per game**

### Linked Events (20.4% of all events)

Most common compound actions:

| Linked Combination | Count | Common Details |
|--------------------|-------|----------------|
| Pass ↔ Zone_Entry_Exit | 75 | Pass_Completed ↔ Zone_Exit (44) |
| Pass ↔ Turnover | 67 | Pass_Missed ↔ Turnover_Giveaway (36) |
| Turnover ↔ Zone_Entry_Exit | 63 | Turnover_Giveaway ↔ Zone_Entry (23) |
| Rebound ↔ Save ↔ Shot | 55 | Full shot sequence |
| Pass ↔ Turnover ↔ Zone_Entry_Exit | 45 | Triple-linked |
| Shot ↔ Turnover | 34 | Shot_Blocked ↔ Turnover_Giveaway |
| DeadIce ↔ Save ↔ Shot ↔ Stoppage | 33 | Goalie freeze sequence |
| Goal sequence | 6 | DeadIce ↔ Goal ↔ Shot ↔ Stoppage |

### Event Sequence Predictions (ML Basis)

**After Shot:**
- 48.7% → Save
- 17.0% → Turnover
- 15.2% → Possession

**After Pass:**
- 32.9% → Zone_Entry_Exit
- 30.2% → Possession
- 15.0% → Turnover

**After Faceoff:**
- 34.3% → Possession
- 19.5% → Pass
- 18.9% → Zone_Entry_Exit

**After Save:**
- 64.2% → Rebound
- 32.5% → Stoppage

**After Turnover:**
- 54.2% → Possession
- 27.9% → Zone_Entry_Exit

**After Zone_Entry_Exit:**
- 35.3% → Possession
- 26.2% → Turnover
- 13.3% → Pass

### Detail-Level Predictions

| After This | Most Likely Next |
|------------|------------------|
| Shot_OnNetSaved | Save_Rebound (66%), Save_Freeze (32%) |
| Save_Rebound | Rebound_TeamRecovered (49%), Rebound_OppTeamRecovered (36%) |
| Save_Freeze | Stoppage_Play (91%) |
| Pass_Completed | Zone_Exit (20%), Pass_Completed (10%) |
| Zone_Entry | Turnover_Giveaway (26%), Shot_OnNetSaved (10%) |
| Turnover_Giveaway | PuckRetrieval (31%), Zone_Keepin (12%) |

### Players Per Event

| Players | Count | Percentage |
|---------|-------|------------|
| 1 | 2,250 | 38.6% |
| 2 | 2,232 | 38.3% |
| 3 | 1,062 | 18.2% |
| 4 | 201 | 3.4% |
| 5+ | 86 | 1.5% |

**Average: 1.92 players per event**

### Player Role Patterns in Shot↔Save Links

**Shot event:**
- event_player_1: Shooter (100%)
- opp_player_1: Goalie (99%)
- opp_player_2: Other defender (50%)

**Save event (roles flip):**
- event_player_1: Goalie (100%)
- opp_player_1: Shooter (99%)
- event_player_2: Other defender (51%)

### Shift Analysis

| Metric | Value |
|--------|-------|
| Shifts per game | ~100 |
| Average duration | 33 sec |
| Median duration | 22 sec |
| Min/Max | 0 / 130 sec |

**Shift Start Types:**
- OtherFaceoff: 66%
- FaceoffAfterGoal: 11%
- PeriodStart/GameStart: 9%
- Intermission: 6%
- FaceoffAfterPenalty: 6%

**Shift Stop Types:**
- Goalie Stopped: 41%
- Icing: 16%
- Puck Out of Play: 10%
- Goal: 13%
- Period End: 7%
- Penalty: 6%

### Player Changes Between Shifts

| Changes | Home | Away |
|---------|------|------|
| 1 player | 32% | 30% |
| 2 players | 36% | 34% |
| 3 players | 13% | 15% |
| 4+ players | 19% | 21% |

**Average: 2.4-2.5 player changes per shift transition**

### Zone Distribution by Event Type

| Event Type | Offensive | Defensive | Neutral |
|------------|-----------|-----------|---------|
| Shot | 100% | 0% | 0% |
| Goal | 100% | 0% | 0% |
| Save | 0% | 100% | 0% |
| Rebound | 0% | 100% | 0% |
| Faceoff | 37% | 31% | 33% |
| Pass | 43% | 34% | 22% |
| Turnover | 41% | 39% | 19% |
| Zone_Entry_Exit | 47% | 48% | 6% |

### Video Time Offset

| Period | Video Start (sec) | Offset |
|--------|-------------------|--------|
| 1 | 0 | - |
| 2 | 1152 | +72 sec (intermission) |
| 3 | 2296 | +64 sec (intermission) |

---

## Requirements Summary

### Must Have (P0)

1. **Event Entry**
   - All current event types and details
   - Multi-player support (1-9 players per event)
   - Linked event support with auto-population
   - XY coordinates (up to 10 per player, 10 for puck)
   - Shot net location XY
   - Highlight flag per event

2. **Shift Entry**
   - 14 player slots (7 home, 7 away)
   - Quick swap UI (not full re-entry)
   - Zone start/end tracking
   - Start/stop type selection

3. **Full CRUD Operations**
   - **Create** new events/shifts
   - **Read** existing games from Supabase
   - **Update** ALL fields on ALL events/shifts (including old games without XY)
   - **Delete** events/shifts/players from events
   - Add/remove players from existing events

4. **Validation & Error Checking**
   - Only on-ice players can be in events
   - Events bounded by shifts
   - Required field validation
   - **NORAD verification** - warn if tracked goals don't match official record
   - Real-time error warnings

5. **Video Integration**
   - Multi-angle switching (local files + YouTube)
   - Variable speed scrubbing ("super scrub")
   - Zooming
   - Video time ↔ game time mapping (handle intermission offsets)
   - Store video seconds for YouTube deep links
   - Videos are pre-synced (same start time across angles)

6. **Data Integration**
   - Load game rosters directly from Supabase
   - Auto-save (no manual save button)
   - Read/write prior games from Supabase
   - Match fact_event_players schema (61 columns)
   - Match fact_shifts schema (129 columns)

7. **UI Essentials**
   - Dependent/cascading dropdowns (event_type → detail → detail_2)
   - Running basic box score during tracking
   - Extensive hotkeys
   - Guides/tooltips for new users

### Should Have (P1)

1. **ML Suggestions**
   - Next event type prediction
   - Next event detail prediction
   - Auto-event creation for common sequences (Shot → Save → Rebound)
   - Based on sequence analysis above

2. **Auto-Fill**
   - Zone from XY coordinates (puck position)
   - Team carry-forward until possession change
   - Linked event data copy (everything except type/detail)
   - Shot→Save player role flip

3. **UI Optimizations**
   - Quick-add buttons for common sequences
   - Undo/redo with history
   - Batch edit capabilities

### Nice to Have (P2)

1. Rink visualization for XY entry (click-to-place)
2. Player tracking overlay on video
3. Auto-shift detection from player XY movement
4. Heat map preview during tracking
5. Offline mode (future consideration)

---

## Automation Opportunities

### High-Value Automations

| Manual Today | Automation | Confidence |
|--------------|------------|------------|
| Zone entry for every event | Infer from puck XY | 100% |
| Team for every event | Carry forward until possession change | 95% |
| Linked event data entry | Copy all fields except type/detail | 100% |
| Event success | Already auto-calculated | 100% |
| Shot → Save flip | Auto-flip player roles | 100% |
| Save_Freeze → Stoppage | Auto-suggest next event | 91% |
| Shot_OnNet → Save | Auto-suggest next event | 66% |
| Shift player changes | Show diff, confirm swaps | 95% |

### Linked Event Auto-Fill

When creating linked event:
```
Copy from primary event:
✓ All player IDs
✓ All XY coordinates  
✓ Play details 1 & 2
✓ Zone
✓ Time
✓ Team

User enters:
- Event type (dropdown)
- Event detail (cascading)
- Event detail 2 (if applicable)

Special case: Shot → Save
✓ Auto-flip: event_player_1 ↔ opp_player_1
✓ Auto-flip: event_player_2 ↔ opp_player_2
```

### ML Suggestion System

Based on transition analysis, show top 3 predicted next events:

```
After: Shot_OnNetSaved
┌─────────────────────────────────────┐
│ Suggested Next:                     │
│ [1] Save_Rebound (66%)    [Enter]   │
│ [2] Save_Freeze (32%)     [2]       │
│ [3] Save_Played (2%)      [3]       │
└─────────────────────────────────────┘
```

### Shift Quick-Swap UI

Instead of entering all 14 players:

```
┌─────────────────────────────────────────────┐
│ HOME                    │ AWAY              │
│ F1: 53 [change]         │ F1: 70 [change]   │
│ F2: 20 [change]         │ F2: 75 [change]   │
│ F3: 12 → [24]           │ F3: 49 [change]   │
│ D1: 8  [change]         │ D1: 52 [change]   │
│ D2: 21 → [77]           │ D2: 22 [change]   │
│ G:  99 [change]         │ G:  39 [change]   │
└─────────────────────────────────────────────┘
│ [Apply 2 changes] [Full line change] [Undo] │
```

---

## Proposed Design Concepts

### Concept A: Integrated Video Player

```
┌─────────────────────────────────────────────────────────────────┐
│ [Angle 1] [Angle 2] [Angle 3]  │ Game: 18969 │ Period: 2      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    VIDEO PLAYER                                 │
│                    (with XY click overlay)                      │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ ◀◀ ◀ [▶] ▶ ▶▶  │ 0.25x 0.5x [1x] 2x │ 12:34 / 54:21          │
├─────────────────────────────────────────────────────────────────┤
│ EVENT ENTRY                    │ CURRENT SHIFT                  │
│ Type: [Shot      ▼]            │ #42: 5v5 Full Strength         │
│ Detail: [Shot_OnNetSaved ▼]    │ 12:45 - ongoing                │
│ Detail2: [Shot-Wrist     ▼]    │ [New Shift] [End Shift]        │
│                                │                                │
│ Players:                       │ HOME         AWAY              │
│ E1: [53] Shooter    (x,y)      │ 53 20 12     70 75 49          │
│ E2: [  ]            (x,y)      │ 8  21        52 22             │
│ O1: [39] Goalie     (x,y)      │ 99           39                │
│                                │                                │
│ [+ Add Linked] [★ Highlight]   │                                │
│                                │                                │
│ SUGGESTED NEXT:                │                                │
│ [Save_Rebound 66%] [Save_Freeze 32%]                           │
└─────────────────────────────────────────────────────────────────┘
```

### Concept B: Side-by-Side Video + Rink

```
┌──────────────────────────┬──────────────────────────────────────┐
│     VIDEO PLAYER         │         RINK DIAGRAM                 │
│                          │    ┌─────────────────────┐            │
│                          │    │  ●53  ●20           │            │
│                          │    │       ●12     ⬤puck │            │
│                          │    │  ●8   ●21           │            │
│                          │    │         [G99]       │            │
│                          │    └─────────────────────┘            │
├──────────────────────────┴──────────────────────────────────────┤
│ QUICK ENTRY BAR                                                 │
│ [Faceoff] [Pass] [Shot] [Save] [Turnover] [Zone] [Stoppage]     │
├─────────────────────────────────────────────────────────────────┤
│ RECENT EVENTS                   │ SHIFT PANEL                   │
│ 12:34 Pass_Completed #53        │ Players on ice...             │
│ 12:32 Zone_Exit #53             │                               │
│ 12:28 Possession #20            │ [Swap Players]                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technical Architecture (Confirmed)

### Platform: Electron + React

**Why Electron:**
- Desktop-first (your requirement)
- Native video handling (local files + YouTube)
- Can access local filesystem for video files
- SQLite for local fast operations
- Cross-platform if needed later

**Stack:**
```
┌─────────────────────────────────────────────────────┐
│                  ELECTRON APP                        │
├─────────────────────────────────────────────────────┤
│  React Frontend                                      │
│  ├── Video Player (react-player or custom)          │
│  ├── Rink Diagram Component (XY entry)              │
│  ├── Event Entry Forms                              │
│  ├── Shift Manager                                  │
│  ├── Box Score Live Display                         │
│  └── Hotkey Handler                                 │
├─────────────────────────────────────────────────────┤
│  State Management (Zustand or Redux)                │
│  ├── Current game state                             │
│  ├── Undo/redo history                              │
│  └── ML suggestion cache                            │
├─────────────────────────────────────────────────────┤
│  Data Layer                                          │
│  ├── Local SQLite (fast ops, auto-save)             │
│  ├── Supabase Client (sync, rosters)                │
│  └── File System (video access)                     │
└─────────────────────────────────────────────────────┘
```

### Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   SUPABASE   │◄───►│  LOCAL DB    │◄───►│   TRACKER    │
│              │     │  (SQLite)    │     │     UI       │
│  - Rosters   │     │              │     │              │
│  - Games     │     │  - Working   │     │  - Events    │
│  - Events    │     │    copy      │     │  - Shifts    │
│  - Shifts    │     │  - Auto-save │     │  - Video     │
│  - NORAD     │     │  - Undo hist │     │  - XY        │
└──────────────┘     └──────────────┘     └──────────────┘
        │                   │                    │
        └───────────────────┴────────────────────┘
                    Real-time sync
```

### Video Architecture

```
Video Sources:
├── Local Files (MP4, MOV, etc.)
│   └── Angle 1: /path/to/game_18969_angle1.mp4
│   └── Angle 2: /path/to/game_18969_angle2.mp4
│   └── Angle 3: /path/to/game_18969_angle3.mp4
│
└── YouTube (after upload)
    └── https://youtube.com/watch?v=ABC123
    └── Deep links: ?t=1234 (seconds)

Time Mapping:
┌─────────────────────────────────────────────────────┐
│ Game Clock: 18:00 P1 │ Video Time: 0:00            │
│ Game Clock: 00:00 P1 │ Video Time: 18:00           │
│ Intermission         │ Video Time: 18:00 - 19:12   │
│ Game Clock: 18:00 P2 │ Video Time: 19:12           │
│ ...                                                 │
└─────────────────────────────────────────────────────┘
```

### Auto-Save Strategy

```javascript
// Debounced auto-save on every change
const autoSave = debounce(async (state) => {
  // 1. Save to local SQLite immediately
  await localDb.saveGame(state);
  
  // 2. Sync to Supabase in background
  await supabase.upsertGame(state);
  
  // 3. Update sync status indicator
  setLastSaved(Date.now());
}, 500); // 500ms debounce
```

### NORAD Validation

```javascript
// On game load, fetch official NORAD data
const noradData = await supabase
  .from('norad_games')
  .select('goals')
  .eq('game_id', gameId);

// Compare during tracking
function validateGoal(goalEvent) {
  const trackedGoals = getTrackedGoals();
  const noradGoals = noradData.goals;
  
  if (!noradGoals.includes(goalEvent.player_id)) {
    return {
      warning: true,
      message: `⚠️ Player ${goalEvent.player_name} scored in tracker but not in NORAD`
    };
  }
}
```

---

## Hotkey Design

### Global Hotkeys (Always Active)

| Key | Action |
|-----|--------|
| `Space` | Play/Pause video |
| `←` / `→` | Frame step (when paused) |
| `Shift+←` / `Shift+→` | 5 second jump |
| `[` / `]` | Slow down / speed up playback |
| `1` / `2` / `3` | Switch camera angle |
| `Ctrl+Z` | Undo |
| `Ctrl+Shift+Z` | Redo |
| `Ctrl+S` | Force sync to Supabase |
| `Escape` | Cancel current action |

### Event Entry Hotkeys

| Key | Action |
|-----|--------|
| `F` | New Faceoff |
| `S` | New Shot |
| `P` | New Pass |
| `G` | New Goal |
| `T` | New Turnover |
| `Z` | New Zone Entry/Exit |
| `V` | New Save |
| `R` | New Rebound |
| `D` | New DeadIce |
| `O` | New Stoppage |
| `H` | Toggle Highlight flag |
| `L` | Create Linked Event |
| `Enter` | Confirm/Save event |
| `Tab` | Next field |
| `Shift+Tab` | Previous field |

### Shift Hotkeys

| Key | Action |
|-----|--------|
| `N` | New Shift |
| `E` | End Current Shift |
| `Q` | Quick swap mode (then click players) |

### Number Pad for Players

| Key | Action |
|-----|--------|
| `Numpad 1-6` | Select event_player slot |
| `Shift+Numpad 1-6` | Select opp_player slot |
| Then type jersey number |

---

## Live Box Score Design

```
┌─────────────────────────────────────────────────────┐
│                  LIVE BOX SCORE                      │
├─────────────────────────────────────────────────────┤
│ PLATINUM (H)          3 - 2          VELODROME (A)  │
├─────────────────────────────────────────────────────┤
│ Period 2    │ 12:34 │ Shift #45 │ 5v5 Full Strength │
├─────────────────────────────────────────────────────┤
│         HOME │ STAT        │ AWAY                   │
│           23 │ Shots       │ 18                     │
│           12 │ SOG         │ 11                     │
│            8 │ Saves       │ 9                      │
│           15 │ Faceoffs    │ 12                     │
│            3 │ Giveaways   │ 5                      │
│            2 │ Takeaways   │ 1                      │
│            1 │ Penalties   │ 2                      │
│          54% │ Zone Time   │ 46%                    │
├─────────────────────────────────────────────────────┤
│ ⚠️ WARNINGS:                                        │
│ • Player #53 has goal not in NORAD                  │
│ • Event at 12:34 outside shift bounds               │
└─────────────────────────────────────────────────────┘
```

---

## Workflow Modes

### Mode 1: New Game Tracking

```
1. Select game from Supabase (or create new)
2. Rosters auto-load from Supabase
3. Load video files (local) or YouTube URL
4. Sync video angles
5. Start tracking
6. Auto-save continuously
7. Close when done (already saved)
```

### Mode 2: Edit Existing Game

```
1. Load game from Supabase
2. All events/shifts populate
3. Video loads (if still available)
4. Edit any field on any event/shift
5. Add XY to old events (backfill)
6. Add/remove players from events
7. Auto-save on every change
```

### Mode 3: Review & Validate

```
1. Load completed game
2. Run validation checks
3. Compare to NORAD official data
4. Fix discrepancies
5. Mark as "verified"
```

---

## Open Questions (Answered)

| Question | Answer |
|----------|--------|
| Video files | Both local and YouTube |
| Angle sync | Pre-synced (same start time) |
| Offline | Not required yet |
| Edit after | **YES - critical requirement** |
| Platform | Desktop (Electron) |
| YouTube | Yes, videos uploaded after tracking |

---

## Next Steps

1. **Confirm hotkey mappings** - Review proposed hotkeys, adjust as needed
2. **Design database schema** - Local SQLite structure for auto-save + undo
3. **Design Supabase sync** - What tables, what fields, conflict resolution
4. **Build video player prototype** - Test multi-angle + scrubbing
5. **Build event entry MVP** - Core form with hotkeys
6. **Build shift tracker** - Quick-swap UI
7. **Integrate ML suggestions** - From transition matrix
8. **Add validations** - NORAD checks, shift bounds, etc.

---

## Estimated Complexity

| Component | Effort | Priority |
|-----------|--------|----------|
| Video player with multi-angle | High | P0 |
| Event entry form + hotkeys | Medium | P0 |
| Supabase integration | Medium | P0 |
| Shift tracker | Medium | P0 |
| Auto-save + local DB | Medium | P0 |
| Cascading dropdowns | Low | P0 |
| XY click-to-place | Medium | P1 |
| ML suggestions | Low | P1 |
| Live box score | Low | P1 |
| NORAD validation | Low | P1 |
| Undo/redo history | Medium | P1 |
| Edit existing games | Medium | P0 |

---

*Document updated with confirmed requirements*
