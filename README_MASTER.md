# 📚 BENCHSIGHT - MASTER README FOR NEW SESSIONS

> **Read this file FIRST** when starting a new chat session.
> 
> **Status**: 98% Complete | 317 Stats | 72 Validations | 88 Tables

---

## 🎯 QUICK START - Read These Files in Order

### 1️⃣ CONTEXT (Read First)
| Priority | File | Purpose |
|----------|------|---------|
| **1** | `docs/handoff/HANDOFF_FINAL_V5.md` | Complete project status, what works, what doesn't |
| **2** | `docs/handoff/NEXT_SESSION_PROMPT_V4_FINAL.md` | Copy/paste prompt for starting new chat |
| **3** | This file (`README_MASTER.md`) | Navigation guide |

### 2️⃣ SCHEMA & DATA STRUCTURE
| Priority | File | Purpose |
|----------|------|---------|
| **4** | `docs/SCHEMA_RELATIONSHIPS.md` | PK→FK mappings, table relationships |
| **5** | `docs/diagrams/ERD_COMPLETE.mermaid` | Entity relationship diagram |
| **6** | `docs/DATA_DICTIONARY_COMPLETE.csv` | All 1,729 columns with types |
| **7** | `docs/TABLE_SUMMARY.csv` | 88 tables with column counts |

### 3️⃣ STATS & VALIDATION
| Priority | File | Purpose |
|----------|------|---------|
| **8** | `docs/STATS_CATALOG_COMPLETE.md` | All 317 player stat definitions |
| **9** | `scripts/test_validations.py` | 54 core validation tests |
| **10** | `scripts/enhanced_validations.py` | 8 additional tests |

### 4️⃣ XY COORDINATE SYSTEM (For Future)
| Priority | File | Purpose |
|----------|------|---------|
| **11** | `data/output/dim_rinkcoordzones.csv` | 84 zones with danger levels |
| **12** | `data/output/dim_rinkboxcoord.csv` | 24 box zones |
| **13** | `data/output/dim_rink_coord.csv` | 12 simple zones |

---

## 📊 KEY STATISTICS

```
┌─────────────────────────────────────────┐
│  BENCHSIGHT PROJECT STATUS              │
├─────────────────────────────────────────┤
│  Completion:        98%                 │
│  Player Stats:      317 columns         │
│  Tables:            88 (44 dim + 44 fact)│
│  Validations:       72 PASSED           │
│  Zero Columns:      48 (need data)      │
│  Games Loaded:      4 of 10             │
└─────────────────────────────────────────┘
```

---

## 🔧 ESSENTIAL COMMANDS

```bash
# Full ETL Pipeline
python etl.py

# Stats Enhancement (run in order)
python src/enhance_all_stats.py          # Phase 1: +161 cols
python src/final_stats_enhancement.py    # Phase 2: +91 cols
python src/fix_data_accuracy.py          # Data fixes

# Validations
python scripts/test_validations.py       # 54 tests
python scripts/enhanced_validations.py   # 8 tests

# FK Population
python src/populate_all_fks_v2.py
```

---

## 📁 DIRECTORY STRUCTURE

```
benchsight_combined/
├── data/
│   ├── raw/games/           # Source Excel tracking files
│   ├── output/              # 88 CSV tables (dim_* and fact_*)
│   └── BLB_Tables.xlsx      # Master dimension data
├── docs/
│   ├── handoff/             # Session handoff documents
│   ├── diagrams/            # ERD, data flow diagrams
│   ├── DATA_DICTIONARY_COMPLETE.csv
│   ├── SCHEMA_RELATIONSHIPS.md
│   └── TABLE_SUMMARY.csv
├── src/                     # Python ETL code
├── scripts/                 # Validation scripts
├── sql/                     # DDL for Supabase
├── tracker/                 # Game tracker HTML
└── dashboard/               # Dashboard HTML
```

---

## 🎮 CRITICAL BUSINESS RULES

### Goal Detection
```python
# A goal is detected when:
event_type == 'Goal' 
OR event_detail IN ('Goal_Scored', 'Shot_Goal')
```

### Player Roles
```
event_player_1 = Primary player (shooter, passer)
event_player_2 = Secondary (assist, pass target)
event_player_3-5 = On-ice teammates
opp_player_1 = Primary defender
opp_player_2-4 = On-ice opponents
```

### Success Flags
```
's' = successful
'u' = unsuccessful
'' (blank) = ignore in calculations
```

### Player Ratings
```
Scale: 2-6 (4 = average)
performance_index: 100 = playing at rating
                   >100 = above rating
                   <100 = below rating
```

---

## ⚠️ KNOWN ISSUES (48 Zero Columns)

| Category | Count | Blocker |
|----------|-------|---------|
| XY-dependent | 12 | Need XY coordinates in events |
| Score state | 6 | Need running score (leading/trailing/tied) |
| Special teams | 3 | Need EN/SH strength tags |
| Micro-stats | 27 | Not in current event vocabulary |

### XY Solution Ready:
The `dim_rinkcoordzones` table has 84 zones with `danger='low'/'mid'/'high'`.
When XY data exists in events, use:
```sql
SELECT danger FROM dim_rinkcoordzones
WHERE x_min <= shot_x AND shot_x <= x_max
  AND y_min <= shot_y AND shot_y <= y_max
```

---

## 🚀 NEXT PRIORITIES

### P0 - Immediate
1. Deploy to Supabase (`sql/01_create_tables_generated.sql`)
2. Load remaining 6 games

### P1 - Short Term
1. Add XY tracking to game tracker
2. Add score state to events
3. Power BI dashboards

### P2 - Long Term
1. Real xG model (logistic regression)
2. RAPM player isolation
3. WAR implementation

---

## 📋 COPY/PASTE PROMPT FOR NEW CHAT

```
Continuing BenchSight hockey analytics. 98% complete, 317 stats, 72 validations.

Working: Game score, xG for/against/diff/%, shot danger zones, H2H/WOWY.

48 zero columns need: (1) XY data, (2) score state, (3) special teams tags.

XY Ready: dim_rinkcoordzones has danger zones defined. Need XY in events.

Read first: docs/handoff/HANDOFF_FINAL_V5.md

Today I need: [YOUR REQUEST]
```

---

## 📞 KEY CONTACTS & RESOURCES

- **Project**: BenchSight Hockey Analytics
- **League**: NORAD Recreational Hockey
- **Database**: Supabase PostgreSQL (pending deployment)
- **Dashboards**: Power BI (schema ready)

---

*Last Updated: December 29, 2024*
*Session: Final XY/Danger Zone Fixes + Documentation*
