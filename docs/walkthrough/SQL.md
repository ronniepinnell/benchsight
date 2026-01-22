# SQL Walkthrough

**Views and schema support for the dashboard**

Last Updated: 2026-01-21  
Version: 2.00

---

## Folder Map
- `sql/views/` — Supabase view definitions
- `sql/reset_supabase.sql` — baseline reset script

## Role
- Provide pre-aggregated views for dashboard performance and consistency.
- Encapsulate calculations so dashboard queries stay simple.

## Flow
1) ETL uploads tables to Supabase.
2) Run view scripts in `sql/views/` to create/refresh views.
3) Dashboard queries views (not raw fact tables) via Supabase.

## Extending Safely
- Add new views for heavy aggregations instead of client-side processing.
- Keep view naming consistent with existing patterns (v_*).
- Document new views in `docs/data/` if they expose new fields or metrics.

## Assessment
- **Good:** Views improve performance and consistency; clear separation from raw facts.
- **Risks/Bad:** View updates need coordination with dashboard; missing documentation if new views added ad hoc.
- **Next:** Document new views in data docs; version view changes; ensure dashboard queries stay aligned.
