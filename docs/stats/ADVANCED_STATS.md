# Advanced Statistics Formulas

## Overview

This document explains all advanced hockey statistics used in this project, including formulas, interpretations, and references.

---

## Shot Metrics

### Corsi

**What it measures**: All shot attempts (shots on goal + missed shots + blocked shots)

**Why it matters**: Proxy for puck possession and territorial dominance

**Formulas**:
```
Corsi For (CF) = SOG + Missed + Blocked (by opponent)
Corsi Against (CA) = Opponent's CF
Corsi (C) = CF - CA
Corsi % (CF%) = CF / (CF + CA) × 100
CF/60 = CF / (TOI / 3600) × 60
```

**Interpretation**:
- CF% = 50%: Neutral (even shot attempts)
- CF% > 50%: Positive (more attempts for)
- CF% < 50%: Negative (more attempts against)

**Benchmarks**:
| Rating | CF% |
|--------|-----|
| Elite | >55% |
| Good | 52-55% |
| Average | 48-52% |
| Below Avg | 45-48% |
| Poor | <45% |

---

### Fenwick

**What it measures**: Unblocked shot attempts (excludes blocked shots)

**Why it matters**: Some argue blocked shots are noise; Fenwick may be purer

**Formulas**:
```
Fenwick For (FF) = SOG + Missed
Fenwick Against (FA) = Opponent's FF
Fenwick % (FF%) = FF / (FF + FA) × 100
```

**Difference from Corsi**: Excludes blocked shots because:
1. Shot-blocking is a repeatable skill
2. Trailing teams block more shots
3. Blocked shots don't threaten the goal

---

## Expected Goals (xG)

**What it measures**: Probability of a shot becoming a goal

**Why it matters**: Accounts for shot quality, not just quantity

**Simple Model** (used in this project):
```
Base xG by zone:
- High Danger (slot): 15-20%
- Medium Danger (circles): 5-8%
- Low Danger (perimeter): 2-3%

Modifiers:
- Rebound: ×1.5
- Rush: ×1.3
- Power Play: ×1.2
- One-timer: ×1.4
```

**Coordinate-Based Model**:
```
distance = sqrt((89-x)² + y²)
angle = atan(y / (89-x))
xG = 0.3 × exp(-0.05 × distance) × cos(angle)^0.5
```

---

## Goalie Metrics

### Save Percentage (SV%)
```
SV% = Saves / (Saves + GA) × 100
```
- Good: >91%
- Elite: >92.5%

### Goals Against Average (GAA)
```
GAA = Goals Against / (TOI / 3600) × 60
```
- Good: <2.50
- Elite: <2.00

### Goals Saved Above Expected (GSAx)
```
GSAx = xGA - Actual GA
```
- Positive = Better than expected
- Negative = Worse than expected

---

## Player Metrics

### Points Per 60 (P/60)
```
P/60 = (Goals + Assists) / (TOI / 3600) × 60
```

### Shooting Percentage (SH%)
```
SH% = Goals / SOG × 100
```
- NHL Average: 9-10%
- Sustained >15%: Usually luck/small sample

### PDO (Luck Indicator)
```
PDO = On-ice SH% + On-ice SV%
```
- PDO = 100: Average
- PDO > 102: Running hot (unsustainable)
- PDO < 98: Running cold (unsustainable)

---

## Skill-Adjusted Metrics

**Purpose**: Adjust stats for opponent quality

**Formula**:
```
opponent_difficulty = (opp_skill - midpoint) / skill_range
adjustment = opponent_difficulty × 0.25
adjusted_stat = raw_stat × (1 + adjustment)
```

**Example**: A skill-3 player scoring against skill-5 opponents:
```
difficulty = (5 - 4) / 4 = 0.25
adjustment = 0.25 × 0.25 = 0.0625
adjusted_goals = 1 × 1.0625 = 1.06
```

---

## Zone Entry Metrics

**Controlled Entry Rate**:
```
Controlled % = (Carry + Pass entries) / Total entries × 100
```

**Entry Success Rate**:
```
Success % = Successful entries / Total attempts × 100
```

---

## Micro-Stats

### Turnover Differential
```
Differential = Takeaways - Giveaways
Takeaway % = Takeaways / (Takeaways + Giveaways) × 100
```

### Loose Puck Win Rate
```
Win % = Battles Won / Total Battles × 100
```

---

## References

- Hockey-Reference Glossary: https://www.hockey-reference.com/about/glossary.html
- Evolving Hockey: https://evolving-hockey.com/glossary/
- Natural Stat Trick: https://www.naturalstattrick.com/glossary.php
- MoneyPuck: https://moneypuck.com/about.htm
- JFresh Hockey: https://jfresh.substack.com/
