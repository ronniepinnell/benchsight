# BenchSight Development Workflow - Quick Start

**Your daily workflow for Claude/Cursor + GitHub + CodeRabbit**

Last Updated: 2026-01-21

---

## TL;DR - The 5-Minute Version

```bash
# 1. Start your day
git checkout develop && git pull
./benchsight.sh env switch dev
./benchsight.sh dashboard dev  # Terminal 1

# 2. Start a feature
git checkout -b feature/my-feature
# ... code ...

# 3. Commit and push
git add . && git commit -m "[FEAT] Add my feature"
git push -u origin feature/my-feature

# 4. Create PR on GitHub
# CodeRabbit reviews automatically
# Address feedback, merge when approved
```

---

## Complete Workflow

### Phase 1: Start Your Session

```bash
# Pull latest and switch to dev
git checkout develop
git pull origin develop
./benchsight.sh env switch dev
./benchsight.sh env status  # Verify: should show "dev"

# Start dashboard (keep running in Terminal 1)
./benchsight.sh dashboard dev

# Optional: Start API (Terminal 2)
./benchsight.sh api dev
```

### Phase 2: Plan Your Work

**For features/refactors (recommended):**

1. **Check existing issues:** github.com/your-repo/issues
2. **Create issue if needed:** Use templates (feature, bug, refactor)
3. **Optional: Write PRD** for complex features:
   ```bash
   cp docs/prds/template.md docs/prds/features/my-feature.md
   # Edit the PRD
   ```

**Quick reference for issue labels:**
- `type:feature`, `type:fix`, `type:refactor`, `type:perf`
- `area:etl`, `area:dashboard`, `area:api`, `area:portal`, `area:tracker`
- `priority:p0` (critical), `priority:p1` (high), `priority:p2` (medium)
- `phase:2` (current phase)

### Phase 3: Create Branch

```bash
# Feature
git checkout -b feature/descriptive-name

# Bug fix
git checkout -b fix/bug-description

# Refactor
git checkout -b refactor/what-youre-refactoring

# Docs
git checkout -b docs/what-youre-documenting
```

**Branch naming:** `{type}/{component}-{description}`
- `feature/dashboard-xg-analysis`
- `fix/etl-goal-counting`
- `refactor/etl-modularization`

### Phase 4: Implement

**Use Claude/Cursor effectively:**

```
You: "I'm working on [feature]. Here's the relevant context:
- Issue: #123
- PRD: docs/prds/features/my-feature.md
- Key files: src/calculations/goals.py

Help me implement [specific task]."
```

**Key rules to follow:**
- Goals: `event_type == 'Goal' AND event_detail == 'Goal_Scored'`
- No `.iterrows()` - use vectorized pandas
- Single source of truth for calculations
- Update docs with code changes

### Phase 5: Test

```bash
# ETL changes
./benchsight.sh etl run
./benchsight.sh etl validate
pytest tests/test_goal_verification.py  # Critical!

# API changes
pytest tests/test_api.py

# Dashboard changes
npm run lint --prefix ui/dashboard
npm run type-check --prefix ui/dashboard

# All tests
pytest
```

### Phase 6: Commit

**Commit message format:**
```
[TYPE] Brief description (#issue-number)

- Detail 1
- Detail 2
```

**Types:** `FEAT`, `FIX`, `REFACTOR`, `PERF`, `DOCS`, `TEST`, `CHORE`

**Examples:**
```bash
git commit -m "[FEAT] Add xG analysis page (#45)

- Create XGAnalysis component
- Add xG vs goals comparison chart
- Update dashboard navigation"

git commit -m "[FIX] Correct goal counting filter (#42)

- Use GOAL_FILTER pattern
- Add regression test
- Verify against official scores"

git commit -m "[REFACTOR] Modularize base_etl.py (#38)

- Extract Phase 1 to phase1_blb_loader.py
- Extract validation to validation.py
- Reduce base_etl.py to orchestration"
```

### Phase 7: Push and Create PR

```bash
# Push branch
git push -u origin feature/my-feature

# Create PR (GitHub CLI)
gh pr create --title "[FEAT] Add my feature" --body "Closes #123"

# Or go to GitHub and create PR manually
```

**PR will trigger:**
1. CodeRabbit automatic review
2. Any CI checks you have configured

### Phase 8: Address CodeRabbit Feedback

**CodeRabbit comments types:**
- :red_circle: **Error** - Must fix
- :yellow_circle: **Warning** - Should fix
- :blue_circle: **Suggestion** - Consider

**How to respond:**
1. **Fix it:** Make the change, push new commit
2. **Explain:** Reply to comment with reasoning
3. **Dismiss:** If truly not applicable

```bash
# After fixing issues
git add .
git commit -m "[FIX] Address CodeRabbit feedback"
git push
```

### Phase 9: Merge

**When ready:**
- All CodeRabbit feedback addressed
- CI checks pass
- Self-review complete

**Merge via GitHub:**
1. Click "Merge pull request"
2. Choose "Squash and merge" for clean history
3. Delete the feature branch

**After merge:**
```bash
git checkout develop
git pull origin develop
git branch -d feature/my-feature  # Delete local branch
```

---

## Quick Reference Cards

### Commit Types

| Type | When to Use |
|------|-------------|
| `FEAT` | New feature |
| `FIX` | Bug fix |
| `REFACTOR` | Code restructuring, no behavior change |
| `PERF` | Performance improvement |
| `DOCS` | Documentation only |
| `TEST` | Tests only |
| `CHORE` | Maintenance, deps, config |

### Common Commands

```bash
# Status
./benchsight.sh status
./benchsight.sh env status
git status

# Development
./benchsight.sh dashboard dev
./benchsight.sh api dev
./benchsight.sh etl run
./benchsight.sh etl validate

# Testing
pytest
pytest tests/test_goal_verification.py
npm run lint --prefix ui/dashboard

# Git
git checkout develop && git pull
git checkout -b feature/name
git add . && git commit -m "[TYPE] Message"
git push -u origin feature/name

# GitHub CLI
gh issue create
gh pr create
gh pr list
gh pr view
```

### Critical Rules Checklist

Before every PR:

- [ ] Goals use `event_type == 'Goal' AND event_detail == 'Goal_Scored'`
- [ ] No `.iterrows()` in ETL code
- [ ] Tests pass: `pytest`
- [ ] ETL validates: `./benchsight.sh etl validate`
- [ ] Docs updated if behavior changed
- [ ] No secrets in code

---

## Claude/Cursor Best Practices

### Starting a New Task

```
"I'm starting work on [task].
Context:
- Issue: #123
- Component: ETL/Dashboard/API
- Key files: [list relevant files]

Help me [specific request]."
```

### When Stuck

```
"I'm trying to [goal] but [problem].
I've tried [attempts].
The error is: [error message]
Relevant code: [paste snippet]"
```

### Code Review Request

```
"Review this code for BenchSight standards:
- Goal counting pattern
- No .iterrows()
- Type safety
- Performance

[paste code]"
```

### Planning a Feature

```
"Help me plan [feature].
Requirements:
- [requirement 1]
- [requirement 2]

Create a step-by-step implementation plan."
```

---

## Workflow Decision Tree

```
Starting new work?
├── Is it a bug? → Create fix/ branch → Fix → Test → PR
├── Is it a feature?
│   ├── Simple (<1 day)? → Create feature/ branch → Implement → PR
│   └── Complex (>1 day)? → Write PRD → Create issue → Create branch → PR
└── Is it a refactor? → Create refactor/ branch → Refactor → Verify tests → PR

Creating a PR?
├── Run tests locally
├── Push branch
├── Create PR with template
├── Wait for CodeRabbit
├── Address feedback
└── Merge when approved

CodeRabbit feedback?
├── Error → Must fix
├── Warning → Should fix (or explain why not)
└── Suggestion → Consider (or dismiss with reason)
```

---

## Environment Quick Reference

| Environment | Supabase | Branch | Vercel |
|-------------|----------|--------|--------|
| Dev | amuisqvhhiigxetsfame | develop | Preview |
| Production | uuaowslhpgyiudmbvqze | main | Production |

```bash
# Switch environments
./benchsight.sh env switch dev
./benchsight.sh env switch production  # Be careful!
```

---

## Related Docs

- [WORKFLOW.md](WORKFLOW.md) - Full workflow details
- [CODERABBIT_WORKFLOW.md](CODERABBIT_WORKFLOW.md) - CodeRabbit specifics
- [MASTER_RULES.md](../MASTER_RULES.md) - Code standards
- [GITHUB_ISSUES_BACKLOG.md](../GITHUB_ISSUES_BACKLOG.md) - Issue backlog

---

*Last Updated: 2026-01-21*
