# XY Detail Sheet Export Example (Aligned with Supabase)

## Supabase Tables Reference

Your Supabase tables:
- `fact_puck_xy_long`: puck_xy_key, event_id, game_id, point_number, x, y, distance_to_net, angle_to_net
- `fact_player_xy_long`: player_xy_key, event_id, game_id, player_id, player_name, player_role, is_event_team, point_number, x, y, distance_to_net, angle_to_net

## Proposed Excel Export Format (for ETL → Supabase)

**Sheet name:** `xy_detail` or `xy_trajectories`

---

## XY Detail Sheet Columns

| Column | Type | Description | Example | Maps to Supabase |
|--------|------|-------------|---------|------------------|
| `game_id` | BIGINT | Game identifier | `19045` | → `game_id` |
| `event_index` | INTEGER | Event identifier (matches events sheet) | `1001` | → `event_id` (via lookup) |
| `entity_type` | TEXT | 'puck' or 'player' | `puck` | Determines table |
| `player_game_number` | INTEGER | Player number (if entity_type='player') | `14` | → `player_id` (via lookup) |
| `point_number` | INTEGER | Sequence number (1, 2, 3, ... up to 10) | `1` | → `point_number` |
| `x` | DOUBLE PRECISION | Raw X coordinate (center-relative) | `75.5` | → `x` (raw) |
| `y` | DOUBLE PRECISION | Raw Y coordinate (center-relative) | `10.2` | → `y` (raw) |
| `x_standardized` | DOUBLE PRECISION | Standardized X coordinate (offense always +x) | `75.5` | → New column |
| `y_standardized` | DOUBLE PRECISION | Standardized Y coordinate | `10.2` | → New column |
| `is_standardized` | BOOLEAN | Flag: 1 if coordinates were flipped, 0 if unchanged | `0` | → New column |
| `zone` | TEXT | Event zone (o/d/n) | `o` | For standardization context |
| `period` | INTEGER | Period number | `1` | For standardization context |
| `team` | TEXT | Event team (home/away) | `home` | For standardization context |

**Note:** The `standardization_info` column can be omitted from Excel export if desired - the `is_standardized` flag provides the key information.

---

## Example Output: XY Detail Sheet

### Example 1: Goal Event (P1, Home, Offensive Zone)

**Event 1001:** Goal, P1, Home team, Offensive zone  
**Game:** 19045, `home_attacks_right_p1 = true`  
**Result:** No standardization needed (positive x already toward offense)

| game_id | event_index | entity_type | player_game_number | point_number | x | y | x_standardized | y_standardized | is_standardized | zone | period | team |
|---------|-------------|-------------|-------------------|--------------|---|---|----------------|----------------|-----------------|------|--------|------|
| 19045 | 1001 | puck | NULL | 1 | 75.5 | 10.2 | 75.5 | 10.2 | FALSE | o | 1 | home |
| 19045 | 1001 | puck | NULL | 2 | 78.0 | 11.0 | 78.0 | 11.0 | FALSE | o | 1 | home |
| 19045 | 1001 | puck | NULL | 3 | 80.5 | 11.8 | 80.5 | 11.8 | FALSE | o | 1 | home |
| 19045 | 1001 | puck | NULL | 4 | 82.8 | 12.2 | 82.8 | 12.2 | FALSE | o | 1 | home |
| 19045 | 1001 | puck | NULL | 5 | 85.3 | 12.5 | 85.3 | 12.5 | FALSE | o | 1 | home |
| 19045 | 1001 | player | 14 | 1 | 70.0 | 8.0 | 70.0 | 8.0 | FALSE | o | 1 | home |
| 19045 | 1001 | player | 14 | 2 | 72.5 | 9.0 | 72.5 | 9.0 | FALSE | o | 1 | home |
| 19045 | 1001 | player | 14 | 3 | 75.0 | 9.8 | 75.0 | 9.8 | FALSE | o | 1 | home |
| 19045 | 1001 | player | 14 | 4 | 77.5 | 10.5 | 77.5 | 10.5 | FALSE | o | 1 | home |
| 19045 | 1001 | player | 14 | 5 | 80.0 | 11.0 | 80.0 | 11.0 | FALSE | o | 1 | home |

---

### Example 2: Pass Event (P2, Home, Neutral Zone) - WITH FLIP

**Event 1002:** Pass, P2, Home team, Neutral zone  
**Game:** 19045, `home_attacks_right_p1 = true` → In P2, home attacks LEFT (switched ends)  
**Result:** **Standardization applied** (negative x was toward offense, flipped to positive)

| game_id | event_index | entity_type | player_game_number | point_number | x | y | x_standardized | y_standardized | is_standardized | zone | period | team |
|---------|-------------|-------------|-------------------|--------------|---|---|----------------|----------------|-----------------|------|--------|------|
| 19045 | 1002 | puck | NULL | 1 | -15.3 | 5.5 | 15.3 | 5.5 | **TRUE** | n | 2 | home |
| 19045 | 1002 | puck | NULL | 2 | -10.0 | 6.0 | 10.0 | 6.0 | **TRUE** | n | 2 | home |
| 19045 | 1002 | puck | NULL | 3 | -5.2 | 6.8 | 5.2 | 6.8 | **TRUE** | n | 2 | home |
| 19045 | 1002 | puck | NULL | 4 | 0.5 | 7.5 | -0.5 | 7.5 | **TRUE** | n | 2 | home |
| 19045 | 1002 | puck | NULL | 5 | 5.8 | 8.0 | -5.8 | 8.0 | **TRUE** | n | 2 | home |
| 19045 | 1002 | puck | NULL | 6 | 10.2 | 8.1 | -10.2 | 8.1 | **TRUE** | n | 2 | home |
| 19045 | 1002 | player | 22 | 1 | -12.0 | 4.0 | 12.0 | 4.0 | **TRUE** | n | 2 | home |
| 19045 | 1002 | player | 22 | 2 | -8.0 | 5.0 | 8.0 | 5.0 | **TRUE** | n | 2 | home |
| 19045 | 1002 | player | 22 | 3 | -4.0 | 5.5 | 4.0 | 5.5 | **TRUE** | n | 2 | home |
| 19045 | 1002 | player | 22 | 4 | 0.0 | 5.8 | 0.0 | 5.8 | FALSE | n | 2 | home |
| 19045 | 1002 | player | 22 | 5 | 4.0 | 6.0 | -4.0 | 6.0 | **TRUE** | n | 2 | home |
| 19045 | 1002 | player | 22 | 6 | 8.0 | 6.0 | -8.0 | 6.0 | **TRUE** | n | 2 | home |

**Key observation:** The `is_standardized` flag is **TRUE** for positions that were flipped. Position at center ice (x=0.0) stays 0.0, so `is_standardized = FALSE`.

---

### Example 3: Shot Event (P2, Away, Defensive Zone) - NO FLIP

**Event 1003:** Shot, P2, Away team, Defensive zone  
**Game:** 19045, `home_attacks_right_p1 = true` → In P2, away attacks RIGHT  
**Result:** No standardization needed (negative x already toward defense)

| game_id | event_index | entity_type | player_game_number | point_number | x | y | x_standardized | y_standardized | is_standardized | zone | period | team |
|---------|-------------|-------------|-------------------|--------------|---|---|----------------|----------------|-----------------|------|--------|------|
| 19045 | 1003 | puck | NULL | 1 | -65.0 | -8.0 | -65.0 | -8.0 | FALSE | d | 2 | away |
| 19045 | 1003 | puck | NULL | 2 | -67.0 | -9.0 | -67.0 | -9.0 | FALSE | d | 2 | away |
| 19045 | 1003 | puck | NULL | 3 | -69.0 | -9.8 | -69.0 | -9.8 | FALSE | d | 2 | away |
| 19045 | 1003 | puck | NULL | 4 | -70.5 | -10.2 | -70.5 | -10.2 | FALSE | d | 2 | away |
| 19045 | 1003 | player | 7 | 1 | -60.0 | -5.0 | -60.0 | -5.0 | FALSE | d | 2 | away |
| 19045 | 1003 | player | 7 | 2 | -62.5 | -6.0 | -62.5 | -6.0 | FALSE | d | 2 | away |
| 19045 | 1003 | player | 7 | 3 | -65.0 | -7.0 | -65.0 | -7.0 | FALSE | d | 2 | away |
| 19045 | 1003 | player | 7 | 4 | -68.0 | -8.0 | -68.0 | -8.0 | FALSE | d | 2 | away |

---

## Summary Table View

Here's a quick reference showing the pattern:

| Scenario | Raw X | Standardized X | is_standardized | Why? |
|----------|-------|----------------|-----------------|------|
| P1, Home, Offense (attacks right) | +75.5 | +75.5 | FALSE | Already toward offense |
| P2, Home, Neutral (attacks left) | -15.3 | +15.3 | **TRUE** | Flipped to make +x toward offense |
| P2, Home, Neutral (center ice) | 0.0 | 0.0 | FALSE | Center ice unchanged |
| P2, Away, Defense (attacks right) | -65.0 | -65.0 | FALSE | Already toward defense |

---

## Benefits of This Format

1. **Aligned with Supabase schema**: Maps directly to `fact_puck_xy_long` and `fact_player_xy_long`
2. **Simple flag**: `is_standardized` (BOOLEAN) clearly shows which coordinates were transformed
3. **Both formats**: Raw (`x`, `y`) and standardized (`x_standardized`, `y_standardized`) preserved
4. **ETL-friendly**: Can load into separate tables or add standardized columns to existing tables
5. **Analytics-ready**: Use `x_standardized` for consistent analysis, `x` for reference

---

## ETL Mapping

**For `fact_puck_xy_long`:**
- `event_index` → Lookup `event_id` from events
- `point_number` → `point_number`
- `x` → `x` (raw)
- `y` → `y` (raw)
- `x_standardized` → New column (optional)
- `y_standardized` → New column (optional)
- `is_standardized` → New column (flag)

**For `fact_player_xy_long`:**
- `player_game_number` → Lookup `player_id` from roster
- `point_number` → `point_number`
- `x` → `x` (raw)
- `y` → `y` (raw)
- `x_standardized` → New column (optional)
- `y_standardized` → New column (optional)
- `is_standardized` → New column (flag)

---

## Recommendations

1. **Export format**: Use the format above for Excel export
2. **Supabase schema**: Can add `x_standardized`, `y_standardized`, `is_standardized` columns to existing tables
3. **ETL**: Load raw first, then populate standardized columns, use flag for filtering/analysis
4. **Flag usage**: Filter `WHERE is_standardized = TRUE` to see which coordinates were transformed

---

## Questions for Implementation

1. **Should `player_game_number` be NULL for puck rows?** (Recommendation: Yes, or use `event_index` as entity_id for puck)

2. **Should we include `standardization_info` column?** (Recommendation: No, the flag is sufficient, and it reduces file size)

3. **Should `point_number` start at 0 or 1?** (Recommendation: Start at 1 to match Supabase schema)

4. **Should we export both puck and player in same sheet?** (Recommendation: Yes, use `entity_type` to differentiate)