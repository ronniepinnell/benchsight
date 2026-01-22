# BenchSight Complete Development Guide

**Everything you need: Issue → Branch → Claude → Commit → PR → Merge**

Last Updated: 2026-01-21

---

## Table of Contents

1. [Quick Start Checklist](#quick-start-checklist)
2. [The Complete Workflow](#the-complete-workflow)
3. [Step 1: Pick an Issue](#step-1-pick-an-issue)
4. [Step 2: Create Branch](#step-2-create-branch)
5. [Step 3: Work with Claude](#step-3-work-with-claude)
6. [Step 4: Commit Changes](#step-4-commit-changes)
7. [Step 5: Push & Create PR](#step-5-push--create-pr)
8. [Step 6: CodeRabbit Review](#step-6-coderabbit-review)
9. [Step 7: Merge](#step-7-merge)
10. [Commands Reference](#commands-reference)
11. [Claude Prompt Templates](#claude-prompt-templates)
12. [Critical Rules](#critical-rules)
13. [Troubleshooting](#troubleshooting)

---

## Quick Start Checklist

### First Time Setup

```bash
# 1. Authenticate GitHub CLI
gh auth login

# 2. Create GitHub labels and issues
./scripts/create-github-issues.sh

# 3. Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Daily Startup

```bash
./scripts/daily-start.sh
# OR manually:
git checkout develop && git pull
./benchsight.sh env switch dev
./benchsight.sh dashboard dev  # Terminal 1
```

---

## The Complete Workflow

### Visual Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. PICK ISSUE        gh issue view 1                           │
│         ↓                                                       │
│  2. CREATE BRANCH     ./scripts/create-feature.sh type name     │
│         ↓                                                       │
│  3. WORK WITH CLAUDE  Give context, implement, test             │
│         ↓                                                       │
│  4. COMMIT            git add . && git commit -m "[TYPE] msg"   │
│         ↓                                                       │
│  5. PUSH & PR         git push && gh pr create                  │
│         ↓                                                       │
│  6. CODERABBIT        Address feedback, push fixes              │
│         ↓                                                       │
│  7. MERGE             gh pr merge --squash --delete-branch      │
│         ↓                                                       │
│  BACK TO DEVELOP      git checkout develop && git pull          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Principle: One Issue = One Branch = One PR

```
Issue #1 ──→ branch: refactor/etl-modularization ──→ PR #1 ──→ merged to develop
Issue #2 ──→ branch: perf/etl-vectorization ──→ PR #2 ──→ merged to develop
Issue #3 ──→ branch: test/table-verification ──→ PR #3 ──→ merged to develop
```

### Why Not Commit Directly to Develop?

- **No review** - Skips CodeRabbit and human review
- **No isolation** - Broken code goes straight to develop
- **No history** - Can't easily revert one feature
- **Team conflict** - Others pulling develop get your WIP

Your changes get to develop **only via PR merge**.

---

## Step 1: Pick an Issue

### View Available Issues

```bash
# List all issues
gh issue list

# Filter by current phase
gh issue list --label "phase:2"

# Filter by priority
gh issue list --label "priority:p0"

# View specific issue
gh issue view 1
```

### Issue Labels

**Priority:**
- `priority:p0` - Critical/blocking (do first)
- `priority:p1` - High priority
- `priority:p2` - Medium priority
- `priority:p3` - Low priority

**Phase:**
- `phase:2` - ETL Optimization (CURRENT)
- `phase:3` - Dashboard Enhancement
- `phase:4` - Portal Development

**Type:**
- `type:feature` - New functionality
- `type:fix` - Bug fix
- `type:refactor` - Code restructuring
- `type:perf` - Performance improvement
- `type:test` - Testing
- `type:docs` - Documentation

---

## Step 2: Create Branch

### Using the Helper Script (Recommended)

```bash
# Feature
./scripts/create-feature.sh feature dashboard-xg-page

# Bug fix
./scripts/create-feature.sh fix etl-goal-counting

# Refactor
./scripts/create-feature.sh refactor etl-modularization

# Performance
./scripts/create-feature.sh perf etl-vectorization

# Documentation
./scripts/create-feature.sh docs api-reference
```

The script automatically:
1. Checks out develop
2. Pulls latest
3. Creates your branch

### Manual Method

```bash
git checkout develop
git pull origin develop
git checkout -b refactor/etl-modularization
```

### Branch Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/{component}-{description}` | `feature/dashboard-xg-analysis` |
| Bug fix | `fix/{component}-{description}` | `fix/etl-goal-counting` |
| Refactor | `refactor/{component}-{description}` | `refactor/etl-modularization` |
| Performance | `perf/{component}-{description}` | `perf/etl-vectorization` |
| Docs | `docs/{description}` | `docs/api-reference` |
| Test | `test/{description}` | `test/table-verification` |

---

## Step 3: Work with Claude

### Starting a Session: Give Context

Always start by giving Claude the issue context:

```
I'm working on Issue #1: ETL-001 Modularize base_etl.py

Context:
- Branch: refactor/etl-modularization
- Goal: Split src/core/base_etl.py (4,400 lines) into smaller modules
- Acceptance criteria:
  - Create src/core/etl_phases/ directory
  - Extract Phase 1 logic → phase1_blb_loader.py
  - Extract Phase 3 logic → phase3_tracking_processor.py
  - All 139 tables still generated
  - All tests pass

Start by analyzing base_etl.py and creating an implementation plan.
```

### Claude's Agents

Claude automatically uses specialized agents based on your request:

| Task | Agent | Triggered By |
|------|-------|--------------|
| Exploring codebase | `Explore` | "analyze", "find", "understand the code" |
| Planning | `Plan` | "plan", "design", "create approach" |
| Code review | `code-reviewer` | "review this code" |
| Testing | `test-automator` | "write tests", "test this" |
| Performance | `performance-engineer` | "optimize", "profile" |
| Debugging | `debugger` | "debug", "fix this error" |

### Explicit Agent Requests (Optional)

```
Use the Explore agent to find all .iterrows() usage in src/.

Use the Plan agent to design the module structure.

Use the code-reviewer agent to review my changes.
```

### Working Session Example

```
SESSION START
─────────────────────────────────────────────────────────────────

PROMPT 1: Set Context
─────────────────────
I'm starting Issue #1: ETL-001 Modularize base_etl.py
Branch: refactor/etl-modularization

First, analyze base_etl.py and show me the logical sections
that could become separate modules.

[Claude explores and shows analysis]

─────────────────────────────────────────────────────────────────

PROMPT 2: Plan
──────────────
Create an implementation plan with specific files and functions
to extract.

[Claude creates plan]

─────────────────────────────────────────────────────────────────

PROMPT 3: Implement
───────────────────
Implement phase1_blb_loader.py with the BLB loading logic.
Update base_etl.py to import from it.

Follow BenchSight rules:
- No .iterrows()
- Type hints required
- Docstrings required

[Claude implements]

─────────────────────────────────────────────────────────────────

PROMPT 4: Test
──────────────
Run the ETL to verify it still works:
./benchsight.sh etl run

[Claude runs ETL]

─────────────────────────────────────────────────────────────────

PROMPT 5: Validate
──────────────────
Run tests:
pytest tests/test_etl.py

[Claude runs tests]

─────────────────────────────────────────────────────────────────

PROMPT 6: Review
────────────────
Review my changes against the acceptance criteria for issue #1.
Am I ready to create a PR?

[Claude reviews]

─────────────────────────────────────────────────────────────────
SESSION END - Ready to commit/push/PR
```

### Prompt Templates by Phase

**Planning:**
```
Analyze [file/component] and create an implementation plan for [issue].
Consider dependencies and risks.
```

**Implementation:**
```
Implement [feature/fix] following BenchSight rules:
- Goals: event_type == 'Goal' AND event_detail == 'Goal_Scored'
- No .iterrows() - use vectorized operations
- Type hints required

Key files: [list relevant files]
```

**Testing:**
```
Run tests and validate the changes:
- pytest [specific test file]
- ./benchsight.sh etl validate
Verify no regressions.
```

**Review:**
```
Review my changes for:
- BenchSight coding standards (MASTER_RULES.md)
- Acceptance criteria from issue #X
- Potential issues before PR
```

---

## Step 4: Commit Changes

### Commit to Your Feature Branch (Not Develop!)

```bash
# Check you're on the right branch
git branch
# * refactor/etl-modularization  <-- should see your branch

# Stage changes
git add .

# Commit with proper message
git commit -m "[REFACTOR] Extract Phase 1 to separate module"
```

### Commit Often

```bash
# First piece of work
git add .
git commit -m "[REFACTOR] Create etl_phases directory structure"

# Second piece
git add .
git commit -m "[REFACTOR] Extract Phase 1 BLB loading logic"

# Third piece
git add .
git commit -m "[REFACTOR] Extract validation logic"

# Fourth piece
git add .
git commit -m "[TEST] Verify all 139 tables still generated"
```

### Commit Message Format

```
[TYPE] Brief description (#issue-number)

- Detail 1
- Detail 2
- Detail 3
```

**Types:**

| Type | When to Use |
|------|-------------|
| `FEAT` | New feature |
| `FIX` | Bug fix |
| `REFACTOR` | Code restructuring (no behavior change) |
| `PERF` | Performance improvement |
| `DOCS` | Documentation only |
| `TEST` | Tests only |
| `CHORE` | Maintenance, deps, config |

**Examples:**

```bash
# Feature
git commit -m "[FEAT] Add xG analysis page (#45)

- Create XGAnalysis component
- Add xG vs goals comparison chart
- Update dashboard navigation"

# Bug fix
git commit -m "[FIX] Correct goal counting filter (#42)

- Use GOAL_FILTER pattern
- Add regression test
- Verify against official scores"

# Refactor
git commit -m "[REFACTOR] Modularize base_etl.py (#1)

- Extract Phase 1 to phase1_blb_loader.py
- Extract validation to validation.py
- Reduce base_etl.py to orchestration only"

# Performance
git commit -m "[PERF] Replace .iterrows() with vectorized ops (#3)

- Convert player stats loop to groupby
- 40% performance improvement
- Data integrity verified"
```

---

## Step 5: Push & Create PR

### Push Your Branch

```bash
# First push (sets upstream)
git push -u origin refactor/etl-modularization

# Subsequent pushes
git push
```

### Create Pull Request

**Using GitHub CLI (Recommended):**

```bash
# Interactive (prompts for title/body)
gh pr create

# One-liner with issue link
gh pr create --title "[REFACTOR] ETL-001: Modularize base_etl.py" --body "Closes #1"

# With full body
gh pr create --title "[REFACTOR] ETL-001: Modularize base_etl.py" --body "## Summary
Splits base_etl.py into smaller modules for maintainability.

## Changes
- Created src/core/etl_phases/ directory
- Extracted Phase 1 logic to phase1_blb_loader.py
- Extracted validation to validation.py

## Testing
- All 139 tables still generated
- pytest passes

Closes #1"
```

**The `Closes #1` automatically:**
- Links PR to issue #1
- Closes issue #1 when PR is merged

### PR Template

The PR template (`.github/PULL_REQUEST_TEMPLATE/`) auto-populates with a checklist:

```markdown
## Summary
[Brief description]

## Type of Change
- [x] `REFACTOR` - Code restructuring

## Related Issues
Closes #1

## Changes Made
- Change 1
- Change 2

## Testing Performed
- [x] ETL validation passed
- [x] pytest passes
- [x] No regressions

## Checklist
- [x] Code follows MASTER_RULES.md
- [x] No .iterrows() usage
- [x] Tests pass
```

---

## Step 6: CodeRabbit Review

### Automatic Review

CodeRabbit automatically reviews your PR within minutes.

### Feedback Types

| Icon | Type | Action |
|------|------|--------|
| 🔴 | Error | Must fix |
| 🟡 | Warning | Should fix |
| 🔵 | Suggestion | Consider |

### BenchSight-Specific Checks

CodeRabbit is configured to flag:

1. **Goal Counting Violations** (Error)
   - Must use: `event_type == 'Goal' AND event_detail == 'Goal_Scored'`

2. **`.iterrows()` Usage** (Error)
   - Must use vectorized pandas operations

3. **Missing Type Hints** (Warning)
   - Functions should have type hints

4. **Stat Counting Issues** (Warning)
   - Only count for `player_role == 'event_player_1'`

### Addressing Feedback

**Option 1: Fix It**
```bash
# Make the fix
git add .
git commit -m "[FIX] Address CodeRabbit feedback"
git push
```

**Option 2: Explain**
- Reply to the CodeRabbit comment
- Explain why you're keeping it as-is

**Option 3: Dismiss (Rare)**
- Only if truly not applicable
- Add a note explaining why

---

## Step 7: Merge

### After Approval

```bash
# Merge with squash (combines all commits into one)
gh pr merge --squash --delete-branch
```

### What Squash Does

```
Your branch:     A ── B ── C ── D (4 commits)
                            ↓
                       [squash merge]
                            ↓
Develop:        ─────────── ABCD (1 commit)
```

### Return to Develop

```bash
git checkout develop
git pull
# Your changes are now in develop!
```

### Full Merge Flow

```bash
# 1. Merge PR
gh pr merge --squash --delete-branch

# 2. Switch to develop
git checkout develop

# 3. Pull latest (includes your merged changes)
git pull

# 4. Clean up local branch (if not auto-deleted)
git branch -d refactor/etl-modularization

# 5. Ready for next issue!
gh issue list --label "phase:2"
```

---

## Commands Reference

### Daily Workflow

```bash
# Start day
./scripts/daily-start.sh

# Pick issue
gh issue list --label "phase:2"
gh issue view 1

# Create branch
./scripts/create-feature.sh refactor etl-modularization

# Work with Claude...

# Commit
git add .
git commit -m "[TYPE] Message"

# Push & PR
git push -u origin branch-name
gh pr create --body "Closes #1"

# After approval
gh pr merge --squash --delete-branch
git checkout develop && git pull
```

### Git Commands

```bash
# Branch
git branch                      # List branches
git checkout -b branch-name     # Create branch
git checkout develop            # Switch branch

# Commit
git status                      # Check status
git add .                       # Stage all
git add file.py                 # Stage specific
git commit -m "message"         # Commit

# Push
git push -u origin branch-name  # First push
git push                        # Subsequent

# Pull
git pull                        # Pull current branch
git pull origin develop         # Pull develop
```

### GitHub CLI Commands

```bash
# Issues
gh issue list                   # List issues
gh issue list --label "phase:2" # Filter
gh issue view 1                 # View issue
gh issue create                 # Create issue

# Pull Requests
gh pr create                    # Create PR
gh pr list                      # List PRs
gh pr view                      # View current PR
gh pr view 1                    # View specific PR
gh pr merge --squash            # Merge with squash
gh pr merge --squash --delete-branch  # Merge + delete branch

# Navigation
gh browse                       # Open repo in browser
gh browse --issues              # Open issues
gh browse --pulls               # Open PRs
```

### Project Commands

```bash
# Status
./benchsight.sh status
./benchsight.sh env status

# ETL
./benchsight.sh etl run
./benchsight.sh etl validate

# Dashboard
./benchsight.sh dashboard dev

# Testing
pytest
pytest tests/test_goal_verification.py
```

---

## Claude Prompt Templates

### Starting Work on an Issue

```
I'm working on Issue #[NUMBER]: [TITLE]

Context:
- Branch: [branch-name]
- Goal: [brief goal]
- Acceptance criteria:
  - [criterion 1]
  - [criterion 2]

Start by [analyzing/planning/implementing].
```

### Implementation Request

```
Implement [feature] following BenchSight rules:
- Goals: event_type == 'Goal' AND event_detail == 'Goal_Scored'
- No .iterrows() - use vectorized operations
- Type hints required
- Docstrings required

Key files: [list files]
```

### Testing Request

```
Run tests and validate:
- pytest [test file]
- ./benchsight.sh etl validate

Verify no regressions and all acceptance criteria are met.
```

### Pre-PR Review Request

```
Review my changes for issue #[NUMBER]:
- Check against acceptance criteria
- Verify BenchSight coding standards
- Identify any issues before I create the PR
```

### Debugging

```
I'm getting this error:
[error message]

While working on:
[what you were doing]

Relevant code:
[paste snippet]
```

### Quick Prompts

| What You Want | Prompt |
|---------------|--------|
| Analyze code | "Analyze [file] and explain the structure" |
| Plan work | "Create an implementation plan for [issue]" |
| Write code | "Implement [feature] following BenchSight rules" |
| Run tests | "Run pytest and verify no regressions" |
| Validate ETL | "Run ./benchsight.sh etl validate" |
| Review | "Review my changes against acceptance criteria" |
| Find code | "Find all .iterrows() usage in src/" |

---

## Critical Rules

### Goal Counting (CRITICAL)

```python
# CORRECT - The ONLY valid pattern
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')

# WRONG - Never do this
wrong = df['event_type'] == 'Shot'  # with event_detail == 'Goal'
```

### No .iterrows()

```python
# WRONG
for idx, row in df.iterrows():
    process(row)

# CORRECT
result = df.groupby('player_id').apply(process_group)
# OR
result = df.apply(lambda row: process(row), axis=1)
```

### Stat Counting

```python
# Only count for event_player_1
stats = df[df['player_role'] == 'event_player_1']
```

### Assists

```python
# Only Primary and Secondary count
assist_mask = df['play_detail'].str.contains('AssistPrimary|AssistSecondary', na=False)
# Tertiary does NOT count
```

### Key Formatting

```python
# Standard: {XX}{ID}{5D}
game_key = f"GK{game_id:05d}"
player_key = f"PK{player_id:05d}"

# Multi-player: use underscore
line_key = f"LN_{player1_id}_{player2_id}_{player3_id}"
```

---

## Troubleshooting

### GitHub CLI Not Authenticated

```bash
gh auth login
```

### Wrong Branch

```bash
# Check current branch
git branch

# Switch to correct branch
git checkout refactor/etl-modularization

# Or start fresh
git checkout develop
git pull
./scripts/create-feature.sh refactor etl-modularization
```

### Forgot to Create Branch (Committed to Develop)

```bash
# Create branch from current state
git checkout -b refactor/etl-modularization

# Reset develop to remote
git checkout develop
git reset --hard origin/develop

# Continue work on feature branch
git checkout refactor/etl-modularization
```

### PR Conflicts

```bash
# Update your branch with latest develop
git checkout refactor/etl-modularization
git fetch origin
git merge origin/develop
# Resolve conflicts if any
git push
```

### CodeRabbit Not Reviewing

1. Check CodeRabbit app is installed on repo
2. Check PR is targeting develop (not main)
3. Try closing and reopening PR

### ETL Failing

```bash
# Check logs
tail -f logs/etl_v5.log

# Validate
./benchsight.sh etl validate

# Run specific tests
pytest tests/test_goal_verification.py -v
```

---

## File Locations

| Purpose | Location |
|---------|----------|
| This guide | `docs/workflows/COMPLETE_DEVELOPMENT_GUIDE.md` |
| Quick reference | `docs/workflows/DEVELOPMENT_REFERENCE.md` |
| Full workflow docs | `docs/workflows/WORKFLOW.md` |
| Issue backlog | `docs/GITHUB_ISSUES_BACKLOG.md` |
| Project rules | `docs/MASTER_RULES.md` |
| Critical rules | `CLAUDE.md` |
| CodeRabbit config | `.coderabbit.yaml` |
| Daily startup | `scripts/daily-start.sh` |
| Create branch | `scripts/create-feature.sh` |
| Create issues | `scripts/create-github-issues.sh` |

---

## Quick Copy-Paste Workflow

```bash
# === START WORK ON ISSUE ===
gh issue view 1
./scripts/create-feature.sh refactor etl-modularization

# === WORK WITH CLAUDE ===
# [Give Claude the issue context, implement, test]

# === COMMIT ===
git add .
git commit -m "[REFACTOR] Modularize base_etl.py (#1)

- Extract Phase 1 to phase1_blb_loader.py
- Extract validation to validation.py
- All tests pass"

# === CREATE PR ===
git push -u origin refactor/etl-modularization
gh pr create --title "[REFACTOR] ETL-001: Modularize base_etl.py" --body "Closes #1"

# === AFTER APPROVAL ===
gh pr merge --squash --delete-branch
git checkout develop && git pull

# === NEXT ISSUE ===
gh issue list --label "phase:2"
```

---

*Last Updated: 2026-01-21*
