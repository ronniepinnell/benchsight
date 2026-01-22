# Draft GitHub Issues (Backlog)

**Purpose:** Ready-to-post issues for professionalizing BenchSight.

---

## Foundation and Workflow

1) **Define issue and PR templates**
- Labels: `type:docs`, `priority:p1`
- Scope: Standardize issue fields, PR checklist, and release notes.

2) **Codify project workflow (Cursor + Claude + CodeRabbit)**
- Labels: `type:docs`, `area:workflow`, `priority:p1`
- Scope: Expand workflow doc with agent usage, subagent reviews, and skills guidance.

3) **Establish docs update policy**
- Labels: `type:docs`, `priority:p1`
- Scope: Add rules for when to update `PROJECT_STATUS`, `MASTER_INDEX`, and component docs.

---

## Automation and Quality Gates

4) **Docs link check automation**
- Labels: `type:chore`, `area:docs`, `priority:p1`
- Scope: Run `scripts/docs-check.sh` in CI and pre-commit.

5) **Pre-commit hooks baseline**
- Labels: `type:chore`, `priority:p1`
- Scope: Add formatting/lint hooks per package (ETL, API, dashboard).

6) **CodeRabbit configuration tuning**
- Labels: `type:chore`, `area:review`, `priority:p2`
- Scope: Calibrate `.coderabbit.yaml` for BenchSight patterns and rules.

---

## Infra and Environments

7) **Supabase dev/prod environment separation**
- Labels: `type:infra`, `area:supabase`, `priority:p1`
- Scope: Confirm dev/prod projects, RLS policy plan, schema migration flow.

8) **Vercel dev/prod projects and envs**
- Labels: `type:infra`, `area:vercel`, `priority:p1`
- Scope: Lock environment variables, preview strategy, and release guardrails.

---

## Product Readiness

9) **Portal API integration (ETL control)**
- Labels: `type:feature`, `area:portal`, `priority:p1`
- Scope: Replace placeholders with real endpoints and status polling.

10) **Game management endpoints**
- Labels: `type:feature`, `area:api`, `priority:p1`
- Scope: CRUD endpoints for games + portal UI wiring.

11) **Multi-tenant architecture plan**
- Labels: `type:design`, `priority:p0`
- Scope: Data isolation, RLS, tenant IDs, migration plan.

---

## Commercialization

12) **Pilot case study buildout**
- Labels: `type:docs`, `area:commercial`, `priority:p1`
- Scope: Populate `docs/commercial/PILOT_CASE_STUDY_TEMPLATE.md`.

13) **Pricing validation plan**
- Labels: `type:research`, `area:commercial`, `priority:p2`
- Scope: Define pilot pricing experiments and success metrics.

