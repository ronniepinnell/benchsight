# BenchSight Tracker - TODO List

**Version:** 17.00  
**Updated:** January 8, 2026

---

## 🔴 Critical / Blocking

- [x] **Ctrl+1-6 browser conflict** - FIXED in v17.00: Added Alt+1-6 as alternative
  - Alt+1-6 works reliably across all browsers
  - Ctrl+1-6 still works in some browsers
  - Workaround: Click opponent buttons manually

- [x] **Shift edit modal shows wrong values** - FIXED in v17.00
  - Added 'OnTheFly' to shiftStart dropdown options
  - Fixed default from 'On The Fly' to 'OnTheFly' (matching LISTS format)

---

## 🟡 High Priority

### Keyboard & UX
- [x] Add Alt+1-6 as alternative to Ctrl+1-6 (FIXED v17.00)
- [x] Fix event log visibility toggle in sidebar (FIXED v17.00)
- [ ] Add "Save As" file picker for local saves
- [ ] Fix score verification loading

### Data Quality
- [ ] Add validation warnings for impossible events (goal without shot, etc.)
- [ ] Add duplicate event detection
- [ ] Add missing required field warnings

### Performance
- [ ] Debounce auto-save to reduce Supabase calls
- [ ] Lazy-load historical events (pagination)
- [ ] Optimize renderAll() - currently re-renders everything

---

## 🟢 Medium Priority

### Video Integration (Major Feature)
- [ ] YouTube IFrame API integration
- [ ] Local video file support (MP4, WebM)
- [ ] Timestamp sync with game clock
- [ ] Frame-by-frame stepping (,/. keys)
- [ ] Playback speed controls (0.25x, 0.5x, 1x, 2x)
- [ ] Period/intermission markers
- [ ] Goal timestamps for quick navigation

### Workflow Improvements
- [ ] Event templates (quick combos)
- [ ] Batch edit mode (select multiple events)
- [ ] Copy/paste events
- [ ] Event reordering (drag and drop)
- [ ] Quick "same as last" event button

### Analytics Preview
- [ ] Mini shot chart in sidebar
- [ ] Possession percentage display
- [ ] Period summary stats
- [ ] Player TOI running total

---

## 🔵 Low Priority / Nice to Have

### UI/UX Polish
- [ ] Resizable panels
- [ ] Dark/light theme toggle
- [ ] Mobile/tablet responsive layout
- [ ] Custom keyboard shortcut editor
- [ ] Customizable event type colors

### Data Management
- [ ] Export to CSV (in addition to Excel)
- [ ] Import from CSV (for corrections)
- [ ] Backup to local file
- [ ] Restore from backup
- [ ] Merge duplicate events

### Collaboration (Future)
- [ ] Real-time sync between multiple trackers
- [ ] Conflict resolution UI
- [ ] Audit log of changes
- [ ] Comments/notes on events

---

## 🟣 Commercial / Platform Features

### Portal (see STRATEGIC_PLAN.md)
- [ ] Admin portal for game management
- [ ] One-click ETL trigger
- [ ] ETL status dashboard
- [ ] User management

### Dashboard
- [ ] Public-facing dashboard
- [ ] Team/player stats pages
- [ ] Leaderboards
- [ ] Embeddable widgets

### API
- [ ] REST API for stats
- [ ] Webhook notifications
- [ ] Rate limiting
- [ ] API key management

### Multi-Tenancy
- [ ] Organization support
- [ ] Custom domains
- [ ] Tier-based features
- [ ] Billing integration

---

## ✅ Recently Completed (v16.xx - v17.xx)

- [x] Alt+1-6 for opponent player selection (v17.00)
- [x] Shift edit dropdown 'OnTheFly' fix (v17.00)
- [x] Event log visibility toggle button (v17.00)
- [x] Fix event_detail_2 code prefix filter (v16.08)
- [x] Add strategic plan documentation (v16.08)
- [x] Fix 1-6 keyboard conflict (v16.07)
- [x] Add backtick for puck mode (v16.07)
- [x] Add auto-calc buttons for success/pressure (v16.07)
- [x] Smaller XY markers with click-through (v16.07)
- [x] Event details from dim_event_detail (v16.06)
- [x] Center-relative XY coordinates (v16.06)
- [x] Side of puck field (v16.01)
- [x] Team colors from Supabase (v16.01)
- [x] Period length 18 min default (v16.02)

---

## Ideas / Brainstorming

### Speed Improvements
- Voice commands for event type ("shot", "pass", etc.)
- Gesture-based XY (swipe to draw path)
- Auto-detect event from video (AI/ML)
- Pre-game lineup import from schedule

### Quality Improvements
- Mandatory XY for shots/goals
- Strength validation (5v5 must have 5 players each)
- Time sequence validation (events in order)
- Cross-reference with play-by-play data

### Integration
- Import official play-by-play as starting point
- Export to StatsCrew format
- Sync with Google Sheets
- Webhook for real-time dashboard updates

---

## Technical Debt

### Code Organization
- [ ] Split into multiple files (events.js, shifts.js, etc.)
- [ ] Move CSS to separate file
- [ ] Add JSDoc comments to functions
- [ ] Remove console.log debug statements
- [ ] Consolidate keyboard handlers into one

### Testing
- [ ] Add unit tests for calculations
- [ ] Add integration tests for Supabase
- [ ] Add E2E tests for critical workflows
- [ ] Set up CI/CD pipeline

### Documentation
- [ ] API documentation for Supabase schema
- [ ] User guide with screenshots
- [ ] Video tutorial for common workflows
- [ ] Troubleshooting guide
