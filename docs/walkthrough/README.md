# BenchSight Walkthrough

**High-level overview + links to deep dives by component**

Last Updated: 2026-01-21  
Version: 2.00

---

## Architecture at a Glance

```mermaid
flowchart LR
    Tracker[Tracker (HTML/JS)] --> ETL[ETL (Python)]
    BLB[BLB Excel] --> ETL
    ETL -->|CSV + Upload| Supabase[(Supabase Postgres)]
    Supabase --> Views[SQL Views]
    Views --> Dashboard[Dashboard (Next.js)]
    Portal[Portal (HTML/JS)] --> API[API (FastAPI)]
    API --> ETL
    API --> Supabase
```

## Read This First
- `docs/walkthrough/ETL.md`
- `docs/walkthrough/etl/base_etl.md`
- `docs/walkthrough/etl/data_loader.md`
- `docs/walkthrough/etl/calculations.md`
- `docs/walkthrough/etl/tables.md`
- `docs/walkthrough/etl/key_utils.md`
- `docs/walkthrough/etl/table_writer.md`
- `docs/walkthrough/etl/safe_csv_table_store.md`
- `docs/walkthrough/etl/shift_enhancer.md`
- `docs/walkthrough/API.md`
- `docs/walkthrough/Dashboard.md`
- `docs/walkthrough/Portal.md`
- `docs/walkthrough/Tracker.md`
- `docs/walkthrough/SQL.md`
- `docs/walkthrough/Scripts.md`

## What You’ll Learn
- How data enters (tracker + BLB Excel), flows through ETL, lands in Supabase, and is consumed by the dashboard
- How control-plane pieces (API/Portal) trigger ETL/uploads
- Where key invariants/validations live
- Where to add new features safely
