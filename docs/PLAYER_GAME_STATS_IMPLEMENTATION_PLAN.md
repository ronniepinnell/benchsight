# Player Game Stats Implementation Plan
## Research Paper Gaps → Implementation Strategy

**Date:** 2026-01-13  
**Target Table:** `fact_player_game_stats`  
**Based On:** Hockey Analytics Replication Manual Gap Analysis  
**Current Version:** v29.7

---

## Executive Summary

This document provides a phased implementation plan for enhancing `fact_player_game_stats` based on the research paper analysis. The plan prioritizes:

1. **Immediate Wins** (No XY required) - Flurry Adjustment, WDBE Faceoffs
2. **XY-Dependent Features** (Coming Soon) - Royal Road, Distance/Angle, Gap Control
3. **Advanced Models** (Future) - GBM xG, RAPM, xT

All changes will maintain backward compatibility and integrate cleanly with the existing `PlayerStatsBuilder` pattern.

---

## Current Architecture Overview

### Code Structure
```
src/builders/player_stats.py
├── PlayerStatsBuilder (class)
│   ├── load_data() - Loads all input tables
│   ├── build_player_stats() - Builds stats for one player-game
│   └── build() - Builds entire table
│
src/tables/core_facts.py
├── calculate_xg_stats() - Current xG (lookup table)
├── calculate_war_stats() - Current WAR/GAR (weighted formula)
├── calculate_micro_stats() - Micro stats
└── [other calculation functions]
```

### Current Flow (build_player_stats)
1. Initialize stats dict with keys/metadata
2. Load player/team/season info
3. **Calculate stats in sequence:**
   - Event stats (goals, assists, shots, passes, faceoffs)
   - Shift stats (TOI, CF%, rating)
   - Zone stats (entries/exits)
   - Micro stats (dekes, drives, etc.)
   - **xG stats** ← **TARGET FOR IMPROVEMENT**
   - Strength splits, shot types, pass types
   - Composite stats (game score, WAR, etc.)
4. Apply formulas (per-60 rates, percentages)
5. Return stats dict

### Current xG Implementation
**Location:** `src/tables/core_facts.py::calculate_xg_stats()` (lines 1491-1515)

**Current Approach:**
- Simple lookup table based on `danger_level`
- Base rates: high=0.25, medium=0.08, low=0.03, default=0.06
- Single modifier: Rush = 1.3x
- Naive summation (no flurry adjustment)

**Limitations:**
- No Royal Road detection
- No distance/angle calculation (needs XY)
- No flurry adjustment
- No shooting talent adjustment
- Not using Gradient Boosting Machine

### Current WAR Implementation
**Location:** `src/tables/core_facts.py::calculate_war_stats()` (lines 1517-1524)

**Current Approach:**
- Weighted formula (GAR components)
- Components: Offense, Defense, Possession, Transition, Poise
- No RAPM (Ridge Regression)
- No player isolation from teammates

---

## Phase 1: Immediate Improvements (No XY Required)

### 1.1 Flurry Adjustment for xG

**Current Gap:** Naive xG summation (0.4 + 0.5 + 0.6 = 1.5 for 3 shots in sequence)  
**Research Prescription:** Probabilistic adjustment: $P(AtLeastOneGoal) = 1 - \prod_{i=1}^{n} (1 - xG_i)$

**Implementation Plan:**

**File:** `src/tables/core_facts.py`  
**Function:** `calculate_xg_stats()`  
**New Function:** `apply_flurry_adjustment(shot_sequence, xg_values)`

**Steps:**
1. **Identify Shot Sequences:**
   - Group shots within 3 seconds of each other
   - Same team, same stoppage (or consecutive events)
   - Use `event_start_seconds` or `event_time` from events table

2. **Apply Flurry Logic:**
   ```python
   def apply_flurry_adjustment(shot_sequence, xg_values):
       """
       Apply probabilistic flurry adjustment to xG sequence.
       
       Formula: P(AtLeastOneGoal) = 1 - ∏(1 - xG_i)
       
       Args:
           shot_sequence: List of shot events (same team, within 3s)
           xg_values: List of xG values for each shot
       
       Returns:
           Adjusted xG total for the sequence
       """
       if len(shot_sequence) <= 1:
           return sum(xg_values)
       
       # Probability of NOT scoring
       prob_no_goal = 1.0
       for xg in xg_values:
           prob_no_goal *= (1.0 - xg)
       
       # Probability of scoring at least once
       xg_flurry = 1.0 - prob_no_goal
       return min(xg_flurry, 0.99)  # Cap at 0.99
   ```

3. **Integration:**
   - Modify `calculate_xg_stats()` to:
     - Identify shot sequences (group by time)
     - Calculate raw xG for each shot
     - Apply flurry adjustment per sequence
     - Sum adjusted xG values
   - Keep `xg_for` as adjusted total
   - Add `xg_raw` (unadjusted) for comparison
   - Add `xg_flurry_adjustment` (difference) for tracking

**New Columns:**
- `xg_raw` - Unadjusted xG sum
- `xg_flurry_adjusted` - Flurry-adjusted xG (replaces `xg_for` or keep both)
- `xg_flurry_adjustment` - Difference (raw - adjusted)
- `shot_sequences_count` - Number of shot sequences

**Dependencies:**
- Event timing data (already available)
- Event sequencing (already tracked via `linked_event_index`)

**Effort:** Low (2-4 hours)  
**Risk:** Low (backward compatible, additive)

---

### 1.2 WDBE (Win Direction Based Events) for Faceoffs

**Current Gap:** Faceoffs tracked as simple win/loss  
**Research Prescription:** Value faceoffs by where puck goes (direction + clean vs scrum)

**Implementation Plan:**

**File:** `src/tables/core_facts.py`  
**Function:** `calculate_faceoff_zone_stats()` (already exists)  
**New Function:** `calculate_wdbe_faceoffs(player_id, game_id, event_players, events)`

**Steps:**
1. **Classify Faceoff Wins:**
   - **Clean Win:** Direct to teammate (no puck battle)
     - Check `play_detail1` or `play_detail2` for clean win indicators
     - Look for: "CleanWin", "Direct", "StraightBack", etc.
   - **Scrum Win:** Puck battle (less valuable)
     - Default if not clean

2. **Classify Direction:**
   - **Forward:** Puck goes toward offensive zone
   - **Back/Center:** Puck goes toward defensive zone (more valuable for D-zone FO)
   - **Neutral:** Stays in neutral zone
   - Use event_detail or next event location

3. **Calculate Expected Value:**
   - Historical data: What happens after each win type?
   - Clean Win Back (D-zone) → Expected next event: Clear (high value)
   - Clean Win Forward (O-zone) → Expected next event: Shot (high value)
   - Scrum Win → Expected next event: Turnover (low value)

4. **WDBE Formula:**
   ```python
   WDBE_weights = {
       ('Clean', 'Back', 'DZone'): 0.15,    # Defensive zone, clean back
       ('Clean', 'Forward', 'OZone'): 0.12,  # Offensive zone, clean forward
       ('Scrum', 'Back', 'DZone'): 0.08,     # Defensive zone, scrum
       ('Scrum', 'Forward', 'OZone'): 0.06,  # Offensive zone, scrum
       # ... other combinations
   }
   
   wdbe_value = sum(weights[win_type, direction, zone] for each faceoff)
   ```

5. **Integration:**
   - Add to `build_player_stats()`:
     - After `calculate_faceoff_zone_stats()`
     - Call `calculate_wdbe_faceoffs()`
     - Add WDBE columns to stats dict

**New Columns:**
- `faceoffs_clean_wins` - Clean faceoff wins
- `faceoffs_scrum_wins` - Scrum faceoff wins
- `faceoffs_wdbe_value` - Total WDBE value
- `faceoffs_wdbe_per_60` - WDBE per 60 minutes
- `faceoff_wdbe_rate` - WDBE value per faceoff win

**Dependencies:**
- Faceoff event data (already available)
- Play detail classification (already tracked)
- Next event tracking (may need enhancement)

**Effort:** Medium (4-6 hours)  
**Risk:** Low-Medium (requires classification logic refinement)

---

## Phase 2: XY-Dependent Features (When XY Available)

### 2.1 Royal Road Pass Detection

**Current Gap:** No Royal Road detection  
**Research Prescription:** Pass crossing y=0 line within 3s before shot

**Implementation Plan:**

**File:** `src/tables/core_facts.py`  
**Function:** `calculate_xg_stats()`  
**New Helper:** `detect_royal_road_pass(shot_event, previous_events)`

**Steps:**
1. **For each shot:**
   - Get previous event (within 3 seconds)
   - If previous event is a pass:
     - Get pass start/end coordinates (y1, y2)
     - Check if pass crosses y=0 line: `sign(y1) != sign(y2)`
     - If crosses AND time_diff < 3.0s: Royal Road = True

2. **Feature Engineering:**
   ```python
   royal_road = (
       (prev_event_type == 'Pass') and
       (time_diff < 3.0) and
       (sign(prev_event_y1) != sign(prev_event_y2))
   )
   ```

3. **xG Modifier:**
   - Add Royal Road multiplier (1.2x - 1.5x, to be calibrated)
   - Apply to base xG calculation

4. **Tracking:**
   - Count Royal Road passes
   - Track xG generated from Royal Road shots
   - Add to playmaking stats

**New Columns:**
- `royal_road_passes` - Count of Royal Road passes
- `royal_road_xg` - xG from Royal Road shots
- `royal_road_xg_per_60` - Rate

**Dependencies:**
- XY coordinates for passes and shots
- Event sequencing (already available)
- Time tracking (already available)

**Effort:** Low (2-3 hours, once XY available)  
**Risk:** Low

---

### 2.2 Distance and Angle Calculation for xG

**Current Gap:** Using danger_level lookup instead of distance/angle  
**Research Prescription:** Calculate from XY coordinates

**Implementation Plan:**

**File:** `src/tables/core_facts.py`  
**Function:** `calculate_xg_stats()`  
**New Helper:** `calculate_shot_distance_angle(x, y, net_x=89, net_y=0)`

**Steps:**
1. **Normalize Coordinates:**
   - Apply period-dependent normalization (see Section 2.2 in research)
   - Standardize to offensive half (net at x=89, y=0)

2. **Calculate Distance:**
   ```python
   distance = sqrt((net_x - x_norm)**2 + (net_y - y_norm)**2)
   ```

3. **Calculate Angle:**
   ```python
   angle = abs(arctan(y_norm / (net_x - x_norm))) * 180 / pi
   ```

4. **Replace Danger Level:**
   - Use distance/angle instead of `danger_level`
   - Map to xG base rate (or use in GBM model - Phase 3)

**New Columns:**
- `shot_distance_avg` - Average shot distance
- `shot_angle_avg` - Average shot angle
- `shots_high_danger_distance` - Shots from <20ft
- `shots_medium_danger_distance` - Shots from 20-40ft
- `shots_low_danger_distance` - Shots from >40ft

**Dependencies:**
- XY coordinates for shots
- Coordinate normalization (period-dependent)

**Effort:** Medium (4-6 hours, once XY available)  
**Risk:** Low-Medium (coordinate normalization needs testing)

---

### 2.3 Enhanced xG Model (Distance/Angle Based)

**Phase 2.3a: Distance/Angle Lookup Table (Quick Win)**

Replace danger_level lookup with distance-based lookup:

```python
def get_xg_from_distance_angle(distance, angle):
    """
    Get base xG from distance and angle.
    
    Base rates (to be calibrated):
    - Distance < 15ft: 0.30-0.40
    - Distance 15-25ft: 0.15-0.25
    - Distance 25-35ft: 0.08-0.15
    - Distance > 35ft: 0.03-0.08
    
    Angle penalty: Shots from wider angles have lower xG
    """
    # Distance base
    if distance < 15:
        base_xg = 0.35
    elif distance < 25:
        base_xg = 0.18
    elif distance < 35:
        base_xg = 0.10
    else:
        base_xg = 0.05
    
    # Angle adjustment
    angle_factor = cos(radians(angle * 0.8))
    base_xg *= max(angle_factor, 0.3)
    
    return base_xg
```

**Phase 2.3b: Gradient Boosting Machine (Long-term)**

See Phase 3 for full GBM implementation.

---

## Phase 3: Advanced Models (Future)

### 3.1 Gradient Boosting Machine (GBM) xG Model

**Current Gap:** Lookup table instead of GBM  
**Research Prescription:** XGBoost/LightGBM model with feature engineering

**Implementation Plan:**

**New File:** `src/models/xg_model.py`

**Steps:**
1. **Feature Engineering:**
   - Distance, angle (from XY)
   - Royal Road boolean
   - Shot type (wrist, slap, snap, tip)
   - Rush indicator
   - Time since zone entry
   - Previous event type
   - Game state (score, strength)

2. **Model Training:**
   - Train on historical shot/goal data
   - Use XGBoost or LightGBM
   - Cross-validation for hyperparameter tuning
   - Save model to file

3. **Integration:**
   - Load model in `calculate_xg_stats()`
   - Apply model to each shot
   - Store predictions

**New Files:**
- `src/models/xg_model.py` - Model definition and training
- `src/models/xg_model.pkl` - Trained model (gitignored)
- `scripts/train_xg_model.py` - Training script

**Dependencies:**
- XY coordinates
- Sufficient historical data (100+ games recommended)
- XGBoost or LightGBM library

**Effort:** High (20-40 hours)  
**Risk:** Medium (requires data, calibration, validation)

---

### 3.2 Shooting Talent Adjustment

**Current Gap:** No shooter quality adjustment  
**Research Prescription:** Bayesian regression on residuals

**Implementation Plan:**

**File:** `src/tables/core_facts.py`  
**Function:** `calculate_shooting_talent_adjustment(player_id, xg_residuals, shots_count)`

**Steps:**
1. **Calculate Residuals:**
   - For each player: `R = Goals - xG`
   - Aggregate across games/seasons

2. **Apply Regression:**
   ```python
   reg_threshold = 300  # Shots needed to regress halfway to mean
   shooting_talent = (R * shots) / (shots + reg_threshold)
   ```

3. **Adjust xG:**
   - `xg_adjusted = xg_raw + (shooting_talent / shots)`

**Integration:**
- Run after xG calculation
- Apply as post-processing step
- Store both raw and adjusted xG

**New Columns:**
- `shooting_talent_rating` - Regressed shooting talent
- `xg_adjusted_for_talent` - Talent-adjusted xG
- `xg_talent_adjustment` - Difference

**Dependencies:**
- Multi-game/multi-season data
- xG model (Phase 2 or 3)

**Effort:** Medium (6-8 hours)  
**Risk:** Low-Medium (requires sufficient data)

---

## Phase 4: RAPM Implementation (Separate System)

**Note:** RAPM is a different methodology that requires stint-level data structure. This is NOT a direct enhancement to `player_game_stats` but rather a replacement/complement system.

**Implementation:** Separate module (outside scope of this document)

---

## Implementation Priority Matrix

### Immediate (Phase 1)
| Feature | Effort | Impact | Risk | Priority |
|---------|--------|--------|------|----------|
| Flurry Adjustment | Low | High | Low | **P0** ✅ |
| WDBE Faceoffs | Medium | Medium | Low-Med | **P1** ✅ |

### XY-Dependent (Phase 2)
| Feature | Effort | Impact | Risk | Priority |
|---------|--------|--------|------|----------|
| Royal Road Detection | Low | High | Low | **P0** (with XY) |
| Distance/Angle Calc | Medium | High | Low-Med | **P0** (with XY) |
| Distance-Based xG | Medium | High | Low-Med | **P1** (with XY) |

### Advanced (Phase 3)
| Feature | Effort | Impact | Risk | Priority |
|---------|--------|--------|------|----------|
| GBM xG Model | High | Very High | Medium | **P2** (after XY + data) |
| Shooting Talent | Medium | Medium | Low-Med | **P2** (after xG model) |

---

## Detailed Implementation: Phase 1.1 - Flurry Adjustment

### Code Changes

**File:** `src/tables/core_facts.py`

**1. Add Flurry Adjustment Function (after calculate_xg_stats):**

```python
def apply_flurry_adjustment_to_shots(shot_events: pd.DataFrame) -> Dict[str, float]:
    """
    Apply probabilistic flurry adjustment to xG values.
    
    Groups shots into sequences (within 3 seconds, same team) and applies
    the formula: P(AtLeastOneGoal) = 1 - ∏(1 - xG_i)
    
    Args:
        shot_events: DataFrame with columns:
            - event_start_seconds (or event_time)
            - xg_value (raw xG for each shot)
            - event_team_id (to group by team)
            - event_id
    
    Returns:
        Dict with:
            - xg_raw: Unadjusted sum
            - xg_flurry_adjusted: Adjusted total
            - xg_flurry_adjustment: Difference
            - shot_sequences_count: Number of sequences
    """
    if len(shot_events) == 0:
        return {
            'xg_raw': 0.0,
            'xg_flurry_adjusted': 0.0,
            'xg_flurry_adjustment': 0.0,
            'shot_sequences_count': 0
        }
    
    # Sort by time
    shot_events = shot_events.sort_values('event_start_seconds')
    
    # Group into sequences (shots within 3 seconds)
    sequences = []
    current_sequence = []
    
    for idx, shot in shot_events.iterrows():
        if len(current_sequence) == 0:
            current_sequence.append(shot)
        else:
            last_shot_time = current_sequence[-1]['event_start_seconds']
            time_diff = shot['event_start_seconds'] - last_shot_time
            
            # Same team and within 3 seconds = same sequence
            if (time_diff <= 3.0 and 
                shot['event_team_id'] == current_sequence[-1]['event_team_id']):
                current_sequence.append(shot)
            else:
                # Start new sequence
                sequences.append(current_sequence)
                current_sequence = [shot]
    
    if len(current_sequence) > 0:
        sequences.append(current_sequence)
    
    # Calculate adjusted xG for each sequence
    xg_raw = shot_events['xg_value'].sum()
    xg_adjusted = 0.0
    
    for sequence in sequences:
        if len(sequence) == 1:
            # Single shot: no adjustment needed
            xg_adjusted += sequence[0]['xg_value']
        else:
            # Multiple shots: apply flurry adjustment
            xg_values = [s['xg_value'] for s in sequence]
            prob_no_goal = 1.0
            for xg in xg_values:
                prob_no_goal *= (1.0 - xg)
            xg_flurry = 1.0 - prob_no_goal
            xg_adjusted += min(xg_flurry, 0.99)
    
    return {
        'xg_raw': round(xg_raw, 3),
        'xg_flurry_adjusted': round(xg_adjusted, 3),
        'xg_flurry_adjustment': round(xg_raw - xg_adjusted, 3),
        'shot_sequences_count': len(sequences)
    }
```

**2. Modify calculate_xg_stats() to use flurry adjustment:**

```python
def calculate_xg_stats(player_id, game_id, event_players, events):
    # ... existing code to get player_shots ...
    
    if len(player_shots) == 0: return empty
    
    # Calculate raw xG for each shot
    shot_xg_values = []
    goals_total = 0
    
    for _, shot in player_shots.iterrows():
        danger = str(shot.get('danger_level', 'default')).lower()
        base_xg = XG_BASE_RATES.get(danger, XG_BASE_RATES['default'])
        xg = base_xg * (XG_MODIFIERS['rush'] if shot.get('is_rush') == 1 else 1.0)
        shot_xg_values.append({
            'event_id': shot.get('event_id'),
            'event_start_seconds': shot.get('event_start_seconds', 0),
            'event_team_id': shot.get('event_team_id', ''),
            'xg_value': min(xg, 0.95)
        })
        
        if str(shot.get('event_type', '')).lower() == 'goal':
            goals_total += 1
    
    # Apply flurry adjustment
    shot_df = pd.DataFrame(shot_xg_values)
    flurry_result = apply_flurry_adjustment_to_shots(shot_df)
    
    return {
        'xg_raw': flurry_result['xg_raw'],
        'xg_for': flurry_result['xg_flurry_adjusted'],  # Keep existing name
        'xg_flurry_adjustment': flurry_result['xg_flurry_adjustment'],
        'shot_sequences_count': flurry_result['shot_sequences_count'],
        'goals_actual': goals_total,
        'goals_above_expected': round(goals_total - flurry_result['xg_flurry_adjusted'], 2),
        'xg_per_shot': round(flurry_result['xg_flurry_adjusted'] / len(player_shots), 3) if len(player_shots) > 0 else 0.0,
        'shots_for_xg': len(player_shots),
        'finishing_skill': round(goals_total / flurry_result['xg_flurry_adjusted'], 2) if flurry_result['xg_flurry_adjusted'] > 0 else 0.0,
    }
```

**3. Update empty dict:**
```python
empty = {
    'xg_for': 0.0, 'xg_raw': 0.0, 'xg_flurry_adjustment': 0.0,
    'shot_sequences_count': 0,
    'goals_actual': 0, 'goals_above_expected': 0.0,
    'xg_per_shot': 0.0, 'shots_for_xg': 0, 'finishing_skill': 0.0
}
```

### Testing

**Test Cases:**
1. Single shot: xG = 0.3 → Raw = 0.3, Adjusted = 0.3
2. Two shots in sequence: xG = [0.3, 0.4] → Raw = 0.7, Adjusted = 1 - (0.7 * 0.6) = 0.58
3. Three shots in sequence: xG = [0.4, 0.5, 0.6] → Raw = 1.5, Adjusted = 1 - (0.6 * 0.5 * 0.4) = 0.88
4. Two separate sequences: xG = [0.3, 0.4] (seq1), [0.2] (seq2) → Raw = 0.9, Adjusted = 0.58 + 0.2 = 0.78

### Backward Compatibility

- Keep `xg_for` as the main column (now flurry-adjusted)
- Add `xg_raw` for unadjusted comparison
- Existing formulas/views will use `xg_for` (adjusted) - this is correct behavior

---

## Detailed Implementation: Phase 1.2 - WDBE Faceoffs

### Code Changes

**File:** `src/tables/core_facts.py`

**1. Add WDBE Calculation Function:**

```python
def calculate_wdbe_faceoffs(player_id, game_id, event_players, events):
    """
    Calculate Win Direction Based Events (WDBE) for faceoffs.
    
    Values faceoffs by where puck goes (direction) and win type (clean vs scrum).
    
    Returns:
        Dict with WDBE metrics
    """
    pe = event_players[(event_players['game_id'] == game_id) & 
                       (event_players['player_id'] == player_id)]
    
    empty = {
        'faceoffs_clean_wins': 0,
        'faceoffs_scrum_wins': 0,
        'faceoffs_wdbe_value': 0.0,
        'faceoffs_wdbe_per_60': 0.0,
        'faceoff_wdbe_rate': 0.0
    }
    
    if len(pe) == 0:
        return empty
    
    # Get faceoff events where player is event_player_1 (winner)
    pe_primary = pe[pe['player_role'].astype(str).str.lower() == PRIMARY_PLAYER]
    faceoff_wins = pe_primary[pe_primary['event_type'].astype(str).str.lower() == 'faceoff']
    
    if len(faceoff_wins) == 0:
        return empty
    
    # WDBE weights (to be calibrated with historical data)
    WDBE_WEIGHTS = {
        'clean_forward': 0.12,   # Clean win, forward direction
        'clean_back': 0.15,      # Clean win, back direction (more valuable)
        'clean_neutral': 0.08,   # Clean win, neutral
        'scrum_forward': 0.06,   # Scrum win, forward
        'scrum_back': 0.08,      # Scrum win, back
        'scrum_neutral': 0.04,   # Scrum win, neutral
    }
    
    clean_wins = 0
    scrum_wins = 0
    wdbe_total = 0.0
    
    # Get faceoff events for context
    faceoff_event_ids = faceoff_wins['event_id'].unique()
    faceoff_events = events[(events['game_id'] == game_id) & 
                           (events['event_id'].isin(faceoff_event_ids))]
    
    for _, faceoff in faceoff_wins.iterrows():
        event_id = faceoff['event_id']
        faceoff_event = faceoff_events[faceoff_events['event_id'] == event_id]
        
        if len(faceoff_event) == 0:
            continue
        
        event_row = faceoff_event.iloc[0]
        
        # Classify win type
        play_detail = str(event_row.get('play_detail1', '') + ' ' + 
                         event_row.get('play_detail_2', '')).lower()
        is_clean = any(term in play_detail for term in 
                      ['clean', 'direct', 'straight', 'won clean'])
        
        # Classify direction (simplified - can be enhanced with XY)
        # For now, use event_detail or next event
        direction = 'neutral'  # Default
        event_detail = str(event_row.get('event_detail', '')).lower()
        if 'forward' in event_detail or 'ahead' in event_detail:
            direction = 'forward'
        elif 'back' in event_detail or 'behind' in event_detail:
            direction = 'back'
        
        # Count wins
        if is_clean:
            clean_wins += 1
            wdbe_key = f'clean_{direction}'
        else:
            scrum_wins += 1
            wdbe_key = f'scrum_{direction}'
        
        # Add WDBE value
        wdbe_total += WDBE_WEIGHTS.get(wdbe_key, 0.06)
    
    return {
        'faceoffs_clean_wins': clean_wins,
        'faceoffs_scrum_wins': scrum_wins,
        'faceoffs_wdbe_value': round(wdbe_total, 2),
        'faceoffs_wdbe_per_60': 0.0,  # Will be calculated by formula
        'faceoff_wdbe_rate': round(wdbe_total / (clean_wins + scrum_wins), 3) if (clean_wins + scrum_wins) > 0 else 0.0
    }
```

**2. Add to build_player_stats():**

```python
# In build_player_stats(), after calculate_faceoff_zone_stats():
stats.update(calculate_faceoff_zone_stats(player_id, game_id, event_players))
stats.update(calculate_wdbe_faceoffs(player_id, game_id, event_players, events))  # NEW
```

**3. Add WDBE per-60 formula:**

**File:** `src/formulas/player_stats_formulas.py`

```python
'faceoffs_wdbe_per_60': {
    'type': 'rate',
    'function': lambda df: pd.Series([
        calculate_per_60_rate(wdbe, toi) if pd.notna(toi) else None
        for wdbe, toi in zip(df.get('faceoffs_wdbe_value', pd.Series([0]*len(df))), df['toi_minutes'])
    ]),
    'description': 'WDBE faceoff value per 60 minutes',
    'dependencies': ['faceoffs_wdbe_value', 'toi_minutes'],
},
```

### Testing

**Test Cases:**
1. Player with 10 clean forward wins: WDBE = 10 * 0.12 = 1.2
2. Player with 5 clean back wins: WDBE = 5 * 0.15 = 0.75
3. Player with mixed wins: Verify correct classification
4. Zero faceoffs: Returns empty dict

### Calibration

- WDBE weights need calibration with historical data
- Track: What happens after each win type?
- Adjust weights based on expected value (shots, clears, turnovers)

---

## Integration Checklist

### Phase 1.1 - Flurry Adjustment
- [ ] Add `apply_flurry_adjustment_to_shots()` function
- [ ] Modify `calculate_xg_stats()` to use flurry adjustment
- [ ] Update empty dict with new columns
- [ ] Update `calculate_war_stats()` if needed (uses xg_for)
- [ ] Add tests
- [ ] Update documentation (CALCULATION_LOG.md)
- [ ] Run validation on existing data

### Phase 1.2 - WDBE Faceoffs
- [ ] Add `calculate_wdbe_faceoffs()` function
- [ ] Add to `build_player_stats()` flow
- [ ] Add WDBE per-60 formula
- [ ] Update empty dict
- [ ] Add tests
- [ ] Update documentation
- [ ] Calibrate weights with historical data

### Phase 2 - XY-Dependent (When XY Available)
- [ ] Coordinate normalization function
- [ ] Royal Road detection
- [ ] Distance/angle calculation
- [ ] Distance-based xG lookup
- [ ] Integration with existing xG

### Phase 3 - Advanced Models (Future)
- [ ] GBM model training infrastructure
- [ ] Model integration
- [ ] Shooting talent calculation
- [ ] Multi-season data aggregation

---

## Backward Compatibility Strategy

1. **Additive Changes:** All new features add columns, don't remove existing ones
2. **Default Values:** New columns default to 0 or existing behavior
3. **Formula Updates:** Existing formulas continue to work (may use adjusted values)
4. **Gradual Migration:** Phase in changes incrementally
5. **Feature Flags:** Consider feature flags for new calculations (optional)

---

## Testing Strategy

1. **Unit Tests:** Test each new function in isolation
2. **Integration Tests:** Test full `build_player_stats()` flow
3. **Validation Tests:** Compare results to previous version
4. **Edge Cases:** Empty data, single events, boundary conditions
5. **Performance Tests:** Ensure no significant slowdown

---

## Documentation Updates

1. **CALCULATION_LOG.md:** Document new formulas
2. **DATA_DICTIONARY.md:** Document new columns
3. **SRC_MODULES_GUIDE.md:** Update module descriptions
4. **RESEARCH_PAPER_ANALYSIS.md:** Reference this implementation plan

---

## Next Steps

1. **Review this plan** with team
2. **Prioritize features** based on business needs
3. **Start with Phase 1.1** (Flurry Adjustment) - lowest risk, high impact
4. **Validate Phase 1** before moving to Phase 2
5. **Prepare for XY integration** (Phase 2)
6. **Plan advanced models** (Phase 3) when sufficient data available
