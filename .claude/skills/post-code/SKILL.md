---
name: post-code
description: Run the complete post-code validation and documentation workflow. This is the MASTER skill to run after writing any code - it orchestrates all validation agents in the correct order.
allowed-tools: Bash, Read, Task
---

# Post-Code Workflow Orchestrator

Run this after writing ANY code to ensure quality, compliance, and documentation.

## The Golden Rule

**NEVER mark code as complete without running `/post-code`**

## Invocation Variants

```
/post-code              # Full workflow (recommended)
/post-code quick        # Quick validation only
/post-code commit       # Full workflow + prepare commit
/post-code pr           # Full workflow + create PR
```

---

## Complete Workflow Sequence

```
Code Written
    │
    ▼
┌─────────────────────────────────────┐
│ 1. COMPILE/BUILD CHECK              │
│    - Python: syntax check           │
│    - TypeScript: type-check         │
│    - Build: npm run build           │
└────────────────┬────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────┐
│ 2. CLAUDE.md COMPLIANCE             │
│    @claude-md-compliance-checker    │
│    - Goal counting rules?           │
│    - Vectorized operations?         │
│    - Key formatting?                │
│    - No .iterrows()?                │
└────────────────┬────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────┐
│ 3. TESTS                            │
│    - pytest (Python)                │
│    - npm test (TypeScript)          │
│    - ETL validation                 │
└────────────────┬────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────┐
│ 4. SPECIALIST REVIEW (if needed)    │
│    - Hockey SME (calculations)      │
│    - Supabase (DB changes)          │
│    - Dashboard (UI changes)         │
└────────────────┬────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────┐
│ 5. CODE QUALITY PRAGMATIST          │
│    @code-quality-pragmatist         │
│    - Over-engineered?               │
│    - Unnecessary complexity?        │
└────────────────┬────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────┐
│ 6. TASK COMPLETION VALIDATOR        │
│    @task-completion-validator       │
│    - Does it actually work?         │
│    - Not stubbed or mocked?         │
└────────────────┬────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────┐
│ 7. REALITY CHECK (Karen)            │
│    @karen                           │
│    - Matches requirements?          │
│    - No BS completion claims?       │
└────────────────┬────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────┐
│ 8. DOC SYNC                         │
│    /doc-sync                        │
│    - Update relevant docs           │
│    - Sync GitHub issues             │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ 9. ISSUE MANAGEMENT                 │
│    - Update issue status            │
│    - Create issues for failures     │
│    - Reorg if needed                │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ 10. COMMIT PREP (if --commit/--pr)  │
│    - Stage changes                  │
│    - Generate message               │
│    - Create PR (if --pr)            │
└────────────────┬────────────────────┘
                 │
                 ▼
            ✅ DONE
```

---

## Execution Commands

### Step 1: Build Check

```bash
# Python syntax
python -m py_compile run_etl.py

# TypeScript
cd ui/dashboard && npm run type-check

# Full build (catches more issues)
cd ui/dashboard && npm run build
```

### Step 2: CLAUDE.md Compliance

```bash
# Check for .iterrows() violations
grep -r "iterrows" src/

# Check goal counting (should use proper filter)
grep -r "event_type.*Shot.*Goal" src/  # Should return nothing
```

Call @claude-md-compliance-checker agent for thorough review.

### Step 3: Tests

```bash
# ETL validation (critical!)
./benchsight.sh etl validate

# Python tests
pytest tests/ -x -v

# Dashboard tests
cd ui/dashboard && npm test
```

### Step 4: Specialist Review

Based on files changed:

| Files Changed | Specialist | Invoke |
|---------------|------------|--------|
| `src/calculations/*` | Hockey Stats SME | `/hockey-stats` |
| `src/core/*`, `src/tables/*` | ETL Specialist | Use Task with etl-specialist |
| `ui/dashboard/*` | Dashboard Developer | Use Task with dashboard-developer |
| DB/migrations | Supabase Specialist | Use Task with supabase-specialist |

### Step 5: Code Quality

Call @code-quality-pragmatist to check for:
- Over-engineering
- Unnecessary abstractions
- YAGNI violations
- Premature optimization

### Step 6: Task Completion

Call @task-completion-validator to verify:
- Code actually works
- Not stubbed or mocked
- Error handling exists
- Edge cases handled

### Step 7: Reality Check

Call @karen agent to cut through any BS:
- Does it ACTUALLY work?
- Did we implement what was asked?
- No fake completions?

### Step 8: Doc Sync

```bash
# Check for stale docs
./scripts/docs-check.sh

# Sync GitHub issues
./scripts/sync-github-issues.sh

# Run doc-sync skill
/doc-sync
```

### Step 9: Issue Management

```bash
# Update issue if working on one
gh issue comment [NUMBER] --body "Progress update: [details]"

# Create issues for failures found
gh issue create --title "[TYPE] Issue found during validation" --body "..."

# Close if complete
gh issue close [NUMBER] --comment "Completed in [commit]"
```

### Step 10: Commit Prep

```bash
# Stage changes
git add -A

# Review
git status
git diff --cached

# Commit with proper format
git commit -m "[TYPE] Description

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Quick Mode (`/post-code quick`)

For minor changes, minimum checks:

```bash
# Minimum viable validation
python -m py_compile <changed_files> && \
cd ui/dashboard && npm run type-check && \
./benchsight.sh etl validate && \
pytest tests/ -x
```

Skips: Specialist review, quality check, reality check, doc sync

---

## Commit Mode (`/post-code commit`)

Full workflow plus:
- Auto-stage changes
- Generate commit message
- Prompt for confirmation
- Commit with Co-Author

---

## PR Mode (`/post-code pr`)

Full workflow plus:
- Create branch if needed
- Push to remote
- Create PR with:
  - Summary of changes
  - Test results
  - Validation status

---

## Output Report

```
═══════════════════════════════════════════════════
              POST-CODE VALIDATION REPORT
═══════════════════════════════════════════════════

 1. Build:        ✅ PASS
 2. Compliance:   ✅ PASS (no CLAUDE.md violations)
 3. Tests:        ✅ PASS (42 passed, 0 failed)
 4. Specialist:   ✅ PASS (hockey-stats verified)
 5. Quality:      ✅ PASS (no over-engineering)
 6. Completion:   ✅ PASS (implementation complete)
 7. Reality:      ✅ PASS (Karen approved)
 8. Docs:         ⚠️  UPDATE NEEDED
    - docs/etl/calculations.md
 9. Issues:       ℹ️  #31 should be updated

═══════════════════════════════════════════════════
STATUS: READY FOR COMMIT (with doc updates)
═══════════════════════════════════════════════════

Suggested actions:
  1. Update docs/etl/calculations.md
  2. Run: gh issue comment 31 --body "Progress: ..."
  3. Run: git add -A && git commit -m "[FIX] ..."
```

---

## When to Skip Steps

| Change Type | Skip Steps |
|-------------|------------|
| Typo fix | 4-7 |
| Comment only | 2-9 |
| Config change | 4-7 |
| Major feature | NONE - run all |
| Bug fix | 5 only |
| Refactor | 7 only |

---

## Failure Handling

If any step fails:

1. **Build failure** → Fix syntax/type errors first
2. **Compliance failure** → Fix CLAUDE.md violation immediately
3. **Test failure** → Fix tests before continuing
4. **Quality issues** → Consider simplifying
5. **Reality check fail** → Re-evaluate what was actually done

**NEVER commit with failures!**

Create GitHub issue for any failures that can't be fixed immediately:
```bash
gh issue create --title "[FIX] [description]" \
  --body "Found during post-code validation: ..." \
  --label "type:fix,priority:p1,phase:2"
```

---

## Integration with PM Skill

After `/post-code`, consider running `/pm` to:
- Get next task recommendation
- Check phase progress
- Identify parallel work opportunities
