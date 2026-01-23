# CLAUDE.md - BenchSight Project Instructions

> **Note:** This is the main project instructions file for Claude Code.
> The file at `.claude/CLAUDE.md` is a separate file for subagent collection documentation (different purpose).

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BenchSight is a hockey analytics platform for currentlt for the NORAD Recreational League. It processes game tracking data through an ETL pipeline and presents it via a Next.js dashboard. After prototyping for NORAD, it aims to broaden its scope to be a fully functioning analystics hub for high level youth, junior, and college hockey. 

**Components:**
- **ETL Pipeline** (`src/`, `run_etl.py`): Python pipeline generating 145 tables from Excel game data
- **Validation** (`src/validation/`): Comprehensive table verification framework
- **Dashboard** (`ui/dashboard/`): Next.js 14 analytics dashboard with 50+ pages
- **API** (`api/`): FastAPI backend for ETL operations and data uploads
- **Tracker** (`ui/tracker/`): HTML/JS game tracking application
- **Portal** (`ui/portal/`): Admin interface (UI mockup only)

## Common Commands

```bash
# Unified CLI (preferred)
./benchsight.sh etl run                    # Run ETL pipeline (~80 seconds for 4 games)
./benchsight.sh etl run --wipe             # Clean slate + run ETL
./benchsight.sh etl validate               # Validate ETL output
./benchsight.sh dashboard dev              # Start dashboard dev server (port 3000)
./benchsight.sh api dev                    # Start API dev server (port 8000)
./benchsight.sh db upload                  # Upload CSVs to Supabase
./benchsight.sh status                     # Show project status

# Dashboard (from ui/dashboard/)
npm run dev                                # Dev server
npm run build                              # Production build
npm run lint                               # ESLint
npm run type-check                         # TypeScript checking

# Testing
pytest                                     # Run all Python tests
pytest tests/test_goal_verification.py    # Run specific test
pytest -m "not slow"                       # Skip slow tests
```

## Critical Rules

### Goal Counting (CRITICAL)
Goals are ONLY counted when both conditions are true:
```python
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
```
**Never** count `event_type == 'Shot'` with `event_detail == 'Goal'` - that's a shot attempt.

### Vectorized Operations
Use pandas vectorized operations. **Never use `.iterrows()`** - use `.groupby()` and `.apply()` instead.

### Stat Counting
Events are logged where each player involved in the play has a row for the event, this can lead to duplicate counting for stats such as shots, passes, etc. The stat is only to be counted for the row for in which the player_role column = 'event_player_1'. For example, a zone entry event might have 2 event players and 3 opp players. The zone entry it to only be counted for event_player_1.

### Micro-Stat Counting
Micro-stats are in the play_detail1 and play_detailts_2 columns in the event_players (or raw event tracking files). For any event that also has a linked event (linked_event_key in event_players <> '') the player (player_id) might be listed for each event. Only count the micro-stat once in that linked_event. For example, a pass > zone exit > turnover linked_event might have event_player_2 'receivermissed' in play_detail1 or play_detail_2. Event_player_2 (also confirm it is the same player_id) could have 'receivermissed' present in all 3 events. 'receivermissed' would only be counted once.

### Faceoffs
Event_player_1 (player_role) is faceoff winner, opp_player_1 is faceoff loser.

### Assists
An assist is noted in 'play_details1' or 'play_details_2' columns in event_players. An assist is credited if a player has '%assist%' in one of those two columns. A primary assits are labeled 'AssistPrimary', secondary assists are labeled 'AssistSecondary'. In the event there is an 'AssistTertiary', that assist is not counted to an assist, it is merly noting that there was another pass. In hockey, only the primart and secondary assists count. 

### Single Source of Truth
One canonical implementation per calculation. Reference `src/calculations/` for stats logic and `config/formulas.json` for formula definitions.

### Key Formatting
All keys should be formated in a {XX}{ID}{5D} manner. In some instances such as player game keys, that key could be {XX}{gameid}{playerid}. In instances where there are multiple players (such as line combos, h2h, etc) it is acceptable to have {XX}_{player1_id}_{player2_id}.... In most cases, it is not acceptable to use _ in keys. 

### Key Addition
Foreign keys should be added to any table in which there is a column representing a cooresponding dim table.

### Code Modularization Best Practices

When extracting functions to separate modules:

1. **No wrapper functions** - Call module functions directly with explicit arguments instead of creating thin wrappers that pass globals:
   ```python
   # GOOD: Direct call with explicit args
   build_reference_tables(OUTPUT_DIR, log, save_output_table)

   # BAD: Wrapper that just passes globals
   def create_reference_tables():
       return _create_reference_tables(OUTPUT_DIR, log, save_output_table)
   ```

2. **Use Edit tool for reviewable changes** - Make small, incremental edits that are easy to review in git diff. Avoid bulk operations via scripts.

3. **Verify before cleanup** - When refactoring:
   - First: Add imports and update call sites
   - Second: Run tests/ETL to verify functionality
   - Third: Remove dead code (create GitHub issue if large)

4. **Explicit dependencies** - Module functions should accept their dependencies as parameters, not rely on globals:
   ```python
   # GOOD: Explicit parameters
   def enhance_events(output_dir: Path, log, save_func):

   # BAD: Relies on globals
   def enhance_events():
       # uses OUTPUT_DIR, log from outer scope
   ```

5. **Track dead code** - When modularization creates dead code too large to remove immediately, create a GitHub issue to track cleanup.


## Architecture

### ETL Pipeline
- **Entry point:** `run_etl.py`
- **Core engine:** `src/core/base_etl.py` (~1,065 lines) + `src/core/etl_phases/` modules
- **Phase-based processing:** Loading → Event/Shift Building → Calculations → Advanced Analytics → Table Generation → QA
- **Output:** 139 tables (50 dimensions, 81 facts, 8 QA) as CSVs in `data/output/`

### Dashboard
- **Framework:** Next.js 14 (App Router) with TypeScript strict mode
- **Database:** Supabase (PostgreSQL) via `@supabase/supabase-js`
- **Components:** Server Components by default, Client Components only for interactivity
- **UI:** shadcn/ui + Tailwind CSS + Recharts

### Database
- **Naming:** `dim_*` (dimensions), `fact_*` (facts), `qa_*` (QA tables), `v_*` (views)
- **Pre-aggregated views** in Supabase for complex dashboard queries

## Environment Variables

### Dashboard (`ui/dashboard/.env.local`)

**Development:**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://amuisqvhhiigxetsfame.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFtdWlzcXZoaGlpZ3hldHNmYW1lIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg5MjQ3MjQsImV4cCI6MjA4NDUwMDcyNH0.L_WHElYv1Ffq_aMR8UqOZrP2n8h8Qol_dd_wGXNnh4I
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Production:**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://uuaowslhpgyiudmbvqze.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1YW93c2xocGd5aXVkbWJ2cXplIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NTQ5ODcsImV4cCI6MjA4MjQzMDk4N30.9WjZcLzB555vKaiDeby8nYJ3Ce9L-SCkFrYH1Ts4ILU
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

### ETL/API (`config/config_local.ini`)

**Development:**
```ini
[supabase]
url = https://amuisqvhhiigxetsfame.supabase.co
anon_key = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFtdWlzcXZoaGlpZ3hldHNmYW1lIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg5MjQ3MjQsImV4cCI6MjA4NDUwMDcyNH0.L_WHElYv1Ffq_aMR8UqOZrP2n8h8Qol_dd_wGXNnh4I
service_key = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFtdWlzcXZoaGlpZ3hldHNmYW1lIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODkyNDcyNCwiZXhwIjoyMDg0NTAwNzI0fQ.NuTEo9_lmo8GBk7m42qqBcJvik8kMs7w3F35HZ_D4Ro
```

**Production:**
```ini
[supabase]
url = https://uuaowslhpgyiudmbvqze.supabase.co
anon_key = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1YW93c2xocGd5aXVkbWJ2cXplIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NTQ5ODcsImV4cCI6MjA4MjQzMDk4N30.9WjZcLzB555vKaiDeby8nYJ3Ce9L-SCkFrYH1Ts4ILU
service_key = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1YW93c2xocGd5aXVkbWJ2cXplIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2Njg1NDk4NywiZXhwIjoyMDgyNDMwOTg3fQ.BV5d03x9Hv83XZsveGdU7k7D7gAZ7Yi1tqNB7DeDkrM
```

### API (`api/.env`)
```bash
ENVIRONMENT=development  # or production
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
SUPABASE_URL=https://amuisqvhhiigxetsfame.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFtdWlzcXZoaGlpZ3hldHNmYW1lIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODkyNDcyNCwiZXhwIjoyMDg0NTAwNzI0fQ.NuTEo9_lmo8GBk7m42qqBcJvik8kMs7w3F35HZ_D4Ro
```

### Vercel Environment Variables

Set in Vercel Dashboard → Project Settings → Environment Variables:

| Variable | Dev | Production |
|----------|-----|------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Dev Supabase URL | Prod Supabase URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Dev anon key | Prod anon key |
| `NEXT_PUBLIC_API_URL` | Dev API URL | Prod API URL |

### Switching Environments
```bash
./benchsight.sh env switch dev        # Switch to dev
./benchsight.sh env switch production # Switch to production (careful!)
./benchsight.sh env status            # Show current environment
```

## Code Standards

**Python:** PEP 8, type hints required, Google-style docstrings, max 100 char lines

**TypeScript:** Strict mode, interfaces for all data structures, camelCase functions, PascalCase components

## Key Entry Points

- ETL: `run_etl.py` → `src/core/base_etl.py`
- Dashboard: `ui/dashboard/src/app/layout.tsx`
- API: `api/main.py`
- Calculations: `src/calculations/` (goals, corsi, ratings, time)
- Table definitions: `src/tables/`

## Documentation

- `docs/MASTER_INDEX.md` - Documentation hub
- `docs/PROJECT_STATUS.md` - Current progress (~70% complete)
- `docs/MASTER_RULES.md` - Complete standards reference
- `.agents/core.md` - Core rules (always relevant)
- `.agents/reference/` - Component-specific rules (load as needed)

## Git Workflow

- **Branches:** `main` (production), `develop` (staging/integration), `feature/*`, `fix/*`
- **Default merge target:** `develop` (NOT `main`)
- **Flow:** `feature/*` or `fix/*` → `develop` → `main` (production releases only)
- **Commit format:** `[TYPE] Brief description` (FEAT, FIX, DOCS, REFACTOR, TEST, CHORE)
- **PRD-first:** Create PRD in `docs/prds/` before implementing features
- **Never push directly to `main`** - all changes go through `develop` first
- **Never use "Closes #XX" in PR descriptions** - issues are closed manually after verification
- **Never include "Generated with Claude Code" in PRs** - omit this footer entirely



**Core:**
- Cursor (primary IDE)
- Claude via Cursor (planning + deep review)
- Git + GitHub

**Optional:**
- GitHub CLI (`gh`)
- CodeRabbit (PR review)
- MCPs (browser/IDE for UI testing)

---

## Repository Entry Points

- `docs/MASTER_INDEX.md` — documentation index
- `docs/PROJECT_SPEC.md` — product + tech spec
- `docs/WORKFLOWS/WORKFLOW.md` — operational workflow
- `docs/MASTER_RULES.md` — standards and rules

---

## Subagent Registry (Recommended)

Use subagents as targeted reviewers to reduce mistakes.

1. **Data QA Agent** — ETL integrity, double-counting checks
2. **Performance Agent** — ETL runtime, dashboard load
3. **Security Agent** — auth, RLS, secrets, access control
4. **Frontend UX Agent** — dashboard UX, design consistency
5. **Infra Agent** — Supabase/Vercel envs, release guardrails

---

## Skills Usage

- Use a skill only when it directly applies
- Read the skill’s `SKILL.md` before use
- Keep context small; load only referenced files

---

## Automation and Hooks

**Local:**
- Docs check: `./scripts/docs-check.sh`
- Lint/format on staged files

**CI:**
- Docs check on `docs/**` changes
- Package tests for ETL/API/dashboard

---

## GitHub CLI (Optional)

If installed:
- `gh auth login`
- `gh issue create`
- `gh pr create`

**Install (macOS):**
```bash
brew install gh
gh auth login
```

**Install (Ubuntu):**
```bash
sudo apt update && sudo apt install gh
gh auth login
```

---

## MCP Setup (Optional)

Use MCPs for:
- UI smoke tests
- Visual regression checks

**Cursor MCP config:**
- Update `~/.cursor/mcp.json` with enabled MCPs
- Restart Cursor after changes

**Recommended MCPs:**
- Browser MCP for UI validation
- Filesystem MCP for structured context (if available)

---

## Claude/Cursor CLI Usage

**Cursor:**
- Use Cursor’s built-in agent for implementation
- Use Claude for planning + review passes

**Claude Code CLI (if installed):**
```bash
claude --version
claude chat --help
```

**Best Practices:**
- Start with PRD and scope
- Keep context small and focused
- Use subagents for review passes

---

## Claude/Cursor Workflow

**Research → Plan → Implement → Test → Document → Review**

1. **Research** — read existing docs
2. **Plan** — PRD in `docs/prds/`
3. **Implement** — code + tests
4. **Test** — run ETL validation or API tests
5. **Document** — update docs in the same PR
6. **Review** — CodeRabbit + subagent review

---

## Commands (Reference)

- `./benchsight.sh etl run --games 18969`
- `./benchsight.sh etl validate`
- `./scripts/docs-check.sh`

---

## Model Roles (You Have Claude + ChatGPT + Gemini)

**Claude (Primary Planner/Reviewer):**
- Planning, architecture, long-form reasoning
- Docs/specs and risk analysis

**Cursor Agent (Primary Implementer):**
- Code edits, refactors, tests, file operations

**ChatGPT (Fast Second Opinion):**
- Alternative approaches, debugging heuristics
- Use after a primary draft exists

**Gemini (Multimodal Reviewer):**
- UI/UX screenshots, design feedback, summaries
- Use for UI review or cross-checks

---

## Model Selection Matrix

| Task Type | Primary | Secondary |
|----------|---------|-----------|
| Product planning, PRDs | Claude | ChatGPT |
| Architecture decisions | Claude | ChatGPT |
| Code implementation | Cursor Agent | Claude |
| Data integrity review | Claude | Cursor Agent |
| UI/UX review (screenshots) | Gemini | Claude |
| Quick debugging ideas | ChatGPT | Claude |
