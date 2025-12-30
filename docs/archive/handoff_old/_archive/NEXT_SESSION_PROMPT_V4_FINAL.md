# BenchSight Next Session Prompt - V4 FINAL

## 📋 COPY EVERYTHING BELOW THIS LINE:

---

I'm continuing work on **BenchSight**, a hockey analytics ETL project for the NORAD recreational hockey league.
## What I Need Help With Today:
Pretend you are a data scientist/engineer/data QC/accuraty engineer and a supabase etl dev. with a deep domain expertese in hockey. I need you to take the zips (1,2) and add them to the benchsight zip main folder. this is our porject. then i need you to view the pasted data, read the readme master in the main folder and then follow those directions.i need you to then review the doc/handoff folder. there is a beforewestart text and a handoff_doc text review those. i require both of those. then provide me with a summary of the project, next steps.



## 📊 Project Status: 98% Complete

### What's Working (317 player stat columns):
- Full ETL pipeline: Excel → 88 CSV tables
- **72 validations passing** (54 + 8 + 10)
- Core stats: G/A/P, TOI, +/-, Corsi/Fenwick, FO%
- Game Score, Performance vs Rating, xG For/Against/Diff/%
- Shot danger zones (high/med/low estimated), scoring chances
- Rush stats, pass targets, opponent targeting
- H2H, WOWY, Line Combos all populated

### 48 Columns Still Zero (need source data):
1. **XY-dependent** (12): Real danger zone mapping needs XY coordinates
2. **Score state** (6): goals_leading/trailing/tied - no running score in events
3. **Special teams** (3): EN/SH goals - strength not consistently tagged
4. **Micro-stats** (27): hits, puck_retrievals, etc. - not in event vocabulary

### XY Infrastructure Ready But Empty:
- `dim_rinkcoordzones`: 84 zones with danger='low'/'mid'/'high' ✅
- `dim_rinkboxcoord`: 24 boxes with danger levels ✅
- `dim_rink_coord`: 12 simple zones ✅
- `fact_shot_xy`: 0 data rows ❌ (needs XY in events)
- `fact_player_xy_long`: 0 data rows ❌

### Key Technical Details:
```python
# Goal detection
event_type == 'Goal' OR event_detail in ['Goal_Scored', 'Shot_Goal']

# Player roles
event_player_1 = primary (shooter/passer)
event_player_2 = secondary (assist/pass target)
opp_player_1 = primary defender

# XY → Danger Zone Mapping (for when XY exists):
# Use dim_rinkcoordzones: x_min/x_max/y_min/y_max → danger column
```

## 🧠 Memory Notes
```
BenchSight: 98% complete, 317 stats, 72 validations, 48 zero columns.
XY infrastructure ready (dim_rinkcoordzones has danger zones defined).
fact_shot_xy empty - needs XY coordinates in event tracking.
Goals: event_type='Goal' OR event_detail='Shot_Goal'/'Goal_Scored'
```

## 📁 Key Files:
1. `docs/handoff/HANDOFF_FINAL_V5.md` - Complete status with XY notes
2. `data/output/dim_rinkcoordzones.csv` - Danger zone definitions
3. `src/fix_data_accuracy.py` - Latest data fixes



---

## 🚀 ALTERNATIVE SHORT PROMPT:

---

Continuing BenchSight hockey analytics. **98% complete**, 317 stats, 72 validations passing.

**Working**: Game score, xG for/against, shot danger zones (estimated), rush stats, H2H/WOWY.

**48 zero columns** need: (1) XY coordinates for real danger mapping, (2) score state tracking, (3) special teams tags.

**XY Ready**: dim_rinkcoordzones has 84 zones with danger='low'/'mid'/'high'. Just need XY data in events.

Today I need: [YOUR REQUEST]

---

## ⚡ Quick Commands

```bash
python etl.py                              # Full ETL
python src/enhance_all_stats.py            # Stats phase 1
python src/final_stats_enhancement.py      # Stats phase 2
python src/fix_data_accuracy.py            # Data fixes
python scripts/test_validations.py         # 54 tests
python scripts/enhanced_validations.py     # 8 tests
```

## 📊 Zero Column Categories (48 total)

| Category | Count | Blocker |
|----------|-------|---------|
| XY-dependent | 12 | Need XY in events |
| Score state | 6 | Need running score |
| Special teams | 3 | Need EN/SH tags |
| Micro-stats | 27 | Not in event vocab |

## 🎯 Priority Tasks

### P0 - Immediate
- Supabase deployment (DDL ready)
- Load remaining 6 games

### P1 - Enable XY
- Add XY tracking to game tracker
- Map events → dim_rinkcoordzones
- Recalculate danger stats

### P2 - Score State
- Add score_home/score_away to events
- Calculate leading/trailing/tied stats

---

## 📐 XY Mapping Reference

```
dim_rinkcoordzones columns:
- box_id: Zone identifier (OZ01, OZ17, etc.)
- x_min, x_max, y_min, y_max: Boundaries
- danger: 'low', 'mid', 'high'
- zone: 'offensive', 'neutral', 'defensive'
- slot: 'inside', 'outside', 'outside low'

HIGH DANGER ZONES (slot area):
- OZ17: x=69-89, y=-8.5 to 8.5 (prime slot)
- OZ13-OZ16: Inner slot areas

IMPLEMENTATION:
for each shot with (x, y):
    match to zone where x_min <= x <= x_max AND y_min <= y <= y_max
    get danger level from zone
```
