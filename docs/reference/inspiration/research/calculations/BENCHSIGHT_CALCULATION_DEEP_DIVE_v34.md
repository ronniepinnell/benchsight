# BenchSight ETL - Deep Calculation Documentation
## Version 34.00 - Complete Column-Level Lineage

This document provides **deep dive** documentation for every calculated column, showing:
- **Source table(s)** - Where the raw data comes from
- **Filter context** - What filters are applied before calculation
- **Formula** - Exact calculation logic
- **Code location** - Where in the ETL the calculation happens

---

# TABLE OF CONTENTS

1. [SHIFT-LEVEL CALCULATIONS](#1-shift-level-calculations)
2. [H2H & WOWY CALCULATIONS](#2-h2h--wowy-calculations)
3. [EVENT ANALYTICS CALCULATIONS](#3-event-analytics-calculations)
4. [PLAYER GAME STATS CALCULATIONS](#4-player-game-stats-calculations)
5. [WAR/GAR CALCULATIONS](#5-wargar-calculations)
6. [xG MODEL](#6-xg-model)
7. [CORSI/FENWICK](#7-corsifenwick)
8. [GAME SCORE](#8-game-score)

---

# 1. SHIFT-LEVEL CALCULATIONS

**Code Location:** `src/core/base_etl.py:4404-5008` (`enhance_shift_tables()`)

## Source Tables Required
```
fact_shifts       ← Raw shift data from tracking
fact_events       ← Event data for stats during shifts
fact_gameroster   ← Player ID lookups
dim_team          ← Team ID lookups
dim_schedule      ← Season ID lookups
dim_player        ← Player ratings for team rating calc
```

## fact_shifts - Calculated Columns

### Time Calculations
| Column | Formula | Filter Context |
|--------|---------|----------------|
| `shift_start_total_seconds` | `shift_start_min * 60 + shift_start_sec` | None |
| `shift_end_total_seconds` | `shift_end_min * 60 + shift_end_sec` | None |
| `shift_duration` | `shift_start_total_seconds - shift_end_total_seconds` | None (clock counts down) |

### Event Mapping (Which events belong to which shift)
```python
# Filter: Events within shift time window
mask = (
    (events['game_id'] == shift['game_id']) &
    (events['period'] == shift['period']) &
    (events['event_total_seconds'] <= shift['shift_start_total_seconds']) &
    (events['event_total_seconds'] >= shift['shift_end_total_seconds'])
)
```

### Corsi Stats on Shifts
| Column | Formula | Source | Filter |
|--------|---------|--------|--------|
| `cf` | Count of home team corsi events | `fact_events` | `is_corsi == 1 AND is_home_event == 1` within shift time window |
| `ca` | Total corsi events - cf | `fact_events` | `is_corsi == 1` within shift time window |
| `cf_pct` | `(cf / (cf + ca)) * 100` | Derived | 50.0 if no corsi events |

### Fenwick Stats on Shifts
| Column | Formula | Source | Filter |
|--------|---------|--------|--------|
| `ff` | Count of home team fenwick events | `fact_events` | `is_fenwick == 1 AND is_home_event == 1` within shift time window |
| `fa` | Total fenwick events - ff | `fact_events` | `is_fenwick == 1` within shift time window |
| `ff_pct` | `(ff / (ff + fa)) * 100` | Derived | 50.0 if no fenwick events |

### Shot Stats on Shifts
| Column | Formula | Source | Filter |
|--------|---------|--------|--------|
| `sf` | Count of home team SOG | `fact_events` | `is_sog == 1 AND is_home_event == 1` within shift time window |
| `sa` | Total SOG - sf | `fact_events` | `is_sog == 1` within shift time window |
| `shot_diff` | `sf - sa` | Derived | - |

### Scoring Chances on Shifts
| Column | Formula | Source | Filter |
|--------|---------|--------|--------|
| `scf` | Count of home team scoring chances | `fact_events` | `is_scoring_chance == 1 AND is_home_event == 1` |
| `sca` | Total scoring chances - scf | `fact_events` | `is_scoring_chance == 1` |
| `hdf` | Count of home team high danger chances | `fact_events` | `is_high_danger == 1 AND is_home_event == 1` |
| `hda` | Total high danger - hdf | `fact_events` | `is_high_danger == 1` |

### Goal Stats on Shifts (Plus/Minus)
**CRITICAL**: Goals identified ONLY via `event_type='Goal' AND event_detail='Goal_Scored'`

```python
# Code: base_etl.py:4693
actual_goals = events[
    (events['event_type'] == 'Goal') &
    (events['event_detail'] == 'Goal_Scored')
]
```

| Column | Formula | Context |
|--------|---------|---------|
| `home_gf_all` | Count of home team goals | All goals in shift |
| `home_ga_all` | Count of goals against home | All opponent goals in shift |
| `home_gf_ev` | Count of home goals at even strength | Goal's strength in ['5v5', '4v4', '3v3'] |
| `home_gf_pp` | Count of home power play goals | Goal's strength in ['5v4', '5v3', '4v3'] |
| `home_gf_pk` | Count of home penalty kill goals | Goal's strength in ['4v5', '3v5', '3v4'] |
| `home_pm_all` | `home_gf_all - home_ga_all` | All situations |
| `home_pm_ev` | `home_gf_ev - home_ga_ev` | Even strength only |

### Team Ratings on Shifts
**Code:** `base_etl.py:4641-4689`

```python
# Skater position columns (exclude goalies)
home_skater_cols = [
    'home_forward_1_id', 'home_forward_2_id', 'home_forward_3_id',
    'home_defense_1_id', 'home_defense_2_id'
]
```

| Column | Formula | Source |
|--------|---------|--------|
| `home_avg_rating` | Mean of 5 home skater ratings | `dim_player.current_skill_rating` |
| `home_min_rating` | Min of 5 home skater ratings | `dim_player.current_skill_rating` |
| `home_max_rating` | Max of 5 home skater ratings | `dim_player.current_skill_rating` |
| `rating_differential` | `home_avg_rating - away_avg_rating` | Derived |
| `home_rating_advantage` | `rating_differential > 0` | Boolean |

### Game State Tracking
**Code:** `base_etl.py:4787-4840`

| Column | Formula | Source |
|--------|---------|--------|
| `score_differential` | Home score - Away score at shift start | Running tally from goals |
| `game_state` | `'home_leading'` if diff > 0, `'home_trailing'` if diff < 0, `'tied'` if diff == 0 | Derived |
| `is_close_game` | `abs(score_differential) <= 1` | Boolean |

---

# 2. H2H & WOWY CALCULATIONS

**Code Location:** `src/tables/shift_analytics.py:1-600`

## fact_h2h (Head-to-Head Player Stats)

### Source Data Flow
```
fact_shift_players  ← Player-shift records with stats
    ↓ (merge on shift_id)
Get all unique player pairs where both played together
    ↓ (filter by same team)
Group by (player_1_id, player_2_id, game_id, team_id)
    ↓
Aggregate stats
```

### Key Columns - Deep Dive

#### `gf_together` - Goals For When Playing Together
**Source:** `fact_shift_players`
**Filter:**
```python
# Both players on ice at same shift
shifts_together = shift_players.groupby('shift_id')['player_id'].apply(list)
pair_shifts = shifts_together[shifts_together.apply(lambda x: p1 in x and p2 in x)]

# Sum goals for from those shifts
gf_together = shift_players[shift_players['shift_id'].isin(pair_shifts.index)]['gf'].sum()
```
**Context:** Only counts when BOTH players are on ice simultaneously

#### `ga_together` - Goals Against When Playing Together
**Same logic as `gf_together` but using `ga` column**

#### `cf_together` - Corsi For When Playing Together
**Source:** `fact_shift_players.cf`
**Filter:** Same shift filtering as goals
```python
cf_together = pair_shift_data['cf'].sum()
```

#### `toi_together` - Time on Ice Together
```python
toi_together = pair_shift_data['shift_duration'].sum()
# Converted to minutes: toi_together / 60
```

#### `shifts_together` - Count of Shared Shifts
```python
shifts_together = len(pair_shift_data['shift_id'].unique())
```

#### `cf_pct_together` - Corsi % When Together
```python
total_cf = pair_shift_data['cf'].sum()
total_ca = pair_shift_data['ca'].sum()
cf_pct_together = (total_cf / (total_cf + total_ca)) * 100 if (total_cf + total_ca) > 0 else 50.0
```

## fact_wowy (With Or Without You)

### Calculation Logic
```python
# For player P1 and P2:

# WITH: Stats when P1 and P2 are both on ice
stats_with = aggregate_stats(shifts where both P1 and P2 present)

# WITHOUT: Stats when P1 is on ice but P2 is NOT
stats_without = aggregate_stats(shifts where P1 present and P2 absent)

# Impact metrics
cf_pct_with = stats_with['cf_pct']
cf_pct_without = stats_without['cf_pct']
cf_pct_impact = cf_pct_with - cf_pct_without  # Positive = P1 better with P2
```

### Key WOWY Columns

| Column | Formula | Interpretation |
|--------|---------|----------------|
| `cf_pct_with` | Corsi % when both players on ice | Baseline together |
| `cf_pct_without` | Corsi % when player on ice alone | Baseline apart |
| `cf_pct_impact` | `cf_pct_with - cf_pct_without` | Positive = better together |
| `gf_pct_with` | `(gf_with / (gf_with + ga_with)) * 100` | Goal % together |
| `gf_pct_impact` | `gf_pct_with - gf_pct_without` | Goal differential impact |

---

# 3. EVENT ANALYTICS CALCULATIONS

**Code Location:** `src/tables/event_analytics.py`

## fact_scoring_chances

### danger_level Calculation
**Two Methods:**

#### Method 1: XY-Based (when coordinates available)
```python
# Code: event_analytics.py:269-322
def calculate_xg_from_xy(distance, angle, shot_type, is_rush, is_rebound):
    # Distance-based base xG
    if distance < 15:
        base_xg = 0.35  # high danger
    elif distance < 25:
        base_xg = 0.18  # medium danger
    elif distance < 35:
        base_xg = 0.10  # low danger
    else:
        base_xg = 0.05  # perimeter

    # Angle adjustment
    angle_factor = cos(radians(angle * 0.8))
    base_xg *= max(angle_factor, 0.3)

    # Modifiers
    shot_type_mods = {'wrist': 1.0, 'slap': 0.9, 'snap': 1.05, 'backhand': 0.7, 'tip': 1.3}
    rush_mod = 1.15 if is_rush else 1.0
    rebound_mod = 1.25 if is_rebound else 1.0

    return min(base_xg * shot_mod * rush_mod * rebound_mod, 0.95)
```

#### Method 2: Heuristic (when no XY data)
```python
# Code: event_analytics.py:448-461
high_danger_indicators = ['one_time', 'onetimer', 'tip', 'rebound', 'breakaway']
medium_danger_indicators = ['slot', 'screen', 'rush']

if any(ind in event_detail_2 for ind in high_danger_indicators):
    danger_level = 'high'
elif any(ind in event_detail_2 for ind in medium_danger_indicators):
    danger_level = 'medium'
elif zone == 'o':  # offensive zone
    danger_level = 'low'
else:
    danger_level = 'perimeter'
```

## fact_shot_danger

### xg (Expected Goals) Calculation

**Source columns used:**
- `event_detail` - shot outcome
- `event_detail_2` - shot type, rush/rebound flags
- `event_team_zone` - zone indicator
- XY coordinates (if available)

```python
# Base xG rates (no XY data)
XG_BASE_RATES = {
    'high_danger': 0.25,
    'medium_danger': 0.08,
    'low_danger': 0.03,
    'default': 0.06
}

# Modifiers applied multiplicatively
XG_MODIFIERS = {
    'rush': 1.3,
    'rebound': 1.5,
    'one_timer': 1.4,
    'breakaway': 2.5,
    'screened': 1.2,
    'deflection': 1.3
}
```

## fact_rush_events

### Rush Detection Logic
```python
# Code: event_analytics.py:753-797
# Filter: Zone entry followed by shot within 5 events

entry_events = events[events['event_detail'].contains('zone_entry')]

for entry in entry_events:
    next_5_events = events.iloc[entry_pos+1:entry_pos+6]
    shots = next_5_events[next_5_events['event_type'].isin(['shot', 'goal'])]

    if len(shots) > 0:
        rush = {
            'entry_event_id': entry['event_id'],
            'shot_event_id': shots.iloc[0]['event_id'],
            'events_to_shot': count_between,
            'is_rush': True,
            'entry_type': 'carry' if 'carry' in entry_detail else 'dump' if 'dump' in entry_detail else 'other'
        }
```

---

# 4. PLAYER GAME STATS CALCULATIONS

**Code Location:** `src/tables/core_facts.py` and `src/builders/player_stats.py`

## fact_player_game_stats (325+ columns)

### Source Tables
```
fact_event_players  ← Event-player records
fact_shifts         ← Shift data for TOI
fact_shift_players  ← Enhanced shift-player data
fact_gameroster     ← Player-game linkage
dim_schedule        ← Game metadata
```

### Basic Stats

| Column | Formula | Source | Filter |
|--------|---------|--------|--------|
| `goals` | Count of goal events | `fact_event_players` | `is_goal_scored(event)` AND `player_role == 'event_player_1'` |
| `primary_assists` | Count of primary assist events | `fact_event_players` | `play_detail1.lower() == 'assistprimary'` AND `player_role == 'event_player_1'` |
| `secondary_assists` | Count of secondary assist events | `fact_event_players` | `play_detail1.lower() == 'assistsecondary'` AND `player_role == 'event_player_1'` |
| `assists` | `primary_assists + secondary_assists` | Derived | - |
| `points` | `goals + assists` | Derived | - |

### Shot Stats

| Column | Formula | Source | Filter |
|--------|---------|--------|--------|
| `sog` | Count of shots on goal | `fact_event_players` | `is_sog == 1` AND `player_role == 'event_player_1'` |
| `shots_missed` | Count of missed shots | `fact_event_players` | `is_shot == 1` AND `event_detail.contains('miss')` |
| `shots_blocked` | Count of blocked shots | `fact_event_players` | `is_shot == 1` AND `event_detail.contains('blocked')` |
| `shot_attempts` | `sog + shots_missed + shots_blocked` | Derived | - |
| `shooting_pct` | `(goals / sog) * 100` | Derived | 0 if sog == 0 |

### Time on Ice

| Column | Formula | Source | Filter |
|--------|---------|--------|--------|
| `toi_seconds` | Sum of shift durations | `fact_shift_players` | Player's shifts in game |
| `toi_minutes` | `toi_seconds / 60` | Derived | - |
| `toi_ev` | Sum of even strength shift durations | `fact_shift_players` | `strength in ['5v5', '4v4', '3v3']` |
| `toi_pp` | Sum of power play shift durations | `fact_shift_players` | `strength in ['5v4', '5v3', '4v3']` (for home) |
| `toi_pk` | Sum of penalty kill shift durations | `fact_shift_players` | `strength in ['4v5', '3v5', '3v4']` (for home) |

### Corsi/Fenwick Stats (Player Level)

**Venue Mapping Critical**: For away players, cf/ca are SWAPPED from shift-level values

```python
# Code: base_etl.py:5148-5172
# Home players: cf = shift's cf, ca = shift's ca
# Away players: cf = shift's ca, ca = shift's cf (SWAPPED)

cf_orig = sp['cf'].fillna(0)
ca_orig = sp['ca'].fillna(0)

sp['cf'] = np.where(home_mask, cf_orig, ca_orig)  # Away gets shift's ca
sp['ca'] = np.where(home_mask, ca_orig, cf_orig)  # Away gets shift's cf
```

| Column | Formula | Filter |
|--------|---------|--------|
| `cf` | Sum of player's corsi for | Venue-adjusted |
| `ca` | Sum of player's corsi against | Venue-adjusted |
| `cf_pct` | `(cf / (cf + ca)) * 100` | 50.0 default |
| `cf_pct_rel` | `cf_pct - team_cf_pct` | Relative to team |

### Plus/Minus

| Column | Formula | Source | Filter |
|--------|---------|--------|--------|
| `plus_minus` | `gf - ga` | `fact_shift_players` | All situations |
| `plus_minus_ev` | `gf_ev - ga_ev` | `fact_shift_players` | Even strength only |
| `plus_ev` | Count of goals for when on ice | `fact_shift_players` | All situations |
| `minus_ev` | Count of goals against when on ice | `fact_shift_players` | All situations |

---

# 5. WAR/GAR CALCULATIONS

**Code Location:** `src/tables/core_facts.py:2034-2041`

## GAR (Goals Above Replacement) Components

### Weight Constants
```python
GAR_WEIGHTS = {
    'goals': 1.0,
    'primary_assists': 0.7,
    'secondary_assists': 0.4,
    'shots_generated': 0.015,
    'xg_generated': 0.8,
    'takeaways': 0.05,
    'blocked_shots': 0.02,
    'defensive_zone_exits': 0.03,
    'cf_above_avg': 0.02,
    'zone_entry_value': 0.04,
    'shot_assists': 0.3,
    'pressure_success': 0.02,
}

GOALS_PER_WIN = 4.5
GAMES_PER_SEASON = 20
```

### Calculation Formula
```python
def calculate_war_stats(stats):
    # Offensive GAR
    off_gar = (
        stats['goals'] * 1.0 +
        stats['primary_assists'] * 0.7 +
        stats['secondary_assists'] * 0.4 +
        stats['sog'] * 0.015 +
        stats['xg_for'] * 0.8 +
        stats['shot_assists'] * 0.3
    )

    # Defensive GAR
    def_gar = (
        stats['takeaways'] * 0.05 +
        stats['blocks'] * 0.02 +
        stats['zone_ext_controlled'] * 0.03
    )

    # Possession GAR (based on Corsi above 50%)
    poss_gar = (
        (stats['cf_pct'] - 50.0) / 100 * 0.02 *
        stats['toi_seconds'] / 3600 * 60
    )

    # Transition GAR
    trans_gar = stats['zone_ent_controlled'] * 0.04

    # Poise GAR (new)
    poise_gar = stats['pressure_success_count'] * 0.02

    # Total
    total_gar = off_gar + def_gar + poss_gar + trans_gar + poise_gar

    return {
        'gar_offense': off_gar,
        'gar_defense': def_gar,
        'gar_possession': poss_gar,
        'gar_transition': trans_gar,
        'gar_poise': poise_gar,
        'gar_total': total_gar,
        'war': total_gar / 4.5,  # Convert to wins
        'war_pace': total_gar / 4.5 * 20,  # Projected over 20 games
    }
```

### Goalie WAR
```python
GOALIE_GAR_WEIGHTS = {
    'saves_above_avg': 0.1,
    'high_danger_saves': 0.15,
    'goals_prevented': 1.0,  # GSAx
    'rebound_control': 0.05,
    'quality_start_bonus': 0.5,
}

def calculate_goalie_war(stats):
    gsaa = stats['goals_saved_above_avg']
    hd_bonus = stats['hd_saves'] * 0.15
    qs_bonus = 0.5 if stats['is_quality_start'] else 0
    rebound_control = (stats['saves_freeze'] / stats['saves']) * 0.05 * stats['saves']

    gar_total = gsaa * 1.0 + hd_bonus + qs_bonus + rebound_control

    return {
        'goalie_gar_total': gar_total,
        'goalie_war': gar_total / 4.5,
    }
```

---

# 6. xG MODEL

**Code Location:** `src/tables/core_facts.py:56-58` and `src/tables/event_analytics.py:269-322`

## Base Rates (No XY Data)
```python
XG_BASE_RATES = {
    'high_danger': 0.25,    # Slot, rebound, one-timer
    'medium_danger': 0.08,  # Top of circles
    'low_danger': 0.03,     # Point shots
    'default': 0.06         # Unknown
}
```

## Situation Modifiers
```python
XG_MODIFIERS = {
    'rush': 1.3,        # Odd-man rush
    'rebound': 1.5,     # Second chance
    'one_timer': 1.4,   # One-time shot
    'breakaway': 2.5,   # Penalty shot type
    'screened': 1.2,    # Traffic in front
    'deflection': 1.3,  # Tip/deflection
}
```

## Shot Type Modifiers
```python
SHOT_TYPE_XG_MODIFIERS = {
    'wrist': 1.0,       # Baseline
    'slap': 0.95,       # Less accurate
    'snap': 1.05,       # Quick release
    'backhand': 0.9,    # Difficult
    'tip': 1.15,        # Redirect
    'deflection': 1.1,  # Redirect
}
```

## XY-Based xG Formula
```python
def calculate_xg_from_xy(distance, angle, shot_type, is_rush, is_rebound):
    # Distance-based base (feet from net)
    if distance < 15:
        base_xg = 0.35
    elif distance < 25:
        base_xg = 0.18
    elif distance < 35:
        base_xg = 0.10
    else:
        base_xg = 0.05

    # Angle adjustment (wider angle = lower xG)
    if angle > 0:
        angle_factor = cos(radians(angle * 0.8))
        base_xg *= max(angle_factor, 0.3)

    # Apply all modifiers
    xg = base_xg * shot_type_mod * rush_mod * rebound_mod

    return min(xg, 0.95)  # Cap at 95%
```

---

# 7. CORSI/FENWICK

**Code Location:** `src/calculations/corsi.py`

## Definitions

### Corsi Events
```python
# All shot attempts (shots on goal + missed + blocked)
is_corsi = (
    (event_type == 'Shot') |
    (event_type == 'Goal') |
    (event_detail.contains('Miss')) |
    (event_detail.contains('Blocked'))
)
```

### Fenwick Events
```python
# Unblocked shot attempts (shots on goal + missed only)
is_fenwick = (
    (event_type == 'Shot') |
    (event_type == 'Goal') |
    (event_detail.contains('Miss'))
) & ~(event_detail.contains('Blocked'))
```

## Player-Level Calculations
```python
# For player P during game G:

# Step 1: Find all shifts where P was on ice
player_shifts = shift_players[shift_players['player_id'] == P]

# Step 2: For each shift, get cf/ca (venue-adjusted)
# Home player: cf = home team's corsi, ca = away team's corsi
# Away player: cf = away team's corsi (shift's ca), ca = home team's corsi (shift's cf)

cf = player_shifts['cf'].sum()
ca = player_shifts['ca'].sum()
cf_pct = (cf / (cf + ca)) * 100 if (cf + ca) > 0 else 50.0
```

## Relative Corsi
```python
# cf_pct_rel = Player's CF% - Team's CF% (without player)
cf_pct_rel = player_cf_pct - team_cf_pct_without_player
```

---

# 8. GAME SCORE

**Code Location:** `src/tables/core_facts.py:2043-2150`

## Component Formulas

### Offensive Components
```python
gs_scoring = goals * 1.0 + primary_assists * 0.8 + secondary_assists * 0.5
gs_shots = sog * 0.1 + shots_high_danger * 0.15
gs_playmaking = zone_ent_controlled * 0.08 + second_touch * 0.02 + shot_assists * 0.15
```

### Defensive Components
```python
gs_defense = takeaways * 0.15 + blocks * 0.08 + poke_checks * 0.05
gs_hustle = backchecks * 0.1 + forechecks * 0.08 + puck_battles_total * 0.03
```

### Neutral Components
```python
gs_faceoffs = (fo_wins - fo_losses) * 0.03
gs_poise = poise_index * 0.2
gs_penalties = giveaways * -0.08
```

### Final Aggregation
```python
offensive_game_score = gs_scoring + gs_shots + gs_playmaking
defensive_game_score = gs_defense + gs_hustle - (giveaways * 0.08)

game_score_raw = (
    gs_scoring + gs_shots + gs_playmaking +
    gs_defense + gs_hustle +
    gs_faceoffs + gs_poise + gs_penalties
)

game_score = 2.0 + game_score_raw  # Baseline shift for 2-10 scale
```

### Calculated Rating (2-6 scale)
```python
if game_score < 2.5:
    calculated_rating = 2
elif game_score < 4.0:
    calculated_rating = 3
elif game_score < 6.0:
    calculated_rating = 4
elif game_score < 8.0:
    calculated_rating = 5
else:
    calculated_rating = 6
```

---

# APPENDIX: Quick Reference - Column Source Map

| Table | Column | Primary Source | Filter/Context |
|-------|--------|----------------|----------------|
| fact_h2h | gf_together | fact_shift_players.gf | Both players on same shift |
| fact_h2h | cf_together | fact_shift_players.cf | Both players on same shift |
| fact_h2h | toi_together | fact_shift_players.shift_duration | Both players on same shift |
| fact_shifts | cf | fact_events | is_corsi=1, in shift time window |
| fact_shifts | home_gf_all | fact_events | is_goal=1, in shift time window |
| fact_shift_players | cf | fact_shifts.cf/ca | SWAPPED for away players |
| fact_shift_players | gf | fact_shifts.home_gf/away_gf | MAPPED by venue |
| fact_player_game_stats | goals | fact_event_players | player_role='event_player_1', is_goal_scored |
| fact_player_game_stats | cf_pct | fact_shift_players | Aggregated across all player shifts |
| fact_player_game_stats | war | Derived | gar_total / 4.5 |
| fact_scoring_chances | xg | XY coords or heuristic | Distance/angle model or event flags |

---

*Generated: 2026-01-18 | BenchSight ETL v34.00*
