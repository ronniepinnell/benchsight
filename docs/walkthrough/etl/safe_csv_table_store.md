# safe_csv.py / table_store.py Deep Dive

**Optional helpers for safer I/O and in-memory tables**

Last Updated: 2026-01-21  
Version: 2.00

---

## Purpose
- `safe_csv.py`: safer CSV read/write with fallback/error handling.
- `table_store.py`: in-memory cache for tables to avoid re-reading CSVs.

These modules are imported opportunistically in `base_etl.py` (used only if present).

---

## What They Do
- `safe_csv.py`: `safe_write_csv`, `safe_read_csv`, `CSVWriteError`.
- `table_store.py`: `get_table(name, output_dir)`, returns DataFrame if cached.

---

## Flow (Optional)
```mermaid
flowchart TD
    DF[DataFrame] --> SAFEWRITE[safe_write_csv] --> CSV
    CSV --> SAFEREAD[safe_read_csv] --> DF2
    DF2 --> TABLESTORE[get_table] -.-> base_etl phases
```

---

## Why It Matters
- Reduces risk of partial/failed CSV writes.
- Reuses in-memory tables to cut down on disk IO in long pipelines.

---

## Good / Risks / Next
- **Good:** Safety and performance when available.
- **Risks:** Optional import—pipeline must still work without them; global cache must stay consistent with disk.
- **Next:** Ensure fallback paths are robust; log when falling back; keep cache invalidation in mind.

---

## Changing Safely
- Keep I/O semantics consistent with default CSV handling.
- If adding caching, ensure cache invalidates on write.
