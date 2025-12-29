# BenchSight CHANGELOG

All notable changes to the BenchSight schema and data model are documented here.

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
