# 07 - The Data Model: 139 Tables Explained

**Learning Objectives:**
- Understand dimensional modeling (star schema)
- Know why there are 139 tables
- Navigate table categories effectively
- Understand key design decisions

---

## What is Dimensional Modeling?

Dimensional modeling organizes data into two types of tables:

### Dimension Tables (dim_*)
**What they are:** Lookup/reference tables that describe things
**Examples:** Players, teams, zones, periods
**Characteristics:**
- Relatively small (few rows)
- Change infrequently
- Used for filtering and grouping

### Fact Tables (fact_*)
**What they are:** Transactional tables that record events/measurements
**Examples:** Events, shifts, player stats
**Characteristics:**
- Can be very large (many rows)
- Change frequently (new games added)
- Contain foreign keys to dimensions

### Star Schema Visualization

```
                    ┌─────────────┐
                    │ dim_player  │
                    │ player_id   │
                    │ player_name │
                    │ position    │
                    └──────┬──────┘
                           │
    ┌─────────────┐        │        ┌─────────────┐
    │ dim_team    │        │        │ dim_schedule│
    │ team_id     ├────────┼────────┤ game_id     │
    │ team_name   │        │        │ game_date   │
    └─────────────┘        │        └─────────────┘
                           │
                    ┌──────┴──────┐
                    │ fact_events │ ← Central fact table
                    │ event_id    │
                    │ player_id   │   (FK to dim_player)
                    │ team_id     │   (FK to dim_team)
                    │ game_id     │   (FK to dim_schedule)
                    │ event_type  │
                    │ x_coord     │
                    │ y_coord     │
                    └─────────────┘
```

---

## Why 139 Tables?

The 139 tables serve different purposes and grains:

| Category | Count | Purpose |
|----------|-------|---------|
| **Dimension tables** | ~50 | Lookups and reference data |
| **Core fact tables** | ~15 | Events, shifts, primary stats |
| **Analytics tables** | ~50 | Pre-aggregated analytics |
| **Macro stats** | ~15 | Season/career summaries |
| **QA tables** | ~8 | Validation and debugging |

### Different Grains Require Different Tables

**Grain** = the level of detail in each row.

```
fact_events               → One row per event
fact_player_game_stats    → One row per player per game
fact_player_season_stats  → One row per player per season
fact_player_career_stats  → One row per player (career total)
```

Why not one table? Because queries have different needs:
- "What happened in game 19001?" → Use fact_events
- "How did player P001 do in game 19001?" → Use fact_player_game_stats
- "How did player P001 do this season?" → Use fact_player_season_stats

---

## Table Categories

### 1. Dimension Tables (dim_*)

**From BLB_Tables.xlsx (Phase 1):**
| Table | Rows | Purpose |
|-------|------|---------|
| dim_player | ~337 | Player master list |
| dim_team | ~26 | Team definitions |
| dim_schedule | ~567 | Game schedule |
| dim_season | ~10 | Season definitions |
| dim_league | ~3 | League info |
| dim_event_type | ~15 | Event type lookup |
| dim_event_detail | ~50 | Event detail lookup |

**Static Reference (Phase 5):**
| Table | Rows | Purpose |
|-------|------|---------|
| dim_period | 5 | 1st, 2nd, 3rd, OT, SO |
| dim_zone | 3 | O, N, D zones |
| dim_position | 4 | F, D, G, XTRA |
| dim_strength | 18 | EV, PP, PK, EN, etc. |
| dim_rating | 5 | 2-6 player rating scale |
| dim_danger_zone | 4 | High, Medium, Low, Perimeter |
| dim_shot_outcome | 5 | Scored, Saved, Blocked, Missed, Crossbar |
| dim_stat | 83 | All stat definitions |
| dim_stat_category | 13 | Stat groupings |
| dim_micro_stat | 22 | Screen, Tip, One-timer, etc. |
| dim_rink_zone | 267 | 200ft x 85ft grid |

**Dynamic (from tracking data):**
| Table | Purpose |
|-------|---------|
| dim_zone_entry_type | Types of zone entries |
| dim_zone_exit_type | Types of zone exits |
| dim_stoppage_type | Types of stoppages |
| dim_giveaway_type | Types of giveaways |
| dim_takeaway_type | Types of takeaways |

### 2. Core Fact Tables

| Table | Grain | Columns | Purpose |
|-------|-------|---------|---------|
| **fact_events** | event_id | ~50 | All game events |
| **fact_event_players** | (event_id, player) | ~40 | One row per player per event |
| **fact_shifts** | shift_id | ~30 | Player shift data |
| **fact_shift_players** | (shift_id, player) | ~20 | One row per player per shift |
| **fact_tracking** | tracking_key | ~25 | Unique tracking points |
| **fact_gameroster** | (game_id, player_id) | ~30 | Official roster + stats |

### 3. Player/Team Stats (Phase 6)

| Table | Grain | Columns | Purpose |
|-------|-------|---------|---------|
| **fact_player_game_stats** | (game_id, player_id) | **317** | Complete player stats per game |
| **fact_goalie_game_stats** | (game_id, player_id) | ~50 | Goalie stats per game |
| **fact_team_game_stats** | (game_id, team_id) | ~100 | Team totals per game |

### 4. Macro Stats (Phase 7)

| Table | Grain | Purpose |
|-------|-------|---------|
| fact_player_season_stats_basic | (player_id, season_id) | Official stats (from roster) |
| fact_player_season_stats | (player_id, season_id) | Advanced tracking stats |
| fact_player_career_stats_basic | player_id | Career official stats |
| fact_player_career_stats | player_id | Career advanced stats |
| fact_goalie_season_stats_basic | (player_id, season_id) | Goalie official |
| fact_goalie_season_stats | (player_id, season_id) | Goalie advanced |
| fact_goalie_career_stats | player_id | Goalie career |
| fact_team_season_stats | (team_id, season_id) | Team season totals |

### 5. Analytics Tables (Phases 8-10)

**Event Analytics:**
| Table | Purpose |
|-------|---------|
| fact_sequences | Event sequences (continuous action) |
| fact_plays | Possession sequences |
| fact_scoring_chances | High-danger events |
| fact_shot_danger | Shot danger analysis |
| fact_linked_events | Event causality (pass → shot) |
| fact_rush_events | Rush identification |
| fact_shot_chains | Sequences leading to shots |

**Shift Analytics:**
| Table | Purpose |
|-------|---------|
| fact_h2h | Head-to-head matchups |
| fact_wowy | With/without you analysis |
| fact_line_combos | Forward line combinations |
| fact_shift_quality | Shift quality scoring |
| fact_shift_quality_logical | Quality tiers |

**Other Analytics:**
| Table | Purpose |
|-------|---------|
| fact_player_period_stats | Period-by-period breakdown |
| fact_player_micro_stats | Micro-stat tracking |
| fact_player_qoc_summary | Quality of competition |
| fact_zone_entry_summary | Zone entry aggregation |
| fact_zone_exit_summary | Zone exit aggregation |
| fact_matchup_summary | Direct matchup stats |
| fact_special_teams_summary | PP/PK aggregation |

### 6. QA Tables

| Table | Purpose |
|-------|---------|
| qa_goal_accuracy | Goal count verification |
| qa_data_completeness | Missing data check |
| qa_scorer_comparison | Cross-verify calculations |
| qa_suspicious_stats | Flag anomalies |
| fact_suspicious_stats | Flagged records |
| fact_game_status | Game processing status |

---

## The 10 Most Important Tables

If you're new, focus on these first:

| # | Table | Why It Matters |
|---|-------|----------------|
| 1 | **dim_player** | Master list of all players |
| 2 | **dim_team** | Master list of all teams |
| 3 | **dim_schedule** | All games with dates/scores |
| 4 | **fact_events** | Every event in every game |
| 5 | **fact_shifts** | Every player shift |
| 6 | **fact_player_game_stats** | 317-column stats per game |
| 7 | **fact_gameroster** | Official roster + league stats |
| 8 | **fact_player_season_stats** | Season aggregates |
| 9 | **fact_h2h** | Head-to-head matchups |
| 10 | **qa_goal_accuracy** | Validation of goal counts |

---

## Key Design Decisions

### Decision 1: Pre-aggregated Tables

**Why not calculate on demand?**

```sql
-- Without pre-aggregation (slow):
SELECT
    player_id,
    COUNT(*) FILTER (WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored') as goals,
    SUM(CASE WHEN is_corsi_event THEN 1 ELSE 0 END) as corsi_for,
    -- ... 300+ more calculations
FROM fact_events
GROUP BY player_id, game_id;

-- With pre-aggregation (fast):
SELECT goals, corsi_for, ...
FROM fact_player_game_stats
WHERE player_id = 'P001';
```

**Tradeoff:**
- More storage (139 tables vs fewer)
- Faster queries (no complex calculations)
- Simpler dashboard code

### Decision 2: Basic vs Advanced Stats

Two versions of season/career stats:

| Table | Source | Purpose |
|-------|--------|---------|
| fact_player_season_stats_**basic** | fact_gameroster | Official league stats |
| fact_player_season_stats | fact_player_game_stats | Advanced tracking stats |

**Why separate?**
- Basic stats match official league records exactly
- Advanced stats may not match (different methodology)
- Users can choose which to trust

### Decision 3: Composite Keys

**Pattern:** `{entity_type}{game_id}{entity_id}`

Examples:
- `PG19001P001` - Player game key (player_id + game_id)
- `TG19001T001` - Team game key (team_id + game_id)
- `E19001_P2_0845_001` - Event key (game + period + time + sequence)

**Why?**
- Human-readable (can see what game/player)
- Sortable (keys sort by game then entity)
- Unique (guaranteed by format)

### Decision 4: Denormalization

**Normalized (textbook):**
```
fact_events: event_id, game_id, player_id, event_type_id
dim_event_type: event_type_id, event_type_name
```

**Denormalized (actual):**
```
fact_events: event_id, game_id, player_id, event_type, event_type_id
                                           ↑ Redundant but useful
```

**Why denormalized?**
- Fewer joins in queries
- Easier to debug CSVs
- Minor storage cost

---

## Table Relationships

### Primary Relationships

```
dim_player ←──────┐
                  │
dim_team ←────────┼──── fact_events
                  │
dim_schedule ←────┘


dim_player ←──────┐
                  │
dim_schedule ←────┼──── fact_player_game_stats
                  │
dim_team ←────────┘


fact_player_game_stats ──► fact_player_season_stats ──► fact_player_career_stats
         (aggregate)                (aggregate)
```

### Event Chain

```
fact_event_players  (one row per player per event)
        ↓
fact_events         (one row per event)
        ↓
fact_sequences      (groups of continuous events)
        ↓
fact_plays          (possession sequences)
```

### Stats Chain

```
fact_events + fact_shifts
        ↓
fact_player_game_stats    (317 columns per player per game)
        ↓
fact_player_season_stats  (aggregate per season)
        ↓
fact_player_career_stats  (aggregate career)
```

---

## Finding Tables

### By Name Pattern

| Pattern | Meaning | Example |
|---------|---------|---------|
| `dim_*` | Dimension (lookup) | dim_player |
| `fact_*` | Fact (transactional) | fact_events |
| `qa_*` | Quality assurance | qa_goal_accuracy |
| `*_basic` | Official stats | fact_player_season_stats_basic |
| `*_long` | Long format (unpivoted) | fact_player_stats_long |
| `*_wide` | Wide format | fact_player_xy_wide |
| `*_summary` | Pre-aggregated | fact_zone_entry_summary |

### By Use Case

| I need to... | Use table... |
|--------------|--------------|
| Look up a player | dim_player |
| Look up a game | dim_schedule |
| See all events in a game | fact_events |
| See player stats for a game | fact_player_game_stats |
| See season leaders | fact_player_season_stats |
| Compare two players | fact_h2h |
| Analyze line combos | fact_line_combos |
| Check data quality | qa_* tables |

---

## Key Takeaways

1. **139 tables serve different purposes and grains**
2. **Dimension tables** = lookups (small, stable)
3. **Fact tables** = measurements (large, growing)
4. **Pre-aggregation** trades storage for query speed
5. **Composite keys** (PG19001P001) are human-readable
6. **Start with the 10 most important tables**

---

**Next:** [08-critical-tables.md](08-critical-tables.md) - Deep dive into fact_events and fact_player_game_stats
