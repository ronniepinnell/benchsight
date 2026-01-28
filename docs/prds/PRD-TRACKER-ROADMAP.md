# PRD: Tracker Full Roadmap (Immediate to Commercial)

**Status:** Approved
**Created:** 2026-01-28
**Issue:** #191 (Phase 0), future phases TBD
**Branch:** feature/191-tracker-v29-bugfixes

## Summary

Two-pass tracking strategy with phased new tracker build.

- **Pass 1 (Phase 0):** Use current v29 tracker for highlights + shifts + shots + zone entries
- **Pass 2 (Phase 1+):** Full game tracking with new Next.js tracker

## Phase 0: Track Games NOW (Current v29)

**Goal:** Get meaningful game data into the dashboard ASAP
**Prerequisite:** Fix v29 bugs (GitHub #191)

### Event Tiers

**Tier 1 - MUST Capture (Box Score Foundation, ~3-4 min/game):**
- Goal, Penalty, Save (key), Period Start/End, Faceoff (OZ+DZ), Shifts

**Tier 2 - SHOULD Capture (Analytics Foundation, adds ~4 min):**
- Shot (all on-net), Zone Entry (controlled)

**Tier 3 - SKIP for first pass:**
- Passes, zone exits, turnovers, rebounds, blocked shots, micro-stats

### Deliverables

| # | Deliverable | Status |
|---|-------------|--------|
| 0A | Fix v29 bugs (New Entry, Help modal, Book icon) | In Progress |
| 0B | Track 3-5 games with Tier 1 events | Pending |
| 0C | Run ETL on highlights-only Excel | Pending |
| 0D | Upload to Supabase, verify dashboard | Pending |
| 0E | Dashboard graceful degradation for sparse data | Pending |
| 0F | Add Tier 2 (shots + zone entries) once Tier 1 comfortable | Pending |

## Phase 1: New Next.js Tracker MVP

Unified app: dashboard (`/norad/*`) + tracker (`/track/*`) + admin (`/admin/*`).

**Key features:**
- Auto-timestamps from video (eliminates manual time entry)
- Real-time derivation display with override
- Context-aware minimal forms
- Configurable tracking modes (highlights/standard/full/custom)
- Hardware input controls (HID + scroll)
- Command bar (ported from v29)
- Import from v29 Excel

**Architecture:** Tracker sends raw observations to FastAPI, which validates/derives/enriches and returns data for display. ETL runs batch analytics after game is complete.

## Phase 2: Tauri Desktop Shell

Wrap unified Next.js app in Tauri for local video, offline mode, native HID.

## Phase 3: Video Storage (Cloudflare R2 + Stream)

## Phase 4: Multi-Tenancy (Orgs, Teams, Users, Per-org Config)

## Phase 5: ML/CV Integration (Smart Suggestions to Auto-Tracking)

## Phase 6: dbt Analytics Layer

## Decisions

| Question | Answer |
|----------|--------|
| First pass events | Tier 1+2, ~7-8 min/game |
| Shifts | Yes - low effort, massive payoff |
| Dashboard integration | Unified app at /track/* and /admin/* |
| Desktop app | Tauri wrapping same Next.js app |
| Customizability | Extreme - configurable modes, chains, fields per org |
| Pipeline cleanup | Strict contracts: tracker export schema > API validation > ETL batch |
| dbt | Phase 6, after multi-tenancy |

## Full Roadmap

See `/Users/ronniepinnell/.claude/plans/squishy-meandering-horizon.md` for complete details including architecture diagrams, file structures, build order, and commercial pricing.
