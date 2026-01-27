# Scripts Walkthrough

**CLI wrappers and helper scripts**

Last Updated: 2026-01-21  
Version: 2.00

---

## Key Scripts
- `benchsight.sh` — unified CLI for ETL, dashboard, db uploads, env switching
- `dev.sh` — helper for development tasks
- `scripts/docs-check.sh` — documentation link checker (used in pre-commit/CI)

## Flow
- `benchsight.sh` routes subcommands to Python ETL, Node dashboard, or db upload tasks.
- `scripts/docs-check.sh` scans Markdown links to keep docs consistent.

## Extending Safely
- Add new subcommands to `benchsight.sh` instead of ad-hoc scripts.
- Keep helper scripts idempotent and non-destructive by default.

## Assessment
- **Good:** Unified CLI (`benchsight.sh`) reduces command sprawl; docs checker in place.
- **Risks/Bad:** More scripts could fragment if not routed through `benchsight.sh`; limited guardrails on destructive ops.
- **Next:** Route new helpers via CLI; add dry-run flags for risky actions; keep docs checker in pre-commit/CI.
