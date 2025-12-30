# BenchSight Portal Admin Developer - Next Prompt

Copy and paste this prompt to start or continue portal development.

---

## PROMPT START

I'm building an admin portal for BenchSight, a hockey analytics platform. The portal provides UI access to operations currently done via command line.

### System Overview
- **Database:** Supabase PostgreSQL at `https://uuaowslhpgyiudmbvqze.supabase.co`
- **ETL Pipeline:** Python scripts that transform raw tracking data
- **Current State:** All operations done via bash/terminal

### Portal Features Needed

**1. ETL Pipeline Control**
- Run Full ETL (etl.py → fix_data_integrity.py → fix_final_data.py)
- Run Validation Only
- Run Tests (pytest)
- View real-time logs
- See execution history

**2. Database Table Viewer**
- Browse all 12 tables
- Filter/search data
- Download as CSV
- View row counts

**3. Data Upload**
- Upload CSV to specific table
- Upload new tracking file (xlsx)
- Bulk upload all CSVs

**4. Validation Dashboard**
- Run data quality checks
- View errors/warnings
- Ground truth comparison

**5. Documentation Hub**
- View all docs
- Download data dictionaries
- Access guides

**6. System Health**
- Supabase connection status
- Table statistics
- Recent activity

**7. Game Management**
- List all games
- Add/delete/reprocess games

### Tech Stack Preference
[React/Vue/Svelte] for frontend
[FastAPI/Flask/Node] for backend

### What I Need Help With Today
[DESCRIBE YOUR SPECIFIC TASK]

---

## PROMPT END

---

## Quick Reference

### Scripts to Execute
```bash
# Full ETL
python etl.py
python scripts/fix_data_integrity.py
python scripts/fix_final_data.py
python scripts/etl_validation.py

# Tests
pytest tests/ -v --tb=short
```

### Tables (12 total)
```
Dimensions: dim_player, dim_team, dim_schedule
Facts: fact_events, fact_events_player, fact_shifts, 
       fact_shifts_player, fact_player_game_stats,
       fact_team_game_stats, fact_goalie_game_stats,
       fact_h2h, fact_wowy
```

*Last Updated: December 2024*
