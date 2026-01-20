# XY Data Export Proposal

## Current State
- XY data stored as arrays: `evt.puckXY[]` and `p.xy[]` (up to 10 slots per event/player)
- All XY slots exported in events sheet as `puck_x_1`, `puck_y_1`, ... `puck_x_10`, `puck_y_10`
- Coordinates are center-relative: x = -100 to +100, y = -42.5 to +42.5
- Teams switch ends each period (P1/P3/OT use `homeAttacksRightP1`, P2 is flipped)

## Proposed Changes

### 1. Simplified Events Sheet
**Only export first and last XY positions (start/stop)**

**For Puck:**
- `puck_x_start` / `puck_y_start` - First XY slot (slot 1)
- `puck_x_end` / `puck_y_end` - Last XY slot (variable, could be slot 1-10)

**For Players:**
- `player_x_start` / `player_y_start` - First XY slot (slot 1)
- `player_x_end` / `player_y_end` - Last XY slot (variable)

**Benefits:**
- Reduces column bloat (20 columns → 4 columns per entity)
- Most analytics only need start/stop positions
- Faster import/export

### 2. New XY Detail Sheet
**Export all intermediate XY positions in a separate sheet**

**Sheet name:** `xy_detail` or `xy_positions`

**Columns:**
```
game_id | event_index | entity_type | entity_id | sequence | x | y | x_standardized | y_standardized | is_standardized | standardization_info
```

**Where:**
- `game_id`: Game identifier (for cross-game analysis, references game-specific orientation)
- `event_index`: Event identifier (matches events sheet)
- `entity_type`: 'puck' | 'player'
- `entity_id`: For players, this is `player_game_number`. For puck, use event_index or 'puck'
- `sequence`: Sequence number (1, 2, 3, ... up to 10)
- `x`, `y`: **Raw coordinates** (center-relative, unaltered)
- `x_standardized`, `y_standardized`: **Standardized coordinates** (offense always +x, defense always -x)
- `is_standardized`: Boolean flag (1 = standardized coordinates differ from raw, 0 = no change)
- `standardization_info`: String describing the standardization applied (e.g., "home_attacks_right_p1=true, period=1, team=home, zone=o, flipped=false")

**Example:**
```
game_id | event_index | entity_type | entity_id | sequence | x    | y     | x_standardized | y_standardized | is_standardized | standardization_info
19045   | 1001       | puck        | 1001      | 1        | 25.3 | 10.5  | 25.3          | 10.5          | 0              | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false
19045   | 1001       | puck        | 1001      | 2        | 30.1 | 8.2   | 30.1          | 8.2           | 0              | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false
19045   | 1001       | player      | 14        | 1        | -22.0| 5.0   | 22.0          | 5.0           | 1              | home_attacks_right_p1=true,period=2,team=home,zone=d,flipped=true
19045   | 1001       | player      | 14        | 2        | -28.5| 7.1   | 28.5          | 7.1           | 1              | home_attacks_right_p1=true,period=2,team=home,zone=d,flipped=true
```

**Note:** The `standardization_info` column provides full transparency about how coordinates were transformed, making it easy to reverse the standardization if needed.

**Benefits:**
- Complete trajectory data preserved
- Long format makes analysis easier (filter by sequence, plot trajectories)
- Standardized coordinates for consistent analysis

### 3. Standardization Function

**Goal:** Transform coordinates so offense is always +x, defense is always -x

**Key Requirements:**
1. **Preserve raw coordinates** - Never modify original x, y values
2. **Game-specific orientation** - Use `homeAttacksRightP1` from game metadata (exported in metadata sheet)
3. **Transparency** - Include flag and info about what transformation was applied
4. **Reversibility** - Can reconstruct raw from standardized using `standardization_info`

**Logic:**
```javascript
function standardizeXY(x, y, event) {
  const { team, period } = event;
  
  // Determine if event team is on offense or defense
  // This requires zone information or we use a heuristic
  const isOffense = event.zone === 'o' || 
                    (event.type === 'Goal' || event.type === 'Shot');
  
  // Determine if we need to flip based on period and team orientation
  const isOddPeriod = period === 1 || period === 3 || period === 'OT';
  const homeAttacksRight = isOddPeriod ? S.homeAttacksRightP1 : !S.homeAttacksRightP1;
  
  // If event team is home
  if (team === 'home') {
    const homeIsOffense = isOffense;
    const shouldFlip = homeAttacksRight ? !homeIsOffense : homeIsOffense;
    return shouldFlip ? { x: -x, y: y } : { x: x, y: y };
  } else {
    // Away team
    const awayIsOffense = isOffense;
    const awayAttacksRight = !homeAttacksRight;
    const shouldFlip = awayAttacksRight ? !awayIsOffense : awayIsOffense;
    return shouldFlip ? { x: -x, y: y } : { x: x, y: y };
  }
}
```

**Simpler approach using zone:**
```javascript
function standardizeXY(x, y, event) {
  const { team, period, zone } = event;
  
  // Determine which direction is "offense" for this event's team
  const isOddPeriod = period === 1 || period === 3 || period === 'OT';
  const homeAttacksRight = isOddPeriod ? S.homeAttacksRightP1 : !S.homeAttacksRightP1;
  
  // If event team is home
  if (team === 'home') {
    // In odd periods, home attacks right if homeAttacksRightP1
    // In even periods, home attacks left if homeAttacksRightP1
    const homeAttacksRightThisPeriod = homeAttacksRight;
    
    // If offensive zone, home should be at +x
    // If defensive zone, home should be at -x
    const shouldFlip = (zone === 'o' && !homeAttacksRightThisPeriod) ||
                       (zone === 'd' && homeAttacksRightThisPeriod);
    
    return shouldFlip ? { x: -x, y: y } : { x: x, y: y };
  } else {
    // Away team - opposite of home
    const awayAttacksRightThisPeriod = !homeAttacksRight;
    
    const shouldFlip = (zone === 'o' && !awayAttacksRightThisPeriod) ||
                       (zone === 'd' && awayAttacksRightThisPeriod);
    
    return shouldFlip ? { x: -x, y: y } : { x: x, y: y };
  }
}
```

**Even simpler: Use event's zone directly**
```javascript
function standardizeXY(x, y, event) {
  // If event is in offensive zone, positive x should be toward offense
  // If event is in defensive zone, positive x should be toward defense (flip needed)
  
  const { zone } = event;
  
  // For offensive zone events, keep as-is if x is positive (attacking)
  // For defensive zone events, flip so defense is at -x
  if (zone === 'o') {
    // Offensive zone: +x = attacking direction (good)
    return { x: x, y: y };
  } else if (zone === 'd') {
    // Defensive zone: flip so defense is at -x
    return { x: -x, y: y };
  } else {
    // Neutral zone: keep as-is (or could use team direction)
    return { x: x, y: y };
  }
}
```

**Recommended: Use team, period, and zone with game orientation**
```javascript
/**
 * Standardize XY coordinates so offense is always +x, defense is always -x
 * @param {number} x - Raw x coordinate (center-relative)
 * @param {number} y - Raw y coordinate (center-relative)
 * @param {object} event - Event object with team, period, zone
 * @param {boolean} homeAttacksRightP1 - Game-specific orientation (from metadata)
 * @returns {object} - {x: standardized_x, y: standardized_y, flipped: boolean, info: string}
 */
function standardizeXY(x, y, event, homeAttacksRightP1) {
  const { team, period, zone } = event;
  
  // Determine team's attacking direction for this period
  // Odd periods (1, 3, OT): Use P1 orientation
  // Even periods (2): Flip from P1 orientation (teams switch ends)
  const isOddPeriod = period === 1 || period === 3 || period === 'OT' || period === '4';
  const homeAttacksRightThisPeriod = isOddPeriod ? homeAttacksRightP1 : !homeAttacksRightP1;
  const teamAttacksRightThisPeriod = team === 'home' ? homeAttacksRightThisPeriod : !homeAttacksRightThisPeriod;
  
  // Determine if event team is on offense or defense
  const isOffense = zone === 'o';
  const isDefense = zone === 'd';
  const isNeutral = !zone || zone === 'n';
  
  let flipped = false;
  let stdX = x;
  let stdY = y;
  
  if (isNeutral) {
    // Neutral zone: Still need to standardize based on team's attacking direction
    // If team attacks right this period, positive x = toward offense (good, no flip)
    // If team attacks right this period, negative x = toward defense (flip to make +x toward offense)
    // If team attacks left this period, negative x = toward offense (flip to make +x toward offense)
    // If team attacks left this period, positive x = toward defense (flip to make +x toward offense)
    // Goal: In neutral zone, +x should always be toward the team's offensive end
    if (teamAttacksRightThisPeriod) {
      // Team attacks right: positive x = toward offense (good)
      if (x < 0) {
        stdX = -x; // Flip negative to positive (toward offense)
        flipped = true;
      }
    } else {
      // Team attacks left: negative x = toward offense (need to flip to make +x)
      if (x > 0) {
        stdX = -x; // Flip positive to negative, but we want +x toward offense...
        // Actually: if team attacks left, offense is at negative x
        // But we want offense at +x, so we flip: negative x becomes positive x
        stdX = Math.abs(x); // Ensure positive (toward offense after standardization)
        flipped = true;
      } else {
        // Already negative, flip to make positive (offense at +x)
        stdX = -x;
        flipped = true;
      }
    }
  } else if (isOffense) {
    // Offensive zone: Offense should be at +x
    // If team attacks right this period and x is positive, good (no flip)
    // If team attacks left this period, we need to flip to make offense +x
    if (teamAttacksRightThisPeriod) {
      // Team attacks right: positive x = good, negative x = need flip
      if (x < 0) {
        stdX = -x;
        flipped = true;
      }
    } else {
      // Team attacks left: negative x = good (but we want +x), positive x = need flip
      if (x > 0) {
        stdX = -x;
        flipped = true;
      } else {
        stdX = -x; // Already negative, flip to make positive
        flipped = true;
      }
    }
  } else if (isDefense) {
    // Defensive zone: Defense should be at -x
    // If team attacks right this period, defense is at left (negative x = good)
    // If team attacks left this period, defense is at right (positive x = need flip)
    if (teamAttacksRightThisPeriod) {
      // Team attacks right: defense at left, should be negative x
      if (x > 0) {
        stdX = -x;
        flipped = true;
      }
    } else {
      // Team attacks left: defense at right, should be negative x
      if (x < 0) {
        stdX = -x; // Already negative, but we want to keep it negative
        // Actually, if team attacks left, defense at right (positive x), need to flip
        stdX = -Math.abs(x); // Ensure negative
        flipped = x > 0;
      } else {
        stdX = -x;
        flipped = true;
      }
    }
  }
  
  // Build standardization info string
  const info = `home_attacks_right_p1=${homeAttacksRightP1},period=${period},team=${team},zone=${zone || 'n'},flipped=${flipped}`;
  
  return {
    x: stdX,
    y: stdY,
    flipped: flipped,
    info: info
  };
}
```

**Simplified version (zone-based with neutral zone handling):**
```javascript
function standardizeXY(x, y, event, homeAttacksRightP1) {
  const { team, period, zone } = event;
  
  // Determine team's attacking direction for this period
  const isOddPeriod = period === 1 || period === 3 || period === 'OT' || period === '4';
  const homeAttacksRightThisPeriod = isOddPeriod ? homeAttacksRightP1 : !homeAttacksRightP1;
  const teamAttacksRightThisPeriod = team === 'home' ? homeAttacksRightThisPeriod : !homeAttacksRightThisPeriod;
  
  // Simple rule: Offense at +x, Defense at -x
  if (zone === 'o') {
    // Offensive zone: ensure x is positive (offense toward +x)
    const flipped = x < 0;
    return {
      x: Math.abs(x),
      y: y,
      flipped: flipped,
      info: `zone=o,team_attacks_right=${teamAttacksRightThisPeriod},flipped=${flipped}`
    };
  } else if (zone === 'd') {
    // Defensive zone: ensure x is negative (defense toward -x)
    const flipped = x > 0;
    return {
      x: -Math.abs(x),
      y: y,
      flipped: flipped,
      info: `zone=d,team_attacks_right=${teamAttacksRightThisPeriod},flipped=${flipped}`
    };
  } else {
    // Neutral zone: +x should be toward team's offensive end (based on period)
    // If team attacks right this period: positive x = toward offense (good)
    // If team attacks left this period: negative x = toward offense (flip to make +x)
    let flipped = false;
    let stdX = x;
    
    if (teamAttacksRightThisPeriod) {
      // Team attacks right: positive x = toward offense
      if (x < 0) {
        stdX = -x; // Flip negative to positive
        flipped = true;
      }
    } else {
      // Team attacks left: negative x = toward offense, but we want +x toward offense
      if (x <= 0) {
        stdX = -x; // Flip negative to positive (or keep 0 as 0)
        flipped = x < 0;
      } else {
        // Positive x = toward defense, flip to negative, then flip to positive?
        // Actually: if team attacks left, offense is at negative x direction
        // We want offense at +x, so we flip the sign
        stdX = -x;
        flipped = true;
      }
    }
    
    return {
      x: stdX,
      y: y,
      flipped: flipped,
      info: `zone=n,team_attacks_right=${teamAttacksRightThisPeriod},flipped=${flipped}`
    };
  }
}
```

## Implementation Plan

### Step 1: Create Standardization Function
- Add `standardizeXY(x, y, event, homeAttacksRightP1)` function
- Return object with `{x, y, flipped, info}`
- Test with various periods, teams, zones, and orientation settings
- **Important:** Always use `S.homeAttacksRightP1` from current game state

### Step 2: Modify Events Export
- Change from `puck_x_1`, `puck_y_1`, ... `puck_x_10`, `puck_y_10`
- To: 
  - `puck_x_start` / `puck_y_start` (raw, first slot)
  - `puck_x_end` / `puck_y_end` (raw, last slot)
  - `puck_x_start_std` / `puck_y_start_std` (standardized)
  - `puck_x_end_std` / `puck_y_end_std` (standardized)
- Same pattern for players
- Apply standardization using game's `homeAttacksRightP1`

### Step 3: Create XY Detail Sheet Export
- New function `buildXYDetailSheet(homeAttacksRightP1)`
- Export all XY positions with sequence numbers
- Include:
  - Raw coordinates (`x`, `y`)
  - Standardized coordinates (`x_standardized`, `y_standardized`)
  - Standardization flag (`is_standardized`: 1 if flipped, 0 if not)
  - Standardization info (string with details)
- Include `game_id` in each row for cross-game reference

### Step 4: Update Export Function
- Get `homeAttacksRightP1` from `S.homeAttacksRightP1` (already exported in metadata)
- Call `buildXYDetailSheet(S.homeAttacksRightP1)` in `buildExportWorkbook()`
- Add sheet to workbook as `'xy_detail'` or `'xy_positions'`
- Ensure metadata sheet includes `home_attacks_right_p1` (already done ✅)

## Example Export Structure

### Events Sheet (simplified)
```
event_index | ... | puck_x_start | puck_y_start | puck_x_end | puck_y_end | puck_x_start_std | puck_y_start_std | puck_x_end_std | puck_y_end_std | player_x_start | player_y_start | player_x_end | player_y_end | player_x_start_std | player_y_start_std | player_x_end_std | player_y_end_std
1001       | ... | 25.3          | 10.5         | 45.2       | 15.1       | 25.3             | 10.5             | 45.2           | 15.1           | 22.0            | 5.0             | 40.0         | 12.0         | 22.0                | 5.0                | 40.0             | 12.0
```

### XY Detail Sheet (new)
```
game_id | event_index | entity_type | entity_id | sequence | x    | y     | x_standardized | y_standardized | is_standardized | standardization_info
19045   | 1001       | puck        | 1001      | 1        | 25.3 | 10.5  | 25.3           | 10.5           | 0               | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false
19045   | 1001       | puck        | 1001      | 2        | 30.1 | 8.2   | 30.1           | 8.2            | 0               | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false
19045   | 1001       | puck        | 1001      | 3        | 35.5 | 12.1  | 35.5           | 12.1           | 0               | home_attacks_right_p1=true,period=1,team=home,zone=o,flipped=false
19045   | 1001       | player      | 14        | 1        | -22.0| 5.0   | 22.0           | 5.0            | 1               | home_attacks_right_p1=true,period=2,team=home,zone=d,flipped=true
19045   | 1001       | player      | 14        | 2        | -28.5| 7.1   | 28.5           | 7.1            | 1               | home_attacks_right_p1=true,period=2,team=home,zone=d,flipped=true
```

**Key Points:**
- Raw coordinates (`x`, `y`) always preserved exactly as entered
- Standardized coordinates (`x_standardized`, `y_standardized`) for consistent analysis
- `is_standardized` flag (1 = coordinates were flipped, 0 = no change)
- `standardization_info` provides full context for reversibility

## Benefits

1. **Simplified Events Sheet**: Easier to work with, faster imports
2. **Complete Trajectory Data**: All positions preserved in detail sheet
3. **Standardized Analysis**: Consistent coordinate system regardless of period/team
4. **Backward Compatibility**: Can derive old format from detail sheet if needed
5. **Analytics Ready**: Standardized coordinates make analysis much easier

## Key Design Decisions

### ✅ Resolved:

1. **Raw + Standardized**: Export both raw and standardized coordinates
   - Raw: Always preserved exactly as entered (for reference, debugging, reversibility)
   - Standardized: For consistent cross-game analysis

2. **Standardization Flag**: Include `is_standardized` flag
   - Quick way to see if coordinates were transformed
   - Useful for filtering/analysis

3. **Transparency**: Include `standardization_info` column
   - Documents exactly how standardization was applied
   - Enables reversing standardization if needed
   - Includes game orientation (`home_attacks_right_p1`) in the string

4. **Game-Specific Orientation**: Use `homeAttacksRightP1` from game metadata
   - Each game can have different orientation
   - Already exported in metadata sheet ✅
   - Standardization function receives this as parameter

5. **Entity ID for Puck**: Use `event_index` as entity_id for puck (or could use 'puck', but event_index is more unique)

6. **Sheet Name**: Recommend `xy_detail` (clear and concise)

### ⚠️ Still Need Testing:

1. **Standardization Logic**: Which approach is most accurate?
   - **Zone-based** (simplest): Offense at +x, Defense at -x, Neutral unchanged
   - **Team + Period + Zone** (most accurate): Accounts for period switches and team orientation
   - **Recommendation**: Start with zone-based for simplicity, can enhance later

2. **Neutral Zone Handling**: ✅ RESOLVED
   - Since center ice is 0, neutral zone still has +/- coordinates
   - Must standardize based on team's attacking direction for that period
   - If team attacks right: positive x = toward offense (good)
   - If team attacks left: flip so positive x = toward offense
   - **Result**: +x always represents direction toward team's offensive end

## Final Recommendation

**Export structure:**
- **Events sheet**: Raw start/end + Standardized start/end (8 columns per entity type)
- **XY Detail sheet**: Complete trajectory with raw, standardized, flag, and info
- **Metadata sheet**: Already includes `home_attacks_right_p1` ✅

**Standardization approach:**
- Zone-based with period orientation: 
  - `zone=o` → +x (offense always positive)
  - `zone=d` → -x (defense always negative)
  - `zone=n` → +x toward team's offensive end (based on period and `homeAttacksRightP1`)
- Use game's `homeAttacksRightP1` from metadata for consistency
- Include full transparency via `is_standardized` flag and `standardization_info` column

**Neutral Zone Standardization:**
- Since center ice is 0, neutral zone coordinates can be positive or negative
- Standardize so +x always represents direction toward team's offensive end
- Based on: `team` + `period` + `homeAttacksRightP1` → determines which direction is offense

This provides:
1. ✅ Raw data preserved (always)
2. ✅ Standardized data for analysis (always)
3. ✅ Flag indicating standardization (always)
4. ✅ Game-specific orientation handling (via `homeAttacksRightP1`)
5. ✅ Full transparency and reversibility (via `standardization_info`)