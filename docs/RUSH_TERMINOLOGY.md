# Rush vs Carried Terminology

## Background

The tracker originally used "Rush" for zone entry/exit types, but this conflicted with the NHL analytics definition of "rush" (a transition attack).

## Terminology Mapping

| Tracker Term | New Term | Definition |
|--------------|----------|------------|
| ZoneEntry_Rush | ZoneEntry_Carried | Skating the puck into the zone |
| ZoneEntry_RushBreakaway | ZoneEntry_CarriedBreakaway | Breakaway entry |
| ZoneExit_Rush | ZoneExit_Carried | Skating the puck out of the zone |

## Flag Definitions

| Flag | Definition | Count (4 games) |
|------|------------|-----------------|
| `is_rush` | **NHL definition:** Controlled entry + shot within 7 seconds | 142 |
| `is_controlled_entry` | Zone entry with possession (Pass, Carried, CarriedBreakaway) | 338 |
| `is_carried_entry` | Skating puck into zone (subset of controlled) | 266 |
| `is_controlled_exit` | Zone exit with possession | 307 |
| `is_carried_exit` | Skating puck out of zone | 139 |
| `is_rush_calculated` | Quick attack: entry → shot ≤10s AND ≤5 events | 114 |

## NHL Rush Definition

Based on hockey analytics research (JFresh, Corey Sznajder, Eric Tulsky):

> "A rush goal is a goal where a controlled zone entry occurred and a goal was scored within 5-7 seconds without being given away to the opposing team."

Key characteristics:
- **Controlled entry** (carry or pass, not dump-in)
- **Quick shot** before defense sets up (≤7 seconds)
- Defense hasn't established structure

## Backward Compatibility

The ETL handles both old ("Rush") and new ("Carried") terminology:
- Old tracking files with "ZoneEntry_Rush" work
- New tracking files with "ZoneEntry_Carried" work
- Both map to the same type IDs

## dim_zone_entry_type

The dimension table shows:
- `zone_entry_type_code`: Original code from tracker (ZoneEntry_Rush or ZoneEntry_Carried)
- `zone_entry_type_name`: Display name (always "Carried")
- `is_controlled`: Whether entry maintains possession
