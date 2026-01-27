# BenchSight Calculation Catalog

> **Purpose:** Comprehensive documentation of all calculations and formulas implemented in BenchSight with mathematical notation, code references, and validation criteria.

**Version:** 1.0
**Last Updated:** 2026-01-21
**Owner:** Analytics Team

---

## Table of Contents

1. [Scoring Metrics](#1-scoring-metrics)
2. [Shot & Possession Metrics](#2-shot--possession-metrics)
3. [Expected Goals (xG)](#3-expected-goals-xg)
4. [Player Value Metrics (WAR/GAR)](#4-player-value-metrics-wargar)
5. [Transition Metrics](#5-transition-metrics)
6. [Defensive Metrics](#6-defensive-metrics)
7. [Goalie Metrics](#7-goalie-metrics)
8. [Game Score & Ratings](#8-game-score--ratings)
9. [Micro-Statistics](#9-micro-statistics)
10. [Aggregation & Per-60 Metrics](#10-aggregation--per-60-metrics)

---

## Calculation Template Reference

Each calculation follows this standard format:
- **Category:** Grouping (Scoring, Possession, etc.)
- **Status:** Implemented | Partial | Gap
- **Code Location:** File path and line numbers
- **Formula:** Mathematical notation
- **Variables:** Input definitions with sources
- **Filter Context:** Required conditions
- **Validation:** Expected ranges and QA tables

---

## 1. Scoring Metrics

### 1.1 Goals (CRITICAL - Single Source of Truth)

**Category:** Scoring
**Status:** IMPLEMENTED
**Code Location:** `src/calculations/goals.py:21-37`

**Formula:**
```
Goals = COUNT(events WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored')
```

**CRITICAL FILTER:** Both conditions must be true:
```python
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
```

**WARNING:** Never count:
- `event_type == 'Shot'` with `event_detail == 'Goal'` (this is a shot attempt)
- `event_detail == 'Shot_Goal'` (this is the shot event, not the goal event)

**Variables:**
| Variable | Description | Source |
|----------|-------------|--------|
| event_type | Event classification | fact_events.event_type |
| event_detail | Event subtype | fact_events.event_detail |
| event_player_1 | Scorer (primary actor) | fact_events.event_player_1 |

**Validation:**
- Must match `fact_gameroster` official goal count
- QA table: `qa_goal_accuracy`
- Range: 0-10 per game (typical: 0-5)

---

### 1.2 Assists

**Category:** Scoring
**Status:** IMPLEMENTED
**Code Location:** `src/tables/core_facts.py`

**Formula:**
```
Primary_Assists (A1) = COUNT(events WHERE player = event_player_2 AND event_type = 'Goal')
Secondary_Assists (A2) = COUNT(events WHERE player = event_player_3 AND event_type = 'Goal')
Total_Assists = A1 + A2
```

**Variables:**
| Variable | Description | Source |
|----------|-------------|--------|
| event_player_2 | Primary assist | fact_events.event_player_2 |
| event_player_3 | Secondary assist | fact_events.event_player_3 |

**Validation:**
- A1 + A2 should equal official assist totals
- Range: 0-3 per goal (max 2 assists per goal)

---

### 1.3 Points

**Category:** Scoring
**Status:** IMPLEMENTED
**Code Location:** `src/tables/core_facts.py`

**Formula:**
```
Points = Goals + Assists
Points = Goals + A1 + A2
```

**Validation:**
- Range: 0-15 per game (typical: 0-4)

---

### 1.4 Shooting Percentage

**Category:** Scoring
**Status:** IMPLEMENTED
**Code Location:** `config/formulas.json`

**Formula:**
```
Shooting_Pct = (Goals / SOG) * 100

Where SOG > 0, else Shooting_Pct = 0
```

**Variables:**
| Variable | Description | Source |
|----------|-------------|--------|
| Goals | Goals scored | Calculated (1.1) |
| SOG | Shots on goal | fact_player_game_stats.sog |

**Validation:**
- Range: 0-100%
- League average: ~8-12%
- Outliers: >25% (small sample) or <3% (unlucky/poor shooter)

---

## 2. Shot & Possession Metrics

### 2.1 Shots on Goal (SOG)

**Category:** Possession
**Status:** IMPLEMENTED
**Code Location:** `src/tables/core_facts.py`

**Formula:**
```
SOG = COUNT(shots WHERE outcome IN ('Goal', 'Save'))
```

**Filter:**
```python
SOG_FILTER = (df['event_type'] == 'Shot') & (df['shot_outcome'].isin(['Goal', 'Save']))
```

**Excludes:** Blocked shots, missed shots (wide/high)

---

### 2.2 Corsi (CF/CA/CF%)

**Category:** Possession
**Status:** IMPLEMENTED
**Code Location:** `src/calculations/corsi.py`

**Definition:** All shot attempts (shots on goal + blocked + missed)

**Formula:**
```
CF (Corsi For) = SOG + Blocked + Missed
CA (Corsi Against) = Opponent_CF
CF% = CF / (CF + CA) * 100
```

**Variables:**
| Variable | Description | Source |
|----------|-------------|--------|
| SOG | Shots on goal | fact_player_game_stats.sog |
| Blocked | Shots blocked by opponent | fact_events WHERE shot_outcome = 'Blocked' |
| Missed | Shots missed (wide/high) | fact_events WHERE shot_outcome = 'Missed' |

**Interpretation:**
- CF% > 50%: Team controlling play
- CF% < 50%: Being outplayed
- League average: 50%

**Validation:**
- CF% range: 0-100%
- Typical range: 40-60%

---

### 2.3 Fenwick (FF/FA/FF%)

**Category:** Possession
**Status:** IMPLEMENTED
**Code Location:** `src/calculations/corsi.py`

**Definition:** Unblocked shot attempts (shots on goal + missed, excludes blocked)

**Formula:**
```
FF (Fenwick For) = SOG + Missed
FA (Fenwick Against) = Opponent_FF
FF% = FF / (FF + FA) * 100
```

**Rationale:** Excludes blocked shots which can be influenced by shot-blocking strategy rather than possession.

**Validation:**
- FF% range: 0-100%
- Typically correlates closely with CF%

---

### 2.4 Time on Ice (TOI)

**Category:** Possession
**Status:** IMPLEMENTED
**Code Location:** `src/calculations/time.py`

**Formula:**
```
TOI_seconds = SUM(shift_end - shift_start) for all shifts
TOI_minutes = TOI_seconds / 60
```

**Variables:**
| Variable | Description | Source |
|----------|-------------|--------|
| shift_start | Shift start time (seconds) | fact_shifts.start_time |
| shift_end | Shift end time (seconds) | fact_shifts.end_time |

**Validation:**
- Range: 0-1800 seconds per game (0-30 minutes)
- Typical forward: 600-900s (10-15 min)
- Typical defenseman: 900-1200s (15-20 min)

---

## 3. Expected Goals (xG)

### 3.1 Base xG Model (Lookup-Based)

**Category:** Scoring
**Status:** IMPLEMENTED (Partial)
**Code Location:** `src/tables/core_facts.py:56-58`

**Formula:**
```
xG = base_rate * PRODUCT(modifiers)
```

**Base Rates by Danger Zone:**
| Danger Level | Base Rate | Description |
|--------------|-----------|-------------|
| High | 0.25 | Slot area (0-12ft, <45 deg) |
| Medium | 0.08 | Mid-range (12-30ft, <60 deg) |
| Low | 0.03 | Perimeter (30ft+ or >60 deg) |
| Default | 0.06 | Unknown location |

**Modifiers:**
| Modifier | Value | Condition |
|----------|-------|-----------|
| Rush | 1.3 | is_rush == True |
| Rebound | 1.5 | is_rebound == True |
| One-Timer | 1.4 | 'one_timer' in event_detail_2 |
| Breakaway | 2.5 | 'breakaway' in event_detail_2 |
| Screened | 1.2 | 'screened' in event_detail_2 |
| Deflection | 1.3 | 'deflection' in event_detail_2 |

**Shot Type Modifiers:**
| Shot Type | Value |
|-----------|-------|
| Wrist | 1.0 |
| Slap | 0.95 |
| Snap | 1.05 |
| Backhand | 0.9 |
| Tip | 1.15 |

**Example Calculation:**
```
High-danger rebound wrist shot on rush:
xG = 0.25 * 1.3 * 1.5 * 1.0 = 0.4875
```

**Validation:**
- xG range: 0.01-0.95
- Sum per game: typically 2-5 xG per team

---

### 3.2 XY-Based xG Model

**Category:** Scoring
**Status:** IMPLEMENTED (Partial)
**Code Location:** `src/tables/event_analytics.py:303-356`

**Formula:**
```
distance = sqrt((x - goal_x)^2 + (y - goal_y)^2)
angle = atan2(abs(y), abs(x - goal_x)) * (180 / pi)

xG = f(distance, angle, shot_type, modifiers)
```

**Distance Decay:**
```
xG_distance_factor = max(0.01, 0.35 - (distance * 0.008))
```

**Angle Adjustment:**
```
xG_angle_factor = cos(angle * pi / 180)  # Reduces xG for sharp angles
```

**Gap vs Industry:**
- Missing: GBM/XGBoost model
- Missing: Royal road feature
- Missing: Flurry probability adjustment

---

### 3.3 Flurry-Adjusted xG (GAP)

**Category:** Scoring
**Status:** NOT IMPLEMENTED
**Code Location:** N/A (documented in CLAUDE.md)

**Formula:**
```
Standard (naive):
xG_total = xG_1 + xG_2 + xG_3 + ...

Flurry-adjusted:
xG_total = 1 - PRODUCT(1 - xG_i) for all shots in flurry
         = 1 - [(1 - xG_1) * (1 - xG_2) * (1 - xG_3) * ...]
```

**Example:**
- 3 shots with xG = [0.10, 0.15, 0.08]
- Naive: 0.10 + 0.15 + 0.08 = 0.33
- Adjusted: 1 - (0.90 * 0.85 * 0.92) = 1 - 0.704 = 0.296

**Flurry Detection:**
```python
if (shot_time - prev_shot_time) <= 3.0 and same_possession:
    is_flurry = True
```

**Priority:** P0 - Critical Gap

---

### 3.4 Goals Above Expected (GAE)

**Category:** Scoring
**Status:** IMPLEMENTED
**Code Location:** `src/tables/core_facts.py`

**Formula:**
```
GAE = Goals - xG
```

**Interpretation:**
- GAE > 0: Outperforming expected (good finishing or luck)
- GAE < 0: Underperforming expected (poor finishing or unlucky)
- GAE = 0: Performing as expected

**Validation:**
- Range: typically -3 to +3 per game
- Season range: -15 to +15

---

## 4. Player Value Metrics (WAR/GAR)

### 4.1 Goals Above Replacement (GAR) - Current Implementation

**Category:** Player Value
**Status:** IMPLEMENTED (Weighted Formula)
**Code Location:** `src/tables/core_facts.py:62-69`

**Formula:**
```
GAR_total = GAR_off + GAR_def + GAR_poss + GAR_trans + GAR_poise
```

**Component Formulas:**

**Offensive GAR:**
```
GAR_off = Goals * 1.0
        + Primary_Assists * 0.7
        + Secondary_Assists * 0.4
        + SOG * 0.015
        + xG * 0.8
        + Shot_Assists * 0.3
```

**Defensive GAR:**
```
GAR_def = Takeaways * 0.05
        + Blocks * 0.02
        + Controlled_Zone_Exits * 0.03
```

**Possession GAR:**
```
GAR_poss = ((CF% - 50) / 100) * 0.02 * (TOI_hours * 60)
```

**Transition GAR:**
```
GAR_trans = Controlled_Zone_Entries * 0.04
```

**Poise GAR:**
```
GAR_poise = Pressure_Success * 0.02
```

**Validation:**
- Range: -2 to +5 per game
- Season range: -10 to +30

---

### 4.2 Wins Above Replacement (WAR)

**Category:** Player Value
**Status:** IMPLEMENTED
**Code Location:** `src/tables/core_facts.py`

**Formula:**
```
WAR = GAR_total / 4.5
```

**Goals Per Win Constant:** 4.5 (estimated for recreational hockey)
- NHL standard: 6.0 goals per win

**Validation:**
- Range: -0.5 to +1 per game
- Season range: -3 to +7

---

### 4.3 RAPM (Regularized Adjusted Plus-Minus) - GAP

**Category:** Player Value
**Status:** NOT IMPLEMENTED
**Code Location:** N/A

**Target Formula:**
```
beta_ridge = argmin[ SUM(w_i * (y_i - X_i' * beta)^2) + lambda * SUM(beta_j^2) ]
```

**Where:**
- y_i = target rate (xGF/60, xGA/60, etc.) for stint i
- X_i = player indicator vector (+1 home, -1 away, 0 not on ice)
- w_i = stint duration weight
- lambda = regularization parameter (cross-validated)

**Requires:**
1. Stint table (fact_stints) - NOT IMPLEMENTED
2. Player indicator matrix
3. Ridge regression implementation

**Priority:** P0 - Critical Gap

---

### 4.4 Goalie GAR

**Category:** Player Value
**Status:** IMPLEMENTED
**Code Location:** `src/tables/core_facts.py:72-78`

**Formula:**
```
GAR_goalie = Saves_Above_Average * 0.1
           + HD_Saves * 0.15
           + Goals_Prevented * 1.0
           + Rebound_Control * 0.05
           + QS_Bonus * 0.5
```

**Where:**
```
Saves_Above_Average = Saves - (Shots_Against * League_Avg_Save_Pct)
Goals_Prevented = xGA - GA
QS_Bonus = 1 if Quality_Start else 0
```

---

## 5. Transition Metrics

### 5.1 Zone Entry Rate

**Category:** Transition
**Status:** IMPLEMENTED
**Code Location:** `src/tables/event_analytics.py`

**Formula:**
```
Zone_Entry_Rate = Zone_Entries / (Zone_Entries + Failed_Entries)
```

**By Type:**
```
Carry_Entry_Rate = Carry_Entries / Total_Entries
Pass_Entry_Rate = Pass_Entries / Total_Entries
Dump_Entry_Rate = Dump_Entries / Total_Entries
```

**Validation:**
- Entry rate range: 0-100%
- Controlled (carry+pass): typically 50-70%

---

### 5.2 Zone Exit Rate

**Category:** Transition
**Status:** IMPLEMENTED
**Code Location:** `src/tables/event_analytics.py`

**Formula:**
```
Zone_Exit_Rate = Successful_Exits / (Successful_Exits + Failed_Exits)
Controlled_Exit_Rate = Controlled_Exits / Total_Exits
```

**Exit Types:**
- Controlled: Carry or pass out
- Dump: Clear/rim
- Failed: Turnover in d-zone

---

### 5.3 Rush Chance Generation

**Category:** Transition
**Status:** IMPLEMENTED
**Code Location:** `src/tables/event_analytics.py`

**Formula:**
```
Rush_Chance_Rate = Rush_Shots / Zone_Entries
Rush_xG = SUM(xG WHERE is_rush = True)
```

**Validation:**
- Rush shots typically 10-20% of total shots
- Rush xG higher than non-rush due to 1.3x modifier

---

## 6. Defensive Metrics

### 6.1 Takeaways

**Category:** Defense
**Status:** IMPLEMENTED
**Code Location:** `src/tables/core_facts.py`

**Formula:**
```
Takeaways = COUNT(events WHERE event_type = 'Takeaway')
```

**Validation:**
- Range: 0-10 per game (typical: 0-3)

---

### 6.2 Giveaways

**Category:** Defense
**Status:** IMPLEMENTED
**Code Location:** `src/tables/core_facts.py`

**Formula:**
```
Giveaways = COUNT(events WHERE event_type = 'Giveaway')
```

**Subtypes tracked:**
- Bad giveaways (dangerous zone)
- Neutral zone giveaways
- Forced giveaways (pressure-induced)

---

### 6.3 Blocked Shots

**Category:** Defense
**Status:** IMPLEMENTED
**Code Location:** `src/tables/core_facts.py`

**Formula:**
```
Blocks = COUNT(events WHERE event_type = 'Block' AND player = blocker)
```

**Note:** Blocker is `event_player_1` on block events

---

### 6.4 Entry Denials

**Category:** Defense
**Status:** PARTIAL
**Code Location:** `src/tables/event_analytics.py`

**Formula:**
```
Entry_Denials = COUNT(zone_entries WHERE outcome = 'Denied')
```

**Gap:** Currently tracks denied entries but does not credit to specific defender.

---

## 7. Goalie Metrics

### 7.1 Save Percentage

**Category:** Goalie
**Status:** IMPLEMENTED
**Code Location:** `src/calculations/goalie_calculations.py`

**Formula:**
```
Save_Pct = Saves / Shots_Against
         = (Shots_Against - Goals_Against) / Shots_Against
```

**Validation:**
- Range: 0.800 - 1.000
- League average: ~0.900-0.920

---

### 7.2 High-Danger Save Percentage

**Category:** Goalie
**Status:** IMPLEMENTED
**Code Location:** `src/calculations/goalie_calculations.py`

**Formula:**
```
HD_Save_Pct = HD_Saves / HD_Shots_Against
```

**Where:**
- HD_Shots = shots from high-danger zone
- HD_Saves = HD_Shots - HD_Goals

**Validation:**
- Range: 0.700 - 0.950
- More variable than overall save %

---

### 7.3 Goals Saved Above Expected (GSAx)

**Category:** Goalie
**Status:** IMPLEMENTED
**Code Location:** `src/calculations/goalie_calculations.py`

**Formula:**
```
GSAx = xGA - GA
     = SUM(xG_against) - Goals_Against
```

**Interpretation:**
- GSAx > 0: Goalie saving more than expected (good)
- GSAx < 0: Goalie allowing more than expected (poor)

**Validation:**
- Per game range: -3 to +3
- Season range: -15 to +20

---

### 7.4 Rebound Control

**Category:** Goalie
**Status:** IMPLEMENTED
**Code Location:** `src/calculations/goalie_calculations.py`

**Formula:**
```
Rebound_Control = 1 - (Rebounds_Allowed / Saves)
```

**Where:**
- Rebounds_Allowed = shots that resulted in rebound opportunity

**Validation:**
- Range: 0.70 - 0.95
- Higher = better control

---

## 8. Game Score & Ratings

### 8.1 Game Score

**Category:** Composite
**Status:** IMPLEMENTED
**Code Location:** `src/tables/core_facts.py`

**Formula:**
```
Game_Score = Scoring_Component
           + Shots_Component
           + Playmaking_Component
           + Defense_Component
           + Hustle_Component
```

**Component Breakdown:**
```
Scoring = Goals * 1.0 + Primary_Assists * 0.8 + Secondary_Assists * 0.5
Shots = SOG * 0.1 + HD_Shots * 0.15
Playmaking = Controlled_Entries * 0.08 + Second_Touch * 0.02
Defense = Takeaways * 0.15 + Blocks * 0.08 + Poke_Checks * 0.05
Hustle = (FO_Wins - FO_Losses) * 0.03
```

**Validation:**
- Range: -2 to +5
- Average: ~0.5-1.0

---

### 8.2 Player Rating

**Category:** Composite
**Status:** IMPLEMENTED
**Code Location:** `src/calculations/ratings.py`

**Formula:**
```
Rating = f(Game_Score_Avg, Position, Games_Played)
```

**Scale:** 2.0 - 6.0 (5-point scale)

| Rating | Label | Percentile |
|--------|-------|------------|
| 6.0 | Elite | 95th+ |
| 5.0 | Excellent | 80-95th |
| 4.0 | Good | 50-80th |
| 3.0 | Average | 20-50th |
| 2.0 | Below Average | <20th |

---

### 8.3 Quality of Competition (QoC)

**Category:** Context
**Status:** IMPLEMENTED
**Code Location:** `src/calculations/ratings.py`

**Formula:**
```
QoC = SUM(opponent_rating * shared_toi) / SUM(shared_toi)
```

**Validation:**
- Range: 2.0 - 6.0 (same as rating scale)

---

### 8.4 Quality of Teammates (QoT)

**Category:** Context
**Status:** IMPLEMENTED
**Code Location:** `src/calculations/ratings.py`

**Formula:**
```
QoT = SUM(teammate_rating * shared_toi) / SUM(shared_toi)
```

---

## 9. Micro-Statistics

### 9.1 Tracked Micro-Stats (22 Types)

**Category:** Micro-Stats
**Status:** IMPLEMENTED
**Code Location:** `src/tables/core_facts.py`, `dim_micro_stat`

**Offensive:**
| Stat | Description | Detection |
|------|-------------|-----------|
| Screen | Sets screen on goalie | event_detail_2 contains 'screen' |
| Tip | Deflects shot | event_detail_2 contains 'tip' |
| One-Timer | Shot directly off pass | Pass->Shot <= 1.5s |
| Board_Battle_Win | Wins puck on boards | event_type = 'Board_Battle', outcome = 'Won' |
| Board_Battle_Loss | Loses puck on boards | event_type = 'Board_Battle', outcome = 'Lost' |
| Deke | Dekes defender | event_detail_2 contains 'deke' |
| Drive_Middle | Drives to middle | event_detail contains 'drive_middle' |
| Drive_Wide | Drives wide | event_detail contains 'drive_wide' |
| Crash_Net | Crashes the net | event_detail_2 contains 'crash' |
| Give_Go | Give and go play | event_detail contains 'give_go' |
| Second_Touch | Second touch on play | sequence analysis |
| Cycle | Cycle possession | event_detail contains 'cycle' |

**Defensive:**
| Stat | Description | Detection |
|------|-------------|-----------|
| Poke_Check | Poke checks puck | event_type = 'Poke_Check' |
| Stick_Check | Stick checks player | event_type = 'Stick_Check' |
| Zone_Entry_Denial | Forces failed entry | zone_entry.outcome = 'Denied' |
| Backcheck | Backchecking effort | event_detail_2 contains 'backcheck' |
| Forecheck | Forechecking pressure | event_detail_2 contains 'forecheck' |

**Pass Types:**
| Stat | Description |
|------|-------------|
| Cross_Ice | Pass across ice |
| Stretch | Long stretch pass |
| Breakout | Breakout pass |
| Rim | Rim around boards |
| Bank | Bank pass off boards |
| Slot | Pass to slot |
| Behind_Net | Pass from behind net |

---

### 9.2 Composite Micro-Stat Indices

**Offensive Creativity Index:**
```
OCI = (Dekes * 0.3 + Give_Gos * 0.25 + One_Timers * 0.2 + Cross_Ice * 0.15 + Cycles * 0.1) / TOI_hours
```

**Defensive Activity Index:**
```
DAI = (Poke_Checks * 0.3 + Stick_Checks * 0.2 + Entry_Denials * 0.3 + Backchecks * 0.2) / TOI_hours
```

**Net Front Presence:**
```
NFP = (Screens * 0.4 + Tips * 0.3 + Crash_Net * 0.3) / TOI_hours
```

---

## 10. Aggregation & Per-60 Metrics

### 10.1 Per-60 Minutes Formula

**Category:** Rate Stats
**Status:** IMPLEMENTED
**Code Location:** `config/formulas.json`

**Generic Formula:**
```
Stat_Per60 = (Stat / TOI_minutes) * 60
           = (Stat / TOI_seconds) * 3600
```

**Examples:**
```
Goals_Per60 = (Goals / TOI_minutes) * 60
xG_Per60 = (xG / TOI_minutes) * 60
CF_Per60 = (CF / TOI_minutes) * 60
```

**Validation:**
- Only calculate when TOI > 0
- Flag low-TOI players (< 5 minutes) for rate stat reliability

---

### 10.2 Season Aggregations

**Category:** Aggregation
**Status:** IMPLEMENTED
**Code Location:** `src/tables/aggregations.py`

**Formula:**
```
Season_Stat = SUM(Game_Stat) for all games in season
Season_Rate = SUM(Stat) / SUM(TOI) * 60
```

**Tables:**
- `fact_player_season_stats` - Advanced metrics
- `fact_player_season_stats_basic` - Official league stats
- `fact_goalie_season_stats` - Goalie aggregations
- `fact_team_season_stats` - Team aggregations

---

### 10.3 Career Aggregations

**Category:** Aggregation
**Status:** IMPLEMENTED
**Code Location:** `src/tables/aggregations.py`

**Formula:**
```
Career_Stat = SUM(Season_Stat) for all seasons
Career_Rate = SUM(Stat) / SUM(TOI) * 60
```

**Tables:**
- `fact_player_career_stats` - Advanced metrics
- `fact_player_career_stats_basic` - Official league stats
- `fact_goalie_career_stats` - Goalie aggregations

---

## Appendix A: Formula Constants

| Constant | Value | Usage |
|----------|-------|-------|
| GOALS_PER_WIN | 4.5 | WAR calculation (rec hockey) |
| NHL_GOALS_PER_WIN | 6.0 | NHL standard |
| HD_XG_BASE | 0.25 | High-danger base rate |
| MD_XG_BASE | 0.08 | Medium-danger base rate |
| LD_XG_BASE | 0.03 | Low-danger base rate |
| RUSH_MODIFIER | 1.3 | Rush xG multiplier |
| REBOUND_MODIFIER | 1.5 | Rebound xG multiplier |
| ONETIMER_MODIFIER | 1.4 | One-timer xG multiplier |
| BREAKAWAY_MODIFIER | 2.5 | Breakaway xG multiplier |
| FLURRY_WINDOW | 3.0 | Seconds for flurry detection |
| REBOUND_WINDOW | 3.0 | Seconds for rebound detection |

---

## Appendix B: Gap Summary

| Metric | Status | Priority | Dependency |
|--------|--------|----------|------------|
| Flurry-Adjusted xG | GAP | P0 | None |
| Stint Table | GAP | P0 | None |
| RAPM | GAP | P0 | Stint Table |
| GBM xG Model | GAP | P1 | XY Coordinates |
| Royal Road | GAP | P1 | XY Coordinates |
| WDBE Faceoffs | GAP | P2 | None |
| Gap Control | GAP | P2 | XY Coordinates |
| Replacement Level | GAP | P2 | RAPM |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-21 | Analytics Team | Initial catalog with 50+ calculations |
