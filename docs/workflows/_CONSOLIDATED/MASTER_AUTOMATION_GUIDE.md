# BenchSight Master Automation Guide

**The complete reference for all agents, skills, hooks, MCPs, and workflows.**

---

## Quick Navigation

| Guide | Purpose | Link |
|-------|---------|------|
| **This Document** | Master reference | You're here |
| Agent Best Practices | When to use which agent | [AGENT_BEST_PRACTICES.md](./AGENT_BEST_PRACTICES.md) |
| Hooks & Skills Guide | How hooks and skills work | [HOOKS_SKILLS_COMMANDS_GUIDE.md](./HOOKS_SKILLS_COMMANDS_GUIDE.md) |
| MCPs & Plugins | MCP installation and usage | [RECOMMENDED_PLUGINS_AND_MCPS.md](./RECOMMENDED_PLUGINS_AND_MCPS.md) |
| Installation Guide | Complete setup instructions | [COMPLETE_INSTALLATION_GUIDE.md](./COMPLETE_INSTALLATION_GUIDE.md) |

---

## All Available Skills (25)

### Component Development

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/dashboard-dev` | Start dashboard dev server | Working on UI features |
| `/dashboard-deploy` | Deploy to Vercel | After validation passes |
| `/portal-dev` | Start portal development | Working on admin interface |
| `/tracker-dev` | Start tracker development | Working on game tracking |
| `/api-dev` | Start API server | Working on backend |
| `/etl` | Run ETL pipeline | Processing game data |
| `/validate` | Validate ETL output | After ETL runs |
| `/etl-issue` | Create GitHub issue for ETL failure | After ETL failures |

### Database & Environment

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/db-dev` | Work with dev database | Schema changes, testing |
| `/db-prod` | Work with prod database | Production deployments |
| `/env-switch` | Switch dev/prod | Changing targets |
| `/schema-design` | Design database schemas | Adding tables/columns |

### Quality & Validation

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/post-code` | Run full validation workflow | **After ANY code changes** |
| `/compliance-check` | Check CLAUDE.md rules | Before marking complete |
| `/reality-check` | Call Karen agent | Verify actual vs claimed |
| `/doc-sync` | Update documentation | After code changes |
| `/pr-workflow` | Create validated PR | Ready for review |

### Analytics & Domain

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/hockey-stats` | Hockey analytics SME | Stat methodology questions |
| `/xg-model` | Expected goals model | xG development |
| `/ml-pipeline` | Machine learning work | ML feature development |
| `/cv-tracking` | Computer vision | Video tracking features |

### Business & Strategy

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/competitive-research` | Research competitors | Feature planning |
| `/ui-ux-design` | Design assistance | UI planning |
| `/monetization` | Revenue planning | Business model |
| `/go-to-market` | Launch strategy | Commercial launch |
| `/scale-architecture` | Scaling plans | Growth architecture |

---

## All Available Agents (By Category)

### Project-Specific Agents (8)

| Agent | Color | Purpose | Trigger |
|-------|-------|---------|---------|
| `hockey-analytics-sme` | Red | Hockey domain expert | Stat calculations, methodology |
| `github-integration-expert` | Cyan | GitHub/CI/CD workflows | Pipeline setup, PR automation |
| `Jenny` | Orange | Spec verification | Implementation vs requirements |
| `karen` | Yellow | Reality assessment | Cut through incomplete claims |
| `task-completion-validator` | Blue | Completion validation | "I finished X" claims |
| `claude-md-compliance-checker` | Green | Rule compliance | After code changes |
| `code-quality-pragmatist` | Orange | Over-engineering check | After implementation |
| `ui-comprehensive-tester` | Blue | UI testing | After UI changes |

### Built-in Development Agents

| Agent | Purpose |
|-------|---------|
| `Explore` | Codebase exploration and search |
| `Plan` | Implementation planning |
| `frontend-developer` | Frontend development |
| `backend-developer` | Backend development |
| `fullstack-developer` | Full-stack development |
| `nextjs-developer` | Next.js specific |
| `react-specialist` | React development |
| `typescript-pro` | TypeScript expertise |
| `python-pro` | Python expertise |
| `rust-engineer` | Rust development |

### Quality & Testing Agents

| Agent | Purpose |
|-------|---------|
| `code-reviewer` | Code review |
| `debugger` | Debugging issues |
| `test-automator` | Test automation |
| `qa-expert` | Quality assurance |
| `security-auditor` | Security review |
| `performance-engineer` | Performance optimization |

### Data & ML Agents

| Agent | Purpose |
|-------|---------|
| `data-engineer` | Data pipeline development |
| `ml-engineer` | Machine learning |
| `data-scientist` | Data analysis |
| `database-optimizer` | Query optimization |
| `postgres-pro` | PostgreSQL expertise |
| `sql-pro` | SQL development |

### Infrastructure Agents

| Agent | Purpose |
|-------|---------|
| `devops-engineer` | DevOps practices |
| `cloud-architect` | Cloud architecture |
| `kubernetes-specialist` | Kubernetes |
| `terraform-engineer` | Infrastructure as code |
| `sre-engineer` | Site reliability |

### Business Agents

| Agent | Purpose |
|-------|---------|
| `product-manager` | Product planning |
| `business-analyst` | Business analysis |
| `ui-designer` | UI/UX design |
| `technical-writer` | Documentation |

---

## Active Hooks (4)

| Hook | Trigger | Purpose |
|------|---------|---------|
| `bash-validator.py` | PreToolUse: Bash | Blocks dangerous commands |
| `goal-counting-guard.py` | PreToolUse: Edit/Write | Goal counting rule reminder |
| `post-etl-reminder.py` | PostToolUse: Bash | Validation reminder after ETL |
| `etl-failure-handler.py` | PostToolUse: Bash | Detects ETL failures, offers to create GitHub issues |

---

## Installed MCPs

### Essential (Install First)

| MCP | Command | Purpose |
|-----|---------|---------|
| Supabase | `claude mcp add supabase` | Database operations |
| GitHub | `claude mcp add github` | Version control |
| Filesystem | `claude mcp add filesystem` | File operations |
| Playwright | `claude mcp add playwright` | Browser testing |

### Recommended

| MCP | Command | Purpose |
|-----|---------|---------|
| Vercel | `claude mcp add vercel` | Deployments |
| PostgreSQL | `claude mcp add postgres` | DB analysis |
| Memory | `claude mcp add memory` | Session persistence |
| Next.js | `claude mcp add nextjs` | Dashboard dev tools |

### Advanced

| MCP | Purpose | Use Case |
|-----|---------|----------|
| ECharts | Chart generation | Dynamic visualizations |
| Pinecone | Vector search | Similar play retrieval |
| Neo4j | Graph database | Player relationships |
| Slack | Notifications | Team alerts |
| Linear | Issue tracking | Project management |

---

## Post-Code Workflow (CRITICAL)

**Run `/post-code` after ANY code changes.**

### Workflow Sequence

```
Code Written
    │
    ▼
┌─────────────────────────────────────┐
│ 1. BUILD CHECK                      │
│    Python: py_compile               │
│    TypeScript: type-check           │
│    Dashboard: npm run build         │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ 2. @task-completion-validator       │
│    Does it actually work?           │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ 3. @code-quality-pragmatist         │
│    Is it over-engineered?           │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ 4. @claude-md-compliance-checker    │
│    Follows CLAUDE.md rules?         │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ 5. @Jenny                           │
│    Matches spec?                    │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ 6. TESTS                            │
│    pytest / npm test / ETL validate │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ 7. /doc-sync                        │
│    Update documentation             │
└────────────────┬────────────────────┘
                 │
                 ▼
            ✅ READY FOR COMMIT
```

---

## Agent Selection Matrix

### By Task Type

| Task | Primary Agent | Secondary |
|------|---------------|-----------|
| Hockey stat question | `hockey-analytics-sme` | — |
| "I finished X" | `task-completion-validator` | `claude-md-compliance-checker` |
| Over-engineered? | `code-quality-pragmatist` | — |
| Matches spec? | `Jenny` | `task-completion-validator` |
| What's actually done? | `karen` | (runs full chain) |
| GitHub/CI/CD | `github-integration-expert` | — |
| UI testing | `ui-comprehensive-tester` | — |
| Debug issue | `debugger` | `hockey-analytics-sme` (if data) |
| Optimize queries | `database-optimizer` | `postgres-pro` |
| ML development | `ml-engineer` | `data-scientist` |
| Architecture review | `architect-reviewer` | `scale-architecture` skill |

### By Component

| Component | Primary Agent | Skill |
|-----------|---------------|-------|
| Dashboard | `nextjs-developer` | `/dashboard-dev` |
| Portal | `frontend-developer` | `/portal-dev` |
| Tracker | `fullstack-developer` | `/tracker-dev` |
| ETL | `python-pro` | `/etl`, `/validate` |
| API | `backend-developer` | `/api-dev` |
| Database | `postgres-pro` | `/db-dev` |
| ML/CV | `ml-engineer` | `/ml-pipeline`, `/cv-tracking` |

---

## Development Phases

### Phase 1: Current (NORAD Beta)

**Focus:** Complete core functionality

| Task | Skills/Agents |
|------|---------------|
| Dashboard improvements | `/dashboard-dev`, `nextjs-developer` |
| Portal API integration | `/portal-dev`, `/api-dev` |
| ETL refinements | `/etl`, `/validate`, `hockey-analytics-sme` |
| Data quality | `/compliance-check`, validation agents |

### Phase 2: Commercial Ready

**Focus:** Production hardening, features

| Task | Skills/Agents |
|------|---------------|
| Multi-tenancy | `/scale-architecture`, `architect-reviewer` |
| Authentication | `security-auditor`, `backend-developer` |
| API expansion | `/api-dev`, `api-designer` |
| Premium features | `/monetization`, `product-manager` |

### Phase 3: ML/CV Integration

**Focus:** Advanced analytics

| Task | Skills/Agents |
|------|---------------|
| xG model | `/xg-model`, `ml-engineer` |
| Win probability | `/ml-pipeline`, `data-scientist` |
| Video tracking | `/cv-tracking`, `ai-engineer` |
| Real-time predictions | `backend-developer`, `websocket-engineer` |

### Phase 4: Scale & Launch

**Focus:** Growth and monetization

| Task | Skills/Agents |
|------|---------------|
| Go-to-market | `/go-to-market`, `product-manager` |
| Infrastructure | `devops-engineer`, `cloud-architect` |
| Monitoring | `sre-engineer`, `performance-monitor` |
| Support systems | `customer-success-manager` |

---

## Daily Workflow Cheat Sheet

```bash
# Morning: Check status
./benchsight.sh status
./benchsight.sh env status

# Development: Start servers
/dashboard-dev              # or /api-dev, /portal-dev

# After writing code: ALWAYS run
/post-code

# ETL changes: Rebuild and validate
/etl --wipe && /validate

# Questions about hockey stats
/hockey-stats "How should we calculate Corsi?"

# Verify something is actually complete
/reality-check "Is the player page done?"

# Before creating PR
/pr-workflow "Feature: Player comparison page"

# Update docs after changes
/doc-sync

# Research competitors
/competitive-research "ESPN player pages"
```

---

## Critical Rules (Always Enforced)

### Goal Counting
```python
# ONLY this combination counts as a goal:
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
```

### Stat Attribution
```python
# Count stats ONLY for event_player_1
df[df['player_role'] == 'event_player_1']
```

### Vectorized Operations
```python
# NEVER use .iterrows()
# ALWAYS use vectorized operations
```

### Micro-Stats
```python
# Count ONCE per linked_event_key, not per event
```

---

## File Locations

```
.claude/
├── settings.json           # Hooks configuration
├── settings.local.json     # Local permissions
├── agents/                 # Agent definitions
│   ├── hockey-analytics-sme.md
│   ├── github-integration-expert.md
│   ├── jenny.md
│   ├── karen.md
│   └── ...
├── skills/                 # Skill definitions
│   ├── etl/SKILL.md
│   ├── validate/SKILL.md
│   ├── dashboard-dev/SKILL.md
│   ├── post-code/SKILL.md
│   └── ... (25 total)
└── hooks/                  # Hook scripts
    ├── bash-validator.py
    ├── goal-counting-guard.py
    └── post-etl-reminder.py

docs/workflows/
├── MASTER_AUTOMATION_GUIDE.md      # This file
├── AGENT_BEST_PRACTICES.md         # Agent usage guide
├── HOOKS_SKILLS_COMMANDS_GUIDE.md  # Skills/hooks guide
├── RECOMMENDED_PLUGINS_AND_MCPS.md # MCPs and plugins
└── COMPLETE_INSTALLATION_GUIDE.md  # Setup instructions
```

---

## Getting Help

1. **Skill help:** Run `/help` or check skill YAML
2. **Agent help:** Check agent .md file description
3. **MCP help:** `claude mcp list` and `claude mcp test <name>`
4. **Project docs:** `docs/MASTER_INDEX.md`
5. **Claude Code:** `claude /help`
