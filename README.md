# BenchSight Hockey Analytics Platform

**Version:** 16.08  
**Date:** January 8, 2026  
**Status:** Production-Ready ETL + Tracker v16.08

---

## 🚀 Quick Start

### For LLMs/Developers
```bash
# ALWAYS read this first
cat LLM_REQUIREMENTS.md

# Run the pre-delivery pipeline (does everything)
python scripts/pre_delivery.py
```

### For Users
1. Open `docs/html/index.html` in browser for documentation
2. Open `ui/tracker/index.html` to track games
3. Read `docs/HONEST_ASSESSMENT.md` for current status
4. Read `docs/TODO.md` for known issues and roadmap

---

## 📊 Project Overview

BenchSight is a comprehensive hockey analytics ETL platform for the NORAD recreational hockey league. It processes game tracking data into a 111+ table data warehouse for analysis.

### Key Stats
| Metric | Value |
|--------|-------|
| Total Tables | 111+ (dimensions, facts, analysis) |
| Games Tracked | 4 (18969, 18977, 18981, 18987) |
| Total Goals | 17 (verified vs noradhockey.com) |
| Player Stats Columns | 317+ |
| Passing Tests | 326+ |

---

## 🎮 Tracker Application

The BenchSight Tracker is a web-based game tracking interface at `ui/tracker/index.html`.

### Key Features (v16.08)
- **Event Tracking:** Full event types with cascading dropdowns from Supabase
- **XY Coordinates:** Center-relative (0,0 = center ice), click-through markers
- **Shift Management:** Track players on ice per shift
- **Play Details:** From dim_play_detail and dim_play_detail_2 tables
- **Event Details:** From dim_event_detail and dim_event_detail_2 tables
- **Player Roles:** 14 role types from dim_player_role
- **Auto-Calculate:** Pressure from XY, success from event type
- **Keyboard Shortcuts:** 40+ hotkeys for fast tracking

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| 1-6 | Select Event Player 1-6 |
| Ctrl+1-6 | Select Opponent Player 1-6 (may conflict with browser) |
| ` (backtick) | Switch to Puck XY mode |
| H / A | Select Home / Away team |
| Tab | Toggle Puck/Player XY mode |
| F/G/T/X | Faceoff/Goal/Turnover/Stoppage |
| Enter | Log event |
| L | Log shift |
| E/W | Edit last event/shift |
| Tab | Toggle team |
| Escape | Close modal |

### Workflow Goal
- **Before:** 8 hours per game
- **Target:** 1-2 hours per game
- Minimal clicks, maximum automation

---

## 📁 Directory Structure

```
benchsight/
├── LLM_REQUIREMENTS.md      # START HERE - critical rules
├── README.md                # This file
├── CHANGELOG.md             # Version history (v14.20)
├── MASTER_GUIDE.md          # Comprehensive guide
├── config/                  # Configuration files
│   ├── VERSION.json         # Version control
│   ├── IMMUTABLE_FACTS.json # Verified goal counts
│   └── TABLE_METADATA.json  # Table definitions
├── data/
│   ├── raw/games/           # Source tracking files
│   └── output/              # ETL output CSVs (59 tables)
├── docs/
│   ├── html/                # HTML documentation
│   │   ├── index.html       # Main docs index
│   │   ├── tables/          # Per-table docs
│   │   └── diagrams/        # ERD viewer
│   ├── roles/               # Role-specific guides
│   └── *.md                 # Markdown docs
├── ui/
│   └── tracker/             # Tracker application
│       └── index.html       # Main tracker UI
├── scripts/
│   ├── pre_delivery.py      # Master pipeline
│   ├── bs_detector.py       # Verification
│   └── utilities/           # Helper scripts
├── src/
│   ├── etl_orchestrator.py  # Main ETL
│   ├── core/                # Core modules
│   └── tables/              # Table builders
├── supabase/                # Supabase config
└── tests/                   # Test suite
```

---

## 🔧 Recent Changes (v14.x)

### v14.20 - January 8, 2026
- **Play Details:** Dropdowns load from Supabase dim tables (138 + 72 options)
- **Edit Modal:** Navigation arrows, role selection, two play details per player
- **Shift Editor:** Full player editing with position grouping
- **Event Log:** More columns, better tooltips
- **Clear Functions:** Clear all events/shifts buttons
- **Bug Fixes:** Shift log ascending order, player positions

### v14.01 - January 7, 2026
- Tracker v3 complete delivery
- ETL-aligned export format
- XY tracking with 10 points per player
- Full shift tracking

---

## ⚠️ Critical Rules

### Goal Counting (NEVER CHANGE)
```sql
-- ONLY way to count goals
SELECT COUNT(*) FROM fact_events 
WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored'
```

### Verified Goal Counts
| Game ID | Goals | Verified Source |
|---------|-------|-----------------|
| 18969 | 7 | noradhockey.com |
| 18977 | 6 | noradhockey.com |
| 18981 | 3 | noradhockey.com |
| 18987 | 1 | noradhockey.com |
| **Total** | **17** | |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `LLM_REQUIREMENTS.md` | Critical rules for LLMs |
| `CHANGELOG.md` | Version history |
| `docs/LLM_HANDOFF.md` | Session handoff guide |
| `docs/TRACKER_ETL_SPECIFICATION.md` | Tracker export format |
| `docs/html/index.html` | HTML documentation portal |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Tier 1 only (blocking)
pytest tests/test_tier1_blocking.py -v

# Tier 2 only (warnings)
pytest tests/test_tier2_warning.py -v
```

---

## 📦 Delivery

```bash
# Full pre-delivery pipeline
python scripts/pre_delivery.py

# Quick check (no ETL)
python scripts/pre_delivery.py --quick

# Dry run
python scripts/pre_delivery.py --dry-run
```

---

## 🔗 Supabase

```bash
# Sync to Supabase
python supabase/sync_to_supabase.py

# Generate schema
python supabase/generate_schema.py
```

See `docs/SUPABASE_SETUP_GUIDE.md` for full setup instructions.

---

## License

Proprietary - NORAD Hockey League
