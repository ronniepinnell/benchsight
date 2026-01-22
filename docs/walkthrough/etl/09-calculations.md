# 09 - Calculations Reference: All Formulas Explained

**Learning Objectives:**
- Understand every major calculation formula
- Know the inputs and outputs for each metric
- Reproduce calculations manually if needed

---

## Basic Counting Stats

### Goals

🔑 **CRITICAL RULE:**
```python
Goals = COUNT(*)
WHERE event_type = 'Goal'
  AND event_detail = 'Goal_Scored'
  AND event_player_1 = player_id
```

**Common Mistake:**
```python
# WRONG - Shot_Goal is a shot, not a goal!
goals = df[df['event_detail'] == 'Shot_Goal']
```

### Assists

```python
primary_assists = COUNT(*)
WHERE play_detail = 'AssistPrimary'
  AND event_player_1 = player_id

secondary_assists = COUNT(*)
WHERE play_detail = 'AssistSecondary'
  AND event_player_1 = player_id

assists = primary_assists + secondary_assists
```

### Points

```python
points = goals + assists
```

### Shots

```python
shots = COUNT(*)
WHERE event_type = 'Shot'
  AND event_player_1 = player_id

sog = COUNT(*)  # Shots on Goal
WHERE is_shot_on_goal = true
  AND event_player_1 = player_id
# Note: Goals are included in SOG
```

### Shooting Percentage

```python
shooting_pct = (goals / sog) * 100
# Only calculate when sog > 0, else 0.00
```

---

## Time on Ice (TOI)

### Total TOI

```python
toi_seconds = SUM(shift_duration)
WHERE player_id = player_id
  AND game_id = game_id

toi_minutes = toi_seconds / 60
toi_hours = toi_seconds / 3600
```

### Shift Count

```python
shift_count = COUNT(DISTINCT logical_shift_number)
# Use logical_shift_number to handle overlapping shifts
```

### Average Shift Length

```python
avg_shift = toi_seconds / shift_count
```

### TOI by Strength

```python
toi_5v5 = SUM(shift_duration) WHERE strength = '5v5'
toi_pp = SUM(shift_duration) WHERE strength LIKE '%PP%'
toi_pk = SUM(shift_duration) WHERE strength LIKE '%PK%'
toi_en = SUM(shift_duration) WHERE strength LIKE '%EN%'
```

---

## Rate Stats (Per 60 Minutes)

All rate stats follow this pattern:

```python
stat_per_60 = stat / toi_hours * 60

# Examples:
goals_per_60 = goals / (toi_seconds / 3600) * 60
assists_per_60 = assists / (toi_seconds / 3600) * 60
points_per_60 = points / (toi_seconds / 3600) * 60
shots_per_60 = shots / (toi_seconds / 3600) * 60
```

**Why per-60?**
- Normalizes for ice time differences
- Player A: 2 goals in 20 min = 6.0 goals/60
- Player B: 2 goals in 10 min = 12.0 goals/60
- Player B had better rate production

**Caution:** Rate stats can be misleading with low TOI
- 1 goal in 1 minute = 60.0 goals/60 (unrealistic!)
- Filter for minimum TOI (e.g., toi_seconds >= 300)

---

## Corsi and Fenwick

### What They Measure

**Corsi** = Shot attempt differential (all shot attempts)
**Fenwick** = Shot attempt differential (unblocked only)

### Corsi Calculation

```python
# Corsi Events = SOG + Missed + Blocked
is_corsi_event = (
    (event_type == 'Shot' AND event_detail IN ('Shot_OnNetSaved', 'Shot_OnNet', 'Shot_Goal'))
    OR event_detail LIKE '%Blocked%'
    OR event_detail IN ('Shot_Missed', 'Shot_MissedPost')
)

# Corsi For = Shot attempts BY player's team
corsi_for = COUNT(*)
WHERE is_corsi_event = true
  AND team_id = player_team_id
  AND player_on_ice = true  # During player's shifts

# Corsi Against = Shot attempts BY opponent team
corsi_against = COUNT(*)
WHERE is_corsi_event = true
  AND team_id = opponent_team_id
  AND player_on_ice = true

# Corsi For Percentage
cf_pct = (corsi_for / (corsi_for + corsi_against)) * 100
```

### Fenwick Calculation

```python
# Fenwick Events = SOG + Missed (excludes blocked)
is_fenwick_event = (
    (event_type == 'Shot' AND event_detail IN ('Shot_OnNetSaved', 'Shot_OnNet', 'Shot_Goal'))
    OR event_detail IN ('Shot_Missed', 'Shot_MissedPost')
)

fenwick_for = COUNT(*)
WHERE is_fenwick_event = true
  AND team_id = player_team_id
  AND player_on_ice = true

fenwick_against = COUNT(*)
WHERE is_fenwick_event = true
  AND team_id = opponent_team_id
  AND player_on_ice = true

ff_pct = (fenwick_for / (fenwick_for + fenwick_against)) * 100
```

### Interpretation

- **CF% > 50%**: Team is outshot-attempting opponents when this player is on ice (good)
- **CF% < 50%**: Team is being outshot-attempted (bad)
- **CF% = 50%**: Even shot attempts

---

## Expected Goals (xG)

### What xG Measures

**xG** = Probability that a shot becomes a goal, based on shot quality factors.

A shot from the crease has higher xG than a shot from the blue line.

### xG Formula

```python
shot_xg = base_rate × rush_modifier × shot_type_modifier × flurry_adjustment
shot_xg = min(shot_xg, 0.95)  # Cap at 95%
```

### Base Rates (by Danger Level)

| Danger Level | Base Rate | Description |
|--------------|-----------|-------------|
| High Danger | 0.25 | Slot, crease area |
| Medium Danger | 0.08 | Mid-slot, circles |
| Low Danger | 0.03 | Perimeter, point |
| Default | 0.06 | Unknown location |

**Danger zones determined by XY coordinates:**
```python
if x_coord >= 180 and 30 <= y_coord <= 55:
    danger = 'high'      # Crease/slot
elif x_coord >= 160 and 20 <= y_coord <= 65:
    danger = 'medium'    # Mid-range
else:
    danger = 'low'       # Perimeter
```

### Rush Modifiers

| Situation | Modifier | Why |
|-----------|----------|-----|
| Rush | 1.3x | Goalie out of position |
| Rebound | 1.5x | Goalie recovering |
| One-timer | 1.4x | No time to set |
| Breakaway | 2.5x | 1-on-0 |
| Screened | 1.2x | Goalie can't see |
| Deflection | 1.3x | Unpredictable |

### Shot Type Modifiers

| Shot Type | Modifier | Why |
|-----------|----------|-----|
| Wrist | 1.0x | Baseline |
| Slap | 0.95x | Less accurate |
| Snap | 1.05x | Quick release |
| Backhand | 0.9x | Harder to control |
| Tip | 1.15x | Redirects are effective |
| Deflection | 1.1x | Unpredictable |

### Flurry Adjustment

**Problem:** Multiple quick shots shouldn't each get full xG
**Solution:** Group shots within 3 seconds and calculate combined probability

```python
# Group shots into sequences (within 3 seconds of each other)
for shot in sorted_shots_by_time:
    if time_since_last_shot <= 3.0:
        add_to_current_sequence(shot)
    else:
        start_new_sequence(shot)

# Calculate adjusted xG per sequence
for sequence in sequences:
    if len(sequence) == 1:
        xg_adjusted += sequence[0].xg_value  # No adjustment
    else:
        # Multi-shot: P(at least one goal) = 1 - P(all miss)
        prob_all_miss = 1.0
        for xg in sequence:
            prob_all_miss *= (1.0 - xg)
        xg_flurry = 1.0 - prob_all_miss
        xg_adjusted += min(xg_flurry, 0.99)  # Cap at 0.99
```

### xG Metrics

```python
xg_for = SUM(shot_xg)
WHERE event_player_1 = player_id

xg_against = SUM(shot_xg)
WHERE team_id = opponent_team_id
  AND player_on_ice = true

goals_above_xg = goals - xg_for
# Positive = finishing above expectation (skill or luck)
# Negative = finishing below expectation

xg_per_shot = xg_for / shots
# Average shot quality
```

---

## WAR/GAR (Wins/Goals Above Replacement)

### What It Measures

**GAR** = Goals Above Replacement - How many goals a player contributes above a replacement-level player

**WAR** = Wins Above Replacement - GAR converted to wins

### GAR Components

#### Offense GAR
```python
gar_offense = (
    goals × 1.0
    + primary_assists × 0.7
    + secondary_assists × 0.4
    + sog × 0.015
    + xg_for × 0.8
    + shot_assists × 0.3
)
```

#### Defense GAR
```python
gar_defense = (
    takeaways × 0.05
    + blocks × 0.02
    + zone_exit_controlled × 0.03
)
```

#### Possession GAR
```python
gar_possession = (cf_pct - 50) / 100 × 0.02 × toi_hours × 60
# Above-average possession drives value
```

#### Transition GAR
```python
gar_transition = zone_entry_controlled × 0.04
```

#### Poise GAR
```python
gar_poise = pressure_success_count × 0.02
```

### Total GAR and WAR

```python
gar_total = gar_offense + gar_defense + gar_possession + gar_transition + gar_poise

war = gar_total / 4.5
# 4.5 goals per win in rec hockey (20-game season)
```

### GAR Weight Table

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Goals | 1.0 | Direct scoring |
| Primary Assists | 0.7 | Key setup |
| Secondary Assists | 0.4 | Contributing role |
| SOG | 0.015 | Shot generation |
| xG | 0.8 | Quality chances |
| Takeaways | 0.05 | Turnovers created |
| Blocks | 0.02 | Defensive plays |
| Zone Exits | 0.03 | Breakout value |
| Zone Entries | 0.04 | Attack creation |
| Shot Assists | 0.3 | Playmaking |
| Pressure Success | 0.02 | Under-pressure plays |

---

## Game Score

### What It Measures

**Game Score** = Single-number performance rating for a game

### Components

```python
gs_scoring = goals × 1.0 + primary_assists × 0.8 + secondary_assists × 0.5

gs_shots = sog × 0.1 + high_danger_shots × 0.15

gs_playmaking = controlled_entries × 0.08 + second_touch × 0.02

gs_defense = takeaways × 0.15 + blocks × 0.08 + poke_checks × 0.05

gs_hustle = (fo_wins - fo_losses) × 0.03

game_score_raw = gs_scoring + gs_shots + gs_playmaking + gs_defense + gs_hustle

game_score = 2.0 + game_score_raw  # Baseline shift for 2-10 scale
```

### Game Score Interpretation

| Score | Rating |
|-------|--------|
| 8+ | Elite game |
| 6-8 | Above average |
| 4-6 | Average |
| 2-4 | Below average |
| <2 | Poor game |

### Game Score per 60

```python
game_score_per_60 = game_score × 3600 / toi_seconds
```

---

## Quality of Competition/Teammates

### Quality of Competition (QoC)

```python
# Average rating of opponents faced
qoc = AVG(opponent_rating)
WHERE player_on_ice = true
  AND opponent_on_ice = true
```

High QoC = Facing tough opponents
Low QoC = Facing weaker opponents

### Quality of Teammates (QoT)

```python
# Average rating of linemates
qot = AVG(teammate_rating)
WHERE player_on_ice = true
  AND teammate_on_ice = true
```

High QoT = Playing with good linemates
Low QoT = Playing with weaker linemates

### Competition Tier Analysis

| Tier | Rating Range |
|------|--------------|
| Elite | 5.0 - 6.0 |
| Above Average | 4.0 - 4.99 |
| Average | 3.0 - 3.99 |
| Below Average | 2.0 - 2.99 |

---

## Goalie Stats

### Save Percentage

```python
saves = COUNT(*) WHERE event_detail = 'Shot_OnNetSaved'
goals_against = COUNT(*) WHERE is_goal = true AND goalie_on_ice = true
shots_against = saves + goals_against

save_pct = saves / shots_against × 100
```

### Goals Saved Above Average (GSAx)

```python
# Expected goals against based on xG
xga = SUM(shot_xg) WHERE opponent shot AND goalie_on_ice

# Actual goals against
ga = goals_against

# Goals saved above average
gsax = xga - ga
# Positive = goalie saving more than expected
```

### Quality Start

```python
quality_start = 1 IF save_pct >= 0.917 ELSE 0
# Old school: 91.7% is league average
```

---

## Summary Table

| Metric | Formula | Purpose |
|--------|---------|---------|
| Goals | COUNT WHERE event_type='Goal' AND event_detail='Goal_Scored' | Scoring |
| Corsi | (CF - CA) / (CF + CA) | Possession proxy |
| Fenwick | Same as Corsi but no blocked shots | Unblocked possession |
| xG | Shot probability × modifiers | Shot quality |
| GAR | Sum of component values | Total contribution |
| WAR | GAR / 4.5 | Wins added |
| Game Score | Weighted event sum | Single-game rating |

---

## Key Takeaways

1. **Goal filter is CRITICAL:** `event_type='Goal' AND event_detail='Goal_Scored'`
2. **Rate stats normalize for ice time** (per 60 minutes)
3. **Corsi/Fenwick measure shot attempt share**
4. **xG considers shot location, type, and situation**
5. **WAR/GAR converts everything to goal/win value**
6. **Game Score is a single-number game rating**

---

**Next:** [10-dashboard.md](10-dashboard.md) - Understanding the Next.js dashboard
