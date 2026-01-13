# BenchSight Roadmap

**MVP → Commercial Implementation Plan**

Updated: 2026-01-12
Version: 24.4

---

## Overview

```
Phase 0 ──▶ Phase 0.5 ──▶ Phase 0.75 ──▶ Phase 1 ──▶ Phase 2 ──▶ Phase 3 ──▶ Phase 4 ──▶ Phase 5
Foundation  Validation   Stats Expand    MVP        Alpha       Beta      Commercial   Growth
  (Done)     (Done)      (Current)    (Wk 1-2)   (Wk 3-4)   (Wk 5-8)    (Wk 9-12)  (Ongoing)
```

### v28.3 Status Update (2026-01-12)
- **Phase 0.75 Stats Expand: 85% Complete**
  - ✓ Advanced goalie stats (39→128 columns)
  - ✓ Macro stats tables (8 new: basic + advanced tiers)
  - ✓ View layer (30 views for dashboard)
  - ✓ 139 ETL tables, validated
  - ☐ Performance optimization (vectorization)
  - ☐ base_etl.py refactoring

---

## ⚠️ Technical Debt Assessment (HONEST)

### What Works Well
| Aspect | Status | Notes |
|--------|--------|-------|
| Goal counting | ✅ Solid | Single source of truth, well documented |
| Validation framework | ✅ Good | Catches errors before propagation |
| Documentation | ✅ Good | CHANGELOG, TODO, HANDOFF maintained |
| Data output accuracy | ✅ Correct | Numbers verified, venue mapping works |
| Data model | ✅ Sound | Dimensional model is appropriate |

### What Will Cause Problems

#### 1. base_etl.py is a 4,400-line monster
```python
# Current state - NOT maintainable
def build_fact_shifts(...):     # 500+ lines
def build_fact_shift_players(...):  # 400+ lines
def build_fact_events(...):     # 300+ lines
```
**Impact:** Any bug fix requires reading thousands of lines. New developers will struggle.

**Solution:** Break into focused modules:
```
src/
├── calculations/
│   ├── corsi.py      # CF%, FF%, shot metrics
│   ├── ratings.py    # Player ratings, QoC, QoT
│   ├── goals.py      # Goal counting (single source)
│   └── time.py       # TOI, shift duration
├── builders/
│   ├── events.py     # fact_events builder
│   ├── shifts.py     # fact_shifts builder
│   └── players.py    # fact_shift_players builder
└── core/
    └── etl.py        # Orchestration only
```

#### 2. Performance is terrible
```python
# This pattern appears everywhere - SLOW
shifts.apply(lambda r: calc_team_ratings(r, cols, map), axis=1)

# iterrows() is the slowest pandas operation
for i, shift in shifts.iterrows():
    shift_ev = shift_events_map[shift['shift_id']]
```
**Impact:** 4 games = fine. 100 games = hours. Full season = unusable.

**Solution:** Vectorized operations:
```python
# Instead of apply with lambda
shifts['home_avg_rating'] = shifts[home_cols].apply(
    lambda row: row.map(rating_map).mean(), axis=1
)

# Use merge instead of iterrows + map
shifts = shifts.merge(events_agg, on='shift_id', how='left')
```

#### 3. Zero unit tests
**Impact:** No confidence in changes. Bugs discovered only after full ETL run.

**Solution:** Test critical calculations:
```python
# tests/test_goals.py
def test_goal_counting_excludes_shot_goal():
    events = pd.DataFrame({
        'event_type': ['Goal', 'Shot'],
        'event_detail': ['Goal_Scored', 'Shot_Goal']
    })
    assert count_goals(events) == 1

# tests/test_ratings.py
def test_competition_tier_elite():
    assert get_competition_tier(5.5) == 'TI01'
    
def test_competition_tier_boundaries():
    assert get_competition_tier(5.0) == 'TI01'
    assert get_competition_tier(4.99) == 'TI02'
```

#### 4. Magic numbers everywhere
```python
# Current - what do these mean?
if opp_rating >= 5.0:
    return 'TI01'
sp['expected_cf_pct'] = 50 + (sp['rating_differential'].fillna(0) * 5)
```
**Solution:** Config file with documented constants:
```python
# config/constants.py
class RatingThresholds:
    """Competition tier boundaries based on NORAD skill ratings."""
    ELITE = 5.0       # Top tier players
    ABOVE_AVG = 4.0   # Strong players
    AVERAGE = 3.0     # Middle tier
    BELOW_AVG = 2.0   # Developing players

class AnalyticsFormulas:
    """Coefficients for calculated metrics."""
    CF_PCT_BASELINE = 50        # Neutral CF%
    RATING_TO_CF_MULTIPLIER = 5 # Each rating point = 5% CF advantage
```

#### 5. Empty placeholder tables (19 tables with 0 rows)
```
fact_player_season_stats: 0 rows
fact_player_career_stats: 0 rows
fact_team_season_stats: 0 rows
fact_player_xy_long: 0 rows
... (15 more)
```
**Impact:** Confusing. Are they broken or just empty?

**Solution:** Either:
- Remove placeholders until needed
- Add `_placeholder` suffix
- Populate with real data

#### 6. Duplicate calculation logic
Goal counting appears in 4+ places:
- `base_etl.py` (fact_events)
- `base_etl.py` (fact_shifts plus/minus)
- `core_facts.py` (player_game_stats)
- `core_facts.py` (goalie_game_stats)

**Impact:** Rule change = hunt through entire codebase.

**Solution:** Single function, imported everywhere:
```python
# src/calculations/goals.py
def get_goals(events: pd.DataFrame) -> pd.DataFrame:
    """
    Extract goals from events.
    
    CRITICAL: This is the ONLY place goal logic should exist.
    Goals = event_type='Goal' AND event_detail='Goal_Scored'
    """
    return events[
        (events['event_type'] == 'Goal') & 
        (events['event_detail'] == 'Goal_Scored')
    ]
```

#### 7. No FK validation across all tables
We manually fixed `competition_tier_id`. There could be others lurking.

**Solution:** Automated FK check in validation:
```python
FK_RELATIONSHIPS = [
    ('fact_shift_players', 'competition_tier_id', 'dim_competition_tier', 'competition_tier_id'),
    ('fact_events', 'player_id', 'dim_player', 'player_id'),
    ('fact_shifts', 'game_id', 'dim_schedule', 'game_id'),
    # ... all relationships
]

def validate_fks():
    for fact, fk_col, dim, pk_col in FK_RELATIONSHIPS:
        fact_vals = set(load_table(fact)[fk_col].dropna())
        dim_vals = set(load_table(dim)[pk_col])
        orphans = fact_vals - dim_vals
        if orphans:
            raise ValueError(f"{fact}.{fk_col} has orphan values: {orphans}")
```

#### 8. No logging of intermediate steps
**Impact:** When data is wrong, no way to trace where it went bad.

**Solution:** Add debug logging:
```python
import logging
log = logging.getLogger(__name__)

def build_fact_shifts(events, shifts):
    log.info(f"Input: {len(events)} events, {len(shifts)} shifts")
    
    # After each major step
    log.debug(f"After goal attribution: {shifts['home_gf_all'].sum()} home goals")
    log.debug(f"After rating calc: {shifts['home_avg_rating'].mean():.2f} avg")
    
    log.info(f"Output: {len(shifts)} shifts with {len(shifts.columns)} columns")
```

---

## Refactoring Roadmap

### Phase R1: Critical Fixes (Before scaling)
| Task | Priority | Effort | Impact |
|------|----------|--------|--------|
| Extract goal counting to single function | 🔴 High | 2 hrs | Prevents bugs |
| Add FK validation to validate_tables.py | 🔴 High | 2 hrs | Catches orphans |
| Create constants.py for magic numbers | 🔴 High | 1 hr | Self-documenting |
| Remove or mark placeholder tables | 🟡 Med | 1 hr | Reduces confusion |

### Phase R2: Performance (Before 20+ games)
| Task | Priority | Effort | Impact |
|------|----------|--------|--------|
| Replace iterrows with vectorized ops | 🔴 High | 8 hrs | 10x+ speedup |
| Replace apply(lambda) with vectorized | 🔴 High | 4 hrs | 5x speedup |
| Add incremental processing flag | 🟡 Med | 4 hrs | Process only new games |
| Profile ETL to find bottlenecks | 🟡 Med | 2 hrs | Target optimization |

### Phase R3: Maintainability (Before other developers)
| Task | Priority | Effort | Impact |
|------|----------|--------|--------|
| Split base_etl.py into modules | 🟡 Med | 8 hrs | Readable code |
| Add unit tests for calculations | 🟡 Med | 8 hrs | Confidence in changes |
| Add integration tests | 🟡 Med | 4 hrs | Catch regressions |
| Add debug logging | 🟢 Low | 2 hrs | Easier debugging |

### Phase R4: Future-Proofing
| Task | Priority | Effort | Impact |
|------|----------|--------|--------|
| Add type hints throughout | 🟢 Low | 4 hrs | IDE support, docs |
| Create ETL pipeline abstraction | 🟢 Low | 8 hrs | Easier extensions |
| Add data lineage tracking | 🟢 Low | 4 hrs | Audit trail |

---

## Phase 0: Foundation ✓
**Status: COMPLETE**  
**Goal:** Clean ETL that populates Supabase reliably

### Deliverables
| Item | Status | Notes |
|------|--------|-------|
| base_etl.py | ✓ | Main ETL (52 tables) |
| Table modules | ✓ | dimension_tables, core_facts, etc. |
| validate_tables.py | ✓ | Data integrity checks |
| Clean documentation | ✓ | 20+ docs |
| Archive old code | ✓ | Moved to `archive/` |

### Current Output
- **120 tables** generated
- **89,120 total rows**
- **50 dimension tables**, **58 fact tables**
- **4 games** tracked (17 goals verified)

---

## Phase 0.5: Data Validation ← CURRENT
**Status: MOSTLY COMPLETE**  
**Goal:** Verify all calculations are accurate

### Completed
| Table | Status | Notes |
|-------|--------|-------|
| fact_events | ✅ | 129 columns, 43 context cols, 29 flags |
| fact_shifts | ✅ | 137 columns, team-specific events |
| fact_shift_players | ✅ | 86 columns, venue mapping fixed |
| fact_event_players | ✅ | 140 columns validated |
| fact_player_game_stats | ✅ | 107 rows, 70 columns |
| fact_goalie_game_stats | ✅ | 8 rows (1 warning) |

### Remaining
| Task | Status |
|------|--------|
| Review is_high_danger flag | ⏳ |
| Review is_scoring_chance flag | ⏳ |
| Review is_highlight flag | ⏳ |
| Taxonomy dimension sync (117 values) | ⏳ |

### Success Criteria
- [x] All Tier 1 tables validated
- [x] Key metrics match noradhockey.com (17 goals)
- [x] Venue mapping verified for all stat columns
- [ ] 3 remaining flags verified
- [ ] Automated FK checks added

---

## Phase 0.75: Stats Expansion ← NEXT
**Status: NOT STARTED**  
**Goal:** Comprehensive player/goalie stats before building dashboard

### Why This Phase
Building a dashboard on incomplete stats means rebuilding later. Better to have comprehensive data first.

### fact_player_game_stats: 70 → 200+ columns

**Tier 1 - Core Advanced (MUST HAVE for dashboard):**
| Category | Columns | Source |
|----------|---------|--------|
| Fenwick | fenwick_for, fenwick_against, ff_pct | fact_shift_players.ff/fa |
| PDO | pdo, on_ice_sh_pct, on_ice_sv_pct | Calculated from on-ice events |
| Quality | qoc_rating, qot_rating | fact_shift_players averages |
| Danger | scoring_chances, high_danger_chances | fact_events is_scoring_chance |
| Plus/Minus | plus_minus_total, plus_minus_ev | fact_shift_players gf/ga |

**Tier 2 - Zone Analysis (HIGH VALUE):**
| Category | Columns | Source |
|----------|---------|--------|
| Zone Entries | zone_entries_controlled, zone_entry_control_pct | fact_events is_controlled |
| Zone Exits | zone_exits_controlled, zone_exit_control_pct | fact_events is_controlled |
| Entry Types | zone_entry_carry, zone_entry_pass, zone_entry_dump | fact_events event_detail_2 |
| Exit Types | zone_exit_carry, zone_exit_pass, zone_exit_clear | fact_events event_detail_2 |
| Zone Starts | zone_starts_oz_pct, zone_starts_dz_pct | fact_shift_players start_zone |
| FO by Zone | fo_wins_oz, fo_wins_nz, fo_wins_dz + losses + pct | fact_events zone |

**Tier 3 - Situational (NICE TO HAVE):**
| Category | Columns | Source |
|----------|---------|--------|
| Period Splits | first/second/third_period_points, shots | fact_events period |
| Score State | goals_leading, goals_trailing, goals_tied | fact_events game_state |
| Rush/Transition | odd_man_rushes, breakaway_goals, rush_entries | fact_events is_rush |
| Turnover Zone | turnovers_oz, turnovers_nz, turnovers_dz | fact_events zone |

**Tier 4 - Micro Stats (FROM TRACKER DATA):**
| Category | Columns | Source |
|----------|---------|--------|
| Drives | drives_middle, drives_wide, drives_corner + success | play_detail_2 |
| Net Front | crash_net, screens, front_of_net | play_detail_2 |
| Puck Battles | puck_battles, puck_battle_wins, retrievals | play_detail |
| Support | cycle_plays, reverse_passes, quick_ups | play_detail |

### fact_goalie_game_stats: 17 → 30+ columns

| Category | Columns | Source |
|----------|---------|--------|
| Core Missing | toi_seconds, empty_net_ga, season_id | fact_events/shifts |
| Save Location | saves_left_pad, saves_right_pad | fact_events event_detail_2 |
| Quality | high_danger_save_pct, expected_save_pct | fact_events is_high_danger |
| Advanced | goals_saved_above_expected (GSAx) | Calculated |
| Game Quality | quality_starts, really_bad_starts | Calculated from sv% |

### Missing Tables

| Table | Description | Priority |
|-------|-------------|----------|
| fact_team_standings | W-L-T, points, streaks | 🔴 HIGH |
| dim_game_state | Score differential states | 🟡 MED |
| dim_time_bucket | Game time periods | 🟡 MED |
| qa_data_completeness | Data quality metrics | 🟢 LOW |
| qa_goal_accuracy | Goal verification | 🟢 LOW |

### Success Criteria
- [ ] fact_player_game_stats has 150+ columns
- [ ] fact_goalie_game_stats has 25+ columns
- [ ] fact_team_standings exists with correct records
- [ ] All new columns documented in DATA_DICTIONARY

---

## Phase 1: MVP
**Status: NOT STARTED**  
**Timeline: Week 1-2**  
**Goal:** Working system end-to-end

### Prerequisites (from Refactoring)
- [ ] Extract goal counting to single function
- [ ] Add FK validation
- [ ] Create constants.py

### Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Tracker   │────▶│   Supabase  │────▶│   Python    │────▶│  Dashboard  │
│   (Local)   │     │    (Raw)    │     │    ETL      │     │  (Static)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Tasks
| Task | Description | Status |
|------|-------------|--------|
| Create `raw_events` table | Mirror tracker export | ☐ |
| Create `raw_shifts` table | Mirror tracker export | ☐ |
| Tracker "Publish to Supabase" | Export directly to DB | ☐ |
| ETL `--source supabase` flag | Read from Supabase | ☐ |
| Basic dashboard HTML | Query fact tables | ☐ |

### Success Criteria
- [ ] Track a game → Publish → Run ETL → See stats
- [ ] Under 5 minutes end-to-end

---

## Phase 2: Alpha
**Status: NOT STARTED**  
**Timeline: Week 3-4**  
**Goal:** Deployable, shareable prototype

### Prerequisites (from Refactoring)
- [ ] Performance optimizations (vectorized ops)
- [ ] Unit tests for critical calculations

### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    benchsight.app (Vercel)                      │
├─────────────────────────────────────────────────────────────────┤
│  /dashboard        │  /tracker           │  /admin              │
│  Public stats      │  Password protected │  Password protected  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │    Supabase     │
                    │  + Railway ETL  │
                    └─────────────────┘
```

### Tasks
| Task | Description | Status |
|------|-------------|--------|
| Deploy to Vercel | Host frontend | ☐ |
| Deploy ETL to Railway | API endpoint | ☐ |
| Domain setup | benchsight.app | ☐ |
| Supabase Auth | Email/password | ☐ |
| Basic roles | admin, viewer | ☐ |
| Admin "Run ETL" button | Trigger Railway | ☐ |

### Infrastructure Cost
| Service | Cost |
|---------|------|
| Vercel | $0 (free tier) |
| Railway | $5/mo |
| Domain | $12/yr |
| **Total** | **~$6/mo** |

---

## Phase 3: Beta
**Status: NOT STARTED**  
**Timeline: Week 5-8**  
**Goal:** Multi-user, polished, feedback-ready

### Prerequisites (from Refactoring)
- [ ] Split base_etl.py into modules
- [ ] Add integration tests
- [ ] Add debug logging

### User Roles
| Role | Permissions |
|------|-------------|
| `admin` | Everything |
| `scorer` | Track games, publish |
| `team_manager` | View own team |
| `viewer` | View public stats |

### Features
| Feature | Description | Status |
|---------|-------------|--------|
| User management | Invite, roles, disable | ☐ |
| Game management | Schedule, assign scorers | ☐ |
| Player profiles | Career stats, trends | ☐ |
| Team pages | Roster, stats | ☐ |
| Leaderboards | Goals, assists, etc. | ☐ |
| Charts | Recharts visualizations | ☐ |
| Auto-save tracker | Real-time sync | ☐ |

---

## Phase 4: Commercial
**Status: NOT STARTED**  
**Timeline: Week 9-12**  
**Goal:** Ready for paying customers

### Multi-Tenancy
```
┌─────────────────────────────────────────────────────────────────┐
│                      BenchSight Platform                         │
├─────────────────────────────────────────────────────────────────┤
│  NORAD League     │  League A          │  League B              │
│  (isolated)       │  (isolated)        │  (isolated)            │
└─────────────────────────────────────────────────────────────────┘
```

### Pricing Model
| Tier | Price | Includes |
|------|-------|----------|
| **Free** | $0 | 1 season, 10 games, 2 users |
| **Basic** | $19/mo | 2 seasons, 50 games, 10 users |
| **Pro** | $49/mo | Unlimited |
| **Enterprise** | Custom | Multi-league, API |

### Tasks
| Task | Description | Status |
|------|-------------|--------|
| Tenant isolation | Row-level security | ☐ |
| Self-service signup | Onboarding flow | ☐ |
| Stripe integration | Billing | ☐ |
| Error monitoring | Sentry | ☐ |
| Mobile responsive | Works on phones | ☐ |

---

## Phase 5: Growth
**Status: FUTURE**  
**Timeline: Ongoing**  
**Goal:** Scale and expand

### Feature Roadmap
| Feature | Value |
|---------|-------|
| Mobile app | Native iOS/Android tracker |
| Video integration | LiveBarn, GameSheet sync |
| AI insights | "Player X is underperforming..." |
| API access | Teams build own tools |
| White-label | Leagues brand as their own |

---

## Tech Stack Summary

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React, Tailwind |
| Auth | Supabase Auth |
| Database | Supabase (PostgreSQL) |
| ETL | Python (pandas, numpy) |
| Hosting | Vercel (frontend), Railway (backend) |
| Payments | Stripe |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ETL too slow at scale | High | High | Vectorize before 20+ games |
| Calculation bugs | Medium | High | Add unit tests |
| Code unmaintainable | High | Medium | Refactor before Phase 2 |
| Supabase limits | Low | Medium | Monitor usage |
| User adoption | Medium | Medium | Start with NORAD feedback |

---

## Future Improvements (Wish List)

### Inspiration Sources
Key hockey analytics sites for reference:
- **MoneyPuck** (moneypuck.com) - xG models, shot maps, player cards
- **Natural Stat Trick** (naturalstattrick.com) - On-ice stats, 5v5 analysis
- **Evolving Hockey** (evolving-hockey.com) - GAR, RAPM, xG methodology
- **Hockey Reference** (hockey-reference.com) - Historical data, advanced stats
- **NHL EDGE** (nhl.com/edge) - Tracking data, speed, distance
- **PuckPedia** (puckpedia.com) - Salary, contracts, stats glossary

### Advanced Metrics to Implement (from research)

**Expected Goals (xG) Model:**
- Shot location (distance, angle)
- Shot type (wrist, slap, backhand, tip)
- Shot context (rush, rebound, one-timer)
- Shooter/goalie quality adjustment
- Output: ixG (individual), xGF/xGA (on-ice)

**Goals Above Replacement (GAR):**
- Even strength offense/defense
- Power play contribution
- Penalty differential
- Faceoff impact
- Output: Single WAR-like number

**RAPM (Regularized Adjusted Plus-Minus):**
- Isolate player impact from teammates
- Account for competition quality
- Score effects adjustment
- Zone start adjustment

**PDO/Luck Metrics:**
- On-ice shooting % (OiSH%)
- On-ice save % (OiSV%)
- PDO = OiSH% + OiSV% (expected ~100)
- dFSh%, dFSv% (differential from expected)

**Goalie Advanced:**
- GSAx (Goals Saved Above Expected)
- High/Medium/Low danger save %
- Rebound control rate
- Freeze rate
- Post-shot recovery time

### Analytics Enhancements
- Expected goals (xG) model based on shot location
- Heat maps from XY coordinate data
- Player comparison radar charts
- Game flow visualizations (momentum charts)
- Shift-by-shift breakdown views
- Line combination analysis
- Zone time possession tracking
- Scoring chance quality grades

### Data Quality
- Automated anomaly detection (unusual stat patterns)
- Cross-game consistency checks
- Historical trend analysis
- Data completeness scoring per game
- Tracker error flagging (impossible events)

### Developer Experience
- CLI tool for common operations (`benchsight etl --game 18969`)
- Pre-commit hooks for code quality
- CI/CD pipeline with test requirements
- Docker container for reproducible environment
- Auto-generated API documentation
- Database migration tooling

### Performance
- Database indexing strategy
- Query result caching
- Lazy loading for large tables
- Parallel processing for multi-game ETL
- Incremental ETL (process only changed games)
- Connection pooling for Supabase

### Tracker Improvements
- Undo/redo functionality
- Keyboard shortcuts for common events
- Event validation warnings (e.g., goal without SOG)
- Auto-suggest player based on position
- Offline mode with sync
- Tablet-optimized layout

### Dashboard Features
- Custom date range filtering
- Export to PDF/Excel
- Shareable links for specific views
- Compare two players side-by-side
- Team vs team historical matchups
- Season-over-season comparisons

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-12 | Document technical debt honestly | Future me needs to know |
| 2026-01-12 | Add refactoring roadmap | Technical debt will block scaling |
| 2026-01-12 | Prioritize vectorization before Phase 2 | Performance critical for growth |
| 2026-01-10 | Keep Python ETL | Works, no rewrite needed |
| 2026-01-10 | Supabase for DB | Auth + DB in one, generous free tier |
| 2026-01-10 | Railway for backend | Simple Python hosting, $5/mo |
| 2026-01-10 | CSV intermediate | Allows validation before upload |

---

*Last updated: 2026-01-12*
