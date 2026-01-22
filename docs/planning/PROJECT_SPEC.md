# BenchSight Project Spec

**Single source of truth for product requirements, UX workflows, tech design, and delivery**

Last Updated: 2026-01-21
Version: 2.00

---

## 1) Product Requirements

### Audience (Who)
- Primary: Junior hockey teams and leagues
- Secondary: College club hockey programs
- Prototype/Pilot: Personal rec league (validation cohort)

### Problems (Why)
- Manual tracking is slow and inconsistent
- Pro analytics tools are too expensive for junior/college
- Coaches need clear, actionable insights, not raw logs

### Solution (What It Does)
- Capture game events and shifts via tracker
- Transform raw logs into validated analytics via ETL
- Provide dashboards for players, teams, games, standings
- Offer admin portal to manage ETL runs and data uploads

### Success Criteria
- ETL completes within target time and passes validation
- Dashboard loads in < 2 seconds for core pages
- Pilot users can run end-to-end flow without support

---

## 2) UX Workflows (How Users Use It)

### Coach / Analyst Workflow
1. Record or enter game tracking (tracker)
2. Run ETL (portal or CLI)
3. Review dashboards for player/team insights
4. Export or share insights with staff/players

### Admin Workflow
1. Upload tracking + BLB tables
2. Trigger ETL and monitor status
3. Validate QA tables
4. Manage games and data tables

### Player/Parent Workflow (future)
1. View player profile
2. Compare stats over time
3. Review team standings and leaders

---

## 3) MVP Definition of Done

**MVP = production‑ready prototype for junior/college buyers**

- [ ] End‑to‑end workflow works for pilot game(s)
- [ ] ETL validation passes on `18969`
- [ ] Core dashboards render and match ETL outputs
- [ ] Portal can trigger ETL and show job status
- [ ] Documentation updated for any MVP changes
- [ ] QA and testing strategies in place

---

## 4) Milestones and Phases

**Source:** `docs/MASTER_ROADMAP.md` + `docs/MASTER_IMPLEMENTATION_PLAN.md`

### Phases (Summary)
1. Foundation and Documentation (Complete)
2. ETL Optimization
3. Dashboard Enhancement
4. Portal Development
5. Tracker Conversion
6. ML/CV Integration
7. Multi‑Tenancy & Scale
8. Commercial Launch Prep

---

## 5) Technical Design (Summary)

### Core Architecture
- Tracker → ETL → Supabase → Dashboard
- Admin portal orchestrates ETL and data management

### Current Stack
- ETL: Python, pandas
- API: FastAPI
- DB: Supabase (Postgres)
- Dashboard: Next.js 14 + TypeScript
- Portal: HTML/CSS/JS (current)

### Commercialization Additions
- Auth + RBAC
- Multi‑tenant schema + RLS
- Billing (Stripe)
- Monitoring/alerting

---

## 6) Linked Source Docs

- `docs/PROJECT_SCOPE.md`
- `docs/MASTER_ROADMAP.md`
- `docs/MASTER_IMPLEMENTATION_PLAN.md`
- `docs/TECH_STACK_ROADMAP.md`
- `docs/QA_STRATEGY.md`
- `docs/TESTING_STRATEGY.md`
- `docs/commercial/COMMERCIAL_READINESS_CHECKLIST.md`

