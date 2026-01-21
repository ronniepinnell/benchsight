# System Evolution Workflow

**How bugs and improvements evolve the system**

Last Updated: 2026-01-15

---

## Overview

Every bug is an opportunity to evolve the system. When a bug occurs, we fix it AND evolve the system to prevent recurrence.

**Principle:** Every time you develop a new feature, your coding agent gets smarter.

---

## Bug Evolution Process

### Step 1: Document the Bug

**Create:** `docs/system-evolution/bugs/YYYY-MM-DD-bug-description.md`

**Template:**
```markdown
# Bug: [Bug Description]

**Date:** YYYY-MM-DD
**Component:** ETL/Dashboard/API/Tracker/Portal
**Severity:** Critical/High/Medium/Low

## Bug Description

[What went wrong]

## Root Cause

[Why it happened]

## Fix Applied

[How it was fixed]

## Rule/Context Added

[What rule or context was added to prevent recurrence]

## Prevention Strategy

[How the system now prevents this bug]
```

### Step 2: Fix the Bug

**Fix in code:**
- Apply the fix
- Test the fix
- Verify it works

### Step 3: Evolve the System

**Add rule/context:**
- Identify where rule should go
- Add to appropriate `.agents/reference/` file
- Update `.coderabbit.yaml` if needed
- Update documentation

**Locations:**
- `.agents/core.md` - Critical rules
- `.agents/reference/[component].md` - Component-specific rules
- `.coderabbit.yaml` - CodeRabbit rules
- `docs/MASTER_RULES.md` - Master rules

### Step 4: Update Rules History

**Update:** `docs/system-evolution/rules-history.md`

**Add entry:**
- Date
- Rule added
- Trigger (bug/improvement)
- Location

---

## Improvement Evolution Process

### Step 1: Document the Improvement

**Create:** `docs/system-evolution/improvements/YYYY-MM-DD-improvement.md`

**Template:**
```markdown
# Improvement: [Improvement Name]

**Date:** YYYY-MM-DD
**Component:** ETL/Dashboard/API/Tracker/Portal

## Improvement Description

[What was improved]

## Why

[Why this improvement was needed]

## Implementation

[How it was implemented]

## System Evolution

[How the system evolved]
```

### Step 2: Implement Improvement

**Implement:**
- Make the improvement
- Test it
- Verify it works

### Step 3: Update System

**Update:**
- Rules if needed
- Context if needed
- Documentation

### Step 4: Update Rules History

**Update:** `docs/system-evolution/rules-history.md`

---

## Examples

### Example 1: Goal Counting Bug

**Bug:** AI used `event_type == 'Goal'` without checking `event_detail == 'Goal_Scored'`

**Fix:** Added GOAL_FILTER constant and rule

**Evolution:**
1. Documented in `bugs/2026-01-15-goal-counting.md`
2. Added rule to `.agents/core.md`
3. Added rule to `.coderabbit.yaml`
4. Updated `rules-history.md`

**Result:** System now prevents incorrect goal counting

### Example 2: Iterrows Performance

**Bug:** AI used `.iterrows()` causing performance issues

**Fix:** Added rule to use vectorized operations

**Evolution:**
1. Documented in `bugs/2026-01-15-iterrows.md`
2. Added rule to `.agents/reference/etl.md`
3. Added rule to `.coderabbit.yaml`
4. Updated `rules-history.md`

**Result:** System now prevents `.iterrows()` usage

### Example 3: Type Consistency

**Bug:** AI didn't ensure type consistency before merges

**Fix:** Added type checking rule

**Evolution:**
1. Documented in `bugs/2026-01-15-type-consistency.md`
2. Added rule to `.agents/reference/data.md`
3. Added rule to `.coderabbit.yaml`
4. Updated `rules-history.md`

**Result:** System now checks type consistency

---

## Best Practices

### ✅ Do:

- Document every significant bug
- Fix the bug AND evolve the system
- Add rules to prevent recurrence
- Update rules history
- Keep evolution documentation current

### ❌ Don't:

- Just fix bugs without evolving
- Skip documentation
- Forget to update rules
- Ignore patterns

---

## Related Documentation

- [System Evolution Index](system-evolution/README.md) - Evolution structure
- [Rules History](system-evolution/rules-history.md) - Rules evolution log
- `.agents/` - Modular rules
- `.coderabbit.yaml` - CodeRabbit rules

---

*Last Updated: 2026-01-15*
