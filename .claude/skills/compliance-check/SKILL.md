---
name: compliance-check
description: Verify recent code changes adhere to CLAUDE.md guidelines and project standards. Use after implementing features or making significant changes.
---

# CLAUDE.md Compliance Check

Verify recent changes follow project-specific rules.

## Critical Rules Checked

### Goal Counting (CRITICAL)
```python
# ONLY this counts as a goal:
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
```

### Stat Attribution
```python
# Count ONLY for event_player_1
df[df['player_role'] == 'event_player_1']
```

### Vectorized Operations
```python
# NEVER use .iterrows()
# ALWAYS use .groupby().apply() or vectorized operations
```

### Key Formatting
All keys: `{XX}{ID}{5D}` format

## Also Checks

- Foreign key relationships exist
- Single source of truth (no duplicated calculations)
- Performance targets met (ETL < 90s, Dashboard < 2s, API < 200ms)
- Type hints on Python functions
- TypeScript strict mode for dashboard

## Task

Check $ARGUMENTS for compliance with all CLAUDE.md rules.
Flag deviations with file:line references and suggest fixes.
