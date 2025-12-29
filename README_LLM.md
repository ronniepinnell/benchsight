# BenchSight - Instructions for AI Assistants
**Last Updated:** 2024-12-28
**Project:** Hockey Analytics Platform for NORAD League

---

## 🚨 READ THIS FIRST

**THE DATA IS CURRENTLY BROKEN.** The validation rules are documented but NOT yet applied to the output files. Your first priority should be rebuilding the data with correct rules.

---

## Quick Context Prompt

Copy this to start any session:

```
You are a senior data engineer working on BenchSight, a hockey analytics platform 
for the NORAD recreational hockey league. You're helping rebuild the ETL pipeline.

CRITICAL CONTEXT:
- 115 stats validated with correct counting rules (see docs/VALIDATION_LOG.tsv)
- THE DATA FILES ARE STILL WRONG - they use old incorrect calculations
- Key bugs found: goals double-counted, assists in wrong column, FO logic backwards

PRIORITY TASKS (in order):
1. Run: python -m src.etl_orchestrator --all
2. Validate output against NORAD website
3. Reset Supabase: run sql/supabase_reset.sql
4. Upload data: python supabase_setup.py

READ THESE FILES FIRST:
1. docs/HONEST_ASSESSMENT.md - Current state (brutally honest)
2. docs/HANDOFF.md - Full context and rules
3. docs/VALIDATION_LOG.tsv - Correct counting rules
4. docs/PROJECT_REQUIREMENTS.md - Full requirements
```

---

## 📁 Key Files (Priority Order)

| File | Purpose | Read When |
|------|---------|-----------|
| `docs/HONEST_ASSESSMENT.md` | Brutally honest current state | ALWAYS FIRST |
| `docs/HANDOFF.md` | Session context, rules, roadmap | Starting any work |
| `docs/VALIDATION_LOG.tsv` | 115 validated stat calculations | Building/fixing stats |
| `docs/PROJECT_REQUIREMENTS.md` | Full requirements & history | Understanding scope |
| `scripts/validate_stats.py` | Validation test script | Before any delivery |
| `src/etl_orchestrator.py` | Flexible ETL pipeline | Running ETL |
| `sql/supabase_reset.sql` | Database reset script | Resetting Supabase |

---

## 🔧 Key Commands

```bash
# Run full ETL rebuild
python -m src.etl_orchestrator --all

# Run just dimensions
python -m src.etl_orchestrator --dims

# Run just facts
python -m src.etl_orchestrator --facts

# Run specific games
python -m src.etl_orchestrator --games 18969,18977

# Run validation tests
python scripts/validate_stats.py

# Run all pytest tests
python -m pytest tests/ -v
```

---

## ⚠️ Critical Bugs (ALREADY FOUND - USE CORRECT RULES)

| Bug | Wrong Way | Correct Way |
|-----|-----------|-------------|
| Goals | `event_detail LIKE '%Goal%'` | `event_type = 'Goal' AND player_role = 'event_team_player_1'` |
| Assists | Look in event roles | `play_detail LIKE 'Assist%'` |
| FO Wins | `event_successful = 's'` | `player_role = 'event_team_player_1'` |
| FO Losses | `event_successful = 'u'` | `player_role = 'opp_team_player_1'` |
| Shots | Include all Shot events | `event_type = 'Shot'` only (not Goal) |
| Plus/Minus | From events | From SHIFTS (home_team_plus/minus columns) |

---

## 📊 Data Files Status

| File | Status | Notes |
|------|--------|-------|
| `data/output/fact_events_player.csv` | ✅ OK | Correct structure |
| `data/output/fact_shifts_player.csv` | ✅ OK | Has logical shift columns |
| `data/output/fact_player_game_stats.csv` | ❌ WRONG | Needs rebuild with correct rules |
| `data/output/fact_goalie_game_stats.csv` | ⚠️ PARTIAL | Basic stats only |
| `data/output/dim_*.csv` | ✅ OK | Dimensions are fine |

---

## 🎯 Validation Checkpoints

After any ETL run, verify these for game 18969:

| Player | Stat | Correct Value |
|--------|------|---------------|
| Keegan Mantaro | goals | 2 |
| Keegan Mantaro | assists | 1 |
| Keegan Mantaro | fo_wins | 11 |
| Keegan Mantaro | fo_losses | 11 |
| Keegan Mantaro | pass_attempts | 17 |
| Wyatt Crandall | saves | 37 |
| Wyatt Crandall | goals_against | 4 |

If these don't match, the ETL is still broken.

---

## 🗂️ Project Structure

```
benchsight_github/
├── docs/                    # Documentation (READ FIRST)
│   ├── HONEST_ASSESSMENT.md # Current state - brutally honest
│   ├── HANDOFF.md           # Session context & rules
│   ├── VALIDATION_LOG.tsv   # 115 validated stats
│   └── PROJECT_REQUIREMENTS.md
├── src/
│   ├── etl_orchestrator.py  # Main ETL (UNTESTED)
│   └── ...
├── scripts/
│   └── validate_stats.py    # Validation script
├── sql/
│   └── supabase_reset.sql   # Database reset
├── data/
│   ├── raw/                 # Source Excel files
│   └── output/              # CSV outputs (SOME WRONG)
└── tests/                   # Pytest tests
```

---

## 🚫 Don't Do These Things

1. **Don't trust fact_player_game_stats.csv** - It's wrong
2. **Don't skip validation** - Always run validate_stats.py
3. **Don't assume Supabase is correct** - It's probably garbage
4. **Don't add features before fixing data** - Priority is correct data
5. **Don't document without shipping** - Run the code first

---

## ✅ Do These Things

1. **Read HONEST_ASSESSMENT.md first** - Know the real state
2. **Run ETL and validate** - Ship working data
3. **Check against NORAD** - Cross-reference official stats
4. **Test incrementally** - One game, then all games
5. **Commit working code** - Don't leave broken state

---

## 📞 Key Context for Ronnie's Project

- **League:** NORAD recreational hockey
- **Data source:** Excel tracking files per game
- **Target:** Power BI dashboards
- **Database:** Supabase (PostgreSQL)
- **Games tracked:** 18965, 18969, 18977, 18981, 18987, 18991, 18993, 19032
- **Reference game:** 18969 (most complete tracking)

---

## 🔑 Supabase Credentials

```
URL: https://uuaowslhpgyiudmbvqze.supabase.co
Project: BenchSight
```

Service key is in `supabase_setup.py` (don't commit to public repo).

---

*This README is for AI assistants. For human-readable docs, see docs/README_FOR_HUMANS.txt*
