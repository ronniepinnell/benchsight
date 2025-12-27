# BenchSight Tracker Documentation

## Overview

The BenchSight Tracker (v17) is a web-based hockey game tracking application that records detailed play-by-play data including events, shifts, and player positions. It integrates with the BLB (Beer League Bible) data system and can be used to capture tracking data that feeds into advanced analytics.

## Key Features

### ✅ Auto-Load Rosters from BLB Tables
- Rosters are loaded from `data/output/games_config.json`
- Generated from BLB_Tables.xlsx using `python src/roster_loader.py`
- Fallback to embedded data if config file unavailable
- Each game includes: home/away rosters, team colors, game date

### ✅ Auto-Save to Backup Folders
- Auto-saves to localStorage every 30 seconds
- Click the save status indicator (💾) to download a JSON backup
- Backups can be saved to game folder: `data/raw/games/{game_id}/bkups/`

### ✅ Load Existing Tracking Data
- Can import from JSON or Excel files
- Excel format matches tracking spreadsheet format
- Detects game ID from filename (e.g., `18969_tracking.xlsx`)

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   BLB_Tables.xlsx                    NORAD Website                  │
│   ├── dim_schedule                   (Accuracy Check Only)           │
│   ├── fact_gameroster       ─────>   noradhockey.com                │
│   └── dim_player                                                     │
│         │                                                            │
│         ▼                                                            │
│   roster_loader.py                                                   │
│         │                                                            │
│         ▼                                                            │
│   games_config.json ─────────────> Tracker v17                      │
│                                         │                            │
│                                         ▼                            │
│                               tracking_data.json                     │
│                                    (Events + Shifts)                 │
│                                         │                            │
│                                         ▼                            │
│                               Game Folder Backups                    │
│                               data/raw/games/{gid}/bkups/            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## File Structure

```
benchsight_merged/
├── data/
│   ├── BLB_Tables.xlsx           # Primary data source
│   ├── output/
│   │   └── games_config.json     # Generated game configs
│   └── raw/
│       └── games/
│           ├── 18969/
│           │   ├── roster.json       # Game roster
│           │   ├── tracking_current.json  # Current tracking state
│           │   ├── bkups/            # Backup files
│           │   ├── events/           # Event CSV/JSON exports
│           │   ├── shots/            # Shot location data
│           │   └── xy/               # Coordinate data
│           └── [other games...]
├── src/
│   ├── roster_loader.py          # Generate game configs
│   ├── norad_verifier.py         # Verify against NORAD
│   └── tracker_backend.py        # Backend server (optional)
├── tracker/
│   ├── tracker_v16.html          # Previous version
│   └── tracker_v17.html          # Current version
└── html/
    └── tracker_v17.html          # Deployed version
```

## Usage

### 1. Generate Game Configs

Run the roster loader to generate game configurations from BLB tables:

```bash
# Generate all current season games
python src/roster_loader.py

# Generate specific game
python src/roster_loader.py --game 18969

# Generate specific season
python src/roster_loader.py --season 20252026
```

This creates:
- `data/output/games_config.json` - Combined config for all games
- `data/raw/games/{gid}/roster.json` - Individual game roster files

### 2. Open Tracker

Open `html/tracker_v17.html` in a browser. If running locally, you may need to serve the files:

```bash
# Simple Python server
cd benchsight_merged
python -m http.server 8080

# Then open: http://localhost:8080/html/tracker_v17.html
```

### 3. Track a Game

1. **Select Game**: Use the dropdown to select a game. Rosters auto-load.
2. **Set Up Shift**: Click position slots (F1, F2, D1, etc.) and assign players
3. **Log Shift**: Click "LOG SHIFT" or press Alt+Shift+S
4. **Track Events**: Use event buttons (Shot, Pass, Goal, etc.) or keyboard shortcuts
5. **Mark Locations**: Click on rink to mark puck positions
6. **Save**: Auto-saves every 30 seconds. Click 💾 to download backup.

### 4. Export Data

- **JSON Export**: File > Export JSON
- **CSV Export**: File > Export Events CSV / Shifts CSV  
- **Excel Export**: File > Export Excel (includes all sheets)

### 5. Import Data

- **Import JSON**: File > Import JSON
- **Import Excel**: File > Import Excel (matches tracking spreadsheet format)

## Keyboard Shortcuts

### Event Types
| Key | Event |
|-----|-------|
| S | Shot |
| P | Pass |
| F | Faceoff |
| G | Goal |
| Z | Zone Entry/Exit |
| T | Turnover |
| O | Possession |
| V | Save |
| D | Dead Ice |
| X | Stoppage |
| R | Rebound |
| N | Penalty |

### Controls
| Key | Action |
|-----|--------|
| H | Select Home team |
| A | Select Away team |
| Tab | Toggle team |
| 1-9 | Select player (in shift) |
| Ctrl+1-9 | Select opponent player |
| Enter | Log event |
| Escape | Clear/Cancel |
| [ ] | Adjust clock |
| Space | Play/Pause video |
| , . | Frame step |
| Alt+Shift+S | Log shift |

### Puck Position Modes
| Key | Mode |
|-----|------|
| ` | Puck mode |
| Q | XY Slot 1 |
| W | XY Slot 2 |
| E | XY Slot 3 |

## Event Data Model

### Event Object
```javascript
{
  id: "E18969-001",          // Unique event ID
  idx: 1,                     // Event index
  gid: 18969,                 // Game ID
  period: "1",                // Period (1, 2, 3, OT)
  shiftIdx: 1,                // Parent shift index
  shiftId: "SH18969-001",     // Parent shift ID
  team: "home",               // Team (home/away)
  type: "Shot",               // Event type
  d1: "Shot_OnNetSaved",      // Detail 1
  d2: "Wrist",                // Detail 2
  succ: true,                 // Success (true/false/null)
  zone: "o",                  // Zone (o=offensive, n=neutral, d=defensive)
  clockS: "15:32",            // Clock start
  clockE: "15:30",            // Clock end
  vidTime: 125.5,             // Video timestamp (seconds)
  puck: [{x: 50, y: 20}],     // Puck positions
  evtPlayers: [{              // Event players
    n: "45",
    role: "evt_1",
    pd1: "AttemptedShot",
    pd2: ""
  }],
  oppPlayers: [{              // Opponent players
    n: "22",
    role: "opp_1",
    pd1: "BlockedShot",
    pd2: ""
  }],
  linkToId: null              // Linked event ID (for shot-save pairs)
}
```

### Shift Object
```javascript
{
  id: "SH18969-001",          // Unique shift ID
  idx: 1,                     // Shift index
  gid: 18969,                 // Game ID
  period: "1",                // Period
  start: "18:00",             // Shift start time
  end: "17:15",               // Shift end time
  startType: "PeriodStart",   // How shift started
  stopType: "Goalie_H",       // Why shift ended
  vidTime: 0,                 // Video timestamp
  strength: "5v5",            // Situation
  homeSlots: {                // Home players on ice
    F1: "12", F2: "21", F3: "34",
    D1: "3", D2: "45",
    G: "99", X: ""
  },
  awaySlots: {                // Away players on ice
    F1: "42", F2: "49", F3: "70",
    D1: "9", D2: "52",
    G: "39", X: ""
  }
}
```

## NORAD Verification

The NORAD website (noradhockey.com) is used as an accuracy check, NOT a primary data source. All roster and schedule data comes from BLB_Tables.xlsx.

Run verification:
```bash
# Full check
python src/norad_verifier.py --check

# Standings only
python src/norad_verifier.py --standings

# Export report
python src/norad_verifier.py --export data/output/verification_report.json
```

## Troubleshooting

### Games not loading
1. Check that `data/output/games_config.json` exists
2. Run `python src/roster_loader.py` to regenerate
3. Check browser console for errors

### Rosters empty
1. Verify game exists in `dim_schedule` 
2. Verify roster data in `fact_gameroster`
3. Run roster_loader.py for specific game

### Data not saving
1. Check browser localStorage is enabled
2. Click 💾 to manually download backup
3. Check browser console for errors

### Import failing
1. Check file format matches expected schema
2. For Excel: ensure sheet names are "Events" and "Shifts"
3. Check console for detailed error messages

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v17 | 2025-12-27 | Auto-load from games_config.json, enhanced backup system |
| v16 | 2025-12-20 | Excel import/export, admin portal integration |
| v15 | 2025-12-19 | Video sync, keyboard shortcuts |
| v14 | 2025-12-15 | Player cards, XY tracking |

## Related Documentation

- [BLB Datamart Overview](./BLB_Datamart_Overview.md)
- [Complete Schema](./COMPLETE_SCHEMA.md)
- [Advanced Stats](./ADVANCED_STATS.md)
- [Project Guide](./PROJECT_GUIDE.md)
