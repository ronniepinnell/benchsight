# BenchSight Roadmap

**Last Updated:** January 8, 2026  
**Current Version:** 16.08

> **Note:** For full strategic planning including commercial platform, hosting, and API design, see [STRATEGIC_PLAN.md](STRATEGIC_PLAN.md)

## Current State

| Component | Status | Version |
|-----------|--------|---------|
| ETL Pipeline | ✅ Production | 14.21 |
| Tracker UI | 🟡 Beta | 16.08 |
| Supabase | ✅ Connected | - |
| Dashboard | 🔴 Not Started | - |
| Portal | 🔴 Not Started | - |
| API | 🔴 Not Started | - |

## Tracker v16.08 Changes

### Just Completed
- [x] Event detail 2 from dim_event_detail_2 (code prefix filter)
- [x] Strategic planning documentation
- [x] XY coordinates center-relative (0,0 = center ice)
- [x] Event details from dim_event_detail
- [x] Play details from dim_play_detail/dim_play_detail_2
- [x] 1-6 hotkeys for event players (fixed)
- [x] Backtick hotkey to switch to puck XY mode
- [x] Smaller markers that don't block clicks
- [x] Auto-calc buttons for success/pressure

### Immediate Priorities (v16.09+)

#### 1. Video Integration
- [ ] YouTube IFrame API embed
- [ ] Local file video playback
- [ ] Time sync (game time → video time)
- [ ] Click-to-seek from events
- [ ] Slow motion / frame advance

#### 2. Hotkey Improvements
- [ ] Fix period selection (F1-F4 instead of 1-4)
- [ ] Add mode indicator (EVENT vs XY vs SHIFT)
- [ ] Hotkey cheat sheet overlay

#### 3. UX Polish
- [ ] Save file location picker
- [ ] Better error messages (toasts not console)
- [ ] Undo for player add/remove
- [ ] Confirm on delete

### Short-Term (2-4 weeks)

#### 4. Batch Operations
- [ ] Select multiple events
- [ ] Bulk edit fields
- [ ] Bulk delete

#### 5. Validation
- [ ] NORAD score verification display
- [ ] Missing required field warnings
- [ ] Duplicate event detection

#### 6. Performance
- [ ] Lazy load historical events
- [ ] Virtualized event list
- [ ] IndexedDB for large datasets

### Medium-Term (1-3 months)

#### 7. Dashboard
- [ ] Player stats page
- [ ] Team comparison
- [ ] Game summary
- [ ] Heat maps from XY data

#### 8. ETL Enhancements
- [ ] Process tracker exports automatically
- [ ] XY coordinate tables
- [ ] Expected goals (xG) calculation

#### 9. Deployment
- [ ] Electron desktop wrapper
- [ ] Auto-update mechanism
- [ ] Cloud sync via Supabase

### Long-Term (3+ months)

#### 10. Advanced Analytics
- [ ] ML-based play type prediction
- [ ] Video object detection assist
- [ ] Player tracking integration

#### 11. Collaboration
- [ ] Multi-user editing
- [ ] Real-time sync
- [ ] Comment/annotation system

## Known Issues to Fix

| Issue | Priority | Est. Effort |
|-------|----------|-------------|
| Period hotkey conflict | HIGH | 30 min |
| Shift edit dropdowns wrong | MEDIUM | 1 hour |
| Modal arrow key nav | LOW | 30 min |
| Score verification not showing | MEDIUM | 1 hour |

## Feature Ideas (Backlog)

- Voice commands for event logging
- Automatic shift detection from video
- Integration with official league APIs
- Mobile companion app
- Printable game reports
- Export to other analytics platforms

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Time to track 1 game | ~4 hours | <2 hours |
| Events per minute (avg) | 1.5 | 3+ |
| Error rate | Unknown | <5% |
| User satisfaction | N/A | High |

---

*This roadmap is updated each session. Priority changes based on user feedback.*
