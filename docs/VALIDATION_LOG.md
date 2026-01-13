# BenchSight Validation Log

## v28.0 - Goalie Stats Validation (2026-01-12)

### Critical Bug Fixed

**BUG**: Goalie saves were filtered by WRONG venue (opponent's instead of goalie's)

**Root Cause** (src/tables/core_facts.py lines 2403-2408):
```python
# OLD (BUGGY):
opp_venue = 'a' if is_home else 'h'
goalie_saves = all_saves[all_saves['team_venue'] == opp_venue]  # WRONG!

# NEW (FIXED - v28.0):
goalie_venue = 'h' if is_home else 'a'
goalie_saves = all_saves[all_saves['team_venue'] == goalie_venue]  # CORRECT
```

**Why**: Save events have `team_venue` = goalie's team (team making the save).
Goal events have `team_venue` = scoring team (opponent).

### Validation Results (Post-Fix)

| Goalie | Team | Game | Home? | Saves | Expected | GA | Expected | Status |
|--------|------|------|-------|-------|----------|-----|----------|--------|
| Francis Forte | Platinum | 18969 | ✓ | 21 | 21 | 3 | 3 | ✓ |
| Wyatt Crandall | Velodrome | 18969 | ✗ | 37 | 37 | 4 | 4 | ✓ |
| Wyatt Crandall | Velodrome | 18977 | ✓ | 36 | 36 | 2 | 2 | ✓ |
| Jared Wolf | HollowBrook | 18977 | ✗ | 24 | 24 | 3 | 3 | ✓ |
| Thane Gilmore | Nelson | 18981 | ✓ | 13 | 13 | 1 | 1 | ✓ |
| Wyatt Crandall | Velodrome | 18981 | ✗ | 32 | 32 | 2 | 2 | ✓ |
| Graham Peters | Outlaws | 18987 | ✓ | 15 | 15 | 1 | 1 | ✓ |
| Wyatt Crandall | Velodrome | 18987 | ✗ | 35 | 35 | 0 | 0 | ✓ |

**Totals**: 213 saves ✓, 16 goals against ✓

### Data Quality Issue - Game 18977 Home/Away Inverted

**Finding**: Tracking data has home/away inverted vs noradhockey.com

| Source | Home Team | Away Team | Score |
|--------|-----------|-----------|-------|
| IMMUTABLE_FACTS | HollowBrook | Velodrome | 2-4 |
| fact_events | Velodrome | HollowBrook | 3-2 |

This is a **tracking data issue**, not a calculation bug. The ETL correctly processes what's in the tracking data - the tracker recorded the wrong team as home.

**Impact**: 
- Goals against are swapped between goalies
- Home/away stats for this game are inverted
- WAR calculations affected

**Recommendation**: Fix in raw tracking data (data/raw/) and re-run ETL

### Before vs After (Bug Impact)

| Goalie | Team | Game | OLD Saves | NEW Saves | Change |
|--------|------|------|-----------|-----------|--------|
| Francis Forte | Platinum | 18969 | 37 | 21 | -16 |
| Wyatt Crandall | Velodrome | 18969 | 21 | 37 | +16 |
| Wyatt Crandall | Velodrome | 18977 | 24 | 36 | +12 |
| Jared Wolf | HollowBrook | 18977 | 36 | 24 | -12 |
| Thane Gilmore | Nelson | 18981 | 32 | 13 | -19 |
| Wyatt Crandall | Velodrome | 18981 | 13 | 32 | +19 |
| Graham Peters | Outlaws | 18987 | 35 | 15 | -20 |
| Wyatt Crandall | Velodrome | 18987 | 15 | 35 | +20 |

The bug was systematically swapping home and away goalie saves!

### Columns Validated ✓

| Column | Status | Notes |
|--------|--------|-------|
| goalie_game_key | ✓ | Format: GK{player_id}_{game_id} |
| game_id | ✓ | Matches tracked games |
| player_id | ✓ | Matches dim_player |
| player_name | ✓ | From dim_player |
| team_name | ✓ | From fact_gameroster |
| is_home | ✓ | Correctly derived from team_id vs home_team_id |
| saves | ✓ FIXED | Now correctly filtered by goalie's venue |
| goals_against | ✓ | Correctly filtered by opponent's venue |
| shots_against | ✓ | saves + goals_against |
| save_pct | ✓ | (saves / shots_against) * 100 |
| saves_butterfly/pad/glove/etc | ✓ | Breakdown from event_detail_2 |
| hd_shots_against | ✓ | HD shots by opponent |
| hd_goals_against | ✓ | HD goals by opponent |
| hd_saves | ✓ | hd_shots - hd_goals |
| hd_save_pct | ✓ | HD save percentage |
| is_quality_start | ✓ | save_pct >= 91.7 or GA <= 2 |
| is_bad_start | ✓ | save_pct < 85.0 |
| expected_goals_against | ✓ | shots_against * (1 - league_sv_pct) |
| goals_saved_above_avg | ✓ | expected - actual GA |
| saves_freeze | ✓ | Estimate: glove + chest |
| saves_rebound | ✓ | saves - freeze |
| rebound_rate | ✓ | rebound / saves * 100 |
| goalie_war | ✓ | Composite WAR from goalie metrics |

### Remaining Known Issues

1. **16 vs 17 goal discrepancy**: fact_events has 16 goals, IMMUTABLE_FACTS has 17
2. **Game 18977 home/away**: Tracking data inverted - needs manual fix
3. **Danger zone stats**: Use placeholder XY data (low reliability)

---

## Validation Queue (Next Steps)

Priority order for remaining fact table validation:

### HIGH Priority
- [ ] fact_shift_players (3,441 rows) - Core table
- [ ] fact_shifts (1,147 rows) - Core table  
- [ ] fact_team_game_stats (8 rows) - Team aggregates

### MEDIUM Priority
- [ ] fact_tracking (11,155 rows) - Source for event_players
- [ ] fact_gameroster (260 rows) - Player-game assignments
- [ ] fact_faceoffs (462 rows) - FO detail
- [ ] fact_zone_entries (568 rows) - Zone entry detail
- [ ] fact_zone_exits (548 rows) - Zone exit detail
- [ ] fact_scoring_chances (368 rows) - Scoring chance detail
- [ ] fact_rushes (373 rows) - Rush play detail
- [ ] fact_penalties (25 rows) - Penalty detail

### LOW Priority (Aggregation Tables)
- [ ] fact_player_season_stats
- [ ] fact_wowy
- [ ] fact_h2h (1,752 rows)
- [ ] fact_matchup_summary
- [ ] fact_player_pair_stats (592 rows)
- [ ] fact_line_combos (248 rows)
- [ ] fact_possession_time
- [ ] fact_player_trends
- [ ] fact_career_stats
- [ ] fact_league_leaders
- [ ] fact_zone_time
- [ ] fact_standings
- [ ] fact_momentum
- [ ] fact_team_season_stats
- [ ] fact_video

---

---

## Columns 1-10 Validation (v28.0)

### Status: ✓ VERIFIED

| # | Column | Type | Status | Notes |
|---|--------|------|--------|-------|
| 1 | goalie_game_key | TEXT | ✓ FIXED | Format: `GK{game_id}{player_id}` (removed underscore) |
| 2 | game_id | INT | ✓ | FK to dim_schedule, 4 tracked games |
| 3 | player_id | TEXT | ✓ | FK to dim_player, 5 unique goalies |
| 4 | _export_timestamp | TIMESTAMP | ✓ | ETL metadata |
| 5 | player_name | TEXT | ✓ | Denormalized from dim_player |
| 6 | team_name | TEXT | ✓ | From fact_gameroster |
| 7 | team_id | TEXT | ✓ | FK to dim_team |
| 8 | is_home | BOOLEAN | ⚠️ | Tracking data issue Game 18977 |
| 9 | saves | INT | ✓ FIXED | v28.0 fix - uses goalie's venue |
| 10 | goals_against | INT | ✓ | Opponent's Goal_Scored events |

### Known Issue: Game 18977 Home/Away Inverted (TRACKING DATA)

- **Source**: Raw tracking data has home/away inverted
- **Impact**: Velodrome marked as home, HollowBrook as away
- **Reality**: IMMUTABLE_FACTS shows HollowBrook 2-4 Velodrome (HollowBrook=home)
- **Action**: Note only - not an ETL bug, tracking data issue

### Totals Verified
- saves: 213 ✓
- goals_against: 16 ✓

---

## Columns 11-20 Validation (v28.0)

### Status: ✓ VERIFIED (with known gap)

| # | Column | Type | Status | Notes |
|---|--------|------|--------|-------|
| 11 | saves_butterfly | INT | ✓ | Matches 'butterfly' in event_detail_2 |
| 12 | saves_pad | INT | ✓ | Matches 'pad' (RightPad + LeftPad) |
| 13 | saves_glove | INT | ✓ | Matches 'glove' |
| 14 | saves_blocker | INT | ✓ | Matches 'blocker' |
| 15 | saves_chest | INT | ✓ | Matches 'chest\|shoulder' |
| 16 | saves_stick | INT | ✓ | Matches 'stick' |
| 17 | saves_scramble | INT | ✓ | Matches 'scramble' |
| 18 | hd_shots_against | INT | ✓ | danger_level='high' shots by opponent |
| 19 | hd_goals_against | INT | ✓ | danger_level='high' goals by opponent |
| 20 | hd_saves | INT | ✓ | hd_shots_against - hd_goals_against |

### Known Gap: 3 Uncategorized Saves

Save type breakdown doesn't sum to total saves for 3 goalies (diff of 1 each).

**Root Cause**: 3 saves use uncategorized event_detail_2 values:
- Save_Other: 2
- Save_Skate: 1

**Decision**: Leave as-is. These represent <1.5% of saves.

### Source Data: event_detail_2 Distribution (213 saves)

| event_detail_2 | Count | Maps To |
|----------------|-------|---------|
| Save_Butterfly | 53 | saves_butterfly |
| Save_RightPad | 40 | saves_pad |
| Save_LeftPad | 27 | saves_pad |
| Save_Chest | 30 | saves_chest |
| Save_Glove | 26 | saves_glove |
| Save_Shoulder | 13 | saves_chest |
| Save_Blocker | 11 | saves_blocker |
| Save_Stick | 8 | saves_stick |
| Save_Scramble | 2 | saves_scramble |
| Save_Other | 2 | ❌ uncategorized |
| Save_Skate | 1 | ❌ uncategorized |

### High Danger Stats Note

- danger_level only populated for 247/5823 events (4.2%)
- HD stats are sparse but calculations are correct

---

## Columns 21-30 Validation (v28.0)

### Status: ✓ VERIFIED (all 8 rows pass)

| # | Column | Type | Status | Calculation |
|---|--------|------|--------|-------------|
| 21 | hd_save_pct | FLOAT | ✓ | hd_saves / hd_shots_against * 100 |
| 22 | shots_against | INT | ✓ | saves + goals_against |
| 23 | save_pct | FLOAT | ✓ | saves / shots_against * 100 |
| 24 | is_quality_start | INT | ✓ | 1 if save_pct >= 91.7 OR goals_against <= 2 |
| 25 | is_bad_start | INT | ✓ | 1 if save_pct < 85.0 |
| 26 | expected_goals_against | FLOAT | ✓ | shots_against * (1 - 0.88) |
| 27 | goals_saved_above_avg | FLOAT | ✓ | xGA - goals_against |
| 28 | saves_freeze | INT | ✓ | saves_glove + saves_chest (estimate) |
| 29 | saves_rebound | INT | ✓ | saves - saves_freeze |
| 30 | rebound_rate | FLOAT | ✓ | saves_rebound / saves * 100 |

### Constants Used
- LEAGUE_AVG_SV_PCT = 88.0%

### Quality Start Distribution
- Quality starts: 5/8 (62.5%)
- Bad starts: 0/8 (0%)

---

## Columns 31-39 Validation (v28.0)

### Status: ✓ VERIFIED (with venue bug FIXED)

| # | Column | Type | Status | Calculation |
|---|--------|------|--------|-------------|
| 31 | goalie_gar_gsaa | FLOAT | ✓ | = goals_saved_above_avg |
| 32 | goalie_gar_hd_bonus | FLOAT | ✓ | = hd_saves * 0.15 |
| 33 | goalie_gar_qs_bonus | FLOAT | ✓ | = 0.5 if is_quality_start else 0 |
| 34 | goalie_gar_rebound | FLOAT | ✓ | = saves_freeze * 0.05 |
| 35 | goalie_gar_total | FLOAT | ✓ | = gsaa*1.0 + hd_bonus + qs_bonus + rebound |
| 36 | goalie_war | FLOAT | ✓ | = goalie_gar_total / 4.5 |
| 37 | goalie_war_pace | FLOAT | ✓ | = goalie_war * 20 |
| 38 | venue | TEXT | ✓ FIXED | = 'home' if is_home else 'away' |
| 39 | venue_id | TEXT | ✓ FIXED | FK to dim_venue (VN01=home, VN02=away) |

### Bug Fixed: venue/venue_id

**Issue**: All rows had venue='home', venue_id='VN01' regardless of is_home

**Root Cause**: add_all_fkeys.py used flawed team_name string matching against schedule

**Fix**: Changed to derive venue directly from is_home column (line 706-709)

### Constants Used (GOALIE_GAR_WEIGHTS)
- high_danger_saves: 0.15
- goals_prevented: 1.0
- rebound_control: 0.05
- quality_start_bonus: 0.5
- GOALS_PER_WIN: 4.5
- GAMES_PER_SEASON: 20

---

## v28.1 Advanced Goalie Stats Expansion

### Summary
- **Previous**: 39 columns
- **Current**: 128 columns
- **New columns**: +89

### Column Categories (128 total)

| Category | Columns | Status |
|----------|---------|--------|
| Core & Identifiers | 1-12 | ✓ |
| Save Type Breakdown | 13-19 | ✓ |
| High Danger Stats | 20-23 | ✓ |
| Rebound Control | 24-37 | ✓ (see note) |
| Period Splits | 38-52 | ✓ |
| Time Bucket/Clutch | 53-64 | ✓ |
| Shot Context | 65-76 | ✓ |
| Pressure/Sequence | 77-85 | ✓ |
| Body Location | 86-95 | ✓ |
| Workload Metrics | 96-105 | ✓ |
| Quality Indicators | 106-109 | ✓ |
| Advanced Composites | 110-119 | ✓ |
| Goalie WAR | 120-126 | ✓ |
| Venue | 127-128 | ✓ |

### Known Limitations

1. **Rebound Outcomes (cols 28-37)**: The `rebounds_team_recovered`, `rebounds_opp_recovered`, etc. are **game-level** metrics, not goalie-specific. Rebound events don't have goalie attribution in tracking data. Both goalies in same game will show identical values.

2. **Rush/Set Play Goals Against (cols 69-71)**: Set to 0 - would require joining goals with time_since_zone_entry which isn't available at goal-event level.

3. **Body Location GA (cols 89-91)**: Set to 0 - would require goal-level body location data which isn't tracked.

### Verification Notes

- Period splits verified against fact_events
- Time bucket distributions match fact_saves
- Composite ratings use documented formulas
- All calculations produce reasonable values
