# BenchSight QA Strategy

**Point-by-point QA plan for ETL, data integrity, and dashboard outputs**

Last Updated: 2026-01-21
Version: 2.00

---

## Goals

- Prevent double counting and duplicate records
- Ensure table relationships are consistent
- Catch data drift between raw inputs and derived outputs
- Provide repeatable checks after every ETL run

---

## QA Coverage by ETL Phase

### Phase 1: Raw Ingestion (BLB + Tracking)

**Checks:**
- Row counts match expected sheets/files
- Primary keys are unique (`dim_*` tables)
- Required columns exist and are non-null for key fields
- Tracking files loaded for every game requested

**Double-counting risks:**
- Duplicate events from re-imported tracking files
- Duplicate players in BLB sheets

**Actions:**
- Enforce uniqueness on `event_id`, `player_id`, `game_id`
- Validate one tracking file per game

---

### Phase 2: Core Fact Tables

**Checks:**
- `fact_events` is unique by `event_id`
- `fact_event_players` equals `fact_events` expanded by players (no unexpected fan-out)
- `fact_shifts` unique by `shift_id`
- `fact_shift_players` equals `fact_shifts` expanded by players

**Double-counting risks:**
- Event-player expansion multiplied by incorrect joins
- Shifts duplicated across period boundaries

**Actions:**
- Validate `fact_event_players` row count = sum of event player slots
- Validate `fact_shift_players` row count = sum of shift player slots

---

### Phase 3: Derived Event Tables (Shots, Goals, Rushes)

**Checks:**
- `fact_goals` count matches goal filter definition
- `fact_shots` + `fact_goals` reconcile with shot outcomes
- `fact_faceoffs` counts align with event type

**Double-counting risks:**
- Goals counted from shot rows instead of goal rows
- Events duplicated due to incorrect filters

**Actions:**
- Enforce goal rule: `event_type == 'Goal'` AND `event_detail == 'Goal_Scored'`
- Reconcile derived table counts back to `fact_events`

---

### Phase 4: Aggregations (Player, Team, Game)

**Checks:**
- Sum of player goals equals game goals
- Sum of team stats equals league totals
- Player stats reconcile to event-level tables

**Double-counting risks:**
- Aggregating from already-aggregated tables
- Incorrect group-by keys

**Actions:**
- Aggregate only from raw facts (`fact_events`, `fact_shifts`)
- Use QA tables to reconcile totals

---

### Phase 5: QA Tables and Validation

**Checks:**
- `qa_goal_verification` matches expected totals
- `qa_*` tables are present and populated
- Validation script passes for all tables

**Actions:**
- Run `./benchsight.sh etl validate` after every ETL
- Compare output counts to expected ranges

---

## QA Artifacts (Existing)

- QA tables: `qa_*` tables produced by ETL
- Validation script: `validate.py`
- Table verification docs: `docs/validated_tables/`

---

## Required QA Checks (Every ETL Run)

1. Run ETL
2. Run validation
3. Check QA tables for anomalies
4. Spot-check goals, shots, and penalties for at least 1 game
5. Confirm row counts for core tables

**Recommended QA Test Set (default):**
- Game ID: `18969` (single-game validation baseline)

---

## Optional Deep QA (Weekly)

- Reconcile player totals against raw event logs
- Validate no orphaned foreign keys
- Check null rates for critical fields
- Compare against previous season ranges

---

## Ownership and Review

**Primary:** ETL owner  
**Secondary:** Data QA reviewer (subagent or teammate)  
**Escalation:** Stop release if QA mismatches detected
