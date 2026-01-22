# BenchSight Agents Guide

**How and when to use each agent, plus recommendations for the project**

---

## Quick Reference: Agents by Use Case

| Situation | Agent | Trigger Phrase |
|-----------|-------|----------------|
| Need hockey stat methodology | `hockey-analytics-sme` | "What's the right way to calculate xG?" |
| Verify implementation matches spec | `Jenny` | "Does this match what we specified?" |
| Check if task is actually done | `task-completion-validator` | "Is this feature really complete?" |
| Cut through BS, get real status | `karen` | "What's the actual state of this?" |
| Review for over-engineering | `code-quality-pragmatist` | "Is this too complex?" |
| Check CLAUDE.md compliance | `claude-md-compliance-checker` | "Does this follow project rules?" |
| CI/CD or GitHub integration | `github-integration-expert` | "How do I set up deployment?" |
| UI testing (dashboard) | `ui-comprehensive-tester` | "Test the dashboard thoroughly" |
| **Understand code** | `code-explainer` | "Explain this file line by line" |
| **Understand tables** | `table-explainer` | "Explain fact_player_game_stats" |
| **Data dictionary/lineage** | `data-dictionary-specialist` | "Document this new table" |

---

## Project-Specific Agents (KEEP - Essential for BenchSight)

### 1. `hockey-analytics-sme` ⭐ ESSENTIAL
**When to use:**
- Implementing new stat calculations (xG, WAR, Corsi)
- Validating formulas against industry standards
- Designing dashboard visualizations for hockey data
- Understanding micro-stats from tracking data
- ML model feature engineering for hockey

**Example prompts:**
```
"How should we calculate expected goals given our tracking data features?"
"Is our Corsi calculation correct? Compare to Natural Stat Trick."
"What metrics should we show on a player card?"
"How do NHL Edge and MoneyPuck differ in their xG models?"
```

**BenchSight integration:** Knows the goal counting rule, stat attribution rules, faceoff logic, and assist counting from CLAUDE.md.

---

### 2. `Jenny` ⭐ ESSENTIAL
**When to use:**
- Verifying feature implementation matches requirements
- Auditing completion claims against specs
- Gap analysis between docs and code
- Pre-release validation

**Example prompts:**
```
"Does the ETL actually produce all 139 tables as specified?"
"Verify the dashboard filtering matches the PRD requirements"
"Is the multi-tenant schema implemented correctly?"
```

**Chain with:** Use before `karen` for comprehensive reality check.

---

### 3. `karen` ⭐ ESSENTIAL
**When to use:**
- Multiple tasks marked "done" but things don't work
- Need honest assessment of project state
- Creating realistic completion plans
- Cutting through false completions

**Example prompts:**
```
"What's the ACTUAL status of the ETL refactoring?"
"Several dashboard pages are marked complete but broken. Reality check?"
"Create a no-BS plan to finish the API integration"
```

**Chain with:** After `Jenny` and `task-completion-validator` for full picture.

---

### 4. `task-completion-validator` ⭐ ESSENTIAL
**When to use:**
- Developer claims a task is done
- Before marking GitHub issues closed
- PR review validation
- Post-implementation checks

**Example prompts:**
```
"Verify the ETL vectorization is actually complete"
"Is the dashboard export feature fully working?"
"Check if the API endpoint handles all error cases"
```

---

### 5. `claude-md-compliance-checker` ⭐ ESSENTIAL
**When to use:**
- After implementing features
- Before committing code
- When refactoring
- Post-PR reviews

**Example prompts:**
```
"Check if my ETL changes follow the goal counting rules"
"Does this new calculation use vectorized operations?"
"Verify I didn't violate any CLAUDE.md rules"
```

**Critical for:** Goal counting rule, vectorization requirement, stat attribution.

---

### 6. `code-quality-pragmatist` ⭐ ESSENTIAL
**When to use:**
- After implementing features
- Reviewing architectural decisions
- When code feels complex
- Before PR submission

**Example prompts:**
```
"Is this abstraction layer necessary?"
"Am I over-engineering the caching?"
"Review the new module for unnecessary complexity"
```

---

### 7. `github-integration-expert` ⭐ ESSENTIAL
**When to use:**
- Setting up CI/CD pipelines
- Configuring CodeRabbit
- Managing Vercel deployments
- Supabase migrations in CI
- Environment variable management

**Example prompts:**
```
"Set up GitHub Actions for ETL validation on PR"
"Configure CodeRabbit to check CLAUDE.md rules"
"Automate Supabase migrations on merge to main"
```

---

### 8. `ui-comprehensive-tester` ⭐ USEFUL
**When to use:**
- After dashboard page implementation
- Before deployment
- Testing responsive layouts
- Validating user flows

**Example prompts:**
```
"Test the player comparison page thoroughly"
"Verify all filters work on the standings page"
"Test the game detail page across viewports"
```

---

### 9. `code-explainer` ⭐ ESSENTIAL (NEW)
**When to use:**
- Learning a new part of the codebase
- Onboarding or knowledge transfer
- Understanding complex logic
- Preparing PR descriptions
- Creating documentation

**Example prompts:**
```
"Explain src/calculations/goals.py line by line"
"Walk me through the ETL data flow"
"Explain how shifts are calculated"
"Trace how a goal gets counted from raw data to dashboard"
```

**Features:**
- Creates **living docs** in `docs/code-docs/` that auto-update on review
- **Auto-detects issues** during explanation (CLAUDE.md violations, performance, etc.)
- **Auto-escalates CRITICAL issues** to GitHub
- Logs sessions for future reference

---

### 10. `table-explainer` ⭐ ESSENTIAL (NEW)
**When to use:**
- Understanding table schemas
- Debugging data issues
- Learning ETL output structure
- Documenting database design

**Example prompts:**
```
"Explain fact_player_game_stats"
"Show me the ETL path for dim_players"
"What columns are in fact_goals and how are they calculated?"
"Trace data lineage for the goals column"
```

**Features:**
- Creates **living docs** in `docs/table-docs/` that auto-update on review
- Shows ETL path from source to output
- Documents QA rules and validation
- Maps table relationships

---

### 11. `data-dictionary-specialist` ⭐ ESSENTIAL (NEW)
**When to use:**
- Adding new tables to DATA_DICTIONARY.md
- Tracing data lineage for columns
- Updating ERDs after schema changes
- Documenting calculation flows

**Example prompts:**
```
"Document fact_line_combinations in the data dictionary"
"Where does the xg column come from?"
"Update the ERD with new relationships"
"Trace lineage for goals column from source to dashboard"
```

**Features:**
- Maintains all `docs/data/` files
- Traces full data lineage (source → transforms → output)
- Documents column sources (explicit/calculated/derived)
- Updates ERDs and calculation flows

---

## Generic Agents Worth Keeping

### 01-core-development/
| Agent | Keep? | BenchSight Use Case |
|-------|-------|---------------------|
| `frontend-developer` | ✅ | Dashboard React/Next.js work |
| `backend-developer` | ✅ | FastAPI, ETL Python |
| `fullstack-developer` | ✅ | Cross-cutting features |
| `api-designer` | ✅ | API endpoint design |
| `ui-designer` | ✅ | Dashboard UX decisions |
| `mobile-developer` | ❌ | Not using mobile |
| `electron-pro` | ❌ | Not using Electron |
| `graphql-architect` | ❌ | Using REST, not GraphQL |
| `websocket-engineer` | 🔮 | Future real-time features |

### 02-language-specialists/
| Agent | Keep? | BenchSight Use Case |
|-------|-------|---------------------|
| `python-pro` | ✅ | ETL, calculations, API |
| `typescript-pro` | ✅ | Dashboard, type safety |
| `react-specialist` | ✅ | Dashboard components |
| `nextjs-developer` | ✅ | Dashboard framework |
| `sql-pro` | ✅ | Supabase queries |
| `rust-engineer` | 🔮 | Future tracker conversion |
| Others | ❌ | Not using |

### 03-infrastructure/
| Agent | Keep? | BenchSight Use Case |
|-------|-------|---------------------|
| `database-administrator` | ✅ | Supabase optimization |
| `devops-engineer` | ✅ | CI/CD, deployments |
| `deployment-engineer` | ✅ | Vercel deployments |
| `cloud-architect` | 🔮 | Future scaling |
| `kubernetes-specialist` | ❌ | Not using K8s |
| Azure/Windows agents | ❌ | Using Vercel/Supabase |

### 04-quality-security/
| Agent | Keep? | BenchSight Use Case |
|-------|-------|---------------------|
| `code-reviewer` | ✅ | PR reviews |
| `debugger` | ✅ | ETL debugging |
| `performance-engineer` | ✅ | ETL optimization |
| `qa-expert` | ✅ | Testing strategy |
| `test-automator` | ✅ | pytest, Jest |
| `security-auditor` | ✅ | Auth, RLS |
| PowerShell agents | ❌ | Not using |

### 05-data-ai/
| Agent | Keep? | BenchSight Use Case |
|-------|-------|---------------------|
| `data-engineer` | ✅ | ETL pipeline |
| `data-analyst` | ✅ | Hockey analytics |
| `ml-engineer` | ✅ | xG, predictions |
| `postgres-pro` | ✅ | Supabase (PostgreSQL) |
| `data-scientist` | ✅ | Analytics modeling |

### 06-developer-experience/
| Agent | Keep? | BenchSight Use Case |
|-------|-------|---------------------|
| `documentation-engineer` | ✅ | Doc maintenance |
| `refactoring-specialist` | ✅ | Code cleanup |
| `cli-developer` | ✅ | benchsight.sh |
| `git-workflow-manager` | ✅ | Branch strategy |
| `dx-optimizer` | ✅ | Dev experience |
| PowerShell agents | ❌ | Not using |

### 10-research-analysis/
| Agent | Keep? | BenchSight Use Case |
|-------|-------|---------------------|
| `competitive-analyst` | ✅ | Hockey platform research |
| `market-researcher` | ✅ | Commercial planning |
| `research-analyst` | ✅ | Feature research |

---

## Agents to Remove (Not Relevant)

### Safe to Delete:
1. **PowerShell agents** (7 agents) - Not using Windows/PowerShell
2. **Azure agents** - Using Vercel/Supabase
3. **Kubernetes agents** - Not using K8s
4. **Windows infrastructure** - macOS/Linux only
5. **Slack expert** - Not integrating Slack
6. **Blockchain developer** - Not using blockchain
7. **IoT engineer** - Not IoT
8. **Embedded systems** - Not embedded

### Consider Removing:
- `chaos-engineer` - Overkill for current stage
- `penetration-tester` - Not at security audit phase
- `ad-security-reviewer` - Not using Active Directory
- Most meta-orchestration agents (09) - Complex, rarely needed

---

## Agents to Add (BenchSight-Specific)

### 1. `etl-specialist` (CREATE)
```yaml
---
name: etl-specialist
description: Use for ETL pipeline work - debugging, optimization, new table creation
---

Expert in BenchSight ETL pipeline. Knows:
- 11-phase execution flow
- Goal counting rule (event_type='Goal' AND event_detail='Goal_Scored')
- Stat attribution (player_role='event_player_1')
- Vectorization requirements (never use .iterrows())
- etl_phases/ module structure
- Table dependencies and foreign keys
```

### 2. `supabase-specialist` (CREATE)
```yaml
---
name: supabase-specialist
description: Use for Supabase database work - queries, RLS, migrations, views
---

Expert in BenchSight Supabase setup. Knows:
- Dev vs Production environments
- RLS policies for multi-tenancy
- View optimization for dashboard
- Migration workflows
- Environment variable management
```

### 3. `dashboard-developer` (CREATE)
```yaml
---
name: dashboard-developer
description: Use for Next.js dashboard development - pages, components, data fetching
---

Expert in BenchSight dashboard. Knows:
- Next.js 14 App Router patterns
- Supabase client configuration
- shadcn/ui component library
- Recharts visualization patterns
- Server/Client component decisions
```

### 4. `tracker-specialist` (CREATE)
```yaml
---
name: tracker-specialist
description: Use for tracker app work - features, bugs, future conversion planning
---

Expert in BenchSight tracker (v28.0). Knows:
- 722 functions, 35,008 lines
- State management (S object)
- Video integration patterns
- Export formats for ETL compatibility
- Future Rust/Next.js conversion plan
```

---

## Agent Customization Recommendations

### Update `hockey-analytics-sme`:
Add BenchSight table references:
```
- fact_player_game_stats (317 columns)
- fact_goalie_game_stats (128 columns)
- dim_player, dim_team, dim_game
- v_standings, v_player_season_stats (views)
```

### Update `github-integration-expert`:
Add BenchSight-specific:
```
- Branch strategy: feature/* → develop → main
- CodeRabbit configuration for goal counting rules
- Vercel environment variables (dev/prod Supabase)
- ETL validation in CI
```

### Update `ui-comprehensive-tester`:
Add dashboard specifics:
```
- Test at localhost:3000
- Key pages: /standings, /leaders, /players/[id], /games/[id]
- Filter testing: season, game type
- Data validation against Supabase
```

---

## Agent Workflow Chains

### After Writing Code:
```
1. @claude-md-compliance-checker (rules check)
2. @code-quality-pragmatist (complexity check)
3. @task-completion-validator (actually works?)
```

### Before Marking Issue Done:
```
1. @task-completion-validator (verify complete)
2. @Jenny (matches requirements?)
3. @karen (realistic assessment)
```

### For ETL Changes:
```
1. @hockey-analytics-sme (methodology correct?)
2. @etl-specialist (implementation correct?)
3. @claude-md-compliance-checker (follows rules?)
```

### For Dashboard Features:
```
1. @dashboard-developer (implement)
2. @ui-comprehensive-tester (test)
3. @code-quality-pragmatist (not over-engineered?)
```

---

## How to Edit Agents

### Agent File Location

Project-specific agents: `.claude/agents/`
Generic category agents: `.claude/categories/[category]/`

### Agent File Structure

```yaml
---
name: agent-name
description: When this agent should be invoked (triggers auto-selection)
tools: Read, Write, Edit, Bash, Glob, Grep
---

You are a [role description]...

## Key Responsibilities
- Responsibility 1
- Responsibility 2

## Project Context
[BenchSight-specific knowledge]

## Checklist
- [ ] Step 1
- [ ] Step 2

## Output Format
[What the agent should produce]
```

### Editing an Agent

1. **Read the agent file** to understand current behavior
2. **Identify what to change:**
   - Description (when it triggers)
   - Tools (what it can use)
   - Instructions (what it does)
   - Context (what it knows)
3. **Edit the markdown file**
4. **Test by invoking** the agent

### Example: Adding BenchSight Context

Before:
```markdown
You are a data engineer expert...
```

After:
```markdown
You are a data engineer expert specializing in the BenchSight hockey analytics pipeline.

## BenchSight Context

- ETL produces 139 tables from game tracking data
- Goal counting rule: event_type='Goal' AND event_detail='Goal_Scored'
- Never use .iterrows() - use vectorized operations
- Tables: dim_* (dimensions), fact_* (facts), qa_* (QA)
```

---

## How to Create New Agents

### Step 1: Choose Location

- Project-specific: `.claude/agents/my-agent.md`
- Category-based: `.claude/categories/[category]/my-agent.md`

### Step 2: Use Template

```markdown
---
name: my-agent-name
description: Use this agent when [specific situation]. Examples: [trigger phrases]
tools: Read, Write, Edit, Bash, Glob, Grep
---

You are an expert [role] specializing in [domain].

## Context

[What this agent needs to know about the project]

## Key Responsibilities

1. [Primary responsibility]
2. [Secondary responsibility]
3. [Tertiary responsibility]

## Checklist

When invoked, follow this checklist:

- [ ] Step 1: Understand the request
- [ ] Step 2: Gather context
- [ ] Step 3: Perform analysis
- [ ] Step 4: Take action
- [ ] Step 5: Report results

## BenchSight Integration

[Project-specific knowledge]

## Output Format

[What to produce and how to format it]
```

### Step 3: Test

Invoke the agent and verify it behaves correctly.

---

## Tool Assignment Guide

| Agent Role | Recommended Tools |
|------------|-------------------|
| Read-only reviewers | Read, Grep, Glob |
| Research/analysis | Read, Grep, Glob, WebFetch, WebSearch |
| Code writers | Read, Write, Edit, Bash, Glob, Grep |
| Documentation | Read, Write, Edit, Glob, Grep, WebFetch, WebSearch |
| Full access | All tools |

---

## Proposed New Agents for Full Lifecycle

### Phase 2: ETL Optimization

| Agent | Purpose |
|-------|---------|
| `etl-debugger` | Debug ETL pipeline issues |
| `table-validator` | Validate table integrity |
| `performance-profiler` | Profile ETL performance |

### Phase 3-4: Dashboard & Portal

| Agent | Purpose |
|-------|---------|
| `component-reviewer` | Review React components |
| `api-tester` | Test API endpoints |
| `ux-auditor` | Audit user experience |

### Phase 5: Tracker Conversion

| Agent | Purpose |
|-------|---------|
| `rust-migration-advisor` | Plan Rust migration |
| `js-to-rust-converter` | Convert JS patterns to Rust |

### Phase 6: ML/CV

| Agent | Purpose |
|-------|---------|
| `model-evaluator` | Evaluate ML model performance |
| `cv-pipeline-expert` | Computer vision pipeline |

### Phase 7-8: Commercial

| Agent | Purpose |
|-------|---------|
| `tenant-onboarding` | Multi-tenant setup |
| `billing-validator` | Validate billing integration |
| `security-reviewer` | Security audit |

### Phase 9-12: AI Coaching

| Agent | Purpose |
|-------|---------|
| `ai-coach-tester` | Test AI coach responses |
| `nl-query-validator` | Validate NL query accuracy |

---

## Summary

**Essential (11 agents):**
- hockey-analytics-sme, Jenny, karen, task-completion-validator
- claude-md-compliance-checker, code-quality-pragmatist
- github-integration-expert, ui-comprehensive-tester
- **code-explainer**, **table-explainer**, **data-dictionary-specialist** (NEW)

**Add (4 new agents):**
- etl-specialist, supabase-specialist, dashboard-developer, tracker-specialist

**Remove (~20 agents):**
- All PowerShell, Azure, Windows, Kubernetes, blockchain, IoT agents

**Keep from categories (~30 agents):**
- Python, TypeScript, React, Next.js, SQL specialists
- Data engineering, ML, analytics agents
- DevOps, deployment, database admins
- Code review, debugging, testing agents

---

## Related Documentation

- [HOOKS_GUIDE.md](../docs/HOOKS_GUIDE.md) - Hooks guide
- [SKILLS_GUIDE.md](../docs/SKILLS_GUIDE.md) - Skills guide
- [CLAUDE_CODE_BEST_PRACTICES.md](../docs/CLAUDE_CODE_BEST_PRACTICES.md) - Overall best practices

---

*Last Updated: 2026-01-22*
