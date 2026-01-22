---
name: pm
description: Project management, work prioritization, phase transitions, and continuous improvement. Use for task selection, progress validation, and workflow guidance.
allowed-tools: Bash, Read, Grep, Write, Edit, Task
---

# PM Skill - Project Management & Continuous Improvement

Use this skill when you need:
- Guidance on Claude Code best practices
- Next step recommendations
- Phase transition decisions
- Progress validation
- Work prioritization
- Issue reorganization after failures
- Continuous improvement recommendations

## Invocation

```
/pm                    # General PM guidance
/pm status             # Current project status + next steps
/pm phase              # Phase transition readiness check
/pm prioritize         # Get work priority recommendations
/pm review             # Review recent work against best practices
/pm reorg              # Reorganize issues after changes/failures
/pm improve            # Continuous improvement suggestions
/pm next               # What should I work on next?
```

---

## Continuous Improvement System

### After Every Commit

The PM skill tracks patterns and suggests improvements:

```
┌─────────────────────────────────────────────────────────────┐
│              CONTINUOUS IMPROVEMENT CYCLE                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  COMMIT MADE                                                │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                    │
│  │ Was it a fix for    │──YES──► Create prevention issue    │
│  │ a previous issue?   │         (test gap, validation gap) │
│  └─────────────────────┘                                    │
│      │ NO                                                   │
│      ▼                                                      │
│  ┌─────────────────────┐                                    │
│  │ Did it create new   │──YES──► Create tracking issue      │
│  │ technical debt?     │         (refactor needed later)    │
│  └─────────────────────┘                                    │
│      │ NO                                                   │
│      ▼                                                      │
│  ┌─────────────────────┐                                    │
│  │ Did it reveal a     │──YES──► Update process/docs        │
│  │ process gap?        │         (add to /mentor)           │
│  └─────────────────────┘                                    │
│      │ NO                                                   │
│      ▼                                                      │
│  ✅ CLEAN COMMIT                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Issue Reorganization (`/pm reorg`)

After code failures or new discoveries, reorganize issues:

```bash
# 1. Check for issues that should be reprioritized
gh issue list --label "phase:2" --state open --json number,title,labels

# 2. Identify blocking relationships
# - If #A blocks #B, ensure #A has higher priority

# 3. Create new issues from failures
gh issue create --title "[FIX] [description]" \
  --body "Created from failure during: [context]" \
  --label "type:fix,priority:p1"

# 4. Update execution order in issue descriptions
# - "Execution Order: N (after #X, #Y)"
```

---

## What This Skill Does

1. **Best Practices Enforcement**
   - Checks if PRDs exist for work being done
   - Validates documentation is updated
   - Ensures tests accompany code changes
   - Verifies GitHub issues are linked

2. **Next Step Recommendations**
   - Based on current phase and P0/P1 issues
   - Considers dependencies between tasks
   - Suggests parallel work opportunities

3. **Phase Transition Guidance**
   - Checks phase completion criteria
   - Validates when to create next phase issues
   - Ensures clean handoffs

4. **Progress Validation**
   - Compares claimed vs actual progress
   - Identifies incomplete implementations
   - Flags technical debt accumulation

5. **Continuous Improvement**
   - Tracks patterns in failures
   - Suggests process improvements
   - Creates prevention issues

---

## PM Decision Framework

### When Starting Work

```
1. Does this have a GitHub issue? If not, create one
2. Does this have a PRD? If not, create one for P0/P1 work
3. Is the issue in the current phase? If not, question priority
4. Are dependencies satisfied? If not, work on blockers first
```

### When Completing Work

```
1. Are tests written and passing?
2. Is documentation updated?
3. Is the GitHub issue updated/closed?
4. Are any new issues discovered? Create them
5. Is validation passing?
6. /pm improve - Check for process improvements
```

### When Transitioning Phases

```
Phase is ready to transition when:
- ≥80% of P0 issues closed
- ≥60% of P1 issues closed
- All critical validation passing
- No blocking issues remain

Actions at transition:
- Create next phase P0/P1 issues
- Update PROJECT_STATUS.md
- Review and archive completed PRDs
```

---

## Current Project Context

### Phase 2: ETL Optimization (CURRENT)

**Milestones:**
- M1: MVP Foundation (Phases 1-4) ← CURRENT
- M2: Tracker Modernization (Phase 5)
- M3: ML/CV Integration (Phase 6)
- M4: Commercial Ready (Phases 7-8)
- M5: AI Coaching Platform (Phases 9-12)

**P0 Execution Order (do these in order):**

| Order | Issue | Title | Depends On |
|-------|-------|-------|------------|
| 1 | #31 | Missing 7 tables | None |
| 2 | #35 | Table verification framework | #31 |
| 3 | #36 | Unit tests for calculations | #35 |
| 4 | #13 | Goal counting verification | #35 |
| 5 | #37 | Error handling | #36 |
| 6 | #38 | Phase validation | #37 |
| 7 | #5 | Vectorization | #36, #35 |

**PostgreSQL Debug Infrastructure (P1):**
- Should come AFTER #35 (verification framework)
- Helps with debugging but not blocking P0 work
- Good parallel work while doing #36-#38

---

## Phase Transition Criteria

### Phase 2 → Phase 3 Checklist

```
[ ] All 139 tables generating correctly
[ ] Goal counting verified against official scores
[ ] Unit tests >80% coverage for calculations
[ ] Verification framework running in CI
[ ] Error handling throughout ETL
[ ] ETL runtime <60s for 4 games
[ ] All P0 issues closed
[ ] >60% P1 issues closed
```

**When criteria met:**
1. Create Phase 3 P0/P1 GitHub issues
2. Update docs/PROJECT_STATUS.md
3. Update GITHUB_ISSUES_BACKLOG.md sync status

---

## Issue Management Commands

### Check Priority Queue

```bash
# P0 issues in current phase
gh issue list --label "priority:p0,phase:2" --state open --json number,title

# Issues blocked by something
gh issue list --state open --json number,title,body | \
  python -c "import json,sys; [print(f'#{i[\"number\"]} blocked') for i in json.load(sys.stdin) if 'Depends On' in i.get('body','')]"
```

### Create Issue from Failure

```bash
gh issue create \
  --title "[FIX] Description from failure" \
  --body "## Context
Found during: [validation/test/implementation]

## Error
\`\`\`
[error message]
\`\`\`

## Root Cause
[analysis]

## Fix
[proposed solution]

## Related Issues
- #NN (parent issue)" \
  --label "type:fix,priority:p1,phase:2" \
  --milestone "M1: MVP Foundation"
```

### Update Issue Progress

```bash
# Add progress comment
gh issue comment [NUMBER] --body "Progress: [description]

Changes:
- [x] Step 1
- [ ] Step 2

Next: [what's next]"

# Close with summary
gh issue close [NUMBER] --comment "Completed in [commit hash]

Summary:
- [what was done]
- [validation status]"
```

### Reorganize After Failure

```bash
# 1. List affected issues
gh issue list --label "phase:2" --state open

# 2. Reprioritize (add priority label)
gh issue edit [NUMBER] --add-label "priority:p0"

# 3. Add dependency notes
gh issue edit [NUMBER] --body "[existing body]

## Updated Dependencies
- Blocked by: #NN
- Execution Order: X (after #Y, #Z)"
```

---

## Best Practices Checklist

### For Every PR

- [ ] Links to GitHub issue
- [ ] Has tests (if code change)
- [ ] Has PRD (if P0/P1 feature)
- [ ] Documentation updated
- [ ] Validation passing
- [ ] No new warnings introduced

### For Every Session

- [ ] Start by checking `/pm status`
- [ ] Work on highest priority first
- [ ] Update issue status as you work
- [ ] End by validating work done

### For Every Commit

- [ ] Run `/post-code` before committing
- [ ] Reference issue number in commit
- [ ] Update issue with progress
- [ ] Check for new issues to create

### For Every Week

- [ ] Review phase progress
- [ ] Check if transition criteria met
- [ ] Update roadmap/status docs
- [ ] Sync GitHub issues with backlog
- [ ] Run `/pm improve` for suggestions

---

## Continuous Improvement Patterns

### Pattern: Test Gap Prevention

When a bug is fixed:
```
1. Create test that would have caught it
2. Add to validation suite
3. Document in CLAUDE.md if it's a new rule
```

### Pattern: Validation Gap Prevention

When validation misses something:
```
1. Add check to /validate
2. Consider if /post-code should include it
3. Update skill documentation
```

### Pattern: Process Gap Prevention

When a process is unclear:
```
1. Add to /mentor skill
2. Update workflow docs
3. Consider if automation helps
```

### Pattern: Dead Code Prevention

Weekly or after major refactors:
```bash
# 1. Check for unused skills/agents
python scripts/analyze-usage.py --unused

# 2. Check for files with no recent references
find sql scripts -type f -mtime +180  # Files not modified in 6 months

# 3. Search for orphaned code
grep -r "def unused_" src/  # Functions with 'unused' prefix

# 4. Create cleanup issue if found
gh issue create --title "[CHORE] Clean up dead code" \
  --label "type:chore,priority:p2"
```

**Related issue:** #50 (Dead code cleanup)

---

## Quick Commands

```bash
# Check current phase P0 issues
gh issue list --label "priority:p0,phase:2" --state open

# Check overall progress
gh issue list --state all --json state --jq 'group_by(.state) | map({state: .[0].state, count: length})'

# View recent commits
git log --oneline -10

# Run validation
./benchsight.sh etl validate

# Check for outdated docs
./scripts/docs-check.sh

# Sync GitHub issues
./scripts/sync-github-issues.sh
```

---

## Environment Management

### Dev vs Prod Decision Matrix

| Action | Environment | Command |
|--------|-------------|---------|
| Feature development | Dev | `./benchsight.sh env switch dev` |
| Bug fixes | Dev | `./benchsight.sh env switch dev` |
| ETL testing | Dev | `./benchsight.sh env switch dev` |
| PR previews | Dev (automatic) | Vercel preview deployments |
| Release to users | Prod | `./benchsight.sh env switch production` |
| Merge to main | Prod (automatic) | Vercel production deployment |

### Environment Check Workflow

```
Before ANY work:
  1. ./benchsight.sh env status
  2. Should show "dev" for 99% of work

Before merge to main:
  1. Verify all tests pass in dev
  2. Confirm intentional production deployment
  3. Have rollback plan ready
```

### Never Do In Production

- Schema migrations without testing in dev first
- Bulk data operations without backup
- ETL runs without validation
- Direct database edits

---

## Context & Session Management

### When to Start New Session

| Trigger | Action |
|---------|--------|
| Context >75% full | Start new session |
| Major milestone complete | Start new session |
| Switching issues | Consider new session |
| After merge | Start new session |
| Confusion/repetition | Start new session |

### Session Efficiency

**Keep sessions focused:**
- One issue per session ideal
- Commit before context fills
- Update issue with progress before switching
- Use `/pm status` at session start

### Handoff Checklist

Before ending session:
```
□ Work committed
□ logs/*.log.md updated
□ CHANGELOG.md updated (if significant)
□ Issue updated with progress
□ Next steps documented
```

### Documentation Drift Warning

**Update docs BEFORE Claude gets confused.** Signs docs need updating:

| Warning Sign | Action |
|--------------|--------|
| Claude references wrong file paths | Update MASTER_INDEX.md, PROJECT_STRUCTURE.md |
| Claude uses old function names | Update relevant component docs |
| Claude applies outdated rules | Update CLAUDE.md, MASTER_RULES.md |
| Claude forgets recent architecture changes | Update ETL_ARCHITECTURE.md or similar |
| Claude suggests deprecated patterns | Update code walkthrough docs |

**When to proactively update docs:**
- After renaming/moving files
- After changing architecture
- After adding new skills/agents
- After modifying key workflows
- When docs reference line numbers that changed

**Quick doc sync:**
```bash
# Run doc-sync skill
/doc-sync

# Or manually check for stale references
grep -r "base_etl.py:4400" docs/  # Find outdated line refs
grep -r "v27.0" docs/             # Find old version refs
```

---

## Anti-Patterns to Avoid

1. **Working without issues** - Always have a GitHub issue
2. **Skipping PRDs for P0 work** - PRD prevents rework
3. **Fixing multiple issues in one PR** - Harder to review/revert
4. **Marking issues done without validation** - Trust but verify
5. **Creating future phase issues too early** - They become stale
6. **Ignoring documentation updates** - Docs drift from code
7. **Not creating prevention issues** - Same bugs repeat
8. **Skipping /post-code** - Problems slip through
9. **Working in wrong environment** - Always check env status
10. **Long sessions without commits** - Lose work, fill context

---

## Integration with Other Skills

After `/pm`:
- `/mentor` - For best practice guidance
- `/post-code` - After implementing
- `/validate` - For ETL validation
- `/reality-check` - For completion verification

---

## Notes

- This skill is for guidance, not enforcement
- Use judgment - rules have exceptions
- The goal is quality, not bureaucracy
- When in doubt, ask the user
