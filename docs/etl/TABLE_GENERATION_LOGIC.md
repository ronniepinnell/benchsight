# Table Generation Logic

**Documentation of how each table is generated, including business logic and dependencies.**

Last Updated: 2026-01-22

---

## Overview

This document describes the generation logic for each table in the BenchSight system, including:
- Source data
- Business rules
- Calculation formulas
- Dependencies

---

## Table Categories

### Dimension Tables (dim_*)

**Purpose:** Reference data for foreign keys

**Generation:** Static data from BLB tables or extracted from fact tables

**Examples:**
- `dim_player` - From BLB_Tables.xlsx
- `dim_team` - From BLB_Tables.xlsx
- `dim_zone` - Static reference data

### Fact Tables (fact_*)

**Purpose:** Transactional/analytical data

**Generation:** Aggregated from events, shifts, or other fact tables

**Examples:**
- `fact_events` - From tracking data
- `fact_player_game_stats` - Aggregated from events
- `fact_h2h` - Calculated from shifts

### QA Tables (qa_*)

**Purpose:** Quality assurance and validation

**Generation:** Validation checks on other tables

**Examples:**
- `qa_game_status` - Game processing status
- `qa_table_counts` - Row counts per table

---

## Key Table Generation Logic

### fact_events

**Source:** `{game_id}_tracking.xlsx` Events sheet

**Generation:**
1. Load events from Excel
2. Normalize column names
3. Add derived columns (time, zone, etc.)
4. Generate `event_id` key
5. Save to CSV

**Business Rules:**
- Each event has unique `event_id`
- `event_type` and `event_detail` required
- Goal counting: `event_type == 'Goal' AND event_detail == 'Goal_Scored'`

**Dependencies:** None

---

### fact_player_game_stats

**Source:** `fact_events`, `fact_event_players`

**Generation:**
1. Filter events by `player_id`
2. Group by `player_id`, `game_id`
3. Calculate stats:
   - Goals: Count where `event_type == 'Goal' AND event_detail == 'Goal_Scored'`
   - Assists: Count where `play_details1` or `play_details2` contains 'Assist'
   - Shots: Count where `event_type == 'Shot'`
4. Generate `player_game_key`
5. Save to CSV

**Business Rules:**
- Only count stats for `player_role == 'event_player_1'`
- Micro-stats counted once per linked event

**Dependencies:** Phase 1 (events), Phase 3B (dim_player)

---

### fact_h2h

**Source:** `fact_shifts`, `fact_shift_players`

**Generation:**
1. Load shifts with players
2. Identify player matchups (same shift, opposite teams)
3. Calculate head-to-head statistics
4. Generate `h2h_key`
5. Save to CSV

**Business Rules:**
- Only count shifts where both players on ice
- Calculate CF%, xGF%, etc. for matchup

**Dependencies:** Phase 1 (shifts), Phase 3B (dim_player)

---

## Calculation Formulas

### Goals

```python
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
goals = df[GOAL_FILTER].groupby('player_id').size()
```

### Assists

```python
assist_filter = (
    df['play_details1'].str.contains('Assist', na=False) |
    df['play_details2'].str.contains('Assist', na=False)
)
assists = df[assist_filter].groupby('player_id').size()
```

### Corsi

```python
corsi_events = ['Shot', 'Missed', 'Blocked']
corsi = df[df['event_type'].isin(corsi_events)].groupby('player_id').size()
```

---

## Related Documentation

- [Table Registry](TABLE_REGISTRY.md) - Complete table metadata
- [ETL Phase Flow](../etl/ETL_PHASE_FLOW.md) - Phase overview
