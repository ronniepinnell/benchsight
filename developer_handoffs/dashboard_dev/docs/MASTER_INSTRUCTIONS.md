# BenchSight Master Instructions for Next Chat

## Project Overview

BenchSight is a comprehensive hockey analytics platform for the NORAD recreational hockey league. The system processes game tracking data through an ETL pipeline and outputs to a Supabase PostgreSQL database.

## Current State (December 2024)

### ✅ Completed
- **ETL Pipeline:** 317 columns, 293 tests passing
- **Database:** Supabase PostgreSQL at `https://uuaowslhpgyiudmbvqze.supabase.co`
- **Ground Truth Validation:** 100% game scores, 96% goals, 91% assists
- **Data Dictionary:** 10 comprehensive files covering all tables
- **Key Standardization:** `{prefix}{game_id}{5d}` format for all PKs/FKs

### 📊 Tables in Production
```
DIMENSION TABLES:
- dim_player (player_id, player_name, etc.)
- dim_team (team_id, team_name)
- dim_schedule (game_id, home_team, away_team, scores)

FACT TABLES:
- fact_events (wide format - one row per event)
- fact_events_player (long format - one row per player per event)
- fact_shifts (shift-level data with on-ice players)
- fact_shifts_player (player-shift assignments)
- fact_player_game_stats (29 columns - player aggregates)
- fact_team_game_stats (18 columns - team aggregates)
- fact_goalie_game_stats (19 columns - goalie stats + microstats)
- fact_h2h (head-to-head matchups)
- fact_wowy (with-or-without-you analysis)
```

### 🔑 Critical Business Rules

1. **player_role is CRITICAL:** Only `event_team_player_1` gets stat credit
2. **Shots = Corsi:** All shot attempts (60-70 per team is CORRECT)
3. **SOG requires filter:** `event_detail IN (Shot_OnNetSaved, Shot_Goal, ...)`
4. **Assists in play_detail1:** `AssistPrimary`, `AssistSecondary`
5. **Logical Shifts:** 10-14 typical (continuous periods, not micro-shifts)

### ⚠️ Known Data Gaps
- Pass completion missing in games 18977, 18981, 18987
- Save events show dual perspective (shooter + goalie both credited)
- Assist tracking ~83% match rate due to tracking gaps

## Workflow Commands

```bash
# Full ETL Pipeline
python etl.py
python scripts/fix_data_integrity.py
python scripts/fix_final_data.py
python scripts/etl_validation.py
pytest tests/

# Generate Data Dictionary
python scripts/generate_data_dictionary_complete.py

# Upload to Supabase
python upload.py
```

## File Locations

```
/data/raw/games/{game_id}/     # Raw tracking files
/data/output/                   # ETL output CSVs
/data/output/data_dictionary/   # Data dictionaries
/scripts/                       # Utility scripts
/tracker/                       # Game tracker HTML
/docs/handoff/                  # Handoff documentation
```

## Delivery Checklist

Before packaging any delivery:
1. Run `python scripts/verify_delivery.py`
2. Include ALL files (src/, data/raw/, config/, dashboard/, etc.)
3. Verify goals match noradhockey.com
4. Include updated handoff docs and HTML previews
5. Package as `benchsight_FINAL_vX_DESCRIPTION.zip`

## Key Contacts & Resources

- **Supabase Dashboard:** https://supabase.com/dashboard/project/uuaowslhpgyiudmbvqze
- **Ground Truth:** noradhockey.com game pages
- **Inspiration Docs:** `/docs/handoff/` folder

## Next Steps (Prioritized)

### Immediate
1. Tracker fixes: roster loading from BLB tables
2. Event/shift ordering and editing capabilities
3. Ensure all tracked games appear in dropdown

### Short-term
1. Phase 3: Linked events tables
2. Possession time calculations
3. Event chains for xG modeling

### Medium-term
1. XY coordinate integration
2. Dashboard development
3. Real game data testing

## Stat Definitions Quick Reference

| Stat | Formula | Source |
|------|---------|--------|
| Goals | COUNT(event_type="Goal" AND player_role="event_team_player_1") | fact_events |
| Assists | COUNT(play_detail1 CONTAINS "Assist") | fact_events_player |
| Shots (Corsi) | COUNT(event_type="Shot") | fact_events |
| SOG | Shots WHERE event_detail IN (OnNet types) | fact_events |
| FO Wins | event_team_player_1 on Faceoff events | fact_events |
| FO Losses | opp_team_player_1 on Faceoff events | fact_events |
| TOI | SUM(shift_duration) for player's shifts | fact_shifts_player |
| Save% | saves / shots_against * 100 | fact_goalie_game_stats |

---

*Always provide complete project zip with updated docs, updated handoff docs, and all HTML previews.*
