# BenchSight Tracker Developer Handoff

## 🎯 Your Mission

Build and maintain the game tracking interface for BenchSight. The tracker is an HTML/JavaScript application that records hockey game events in real-time, saving data that flows through the ETL pipeline into Supabase.

---

## 📖 Required Reading (In Order)

### 1. Start Here (This README)
You're reading it. Critical status and issues below.

### 2. Tracker Developer Guide (`docs/TRACKER_DEV_COMPLETE_GUIDE.md`)
**CRITICAL** - 26KB comprehensive guide covering:
- All event types and validation lists
- Event detail hierarchies (shots, saves, passes, turnovers, zones)
- **Event linking patterns for predictive suggestions**
- XY coordinate requirements
- Player role logic (who gets stat credit)
- Data validation rules

### 3. Schema & ERD (`docs/SCHEMA_AND_ERD.md`)
Understand where tracker data goes:
- fact_events structure
- fact_shifts structure
- Primary key formats

### 4. Data Dictionaries
- `dd_fact_events.csv` - Event table structure
- `dd_fact_shifts.csv` - Shift table structure

### 5. Master Instructions (`docs/MASTER_INSTRUCTIONS.md`)
Business rules, especially:
- player_role determines stat credit
- event_team_player_1 = primary actor
- Shots = Corsi (all attempts)

---

## 🔌 Supabase Integration

### Connection Details
```
Project URL: https://uuaowslhpgyiudmbvqze.supabase.co
API URL: https://uuaowslhpgyiudmbvqze.supabase.co/rest/v1/
```

### Writing Events to Supabase
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

// Insert event
async function saveEvent(event) {
  const { data, error } = await supabase
    .from('fact_events')
    .insert({
      event_key: `E${event.game_id}${String(event.event_index).padStart(5, '0')}`,
      game_id: event.game_id,
      event_index: event.event_index,
      period: event.period,
      event_type: event.event_type,
      event_detail: event.event_detail,
      event_detail_2: event.event_detail_2,
      event_successful: event.event_successful,
      event_start_seconds: event.event_start_seconds,
      // ... other columns
    })
  
  if (error) throw error
  return data
}
```

### Reading Existing Data
```javascript
// Get games for dropdown
const { data: games } = await supabase
  .from('dim_schedule')
  .select('game_id, game_date, home_team, away_team')
  .order('game_date', { ascending: false })

// Get roster for game
const { data: roster } = await supabase
  .from('dim_player')
  .select('player_id, player_name, jersey_number')
  .in('team_id', [homeTeamId, awayTeamId])

// Get existing events for game
const { data: events } = await supabase
  .from('fact_events')
  .select('*')
  .eq('game_id', gameId)
  .order('event_index', { ascending: true })
```

---

## ⚠️ CRITICAL: Current Issues to Fix

### P0 - Must Fix Immediately

#### 1. Roster Loading Fails
**Symptom:** BLB table parsing fails, no players appear
**Root Cause:** Table format changed or parsing logic broken
**Fix Needed:**
- Debug `loadRosterFromBLB()` function
- Add fallback to JSON roster file
- Validate roster against dim_player

#### 2. Games Missing from Dropdown
**Symptom:** Some tracked games don't appear in game selector
**Root Cause:** Game list query not finding all game folders
**Fix Needed:**
- Query `/data/raw/games/` directory
- Or query dim_schedule from Supabase
- Show all games regardless of tracking status

#### 3. Event Ordering Bugs
**Symptom:** Events save in wrong order or overwrite each other
**Root Cause:** event_index collision or sort issues
**Fix Needed:**
- Ensure unique event_index per game
- Sort by event_start_seconds, then event_index
- Lock event_index once assigned

### P1 - Important

#### 4. Edit Functionality Missing
**Current State:** Can't edit or delete existing events
**Need:**
- Edit button per event row
- Delete with confirmation
- Bulk operations (delete range)
- Undo support

#### 5. Shift Auto-Creation
**Current State:** Shifts created manually
**Need:**
- Auto-create shift on period start
- Auto-end shift on stoppage
- Allow manual override

### P2 - Should Have

#### 6. XY Coordinate Capture
**Current State:** No position tracking
**Need:**
- Clickable rink diagram
- Capture puck (x, y) per event
- Optional: player positions
- Save to event record

#### 7. Prediction/Suggestions
**Current State:** Manual event type selection
**Need:**
- Suggest next event based on current (see linking patterns)
- Example: After Shot, suggest Save (70%) or Goal (10%)
- Keyboard shortcuts for common patterns

---

## 📋 Event Type Quick Reference

### Primary Events (event_type)
```
Faceoff, Shot, Pass, Goal, Turnover, Zone_Entry_Exit
Penalty, Save, Rebound, Possession, Stoppage, DeadIce
Hit, LoosePuck, Play, GameStart, GameEnd
```

### Event Details (event_detail)
```
SHOTS: Shot_OnNetSaved, Shot_Missed, Shot_Blocked, Shot_Goal
PASSES: Pass_Completed, Pass_Missed, Pass_Intercepted
SAVES: Save_Rebound, Save_Freeze
TURNOVERS: Giveaway-*, Takeaway-*
ZONES: Zone_Entry, Zone_Exit, Zone_Keepin
```

### Success Indicator
```
's' = Successful (pass completed, shot on goal, entry made)
'u' = Unsuccessful (pass missed, shot blocked, entry failed)
```

---

## 🔄 Event Linking Predictions

Use these patterns for smart suggestions:

| After This | Suggest This | Confidence |
|------------|--------------|------------|
| Stoppage | DeadIce | 100% |
| DeadIce | Faceoff | 100% |
| Goal | Stoppage | 100% |
| Shot | Save | 70% |
| Save_Freeze | Stoppage | 95% |
| Save_Rebound | Rebound | 90% |
| Rebound | Possession | 50% |
| Rebound | Shot | 35% |
| Pass (success) | Possession | 40% |
| Pass (fail) | Turnover | 70% |
| Zone_Entry (success) | Possession | 60% |
| Zone_Entry (fail) | Turnover | 80% |
| Turnover | Possession | 55% |
| Faceoff | Possession | 50% |
| Possession | Pass | 50% |
| Possession | Shot | 15% |

---

## 🎮 Player Role Logic

**CRITICAL:** This determines who gets stat credit!

```javascript
// event_team_player_1 = PRIMARY ACTOR (gets the stat)
// opp_team_player_1 = OPPONENT ACTOR (for faceoffs, etc.)
// event_team_player_2-6 = SUPPORTING (on ice but not actor)

// Example: Recording a shot
{
  event_type: 'Shot',
  event_team_player_1: 53,  // ← SHOOTER (gets shots stat)
  event_team_player_2: 20,  // on ice
  event_team_player_3: 12,  // on ice
  // ...
}

// Example: Recording a faceoff
{
  event_type: 'Faceoff',
  event_team_player_1: 53,  // ← WINNER (gets fo_wins)
  opp_team_player_1: 70,    // ← LOSER (gets fo_losses)
}

// Example: Goal with assist
// Record as separate events with linked_event_index
{
  event_type: 'Pass',
  event_team_player_1: 12,  // ← ASSISTER
  play_detail1: 'AssistPrimary',
  linked_event_index: 1005  // points to goal event
}
```

---

## 📁 File Structure

### Tracker Files
```
tracker/
├── tracker_v19.html     # Current version (USE THIS)
├── tracker_v18.html     # Previous version
├── tracker_v17.html     # Older
└── tracker_v16.html     # Oldest
```

### Data Files
```
data/raw/games/{game_id}/
├── {game_id}_tracking.xlsx   # Main tracking file
├── roster.json               # Backup roster
├── !info.rtf                 # Game notes
└── xy/                       # XY data (future)
```

### Output Files (Created by ETL)
```
data/output/
├── fact_events.csv
├── fact_events_player.csv
├── fact_shifts.csv
└── fact_shifts_player.csv
```

---

## 🔧 Development Setup

### Local Testing
1. Open tracker HTML directly in browser
2. Use browser dev tools for debugging
3. Save events to local storage initially
4. Test Supabase integration separately

### Supabase Testing
```javascript
// Test write
const testEvent = {
  event_key: 'E9999900001',
  game_id: 99999,
  event_index: 1,
  event_type: 'Test',
  // ...
}
const { error } = await supabase.from('fact_events').insert(testEvent)
console.log(error ? 'FAIL: ' + error.message : 'SUCCESS')

// Clean up
await supabase.from('fact_events').delete().eq('game_id', 99999)
```

### ETL Integration
After tracking a game:
```bash
# Run ETL to process tracking file
python etl.py

# Fix any data issues
python scripts/fix_data_integrity.py

# Validate
python scripts/etl_validation.py

# Run tests
pytest tests/
```

---

## 📁 Files in This Handoff

```
tracker_dev/
├── README.md                         # This file
├── NEXT_PROMPT.md                    # Prompt for continuing
├── docs/
│   ├── TRACKER_DEV_COMPLETE_GUIDE.md # Full event guide
│   ├── SCHEMA_AND_ERD.md             # Database schema
│   └── MASTER_INSTRUCTIONS.md        # Business rules
├── data_dictionary/
│   ├── dd_fact_events.csv            # Event columns
│   └── dd_fact_shifts.csv            # Shift columns
├── tracker/
│   └── tracker_v19.html              # Current tracker
└── examples/
    └── sample_tracking.xlsx          # Example tracking file
```

---

## ✅ Success Criteria

### Phase 1: Stability
- [ ] Roster loads 100% of time
- [ ] All games appear in dropdown
- [ ] Events save in correct order
- [ ] No data loss on crashes
- [ ] Edit/delete works

### Phase 2: Enhancements
- [ ] Event predictions implemented
- [ ] Keyboard shortcuts work
- [ ] Shift auto-creation
- [ ] Offline mode with sync

### Phase 3: XY Data
- [ ] Rink diagram clickable
- [ ] Puck position captured
- [ ] XY data saves to events
- [ ] Validated coordinate system

---

## 🆘 Getting Help

- **Event types:** See `TRACKER_DEV_COMPLETE_GUIDE.md`
- **Data issues:** Re-run ETL pipeline
- **Supabase connection:** Contact Supabase dev
- **Business rules:** See `MASTER_INSTRUCTIONS.md`

---

*Last Updated: December 2024*
