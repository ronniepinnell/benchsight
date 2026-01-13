# dim_event_type - Validation Documentation

**Status:** ✅ VALIDATED  
**Date:** 2026-01-10  
**Reviewers:** Ronnie + Claude

---

## Table Overview

| Property | Value |
|----------|-------|
| **Table Name** | `dim_event_type` |
| **Type** | Dimension (Taxonomy) |
| **Description** | All possible event types that can occur in a game |
| **Purpose** | Classify events; defines Corsi/Fenwick inclusion; FK target for fact_events |
| **Source** | BLB_Tables.xlsx → dim_event_type sheet |
| **Source Module** | `src/models/dimensions.py` |
| **Logic** | One row per event type from taxonomy |
| **Grain** | One row = One event type |
| **Row Count** | 23 |
| **Column Count** | 7 |

---

## Column Documentation

| # | Column | Data Type | Type | Description | Source/Calculation | Non-Null | Status |
|---|--------|-----------|------|-------------|-------------------|----------|--------|
| 1 | event_type_id | TEXT | 🟡 PK | Primary key (ET####) | Generated sequence | 23 (100%) | ✅ Keep |
| 2 | event_type_code | TEXT | 🟢 Explicit | Event type code (used in tracking) | BLB_Tables | 23 (100%) | ✅ Keep |
| 3 | event_type_name | TEXT | 🟢 Explicit | Display name | BLB_Tables | 23 (100%) | ✅ Keep |
| 4 | event_category | TEXT | 🟢 Explicit | Category grouping | BLB_Tables | 23 (100%) | ✅ Keep |
| 5 | description | TEXT | 🟢 Explicit | Human-readable description | BLB_Tables | 23 (100%) | ✅ Keep |
| 6 | is_corsi | BOOL | 🟢 Explicit | Counts toward Corsi stat | BLB_Tables | 23 (100%) | ✅ Keep |
| 7 | is_fenwick | BOOL | 🟢 Explicit | Counts toward Fenwick stat | BLB_Tables | 23 (100%) | ✅ Keep |

---

## All Event Types

| ID | Code | Name | Category | is_corsi | is_fenwick |
|----|------|------|----------|----------|------------|
| ET0001 | Shot | Shot | offensive | ✅ | ✅ |
| ET0002 | Save | Save | goaltending | ❌ | ❌ |
| ET0003 | Pass | Pass | playmaking | ❌ | ❌ |
| ET0004 | Faceoff | Faceoff | faceoff | ❌ | ❌ |
| ET0005 | Turnover | Turnover | turnover | ❌ | ❌ |
| ET0006 | Zone_Entry_Exit | Zone Entry Exit | transition | ❌ | ❌ |
| ET0007 | Possession | Possession | possession | ❌ | ❌ |
| ET0008 | Penalty | Penalty | penalty | ❌ | ❌ |
| ET0009 | Hit | Hit | physical | ❌ | ❌ |
| ET0010 | Block | Block | defensive | ✅ | ❌ |
| ET0011 | Stoppage | Stoppage | stoppage | ❌ | ❌ |
| ET0012 | Goal | Goal | scoring | ✅ | ✅ |
| ET0013 | PenaltyShot_Shootout | Penalty Shot or Shootout | offensive | ❌ | ❌ |
| ET0014 | LoosePuck | Loose Puck | transition | ❌ | ❌ |
| ET0015 | Rebound | Rebound from Shot | goaltending | ❌ | ❌ |
| ET0016 | DeadIce | Deadice | time | ❌ | ❌ |
| ET0017 | Play | Play | other | ❌ | ❌ |
| ET0018 | Timeout | Clockstop | time | ❌ | ❌ |
| ET0019 | Intermission | Intermission | time | ❌ | ❌ |
| ET0020 | Clockstop | Clockstop | time | ❌ | ❌ |
| ET0021 | GameStart | Game Start | time | ❌ | ❌ |
| ET0022 | GameEnd | Game End | time | ❌ | ❌ |
| ET0023 | Penalty_Delayed | Delayed Penalty | penalty | ❌ | ❌ |

---

## Corsi vs Fenwick Definitions

| Metric | Formula | Events Included |
|--------|---------|-----------------|
| **Corsi** | All shot attempts | Shot, Goal, Block |
| **Fenwick** | Unblocked shot attempts | Shot, Goal |

---

## Validation Results

### Data Quality ✅

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Primary key unique | 23 | 23 | ✅ Pass |
| All codes unique | 23 | 23 | ✅ Pass |
| No nulls | 0 | 0 | ✅ Pass |

### Cross-Table Validation ✅

| Check | Result |
|-------|--------|
| All fact_events.event_type exist in dim | ✅ 20/20 found |
| Unused types in dim | 3 (Hit, Block, PenaltyShot_Shootout) - OK for future |

---

## Event Categories

| Category | Events | Count |
|----------|--------|-------|
| time | DeadIce, Timeout, Intermission, Clockstop, GameStart, GameEnd | 6 |
| offensive | Shot, PenaltyShot_Shootout | 2 |
| penalty | Penalty, Penalty_Delayed | 2 |
| transition | Zone_Entry_Exit, LoosePuck | 2 |
| goaltending | Save, Rebound | 2 |
| turnover | Turnover | 1 |
| playmaking | Pass | 1 |
| faceoff | Faceoff | 1 |
| possession | Possession | 1 |
| physical | Hit | 1 |
| defensive | Block | 1 |
| stoppage | Stoppage | 1 |
| scoring | Goal | 1 |
| other | Play | 1 |

---

## Issues Found

None ✅

---

## Sign-Off

| Reviewer | Date | Verdict |
|----------|------|---------|
| Ronnie | 2026-01-10 | ✅ Validated |
| Claude | 2026-01-10 | ✅ Validated |

**Notes:** Clean table. Source is BLB_Tables.xlsx. Corsi/Fenwick flags are correct.

---

**Next Table:** dim_event_detail
