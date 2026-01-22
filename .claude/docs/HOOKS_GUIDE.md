# BenchSight Hooks Guide

**Complete guide to understanding, using, editing, and creating Claude Code hooks**

Last Updated: 2025-01-22

---

## Table of Contents

1. [What Are Hooks?](#what-are-hooks)
2. [How Hooks Work](#how-hooks-work)
3. [Current BenchSight Hooks](#current-benchsight-hooks)
4. [When to Call Each Hook](#when-to-call-each-hook)
5. [How to Edit Hooks](#how-to-edit-hooks)
6. [How to Add Files to doc-update-reminder](#how-to-add-files-to-doc-update-reminder)
7. [Creating New Hooks](#creating-new-hooks)
8. [Hook Chains and Integration](#hook-chains-and-integration)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## What Are Hooks?

Hooks are Python scripts that automatically run in response to Claude Code tool calls. They act as guardrails, validators, and reminders that:

- **Prevent mistakes** before they happen
- **Remind you** of important standards
- **Validate** code/data integrity
- **Enforce** project-specific rules

**Location:** `.claude/hooks/`

**Configuration:** Hooks are registered in `.claude/settings.json` (or globally in `~/.claude/settings.json`)

---

## How Hooks Work

### Trigger Types

Hooks can trigger on:

| Trigger | When It Runs |
|---------|--------------|
| `PreToolUse` | BEFORE a tool executes |
| `PostToolUse` | AFTER a tool executes |
| `Notification` | On specific events |

### Hook Input

Hooks receive JSON input via stdin:

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "git commit -m 'message'"
  },
  "session_id": "abc123"
}
```

### Hook Output

Hooks output JSON to stdout with a decision:

```json
{
  "decision": "allow",  // or "block", "ask"
  "reason": "Optional message to show"
}
```

| Decision | Effect |
|----------|--------|
| `allow` | Let the tool proceed (silent) |
| `block` | Stop the tool with error message |
| `ask` | Prompt user to confirm |

---

## Current BenchSight Hooks

### 1. `goal-counting-guard.py` (P0 CRITICAL)

**Purpose:** Prevents incorrect goal counting patterns

**Triggers:** `PreToolUse` on Edit, Write

**What it catches:**
- `event_type == 'Shot'` when counting goals
- Missing `event_detail == 'Goal_Scored'` check
- Direct `event_type == 'Goal'` without the AND

**Why it matters:** Goal counting is the #1 data integrity rule in BenchSight

**Example block:**
```
GOAL COUNTING VIOLATION DETECTED

Found: event_type == 'Shot'
This may incorrectly count shots as goals!

RULE: Goals ONLY when event_type='Goal' AND event_detail='Goal_Scored'
```

---

### 2. `bash-validator.py`

**Purpose:** Validates bash commands for safety

**Triggers:** `PreToolUse` on Bash

**What it catches:**
- Dangerous commands (rm -rf, force push)
- Git push to protected branches without flag
- Accidental production operations

---

### 3. `etl-integrity-check.py`

**Purpose:** Verifies ETL output after runs

**Triggers:** `PostToolUse` on Bash (when running ETL)

**What it checks:**
- Table count matches expected
- Key tables have data
- No duplicate primary keys

---

### 4. `etl-failure-handler.py`

**Purpose:** Creates GitHub issues on ETL failures

**Triggers:** `PostToolUse` on Bash (when ETL fails)

**What it does:**
- Captures error output
- Creates detailed GitHub issue
- Tags with appropriate labels

---

### 5. `post-etl-reminder.py`

**Purpose:** Reminds to validate after ETL runs

**Triggers:** `PostToolUse` on Bash (when running ETL)

**What it suggests:**
- Run `/validate` skill
- Check goal counts
- Verify table counts

---

### 6. `doc-update-reminder.py`

**Purpose:** Reminds to update docs when code changes

**Triggers:** `PreToolUse` on Bash (git commit)

**What it checks:**
- Code files staged but no docs
- Suggests relevant doc files to update

---

## When to Call Each Hook

Hooks are called **automatically** based on triggers. You don't call them manually.

| Action You Take | Hooks That Fire |
|-----------------|-----------------|
| Edit Python file | `goal-counting-guard.py` |
| Run `git commit` | `doc-update-reminder.py` |
| Run `./benchsight.sh etl run` | `etl-integrity-check.py`, `post-etl-reminder.py` |
| ETL fails | `etl-failure-handler.py` |
| Run `rm` command | `bash-validator.py` |

---

## How to Edit Hooks

### Step 1: Locate the Hook

```bash
ls -la .claude/hooks/
```

### Step 2: Read and Understand

Read the hook file to understand:
- What triggers it (`tool_name` check)
- What it validates (regex patterns, conditions)
- What output it produces

### Step 3: Edit the Python Script

```python
# Example: Add new file to doc-update-reminder.py

# Find the doc_suggestions list and add:
if any(f.startswith('src/tables/') for f in staged_files):
    doc_suggestions.append("- docs/data/DATA_DICTIONARY.md (table changes)")
```

### Step 4: Test the Hook

```bash
# Test with sample input
echo '{"tool_name": "Bash", "tool_input": {"command": "git commit"}}' | python .claude/hooks/doc-update-reminder.py
```

### Step 5: Verify No Errors

```bash
# Run Python syntax check
python -m py_compile .claude/hooks/your-hook.py
```

---

## How to Add Files to doc-update-reminder

### Current Mappings (in `doc-update-reminder.py`)

```python
# ETL changes
if any(f.startswith('src/core/') for f in staged_files):
    doc_suggestions.append("- docs/etl/CODE_FLOW_ETL.md")

# API changes
if any(f.startswith('api/routes/') for f in staged_files):
    doc_suggestions.append("- docs/api/endpoints.md")

# Dashboard changes
if any(f.startswith('ui/dashboard/') for f in staged_files):
    doc_suggestions.append("- docs/dashboard/")

# Tracker changes
if any(f.startswith('ui/tracker/') for f in staged_files):
    doc_suggestions.append("- docs/tracker/TRACKER_REFERENCE.md")

# Skills/hooks changes
if any(f.startswith('.claude/skills/') for f in staged_files):
    doc_suggestions.append("- docs/MASTER_INDEX.md")
    doc_suggestions.append("- CLAUDE.md")
```

### To Add New Mappings

Edit `.claude/hooks/doc-update-reminder.py` and add to the `doc_suggestions` section:

```python
# Add after existing mappings:

# Data dictionary changes
if any(f.startswith('src/tables/') for f in staged_files):
    doc_suggestions.append("- docs/data/DATA_DICTIONARY.md (table structure changes)")

# Calculation changes
if any(f.startswith('src/calculations/') for f in staged_files):
    doc_suggestions.append("- docs/reference/FORMULA_DEFINITIONS.md (calculation changes)")

# Database migration changes
if any('migrations' in f or f.endswith('.sql') for f in staged_files):
    doc_suggestions.append("- docs/data/SCHEMA_CHANGES.md (migration changes)")

# Test changes
if any(f.startswith('tests/') for f in staged_files):
    doc_suggestions.append("- docs/testing/TEST_COVERAGE.md (test changes)")

# Configuration changes
if any(f.startswith('config/') for f in staged_files):
    doc_suggestions.append("- docs/setup/CONFIGURATION.md (config changes)")
```

### Recommended Additions for BenchSight

| Code Path | Doc File to Update |
|-----------|-------------------|
| `src/tables/` | `docs/data/DATA_DICTIONARY.md` |
| `src/calculations/` | `docs/reference/FORMULA_DEFINITIONS.md` |
| `config/formulas.json` | `docs/reference/FORMULA_DEFINITIONS.md` |
| `tests/` | `docs/testing/` |
| `.github/workflows/` | `docs/workflows/CI_CD.md` |
| `scripts/` | `docs/MASTER_INDEX.md` |
| `benchsight.sh` | `CLAUDE.md` (commands section) |

---

## Creating New Hooks

### Template

```python
#!/usr/bin/env python3
"""
hook-name.py - Brief description of what this hook does.

Triggers on [tool] commands and checks for [condition].
"""
import json
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only trigger on specific tools
    if tool_name != "YourTargetTool":
        sys.exit(0)

    # Your validation logic here
    should_block = False
    reason = ""

    if should_block:
        print(json.dumps({
            "decision": "block",  # or "ask"
            "reason": reason
        }))

    # Silent allow (no output needed)
    sys.exit(0)


if __name__ == "__main__":
    main()
```

### Registering a Hook

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "ToolName",
        "command": "python .claude/hooks/your-hook.py"
      }
    ]
  }
}
```

### Suggested New Hooks for BenchSight

| Hook Name | Purpose | Trigger |
|-----------|---------|---------|
| `iterrows-guard.py` | Block `.iterrows()` usage | PreToolUse (Edit/Write) |
| `stat-attribution-guard.py` | Ensure `player_role='event_player_1'` | PreToolUse (Edit/Write) |
| `test-reminder.py` | Remind to run tests before commit | PreToolUse (Bash: git commit) |
| `env-safety.py` | Block production commands in dev | PreToolUse (Bash) |
| `roadmap-update-reminder.py` | Remind to update roadmap on phase changes | PreToolUse (Bash: git commit) |

---

## Hook Chains and Integration

### Example Chain: ETL Development

1. **Write ETL code** → `goal-counting-guard.py` validates
2. **Run ETL** → `etl-integrity-check.py` validates output
3. **ETL succeeds** → `post-etl-reminder.py` suggests validation
4. **ETL fails** → `etl-failure-handler.py` creates issue
5. **Commit changes** → `doc-update-reminder.py` suggests docs

### Integrating Hooks with Skills

Hooks and skills work together:

- **Hooks** = Automatic guardrails (passive)
- **Skills** = On-demand actions (active)

Example flow:
1. `post-etl-reminder.py` suggests running `/validate`
2. You run `/validate` skill
3. Skill performs comprehensive validation
4. Results inform next steps

### Integrating Hooks with Agents

Hooks fire regardless of which agent is running:

- `karen` agent edits code → `goal-counting-guard.py` still validates
- `etl-specialist` agent runs ETL → `etl-integrity-check.py` still fires

---

## Best Practices

### 1. Keep Hooks Fast

Hooks run on every tool call. Keep them < 100ms.

```python
# GOOD: Quick pattern check
if "iterrows" in content:
    # Block

# BAD: Running external commands
subprocess.run(["some", "slow", "command"])
```

### 2. Use `ask` for Reminders, `block` for Violations

```python
# Reminder (user can proceed)
print(json.dumps({"decision": "ask", "reason": "Consider updating docs"}))

# Violation (must stop)
print(json.dumps({"decision": "block", "reason": "Goal counting violation!"}))
```

### 3. Provide Actionable Messages

```python
# GOOD
"GOAL COUNTING VIOLATION: Found 'event_type == Shot'.
Use: event_type == 'Goal' AND event_detail == 'Goal_Scored'"

# BAD
"Invalid pattern detected"
```

### 4. Fail Safe

If hook errors, allow the operation:

```python
try:
    # validation logic
except Exception:
    sys.exit(0)  # Allow on error
```

### 5. Test Hooks Locally

```bash
# Create test input
cat > /tmp/test_input.json << 'EOF'
{"tool_name": "Bash", "tool_input": {"command": "git commit -m 'test'"}}
EOF

# Test hook
cat /tmp/test_input.json | python .claude/hooks/your-hook.py
```

---

## Troubleshooting

### Hook Not Firing

1. Check registration in `.claude/settings.json`
2. Verify `tool_name` matcher matches exactly
3. Check Python path is correct

### Hook Blocking Everything

1. Check condition logic (too broad?)
2. Test with specific inputs
3. Add debug logging temporarily

### Hook Errors

1. Run hook manually with test input
2. Check for Python syntax errors
3. Verify all imports available

### Debug Mode

Add temporary debug output:

```python
import sys
print(f"DEBUG: tool_name={tool_name}", file=sys.stderr)
print(f"DEBUG: tool_input={tool_input}", file=sys.stderr)
```

---

## Related Documentation

- [SKILLS_GUIDE.md](SKILLS_GUIDE.md) - Skills guide
- [AGENTS_GUIDE.md](../agents/AGENTS_GUIDE.md) - Agents guide
- [CLAUDE_CODE_BEST_PRACTICES.md](CLAUDE_CODE_BEST_PRACTICES.md) - Overall best practices
- [docs/workflows/CONTEXT_RESET_STRATEGY.md](../../docs/workflows/CONTEXT_RESET_STRATEGY.md) - Context management

---

*Last Updated: 2025-01-22*
