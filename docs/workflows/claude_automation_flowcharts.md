# Claude Automations (Hooks, Skills, Agents)

What runs automatically vs. what you must call manually when using Claude with this repo. All charts are ASCII for easy reading in the terminal.

## How the wiring works
- **Hooks (auto):** Defined in `.claude/settings.json`. PreToolUse (before a Claude Bash/Edit/Write call) and PostToolUse (after). Implemented as Python scripts in `.claude/hooks/`.
- **Rules (always loaded):** `.cursorrules` points to `.agents/core.md` and on-demand `.agents/reference/*.md`.
- **Skills (manual):** Slash-style commands (e.g., `/etl`, `/validate`) defined in `.claude/skills/*/SKILL.md`. They do nothing unless you invoke them.
- **Agents (manual prompts):** Prompt libraries in `.claude/agents/` (Volt subagents + local SMEs). Not auto-triggered; you explicitly ask Claude to “use” one.

## Hook flow charts (automatic)

### PreToolUse: Bash – `bash-validator.py`
```
Bash command
  └─> bash-validator.py
       ├─ Block if dangerous pattern (rm -rf data/output, drop tables, force push main, etc.)
       ├─ Ask if risky pattern (production, supabase migration push, vercel --prod)
       └─ Pass through otherwise
```

### PreToolUse: Bash – `doc-update-reminder.py`
```
git commit command
  └─> doc-update-reminder.py
       ├─ List staged files
       ├─ If code paths staged AND no docs staged -> ask to update docs (with targeted suggestions)
       └─ Otherwise no prompt
```

### PreToolUse: Edit/Write – `goal-counting-guard.py`
```
Edit/Write file
  └─> goal-counting-guard.py
       ├─ If path matches goal-related patterns (goals.py, fact_goals, etc.)
       │     └─ Emit critical goal-counting reminder
       └─ Otherwise no message
```

### PostToolUse: Bash – `post-etl-reminder.py`
```
Bash command completes
  └─> post-etl-reminder.py
       ├─ If command contains "etl run" AND no errors detected
       │     └─ Print reminder to run /validate
       └─ Otherwise silent
```

### PostToolUse: Bash – `etl-failure-handler.py`
```
ETL-related Bash command completes
  └─> etl-failure-handler.py
       ├─ Detect failure via exit code or error patterns
       ├─ Log context to ~/.claude/etl-failures/etl_failure_<timestamp>.json
       ├─ Build GitHub issue title/body (recent commits, changed files, traceback)
       └─ Ask whether to create the issue via gh (if configured)
```

### Post-ETL (manual/optional) – `etl-integrity-check.py`  *(not wired by default)*
```
Run manually after successful ETL (e.g., python .claude/hooks/etl-integrity-check.py via script)
  └─> Checks:
       - Table existence counts (dim/fact/qa), missing critical tables
       - Empty critical tables
       - High null percentages (>20%, excluding known high-null cols)
       - Key format validations (e.g., PL00000)
       - Statistical sanity (goal/shot/TOI ranges, goalie SV%)
  └─> Writes log to ~/.claude/etl-integrity/..., prints summary; asks for review when issues found
```

## Skills (manual triggers)
- Invoke via slash commands in Claude. No auto-run.
- Summary of available skills (`.claude/skills/*/SKILL.md`):
  - `api-dev` – Start FastAPI backend dev server / backend debugging
  - `competitive-research` – Research competitor platforms/features/UI
  - `compliance-check` – Verify changes align with CLAUDE.md and standards
  - `cv-tracking` – Computer-vision tracking pipeline work
  - `dashboard-deploy` – Deploy dashboard to Vercel
  - `dashboard-dev` – Dashboard dev server / UI debugging
  - `db-dev` – Work with dev Supabase DB (migrations/queries)
  - `db-prod` – Work with prod Supabase DB (with confirmations)
  - `doc-sync` – Detect and sync documentation updates
  - `env-switch` – Switch between dev/prod environments
  - `etl` – Run BenchSight ETL pipeline (all/specific games, wipe)
  - `etl-issue` – Create GH issue for ETL failures with context
  - `go-to-market` – GTM strategy planning
  - `hockey-stats` – Consult hockey analytics SME
  - `ml-pipeline` – ML pipeline work (xG, win prob, clustering)
  - `monetization` – Monetization strategy and pricing
  - `portal-dev` – Admin portal development/debugging
  - `post-code` – Master post-code validation/documentation workflow
  - `pr-workflow` – Pull request creation workflow
  - `reality-check` – “Karen” agent to validate claimed progress
  - `scale-architecture` – Scale/infra architecture planning
  - `schema-design` – Database schema design and documentation
  - `tracker-dev` – Game tracker development/debugging
  - `ui-ux-design` – UI/UX design guidance for dashboard/portal/tracker
  - `validate` – Run ETL validation and data-quality checks
  - `xg-model` – Expected Goals model development/evaluation

## Agents (manual prompts)
- Location: `.claude/agents/` (Volt subagents categories 01–10 plus local SME files like `hockey-analytics-sme.md`, `task-completion-validator.md`, `ui-comprehensive-tester.md`, etc.).
- Trigger: Only when you explicitly ask Claude to “use” or “call” an agent; no automatic activation.
- Purpose: Specialized prompt packs (language specialists, QA/security, infra, data/ML, product/business, orchestration). Use as reference prompts or paste-in helpers; Cursor does not auto-load them.
