# Rush Definitions - BenchSight v26.3

## The Problem

The tracker uses "Rush" to describe zone entries/exits where the puck is **carried** with speed. But this is NOT the same as an NHL analytics "rush" which requires a **quick shot** after the entry.

## NHL Definition of Rush

Based on hockey analytics research (JFresh, Corey Sznajder, etc.):

> "A rush goal is a goal where a controlled zone entry occurred and a goal was scored within 5-7 seconds without being given away to the opposing team."

Key components:
1. **Controlled entry** - carrying or passing the puck in (not dump-in)
2. **Quick shot** - before defense can set up (typically ≤7 seconds)

## BenchSight Flags

### Entry/Exit Control Flags

| Flag | Count | Definition |
|------|-------|------------|
| `is_zone_entry` | 495 | Successful zone entry |
| `is_zone_exit` | 476 | Successful zone exit |
| `is_controlled_entry` | 338 | Entry with puck control (Pass/Carried/CarriedBreakaway) |
| `is_carried_entry` | 266 | Tracker's "Rush" type - carried in with speed |
| `is_controlled_exit` | 307 | Exit with puck control (Pass/Carried) |
| `is_carried_exit` | 139 | Tracker's "Rush" exit - carried out with speed |

### Rush Flags

| Flag | Count | Definition |
|------|-------|------------|
| **`is_rush`** | **142** | **NHL definition: controlled entry + shot ≤7 seconds** |
| `is_rush_calculated` | 114 | Any entry → shot ≤10s AND ≤5 events |

## Dim Table Changes

Renamed "Rush" to "Carried" in dim tables for clarity:

**dim_zone_entry_type:**
- ZE0011: `ZoneEntry_Rush` → name: "Carried"
- ZE0012: `ZoneEntry_RushBreakaway` → name: "CarriedBreakaway"

**dim_zone_exit_type:**
- ZX0011: `ZoneExit_Rush` → name: "Carried"

The `zone_entry_type_code` still contains "Rush" (from raw data), but `zone_entry_type_name` is now "Carried".

## Player Stats

All `rush_*` columns now use `is_rush` (NHL definition):
- `rush_involvement` = involvement on true rushes
- `rush_off_goal_generated` = goals on true rushes
- etc.

For "any quick attack" metrics, use `rush_calc_*` columns:
- `rush_calc_off` = involvement on any entry → quick shot
- `rush_calc_off_goal` = goals on any quick attack
