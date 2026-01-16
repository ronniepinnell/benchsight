# BenchSight Game Tracker v23.9
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
9. [Linked Events & Auto-Suggestions (v23.9)](#9-linked-events--auto-suggestions-v239)
10. [Data Management](#10-data-management)
11. [Keyboard Shortcuts](#11-keyboard-shortcuts)
12. [Tips & Best Practices](#12-tips--best-practices)

---

# 1. Quick Start

## First Time Setup

1. **Open the tracker** in a modern browser (Chrome/Edge recommended)
2. **Click ⚙️ Settings** to configure:
   - Supabase URL and Key (optional - for cloud sync)
   - Auto-save interval (default: 30 seconds)
   - Period length (default: 18 minutes for rec leagues)
   - **Event Chain Templates** (v23.9) - Define auto-suggestions for next events
3. **Create or load a game**
4. **Load video** (optional but recommended)
5. **Start tracking!**

## Basic Workflow

```
1. Load Video → 2. Set Period Markers → 3. Play Video → 4. Pause at Event
     ↓
5. Select Event Type → 6. Add Players → 7. Click Rink for XY → 8. Log Event
     ↓
9. (v23.9) Auto-suggestion modal may appear → Accept/Deny next event
     ↓
10. Repeat → 11. Export Data
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
│ │                     │ │ (scrollable list)     │ │           │ │
│ │ Linked Event #      │ │                       │ │           │ │
│ │ [🔗 Select...]      │ │                       │ │           │ │
│ └─────────────────────┘ └───────────────────────┘ └───────────┘ │
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

## Success Toggle

| Button | Success | Hotkey |
|--------|---------|--------|
| **✓** | Successful | `Y` |
| **✗** | Unsuccessful | `U` |

## Event Confirmation Modal

When you press `Enter` to log an event, a confirmation modal appears showing all event details. You can:

- **Edit** any field (type, detail1, detail2, zone, success, time, players, etc.)
- **Review** player details and play details (PD1, PD2, success, pressure)
- **Confirm & Log** - Log the event and close modal
- **Log & Continue** - Log the event but keep form open for next event
- **Log & Next** (v23.9) - Log event and auto-create next linked event from templates

### v23.9: Log & Next Feature

The **"✓ Log & Next"** button (or `Ctrl+L` / `Cmd+L` hotkey) in the confirmation modal:

1. Logs the current event
2. Checks event chain templates for matches
3. If a template matches, automatically creates the next linked event with:
   - Event type, detail1, detail2 from template
   - XY data copied (if configured)
   - Zone copied (if configured)
   - Player mappings applied (e.g., event_player_1 → opp_player_1 for Shot→Save)
   - Teams swapped if needed (e.g., Shot→Save)
   - Events automatically linked

**Example:** Log a Shot with `OnNetSaved` detail1 → Press "Log & Next" → Automatically creates a Save event with goalie as opp_player_1, XY data copied, team swapped.

---

# 5. XY Positioning

## Modes

| Mode | Button | Hotkey | Description |
|------|--------|--------|-------------|
| **Puck** | 🏒 | `Tab` or `M` | Place puck position |
| **Player** | 👤 | `Tab` or `M` | Place player positions |

## Placing XY

1. Select mode (Puck or Player)
2. If Player mode, select player from dropdown
3. Click on rink to place position
4. Use slot buttons [1][2][3]... to place multiple points
5. XY positions are stored as center-relative coordinates (-100 to +100 for x, -42.5 to +42.5 for y)

## XY Slot System

Each event can have up to 10 XY points:
- **Slot 1** = Starting position
- **Slot 2-9** = Intermediate positions
- **Slot 10** = Ending position

Use the slot buttons to place multiple points along a path (e.g., puck movement during a pass).

## v23.9: XY Auto-Sync for Possession Events

For possession events (Zone Entry/Exit Rush, Possession), puck XY and event_player_1 XY sync automatically:

- **Edit puck XY** → Automatically updates event_player_1 XY (all points sync)
- **Edit event_player_1 XY** → Automatically updates puck XY (all points sync)
- This bidirectional sync ensures puck and player positions stay aligned for possession plays

**Note:** This only applies to events where the player has possession (Zone Entry/Exit with "Rush" detail2, or Possession events).

---

# 6. Shift Tracking

## Logging Shifts

1. **Press `L`** or click "Log Shift"
2. Select period
3. Enter start/end times (or click to capture from clock)
4. Select players from roster
5. Set start/stop types (e.g., "Period Start", "Icing")
6. Click "Save Shift"

## Quick Line Change

**Press `Q`** to quickly change lines while tracking:
- Preserves current period and time
- Sets stop type to "Line Change"
- Opens shift modal with pre-filled values

## Ending Shifts

**Press `E`** to end current shift:
- Sets end time to current clock
- Sets stop type to "Line Change"
- Saves shift

## Shift Panel

The right panel shows:
- **Current on-ice players** for both teams
- **Line presets** (save common line combinations)
- **Shift history** (scrollable list)

---

# 7. Workflow Automation

## Sequence Mode

**🔗 Sequence Mode** button automatically links consecutive events:
- When enabled, each new event links to the previous one
- Creates a play sequence (useful for multi-event plays)
- Example: Pass → Pass → Shot → Goal (all linked together)

## Possession Mode

**🏒 Possession Mode** button:
- Automatically links events together
- Sets event type to Possession
- Enables sequence mode to track full possession sequence

## Shot Mode

**🎯 Shot Mode** button:
- Enable to quickly log shots by clicking on the rink
- Automatically sets event type to Shot
- Great for rapid shot tracking during fast-paced sequences

## Auto-Add Goalie

**🥅 AutoG** button automatically adds opposing goalie:
- Works for: Shot, Goal, Save, Rebound events
- Finds goalie from roster (position = G)
- Saves time by not having to manually add goalie each time

## Auto Zone

**🎯 AutoZ** automatically sets zone based on click position:
- Click offensive end → Zone = O
- Click defensive end → Zone = D
- Click center → Zone = N

## Mirror Mode

**🔄 Mirror** button auto-flips XY coordinates for period 2:
- When teams switch ends, XY coordinates automatically flip
- No need to mentally flip coordinates when placing players/puck

---

# 8. Advanced Features (v23.5)

## Event Macros

Record and replay event sequences:

1. Click **⏺ Rec** to start recording
2. Log your event sequence
3. Click **⏹ Stop** when done
4. Name your macro
5. Click **🎬 Macros** to replay

*Great for: PP setups, breakouts, recurring plays*

## Smart Defaults

The tracker learns your patterns:
- Tracks most common Detail 1 for each event type
- After 3+ uses, auto-fills defaults
- Learns zone preferences by event type

## Quick Queue

Mark events quickly, fill details later:

| Button | Action |
|--------|--------|
| **Sh** | Queue Shot |
| **Pa** | Queue Pass |
| **TO** | Queue Turnover |
| **Hi** | Queue Hit |
| **ZE** | Queue Zone Entry/Exit |

Useful for fast-paced sequences where you need to mark events quickly.

## Shot Chart Overlay

**📍 Shots** button displays all tracked shots on the rink:
- Goals appear in green
- Shots on goal in team colors
- Helps visualize shot locations and patterns

---

# 9. Linked Events & Auto-Suggestions (v23.9)

## Linking Events

Events can be linked together to create sequences (e.g., Shot→Save, Pass→Turnover):

### Manual Linking

1. Select a previous event number in the **"Linked Event #"** dropdown
2. Or press **`K`** to quickly link to the last event
3. XY data automatically propagates to all linked events in the chain

### Sequence Mode

Enable **🔗 Sequence Mode** to automatically link consecutive events:
- Each new event links to the previous one
- Creates continuous play sequences
- Useful for tracking multi-event plays

### Quick Link Hotkey

**Press `K`** to quickly link to the last event:
- Works for all event types
- Auto-links if current type is compatible with last event type
- Otherwise creates manual link

## XY Propagation

When events are linked, XY data automatically propagates to all events in the chain:

- **Puck XY** - All puck positions copied to all linked events
- **Player XY** - All player positions copied to all linked events
- **Net XY** - Net positions copied if available
- Ensures consistent tracking across multi-event sequences

**Example:** Link a Shot event to a Save event → Save event automatically gets all puck and player XY positions from the Shot.

## Event Chain Templates (v23.9)

Event chain templates automatically suggest/create next events based on triggers.

### Accessing Templates

Go to **Settings → Manage Event Chain Templates** to:
- View existing templates
- Create new templates
- Edit existing templates
- Delete templates

### Creating Templates

Each template has:

- **Trigger** - Conditions that must match:
  - Event type (e.g., "Shot")
  - Detail1 (e.g., "OnNetSaved")
  - Detail2 (optional)
  - Play Detail1 on event_player_1 (e.g., "breakout")
  - Play Detail2 on event_player_1 (optional)
- **Suggested Event** - What to create:
  - Event type (e.g., "Save")
  - Detail1 (e.g., "Save_Played")
  - Detail2 (optional)
- **Player Mapping** - How to map players:
  - Example: `event_team_player_1` → `opp_team_player_1` (for Shot→Save)
- **Options**:
  - Copy XY data (puck and all players)
  - Copy zone

### Default Templates

The tracker comes with three default templates:

1. **Shot On Net → Save**
   - Trigger: Shot with detail1 "OnNetSaved"
   - Suggested: Save event
   - Player mapping: event_player_1 (shooter) → opp_player_1 (goalie)
   - Copies XY and zone, swaps teams

2. **Pass Breakout → Zone Exit**
   - Trigger: Pass with play_detail_1 "breakout"
   - Suggested: Zone Entry/Exit with detail1 "Zone_Exit", detail2 "ZoneExit-Rush"
   - Copies XY and zone

3. **Pass Intercepted → Turnover Giveaway**
   - Trigger: Pass with detail1 "Intercepted"
   - Suggested: Turnover with detail1 "Turnover_Giveaway", detail2 "Giveaway-PassIntercepted"
   - Copies XY and zone

### Auto-Suggestion

After logging an event, if a template matches:
1. A suggestion modal appears showing the suggested next event
2. Click **"✓ Accept"** to create the suggested event
3. Click **"✕ Deny"** to dismiss

### Auto-Create (Log & Next)

In the confirmation modal, use **"✓ Log & Next"** button (or `Ctrl+L` / `Cmd+L`):
1. Logs the current event
2. Automatically checks templates
3. If a match is found, automatically creates the next linked event
4. Pre-populates all fields from template
5. Links the events together

**Example Workflow:**
1. Create a Shot event with detail1 "OnNetSaved"
2. Press `Enter` to open confirmation modal
3. Press `Ctrl+L` (or click "Log & Next")
4. Shot is logged and Save event is automatically created with:
   - Goalie as opp_player_1
   - All XY data copied
   - Zone copied
   - Team swapped
   - Events linked

---

# 10. Data Management

## Exporting Data

Click **"Export"** button to download Excel file with:
- **Events** sheet - All events with details
- **Shifts** sheet - All shifts with players
- **Video** sheet - Game-level video metadata with period start times
- **xy_detail** sheet (v23.9) - Detailed XY data (all points, raw and standardized)
- **Metadata** sheet - Game information, team names, homeAttacksRightP1 setting

## Importing Data

Click **"Import"** button to load an Excel file:
- Restores events and shifts
- Validates against dim tables (schedule, rosters, event types, etc.)
- **v23.9:** Automatically fixes swapped home/away teams if Excel teams don't match schedule
- **v23.9:** Automatically propagates XY data to all linked events

## Auto-Save

Game data auto-saves to browser localStorage every 30 seconds (configurable in Settings).

Manual save:
- Click **"Quick Save"** button
- Or press hotkey (if configured)

## Backup System

If a save folder is selected in Settings:
- Auto-saves create backups in `bkup/` folder
- Keeps last 10 backups
- Filename format: `benchsight_game_[TEAM]_vs_[TEAM]_[GAME_ID]_[TIMESTAMP].json`

---

# 11. Keyboard Shortcuts

## Event Logging

| Hotkey | Action |
|--------|--------|
| `Enter` | Log event (shows confirmation modal) |
| `Shift+Enter` | Quick log (no confirmation) |
| `Ctrl+L` / `Cmd+L` | (v23.9) Log & auto-create next linked event (in confirm modal) |
| `Escape` | Cancel / Close modals |

## Event Types

| Hotkey | Type |
|--------|------|
| `F` | Faceoff |
| `S` | Shot |
| `P` | Pass |
| `G` | Goal |
| `T` | Turnover |
| `Z` | Zone Entry/Exit |
| `N` | Penalty |
| `X` | Stoppage |
| `O` | Possession |
| `V` | Save |
| `R` | Rebound |
| `D` | Dead Ice |
| `Y` | Play |

## Navigation & Selection

| Hotkey | Action |
|--------|--------|
| `Tab` or `M` | Toggle Puck/Player XY mode |
| `` ` `` | Switch to Puck XY mode |
| `P` | Switch to Puck XY mode |
| `H` / `A` | Set team Home/Away |
| `Shift+S` | Swap Event/Opp Teams |
| `1-6` | Select Event Player 1-6 |
| `Alt+1-6` | Select Opp Player 1-6 |
| `[` / `]` | Cycle prev/next player in XY mode |
| `K` | (v23.9) Quickly link to last event |
| `←` / `→` | Navigate prev/next event when editing |

## Zone & Success

| Hotkey | Zone | Success |
|--------|------|---------|
| `Q` | Offensive | - |
| `W` | Neutral | - |
| `E` | Defensive | - |
| `Y` | - | Success |
| `U` | - | Unsuccess |

## Shifts

| Hotkey | Action |
|--------|--------|
| `L` | Log shift |
| `E` | End shift (set end time) |
| `Q` | Quick line change |

## Other

| Hotkey | Action |
|--------|--------|
| `Backspace` | Undo last XY point |
| `?` | Open help modal |
| `Ctrl+1-9` | Switch video source |

## Video Controls

| Hotkey | Action |
|--------|--------|
| `Space` | Play/Pause |
| `←` / `→` | Seek ±1 second |
| `Shift+←/→` | Seek ±10 seconds |
| `↑` / `↓` | Speed up/down |
| `;` / `'` | Frame back/forward |
| `+` / `-` | Zoom in/out |
| `0` | Reset zoom |

---

# 12. Tips & Best Practices

## Efficient Tracking

### Before the Game
1. Import rosters for both teams
2. Set up line presets
3. Configure period length (18 min for rec)
4. Load video and set period markers
5. **(v23.9)** Set up event chain templates in Settings

### During Tracking
1. **Use hotkeys** - much faster than clicking
2. **Use "Log & Next"** (v23.9) for common sequences (Shot→Save, Pass Breakout→Zone Exit)
3. **Drag for passes/shots** - single gesture creates event
4. **Use chains** for common sequences
5. **Quick log** (`Shift+Enter`) when confident
6. **Press `K`** (v23.9) to quickly link to last event

### Speed Tips
- Keep one hand on keyboard (event types, logging)
- Keep one hand on mouse (XY, players)
- Use `Tab` to toggle XY modes
- Use **📋 Copy Players** for similar events
- For possession events, edit either puck or player XY - they sync automatically
- Use event chain templates to automate common sequences

## Common Workflows

### Tracking a Shot Sequence (v23.9)
1. Pause video at shot
2. Press `S` (Shot)
3. Click quick detail: [OnNet]
4. Drag from shooter to net (or click twice)
5. Press `Enter` to open confirmation modal
6. Press `Ctrl+L` (or click "Log & Next")
7. Shot is logged and Save event is automatically created!

### Tracking a Pass Breakout → Zone Exit (v23.9)
1. Press `P` (Pass)
2. Set play_detail_1 on event_player_1 to "breakout"
3. Add XY positions
4. Press `Enter` → `Ctrl+L`
5. Pass is logged and Zone Exit event is automatically created with same XY!

### Tracking a Possession Event (v23.9)
1. Press `O` (Possession) or `Z` (Zone Entry/Exit) with "Rush" detail
2. Add event_player_1
3. Edit either puck XY or player XY - they sync automatically!
4. Place multiple XY points - all sync bidirectionally

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

## Event Chain Templates Best Practices

### When to Create Templates

Create templates for common event sequences:
- Shot On Net → Save
- Pass Breakout → Zone Exit
- Pass Intercepted → Turnover
- Shot → Rebound → Shot
- Any sequence you track frequently

### Template Trigger Design

**Be specific enough** to avoid false matches:
- Include event type AND detail1
- Use play_detail_1/2 if needed (e.g., "breakout")
- Don't be too general (e.g., "any Pass" might match too often)

**But flexible enough** to match variations:
- Use partial matching (e.g., "OnNet" matches "OnNetSaved", "OnNetGoal")
- Only include detail2 if it's necessary

### Player Mapping Tips

- **Shot→Save**: Map `event_team_player_1` (shooter) → `opp_team_player_1` (goalie)
- **Same team plays**: Keep players as-is (no mapping needed)
- **Team swap scenarios**: Always swap teams in template if needed (e.g., Shot→Save)

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

### Linked events not getting XY (v23.9)
- XY propagates automatically when events are linked
- If XY is missing, check that source event has XY data
- XY propagation runs after logging events and after importing Excel

### Templates not suggesting (v23.9)
- Check Settings → Manage Event Chain Templates to see if templates exist
- Verify trigger conditions match your event (type, detail1, detail2, play_detail)
- Templates only suggest after logging an event, not during creation

---

# Appendix: Data Fields

## Event Fields

| Field | Description | Type |
|-------|-------------|------|
| `game_id` | Game identifier | Integer |
| `period` | Period number (1, 2, 3, OT) | Integer/String |
| `start_time` | Game clock time (MM:SS) | String |
| `end_time` | Event end time (MM:SS) | String |
| `team` | Home/Away | String |
| `type` | Event type (Shot, Goal, Pass, etc.) | String |
| `detail1` | Event detail 1 (e.g., "OnNetSaved") | String |
| `detail2` | Event detail 2 (e.g., "ZoneEntry-Rush") | String |
| `zone` | Off/Neu/Def (o/n/d) | String |
| `success` | Success flag (s/u) | String |
| `strength` | On-ice strength (5v5, 5v4, etc.) | String |
| `linkedEventIdx` | Index of linked event (0-based) | Integer |
| `isHighlight` | Highlight flag | Boolean |
| `videoUrl` | YouTube URL for highlight (v23.9) | String |
| `puckXY` | Array of puck XY positions | Array |
| `netXY` | Net XY position | Object |
| `players` | Array of player objects with XY | Array |

## Player Object Fields

| Field | Description | Type |
|-------|-------------|------|
| `num` | Jersey number | Integer |
| `name` | Player name | String |
| `team` | Home/Away | String |
| `role` | Role (event_team_player_1, opp_team_player_1, etc.) | String |
| `roleNum` | Role number (1, 2, 3, etc.) | Integer |
| `xy` | Array of player XY positions | Array |
| `playD1` | Play detail 1 | String |
| `playD2` | Play detail 2 | String |
| `playSuccess` | Play success (s/u) | String |
| `pressure` | Pressured by (player number) | Integer |
| `sideOfPuck` | Side of puck (Offensive/Defensive) | String |

## XY Position Object

| Field | Description | Type |
|-------|-------------|------|
| `x` | X coordinate (-100 to +100, center-relative) | Number |
| `y` | Y coordinate (-42.5 to +42.5, center-relative) | Number |
| `seq` | Sequence number (1-10) | Integer |

---

# Version History

## v23.9 (Current)

### New Features
- **Event Chain Templates** - Define auto-suggestions for next events
- **"Log & Next" Button** - Auto-create next linked event from templates (Ctrl+L hotkey)
- **XY Auto-Sync** - Puck and event_player_1 XY sync bidirectionally for possession events
- **Quick Link Hotkey** - Press `K` to quickly link to last event
- **Auto XY Propagation** - XY data automatically propagates to all linked events
- **Excel Import Team Auto-Correction** - Automatically fixes swapped home/away teams
- **Video Link Fallback** - Highlight videos auto-use main YouTube link with start time if no specific URL
- **Giveaway Types Fix** - All giveaway types now appear in event_details_2 dropdown

### Improvements
- Enhanced linked event XY propagation to include all players, not just puck
- Improved giveaway type filtering to merge Supabase and fallback options
- Better template matching with support for partial matches and play_detail conditions

## v23.5

See previous version for v23.5 features.

---

*Last updated: v23.9*
