# Hockey Analytics Pipeline - Complete Guide

**Version:** 2.0  
**Last Updated:** December 2024

---

## Table of Contents

1. [What This System Does (Plain English)](#1-what-this-system-does-plain-english)
2. [The Big Picture - System Architecture](#2-the-big-picture---system-architecture)
3. [Data Flow - How Data Moves Through the System](#3-data-flow---how-data-moves-through-the-system)
4. [File & Folder Structure](#4-file--folder-structure)
5. [Running the System - User Controls](#5-running-the-system---user-controls)
6. [Two Types of Games](#6-two-types-of-games)
7. [How Each Component Works](#7-how-each-component-works)
8. [Key Concepts Explained](#8-key-concepts-explained)
9. [Output Tables Reference](#9-output-tables-reference)
10. [Power BI Integration](#10-power-bi-integration)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. What This System Does (Plain English)

### The Problem
You have hockey game data in different formats:
- **Detailed tracking data** you manually create (every pass, shot, turnover)
- **Basic league stats** from the BLB system (just goals, assists, etc.)
- **XY coordinates** from shot plotters showing WHERE things happened

You need to:
1. Combine all this data into one place
2. Calculate advanced statistics
3. Analyze it in Power BI

### The Solution
This pipeline:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  YOUR RAW DATA  │ ──▶ │  THIS PIPELINE  │ ──▶ │  POWER BI       │
│                 │     │                 │     │                 │
│  • Excel files  │     │  • Cleans       │     │  • Dashboards   │
│  • CSV files    │     │  • Calculates   │     │  • Reports      │
│  • BLB tables   │     │  • Combines     │     │  • Analysis     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**In simple terms:** You put raw data in, run the pipeline, get organized data out.

---

## 2. The Big Picture - System Architecture

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     HOCKEY ANALYTICS PIPELINE ARCHITECTURE                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │                           INPUT DATA                                   │  ║
║  │                                                                        │  ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  ║
║  │  │ BLB_Tables   │  │ Game         │  │ XY           │  │ Shot       │ │  ║
║  │  │ .xlsx        │  │ Tracking     │  │ Coordinates  │  │ Locations  │ │  ║
║  │  │              │  │ .xlsx        │  │ .csv files   │  │ .csv files │ │  ║
║  │  │ 14 tables:   │  │              │  │              │  │            │ │  ║
║  │  │ • Players    │  │ • events     │  │ Multiple     │  │ Where on   │ │  ║
║  │  │ • Teams      │  │   sheet      │  │ files per    │  │ the net    │ │  ║
║  │  │ • Schedule   │  │ • shifts     │  │ game, all    │  │ shots hit  │ │  ║
║  │  │ • Rosters    │  │   sheet      │  │ combined     │  │            │ │  ║
║  │  │ • etc.       │  │              │  │              │  │            │ │  ║
║  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │  ║
║  └─────────┼─────────────────┼─────────────────┼────────────────┼────────┘  ║
║            │                 │                 │                │            ║
║            ▼                 ▼                 ▼                ▼            ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │                        INGESTION LAYER                                 │  ║
║  │                                                                        │  ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐ │  ║
║  │  │ BLB Loader   │  │ Game Loader  │  │ XY Loader                    │ │  ║
║  │  │              │  │              │  │                              │ │  ║
║  │  │ Loads all 14 │  │ Finds and    │  │ Scans subfolders for ALL     │ │  ║
║  │  │ BLB sheets   │  │ loads the    │  │ CSV files, appends them      │ │  ║
║  │  │ exactly as   │  │ tracking     │  │ together into one DataFrame  │ │  ║
║  │  │ they are     │  │ Excel file   │  │                              │ │  ║
║  │  └──────────────┘  └──────────────┘  └──────────────────────────────┘ │  ║
║  │                                                                        │  ║
║  └────────────────────────────────────────────────────────────────────────┘  ║
║                                      │                                       ║
║                                      ▼                                       ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │                     TRANSFORMATION LAYER                               │  ║
║  │                                                                        │  ║
║  │  ┌─────────────────────────────────────────────────────────────────┐  │  ║
║  │  │                     Data Transformer                             │  │  ║
║  │  │                                                                  │  │  ║
║  │  │  STEP 1: Clean Data                                              │  │  ║
║  │  │  • Remove duplicate columns (ending with _)                      │  │  ║
║  │  │  • Handle missing values                                         │  │  ║
║  │  │  • Convert data types                                            │  │  ║
║  │  │                                                                  │  │  ║
║  │  │  STEP 2: Create Composite Keys                                   │  │  ║
║  │  │  • event_key = "18969_1" (game_id + event_index)                 │  │  ║
║  │  │  • Allows multiple games in same table                           │  │  ║
║  │  │                                                                  │  │  ║
║  │  │  STEP 3: Enrich with Skill Ratings                               │  │  ║
║  │  │  • Look up each player's skill rating                            │  │  ║
║  │  │  • Calculate team averages                                       │  │  ║
║  │  │  • Calculate skill differentials                                 │  │  ║
║  │  │                                                                  │  │  ║
║  │  │  STEP 4: Calculate Advanced Stats                                │  │  ║
║  │  │  • Shots, passes, turnovers per player                           │  │  ║
║  │  │  • Micro-stats (stick checks, dekes, etc.)                       │  │  ║
║  │  │  • ML features (prev/next event, goal proximity)                 │  │  ║
║  │  │                                                                  │  │  ║
║  │  │  STEP 5: Deduplicate Linked Events                               │  │  ║
║  │  │  • Don't double-count play_details on linked events              │  │  ║
║  │  │                                                                  │  │  ║
║  │  │  STEP 6: Build Box Score                                         │  │  ║
║  │  │  • 64 columns of stats per player                                │  │  ║
║  │  │                                                                  │  │  ║
║  │  └─────────────────────────────────────────────────────────────────┘  │  ║
║  │                                                                        │  ║
║  └────────────────────────────────────────────────────────────────────────┘  ║
║                                      │                                       ║
║                                      ▼                                       ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │                        OUTPUT LAYER                                    │  ║
║  │                                                                        │  ║
║  │  ┌─────────────────────────────────────────────────────────────────┐  │  ║
║  │  │                     CSV Exporter                                 │  │  ║
║  │  │                                                                  │  │  ║
║  │  │  BLB Tables (14)        → OVERWRITE each time (master data)     │  │  ║
║  │  │  Dimension Tables (15)  → OVERWRITE each time (static lookups)  │  │  ║
║  │  │  Game Tables (9)        → APPEND new games (accumulates data)   │  │  ║
║  │  │                                                                  │  │  ║
║  │  │  Append Logic:                                                   │  │  ║
║  │  │  1. Load existing CSV (if exists)                                │  │  ║
║  │  │  2. Add new game data                                            │  │  ║
║  │  │  3. Remove duplicates (by primary key, keep newest)              │  │  ║
║  │  │  4. Save combined file                                           │  │  ║
║  │  │                                                                  │  │  ║
║  │  └─────────────────────────────────────────────────────────────────┘  │  ║
║  │                                                                        │  ║
║  └────────────────────────────────────────────────────────────────────────┘  ║
║                                      │                                       ║
║                                      ▼                                       ║
║  ┌────────────────────────────────────────────────────────────────────────┐  ║
║  │                         DATA MART (38 CSV FILES)                       │  ║
║  │                                                                        │  ║
║  │  Import these into Power BI for analysis                               │  ║
║  │                                                                        │  ║
║  └────────────────────────────────────────────────────────────────────────┘  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 3. Data Flow - How Data Moves Through the System

### Processing a Manually Tracked Game

```
START: User runs pipeline and selects "Process Tracked Game"
   │
   │  User enters: game_id = 18969
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: FIND THE TRACKING FILE                                  │
│                                                                 │
│ System looks for:                                               │
│   data/raw/games/18969/18969_tracking.xlsx                      │
│                                                                 │
│ If not found → ERROR, suggest using league stats mode           │
│ If found → Continue to Step 2                                   │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: LOAD RAW DATA                                           │
│                                                                 │
│ From tracking file:                                             │
│   • events sheet → 3,596 rows (one per player per event)        │
│   • shifts sheet → 98 rows (one per shift)                      │
│                                                                 │
│ From BLB_Tables.xlsx:                                           │
│   • fact_gameroster → Get roster for game 18969 (27 players)    │
│   • dim_player → Get skill ratings for each player              │
│                                                                 │
│ From XY folders (if they exist):                                │
│   • xy/event_locations/*.csv → Event coordinates                │
│   • shots/shot_locations/*.csv → Shot net locations             │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: TRANSFORM EVENTS                                        │
│                                                                 │
│ Raw events (3,596 rows) contain duplicate info because each     │
│ event has multiple players involved. Transform to:              │
│                                                                 │
│ fact_events_tracking (1,595 rows)                               │
│   • One row per unique event                                    │
│   • Added: event_key, shift_key, skill ratings                  │
│   • Added: ML features (prev_event, next_event, etc.)           │
│                                                                 │
│ fact_event_players_tracking (3,139 rows)                        │
│   • One row per player per event (bridge table)                 │
│   • Links events to players                                     │
│   • Contains play_detail1, play_detail_2                        │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: TRANSFORM SHIFTS                                        │
│                                                                 │
│ fact_shifts_tracking (98 rows)                                  │
│   • Added: shift_key, skill averages                            │
│   • Added: per-shift event counts (shots, passes, etc.)         │
│                                                                 │
│ fact_shift_players_tracking (1,286 rows)                        │
│   • One row per player per shift (bridge table)                 │
│   • Links shifts to players                                     │
│   • Contains plus_minus for each player-shift                   │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: BUILD BOX SCORE                                         │
│                                                                 │
│ fact_box_score_tracking (27 rows × 64 columns)                  │
│   • One row per player in the game                              │
│   • Scoring: goals, assists, points                             │
│   • Shooting: shots, shots_on_goal, shooting_%                  │
│   • Passing: passes, pass_completion_%                          │
│   • Defense: takeaways, giveaways, blocked_shots               │
│   • Micro-stats: stick_checks, dekes, zone_entries             │
│   • Rates: goals_per_60, assists_per_60, etc.                   │
│                                                                 │
│ IMPORTANT: Linked events are deduplicated!                      │
│   If a "PassIntercepted" play_detail appears on both the        │
│   Pass event AND the Turnover event (linked), it only counts    │
│   as 1, not 2.                                                  │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: SAVE TO DATA MART                                       │
│                                                                 │
│ CSV files are APPENDED (not overwritten):                       │
│                                                                 │
│ Before:                                                         │
│   fact_events_tracking.csv has 0 rows (empty)                   │
│                                                                 │
│ After processing game 18969:                                    │
│   fact_events_tracking.csv has 1,595 rows                       │
│                                                                 │
│ After processing game 19001:                                    │
│   fact_events_tracking.csv has 3,200 rows (both games)          │
│                                                                 │
│ Deduplication ensures no duplicate event_keys                   │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼
END: Data ready for Power BI!
```

### Processing a League-Stats-Only Game

When you don't have a tracking file:

```
START: User selects "Process League Stats Game"
   │
   │  User enters: game_id = 19050
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: CHECK fact_gameroster                                   │
│                                                                 │
│ Look for game_id = 19050 in BLB fact_gameroster                 │
│                                                                 │
│ Found: 24 players with basic stats:                             │
│   • goals, assists                                              │
│   • plus_minus                                                  │
│   • penalty_minutes                                             │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: CREATE SIMPLIFIED BOX SCORE                             │
│                                                                 │
│ fact_box_score_tracking (24 rows × ~15 columns)                 │
│   • Player identity                                             │
│   • goals, assists, points                                      │
│   • plus_minus, penalty_minutes                                 │
│   • skill_rating                                                │
│   • is_tracked = FALSE  ← Important flag!                       │
│                                                                 │
│ NO event-level data (no tracking file)                          │
│ NO shift-level data                                             │
│ NO XY coordinates                                               │
│ NO micro-stats                                                  │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: SAVE TO DATA MART                                       │
│                                                                 │
│ Box score is appended with is_tracked = FALSE                   │
│ This allows filtering in Power BI:                              │
│   • "Show only tracked games" for detailed analysis             │
│   • "Show all games" for season totals                          │
└─────────────────────────────────────────────────────────────────┘
   │
   ▼
END: Limited analysis available (season totals, with/without, etc.)
```

---

## 4. File & Folder Structure

### Complete Project Structure

```
hockey_analytics_project/
│
├── main.py                          # 🚀 RUN THIS FILE!
│
├── config/
│   └── settings.py                  # Configuration (paths, etc.)
│
├── src/
│   ├── ingestion/                   # Loading raw data
│   │   ├── blb_loader.py            # Load BLB_Tables.xlsx
│   │   ├── game_loader.py           # Load tracking files
│   │   └── xy_loader.py             # Load XY coordinate files
│   │
│   ├── transformation/              # Processing data
│   │   ├── data_transformer.py      # Main transformation
│   │   ├── play_detail_counter.py   # Linked event deduplication
│   │   └── league_stats_processor.py # Non-tracked games
│   │
│   ├── models/
│   │   └── dimensions.py            # Dimension table builder
│   │
│   ├── loading/
│   │   └── csv_exporter.py          # Save to CSV with append
│   │
│   └── utils/
│       └── logger.py                # Colored logging
│
├── data/
│   │
│   ├── raw/                         # 📥 INPUT DATA GOES HERE
│   │   │
│   │   ├── BLB_Tables.xlsx          # Master tables (required)
│   │   │
│   │   └── games/                   # One folder per game
│   │       │
│   │       ├── 18969/               # Game 18969 folder
│   │       │   │
│   │       │   ├── 18969_tracking.xlsx    # Required for tracked games
│   │       │   │
│   │       │   ├── xy/                    # XY coordinates (optional)
│   │       │   │   └── event_locations/   # SUBFOLDER with CSVs
│   │       │   │       ├── period1.csv
│   │       │   │       ├── period2.csv
│   │       │   │       └── period3.csv
│   │       │   │
│   │       │   ├── shots/                 # Shot locations (optional)
│   │       │   │   └── shot_locations/    # SUBFOLDER with CSVs
│   │       │   │       ├── period1_shots.csv
│   │       │   │       └── period2_shots.csv
│   │       │   │
│   │       │   └── video/                 # Video links (optional)
│   │       │       └── video_links.csv
│   │       │
│   │       └── 19001/               # Another game...
│   │           └── ...
│   │
│   └── output/                      # 📤 OUTPUT DATA (DATA MART)
│       │
│       ├── dim_player.csv           # BLB master tables (14)
│       ├── dim_team.csv
│       ├── fact_gameroster.csv
│       ├── ...
│       │
│       ├── dim_period.csv           # Dimension tables (15)
│       ├── dim_event_type.csv
│       ├── ...
│       │
│       ├── fact_events_tracking.csv      # Game tables (9)
│       ├── fact_shifts_tracking.csv      # These APPEND across games
│       ├── fact_box_score_tracking.csv
│       └── ...
│
├── docs/                            # 📚 DOCUMENTATION
│   ├── PROJECT_GUIDE.md             # This file
│   ├── DATA_DICTIONARY.md           # Column definitions
│   └── ADVANCED_STATS.md            # Stat calculations
│
├── powerbi/                         # 📊 POWER BI RESOURCES
│   ├── SCHEMA.md                    # Data model relationships
│   ├── DAX_FORMULAS.md              # DAX measures
│   └── VISUALIZATIONS.md            # Dashboard designs
│
└── sql/
    └── ddl/
        └── create_tables.sql        # SQL definitions
```

### XY Coordinate Folder Structure (Detailed)

```
data/raw/games/18969/
│
├── 18969_tracking.xlsx              # Main tracking file
│
├── xy/                              # XY coordinate data
│   │
│   └── event_locations/             # ⚠️ MUST BE A SUBFOLDER
│       │
│       │   The system loads ALL CSV files in this folder
│       │   and combines them into one DataFrame.
│       │
│       │   You can split by period, by event type, or any
│       │   way that makes sense for your workflow.
│       │
│       ├── period1_events.csv
│       ├── period2_events.csv
│       ├── period3_events.csv
│       └── overtime_events.csv      # If applicable
│
├── shots/                           # Shot net location data
│   │
│   └── shot_locations/              # ⚠️ MUST BE A SUBFOLDER
│       │
│       ├── period1_shots.csv
│       ├── period2_shots.csv
│       └── period3_shots.csv
│
└── video/
    └── video_links.csv
```

### Event Location CSV Format

Each CSV in `xy/event_locations/` should have these columns:

```csv
event_index,player_game_number,player_team,event_x1,event_y1,event_x2,event_y2,event_x3,event_y3,puck_start_x,puck_start_y,puck_end_x,puck_end_y
1,45,Platinum,25.5,10.2,45.0,15.3,,,25.5,10.2,45.0,15.3
2,12,Platinum,-30.0,5.5,-10.0,2.0,15.0,8.0,-30.0,5.5,15.0,8.0
3,8,Velodrome,50.0,20.0,,,,,50.0,20.0,,
```

**Column Explanations:**

| Column | Required | Description |
|--------|----------|-------------|
| event_index | ✓ | Links to fact_events_tracking |
| player_game_number | ✓ | Jersey number (links to dim_game_players) |
| player_team | ✓ | Team name (e.g., "Platinum") |
| event_x1 | ✓ | X coordinate where event started |
| event_y1 | ✓ | Y coordinate where event started |
| event_x2 | | X coordinate where event ended (e.g., pass target) |
| event_y2 | | Y coordinate where event ended |
| event_x3 | | Third X coordinate (e.g., deflection point) |
| event_y3 | | Third Y coordinate |
| puck_start_x | | Puck X at event start |
| puck_start_y | | Puck Y at event start |
| puck_end_x | | Puck X at event end |
| puck_end_y | | Puck Y at event end |

---

## 5. Running the System - User Controls

### Starting the Pipeline

```bash
cd hockey_analytics_project
python main.py
```

### Main Menu

```
╔════════════════════════════════════════════════════════════════╗
║           HOCKEY ANALYTICS PIPELINE                            ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║   1. Process Single Game (Manual Tracking)                     ║
║   2. Process Single Game (League Stats Only)                   ║
║   3. Process All Untracked Games                               ║
║   4. View Data Mart Status                                     ║
║   5. Export to Excel                                           ║
║   6. Remove Game from Mart                                     ║
║   7. With/Without Player Analysis                              ║
║   8. Goalie vs Opponents Analysis                              ║
║   9. Exit                                                      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

Enter choice (1-9): _
```

### Option 1: Process Single Game (Manual Tracking)

**Use when:** You have a full tracking file for the game.

**User interaction:**
```
Enter choice: 1
Enter game ID: 18969
Include XY coordinates if available? (y/n): y
```

**What happens:**
1. Finds `data/raw/games/18969/18969_tracking.xlsx`
2. Loads events and shifts
3. Checks for XY files in subfolders (loads ALL CSVs if found)
4. Transforms data, calculates stats
5. Appends to data mart CSVs

**Output:**
```
✓ Loaded tracking file: 18969_tracking.xlsx
    Events: 3596 rows
    Shifts: 98 rows
    XY data: Found (3 files, 1420 rows)
    
Processing...
✓ Transformation complete
    fact_events_tracking: 1595 rows
    fact_box_score_tracking: 27 rows
    
✓ Data mart updated
```

### Option 2: Process Single Game (League Stats Only)

**Use when:** No tracking file exists, but game is in fact_gameroster.

**User interaction:**
```
Enter choice: 2
Enter game ID: 19050
```

**What happens:**
1. Looks up game in `fact_gameroster` table
2. Creates simplified box score with basic stats
3. Marks `is_tracked = False`
4. Appends to data mart

**Output:**
```
ℹ Game: Thunder vs Storm
ℹ Players: 24

✓ Created simplified box score
    fact_box_score_tracking: 24 rows

⚠ Note: Event-level analysis not available for this game
```

### Option 4: View Data Mart Status

Shows current state of all tables:

```
╔═══════════════════════════════════════════════════════════════════╗
║                      DATA MART STATUS                             ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  BLB TABLES (Master Data)                                         ║
║  ────────────────────────────────────────────────────────────────║
║  dim_player              335 rows    28 cols      45 KB           ║
║  dim_team                 26 rows    15 cols       4 KB           ║
║  fact_gameroster      14,239 rows    27 cols     1.2 MB           ║
║  ... (11 more)                                                    ║
║                                                                   ║
║  GAME TRACKING TABLES (Appended)                                  ║
║  ────────────────────────────────────────────────────────────────║
║  fact_events_tracking   1,595 rows   38 cols   Games: [18969]     ║
║  fact_shifts_tracking      98 rows   27 cols   Games: [18969]     ║
║  fact_box_score            27 rows   64 cols   Games: [18969]     ║
║                                                                   ║
║  TOTAL: 38 tables, 19,541 total rows                              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

### Option 6: Remove Game from Mart

**Use when:** Need to reprocess a game or remove bad data.

```
Enter choice: 6
Enter game ID to remove: 18969

✓ fact_events_tracking: Removed 1595 rows
✓ fact_shifts_tracking: Removed 98 rows
✓ fact_box_score_tracking: Removed 27 rows

✓ Total: Removed 1720 rows for game 18969
```

### Option 7: With/Without Player Analysis

**Use for:** See how team performs with vs without a specific player.

```
Enter choice: 7
Enter player_id: 12345
Enter team name: Platinum

Results for Player 12345 on Platinum
──────────────────────────────────────────────────
  Games WITH player:    24
  Goals per game:       3.54
  Games WITHOUT player: 8
  Goals per game:       2.75
  Impact:               +0.79 GF/G
```

### Command Line Options

```bash
# Process specific game directly
python main.py --game 18969

# Process using league stats only
python main.py --game 19050 --league-stats

# View status without interactive menu
python main.py --status
```

---

## 6. Two Types of Games

### Comparison

| Feature | Tracked Game | Non-Tracked Game |
|---------|--------------|------------------|
| **Source** | tracking.xlsx file | fact_gameroster only |
| **Events** | ✓ 1,500+ per game | ✗ None |
| **Shifts** | ✓ Full detail | ✗ None |
| **Box Score** | ✓ 64 columns | ✓ ~15 columns |
| **XY Coordinates** | ○ Optional | ✗ None |
| **Micro-stats** | ✓ Dekes, stick checks, etc. | ✗ None |
| **is_tracked flag** | TRUE | FALSE |

### What You CAN Analyze (Non-Tracked Games)

Even without tracking files, you can analyze:

1. **Season Totals**
   - Goals, assists, points across all games
   - Plus/minus totals

2. **With/Without Analysis**
   - Team performance WITH player in lineup
   - Team performance WITHOUT player
   - Calculate player "impact score"

3. **Goalie vs Opponents**
   - Which teams does the goalie struggle against?
   - Save % by opponent

4. **Lineup Skill Analysis**
   - Average skill rating in lineup
   - Does higher skill = more wins?

5. **Trends Over Time**
   - Points per game rolling average
   - Team performance by month

### What You CANNOT Analyze (Non-Tracked Games)

- Shot maps / heat maps
- Corsi / Fenwick
- Zone entries / exits
- Passing patterns
- Micro-stats (stick checks, dekes, etc.)
- Shift-by-shift analysis
- Line combo performance
- xG (expected goals)

---

## 7. How Each Component Works

### BLB Loader (`src/ingestion/blb_loader.py`)

**Purpose:** Load all 14 tables from BLB_Tables.xlsx

**What it does:**
1. Opens BLB_Tables.xlsx
2. Reads each sheet into a DataFrame
3. Cleans up index columns
4. Returns dictionary of tables

**Tables loaded:**
- dim_player, dim_team, dim_schedule, dim_season, dim_league
- dim_rinkboxcoord, dim_rinkcoordzones, dim_randomnames, dim_playerurlref
- fact_gameroster, fact_leadership, fact_registration, fact_draft, fact_playergames

### Game Loader (`src/ingestion/game_loader.py`)

**Purpose:** Find and load game tracking files

**What it does:**
1. Looks for `{game_id}_tracking.xlsx` in game folder
2. Loads `events` and `shifts` sheets
3. Coordinates with XY Loader for coordinate files

### XY Loader (`src/ingestion/xy_loader.py`)

**Purpose:** Load XY coordinate data from subfolders

**What it does:**
1. Scans `xy/event_locations/` folder
2. Finds ALL CSV files (any name)
3. Loads each CSV
4. Appends them all together
5. Removes duplicates (by event_index)
6. Calculates derived fields (zones, distances, angles)

**Example:**
```
Folder contains:
  xy/event_locations/
    period1.csv (500 rows)
    period2.csv (480 rows)
    period3.csv (440 rows)

Result: Single DataFrame with 1,420 rows
```

### Data Transformer (`src/transformation/data_transformer.py`)

**Purpose:** Transform raw data into star schema format

**Main steps:**
1. Clean data (remove underscore columns)
2. Create composite keys
3. Enrich with skill ratings
4. Calculate ML features
5. Aggregate statistics
6. Build box score

### Play Detail Counter (`src/transformation/play_detail_counter.py`)

**Purpose:** Count play_details without double-counting linked events

**The problem:**
```
Event 100 (Pass):     play_detail1 = "PassIntercepted"
Event 101 (Turnover): play_detail1 = "PassIntercepted"
Both have linked_event_index = 5000

Without dedup: PassIntercepted = 2
With dedup:    PassIntercepted = 1 (correct!)
```

**How it works:**
1. Group events by `linked_event_index`
2. For each player, get DISTINCT play_detail values per chain
3. Count each only once

### League Stats Processor (`src/transformation/league_stats_processor.py`)

**Purpose:** Handle games without tracking files

**What it does:**
1. Load game from fact_gameroster
2. Create simplified box score
3. Set `is_tracked = False`
4. Calculate with/without analysis
5. Calculate goalie vs opponents

---

## 8. Key Concepts Explained

### Composite Keys

**Why they exist:** Allow multiple games in same table

**Format:** `{game_id}_{local_index}`

**Examples:**
```
event_key = "18969_1"      (Game 18969, event 1)
event_key = "18969_2"      (Game 18969, event 2)
event_key = "19001_1"      (Game 19001, event 1) ← Different game, same local index
```

**Tables and their keys:**
| Table | Primary Key |
|-------|-------------|
| fact_events_tracking | event_key |
| fact_shifts_tracking | shift_key |
| fact_box_score_tracking | player_game_key |
| fact_event_players_tracking | event_player_key |
| fact_shift_players_tracking | shift_player_key |

### Linked Events

**What they are:** Multiple events that are part of the same "play"

**Example:** A shot that gets saved:
```
Event 100: Shot (shooter)           linked_event_index = 5000
Event 101: Save (goalie)            linked_event_index = 5000
Event 102: Zone_Exit (defender)     linked_event_index = 5000
```

All three events share the same `linked_event_index`, meaning they're connected.

### is_tracked Flag

**Purpose:** Distinguish between detailed and basic game data

```
is_tracked = TRUE:  Full event-level data available
is_tracked = FALSE: Only basic stats from fact_gameroster
```

**Use in Power BI:**
```dax
// Show only tracked games
DetailedStats = CALCULATE([Goals Per 60], fact_box_score[is_tracked] = TRUE())

// Show all games (season totals)
SeasonGoals = SUM(fact_box_score[goals])
```

### Skill Ratings

**Scale:** 2.0 to 6.0 (4.0 is average)

**Where they're used:**
- Player skill (from dim_player)
- Event team skill average
- Opponent team skill average
- Skill differential (team vs opponent)

---

## 9. Output Tables Reference

### BLB Tables (14) - Master Data

| Table | Rows | Description |
|-------|------|-------------|
| dim_player | 335 | Player master data |
| dim_team | 26 | Team information |
| dim_schedule | 552 | Game schedule |
| dim_season | 9 | Season definitions |
| dim_league | 2 | League info |
| dim_rinkboxcoord | 50 | Rink zone coordinates |
| dim_rinkcoordzones | 297 | Detailed rink zones |
| dim_randomnames | 486 | Anonymized names |
| dim_playerurlref | 543 | Player URLs |
| fact_gameroster | 14,239 | Game rosters + basic stats |
| fact_leadership | 28 | Team captains |
| fact_registration | 191 | Player registrations |
| fact_draft | 160 | Draft picks |
| fact_playergames | 3,010 | Historical player-game stats |

### Dimension Tables (15) - Static Lookups

| Table | Rows | Description |
|-------|------|-------------|
| dim_period | 5 | 1, 2, 3, OT, SO |
| dim_event_type | 19 | Pass, Shot, Turnover, etc. |
| dim_event_detail | 59 | Pass_Completed, Shot_Goal, etc. |
| dim_play_detail | 81 | StickCheck, Deke, etc. |
| dim_shot_type | 8 | Wrist, Slap, Snap, etc. |
| dim_pass_type | 12 | Tape_to_Tape, Saucer, etc. |
| dim_zone | 3 | OZ, NZ, DZ |
| dim_strength | 13 | 5v5, 5v4, 4v5, etc. |
| dim_situation | 5 | even, pp, pk, en, pp_en |
| dim_position | 8 | F, C, LW, RW, D, G |
| dim_player_role | 12 | event_team_player_1, etc. |
| dim_shift_type | 4 | Regular, PP, PK |
| dim_venue | 2 | home, away |
| dim_time_bucket | 4 | 0-5, 5-10, 10-15, 15-20 |
| dim_danger_zone | 3 | HD, MD, LD |

### Game Tables (9) - Append Across Games

| Table | Description | Key |
|-------|-------------|-----|
| fact_events_tracking | All events | event_key |
| fact_event_players_tracking | Player-event links | event_player_key |
| fact_shifts_tracking | All shifts | shift_key |
| fact_shift_players_tracking | Player-shift links | shift_player_key |
| fact_box_score_tracking | Player game stats | player_game_key |
| fact_linked_events_tracking | Shot→Save chains | chain_id |
| fact_sequences_tracking | Possession sequences | sequence_key |
| fact_plays_tracking | Play-level groups | play_key |
| dim_game_players_tracking | Per-game player info | player_game_key |

---

## 10. Power BI Integration

See the `powerbi/` folder for complete documentation:

- **SCHEMA.md** - Data model relationships
- **DAX_FORMULAS.md** - DAX measures for all analysis types
- **VISUALIZATIONS.md** - Dashboard designs (ESPN/NHL Edge style)

### Quick Start

1. Open Power BI Desktop
2. Get Data → Folder → Select `data/output/`
3. Load all CSV files
4. Set up relationships (see SCHEMA.md)
5. Create measures (see DAX_FORMULAS.md)

---

## 11. Troubleshooting

### "No tracking file found"

**Cause:** File doesn't exist or wrong location

**Solution:**
1. Check file exists: `data/raw/games/{game_id}/{game_id}_tracking.xlsx`
2. If no tracking file, use Option 2 (League Stats Only)

### "XY files not loading"

**Cause:** Wrong folder structure

**Wrong:**
```
xy/event_locations.csv  ← File directly in xy folder
```

**Correct:**
```
xy/event_locations/     ← SUBFOLDER
  event_locations.csv   ← Files inside subfolder
```

### "Duplicate rows after processing"

**This is normal!** The append logic:
1. Loads existing + new data
2. Deduplicates by primary key
3. Keeps newest version

If you see the same row count after reprocessing, deduplication worked correctly.

### "Game not found in fact_gameroster"

**Cause:** The game isn't in the BLB system yet

**Solution:**
1. Wait for BLB data to be updated
2. Add the game to fact_gameroster manually
3. Or create a tracking file and use Option 1

---

*End of Project Guide*
