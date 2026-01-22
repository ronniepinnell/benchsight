# BenchSight Agent Best Practices Guide

## Overview

This guide defines when and how to use agents, skills, and hooks in the BenchSight project. Follow these workflows to maintain code quality, ensure spec compliance, and avoid incomplete implementations.

---

## Slash Commands (Skills)

Use these commands for common operations:

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/etl` | Run ETL pipeline | Processing new games, rebuilding data |
| `/validate` | Run validation suite | After ETL, checking data quality |
| `/etl-issue` | Create GitHub issue for ETL failure | After ETL failures |
| `/reality-check` | Call Karen agent | Verify claimed completions |
| `/compliance-check` | Check CLAUDE.md rules | After implementing features |
| `/hockey-stats` | Consult analytics SME | Before implementing any stat calculation |

### Usage Examples

```bash
/etl --games 18969,18970     # Process specific games
/etl --wipe                  # Clean slate + full run
/validate                    # Verify data quality
/etl-issue last              # Create issue for most recent failure
/reality-check I finished the player stats page
/compliance-check recent API changes
/hockey-stats How should we calculate expected goals?
```

---

## Active Hooks

These run automatically:

| Hook | Trigger | Purpose |
|------|---------|---------|
| `bash-validator` | Before Bash commands | Blocks dangerous operations |
| `goal-counting-guard` | Before Edit/Write on goal files | Reminds of critical rule |
| `post-etl-reminder` | After ETL runs | Prompts to run validation |
| `etl-failure-handler` | After ETL failures | Creates GitHub issues with full context |

---

---

## Quick Reference: Agent Selection Matrix

| Situation | Primary Agent | Secondary Agent(s) |
|-----------|---------------|-------------------|
| "How do I calculate this hockey stat?" | `hockey-analytics-sme` | — |
| "I finished implementing X" | `task-completion-validator` | `claude-md-compliance-checker` |
| "Is this over-engineered?" | `code-quality-pragmatist` | — |
| "Does this match the spec?" | `Jenny` | `task-completion-validator` |
| "What's actually working vs claimed?" | `karen` | (runs full validation chain) |
| "Set up CI/CD pipeline" | `github-integration-expert` | — |
| "Test the dashboard UI" | `ui-comprehensive-tester` | — |
| "Review this code" | `code-reviewer` | `code-quality-pragmatist` |
| "Debug ETL issue" | `debugger` | `hockey-analytics-sme` |
| "Optimize database queries" | `database-optimizer` | `postgres-pro` |

---

## The 8 Project-Specific Agents

### 1. `hockey-analytics-sme` (Red)
**When to call:** Any hockey statistics question, calculation methodology, or data visualization decision.

**Triggers:**
- "How should we calculate Corsi?"
- "What features for xG model?"
- "What does 'receivermissed' mean in play_detail?"
- "Is our calculation matching NHL Edge?"

**Best practice:** Call BEFORE implementing any stat calculation to ensure methodology aligns with industry standards and project rules.

---

### 2. `task-completion-validator` (Blue)
**When to call:** Whenever you or a developer claims a task is "done."

**Triggers:**
- "I've finished the authentication system"
- "Database integration is complete"
- "Tests are passing"

**What it checks:**
- Core functionality isn't stubbed/mocked
- Error handling exists for critical paths
- Integration points actually work
- Test coverage is real (not just mocks)

**Best practice:** Run immediately after claiming completion. Do NOT mark tasks complete until this passes.

---

### 3. `code-quality-pragmatist` (Orange)
**When to call:** After implementing features to check for over-engineering.

**Triggers:**
- After writing new code
- After architectural decisions
- When code feels "too complex"

**What it detects:**
- Enterprise patterns in MVP code
- Unnecessary abstractions
- Premature optimization
- Boilerplate bloat

**Best practice:** Run after `task-completion-validator` confirms functionality works.

---

### 4. `Jenny` (Orange)
**When to call:** To verify implementation matches specifications.

**Triggers:**
- "Verify this matches the PRD"
- "Check against requirements"
- "Assess project completion status"

**What it does:**
- Independent codebase examination
- Gap analysis (Missing/Incomplete/Incorrect/Extra)
- Evidence-based assessment with file:line references

**Best practice:** Use when you suspect gaps between what was requested and what was built.

---

### 5. `claude-md-compliance-checker` (Green)
**When to call:** After completing any task to verify CLAUDE.md rule compliance.

**Triggers:**
- After implementing features
- After making significant changes
- Before marking work "ready for review"

**Key rules it enforces:**
- Goal counting (CRITICAL): `event_type == 'Goal' AND event_detail == 'Goal_Scored'`
- Stat attribution: Only count for `player_role == 'event_player_1'`
- No `.iterrows()` usage
- Single source of truth for calculations

**Best practice:** Always run as the final check before considering work complete.

---

### 6. `karen` (Yellow)
**When to call:** When you need a reality check on project state.

**Triggers:**
- "Multiple tasks marked done but things aren't working"
- "What's the real status?"
- "Cut through the BS and tell me what's actually complete"

**What it does:**
- Assesses actual vs claimed progress
- Identifies incomplete implementations hiding behind "done" markers
- Creates realistic completion plans

**Best practice:** Call when you're suspicious about claimed completions or need project-wide status assessment.

---

### 7. `github-integration-expert` (Cyan)
**When to call:** GitHub Actions, CI/CD, CodeRabbit, Supabase, or Vercel configuration.

**Triggers:**
- "Set up automated deployments"
- "Configure CodeRabbit for PR reviews"
- "Sync environment variables across platforms"
- "Run Supabase migrations in CI"

**Best practice:** Use for any cross-platform coordination or deployment pipeline work.

---

### 8. `ui-comprehensive-tester` (Blue)
**When to call:** After UI implementation for thorough testing.

**Triggers:**
- "Test the login form"
- "Validate dashboard functionality"
- "Check mobile responsiveness"

**Auto-selects testing tool:**
- Puppeteer MCP: Lightweight web tests
- Playwright MCP: Cross-browser, complex scenarios
- Mobile MCP: iOS/Android specific

**Best practice:** Run after any dashboard or UI changes before considering complete.

---

## Standard Workflows

### Workflow 1: Feature Implementation

```
1. PLAN
   └── Create PRD in docs/prds/ (if significant feature)
   └── Call hockey-analytics-sme if stats-related

2. IMPLEMENT
   └── Write code following CLAUDE.md rules
   └── Use vectorized pandas (never .iterrows())
   └── Follow single source of truth principle

3. VALIDATE (run in sequence)
   ├── task-completion-validator → "Does it actually work?"
   ├── code-quality-pragmatist → "Is it over-engineered?"
   ├── Jenny → "Does it match the spec?"
   └── claude-md-compliance-checker → "Does it follow project rules?"

4. TEST
   └── Run pytest for ETL/API changes
   └── Run ui-comprehensive-tester for dashboard changes
   └── ./benchsight.sh etl validate

5. COMMIT
   └── Use format: [TYPE] Brief description
   └── Types: FEAT, FIX, DOCS, REFACTOR, TEST, CHORE
```

---

### Workflow 2: ETL Changes

```
1. CONSULT
   └── hockey-analytics-sme for stat methodology questions

2. IMPLEMENT
   └── Modify files in src/calculations/ or src/tables/
   └── CRITICAL: Respect goal counting rules
   └── CRITICAL: No duplicate stat counting

3. VALIDATE
   └── ./benchsight.sh etl run --wipe
   └── ./benchsight.sh etl validate
   └── task-completion-validator
   └── claude-md-compliance-checker

4. VERIFY DATA
   └── Check data/output/ CSVs
   └── Confirm no double-counting
   └── Verify goal totals match expected
```

---

### Workflow 3: Dashboard Changes

```
1. IMPLEMENT
   └── Server Components by default
   └── Client Components only for interactivity
   └── Follow shadcn/ui + Tailwind patterns

2. TEST
   └── npm run type-check
   └── npm run lint
   └── ui-comprehensive-tester for functional testing

3. VALIDATE
   └── task-completion-validator
   └── code-quality-pragmatist
   └── claude-md-compliance-checker

4. PREVIEW
   └── npm run dev (local)
   └── Vercel preview (on PR)
```

---

### Workflow 4: Bug Fix

```
1. DIAGNOSE
   └── debugger agent for complex issues
   └── hockey-analytics-sme if stats-related

2. FIX
   └── Minimal changes (don't refactor unrelated code)
   └── Don't add features

3. VALIDATE
   └── task-completion-validator
   └── claude-md-compliance-checker

4. TEST
   └── Add/update test if appropriate
   └── ./benchsight.sh etl validate (if ETL)
```

---

### Workflow 5: Reality Check (When Things Feel Off)

```
1. CALL karen
   └── "What's actually working vs what's claimed?"

2. karen AUTOMATICALLY RUNS:
   └── task-completion-validator
   └── code-quality-pragmatist
   └── Jenny
   └── claude-md-compliance-checker

3. REVIEW FINDINGS
   └── Prioritize Critical issues
   └── Create realistic completion plan
   └── Address gaps systematically
```

---

### Workflow 6: PR/Code Review

```
1. BEFORE PR
   └── Run full validation sequence
   └── ./benchsight.sh etl validate (if ETL changes)
   └── npm run build (if dashboard changes)

2. CREATE PR
   └── github-integration-expert for CI/CD issues
   └── CodeRabbit auto-reviews against CLAUDE.md

3. REVIEW FEEDBACK
   └── code-reviewer for manual review
   └── Address Critical/High severity first

4. MERGE
   └── Squash and merge to develop
   └── develop → main for releases
```

---

## Agent Chaining Patterns

### Pattern A: Standard Completion Validation
```
task-completion-validator
    ↓ (passes)
code-quality-pragmatist
    ↓ (passes)
claude-md-compliance-checker
    ↓ (passes)
READY
```

### Pattern B: Full Spec Verification
```
task-completion-validator
    ↓
Jenny
    ↓
code-quality-pragmatist
    ↓
claude-md-compliance-checker
    ↓
READY
```

### Pattern C: Karen's Reality Check (runs automatically)
```
karen (orchestrates)
    ├── task-completion-validator
    ├── code-quality-pragmatist
    ├── Jenny
    └── claude-md-compliance-checker
```

### Pattern D: Hockey Stats Implementation
```
hockey-analytics-sme (methodology)
    ↓
IMPLEMENT
    ↓
task-completion-validator
    ↓
claude-md-compliance-checker (goal counting rules!)
    ↓
READY
```

---

## Context Management Best Practices

### Keep Context Clean

1. **Compact after milestones**
   ```
   /compact
   ```
   Run after completing major features or validation sequences.

2. **Use Explore agent for searches**
   - Offloads search context to subagent
   - Results come back summarized
   - Main context stays clean

3. **Read specific files, not directories**
   - Good: `Read src/calculations/goals.py`
   - Bad: "Read everything in src/"

4. **Start fresh for unrelated tasks**
   - New conversation for new features
   - Resume agents only for continuing related work

### When to Compact

- After completing a feature
- After running validation sequence
- Before starting new unrelated work
- When responses get slow/confused
- After extensive file exploration

### Parallel vs Sequential Agents

**Run in parallel** (independent tasks):
```
# Can run simultaneously - no dependencies
- code-reviewer + security-auditor
- Explore agent for search + Read specific file
```

**Run sequentially** (dependent results):
```
# Must run in order
1. task-completion-validator (does it work?)
2. code-quality-pragmatist (is it simple?)
3. claude-md-compliance-checker (follows rules?)
```

---

## Critical Rules Enforcement

These rules are enforced by agents and must never be violated:

### Goal Counting (CRITICAL)
```python
# ONLY this combination counts as a goal:
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')

# NEVER count this as a goal:
# event_type == 'Shot' with event_detail == 'Goal' is a shot attempt
```

### Stat Attribution
```python
# Count stats ONLY for event_player_1
df[df['player_role'] == 'event_player_1']
```

### Micro-Stat Deduplication
```python
# In linked events, count micro-stats ONCE per linked_event_key
# Not once per event in the chain
```

### Vectorized Operations
```python
# NEVER use:
for index, row in df.iterrows():  # PROHIBITED

# ALWAYS use:
df.groupby('column').apply(func)
df['new_col'] = df['col'].map(func)
```

---

## Available Utility Agents (From VoltAgent Catalog)

For specialized tasks beyond project-specific agents:

| Category | Use For | Example Agents |
|----------|---------|----------------|
| Development | Code implementation | `backend-developer`, `frontend-developer`, `nextjs-developer` |
| Language | Language-specific help | `python-pro`, `typescript-pro`, `sql-pro` |
| Infrastructure | DevOps/deployment | `devops-engineer`, `terraform-engineer` |
| Quality | Testing/security | `test-automator`, `security-auditor`, `qa-expert` |
| Data | Data engineering | `data-engineer`, `postgres-pro`, `database-optimizer` |
| Research | Information gathering | `research-analyst`, `search-specialist` |

---

## Anti-Patterns to Avoid

### ❌ Don't: Skip validation
```
# BAD: Claim done without validation
"I finished the feature, marking as complete"
```

### ✅ Do: Always validate
```
# GOOD: Run validation sequence
task-completion-validator → code-quality-pragmatist → claude-md-compliance-checker
```

### ❌ Don't: Over-engineer
```
# BAD: Add abstraction layers, factories, future-proofing
```

### ✅ Do: Keep it simple
```
# GOOD: Minimal code that solves the current problem
```

### ❌ Don't: Ignore agent feedback
```
# BAD: "The agent said there are issues but I'll merge anyway"
```

### ✅ Do: Address all Critical/High issues
```
# GOOD: Fix identified issues before proceeding
```

### ❌ Don't: Run agents on polluted context
```
# BAD: 50+ files read, long conversation, no compacting
```

### ✅ Do: Compact and focus
```
# GOOD: /compact, then targeted agent call
```

---

## Summary Checklist

Before marking ANY task complete:

- [ ] `task-completion-validator` passes
- [ ] `code-quality-pragmatist` finds no over-engineering
- [ ] `claude-md-compliance-checker` confirms rule compliance
- [ ] `Jenny` confirms spec alignment (for significant features)
- [ ] Tests pass (`pytest`, `npm run build`, etc.)
- [ ] ETL validation passes (if ETL changes)
- [ ] No Critical/High severity issues outstanding

When in doubt, call `karen` for a reality check.
