---
name: github-workflow
description: Complete GitHub workflow from issue selection to commit. Use when starting work, creating branches, or managing the full development cycle.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
argument-hint: [issue-number | next | status | branch | commit | pr]
---

# GitHub Workflow Skill

Complete development workflow from issue selection through commit and PR.

## Invocation

```
/github-workflow              # Show current status and next steps
/github-workflow next         # Get next priority issue and create branch
/github-workflow issue 31     # Start working on specific issue
/github-workflow branch       # Create branch for current issue
/github-workflow commit       # Validate and commit current work
/github-workflow pr           # Create PR for current branch
/github-workflow status       # Show current branch/issue status
```

---

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE GITHUB WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ PHASE 1: ISSUE SELECTION                                            │   │
│  │                                                                     │   │
│  │  /github-workflow next                                              │   │
│  │      │                                                              │   │
│  │      ├── 1. Query P0 issues in current phase                        │   │
│  │      │      gh issue list --label "priority:p0,phase:2" --state open│   │
│  │      │                                                              │   │
│  │      ├── 2. Check dependencies (Depends On in issue body)           │   │
│  │      │      Skip issues with open dependencies                      │   │
│  │      │                                                              │   │
│  │      ├── 3. Select highest priority unblocked issue                 │   │
│  │      │                                                              │   │
│  │      └── 4. Display issue details and ask for confirmation          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ PHASE 2: BRANCH CREATION                                            │   │
│  │                                                                     │   │
│  │  /github-workflow branch (auto-runs after issue selection)          │   │
│  │      │                                                              │   │
│  │      ├── 1. Checkout develop and pull latest                        │   │
│  │      │      git checkout develop && git pull                        │   │
│  │      │                                                              │   │
│  │      ├── 2. Determine branch type from issue labels                 │   │
│  │      │      type:fix → fix/                                         │   │
│  │      │      type:feature → feature/                                 │   │
│  │      │      type:refactor → refactor/                               │   │
│  │      │      type:perf → perf/                                       │   │
│  │      │      type:test → test/                                       │   │
│  │      │      type:docs → docs/                                       │   │
│  │      │                                                              │   │
│  │      ├── 3. Create branch with descriptive name                     │   │
│  │      │      git checkout -b {type}/{short-description}              │   │
│  │      │                                                              │   │
│  │      └── 4. Update issue with "In Progress" comment                 │   │
│  │             gh issue comment N --body "🚧 Started work on branch X" │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ PHASE 3: IMPLEMENTATION                                             │   │
│  │                                                                     │   │
│  │  [User works with Claude to implement the issue]                    │   │
│  │      │                                                              │   │
│  │      ├── Read acceptance criteria from issue                        │   │
│  │      ├── Review related PRD if exists                               │   │
│  │      ├── Implement changes                                          │   │
│  │      ├── Write tests if applicable                                  │   │
│  │      └── Make incremental commits                                   │   │
│  │                                                                     │   │
│  │  During implementation, use:                                        │   │
│  │      /mentor          → Best practice guidance                      │   │
│  │      /hockey-stats    → If calculation changes                      │   │
│  │      /validate        → If ETL changes                              │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ PHASE 4: VALIDATION & COMMIT                                        │   │
│  │                                                                     │   │
│  │  /github-workflow commit (runs /post-code internally)               │   │
│  │      │                                                              │   │
│  │      ├── 1. Run /post-code validation                               │   │
│  │      │      ├── Build check                                         │   │
│  │      │      ├── CLAUDE.md compliance                                │   │
│  │      │      ├── Tests (pytest, npm test)                            │   │
│  │      │      ├── Specialist review (if needed)                       │   │
│  │      │      ├── Quality check                                       │   │
│  │      │      ├── Completion validation                               │   │
│  │      │      ├── Reality check (Karen)                               │   │
│  │      │      └── Doc sync                                            │   │
│  │      │                                                              │   │
│  │      ├── 2. Stage changes                                           │   │
│  │      │      git add -A                                              │   │
│  │      │                                                              │   │
│  │      ├── 3. Generate commit message from issue                      │   │
│  │      │      [TYPE] Description (#issue-number)                      │   │
│  │      │                                                              │   │
│  │      ├── 4. Commit with Co-Author                                   │   │
│  │      │      git commit -m "..." --trailer "Co-Authored-By: ..."     │   │
│  │      │                                                              │   │
│  │      └── 5. Update issue with progress                              │   │
│  │             gh issue comment N --body "✅ Committed: [summary]"     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ PHASE 5: PUSH & PR                                                  │   │
│  │                                                                     │   │
│  │  /github-workflow pr                                                │   │
│  │      │                                                              │   │
│  │      ├── 1. Push branch to remote                                   │   │
│  │      │      git push -u origin {branch-name}                        │   │
│  │      │                                                              │   │
│  │      ├── 2. Create PR with template                                 │   │
│  │      │      gh pr create --title "[TYPE] Title" --body "..."        │   │
│  │      │      Body includes:                                          │   │
│  │      │        - Summary                                             │   │
│  │      │        - Changes made                                        │   │
│  │      │        - Testing performed                                   │   │
│  │      │        - Closes #N                                           │   │
│  │      │                                                              │   │
│  │      ├── 3. Wait for CodeRabbit review                              │   │
│  │      │                                                              │   │
│  │      ├── 4. Address feedback if needed                              │   │
│  │      │      git add . && git commit --amend && git push --force     │   │
│  │      │                                                              │   │
│  │      └── 5. Merge when approved                                     │   │
│  │             gh pr merge --squash --delete-branch                    │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ PHASE 6: CLEANUP & NEXT                                             │   │
│  │                                                                     │   │
│  │  After merge:                                                       │   │
│  │      │                                                              │   │
│  │      ├── 1. Return to develop                                       │   │
│  │      │      git checkout develop && git pull                        │   │
│  │      │                                                              │   │
│  │      ├── 2. Issue auto-closed by "Closes #N" in PR                  │   │
│  │      │                                                              │   │
│  │      ├── 3. Run /pm improve                                         │   │
│  │      │      Check for process improvements                          │   │
│  │      │                                                              │   │
│  │      └── 4. Run /github-workflow next                               │   │
│  │             Start next issue                                        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Commands

### `/github-workflow next` - Get Next Issue

```bash
# 1. Get P0 issues in current phase
gh issue list --label "priority:p0,phase:2" --state open --json number,title,body,labels

# 2. Check for unblocked issues (no open dependencies)
# Parse "Depends On: #X" from body, check if #X is closed

# 3. Display recommended issue
echo "Recommended: #31 - Investigate missing 7 tables"
echo "Priority: P0"
echo "Depends On: None (unblocked)"

# 4. Ask user to confirm
# "Start working on this issue? (y/n)"
```

### `/github-workflow issue N` - Start Specific Issue

```bash
# 1. Get issue details
gh issue view N --json number,title,body,labels

# 2. Check dependencies
# If blocked, warn user

# 3. Create branch
git checkout develop && git pull
git checkout -b {type}/{description}

# 4. Update issue
gh issue comment N --body "🚧 Started work

Branch: \`{branch-name}\`
Started: $(date)"
```

### `/github-workflow status` - Current Status

```bash
# Show current branch
git branch --show-current

# Show staged/unstaged changes
git status --short

# Show related issue (if branch follows naming convention)
# Parse issue number from branch name or commit messages

# Show validation status
echo "Last validation: [timestamp]"
echo "Tests: ✅ passing"
```

### `/github-workflow commit` - Validate and Commit

```bash
# 1. Run full validation
/post-code

# 2. If validation passes, stage changes
git add -A

# 3. Show diff summary
git diff --cached --stat

# 4. Generate commit message
# [TYPE] Description (#N)
#
# - Change 1
# - Change 2
#
# Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

# 5. Update version/changelog/logs (REQUIRED)
#    See "Version & Log Updates" section below

# 6. Commit
git commit -m "$(cat <<'EOF'
[TYPE] Description (#N)

- Change 1
- Change 2

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"

# 7. Update issue
gh issue comment N --body "✅ Committed: [summary]

Changes:
- [list changes]

Validation: All checks passed"
```

---

## Version & Log Updates (REQUIRED at Each Commit)

Every commit must update these files:

### 1. Component Log (`logs/{component}.log.md`)

Determine which component(s) changed and update the corresponding log:

| Changes In | Update Log |
|------------|------------|
| `src/`, `run_etl.py` | `logs/etl.log.md` |
| `ui/dashboard/` | `logs/dashboard.log.md` |
| `ui/tracker/` | `logs/tracker.log.md` |
| `ui/portal/` | `logs/portal.log.md` |
| `sql/`, Supabase migrations | `logs/supabase.log.md` |
| `api/` | `logs/api.log.md` |

**Entry format:**
```markdown
## YYYY-MM-DD - Brief Title

**Issue:** #N
**Type:** FEAT | FIX | REFACTOR | DOCS | CHORE

### Changes
- What changed

### Why
- Reasoning
```

### 2. CHANGELOG.md (for significant changes)

Add to `[Unreleased]` section for:
- New features (FEAT)
- Bug fixes (FIX)
- Breaking changes
- Performance improvements

Skip for: typo fixes, minor docs, internal refactors

### 3. VERSION.txt (for version bumps only)

Update when:
- Releasing to production
- Milestone completion
- Breaking changes

Format: `MAJOR.MINOR.PATCH-prerelease`
- `alpha.N` - Development builds
- `beta.N` - Testing builds
- `rc.N` - Release candidates

### `/github-workflow pr` - Create Pull Request

```bash
# 1. Push branch
git push -u origin $(git branch --show-current)

# 2. Create PR
gh pr create --title "[TYPE] Title (#N)" --body "$(cat <<'EOF'
## Summary
Brief description of changes.

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing Performed
- [x] pytest passes
- [x] ETL validation passes
- [x] /post-code completed

## Checklist
- [x] Code follows CLAUDE.md rules
- [x] No .iterrows() usage
- [x] Tests added/updated
- [x] Documentation updated

Closes #N

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
)"

# 3. Show PR URL
echo "PR created: https://github.com/..."
echo "Waiting for CodeRabbit review..."
```

---

## Branch Naming Convention

| Issue Label | Branch Prefix | Example |
|-------------|---------------|---------|
| `type:feature` | `feature/` | `feature/dashboard-xg-page` |
| `type:fix` | `fix/` | `fix/goal-counting-filter` |
| `type:refactor` | `refactor/` | `refactor/etl-modularization` |
| `type:perf` | `perf/` | `perf/vectorize-iterrows` |
| `type:test` | `test/` | `test/table-verification` |
| `type:docs` | `docs/` | `docs/api-reference` |
| `type:chore` | `chore/` | `chore/update-dependencies` |

---

## Commit Message Format

```
[TYPE] Brief description (#issue-number)

- Detail 1
- Detail 2
- Detail 3

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**Types:** FEAT, FIX, REFACTOR, PERF, TEST, DOCS, CHORE

---

## Integration with Other Skills

| Phase | Skills Used |
|-------|-------------|
| Issue Selection | `/pm prioritize` |
| Implementation | `/mentor`, `/hockey-stats`, `/validate` |
| Validation | `/post-code` |
| Commit | `/post-code commit` |
| PR | `/pr-workflow` |
| After Merge | `/pm improve`, `/pm next` |

---

### `/github-workflow merge` - Merge PR and Cleanup

```bash
# 1. Final validation before merge
echo "Running final validation..."
/post-code

# 2. Check PR status
gh pr status

# 3. Check CI status
gh pr checks

# 4. If all checks pass, merge
gh pr merge --squash --delete-branch

# 5. Return to develop
git checkout develop
git pull

# 6. Verify issue is closed
gh issue view N --json state

# 7. Run continuous improvement
/pm improve

# 8. Show next issue
echo "Ready for next issue. Run /github-workflow next"
```

---

## Full Workflow Quick Reference

```bash
# ══════════════════════════════════════════════════════════
# START OF DAY
# ══════════════════════════════════════════════════════════
/github-workflow next           # Get next priority issue

# ══════════════════════════════════════════════════════════
# DURING IMPLEMENTATION
# ══════════════════════════════════════════════════════════
/mentor                         # Best practices guidance
/post-code quick                # Quick validation check
/hockey-stats                   # If calculation changes
/validate                       # If ETL changes

# ══════════════════════════════════════════════════════════
# READY TO COMMIT
# ══════════════════════════════════════════════════════════
/github-workflow commit         # Full validation + commit

# ══════════════════════════════════════════════════════════
# READY FOR PR
# ══════════════════════════════════════════════════════════
/github-workflow pr             # Push + create PR

# ══════════════════════════════════════════════════════════
# AFTER CODERABBIT APPROVAL
# ══════════════════════════════════════════════════════════
/github-workflow merge          # Final test + merge + cleanup

# ══════════════════════════════════════════════════════════
# NEXT ISSUE
# ══════════════════════════════════════════════════════════
/github-workflow next           # Start next issue
```

---

## Environment Management

### Dev vs Prod Environments

| Environment | Supabase | Vercel | When to Use |
|-------------|----------|--------|-------------|
| **Development** | `amuisqvhhiigxetsfame` | Preview | All development, testing, PR previews |
| **Production** | `uuaowslhpgyiudmbvqze` | Production | Final release deployments only |

### Environment Check Before Merge

**CRITICAL:** Before merging to `main`, verify:

```bash
# 1. Check current environment
./benchsight.sh env status

# 2. Ensure on development
./benchsight.sh env switch dev  # Should already be dev

# 3. Verify changes work in dev environment
./benchsight.sh etl run
./benchsight.sh etl validate

# 4. Only merge to main goes to production
# PR to develop → dev Vercel preview
# PR to main → production Vercel deployment
```

### Merge Target Rules

| From Branch | Merge To | Environment | Requires |
|-------------|----------|-------------|----------|
| `feature/*`, `fix/*` | `develop` | Dev preview | CodeRabbit approval |
| `develop` | `main` | Production | Full validation + explicit approval |

**NEVER merge directly to `main`** - always go through `develop` first.

### Environment Switch Commands

```bash
./benchsight.sh env switch dev        # Switch to development (default)
./benchsight.sh env switch production # Switch to production (careful!)
./benchsight.sh env status            # Show current environment
```

---

## Context & Token Management

### Monitor Context Usage

Watch for these signs you're running low on context:

1. **Responses getting shorter** or less detailed
2. **Forgetting earlier conversation** parts
3. **Repeating questions** already answered
4. **Token counter** in Claude Code status bar

### When to Start Fresh Session

Start a new conversation when:
- **Context >75% full** - proactive switch
- **Completing a major milestone** - clean slate
- **Switching to different issue** - fresh context
- **After merge** - new task = new session

### Context Efficiency Tips

**DO:**
```
- Keep issue number handy (Claude can fetch details)
- Use specific file paths instead of searching
- Reference docs by path: "see docs/etl/CODE_FLOW_ETL.md"
- Commit often (smaller diffs to review)
- Use /post-code quick for minor changes
```

**DON'T:**
```
- Paste entire files when editing small sections
- Ask open-ended exploration questions
- Request full code reviews (use agents)
- Repeat context from the issue
- Keep conversation going after major completion
```

### Session Handoff Checklist

Before ending a long session:

```
□ All work committed
□ Component log updated (logs/*.log.md)
□ CHANGELOG.md updated (if significant)
□ Issue updated with progress
□ Any blockers documented in issue
□ Next steps clear for new session
```

### Quick Session Summary

At end of session, note:
```markdown
## Session Summary - YYYY-MM-DD

**Issue:** #N
**Branch:** feature/x

### Completed
- [what was done]

### In Progress
- [what's partially done]

### Next Steps
- [what to do next session]

### Blockers
- [any blockers]
```

---

## Guardrails & Reminders

### Automatic Commit Prompts

The workflow will prompt you to commit when:
- **3+ files changed** without a commit
- **30+ minutes elapsed** since last commit
- **Logical checkpoint reached** (phase complete, feature working)
- **Before switching context** (different issue, break, etc.)

### Stay On Task Checklist

Before ANY action, verify:
```
□ Am I working on the current issue? (check branch name)
□ Is this change in scope for the issue?
□ Have I committed recent work?
□ Am I following CLAUDE.md rules?
```

### Token Efficiency Rules

**DO:**
- Use `/post-code quick` for minor changes (saves tokens)
- Commit frequently (smaller context per commit)
- Use specific agents only when needed
- Reference issue number (Claude can fetch details)

**DON'T:**
- Run full `/post-code` for typo fixes
- Ask open-ended exploration questions
- Repeat context that's in the issue
- Request validation for uncommitted exploratory code

### Mid-Task Commit Points

Commit when you complete ANY of these:
```
✓ Single function implemented and working
✓ Test written and passing
✓ Bug fixed and verified
✓ Refactor complete (code still works)
✓ Documentation section written
✓ Configuration change tested
```

**Rule:** If you'd be upset losing it, commit it.

### Scope Creep Prevention

If you think "while I'm here, I should also..."
```
1. STOP
2. Is it in the current issue?
   - YES → Do it
   - NO → Create new issue, continue current work
3. Never expand scope mid-implementation
```

---

## Example Session

```
User: /github-workflow next

Claude: Checking P0 issues in Phase 2...

Found 7 P0 issues. Checking dependencies...

✅ RECOMMENDED ISSUE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#31 - Investigate missing 7 tables (132 vs 139)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Priority: P0 (Critical)
Execution Order: 1 (DO FIRST)
Depends On: None ✓
Milestone: M1: MVP Foundation

Acceptance Criteria:
- [ ] Identify all 7 missing tables by name
- [ ] Determine why each is missing
- [ ] Update table manifest

Start working on this issue?

User: yes

Claude: Creating branch...

✅ Branch created: fix/missing-tables-investigation
✅ Issue #31 updated with start comment

Ready to implement. The issue acceptance criteria are:
1. Identify all 7 missing tables by name
2. Determine why each is missing
3. Update table manifest

Let me start by comparing the manifest to actual output...
```
