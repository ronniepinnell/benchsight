# BENCHSIGHT QUICK HANDOFF
## TL;DR for New LLM Sessions

**Project:** Hockey analytics platform for NORAD rec league
**User:** Ronnie - SQL Server expert, building data pipeline
**Status:** MVP Complete, Production Ready
**Last Session:** Dec 27, 2025 - Session 2 (continuing after message limit)

### ⚠️ SESSION CONTINUITY NOTES
- Previous chat hit message limits during dashboard work
- User uploaded benchsight_merged.zip + raw.zip to continue
- Raw data now integrated into data/raw/games/
- See docs/CHANGELOG.md for version history

---

## WHAT EXISTS

| Component | File | Status |
|-----------|------|--------|
| Main UI | orchestrator.py | ✅ Done |
| Tracker | tracker_v16.html | ✅ Done |
| Dashboards | html/*.html (10 pages) | ✅ Done |
| Data Export | export_all_data.py | ✅ Done |
| Database | sql/setup_complete_database.sql | ✅ Done |
| Docs | docs/LLM_HANDOFF.md | ✅ Done |
| Power BI | powerbi/POWERBI_INTEGRATION.md | ✅ Done |

## NEW DASHBOARDS (Dec 27)
- standings.html - League standings (10 NORAD teams)
- team_profile.html - Team profiles with roster/schedule
- player_comparison.html - Side-by-side player stats

## DATA COUNTS

- 552 games in schedule
- 8 games fully tracked
- 335 players total
- 10 active NORAD teams (no divisions)
- 24,089 events
- 47 CSV output files

## KEY COMMANDS

```bash
python orchestrator.py     # Main UI at localhost:5001
python export_all_data.py  # Export CSVs
python extract_roster.py --all  # Extract rosters
```

## USER PREFERENCES

- UI over CLI
- Single entry point
- Wix-embeddable dashboards
- SQL Server background
- Plans Power BI integration

## LIKELY NEXT REQUESTS

1. Power BI connection
2. More dashboard pages
3. Advanced hockey stats
4. Deployment help

## FILES TO READ FIRST

1. `docs/LLM_HANDOFF.md` - Full details
2. `PROJECT_STATUS.md` - Current state
3. `orchestrator.py` - Main app

---

*Last Updated: December 27, 2025 (Session 2)*
*See docs/CHANGELOG.md for version history*
