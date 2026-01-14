# Tracker Logic Extraction Summary

**Complete extraction of all logic from tracker_index_v23.5.html**

Last Updated: 2026-01-13  
Status: ✅ **COMPLETE** (Documentation Complete)

---

## What Has Been Extracted

### ✅ Documentation Created

1. **`TRACKER_FUNCTIONS_INDEX.md`**
   - Complete index of all 200+ functions
   - Organized into 17 categories
   - Function signatures and descriptions
   - Dependencies mapped

2. **`TRACKER_LOGIC_EXTRACTION.md`**
   - Complete logic extraction
   - State management patterns
   - Business rules
   - Data structures
   - Utility functions

3. **`TRACKER_REBUILD_PLAN.md`**
   - 6-phase implementation plan
   - Timeline and milestones
   - Technology stack
   - Success criteria

4. **`TRACKER_REBUILD_ANALYSIS.md`**
   - Platform comparison
   - Next.js recommendation
   - Architecture proposal

5. **`TRACKER_TYPES.ts`** (in `ui/dashboard/src/lib/tracker/types.ts`)
   - Complete TypeScript type definitions
   - All interfaces and types extracted

---

## Extraction Statistics

- **Source File:** 16,162 lines
- **Functions Cataloged:** 200+ functions
- **Categories:** 17 function categories
- **Types Defined:** 30+ TypeScript interfaces
- **State Properties:** 50+ properties in S object
- **Reference Data:** Complete LISTS object structure

---

## Function Categories Extracted

1. **Initialization & Setup** - 12 functions
2. **Period & Time Management** - 9 functions
3. **Video Player Integration** - 35+ functions
4. **Event Management** - 25+ functions
5. **Shift Management** - 20+ functions
6. **Player Management** - 15+ functions
7. **XY Positioning / Rink** - 20+ functions
8. **Slot Management** - 10+ functions
9. **Auto-Functions & Derivation** - 10+ functions
10. **Data Export & Import** - 10+ functions
11. **UI Rendering** - 20+ functions
12. **Modal Management** - 15+ functions
13. **Keyboard Shortcuts** - 5+ functions
14. **Persistence & Sync** - 8+ functions
15. **Game Management** - 10+ functions
16. **Validation & Error Handling** - 8+ functions
17. **Advanced Features** - 20+ functions

**Total: 200+ functions documented**

---

## Key Logic Patterns Extracted

### Event Creation Flow
```
1. Select event type
2. Add players
3. Set XY positions (optional)
4. Auto-derive zone, success, strength
5. Validate
6. Log event
7. Auto-save
8. Update UI
```

### Shift Creation Flow
```
1. Set start/end times
2. Fill on-ice slots
3. Auto-derive strength
4. Auto-derive stop type (from last event)
5. Validate
6. Log shift
7. Auto-save
8. Update UI
```

### Video Sync Flow
```
1. Set period markers (P1Start, P1End, etc.)
2. Calculate running video time
3. Convert video time → game time
4. Capture times to event fields
5. Auto-sync if enabled
```

### Export Flow
```
1. Build events in LONG format (one row per player per event)
2. Build shifts in format
3. Calculate running times
4. Format as Excel (metadata, events, shifts sheets)
5. Download file
```

---

## State Structure Extracted

Complete `S` object structure (50+ properties):
- Game info (gameId, teams, rosters)
- Period/time (period, periodLengths, clock)
- Events/shifts (events[], shifts[], indices)
- Current editing (curr object, selected items)
- XY positioning (xyMode, xySlot, coordinates)
- Video (videoPlayer state, videoTiming)
- Sync (lastSave, connected)

---

## Reference Data Extracted

Complete `LISTS` object structure:
- Event types (16 types)
- Hotkeys mapping
- Event details (detail1/detail2 per type)
- Shift start/stop types
- Event suggestions
- Linked events rules

---

## Data Structures Extracted

Complete TypeScript types for:
- Event object
- Shift object
- Player object
- XYCoordinate
- VideoPlayerState
- GameState
- All related types

---

## Code Location Reference

All functions can be found in:
- **Source File:** `ui/tracker/tracker_index_v23.5.html`
- **Line Range:** Lines 1-16,162
- **Function Patterns:** `^function [name]` (200+ matches)

Use `grep "^function [name]"` to find specific functions.

---

## How to Use This Extraction

### For Rebuild Reference

1. **Check Function Index** - Find function by category
2. **Read Logic Extraction** - Understand patterns and rules
3. **Reference Original Code** - Read actual implementation from tracker file
4. **Convert to TypeScript** - Transform to TypeScript with types
5. **Organize into Modules** - Group related functions

### Extraction Approach

Since the tracker is 16,162 lines with 200+ functions, the recommended approach is:

1. **Use documentation as reference** - Function index tells you what exists
2. **Extract functions as needed** - When building a module, extract its functions
3. **Read from original file** - Use line numbers/grep to find implementations
4. **Convert incrementally** - One module at a time
5. **Test after extraction** - Ensure correctness

---

## Next Steps for Rebuild

### Phase 1: Foundation (Current)
- ✅ Types extracted
- ✅ Function index created
- ✅ Logic patterns documented
- ⏳ Start building modules (extract functions as needed)

### Phase 2: Core Functions
- Extract event management functions (`events.ts`)
- Extract shift management functions (`shifts.ts`)
- Extract utility functions (`utils.ts`, `time.ts`)

### Phase 3: Advanced Functions
- Extract video functions (`video.ts`)
- Extract export functions (`export.ts`)
- Extract XY functions (`xy.ts`)

### Phase 4: Integration
- Convert UI functions to React components
- Integrate with Next.js
- Add TypeScript types throughout

---

## Important Notes

### Original Code Location
- **File:** `ui/tracker/tracker_index_v23.5.html`
- **Size:** 16,162 lines
- **Functions:** 200+ functions (all cataloged)
- **State:** Single global `S` object (extracted structure)
- **Reference Data:** `LISTS` object (extracted structure)

### Code Access
- Functions start with `function [name]` or `async function [name]`
- Use `grep "^function [name]"` to find specific functions
- Line numbers available in function index
- Code needs TypeScript conversion

### Extraction Status
- ✅ **Function cataloging:** COMPLETE (all 200+ functions indexed)
- ✅ **Type definitions:** COMPLETE (all types extracted)
- ✅ **Logic patterns:** COMPLETE (patterns documented)
- ✅ **State structure:** COMPLETE (S object documented)
- ✅ **Reference data:** COMPLETE (LISTS object documented)
- ⏳ **Code extraction:** As needed during rebuild (functions extracted when building modules)

---

## Summary

**All logic has been cataloged and documented.** The extraction documents provide:

1. **Complete function index** - All 200+ functions cataloged
2. **TypeScript types** - All data structures defined
3. **Logic patterns** - All business rules documented
4. **State structure** - Complete state management documented
5. **Reference guide** - How to find and extract functions

**For the rebuild:**
- Use these documents as reference
- Extract functions as needed when building modules
- Convert to TypeScript during extraction
- Test incrementally

The extraction is **complete for documentation purposes**. Actual code extraction will happen incrementally during the rebuild process as modules are built.

---

*Extraction complete: 2026-01-13*  
*All logic cataloged and documented*  
*Ready for Next.js rebuild*
