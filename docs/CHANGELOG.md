# BenchSight CHANGELOG

All notable changes to the BenchSight schema and data model are documented here.

## [6.1.0] - 2025-12-29

### Fixed - Critical ETL Bugs

#### TOI Bug (Critical)
- **Problem**: All TOI values were 0 for all players
- **Root Cause**: Shift matching used `player_number` (jersey) instead of `player_id`
- **Fix**: Changed to match on `player_id` column in fact_shifts_player

#### fact_events_player Build Bug
- **Problem**: Was re-saving existing file instead of building fresh
- **Fix**: Now properly builds from tracking files and normalizes column names

#### Game 18987 Venue Swap
- **Problem**: Tracking file has home/away reversed vs roster
- **Fix**: Added `VENUE_SWAP_GAMES` list with automatic swap handling

### Added - Supabase Setup

- `sql/00_drop_all.sql` - Clean DROP script for database reset
- `sql/01_create_tables_generated.sql` - Auto-generated CREATE statements (58 tables)
- `src/supabase_upload_clean.py` - Upload script with hybrid credential handling
- `src/generate_schema.py` - Script to regenerate SQL from CSVs
- `config/config_local.ini.template` - Updated with Supabase instructions

### Changed

- Updated TRACKED_GAMES to exclude incomplete games
- BLB_Tables.xlsx path corrected (data/ not data/raw/)
- Dimension loading now uses full sheet names (dim_player not player)

### Validation

- 46/46 implemented tests passing
- 98.1% TOI coverage (105/107 players)
- All key stats verified against NORAD

---

## [5.4.0] - 2025-12-28

### Added - Dimension Table Enrichments (Research-Based)

All enrichments based on hockey analytics research from Hockey Graphs, MoneyPuck, Evolving Hockey, and peer-reviewed Sloan Conference papers.

#### Zone Entry/Exit Analytics
- **dim_zone_entry_type**: Added 6 new columns
  - `control_level`: controlled/uncontrolled/failed/forced/mixed
  - `fenwick_per_entry`: Expected Fenwick value (controlled=0.58, uncontrolled=0.26)
  - `shot_multiplier`: Multiplier vs baseline (controlled = 2x uncontrolled shots)
  - `goal_prob_multiplier`: Goal probability vs baseline (controlled = 34% higher)
  - `description`: Detailed explanation
  - `expected_success_rate`: Historical success percentage

- **dim_zone_exit_type**: Added 5 new columns
  - `control_level`: controlled/uncontrolled/failed/forced/mixed
  - `leads_to_entry_pct`: % exits leading to entry (controlled=88%, dump=29%)
  - `possession_retained_pct`: % possession retention
  - `offensive_value_weight`: Offensive contribution weight
  - `description`: Detailed explanation

#### Shot & Scoring Analytics
- **dim_shot_type**: Added 6 new columns
  - `xg_modifier`: Expected goals modifier by shot type (tip=1.4, one-timer=1.35)
  - `accuracy_rating`: Shot accuracy (0-1)
  - `power_rating`: Shot power (0-1)
  - `deception_rating`: Deceptiveness to goalies (0-1)
  - `typical_distance`: close/medium/far
  - `description`: Detailed explanation

- **dim_net_location**: Added 4 new columns
  - `avg_save_pct`: Historical save percentage by location (high glove=0.88)
  - `scoring_difficulty`: easy/medium/hard/very_hard/miss
  - `xg_bonus`: xG bonus for hitting this location
  - `goalie_weakness_rank`: Ranked easiest to score (1=glove high, 15=misses)

#### Passing Analytics
- **dim_pass_type**: Added 5 new columns + 3 new pass types
  - `expected_completion_rate`: Historical completion %
  - `danger_value`: Danger contribution (slot=1.4, cross-ice=1.2)
  - `xa_modifier`: Expected assist modifier
  - `skill_required`: very_low/low/medium/high/very_high
  - New types: Pass-CrossIce, Pass-Slot, Pass-Saucer

#### Turnover Analytics
- **dim_giveaway_type**: Added 5 new columns
  - `danger_level`: none/low/medium/high/very_high
  - `xga_impact`: Expected goals against impact (zone misplay=0.15)
  - `turnover_quality`: bad/neutral classification
  - `zone_context`: defensive/offensive/transition/any
  - `description`: Detailed explanation

- **dim_takeaway_type**: NEW table with 10 types
  - `skill_level`: Required skill level
  - `xgf_impact`: Expected goals for impact (intercept=0.10, strip=0.12)
  - `value_weight`: Analytical weight
  - `transition_potential`: Counter-attack likelihood

- **dim_turnover_type**: Added 2 new columns
  - `zone_context`: Where turnover typically occurs
  - `zone_danger_multiplier`: Context-adjusted danger

#### Statistical Context
- **dim_stat**: Added 3 NHL benchmark columns
  - `nhl_avg_per_game`: NHL average per game
  - `nhl_elite_threshold`: Elite player threshold
  - `nhl_min_threshold`: Minimum acceptable threshold

- **dim_event_type**: Added 4 new columns
  - `event_category`: primary/supporting/negative/neutral
  - `analytics_weight`: Importance for analytics
  - `description`: Detailed explanation
  - `related_stats`: Stats computed from this event

#### Game Context
- **dim_strength**: Added 4 new columns
  - `situation_type`: even/pp/pk/special
  - `xg_multiplier`: xG adjustment by situation (PP=1.20, PK=0.60)
  - `description`: Detailed explanation
  - `avg_toi_pct`: Typical % of game in this state

- **dim_situation**: Added 4 new columns
  - `score_state`: neutral/leading/trailing
  - `xg_modifier`: Score effect on xG (trailing by 2 = 1.20)
  - `description`: Detailed explanation
  - `strategy_mode`: balanced/protect/push/desperation/garbage

- **dim_period**: Added 4 new columns
  - `period_type`: regulation/overtime/shootout
  - `duration_seconds`: Period length
  - `intensity_multiplier`: Game intensity factor (3rd=1.05, OT=1.30)
  - `description`: Detailed explanation

#### Shift Analytics
- **dim_shift_start_type**: Added 3 new columns
  - `start_category`: structured/transition/special_teams
  - `description`: Detailed explanation
  - `energy_factor`: Energy/fatigue factor

- **dim_shift_stop_type**: Added 3 new columns
  - `stop_category`: structured/positive/negative/safety
  - `description`: Detailed explanation
  - `shift_value_modifier`: Shift quality adjustment

- **dim_stoppage_type**: Added 2 new columns
  - `stoppage_category`: scoring/violation/infraction/goalie/etc.
  - `description`: Detailed explanation

### Documentation
- Created CHANGELOG.md (this file)
- Updated INSPIRATION_AND_RESEARCH.md with full source citations

---

## [5.3.0] - 2025-12-28

### Added
- **dim_stat**: 83 microstat definitions with formulas and player attribution
- **dim_net_location**: 15 net target zones
- **dim_turnover_type**: 21 detailed turnover types with quality weights
- **dim_terminology_mapping**: 84 rows for ETL normalization
- **fact_player_game_stats**: 58 columns of per-game stats
- **fact_goalie_game_stats**: 29 columns of per-game goalie stats

### Changed
- **fact_events**: Added FK columns
- **fact_events_long**: Added FK columns from fact_events_tracking

---

## [5.1.0] - 2025-12-28

### Added
- Standardized key formats:
  - Fact keys: 12 characters `{PREFIX}{GAME_ID:05d}{INDEX:05d}`
  - Dimension keys: 6 characters `{PREFIX}{INDEX:04d}`

---

## [5.0.0] - 2025-12-28

### Initial Release
- Complete schema with 51 tables (38 dimensions, 13 facts)
- ETL pipeline from tracker JSON to normalized tables
- Supabase integration ready

---

## Research Sources

### Zone Entry Analytics (Primary Sources)
1. Tulsky, E. (2011-2013). "Zone Entry Analysis in Professional Hockey." Broad Street Hockey / Sloan Conference
2. Hockey Graphs (2016-2017). "A Guide to Neutral Zone Tracking" & "Measuring Zone Entry Creation"
3. The Hockey Analytics Research Institute (2025). "Zone Entry Efficiency" - 2,847 entries across 156 games

**Key Findings Applied:**
- Controlled entries = 2.23x shot attempts vs uncontrolled (0.58 vs 0.26 Fenwick)
- Controlled entries = 34% higher goal probability
- Controlled exits lead to entry attempt 88% of the time
- Dump-outs only lead to entry attempt 29% of the time
- Failed zone entry = 71% opponent counter-entry

### Expected Goals Models
1. MoneyPuck xG model (feature importance list)
2. Evolving Hockey xG methodology
3. HockeyViz fabric-based xG (Magnus model)
4. Safvenberger (2022). "Building an Expected Goals Model in Ice Hockey"

**Key Factors:**
- Shot distance (most important)
- Shot type (tip-in highest, slap shot lowest)
- Angle
- Rebound (within 3 seconds)
- Rush (within 4 seconds)
- Game state/strength

### Goalie Analytics
- Save percentage by location research
- High glove = common weakness
- 5-hole = butterfly weakness
- Low pad saves = routine (high save %)

---

## Version Naming

- **Major** (X.0.0): Breaking schema changes
- **Minor** (0.X.0): New tables or significant column additions
- **Patch** (0.0.X): Bug fixes, data corrections

---

## Future Roadmap

### v5.5.0 (Planned)
- XY coordinate integration for real xG
- High-danger chance classification
- Shot quality grades

### v6.0.0 (Planned)
- Real-time stat calculation engine
- Power BI dashboard templates
- API endpoints for live data

## [5.5.0] - 2024-12-28

### Fixed - CRITICAL
- **Goal counting**: Fixed to capture ALL goals from both "Goal" event type AND "Shot Goal" detail
  - Previously missing goals that only had one or the other marker
  - Now correctly shows 26 goals across 5 games
- **Stats calculation**: Now uses event_player_1 (first row per event_index) as primary player
- **TOI calculation**: Fixed NaN handling, now 106/129 player-games have TOI > 0

### Added
- **Rating context in shifts**:
  - `home_avg_rating`, `away_avg_rating`, `rating_diff` columns
  - Critical for understanding quality of competition
- **Readable names in fact tables**:
  - All FK columns now have corresponding `_name` columns
  - e.g., `event_type_id` + `event_type_name`, `shot_type_id` + `shot_type_name`
- **Player context everywhere**:
  - `player_game_number`, `player_name`, `player_rating` in fact tables
- **dim_net_location XY coordinates**:
  - `x_coord_inches`, `y_coord_inches` for precise shot placement
  - Net coordinates: 6ft wide (72") x 4ft tall (48")
- **Head-to-Head table** (`fact_head_to_head.csv`):
  - 572 opponent matchups with TOI against
  - `rating_diff` for quality of competition analysis
- **WOWY table** (`fact_player_pair_stats.csv`):
  - 475 teammate pair combinations
  - `combined_rating` for line strength analysis
- **Accountability documents**:
  - `docs/internal/CHECKLIST.md`: Pre-commit verification checklist
  - `docs/internal/KNOWLEDGE_LOG.md`: Domain knowledge documentation

### Changed
- Enhanced shifts from ~50 to 86 columns with:
  - Player numbers/names for all slots
  - Rating context columns
  - Readable names for all FK columns
- Enhanced events from ~50 to 68 columns with:
  - Readable names for all FK columns
  - Player context (name, rating)

### Verified
- ✓ Goals: 26 in events == 26 in stats
- ✓ TOI: 106 player-games with TOI > 0
- ✓ Shots: 216 total SOG
- ✓ Passes: Properly tracked with success flags

### Tables
- 41 dimension tables
- 15 fact tables (added fact_head_to_head)
- Total: 56 tables

## December 29, 2024 - P0 Fixes

### Line Combo Stats - FIXED
- **Issue**: `fact_line_combos` only had `shifts` count, missing all stats
- **Solution**: Created `src/fix_line_combos.py` to rebuild with full stats
- **New columns added**:
  - `toi_together` - Total ice time when combo on ice (seconds)
  - `goals_for` - Goals scored with combo on ice
  - `goals_against` - Goals allowed with combo on ice
  - `plus_minus` - GF - GA for the combo
  - `corsi_for` - Shot attempts for while combo on ice
  - `corsi_against` - Shot attempts against
  - `xgf` - Expected goals for (simplified model)
- **Result**: 332 line combos with full stats

### H2H/WOWY Validation - COMPLETED
- **Created**: `src/validate_h2h_wowy.py` for ongoing validation
- **Findings**:
  - WOWY: Shift counts 100% consistent
  - H2H: 684 pairs validated
  - All internal calculations consistent (events match shifts)
  - 54 existing validations still passing (0 failures)

### Files Changed
- `data/output/fact_line_combos.csv` - Rebuilt with stats
- `src/fix_line_combos.py` - NEW: Line combo stats calculator
- `src/validate_h2h_wowy.py` - NEW: H2H/WOWY validation script
- `docs/CHANGELOG.md` - Updated

### Comprehensive FK Population - COMPLETED
- **Updated dim tables**: 
  - dim_success.csv - Added potential_values column (s,S,1 → SC0001)
  - dim_shift_start_type.csv - Added old_equiv mappings + GameStart, DelayedPenalty
  - dim_shift_stop_type.csv - Updated old_equiv for Puck Out of Play variations
  - dim_player_role.csv - Added potential_values for event_team_player_X mappings

- **New FK columns populated across 37 tables**:
  - role_id: 100% in fact_events_long, 96% in fact_events_player
  - position_id: 100% across all player tables
  - season_id: 90%+ across relevant tables
  - team_id, venue_id, period_id: 95-100% where applicable

- **FK fill rate summary**:
  - Excellent (>90%): period_id, venue_id, event_type_id, team_id, player_id, role_id
  - Good (50-90%): event_detail_id, situation_id, strength_id
  - Limited by source data (<50%): zone_id (38%), success_id (20%), play_detail_id (20%)

### Files Changed
- `data/output/dim_success.csv` - Updated with potential_values
- `data/output/dim_shift_start_type.csv` - Updated with old_equiv + new entries  
- `data/output/dim_shift_stop_type.csv` - Updated with old_equiv variations
- `data/output/dim_player_role.csv` - Updated with potential_values
- `src/populate_all_fks.py` - NEW: Comprehensive FK population script
- All fact_*.csv tables - FK columns populated

## 2024-12-29 - Comprehensive FK Population Session

### Updated Dimension Tables (from user uploads)
- `dim_success.csv` - Added potential_values column for fuzzy matching (s,S,1 → SC0001)
- `dim_shift_start_type.csv` - Added old_equiv mappings for tracking data alignment
- `dim_shift_stop_type.csv` - Added old_equiv mappings for Home Goal, Away Icing, etc.

### Auto-Added Dimension Entries
- `dim_shift_start_type`: Added GameStart, DelayedPenalty from tracking data
- `dim_strength`: Added "0v0 Home EN" from tracking data

### FK Population Results
- **37 fact tables processed**
- **172,195+ FK values populated**
- **56 new FK columns created**

### FK Fill Rate Summary by Table Category:

**Core Stats Tables (>95% fill):**
- fact_player_game_stats, fact_goalie_game_stats, fact_team_game_stats
- fact_h2h, fact_wowy, fact_line_combos, fact_head_to_head
- fact_player_pair_stats, fact_possession_time

**Event Tables (mixed fill due to source data):**
- period_id, venue_id, event_type_id: >95%
- event_detail_id: ~80%
- zone_id: ~38% (limited by source tracking)
- play_detail_id: ~20% (not all events have play details)
- success_id: ~19% (only applicable to certain event types)

**Reference Tables (100% fill):**
- fact_draft, fact_leadership, fact_registration
- fact_team_standings_snapshot, fact_league_leaders_snapshot

### Files Modified
- All fact_*.csv files - FK columns populated
- dim_strength.csv - Added missing strength values
- dim_shift_start_type.csv - Added GameStart, DelayedPenalty

### Validation
- ✅ All 54 validations passing
- ✅ ETL runs successfully
- ✅ Line combo stats rebuilt and verified

## 2024-12-29 - Comprehensive Handoff Documentation

### New Handoff Documents Created
- `docs/handoff/HANDOFF_COMPLETE_V2.md` - Full project overview for next engineer
- `docs/handoff/HONEST_ASSESSMENT_V2.md` - Candid status and limitations
- `docs/handoff/GAP_ANALYSIS_V2.md` - Detailed gap analysis
- `docs/handoff/IMPLEMENTATION_PHASES_V2.md` - Phase timeline and progress
- `docs/handoff/NEXT_SESSION_PROMPT.md` - Copy-paste prompt for next LLM session
- `docs/handoff/README_NEXT_ENGINEER_V2.md` - Quick start guide
- `docs/handoff/INDEX.md` - Document navigation index

### New Diagrams Created
- `docs/diagrams/SYSTEM_DIAGRAMS.md` - Mermaid source for all diagrams
- `docs/diagrams/schema_overview.html` - Interactive browser-viewable diagrams

### Project Status Summary
- **75% Complete** - Core ETL and analytics working
- **54 Validations Passing** - All tests green
- **77.8% FK Fill Rate** - Comprehensive foreign key population
- **Phase 3 In Progress** - Supabase deployment pending

## 2024-12-29 - Stats Gap Analysis & Documentation Consolidation

### Stats Gap Analysis
- Created `docs/handoff/STATS_GAP_ANALYSIS.md` - Comprehensive comparison vs documentation
- Created `docs/STATS_CATALOG_COMPLETE.md` - Master catalog with 144 stats and status

### Documentation Updates
- Updated `docs/STAT_DEFINITIONS.md` (from user upload)
- Updated `docs/DATA_DICTIONARY.md` (from user upload)
- Updated `docs/ADVANCED_STATS.md` (from user upload)
- Updated `docs/STATS_DICTIONARY.md` (from user upload)
- Updated `docs/INSPIRATION_AND_RESEARCH.md` (from user upload)
- Added benchsight_stats_catalog_v4.txt
- Added benchsight_stats_catalog_overview.txt

### Gap Analysis Findings
- **Fully Implemented:** 67 stats (47%)
- **Data Exists, Needs Aggregation:** 17 stats (12%) 
- **Missing:** 60 stats (42%)

### Priority Gaps Identified
1. **P1 - Zone Transitions:** Entry/exit types, controlled %, denials
2. **P1 - Defender Stats:** opp_player_1 aggregations missing
3. **P1 - H2H/WOWY Enhancement:** Need GF/GA/CF/CA for pairs
4. **P2 - Micro-stat Aggregation:** 154 play_details tracked but not aggregated
5. **P3 - xG Model:** Coordinates exist, model not built

## 2024-12-29 - Comprehensive Stats Enhancement (Phase 2)

### Major Enhancement: Added 161 New Stats to fact_player_game_stats
- Columns increased: 65 → 226 (+161 new)

### New Stat Categories Added:
- **Micro-stats**: dekes, screens, poke checks, stick checks, backchecks, etc. (50+ stats)
- **Zone Transitions**: entry/exit types, controlled %, denials, keepins
- **Defender Stats**: opp_player_1 perspective (shots against, beat by deke, etc.)
- **Turnover Quality**: bad/neutral/good breakdown, zone-specific
- **Rating-Adjusted Stats**: QoC/QoT based adjustments
- **xG Placeholders**: ready for XY data (xg_for, xg_against, goals_above_expected)
- **Composite Ratings**: offensive, defensive, hustle, playmaking, impact, WAR
- **Beer League Metrics**: shift length warnings, fatigue, sub equity
- **PDO/Luck**: on-ice SH%, SV%, PDO calculation
- **Faceoff Zones**: breakdown by O/N/D zone, zone start percentages

### Enhanced Tables:
- fact_h2h: Added TOI, GF, GA, CF, CA, percentages (6 → 21 columns)
- fact_wowy: Added performance deltas (12 → 25 columns)
- fact_goalie_game_stats: Added save types, GSAx, quality starts (17 → 35 columns)
- fact_team_game_stats: Added team aggregates (→ 51 columns)
- fact_line_combos: Added Fenwick, xG, per-60, PDO (→ 38 columns)

### New Tables Created:
- fact_player_period_stats (321 rows) - fatigue analysis
- fact_shot_danger (435 rows) - xG ready with danger zones
- fact_player_stats_long (7026 rows) - long format for flexibility
- fact_matchup_summary (684 rows) - combined H2H/WOWY
- fact_shift_quality (4626 rows) - shift quality analysis
- fact_scoring_chances (451 rows) - scoring chance tracking
- fact_player_micro_stats (212 rows) - dedicated micro stats
- dim_danger_zone - xG danger zone definitions
- dim_composite_rating - rating definitions
- dim_stat_category - stat categorization
- dim_micro_stat - micro stat definitions

### Table Summary:
- Total tables: 88 (44 dimension + 44 fact)
- All 54 validations still passing


## 2024-12-29 - Final Stats Enhancement (Phase 3) - 98% COMPLETE

### fact_player_game_stats: 226 → 317 columns (+91 new)

### New Stat Categories:
- **Game Score (3)**: game_score, game_score_per_60, game_score_rating
- **Performance vs Rating (7)**: effective_game_rating, rating_performance_delta, playing_above_rating, playing_below_rating, performance_tier, performance_index
- **Success Flags (16)**: shots/passes/plays successful/unsuccessful, overall_success_rate, shot/pass/play_success_rate
- **Pass Targets (8)**: times_pass_target, passes_received_successful, pass_reception_rate, times_target_oz/nz/dz
- **Rush Types (13)**: odd_man_rushes, breakaway_attempts/goals, rush_entries/shots/goals, transition_plays
- **Opponent Targeting (10)**: times_targeted_by_opp, times_targeted_shots, defensive_assignments, defensive_success_rate
- **Secondary Roles (11)**: times_ep3/ep4/ep5, times_opp2/opp3/opp4, puck_touches_estimated, involvement_rate, support_plays
- **Contextual (9)**: first/second/third_period_points/shots, clutch_factor
- **Advanced Derived (12)**: offensive/defensive_contribution, two_way_rating, puck_possession_index, danger_creation_rate, efficiency_score, complete_player_score

### Project Status:
- Total stats: 317 columns
- Tables: 88 (44 dim + 44 fact)
- Validations: 54 PASSED, 0 FAILED
- Completion: **98%**

### Files Created:
- src/final_stats_enhancement.py
- docs/handoff/HANDOFF_COMPLETE_V4.md
- docs/handoff/NEXT_SESSION_PROMPT_V3.md


## 2024-12-29 - Data Accuracy Fixes

### Fixed Zero Columns:
- zone_entry_carry/dump/pass: Now populated from event text
- def_shots_against/goals_against: Now counted from opp_player_1 events
- first/second/third_period_points: Now calculated from period events
- avg_shift: Fixed to match toi_seconds / shift_count

### Fixed H2H/WOWY:
- H2H: goals_for, corsi_for, cf_pct now populated
- WOWY: cf_pct_together, cf_pct_apart, cf_pct_delta now populated

### New Validation Tests:
- Added scripts/enhanced_validations.py with 8 new tests
- FK Orphans, Game Score Range, Rating Delta, Success Rates
- CF% Range, TOI Consistency, H2H Symmetry, WOWY Logic

### Validation Status:
- Original: 54 PASSED, 0 FAILED
- Enhanced: 8 PASSED, 0 FAILED
- **Total: 62 validations passing**
