# BenchSight Complete System Guide
## From Setup to Wix-Embedded Dashboard

**Version:** 1.0  
**Last Updated:** December 2025  
**Author:** BenchSight Team

---

# Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture & Data Flow](#2-architecture--data-flow)
3. [Complete File Structure](#3-complete-file-structure)
4. [Quick Start Guide](#4-quick-start-guide)
5. [Detailed Component Guide](#5-detailed-component-guide)
6. [Data Schema Reference](#6-data-schema-reference)
7. [Code Documentation](#7-code-documentation)
8. [Step-by-Step: Tracking a Game](#8-step-by-step-tracking-a-game)
9. [Step-by-Step: Running the ETL](#9-step-by-step-running-the-etl)
10. [Step-by-Step: Deploying to Wix](#10-step-by-step-deploying-to-wix)
11. [Troubleshooting](#11-troubleshooting)
12. [Advanced Configuration](#12-advanced-configuration)

---

# 1. System Overview

## What is BenchSight?

BenchSight is a complete hockey analytics system designed for beer league and amateur hockey. It transforms manual game tracking into NHL-style advanced statistics.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BENCHSIGHT SYSTEM                               │
│                                                                         │
│  "Moneyball for Beer League Hockey"                                     │
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │   TRACK     │───►│  PROCESS    │───►│  VISUALIZE  │                 │
│  │   Games     │    │  Data       │    │  Stats      │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│                                                                         │
│  Components:                                                            │
│  • HTML Tracker (manual event/shift logging)                           │
│  • Python ETL Pipeline (data transformation)                           │
│  • Flask Admin Portal (unified control panel)                          │
│  • Static Dashboards (Wix-embeddable HTML)                             │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Features

| Feature | Description |
|---------|-------------|
| **Game Tracker** | Browser-based tool for logging events, shifts, and XY coordinates |
| **Auto-Save** | Tracker saves to localStorage every 30 seconds |
| **Excel Import/Export** | Import from existing tracking files, export to Excel |
| **ETL Pipeline** | Python-based data transformation with SQL logic |
| **80+ Stats** | Goals, Assists, Corsi, Fenwick, Zone Entries, and more |
| **Rating-Aware** | Stats adjusted for player skill ratings (2-6 scale) |
| **Wix Integration** | Static HTML dashboards that embed anywhere |

## Current Data

| Metric | Count |
|--------|-------|
| Players in Database | 335 |
| Teams | 26 |
| Games in Schedule | 552 |
| Games Tracked | 8 |
| Total Events Logged | 24,089 |
| Total Shifts Logged | 770 |

---

# 2. Architecture & Data Flow

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  ┌───────────────────┐                                                  │
│  │  DATA SOURCES     │                                                  │
│  ├───────────────────┤                                                  │
│  │ • BLB_Tables.xlsx │──┐                                               │
│  │   (Master Data)   │  │                                               │
│  │ • Game Tracking   │  │                                               │
│  │   Excel Files     │──┼──────────────────────────────────────────┐    │
│  │ • Video Files     │  │                                          │    │
│  │   (YouTube)       │──┘                                          │    │
│  └───────────────────┘                                             │    │
│                                                                    ▼    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      ETL PIPELINE                                │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                  │   │
│  │  ┌──────────┐    ┌──────────────┐    ┌──────────────┐           │   │
│  │  │  STAGE   │───►│ INTERMEDIATE │───►│   DATAMART   │           │   │
│  │  │  stg_*   │    │    int_*     │    │  dim_/fact_  │           │   │
│  │  └──────────┘    └──────────────┘    └──────────────┘           │   │
│  │                                                                  │   │
│  │  • Load raw      • Transform       • Build final                │   │
│  │  • Validate      • Enrich          • Calculate stats            │   │
│  │  • Stage         • Join            • Export CSVs                │   │
│  │                                                                  │   │
│  └────────────────────────────────────┬────────────────────────────┘   │
│                                       │                                 │
│                                       ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      OUTPUT LAYER                                │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │   │
│  │  │  CSV Files   │  │   PostgreSQL │  │   Power BI   │           │   │
│  │  │  data/output │  │   (optional) │  │  (optional)  │           │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │   │
│  │         │                                                        │   │
│  │         ▼                                                        │   │
│  │  ┌──────────────────────────────────────────────────────┐       │   │
│  │  │              VISUALIZATION LAYER                      │       │   │
│  │  ├──────────────────────────────────────────────────────┤       │   │
│  │  │  • Static HTML Dashboards (Wix-embeddable)           │       │   │
│  │  │  • Flask Admin Portal (local use)                    │       │   │
│  │  │  • Power BI Reports (optional)                       │       │   │
│  │  └──────────────────────────────────────────────────────┘       │   │
│  │                                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
                    ┌─────────────────────────────────────┐
                    │         USER ACTIONS                │
                    └─────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐          ┌───────────────┐
│ 1. UPLOAD     │         │ 2. TRACK      │          │ 3. RUN ETL    │
│ BLB_Tables    │         │ Game Events   │          │ Pipeline      │
└───────────────┘         └───────────────┘          └───────────────┘
        │                           │                           │
        ▼                           ▼                           │
┌───────────────┐         ┌───────────────┐                     │
│data/          │         │data/raw/games/│                     │
│BLB_Tables.xlsx│         │{game_id}/     │                     │
│               │         │*_tracking.xlsx│                     │
│ • dim_player  │         │               │                     │
│ • dim_team    │         │ • events sheet│                     │
│ • dim_schedule│         │ • shifts sheet│                     │
│ • fact_*      │         │ • roster sheet│                     │
└───────────────┘         └───────────────┘                     │
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │       export_all_data.py            │
                    │   OR  main.py (full ETL)            │
                    └─────────────────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │         data/output/                │
                    │                                     │
                    │   dim_player.csv    (335 rows)      │
                    │   dim_team.csv      (26 rows)       │
                    │   dim_schedule.csv  (552 rows)      │
                    │   fact_events.csv   (24,089 rows)   │
                    │   fact_shifts.csv   (770 rows)      │
                    │   fact_box_score.csv                │
                    │   ... (47 total files)              │
                    └─────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
        ┌───────────────────┐           ┌───────────────────┐
        │  LOCAL VIEWING    │           │  WIX DEPLOYMENT   │
        │                   │           │                   │
        │  • Admin Portal   │           │  • GitHub Pages   │
        │  • HTML Previews  │           │  • Wix iframe     │
        │  • Power BI       │           │  • JSON data      │
        └───────────────────┘           └───────────────────┘
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      COMPONENT INTERACTION MAP                          │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                              ADMIN PORTAL                                │
│                          (admin_portal.py)                               │
│                                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Dashboard │  │BLB Tables│  │ Tracker  │  │   ETL    │  │  Notes   │  │
│  │  /       │  │  /blb    │  │ /tracker │  │  /etl    │  │ /notes   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │             │             │             │         │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────┘
        │             │             │             │             │
        │             │             │             │             │
        ▼             ▼             ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│data/output/  │ │data/         │ │tracker/      │ │export_all_   │
│*.csv         │ │BLB_Tables.   │ │tracker_v16.  │ │data.py       │
│              │ │xlsx          │ │html          │ │main.py       │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │             │             │                     │
        │             │             │                     │
        └─────────────┴─────────────┴─────────────────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │       html/                  │
                    │                              │
                    │  dashboard_static.html       │
                    │  game_summary.html           │
                    │  player_card.html            │
                    │                              │
                    │  ──────► EMBED IN WIX        │
                    └──────────────────────────────┘
```

---

# 3. Complete File Structure

```
benchsight_merged/
│
├── admin_portal.py              # 🖥️  Flask admin interface (run this!)
├── export_all_data.py           # 📤 Direct data export script
├── main.py                      # 🔧 Full ETL pipeline entry point
├── requirements.txt             # 📦 Python dependencies
├── admin_notes.json             # 📝 Notes/request log storage
│
├── html/                        # 🌐 STATIC HTML FOR WIX
│   ├── WIX_DEPLOYMENT_GUIDE.md  #    Deployment instructions
│   ├── COMPLETE_SYSTEM_GUIDE.md #    This file!
│   ├── admin_portal_preview.html#    Admin portal preview
│   ├── dashboard_static.html    #    Main dashboard (embed in Wix)
│   ├── game_summary.html        #    Game view (embed in Wix)
│   ├── player_card.html         #    Player cards (embed in Wix)
│   └── tracker_v16.html         #    Tracker copy
│
├── tracker/                     # 🏒 GAME TRACKER
│   └── tracker_v16.html         #    Main tracker tool
│
├── data/                        # 💾 ALL DATA FILES
│   ├── BLB_Tables.xlsx          #    Master dimension data
│   │
│   ├── raw/games/               #    Game tracking files
│   │   ├── 18955/               #    (CSV only - not tracked)
│   │   ├── 18965/               #    ✅ 3,999 events
│   │   │   └── 18965_tracking.xlsx
│   │   ├── 18969/               #    ✅ 3,596 events
│   │   │   └── 18969_tracking.xlsx
│   │   ├── 18977/               #    ✅ 2,527 events
│   │   │   └── 18977_tracking.xlsx
│   │   ├── 18981/               #    ✅ 2,428 events
│   │   │   └── 18981_tracking.xlsx
│   │   ├── 18987/               #    ✅ 3,084 events
│   │   │   └── 18987_tracking.xlsx
│   │   ├── 18991/               #    ✅ 4,000 events
│   │   │   └── 18991_tracking.xlsx
│   │   ├── 18993/               #    ✅ 456 events
│   │   │   └── _tracking.xlsx
│   │   └── 19032/               #    ✅ 3,999 events
│   │       └── 19032_tracking.xlsx
│   │
│   └── output/                  #    Exported CSV files
│       ├── dim_player.csv       #    335 players
│       ├── dim_team.csv         #    26 teams
│       ├── dim_schedule.csv     #    552 games
│       ├── fact_events_long.csv #    24,089 events (long format)
│       ├── fact_events.csv      #    1,641 events (wide format)
│       ├── fact_shifts.csv      #    770 shifts
│       └── ... (47 files)
│
├── src/                         # 🐍 PYTHON ETL CODE
│   ├── pipeline/
│   │   ├── stage/               #    Stage layer (load raw data)
│   │   ├── intermediate/        #    Intermediate layer (transform)
│   │   └── datamart/            #    Datamart layer (build outputs)
│   ├── database/                #    Database connections
│   ├── ingestion/               #    Data loading utilities
│   └── transformation/          #    Transformation logic
│
├── docs/                        # 📚 DOCUMENTATION
│   ├── MASTER_DOCUMENTATION.md  #    Comprehensive reference
│   ├── INSPIRATION_AND_RESEARCH.md  # Research links
│   └── benchsight_stats_catalog_master_ultimate.csv  # 80+ stats
│
├── checklists/                  # ✅ PROJECT TRACKING
│   └── BenchSight_Master_Checklist.md
│
├── powerbi/                     # 📊 POWER BI RESOURCES
│   ├── DAX_FORMULAS.md
│   └── SCHEMA.md
│
├── dashboard/                   # 📈 LEGACY DASHBOARDS
│   └── app.py                   #    Dash/Plotly dashboard
│
├── backups/                     # 💾 AUTO-SAVE BACKUPS
│   └── (JSON backups go here)
│
└── logs/                        # 📋 LOG FILES
    └── hockey_analytics_*.log
```

---

# 4. Quick Start Guide

## Prerequisites

```bash
# Python 3.8+ required
python --version  # Should show 3.8 or higher

# Install dependencies
pip install flask pandas openpyxl
```

## Option A: Run Admin Portal (Recommended)

```bash
# Navigate to project
cd benchsight_merged

# Start the admin portal
python admin_portal.py

# Open in browser
# http://localhost:5000
```

The admin portal provides:
- **Dashboard**: System overview and stats
- **BLB Tables**: Upload and view master data
- **Tracker**: Embedded game tracker with save/publish
- **ETL**: Run data pipeline
- **Reports**: View and download CSV files
- **Notes**: Personal request log

## Option B: Export Data Directly

```bash
# Export all games
python export_all_data.py

# Export specific games
python export_all_data.py --games 18969,18977

# Custom output directory
python export_all_data.py --output-dir ./my_output
```

## Option C: Open HTML Files Directly

```bash
# Open dashboard in browser
open html/dashboard_static.html

# Open tracker
open html/tracker_v16.html

# Open game summary
open html/game_summary.html
```

---

# 5. Detailed Component Guide

## 5.1 Game Tracker (tracker_v16.html)

The tracker is a standalone HTML file for logging game events.

### Features:
- **Event Logging**: Track shots, passes, faceoffs, zone entries, etc.
- **Shift Tracking**: Log line changes with player assignments
- **XY Coordinates**: Click on rink to record event locations
- **Video Sync**: Link events to video timestamps
- **Keyboard Shortcuts**: Fast entry with hotkeys
- **Auto-Save**: Saves to localStorage every 30 seconds
- **Excel Export**: Export to .xlsx with events and shifts sheets

### Key Functions:

```javascript
// Core state object
const S = {
    gid: null,           // Game ID
    events: [],          // Array of event objects
    shifts: [],          // Array of shift objects
    roster: {},          // Player roster {home: [], away: []}
    hGoals: 0,           // Home score
    aGoals: 0,           // Away score
    // ...
};

// Log an event
function logEvent(type, opts = {}) {
    // Creates event object with:
    // - id: unique identifier
    // - type: event type (Shot, Pass, etc.)
    // - clockS: start time
    // - evtPlayers: players involved
    // - zone: ice zone (OZ, NZ, DZ)
    // - shiftId: associated shift
}

// Log a shift change
function logShift() {
    // Creates shift object with:
    // - id: unique identifier
    // - period: game period
    // - start/end: time range
    // - homeSlots: {F1, F2, F3, D1, D2, G, X}
    // - awaySlots: same structure
}

// Export to Excel
function exportExcel() {
    // Uses SheetJS (XLSX) library
    // Creates workbook with:
    // - events sheet
    // - shifts sheet
    // - game_rosters sheet
}

// Auto-save to localStorage
function autoSave() {
    localStorage.setItem('blb_' + S.gid, JSON.stringify({
        events: S.events,
        shifts: S.shifts,
        // ...
    }));
}

// Export for admin portal integration
window.exportGameData = function() {
    return {
        gid: S.gid,
        events: S.events,
        shifts: S.shifts,
        // ...
    };
};
```

### Keyboard Shortcuts:
| Key | Action |
|-----|--------|
| 1-9 | Log event type |
| Space | Play/pause video |
| S | Log shift |
| E | Edit mode |
| X | Toggle XY mode |

---

## 5.2 Admin Portal (admin_portal.py)

Flask-based web interface for managing the entire system.

### Routes:

```python
# Main pages
@app.route('/')              # Dashboard
@app.route('/blb')           # BLB Tables management
@app.route('/tracker')       # Tracker interface
@app.route('/etl')           # ETL pipeline control
@app.route('/reports')       # View/download reports
@app.route('/notes')         # Notes and request log

# API endpoints
@app.route('/api/etl/<stage>', methods=['POST'])  # Run ETL
@app.route('/api/publish/<game_id>', methods=['POST'])  # Publish game
@app.route('/api/backup', methods=['POST'])  # Save backup

# File operations
@app.route('/blb/upload', methods=['POST'])  # Upload BLB_Tables
@app.route('/download/<filename>')  # Download output file
```

### Key Functions:

```python
def get_game_list():
    """
    Scan data/raw/games/ for game directories.
    Returns list of games with tracking status.
    """
    
def get_output_files():
    """
    List all CSV files in data/output/.
    Returns filename, size, and modification date.
    """
    
def load_notes():
    """
    Load notes from admin_notes.json.
    Notes have: id, category, title, content, time
    """
    
def render_page(content, active='dashboard', **kwargs):
    """
    Render page with NORAD dark theme.
    Uses Jinja2 templates embedded in Python.
    """
```

---

## 5.3 Export Script (export_all_data.py)

Direct data export bypassing the full ETL.

### Key Functions:

```python
def load_blb_tables(blb_path):
    """
    Load all sheets from BLB_Tables.xlsx.
    Returns dict mapping sheet names to DataFrames.
    """

def load_game_tracking(game_dir):
    """
    Load events, shifts, roster from game tracking file.
    Handles various column naming conventions.
    Returns tuple of (events_df, shifts_df, roster_df).
    """

def standardize_events(events_df, game_id):
    """
    Map various column names to standard schema.
    Handles: event_type/Type, team/team_, etc.
    """

def pivot_events_to_wide(events_df):
    """
    Convert long format (one row per player) to
    wide format (one row per event).
    """

def calculate_box_score(events_df, shifts_df):
    """
    Aggregate player statistics from events.
    Calculates: G, A, PTS, SOG, TOI
    """

def run_export(games=None, output_dir=None):
    """
    Main export function.
    1. Load BLB_Tables
    2. Load all game tracking files
    3. Standardize formats
    4. Export to CSV
    """
```

---

## 5.4 Static Dashboards (html/*.html)

Standalone HTML files that work without a server.

### dashboard_static.html
- Main dashboard with stats overview
- Games list with tracking status
- Player leaderboard
- Team standings

### game_summary.html
- ESPN-style game layout
- Score and period breakdown
- Shot chart with XY coordinates
- Box score tables
- Scoring summary

### player_card.html
- NHL Edge-style player card
- Season stats highlights
- Radar chart visualization
- League percentile bars
- Game log table

---

# 6. Data Schema Reference

## Dimension Tables (dim_*)

### dim_player
| Column | Type | Description |
|--------|------|-------------|
| player_id | VARCHAR | Unique ID (P100001) |
| player_full_name | VARCHAR | Legal name |
| display_name | VARCHAR | Roster name |
| primary_position | VARCHAR | FORWARD, DEFENSE, GOALIE |
| skill_rating | INT | 2-6 scale |
| player_hand | VARCHAR | L, R |
| birth_year | INT | Year born |

### dim_team
| Column | Type | Description |
|--------|------|-------------|
| team_id | VARCHAR | Unique ID |
| team_name | VARCHAR | Full name |
| team_abbr | VARCHAR | 3-letter code |
| division | VARCHAR | Division name |
| skill_tier | INT | Team rating |

### dim_schedule
| Column | Type | Description |
|--------|------|-------------|
| game_id | INT | Unique game ID |
| season_id | VARCHAR | Season reference |
| game_date | DATE | Game date |
| game_time | TIME | Start time |
| home_team_id | VARCHAR | Home team |
| away_team_id | VARCHAR | Away team |
| venue_id | VARCHAR | Location |
| home_score | INT | Final score |
| away_score | INT | Final score |

## Fact Tables (fact_*)

### fact_events (wide format)
| Column | Type | Description |
|--------|------|-------------|
| game_id | VARCHAR | Game reference |
| event_index | INT | Sequence number |
| event_type | VARCHAR | Shot, Pass, Faceoff, etc. |
| period | INT | 1, 2, 3, OT |
| zone | VARCHAR | OZ, NZ, DZ |
| team | VARCHAR | home, away |
| success | INT | 1 = successful |
| detail_1 | VARCHAR | Primary detail |
| detail_2 | VARCHAR | Secondary detail |
| evt_1_number | INT | Primary player |
| evt_2_number | INT | Secondary player |
| opp_1_number | INT | Opponent player |
| clock_start_seconds | INT | Time in seconds |
| video_time | FLOAT | Video timestamp |

### fact_events_long (long format)
Same as above but with:
| Column | Type | Description |
|--------|------|-------------|
| player_number | INT | Jersey number |
| player_role | VARCHAR | evt_1, evt_2, opp_1, etc. |

### fact_shifts
| Column | Type | Description |
|--------|------|-------------|
| game_id | VARCHAR | Game reference |
| shift_index | INT | Sequence number |
| period | INT | Game period |
| start_seconds | INT | Shift start |
| end_seconds | INT | Shift end |
| duration_seconds | INT | Shift length |
| start_type | VARCHAR | faceoff, on-the-fly |
| stop_type | VARCHAR | whistle, change |
| home_f1 | INT | Home forward 1 |
| home_f2 | INT | Home forward 2 |
| home_f3 | INT | Home forward 3 |
| home_d1 | INT | Home defense 1 |
| home_d2 | INT | Home defense 2 |
| home_g | INT | Home goalie |
| away_f1..g | INT | Away players |

### fact_box_score
| Column | Type | Description |
|--------|------|-------------|
| game_id | VARCHAR | Game reference |
| player_number | INT | Jersey number |
| goals | INT | Goals scored |
| assists | INT | Total assists |
| points | INT | G + A |
| shots | INT | Shots on goal |
| toi_seconds | INT | Time on ice |
| plus_minus | INT | +/- rating |

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ dim_player  │       │ dim_team    │       │ dim_schedule│
├─────────────┤       ├─────────────┤       ├─────────────┤
│ player_id   │       │ team_id     │       │ game_id     │
│ display_name│       │ team_name   │       │ game_date   │
│ position    │       │ division    │       │ home_team_id│───┐
│ skill_rating│       │             │       │ away_team_id│───┤
└──────┬──────┘       └──────┬──────┘       └──────┬──────┘   │
       │                     │                     │          │
       │                     └─────────────────────┤          │
       │                                           │          │
       ▼                                           ▼          ▼
┌─────────────────────────────────────────────────────────────┐
│                      fact_events                            │
├─────────────────────────────────────────────────────────────┤
│ game_id, event_index, event_type, player_number, ...        │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                     fact_box_score                          │
├─────────────────────────────────────────────────────────────┤
│ game_id, player_number, goals, assists, points, shots, toi  │
└─────────────────────────────────────────────────────────────┘
```

---

# 7. Code Documentation

## 7.1 Tracker Core Functions

```javascript
/**
 * ==========================================================================
 * EVENT LOGGING
 * ==========================================================================
 */

/**
 * Log a game event to the events array
 * 
 * @param {string} type - Event type (Shot, Pass, Faceoff, etc.)
 * @param {object} opts - Optional parameters
 * @param {boolean} opts.link - Link to previous event
 * @param {string} opts.d1 - Detail 1 (shot type, pass type)
 * @param {string} opts.d2 - Detail 2 (secondary detail)
 * 
 * @example
 * logEvent('Shot', { d1: 'wrist', d2: 'high' });
 * logEvent('Pass', { link: true });
 */
function logEvent(type, opts = {}) {
    // Validate we have a game loaded
    if (!S.gid) {
        alert('Please select a game first');
        return;
    }
    
    // Get current clock time from video or manual entry
    const clock = getClockTime();
    
    // Create event object
    const evt = {
        id: `${S.gid}_${S.evtIdx}`,  // Unique ID
        idx: S.evtIdx++,              // Sequential index
        type: type,                   // Event type
        clockS: clock.start,          // Start time
        clockE: clock.end,            // End time
        period: S.period,             // Current period
        team: S.evtTeam,              // Team (home/away)
        zone: S.evtZone,              // Zone (OZ/NZ/DZ)
        succ: S.evtSuccess,           // Success flag
        d1: opts.d1 || S.evtDetail1,  // Detail 1
        d2: opts.d2 || S.evtDetail2,  // Detail 2
        shiftId: S.currShift?.id,     // Associated shift
        evtPlayers: [...S.evtPlayers],// Event team players
        oppPlayers: [...S.oppPlayers],// Opponent players
        xy: S.evtXY ? {...S.evtXY} : null,  // XY coordinates
        videoTime: getVideoTime(),    // Video timestamp
        linkToId: opts.link ? S.events[S.events.length-1]?.id : null
    };
    
    // Add to events array
    S.events.push(evt);
    
    // Update UI
    updateLists();
    updateBoxScores(evt);
    
    // Auto-save
    autoSave();
}

/**
 * ==========================================================================
 * SHIFT LOGGING
 * ==========================================================================
 */

/**
 * Log a shift change
 * 
 * Captures current on-ice personnel for both teams.
 * Automatically calculates duration from previous shift.
 * 
 * @example
 * // Fill slots first
 * setSlot('home', 'F1', 17);
 * setSlot('home', 'F2', 9);
 * // Then log shift
 * logShift();
 */
function logShift() {
    // Get current time
    const clock = getClockTime();
    
    // Calculate end time of previous shift
    if (S.currShift && S.currShift.end === null) {
        S.currShift.end = clock.start;
    }
    
    // Create new shift object
    const shift = {
        id: `${S.gid}_S${S.shiftIdx}`,
        idx: S.shiftIdx++,
        period: S.period,
        start: clock.start,
        end: null,  // Set when next shift starts
        startType: S.shiftStartType,
        stopType: null,
        homeSlots: {...S.slots.home},
        awaySlots: {...S.slots.away}
    };
    
    // Add to shifts array
    S.shifts.push(shift);
    S.currShift = shift;
    
    // Update UI
    updateLists();
    autoSave();
}

/**
 * ==========================================================================
 * IMPORT/EXPORT
 * ==========================================================================
 */

/**
 * Import data from Excel file
 * 
 * Handles various column naming conventions by using getVal() helper.
 * Imports events, shifts, and roster sheets.
 * 
 * @param {File} file - Excel file to import
 */
function importExcel(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, {type: 'array'});
        
        // Import events sheet
        if (workbook.SheetNames.includes('events')) {
            const eventsSheet = XLSX.utils.sheet_to_json(
                workbook.Sheets['events']
            );
            importEvents(eventsSheet);
        }
        
        // Import shifts sheet
        if (workbook.SheetNames.includes('shifts')) {
            const shiftsSheet = XLSX.utils.sheet_to_json(
                workbook.Sheets['shifts']
            );
            importShifts(shiftsSheet);
        }
        
        // Import roster
        if (workbook.SheetNames.includes('game_rosters')) {
            const rosterSheet = XLSX.utils.sheet_to_json(
                workbook.Sheets['game_rosters']
            );
            importRoster(rosterSheet);
        }
    };
    reader.readAsArrayBuffer(file);
}

/**
 * Get value from row with flexible column name matching
 * 
 * Handles column name variants like:
 * - event_type vs Type vs EVENT_TYPE
 * - team vs team_ vs event_team
 * 
 * @param {object} row - Row object from XLSX
 * @param {string[]} keys - Array of possible column names
 * @returns {*} - Column value or undefined
 * 
 * @example
 * const eventType = getVal(row, ['event_type', 'Type', 'EVENT_TYPE']);
 */
function getVal(row, keys) {
    for (const k of keys) {
        if (row[k] !== undefined && row[k] !== null && row[k] !== '') {
            return row[k];
        }
    }
    return undefined;
}
```

## 7.2 Admin Portal Functions

```python
"""
=============================================================================
ADMIN PORTAL KEY FUNCTIONS
=============================================================================
"""

def get_game_list():
    """
    Scan game directories and return list with tracking info.
    
    Scans data/raw/games/ for directories with numeric names.
    For each game, loads the tracking file and counts events/shifts.
    
    Returns:
        list[dict]: List of game info dicts:
            - id: Game ID (string)
            - home: Home team name
            - away: Away team name
            - events: Number of events tracked
            - shifts: Number of shifts tracked
            - status: 'tracked', 'partial', or 'untracked'
    
    Example:
        >>> games = get_game_list()
        >>> games[0]
        {'id': '18969', 'home': 'Velociraptors', 'away': 'Capitals',
         'events': 3596, 'shifts': 98, 'status': 'tracked'}
    """
    games = []
    
    for game_dir in sorted(RAW_GAMES_DIR.iterdir()):
        # Skip non-directories and non-numeric names
        if not game_dir.is_dir() or not game_dir.name.isdigit():
            continue
        
        game_id = game_dir.name
        
        # Find tracking file
        tracking_file = None
        for f in game_dir.glob('*tracking*.xlsx'):
            if not f.name.startswith('~$'):  # Skip temp files
                tracking_file = f
                break
        
        # Count events and shifts
        events = 0
        shifts = 0
        status = 'untracked'
        
        if tracking_file:
            try:
                xl = pd.ExcelFile(tracking_file)
                if 'events' in xl.sheet_names:
                    events = len(pd.read_excel(xl, 'events'))
                if 'shifts' in xl.sheet_names:
                    shifts = len(pd.read_excel(xl, 'shifts'))
                status = 'tracked' if events > 100 else 'partial'
            except Exception:
                pass
        
        games.append({
            'id': game_id,
            'home': 'Home',  # Could look up from schedule
            'away': 'Away',
            'events': events,
            'shifts': shifts,
            'status': status
        })
    
    return games


def render_page(content, active='dashboard', **kwargs):
    """
    Render an admin portal page with the NORAD theme.
    
    Uses Jinja2 templates embedded as Python strings.
    Injects common variables like current time and game count.
    
    Args:
        content: HTML content string (template)
        active: Active nav item name
        **kwargs: Additional template variables
        
    Returns:
        str: Rendered HTML page
        
    Example:
        >>> html = render_page(DASHBOARD_CONTENT, 'dashboard', 
        ...                    stats={'players': 335})
    """
    from jinja2 import Template
    
    base = Template(BASE_TEMPLATE)
    content_template = Template(content)
    
    rendered_content = content_template.render(**kwargs)
    
    return base.render(
        css=NORAD_CSS,
        content=rendered_content,
        active=active,
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        game_count=get_game_count()
    )
```

## 7.3 Export Script Functions

```python
"""
=============================================================================
EXPORT SCRIPT KEY FUNCTIONS
=============================================================================
"""

def standardize_events(events_df: pd.DataFrame, game_id: str) -> pd.DataFrame:
    """
    Standardize event data from various column naming conventions.
    
    Different tracking files may use different column names:
    - 'event_type' vs 'Type' vs 'EVENT_TYPE'
    - 'team' vs 'team_' vs 'event_team'
    
    This function maps them all to a consistent schema.
    
    Args:
        events_df: Raw events DataFrame from Excel
        game_id: Game identifier to add to all rows
        
    Returns:
        DataFrame with standardized columns:
        - game_id, event_index, event_type, period
        - zone, team, success, detail_1, detail_2
        - shift_index, player_number, player_role
        - video_time, clock_start_seconds, clock_end_seconds
        
    Example:
        >>> raw_df = pd.read_excel('18969_tracking.xlsx', sheet_name='events')
        >>> std_df = standardize_events(raw_df, '18969')
        >>> std_df.columns
        Index(['game_id', 'event_index', 'event_type', ...])
    """
    if events_df is None or len(events_df) == 0:
        return pd.DataFrame()
    
    cv = Config.EVENT_COLUMN_VARIANTS
    
    # Build standardized DataFrame
    std_df = pd.DataFrame()
    std_df['game_id'] = game_id
    
    # Use safe_get to handle missing columns gracefully
    std_df['event_index'] = safe_get(events_df, cv['event_index'])
    std_df['event_type'] = safe_get(events_df, cv['event_type'])
    # ... (more columns)
    
    return std_df


def pivot_events_to_wide(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert long-format events to wide format.
    
    Long format: One row per player per event
        event_index | player_number | player_role
        1           | 17            | evt_1
        1           | 9             | evt_2
        
    Wide format: One row per event
        event_index | evt_1_number | evt_2_number
        1           | 17           | 9
    
    This is more natural for analysis and visualization.
    
    Args:
        events_df: Long-format events DataFrame
        
    Returns:
        Wide-format DataFrame with one row per event
        
    Example:
        >>> long_df = pd.read_csv('fact_events_long.csv')
        >>> wide_df = pivot_events_to_wide(long_df)
        >>> len(wide_df) < len(long_df)  # Fewer rows
        True
    """
    # Get unique events (drop player-specific columns)
    group_cols = [c for c in events_df.columns 
                  if c not in ['player_number', 'player_role']]
    events_wide = events_df[group_cols].drop_duplicates()
    
    # Pivot player data
    if 'player_role' in events_df.columns:
        player_pivot = events_df.pivot_table(
            index=['game_id', 'event_index'],
            columns='player_role',
            values='player_number',
            aggfunc='first'
        ).reset_index()
        
        # Merge back
        events_wide = events_wide.merge(
            player_pivot, 
            on=['game_id', 'event_index'], 
            how='left'
        )
    
    return events_wide
```

---

# 8. Step-by-Step: Tracking a Game

## Prerequisites
- Game video (YouTube or local)
- Player roster for both teams
- Game ID from schedule

## Process

### Step 1: Open the Tracker

```bash
# Option A: Through admin portal
python admin_portal.py
# Navigate to /tracker

# Option B: Direct file
open tracker/tracker_v16.html
```

### Step 2: Load Game Data

1. Enter **Game ID** in the header input
2. Load roster:
   - Click "📁 Import" to load from existing file, OR
   - Manually add players in roster picker

### Step 3: Set Up Video

1. Click "Add Video" tab
2. Paste YouTube URL or select local file
3. Video will sync with tracker timeline

### Step 4: Track Events

```
For each event in the game:

1. Fill player slots (click on position, then player button)
   - Home team on left panel
   - Away team on right panel

2. Select event type:
   - Click button OR press keyboard shortcut
   - Event types: Shot, Pass, Faceoff, ZoneEntry, etc.

3. Add details:
   - Detail 1: Shot type, pass type, etc.
   - Detail 2: Secondary detail
   - Success: Check if successful

4. Log event:
   - Press button or Enter
   - Event appears in list below

5. Repeat for all events
```

### Step 5: Track Shifts

```
When players change:

1. Update player slots with new lineup
2. Click "Log Shift" or press Alt+Shift+S
3. Previous shift automatically ends
4. New shift begins with current lineup
```

### Step 6: Save and Export

```
Auto-save: Every 30 seconds to localStorage

Manual save:
1. Click "💾 Save" button
2. Downloads JSON backup

Export Excel:
1. Click "📊 Export Excel"
2. Downloads .xlsx with events and shifts sheets
```

### Step 7: Publish to Data Folder

```
Through admin portal:
1. Click "Publish to Data" button
2. Copies tracking file to data/raw/games/{game_id}/

Manual:
1. Save Excel file as {game_id}_tracking.xlsx
2. Copy to data/raw/games/{game_id}/
```

---

# 9. Step-by-Step: Running the ETL

## Quick Export (Recommended)

```bash
# Navigate to project
cd benchsight_merged

# Export all data
python export_all_data.py

# Check output
ls -la data/output/*.csv
```

## Full ETL Pipeline

```bash
# Run complete pipeline
python main.py --process-all

# Run specific games
python main.py --games 18969,18977

# Run specific stage only
python main.py --stage stage       # Load raw data
python main.py --stage intermediate # Transform
python main.py --stage datamart     # Build outputs
```

## Through Admin Portal

1. Open http://localhost:5000/etl
2. Click "Run Full Pipeline" button
3. Watch log output
4. Check /reports for output files

## Output Verification

```bash
# Check row counts
wc -l data/output/*.csv

# Expected:
# dim_player.csv:     336 rows
# dim_team.csv:       27 rows  
# dim_schedule.csv:   553 rows
# fact_events_long:   24,090 rows
# fact_shifts.csv:    771 rows
```

---

# 10. Step-by-Step: Deploying to Wix

## Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      WIX DEPLOYMENT OPTIONS                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Option A: GitHub Pages (Recommended)                                   │
│  ─────────────────────────────────────                                  │
│  1. Push html/ folder to GitHub                                         │
│  2. Enable GitHub Pages                                                 │
│  3. Embed URL in Wix iframe                                             │
│                                                                         │
│  Option B: Direct HTML Embed                                            │
│  ─────────────────────────────────                                      │
│  1. Copy HTML code into Wix HTML element                                │
│  2. Works for smaller dashboards                                        │
│                                                                         │
│  Option C: Wix Velo + API                                               │
│  ─────────────────────────────────                                      │
│  1. Host Flask API on Render.com                                        │
│  2. Use Wix Velo to fetch data                                          │
│  3. Build dynamic pages with Wix Repeaters                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Option A: GitHub Pages (Detailed)

### Step 1: Create GitHub Repository

```bash
# Create new repo on GitHub
# Name: benchsight-dashboard

# Clone locally
git clone https://github.com/yourusername/benchsight-dashboard.git
cd benchsight-dashboard
```

### Step 2: Copy HTML Files

```bash
# Copy html folder contents
cp -r /path/to/benchsight_merged/html/* .

# Should have:
# - dashboard_static.html
# - game_summary.html
# - player_card.html
# - tracker_v16.html
```

### Step 3: Add Data File (Optional)

```bash
# Export data as JSON
cd /path/to/benchsight_merged
python -c "
import pandas as pd
import json

# Load CSVs
players = pd.read_csv('data/output/dim_player.csv')
games = pd.read_csv('data/output/fact_events.csv')

# Create JSON
data = {
    'stats': {
        'players': len(players),
        'games': 8,
        'events': 24089
    }
}

with open('html/dashboard_data.json', 'w') as f:
    json.dump(data, f)
"

# Copy to repo
cp html/dashboard_data.json /path/to/benchsight-dashboard/
```

### Step 4: Push to GitHub

```bash
cd benchsight-dashboard
git add .
git commit -m "Add BenchSight dashboard files"
git push origin main
```

### Step 5: Enable GitHub Pages

1. Go to repository Settings
2. Scroll to "Pages" section
3. Source: "Deploy from a branch"
4. Branch: main, folder: / (root)
5. Click Save
6. Wait 1-2 minutes
7. Your URL: `https://yourusername.github.io/benchsight-dashboard/`

### Step 6: Embed in Wix

1. Open Wix Editor
2. Add element: "Embed" → "HTML iframe"
3. Click "Enter Code"
4. Paste:
```html
<iframe 
    src="https://yourusername.github.io/benchsight-dashboard/dashboard_static.html" 
    width="100%" 
    height="800px" 
    frameborder="0"
    style="border: none;">
</iframe>
```
5. Adjust size and position
6. Publish Wix site

## Option B: Direct HTML Embed

For smaller pages, copy HTML directly:

1. Open `dashboard_static.html` in text editor
2. Copy entire contents
3. In Wix, add "HTML iframe" element
4. Click "Enter Code"
5. Paste HTML
6. Note: May need to adjust CSS paths

## Option C: Wix Velo + API

### Step 1: Deploy API to Render.com

1. Create account at render.com
2. Connect GitHub repository
3. Create new "Web Service"
4. Settings:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python admin_portal.py`
5. Deploy

### Step 2: Add CORS to Flask

```python
# Add to admin_portal.py
from flask_cors import CORS
CORS(app)

# Or manually:
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
```

### Step 3: Create Wix Backend

```javascript
// backend/dashboardApi.jsw
import { fetch } from 'wix-fetch';

export async function getDashboardData() {
    const response = await fetch(
        'https://your-app.onrender.com/api/dashboard'
    );
    return response.json();
}
```

### Step 4: Create Wix Page

```javascript
// Page code
import { getDashboardData } from 'backend/dashboardApi';

$w.onReady(async function() {
    const data = await getDashboardData();
    
    $w('#statPlayers').text = data.stats.players.toString();
    $w('#statTeams').text = data.stats.teams.toString();
    
    // Populate repeater
    $w('#gamesRepeater').data = data.games;
});
```

---

# 11. Troubleshooting

## Common Issues

### "No tracking file found"
**Cause:** Tracking Excel file not named correctly or in wrong folder.
**Fix:** 
- Rename to `{game_id}_tracking.xlsx`
- Place in `data/raw/games/{game_id}/`

### "Column not found" errors
**Cause:** Column names vary between tracking files.
**Fix:** The export script uses `getVal()` helper to handle variants. Check that your column names match one of the expected variants in `Config.EVENT_COLUMN_VARIANTS`.

### "Module not found" errors
**Cause:** Missing Python dependencies.
**Fix:**
```bash
pip install flask pandas openpyxl
```

### Wix iframe not loading
**Cause:** HTTPS or CORS issues.
**Fix:**
- Ensure hosted URL uses HTTPS
- Check browser console for errors
- Try Wix's built-in HTML component

### Data not updating in dashboard
**Cause:** Cached data or old export.
**Fix:**
1. Re-run export: `python export_all_data.py`
2. Push new files to GitHub
3. Clear browser cache
4. Force refresh: Ctrl+Shift+R

---

# 12. Advanced Configuration

## Custom Column Mappings

Edit `Config.EVENT_COLUMN_VARIANTS` in `export_all_data.py`:

```python
EVENT_COLUMN_VARIANTS = {
    'event_type': [
        'event_type', 
        'Type', 
        'your_custom_column_name'  # Add your variant
    ],
    # ...
}
```

## Adding New Stats

1. Edit `calculate_box_score()` function
2. Add calculation logic
3. Add column to output

```python
def calculate_box_score(events_df, shifts_df):
    # ... existing code ...
    
    # Add new stat
    zone_entries = len(player_events[
        player_events['event_type'] == 'ZoneEntry'
    ])
    
    box_scores.append({
        # ... existing fields ...
        'zone_entries': zone_entries,  # New field
    })
```

## Database Integration

To write to PostgreSQL instead of CSV:

```python
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:pass@host:5432/dbname')

# Replace CSV export with database write
df.to_sql('table_name', engine, if_exists='replace', index=False)
```

---

# Appendix A: Stats Catalog (Selected)

| Stat | Category | Formula |
|------|----------|---------|
| Goals (G) | Core | Count of successful shots |
| Assists (A) | Core | Count of assists on goals |
| Points (PTS) | Core | G + A |
| Corsi For (CF) | Possession | Shots + Missed + Blocked |
| Corsi Against (CA) | Possession | Opponent CF |
| Corsi % (CF%) | Possession | CF / (CF + CA) |
| Zone Entry % | Transition | Successful entries / attempts |
| Points/60 | Rate | PTS * 60 / TOI_minutes |

See `docs/benchsight_stats_catalog_master_ultimate.csv` for full list of 80+ stats.

---

# Appendix B: Keyboard Shortcuts (Tracker)

| Key | Action |
|-----|--------|
| 1 | Shot |
| 2 | Pass |
| 3 | Faceoff |
| 4 | Zone Entry |
| 5 | Zone Exit |
| 6 | Turnover |
| 7 | Block |
| 8 | Hit |
| 9 | Penalty |
| Space | Play/Pause video |
| ← → | Skip 5 seconds |
| S | Log shift |
| E | Edit selected event |
| X | XY coordinate mode |
| Tab | Switch team |
| Esc | Clear selection |

---

*Document Version: 1.0*  
*Last Updated: December 2025*  
*Total Pages: ~50 equivalent*
