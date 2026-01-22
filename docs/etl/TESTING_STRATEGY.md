# BenchSight Testing Strategy

**Test plan for ETL, API, dashboard, and portal**

Last Updated: 2026-01-21
Version: 2.00

---

## Principles

- Test closest to the source of truth (raw facts first)
- Avoid duplicate aggregation in tests
- Run fast checks on every change, deeper checks weekly

---

## Test Layers

### 1) ETL Unit Tests (Fast)

**Scope:** Core calculations, filters, key utilities  
**Focus:** Prevent double counting and logic drift

**Examples:**
- Goal filter correctness
- Event-to-player expansion counts
- Shift parsing boundaries

---

### 2) ETL Integration Tests (Medium)

**Scope:** `run_etl.py` with limited games  
**Focus:** Output tables exist and are populated

**Run:**
- `./benchsight.sh etl run --games 18969`
- `./benchsight.sh etl validate`

---

### 3) Data Consistency Tests (Medium)

**Scope:** Reconciliations across tables  
**Focus:** Aggregates match event-level totals

**Examples:**
- Sum of player goals = game goals
- Team totals = sum of player totals
- No orphaned foreign keys

---

### 4) API Tests (Fast)

**Scope:** Endpoint contracts and status codes  
**Focus:** Core ETL endpoints and upload workflows

**Run:**
- `./benchsight.sh api test` (if available)

---

### 5) Dashboard Smoke Tests (Fast)

**Scope:** Key routes render and data loads  
**Focus:** Pages load under 2 seconds

**Run:**
- Manual spot checks for top pages
- Optional automated smoke tests (future)

---

## Recommended Test Cadence

**Every PR:**
- ETL validation (if ETL changes)
- API checks (if API changes)
- Dashboard smoke test (if UI changes)
- Docs link check (if docs change)

**Weekly:**
- Full ETL run on latest data
- Deep data consistency checks

---

## Subagent Review Pattern

**When to use:**
- ETL logic changes
- Aggregations and derived tables
- Any double-counting fixes

**Roles:**
- Primary agent: implements
- Subagent: reviews data integrity and edge cases
- Human: approves after QA confirmation

---

## Required Outputs (Per Change Type)

| Change Type | Required Checks |
|-------------|------------------|
| ETL logic | `etl run` + `etl validate` + QA table review |
| API | Endpoint response check + error handling |
| Dashboard | Smoke test on key pages |
| Docs | `./scripts/docs-check.sh` |
