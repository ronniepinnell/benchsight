# Rules Evolution History

**Tracking how rules evolve based on bugs and improvements**

Last Updated: 2026-01-15

---

## Overview

This document tracks the evolution of rules, when they were added, why they were added, and what triggered them.

---

## Rules Added

### 2026-01-15: Goal Counting Rule

**Trigger:** Bug in goal counting logic

**Rule Added:**
- Location: `.agents/core.md`
- Rule: Goals must use `GOAL_FILTER` pattern
- Also added to: `.coderabbit.yaml`

**Prevention:** Prevents incorrect goal counting

---

### 2026-01-15: Iterrows Rule

**Trigger:** Performance issue with `.iterrows()` usage

**Rule Added:**
- Location: `.agents/reference/etl.md`
- Rule: Never use `.iterrows()`, use vectorized operations
- Also added to: `.coderabbit.yaml`

**Prevention:** Prevents performance issues

---

## Rules Updated

### [Date]: [Rule Name]

**Trigger:** [What triggered the update]

**Change:** [What changed]

**Location:** [Where rule is located]

---

## Related Documentation

- [SYSTEM_EVOLUTION_WORKFLOW.md](SYSTEM_EVOLUTION_WORKFLOW.md) - Evolution workflow
- `bugs/` - Bug documentation
- `improvements/` - Improvement documentation

---

*Last Updated: 2026-01-15*
