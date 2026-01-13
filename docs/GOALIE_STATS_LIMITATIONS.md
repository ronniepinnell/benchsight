# Goalie Stats Limitations & Required Data

## v28.1 Status Update

**FIXED in v28.1:**
- ✅ Rebound attribution - Now goalie-specific via prev_event_id linkage
- ✅ Rush/Set Play GA - Now calculated using time_since_zone_entry on goals
- ✅ Multi-shot SV% - Now calculated using sequence_shot_count on goals

**Still Limited:**
- ⚠️ Goal location (glove/blocker side) - No data available
- ⚠️ Second chance GA - Partial (can detect via sequence, not rebound linkage)

---

## Remaining Limitations

### 1. Body Location Goals Against (Set to 0)

**Affected Columns:**
- `glove_side_ga`
- `blocker_side_ga`
- `five_hole_ga`
- `glove_side_sv_pct` (always 100% due to 0 GA)
- `blocker_side_sv_pct` (always 100% due to 0 GA)
- `five_hole_sv_pct` (always 100% due to 0 GA)

**Current Behavior:** All set to 0. We know save body locations from Save events (event_detail_2), but Goal events don't have goal location data.

**Data Needed to Fix:**
```
Goal events need ONE of:
- goal_location: "glove_side", "blocker_side", "five_hole", etc.
- event_detail_2: Populated with goal location
```

**Tracker Change Needed:**
Add a "Goal Location" dropdown to goal entry:
- Glove Side (Low)
- Glove Side (High)
- Blocker Side (Low)
- Blocker Side (High)
- Five Hole
- Short Side
- Far Side

---

### 2. Second Chance Goals (Partial)

**Current Behavior:** We can detect goals in multi-shot sequences via sequence_shot_count, but we can't directly link a goal to a preceding rebound event.

**What We Have:**
- sequence_shot_count on goals (0=first shot, 1=second shot, etc.)
- 13 goals with sequence_shot_count=0, 2 with 1, 1 with 2

**Data Needed for Full Attribution:**
```
Goal events need:
- is_second_chance: Boolean flag
- preceding_rebound_id: Link to the Rebound event
```

---

## What's Now Working (v28.1)

### Rush/Set Play GA ✅
Goals now have `time_since_zone_entry` populated (100% of goals), enabling:
- Rush GA: Goals <5s after zone entry
- Quick Attack GA: Goals 5-10s after zone entry  
- Set Play GA: Goals >10s after zone entry

### Rebound Attribution ✅
Rebounds now linked to specific goalies via `prev_event_id`:
- 133/139 rebounds preceded by Save events
- prev_event_id links to the save's event_id
- Each goalie now shows their own rebound outcomes

### Multi-Shot Sequence SV% ✅
Goals have `sequence_shot_count`, enabling:
- Detection of goals during multi-shot sequences
- Actual multi_shot_sv_pct calculations (e.g., Wyatt: 95.7% in Game 18969)

---

## Future Enhancement: Goal Location from shot_xy

### Available Data

**dim_net_location** (10 zones):
```
NL01 - Glove High
NL02 - Glove Low
NL03 - Blocker High
NL04 - Blocker Low
NL05 - Five Hole
NL06 - Short Side High
NL07 - Short Side Low
NL08 - Far Side High
NL09 - Far Side Low
NL10 - Crossbar
```

**fact_shot_event** columns:
- `net_target_x`, `net_target_y` - Target coordinates
- `net_location_id` - FK to dim_net_location

**fact_shot_xy** columns (currently 0 rows):
- `shot_x`, `shot_y` - Shot origin coordinates
- `target_x`, `target_y` - Target coordinates
- `distance`, `angle` - Calculated fields
- `danger_zone` - Danger classification

### Once You Have XY Data

When you start tracking shot XY coordinates:

1. fact_shot_xy will populate with shot locations
2. fact_shot_event.net_location_id can be populated
3. We can then calculate:
   - `glove_side_ga` (NL01, NL02)
   - `blocker_side_ga` (NL03, NL04)
   - `five_hole_ga` (NL05)
   - Short/far side GA
   - Goal location SV%

### Tracker Change for Goal Location

Add to Goal entry in tracker:
```
Goal Location: [dropdown]
- Glove Side High (NL01)
- Glove Side Low (NL02)
- Blocker Side High (NL03)
- Blocker Side Low (NL04)
- Five Hole (NL05)
- Short Side High (NL06)
- Short Side Low (NL07)
- Far Side High (NL08)
- Far Side Low (NL09)
- Crossbar (NL10)
```

This will enable full body location GA tracking for goalies.
