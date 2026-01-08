# BenchSight Tracker - Honest Assessment

**Version:** 16.08  
**Date:** January 8, 2026  
**Author:** Claude (AI Assistant)

---

## Executive Summary

BenchSight Tracker is a **functional but rough** hockey event tracking application. It successfully captures events, shifts, and XY coordinates for the BenchSight ETL pipeline. However, it has accumulated significant technical debt, UX friction, and unresolved bugs that limit its efficiency.

**Current State: 70-75% of potential value captured**

---

## What Works Well ✅

### Core Functionality
| Feature | Status | Notes |
|---------|--------|-------|
| Event tracking | ✅ Working | All 12+ event types supported |
| Shift management | ✅ Working | Start/end times, players on ice |
| XY coordinates | ✅ Working | Center-relative (0,0 = center ice) |
| Excel export | ✅ Working | Compatible with ETL pipeline |
| Supabase integration | ✅ Working | Loads games, rosters, dimensions |
| Linked events | ✅ Working | Shot → rebound → goal chains |
| Team colors/logos | ✅ Working | Loaded from dim_team |
| Event details 1 | ✅ Working | From dim_event_detail |
| Event details 2 | ✅ Working | From dim_event_detail_2 (v16.08 fix) |

### Data Quality
- Event details load from `dim_event_detail` filtered by event_type_name
- Event details 2 load from `dim_event_detail_2` filtered by code prefix
- Play details load from `dim_play_detail` and `dim_play_detail_2`
- Player roles load from `dim_player_role`
- Validation against NORAD official records possible

---

## What Doesn't Work ❌

### Critical Issues
| Issue | Impact | Status |
|-------|--------|--------|
| **Ctrl+1-6 browser conflict** | Can't quickly select opponent players | Partial - browser intercepts Ctrl+number |
| **No video sync** | Manual time entry is slow and error-prone | Not started |
| **Shift edit dropdowns mismatch** | Confusing UX when editing shifts | Not fixed |
| **Player slot click doesn't always select** | Frustrating workflow | Intermittent |

### Medium Issues
| Issue | Impact | Status |
|-------|--------|--------|
| Event log visibility toggle broken | Minor UX annoyance | Not fixed |
| Save file location unclear | User confusion | No file picker |
| Score verification not loading | Debug feature broken | Not fixed |
| No undo for events | Can only delete, not undo | Not implemented |

### Low Priority
| Issue | Impact | Status |
|-------|--------|--------|
| No mobile/tablet layout | Desktop only | Not started |
| No dark/light toggle | Dark only | Not started |
| No resizable panels | Fixed layout | Not started |

---

## Technical Debt Assessment

### Architecture Problems
1. **Single 7000+ line HTML file** - Impossible to maintain, test, or refactor
2. **Two conflicting keyboard handlers** - Lines 1974 and 6530 both handle keydown
3. **Global state object `S`** - No encapsulation, hard to reason about
4. **No error boundaries** - Supabase failures can break UI silently
5. **Mixed concerns** - UI, data, export all interleaved

### Code Quality
```
Lines of code: ~7,000
Functions: ~150
Global variables: 50+
Comments: Sparse
Tests: None
```

### What I Would Do Differently
If starting over:
1. **Use React/Vue** - Component-based architecture
2. **TypeScript** - Type safety for complex data structures
3. **Split into modules** - Separate files for events, shifts, XY, export
4. **IndexedDB** - Better than localStorage for large datasets
5. **Video sync first** - Most valuable feature for accuracy

---

## Feature Roadmap

### Phase 1: Stabilization (Current)
- [x] Fix 1-6 keyboard conflict
- [x] Add auto-calc for pressure/success
- [x] Smaller XY markers with click-through
- [ ] Fix Ctrl+1-6 (may need Electron)
- [ ] Fix shift edit dropdown display
- [ ] Add comprehensive error handling

### Phase 2: Video Integration (High Value)
- [ ] YouTube IFrame API integration
- [ ] Video file playback support
- [ ] Time sync between video and clock
- [ ] Frame-by-frame stepping
- [ ] Slow motion / speed controls
- [ ] Game markers (period starts, goals)

### Phase 3: Workflow Optimization
- [ ] Batch event templates (common sequences)
- [ ] Quick replay review mode
- [ ] Keyboard-only workflow
- [ ] Auto-save with conflict resolution
- [ ] Multi-game session support

### Phase 4: Analytics Preview
- [ ] Real-time shot chart
- [ ] Possession timeline
- [ ] Player heat maps
- [ ] Expected goals preview

---

## Known Workarounds

### Ctrl+1-6 Not Working
**Workaround:** Click the opponent player number buttons directly, or use the roster panel to add opposing players.

### Can't Click Through Markers
**Status:** Fixed in v16.07 - markers now have `pointer-events: none`

### Getting Back to Puck Mode
**Workaround:** Press ` (backtick) or Tab to toggle modes

### Team Selection
**Workaround:** Press H for Home, A for Away (1/2 no longer work)

---

## Time Estimates

| Task | Hours | Priority |
|------|-------|----------|
| Fix remaining keyboard issues | 2-4 | High |
| Add proper error handling | 4-8 | High |
| Video integration (basic) | 20-30 | High |
| Video integration (full) | 40-60 | Medium |
| Refactor to React | 80-120 | Low |
| Mobile layout | 20-40 | Low |

---

## Recommendations

### Do Now
1. **Use the tracker as-is** for catching up on games
2. **Export after each session** - don't trust auto-save alone
3. **Verify goals against noradhockey.com** after each game

### Do Next
1. **Video integration** is the single highest-ROI feature
2. Consider **Electron wrapper** for better keyboard control
3. Build **validation dashboard** for data quality checks

### Don't Bother
1. Mobile optimization (low ROI for single user)
2. Multi-user collaboration (not needed)
3. Full React rewrite (diminishing returns)

---

## Conclusion

BenchSight Tracker is **good enough for its purpose** - tracking hockey games to feed the ETL pipeline. The core functionality works. The rough edges are frustrating but workable.

**Investment recommendation:** Focus on video integration (20-30 hours) rather than polish. Video sync would dramatically improve tracking speed and accuracy, delivering more value than fixing minor UX issues.

The tracker has reached the point of diminishing returns for incremental improvements. Either use it as-is, or invest in the video feature that would be transformational.
