# BenchSight Validation Session Template

**For each table we validate together, we'll document:**

---

## Table Overview

| Property | Value |
|----------|-------|
| **Table Name** | `table_name` |
| **Description** | What this table contains |
| **Purpose** | Why it exists / business question it answers |
| **Source** | Where the data comes from |
| **Source Module** | Which ETL code creates it |
| **Logic** | How rows are generated |
| **Grain** | What each row represents |
| **Row Count** | Number of rows |
| **Column Count** | Number of columns |

---

## Column Documentation

| Column | Data Type | Description | Context/Mapping | Calculation/Formula | Type | Non-Null | Null % |
|--------|-----------|-------------|-----------------|---------------------|------|----------|--------|
| col_1 | TEXT | Description | Where from | How calculated | Explicit/Calculated/Derived/FK | 100 | 0% |

### Column Type Legend

| Type | Badge | Meaning |
|------|-------|---------|
| **Explicit** | 🟢 | Directly from raw source data (BLB, tracking file) |
| **Calculated** | 🔵 | Computed via formula from other columns |
| **Derived** | 🟡 | Generated key, aggregate, or transformation |
| **FK** | 🟣 | Foreign key lookup to dimension table |

---

## Validation Checks

### Data Quality
| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Row count | X | Y | ✅/❌ |
| No duplicate keys | 0 | 0 | ✅/❌ |
| No unexpected nulls | 0 | 0 | ✅/❌ |

### Calculation Verification
| Calculation | Formula | Sample Check | Status |
|-------------|---------|--------------|--------|
| points | goals + assists | Row 1: 2 = 1 + 1 | ✅/❌ |

### Cross-Table Consistency
| Check | Source | Target | Match |
|-------|--------|--------|-------|
| Goal count | dim_schedule | fact_events | ✅/❌ |

---

## Sample Data

First 5 rows of key columns:

| col_1 | col_2 | col_3 |
|-------|-------|-------|
| val | val | val |

---

## Issues Found

| Issue | Severity | Description | Action |
|-------|----------|-------------|--------|
| None | - | - | - |

---

## Sign-Off

| Reviewer | Date | Verdict |
|----------|------|---------|
| Ronnie | YYYY-MM-DD | ✅ Valid / ⚠️ Needs Fix / ❌ Invalid |

---
