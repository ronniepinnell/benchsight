# LLM Handoff Guide

**Version:** 14.01  
**Updated:** January 7, 2026

---

## Quick Start for New Chat

1. Read `LLM_REQUIREMENTS.md` first (CRITICAL)
2. Check `config/VERSION.json` for current version
3. Run `python scripts/utilities/doc_consistency.py --new-chat` to bump version
4. Read `CHANGELOG.md` for recent history

---

## Current State

| Component | Status |
|-----------|--------|
| **ETL Pipeline** | ✅ 59 tables, 17 goals verified |
| **Tracker App** | ✅ v3 complete at `docs/html/tracker/` |
| **Supabase Setup** | ⏳ Needs user to configure |
| **Documentation** | ✅ All HTML generated |
| **Tests** | ✅ 32 Tier 1, 17 Tier 2 passing |

---

## Key Files

### Must Read
- `LLM_REQUIREMENTS.md` - Critical rules
- `config/IMMUTABLE_FACTS.json` - Verified goal counts (DO NOT MODIFY)
- `config/VERSION.json` - Version control

### Tracker Docs
- `docs/TRACKER_ETL_SPECIFICATION.md` - Export format
- `docs/TRACKER_REQUIREMENTS.md` - Requirements
- `docs/SUPABASE_SETUP_GUIDE.md` - Database setup

### Scripts
- `scripts/pre_delivery.py` - Master pipeline (RUN THIS)
- `scripts/bs_detector.py` - Verification
- `scripts/utilities/doc_consistency.py` - Version management

---

## Goal Counting Rule (MEMORIZE)

```python
# CORRECT
event_type = 'Goal' AND event_detail = 'Goal_Scored'

# WRONG - Shot_Goal is the shot, not the goal
event_detail = 'Shot_Goal'  # THIS IS WRONG
```

---

## Version Naming

**Format:** `v{CHAT}.{OUTPUT}`

- New chat: Run `doc_consistency.py --new-chat`
- New output: Run `doc_consistency.py --bump`

---

## Pre-Delivery Checklist

```bash
# Run this BEFORE creating any package
python scripts/pre_delivery.py
```

This automatically:
1. Wipes output
2. Runs ETL
3. Verifies goals
4. Runs tests
5. Bumps version
6. Fixes docs
7. Creates package

---

## Recent Work (Chat 13-14)

1. ✅ Tracker MVP implemented
2. ✅ Tracker v3 with all features
3. ✅ ETL export format specified
4. ✅ Cascading dropdowns from Lists tab
5. ✅ XY tracking (10 pts/player/event)
6. ✅ Play details per player with s/u
7. ✅ Shift tracking with intermissions
8. ⏳ Supabase needs user setup
9. ⏳ NORAD validation needs Supabase

---

## Next Steps

1. User sets up Supabase using guide
2. Upload dim tables to Supabase
3. Test tracker with real data
4. Track new games
5. Run ETL on tracked data

---

**END OF HANDOFF**
