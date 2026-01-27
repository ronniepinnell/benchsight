# BenchSight Canonical Definitions

> **Purpose:** Single source of truth for all hockey analytics terminology used in BenchSight. These definitions establish unambiguous criteria for implementation consistency and industry alignment.

**Version:** 1.0
**Last Updated:** 2026-01-21
**Owner:** Analytics Team

---

## Table of Contents

1. [Event & Sequence Concepts](#1-event--sequence-concepts)
2. [Scoring & Chance Concepts](#2-scoring--chance-concepts)
3. [Spatial & Zone Concepts](#3-spatial--zone-concepts)
4. [Defensive Concepts](#4-defensive-concepts)
5. [Player Evaluation Concepts](#5-player-evaluation-concepts)
6. [Game State Concepts](#6-game-state-concepts)

---

## 1. Event & Sequence Concepts

### 1.1 Stint

**Definition:** A continuous time interval during which all 10 skaters and both goalies remain constant on the ice.

**Technical Criteria:**
- **Start Triggers:** Game start, any player substitution (line change), goal scored, penalty start, penalty end, period start
- **End Triggers:** Same as start triggers (next stint begins)
- **Minimum Duration:** 0 seconds (instantaneous stints possible during rapid changes)
- **Maximum Duration:** Unbounded (limited by game clock)

**Schema:**
```
stint_id = {game_id}_{period}_{stint_sequence_number}
```

**Grain:** One row per continuous personnel configuration

**Why It Matters:** Stints are the foundational unit for RAPM (Regularized Adjusted Plus-Minus) calculations. Without properly materialized stint data, player contributions cannot be isolated from linemate effects.

**Industry Reference:** Evolving Hockey uses stints as the basis for their WAR model's ridge regression.

**Implementation Status:** NOT IMPLEMENTED (Critical Gap)

---

### 1.2 Play

**Definition:** A possession-linked chain of events that represents a single tactical unit of hockey action.

**Technical Criteria:**
- **Start Triggers:**
  - Faceoff win
  - Turnover gain (takeaway, interception, loose puck recovery)
  - Zone entry
  - Controlled breakout
  - Goalie freeze (for opposing team's next play)

- **End Triggers:**
  - Shot on goal (any outcome)
  - Turnover loss (giveaway, failed pass, lost board battle)
  - Icing
  - Offside
  - Penalty
  - Goalie freeze
  - Period end

**Key:** `play_key` in event tables

**Grain:** Multiple events per play; one `play_key` shared by all events in the play

**Relationship to Sequence:** A sequence contains one or more plays; plays are subsets of sequences.

**Implementation Status:** IMPLEMENTED via `play_key` column

---

### 1.3 Sequence

**Definition:** A longer chain of related plays that spans possession changes but maintains thematic continuity (e.g., offensive zone pressure despite brief turnovers).

**Technical Criteria:**
- **Start Triggers:**
  - Zone entry (begins offensive sequence)
  - Defensive zone clearance failure (begins sustained pressure sequence)
  - Power play start

- **End Triggers:**
  - Full zone clearance (puck crosses opposite blue line)
  - Goal
  - Penalty
  - Period end
  - Extended neutral zone play (>10 seconds without zone entry)

**Key:** `sequence_key` in event tables

**Grain:** Multiple plays per sequence; one `sequence_key` shared

**Use Case:** Analyzing sustained pressure, cycle effectiveness, and extended zone time.

**Implementation Status:** IMPLEMENTED via `sequence_key` column

---

### 1.4 Possession

**Definition:** A team-controlled stretch of play between turnovers or stoppages where one team has primary control of the puck.

**Technical Criteria:**
- **Possession Start:**
  - Faceoff win
  - Takeaway
  - Loose puck recovery
  - Goalie gaining control
  - Interception

- **Possession End:**
  - Giveaway
  - Shot blocked/saved (if opponent gains control)
  - Lost board battle
  - Failed pass
  - Icing
  - Offside

**Duration Calculation:**
```
possession_duration = end_time - start_time (seconds)
```

**Team Attribution:** The team of the player who last had confirmed puck control.

**Contested Possession:** Loose puck situations are attributed to neither team until control is established.

**Implementation Status:** IMPLICIT (derived from event sequences, not explicitly materialized)

---

### 1.5 Rush

**Definition:** A zone entry followed by a shot attempt within a defined event/time window, representing a quick-strike offensive opportunity.

**Technical Criteria:**
- **Rush Start:** Zone entry event (carry, dump, or pass)
- **Rush End:** Shot attempt (SOG, goal, blocked, missed)
- **Maximum Events:** 5 events between entry and shot
- **Maximum Time:** 10 seconds between entry and shot
- **Manpower Context:** Track whether numerical advantage (odd-man) or standard rush

**Classification:**
| Rush Type | Definition |
|-----------|------------|
| Odd-Man Rush | Attackers outnumber defenders at entry (2v1, 3v2, etc.) |
| Standard Rush | Even or defender advantage (2v2, 3v3, etc.) |
| Breakaway | 1v0 (shooter vs goalie only) |

**Key:** `rush_event_id` or `is_rush` flag on shot events

**xG Modifier:** Rush shots receive 1.3x xG multiplier

**Implementation Status:** IMPLEMENTED (entry to shot <=5 events)

---

### 1.6 Odd-Man Rush

**Definition:** A rush where the attacking team has a numerical advantage over defenders at the time of zone entry.

**Technical Criteria:**
- **2-on-1:** Two attackers vs one defender (plus goalie)
- **3-on-2:** Three attackers vs two defenders
- **3-on-1:** Three attackers vs one defender
- **Breakaway:** One attacker vs goalie (0 defenders)

**Detection Logic:**
```python
if attackers_at_entry > defenders_at_entry:
    is_odd_man = True
    odd_man_type = f"{attackers_at_entry}v{defenders_at_entry}"
```

**xG Modifier:** Additional 1.2-2.5x depending on odd-man type (breakaway highest)

**Implementation Status:** PARTIAL (detected but not fully typed)

---

## 2. Scoring & Chance Concepts

### 2.1 Scoring Chance

**Definition:** A shot attempt with elevated goal probability, determined by location and/or pre-shot context.

**Technical Criteria (OR conditions):**
1. Shot xG > 0.05 (5% goal probability)
2. Shot from high-danger zone (slot area)
3. Shot with significant modifier (rebound, one-timer, breakaway)

**Classification:**
| Category | xG Threshold | Location | Context |
|----------|--------------|----------|---------|
| High-Danger | xG > 0.15 | Slot (inner) | Any |
| Medium-Danger | 0.05 < xG <= 0.15 | Slot (outer) or point with screen | Rush, one-timer |
| Low-Danger | xG <= 0.05 | Perimeter | Standard shot |

**Implementation Status:** IMPLEMENTED via danger zone classification

---

### 2.2 High-Danger Chance

**Definition:** A shot attempt from the most dangerous scoring area with the highest goal probability.

**Technical Criteria:**
- **Location:** Within the "slot" - defined as:
  - Distance: <=12 feet from goal center
  - Angle: Within 45 degrees of goal line center
  - Alternative: Inside the "home plate" area (trapezoid from posts to hashmarks)

- **xG Threshold:** Typically xG > 0.15

**Spatial Definition (XY Coordinates):**
```
High-Danger Zone:
  x: goal_line to 12ft out
  y: -8ft to +8ft from center (within post width extended)
```

**Implementation Status:** IMPLEMENTED via `dim_danger_zone`

---

### 2.3 Flurry

**Definition:** A cluster of multiple shot attempts occurring in rapid succession, requiring probability adjustment to avoid over-counting expected goals.

**Technical Criteria:**
- **Time Window:** 2+ shots within 3 seconds
- **Same Possession:** All shots must occur without change of possession
- **Types:** Rebound sequences, deflection attempts, scramble situations

**Probability Adjustment Formula:**
```
Standard (naive):     xG_total = xG_1 + xG_2 + xG_3
Flurry-adjusted:      xG_total = 1 - [(1-xG_1) * (1-xG_2) * (1-xG_3)]
```

**Example:**
- Three shots with xG = 0.10 each
- Naive sum: 0.30
- Flurry-adjusted: 1 - (0.9 * 0.9 * 0.9) = 0.271

**Rationale:** The probability of at least one goal is less than the sum of individual probabilities because goals are mutually exclusive within a flurry (only one can be scored at a time).

**Implementation Status:** DETECTION ONLY (probability adjustment NOT implemented - Critical Gap)

---

### 2.4 Rebound

**Definition:** A shot attempt that occurs within a short time window after a previous shot was saved, blocked, or missed.

**Technical Criteria:**
- **Time Window:** <=3 seconds after prior shot outcome
- **Prior Outcomes:** Saved, blocked, missed (not goal)
- **Same Team:** Rebound shot must be by same team as original shot

**Detection:**
```python
if (current_shot_time - prior_shot_time) <= 3.0 and prior_shot_outcome != 'Goal':
    is_rebound = True
```

**xG Modifier:** 1.5x (rebounds have elevated conversion rates)

**Implementation Status:** IMPLEMENTED via `is_rebound` flag

---

### 2.5 One-Timer

**Definition:** A shot taken directly off a pass without stopping the puck, creating a quick-release scoring opportunity.

**Technical Criteria:**
- **Pass-to-Shot Time:** <=1.5 seconds (no puck control/deke)
- **Pass Type:** Direct pass to shooting position
- **Detection:** Event sequence of Pass followed by Shot within time window

**xG Modifier:** 1.4x

**Implementation Status:** IMPLEMENTED via `event_detail_2` flag

---

### 2.6 Royal Road Pass

**Definition:** A pass that crosses the center line of the ice (y=0) within a short time window before a shot, forcing the goalie to move laterally and creating a higher-danger opportunity.

**Technical Criteria:**
- **Pass Trajectory:** Crosses y=0 (center ice line perpendicular to goal)
- **Time to Shot:** <=3 seconds between pass and shot
- **Lateral Movement:** Forces goalie to move side-to-side

**Detection (requires XY):**
```python
if pass_start_y * pass_end_y < 0:  # Opposite sides of center
    if shot_time - pass_time <= 3.0:
        is_royal_road = True
```

**xG Modifier:** 1.3-1.5x (significant elevation in goal probability)

**Industry Reference:** MoneyPuck and Evolving Hockey both include royal road as an xG feature.

**Implementation Status:** NOT IMPLEMENTED (requires XY coordinates - High Priority Gap)

---

## 3. Spatial & Zone Concepts

### 3.1 Zones

**Definition:** The three primary ice surface divisions that define play location.

**Technical Criteria:**
| Zone | Code | Boundary | Team Context |
|------|------|----------|--------------|
| Offensive Zone | O | Beyond attacking blue line | Team attacking |
| Neutral Zone | N | Between blue lines | Neither attacking nor defending |
| Defensive Zone | D | Beyond defending blue line | Team defending |

**Zone Attribution:** Always relative to the team being measured. Team A's offensive zone is Team B's defensive zone.

**Implementation Status:** IMPLEMENTED via `dim_zone`

---

### 3.2 Danger Zones (Shot Location)

**Definition:** Sub-divisions of the offensive zone that classify shot danger based on proximity and angle to goal.

**Technical Criteria:**
| Zone | Distance | Angle | xG Base Rate |
|------|----------|-------|--------------|
| High-Danger | 0-12 ft | <45 deg | 0.25 |
| Medium-Danger | 12-30 ft | <60 deg | 0.08 |
| Low-Danger | 30+ ft or >60 deg | Any | 0.03 |
| Perimeter | Behind goal line | N/A | 0.01 |

**Implementation Status:** IMPLEMENTED via `dim_danger_zone`

---

### 3.3 Gap

**Definition:** The distance between the puck carrier and the nearest defender at a specific moment, typically measured at zone entry.

**Technical Criteria:**
- **Measurement Point:** Blue line crossing (zone entry)
- **Distance Unit:** Feet
- **Calculation:**
```
gap = distance(puck_carrier_xy, nearest_defender_xy)
```

**Classification:**
| Gap | Distance | Defensive Quality |
|-----|----------|-------------------|
| Tight | <6 ft | Excellent |
| Standard | 6-12 ft | Good |
| Loose | 12-20 ft | Poor |
| Blown | >20 ft | Failure |

**Industry Reference:** NHL Edge tracks gap as a primary defensive metric.

**Implementation Status:** NOT IMPLEMENTED (requires XY tracking - Medium Priority Gap)

---

### 3.4 Effective Gap

**Definition:** Gap distance adjusted for defender closing velocity, representing the true defensive pressure.

**Technical Criteria:**
```
effective_gap = raw_gap - (defender_velocity * time_to_contact)
```

**Use Case:** A 15ft gap with a defender skating at high speed toward the puck carrier may be more effective than a 10ft gap with a stationary defender.

**Implementation Status:** NOT IMPLEMENTED (requires XY + velocity - Low Priority Gap)

---

## 4. Defensive Concepts

### 4.1 Zone Entry

**Definition:** The act of moving the puck from the neutral zone into the offensive zone across the blue line.

**Technical Criteria:**
| Entry Type | Definition | Success Rate | Shot Rate |
|------------|------------|--------------|-----------|
| Carry | Player skates puck across blue line | High | High |
| Pass | Puck passed across blue line to teammate | Medium | High |
| Dump | Puck shot into zone, team retrieves | Low | Medium |
| Failed | Entry attempt turned over at blue line | N/A | N/A |

**Tracking:**
- `zone_entry_type`: Carry, Pass, Dump, Failed
- `zone_entry_outcome`: Successful, Denied, Icing, Offside
- `zone_entry_player_id`: Player who executed entry

**Implementation Status:** IMPLEMENTED via `fact_zone_entries`

---

### 4.2 Zone Exit

**Definition:** The act of moving the puck from the defensive zone into the neutral zone across the blue line.

**Technical Criteria:**
| Exit Type | Definition | Quality |
|-----------|------------|---------|
| Controlled | Player carries or passes puck out | High |
| Dump | Puck cleared (rim, flip, bank) | Medium |
| Icing | Failed clearance resulting in icing | Low |
| Failed | Exit attempt turned over in d-zone | Negative |

**Tracking:**
- `zone_exit_type`: Controlled, Dump, Icing, Failed
- `zone_exit_player_id`: Player who executed exit

**Implementation Status:** IMPLEMENTED via `fact_zone_exits`

---

### 4.3 Entry Denial

**Definition:** A defensive action that prevents a controlled zone entry, forcing a dump-in or turnover at the blue line.

**Technical Criteria:**
- **Trigger:** Attacker attempts carry/pass entry
- **Outcome:** Entry fails (dump forced, turnover, offside)
- **Credit:** Defender who forced the change in entry type

**Value:** Entry denials are high-value defensive plays as controlled entries generate significantly more shot attempts than dump-ins.

**Implementation Status:** PARTIAL (tracked as failed entries, not credited to defenders)

---

### 4.4 WDBE (Won-Draw-Back-Exit) Faceoffs

**Definition:** A faceoff classification system that categorizes wins by cleanliness and puck destination.

**Technical Criteria:**
| Category | Definition | Value |
|----------|------------|-------|
| **Won** | Clean win, puck to teammate in good position | High (+) |
| **Draw** | Contested, neither team gains clear possession | Neutral |
| **Back** | Puck goes back to own zone/defenseman | Medium (+) |
| **Exit** | Puck directly exits zone (icing risk) | Low (+) |

**Additional Classification:**
- **Clean Win:** Direct to intended target
- **Scrum Win:** Won after contested battle

**Expected Value Weighting:**
```
WDBE_EV = (Won * 1.0) + (Draw * 0.0) + (Back * 0.3) + (Exit * 0.1)
```

**Industry Reference:** Sportslogiq tracks WDBE as a primary faceoff quality metric.

**Implementation Status:** NOT IMPLEMENTED (tracks win/loss only - Medium Priority Gap)

---

## 5. Player Evaluation Concepts

### 5.1 Quality of Competition (QoC)

**Definition:** A measure of the average skill level of opponents a player faces during their ice time.

**Technical Criteria:**
```
QoC = SUM(opponent_rating * shared_ice_time) / SUM(shared_ice_time)
```

**Calculation:** Weighted average of opponent ratings based on time spent on ice together.

**Implementation Status:** IMPLEMENTED via `fact_player_qoc_summary`

---

### 5.2 Quality of Teammates (QoT)

**Definition:** A measure of the average skill level of teammates a player shares ice time with.

**Technical Criteria:**
```
QoT = SUM(teammate_rating * shared_ice_time) / SUM(shared_ice_time)
```

**Use Case:** Contextualizes player performance - strong stats with weak teammates may be more impressive than similar stats with elite linemates.

**Implementation Status:** IMPLEMENTED via linemate analysis

---

### 5.3 Competition Tier

**Definition:** A categorical grouping of opponent strength for split analysis.

**Technical Criteria (BenchSight Rating Scale 2.0-6.0):**
| Tier | Rating Range | Label |
|------|--------------|-------|
| TI01 | 5.0+ | Elite |
| TI02 | 4.0-5.0 | Above Average |
| TI03 | 3.0-4.0 | Average |
| TI04 | 2.0-3.0 | Below Average |

**Use Case:** Analyze player performance against different quality opponents.

**Implementation Status:** IMPLEMENTED via `dim_competition_tier`

---

### 5.4 Replacement Level

**Definition:** The baseline performance level of a freely available player (minor league call-up or waiver claim) used as the zero point for WAR calculations.

**Technical Criteria (NHL Standard):**
- **Forwards:** Performance of 13th+ forward by TOI (outside top 12)
- **Defensemen:** Performance of 7th+ defenseman by TOI (outside top 6)
- **Goalies:** Performance of replacement-level backup

**BenchSight Current:** Uses average (50th percentile) as baseline instead of replacement level.

**Impact:** Using average baseline undervalues below-average players and overvalues above-average players compared to true replacement-level WAR.

**Implementation Status:** NOT IMPLEMENTED (uses average baseline - Medium Priority Gap)

---

## 6. Game State Concepts

### 6.1 Strength State

**Definition:** The numerical skater configuration on ice for both teams.

**Technical Criteria:**
| Code | Home | Away | Situation |
|------|------|------|-----------|
| 5v5 | 5 | 5 | Even Strength |
| 5v4 | 5 | 4 | Home PP / Away PK |
| 4v5 | 4 | 5 | Home PK / Away PP |
| 5v3 | 5 | 3 | Home 5-on-3 PP |
| 4v4 | 4 | 4 | 4-on-4 |
| 3v3 | 3 | 3 | OT or double minor |
| 6v5 | 6 | 5 | Home EN (goalie pulled) |
| 5v6 | 5 | 6 | Away EN |

**Implementation Status:** IMPLEMENTED via `dim_strength`

---

### 6.2 Score State

**Definition:** The goal differential from the perspective of a specific team at any point in the game.

**Technical Criteria:**
```
score_state = team_goals - opponent_goals
```

| State | Value | Context |
|-------|-------|---------|
| Trailing | <0 | Behind in game |
| Tied | 0 | Score is even |
| Leading | >0 | Ahead in game |
| Close | -1, 0, +1 | Within one goal |
| Comfortable | >=+2 | Two+ goal lead |
| Desperate | <=-2 | Two+ goals behind |

**Use Case:** Player performance varies significantly by score state (e.g., playing with lead vs. chasing).

**Implementation Status:** IMPLEMENTED via game state tracking

---

### 6.3 Game Clock Context

**Definition:** Temporal context within a game that affects play style and urgency.

**Technical Criteria:**
| Context | Definition | Behavioral Impact |
|---------|------------|-------------------|
| Early Period | First 5 minutes | Standard play |
| Mid Period | Minutes 5-15 | Standard play |
| Late Period | Final 5 minutes | Increased urgency |
| Final Minute | Last 60 seconds | High urgency, EN likely |
| OT | Overtime period | High event, conservative |

**Implementation Status:** IMPLEMENTED via `dim_time_bucket`

---

## Appendix A: Cross-Reference to Implementation

| Concept | Primary Table | Key Column | Status |
|---------|---------------|------------|--------|
| Stint | fact_stints | stint_id | NOT IMPLEMENTED |
| Play | fact_events | play_key | IMPLEMENTED |
| Sequence | fact_events | sequence_key | IMPLEMENTED |
| Rush | fact_rush_events | rush_event_id | IMPLEMENTED |
| Scoring Chance | fact_scoring_chances | chance_id | IMPLEMENTED |
| Flurry | fact_events | is_flurry | PARTIAL |
| Rebound | fact_events | is_rebound | IMPLEMENTED |
| Zone Entry | fact_zone_entries | entry_id | IMPLEMENTED |
| Zone Exit | fact_zone_exits | exit_id | IMPLEMENTED |
| WDBE | N/A | N/A | NOT IMPLEMENTED |
| Gap | N/A | N/A | NOT IMPLEMENTED |
| Royal Road | N/A | N/A | NOT IMPLEMENTED |

---

## Appendix B: Industry Standard Alignment

| Concept | BenchSight | Evolving Hockey | MoneyPuck | NHL Edge |
|---------|------------|-----------------|-----------|----------|
| Stint | Missing | Core unit | Core unit | N/A |
| Rush | 5 events/10s | Similar | Similar | Similar |
| xG Flurry | Naive sum | Probabilistic | Probabilistic | N/A |
| Royal Road | Missing | Feature | Feature | N/A |
| Gap Control | Missing | N/A | N/A | Primary metric |
| WDBE | Missing | N/A | N/A | Sportslogiq |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-21 | Analytics Team | Initial canonical definitions |
