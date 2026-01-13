# BenchSight Calculation Log

Last Updated: 2026-01-12
Version: 27.2

This document provides detailed formulas and methodologies for all calculated statistics.

---

## Goal Counting (CRITICAL - Single Source of Truth)

```python
# THE canonical way to identify goals
def is_goal_scored(df):
    return (
        (df['event_type'].str.lower() == 'goal') &
        (df['event_detail'].str.lower().str.contains('goal_scored'))
    )
```

**Player Attribution (CRITICAL):**
- `event_player_1` = Gets credit for ALL events (scorer, shooter, passer, etc.)
- Only `event_player_1` counts for shots, passes, turnovers, etc.

**Assist Tracking:**
- Assists are tracked via `play_detail1` column on the assist event (not on goal event)
- `play_detail1='AssistPrimary'` → Primary assist (A1)
- `play_detail1='AssistSecondary'` → Secondary assist (A2)
- The assister is `event_player_1` on their pass/shot event

**Faceoff Win/Loss:**
- Winner = `event_player_1` on faceoff event
- Loser = `opp_player_1` on faceoff event

**play_detail Counting:**
- For `play_detail1/2` counts, use DISTINCT by `linked_event_index_flag` 
- This avoids double-counting on linked events (e.g., pass > turnover)

---

## Rush Stats (v27.1 - CORRECTED)

**Definition:** `is_rush=1` = controlled zone entry + shot within 7 seconds (NHL definition)

```python
# Rush events ARE zone entries (not shots!)
# The shot/goal info is in time_to_next_sog and next_sog_result columns

# rush_shots = count of rush entries that led to a shot
rush_shots = player_rush_events['time_to_next_sog'].notna().sum()

# rush_goals = count of rush entries where the resulting shot was a goal
rush_goals = (player_rush_events['next_sog_result'].str.lower() == 'goal').sum()

# rush_primary = player was event_player_1 on the rush entry
# rush_support = player was event_player_2-6 on the rush entry
```

**Key insight:** Don't look for event_type='shot' within rush events. Rush events ARE zone entries. The shot info is in the time_to_next_sog and next_sog_result columns.

### Defensive Rush Stats (v27.1 - CORRECTED)

```python
# For is_rush=1, shot ALREADY happened within 7s
# So "prevent shot" is impossible - measure "prevent goal" instead

# Defensive success = no goal allowed (shot saved/missed)
no_goal = (defense_rush_events['next_sog_result'].str.lower() != 'goal')
rush_def_success = no_goal.sum()
rush_def_stop = no_goal.sum()  # Same meaning

# Goals allowed on rushes
rush_def_ga = (defense_rush_events['next_sog_result'].str.lower() == 'goal').sum()
```

---

## Period SOG (v27.1 - ADDED)

```python
# SOG = shots that reached net + goals
# Same logic as main sog column

# Get saved/on-net shots in this period
period_shots = period_primary[event_type == 'shot']
sog = period_shots[event_detail.contains('onnet|saved', regex=True)]

# Add goals (goals are also SOG)
p{N}_sog = len(sog) + p{N}_goals
```

---

## Play Detail Success/Failure Tracking

**Critical: play_detail_successful column values:**
- `s` = Successful (play achieved its purpose)
- `u` = Unsuccessful (play failed)
- blank/NaN = Not tracked/not applicable (DO NOT COUNT as either)

**Example:** A deke event with play_detail_successful='s' means the deke beat the defender. 'u' means the defender stopped it.

**Current micro stats (dekes, drives, etc.) count ALL occurrences regardless of success.**

**Future enhancement:** Break down by success:
- `dekes_successful` = dekes where play_detail_successful='s'
- `dekes_unsuccessful` = dekes where play_detail_successful='u'

---

## Micro Stats Counting (play_detail1, play_detail_2) - v27.1 FIXED

**Current logic (CORRECT):**
```python
def count_distinct(pattern, exclude_pattern=None):
    """
    Count DISTINCT events matching pattern in play_detail1 OR play_detail_2.
    Uses linked_event_index_flag for deduplication if available.
    """
    # Find matches in both columns
    for col in ['play_detail1', 'play_detail_2']:
        mask = player_events[col].str.contains(pattern, regex=True)
        if exclude_pattern:
            mask = mask & ~player_events[col].str.contains(exclude_pattern, regex=True)
        matches = player_events[mask]
    
    # Deduplicate by linked_event_index_flag or event_id
    if 'linked_event_index_flag' in matching_events.columns:
        linked = matching_events[linked_event_index_flag.notna()]
        unlinked = matching_events[linked_event_index_flag.isna()]
        return linked['linked_event_index_flag'].nunique() + unlinked['event_id'].nunique()
    else:
        return matching_events['event_id'].nunique()

# Example usage with defensive exclusion:
'dekes': count_distinct(r'deke', exclude_pattern=r'beatdeke|stoppeddeke')
```

**Key principles:**
1. Uses DISTINCT counting by linked_event_index_flag (or event_id)
2. Excludes defensive variants where appropriate (BeatDeke = opponent beat YOUR deke)
3. Combines both columns but deduplicates to avoid double-counting same event

---

## Expected Goals (xG) Model

### Base Rates by Danger Level
| Zone | xG |
|------|-----|
| High Danger | 0.25 |
| Medium Danger | 0.08 |
| Low Danger | 0.03 |
| Default | 0.06 |

### Modifiers
| Situation | Multiplier |
|-----------|------------|
| Rush | 1.3x |
| Rebound | 1.5x |
| One-timer | 1.4x |
| Breakaway | 2.5x |
| Screened | 1.2x |
| Deflection | 1.3x |

### XY-Based Calculation (when available)
```python
# Distance from goal center (goal at x=89, y=42.5)
dist = sqrt((89 - abs(x))² + (42.5 - y)²)

if dist < 10:     base_xg = 0.35  # Crease
elif dist < 20:   base_xg = 0.15  # Slot
elif dist < 35:   base_xg = 0.06  # High slot
else:             base_xg = 0.02  # Point shot

# Angle adjustment
angle = atan2(42.5 - y, 89 - abs(x))
angle_mod = 1.0 - (angle / π) * 0.5
final_xg = base_xg * angle_mod * modifiers
```

### xG-Derived Statistics
```python
# xg_for = sum of xG for all player's shots
xg_for = sum(shot_xg for each shot where player is event_player_1)

# goals_above_expected = actual goals - expected goals
goals_above_expected = goals_actual - xg_for

# xg_per_shot = average xG per shot (default 0.06 without XY data)
xg_per_shot = xg_for / shots_for_xg

# finishing_skill = ratio of actual goals to expected goals
# > 1.0 = outperforming (efficient/lucky finisher)
# < 1.0 = underperforming
# 0 = no shots or no goals
finishing_skill = goals_actual / xg_for
```

---

## Strength Splits (EV, PP, PK, EN)

### Strength Mapping
```python
strength_map = {
    'ev': ['5v5', '4v4', '3v3'],      # Even strength
    'pp': ['5v4', '5v3', '4v3'],      # Power play
    'pk': ['4v5', '3v5', '3v4'],      # Penalty kill
    'en': ['5v6', '6v5', '4v6', '6v4'] # Empty net
}
```

### Per-Situation Calculations
```python
# TOI by situation
ev_toi_seconds = sum(shift_duration) WHERE strength IN ev_strengths

# Corsi by situation (from shift-level data)
ev_cf = sum(cf) WHERE strength IN ev_strengths
ev_ca = sum(ca) WHERE strength IN ev_strengths
ev_cf_pct = ev_cf / (ev_cf + ev_ca) * 100

# Goals for/against by situation (from shift-level data)
ev_gf = sum(gf) WHERE strength IN ev_strengths
ev_ga = sum(ga) WHERE strength IN ev_strengths

# Individual scoring by situation (from events)
ev_goals = count(goals) WHERE event.strength IN ev_strengths AND player_role='event_player_1'
ev_assists = count(assists) WHERE event.strength IN ev_strengths AND player_role='event_player_1'
ev_points = ev_goals + ev_assists

# TOI percentage
pp_toi_pct = pp_toi_seconds / (ev_toi + pp_toi + pk_toi) * 100
```

### Known Bug (v27.1)
**Shift-level gf_pp/ga_pk incorrectly counting 5v5 goals.** All 16 tracked goals were 5v5, but pp_gf=5 and pk_ga=4. The shift-level calculation is not respecting the goal's actual strength.

---

## Game Score (v27.2 - Fully Transparent)

Game Score is a single-number summary of a player's contribution in a game. It's composed of offensive and defensive components.

### Formula Breakdown

```python
# OFFENSIVE COMPONENTS
gs_scoring = goals * 1.0 + primary_assists * 0.8 + secondary_assists * 0.5
gs_shots = sog * 0.1 + shots_high_danger * 0.15
gs_playmaking = zone_ent_controlled * 0.08 + second_touch * 0.02 + shot_assists * 0.15

# DEFENSIVE COMPONENTS  
gs_defense = takeaways * 0.15 + blocks * 0.08 + poke_checks * 0.05
gs_hustle = backchecks * 0.1 + forechecks * 0.08 + puck_battles_total * 0.03

# NEUTRAL COMPONENTS
gs_faceoffs = (fo_wins - fo_losses) * 0.03  # Only if player took faceoffs
gs_poise = poise_index * 0.2
gs_penalties = giveaways * -0.08

# AGGREGATES
offensive_game_score = gs_scoring + gs_shots + gs_playmaking
defensive_game_score = gs_defense + gs_hustle - (giveaways * 0.08)  # Giveaways hurt defense

game_score_raw = gs_scoring + gs_shots + gs_playmaking + gs_defense + gs_hustle + gs_faceoffs + gs_poise + gs_penalties
game_score = 2.0 + game_score_raw  # Baseline shift for readability
```

### Weights Rationale

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Goal | 1.0 | Most valuable outcome |
| Primary Assist | 0.8 | Direct contribution to goal |
| Secondary Assist | 0.5 | Supporting contribution |
| SOG | 0.1 | Creates scoring chance |
| High Danger Shot | 0.15 | Quality shot attempt |
| Controlled Entry | 0.08 | Creates possession in ozone |
| Takeaway | 0.15 | Creates possession change |
| Block | 0.08 | Prevents shot against |
| Giveaway | -0.08 | Surrenders possession |

---

## Calculated Rating (2-6 Scale)

Maps game_score to a 2-6 rating scale for easy comparison to player's actual rating.

```python
# Thresholds calibrated for rec hockey
if game_score < 2.5:
    calculated_rating = 2.0
elif game_score < 3.5:
    calculated_rating = 2.0 + (game_score - 2.5) / 1.0  # 2-3 range
elif game_score < 5.0:
    calculated_rating = 3.0 + (game_score - 3.5) / 1.5  # 3-4 range
elif game_score < 7.0:
    calculated_rating = 4.0 + (game_score - 5.0) / 2.0  # 4-5 range
else:
    calculated_rating = 5.0 + min((game_score - 7.0) / 3.0, 1.0)  # 5-6 range

# Capped at 2.0 minimum, 6.0 maximum
calculated_rating = max(2.0, min(6.0, calculated_rating))

# rating_differential = calculated_rating - player_actual_rating
# Positive = outperformed, Negative = underperformed
```

### Interpretation Guide

| rating_differential | Meaning |
|---------------------|---------|
| > +1.0 | Significantly outperformed rating |
| +0.5 to +1.0 | Played above their level |
| -0.5 to +0.5 | Played to their rating |
| -1.0 to -0.5 | Played below their level |
| < -1.0 | Significantly underperformed |

---

## Game State Stats (v27.2 - NEW)

Tracks performance when leading, trailing, or tied.

### Calculation Method

```python
# Game state is calculated at the SHIFT level based on running score
# 1. Sort all goals in game by time
# 2. Calculate cumulative home_score, away_score at each goal
# 3. For each shift, find score at shift_start time

def get_game_state_at_shift(shift_start, goals_chronological):
    home_score, away_score = 0, 0
    for goal in goals_chronological:
        if goal.time < shift_start:
            if goal.is_home_goal:
                home_score += 1
            else:
                away_score += 1
    
    diff = home_score - away_score
    if diff > 0: return 'home_leading'
    elif diff < 0: return 'home_trailing'
    else: return 'tied'

# Player perspective mapping
# For HOME player: home_leading = 'leading'
# For AWAY player: home_leading = 'trailing' (their team is behind)
```

### Derived Stats

```python
# TOI by game state
leading_toi = sum(shift_duration) WHERE player_state = 'leading'
trailing_toi = sum(shift_duration) WHERE player_state = 'trailing'
tied_toi = sum(shift_duration) WHERE player_state = 'tied'
close_game_toi = sum(shift_duration) WHERE |score_differential| <= 1

# CF% by game state
leading_cf_pct = sum(cf_leading) / (sum(cf_leading) + sum(ca_leading)) * 100
# etc. for trailing, tied, close_game

# Goals by game state
leading_goals = sum(gf) WHERE player_state = 'leading'
# etc.
```

---

## Rebound Stats (v27.2 - CORRECTED)

### Definition

A **rebound shot** is a shot where the previous event was a Rebound (goalie save that bounced back).

```python
# CORRECT: Use prev_event_type to identify shots following rebounds
rebound_shots = count(shots WHERE prev_event_type = 'Rebound')
rebound_goals = count(goals WHERE prev_event_type = 'Rebound')

# WRONG (old logic): time_since_prev <= 3
# This was counting ALL quick shots, not just shots following rebounds
```

### Related Stats

```python
rebound_recoveries = count(events WHERE is_rebound = 1)  # Who grabbed the rebound
rebound_shot_pct = rebound_goals / rebound_shots * 100
garbage_goals = count(goals WHERE shot location is close-range AND prev_event was scramble/rebound)
```

---

## Strength Split Goals (v27.2 - CORRECTED)

### Bug Fix

Goals were being credited to PP/PK based on SHIFT strength, not GOAL strength.
A goal scored at 5v5 could be credited as a PP goal if the shift started during a power play.

```python
# CORRECT: Use the GOAL's strength, not the shift's strength
for goal in shift_goals:
    goal_strength = goal['strength']  # e.g., '5v5', '5v4'
    
    if goal_strength in ['5v5', '4v4', '3v3']:
        # Credit as EV goal
        gf_ev += 1
    elif goal_strength in ['5v4', '5v3', '4v3']:
        # Credit as PP goal (home perspective if home has more players)
        gf_pp += 1
    elif goal_strength in ['4v5', '3v5', '3v4']:
        # Credit as PK goal
        gf_pk += 1

# WRONG (old logic): Used shift's is_home_pp flag
# This incorrectly credited 5v5 goals as PP/PK
```

---

## WAR/GAR (Wins/Goals Above Replacement)

### GAR Component Weights
```python
GAR_WEIGHTS = {
    # Offensive
    'goals': 1.0,
    'primary_assists': 0.7,
    'secondary_assists': 0.4,
    'shots_generated': 0.015,  # Per SOG
    'xg_generated': 0.8,       # Per xG
    
    # Defensive
    'takeaways': 0.05,
    'blocked_shots': 0.02,
    'defensive_zone_exits': 0.03,
    
    # Possession
    'cf_above_avg': 0.02,      # Per CF event above team avg
    'zone_entry_value': 0.04,  # Per controlled entry
}
```

### Calculations
```python
# Offensive GAR
gar_offense = (goals * 1.0 + 
               primary_assists * 0.7 + 
               secondary_assists * 0.4 + 
               sog * 0.015 + 
               xg_for * 0.8)

# Defensive GAR
gar_defense = (takeaways * 0.05 + 
               blocks * 0.02 + 
               zone_exits_controlled * 0.03)

# Possession GAR
cf_diff = (cf_pct - 50.0) / 100
toi_hours = toi_seconds / 3600
gar_possession = cf_diff * 0.02 * toi_hours * 60

# Transition GAR
gar_transition = zone_entries_controlled * 0.04

# Total
gar_total = gar_offense + gar_defense + gar_possession + gar_transition

# WAR (4.5 goal differential = 1 win in rec hockey)
war = gar_total / 4.5

# Season pace (20 games)
war_pace = war * 20
```

---

## BenchSight Game Score

### Component Formulas
```python
# Scoring (max ~4 points for big game)
gs_scoring = (goals * 1.0 + 
              primary_assists * 0.8 + 
              secondary_assists * 0.5)

# Shots (max ~1.5 points)
gs_shots = (sog * 0.1 + 
            shots_high_danger * 0.15)

# Playmaking (max ~1 point)
gs_playmaking = (zone_entries_controlled * 0.08 + 
                 second_touch * 0.02)

# Defense (max ~1.5 points)
gs_defense = (takeaways * 0.15 + 
              blocks * 0.08 + 
              poke_checks * 0.05 + 
              stick_checks * 0.05)

# Faceoffs
gs_faceoffs = (fo_wins - fo_losses) * 0.03

# Hustle
gs_hustle = (backchecks * 0.1 + 
             forechecks * 0.08 + 
             puck_battles_total * 0.03)

# Penalties
gs_penalties = giveaways * -0.08

# Total
game_score_raw = sum(components)
game_score = 2.0 + game_score_raw  # Baseline of 2.0

# Per-60 normalization
game_score_per_60 = game_score * (3600 / toi_seconds)
```

---

## Performance vs Rating

### Expected Values by Rating
```python
# Points expectation (exponential curve)
# Rating 2 ≈ 0.2 pts/game, Rating 4 ≈ 0.5, Rating 6 ≈ 1.2
expected_points = 0.1 * (1.4 ** (rating - 1))

# Game Score expectation (linear)
expected_game_score = 1.5 + (rating * 0.8)

# Performance Index
performance_index = (actual_game_score / expected_game_score) * 100

# Tiers
if performance_index >= 130:   tier = 'Elite'
elif performance_index >= 110: tier = 'Above Expected'
elif performance_index >= 90:  tier = 'As Expected'
elif performance_index >= 70:  tier = 'Below Expected'
else:                          tier = 'Struggling'

# QoC Adjustment
adj_factor = 1.0 + (qoc_rating - player_rating) * 0.1
adjusted_performance_index = performance_index * adj_factor
```

---

## Per-60 Rates

```python
if toi_seconds > 60:
    multiplier = 3600 / toi_seconds
    
    goals_per_60 = goals * multiplier
    assists_per_60 = assists * multiplier
    points_per_60 = points * multiplier
    sog_per_60 = sog * multiplier
    xg_per_60 = xg_for * multiplier
    # etc.
else:
    # All rates = 0.0 for < 1 minute TOI
```

---

## Relative Stats

```python
# All relative stats are vs 50% baseline (neutral)
cf_pct_rel = cf_pct - 50.0
ff_pct_rel = ff_pct - 50.0

# Goals For Percentage
gf = plus_total  # Goals while on ice
ga = minus_total
gf_pct = (gf / (gf + ga)) * 100 if (gf + ga) > 0 else 50.0
gf_pct_rel = gf_pct - 50.0
```

---

## Goalie Metrics

### Goals Saved Above Average (GSAx)
```python
LEAGUE_AVG_SV_PCT = 88.0  # Rec hockey league average

expected_goals_against = shots_against * (1 - LEAGUE_AVG_SV_PCT / 100)
goals_saved_above_avg = expected_goals_against - goals_against
```

### Quality Start Definition
```python
is_quality_start = (save_pct >= 91.7) or (goals_against <= 2)
is_bad_start = (save_pct < 85.0)
```

---

## Period 3 Clutch Differential

```python
# Points per minute for P1/P2
p1p2_points = p1_points + p2_points
p1p2_toi = p1_toi_seconds + p2_toi_seconds
p1p2_ppm = p1p2_points / (p1p2_toi / 60) if p1p2_toi > 0 else 0

# Points per minute for P3
p3_ppm = p3_points / (p3_toi_seconds / 60) if p3_toi_seconds > 0 else 0

# Clutch differential (positive = performs better in P3)
p3_clutch_diff = p3_ppm - p1p2_ppm
```

---

## Notes on Model Calibration

- **xG Model**: Based on NHL models, adjusted for rec hockey. Will refine with XY coordinate data.
- **GAR Weights**: Initial estimates based on goal impact. Will calibrate with more data.
- **Performance Rating**: Uses registered skill_rating (1-10 scale, 2-6 typical in NORAD).
- **League Average SV%**: 88% is estimate for rec hockey. Track and adjust as needed.

All formulas are implemented in `src/tables/core_facts.py` with named constants for easy adjustment.

---

## v25.2 New Calculations

### Adjusted Rating

Maps game score back to equivalent skill rating to answer: "What rating did this player perform like?"

```python
RATING_GAME_SCORE_MAP = {
    1: 1.0, 2: 2.3, 3: 3.5, 4: 4.7, 5: 5.9,
    6: 7.1, 7: 8.3, 8: 9.5, 9: 10.7, 10: 12.0
}

def calculate_adjusted_rating(game_score):
    # Linear interpolation between rating levels
    for r in range(1, 10):
        low_gs = RATING_GAME_SCORE_MAP[r]
        high_gs = RATING_GAME_SCORE_MAP[r + 1]
        if low_gs <= game_score <= high_gs:
            pct = (game_score - low_gs) / (high_gs - low_gs)
            return r + pct
    
    # Edge cases
    if game_score < 1.0: return 1.0
    if game_score > 12.0: return 10.0

# Example:
# Player rated 4, game_score = 7.1 → adjusted_rating = 6.0
# rating_delta = 6.0 - 4.0 = +2.0 (played 2 ratings above their level)
```

### Goalie WAR

Separate WAR model for goalies based on save quality.

```python
GOALIE_GAR_WEIGHTS = {
    'goals_prevented': 1.0,      # GSAx directly
    'high_danger_saves': 0.15,   # HD saves worth more
    'quality_start_bonus': 0.5,  # Bonus for QS
    'rebound_control': 0.05,     # Freeze vs rebound
}

def calculate_goalie_war(stats):
    # Goals Saved Above Average (main component)
    gsaa = stats['goals_saved_above_avg']
    
    # High danger save bonus
    hd_bonus = stats['hd_saves'] * 0.15
    
    # Quality start bonus
    qs_bonus = 0.5 if stats['is_quality_start'] == 1 else 0
    
    # Rebound control
    freeze_pct = stats['saves_freeze'] / stats['saves']
    rebound_bonus = freeze_pct * 0.05 * stats['saves']
    
    # Total GAR
    gar_total = gsaa * 1.0 + hd_bonus + qs_bonus + rebound_bonus
    
    # WAR (4.5 goal differential = 1 win)
    war = gar_total / 4.5
    war_pace = war * 20  # Season projection

# Example:
# Goalie: 30 saves, 2 GA, 5 HD saves, SV% 93.8% (QS)
# xGA = 30 * 0.12 = 3.6, GSAx = 3.6 - 2 = 1.6
# gar_total = 1.6 + (5 * 0.15) + 0.5 = 2.85
# goalie_war = 2.85 / 4.5 = 0.63
```

### Poise Index

Measures composure under pressure.

```python
def calculate_poise_index(stats):
    pressure_success = stats['pressure_success_pct'] / 100
    pressure_giveaways = stats['pressure_giveaways']
    failure_rate = (100 - stats['pressure_success_pct']) / 100
    
    poise = pressure_success * 2 - pressure_giveaways * 0.1 - failure_rate
    
    # Range: roughly -1 to +2
    # Positive = handles pressure well
    # Negative = struggles under pressure
```

### Playmaking Index

Composite measure of playmaking ability.

```python
def calculate_playmaking_index(stats):
    return (
        stats['shot_assists'] * 1.0 +
        stats['goal_creating_actions'] * 2.0 +
        stats['pre_shot_touches'] * 0.3 +
        stats['sog_sequences'] * 0.5
    )
```

---

## Phase 3 Calculations (v26.1)

### Linemate Analysis

#### unique_linemates
```python
# Count distinct players who shared a shift with this player
teammates_on_shifts = shift_players[
    (shift_players['shift_id'].isin(player_shift_ids)) & 
    (shift_players['player_id'] != player_id) &
    (shift_players['team_id'] == player_team)
]
unique_linemates = teammates_on_shifts['player_id'].nunique()
```

#### top_linemate_player_id, top_linemate_toi_together
```python
# Sum shift_duration by linemate, find max
linemate_toi = {}
for tm in teammates_on_shifts:
    linemate_toi[tm.player_id] += tm.shift_duration
top_linemate = max(linemate_toi.items(), key=lambda x: x[1])
```

#### top_line_cf_pct
```python
# CF% of shifts with top linemate
top_cf = sum(cf for shifts with top_linemate)
top_ca = sum(ca for shifts with top_linemate)
top_line_cf_pct = top_cf / (top_cf + top_ca) * 100
```

#### chemistry_score
```python
# Deviation from neutral (50%)
chemistry_score = top_line_cf_pct - 50.0
```

#### d_partner_player_id, d_partner_toi_together
```python
# For defensemen only - filter to D1/D2 positions
if is_defenseman:
    d_teammates = teammates[position.startswith('D')]
    d_partner = max(d_teammates, key=toi)
```

#### line_consistency_pct
```python
# % of shifts with same top 2 linemates
top_2_linemates = sorted(linemate_toi, reverse=True)[:2]
shifts_with_top_2 = count(shifts where both top_2 present)
line_consistency = shifts_with_top_2 / total_shifts * 100
```

### Time Bucket Analysis

#### Time Bucket Mapping
| Bucket | Period Time | Description |
|--------|-------------|-------------|
| TB01 | 0:00-4:00 | Early period |
| TB02 | 4:00-8:00 | Early period |
| TB03 | 8:00-12:00 | Mid period |
| TB04 | 12:00-16:00 | Late period |
| TB05 | 16:00-20:00 | Late period |

#### early_period_* / late_period_*
```python
# Filter events by time_bucket_id
early_events = events[time_bucket_id in ['TB01', 'TB02']]
late_events = events[time_bucket_id in ['TB04', 'TB05']]

# Count goals, shots from filtered events
early_period_goals = count(player goals in early_events)
late_period_shots = count(player shots in late_events)
```

#### first_goal_involvement
```python
# Check if player participated in first goal of game
first_goal = game_goals.nsmallest(1, 'time_start_total_seconds')
first_goal_involvement = 1 if player in first_goal.participants else 0
```

### Rebound/Second Chance Stats

#### rebound_recoveries
```python
# Count events where is_rebound=1 and player is primary
rebound_recoveries = len(player_events[is_rebound == 1])
```

#### rebound_shots, rebound_goals
```python
# Quick shots within 3 seconds of previous event
quick_shots = player_events[
    (event_type in ['shot', 'goal']) &
    (time_since_prev <= 3)
]
rebound_shots = len(quick_shots)
rebound_goals = len(quick_shots[is_goal_scored])
```

#### rebound_shot_pct
```python
rebound_shot_pct = rebound_goals / rebound_shots * 100
```

#### crash_net_attempts
```python
# Count from play_detail containing 'crashnet'
crash_net = player_events['play_detail1'].str.contains('crashnet').sum()
```

#### garbage_goals
```python
# Goals from scrambles, deflections, tips
garbage = player_goals['event_detail_2'].str.contains(
    'scramble|rebound|deflection|tip'
).sum()
```

---

## Shift Counting (CRITICAL)

### Logical vs Raw Shifts

```
Raw shift rows: Multiple segments of a single shift on ice
Logical shift: One continuous period on ice (player goes over boards once)

RULE: Any gap in shift_index = new logical shift
```

### Calculation

```python
# CORRECT: Use logical_shift_number
shift_count = shift_players.groupby(['game_id', 'player_id'])['logical_shift_number'].nunique()
avg_shift = toi_seconds / shift_count

# WRONG: Using raw rows
shift_count = len(shift_players)  # Overcounts!
```

### Example
```
Player P100001 in game 18969:
- Raw shift rows: 49
- Logical shifts: 13 (this is the correct "shift count")
- TOI: 1730 seconds
- Avg shift: 1730 / 13 = 133 seconds (~2.2 min)
```

---

## v26.2 Rush & Zone Success Calculations

### Rush Success - Offensive (when player on attacking team)

```
rush_off_success = COUNT(event_successful=True OR time_to_next_sog<=10)
rush_off_shot_generated = COUNT(time_to_next_sog <= 10)
rush_off_goal_generated = COUNT(time_to_next_goal <= 15)
```

### Rush Success by Role

**Primary Rusher (event_player_1):**
```
rush_primary_success = COUNT(successful rushes WHERE player_role='event_player_1')
rush_primary_shot = COUNT(shot within 10s WHERE player_role='event_player_1')
rush_primary_goal = COUNT(goal within 15s WHERE player_role='event_player_1')
```

**Support Rusher (event_player_2-6):**
```
rush_support_success = COUNT(successful rushes WHERE player_role LIKE 'event_player_[2-6]')
rush_support_shot = COUNT(shot within 10s WHERE player_role LIKE 'event_player_[2-6]')
rush_support_goal = COUNT(goal within 15s WHERE player_role LIKE 'event_player_[2-6]')
```

### Rush Defense (when player on defending team)

**Combined:**
```
rush_def_success = COUNT(time_to_next_sog > 15 OR time_to_next_sog IS NULL)
rush_def_stop = COUNT(event_successful = False)
rush_def_ga = COUNT(time_to_next_goal <= 15)
```

**Primary Defender (opp_player_1):**
```
rush_primary_def_success = no shot in 15s WHERE player_role='opp_player_1'
rush_primary_def_stop = entry failed WHERE player_role='opp_player_1'
rush_primary_def_ga = goal within 15s WHERE player_role='opp_player_1'
```

**Support Defender (opp_player_2-6):**
```
rush_support_def_success = no shot in 15s WHERE player_role LIKE 'opp_player_[2-6]'
rush_support_def_stop = entry failed WHERE player_role LIKE 'opp_player_[2-6]'
rush_support_def_ga = goal within 15s WHERE player_role LIKE 'opp_player_[2-6]'
```

### Zone Entry/Exit Shot Generation

```
zone_ent_shot_generated = COUNT(zone entries WHERE time_to_next_sog <= 10)
zone_ent_controlled_shot = COUNT(controlled entries WHERE time_to_next_sog <= 10)
zone_ent_uncontrolled_shot = COUNT(uncontrolled entries WHERE time_to_next_sog <= 10)

zone_ent_goal_generated = COUNT(zone entries WHERE time_to_next_goal <= 15)
zone_ent_controlled_goal = COUNT(controlled entries WHERE time_to_next_goal <= 15)
zone_ent_uncontrolled_goal = COUNT(uncontrolled entries WHERE time_to_next_goal <= 15)
```

### Shift Count Calculation (CORRECTED)

```python
# WRONG (old way):
shift_count = COUNT(shift_player rows)  # Overcounts due to multiple rows per shift

# CORRECT (new way):
shift_count = COUNT(DISTINCT logical_shift_number)
# logical_shift_number = shift grouping where any gap in shift_index = new logical shift
avg_shift = toi_seconds / logical_shift_count
```

### Faceoff Win/Loss (CORRECTED)

```python
# WRONG (old way):
fo_win = event_detail contains 'won'

# CORRECT (new way):
fo_win = player_role = 'event_player_1' on faceoff event
fo_loss = player_role = 'opp_player_1' on faceoff event
```

### Assist Tracking (CORRECTED)

```python
# WRONG (old way):
assist = player_role in ['event_player_2', 'event_player_3'] on goal event

# CORRECT (new way):
primary_assist = play_detail1 = 'AssistPrimary' WHERE player_role = 'event_player_1'
secondary_assist = play_detail1 = 'AssistSecondary' WHERE player_role = 'event_player_1'
```

---
