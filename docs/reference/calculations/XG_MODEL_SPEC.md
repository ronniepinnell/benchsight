# xG Model Specification: Current vs. Industry Standard

> **Purpose:** Comprehensive documentation of BenchSight's Expected Goals (xG) model, comparing the current lookup-based implementation to industry-standard GBM/XGBoost approaches.

**Version:** 1.0
**Last Updated:** 2026-01-21
**Owner:** Analytics Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current Implementation: Lookup-Based xG](#2-current-implementation-lookup-based-xg)
3. [Industry Standard: GBM/XGBoost xG](#3-industry-standard-gbmxgboost-xg)
4. [Feature Engineering](#4-feature-engineering)
5. [Flurry Adjustment](#5-flurry-adjustment)
6. [Shooting Talent Adjustment](#6-shooting-talent-adjustment)
7. [Gap Analysis](#7-gap-analysis)
8. [Implementation Roadmap](#8-implementation-roadmap)

---

## 1. Executive Summary

### Current State
BenchSight uses a **lookup table approach** for xG calculation:
- Assigns base rates by danger zone (High: 0.25, Medium: 0.08, Low: 0.03)
- Applies multiplicative modifiers (rush: 1.3x, rebound: 1.5x, etc.)
- Simple, interpretable, but lacks granularity

### Target State
Industry leaders use **gradient boosting models (GBM/XGBoost)**:
- 20+ input features (distance, angle, shot type, game state, etc.)
- Nonlinear interactions captured automatically
- Calibrated probabilities with higher accuracy

### Key Gaps
1. **No ML model** - Lookup table vs. trained classifier
2. **No flurry adjustment** - Naive xG summation overstates clustered shots
3. **No royal road feature** - Missing key lateral pass detection
4. **No shooting talent adjustment** - Raw xG ignores individual skill

---

## 2. Current Implementation: Lookup-Based xG

### 2.1 Architecture

**Type:** Rule-based lookup with multiplicative modifiers
**Code Location:** `src/tables/core_facts.py:56-58`, `src/tables/event_analytics.py:303-356`

### 2.2 Base Rate Lookup

**Danger Zone Classification:**

| Zone | Distance | Angle | Base xG |
|------|----------|-------|---------|
| High Danger | 0-12 ft | <45° | 0.25 |
| Medium Danger | 12-30 ft | <60° | 0.08 |
| Low Danger | 30+ ft or >60° | Any | 0.03 |
| Default | Unknown | Unknown | 0.06 |

**Implementation:**
```python
def get_base_xg(danger_zone):
    base_rates = {
        'High': 0.25,
        'Medium': 0.08,
        'Low': 0.03,
        'Perimeter': 0.01,
        'Default': 0.06
    }
    return base_rates.get(danger_zone, 0.06)
```

### 2.3 Modifier System

**Pre-Shot Context Modifiers:**

| Modifier | Value | Detection Criteria |
|----------|-------|-------------------|
| Rush | 1.3 | Zone entry within 5 events/10 seconds |
| Rebound | 1.5 | Shot within 3 seconds of prior save/block |
| One-Timer | 1.4 | Pass-to-shot within 1.5 seconds |
| Breakaway | 2.5 | 1-on-0 with goalie |
| Screened | 1.2 | Screen event flagged |
| Deflection | 1.3 | Tip/deflection in event_detail_2 |

**Shot Type Modifiers:**

| Shot Type | Value | Rationale |
|-----------|-------|-----------|
| Wrist | 1.0 | Baseline |
| Slap | 0.95 | Lower accuracy |
| Snap | 1.05 | Quick release |
| Backhand | 0.9 | Harder angle |
| Tip | 1.15 | Redirections effective |
| Wrap-around | 0.7 | Low percentage |

### 2.4 xG Calculation Formula

```python
def calculate_xg(shot):
    # Base rate from danger zone
    base = get_base_xg(shot['danger_zone'])

    # Apply context modifiers
    modifiers = 1.0
    if shot['is_rush']:
        modifiers *= 1.3
    if shot['is_rebound']:
        modifiers *= 1.5
    if shot['is_one_timer']:
        modifiers *= 1.4
    if shot['is_breakaway']:
        modifiers *= 2.5
    if shot['is_screened']:
        modifiers *= 1.2
    if shot['is_deflection']:
        modifiers *= 1.3

    # Shot type modifier
    shot_type_mod = get_shot_type_modifier(shot['shot_type'])
    modifiers *= shot_type_mod

    # Cap at reasonable maximum
    xg = min(base * modifiers, 0.95)

    return xg
```

### 2.5 XY-Based Enhancement

When XY coordinates are available:

```python
def calculate_xg_xy(shot):
    """XY-based xG with distance/angle."""
    # Goal location (center of net)
    goal_x = 0  # Goal line
    goal_y = 0  # Center

    # Calculate distance
    distance = sqrt((shot['x'] - goal_x)**2 + (shot['y'] - goal_y)**2)

    # Calculate angle (radians to degrees)
    angle = abs(atan2(shot['y'], shot['x'])) * (180 / pi)

    # Distance decay factor
    distance_factor = max(0.01, 0.35 - (distance * 0.008))

    # Angle adjustment (shots from center more dangerous)
    angle_factor = cos(angle * pi / 180)

    # Base xG from XY
    base_xg = distance_factor * angle_factor

    # Apply modifiers
    return base_xg * get_modifiers(shot)
```

### 2.6 Current Limitations

| Limitation | Impact |
|------------|--------|
| Discrete zones | Loses granularity between zone boundaries |
| Linear modifiers | Cannot capture nonlinear interactions |
| No calibration | Probabilities may not reflect true conversion rates |
| Fixed weights | Same modifiers regardless of context |
| No game state | Score/period not considered |
| No shooter handedness | Left/right hand affects angle |
| No goalie factors | All goalies treated equally |

---

## 3. Industry Standard: GBM/XGBoost xG

### 3.1 Model Architecture

**Industry Leaders:**
| Source | Model | Features | Training Data |
|--------|-------|----------|---------------|
| MoneyPuck | XGBoost | 22 features | 10+ NHL seasons |
| Evolving Hockey | GBM | 18 features | 10+ NHL seasons |
| NHL Edge | Proprietary | Unknown | Tracking data |
| Sportlogiq | Ensemble | 30+ features | Multi-league |

### 3.2 XGBoost Model Specification

**Target Variable:**
- Binary: Goal (1) or No Goal (0)

**Model Type:**
- XGBoost Classifier (binary logistic)
- Output: Probability of goal [0, 1]

**Hyperparameters (Typical):**
```python
xgb_params = {
    'objective': 'binary:logistic',
    'eval_metric': 'logloss',
    'max_depth': 6,
    'learning_rate': 0.05,
    'n_estimators': 500,
    'min_child_weight': 50,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'scale_pos_weight': 10,  # Handle class imbalance (goals rare)
    'random_state': 42
}
```

### 3.3 Feature Set

**Core Spatial Features:**

| Feature | Type | Description |
|---------|------|-------------|
| distance | float | Distance to goal center (feet) |
| angle | float | Angle to goal (degrees, 0 = straight on) |
| x_coord | float | Horizontal position |
| y_coord | float | Vertical position (side-to-side) |

**Shot Context Features:**

| Feature | Type | Description |
|---------|------|-------------|
| shot_type | categorical | Wrist, slap, snap, backhand, tip |
| is_rebound | bool | Shot within 3s of prior shot |
| is_rush | bool | Shot within 10s of zone entry |
| is_one_timer | bool | Shot within 1.5s of pass |
| is_royal_road | bool | Pass crossed center ice before shot |
| time_since_last_event | float | Seconds since prior event |
| last_event_type | categorical | Pass, faceoff win, rebound, etc. |
| last_event_x | float | X of prior event |
| last_event_y | float | Y of prior event |

**Game State Features:**

| Feature | Type | Description |
|---------|------|-------------|
| strength | categorical | 5v5, 5v4, 4v5, etc. |
| score_diff | int | Shooter's team goal differential |
| period | int | 1, 2, 3, OT |
| time_remaining | float | Seconds left in period |
| is_home | bool | Shooter on home team |

**Shooter/Goalie Features:**

| Feature | Type | Description |
|---------|------|-------------|
| shooter_hand | categorical | L/R (affects angle advantage) |
| shooter_xg_history | float | Shooter's career xG/shot (talent) |
| goalie_gsax | float | Goalie's GSAx (save ability) |

**Derived Features:**

| Feature | Calculation |
|---------|-------------|
| speed_into_zone | distance / time_since_entry |
| angle_change | angle - last_event_angle |
| royal_road_angle | angle of pass relative to goal line |

### 3.4 Training Process

```python
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV

def train_xg_model(shots_df):
    """Train XGBoost xG model with calibration."""

    # Feature columns
    features = [
        'distance', 'angle', 'shot_type_encoded',
        'is_rebound', 'is_rush', 'is_one_timer', 'is_royal_road',
        'time_since_last_event', 'last_event_type_encoded',
        'strength_encoded', 'score_diff', 'period',
        'shooter_hand_encoded', 'is_home'
    ]

    X = shots_df[features]
    y = shots_df['is_goal']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train XGBoost
    model = XGBClassifier(**xgb_params)
    model.fit(X_train, y_train)

    # Calibrate probabilities (isotonic regression)
    calibrated = CalibratedClassifierCV(model, method='isotonic', cv=5)
    calibrated.fit(X_train, y_train)

    return calibrated

def predict_xg(model, shot):
    """Predict xG for a single shot."""
    features = extract_features(shot)
    xg = model.predict_proba(features)[0, 1]
    return xg
```

### 3.5 Calibration

**Why Calibration Matters:**
Raw XGBoost probabilities may not be well-calibrated (e.g., predicting 0.20 but actual conversion rate is 0.15).

**Methods:**
1. **Isotonic Regression:** Non-parametric, flexible
2. **Platt Scaling:** Logistic sigmoid transformation
3. **Temperature Scaling:** Single parameter adjustment

**Validation:**
- Reliability diagram (calibration curve)
- Brier score (lower = better calibrated)

---

## 4. Feature Engineering

### 4.1 Royal Road Detection

**Definition:** A pass that crosses the center line (y=0) within 3 seconds before a shot.

**Implementation:**
```python
def detect_royal_road(shot, previous_events):
    """
    Detect if shot was preceded by royal road pass.

    Royal road = pass crossing y=0 forcing goalie lateral movement.
    """
    # Find most recent pass before shot
    passes = [e for e in previous_events
              if e['event_type'] == 'Pass'
              and (shot['time'] - e['time']) <= 3.0]

    if not passes:
        return False

    last_pass = passes[-1]

    # Check if pass crossed center (y=0)
    pass_start_y = last_pass['start_y']
    pass_end_y = last_pass['end_y']

    # Opposite sides of center = crossed royal road
    if pass_start_y * pass_end_y < 0:
        return True

    return False
```

**Why It Matters:**
- Lateral movement is hardest for goalies
- Royal road shots have ~40% higher conversion rate
- Industry xG models weight this heavily

### 4.2 Pre-Shot Movement

**Concept:** Track what happened immediately before the shot.

**Features:**
```python
def extract_pre_shot_features(shot, events):
    """Extract features from events leading to shot."""

    # Time since last event
    prev_event = get_previous_event(shot, events)
    time_since = shot['time'] - prev_event['time']

    # Event type sequence
    recent_events = get_events_within(events, shot['time'], window=5)
    event_sequence = [e['event_type'] for e in recent_events]

    # Pass characteristics
    if prev_event['event_type'] == 'Pass':
        pass_distance = calculate_distance(
            prev_event['start_x'], prev_event['start_y'],
            prev_event['end_x'], prev_event['end_y']
        )
        pass_angle = calculate_angle(prev_event)
    else:
        pass_distance = 0
        pass_angle = 0

    return {
        'time_since_last_event': time_since,
        'last_event_type': prev_event['event_type'],
        'pass_distance': pass_distance,
        'pass_angle': pass_angle,
        'events_in_5s': len(recent_events)
    }
```

### 4.3 Shooter Handedness

**Why It Matters:**
- Right-handed shooters have better angles from left side
- Left-handed shooters have better angles from right side
- Backhand attempts affected by hand

**Implementation:**
```python
def adjust_for_handedness(shot, shooter_hand):
    """Calculate handedness advantage."""

    # Shot from left side (negative y)
    if shot['y'] < 0:
        if shooter_hand == 'R':
            return 1.05  # Forehand side
        else:
            return 0.95  # Backhand side

    # Shot from right side (positive y)
    else:
        if shooter_hand == 'L':
            return 1.05  # Forehand side
        else:
            return 0.95  # Backhand side
```

---

## 5. Flurry Adjustment

### 5.1 The Problem

When multiple shots occur in rapid succession (flurry), naive xG summation overstates expected goals.

**Example:**
- Shot 1: xG = 0.10
- Shot 2 (rebound): xG = 0.15
- Shot 3 (scramble): xG = 0.08

**Naive sum:** 0.10 + 0.15 + 0.08 = 0.33

**Reality:** Only one goal can be scored. The probability of at least one goal is less than the sum.

### 5.2 Probability-Correct Formula

**Complement Method:**
```
P(at least one goal) = 1 - P(no goals)
                     = 1 - [(1 - xG_1) * (1 - xG_2) * (1 - xG_3)]
```

**Example:**
```
P(at least one) = 1 - [(1 - 0.10) * (1 - 0.15) * (1 - 0.08)]
                = 1 - [0.90 * 0.85 * 0.92]
                = 1 - 0.704
                = 0.296
```

**Difference:** Naive (0.33) vs. Adjusted (0.296) = 10% overstatement

### 5.3 Flurry Detection

```python
def detect_flurries(shots_df, window=3.0):
    """
    Group shots into flurries.

    Flurry = 2+ shots within 3 seconds by same team.
    """
    shots_df = shots_df.sort_values(['game_id', 'time'])

    flurry_id = 0
    flurries = []

    for i, shot in shots_df.iterrows():
        # Check previous shots
        recent = shots_df[
            (shots_df['game_id'] == shot['game_id']) &
            (shots_df['team'] == shot['team']) &
            (shots_df['time'] >= shot['time'] - window) &
            (shots_df['time'] < shot['time'])
        ]

        if len(recent) > 0:
            # Part of existing flurry
            flurries.append(flurry_id)
        else:
            # New flurry
            flurry_id += 1
            flurries.append(flurry_id)

    shots_df['flurry_id'] = flurries
    return shots_df
```

### 5.4 Adjusted xG Calculation

```python
def calculate_flurry_adjusted_xg(shots_df):
    """
    Calculate flurry-adjusted xG.

    Returns both naive and adjusted totals.
    """
    shots_df = detect_flurries(shots_df)

    results = []

    for flurry_id, group in shots_df.groupby('flurry_id'):
        xg_list = group['xg'].tolist()

        # Naive sum
        naive_xg = sum(xg_list)

        # Probability-adjusted
        prob_no_goal = 1.0
        for xg in xg_list:
            prob_no_goal *= (1 - xg)
        adjusted_xg = 1 - prob_no_goal

        results.append({
            'flurry_id': flurry_id,
            'shot_count': len(xg_list),
            'naive_xg': naive_xg,
            'adjusted_xg': adjusted_xg,
            'overstatement': naive_xg - adjusted_xg
        })

    return pd.DataFrame(results)
```

### 5.5 Impact Analysis

**Typical Overstatement:**
- 2-shot flurry: 5-10% overstatement
- 3-shot flurry: 10-15% overstatement
- 4+ shot flurry: 15-25% overstatement

**Season Impact:**
- ~10-15% of shots occur in flurries
- Total xG overstatement: 3-5% per team

---

## 6. Shooting Talent Adjustment

### 6.1 The Problem

Raw xG treats all shooters equally. In reality:
- Elite finishers convert above expected
- Poor shooters convert below expected

Without adjustment, xG over-credits poor shooters and under-credits elite finishers.

### 6.2 Bayesian Shrinkage

**Concept:** Regress individual shooting talent toward league average based on sample size.

**Formula:**
```
Talent_adjusted = (n * Individual_Rate + k * League_Rate) / (n + k)
```

**Where:**
- n = player's shot count
- k = shrinkage constant (typically 100-200 shots)
- Individual_Rate = player's historical goals/shot
- League_Rate = league average goals/shot

**Example:**
- Player A: 3 goals on 15 shots (20% rate)
- League average: 8%
- Shrinkage k = 100

```
Adjusted = (15 * 0.20 + 100 * 0.08) / (15 + 100)
         = (3.0 + 8.0) / 115
         = 0.096 (9.6%)
```

Player regresses from 20% toward league average due to small sample.

### 6.3 Implementation

```python
def calculate_shooting_talent(player_shots_df, league_rate=0.08, shrinkage=100):
    """
    Calculate shooting talent with Bayesian shrinkage.
    """
    player_stats = player_shots_df.groupby('player_id').agg({
        'is_goal': 'sum',
        'shot_id': 'count'
    }).rename(columns={'is_goal': 'goals', 'shot_id': 'shots'})

    # Raw shooting percentage
    player_stats['raw_pct'] = player_stats['goals'] / player_stats['shots']

    # Bayesian adjusted
    player_stats['adjusted_pct'] = (
        (player_stats['shots'] * player_stats['raw_pct'] + shrinkage * league_rate) /
        (player_stats['shots'] + shrinkage)
    )

    # Talent multiplier relative to league average
    player_stats['talent_multiplier'] = player_stats['adjusted_pct'] / league_rate

    return player_stats


def apply_shooting_talent(shot, talent_lookup):
    """
    Adjust xG for shooter talent.
    """
    base_xg = calculate_base_xg(shot)

    talent_mult = talent_lookup.get(shot['player_id'], 1.0)

    adjusted_xg = base_xg * talent_mult

    return min(adjusted_xg, 0.95)  # Cap at 95%
```

### 6.4 When to Apply

**Use Shooting Talent Adjustment:**
- Season-level analysis
- Player comparisons
- Future performance prediction

**Don't Use (Use Raw xG):**
- Single-game analysis
- Team-level totals
- Goalie evaluation (GSAx)

---

## 7. Gap Analysis

### 7.1 Feature Comparison

| Feature | BenchSight | MoneyPuck | Evolving Hockey |
|---------|------------|-----------|-----------------|
| Distance | Zone-based | Continuous | Continuous |
| Angle | Zone-based | Continuous | Continuous |
| Shot type | Yes | Yes | Yes |
| Rebound | Yes | Yes | Yes |
| Rush | Yes | Yes | Yes |
| One-timer | Yes | Yes | Yes |
| Royal road | NO | Yes | Yes |
| Time since event | Partial | Yes | Yes |
| Score state | NO | Yes | Yes |
| Period | NO | Yes | Yes |
| Shooter hand | NO | Yes | Yes |
| Goalie factors | NO | Yes | Yes |
| Flurry adjustment | NO | Yes | Yes |
| Shooting talent | NO | Yes | Yes |

### 7.2 Model Comparison

| Aspect | BenchSight | Industry |
|--------|------------|----------|
| Model type | Lookup table | XGBoost/GBM |
| Features | 10 | 20-30 |
| Calibration | None | Isotonic/Platt |
| Training data | N/A | 10+ seasons |
| Interactions | Linear only | Nonlinear |
| Accuracy | ~70% AUC | ~78% AUC |

### 7.3 Impact of Gaps

| Gap | Impact Severity | Fix Complexity |
|-----|-----------------|----------------|
| No ML model | HIGH | HIGH |
| No flurry adjustment | MEDIUM | LOW |
| No royal road | MEDIUM | MEDIUM (needs XY) |
| No shooting talent | LOW | LOW |
| No game state features | LOW | LOW |

---

## 8. Implementation Roadmap

### 8.1 Phase 1: Quick Wins (No XY Required)

**Priority:** P0-P1

1. **Flurry Adjustment** (P0)
   - Implement flurry detection
   - Apply probability formula
   - Update xG aggregations

2. **Game State Features** (P1)
   - Add score_diff to xG calculation
   - Add period weighting

3. **Shooting Talent** (P1)
   - Calculate historical rates
   - Apply Bayesian shrinkage

### 8.2 Phase 2: XY-Dependent Features

**Priority:** P1-P2 (Requires XY coordinates)

4. **Royal Road Detection** (P1)
   - Track pass trajectory
   - Detect center-crossing passes

5. **Continuous Distance/Angle** (P1)
   - Replace zone lookup with continuous calculation

6. **Pre-Shot Movement** (P2)
   - Time since last event
   - Pass distance/angle

### 8.3 Phase 3: ML Model

**Priority:** P1 (After sufficient data)

7. **XGBoost Implementation**
   - Feature engineering pipeline
   - Model training infrastructure
   - Calibration process

8. **Model Validation**
   - Cross-validation
   - Calibration curves
   - Feature importance analysis

### 8.4 Data Requirements

| Phase | Requirement | Current Status |
|-------|-------------|----------------|
| 1 | Shot events with timestamps | AVAILABLE |
| 2 | XY coordinates | PARTIAL |
| 3 | Multi-season training data | AVAILABLE (4 games) |
| 3 | Historical shooter stats | AVAILABLE |

---

## Appendix: xG Calibration Targets

**Ideal Calibration:**
| Predicted xG Range | Actual Conversion Rate |
|--------------------|----------------------|
| 0.00-0.05 | ~2-3% |
| 0.05-0.10 | ~7-8% |
| 0.10-0.15 | ~12-13% |
| 0.15-0.25 | ~18-22% |
| 0.25-0.40 | ~30-35% |
| 0.40+ | ~50%+ |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-21 | Analytics Team | Initial xG model specification |
