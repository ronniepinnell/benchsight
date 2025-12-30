# 🚨 MUST READ FIRST - BenchSight Project Rules

## Ronnie's Development Rules

These rules govern how development should proceed on this project:

```
Rules I require: 
- When we hit 50% of message length, let me know how much we have left after each message. 
- When we hit 90% please package everything up and update/upload complete handoff docs. 
- When i say package and download, please provide full project folders, update all documents, 
  handoff documents, update visualizations/flowcharts/schemas, etc. 
- Dont ever remove anything from project, append, update. 
- Always ask questions if you do not understand my request, before stating a task, 
  please summarize my request and let me know your plan
- Keep a running log of requests/chat summary
- Keep running log of requirements
- Keep running log of changes made
```

---

## Project Context

### What is BenchSight?
A comprehensive hockey analytics platform for the NORAD recreational hockey league. It processes game tracking data, integrates with dimensional tables, and outputs to a Supabase PostgreSQL database.

### Ground Truth Validation
- **Source:** noradhockey.com game pages
- **Goals accuracy:** 96%
- **Assists accuracy:** 91% (tracking gaps documented)
- **Game scores:** 100%

### Critical Business Rules
1. **player_role is CRITICAL** - Only `event_team_player_1` gets stat credit
2. **Shots = Corsi** - All shot attempts (60-70 per team is CORRECT)
3. **Assists in play_detail1** - Look for 'AssistPrimary', 'AssistSecondary'
4. **Goals via:** event_type "Goal" OR event_detail containing "Goal"

---

## Required Reading Order

### For ALL Developers
1. **This file** (MUST_READ_FIRST.md)
2. **INSPIRATION_AND_RESEARCH.md** - Analytics sites to reference for design
3. **MASTER_INSTRUCTIONS.md** - Business rules and stat definitions
4. **SCHEMA_AND_ERD.md** - Database structure

### Then Go To Your Role
- **Supabase Dev:** `developer_handoffs/supabase_dev/README.md`
- **Tracker Dev:** `developer_handoffs/tracker_dev/README.md`
- **Dashboard Dev:** `developer_handoffs/dashboard_dev/README.md`
- **Portal Dev:** `developer_handoffs/portal_dev/README.md`

---

## Inspiration - What Good Looks Like

Before building anything, review these sites for design inspiration:

| Site | URL | What to Learn |
|------|-----|---------------|
| **Evolving Hockey** | https://evolving-hockey.com | xG models, player cards, WAR |
| **Money Puck** | https://moneypuck.com | Shot maps, game predictions |
| **Natural Stat Trick** | https://naturalstattrick.com | On-ice stats, shift charts |
| **HockeyViz** | https://hockeyviz.com | Heat maps, shot visualization |

**Full list:** See `docs/handoff/INSPIRATION_AND_RESEARCH.md`

---

## Supabase Connection

```
Project URL: https://uuaowslhpgyiudmbvqze.supabase.co
Tables: 12 (3 dimension, 9 fact)
Columns: 317 total
Status: Schema ready, needs deployment
```

---

## ETL Workflow

```bash
# Standard ETL Pipeline
python etl.py                           # Transform raw → output
python scripts/fix_data_integrity.py    # Fix PKs/FKs
python scripts/fix_final_data.py        # Final cleanup
python scripts/etl_validation.py        # Validate
pytest tests/                           # Run 205 tests

# Upload to Supabase
python upload.py
```

---

## Key Files

| File | Purpose |
|------|---------|
| `etl.py` | Main ETL transformation |
| `upload.py` | Supabase uploader |
| `scripts/fix_data_integrity.py` | PK/FK fixes |
| `scripts/fix_final_data.py` | Final data cleanup |
| `scripts/etl_validation.py` | Data validation |
| `scripts/generate_data_dictionary_complete.py` | Generate column docs |

---

## Package Delivery Checklist

When packaging deliverables:
- [ ] Run `scripts/verify_delivery.py` (if exists)
- [ ] Include ALL files (src/, data/raw/, config/, etc.)
- [ ] Verify goals match noradhockey.com
- [ ] Update handoff docs
- [ ] Include HTML previews
- [ ] Update version number in filename

---

## Don't Forget

- **Read INSPIRATION_AND_RESEARCH.md** - Shows what good hockey analytics look like
- **Check data_dictionary/** - Column definitions for all tables
- **Validate against ground truth** - noradhockey.com is source of truth
- **Never delete, only archive** - Move old files to _archive folders

---

*This document should be read by EVERY developer before starting work.*
