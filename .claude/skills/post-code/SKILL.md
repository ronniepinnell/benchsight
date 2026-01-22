---
name: post-code
description: Run the complete post-code validation and documentation workflow. This is the MASTER skill to run after writing any code - it orchestrates all validation agents in the correct order.
allowed-tools: Bash, Read, Task
---

# Post-Code Workflow Orchestrator

Run this after writing ANY code to ensure quality, compliance, and documentation.

## The Golden Rule

**NEVER mark code as complete without running `/post-code`**

## Workflow Sequence

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
│ 2. TASK COMPLETION VALIDATOR        │
│    @task-completion-validator       │
│    - Does it actually work?         │
│    - Not stubbed or mocked?         │
│    - Error handling exists?         │
└────────────────┬────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────┐
│ 3. CODE QUALITY PRAGMATIST          │
│    @code-quality-pragmatist         │
│    - Over-engineered?               │
│    - Unnecessary complexity?        │
│    - YAGNI violations?              │
└────────────────┬────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────┐
│ 4. CLAUDE-MD COMPLIANCE             │
│    @claude-md-compliance-checker    │
│    - Goal counting rules?           │
│    - Vectorized operations?         │
│    - Key formatting?                │
└────────────────┬────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────┐
│ 5. JENNY (Spec Verification)        │
│    @Jenny                           │
│    - Matches requirements?          │
│    - No missing features?           │
│    - No extra features?             │
└────────────────┬────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────┐
│ 6. TESTS                            │
│    - pytest (Python)                │
│    - npm test (TypeScript)          │
│    - ETL validation                 │
└────────────────┬────────────────────┘
                 │ Pass?
                 ▼
┌─────────────────────────────────────┐
│ 7. DOC SYNC                         │
│    /doc-sync                        │
│    - Update relevant docs           │
│    - Flag outdated docs             │
└────────────────┬────────────────────┘
                 │
                 ▼
            ✅ READY
```

## Execution Commands

Run each step in sequence. Stop on first failure.

### Step 1: Build Check
```bash
# Python
python -m py_compile <changed_files>

# TypeScript
cd ui/dashboard && npm run type-check

# Full build
cd ui/dashboard && npm run build
```

### Step 2: Task Completion Validator
```
Call @task-completion-validator agent with:
"Validate the following code changes actually work: <description>"
```

### Step 3: Code Quality Pragmatist
```
Call @code-quality-pragmatist agent with:
"Review for over-engineering: <changed_files>"
```

### Step 4: CLAUDE.md Compliance
```
Call @claude-md-compliance-checker agent with:
"Check compliance for: <changed_files>"
```

### Step 5: Jenny (Spec Verification)
```
Call @Jenny agent with:
"Verify implementation matches spec: <feature_description>"
```

### Step 6: Tests
```bash
# ETL changes
./benchsight.sh etl validate

# Python tests
pytest tests/ -x

# Dashboard tests
cd ui/dashboard && npm test
```

### Step 7: Doc Sync
```
Run /doc-sync to update documentation
```

## Quick Mode

For minor changes, minimum checks:

```bash
# Minimum viable validation
npm run type-check && \
npm run build && \
./benchsight.sh etl validate
```

## Output

Post-code report:
```
POST-CODE VALIDATION REPORT
===========================
1. Build:      ✅ PASS
2. Completion: ✅ PASS
3. Quality:    ✅ PASS (no over-engineering)
4. Compliance: ✅ PASS
5. Spec:       ✅ PASS
6. Tests:      ✅ PASS (23 passed, 0 failed)
7. Docs:       ⚠️  UPDATE NEEDED (2 files)

STATUS: READY FOR COMMIT
```

## When to Skip Steps

| Change Type | Skip |
|-------------|------|
| Typo fix | Steps 2-5 |
| Comment only | Steps 2-7 |
| Config change | Steps 2-5 |
| Major feature | NONE - run all |
| Bug fix | Step 5 (Jenny) |
