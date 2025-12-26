# BenchSight Hockey Analytics Platform
## Complete Project Status, Triage & Implementation Plan
**Generated: December 26, 2025**

---

# 🎯 EXECUTIVE SUMMARY

BenchSight is an end-to-end hockey analytics platform bringing NHL-level analytics to beer league and junior hockey. The project encompasses:

- **Manual event tracking** via web-based tracker
- **Automated ETL pipeline** (Raw → Stage → Intermediate → Mart)
- **Interactive dashboards** with drill-down capabilities
- **Video integration** with timestamp sync
- **Advanced/micro statistics** (Corsi, Fenwick, xG, possession time, zone entries)
- **Rating-adjusted metrics** for contextual analysis
- **Computer vision foundation** for future automated tracking
- **Commercial-ready architecture** for multi-tenant deployment

### Project Goals
| Timeline | Goal | Status |
|----------|------|--------|
| Near-term | View games for teammates | 🔄 In Progress |
| Mid-term | Resume/portfolio showcase | 🔄 In Progress |
| Long-term | Commercial product | 📋 Planned |

---

# 📊 CURRENT DATA INVENTORY

## Tracked Games (9 Total)

| Game ID | Date | Home Team | Away Team | Score | Events | Shifts | Video Times | Status |
|---------|------|-----------|-----------|-------|--------|--------|-------------|--------|
| 18955 | 2025-08-10 | Velodrome | Orphans | 5-1 | CSV files | Yes | ✅ | Partial tracking |
| 18965 | 2025-08-24 | Velodrome | OS Offices | 2-4 | 3,999 | 98 | ❌ | Full tracking |
| **18969** | **2025-09-07** | **Platinum** | **Velodrome** | **4-3** | 3,596 | 98 | ✅ | **SCORE CORRECTED** |
| 18977 | 2025-09-14 | Velodrome | HollowBrook | 4-2 | 2,527 | 88 | ✅ | Full tracking |
| 18981 | 2025-09-28 | Nelson | Velodrome | 2-1 | 2,428 | 106 | ✅ | Full tracking |
| 18987 | 2025-10-05 | Outlaws | Velodrome | 0-1 | 3,084 | 106 | ✅ | Full tracking |
| 18991 | 2025-10-12 | Triple J | Velodrome | 1-5 | 4,000 | 78 | ✅ | Full tracking |
| 18993 | 2025-10-19 | Ace | Velodrome | 1-2 | 456 | 98 | ❌ | Partial tracking |
| 19032 | TBD | TBD | TBD | TBD | 3,999 | 98 | ✅ | Full tracking |

**Total Events Tracked: ~24,089**
**Total Shifts Tracked: ~868**

## Data Sources

### BenchSight_Tables.xlsx (Master Dimensions)
| Sheet | Records | Key Columns |
|-------|---------|-------------|
| dim_player | 100+ | player_id, player_full_name, current_skill_rating, player_image, random_player_full_name |
| dim_team | 15 | team_id, team_name, team_color1-4, team_logo |
| dim_schedule | 500+ | game_id, date, home/away teams, scores, video_url |
| dim_season | Multiple | season_id, session info |
| dim_dates | 365+ | Full date dimension |
| dim_rinkboxcoord | 12 | XY coordinate zones |
| dim_rinkcoordzones | 14 | Extended zone definitions |
| dim_randomnames | 100+ | Random names for privacy mode |
| fact_gameroster | Per game | Player-game assignments |

### Per-Game Tracking Files
Each game folder contains:
- `{game_id}_tracking.xlsx` - Events and shifts
- `{game_id}_video_times.xlsx` - Video timestamps
- `!info_checklist.xlsx` - Game metadata
- `bkups/` - Backup saves
- `events/` - Event CSVs
- `shifts/` - Shift CSVs
- `shots/` - Shot location CSVs
- `xy/` - Coordinate data

---

# ⚠️ KNOWN ISSUES (To Fix)

## Critical Issues
1. **❌ Game 18969 Score Wrong** - Dashboard shows incorrect score (should be Platinum 4, Velodrome 3)
2. **❌ Faceoff Winner Incorrect** - R.Pinnell listed incorrectly as faceoff winner
3. **❌ Tracker Version** - Shows v14, should be latest (v16+)
4. **❌ Game Selection Broken** - Clicking any game shows only 9/7 game
5. **❌ Filters Not Working** - P1/P2/P3 period filters non-functional
6. **❌ Missing Events** - Play-by-play missing many tracked events

## UI/UX Issues
1. **❌ Team Logos** - Not fully populating from dim_team
2. **❌ Player Images** - Not loading from player_image field
3. **❌ Event/Shift Logs** - Only showing few items, need scrollable full lists
4. **❌ No Drill-Downs** - Clicking stats/events doesn't navigate
5. **❌ No Interactivity** - Cannot filter by clicking event types

## Data Issues
1. **❌ Not All Games Loaded** - Only partial games appearing
2. **❌ Video URLs** - Not loading from video_times files
3. **❌ Sequence/Play Index** - Logic not implemented

---

# 📋 TRIAGE: IMPLEMENTATION PRIORITY

## TIER 1: CRITICAL FIXES (Day 1-2) 🔴

### 1.1 Data Loading & Correction
- [ ] Rename all BLB_* references to BenchSight
- [ ] Load ALL 9 games from Excel tracking files
- [ ] Correct game 18969 score (Platinum 4-3)
- [ ] Fix faceoff winner attribution
- [ ] Load video URLs from video_times files
- [ ] Populate team logos from dim_team
- [ ] Populate player images from dim_player

### 1.2 Dashboard Fixes
- [ ] Fix game selection (load correct game data)
- [ ] Fix period filters (P1/P2/P3)
- [ ] Make event/shift logs scrollable (show ALL)
- [ ] Display all events in play-by-play
- [ ] Load correct team colors

### 1.3 Tracker Update
- [ ] Update version to v16
- [ ] Fix Excel import for actual column formats
- [ ] Support actual tracking file structure

## TIER 2: CORE FUNCTIONALITY (Week 1) 🟡

### 2.1 ETL Pipeline
- [ ] Python extract scripts for tracking files
- [ ] Stage layer transforms
- [ ] Intermediate layer with sequence/play index
- [ ] Mart layer aggregations
- [ ] PostgreSQL schema creation

### 2.2 Interactive Dashboards
- [ ] Click event → detail modal
- [ ] Click shift → shift detail view
- [ ] Click stat → filtered view
- [ ] Click player → player card
- [ ] Click game → game dashboard
- [ ] Event type filter (click to filter)

### 2.3 Admin Portal
- [ ] ETL runner interface
- [ ] Table viewer (stage/intermediate/mart)
- [ ] Schema documentation page
- [ ] Python log viewer
- [ ] Source code browser
- [ ] Download ZIP functionality

## TIER 3: ADVANCED FEATURES (Week 2-3) 🟢

### 3.1 Advanced Statistics
- [ ] Corsi For/Against (CF%, CA%)
- [ ] Fenwick For/Against (FF%, FA%)
- [ ] Possession time (duration-based, not just count)
- [ ] Zone entry/exit success rates
- [ ] Pass completion percentage
- [ ] True giveaways (exclude dumps)
- [ ] Takeaways
- [ ] Shot quality metrics

### 3.2 Rating-Adjusted Metrics
- [ ] Opponent rating context
- [ ] Teammate rating context
- [ ] Quality of competition
- [ ] Rating-weighted Corsi
- [ ] Expected performance vs actual

### 3.3 Video Integration
- [ ] Click goal → video playback (rewind 10s)
- [ ] Play chain video clips
- [ ] Shot type video drill-downs

### 3.4 Player Experience
- [ ] NHL Edge-style player cards
- [ ] Defensive player view (goals against analysis)
- [ ] Privacy mode (random names)
- [ ] Hide player images in privacy mode

## TIER 4: COMMERCIAL PREP (Month 1-3) 🔵

### 4.1 Power BI Integration
- [ ] Export mart tables to CSV
- [ ] DAX measure library
- [ ] Embedded report links in portal

### 4.2 Computer Vision
- [ ] YOLOv8 puck detection setup
- [ ] Rink homography calibration
- [ ] CV-to-manual alignment

### 4.3 User Features
- [ ] User-defined custom stats
- [ ] Stat request system
- [ ] Upload stat definition files

### 4.4 Infrastructure
- [ ] Multi-tenant architecture
- [ ] User authentication
- [ ] NORAD scraping (or API)

---

# 🏗️ TECHNICAL ARCHITECTURE

## Data Flow
```
┌─────────────────────────────────────────────────────────────────┐
│                        RAW LAYER                                │
│  BenchSight_Tables.xlsx  │  Game Tracking Excel  │  Video URLs  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       STAGE LAYER                               │
│  stg_events  │  stg_shifts  │  stg_rosters  │  stg_video       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INTERMEDIATE LAYER                            │
│  int_events_enriched (with sequence/play index)                │
│  int_shifts_enriched (with on-ice players)                     │
│  int_possession_chains                                          │
│  int_player_onice                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        MART LAYER                               │
│  fact_playbyplay  │  fact_shifts  │  fact_player_game_stats    │
│  fact_player_season_stats  │  fact_team_stats  │  fact_video   │
│  dim_player  │  dim_team  │  dim_game  │  dim_dates            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION                               │
│  Portal Dashboard  │  Tracker App  │  Admin Portal  │  Power BI │
└─────────────────────────────────────────────────────────────────┘
```

## Statistics Catalog (Priority Implementation)

### Basic Stats (from catalog)
| Stat ID | Name | Formula | Status |
|---------|------|---------|--------|
| BS01 | Goals | Count goal events | ✅ Ready |
| BS02 | Assists | Count assist events | ✅ Ready |
| BS03 | Points | G + A | ✅ Ready |
| BS04 | Shots on Goal | Count SOG events | ✅ Ready |
| BS08 | TOI (Seconds) | Sum shift durations | ✅ Ready |
| BS09 | TOI (Minutes) | TOI_sec / 60 | ✅ Ready |

### Advanced Stats
| Stat ID | Name | Formula | Status |
|---------|------|---------|--------|
| BS05 | Corsi For | Shot attempts while on ice | 🔄 Implement |
| BS06 | Fenwick For | Unblocked shot attempts | 🔄 Implement |
| BS11 | CF% | CF / (CF + CA) | 🔄 Implement |
| BS12 | FF% | FF / (FF + FA) | 🔄 Implement |
| BS13 | xG | Model-based expected goals | 📋 Planned |

### Micro Stats (Your Tracked Data)
| Stat | Description | Implementation |
|------|-------------|----------------|
| Possession Time | Duration-based possession | Sum duration where team has puck |
| Zone Entry Success | Controlled vs dump entries | event_type='zone_entry', event_detail |
| Zone Exit Success | Controlled vs cleared | event_type='zone_exit', event_detail |
| Pass Completion % | Successful / total passes | event_type='pass', event_successful |
| True Giveaways | Misplays only (exclude dumps) | event_type='turnover' AND NOT dump |
| Takeaways | Forced turnovers | event_type='takeaway' |
| Rush Attempts | Controlled zone entries | zone_entry with rush detail |

### Rating-Adjusted Stats (Unique to BenchSight)
| Stat | Description |
|------|-------------|
| Rating-Weighted CF | CF adjusted by opponent rating |
| Quality of Competition | Average opponent rating faced |
| Quality of Teammates | Average teammate rating |
| Rating Differential | Team rating vs opponent rating |
| Expected vs Actual | Performance given rating context |

---

# 🤖 COMPUTER VISION STATUS

## Current State
- **Model Selected**: YOLOv8 for puck/player detection
- **Infrastructure**: Designed but not implemented
- **Video Data**: Available for 7+ games via YouTube
- **Manual Alignment**: Video timestamps in video_times files

## Implementation Plan
1. Set up YOLOv8 inference pipeline
2. Train/fine-tune on hockey puck detection
3. Implement rink homography for coordinate mapping
4. Align CV detections with manual tracking timestamps
5. Build confidence scoring for automated events
6. Create hybrid tracking (CV + manual verification)

## Required Resources
- GPU compute for inference
- Labeled training data (puck positions)
- Rink calibration images
- Video processing pipeline

---

# 💡 FEATURE IDEAS (From Documentation)

## User-Defined Statistics
- Allow users to define custom stat formulas
- Upload stat definition CSV/JSON files
- Auto-generate ETL for new stats
- Request new stats through UI

## Play Chain Analysis
- Link events: Zone Entry → Pass → Shot → Save → Rebound → Goal
- Clickable drill-down from any stat
- Video clips for each play chain segment
- Success rate by chain pattern

## Comparative Analysis
- Player vs Player comparison
- Line vs Line analysis
- This game vs season average
- BLB player → NHL player similarity (from ETL plan)

## Time-Series Trends
- League standings over time
- Player performance trending
- Team rating changes by date
- NORAD stats historical view

## Defensive Player View (R.Pinnell Use Case)
- Goals against with extensive filters
- Opponent rating context
- Shot type breakdown (wrist/slap/snap)
- Screen presence
- Play chain leading to goal
- Zone entry type before goal
- Video clips of goals against

---

# 📁 PROJECT STRUCTURE

```
benchsight/
├── config/
│   └── settings.py              # Configuration
├── data/
│   ├── raw/
│   │   ├── master/              # BenchSight_Tables.xlsx
│   │   └── games/               # Per-game folders
│   │       ├── 18955/
│   │       ├── 18965/
│   │       ├── 18969/           # Platinum 4-3 Velodrome
│   │       └── ...
│   ├── processed/
│   │   ├── stage/               # Stage layer CSVs
│   │   ├── intermediate/        # Intermediate layer CSVs
│   │   └── mart/                # Mart layer CSVs
│   └── exports/                 # Power BI exports
├── src/
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── extract.py           # Load tracking files
│   │   ├── transform.py         # Build fact tables
│   │   ├── load.py              # Push to Postgres
│   │   └── orchestrator.py      # Main ETL runner
│   ├── stats/
│   │   ├── basic.py             # G, A, P, SOG
│   │   ├── advanced.py          # CF%, FF%, xG
│   │   └── micro.py             # Entries, exits, possession
│   ├── utils/
│   │   ├── video.py             # Video time sync
│   │   ├── scraper.py           # NORAD scraping
│   │   └── helpers.py           # Utility functions
│   └── cv/
│       ├── detection.py         # YOLOv8 inference
│       └── tracking.py          # Object tracking
├── sql/
│   ├── create_schema.sql        # Full schema DDL
│   ├── stage/                   # Stage layer SQL
│   ├── intermediate/            # Intermediate SQL
│   └── mart/                    # Mart layer SQL
├── portal/
│   ├── index.html               # Main dashboard
│   ├── tracker.html             # Event tracker
│   ├── game.html                # Game detail view
│   ├── player.html              # Player cards
│   ├── admin.html               # Admin portal
│   ├── docs.html                # Documentation viewer
│   ├── css/
│   │   └── benchsight.css       # Styles
│   ├── js/
│   │   ├── data.js              # Data loading
│   │   ├── dashboard.js         # Dashboard logic
│   │   ├── tracker.js           # Tracker logic
│   │   └── admin.js             # Admin functions
│   └── assets/
│       └── logos/               # Team logos
├── powerbi/
│   ├── BenchSight.pbit          # Template
│   ├── measures.dax             # DAX measures
│   └── README.md                # PBI instructions
├── embed/                       # Wix hosting files
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
├── docs/
│   ├── catalogs/
│   │   ├── stats_catalog.csv
│   │   └── tables_catalog.csv
│   ├── flows/
│   │   └── etl_flow.png
│   ├── llm/
│   │   └── LLM_README.md        # For GPT/Gemini
│   ├── human/
│   │   └── USER_GUIDE.md
│   └── pbi/
│       └── PBI_SETUP.md
├── notebooks/
│   └── exploration.ipynb
└── README.md
```

---

# 🔧 LLM CONSULTATION GUIDE

## For Sharing with GPT/Gemini

### Essential Files to Share
1. `BENCHSIGHT_MASTER_STATUS.md` (this document)
2. `stats_catalog_master_ultimate.csv`
3. `tables_catalog.csv`
4. `LLM_README_MASTER.txt`
5. Sample tracking file structure

### Key Context to Provide
```
BenchSight is a hockey analytics platform for beer league/junior hockey.

DATA SOURCES:
- Manual tracking via Excel (events, shifts, XY coordinates)
- BenchSight_Tables.xlsx (master dimensions: players, teams, schedule)
- Video timestamps in video_times.xlsx per game

ARCHITECTURE:
- Raw → Stage → Intermediate → Mart data pipeline
- PostgreSQL for persistent storage
- Python ETL (pandas, SQLAlchemy)
- HTML/JS portal with interactive dashboards
- Power BI for advanced visualizations

UNIQUE FEATURES:
- Rating-adjusted metrics (opponent/teammate quality)
- Play chain analysis (entry → pass → shot → goal)
- Privacy mode (random names, hidden images)
- Video sync with click-to-play
- Defensive player analysis view

GOALS:
1. Near-term: Team game viewing
2. Mid-term: Resume/portfolio
3. Long-term: Commercial product
```

### Questions to Ask Other LLMs
1. "Review this stat catalog - what hockey analytics stats are missing?"
2. "What's the best architecture for real-time event tracking UI?"
3. "How would you implement an xG model with this data schema?"
4. "What's the best way to handle video synchronization with events?"
5. "How should I structure the multi-tenant database for commercial use?"
6. "What ML models would be most valuable for hockey analytics?"
7. "How can I optimize the ETL pipeline for near-real-time updates?"

---

# ✅ NEXT STEPS

## Immediate Actions (This Session)
1. ✅ Create comprehensive status document
2. 🔄 Build Python ETL pipeline
3. 🔄 Create SQL schema
4. 🔄 Build portal with all pages
5. 🔄 Create admin portal with ETL controls
6. 🔄 Fix all dashboard issues
7. 🔄 Package complete ZIP

## Pending: Ideas.zip Review
⚠️ The `ideas.zip` file was mentioned but not uploaded. Please upload for:
- Commercial product vision
- Advanced stats documentation
- Gemini deep research paper
- Additional feature requirements

---

*Document Version: 1.0*
*Last Updated: December 26, 2025*
