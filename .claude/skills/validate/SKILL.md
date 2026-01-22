---
name: validate
description: Run ETL validation suite and verify output integrity. Use after ETL runs, when checking goal counting, or verifying data quality.
allowed-tools: Bash, Read, Grep
---

# ETL Validation Suite

Validate the ETL pipeline output and check data integrity.

## Execution

```bash
./benchsight.sh etl validate
```

## What This Validates

1. **Goal Counting**: ONLY `event_type == 'Goal'` AND `event_detail == 'Goal_Scored'`
2. **Stat Attribution**: Only `player_role == 'event_player_1'` (no duplicate counting)
3. **Micro-stat Deduplication**: Once per `linked_event_key`, not per event
4. **Key Formatting**: All keys follow `{XX}{ID}{5D}` format
5. **Foreign Keys**: Dimension table references exist
6. **Performance**: ETL runtime under 90 seconds

## After Running

Check `data/output/qa_*` tables for any flagged issues.
Report any Critical or High severity findings.
