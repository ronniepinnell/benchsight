# BenchSight Hockey Analytics Platform

**Version:** 14.01  
**Date:** January 7, 2026  
**Status:** Production-Ready ETL + Tracker v3

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
1. Open `docs/html/index.html` in browser
2. Or open `docs/html/tracker/benchsight_tracker_v3.html` to track games

---

## 📊 Project Overview

BenchSight is a comprehensive hockey analytics ETL platform for the NORAD recreational hockey league. It processes game tracking data into a 59-table data warehouse for analysis.

### Key Stats
| Metric | Value |
|--------|-------|
| Total Tables | 59 (33 dim, 24 fact, 2 qa) |
| Games Tracked | 4 (18969, 18977, 18981, 18987) |
| Total Goals | 17 (verified vs noradhockey.com) |
| Player Stats Columns | 317 |
| Passing Tests | 32 Tier 1, 17 Tier 2 |

---

## 📁 Directory Structure

```
benchsight/
├── LLM_REQUIREMENTS.md      # START HERE - critical rules
├── README.md                # This file
├── CHANGELOG.md             # Version history
├── MASTER_GUIDE.md          # Comprehensive guide
├── config/                  # Configuration files
│   ├── VERSION.json         # Version control
│   ├── IMMUTABLE_FACTS.json # Verified goal counts
│   └── TABLE_METADATA.json  # Table definitions
├── data/
│   ├── raw/games/           # Source tracking files
│   └── output/              # ETL output CSVs
├── docs/
│   ├── html/                # HTML documentation
│   │   ├── index.html       # Main docs index
│   │   ├── tracker/         # Tracker docs & app
│   │   ├── tables/          # Per-table docs
│   │   └── diagrams/        # ERD viewer
│   ├── roles/               # Role-specific guides
│   └── *.md                 # Markdown docs
├── scripts/
│   ├── pre_delivery.py      # Master pipeline
│   ├── bs_detector.py       # Verification
│   └── utilities/           # Helper scripts
├── src/
│   ├── etl_orchestrator.py  # Main ETL
│   ├── core/                # Core modules
│   └── tables/              # Table builders
├── sql/                     # Supabase schemas
├── supabase/                # Supabase config
└── tests/                   # Test suite
```

---

## 🎮 Tracker Application

The BenchSight Tracker replaces Excel-based game tracking.

### Quick Access
- **Launch Tracker:** `docs/html/tracker/benchsight_tracker_v3.html`
- **Setup Guide:** `docs/SUPABASE_SETUP_GUIDE.md`
- **ETL Format:** `docs/TRACKER_ETL_SPECIFICATION.md`
- **Requirements:** `docs/TRACKER_REQUIREMENTS.md`

### Features
- ✅ Event tracking with hotkeys
- ✅ Cascading dropdowns (type → detail1 → detail2)
- ✅ XY coordinate tracking (10 pts/player, 10 pts/puck)
- ✅ Per-player play details with s/u
- ✅ Auto zone calculation from XY
- ✅ Shift tracking with lineup management
- ✅ Intermission handling for video sync
- ✅ Excel export in ETL-compatible format
- ⏳ Supabase integration (needs setup)
- ⏳ NORAD validation (needs Supabase)

---

## ⚠️ Critical Rules

### Goal Counting
```python
# CORRECT - Goals are ONLY:
event_type = 'Goal' AND event_detail = 'Goal_Scored'

# WRONG - Shot_Goal is the SHOT, not the goal:
event_detail = 'Shot_Goal'  # THIS IS WRONG
```

### Before Any Package
```bash
python scripts/pre_delivery.py
```

### Expected Outputs
- 59 CSV files in `data/output/`
- 17 total goals across 4 games
- All tests passing

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `LLM_REQUIREMENTS.md` | Critical rules for LLMs |
| `docs/html/index.html` | Main documentation portal |
| `docs/html/tracker/index.html` | Tracker documentation |
| `docs/html/SCRIPTS_REFERENCE.html` | Scripts guide |
| `docs/roles/*.md` | Role-specific guides |
| `CHANGELOG.md` | Version history |

---

## 🔧 Common Commands

```bash
# Run full ETL
python -m src.etl_orchestrator full

# Run pre-delivery (does everything)
python scripts/pre_delivery.py

# Verify package
python scripts/utilities/verify_delivery.py

# Check for issues
python scripts/bs_detector.py

# Bump version
python scripts/utilities/doc_consistency.py --bump

# Fix all docs
python scripts/utilities/doc_consistency.py --fix

# Run tests
python -m pytest tests/test_etl.py -v
```

---

## 📞 Contact Points in Code

| What | File | Location |
|------|------|----------|
| ETL Entry | `src/etl_orchestrator.py` | `run_full()` |
| Goal Logic | `src/core/base_etl.py` | Line ~657 |
| Key Generation | `src/core/key_utils.py` | `format_key()` |
| Pre-Delivery | `scripts/pre_delivery.py` | Main pipeline |

---

## 📝 Version Naming

**Format:** `benchsight_v{CHAT}.{OUTPUT}`

- **CHAT** = New Claude chat session number
- **OUTPUT** = Package number within chat

Example: `v14.01` = Chat 14, first output

---

**END OF README**
