---
name: etl-issue
description: Create a GitHub issue for ETL failures with full context including error details, recent commits, and changed files. Use after ETL failures or to document known issues.
allowed-tools: Bash, Read, Grep
argument-hint: [error description or "last" for most recent failure]
---

# ETL Issue Creator

Create detailed GitHub issues for ETL failures.

## Usage

**From recent failure:**
```bash
/etl-issue last
```

**With description:**
```bash
/etl-issue Goal counting returning wrong totals in phase 3
```

## What This Does

1. **Gathers Context:**
   - Error details from logs or description
   - Recent git commits (last 5)
   - Changed files (last 3 commits)
   - Current branch
   - ETL output state

2. **Creates Issue:**
   - Descriptive title with phase and error type
   - Full error context in body
   - Labels: `bug`, `etl`, `auto-generated`
   - Links to relevant files

3. **Suggests Actions:**
   - Review checklist
   - Related skills to run
   - Investigation steps

## Issue Template

```markdown
## ETL Failure Report

**Generated:** YYYY-MM-DD HH:MM:SS
**Branch:** `branch-name`
**Phase:** Loading/Calculations/etc.

## Error Details

**Type:** `ErrorType`
**Message:** Error description

## Command Run

```bash
./benchsight.sh etl run
```

## Traceback

```python
Full traceback if available
```

## Recent Commits

- abc1234 Recent commit message
- def5678 Another commit

## Recently Changed Files

- src/calculations/goals.py
- config/formulas.json

## Suggested Actions

- [ ] Review the error
- [ ] Check recent commits
- [ ] Run /validate
```

## Manual Issue Creation

If you prefer manual control:

```bash
# Get failure context
cat ~/.claude/etl-failures/etl_failure_*.json | tail -1 | jq .

# Create issue manually
gh issue create \
  --title "[ETL] Phase failed: ErrorType" \
  --body "$(cat issue_body.md)" \
  --label bug,etl
```

## Failure Log Location

All ETL failures are logged to:
```
~/.claude/etl-failures/etl_failure_YYYYMMDD_HHMMSS.json
```

## View Recent Failures

```bash
# List recent failures
ls -la ~/.claude/etl-failures/

# View most recent
cat ~/.claude/etl-failures/$(ls -t ~/.claude/etl-failures/ | head -1) | jq .
```

## Labels Used

| Label | Purpose |
|-------|---------|
| `bug` | It's a bug |
| `etl` | ETL-related |
| `auto-generated` | Created by automation |
| `priority:high` | Added if goal counting affected |
| `data-integrity` | Added if validation failed |

## Related Skills

After creating an issue:
- `/validate` - Check current data state
- `/hockey-stats` - If calculation methodology question
- `/compliance-check` - If rule violation suspected
