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

### Branch Flow (CRITICAL)

```
feature/* or fix/*  →  develop  →  main
       ↑                  ↑          ↑
   (work here)       (staging)  (production)
```

**Always merge to `develop` first, NEVER directly to `main`.**

- `develop` is the staging/integration branch
- `main` is reserved for production releases only
- All PRs target `develop` by default

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

## Part 2: Creating and Using Hooks

### What Are Hooks?

Hooks are automatic triggers that run at specific lifecycle points in Claude Code. They can:
- **Block** dangerous operations
- **Warn** about risky actions
- **Remind** about best practices
- **Inject** context into conversations

### Hook Lifecycle Events

| Event | When | Use For |
|-------|------|---------|
| `PreToolUse` | Before tool executes | Validation, blocking, warnings |
| `PostToolUse` | After tool executes | Reminders, follow-up actions |
| `UserPromptSubmit` | When user sends message | Context injection |
| `SessionStart` | When session begins | Environment setup |
| `SessionEnd` | When session ends | Cleanup, logging |

### Hook File Structure

**Location:** `.claude/hooks/{hook-name}.py`

```python
#!/usr/bin/env python3
"""
Hook description - what this hook does.
"""
import json
import sys

# 1. Parse input from Claude Code
try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)  # Fail gracefully

# 2. Extract relevant data
tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input", {})
tool_result = data.get("tool_result", {})  # PostToolUse only

# 3. Your logic here
# Check conditions, make decisions

# 4. Output (choose ONE):

# Option A: Allow silently (no output, exit 0)
sys.exit(0)

# Option B: Block execution
print(json.dumps({
    "decision": "block",
    "reason": "Explanation of why blocked and what to do instead"
}))
sys.exit(0)

# Option C: Ask user confirmation
print(json.dumps({
    "decision": "ask",
    "reason": "Question to ask the user"
}))
sys.exit(0)

# Option D: Add context message
print(json.dumps({
    "message": "Information to display to Claude"
}))
sys.exit(0)
```

### Configuring Hooks in settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/my-hook.py\""
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/another-hook.py\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/post-hook.py\""
          }
        ]
      }
    ]
  }
}
```

**Matcher patterns:**
- `Bash` - Matches Bash tool only
- `Edit|Write` - Matches Edit OR Write tools
- `*` - Matches all tools (use sparingly)

### Example: Creating a Pre-Commit Reminder Hook

**1. Create the hook file (`.claude/hooks/pre-commit-reminder.py`):**

```python
#!/usr/bin/env python3
"""Remind to run tests before committing."""
import json
import sys

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

tool_name = data.get("tool_name", "")
command = data.get("tool_input", {}).get("command", "")

if tool_name == "Bash" and "git commit" in command:
    print(json.dumps({
        "message": """
COMMIT CHECKLIST:
- Have you run tests? (pytest / npm test)
- Have you run /post-code?
- Is documentation updated?
"""
    }))

sys.exit(0)
```

**2. Make executable:**
```bash
chmod +x .claude/hooks/pre-commit-reminder.py
```

**3. Add to settings.json hooks section.**

### Can Hooks Call Agents?

**Short answer: Not directly, but they can prompt for it.**

Hooks run synchronously during tool execution. They can:
- Output a message suggesting an agent be called
- Block an action until validation happens

**Recommended pattern:**

```python
# In your hook:
print(json.dumps({
    "message": """
ETL validation detected issues. Consider running:
- /validate to check data integrity
- @task-completion-validator to verify completion
"""
}))
```

**Why not direct agent calls?**
1. Hooks are synchronous - agent calls would block
2. Hooks have limited context compared to the main session
3. User should decide when to invoke agents

**Better alternative:** Create a skill that orchestrates multiple agents (like `/post-code`).

### Debugging Hooks

```bash
# Test hook with sample input
echo '{"tool_name":"Bash","tool_input":{"command":"git commit"}}' | \
  python3 .claude/hooks/pre-commit-reminder.py

# Check for Python errors
python3 -m py_compile .claude/hooks/my-hook.py
```

---

## Part 3: Creating and Using Skills

### What Are Skills?

Skills (slash commands) are custom workflows invoked with `/command-name`. They:
- Encapsulate complex multi-step workflows
- Have their own tool permissions
- Can accept arguments
- Can invoke agents

### Skill File Structure

**Location:** `.claude/skills/{skill-name}/SKILL.md`

```yaml
---
name: skill-name
description: When this skill should be used (for auto-selection)
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [optional args]
context: fork  # Optional: isolate context
agent: agent-name  # Optional: specific agent to use
---

# Skill Title

Description of what this skill does.

## Usage

\`\`\`bash
/skill-name [arguments]
\`\`\`

## What It Does

Step-by-step explanation.

## Task

$ARGUMENTS

Instructions for Claude to follow when this skill is invoked.
```

### Skill Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Command name (no slash) |
| `description` | Yes | When to use (for auto-selection) |
| `allowed-tools` | No | Comma-separated tool list |
| `argument-hint` | No | Help text for arguments |
| `context` | No | `fork` for isolated context |
| `agent` | No | Specific agent to invoke |

### Tool Permissions by Role

| Role | Tools |
|------|-------|
| Read-only (reviewers) | `Read, Grep, Glob` |
| Research (analysts) | `Read, Grep, Glob, WebFetch, WebSearch` |
| Code writers | `Read, Write, Edit, Bash, Glob, Grep` |
| Documentation | `Read, Write, Edit, Glob, Grep, WebFetch, WebSearch` |

### Example: Creating a `/test-coverage` Skill

**1. Create directory:**
```bash
mkdir -p .claude/skills/test-coverage
```

**2. Create SKILL.md:**

```yaml
---
name: test-coverage
description: Run tests and report coverage. Use after implementing features.
allowed-tools: Bash, Read, Glob
argument-hint: [module or path]
---

# Test Coverage

Run pytest with coverage reporting.

## Usage

\`\`\`bash
/test-coverage               # All tests
/test-coverage src/tables/   # Specific module
\`\`\`

## Task

$ARGUMENTS

Run test coverage analysis:

1. Run tests with coverage:
   \`\`\`bash
   pytest --cov=src --cov-report=term-missing $ARGUMENTS
   \`\`\`

2. Report:
   - Overall coverage percentage
   - Files with low coverage (<80%)

3. If coverage < 80%, warn about low coverage.
```

### Skills That Call Agents

Skills can orchestrate multiple agents. Example from `/post-code`:

```yaml
## Task

Run the complete post-code validation sequence:

1. **Build Check** - verify code compiles

2. **Task Completion Validation:**
   Use the Task tool to launch `task-completion-validator` agent:
   "Verify that the recent code changes actually work."

3. **Code Quality Check:**
   Use the Task tool to launch `code-quality-pragmatist` agent:
   "Review recent changes for over-engineering."

4. **Compliance Check:**
   Use the Task tool to launch `claude-md-compliance-checker` agent:
   "Verify recent changes follow CLAUDE.md guidelines."
```

---

## Part 4: Automatic Documentation Updates

### The Problem

Documentation becomes stale when:
- Code changes without doc updates
- New features are added
- APIs are modified

### Solution: Multi-Layer Automation

#### Layer 1: Pre-Commit Hook (Doc Reminder)

Create `.claude/hooks/doc-update-reminder.py`:

```python
#!/usr/bin/env python3
"""Remind to update docs when committing code changes."""
import json
import sys
import subprocess

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

tool_name = data.get("tool_name", "")
command = data.get("tool_input", {}).get("command", "")

if tool_name == "Bash" and "git commit" in command:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True
    )
    staged_files = result.stdout.strip().split('\n')

    code_changed = any(
        f.startswith(('src/', 'api/', 'ui/'))
        for f in staged_files if f
    )
    docs_changed = any(
        f.startswith('docs/') or f.endswith('.md')
        for f in staged_files if f
    )

    if code_changed and not docs_changed:
        print(json.dumps({
            "decision": "ask",
            "reason": """
Code changes detected but no documentation updates.

Consider updating:
- docs/etl/ (if ETL changes)
- docs/api/ (if API changes)
- docs/dashboard/ (if dashboard changes)

Continue without doc updates?
"""
        }))

sys.exit(0)
```

#### Layer 2: The `/doc-sync` Skill

Use the existing skill:
```bash
/doc-sync              # Check and update docs
/doc-sync check        # Check only
/doc-sync generate     # Generate from code
```

#### Layer 3: Post-Code Integration

The `/post-code` skill includes documentation sync as the final step.

#### Layer 4: CI Check (GitHub Actions)

The workflow at `.github/workflows/docs-check.yml` checks for doc updates on PRs.

### Documents That MUST Be Updated

| Code Change | Required Doc Update |
|-------------|---------------------|
| New ETL calculation | `docs/etl/calculations.md` |
| New API endpoint | `docs/api/endpoints.md` |
| New dashboard page | `docs/dashboard/pages.md` |
| Schema change | `docs/data/schema.md` |
| Status change | `docs/PROJECT_STATUS.md` |

---

## Part 5: Active Hooks Reference

| Hook | Trigger | Purpose |
|------|---------|---------|
| `bash-validator.py` | PreToolUse: Bash | Blocks dangerous commands |
| `goal-counting-guard.py` | PreToolUse: Edit/Write | Goal counting rule reminder |
| `post-etl-reminder.py` | PostToolUse: Bash | Validation reminder after ETL |
| `etl-failure-handler.py` | PostToolUse: Bash | Detects ETL failures, offers GitHub issue |
| `etl-integrity-check.py` | PostToolUse: Bash | Validates data integrity |

---

## Part 6: Available Skills Reference (26)

### Component Development
| Command | Purpose |
|---------|---------|
| `/dashboard-dev` | Start dashboard dev server |
| `/dashboard-deploy` | Deploy to Vercel |
| `/portal-dev` | Start portal development |
| `/tracker-dev` | Start tracker development |
| `/api-dev` | Start API server |
| `/etl` | Run ETL pipeline |
| `/validate` | Validate ETL output |
| `/etl-issue` | Create GitHub issue for ETL failure |

### Database & Environment
| Command | Purpose |
|---------|---------|
| `/db-dev` | Work with dev database |
| `/db-prod` | Work with prod database |
| `/env-switch` | Switch dev/prod |
| `/schema-design` | Design database schemas |

### Quality & Validation
| Command | Purpose |
|---------|---------|
| `/post-code` | Run full validation workflow (CRITICAL) |
| `/compliance-check` | Check CLAUDE.md rules |
| `/reality-check` | Call Karen agent |
| `/doc-sync` | Update documentation |
| `/pr-workflow` | Create validated PR |

### Analytics & Domain
| Command | Purpose |
|---------|---------|
| `/hockey-stats` | Hockey analytics SME |
| `/xg-model` | Expected goals model |
| `/ml-pipeline` | Machine learning work |
| `/cv-tracking` | Computer vision |

### Business & Strategy
| Command | Purpose |
|---------|---------|
| `/competitive-research` | Research competitors |
| `/ui-ux-design` | Design assistance |
| `/monetization` | Revenue planning |
| `/go-to-market` | Launch strategy |
| `/scale-architecture` | Scaling plans |

---

## File Locations Summary

```
.claude/
├── settings.json           # Hooks configuration
├── agents/                 # Agent definitions (8 project-specific)
├── skills/                 # Skill definitions (26 total)
│   ├── etl/SKILL.md
│   ├── validate/SKILL.md
│   ├── post-code/SKILL.md
│   ├── doc-sync/SKILL.md
│   └── ...
└── hooks/                  # Hook scripts (5 total)
    ├── bash-validator.py
    ├── goal-counting-guard.py
    ├── post-etl-reminder.py
    ├── etl-failure-handler.py
    └── etl-integrity-check.py
```

---

## Part 7: ETL Debug System with Local PostgreSQL

### Overview

The ETL Debug system enables phase-by-phase debugging with local PostgreSQL staging. This allows you to:
- Step through each ETL phase
- Inspect intermediate data at any stage
- Compare local results with production Supabase
- Resume from checkpoints after failures

**GitHub Issues:** #17-#23 track implementation

### Architecture: 4-Schema Design

| Schema | Purpose | When Populated |
|--------|---------|----------------|
| `raw` | Original source data | Phase 1 (BLB tables, tracking data) |
| `stage` | Intermediate transformations | Phases 2-4 (enhanced events/shifts) |
| `intermediate` | Calculation-ready data | Phases 5-9 (stats, analytics) |
| `datamart` | Final tables (mirrors Supabase) | Phases 10-11 (all dim_*, fact_*, qa_*) |

### Prerequisites

**Required:**
- Docker Desktop (for PostgreSQL container)
- Python 3.10+ with psycopg2
- Git

**Install Docker:**
```bash
# macOS
brew install --cask docker

# Ubuntu
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER  # Log out/in after this
```

**Install psycopg2:**
```bash
pip install psycopg2-binary
```

### Setup Instructions

#### Step 1: Create Docker Configuration

Create `docker/docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: benchsight-pg
    environment:
      POSTGRES_DB: benchsight
      POSTGRES_USER: benchsight
      POSTGRES_PASSWORD: benchsight_dev
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d

volumes:
  pg_data:
```

#### Step 2: Create Schema Initialization

Create `docker/init/01_schemas.sql`:
```sql
-- Create the 4-schema architecture
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS stage;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS datamart;

-- Grant access to benchsight user
GRANT ALL ON SCHEMA raw TO benchsight;
GRANT ALL ON SCHEMA stage TO benchsight;
GRANT ALL ON SCHEMA intermediate TO benchsight;
GRANT ALL ON SCHEMA datamart TO benchsight;

-- Set search path
ALTER DATABASE benchsight SET search_path TO datamart, intermediate, stage, raw, public;
```

Create `docker/init/02_functions.sql`:
```sql
-- Helper function: Get row counts for all tables in a schema
CREATE OR REPLACE FUNCTION get_table_counts(schema_name text)
RETURNS TABLE(table_name text, row_count bigint) AS $$
BEGIN
    RETURN QUERY
    SELECT t.tablename::text,
           (xpath('/row/cnt/text()',
                  query_to_xml(format('SELECT count(*) as cnt FROM %I.%I', schema_name, t.tablename), false, true, ''))
           )[1]::text::bigint
    FROM pg_tables t
    WHERE t.schemaname = schema_name;
END;
$$ LANGUAGE plpgsql;

-- Helper function: Compare two schemas
CREATE OR REPLACE FUNCTION compare_schemas(schema1 text, schema2 text)
RETURNS TABLE(table_name text, schema1_count bigint, schema2_count bigint, diff bigint) AS $$
BEGIN
    RETURN QUERY
    SELECT COALESCE(s1.table_name, s2.table_name),
           COALESCE(s1.row_count, 0),
           COALESCE(s2.row_count, 0),
           COALESCE(s1.row_count, 0) - COALESCE(s2.row_count, 0)
    FROM get_table_counts(schema1) s1
    FULL OUTER JOIN get_table_counts(schema2) s2 USING (table_name)
    WHERE COALESCE(s1.row_count, 0) != COALESCE(s2.row_count, 0);
END;
$$ LANGUAGE plpgsql;
```

#### Step 3: Create Debug Configuration

Create `config/debug_config.ini`:
```ini
[postgres]
host = localhost
port = 5432
database = benchsight
user = benchsight
password = benchsight_dev

[debug]
state_file = data/debug/.etl_state.json
snapshot_enabled = true
snapshot_dir = data/debug/snapshots

[comparison]
ignore_columns = created_at,updated_at
tolerance_pct = 0.01
```

#### Step 4: Create Debug Directory

```bash
mkdir -p data/debug/snapshots
```

### Usage

#### Start Local PostgreSQL

```bash
# Start container
./benchsight.sh debug start
# OR
docker-compose -f docker/docker-compose.yml up -d

# Verify it's running
docker ps | grep benchsight-pg

# Check schemas exist
./benchsight.sh debug shell
# In psql: \dn
# Should show: raw, stage, intermediate, datamart
```

#### Run ETL in Debug Mode

```bash
# Full debug run
./benchsight.sh debug run

# Run up to specific phase
./benchsight.sh debug run --to-phase 4B

# Step through interactively
./benchsight.sh debug run --step

# Resume from last checkpoint
./benchsight.sh debug resume
```

#### Inspect Data

```bash
# Open psql shell
./benchsight.sh debug shell

# List tables in a schema
./benchsight.sh debug tables raw
./benchsight.sh debug tables datamart

# Get row counts
./benchsight.sh debug counts

# Run ad-hoc query
./benchsight.sh debug query "SELECT COUNT(*) FROM datamart.fact_events"
```

#### Compare with Supabase

```bash
# Compare all tables
./benchsight.sh debug compare

# Compare specific table
./benchsight.sh debug diff fact_events

# Export local datamart to CSV
./benchsight.sh debug export
```

#### Stop/Reset

```bash
# Stop (preserves data)
./benchsight.sh debug stop

# Reset (deletes all data)
./benchsight.sh debug reset
```

### ETL Phase Reference

| Phase | Name | Target Schema | Key Tables |
|-------|------|---------------|------------|
| 1 | Base ETL | raw | blb_*, tracking_* |
| 3B | Static Dimensions | datamart | 52 dim_* tables |
| 4 | Core Player Stats | intermediate | player_game_stats, team_game_stats |
| 4B | Shift Analytics | intermediate | h2h, linemate, wowy, line_combos |
| 4C | Remaining Facts | datamart | fact_faceoffs, fact_penalties |
| 4D | Event Analytics | datamart | fact_rush_events, fact_linked_events |
| 4E | Shot Chains | datamart | fact_shot_chains |
| 5 | Foreign Keys | datamart | (adds FK columns) |
| 6-8 | Extended/Post | datamart | Extended analysis |
| 9 | QA Tables | datamart | qa_* tables |
| 10 | V11 Enhancements | datamart | Advanced features |
| 10B | XY Tables | datamart | Spatial analytics |
| 11 | Macro Stats | datamart | Season/career aggregations |

### State File

The debug system tracks progress in `data/debug/.etl_state.json`:

```json
{
  "run_id": "20260121_143000",
  "current_phase": "4B",
  "completed_phases": ["1", "3B", "4"],
  "phase_timestamps": {
    "1": {"start": "2026-01-21T14:30:00", "end": "2026-01-21T14:30:45", "tables": 15},
    "3B": {"start": "2026-01-21T14:30:46", "end": "2026-01-21T14:31:02", "tables": 52}
  },
  "errors": []
}
```

### Troubleshooting

**Docker not starting:**
```bash
# Check Docker daemon
docker info

# On macOS, ensure Docker Desktop is running
open -a Docker
```

**Connection refused:**
```bash
# Check container is running
docker ps

# Check port is available
lsof -i :5432

# Restart container
docker-compose -f docker/docker-compose.yml restart
```

**Schemas not created:**
```bash
# Manually run init scripts
docker exec -i benchsight-pg psql -U benchsight -d benchsight < docker/init/01_schemas.sql
```

**Permission denied:**
```bash
# On Linux, add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### Implementation Status

| Issue | Component | Status |
|-------|-----------|--------|
| #17 | Docker Infrastructure | Not started |
| #18 | PostgreSQL Manager | Not started |
| #19 | State Manager | Not started |
| #20 | Phase Executor | Not started |
| #21 | Data Comparator | Not started |
| #22 | run_etl.py Integration | Not started |
| #23 | benchsight.sh Commands | Not started |

**To implement:** Work through issues #17-#23 in order.

---

## Part 8: Quick Setup Checklist

### New Developer Setup

```bash
# 1. Clone repository
git clone https://github.com/ronniepinnell/benchsight.git
cd benchsight

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Node dependencies (dashboard)
cd ui/dashboard && npm install && cd ../..

# 4. Set up environment
cp config/config_local.ini.example config/config_local.ini
# Edit with your Supabase credentials

# 5. Set up hooks
chmod +x .claude/hooks/*.py

# 6. Verify ETL works
./benchsight.sh etl run
./benchsight.sh etl validate

# 7. Start dashboard
./benchsight.sh dashboard dev
```

### Debug Environment Setup

```bash
# 1. Install Docker
# macOS: brew install --cask docker
# Linux: sudo apt-get install docker.io docker-compose

# 2. Install psycopg2
pip install psycopg2-binary

# 3. Create docker config (see Part 7)
mkdir -p docker/init
# Create docker-compose.yml and init scripts

# 4. Create debug config
cp config/debug_config.ini.example config/debug_config.ini

# 5. Create debug directory
mkdir -p data/debug/snapshots

# 6. Start PostgreSQL
./benchsight.sh debug start

# 7. Verify setup
./benchsight.sh debug shell
# \dn should show 4 schemas
```

### Environment Variables

| Variable | Dev Value | Prod Value |
|----------|-----------|------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Dev Supabase URL | Prod Supabase URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Dev anon key | Prod anon key |
| `ENVIRONMENT` | development | production |

See `CLAUDE.md` for complete credential reference.

---

*Last Updated: 2026-01-21*
