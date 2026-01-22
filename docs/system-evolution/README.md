# System Evolution Tracking

**Every bug is an opportunity to evolve the system**

Last Updated: 2026-01-21

---

## Overview

This directory tracks how bugs and improvements lead to system evolution. When a bug occurs, we fix it AND evolve the system to prevent recurrence.

**Principle:** Every bug is an opportunity to evolve your SYSTEM for AI coding.

---

## Structure

```
docs/system-evolution/
├── README.md                    # This file
├── bugs/                        # Bug → Rule evolution
│   ├── 2026-01-15-goal-counting.md
│   └── ...
├── improvements/                # System improvements
│   └── ...
└── rules-history.md            # Rules evolution log
```

---

## Bug Evolution Process

### When a Bug Occurs

1. **Document the bug** in `bugs/YYYY-MM-DD-bug-description.md`
2. **Fix the bug** in code
3. **Add rule/context** to prevent recurrence
4. **Update relevant** `.agents/reference/` files
5. **Update** `rules-history.md`

### Bug Documentation Template

**File:** `bugs/YYYY-MM-DD-bug-description.md`

**Contents:**
- Bug description
- Root cause
- Fix applied
- Rule/context added
- Prevention strategy

---

## System Improvements

### When Improvement Identified

1. **Document improvement** in `improvements/YYYY-MM-DD-improvement.md`
2. **Implement improvement**
3. **Update system** (rules, context, docs)
4. **Document** in `rules-history.md`

---

## Rules Evolution

### Tracking Changes

**File:** `rules-history.md`

**Tracks:**
- When rules were added
- Why rules were added
- What bugs/improvements triggered them
- Where rules are located

---

## Examples

### Example 1: Goal Counting Bug

**Bug:** AI used wrong goal counting pattern

**Fix:** Added GOAL_FILTER rule

**Evolution:**
- Added to `.agents/core.md`
- Added to `.coderabbit.yaml`
- Documented in `bugs/2026-01-15-goal-counting.md`

### Example 2: Iterrows Usage

**Bug:** AI used `.iterrows()` instead of vectorized operations

**Fix:** Added performance rule

**Evolution:**
- Added to `.agents/reference/etl.md`
- Added to CodeRabbit rules
- Documented in `bugs/2026-01-15-iterrows.md`

---

## Related Documentation

- [SYSTEM_EVOLUTION_WORKFLOW.md](../workflows/SYSTEM_EVOLUTION_WORKFLOW.md) - Complete workflow
- `.agents/` - Modular rules
- `.coderabbit.yaml` - CodeRabbit rules

---

*Last Updated: 2026-01-15*
