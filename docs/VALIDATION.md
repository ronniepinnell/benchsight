# BenchSight Data Validation Plan

Last Updated: 2026-01-10

## Overview

This document defines the validation process for verifying data accuracy across all 131 BenchSight tables. Validation happens in phases: automated checks, then manual table-by-table QC with reference to official NORAD data.

---

## Phase 1: Automated Validation (Already Implemented)

Run with: `python validate.py`

### Checks Performed

| Check | Description | Expected |
|-------|-------------|----------|
| Table Count | Total tables generated | 131 |
| Dim Tables | Dimension tables | 55 |
| Fact Tables | Fact tables | 71 |
| Goal Count | Goals via event_type='Goal' AND event_detail='Goal_Scored' | Matches noradhockey.com |
| Required Columns | Foreign keys and mandatory fields present | All present |
| Referential Integrity | FK values exist in dimension tables | No orphans |

---

## Phase 2: Manual Table-by-Table QC

### Priority Order

**Tier 1 - Core Reference Data (Validate First)**
1. `dim_player` - Player master data
2. `dim_team` - Team master data  
3. `dim_season` - Season definitions
4. `dim_game` - Game master data

**Tier 2 - Event Foundation**
5. `fact_events` - Raw event data (source of truth)
6. `dim_event_type` - Event type codes
7. `dim_event_detail` - Event detail codes

**Tier 3 - Aggregated Stats**
8. `fact_player_season_stats` - Player season totals
9. `fact_team_season_stats` - Team season totals
10. `fact_gameroster` - Game-level player stats

**Tier 4 - Derived Analytics**
11-131. All other tables

### QC Checklist Per Table

```
□ Row count matches expected
□ Primary key unique (no duplicates)
□ Foreign keys valid (referential integrity)
□ Nulls only where expected
□ Data types correct
□ Sample values spot-checked against source
□ Aggregations verified (for fact tables)
```

---

## Phase 3: Cross-Validation Queries

### Goals Validation
```sql
-- Count goals from fact_events
SELECT COUNT(*) FROM fact_events 
WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored';

-- Should match sum from fact_player_season_stats
SELECT SUM(goals) FROM fact_player_season_stats;

-- Should match official NORAD totals
```

### Player Count Validation
```sql
-- Unique players with events
SELECT COUNT(DISTINCT event_player_1) FROM fact_events;

-- Should match dim_player
SELECT COUNT(*) FROM dim_player;
```

### Game Count Validation
```sql
-- Games with events
SELECT COUNT(DISTINCT game_id) FROM fact_events;

-- Should match dim_game
SELECT COUNT(*) FROM dim_game;
```

---

## Phase 4: Source Comparison

### Official Sources
- **noradhockey.com** - Official league stats (scoresheets, standings)
- **Raw tracking data** - Excel files in `data/raw/`

### Comparison Points
1. Season standings match
2. Player point leaders match
3. Goalie stats match
4. Game scores match

---

## Table-Specific Validation Notes

### dim_player
- [ ] Player names match registration
- [ ] Birth years reasonable (1960-2010)
- [ ] Position codes valid (F/D/G)

### dim_team
- [ ] All NORAD teams present
- [ ] Team names standardized

### fact_events
- [ ] No orphan game_ids
- [ ] Event timestamps sequential within games
- [ ] Event types from valid set

### fact_gameroster
- [ ] Player count per game reasonable (10-25)
- [ ] Goals/assists match fact_events
- [ ] No duplicate player-game entries

### fact_registration
- [ ] Email formats valid
- [ ] Season IDs valid
- [ ] No duplicate registrations

---

## Validation Status Tracker

| Table | Status | Issues | Verified By | Date |
|-------|--------|--------|-------------|------|
| dim_player | ⏳ Pending | | | |
| dim_team | ⏳ Pending | | | |
| dim_season | ⏳ Pending | | | |
| ... | | | | |

**Status Key:**
- ⏳ Pending
- 🔄 In Progress  
- ✅ Validated
- ❌ Issues Found

---

## How to Validate a Table (Workflow)

1. **Load table** in Supabase or via SQL
2. **Run standard checks:**
   ```sql
   -- Row count
   SELECT COUNT(*) FROM {table};
   
   -- Check for nulls in PK
   SELECT COUNT(*) FROM {table} WHERE {pk_column} IS NULL;
   
   -- Check for duplicates
   SELECT {pk_column}, COUNT(*) 
   FROM {table} 
   GROUP BY {pk_column} 
   HAVING COUNT(*) > 1;
   ```
3. **Spot check** 5-10 random rows against source
4. **Document** findings in status tracker
5. **Flag issues** for ETL fixes if needed

---

## Issue Reporting Template

When issues are found:

```
Table: {table_name}
Issue Type: [Data Error / Missing Data / Duplicate / Referential Integrity]
Description: {what's wrong}
Sample Rows: {row IDs or examples}
Expected: {what it should be}
Actual: {what we found}
Source Reference: {link to official data}
Priority: [High/Medium/Low]
```
