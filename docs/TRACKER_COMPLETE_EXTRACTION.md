# Tracker Complete Logic Extraction

**Complete extraction of ALL logic from tracker_index_v23.5.html for Next.js rebuild**

Last Updated: 2026-01-13  
Source: `ui/tracker/tracker_index_v23.5.html` (16,162 lines)  
Total Functions: 200+ functions

---

## Extraction Status

✅ **Function Index Created** - All 200+ functions cataloged  
✅ **Types Extracted** - TypeScript types defined  
🟡 **Code Extraction** - In progress  
⏳ **Module Organization** - Pending

---

## Extraction Strategy

Given the massive size (16,162 lines, 200+ functions), extraction is organized by:

1. **Function Index** (`TRACKER_FUNCTIONS_INDEX.md`) - Complete catalog
2. **Logic Patterns** (`TRACKER_LOGIC_EXTRACTION.md`) - Patterns and rules
3. **Module Extraction** (This document) - Actual code extraction by module

---

## Module Organization

Functions will be extracted into these TypeScript modules:

```
src/lib/tracker/
├── types.ts              ✅ Created (TypeScript types)
├── state.ts              ⏳ State management
├── events.ts             ⏳ Event CRUD operations
├── shifts.ts             ⏳ Shift CRUD operations
├── players.ts            ⏳ Player management
├── xy.ts                 ⏳ XY positioning logic
├── video.ts              ⏳ Video player integration
├── export.ts             ⏳ Excel export
├── import.ts             ⏳ Excel import
├── sync.ts               ⏳ Cloud sync (future)
├── validation.ts         ⏳ Validation functions
├── utils.ts              ⏳ Utility functions
├── time.ts               ⏳ Time/period utilities
└── constants.ts          ⏳ Constants and reference data
```

---

## Reference to Original Code

All functions reference line numbers in `tracker_index_v23.5.html`:

- Function definitions found via `grep "^function " tracker_index_v23.5.html`
- Actual implementations need to be read from original file
- Code conversion to TypeScript during extraction

---

## Extraction Process

1. **Read function from original file** (by line number range)
2. **Convert to TypeScript** (add types, fix syntax)
3. **Organize into module** (by category)
4. **Document dependencies** (which functions call which)
5. **Test logic** (ensure correctness)

---

## Next Steps

For complete extraction:

1. Extract core functions first (events, shifts, export)
2. Extract utility functions (time, validation, XY)
3. Extract video functions
4. Extract UI-related functions (for React conversion)
5. Organize into modules
6. Convert to TypeScript

---

## Implementation Note

Full code extraction of 200+ functions is extensive. Recommended approach:

1. **Use extraction docs as reference** during rebuild
2. **Extract functions as needed** when building modules
3. **Convert incrementally** - one module at a time
4. **Test each module** after extraction

The function index and logic extraction documents provide complete reference for rebuilding.

---

*Extraction in progress: 2026-01-13*
