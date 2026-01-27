# Tracker Walkthrough

**Legacy HTML/JS tracker that produces tracking Excel for ETL**

Last Updated: 2026-01-21  
Version: 2.00

---

## Role
- Capture game events/shifts and export tracking files consumed by ETL.
- Future plan: convert to Next.js/Rust (see tracker conversion docs).

## Where to Look
- Legacy tracker code lives in `ui/tracker/` (HTML/JS).
- Docs: `docs/tracker/` and `docs/archive/` (conversion plans, reference).

## Flow
1) User tracks events/shifts in the browser.
2) Tracker exports Excel with events/shifts sheets.
3) ETL ingests tracking Excel via `data_loader.py`.

## Extending Safely
- Keep export format stable (events + shifts sheets) to match ETL expectations.
- For new fields, update both tracker export and ETL ingestion/validation.

## Assessment
- **Good:** Functional legacy tracker with export; clear role in pipeline.
- **Risks/Bad:** Legacy stack; no auth; no cloud persistence; conversion pending.
- **Next:** Plan Next.js/Rust conversion; maintain export compatibility; add tests for export format.
