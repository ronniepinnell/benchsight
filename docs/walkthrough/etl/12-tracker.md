# 12 - Tracker: Game Event Tracking

**Learning Objectives:**
- Understand what the tracker does
- Know the data export format
- Understand the XY coordinate system

---

## What the Tracker Does

The **tracker** is a game event tracking application used to:
- Record every event during a game (shots, goals, passes, faceoffs)
- Track player shifts (who's on the ice)
- Capture XY coordinates on a rink visualization
- Sync events to video timestamps
- Export data for ETL processing

📍 **Location:** `ui/tracker/`

---

## Current Architecture

⚠️ **Technical Debt:** The tracker is currently a single HTML file (~16,000 lines) with global state.

```
ui/tracker/
├── index.html          # Main application (16,000+ lines)
├── src/                # Partial TypeScript rewrite
│   ├── components/
│   └── lib/
└── assets/             # Images, icons
```

### Why It's One Big File

- Original rapid prototype
- Direct manipulation of rink canvas
- Complex state interactions
- Works but hard to maintain

### Planned Rewrite

Future architecture (Rust + Next.js):
- Rust for performance-critical event processing
- Next.js for UI components
- Proper state management
- Modular design

---

## Key Features

### 1. Rink Canvas

A visual representation of the hockey rink where events are recorded:
- Click to record event location
- Drag for movement paths
- Color-coded zones (offensive, neutral, defensive)

### 2. Event Recording

Events are recorded with:
- Event type (Goal, Shot, Pass, Faceoff, etc.)
- Event detail (Shot_OnNet, Goal_Scored, Pass_Completed, etc.)
- Player(s) involved (by jersey number)
- Time (period, minutes, seconds)
- XY coordinates
- Additional details (shot type, zone entry type, etc.)

### 3. Shift Tracking

Player shifts are tracked:
- Who's on the ice at any time
- Shift start/end times
- Line combinations
- Position slots (F1, F2, F3, D1, D2, G)

### 4. Video Sync

Events can be synced to video:
- Link to video file
- Timestamp for each event
- Playback verification

---

## Export Format

The tracker exports to Excel files that ETL processes.

### File Location

```
data/raw/games/{game_id}/{game_id}_tracking.xlsx
```

### Events Sheet

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| event_type | VARCHAR | Goal | Major event category |
| event_detail | VARCHAR | Goal_Scored | Specific event type |
| event_detail_2 | VARCHAR | WristShot | Additional detail |
| team | VARCHAR | Blue | Team name |
| jersey_1 | INT | 12 | Primary player jersey |
| jersey_2 | INT | 7 | Secondary player jersey |
| jersey_3 | INT | 22 | Tertiary player jersey |
| period | INT | 2 | Period number |
| time_min | INT | 8 | Minutes into period |
| time_sec | INT | 45 | Seconds |
| x | INT | 172 | X coordinate (0-200) |
| y | INT | 42 | Y coordinate (0-85) |
| zone | VARCHAR | O | Zone (O/N/D) |
| play_detail | VARCHAR | AssistPrimary | Context detail |
| zone_entry_type | VARCHAR | Carry | Entry type |
| zone_exit_type | VARCHAR | Pass | Exit type |
| video_time | VARCHAR | 12:45 | Video timestamp |

### Shifts Sheet

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| period | INT | 2 | Period number |
| shift_number | INT | 1 | Shift sequence |
| team | VARCHAR | Blue | Team name |
| start_time | INT | 1180 | Start (descending) |
| end_time | INT | 1120 | End |
| f1 | INT | 12 | Forward 1 jersey |
| f2 | INT | 7 | Forward 2 jersey |
| f3 | INT | 22 | Forward 3 jersey |
| d1 | INT | 4 | Defense 1 jersey |
| d2 | INT | 6 | Defense 2 jersey |
| g | INT | 30 | Goalie jersey |

---

## XY Coordinate System

### Rink Dimensions

```
       ┌─────────────────────────────────────────────────────────┐
       │                    RINK (200ft x 85ft)                  │
  0,85 │                                                         │ 200,85
       │    HOME GOAL                           AWAY GOAL        │
       │    x=11, y=42.5                        x=189, y=42.5    │
       │        │                                   │            │
       │        ▼                                   ▼            │
       │       [G]                                 [G]           │
       │                                                         │
       │  ◄──── Defensive ────►◄── Neutral ──►◄── Offensive ───►│
       │       (x: 0-75)        (x: 75-125)      (x: 125-200)   │
       │                                                         │
  0,0  └─────────────────────────────────────────────────────────┘ 200,0
```

### Zone Definitions

| Zone | X Range | Description |
|------|---------|-------------|
| D (Defensive) | 0-75 | Home team's end |
| N (Neutral) | 75-125 | Center ice |
| O (Offensive) | 125-200 | Away team's end |

### Period Direction

- **Periods 1 & 3:** Home attacks right (x increases toward offensive zone)
- **Period 2:** Home attacks left (reversed)

The ETL flips coordinates to normalize:
```python
if period == 2:
    x_normalized = 200 - x_raw
    y_normalized = 85 - y_raw
```

### Danger Zones

| Zone | XY Range | xG Base Rate |
|------|----------|--------------|
| High Danger | x≥180, y: 30-55 | 0.25 |
| Medium | x≥160, y: 20-65 | 0.08 |
| Low | Everything else | 0.03 |

---

## Event Types

### Major Event Types

| Event Type | Description | Key Details |
|------------|-------------|-------------|
| Goal | Goal scored | event_detail=Goal_Scored |
| Shot | Shot attempt | Various outcomes |
| Pass | Pass attempt | Completed/Incomplete |
| Faceoff | Faceoff | Winner/Loser |
| Turnover | Giveaway/Takeaway | Type specified |
| Penalty | Penalty called | Type, duration |
| Stoppage | Play stopped | Whistle reason |

### Shot Details

| event_detail | Description |
|--------------|-------------|
| Shot_OnNetSaved | Saved shot |
| Shot_OnNet | On goal (unspecified) |
| Shot_Goal | Shot that scored |
| Shot_Missed | Missed net |
| Shot_MissedPost | Hit post |
| Shot_Blocked | Blocked by player |

### Pass Types

| event_detail | Description |
|--------------|-------------|
| Pass_Completed | Successful pass |
| Pass_Incomplete | Failed pass |
| Pass_Intercepted | Opponent intercepted |

### Zone Entry Types

| zone_entry_type | Description |
|-----------------|-------------|
| Carry | Carried puck in |
| Dump | Dumped puck in |
| Pass | Passed puck in |
| Failed | Entry attempt failed |

---

## How ETL Uses Tracker Data

### 1. Load Excel File

```python
tracking = pd.ExcelFile(f'data/raw/games/{game_id}/{game_id}_tracking.xlsx')
events = pd.read_excel(tracking, 'Events')
shifts = pd.read_excel(tracking, 'Shifts')
```

### 2. Resolve Player IDs

```python
# Jersey number → player_id via lookup
events['player_id'] = events.apply(
    lambda r: player_lookup.get((game_id, r['team'], r['jersey_1']), None),
    axis=1
)
```

### 3. Calculate Time Fields

```python
events['time_start_total_seconds'] = events['time_min'] * 60 + events['time_sec']
events['event_running_start'] = (events['period'] - 1) * 1200 + events['time_start_total_seconds']
```

### 4. Assign Danger Levels

```python
def get_danger_level(x, y):
    if x >= 180 and 30 <= y <= 55:
        return 'high'
    elif x >= 160 and 20 <= y <= 65:
        return 'medium'
    else:
        return 'low'

events['danger_level'] = events.apply(
    lambda r: get_danger_level(r['x'], r['y']),
    axis=1
)
```

---

## Data Quality

### Garbage In = Garbage Out

The quality of analytics depends entirely on tracking accuracy:
- Accurate event classification
- Correct player identification
- Precise XY coordinates
- Complete shift data

### Common Issues

| Issue | Impact | Mitigation |
|-------|--------|------------|
| Wrong jersey | Wrong player stats | Verify against roster |
| Missing events | Incomplete data | Review game video |
| Wrong coordinates | Bad xG calculations | Use rink zones as guide |
| Missing shifts | TOI errors | Track all line changes |

---

## Key Takeaways

1. **Tracker records all game events** with XY coordinates
2. **Exports to Excel** for ETL processing
3. **XY system:** 200ft x 85ft rink, origin at bottom-left
4. **Period 2 is flipped** (normalized by ETL)
5. **Data quality is critical** - affects all analytics
6. **Current architecture is technical debt** (planned rewrite)

---

**Next:** [13-integration.md](13-integration.md) - How all systems connect
