# BenchSight Stats Gap Analysis
## Comparing Current Implementation vs Documentation & Industry Standards

---

## Executive Summary

| Category | Documented | Implemented | Gap % | Priority |
|----------|------------|-------------|-------|----------|
| Core Counting Stats | 15 | 15 | 0% | ✅ |
| Time Stats | 8 | 10 | 0% | ✅ |
| Shot Metrics | 12 | 10 | 17% | P2 |
| Passing Stats | 6 | 4 | 33% | P2 |
| Faceoff Stats | 4 | 4 | 0% | ✅ |
| Zone Transition | 12 | 6 | 50% | P1 |
| Turnover Stats | 8 | 4 | 50% | P1 |
| Plus/Minus | 6 | 6 | 0% | ✅ |
| Corsi/Fenwick | 8 | 8 | 0% | ✅ |
| Per-60 Rates | 8 | 8 | 0% | ✅ |
| Goalie Stats | 10 | 8 | 20% | P2 |
| Defender Stats | 8 | 2 | 75% | P1 |
| Micro-Stats | 50+ | 25 | 50% | P2 |
| Rating-Aware | 6 | 2 | 67% | P2 |
| H2H/WOWY Details | 10 | 3 | 70% | P1 |
| xG Model | 5 | 1 | 80% | P3 |

---

## ✅ FULLY IMPLEMENTED

### Core Counting Stats
- [x] Goals (G) - verified
- [x] Assists (A) - with A1/A2 distinction
- [x] Points (PTS)
- [x] Shots on Goal (SOG)
- [x] Shot Attempts (shots_blocked, shots_missed)
- [x] Shooting % (shooting_pct)
- [x] Hits
- [x] Blocks

### Time on Ice
- [x] TOI Total (toi_seconds)
- [x] Playing TOI (playing_toi_seconds)
- [x] Stoppage Time (stoppage_seconds)
- [x] Shift Count (shift_count)
- [x] Logical Shifts (logical_shifts)
- [x] Avg Shift Length (avg_shift)
- [x] Avg Playing Shift (avg_playing_shift)

### Faceoffs
- [x] Faceoff Wins (fo_wins)
- [x] Faceoff Losses (fo_losses)
- [x] Faceoff Total (fo_total)
- [x] Faceoff % (fo_pct)

### Plus/Minus
- [x] Plus EV (plus_ev)
- [x] Minus EV (minus_ev)
- [x] Plus/Minus EV (plus_minus_ev)
- [x] Plus Total (plus_total)
- [x] Minus Total (minus_total)
- [x] EN-Adjusted +/- (plus_en_adj, minus_en_adj)

### On-Ice Possession
- [x] Corsi For (corsi_for)
- [x] Corsi Against (corsi_against)
- [x] Fenwick For (fenwick_for)
- [x] Fenwick Against (fenwick_against)
- [x] CF% (cf_pct)
- [x] FF% (ff_pct)

### Per-60 Rates
- [x] Goals Per 60
- [x] Assists Per 60
- [x] Points Per 60
- [x] Shots Per 60
- [x] All stats also have "playing" variants

### Rating Context
- [x] Opponent Avg Rating (opp_avg_rating)
- [x] Skill Differential (skill_diff)
- [x] Player Rating (player_rating)

---

## ⚠️ PARTIALLY IMPLEMENTED (Needs Enhancement)

### Zone Transitions
**Have:**
- [x] Zone Entries (zone_entries)
- [x] Zone Exits (zone_exits)

**Missing:**
- [ ] Controlled Entry % (ZE_C / ZE)
- [ ] Zone Entry Success Rate
- [ ] Controlled Exits (ZX_C)
- [ ] Entry Denials (as defender)
- [ ] Exit Denials (as defender)
- [ ] Entries Allowed (defender perspective)
- [ ] Exit Types (carry vs pass vs dump)

**Source Data Available:** Yes - in dim_event_detail and fact_events_player
**Priority:** P1

### Turnovers
**Have:**
- [x] Giveaways
- [x] Takeaways

**Missing:**
- [ ] Giveaway Quality (BAD/NEUTRAL/GOOD)
- [ ] Turnover Differential (TAKE - GIVE_BAD)
- [ ] Turnover Rate (per 60)
- [ ] Zone-specific turnovers (OZ, NZ, DZ)

**Source Data Available:** Yes - dim_turnover_quality exists
**Priority:** P1

### Micro-Stats (Play Details)
**Have (154 play_detail codes tracked, but not aggregated to player stats):**
- [x] Tracking of: Dekes, Screens, Backchecks, Poke checks, Stick checks, etc.

**Missing Aggregations:**
- [ ] Dekes Attempted
- [ ] Dekes Successful
- [ ] Screens
- [ ] Backchecks
- [ ] Poke Checks
- [ ] Stick Checks
- [ ] Blocked Shots (as play detail)
- [ ] In Shot/Pass Lane
- [ ] Separate from Puck
- [ ] Zone Entry Denials
- [ ] Zone Exit Denials
- [ ] Loose Puck Battles Won
- [ ] Loose Puck Battles Lost
- [ ] Puck Recoveries
- [ ] Beat by Deke (defender)
- [ ] Beat by Speed (defender)
- [ ] Crash Net
- [ ] Drive attempts

**Note:** All data exists in fact_events_player.play_detail - just needs aggregation!
**Priority:** P2 (high value, moderate effort)

### Goalie Stats
**Have:**
- [x] Saves
- [x] Goals Against
- [x] TOI
- [x] Shots Faced
- [x] Save %
- [x] GAA

**Missing:**
- [ ] Rebound Control % (from Save_Rebound events)
- [ ] Freeze % (from Save_Freeze events)
- [ ] High Danger Save %
- [ ] Expected Saves (based on xG)
- [ ] Goals Saved Above Expected (GSAx)

**Source Data Available:** Partial - have Save_Rebound, Save_Freeze in event_detail
**Priority:** P2

### H2H/WOWY Details
**Have:**
- [x] shifts_together
- [x] Venue tracking

**Missing (from WOWY inspiration):**
- [ ] GF% Together vs Apart
- [ ] GA% Together vs Apart
- [ ] CF% Together vs Apart
- [ ] xGF% Together vs Apart
- [ ] TOI Together (not just shifts)
- [ ] Relative Corsi Impact

**Priority:** P1 (easy to add, high value)

---

## ❌ NOT IMPLEMENTED (Gap Items)

### Defender-Specific Stats
**Documented but missing:**
- [ ] Shots Against (as primary defender)
- [ ] Goals Against (as primary defender)
- [ ] Entries Allowed (opp_player_1)
- [ ] Exits Denied
- [ ] Times Beat by Deke
- [ ] Times Beat by Speed
- [ ] Defensive Impact Rating

**Source Data:** opp_player_1 role exists in fact_events_player
**Priority:** P1 (unique value prop)

### Rating-Adjusted Stats
**Documented but missing:**
- [ ] Rating-Adjusted Goals
- [ ] Rating-Adjusted +/-
- [ ] Quality of Competition (QoC)
- [ ] Quality of Teammates (QoT)
- [ ] Expected Performance vs Rating

**Source Data:** player_rating and opp_avg_rating exist
**Priority:** P2

### xG Model Components
**Documented but missing:**
- [ ] Shot Distance (from XY)
- [ ] Shot Angle (from XY)
- [ ] Rush Shot Flag
- [ ] Rebound Shot Flag
- [ ] One-Timer Flag
- [ ] xG per shot
- [ ] xGF/xGA aggregations
- [ ] Goals Above Expected

**Source Data:** fact_shot_xy has coordinates
**Note:** Line combos has xgf placeholder but not fully implemented
**Priority:** P3 (complex)

### Composite Ratings (from STATS_DICTIONARY)
**Documented but missing:**
- [ ] Offensive Rating (weighted composite)
- [ ] Defensive Rating (weighted composite)
- [ ] Hustle Rating (backcheck, forechecks, battles)
- [ ] Impact Score
- [ ] WAR (Wins Above Replacement)

**Priority:** P3 (requires other stats first)

### PDO / Luck Metrics
**Documented but missing:**
- [ ] On-ice Shooting %
- [ ] On-ice Save %
- [ ] PDO (SH% + SV%)

**Priority:** P2

---

## Inspiration Link Findings (NEW IDEAS)

### From Evolving Hockey
- [ ] RAPM (Regularized Adjusted Plus-Minus)
- [ ] Isolated impact metrics
- [ ] Multi-year regression models

### From MoneyPuck
- [ ] Shot probability heat maps
- [ ] Pre-shot movement tracking
- [ ] Game prediction models

### From Natural Stat Trick
- [ ] Shift-by-shift breakdown
- [ ] Zone start % (O-Zone, D-Zone, Neutral)
- [ ] High Danger scoring chances

### From JFresh Hockey
- [ ] Player card visualizations
- [ ] Percentile rankings vs position
- [ ] Isolated offense/defense impacts

### From All Three Zones
- [ ] Transition stat specialization
- [ ] Entry success by type
- [ ] Exit efficiency metrics

### Beer League Specific (from docs)
- [ ] Shift Length Warning (fatigue indicator)
- [ ] Sub Pattern Equity
- [ ] Bench Minor Rate
- [ ] Performance Decay by Period
- [ ] Fatigue Score

---

## Priority Implementation Roadmap

### P1 - High Value, Data Already Exists

| Stat | Source | Effort |
|------|--------|--------|
| Zone Entry/Exit Types | fact_events_player.event_detail_2 | 2 hrs |
| Controlled Entry % | Derived calculation | 1 hr |
| Turnover Quality Aggregation | dim_turnover_quality join | 2 hrs |
| H2H with GF/GA/CF/CA | Match events to shifts | 4 hrs |
| WOWY with performance deltas | Same as above | 4 hrs |
| Defender Stats | opp_player_1 aggregations | 4 hrs |
| Zone Starts % | Count faceoff locations | 2 hrs |

**Total P1 Effort: ~20 hours**

### P2 - Medium Value, Moderate Effort

| Stat | Source | Effort |
|------|--------|--------|
| Micro-stat Aggregations | play_detail counts | 8 hrs |
| Goalie Rebound/Freeze % | event_detail analysis | 2 hrs |
| PDO Calculation | Derived from on-ice stats | 2 hrs |
| Rating-Adjusted Stats | Apply adjustment formula | 4 hrs |
| Pass Completion by Zone | Add zone context | 2 hrs |

**Total P2 Effort: ~18 hours**

### P3 - Advanced, Complex

| Stat | Source | Effort |
|------|--------|--------|
| xG Model | fact_shot_xy + model training | 16 hrs |
| GSAx (Goals Saved Above Expected) | xG + actual GA | 4 hrs |
| Composite Ratings | Weighted formulas | 4 hrs |
| WAR Framework | Multiple inputs | 16 hrs |
| RAPM Model | Ridge regression | 24 hrs |

**Total P3 Effort: ~64 hours**

---

## Quick Wins (Can Add Today)

1. **Controlled Entry Rate** - Just divide controlled_entries / total_entries
2. **Turnover Differential** - takeaways - giveaways (already have columns)
3. **Zone Starts %** - Count faceoffs by zone from event_detail
4. **Per-60 Turnovers** - Apply formula to existing columns

---

## Data Availability Matrix

| Stat Category | Source Table | Column Exists | Notes |
|---------------|--------------|---------------|-------|
| Zone Entry Types | fact_events_player | event_detail_2 | Has ZoneEntry-Carry, etc |
| Defender Target | fact_events_player | opp_player_1 | Already tracked |
| Play Details | fact_events_player | play_detail | 154 unique values |
| Shot XY | fact_shot_xy | x, y, game_id | Has coords |
| Turnover Quality | dim_turnover_quality | quality | BAD/NEUTRAL/GOOD |
| Save Types | fact_events | event_detail | Save_Freeze, Save_Rebound |
| Rating Context | fact_events | skill columns | player vs opp skill |

---

*Generated: December 29, 2024*
*Sources: STAT_DEFINITIONS.md, STATS_DICTIONARY.md, ADVANCED_STATS.md, INSPIRATION_AND_RESEARCH.md*
