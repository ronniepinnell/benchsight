# BenchSight - Hockey Analytics Platform

A comprehensive analytics platform for the NORAD recreational hockey league.

## 🚀 Quick Start

1. **Read the handoff document**: `docs/HANDOFF.md`
2. **Run validation**: `python scripts/validate_stats.py`
3. **Check requirements**: `docs/PROJECT_REQUIREMENTS.md`

## 📊 Project Status

- **Stats Validated**: 115
- **Games Tracked**: 8
- **Last Updated**: 2024-12-28

## 📁 Key Files

| File | Purpose |
|------|---------|
| `docs/HANDOFF.md` | Session handoff with context prompts |
| `docs/PROJECT_REQUIREMENTS.md` | Full requirements & history |
| `docs/VALIDATION_LOG.tsv` | 115 validated stat calculations |
| `scripts/validate_stats.py` | Stat validation tests |

## 🎯 Current Focus

Rebuilding `fact_player_game_stats` with all validated counting rules.

## ⚙️ Running Validation

```bash
python scripts/validate_stats.py
```

Expected output: `🎉 ALL IMPLEMENTED TESTS PASSED!`

## 📋 Documentation

- `docs/HANDOFF.md` - Session context and quick start
- `docs/PROJECT_REQUIREMENTS.md` - Full requirements
- `docs/SCHEMA.md` - Database schema
- `docs/DATA_DICTIONARY.md` - Column definitions

## 🔧 Tech Stack

- Python 3.12
- pandas
- PostgreSQL (staging)
- Power BI (dashboards)

---

*BenchSight - Making hockey data accessible*
