# BenchSight Tracker Developer - Next Prompt

Copy and paste this prompt to start or continue tracker development.

---

## PROMPT START

I'm building the game tracker for BenchSight, a hockey analytics platform. The tracker records game events that flow to **Supabase PostgreSQL**.

### Current State
- **Working:** Basic event entry, save to Excel
- **Broken:** Roster loading, game dropdown, event ordering
- **Missing:** Edit/delete, XY coordinates, predictions

### Supabase Connection
```
URL: https://uuaowslhpgyiudmbvqze.supabase.co
API: https://uuaowslhpgyiudmbvqze.supabase.co/rest/v1/
Tables: fact_events, fact_shifts, dim_player, dim_schedule
```

### Event Data Structure
```javascript
{
  event_key: 'E1896900001',      // PK: E{game_id}{5-digit index}
  game_id: 18969,                // FK to dim_schedule
  event_index: 1,                // Unique within game
  period: 1,
  event_start_seconds: 1080,     // Countdown from period start
  event_type: 'Shot',            // Primary classification
  event_detail: 'Shot_OnNetSaved', // Secondary
  event_detail_2: 'Shot-Wrist',  // Tertiary
  event_successful: 's',         // 's' or 'u'
  event_team_player_1: 53,       // PRIMARY ACTOR (gets stat)
  opp_team_player_1: 70,         // Opponent (for faceoffs)
  linked_event_index: null,      // For assists → goal
  // ... more columns
}
```

### Critical Rules
1. **event_team_player_1** = gets stat credit (shooter, passer, etc.)
2. **Shots = Corsi** = all shot attempts (60-70 per team normal)
3. **Assists** recorded in `play_detail1` as 'AssistPrimary'/'AssistSecondary'
4. Events must have unique `event_index` per game

### What I Need Help With Today
[DESCRIBE YOUR SPECIFIC TASK]

**Examples:**
- "Fix the roster loading - BLB table parsing is broken"
- "Implement event prediction based on current event type"
- "Add XY coordinate capture with clickable rink diagram"
- "Create edit/delete functionality for existing events"

---

## PROMPT END

---

## Alternative Prompts

### For Roster Loading Fix
```
The BenchSight tracker's roster loading is broken.

Current behavior:
- loadRosterFromBLB() function fails silently
- No players appear in player dropdowns
- Works sometimes, fails other times

Expected behavior:
- Load roster from BLB table OR dim_player in Supabase
- Populate home_team and away_team player lists
- Show jersey number + name in dropdowns

Current code snippet:
[PASTE RELEVANT CODE]

Error in console:
[PASTE ERROR]

Help me debug and fix this. Should also add fallback to Supabase query.
```

### For Event Predictions
```
I need to implement smart event suggestions in the BenchSight tracker.

After user enters an event, suggest the next likely event based on these patterns:

| Current Event | Suggest | Confidence |
|--------------|---------|------------|
| Stoppage | DeadIce | 100% |
| DeadIce | Faceoff | 100% |
| Shot | Save | 70% |
| Save_Freeze | Stoppage | 95% |
| Rebound | Possession (50%), Shot (35%) | |
| Zone_Entry (success) | Possession | 60% |
| Zone_Entry (fail) | Turnover | 80% |
| Pass (success) | Possession (40%), Zone_Entry (30%) | |
| Pass (fail) | Turnover | 70% |

UI requirements:
- Show top 2-3 suggestions as buttons
- Keyboard shortcuts (1, 2, 3 to select)
- Still allow manual selection

Help me implement this prediction system.
```

### For XY Coordinate Capture
```
I need to add XY coordinate capture to the BenchSight tracker.

Requirements:
- Clickable rink diagram (200ft x 85ft)
- Click captures (x, y) for puck position
- Store in event record as puck_x, puck_y
- Calculate derived values: shot_distance, shot_angle, zone

Coordinate system:
- Origin (0, 0) at bottom-left of rink
- X: 0-200 (length)
- Y: 0-85 (width)
- Goal lines at x=11 and x=189
- Blue lines at x=75 and x=125

UI needs:
- Rink SVG or Canvas
- Click handler with position calculation
- Visual marker showing clicked position
- Ability to adjust/re-click

Help me build this feature.
```

### For Edit/Delete Events
```
BenchSight tracker needs edit and delete functionality.

Current state:
- Can add events
- Cannot modify after save
- Cannot delete mistakes

Needed features:
1. Edit button on each event row
2. Opens event in edit mode (same form)
3. Save updates existing record
4. Delete button with confirmation
5. Bulk delete (select multiple)
6. Undo last action (nice to have)

Supabase operations needed:
```javascript
// Update
await supabase.from('fact_events')
  .update({ event_type: 'Shot', ... })
  .eq('event_key', 'E1896900001')

// Delete
await supabase.from('fact_events')
  .delete()
  .eq('event_key', 'E1896900001')
```

Help me implement this with proper UI and confirmation dialogs.
```

### For Game Dropdown Fix
```
The game selector dropdown in BenchSight tracker is missing games.

Current behavior:
- Only shows some games
- Recently tracked games don't appear
- No error messages

Expected behavior:
- Show all games from dim_schedule
- Or all game folders in /data/raw/games/
- Sort by date descending
- Show: "Game ID - Date - Home vs Away"

Current query:
[PASTE CODE]

Help me fix this to show all available games.
```

### For Offline Mode
```
BenchSight tracker needs offline capability.

Use case: Tracking games at rinks without internet

Requirements:
1. Save events to localStorage when offline
2. Detect connection status
3. Queue events for sync
4. Sync to Supabase when online
5. Handle conflicts (server has newer data)
6. Show sync status indicator

Help me implement offline-first architecture.
```

---

## Quick Reference

### Event Types
```
Primary: Faceoff, Shot, Pass, Goal, Turnover, Zone_Entry_Exit,
         Penalty, Save, Rebound, Possession, Stoppage, DeadIce

Shot Details: Shot_OnNetSaved, Shot_Missed, Shot_Blocked, Shot_Goal
Pass Details: Pass_Completed, Pass_Missed, Pass_Intercepted
Save Details: Save_Rebound, Save_Freeze
```

### Player Roles
```
event_team_player_1 = PRIMARY (gets stat credit)
opp_team_player_1   = OPPONENT (for faceoffs)
event_team_player_2-6 = On ice but not primary actor
```

### Key Calculations
```javascript
// Event key format
const eventKey = `E${gameId}${String(eventIndex).padStart(5, '0')}`

// Time to seconds (from 18:30 format)
const toSeconds = (min, sec) => min * 60 + sec

// Period offset
const periodStartSeconds = (period - 1) * 1200 // 20 min periods
```

### Supabase Patterns
```javascript
// Insert event
await supabase.from('fact_events').insert(event)

// Get events for game
await supabase.from('fact_events')
  .select('*')
  .eq('game_id', gameId)
  .order('event_index')

// Get roster
await supabase.from('dim_player')
  .select('*')
  .in('team_id', [homeTeamId, awayTeamId])
```

---

*Last Updated: December 2024*
