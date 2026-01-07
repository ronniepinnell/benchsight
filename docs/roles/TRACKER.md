# Role: Tracker Developer

**Version:** 3.0  
**Updated:** January 7, 2026

---

## Overview

The BenchSight Tracker replaces Excel-based game tracking with a purpose-built web application. Goal: **Reduce game tracking time from 1 day to ~1 hour**.

---

## Essential Documents (Read in Order)

1. **LLM_REQUIREMENTS.md** - Critical data rules, goal counting
2. **docs/TRACKER_ETL_SPECIFICATION.md** - EXACT export format ETL expects
3. **docs/TRACKER_V3_SPECIFICATION.md** - Complete feature spec
4. **docs/TRACKER_REQUIREMENTS.md** - Detailed requirements v2
5. **docs/TRACKER_DEVELOPER_HANDOFF.md** - Implementation details
6. **docs/SUPABASE_SETUP_GUIDE.md** - Database setup
7. **docs/TRACKING_TEMPLATE_ANALYSIS.md** - ML analysis of existing data

---

## Current Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| **Tracker MVP** | ✅ Complete | docs/html/tracker/benchsight_tracker_v3.html |
| **Supabase Setup** | 📋 Needs User | docs/SUPABASE_SETUP_GUIDE.md |
| **ETL Alignment** | ✅ Specified | docs/TRACKER_ETL_SPECIFICATION.md |
| **Cascading Dropdowns** | ✅ Implemented | From Lists tab in Excel |
| **XY Tracking** | ✅ 10 pts/player | Click on rink SVG |
| **Play Details per Player** | ✅ Implemented | s/u, offensive/defensive |
| **NORAD Validation** | ⏳ Needs Supabase | Compare vs official goals |

---

## Critical Data Rules

### Goal Counting (MEMORIZE THIS)
```python
# CORRECT - Goals are ONLY:
event_type = 'Goal' AND event_detail = 'Goal_Scored'

# WRONG - Shot_Goal is the SHOT, not the goal:
event_detail = 'Shot_Goal'  # THIS IS WRONG
```

### Player Roles
| Role | Meaning | Example |
|------|---------|---------|
| event_team_player_1 | PRIMARY | Scorer, shooter, passer |
| event_team_player_2 | SECONDARY | Primary assist, receiver |
| event_team_player_3 | TERTIARY | Secondary assist |
| opp_team_player_1 | OPP PRIMARY | Defending player |
| opp_team_player_2 | OPP SECONDARY | Other defender |

### Time Format
- **Game Clock:** MM:SS counting DOWN from 18:00 (NORAD) or 20:00 (NHL)
- **Export Format:** shift_start_min, shift_start_sec as separate columns

### Success/Unsuccessful
- s = successful (shot on net, pass completed, takeaway)
- u = unsuccessful (shot missed, pass intercepted, giveaway)

---

## Export Format (CRITICAL)

### Events Tab: LONG FORMAT
One row PER PLAYER PER EVENT. If event has 3 players → 3 rows.

### Shifts Tab: WIDE FORMAT
One row PER SHIFT with all players in columns.

### XY Data: SEPARATE CSV
game_id, link_event_index, Player, X, Y, X2, Y2, ... X10, Y10

---

## Keyboard Shortcuts

| Key | Action | Key | Action |
|-----|--------|-----|--------|
| S | Shot | P | Pass |
| F | Faceoff | G | Goal |
| T | Turnover | Z | Zone |
| V | Save | R | Rebound |
| D | DeadIce | X | Stoppage |
| N | Penalty | O | Possession |
| H | Home team | A | Away team |
| Enter | Log event | Esc | Clear form |
| Shift+S | Log shift | Ctrl+Z | Undo |

---

## Files Reference

| File | Purpose |
|------|---------|
| docs/html/tracker/benchsight_tracker_v3.html | Main tracker app |
| docs/TRACKER_ETL_SPECIFICATION.md | Export format spec |
| docs/TRACKER_V3_SPECIFICATION.md | Feature spec |
| docs/TRACKER_REQUIREMENTS.md | Detailed requirements |
| docs/TRACKER_DEVELOPER_HANDOFF.md | Dev continuation guide |
| docs/SUPABASE_SETUP_GUIDE.md | Database setup |
| docs/TRACKING_TEMPLATE_ANALYSIS.md | ML analysis |

---

**END OF TRACKER ROLE DOCUMENT**
