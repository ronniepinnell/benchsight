---
name: reality-check
description: Call the Karen agent to validate actual project state vs claimed progress. Use when tasks are marked done but functionality is unclear, or when you suspect incomplete work.
---

# Reality Check: Validate Task Completion

Cut through claimed completions and assess what actually works.

## When to Use

- Tasks marked "done" but functionality unclear
- Multiple completions claimed but errors occurring
- Need to verify implementation matches spec
- Suspicious about claimed progress

## What This Does

Runs the validation chain:
1. `task-completion-validator` - Does it actually work?
2. `code-quality-pragmatist` - Is it over-engineered?
3. `Jenny` - Does it match the spec?
4. `claude-md-compliance-checker` - Follows project rules?

## Task

$ARGUMENTS

Validate this claim by:
1. Finding and examining the actual implementation
2. Testing code to ensure it works end-to-end
3. Comparing against requirements/spec
4. Identifying gaps or incomplete pieces
5. Creating realistic plan to finish if needed

Do NOT accept superficial implementations or mocks.
