---
name: mentor
description: Get best practice guidance, workflow recommendations, and learn Claude Code patterns. Acts as a knowledgeable guide until you become an expert.
allowed-tools: Read, Glob, Grep
---

# Mentor Skill - Best Practice Guide

Your personal guide to mastering Claude Code and BenchSight development workflows.

## Invocation

```
/mentor                 # General guidance for current context
/mentor workflow        # Show complete workflow for current task
/mentor checklist       # Pre/post task checklists
/mentor why [topic]     # Explain why we do something
/mentor patterns        # Show common patterns to follow
/mentor mistakes        # Common mistakes to avoid
```

---

## Core Philosophy

### The BenchSight Way

1. **PRD First** - Write requirements before code (for P0/P1 work)
2. **Issue Linked** - Every task has a GitHub issue
3. **Test Driven** - Tests exist before refactoring
4. **Validate Always** - Run `/post-code` after every change
5. **Document Continuously** - Docs updated with code

### When in Doubt

```
/pm status          # What should I work on?
/mentor workflow    # How should I do this?
/post-code          # Did I do it right?
```

---

## Complete Development Workflow

### Starting a Task

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SELECT TASK                                              │
│    /pm prioritize → Get next task from P0 queue             │
│    Review GitHub issue → Understand requirements            │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. UNDERSTAND CONTEXT                                       │
│    Read related code → Use Explore agent                    │
│    Read related docs → Check docs/ folder                   │
│    Check PRD → Does one exist? Create if P0/P1              │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. PLAN (if complex)                                        │
│    /plan → Enter plan mode for design                       │
│    Get user approval before implementing                    │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. IMPLEMENT                                                │
│    Write tests first (if adding functionality)              │
│    Make small, incremental changes                          │
│    Commit frequently (use Edit, not Write where possible)   │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. VALIDATE                                                 │
│    /post-code → Full validation workflow                    │
│    Fix any failures before continuing                       │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. COMMIT                                                   │
│    /post-code commit → Stage, message, commit               │
│    Update GitHub issue                                      │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. NEXT TASK                                                │
│    /pm status → Get next priority                           │
│    Repeat from step 1                                       │
└────────────────────────────────────────────────────────────┘
```

---

## Pre-Task Checklist

Before starting any work:

- [ ] Do I have a GitHub issue for this? If not, create one
- [ ] Is this the highest priority task? Check `/pm prioritize`
- [ ] Do I understand the requirements? Read issue + PRD
- [ ] Are there dependencies? Check "Depends On" in issue
- [ ] Do I need a PRD? (Yes if P0/P1 feature)

---

## Post-Task Checklist

After completing any work:

- [ ] Did I run `/post-code`? REQUIRED
- [ ] Did all tests pass? Must be yes to continue
- [ ] Did I update the GitHub issue? Add progress comment
- [ ] Did I update docs if needed? `/doc-sync` will tell you
- [ ] Did I sync GitHub issues? `./scripts/sync-github-issues.sh`

---

## Common Patterns

### Pattern: Safe Refactoring

```
1. Create tests first (#36)
2. Verify tests pass with current code
3. Make ONE change at a time
4. Run tests after each change
5. Commit when tests pass
6. Repeat
```

### Pattern: New Feature

```
1. Create GitHub issue
2. Write PRD (if P0/P1)
3. Get user approval on approach
4. Write failing tests
5. Implement until tests pass
6. /post-code
7. Close issue
```

### Pattern: Bug Fix

```
1. Create/find GitHub issue
2. Reproduce the bug
3. Write test that fails (proves bug)
4. Fix the bug
5. Test passes
6. /post-code
7. Close issue with root cause
```

### Pattern: ETL Changes

```
1. Run ETL before changes (baseline)
2. Save output for comparison
3. Make changes
4. Run ETL again
5. Diff outputs (should be same unless intended)
6. /validate
7. /post-code
```

---

## Why We Do Things

### Why PRDs?

PRDs prevent:
- Misunderstanding requirements
- Scope creep
- Rework after implementation
- Missing edge cases

### Why Tests First?

Tests first means:
- You understand what "done" looks like
- Safe to refactor later
- Documentation of expected behavior
- Prevents regression

### Why /post-code?

/post-code catches:
- CLAUDE.md violations (before they cause bugs)
- Incomplete implementations
- Over-engineering
- Documentation drift
- Broken tests

### Why Issue-Linked?

Issues provide:
- Traceability (what changed and why)
- Progress tracking
- Context for future reference
- Collaboration point

---

## Common Mistakes to Avoid

### ❌ Starting Without Issue

**Wrong:**
```
"Let me just quickly fix this..."
```

**Right:**
```
1. Create/find issue
2. Reference issue in commits
3. Close issue when done
```

### ❌ Big Bang Changes

**Wrong:**
```
*Changes 20 files at once*
*Commits everything together*
```

**Right:**
```
*Change 1-3 files*
*Test*
*Commit*
*Repeat*
```

### ❌ Skipping Validation

**Wrong:**
```
"It works on my machine, I'll commit"
```

**Right:**
```
/post-code
*Wait for all checks*
*Then commit*
```

### ❌ Marking Done Without Verification

**Wrong:**
```
*Writes code*
"Task complete!"
```

**Right:**
```
*Writes code*
/post-code
*Karen validates*
"Task complete with validation proof"
```

### ❌ Using .iterrows()

**Wrong:**
```python
for idx, row in df.iterrows():
    df.loc[idx, 'col'] = calculate(row)
```

**Right:**
```python
df['col'] = df.apply(lambda r: calculate(r), axis=1)
# or better
df['col'] = np.where(condition, value1, value2)
```

---

## Quick Reference Commands

| Need | Command |
|------|---------|
| What to work on? | `/pm prioritize` |
| How to do this? | `/mentor workflow` |
| Is my code good? | `/post-code` |
| Match requirements? | `/reality-check` |
| Check compliance? | `/compliance-check` |
| Update docs? | `/doc-sync` |
| Create PR? | `/pr-workflow` |
| Hockey stats help? | `/hockey-stats` |
| ETL help? | Use Task with etl-specialist |
| DB help? | `/db-dev` |

---

## Learning Path

### Week 1: Basics
- Learn to always run `/post-code`
- Get comfortable with GitHub issues
- Understand the skill system

### Week 2: Workflow
- Master the complete development workflow
- Use `/pm` for task selection
- Link everything to issues

### Week 3: Quality
- Use specialists appropriately
- Understand validation agents
- Write tests confidently

### Week 4+: Expert
- You rarely need `/mentor` anymore
- You instinctively run validations
- You catch issues before agents do

---

## Getting Help

```
/mentor              # General guidance
/mentor why [topic]  # Understand reasoning
/pm                  # Project management
/hockey-stats        # Domain expertise
```

When stuck:
1. Check the related PRD
2. Check the GitHub issue
3. Ask `/mentor why [topic]`
4. Use Task with appropriate specialist agent
