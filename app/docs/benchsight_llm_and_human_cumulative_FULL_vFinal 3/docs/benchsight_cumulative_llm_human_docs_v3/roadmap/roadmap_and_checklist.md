# BenchSight Roadmap & Implementation Checklist (High Level)

This document is a **roadmap for humans and LLMs** describing what exists, what is planned,
and how pieces fit together.

## Layers

1. **Raw / Tracker**
   - Excel-style tracker UI (future: web tracker) to record shifts, events, XY, and video tags.
   - Existing manual tracking workbooks (e.g. 18969) remain the ground truth for layout and logic.

2. **Stage**
   - Staging schemas for:
     - BLB tracking data
     - NHL public data (MoneyPuck, NHL API)
   - Goal: lightly cleaned, row-level mirrors of the source files.

3. **Mart**
   - Fact & dimension tables for:
     - Events (long + wide)
     - Shifts (long + wide)
     - Player boxscores
     - Event chains
     - XY (rink + net)
     - Video bookmarks
   - All keyed to dim tables (player, team, game, dates, zones, etc.).

4. **Analytics / Apps**
   - Power BI semantic model and report pages (team, player, game, microstats).
   - Python/Dash BenchSight prototype for web dashboards.
   - Future ML notebooks for xG, player comps, and microstat-based clustering.

## Implementation Checklist (0–1 month)
- [ ] Confirm database and connection configuration (Postgres, schemas).
- [ ] Run orchestrator script for:
      - BLB tracking ingest → stage → mart.
- [ ] Validate outputs for a few games vs the original Excel tracking.
- [ ] Hook Power BI to CSV exports from the mart tables.
- [ ] Iterate on tracker UI to match Excel logic and reduce clicks.

## Implementation Checklist (1–3 months)
- [ ] Add NHL ingest pipelines (MoneyPuck + NHL API).
- [ ] Build NHL feature tables and BLB–NHL player comparison fact.
- [ ] Expand BenchSight dashboards for teammate/foe, line combos, and head-to-head matchups.
- [ ] Tighten documentation and error handling for non-technical users.

## Implementation Checklist (3+ months)
- [ ] Introduce tracking-derived speed, distance and zone time.
- [ ] Train xG and microstat-based player style models.
- [ ] Integrate fully hosted cloud stack (DB + APIs + dashboards).
- [ ] Explore commercial pilots with local/junior teams.
