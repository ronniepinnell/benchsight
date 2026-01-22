# Planning Workflow

**PRD-first development process**

Last Updated: 2026-01-21

---

## Overview

This document outlines the planning workflow for BenchSight, emphasizing PRD-first development where documentation precedes coding.

**Principle:** Document before coding - PRD becomes source of truth for every AI conversation.

---

## When to Create a PRD

### Always Create PRD

- **New Features** - Any new functionality
- **Significant Refactors** - Major code restructuring (> 3 files)
- **Complex Bug Fixes** - Bugs requiring architectural changes
- **Integration Work** - Connecting components
- **Performance Improvements** - Optimization work

### Optional PRD

- **Simple Bug Fixes** - Quick fixes (document in issue)
- **Documentation Updates** - Minor doc changes
- **Small Refactors** - Minor code improvements (< 3 files)

---

## PRD Creation Process

### Step 1: Create PRD

**Option A: Using CLI (when implemented)**
```bash
./benchsight.sh prd create feature-name
```

**Option B: Manual**
```bash
cp docs/prds/template.md docs/prds/features/feature-name.md
# Edit the PRD
```

### Step 2: Fill Out PRD

**Use template:** `docs/prds/template.md`

**Required Sections:**
1. Problem Statement
2. Solution Approach
3. Technical Design
4. Implementation Phases
5. Success Criteria
6. Dependencies
7. Risks
8. Timeline

### Step 3: Review PRD

**Self-Review Checklist:**
- [ ] Problem clearly stated
- [ ] Solution approach defined
- [ ] Technical design complete
- [ ] Phases broken down
- [ ] Success criteria measurable
- [ ] Dependencies identified
- [ ] Risks assessed
- [ ] Timeline realistic

**Get Feedback (if needed):**
- Share PRD for review
- Address feedback
- Update PRD

### Step 4: Create GitHub Issue

**Link PRD to Issue:**
```markdown
## PRD Reference
- PRD: `docs/prds/features/feature-name.md`
- Status: Approved
```

**Issue should reference PRD, not duplicate it.**

### Step 5: Approval

**PRD Status:**
- `Draft` - Being written
- `In Review` - Awaiting feedback
- `Approved` - Ready for implementation
- `In Progress` - Being implemented
- `Complete` - Implementation done

---

## PRD → Implementation Flow

### Planning Conversation

**Start new conversation with:**
```
I'm planning to implement [feature]. 
Please read docs/prds/features/[feature-name].md 
and help me refine the plan.
```

**Focus:**
- Research and design
- Create/refine PRD
- Break down into phases
- Identify dependencies

**Output:**
- Complete PRD
- Clear implementation plan

### Context Reset

**After planning, start fresh conversation:**
```
I'm implementing [feature] as specified in 
docs/prds/features/[feature-name].md

Let's start with Phase 1: [phase name]
```

**Why reset?**
- Planning and execution are separate
- Context window degradation is real
- Fresh start = sharp focus

### Execution Conversation

**Reference PRD in every message:**
- "Following the PRD..."
- "As specified in Phase 1..."
- "Per the technical design..."

**Update PRD as needed:**
- Document learnings
- Update phases
- Adjust timeline

---

## PRD Maintenance

### During Implementation

**Update PRD when:**
- You learn something new
- Design changes
- Timeline changes
- Dependencies change

**Keep PRD current:**
- Mark phases complete
- Update status
- Document decisions

### After Implementation

**Final PRD Update:**
- Mark all phases complete
- Update success criteria
- Document final state
- Add to change log

**Link in PR:**
- Reference PRD in PR description
- Show PRD completion

---

## PRD Review Process

### Self-Review

**Check:**
- Completeness
- Clarity
- Feasibility
- Dependencies

### Peer Review (Optional)

**For significant features:**
- Share PRD
- Get feedback
- Address concerns
- Update PRD

### Approval

**PRD is approved when:**
- All sections complete
- Technical design sound
- Dependencies clear
- Timeline realistic
- Ready for implementation

---

## PRD Templates

### Feature PRD

**Location:** `docs/prds/features/[name].md`

**Use for:** New features, enhancements

### Refactor PRD

**Location:** `docs/prds/refactors/[name].md`

**Use for:** Code restructuring, improvements

### Bug Fix PRD

**Location:** `docs/prds/bugs/YYYY-MM-DD-[name].md`

**Use for:** Significant bug fixes requiring design changes

---

## Best Practices

### ✅ Do:

- Create PRD before coding
- Be specific and detailed
- Include examples and diagrams
- Reference PRD in all conversations
- Update PRD as you learn
- Link PRD to issues and PRs
- Reset context after planning

### ❌ Don't:

- Skip PRD for complex work
- Write PRD after coding
- Make PRD too vague
- Forget to update PRD
- Mix planning and execution
- Ignore PRD during implementation

---

## Examples

### Example 1: Feature PRD

**Feature:** Portal API Integration

**PRD:** `docs/prds/features/portal-api-integration.md`

**Process:**
1. Create PRD with technical design
2. Create GitHub issue, link PRD
3. Start planning conversation
4. Refine PRD
5. Reset context
6. Start implementation conversation
7. Reference PRD throughout
8. Update PRD as needed
9. Complete implementation
10. Mark PRD complete

### Example 2: Refactor PRD

**Refactor:** Base ETL Modularization

**PRD:** `docs/prds/refactors/base-etl-modularization.md`

**Process:**
1. Create PRD with breakdown
2. Plan modularization approach
3. Reset context
4. Implement phase by phase
5. Reference PRD throughout

---

## Related Documentation

- [PRD Index](../prds/README.md) - PRD directory
- [PRD Template](../prds/template.md) - PRD template
- [WORKFLOW.md](WORKFLOW.md) - Development workflow
- [CONTEXT_RESET_STRATEGY.md](CONTEXT_RESET_STRATEGY.md) - Context reset strategy

---

*Last Updated: 2026-01-15*
