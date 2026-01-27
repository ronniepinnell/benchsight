# Claude Code Best Practices Guide

**Complete guide to using Claude Code effectively for the BenchSight project**

Last Updated: 2025-01-22

---

## Table of Contents

1. [Context Window Management](#context-window-management)
2. [When to Reset Context](#when-to-reset-context)
3. [Planning vs Execution](#planning-vs-execution)
4. [Hook, Skill, Agent Integration](#hook-skill-agent-integration)
5. [Effective Prompting](#effective-prompting)
6. [Workflow Patterns](#workflow-patterns)
7. [BenchSight-Specific Best Practices](#benchsight-specific-best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Context Window Management

### Understanding Context Windows

Claude Code has a limited context window (~200K tokens). As conversations grow:
- Earlier context gets summarized
- Claude may lose track of details
- Mistakes/bad assumptions compound
- Performance degrades

### Signs of Context Degradation

Watch for:
- Repeating mistakes you've already corrected
- Forgetting earlier decisions
- Suggesting already-discussed approaches
- Losing focus on the current task
- Making incorrect assumptions

### How to Manage Context

**DO:**
- Use PRDs/docs as external memory
- Reset context between phases
- Reference docs instead of re-explaining
- Keep focused on one task at a time

**DON'T:**
- Have 100+ message conversations
- Mix planning and execution
- Expect Claude to remember everything
- Ignore degradation signs

---

## When to Reset Context

### Always Reset After:

| Trigger | Action |
|---------|--------|
| Planning complete | Start new conversation for execution |
| Switching phases | Start fresh with new phase context |
| After 50+ messages | Evaluate if reset needed |
| Task complete | Start new for next task |
| Signs of degradation | Reset immediately |

### How to Reset

**Method 1: New Conversation**
```
End current conversation
Start new conversation
Reference: "I'm implementing X as specified in docs/prds/Y.md"
```

**Method 2: Clear Context Command**
```
/clear (if available)
```

**Method 3: Explicit Handoff**
```
Create docs/handoffs/YYYY-MM-DD-task-name.md with:
- Current state
- Decisions made
- Next steps
- Reference docs

Then start new conversation referencing handoff doc
```

### The PRD Pattern

**Planning Conversation:**
1. Research requirements
2. Create/refine PRD
3. Design approach
4. End conversation

**Reset**

**Execution Conversation:**
1. Start fresh
2. Reference PRD: "Implementing per docs/prds/feature.md"
3. Execute phases
4. Update PRD with learnings

---

## Planning vs Execution

### Key Principle

**Planning and execution are SEPARATE conversations.**

### Planning Phase

**Purpose:** Research, design, document

**Activities:**
- Read existing code/docs
- Design architecture
- Create PRD
- Break into phases
- Identify risks

**Output:**
- Complete PRD in `docs/prds/`
- Clear implementation plan
- Success criteria

**Duration:** Until PRD is ready

### Execution Phase

**Purpose:** Implement the plan

**Activities:**
- Follow PRD step-by-step
- Write code
- Run tests
- Update docs

**Input:**
- Reference PRD frequently
- Follow defined phases

**Duration:** Until phase/task complete

### Why Separate?

| Planning | Execution |
|----------|-----------|
| Explores options | Follows one path |
| Accumulates context | Needs fresh focus |
| Makes decisions | Implements decisions |
| Output = PRD | Output = Code |

---

## Hook, Skill, Agent Integration

### The Three Pillars

| Component | Type | When It Runs |
|-----------|------|--------------|
| Hooks | Automatic | On tool calls |
| Skills | On-demand | When you invoke |
| Agents | Specialized | For complex tasks |

### How They Work Together

```
You write code
  ↓
Hook validates (automatic)
  ↓
You run /validate skill (on-demand)
  ↓
Skill invokes agents for deep analysis (specialized)
  ↓
Results inform next steps
```

### Integration Patterns

**Pattern 1: Hook → Skill**
```
Hook warns about issue → You run skill to fix
Example: doc-update-reminder → /doc-sync
```

**Pattern 2: Skill → Agent**
```
Skill delegates to specialized agent
Example: /post-code → invokes compliance-checker, code-quality-pragmatist
```

**Pattern 3: Full Chain**
```
Edit code → goal-counting-guard (hook)
Run /etl → etl-integrity-check (hook)
Run /validate → validation logic (skill)
Run /compliance-check → compliance-checker (agent)
Run /pr-workflow → create PR (skill)
```

### Orchestrating Complex Workflows

**ETL Development:**
```
1. Write ETL code
   - Hook: goal-counting-guard validates

2. Run /etl
   - Skill: runs pipeline
   - Hook: etl-integrity-check validates output
   - Hook: post-etl-reminder suggests /validate

3. Run /validate
   - Skill: comprehensive validation

4. Run /compliance-check
   - Agent: claude-md-compliance-checker reviews

5. Run /pr-workflow
   - Skill: creates PR with proper format
```

**Dashboard Development:**
```
1. Start /dashboard-dev
   - Skill: starts dev server

2. Write component code
   - Hook: validates patterns

3. Run /post-code
   - Skill: orchestrates validation
   - Agent: code-quality-pragmatist reviews
   - Agent: claude-md-compliance-checker reviews

4. Run /pr-workflow
```

---

## Effective Prompting

### Be Specific

```
# BAD
"Fix the bug"

# GOOD
"Fix the goal counting bug in src/calculations/goals.py.
Goals should only count when event_type='Goal' AND event_detail='Goal_Scored'.
Currently it's counting event_type='Shot' with event_detail='Goal'."
```

### Reference Docs

```
# BAD
"Implement the feature we discussed"

# GOOD
"Implement the xG calculation per docs/prds/xg-model.md,
specifically Phase 2: Feature Engineering"
```

### Provide Context

```
# BAD
"Why isn't this working?"

# GOOD
"The ETL is failing at Phase 4 with error 'KeyError: player_id'.
Here's the relevant code: [code]
Here's the input data structure: [structure]
What's causing the error?"
```

### Set Expectations

```
# BAD
"Build the dashboard"

# GOOD
"Create the player comparison page (docs/prds/player-comparison.md).
Acceptance criteria:
- Select 2-5 players
- Compare stats in table format
- Show radar chart visualization
Let's start with the data fetching hook."
```

### Use Skills Instead of Explaining

```
# BAD
"Run the ETL pipeline by executing ./benchsight.sh etl run
and then check the output tables..."

# GOOD
"/etl"
```

---

## Workflow Patterns

### Daily Development Flow

```
Morning:
1. Review TODO/issues
2. Start fresh conversation
3. Reference today's task

Working:
1. Focus on one task
2. Use skills for common operations
3. Let hooks validate

Committing:
1. /compliance-check
2. /doc-sync (if needed)
3. /pr-workflow

End of day:
1. Update PRD with progress
2. Create handoff doc if needed
```

### Task-Based Flow

```
1. Create/read PRD for task
2. Start fresh conversation
3. Reference PRD explicitly
4. Execute one phase
5. Validate with skills
6. Update PRD
7. Repeat until complete
```

### Debug Flow

```
1. Start fresh conversation
2. Describe specific issue
3. Use /reality-check if unclear
4. Investigate systematically
5. Propose fix
6. Implement and validate
7. Document root cause
```

---

## BenchSight-Specific Best Practices

### Always Remember

| Rule | Why |
|------|-----|
| Goal counting: `event_type='Goal' AND event_detail='Goal_Scored'` | #1 data integrity rule |
| Never use `.iterrows()` | Performance critical |
| Stat attribution: `player_role='event_player_1'` | Prevent double-counting |
| Keys format: `{XX}{ID}{5D}` | Consistency |
| 139 tables target | Schema contract |

### Before Any ETL Work

1. Re-read goal counting rule
2. Understand which tables affected
3. Plan vectorized approach
4. Consider validation needs

### Before Any Dashboard Work

1. Check which Supabase views exist
2. Understand data flow
3. Plan component structure
4. Consider server vs client

### Before Any Calculation Work

1. Consult `/hockey-stats` for methodology
2. Check `config/formulas.json`
3. Plan validation tests
4. Document formula

### Reference These Docs

| Doc | When |
|-----|------|
| `CLAUDE.md` | Always |
| `docs/etl/CODE_FLOW_ETL.md` | ETL work |
| `docs/data/DATA_DICTIONARY.md` | Table questions |
| `docs/MASTER_ROADMAP.md` | Planning |
| `config/formulas.json` | Calculations |

---

## Troubleshooting

### "Claude keeps making the same mistake"

**Cause:** Context degradation or unclear instruction

**Fix:**
1. Reset context (new conversation)
2. Be more explicit about the rule
3. Add hook if recurring

### "Claude forgot what we decided"

**Cause:** Context too long, decision lost

**Fix:**
1. Document decisions in PRD
2. Reference doc in new conversation
3. Keep conversations focused

### "Skills/hooks not working"

**Cause:** Registration or path issues

**Fix:**
1. Check `.claude/settings.json`
2. Verify file paths
3. Test manually

### "Agent giving wrong advice"

**Cause:** Missing project context

**Fix:**
1. Add BenchSight context to agent
2. Reference project docs in prompt
3. Be specific about constraints

### "Too many agents/skills, confusion"

**Cause:** Unclear when to use what

**Fix:**
1. Use this guide's "When to Call" sections
2. Start simple (hooks + 2-3 skills)
3. Add complexity gradually

---

## Quick Reference Card

### Context Management
```
- Reset after planning
- Reset after 50+ messages
- Reset on degradation signs
- Always reference PRD in execution
```

### Daily Commands
```
/dashboard-dev    - Start dashboard server
/etl              - Run ETL pipeline
/validate         - Validate ETL output
/compliance-check - Check CLAUDE.md rules
/pr-workflow      - Create pull request
```

### Key Agents
```
hockey-analytics-sme  - Stat methodology
karen                 - Reality check
Jenny                 - Spec validation
code-quality-pragmatist - Over-engineering check
```

### Critical Rules
```
Goals: event_type='Goal' AND event_detail='Goal_Scored'
Stats: player_role='event_player_1'
Code: Never use .iterrows()
Keys: {XX}{ID}{5D} format
```

---

## Related Documentation

- [HOOKS_GUIDE.md](HOOKS_GUIDE.md) - Hooks guide
- [SKILLS_GUIDE.md](SKILLS_GUIDE.md) - Skills guide
- [AGENTS_GUIDE.md](../agents/AGENTS_GUIDE.md) - Agents guide
- [docs/workflows/CONTEXT_RESET_STRATEGY.md](../../docs/workflows/CONTEXT_RESET_STRATEGY.md) - Context reset strategy
- [docs/workflows/PLANNING_WORKFLOW.md](../../docs/workflows/PLANNING_WORKFLOW.md) - PRD workflow

---

*Last Updated: 2025-01-22*
