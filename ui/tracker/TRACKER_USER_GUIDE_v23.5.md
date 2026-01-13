# BenchSight Game Tracker v23.5
## Complete User Guide

---

# Table of Contents

1. [Quick Start](#1-quick-start)
2. [Interface Overview](#2-interface-overview)
3. [Video Playback](#3-video-playback)
4. [Event Tracking](#4-event-tracking)
5. [XY Positioning](#5-xy-positioning)
6. [Shift Tracking](#6-shift-tracking)
7. [Workflow Automation](#7-workflow-automation)
8. [Advanced Features (v23.5)](#8-advanced-features-v235)
9. [Data Management](#9-data-management)
10. [Keyboard Shortcuts](#10-keyboard-shortcuts)
11. [Tips & Best Practices](#11-tips--best-practices)

---

# 1. Quick Start

## First Time Setup

1. **Open the tracker** in a modern browser (Chrome/Edge recommended)
2. **Click ⚙️ Settings** to configure:
   - Supabase URL and Key (optional - for cloud sync)
   - Auto-save interval (default: 30 seconds)
   - Period length (default: 18 minutes for rec leagues)
3. **Create or load a game**
4. **Load video** (optional but recommended)
5. **Start tracking!**

## Basic Workflow

```
1. Load Video → 2. Set Period Markers → 3. Play Video → 4. Pause at Event
     ↓
5. Select Event Type → 6. Add Players → 7. Click Rink for XY → 8. Log Event
     ↓
9. Repeat → 10. Export Data
```

---

# 2. Interface Overview

## Main Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER: Game Selection | Period | Team Colors | Save Status     │
├─────────────────────────────────────────────────────────────────┤
│ VIDEO PLAYER (collapsible)                                      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [Sources ▼] [+] [📁] [⚙️]     00:15:32 → P1 12:30    [▼]   │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │                    VIDEO DISPLAY                        │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ │ [⏪10][◀1][|◀][▶][▶|][1▶][10⏩] | Speed: [.25][.5][1][1.5][2]│ │
│ │ Sync: [✓ Auto] [📍Start] [📍End] | Zoom: [-][1:1][+]        │ │
│ │ Markers: [P1🏒][P1🛑][P2🏒][P2🛑][P3🏒][P3🛑][OT🏒][⏸️+]    │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ LEFT PANEL              │ CENTER: RINK          │ RIGHT PANEL   │
│ ┌─────────────────────┐ │ ┌─────────────────┐   │ ┌───────────┐ │
│ │ Event Type Buttons  │ │ │                 │   │ │ Shifts    │ │
│ │ [Shot][Goal][Pass]..│ │ │    ICE RINK     │   │ │           │ │
│ │                     │ │ │   (click for    │   │ │ On-Ice    │ │
│ │ Quick Details       │ │ │   XY positions) │   │ │ Players   │ │
│ │ [OnNet][Missed]...  │ │ │                 │   │ │           │ │
│ │                     │ │ └─────────────────┘   │ │ Line      │ │
│ │ Zone: [O][N][D]     │ │                       │ │ Presets   │ │
│ │ Success: [✓][✗]     │ │ Timeline: [Sh][Pa]... │ │           │ │
│ │                     │ │                       │ │           │ │
│ │ Event Players       │ │ XY Controls           │ │           │ │
│ │ [+All][📋][📍All]   │ │ [🏒Puck][👤Player]   │ │           │ │
│ │ #10 Smith [E1]      │ │ Slots: [1][2][3]...   │ │           │ │
│ │ #23 Jones [E2]      │ │                       │ │           │ │
│ │                     │ ├───────────────────────┤ │           │ │
│ │ Chains: [Entry]...  │ │ EVENT LOG             │ │           │ │
│ └─────────────────────┘ │ (scrollable list)     │ └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Color Coding

| Element | Color | Meaning |
|---------|-------|---------|
| Home Team | Blue (default) | Home team players/events |
| Away Team | Red (default) | Away team players/events |
| Accent | Cyan | Active/selected items |
| Success | Green | Successful plays, goals |
| Danger | Red | Errors, unsuccessful |
| Warning | Orange | Cautions, penalties |

---

# 3. Video Playback

## Loading Video

### YouTube
1. Click **+** button in video header
2. Paste YouTube URL
3. Assign name and hotkey (1-9)
4. Click "Add Video"

### Local File
1. Click **📁** button
2. Select video file from computer
3. Video loads automatically

### Multiple Sources
Add multiple camera angles (main, overhead, behind-net):

| Hotkey | Source |
|--------|--------|
| Ctrl+1 | Main Camera |
| Ctrl+2 | Overhead |
| Ctrl+3 | Behind Net |

Click the numbered buttons in header or press **Ctrl+1-9** to switch.

## Playback Controls

| Control | Button | Hotkey |
|---------|--------|--------|
| Play/Pause | ▶/⏸ | `Space` |
| Back 1s | ◀1 | `←` |
| Forward 1s | 1▶ | `→` |
| Back 10s | ⏪10 | `Shift+←` |
| Forward 10s | 10⏩ | `Shift+→` |
| Frame back | \|◀ | `;` |
| Frame forward | ▶\| | `'` |
| Speed up | - | `↑` |
| Speed down | - | `↓` |
| Zoom in | + | `+` or `=` |
| Zoom out | − | `-` |
| Reset zoom | 1:1 | `0` |

## Clock Sync

### Setting Game Markers
Mark when each period starts/ends in the video:

1. Play video to P1 puck drop
2. Click **P1🏒** (marks P1 start)
3. Continue to P1 end, click **P1🛑**
4. Repeat for P2, P3, OT

### Capturing Event Times
When paused at an event:
- Click **📍 Start** → Captures game clock to Start Time field
- Click **📍 End** → Captures game clock to End Time field

The display shows: `00:15:32 → P1 12:30` (video time → calculated game clock)

### Stoppages
Click **⏸️+** to mark timeouts, injuries, or other stoppages that affect time sync.

---

# 4. Event Tracking

## Event Types

| Type | Hotkey | Description |
|------|--------|-------------|
| **Faceoff** | `F` | Faceoff won/lost |
| **Shot** | `S` | Shot attempt (on net, missed, blocked) |
| **Goal** | `G` | Goal scored |
| **Pass** | `P` | Pass attempt |
| **Turnover** | `T` | Puck turnover |
| **Zone Entry/Exit** | `Z` | Zone transitions |
| **Penalty** | `N` | Penalty called |
| **Stoppage** | `X` | Play stoppage |
| **Possession** | `O` | Puck possession |
| **Save** | `V` | Goalie save |
| **Rebound** | `R` | Rebound |
| **Dead Ice** | `D` | Dead puck situation |

## Quick Detail Buttons

Based on event type, quick buttons appear:

| Event Type | Quick Buttons |
|------------|---------------|
| Shot | [OnNet] [Missed] [Blocked] [Goal] |
| Pass | [Completed] [Incomplete] [Intercepted] |
| Faceoff | [Won] [Lost] |
| Zone Entry | [Carry] [Dump] [Pass] |

## Zone Selection

| Button | Zone | Hotkey |
|--------|------|--------|
| **O** | Offensive | `Q` |
| **N** | Neutral | `W` |
| **D** | Defensive | `E` |

*Zone auto-detects from rink click position*

## Success Indicator

| Button | Meaning | Hotkey |
|--------|---------|--------|
| **✓** | Successful | `Y` |
| **✗** | Unsuccessful | `U` |

## Adding Players

### Quick Add
Click player chips below the player list to add them.

### By Jersey Number
Type number in input, press Enter or click **+#**

### Add All On-Ice
Click **+All** to add all players currently on ice.

### Copy from Last Event
Click **📋** to copy players from previous event.

### Player Roles

| Role | Abbreviation | Description |
|------|--------------|-------------|
| Event Player 1 | E1 | Primary player (shooter, passer) |
| Event Player 2 | E2 | Secondary (assist, receiver) |
| Event Player 3 | E3 | Third player |
| Opponent Player 1 | O1 | Primary opponent |
| Opponent Player 2 | O2 | Secondary opponent |

**Reassigning roles:** Select a player, then press `1-6` to change their role.

## Logging Events

| Action | Hotkey |
|--------|--------|
| Log with confirmation | `Enter` or `L` |
| Quick log (no confirmation) | `Shift+Enter` |
| Clear current event | `Escape` |
| Undo last event | **↩️ Undo** button |

---

# 5. XY Positioning

## Modes

| Mode | Icon | Description |
|------|------|-------------|
| **Puck** | 🏒 | Click places puck trajectory points |
| **Player** | 👤 | Click places selected player |

Toggle with `Tab` or click mode buttons.

## Placing Points

### Puck Mode
1. Click rink for puck position
2. Click again for trajectory endpoint
3. Auto-advances to next slot

### Player Mode
1. Select player from dropdown or click their chip
2. Click rink to place them
3. Select next player and repeat

## Smart Auto-Linking

Puck positions automatically link to players based on event type:

| Event | Slot 1 | Slot 2 |
|-------|--------|--------|
| **Shot** | E1 (shooter) | Net location |
| **Pass** | E1 (passer) | E2 (receiver) |
| **Hit/Battle** | E1 + O1 (both) | - |
| **Possession** | E1 (carrier) | - |

## Drag to Create

**Drag on rink** instead of clicking twice:
- Drag toward net (offensive zone) → Creates **Shot**
- Drag elsewhere → Creates **Pass**
- Start and end points auto-set

## All Here Button

Click **📍 All Here** to place ALL event players at the last puck location (useful for hits, battles, board play).

## XY Controls

| Button | Action | Hotkey |
|--------|--------|--------|
| ↩ | Undo last placement | `Backspace` |
| ✕ | Clear current item XY | - |
| 🗑 | Clear all rink markers | - |

## Slot Selection

Click slot buttons [1][2][3][4][5][6] to edit specific positions.

## Keyboard XY Assignment

Hold a number key while clicking rink:
- Hold `1` + click → Places at E1 position
- Hold `2` + click → Places at E2 position
- etc.

---

# 6. Shift Tracking

## Recording Shifts

### Start a Shift
1. Select players going on ice
2. Set start time (or use **📍 Start**)
3. Click **Log Shift** or press `L`

### End a Shift
1. When players come off, click **End Shift** or press `E`
2. End time auto-captures

## Line Presets

Save common line combinations:
1. Set up players
2. Click **⚙️** next to Lines
3. Save as preset (F1, F2, D1, etc.)

Quick line changes:
- Click preset button to load that line
- Press `Q` for quick line change modal

## On-Ice Roster

The right panel shows:
- Current on-ice players
- Time on ice
- Shift warnings (long shifts highlighted)

---

# 7. Workflow Automation

## Quick Chains

Pre-defined multi-event sequences:

| Button | Sequence |
|--------|----------|
| **Entry** | Zone Entry → Possession |
| **Dump** | Dump In → Forecheck |
| **Shot+** | Shot → Save → Rebound |
| **Break** | Breakout → Pass → Zone Exit |
| **PP** | PP Cycle → Pass → Shot |

Click a chain button to start the sequence. Events auto-flow.

## Sequence Mode

Enable **🔗** to auto-link consecutive events:
- Events automatically connect
- Follow-up events suggested
- Great for tracking play sequences

## One-Click Zone Events

Click on rink with no event type selected:
- **Offensive zone** → Auto-creates Shot
- **Defensive zone** → Auto-creates Possession (Breakout)
- **Neutral zone** → Auto-creates Zone Entry

## Auto-Populate Features

| Feature | Description |
|---------|-------------|
| Auto goalie | Opposing goalie auto-added for shots |
| Copy last players | Recent players pinned at top |
| Auto time format | Times auto-format as MM:SS |
| Auto reindex | Events auto-sort by time |

## Templates

Save custom event setups:
1. Configure an event
2. Click **💾 Save** 
3. Name your template
4. Access from Templates dropdown

---

# 8. Advanced Features (v23.5)

## Quick Queue

Mark events during fast action, fill details later:

1. Click **Queue** buttons: `Sh` `Pa` `TO` `Hi` `ZE`
2. Events appear in queue bar (yellow)
3. Click queued event to complete it
4. Video seeks to that moment automatically

*Perfect for fast-paced sequences you can't track in real-time*

## Possession Tracker

Track time of possession:

| Button | Action |
|--------|--------|
| **H** | Start home possession |
| **A** | Start away possession |
| **↺** | Reset counters |

The bar shows live possession percentage.

## Penalty Box Manager

Live countdown timers for penalties:

- Auto-tracks penalty time remaining
- Updates strength indicator (5v4, 4v4, etc.)
- Penalties auto-remove when expired
- Click ✕ to clear manually

## Recent Players Bar

Last 8 used players pinned at top:

- Click any player chip for quick add
- Color-coded by team (home/away)
- Persists during session

## Event Suggestions

Context-aware next event suggestions:

| After | Suggests |
|-------|----------|
| Goal | Faceoff |
| Shot | Save, Rebound, Goal |
| Save | Rebound, Possession |
| Pass | Shot, Pass |
| Turnover | Possession, Shot |

Toggle with **💡** button.

## Multi-Level Undo

Full undo stack (up to 20 actions):

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Smart undo (XY first, then events) |
| `Ctrl+Shift+Z` | Force undo event |

Undo button shows stack count.

## Batch Edit

Edit multiple events at once:

1. Click **☑ Batch** button
2. Click events to select (blue highlight)
3. Click **☑ Batch** again
4. Choose fields to change (Zone, Success, Team, Highlight)
5. Apply to all selected

## Goal Review Mode

Slow-motion goal analysis:

1. Find goal in event log
2. Click **🎬** button on goal row
3. Video seeks to 10s before goal
4. Playback at 0.5x speed
5. Related events highlighted in green

## Keyboard XY Mode (WASD)

Position without mouse:

1. Click **⌨ XY** button (or hotkey)
2. Use WASD to move cursor
3. `Shift+WASD` = larger steps
4. `Enter` = place point
5. `Escape` = exit mode

## Quick Notes

Attach notes to events:

1. Click **📝** button
2. Enter note text
3. Notes saved with event
4. View in edit modal

## Live Stats Overlay

Show stats on video:

1. Click **📊** button
2. Stats appear on video (top-right)
3. Updates in real-time
4. Shows: Score, SOG, team names

---

# 8b. Speed Features (v23.5)

## Mirror Mode

Auto-flip XY coordinates for period 2 (when teams switch ends):

- **🔄 Mirror** button toggles
- Automatically applies to all XY placements
- No need to mentally flip coordinates

## Auto Zone from XY

Automatically sets zone based on where you click:

- **🎯 AutoZ** button toggles
- Click offensive end → Zone = O
- Click defensive end → Zone = D
- Accounts for team and period

## Goalie Auto-Add

Automatically adds opposing goalie on shot events:

- **🥅 AutoG** button toggles
- Works for: Shot, Goal, Save, Rebound
- Finds goalie from roster (position = G)

## Numpad Mode

Use number pad for faster player selection:

- **🔢 Numpad** button toggles
- Numpad 1-6 = Event player slots
- Shift+Numpad = Opponent player slots
- NumpadEnter = Log event
- NumpadAdd = Toggle highlight

## Quick Stoppages

One-click stoppage events:

| Button | Action |
|--------|--------|
| **Ice-H** | Icing (Home) |
| **Ice-A** | Icing (Away) |
| **Offside** | Offside |

## Quick Strength

One-click strength setting:

| Button | Strength |
|--------|----------|
| **5v5** | Even strength |
| **PP** | Power play (5v4) |
| **PK** | Penalty kill (4v5) |
| **4v4** | 4-on-4 |

## Empty Net Toggle

Track empty net situations:

- **EN-H** = Home goalie pulled
- **EN-A** = Away goalie pulled
- Indicator shows in header

## Gap Finder

Find missing event coverage:

1. Click **🔍 Gaps**
2. Shows periods with no events for >1 minute
3. Click "Go" to jump to that video time

## Duplicate Detection

Warn about possible duplicates:

- **⚠️ Dup?** checks current event
- Warns if similar event exists within 5 seconds
- Helps avoid double-logging

## Shift Length Alerts

Visual warnings for long shifts:

| Duration | Alert |
|----------|-------|
| 45+ sec | Yellow highlight |
| 60+ sec | Red pulse animation |

## Auto-Link Suggestions

Automatically suggests linking related events:

| Event | Links to |
|-------|----------|
| Save | Previous Shot |
| Rebound | Previous Shot/Save |
| Goal | Previous Shot/Rebound |
| Turnover | Previous Pass |

---

# 8c. Advanced Speed Features (v23.5)

## Event Macros

Record and replay event sequences:

1. Click **⏺ Rec** to start recording
2. Log your event sequence
3. Click **⏹ Stop** when done
4. Name your macro
5. Click **🎬 Macros** to replay

*Great for: PP setups, breakouts, recurring plays*

## Smart Defaults

Claude learns your patterns:

- Tracks most common Detail 1 for each event type
- After 3+ uses, auto-fills defaults
- Learns zone preferences by event type

## Shot Chart Overlay

See all shots on the rink:

- **📍 Shots** toggle
- Green = Goals, Team color = Shots
- Updates as you track

## Consistency Checker

Find tracking issues:

- **✅ Check** button
- Warns: Shot without Save, Goal without Shot
- Flags events without players
- Click "Fix" to jump to issue

## Floating Video

Draggable video window:

- **📺 Float** toggle
- Drag header to move
- Resize from corners
- Stays on top while scrolling

## Progress Estimator

Track your progress:

- Shows event count
- Estimates completion %
- Based on period and time

## Period Progress Ring

Visual period indicator:

- Circular progress around period number
- Shows time elapsed in period

---

# 9. Data Management

## Saving

| Method | Description |
|--------|-------------|
| **Auto-save** | Every 30 seconds to browser storage |
| **Quick Save** | 💾 button saves to selected folder |
| **Export** | Download as Excel file |

## Settings Export/Import

### Period-Specific Lengths

Configure different lengths for each period in **Settings (⚙️)** or **Video Timing (🎬)**:

| Setting | Default | Description |
|---------|---------|-------------|
| **P1** | 18 min | Period 1 length |
| **P2** | 18 min | Period 2 length |
| **P3** | 18 min | Period 3 length |
| **OT** | 5 min | Overtime length |

*Example: P1=20, P2=18, P3=17 for variable ice time allocation*

**Where to Set:**
- **Settings Modal** (⚙️) - Quick access
- **Video Timing Modal** (🎬) - With video sync preview

Both modals stay in sync - changes in one update the other.

**Indicator:** Header shows current period length: `(P1: 20m)` or `(18m)` if all equal.

Hover over indicator to see all period lengths.

**Features:**
- Clock auto-sets to correct length when changing periods
- Export uses per-period lengths for running time calculations
- Video sync accounts for variable period durations
- Saved with game data
- Running Time Preview updates live in Video Timing modal

### Export Settings
Click **📤 Export Settings** to save:
- Custom chain presets
- Penalty minutes setting
- Video sources
- Team colors
- Rosters

### Import Settings
Click **📥 Import Settings** to restore from JSON file.

## Roster Import

### From Excel/CSV
1. Click **📋 Import Roster**
2. Select .xlsx, .xls, or .csv file
3. Preview parsed players
4. Choose Home or Away team

**Expected columns:** Jersey #, Name (or First/Last), Position

### Manual Entry
1. Click **✏️ Manual Roster**
2. Enter one player per line: `10, John Smith`
3. Choose Home or Away team

## Validation

Click **🔍 Validate** to check:
- Players match official roster
- Goals match noradhockey.com
- Jersey numbers are valid
- No duplicate events

## Importing Old Games

When importing Excel files from older tracking sessions, the fuzzy matcher automatically maps old terminology to current values:

### Synonym Mappings (v23.5)

| Old Value | Maps To |
|-----------|---------|
| `ZoneEntry_Rush` | `ZoneEntry_Carried` |
| `ZoneEntry-Rush` | `ZoneEntry-Carried` |
| `ZoneExit_Rush` | `ZoneExit_Carried` |
| `ZoneExit-Rush` | `ZoneExit-Carried` |
| `Entry_Rush` | `Entry_Carried` |
| `Exit_Rush` | `Exit_Carried` |
| `Shot_OnNet` | `Shot_OnNetSaved` |
| `Blocked` | `Shot_Blocked` |
| `Missed` | `Shot_Missed` |

**Note:** "Rush" in zone entry/exit context means controlled carry with the puck. The tracker now uses "Carried" to match Supabase dimension tables.

### How It Works

1. Import old Excel file
2. Fuzzy matcher detects old values (e.g., `ZoneEntry_Rush`)
3. Applies synonym mapping → `ZoneEntry_Carried`
4. Matches against Supabase dropdown values
5. Event imports with correct terminology

### Mapping Preview

When importing, the mapping modal shows:
- ✓ Exact matches (green)
- ≈ Fuzzy/synonym matches (accent color)
- ? Unmapped values (need manual selection)

---

# 10. Keyboard Shortcuts

## Complete Reference

### Event Types
| Key | Action |
|-----|--------|
| `F` | Faceoff |
| `S` | Shot |
| `G` | Goal |
| `P` | Pass |
| `T` | Turnover |
| `Z` | Zone Entry/Exit |
| `N` | Penalty |
| `X` | Stoppage |
| `O` | Possession |
| `V` | Save |
| `R` | Rebound |
| `D` | Dead Ice |

### Zone & Success
| Key | Action |
|-----|--------|
| `Q` | Offensive zone |
| `W` | Neutral zone |
| `E` | Defensive zone |
| `Y` | Success |
| `U` | Unsuccess |

### Teams
| Key | Action |
|-----|--------|
| `H` | Set Home team |
| `A` | Set Away team |
| `Shift+S` | Swap teams |

### Players
| Key | Action |
|-----|--------|
| `1-6` | Select/assign Event Player 1-6 |
| `Alt+1-6` | Select/assign Opponent Player 1-6 |
| `Shift+1-6` | Force add player (bypass reassign) |
| `Tab` | Toggle Puck/Player XY mode |
| `` ` `` | Switch to Puck mode |

### Logging
| Key | Action |
|-----|--------|
| `Enter` | Log event (with confirmation) |
| `Shift+Enter` | Quick log (no confirmation) |
| `L` | Log event |
| `Escape` | Clear/Cancel |

### Shifts
| Key | Action |
|-----|--------|
| `[` | Log shift |
| `]` | Set shift start |

### Navigation
| Key | Action |
|-----|--------|
| `I` | Edit last event |
| `,` | Jump to first event |
| `.` | Jump to last event |
| `?` | Open help |

### Video Controls
| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `←` | Seek -1s |
| `→` | Seek +1s |
| `Shift+←` | Seek -10s |
| `Shift+→` | Seek +10s |
| `↑` | Speed up |
| `↓` | Speed down |
| `;` | Frame back |
| `'` | Frame forward |
| `+` / `=` | Zoom in |
| `-` | Zoom out |
| `0` | Reset zoom |
| `Ctrl+1-9` | Switch video source |

### XY Placement
| Key | Action |
|-----|--------|
| `Backspace` | Undo last XY |
| Hold `1-6` + click | Place at player slot |

### Periods
| Key | Action |
|-----|--------|
| `Shift+1` (`!`) | Period 1 |
| `Shift+2` (`@`) | Period 2 |
| `Shift+3` (`#`) | Period 3 |
| `Shift+4` (`$`) | Overtime |

---

# 11. Tips & Best Practices

## Efficient Tracking

### Before the Game
1. Import rosters for both teams
2. Set up line presets
3. Configure period length (18 min for rec)
4. Load video and set period markers

### During Tracking
1. **Use hotkeys** - much faster than clicking
2. **Drag for passes/shots** - single gesture creates event
3. **Use chains** for common sequences
4. **Quick log** (`Shift+Enter`) when confident

### Speed Tips
- Keep one hand on keyboard (event types, logging)
- Keep one hand on mouse (XY, players)
- Use `Tab` to toggle XY modes
- Use **📋 Copy Players** for similar events

## Common Workflows

### Tracking a Shot
1. Pause video at shot
2. Press `S` (Shot)
3. Click quick detail: [OnNet]
4. Drag from shooter to net (or click twice)
5. Press `Enter` to log

### Tracking a Goal
1. Press `G` (Goal)
2. Click [Goal_Scored]
3. Add scorer (E1), assisters (E2, E3)
4. Click shooter position
5. Click **⭐** for highlight
6. Press `Enter`

### Tracking a Faceoff
1. Press `F` (Faceoff)
2. Click on faceoff dot (auto-positions)
3. Select winner, set [Won] or [Lost]
4. Press `Enter`

### Tracking a Pass Play
1. Drag from passer to receiver
2. (Auto-creates Pass event)
3. Verify players
4. Press `Enter`

### Tracking a Hit
1. Press event type or click Hit
2. Add hitting player (E1) and hit player (O1)
3. Click location once
4. Click **📍 All Here** (places both at puck)
5. Press `Enter`

## Troubleshooting

### Video won't load
- Check URL is correct
- Try a different browser
- For YouTube, ensure video is public/unlisted

### Events not saving
- Check browser console for errors
- Verify Supabase connection (if using)
- Use Export to backup data

### XY not placing
- Make sure event type is selected
- Check you're in correct mode (Puck vs Player)
- Try clicking directly on rink area

### Players not showing
- Import roster first
- Check correct game is selected
- Verify team selection (Home/Away)

---

# Appendix: Data Fields

## Event Record

| Field | Description |
|-------|-------------|
| idx | Event index |
| period | Period (1, 2, 3, OT) |
| start_time | Game clock at start |
| end_time | Game clock at end |
| type | Event type |
| detail1 | Primary detail |
| detail2 | Secondary detail |
| team | Event team (home/away) |
| zone | Zone (o/n/d) |
| success | Success (true/false/null) |
| strength | Game strength (5v5, 5v4, etc.) |
| players[] | Array of player objects |
| puckXY[] | Puck position(s) |
| netXY | Net target (for shots) |
| isHighlight | Highlight flag |
| linkedEventIdx | Linked event index |

## Player Record (within event)

| Field | Description |
|-------|-------------|
| num | Jersey number |
| name | Player name |
| team | Player team |
| role | Role (event_team_player_1, etc.) |
| playD1 | Play detail 1 |
| playD2 | Play detail 2 |
| playSuccess | Play success |
| xy[] | Player position(s) |

---

# 12. Version 23.5 Summary

## Speed & Workflow Features

| Feature | Description |
|---------|-------------|
| 🔄 Mirror Mode | Auto-flip XY for period 2 |
| 🎯 Auto Zone | Zone from click position |
| 🥅 Auto Goalie | Add goalie on shots |
| 🔢 Numpad Mode | Use numpad for players |
| ⏺ Event Macros | Record/replay sequences |
| 📍 Shot Chart Overlay | Show shots on rink |
| 🔍 Gap Finder | Find missing events |
| ✅ Consistency Check | Validate tracking |
| 📺 Floating Video | Draggable window |

## Per-Period Lengths

Configure different lengths for P1, P2, P3, OT in Settings or Video Timing modal.

## Import Synonyms

Automatic mapping of old terminology:
- `Rush` → `Carried` (zone entries/exits)
- `Shot_OnNet` → `Shot_OnNetSaved`

---

*BenchSight Game Tracker v23.5 - Built for NORAD Recreational Hockey League*
