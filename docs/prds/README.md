# Product Requirements Documents (PRDs)

**PRD-first development - Document before coding**

Last Updated: 2026-01-21

---

## Overview

PRDs are the source of truth for every AI conversation and each granular feature. They ensure clarity, prevent context drift, and make development more efficient.

**Principle:** Document before coding, not during or after.

---

## When to Create a PRD

### Always Create PRD For:

- **New Features** - Any new functionality
- **Significant Refactors** - Major code restructuring
- **Complex Bug Fixes** - Bugs requiring architectural changes
- **Integration Work** - Connecting components
- **Performance Improvements** - Optimization work

### Optional PRD For:

- **Simple Bug Fixes** - Quick fixes (document in issue)
- **Documentation Updates** - Minor doc changes
- **Small Refactors** - Minor code improvements

---

## PRD Structure

### Location

```
docs/prds/
├── features/          # Feature PRDs
├── refactors/         # Refactoring PRDs
└── bugs/              # Bug fix PRDs (when significant)
```

### Naming Convention

- Features: `feature-name.md` (kebab-case)
- Refactors: `refactor-name.md` (kebab-case)
- Bugs: `YYYY-MM-DD-bug-description.md` (date prefix)

**Examples:**
- `features/portal-api-integration.md`
- `refactors/base-etl-modularization.md`
- `bugs/2026-01-15-goal-counting-fix.md`

---

## PRD Template

Use `template.md` as a starting point. Each PRD should include:

1. **Problem Statement** - What problem are we solving?
2. **Solution Approach** - How will we solve it?
3. **Technical Design** - Architecture and implementation details
4. **Implementation Phases** - Step-by-step breakdown
5. **Success Criteria** - How do we know it's done?
6. **Dependencies** - What needs to exist first?
7. **Risks** - What could go wrong?
8. **Timeline** - Estimated time

---

## PRD Workflow

### 1. Create PRD

```bash
# Using CLI (when implemented)
./benchsight.sh prd create feature-name

# Or manually
cp docs/prds/template.md docs/prds/features/feature-name.md
```

### 2. Review PRD

- Self-review for completeness
- Get feedback if needed
- Update based on feedback

### 3. Link to Issue

- Create GitHub issue
- Link PRD in issue description
- Reference issue in PRD

### 4. Implementation

- Reference PRD in every AI conversation
- Update PRD as needed during implementation
- Mark phases complete as you go

### 5. Completion

- Verify success criteria met
- Update PRD with final state
- Link PRD in PR description

---

## PRD Best Practices

### ✅ Do:

- Write PRD before starting code
- Be specific and detailed
- Include examples and diagrams
- Update PRD as you learn
- Reference PRD in all conversations
- Link PRD to issues and PRs

### ❌ Don't:

- Skip PRD for complex work
- Write PRD after coding
- Make PRD too vague
- Forget to update PRD
- Ignore PRD during implementation

---

## PRD Index

### Features

- [ ] Create index of all feature PRDs
- [ ] Link to implementation status

### Refactors

- [ ] Create index of all refactor PRDs
- [ ] Link to completion status

### Bugs

- [ ] Create index of significant bug PRDs
- [ ] Link to fixes

---

## Related Documentation

- [PLANNING_WORKFLOW.md](../workflows/PLANNING_WORKFLOW.md) - Planning process
- [WORKFLOW.md](../workflows/WORKFLOW.md) - Development workflow
- [template.md](template.md) - PRD template

---

*Last Updated: 2026-01-15*
