# BenchSight Skills Guide

**Complete guide to understanding, using, editing, and creating Claude Code skills**

Last Updated: 2025-01-22

---

## Table of Contents

1. [What Are Skills?](#what-are-skills)
2. [How Skills Work](#how-skills-work)
3. [Current BenchSight Skills](#current-benchsight-skills)
4. [When to Call Each Skill](#when-to-call-each-skill)
5. [How to Invoke Skills](#how-to-invoke-skills)
6. [How to Edit Skills](#how-to-edit-skills)
7. [Creating New Skills](#creating-new-skills)
8. [Skill Chains and Workflows](#skill-chains-and-workflows)
9. [Best Practices](#best-practices)
10. [Proposed Skills for Full Lifecycle](#proposed-skills-for-full-lifecycle)

---

## What Are Skills?

Skills are on-demand, reusable prompts that Claude Code executes when you invoke them. They're like macros or procedures that:

- **Automate** common tasks
- **Standardize** workflows
- **Provide** context-aware assistance
- **Chain** multiple operations together

**Location:** `.claude/skills/[skill-name]/SKILL.md`

**Invocation:** `/skill-name` or via Skill tool

---

## How Skills Work

### Skill Structure

Each skill has:

```
.claude/skills/
  skill-name/
    SKILL.md         # Skill definition and instructions
    (optional files) # Supporting files, templates, etc.
```

### SKILL.md Format

```markdown
# Skill Name

**Description:** What this skill does

## Instructions

[Detailed instructions for Claude Code to follow]

## Context Files

- File paths to read
- Reference documents

## Output

- What to produce
- Where to save results
```

### Skill Execution

When you invoke `/skill-name`:

1. Claude reads `SKILL.md`
2. Follows instructions
3. Uses tools as needed
4. Produces output per spec

---

## Current BenchSight Skills

### Core Development Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `/etl` | Run ETL pipeline | Processing new game data |
| `/validate` | Validate ETL output | After ETL runs, checking data integrity |
| `/dashboard-dev` | Start dashboard dev server | Working on dashboard features |
| `/portal-dev` | Work on admin portal | Developing portal features |
| `/tracker-dev` | Work on tracker | Tracker bug fixes or features |
| `/api-dev` | Start API dev server | Working on API endpoints |

### Database Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `/db-dev` | Connect to dev Supabase | Testing queries, schema changes |
| `/db-prod` | Connect to prod Supabase | **CAREFUL** - production only |
| `/env-switch` | Switch dev/prod environments | Changing deployment targets |
| `/schema-design` | Design database schemas | Planning new tables |

### Quality & Validation Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `/compliance-check` | Check CLAUDE.md rules | After code changes |
| `/reality-check` | Call Karen agent | Verify actual vs claimed progress |
| `/post-code` | Full post-code validation | After writing any code |
| `/pr-workflow` | Create pull request | Ready to submit changes |

### Analytics & ML Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `/hockey-stats` | Consult hockey SME | Stat calculation questions |
| `/xg-model` | Work on xG model | Expected goals development |
| `/ml-pipeline` | ML pipeline work | Developing ML features |
| `/cv-tracking` | Computer vision work | Video tracking features |

### Business & Research Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `/competitive-research` | Research competitors | Feature planning |
| `/monetization` | Pricing/revenue planning | Commercial strategy |
| `/go-to-market` | Launch strategy | Marketing planning |
| `/scale-architecture` | Architecture planning | Scaling decisions |

### Documentation & Workflow Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `/doc-sync` | Sync docs with code | After code changes |
| `/etl-issue` | Create ETL failure issue | ETL errors/bugs |
| `/ui-ux-design` | UI/UX planning | Dashboard design work |

---

## When to Call Each Skill

### Daily Development Flow

```
Morning Setup:
  /dashboard-dev     → Start dev server if working on dashboard
  /db-dev            → Connect to dev database if needed

After Writing Code:
  /compliance-check  → Verify CLAUDE.md rules
  /post-code         → Full validation workflow

Before Committing:
  /doc-sync          → Check if docs need updates

Creating PR:
  /pr-workflow       → Full PR creation workflow

After ETL Changes:
  /etl               → Run the pipeline
  /validate          → Validate output
```

### By Task Type

| Task | Skills to Use (in order) |
|------|-------------------------|
| ETL work | `/etl` → `/validate` → `/compliance-check` |
| Dashboard feature | `/dashboard-dev` → `/post-code` → `/pr-workflow` |
| New stat calculation | `/hockey-stats` → code → `/validate` |
| Database changes | `/db-dev` → `/schema-design` → `/db-dev` (verify) |
| ML feature | `/ml-pipeline` → `/xg-model` → `/validate` |
| Bug investigation | `/reality-check` → fix → `/post-code` |
| Commercial planning | `/competitive-research` → `/monetization` |

---

## How to Invoke Skills

### Method 1: Slash Command (Recommended)

```
/etl
```

### Method 2: Skill Tool

Claude can invoke via:
```
Skill tool call: skill="etl"
```

### Method 3: With Arguments

```
/etl --games 18969
/pr-workflow --branch feature/new-stat
```

### Method 4: Chained

```
Please run /etl and then /validate
```

---

## How to Edit Skills

### Step 1: Locate the Skill

```bash
ls -la .claude/skills/
cat .claude/skills/skill-name/SKILL.md
```

### Step 2: Understand the Structure

```markdown
# Skill Name

**Trigger:** When this skill should be invoked

## Instructions

1. Step one
2. Step two
3. Step three

## Context Files

- Read this file
- Reference that file

## Output

What to produce
```

### Step 3: Edit SKILL.md

Make changes to:
- Instructions (add/modify steps)
- Context files (add relevant files)
- Output format (change what's produced)

### Step 4: Test the Skill

```
/skill-name
```

Verify it does what you expect.

### Example: Enhancing /validate

Before:
```markdown
## Instructions

1. Run table verification
2. Check row counts
```

After:
```markdown
## Instructions

1. Run table verification
2. Check row counts
3. Verify goal counting specifically
4. Check for duplicate primary keys
5. Validate foreign key relationships
6. Output summary report
```

---

## Creating New Skills

### Step 1: Create Directory

```bash
mkdir -p .claude/skills/my-new-skill
```

### Step 2: Create SKILL.md

```markdown
# My New Skill

**Description:** What this skill does and when to use it

**Trigger:** Phrases that should invoke this skill

## Prerequisites

- What must be true before running
- Required tools/access

## Instructions

1. First, do this
2. Then, do that
3. Finally, produce output

## Context Files

Read these files for context:
- `path/to/relevant/file.md`
- `another/file.py`

## Output

Produce the following:
- Summary of actions taken
- Any issues found
- Recommendations

## Examples

### Example 1: Basic Usage
```
/my-new-skill
```
Expected: [what happens]

### Example 2: With Parameters
```
/my-new-skill --option value
```
Expected: [what happens]
```

### Step 3: Register the Skill

Skills in `.claude/skills/` are automatically available.

No additional registration needed.

### Step 4: Test

```
/my-new-skill
```

---

## Skill Chains and Workflows

### ETL Development Workflow

```
/etl → /validate → /compliance-check → /pr-workflow
```

### Dashboard Development Workflow

```
/dashboard-dev → write code → /post-code → /pr-workflow
```

### Bug Fix Workflow

```
/reality-check → investigate → fix → /compliance-check → /pr-workflow
```

### Commercial Planning Workflow

```
/competitive-research → /monetization → /go-to-market → /scale-architecture
```

### Creating a Workflow Skill

You can create a skill that chains others:

```markdown
# Full ETL Workflow

## Instructions

1. Run `/etl` to process data
2. Run `/validate` to verify output
3. Run `/compliance-check` to verify rules
4. If all pass, run `/pr-workflow`
5. If any fail, report issues and stop
```

---

## Best Practices

### 1. Use Skills Instead of Remembering

Don't remember complex procedures - encode them in skills.

```
# BAD: Trying to remember
"First I need to run the ETL, then check tables, then..."

# GOOD: Use the skill
/etl
```

### 2. Chain Skills for Complex Workflows

```
/etl && /validate && /compliance-check
```

### 3. Keep Skills Focused

One skill = one responsibility

```
# GOOD
/validate - just validates
/etl - just runs ETL

# BAD
/do-everything - validates, runs ETL, commits, deploys...
```

### 4. Include Context Files

Skills work better with relevant context:

```markdown
## Context Files

- `CLAUDE.md` - Project rules
- `docs/etl/CODE_FLOW_ETL.md` - ETL architecture
- `config/formulas.json` - Calculation definitions
```

### 5. Document Expected Output

Be specific about what the skill produces:

```markdown
## Output

1. Summary table of validation results
2. List of any failures with line numbers
3. Recommendations for fixes
```

### 6. Version Your Skills

Add version/date to SKILL.md:

```markdown
# Skill Name

**Version:** 1.2
**Last Updated:** 2025-01-22
```

---

## Proposed Skills for Full Lifecycle

### Phase 2: ETL Optimization

| Skill | Purpose |
|-------|---------|
| `/etl-profile` | Profile ETL performance, find bottlenecks |
| `/table-verify` | Run comprehensive table verification |
| `/dead-code-scan` | Find unused code in ETL |
| `/iterrows-hunt` | Find and fix .iterrows() usage |

### Phase 3: Dashboard Enhancement

| Skill | Purpose |
|-------|---------|
| `/dashboard-test` | Run dashboard test suite |
| `/component-review` | Review component for best practices |
| `/a11y-check` | Accessibility compliance check |

### Phase 4: Portal Development

| Skill | Purpose |
|-------|---------|
| `/portal-test` | Run portal test suite |
| `/api-validate` | Validate API endpoints |

### Phase 5: Tracker Conversion

| Skill | Purpose |
|-------|---------|
| `/tracker-audit` | Audit tracker code for conversion |
| `/rust-scaffold` | Scaffold Rust backend structure |

### Phase 6: ML/CV

| Skill | Purpose |
|-------|---------|
| `/train-model` | Train ML model with validation |
| `/model-evaluate` | Evaluate model performance |
| `/cv-test` | Test computer vision pipeline |

### Phase 7-8: Commercial

| Skill | Purpose |
|-------|---------|
| `/tenant-setup` | Set up new tenant |
| `/billing-test` | Test billing integration |
| `/onboard-check` | Verify onboarding flow |

### Phase 9-12: AI Coaching

| Skill | Purpose |
|-------|---------|
| `/ai-coach-test` | Test AI coach responses |
| `/nl-query-test` | Test natural language queries |
| `/game-plan-gen` | Generate sample game plan |

---

## Related Documentation

- [HOOKS_GUIDE.md](HOOKS_GUIDE.md) - Hooks guide
- [AGENTS_GUIDE.md](../agents/AGENTS_GUIDE.md) - Agents guide
- [CLAUDE_CODE_BEST_PRACTICES.md](CLAUDE_CODE_BEST_PRACTICES.md) - Overall best practices
- [docs/workflows/WORKFLOW.md](../../docs/workflows/WORKFLOW.md) - Development workflow

---

*Last Updated: 2025-01-22*
