# XY Standardization and the Flip Button

## How the Flip Button Works

### The Flip Button (`⟷ Flip`)

**Location:** In the tracker UI (top left, next to period controls)  
**Function:** Toggles which direction the home team attacks in Period 1

**What it does:**
```javascript
function flipZones() {
  S.homeAttacksRightP1 = !S.homeAttacksRightP1;  // Toggle true/false
  updateZoneLabels();  // Update UI labels
  autoSave();  // Save to game data
}
```

**Visual feedback:**
- `homeAttacksRightP1 = true` (home attacks right): Button is gray (`#374151`)
- `homeAttacksRightP1 = false` (home attacks left): Button is purple (`#7c3aed`)

---

## How It's Stored

### In Game State
```javascript
S.homeAttacksRightP1 = true;  // Default: Home attacks right in P1
```

### In Exported Metadata
```javascript
// Metadata sheet
{
  game_id: 19045,
  home_attacks_right_p1: 1,  // 1 = true, 0 = false
  ...
}
```

### In Saved Game Files
- Stored in JSON save files
- Loaded when importing games
- Persists across sessions

---

## How Standardization Uses It

### The Standardization Function

The standardization function receives `homeAttacksRightP1` as a parameter:

```javascript
function standardizeXY(x, y, event, homeAttacksRightP1) {
  // homeAttacksRightP1 comes from game metadata (set by flip button)
  const { team, period, zone } = event;
  
  // Determine which direction home team attacks THIS period
  const isOddPeriod = period === 1 || period === 3 || period === 'OT';
  const homeAttacksRightThisPeriod = isOddPeriod 
    ? homeAttacksRightP1      // P1/P3/OT: Use P1 setting
    : !homeAttacksRightP1;    // P2: Flip (teams switch ends)
  
  // Determine which direction event team attacks
  const teamAttacksRightThisPeriod = team === 'home' 
    ? homeAttacksRightThisPeriod    // Home: Use home direction
    : !homeAttacksRightThisPeriod;  // Away: Opposite of home
  
  // ... then use this to determine if coordinates need flipping
}
```

### Key Logic

**Period-based direction:**
- **P1, P3, OT**: Use `homeAttacksRightP1` directly
  - If `homeAttacksRightP1 = true`: Home attacks right
  - If `homeAttacksRightP1 = false`: Home attacks left
  
- **P2**: Flip from P1 setting (teams switch ends)
  - If `homeAttacksRightP1 = true`: Home attacks **left** in P2 (flipped)
  - If `homeAttacksRightP1 = false`: Home attacks **right** in P2 (flipped)

**Team-based direction:**
- **Home team**: Uses `homeAttacksRightThisPeriod` directly
- **Away team**: Uses opposite of home

---

## Examples

### Example 1: Flip Button NOT Pressed (Default)

**Initial State:**
- `homeAttacksRightP1 = true` (default)
- Button is gray

**Period 1:**
- Home attacks **right** in P1
- Away attacks **left** in P1
- Coordinates where home is attacking: positive x = toward offense (good, no flip)
- Coordinates where home is defending: negative x = toward defense (good, no flip)

**Period 2:**
- Home attacks **left** in P2 (switched ends)
- Away attacks **right** in P2
- Coordinates where home is attacking: negative x = toward offense (need flip to make +x)
- Coordinates where home is defending: positive x = toward defense (need flip to make -x)

---

### Example 2: Flip Button Pressed Once

**After Flip:**
- `homeAttacksRightP1 = false`
- Button is purple

**Period 1:**
- Home attacks **left** in P1
- Away attacks **right** in P1
- Coordinates where home is attacking: negative x = toward offense (need flip to make +x)
- Coordinates where home is defending: positive x = toward defense (need flip to make -x)

**Period 2:**
- Home attacks **right** in P2 (switched ends)
- Away attacks **left** in P2
- Coordinates where home is attacking: positive x = toward offense (good, no flip)
- Coordinates where home is defending: negative x = toward defense (good, no flip)

---

## How This Compensates for Game-to-Game Differences

### The Problem
The same team might attack different directions in different games because:
- Home/away bench assignment varies (especially in beer league)
- Some rinks have fixed benches, others don't
- The flip button allows tracking the actual game configuration

### The Solution

**When exporting XY data:**
1. Read `S.homeAttacksRightP1` from game state (set by flip button)
2. Export it in metadata as `home_attacks_right_p1`
3. Pass it to standardization function as `homeAttacksRightP1` parameter
4. Standardization uses this to determine the correct transformation

**Result:**
- Each game has its own `home_attacks_right_p1` value
- Standardization accounts for game-specific orientation
- Standardized coordinates are consistent across all games
- Same team can have different raw coordinates in different games, but standardized coordinates are comparable

---

## Standardization Flow

```
1. User clicks flip button
   ↓
2. S.homeAttacksRightP1 = !S.homeAttacksRightP1
   ↓
3. Value saved to game data
   ↓
4. Export reads S.homeAttacksRightP1
   ↓
5. Exported to metadata sheet as home_attacks_right_p1
   ↓
6. Standardization function receives homeAttacksRightP1 as parameter
   ↓
7. Uses it to determine team's attacking direction for each period
   ↓
8. Applies transformation if needed (sets is_standardized flag)
```

---

## Key Takeaway

**The flip button compensates for game-to-game differences:**
- Press flip button if home team attacks **left** in P1 (non-standard)
- Don't press if home team attacks **right** in P1 (standard)
- The value is stored per-game and used during export
- Standardization uses this value to ensure consistent output regardless of game configuration

**For standardization:**
- The function always receives `homeAttacksRightP1` from game metadata
- It doesn't matter what the raw orientation is
- Standardization ensures offense is always at +x, defense at -x
- The `is_standardized` flag shows when transformation was applied

---

## Implementation in Export

When exporting XY data:

```javascript
function buildXYDetailSheet() {
  // Get game-specific orientation from state
  const homeAttacksRightP1 = S.homeAttacksRightP1;
  
  // Process each event
  S.events.forEach(evt => {
    // Process each XY position
    (evt.puckXY || []).forEach((xy, idx) => {
      // Standardize using game's orientation
      const standardized = standardizeXY(
        xy.x, 
        xy.y, 
        evt, 
        homeAttacksRightP1  // ← From flip button!
      );
      
      // Export with flag
      rows.push({
        x: xy.x,                    // Raw
        y: xy.y,                    // Raw
        x_standardized: standardized.x,  // Standardized
        y_standardized: standardized.y,  // Standardized
        is_standardized: standardized.flipped ? 1 : 0,  // Flag
        // ...
      });
    });
  });
}
```

The flip button value is automatically used - no additional configuration needed!