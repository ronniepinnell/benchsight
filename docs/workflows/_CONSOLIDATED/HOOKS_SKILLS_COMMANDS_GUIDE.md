# BenchSight Hooks, Skills & Commands Best Practices

## Overview

This guide covers the automation layer built into BenchSight's Claude Code setup: hooks (automatic triggers), skills (slash commands), and how to use them effectively.

---

## Part 1: Slash Commands (Skills)

Skills are custom commands invoked with `/command-name`. They encapsulate common workflows.

### Available Commands

| Command | Purpose | Arguments |
|---------|---------|-----------|
| `/etl` | Run ETL pipeline | `--games ID,ID` `--wipe` |
| `/validate` | Run validation suite | none |
| `/etl-issue` | Create GitHub issue for ETL failure | `last` or description |
| `/reality-check` | Assess actual vs claimed progress | description of claim |
| `/compliance-check` | Verify CLAUDE.md compliance | scope description |
| `/hockey-stats` | Consult hockey analytics SME | question or topic |

### When to Use Each

#### `/etl`
```bash
# After adding new game tracking files
/etl --games 18969

# After modifying calculations or table logic
/etl --wipe

# Regular data refresh
/etl
```

**Best practice:** Always follow with `/validate`.

#### `/validate`
```bash
# After any ETL run
/validate

# After modifying src/calculations/ files
/validate

# Before committing ETL changes
/validate
```

**Best practice:** Never skip validation. The 90-second investment catches data corruption early.

#### `/reality-check`
```bash
# When tasks marked "done" seem incomplete
/reality-check The authentication system is complete

# When multiple completions claimed but errors occur
/reality-check Dashboard player stats page is finished

# Before major releases
/reality-check All v1.0 features are implemented
```

**Best practice:** Use liberally. It's better to catch incomplete work early than discover it in production.

#### `/compliance-check`
```bash
# After implementing any feature
/compliance-check recent changes to goals calculation

# Before creating PR
/compliance-check all changes in this branch

# After refactoring
/compliance-check updated player stats module
```

**Best practice:** Run before marking any task complete.

#### `/hockey-stats`
```bash
# Before implementing new metrics
/hockey-stats How should we calculate expected goals (xG)?

# When unsure about methodology
/hockey-stats What's the difference between Corsi and Fenwick?

# For data visualization decisions
/hockey-stats Best way to display line combination effectiveness?
```

**Best practice:** Consult BEFORE writing code, not after. Saves rework.

---

## Part 2: Hooks (Automatic Triggers)

Hooks run automatically at specific lifecycle points. You don't invoke them—they protect you.

### Active Hooks

#### `bash-validator` (PreToolUse)
**Triggers:** Before any Bash command

**Blocks:**
- `rm -rf data/output` → Use `./benchsight.sh etl run --wipe`
- `rm -rf .git` → Never allowed
- `DROP TABLE fact_*` → Use migrations
- `git push --force main` → Never allowed

**Warns (asks confirmation):**
- Commands containing "production"
- Supabase migration pushes
- Vercel production deployments

**Best practice:** If blocked, read the message—it tells you the safe alternative.

#### `goal-counting-guard` (PreToolUse)
**Triggers:** Before Edit/Write on files containing goal-related patterns

**What it does:** Displays the critical goal counting rule:
```python
# ONLY this counts as a goal:
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
```

**Best practice:** Read the reminder every time. This rule is the #1 source of data bugs.

#### `post-etl-reminder` (PostToolUse)
**Triggers:** After successful ETL run commands

**What it does:** Reminds you to run `/validate`

**Best practice:** Don't dismiss it—actually run validation.

#### `etl-failure-handler` (PostToolUse)
**Triggers:** After ETL commands that fail (non-zero exit or error patterns)

**What it does:**
1. Detects ETL failures automatically
2. Extracts error details (phase, type, message, traceback)
3. Logs failure to `~/.claude/etl-failures/`
4. Prompts: "Create GitHub issue to track this?"
5. If confirmed, creates detailed issue via `gh issue create`

**Issue includes:**
- Error type and full message
- ETL phase that failed
- Complete traceback
- Recent git commits (last 5)
- Recently changed files
- Suggested actions checklist
- Labels: `bug`, `etl`, `auto-generated`

**Failure log location:** `~/.claude/etl-failures/etl_failure_YYYYMMDD_HHMMSS.json`

**Best practice:**
- Say YES for real bugs that need tracking
- Say NO for typos, config errors, or testing failures
- Review logged failures with: `ls ~/.claude/etl-failures/`

---

## Part 3: Workflow Patterns

### Pattern A: ETL Development Cycle

```
1. Make changes to src/calculations/ or src/tables/
2. /etl --wipe
3. /validate
4. /compliance-check ETL changes
5. If all pass → commit
```

### Pattern B: Feature Implementation

```
1. Understand requirements
2. /hockey-stats (if stats-related)
3. Implement feature
4. /compliance-check new feature
5. /reality-check Feature X is complete
6. If all pass → commit
```

### Pattern C: Pre-PR Checklist

```
1. /validate (if ETL changes)
2. /compliance-check all changes
3. npm run build (if dashboard changes)
4. pytest (if Python changes)
5. /reality-check All PR changes work correctly
6. Create PR
```

### Pattern D: Debugging Data Issues

```
1. /validate (identify which checks fail)
2. /hockey-stats (if methodology question)
3. Fix identified issues
4. /etl --wipe
5. /validate (confirm fix)
```

---

## Part 4: Creating New Skills

### Skill File Structure

Location: `.claude/skills/{skill-name}/SKILL.md`

```yaml
---
name: skill-name
description: When to invoke this skill (used by Claude for auto-selection)
allowed-tools: Bash, Read, Edit, Grep, Glob
argument-hint: [optional args]
---

# Skill Title

Description of what this skill does.

## Usage

How to use it with examples.

## What It Does

Step-by-step explanation.

## Task

$ARGUMENTS

Instructions for Claude to follow.
```

### Best Practices for Custom Skills

1. **Be specific in description** — Claude uses this for auto-selection
2. **Limit tools** — Only grant tools the skill needs
3. **Include $ARGUMENTS** — Allows passing context to the skill
4. **Document the "why"** — Future you will thank present you

### Example: Creating a `/dashboard-check` Skill

```yaml
---
name: dashboard-check
description: Verify dashboard builds and type-checks correctly. Use before committing dashboard changes.
allowed-tools: Bash, Read
---

# Dashboard Verification

Check that the Next.js dashboard builds without errors.

## Execution

```bash
cd ui/dashboard && npm run type-check && npm run build
```

## What This Checks

1. TypeScript strict mode compliance
2. No build-time errors
3. All imports resolve correctly
4. Server/Client component boundaries respected

## After Running

If build fails, fix errors before committing.
```

---

## Part 5: Creating New Hooks

### Hook File Structure

Location: `.claude/hooks/{hook-name}.py`

```python
#!/usr/bin/env python3
"""
Hook description.
"""
import json
import sys

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input", {})

# Your logic here

# Output options:
# sys.exit(0) - Allow (no output needed)
# print(json.dumps({"decision": "block", "reason": "..."})) - Block
# print(json.dumps({"decision": "ask", "reason": "..."})) - Ask user
# print(json.dumps({"message": "..."})) - Add context message

sys.exit(0)
```

### Hook Configuration

In `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "ToolName",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/hook-name.py\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "ToolName",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/hook-name.py\""
          }
        ]
      }
    ]
  }
}
```

### Hook Lifecycle Events

| Event | When | Use For |
|-------|------|---------|
| `PreToolUse` | Before tool executes | Validation, blocking, warnings |
| `PostToolUse` | After tool executes | Reminders, follow-up actions |
| `UserPromptSubmit` | When user sends message | Context injection |
| `SessionStart` | When session begins | Environment setup |

### Best Practices for Custom Hooks

1. **Fail gracefully** — Always wrap JSON parsing in try/except
2. **Exit 0 by default** — Non-zero exits can cause issues
3. **Be fast** — Hooks run synchronously; slow hooks = slow experience
4. **Log minimally** — Only output when you have something useful to say
5. **Use matchers** — Don't run on every tool if you only care about Bash

### Example: Pre-commit Hook for Tests

```python
#!/usr/bin/env python3
"""
Remind to run tests before git commit.
"""
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
        "message": "Reminder: Have you run tests? (pytest, npm run build)"
    }))

sys.exit(0)
```

---

## Part 6: Troubleshooting

### Skills Not Working

1. **Check file location:** Must be `.claude/skills/{name}/SKILL.md`
2. **Check YAML frontmatter:** Must have `---` delimiters
3. **Check name field:** Must match directory name
4. **Restart Claude Code:** Skills are loaded at startup

### Hooks Not Triggering

1. **Check settings.json:** Hooks must be in `hooks` object
2. **Check matcher:** Must match tool name exactly (case-sensitive)
3. **Check script permissions:** `chmod +x hook-name.py`
4. **Check script path:** Use `$CLAUDE_PROJECT_DIR` for portability
5. **Check JSON output:** Must be valid JSON if outputting anything

### Hook Blocking Everything

1. **Check exit codes:** Should exit 0 unless intentionally blocking
2. **Check JSON output:** `decision: block` stops execution
3. **Test in isolation:** `echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | python3 hook.py`

### Debugging Hooks

```bash
# Test hook with sample input
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf data/output"}}' | \
  python3 .claude/hooks/bash-validator.py

# Check for Python errors
python3 -m py_compile .claude/hooks/bash-validator.py
```

---

## Part 7: Reference

### Environment Variables Available in Hooks

| Variable | Description |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Absolute path to project root |
| `CLAUDE_SESSION_ID` | Current session identifier |
| `CLAUDE_ENV_FILE` | Path to session env file (SessionStart only) |

### Hook Input Schema (stdin)

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "the command being run"
  },
  "tool_result": {
    "stdout": "...",
    "stderr": "..."
  }
}
```

### Hook Output Schema (stdout)

```json
// Block execution
{"decision": "block", "reason": "Explanation"}

// Ask user confirmation
{"decision": "ask", "reason": "Question"}

// Add context message
{"message": "Information to display"}

// Continue silently
// (no output, just exit 0)
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

---

## Summary Cheat Sheet

### Daily Workflow
```bash
# Start of session
/validate                    # Check data state

# After ETL work
/etl --wipe && /validate     # Rebuild and verify

# After feature work
/compliance-check            # Verify rules followed
/reality-check               # Verify actually complete

# Before commit
/validate && /compliance-check
```

### When Hooks Fire
- **Edit/Write goal files** → Goal counting reminder appears
- **Run dangerous Bash** → Command blocked with safe alternative
- **Complete ETL run** → Validation reminder appears

### Quick Debugging
```bash
# Hook not working?
chmod +x .claude/hooks/*.py
python3 -m py_compile .claude/hooks/hook-name.py

# Skill not found?
ls -la .claude/skills/*/SKILL.md
```
