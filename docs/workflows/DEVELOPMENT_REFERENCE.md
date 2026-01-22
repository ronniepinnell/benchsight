# BenchSight Development Reference

**Complete reference for Claude/Cursor + GitHub + CodeRabbit workflow**

Last Updated: 2026-01-21

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Daily Workflow](#daily-workflow)
3. [Git & GitHub](#git--github)
4. [CodeRabbit](#coderabbit)
5. [Claude/Cursor Best Practices](#claudecursor-best-practices)
6. [Commands Reference](#commands-reference)
7. [Critical Rules](#critical-rules)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### First Time Setup

```bash
# 1. Authenticate GitHub CLI
gh auth login

# 2. Create GitHub labels and issues
./scripts/create-github-issues.sh

# 3. Install pre-commit hooks
pip install pre-commit
pre-commit install

# 4. Verify environment
./benchsight.sh status
```

### Start Your Day

```bash
./scripts/daily-start.sh
```

Or manually:
```bash
git checkout develop && git pull
./benchsight.sh env switch dev
./benchsight.sh dashboard dev  # Terminal 1
```

---

## Daily Workflow

### The Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. PLAN          2. BRANCH         3. CODE          4. TEST   │
│  ─────────        ──────────        ──────────       ─────────  │
│  Check issues     create-feature    Implement        pytest     │
│  Write PRD        git checkout -b   Follow rules     validate   │
│                                                                 │
│  5. COMMIT        6. PUSH           7. PR            8. MERGE   │
│  ──────────       ──────────        ──────────       ─────────  │
│  [TYPE] msg       git push -u       CodeRabbit       Squash     │
│  Frequent         origin branch     reviews          Delete     │
└─────────────────────────────────────────────────────────────────┘
```

### Step-by-Step

**1. Check Issues**
```bash
gh issue list                    # List all issues
gh issue list --label "phase:2"  # Filter by phase
gh issue view 1                  # View issue details
```

**2. Create Branch**
```bash
./scripts/create-feature.sh feature dashboard-xg-page
# OR
./scripts/create-feature.sh fix etl-goal-counting
# OR
./scripts/create-feature.sh refactor etl-modularization
```

**3. Implement**
- Follow [Critical Rules](#critical-rules)
- Use Claude/Cursor effectively (see [Best Practices](#claudecursor-best-practices))
- Commit frequently

**4. Test**
```bash
pytest                                    # All tests
pytest tests/test_goal_verification.py   # Critical goal test
./benchsight.sh etl validate             # ETL validation
npm run lint --prefix ui/dashboard       # Dashboard lint
```

**5. Commit**
```bash
git add .
git commit -m "[FEAT] Add xG analysis page (#45)

- Create XGAnalysis component
- Add comparison chart
- Update navigation"
```

**6. Push & PR**
```bash
git push -u origin feature/dashboard-xg-page
gh pr create --title "[FEAT] Add xG analysis page" --body "Closes #45"
```

**7. Address CodeRabbit Feedback**
- Fix errors (🔴)
- Address warnings (🟡)
- Consider suggestions (🔵)

**8. Merge**
- Squash and merge
- Delete branch
- Close issue

---

## Git & GitHub

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/{component}-{description}` | `feature/dashboard-xg-analysis` |
| Bug fix | `fix/{component}-{description}` | `fix/etl-goal-counting` |
| Refactor | `refactor/{component}-{description}` | `refactor/etl-modularization` |
| Docs | `docs/{description}` | `docs/api-reference` |
| Performance | `perf/{component}-{description}` | `perf/etl-vectorization` |

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
git commit -m "[REFACTOR] Modularize base_etl.py (#38)

- Extract Phase 1 to phase1_blb_loader.py
- Extract validation to validation.py
- Reduce base_etl.py to orchestration"
```

### GitHub CLI Commands

```bash
# Issues
gh issue list                         # List issues
gh issue list --label "priority:p0"   # Filter by label
gh issue view 1                       # View issue
gh issue create                       # Create issue (interactive)

# Pull Requests
gh pr create                          # Create PR (interactive)
gh pr list                            # List PRs
gh pr view 1                          # View PR
gh pr checkout 1                      # Checkout PR branch
gh pr merge 1 --squash                # Merge with squash

# Repository
gh browse                             # Open repo in browser
gh browse --issues                    # Open issues
gh browse --pulls                     # Open PRs
```

### Labels

**Type Labels:**
- `type:feature` - New functionality
- `type:fix` - Bug fix
- `type:refactor` - Code restructuring
- `type:perf` - Performance
- `type:docs` - Documentation
- `type:test` - Testing
- `type:chore` - Maintenance

**Area Labels:**
- `area:etl` - ETL pipeline (src/)
- `area:dashboard` - Dashboard (ui/dashboard/)
- `area:tracker` - Tracker (ui/tracker/)
- `area:portal` - Portal (ui/portal/)
- `area:api` - API (api/)
- `area:data` - Database/schema
- `area:analytics` - ML/analytics

**Priority Labels:**
- `priority:p0` - Critical/blocking
- `priority:p1` - High priority
- `priority:p2` - Medium priority
- `priority:p3` - Low priority

**Phase Labels:**
- `phase:2` - ETL Optimization (CURRENT)
- `phase:3` - Dashboard Enhancement
- `phase:4` - Portal Development
- `phase:5` - Tracker Conversion
- `phase:6` - ML/CV Integration
- `phase:7` - Multi-Tenancy
- `phase:8` - Commercial Launch

---

## CodeRabbit

### How It Works

1. **Automatic Review:** CodeRabbit reviews every PR automatically
2. **BenchSight Rules:** Configured in `.coderabbit.yaml` with project-specific rules
3. **Feedback Types:**
   - 🔴 **Error** - Must fix
   - 🟡 **Warning** - Should fix
   - 🔵 **Suggestion** - Consider

### Responding to Feedback

**Fix It:**
```bash
# Make the fix
git add .
git commit -m "[FIX] Address CodeRabbit feedback"
git push
```

**Explain (if valid reason to keep as-is):**
- Reply to the CodeRabbit comment
- Explain your reasoning

**Dismiss (rare):**
- Only if truly not applicable
- Add a note explaining why

### BenchSight-Specific Rules

CodeRabbit is configured to check:

1. **Goal Counting (CRITICAL)**
   - Must use: `event_type == 'Goal' AND event_detail == 'Goal_Scored'`
   - Flagged as error if violated

2. **Performance**
   - No `.iterrows()` - flagged as error
   - Prefer vectorized pandas operations

3. **Stat Counting**
   - Only count for `player_role == 'event_player_1'`
   - Micro-stats counted once per linked event

4. **Code Quality**
   - Type hints required
   - Docstrings required (Google style)
   - Single source of truth for calculations

---

## Claude/Cursor Best Practices

### Starting a Task

```
I'm working on [task].

Context:
- Issue: #123
- Component: ETL/Dashboard/API
- Key files: [list relevant files]

Help me [specific request].
```

### Effective Prompts

**For Implementation:**
```
Implement [feature] following BenchSight patterns:
- Goals: event_type == 'Goal' AND event_detail == 'Goal_Scored'
- No .iterrows() - use vectorized operations
- Add type hints

Key files to reference:
- src/calculations/goals.py (goal counting)
- [relevant files]
```

**For Code Review:**
```
Review this code for BenchSight standards:
- Goal counting pattern
- No .iterrows()
- Type safety
- Performance

[paste code]
```

**For Planning:**
```
Help me plan [feature].

Requirements:
- [requirement 1]
- [requirement 2]

Create a step-by-step implementation plan.
```

**When Stuck:**
```
I'm trying to [goal] but [problem].
I've tried [attempts].
The error is: [error message]
Relevant code: [paste snippet]
```

### Context Management

- **Keep context small:** Only load relevant files
- **Reference docs:** Point to docs instead of pasting
- **Reset when switching tasks:** Start fresh conversation for new features
- **Use PRDs:** Reference PRD for complex features

---

## Commands Reference

### Project Commands

```bash
# Status
./benchsight.sh status              # Project status
./benchsight.sh env status          # Environment status

# Environment
./benchsight.sh env switch dev      # Switch to dev
./benchsight.sh env switch production  # Switch to prod (careful!)

# ETL
./benchsight.sh etl run             # Run ETL pipeline
./benchsight.sh etl run --wipe      # Clean slate + run
./benchsight.sh etl validate        # Validate output

# Dashboard
./benchsight.sh dashboard dev       # Start dev server
./benchsight.sh dashboard build     # Production build

# API
./benchsight.sh api dev             # Start API server
./benchsight.sh api test            # Run API tests

# Database
./benchsight.sh db upload           # Upload to Supabase
```

### Helper Scripts

```bash
# Daily startup
./scripts/daily-start.sh

# Create feature branch
./scripts/create-feature.sh feature my-feature
./scripts/create-feature.sh fix my-bug
./scripts/create-feature.sh refactor my-refactor

# Create GitHub issues
./scripts/create-github-issues.sh --labels-only
./scripts/create-github-issues.sh --phase2
./scripts/create-github-issues.sh --all

# Check documentation
./scripts/docs-check.sh
```

### Testing

```bash
# Python tests
pytest                                    # All tests
pytest tests/test_goal_verification.py   # Goal verification
pytest tests/test_calculations.py        # Calculations
pytest -m "not slow"                      # Skip slow tests
pytest --cov=src tests/                   # With coverage

# Dashboard
npm run lint --prefix ui/dashboard        # Lint
npm run type-check --prefix ui/dashboard  # Type check
npm run build --prefix ui/dashboard       # Build test
```

### Git

```bash
# Daily
git checkout develop && git pull
git checkout -b feature/my-feature
git add . && git commit -m "[TYPE] Message"
git push -u origin feature/my-feature

# GitHub CLI
gh issue list
gh pr create
gh pr list
gh browse
```

---

## Critical Rules

### Goal Counting (CRITICAL)

```python
# CORRECT - This is the ONLY valid pattern
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')

# WRONG - Never do this
wrong = df['event_type'] == 'Shot'  # with event_detail == 'Goal'
```

### No .iterrows()

```python
# WRONG
for idx, row in df.iterrows():
    # process row

# CORRECT
result = df.groupby('player_id').apply(process_group)
# OR
result = df.apply(lambda row: process(row), axis=1)
```

### Stat Counting

```python
# Only count for event_player_1
stats = df[df['player_role'] == 'event_player_1']

# Micro-stats: once per linked_event
micro = df.drop_duplicates(subset=['linked_event_key', 'player_id', 'micro_stat'])
```

### Assists

```python
# Only Primary and Secondary count
assist_mask = df['play_detail'].str.contains('AssistPrimary|AssistSecondary', na=False)
# Tertiary does NOT count as an assist
```

### Key Formatting

```python
# Standard format: {XX}{ID}{5D}
game_key = f"GK{game_id:05d}"
player_key = f"PK{player_id:05d}"

# Multi-player keys use underscore
line_key = f"LN_{player1_id}_{player2_id}_{player3_id}"
```

---

## Troubleshooting

### Common Issues

**GitHub CLI not authenticated:**
```bash
gh auth login
```

**Environment not switching:**
```bash
./benchsight.sh env status  # Check current
cat config/config_local.ini # Verify config
```

**ETL failing:**
```bash
tail -f logs/etl_v5.log     # Check logs
./benchsight.sh etl validate # Validate output
```

**Dashboard not loading:**
```bash
cd ui/dashboard
npm install                  # Install deps
npm run dev                  # Start dev server
# Check browser console for errors
```

**CodeRabbit not reviewing:**
- Check app installation on GitHub
- Verify repository is selected
- Check PR status

### Getting Help

1. Check docs: `docs/workflows/WORKFLOW.md`
2. Check status: `./benchsight.sh status`
3. Check logs: `logs/`
4. Ask Claude with context

---

## File Locations

| Purpose | Location |
|---------|----------|
| This reference | `docs/workflows/DEVELOPMENT_REFERENCE.md` |
| Full workflow | `docs/workflows/WORKFLOW.md` |
| Quick start | `docs/workflows/QUICKSTART_WORKFLOW.md` |
| CodeRabbit config | `.coderabbit.yaml` |
| Issue backlog | `docs/GITHUB_ISSUES_BACKLOG.md` |
| Project rules | `docs/MASTER_RULES.md` |
| Critical rules | `CLAUDE.md` |
| Daily startup | `scripts/daily-start.sh` |
| Create feature | `scripts/create-feature.sh` |
| Create issues | `scripts/create-github-issues.sh` |

---

## Environment Quick Reference

| Environment | Supabase | Branch | Vercel |
|-------------|----------|--------|--------|
| Dev | amuisqvhhiigxetsfame | develop | Preview |
| Production | uuaowslhpgyiudmbvqze | main | Production |

---

*Last Updated: 2026-01-21*
