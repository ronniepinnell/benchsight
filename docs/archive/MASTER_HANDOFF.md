# BenchSight Master Handoff Document
*Updated: December 28, 2025 - v2.1.0*

## ⚠️ CRITICAL: Schema-Driven Workflow

**As of v2.1.0, all uploads MUST follow this process:**

```bash
# 1. Run tests FIRST (required - all 25 must pass)
pytest tests/test_schema_compliance.py -v

# 2. Preview what will upload
python PRODUCTION_ETL.py --dry-run

# 3. Upload
python PRODUCTION_ETL.py
```

**Source of Truth:** `config/supabase_schema.json` (50 tables, queried from Supabase)

---

## Project Summary

BenchSight is a comprehensive beer league hockey analytics platform tracking 200+ statistics from manual game footage analysis. The system processes Excel tracking data through Python, stores in Supabase (PostgreSQL), and visualizes in Power BI.

---

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip3 install pandas supabase openpyxl requests pytest --break-system-packages
```

### 2. Run Schema Compliance Tests
```bash
cd benchsight
pytest tests/test_schema_compliance.py -v
```
**All 25 tests must pass before uploading.**

### 3. Upload Data
```bash
python PRODUCTION_ETL.py --dry-run  # Preview first
python PRODUCTION_ETL.py            # Upload
```

### 4. Single Table Upload
```bash
python PRODUCTION_ETL.py --table dim_player
```

---

## Key Files

| File | Purpose |
|------|---------|
| `config/supabase_schema.json` | **SOURCE OF TRUTH** - Supabase table/column definitions |
| `PRODUCTION_ETL.py` | Production upload script with schema validation |
| `tests/test_schema_compliance.py` | 25 tests that validate CSVs match schema |
| `data/output/*.csv` | 49 CSV files ready for upload |

---

## Database Schema Overview

### 50 Tables Total
- **30 Dimension Tables**: Reference data (players, teams, events, stats)
- **20 Fact Tables**: Transactional data (events, shifts, stats)

### Key Tables

| Table | Records | Purpose |
|-------|---------|---------|
| dim_player | 337 | Player roster |
| dim_team | 26 | Teams |
| dim_schedule | 562 | Game schedule |
| fact_gameroster | 14,473 | Player-game roster |
| fact_events_tracking | 7,840 | Normalized events |
| fact_events_long | 24,089 | Denormalized events with player data |

---

## Column Naming Rules (CRITICAL)

Schema column names are **case-sensitive**. Common issues:

| Table | Correct | Wrong |
|-------|---------|-------|
| fact_events_tracking | `Type` | `type`, `event_type` |
| fact_gameroster | `assist` | `assists` |
| fact_gameroster | `date` | `game_date` |
| fact_gameroster | `key` | `roster_key` |
| fact_registration | `CAF` | `caf` |
| fact_playergames | `ID`, `Date`, `G`, `A` | `game_id`, `date`, `goals`, `assist` |
| dim_schedule | `home_team_periodOT_goals` | `home_team_periodot_goals` |

---

## Schema Sync Process

When Supabase schema changes:

### 1. Query Current Schema
```sql
-- Run in Supabase SQL Editor
SELECT table_name, column_name 
FROM information_schema.columns 
WHERE table_schema = 'public' 
ORDER BY table_name, ordinal_position;
```

### 2. Export as JSON
Save output as JSON array format.

### 3. Update Schema File
Replace contents of `config/supabase_schema.json` with query output.

### 4. Re-run Tests
```bash
pytest tests/test_schema_compliance.py -v
```

---

## Event Tracking Hierarchy

```
EVENT_TYPE (20 types)
├── Shot, Pass, Turnover, Faceoff, Zone_Entry_Exit, Save, Hit, etc.
│
├── EVENT_DETAIL (57 details)
│   ├── Shot_Blocked, Shot_Missed, Shot_OnNetSaved, Shot_Goal
│   ├── Pass_Completed, Pass_Intercepted, Pass_Missed
│   ├── Turnover_Giveaway, Turnover_Takeaway
│   ├── Zone_Entry, Zone_Exit, Zone_Keepin (+ failed versions)
│   └── Save_Freeze, Save_Played, Save_Rebound
│
└── EVENT_DETAIL_2 (143 sub-details)
    ├── Shot types: Wrist, Slap, Backhand, Snap, Tip, OneTimer
    ├── Giveaway types: Misplayed (bad), ZoneClearDump (neutral)
    ├── Entry types: Rush (controlled), DumpIn (uncontrolled)
    └── Save locations: Glove, Blocker, Pad, Butterfly
```

---

## Player Attribution System

| Role | Description | Example Stats |
|------|-------------|---------------|
| **event_player_1** | Primary actor | Goals, Shots, Passes, Takeaways |
| **event_player_2** | Secondary (pass target) | Primary Assists, Pass Targets |
| **event_player_3** | Tertiary | Secondary Assists |
| **opp_player_1** | Primary defender | Entry Denials, Shots Against, Times Beaten |
| **opp_player_2-6** | Secondary defenders | Supporting defensive stats |
| **goalie** | Goaltender | Saves, GAA, Rebound Control |
| **on_ice** | All players on ice | Corsi, Fenwick, +/- |

---

## Stats Categories (200+ Total)

### 1. Basic Box Score
G, A, A1, A2, PTS, SOG, SH%, +/-, PIM, HITS, BLK

### 2. Deployment
TOI (total/playing/dead), SHIFTS, AVG_SHIFT, OZ_START%

### 3. Turnovers
TAKEAWAY, GIVEAWAY (bad/neutral), TURNOVER_DIFF, TURNOVER_DIFF_ADJ

### 4. Zone Transitions
ZONE_ENTRY (ctrl/dump), ZONE_EXIT (ctrl/clear), ENTRY_DENIAL, EXIT_DENIAL

### 5. Micro-Offense
PASS_ATT/COMP/%, DEKE, SCREEN, TIP, ONE_TIMER, BOARD_BATTLE, CYCLE

### 6. Micro-Defense
STICK_CHECK, POKE_CHECK, BACKCHECK, FORECHECK, GAP_CONTROL, COVERAGE

### 7. Possession
CF, CA, CF%, FF, FA, FF%, PDO

### 8. Faceoffs
FOW, FOL, FO%

### 9. Goalie
SV%, GAA, SA, GA, REBOUND%, FREEZE%

### 10. Composite Ratings
OFFENSIVE_RATING, DEFENSIVE_RATING, HUSTLE_RATING, IMPACT_SCORE

---

## Data Flow

```
1. TRACKING
   Excel tracking template → Manual event entry during video review

2. EXPORT
   export_all_data.py → CSV files in data/output/

3. VALIDATE (NEW - REQUIRED)
   pytest tests/test_schema_compliance.py -v
   All 25 tests must pass

4. UPLOAD
   PRODUCTION_ETL.py → Supabase PostgreSQL

5. CALCULATE
   calculate_stats.py → Player/Goalie game stats

6. VISUALIZE
   Power BI → Connect to Supabase → Dashboards
```

---

## Test Coverage

### Schema Compliance Tests (25)
- Schema file existence and validity
- No extra columns in CSVs
- No metadata columns (_export_timestamp, etc.)
- Core tables exist with data
- Specific table validations (gameroster, events_tracking, playergames)

### ETL Data Cleaning Tests (29)
- NULL detection (NaN, None, empty strings, Excel errors)
- Value cleaning (BOM removal, encoding, truncation)
- DataFrame cleaning (remove unnamed columns)
- Record transformation

**Total: 54 tests**

---

## Common Issues & Solutions

### Schema Mismatch Error
**Error**: `Could not find column 'X' in schema cache`
**Fix**: 
1. Check `config/supabase_schema.json` matches Supabase
2. Run `pytest tests/test_schema_compliance.py -v` to find mismatches
3. Fix CSV column names to match schema

### Case Sensitivity
**Error**: `Column 'type' not found` (but `Type` exists)
**Fix**: Schema columns are case-sensitive. Check exact case in schema file.

### 403 Forbidden
**Error**: `403 Forbidden` on upload
**Fix**: Check RLS policies in Supabase:
```sql
CREATE POLICY "Public insert" ON table_name FOR INSERT WITH CHECK (true);
```

### NaN Values
**Error**: `Token "NaN" is invalid`
**Fix**: PRODUCTION_ETL.py handles this automatically. If persisting, check for literal "NaN" strings.

---

## File Structure

```
benchsight/
├── PRODUCTION_ETL.py           # Main upload script (USE THIS)
├── UPLOAD_GUIDE.md             # Upload instructions
├── config/
│   └── supabase_schema.json    # SOURCE OF TRUTH
├── tests/
│   ├── test_schema_compliance.py  # Schema validation (25 tests)
│   └── test_etl_upload.py         # Data cleaning (29 tests)
├── data/
│   └── output/                 # CSV exports (49 files)
├── docs/
│   ├── MASTER_HANDOFF.md       # This document
│   ├── CHANGELOG.md            # Version history
│   └── ...
├── html/
│   └── validation_report.html  # Visual validation status
└── ...
```

---

## Verification Checklist

Before every upload:

- [ ] `pytest tests/test_schema_compliance.py -v` - All 25 pass
- [ ] `python PRODUCTION_ETL.py --dry-run` - Verify row counts
- [ ] Check log file in `logs/` for any warnings

After upload:

- [ ] Verify row counts in Supabase
- [ ] Spot-check a few records
- [ ] Test Power BI connection

---

## Next Steps

1. **Immediate**: Run tests, upload data
2. **Short-term**: Connect Power BI, build dashboards
3. **Medium-term**: Add more games, refine tracking workflow
4. **Long-term**: ML models, predictive analytics, video integration

---

*End of Master Handoff - v2.1.0*
