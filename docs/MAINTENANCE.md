# BenchSight Maintenance Guide

**Version:** v29.0  
**Updated:** 2026-01-13

---

## Pre-Delivery Checklist

Before packaging any version:

- [ ] Clean output: `rm -rf data/output/*`
- [ ] Run ETL: `python -c "from src.core.base_etl import main; main()"`
- [ ] Run table modules: dimension_tables, core_facts, event_analytics, shift_analytics, remaining_facts
- [ ] Verify 0 errors in validation output
- [ ] Check goal counts match schedule (17 total across 4 games)
- [ ] Update CHANGELOG.md
- [ ] Update TODO.md
- [ ] Update version in docs/VERSION.txt

---

## Critical Business Rules

### Goal Counting (NEVER CHANGE)
```python
# Goals ONLY via:
event_type == 'Goal' AND event_detail == 'Goal_Scored'

# Shot_Goal is the SHOT, not the goal
# event_player_1 = primary player (scorer)
```

### Tracking File Format
- Sheet names: `events`, `shifts`
- Column names end with `_` (stripped during ETL)
- Multiple rows per goal (scorer + assisters) - dedupe by event_index

---

## Common Issues

### Supabase Upload Failures
**Symptom:** Column mismatch errors  
**Cause:** Column names > 63 chars get truncated  
**Fix:** Shorten column names in ETL output

### Missing Goals
**Symptom:** fact_events has fewer goals than schedule  
**Cause:** Usually tracking file data entry issue  
**Check:** Compare unique event_index in raw file vs schedule

### Dropdown Not Loading
**Symptom:** Tracker dropdowns show limited options  
**Cause:** Supabase client variable mismatch  
**Fix:** Ensure using `S.sb` (not `S.sbClient`)

---

## File Locations

| Purpose | Location |
|---------|----------|
| Raw tracking files | `data/raw/games/{game_id}/` |
| ETL output | `data/output/` |
| Config | `config/` |
| Tracker UI | `ui/tracker/index.html` |
| Docs | `docs/` |

---

## Validation Commands

```bash
# Run ETL with clean slate
python run_etl.py --wipe

# Check table counts
ls data/output/*.csv | wc -l

# Verify goal counts
grep ",Goal," data/output/fact_events.csv | grep "Goal_Scored" | wc -l

# Check specific game
grep "^18969" data/output/fact_player_game_stats.csv
```

---

## Version Naming

Format: `benchsight_v{MAJOR}.{MINOR}.zip`

- MAJOR: Increments with significant changes
- MINOR: Increments with fixes/updates within a session

Current: v23.0

---

*Keep this updated with each release*
