# BenchSight - Next Prompt Template

Copy and paste this prompt to continue work on BenchSight in a new chat session.

---

## PROMPT START

I'm continuing work on BenchSight, a hockey analytics platform for the NORAD recreational hockey league. Here's the current state:

### Project Overview
- **ETL Pipeline:** Python-based, transforms raw Excel tracking files to normalized CSVs
- **Database:** Supabase PostgreSQL at https://uuaowslhpgyiudmbvqze.supabase.co
- **Status:** 293 tests passing, 317 columns across 51 tables

### Key Tables
- fact_events (wide format events)
- fact_events_player (long format - player per event)
- fact_shifts (shift data with on-ice players)
- fact_player_game_stats (29 player metrics per game)
- fact_team_game_stats (18 team metrics per game)
- fact_goalie_game_stats (19 goalie metrics including microstats)
- fact_h2h (head-to-head matchups)
- fact_wowy (with-or-without-you analysis)

### Critical Business Rules
1. **player_role is CRITICAL:** Only event_team_player_1 gets stat credit
2. **Shots = Corsi:** All shot attempts (60-70 per team is correct)
3. **Assists in play_detail1:** AssistPrimary, AssistSecondary
4. **Goals via:** event_type "Goal" OR event_detail "Shot_Goal"/"Goal_Scored"

### Known Issues
- Pass completion missing in games 18977, 18981, 18987
- Assist tracking ~83% match rate (tracking gaps)
- Tracker needs fixes for roster loading and event ordering

### Workflow
```bash
python etl.py
python scripts/fix_data_integrity.py
python scripts/fix_final_data.py
python scripts/etl_validation.py
pytest tests/
```

### My Request Today
[DESCRIBE WHAT YOU WANT TO WORK ON]

### Attached Files (if any)
[DESCRIBE ANY FILES YOU'RE ATTACHING]

---

## PROMPT END

---

## Alternative Prompts for Specific Tasks

### For Tracker Development
```
I'm continuing BenchSight tracker development. The tracker is an HTML/JavaScript interface for recording hockey game events. Current issues:
- Roster loading from BLB tables fails
- Event ordering bugs
- Missing games in dropdown

Please help me [SPECIFIC TASK].

Key files: tracker/tracker_v19.html, data/raw/games/{game_id}/
```

### For Dashboard Development
```
I'm starting BenchSight dashboard development. Data is ready in Supabase PostgreSQL. I need dashboards for:
- League standings and leaders
- Team analytics
- Player stats
- Game summaries
- Goalie analytics

Please help me [SPECIFIC TASK].

Database: https://uuaowslhpgyiudmbvqze.supabase.co
Key tables: fact_player_game_stats, fact_team_game_stats, fact_goalie_game_stats
```

### For ETL Fixes
```
I'm fixing BenchSight ETL issues. Current problem:
[DESCRIBE THE ISSUE]

Workflow:
python etl.py → fix_data_integrity.py → fix_final_data.py → etl_validation.py → pytest

Please help me debug/fix this.
```

### For Data Analysis
```
I need help analyzing BenchSight data. Question:
[YOUR QUESTION]

Database: Supabase PostgreSQL
Tables: fact_events, fact_player_game_stats, fact_team_game_stats
Ground truth: noradhockey.com game pages
```

---

## Key File References

```
Documentation:
- docs/handoff/MASTER_INSTRUCTIONS.md
- docs/handoff/HONEST_ASSESSMENT_AND_NEXT_STEPS.md
- docs/handoff/SCHEMA_AND_ERD.md

Data:
- data/raw/games/{game_id}/{game_id}_tracking.xlsx
- data/output/*.csv
- data/output/data_dictionary/*.csv

Scripts:
- etl.py
- scripts/fix_data_integrity.py
- scripts/fix_final_data.py
- scripts/etl_validation.py
- scripts/generate_data_dictionary_complete.py

Tests:
- tests/test_etl.py

Tracker:
- tracker/tracker_v19.html
```

---

## Memory Joggers

If Claude doesn't remember something, reference these:

- "BenchSight uses event_team_player_1 for stat credit"
- "Shots = Corsi (all attempts, not just on goal)"
- "Assists are in play_detail1 column"
- "Primary keys use format {prefix}{game_id}{5d}"
- "Always run fix_data_integrity.py after etl.py"
- "Check noradhockey.com for ground truth validation"

---

*Last Updated: December 2024*
