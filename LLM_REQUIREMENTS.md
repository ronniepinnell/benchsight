# BenchSight LLM Requirements

**CRITICAL: READ THIS ENTIRE FILE BEFORE MAKING ANY CHANGES**

## Version: 14.01 (January 7, 2026)

---

## 🎮 TRACKER APPLICATION

### Current Status
The BenchSight Tracker v3 is complete and located at:
- **App:** `docs/html/tracker/benchsight_tracker_v3.html`
- **Docs:** `docs/html/tracker/index.html`

### Key Tracker Documents
| Document | Purpose |
|----------|---------|
| `docs/TRACKER_ETL_SPECIFICATION.md` | EXACT export format ETL expects |
| `docs/TRACKER_V3_SPECIFICATION.md` | Complete feature spec |
| `docs/TRACKER_REQUIREMENTS.md` | Detailed requirements |
| `docs/TRACKER_DEVELOPER_HANDOFF.md` | Dev continuation guide |
| `docs/SUPABASE_SETUP_GUIDE.md` | Database setup |
| `docs/TRACKING_TEMPLATE_ANALYSIS.md` | ML analysis of data |

### Tracker Export Format (CRITICAL)
- **Events:** LONG format - one row per player per event
- **Shifts:** WIDE format - one row per shift
- **XY Data:** Separate sheet - up to 10 points per player/puck

### Supabase Setup Required
The tracker works offline with demo data but needs Supabase for:
- Real game/roster data
- NORAD goal validation
- Persisting tracked data

See `docs/SUPABASE_SETUP_GUIDE.md` for setup instructions.

---

## ⛔ MANDATORY DELIVERY PROTOCOL ⛔

### The ONLY Way to Create a Valid Package

```bash
python scripts/pre_delivery.py
```

**This script does EVERYTHING automatically:**
1. Wipes all output (nuclear clean)
2. Runs ETL from scratch
3. Verifies goals against IMMUTABLE_FACTS.json
4. Checks for file truncation
5. Runs tests
6. Bumps version number
7. Fixes all documentation
8. Creates verified package with MANIFEST.json

**If it shows PASS** → Package is verified, accept it
**If it shows FAIL** → Package is broken, fix the root cause

### Rules LLMs MUST Follow

1. **NEVER** create a package without running `python scripts/pre_delivery.py`
2. **NEVER** claim success without showing the full output
3. **NEVER** manually zip files
4. **NEVER** modify `config/IMMUTABLE_FACTS.json` without explicit user permission
5. **ALWAYS** fix the root cause - do not modify scripts to make them pass

### Files LLMs Cannot Modify (Without Permission)

- `config/IMMUTABLE_FACTS.json` - Human-verified goal counts
- `scripts/pre_delivery.py` - Master pipeline
- `scripts/bs_detector.py` - Verification script

---

## QUICK REFERENCE

| Item | Value |
|------|-------|
| Current Version | v13.07 |
| Next Chat Version | v14.xx |
| Working Tables | 59 (59 (33 dim, 24 fact, 2 qa)) |
| Games Tracked | 4 (18969, 18977, 18981, 18987) |
| Total Goals | 17 (verified against noradhockey.com) |
| Tier 1 Tests | 32 (blocking) |
| Tier 2 Tests | 17 (warning) |

---

## ⚠️ BS DETECTION - RUN BEFORE ACCEPTING ANY WORK ⚠️

### The Pre-Delivery Pipeline

**ALWAYS run this before accepting ANY package from an LLM:**

```bash
python scripts/pre_delivery.py
```

This script:
1. Wipes all output (nuclear clean)
2. Runs ETL from scratch
3. Verifies table counts match ground truth
4. Verifies goal counts match raw source data
5. Runs pytest
6. Returns EXIT CODE 0 (pass) or 1 (fail)

**If bs_detector.py fails, the LLM broke something. Do not accept the package.**

### Ground Truth Values (MEMORIZE THESE)

| Item | Correct Value | How to Verify |
|------|---------------|---------------|
| Total tables | 59 | `ls data/output/*.csv \| wc -l` |
| Dim tables | 33 | `ls data/output/dim_*.csv \| wc -l` |
| Fact tables | 24 | `ls data/output/fact_*.csv \| wc -l` |
| QA tables | 2 | `ls data/output/qa_*.csv \| wc -l` |
| Total goals | 17 | See goal counting rule below |
| Game 18969 goals | 7 | |
| Game 18977 goals | 6 | |
| Game 18981 goals | 3 | |
| Game 18987 goals | 1 | |

**Goal Counting Rule (CRITICAL):**
```python
# CORRECT - Goals are ONLY:
df[(df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')]

# WRONG - Shot_Goal is the SHOT, not the goal:
df[df['event_detail'] == 'Shot_Goal']  # THIS IS WRONG
```

### Manual Verification Commands

Run these BEFORE accepting any LLM work:

```bash
# 1. Clean slate ETL test
rm -rf data/output/*
python -m src.etl_orchestrator full
ls data/output/*.csv | wc -l  # MUST be 59

# 2. Goal count verification
python -c "
import pandas as pd
df = pd.read_csv('data/output/fact_events.csv')
goals = df[(df['event_type']=='Goal') & (df['event_detail']=='Goal_Scored')]
print(f'Total goals: {len(goals)}')  # MUST be 17
for gid in [18969, 18977, 18981, 18987]:
    g = goals[goals['game_id']==gid]
    print(f'  Game {gid}: {len(g)} goals')
"

# 3. Doc size verification (catch truncation)
wc -l LLM_REQUIREMENTS.md              # Should be 400+ lines
wc -l docs/DATA_DICTIONARY.md          # Should be 500+ lines
wc -l docs/html/index.html             # Should be 200+ lines

# 4. Run tests
python -m pytest tests/test_etl.py -v
```

### 🚨 RED FLAGS - LLM IS BREAKING THINGS 🚨

**STOP the LLM immediately if you see:**

1. **Files getting SMALLER** - "I'll update this file" → file goes from 500 lines to 50
2. **"Rewriting from scratch"** - Should be surgical edits, not full rewrites
3. **Creating new files instead of editing** - Check if file already exists
4. **Version numbers going backwards** - v13.03 should not become v12.xx
5. **Claiming success without running verification** - "I fixed it" without running ETL
6. **Goal counts changing** - Should ALWAYS be 17 total
7. **Table counts changing unexpectedly** - Should be 61 unless intentional
8. **"I'll simplify this"** - Often means "I'll delete working code"
9. **Multiple "fixes" for same issue** - Means they don't understand the problem
10. **Large code blocks without explanation** - Hiding broken logic

### Questions to Ask LLM (BS Detection)

Ask these questions to verify the LLM understands the codebase:

**Before they start:**
```
1. "What is the correct goal counting rule for this project?"
   CORRECT: event_type='Goal' AND event_detail='Goal_Scored'
   WRONG: Anything mentioning Shot_Goal as a goal

2. "How many tables should the ETL produce?"
   CORRECT: 61 (59 (33 dim, 24 fact, 2 qa))
   
3. "What games are tracked and how many goals in each?"
   CORRECT: 18969(7), 18977(6), 18981(3), 18987(1) = 17 total
   
4. "Will you run bs_detector.py before delivering?"
   CORRECT: Yes
   WRONG: Any excuse about why they can't
```

**After they claim a fix:**
```
1. "Did you run `python scripts/bs_detector.py`? What was the exit code?"
   CORRECT: Exit code 0 (all checks passed)
   
2. "Show me the output of `ls data/output/*.csv | wc -l`"
   CORRECT: 61
   
3. "Did any files get smaller? Compare before/after line counts."
   
4. "Is this a root cause fix or a workaround?"
```

### Root Cause vs Patchwork (How to Tell)

**ROOT CAUSE FIX (Good):**
- Fixes the actual source of the problem
- Changes are minimal and surgical
- Explains WHY the bug existed
- Future similar issues won't occur
- Example: "The bug was in line 245 where we used 'Period' instead of 'period' after the rename on line 880"

**PATCHWORK FIX (Bad):**
- Adds code to work around the symptom
- Creates new functions/files to "handle" the issue
- Doesn't explain root cause
- Similar bugs will keep appearing
- Example: "I added a try/except to catch the error" or "I created a new function to handle this case"

**Questions to detect patchwork:**
```
1. "Where was the original bug in the code?"
2. "Why did the bug exist in the first place?"
3. "Did you add new code or modify existing code?"
4. "Will this fix prevent similar issues, or just this one instance?"
```

### LLM Accountability Checklist

Before accepting ANY package, verify the LLM has:

- [ ] Run `python scripts/bs_detector.py` with exit code 0
- [ ] Not reduced any file sizes significantly
- [ ] Made surgical edits (not full rewrites)
- [ ] Explained the root cause of any bugs fixed
- [ ] Verified goal count is 17
- [ ] Verified table count is 61
- [ ] Run `python scripts/utilities/doc_consistency.py --fix`
- [ ] Run `python scripts/utilities/verify_delivery.py`

---

## HTML DOCUMENTATION REFERENCE

All documentation is available in HTML format at `docs/html/`:

| Document | Path | Purpose |
|----------|------|---------|
| **Index/Home** | `docs/html/index.html` | Start here - links to everything |
| **Tables** | `docs/html/tables.html` | Browse all 59 tables |
| **Per-Table** | `docs/html/tables/*.html` | Individual table docs |
| **ERD/Schema** | `docs/html/diagrams/ERD_VIEWER.html` | Entity relationships |
| **Pipeline** | `docs/html/pipeline_visualization.html` | ETL flow diagrams |
| **Modules** | `docs/html/MODULE_REFERENCE.html` | Source code docs |
| **Keys** | `docs/html/KEY_FORMATS.html` | Key format reference |
| **Dictionary** | `docs/html/DATA_DICTIONARY.html` | Column definitions |
| **Assessment** | `docs/html/HONEST_ASSESSMENT.html` | Current status |
| **LLM Guide** | `docs/html/LLM_HANDOFF.html` | AI assistant guide |

---

## VERSION NAMING CONVENTION (CRITICAL)

**Format:** `benchsight_v{CHAT}.{OUTPUT}`

- **CHAT** = Increments each NEW Claude chat session
- **OUTPUT** = Increments each package output within same chat

**Examples:**
- `benchsight_v13.01` = Chat 13, first output
- `benchsight_v13.02` = Chat 13, second output  
- `benchsight_v14.01` = Chat 14 (new chat), first output

**Current:** v13.04 (Chat 13, Output 04)
**Next Chat:** v14.01

---

## UPON OPENING FIRST MESSAGE

1. Summarize project understanding
2. Acknowledge you read this file
3. Verify ETL works: `python -m src.etl_orchestrator status`
4. Propose gameplan for session
5. Do NOT do large work until we agree on what needs to be done

---

## GOAL COUNTING RULES (CRITICAL)

Goals are counted ONLY via:
```python
event_type = 'Goal' AND event_detail = 'Goal_Scored'
```

**⚠️ IMPORTANT:** `Shot_Goal` is the SHOT that resulted in a goal, NOT the goal itself!

The `event_player_1` is ALWAYS the primary player (scorer for goals).

---

## PLAYER ROLE VALUES

| Role | Meaning | Example |
|------|---------|---------|
| `event_player_1` | PRIMARY player | Scorer, shooter, passer |
| `event_player_2` | SECONDARY player | Primary assist, receiver |
| `event_player_3` | TERTIARY player | Secondary assist |
| `event_player_4-6` | Additional players | Other on-ice players |
| `event_goalie` | Event team goalie | |
| `opp_player_1-6` | Opposing players | |
| `opp_goalie` | Opposing goalie | |

---

## ETL ORCHESTRATOR (Primary Entry Point)

### Python Usage
```python
from src.etl_orchestrator import ETLOrchestrator
etl = ETLOrchestrator()

etl.print_status()           # Check status
etl.run_full()               # Full ETL - all games
etl.run_incremental()        # Only new/changed games
etl.run_single_game(18969)   # Single game
```

### CLI Usage
```bash
python -m src.etl_orchestrator status
python -m src.etl_orchestrator full
python -m src.etl_orchestrator incremental
python -m src.etl_orchestrator single 18969
python -m src.etl_orchestrator reset
```

---

## ETL TESTING

Before any changes:
```bash
python3 -m pytest tests/test_etl.py -v
```
Expected: **23 tests passing**

---

## NEVER DO WITHOUT TESTING

1. Delete any code
2. Modify `src/core/base_etl.py`
3. Change key generation logic
4. Alter table schemas

Always run tests BEFORE and AFTER changes.

---

## REQUIRED MODULES (NEVER DELETE)

These files in `src/advanced/` are REQUIRED:
- `create_additional_tables.py`
- `enhance_all_stats.py`
- `final_stats_enhancement.py`
- `extended_tables.py`

---

## PACKAGE EXPORT REQUIREMENTS

### Naming Convention
- Zip: `benchsight_v{CHAT}.{OUTPUT}.zip`
- Folder: `benchsight_v{CHAT}.{OUTPUT}/`

### Required Directory Structure
```
benchsight_v13.01/
├── LLM_REQUIREMENTS.md      # THIS FILE - READ FIRST
├── CHANGELOG.md             # Version history
├── README.md                # Quick start
├── requirements.txt         # Python dependencies
├── run_etl.py               # Simple ETL runner
│
├── data/
│   ├── output/              # 62 CSV tables
│   ├── raw/games/           # Per-game tracking files
│   │   ├── 18969/
│   │   ├── 18977/
│   │   ├── 18981/
│   │   └── 18987/
│   └── BLB_Tables.xlsx      # Master reference data
│
├── src/
│   ├── etl_orchestrator.py  # Main entry point
│   ├── core/                # base_etl.py, key_utils.py
│   ├── advanced/            # Extended tables
│   ├── transformation/      # Data transforms
│   └── ...
│
├── docs/
│   ├── html/                # ALL HTML documentation
│   │   ├── index.html       # Documentation home
│   │   ├── tables/          # Per-table HTML
│   │   ├── diagrams/        # ERD, flowcharts
│   │   └── ...
│   ├── diagrams/            # Mermaid source files
│   ├── *.md                 # Markdown docs
│   └── *.json               # Metadata files
│
├── tests/                   # Test files
├── config/                  # Configuration
├── scripts/                 # Utility scripts
└── sql/                     # SQL files
```

### Pre-Export Checklist

**MUST DO before every package export:**

```bash
# 1. Run tests
python3 -m pytest tests/test_etl.py -v

# 2. Verify table count (should be 62)
ls data/output/*.csv | wc -l

# 3. Check ETL status
python -m src.etl_orchestrator status

# 4. Verify goals match noradhockey.com (manual check)
```

**MUST UPDATE before every package export:**
- [ ] Version in this file (LLM_REQUIREMENTS.md)
- [ ] CHANGELOG.md - add entry
- [ ] docs/VERSION.txt
- [ ] All HTML files - version and timestamp (ensure documents represent current state)
- [ ] docs/html/index.html - stats and version (ensure documents represent current state)
- [ ] docs/HONEST_ASSESSMENT.md (ensure documents represent current state)
- [ ] docs/LLM_HANDOFF.md (ensure documents represent current state)


---

## VERSION HISTORY

| Version | Date | Key Changes |
|---------|------|-------------|
| v13.07 | Jan 7, 2026 | Complete safeguard system: tiered tests, schema snapshots, input validation |
| v13.05 | Jan 7, 2026 | Complete BS-proof delivery system, pre_delivery.py master pipeline, IMMUTABLE_FACTS.json |
| v13.04 | Jan 7, 2026 | BS Detector, corrected ground truth (59 tables, 17 goals), LLM accountability |
| v13.03 | Jan 7, 2026 | Automated version management via config/VERSION.json |
| v13.02 | Jan 7, 2026 | Doc consistency system - auto-fix all docs on delivery |
| v13.01 | Jan 7, 2026 | Table naming refactor (fact_event_players, fact_shift_players), ETL Period bug fix |
| v12.03 | Jan 7, 2026 | Enhanced column metadata, comprehensive HTML docs |
| v12.02 | Jan 7, 2026 | Data dictionary, missing tables documentation |
| v12.01 | Jan 7, 2026 | Emergency documentation recovery |
| v11.04 | Jan 7, 2026 | HTML menu navigation, suspicious stats |
| v11.03 | Jan 7, 2026 | Dimension key formatting, shift consolidation |
| v11.02 | Jan 7, 2026 | Schema consolidation, HTML doc linking |
| v11.01 | Jan 7, 2026 | Event time/TOI context, dim_shift_duration |
| v10.xx | Jan 2026 | Safety module, incremental ETL, verification |
| v9.xx | Jan 2026 | Previous sessions |
| v8.xx | Jan 2026 | Code restoration from backup |

---

## DOCUMENTATION CONSISTENCY SYSTEM (CRITICAL)

### Version is stored in: `config/VERSION.json`

That's the ONLY file that controls versioning. The doc_consistency.py script reads from it.

### Commands

```bash
# Check for issues
python scripts/utilities/doc_consistency.py

# Auto-fix all docs  
python scripts/utilities/doc_consistency.py --fix

# Show current version
python scripts/utilities/doc_consistency.py --status

# Bump version for new output (13.02 -> 13.03)
python scripts/utilities/doc_consistency.py --bump

# Start new chat (13.xx -> 14.01)
python scripts/utilities/doc_consistency.py --new-chat

# Add a banned table name
python scripts/utilities/doc_consistency.py --add-banned old_table_name new_table_name

# Full delivery check
python scripts/utilities/verify_delivery.py
```

### Workflow

**Every output:**
```bash
python scripts/utilities/doc_consistency.py --bump
python scripts/utilities/doc_consistency.py --fix
python scripts/utilities/verify_delivery.py
```

**New chat:**
```bash
python scripts/utilities/doc_consistency.py --new-chat
python scripts/utilities/doc_consistency.py --fix
```

**Renamed a table:**
```bash
python scripts/utilities/doc_consistency.py --add-banned old_name new_name
python scripts/utilities/doc_consistency.py --fix
```

---

## HOW TO UPDATE DOCUMENTATION

### When User Asks to "Update Docs" or "Clean Up"

Run the documentation update script:
```bash
python scripts/utilities/fix_all_html_docs.py
```

This updates:
- `docs/html/index.html`
- `docs/html/HONEST_ASSESSMENT.html`
- `docs/html/MODULE_REFERENCE.html`
- `docs/html/pipeline_visualization.html`
- `docs/html/KEY_FORMATS.html`
- `docs/html/LLM_HANDOFF.html`
- `docs/html/FUTURE_ROADMAP.html`
- `docs/html/diagrams/ERD_VIEWER.html`
- `docs/html/schema_diagram.html`

### Files That Need Manual Updates

| File | When to Update | What to Change |
|------|----------------|----------------|
| `LLM_REQUIREMENTS.md` | Every output | Version, table counts, checklist items |
| `CHANGELOG.md` | Every output | Add new entry at top |
| `docs/VERSION.txt` | Every output | Version, date, table count |
| `docs/HONEST_ASSESSMENT.md` | When issues change | Status of known issues |
| `docs/LLM_HANDOFF.md` | When architecture changes | Key stats, new features |
| `docs/FUTURE_ROADMAP.md` | When priorities change | Completed items, new priorities |
| `docs/diagrams/ERD_COMPLETE.mermaid` | When schema changes | Table relationships |
| `docs/diagrams/TABLE_INVENTORY.csv` | When tables change | Table list with row counts |
| `docs/column_metadata.json` | When columns change | Column definitions |

### HTML File Update Pattern

All HTML files should have:
```html
<p><strong>Last Updated:</strong> {DATE}</p>
<p><strong>Version:</strong> {VERSION}</p>
```

And consistent navigation bar linking to all major docs.

### Update Table HTML Files

Regenerate per-table HTML with:
```bash
python scripts/utilities/generate_enhanced_table_docs.py
```

### Verify All Links Work

Check that `docs/html/index.html` links all work:
- Tables: `tables.html`
- ERD: `diagrams/ERD_VIEWER.html`
- Pipeline: `pipeline_visualization.html`
- Modules: `MODULE_REFERENCE.html`
- Keys: `KEY_FORMATS.html`

---

## DOCUMENT UPDATE CHECKLIST

Every output MUST update:

| File | Location | Update |
|------|----------|--------|
| LLM_REQUIREMENTS.md | Root | Version, counts |
| CHANGELOG.md | Root | Add entry |
| docs/VERSION.txt | docs/ | Version, date |
| docs/html/index.html | docs/html/ | Stats, version |
| docs/html/*.html | docs/html/ | Timestamps |
| docs/HONEST_ASSESSMENT.md | docs/ | Issue status |
| docs/LLM_HANDOFF.md | docs/ | Version, features |

---

## COLUMN NAME CONVENTIONS

| Use This | Not This |
|----------|----------|
| `event_type` | `Type` |
| `event_id` | `event_key`, `event_index` |
| `game_id` | `game`, `gameId` |
| `player_id` | `player`, `playerId` |
| `is_goal` | `goal`, `isGoal` |

---

## KEY FORMAT REFERENCE

| Prefix | Key Name | Example | Description |
|--------|----------|---------|-------------|
| EV | event_id | EV1896901000 | Event identifier |
| SH | shift_id | SH1896900001 | Shift identifier |
| SQ | sequence_key | SQ1896905001 | Possession sequence |
| PL | play_key | PL1896906001 | Play grouping |
| P_ | player_id | P_SMITH_1 | Player identifier |

Format: `{PREFIX}{game_id}{index:05d}`

---

## SHIFT COLUMNS

In `fact_shifts`:
- `shift_duration` - Length in seconds (typically 45-60s)
- `shift_start_total_seconds` - Start time from period start
- `shift_end_total_seconds` - End time from period start

In `dim_shift_duration`:
- Very_Short (<30s), Short (30-45s), Normal (45-60s), Long (60-90s), Very_Long (>90s)

---

## TIME CONTEXT COLUMNS

Added to fact_events and derived tables:
- `time_to_next_event`, `time_from_last_event`
- `time_to_next_goal_for`, `time_to_next_goal_against`
- `time_from_last_goal_for`, `time_from_last_goal_against`
- `time_to_next_stoppage`, `time_from_last_stoppage`

Player TOI at event:
- `event_player_1_toi` through `event_player_6_toi`
- `opp_player_1_toi` through `opp_player_6_toi`

---

## BEST PRACTICES REMINDER

1. **Plan before execute** - Propose changes before implementing
2. **Test before and after** - Run pytest before/after changes
3. **Update docs with code** - Never update code without updating docs
4. **Incremental changes** - Small changes, verify each works
5. **Backup before delete** - Never delete without backup
6. **Dynamic, not hardcoded** - System must work with new games

---

## CURRENT GAMES

| Game ID | Status |
|---------|--------|
| 18969 | ✅ Verified |
| 18977 | ✅ Verified |
| 18981 | ✅ Verified |
| 18987 | ✅ Verified |

All 4 games verified against noradhockey.com with 100% goal accuracy.

---

## CONTACT POINTS IN CODE

| What | File | Function |
|------|------|----------|
| Run ETL | `src/etl_orchestrator.py` | `run_full()` |
| Goal logic | `src/core/base_etl.py:657` | `is_goal` calculation |
| Key generation | `src/core/key_utils.py:79` | `format_key()` |
| Player linkage | `src/core/key_utils.py:266` | `add_player_id_columns()` |

---

**END OF LLM_REQUIREMENTS.md**
