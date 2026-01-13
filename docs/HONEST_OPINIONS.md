# BenchSight Honest Opinions

Last Updated: 2026-01-12
Version: 27.2

This document provides an honest assessment of the BenchSight system - what works well, what needs improvement, and what the limitations are.

---

## What Works Well ✅

### Data Pipeline
- **Robust ETL**: Processes 4 games in ~115 seconds with 135 tables
- **Consistent goal counting**: Single source of truth via `is_goal_scored()` function
- **Comprehensive stats**: 428+ columns covering most hockey analytics
- **Validation framework**: 10 automated checks catch common errors

### Analytics Quality
- **Rush stats**: Now properly track zone entries that lead to shots/goals
- **Micro stats**: DISTINCT counting prevents double-counting
- **Game state tracking**: Properly tracks leading/trailing/tied situations
- **Player attribution**: Correctly uses event_player_1 for credit

### Documentation
- **Complete formula documentation**: Every calculation is documented in CALCULATION_LOG
- **Data dictionary**: All columns defined with types and calculations
- **Code standards**: Clear guidelines for production-quality code

---

## What Needs Improvement ⚠️

### Data Quality Issues
1. **Danger zone accuracy**: Without XY coordinates, high/medium/low danger classifications are unreliable. The data shows 13 "low danger" goals vs 3 "high danger" - clearly inverted.

2. **Missing goal**: 16 tracked vs 17 expected. One goal is missing from tracking data.

3. **early/late_period_cf_pct**: Always returns 50.0 (not implemented). Needs shift-level time buckets.

4. **crash_net_success**: Always 0. Needs sequence analysis to determine if crash led to goal.

### Calibration Needed
1. **Calculated rating skews low**: Most players get calculated_rating around 2-3, even skilled players. This is because rec hockey game scores are compressed - the formula may need different thresholds for rec vs professional hockey.

2. **WAR/GAR weights**: Current weights are estimates based on NHL analytics. May not translate directly to rec hockey where skill gaps and game dynamics differ.

3. **xG model**: Uses default 0.06 xG per shot without XY data. This makes all shot quality look the same.

### Technical Debt
1. **Code duplication**: Some calculations exist in both core_facts.py and base_etl.py
2. **No unit tests**: Validation is manual via validate.py
3. **Performance**: ETL could be faster with more vectorized operations

---

## Limitations 🚫

### Tracking Data
- **No XY coordinates**: Without player/puck location, many advanced stats are impossible or placeholder
- **Manual jersey mapping**: player_id linkage requires manual lookup
- **4 games only**: Small sample size limits statistical significance

### Model Assumptions
- **Equal shot quality**: All shots treated as 0.06 xG without location data
- **Linear scoring weights**: Assumes goal = 1.0, A1 = 0.8, A2 = 0.5 (may not reflect actual value)
- **Rec hockey calibration**: Analytics designed for NHL may not translate directly

### System Constraints
- **Single-game focus**: System optimized for game-level stats, not career/season aggregation
- **Skater only**: Goalie analytics are basic (37 columns vs 428 for skaters)
- **No real-time**: Batch processing only, no live game tracking

---

## Recommendations

### For Users
1. **Don't over-rely on danger zone stats** until XY data is populated
2. **Use rating_differential directionally** - positive = better than expected, negative = worse
3. **Focus on volume stats** (goals, assists, shots, TOI) as most reliable

### For Development
1. **Priority 1**: Implement XY coordinate tracking for accurate xG and danger zones
2. **Priority 2**: Add unit tests for core calculation functions
3. **Priority 3**: Calibrate rating thresholds for rec hockey specifically

### For Interpretation
- **Game score 3-4**: Solid game for most rec players
- **Game score 5+**: Excellent game
- **Game score 2-**: Below average
- **rating_differential > 0**: Outperformed their rating
- **rating_differential < 0**: Underperformed their rating

---

## Confidence Levels

| Stat Category | Confidence | Notes |
|---------------|------------|-------|
| Goals, Assists, Points | 🟢 High | Direct from tracking |
| TOI, Shifts | 🟢 High | From shift data |
| Shots, SOG | 🟢 High | Direct from events |
| Corsi, Fenwick | 🟢 High | Calculated from shots |
| Game State TOI | 🟢 High | Running score tracking |
| Rush Stats | 🟡 Medium | Depends on zone entry tracking accuracy |
| xG | 🟡 Medium | Default values without XY |
| Danger Zones | 🔴 Low | Inverted without XY data |
| WAR/GAR | 🟡 Medium | Weights need calibration |
| Calculated Rating | 🟡 Medium | May need rec hockey calibration |

---

## Version History

### v27.2
- Fixed pp_gf/pk_ga strength split bug
- Fixed rebound stats inflation
- Implemented game state TOI tracking
- Added offensive/defensive game score breakdown
- Added calculated_rating for comparison to actual rating

### v27.1
- Fixed rush stats (shots/goals were all 0)
- Fixed defensive rush success
- Fixed micro stats double-counting
- Added period SOG breakdown
