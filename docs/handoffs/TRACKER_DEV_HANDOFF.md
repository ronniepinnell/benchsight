# Tracker Developer Handoff

**Role:** Game Tracker Developer  
**Version:** 2.0  
**Date:** December 30, 2025

---

## Your Mission

Build an interactive web-based hockey game tracker that allows users to:
1. Load existing game data from Supabase
2. Track live game events and shifts in real-time
3. Write data back to Supabase (save drafts, publish final)
4. Validate data quality before publishing

---

## Quick Start

### 1. Get the Codebase
```bash
unzip benchsight_COMPLETE_FULL.zip
cd benchsight_COMPLETE_FULL
```

### 2. Understand the Data Model
- Events are individual plays (shots, passes, goals, etc.)
- Shifts are time periods when specific players are on ice
- Each event belongs to a shift
- Events can be linked (shot → save → rebound)

### 3. Key Files to Review
- `developer_handoffs/tracker_dev/` - Existing tracker docs
- `dashboard/tracker_*.html` - Prototype tracker UIs
- `data/output/dim_*.csv` - All dimension tables (lookups)
- `data/output/fact_events.csv` - Event structure
- `data/output/fact_shifts.csv` - Shift structure

---

## Data Architecture

### Core Tables You'll Write To

| Table | Purpose | Primary Key |
|-------|---------|-------------|
| `fact_events` | All game events | `event_key` |
| `fact_shifts` | All shifts | `shift_key` |
| `fact_events_player` | Event-player junction | `event_player_key` |
| `fact_shifts_player` | Shift-player junction | `shift_player_key` |
| `staging_events` | Draft events before publish | (use for saves) |
| `staging_shifts` | Draft shifts before publish | (use for saves) |

### Key Generation Patterns

```javascript
// Event Key: EV{game_id}{event_index padded to 5 digits}
const eventKey = `EV${gameId}${String(eventIndex).padStart(5, '0')}`;
// Example: EV1896900001, EV1896900002

// Shift Key: {game_id}_{shift_index}
const shiftKey = `${gameId}_${shiftIndex}`;
// Example: 18969_1, 18969_2

// Event Player Key: {event_key}_{player_index}
const eventPlayerKey = `${eventKey}_${playerIndex}`;
// Example: EV1896900001_1, EV1896900001_2

// Shift Player Key: {shift_key}_{player_id}
const shiftPlayerKey = `${shiftKey}_${playerId}`;
// Example: 18969_1_P001
```

---

## Dimension Tables Reference

### CRITICAL: Load These On Startup

These tables provide dropdowns, validation, and ID lookups:

#### Event Types (`dim_event_type`)
| event_type_id | event_type |
|---------------|------------|
| EVT001 | Shot |
| EVT002 | Pass |
| EVT003 | Faceoff |
| EVT004 | Goal |
| EVT005 | Save |
| EVT006 | Hit |
| EVT007 | Block |
| EVT008 | Turnover |
| EVT009 | Takeaway |
| EVT010 | Zone Entry |
| EVT011 | Zone Exit |
| ... | ... |

#### Event Details (`dim_event_detail`)
Provides detail options based on event type:
| event_detail_id | event_detail | parent_event_type |
|-----------------|--------------|-------------------|
| ED001 | Wrist Shot | Shot |
| ED002 | Slap Shot | Shot |
| ED003 | Snap Shot | Shot |
| ED004 | Backhand | Shot |
| ED005 | Tip-in | Shot |
| ED006 | Saucer Pass | Pass |
| ED007 | Tape to Tape | Pass |
| ... | ... | ... |

#### Play Details (`dim_play_detail`, `dim_play_detail_2`)
```sql
-- Used for play context
SELECT * FROM dim_play_detail;
-- Examples: Rush, Cycle, Power Play, Penalty Kill, Breakaway, Odd-Man Rush

SELECT * FROM dim_play_detail_2;
-- Examples: 2-on-1, 3-on-2, Rebound, Cross-ice, One-timer
```

#### Shot Types (`dim_shot_type`)
| shot_type_id | shot_type |
|--------------|-----------|
| ST001 | Wrist |
| ST002 | Slap |
| ST003 | Snap |
| ST004 | Backhand |
| ST005 | Deflection |
| ST006 | Wrap-around |

#### Pass Types (`dim_pass_type`)
| pass_type_id | pass_type |
|--------------|-----------|
| PT001 | Direct |
| PT002 | Saucer |
| PT003 | Bank |
| PT004 | Cross-ice |
| PT005 | Drop |
| PT006 | Behind-back |

#### Zones (`dim_zone`)
| zone_id | zone_name |
|---------|-----------|
| OZ | Offensive Zone |
| NZ | Neutral Zone |
| DZ | Defensive Zone |

#### Success Outcomes (`dim_success`)
| success_id | success_value |
|------------|---------------|
| s | Successful |
| u | Unsuccessful |

#### Player Roles (`dim_player_role`)
| role_id | role_name | role_abrev |
|---------|-----------|------------|
| R001 | Shooter | SH |
| R002 | Passer | PA |
| R003 | Receiver | RC |
| R004 | Blocker | BL |
| R005 | Hitter | HT |
| R006 | Target | TG |

#### Periods (`dim_period`)
| period_id | period_name | period_number |
|-----------|-------------|---------------|
| P1 | 1st Period | 1 |
| P2 | 2nd Period | 2 |
| P3 | 3rd Period | 3 |
| OT | Overtime | 4 |
| SO | Shootout | 5 |

#### Situations (`dim_situation`)
| situation_id | situation |
|--------------|-----------|
| EV | Even Strength |
| PP | Power Play |
| PK | Penalty Kill |
| EN | Empty Net |
| 4v4 | 4-on-4 |
| 3v3 | 3-on-3 |

#### Strength (`dim_strength`)
| strength_id | strength |
|-------------|----------|
| 5v5 | 5-on-5 |
| 5v4 | 5-on-4 |
| 4v5 | 4-on-5 |
| 5v3 | 5-on-3 |
| 3v5 | 3-on-5 |
| 4v4 | 4-on-4 |
| 3v3 | 3-on-3 |
| 6v5 | 6-on-5 |
| 6v4 | 6-on-4 |

---

## Event Structure

### fact_events Columns

```javascript
const eventRecord = {
  // Keys
  event_key: "EV1896900001",           // PRIMARY KEY
  game_id: "18969",
  shift_key: "18969_1",                // Links to fact_shifts
  
  // Timing
  period: 1,
  event_index: 1,
  event_start_min: 19,
  event_start_sec: 45,
  event_end_min: 19,
  event_end_sec: 43,
  time_start_total_seconds: 15,        // Seconds into period
  time_end_total_seconds: 17,
  
  // Video timing (CRITICAL for dashboard)
  running_video_time: 125.5,           // Seconds from video start
  event_running_start: 125.5,
  event_running_end: 127.5,
  
  // Event classification
  event_type: "Shot",
  event_detail: "Wrist Shot",
  event_detail_2: null,
  event_successful: "s",               // 's' or 'u'
  Type: "Shot",                        // Legacy field
  
  // Play context
  play_detail1: "Rush",
  play_detail_2: "2-on-1",
  play_detail_successful: "s",
  
  // Zone info
  event_team_zone: "OZ",
  home_team_zone: "DZ",
  away_team_zone: "OZ",
  
  // Team context
  team_venue: "Away",
  team_venue_abv: "A",
  home_team: "Storm",
  away_team: "Lightning",
  home_team_id: "T001",
  away_team_id: "T002",
  
  // Linking
  linked_event_index: null,            // For shot→save→rebound chains
  sequence_index: 1,                   // Possession sequence
  play_index: 1,                       // Play within sequence
  
  // IDs for joins
  period_id: "P1",
  venue_id: "H",
  event_type_id: "EVT001",
  event_detail_id: "ED001",
  success_id: "s",
  zone_id: "OZ",
  play_detail_id: "PD001",
  
  // Special
  empty_net_goal: 0
};
```

### fact_events_player Columns

Each event can have multiple players involved:

```javascript
const eventPlayerRecord = {
  // Keys
  event_player_key: "EV1896900001_1",  // PRIMARY KEY
  event_key: "EV1896900001",           // FK to fact_events
  game_id: "18969",
  
  // Player info
  player_id: "P001",
  player_name: "John Smith",
  player_number: 17,
  role_abrev: "SH",                    // Shooter
  
  // Same timing as parent event
  period: 1,
  event_index: 1,
  // ... all timing fields ...
  
  // Same event info
  event_type: "Shot",
  Type: "Shot",
  // ... all event classification fields ...
  
  // Team context for this player
  player_team_id: "T002",
  shift_key: "18969_1"
};
```

---

## Linked Events Logic

### CRITICAL: How Events Chain Together

Events are linked via `linked_event_index`. The pattern:

```
Event 1 (Shot) → Event 2 (Save) → Event 3 (Rebound) → Event 4 (Shot)...
```

### Shot → Save → Rebound Chain

```javascript
// EVENT 1: SHOT
{
  event_key: "EV1896900001",
  event_index: 1,
  event_type: "Shot",
  linked_event_index: null,  // First in chain
  
  // Players:
  // event_player_1: Shooter (team A)
  // opp_player_1: Goalie (team B)
  // event_player_2-6: Other attackers
  // opp_player_2-6: Other defenders
}

// EVENT 2: SAVE (linked to shot)
{
  event_key: "EV1896900002",
  event_index: 2,
  event_type: "Save",
  linked_event_index: 1,     // Links back to shot
  
  // Players SWAP:
  // event_player_1: Goalie (was opp_player_1)
  // opp_player_1: Shooter (was event_player_1)
  // Other players swap sides too
}

// EVENT 3: REBOUND (only goalie involved)
{
  event_key: "EV1896900003",
  event_index: 3,
  event_type: "Rebound",
  linked_event_index: 2,     // Links to save
  
  // Players:
  // event_player_1: Goalie ONLY
  // No other players
}
```

### Player Role Rules by Event Type

| Event Type | event_player_1 | opp_player_1 | Notes |
|------------|----------------|--------------|-------|
| **Shot** | Shooter | Goalie | Other players optional |
| **Save** | Goalie | Shooter | Roles swap from shot |
| **Rebound** | Goalie | - | Goalie only |
| **Goal** | Scorer | Goalie | Assists are player_2, player_3 |
| **Pass** | Passer | - | Receiver is event_player_2 |
| **Hit** | Hitter | Target | - |
| **Block** | Blocker | Shooter | - |
| **Faceoff** | Winner | Loser | - |
| **Turnover** | Player losing puck | - | - |
| **Takeaway** | Player gaining puck | Lost by | - |
| **Stoppage** | Last event_player_1 | - | Inherit from previous |

### Same Players, Different Events

Within a linked chain, typically:
- Same players maintain same roles
- Same `play_detail` and `play_detail_2`
- Only changes: `event_type`, `event_detail`, `event_detail_2`, `success`

---

## Shift Structure

### fact_shifts Columns

```javascript
const shiftRecord = {
  // Keys
  shift_key: "18969_1",                // PRIMARY KEY
  game_id: "18969",
  shift_index: 1,
  
  // Timing
  Period: 1,                           // Note: uppercase P
  shift_start_min: 20,
  shift_start_sec: 0,
  shift_end_min: 19,
  shift_end_sec: 15,
  shift_duration: 45,                  // Seconds
  shift_start_total_seconds: 0,
  shift_end_total_seconds: 45,
  
  // Video timing
  running_video_time: 60.0,
  shift_start_running_time: 60.0,
  shift_end_running_time: 105.0,
  
  // Start/Stop types
  shift_start_type: "Faceoff",
  shift_stop_type: "Whistle",
  shift_start_type_id: "SS001",
  shift_stop_type_id: "ST001",
  
  // Players on ice (by position)
  home_forward_1: 17,                  // Jersey numbers
  home_forward_2: 23,
  home_forward_3: 9,
  home_defense_1: 4,
  home_defense_2: 77,
  home_goalie: 35,
  home_xtra: null,                     // Extra attacker if pulled goalie
  
  away_forward_1: 11,
  away_forward_2: 19,
  away_forward_3: 88,
  away_defense_1: 2,
  away_defense_2: 6,
  away_goalie: 30,
  away_xtra: null,
  
  // Strength/Situation
  home_team_strength: 5,
  away_team_strength: 5,
  strength: "5v5",
  situation: "EV",
  strength_id: "5v5",
  situation_id: "EV",
  
  // Team info
  home_team: "Storm",
  away_team: "Lightning",
  home_team_id: "T001",
  away_team_id: "T002",
  
  // Zone time (accumulated during shift)
  home_ozone_start: 0,
  home_ozone_end: 20,
  home_dzone_start: 0,
  home_dzone_end: 15,
  home_nzone_start: 0,
  home_nzone_end: 10,
  
  // Goals during shift
  home_goals: 0,
  away_goals: 0,
  
  // Plus/Minus during shift
  home_team_plus: 0,
  home_team_minus: 0,
  away_team_plus: 0,
  away_team_minus: 0,
  
  // Special teams
  home_team_en: 0,                     // Empty net
  away_team_en: 0,
  home_team_pk: 0,                     // Penalty kill
  home_team_pp: 0,                     // Power play
  away_team_pp: 0,
  away_team_pk: 0,
  
  // Period reference
  period_id: "P1",
  period_start_total_running_seconds: 0
};
```

---

## Video Integration

### CRITICAL: Video Time Sync

Every event and shift has video timing columns:

```javascript
// Event video timing
running_video_time: 125.5,    // Seconds from video start
event_running_start: 125.5,   // When event starts
event_running_end: 127.5,     // When event ends

// Shift video timing
running_video_time: 60.0,
shift_start_running_time: 60.0,
shift_end_running_time: 105.0,
```

### Building Video URLs

Get video URL from `dim_schedule`:

```javascript
// From dim_schedule
const gameVideo = {
  video_id: "abc123xyz",
  video_url: "https://youtube.com/watch?v=abc123xyz",
  video_start_time: 0  // Offset if video doesn't start at puck drop
};

// Build timestamped URL
function getVideoUrl(baseUrl, seconds) {
  // YouTube format
  return `${baseUrl}&t=${Math.floor(seconds)}s`;
  // Example: https://youtube.com/watch?v=abc123xyz&t=125s
}

// For an event
const eventVideoUrl = getVideoUrl(gameVideo.video_url, event.running_video_time);
```

### Multiple Camera Angles

Check `fact_video` for additional angles:

```sql
SELECT * FROM fact_video WHERE game_id = '18969';
```

May have: Main, Goal Cam, Blue Line, etc.

---

## Supabase Integration

### Reading Data

```javascript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'https://uuaowslhpgyiudmbvqze.supabase.co',
  'YOUR_ANON_KEY'  // Use anon key for reads
);

// Load dimension tables on startup
async function loadDimensions() {
  const { data: eventTypes } = await supabase
    .from('dim_event_type')
    .select('*');
    
  const { data: players } = await supabase
    .from('dim_player')
    .select('player_id, player_full_name, player_primary_position');
    
  const { data: teams } = await supabase
    .from('dim_team')
    .select('team_id, team_name');
    
  // ... load all needed dims
  return { eventTypes, players, teams };
}

// Load game data
async function loadGame(gameId) {
  const { data: events } = await supabase
    .from('fact_events')
    .select('*')
    .eq('game_id', gameId)
    .order('event_index');
    
  const { data: shifts } = await supabase
    .from('fact_shifts')
    .select('*')
    .eq('game_id', gameId)
    .order('shift_index');
    
  return { events, shifts };
}
```

### Writing Data

```javascript
// Use SERVICE_ROLE key for writes (keep secret!)
const supabaseAdmin = createClient(
  'https://uuaowslhpgyiudmbvqze.supabase.co',
  'SERVICE_ROLE_KEY'
);

// Save draft to staging
async function saveDraft(events, shifts, gameId) {
  // Clear existing staging for this game
  await supabaseAdmin
    .from('staging_events')
    .delete()
    .eq('game_id', gameId);
    
  // Insert new staging data
  const { error } = await supabaseAdmin
    .from('staging_events')
    .insert(events);
    
  if (error) throw error;
  
  // Same for shifts
  await supabaseAdmin
    .from('staging_shifts')
    .delete()
    .eq('game_id', gameId);
    
  await supabaseAdmin
    .from('staging_shifts')
    .insert(shifts);
}

// Publish final (move from staging to production)
async function publishGame(gameId) {
  // Get from staging
  const { data: events } = await supabaseAdmin
    .from('staging_events')
    .select('*')
    .eq('game_id', gameId);
    
  // Delete existing in production
  await supabaseAdmin
    .from('fact_events')
    .delete()
    .eq('game_id', gameId);
    
  // Insert to production
  await supabaseAdmin
    .from('fact_events')
    .upsert(events);
    
  // Clear staging
  await supabaseAdmin
    .from('staging_events')
    .delete()
    .eq('game_id', gameId);
}
```

---

## Workflow States

### Game Tracking Workflow

```
1. NEW GAME
   - Create game_id
   - Set up roster from dim_player
   - Initialize empty events/shifts
   
2. TRACKING (Draft)
   - Add events as they happen
   - Auto-create shifts on changes
   - Save to staging_* tables
   - Can edit, delete, reorder
   
3. REVIEW
   - Validate all events
   - Check linked events
   - Verify timing
   - Compare to video
   
4. PUBLISH
   - Move staging → production
   - Lock for editing
   - Generate stats
```

### Save Modes

```javascript
const SAVE_MODES = {
  DRAFT: 'draft',      // Save to staging, can edit
  PARTIAL: 'partial',  // Save incomplete game
  FINAL: 'final'       // Publish to production
};

async function saveGame(gameId, events, shifts, mode) {
  switch(mode) {
    case SAVE_MODES.DRAFT:
      await saveDraft(events, shifts, gameId);
      break;
    case SAVE_MODES.PARTIAL:
      await saveDraft(events, shifts, gameId);
      // Mark as partial in game status
      await updateGameStatus(gameId, 'partial');
      break;
    case SAVE_MODES.FINAL:
      await validateGame(events, shifts);
      await publishGame(gameId);
      await updateGameStatus(gameId, 'complete');
      break;
  }
}
```

---

## Data Validation

### Before Publishing

```javascript
function validateGame(events, shifts) {
  const errors = [];
  
  // 1. Check all events have required fields
  events.forEach(e => {
    if (!e.event_type) errors.push(`Event ${e.event_index}: missing event_type`);
    if (!e.period) errors.push(`Event ${e.event_index}: missing period`);
    if (!e.shift_key) errors.push(`Event ${e.event_index}: not assigned to shift`);
  });
  
  // 2. Check event timing is within shift
  events.forEach(e => {
    const shift = shifts.find(s => s.shift_key === e.shift_key);
    if (shift) {
      if (e.time_start_total_seconds < shift.shift_start_total_seconds ||
          e.time_end_total_seconds > shift.shift_end_total_seconds) {
        errors.push(`Event ${e.event_index}: timing outside shift`);
      }
    }
  });
  
  // 3. Check linked events are valid
  events.forEach(e => {
    if (e.linked_event_index) {
      const linked = events.find(ev => ev.event_index === e.linked_event_index);
      if (!linked) {
        errors.push(`Event ${e.event_index}: invalid linked_event_index`);
      }
    }
  });
  
  // 4. Check goals have at least scorer
  events.filter(e => e.event_type === 'Goal').forEach(e => {
    // Should have event_player entries
  });
  
  return errors;
}
```

---

## UI Recommendations

### Event Entry Form

```
┌─────────────────────────────────────────────────────────────┐
│ EVENT ENTRY                                    [Period: 1]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Time: [19]:[45] - [19]:[43]     Video: [▶ 2:05]           │
│                                                             │
│  Type: [Shot ▼]  Detail: [Wrist ▼]  Success: [✓]           │
│                                                             │
│  Play: [Rush ▼]  Detail: [2-on-1 ▼]                        │
│                                                             │
│  Zone: [OZ ▼]   Team: [Away ▼]                             │
│                                                             │
│  ─── PLAYERS ───────────────────────────────────────────── │
│                                                             │
│  Event Player 1: [#17 Smith ▼] (Shooter)                   │
│  Event Player 2: [#23 Jones ▼] (Passer)                    │
│  Opp Player 1:   [#35 Johnson ▼] (Goalie)                  │
│                                                             │
│  [Link to Previous] [Save] [Next Event →]                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| S | Shot |
| P | Pass |
| G | Goal |
| F | Faceoff |
| H | Hit |
| Space | Success toggle |
| Enter | Save & Next |
| ← → | Navigate events |
| Ctrl+S | Save draft |
| Ctrl+Z | Undo |

---

## Testing Your Implementation

### Test Data

Use game 18969 as reference:
- 5,833 events
- 672 shifts
- 4 periods
- Final score: Available in dim_schedule

### Validation Queries

```sql
-- Check event counts by type
SELECT event_type, COUNT(*) 
FROM fact_events 
WHERE game_id = '18969'
GROUP BY event_type;

-- Check linked events
SELECT e1.event_index, e1.event_type, e2.event_index as linked_to, e2.event_type as linked_type
FROM fact_events e1
LEFT JOIN fact_events e2 ON e1.linked_event_index = e2.event_index AND e1.game_id = e2.game_id
WHERE e1.game_id = '18969' AND e1.linked_event_index IS NOT NULL
LIMIT 20;

-- Check events per shift
SELECT shift_key, COUNT(*) as events
FROM fact_events
WHERE game_id = '18969'
GROUP BY shift_key
ORDER BY COUNT(*) DESC;
```

---

## Common Pitfalls

1. **Forgetting to link events** - Shot-Save-Rebound must be linked
2. **Wrong player roles** - Goalie/Shooter swap on Save
3. **Video time drift** - Sync video to game clock regularly
4. **Missing shift assignment** - Every event needs a shift_key
5. **Duplicate keys** - Ensure unique event_key generation
6. **Time zone issues** - Store all times in game time (period:min:sec)

---

## Resources

- Prototype Tracker: `dashboard/tracker_v4_final_WORKING.html`
- Schema: `sql/05_FINAL_COMPLETE_SCHEMA.sql`
- Sample Data: `data/output/fact_events.csv`
- Dimension Tables: `data/output/dim_*.csv`

---

## Questions?

See `prompts/tracker_dev_prompt.md` for a prompt to start a new Claude chat with full context.
