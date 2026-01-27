# table_writer.py Deep Dive

**Saving tables and toggling Supabase uploads**

Last Updated: 2026-01-21  
Version: 2.00

---

## Purpose
`src/core/table_writer.py` abstracts writing tables to disk and controlling Supabase upload enable/disable flags.

---

## What It Does
- `save_output_table`: write DataFrames to CSV output.
- `enable_supabase` / `disable_supabase`: toggle upload mode.
- `is_supabase_enabled`: check flag.

---

## Flow
```mermaid
flowchart TD
    DF[DataFrame] --> SAVE[save_output_table]
    SAVE --> CSV[data/output/*.csv]
    TOGGLE[enable/disable_supabase] --> FLAG[is_supabase_enabled]
    FLAG --> (upload step outside)
```

---

## Why It Matters
- Centralizes output handling and upload toggles; reduces ad-hoc writes.

---

## Good / Risks / Next
- **Good:** Single place to control output and upload toggles.
- **Risks:** If bypassed, outputs may be inconsistent; upload toggle is global state—use carefully.
- **Next:** Keep all output writes here; consider logging and checksums if needed.

---

## Changing Safely
- Route new output logic through `save_output_table`.
- Avoid global state conflicts; set/clear upload flag explicitly.
