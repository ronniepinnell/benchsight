# XY Export Output Example

This document shows a concrete example of what the XY export would look like with raw and standardized coordinates.

## Scenario

**Game:** 19045 (Home Team vs Away Team)  
**Game Orientation:** `home_attacks_right_p1 = true`  
**Example Events:**
1. Event 1001: Goal (P1, Home, Offensive zone)
2. Event 1002: Pass (P2, Home, Neutral zone) 
3. Event 1003: Shot (P2, Away, Defensive zone)

---

## Events Sheet Output

**Columns shown:** Only XY-related columns (other event columns omitted)

| event_index | period | team | zone | event_type | ... | puck_x_start | puck_y_start | puck_x_end | puck_y_end | puck_x_start_std | puck_y_start_std | puck_x_end_std | puck_y_end_std | player_x_start | player_y_start | player_x_end | player_y_end | player_x_start_std | player_y_start_std | player_x_end_std | player_y_end_std |
|-------------|--------|------|------|------------|-----|--------------|--------------|------------|------------|------------------|------------------|----------------|----------------|----------------|----------------|--------------|--------------|-------------------|-------------------|------------------|------------------|
| 1001 | 1 | home | o | Goal | ... | 75.5 | 10.2 | 85.3 | 12.5 | 75.5 | 10.2 | 85.3 | 12.5 | 70.0 | 8.0 | 80.0 | 11.0 | 70.0 | 8.0 | 80.0 | 11.0 |
| 1002 | 2 | home | n | Pass | ... | -15.3 | 5.5 | 10.2 | 8.1 | 15.3 | 5.5 | -10.2 | 8.1 | -12.0 | 4.0 | 8.0 | 6.0 | 12.0 | 4.0 | -8.0 | 6.0 |
| 1003 | 2 | away | d | Shot | ... | -65.0 | -8.0 | -70.5 | -10.2 | -65.0 | -8.0 | -70.5 | -10.2 | -60.0 | -5.0 | -68.0 | -8.0 | -60.0 | -5.0 | -68.0 | -8.0 |

**Explanations:**
- **Event 1001**: P1, home in offensive zone. Home attacks right in P1, so positive x is already toward offense → no flip needed
- **Event 1002**: P2, home in neutral zone. Home attacks left in P2 (switched ends), so negative x was toward offense → flipped to make +x toward offense
- **Event 1003**: P2, away in defensive zone. Away attacks left in P2, so negative x is already toward defense → no flip needed

---

## XY Detail Sheet Output

**Complete trajectory data with all XY positions:**

| game_id | event_index | entity_type | entity_id | sequence | x | y | x_standardized | y_standardized | is_standardized | standardization_info |
|---------|-------------|-------------|-----------|----------|---|---|----------------|----------------|-----------------|---------------------|
| 19045 | 1001 | puck | 1001 | 1 | 75.5 | 10.2 | 75.5 | 10.2 | 0 | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false |
| 19045 | 1001 | puck | 1001 | 2 | 78.0 | 11.0 | 78.0 | 11.0 | 0 | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false |
| 19045 | 1001 | puck | 1001 | 3 | 80.5 | 11.8 | 80.5 | 11.8 | 0 | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false |
| 19045 | 1001 | puck | 1001 | 4 | 82.8 | 12.2 | 82.8 | 12.2 | 0 | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false |
| 19045 | 1001 | puck | 1001 | 5 | 85.3 | 12.5 | 85.3 | 12.5 | 0 | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false |
| 19045 | 1001 | player | 14 | 1 | 70.0 | 8.0 | 70.0 | 8.0 | 0 | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false |
| 19045 | 1001 | player | 14 | 2 | 72.5 | 9.0 | 72.5 | 9.0 | 0 | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false |
| 19045 | 1001 | player | 14 | 3 | 75.0 | 9.8 | 75.0 | 9.8 | 0 | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false |
| 19045 | 1001 | player | 14 | 4 | 77.5 | 10.5 | 77.5 | 10.5 | 0 | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false |
| 19045 | 1001 | player | 14 | 5 | 80.0 | 11.0 | 80.0 | 11.0 | 0 | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false |
| 19045 | 1002 | puck | 1002 | 1 | -15.3 | 5.5 | 15.3 | 5.5 | 1 | home_attacks_right_p1=true,period=2,team=home,zone=n,flipped=true |
| 19045 | 1002 | puck | 1002 | 2 | -10.0 | 6.0 | 10.0 | 6.0 | 1 | home_attacks_right_p1=true,period=2,team=home,zone=n,flipped=true |
| 19045 | 1002 | puck | 1002 | 3 | -5.2 | 6.8 | 5.2 | 6.8 | 1 | home_attacks_right_p1=true,period=2,team=home,zone=n,flipped=true |
| 19045 | 1002 | puck | 1002 | 4 | 0.5 | 7.5 | -0.5 | 7.5 | 1 | home_attacks_right_p1=true,period=2,team=home,zone=n,flipped=true |
| 19045 | 1002 | puck | 1002 | 5 | 5.8 | 8.0 | -5.8 | 8.0 | 1 | home_attacks_right_p1=true,period=2,team=home,zone=n,flipped=true |
| 19045 | 1002 | puck | 1002 | 6 | 10.2 | 8.1 | -10.2 | 8.1 | 1 | home_attacks_right_p1=true,period=2,team=home,zone=n,flipped=true |
| 19045 | 1002 | player | 22 | 1 | -12.0 | 4.0 | 12.0 | 4.0 | 1 | home_attacks_right_p1=true,period=2,team=home,zone=n,flipped=true |
| 19045 | 1002 | player | 22 | 2 | -8.0 | 5.0 | 8.0 | 5.0 | 1 | home_attacks_right_p1=true,period=2,team=home,zone=n,flipped=true |
| 19045 | 1002 | player | 22 | 3 | -4.0 | 5.5 | 4.0 | 5.5 | 1 | home_attacks_right_p1=true,period=2,team=home,zone=n,flipped=true |
| 19045 | 1002 | player | 22 | 4 | 0.0 | 5.8 | 0.0 | 5.8 | 0 | home_attacks_right_p1=true,period=2,team=home,zone=n,flipped=false |
| 19045 | 1002 | player | 22 | 5 | 4.0 | 6.0 | -4.0 | 6.0 | 1 | home_attacks_right_p1=true,period=2,team=home,zone=n,flipped=true |
| 19045 | 1002 | player | 22 | 6 | 8.0 | 6.0 | -8.0 | 6.0 | 1 | home_attacks_right_p1=true,period=2,team=home,zone=n,flipped=true |
| 19045 | 1003 | puck | 1003 | 1 | -65.0 | -8.0 | -65.0 | -8.0 | 0 | home_attacks_right_p1=true,period=2,team=away,zone=d,flipped=false |
| 19045 | 1003 | puck | 1003 | 2 | -67.0 | -9.0 | -67.0 | -9.0 | 0 | home_attacks_right_p1=true,period=2,team=away,zone=d,flipped=false |
| 19045 | 1003 | puck | 1003 | 3 | -69.0 | -9.8 | -69.0 | -9.8 | 0 | home_attacks_right_p1=true,period=2,team=away,zone=d,flipped=false |
| 19045 | 1003 | puck | 1003 | 4 | -70.5 | -10.2 | -70.5 | -10.2 | 0 | home_attacks_right_p1=true,period=2,team=away,zone=d,flipped=false |
| 19045 | 1003 | player | 7 | 1 | -60.0 | -5.0 | -60.0 | -5.0 | 0 | home_attacks_right_p1=true,period=2,team=away,zone=d,flipped=false |
| 19045 | 1003 | player | 7 | 2 | -62.5 | -6.0 | -62.5 | -6.0 | 0 | home_attacks_right_p1=true,period=2,team=away,zone=d,flipped=false |
| 19045 | 1003 | player | 7 | 3 | -65.0 | -7.0 | -65.0 | -7.0 | 0 | home_attacks_right_p1=true,period=2,team=away,zone=d,flipped=false |
| 19045 | 1003 | player | 7 | 4 | -68.0 | -8.0 | -68.0 | -8.0 | 0 | home_attacks_right_p1=true,period=2,team=away,zone=d,flipped=false |

---

## Detailed Explanation by Event

### Event 1001: Goal (P1, Home, Offensive Zone)

**Context:**
- Period 1
- Home team
- Offensive zone
- `home_attacks_right_p1 = true` → Home attacks right in P1

**Puck Positions:**
- Raw: All positive x values (75.5 → 85.3) moving right toward goal
- Standardized: Same (75.5 → 85.3) - **No flip needed** because positive x is already toward offense
- Flag: `is_standardized = 0` (no change)

**Player 14 Positions:**
- Raw: All positive x values (70.0 → 80.0) moving right
- Standardized: Same (70.0 → 80.0) - **No flip needed**
- Flag: `is_standardized = 0`

---

### Event 1002: Pass (P2, Home, Neutral Zone)

**Context:**
- Period 2 (teams switched ends)
- Home team
- Neutral zone (center ice = 0)
- `home_attacks_right_p1 = true` → In P2, home attacks **LEFT** (switched ends)

**Puck Positions:**
- Raw: Starts at x = -15.3 (left of center), ends at x = 10.2 (right of center)
- Standardized: Starts at x = 15.3, ends at x = -10.2 - **Flipped!**
- **Why flipped?** In P2, home attacks left, so negative x = toward offense. We want +x toward offense, so we flip the sign.
- Flag: `is_standardized = 1` for most positions (flipped)

**Player 22 Positions:**
- Raw: Starts at x = -12.0, crosses center (x = 0.0), ends at x = 8.0
- Standardized: Starts at x = 12.0, crosses center (still 0.0), ends at x = -8.0 - **Flipped!**
- Note: Position at x = 0.0 stays 0.0 (no change)
- Flag: `is_standardized = 1` for all non-zero positions, `0` for center ice

**Key Insight:** In neutral zone, we flip based on which direction is offense. Since home attacks left in P2, negative x was toward offense, so we flip to make positive x toward offense.

---

### Event 1003: Shot (P2, Away, Defensive Zone)

**Context:**
- Period 2
- Away team (in defensive zone)
- `home_attacks_right_p1 = true` → In P2, home attacks left, so **away attacks right**

**Puck Positions:**
- Raw: All negative x values (-65.0 → -70.5) in defensive zone
- Standardized: Same (-65.0 → -70.5) - **No flip needed**
- **Why no flip?** Away is in defensive zone. Since away attacks right in P2, their defense is at left (negative x), which is already correct.
- Flag: `is_standardized = 0`

**Player 7 Positions:**
- Raw: All negative x values (-60.0 → -68.0)
- Standardized: Same (-60.0 → -68.0) - **No flip needed**
- Flag: `is_standardized = 0`

---

## Key Takeaways

1. **Raw coordinates are always preserved** - Never modified, always exported exactly as entered

2. **Standardization depends on zone + period + team orientation:**
   - **Offensive zone**: +x always represents offense (flip if needed)
   - **Defensive zone**: -x always represents defense (flip if needed)
   - **Neutral zone**: +x always represents direction toward team's offensive end (flip based on period direction)

3. **The `is_standardized` flag** quickly shows which coordinates were transformed:
   - `0` = No change (raw = standardized)
   - `1` = Flipped (raw ≠ standardized)

4. **The `standardization_info` column** provides full transparency:
   - Shows game orientation (`home_attacks_right_p1`)
   - Shows period, team, zone
   - Shows whether flip was applied
   - Can be used to reverse the standardization if needed

5. **Period switching matters:**
   - P1/P3/OT: Use `home_attacks_right_p1` as-is
   - P2: Flip the orientation (teams switch ends)

---

## Metadata Sheet Reference

The metadata sheet (not shown in detail here) contains:
```
game_id: 19045
home_attacks_right_p1: 1  (true)
```

This value is used in the standardization function to determine how to transform coordinates for each event.

---

## Use Cases

**For Analytics:**
- Use `x_standardized` and `y_standardized` columns for consistent analysis across games/periods
- Offense always at +x, defense always at -x regardless of period or game orientation

**For Reference:**
- Use `x` and `y` columns to see exactly what was entered in the tracker
- Use `standardization_info` to understand how the transformation was applied

**For Debugging:**
- Use `is_standardized` flag to quickly identify which positions were transformed
- Use `standardization_info` to verify the logic matches expectations