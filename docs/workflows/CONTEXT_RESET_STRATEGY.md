# Context Reset Strategy

**Planning and execution are separate conversations**

Last Updated: 2026-01-15

---

## Overview

Context window degradation is real. After many messages, coding agents get overwhelmed and repeat mistakes/bad assumptions. Fresh starts provide sharp focus and better results.

**Principle:** Planning and execution are SEPARATE conversations.

---

## When to Reset Context

### After Planning

**Reset when:**
- PRD is complete
- Implementation plan is ready
- Technical design is finalized
- Ready to start coding

**Why:**
- Planning conversation has accumulated context
- Execution needs clean, focused context
- PRD becomes the source of truth

### Before Execution

**Reset when:**
- Starting implementation
- Beginning new phase
- Switching components
- After long planning session

**Why:**
- Fresh start = sharp focus
- PRD provides all needed context
- Avoids confusion from planning details

---

## How to Reset Context

### Method 1: New Conversation

**Steps:**
1. End planning conversation
2. Start new conversation
3. Reference PRD immediately
4. Begin implementation

**Example:**
```
New conversation:
"I'm implementing [feature] as specified in 
docs/prds/features/[feature-name].md

Let's start with Phase 1: [phase name]"
```

### Method 2: Clear Context

**Steps:**
1. Summarize key points
2. Reference PRD
3. Clear conversation history
4. Start fresh

---

## Planning Conversation Structure

### Start Planning

**Opening:**
```
I'm planning to implement [feature]. 
Please read docs/prds/features/[feature-name].md 
and help me refine the plan.
```

**Focus:**
- Research and design
- Create/refine PRD
- Break down into phases
- Identify dependencies
- Assess risks

**Output:**
- Complete PRD
- Clear implementation plan
- Phased approach

### End Planning

**Closing:**
```
Planning complete. PRD is at docs/prds/features/[feature-name].md

Next: Start new conversation for implementation.
```

---

## Execution Conversation Structure

### Start Execution

**Opening:**
```
I'm implementing [feature] as specified in 
docs/prds/features/[feature-name].md

Let's start with Phase 1: [phase name]
```

**Reference PRD:**
- "Following the PRD..."
- "As specified in Phase 1..."
- "Per the technical design..."

**Focus:**
- Implementation
- Code quality
- Testing
- Documentation

### During Execution

**Keep PRD Updated:**
- Document learnings
- Update phases
- Adjust timeline
- Note decisions

**Stay Focused:**
- One phase at a time
- Reference PRD frequently
- Avoid scope creep

---

## Context Handoff Process

### Planning → Execution Handoff

**Document:**
1. PRD location
2. Current phase
3. Key decisions
4. Dependencies
5. Next steps

**Template:** `docs/templates/context-handoff.md`

**Example:**
```markdown
# Context Handoff: [Feature Name]

**PRD:** docs/prds/features/[feature-name].md
**Status:** Planning complete, ready for implementation
**Phase:** Phase 1 - [Phase Name]
**Key Decisions:** [Decisions made]
**Next Steps:** [What to do next]
```

---

## Best Practices

### ✅ Do:

- Reset after planning
- Reference PRD in execution
- Keep PRD updated
- Stay focused on current phase
- Document decisions in PRD

### ❌ Don't:

- Mix planning and execution
- Continue long conversations
- Ignore context degradation
- Skip PRD updates
- Lose focus on current phase

---

## Examples

### Example 1: Feature Implementation

**Planning Conversation:**
1. Research feature requirements
2. Create PRD
3. Design technical approach
4. Break into phases
5. End conversation

**Reset Context**

**Execution Conversation:**
1. Start new conversation
2. Reference PRD
3. Implement Phase 1
4. Update PRD
5. Continue to Phase 2

### Example 2: Bug Fix

**Planning Conversation:**
1. Analyze bug
2. Identify root cause
3. Design fix
4. Create PRD (if significant)
5. End conversation

**Reset Context**

**Execution Conversation:**
1. Start new conversation
2. Reference PRD/bug analysis
3. Implement fix
4. Test fix
5. Document solution

---

## Context Degradation Warning Signs

**Watch for:**
- Agent repeating mistakes
- Agent making bad assumptions
- Agent forgetting earlier decisions
- Agent suggesting already-discussed approaches
- Agent losing focus

**When you see these:**
- Reset context
- Start fresh conversation
- Reference PRD/planning docs

---

## Related Documentation

- [PLANNING_WORKFLOW.md](PLANNING_WORKFLOW.md) - PRD-first development
- [templates/context-handoff.md](templates/context-handoff.md) - Handoff template
- [templates/planning-conversation.md](templates/planning-conversation.md) - Planning template
- [templates/execution-conversation.md](templates/execution-conversation.md) - Execution template

---

*Last Updated: 2026-01-15*
