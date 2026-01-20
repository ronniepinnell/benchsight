# Tracker Rebuild Implementation Plan

**Complete rebuild of BenchSight Game Tracker in Next.js 14**

Last Updated: 2026-01-13  
Status: In Progress  
Timeline: 4-6 weeks  
Current Tracker: v23.5 (keep running)  
New Tracker: v24.0 (Next.js rebuild)

---

## Overview

**Goal:** Rebuild the game tracker from scratch in Next.js 14 with TypeScript, modular components, and modern architecture.

**Strategy:** Build new tracker alongside current tracker, migrate when ready.

---

## Project Structure

```
ui/dashboard/src/
├── app/
│   └── (dashboard)/
│       └── tracker/                          ← NEW: Tracker routes
│           ├── page.tsx                      ← Tracker home (game list)
│           ├── [gameId]/
│           │   └── page.tsx                  ← Game tracker page
│           └── layout.tsx                    ← Tracker layout
│
├── components/
│   └── tracker/                              ← NEW: Tracker components
│       ├── layout/
│       │   ├── TrackerLayout.tsx            ← Main layout (panels)
│       │   ├── TrackerHeader.tsx            ← Header (game select, clock, score)
│       │   └── TrackerPanel.tsx             ← Resizable panel wrapper
│       │
│       ├── video/
│       │   ├── VideoPlayer.tsx              ← Video player (YouTube/local)
│       │   ├── VideoControls.tsx            ← Playback controls
│       │   └── VideoMarkers.tsx             ← Period markers
│       │
│       ├── rink/
│       │   ├── Rink.tsx                     ← SVG rink component
│       │   ├── RinkXY.tsx                   ← XY positioning logic
│       │   └── RinkControls.tsx             ← XY mode controls
│       │
│       ├── events/
│       │   ├── EventForm.tsx                ← Event input form
│       │   ├── EventTypeSelector.tsx        ← Event type buttons
│       │   ├── EventLog.tsx                 ← Event list display
│       │   ├── EventItem.tsx                ← Single event row
│       │   └── PlayerSelector.tsx           ← Player selection
│       │
│       ├── shifts/
│       │   ├── ShiftPanel.tsx               ← Shift tracking panel
│       │   ├── ShiftForm.tsx                ← Shift input form
│       │   ├── LinePresets.tsx              ← Line preset buttons
│       │   └── OnIceRoster.tsx              ← Current on-ice players
│       │
│       └── shared/
│           ├── GameSelector.tsx             ← Game selection dropdown
│           ├── PeriodSelector.tsx           ← Period buttons
│           └── ClockDisplay.tsx             ← Game clock display
│
├── lib/
│   └── tracker/                              ← NEW: Tracker business logic
│       ├── types.ts                          ← TypeScript types
│       ├── state.ts                          ← State management (Zustand?)
│       ├── events.ts                         ← Event CRUD operations
│       ├── shifts.ts                         ← Shift CRUD operations
│       ├── sync.ts                           ← Cloud sync (Supabase)
│       ├── export.ts                         ← Excel export
│       ├── video.ts                          ← Video integration
│       └── utils.ts                          ← Tracker utilities
│
└── types/
    └── tracker.ts                            ← Tracker TypeScript types
```

---

## Phase 1: Foundation (Week 1)

**Goal:** Set up structure, extract types, create basic layout

### Tasks

1. ✅ **Project Structure**
   - Create tracker directory structure
   - Set up Next.js page routes
   - Create component directories

2. ✅ **TypeScript Types**
   - Extract types from current tracker
   - Define Event, Shift, State types
   - Create type definitions

3. ✅ **Basic Layout**
   - Create TrackerLayout component
   - Create TrackerHeader component
   - Create panel structure (left, center, right)

4. ✅ **State Management**
   - Set up state management (React state or Zustand)
   - Define state structure
   - Create state hooks

**Deliverables:**
- Project structure created
- TypeScript types defined
- Basic layout working
- State management set up

---

## Phase 2: Core Components (Week 2)

**Goal:** Build core tracker components

### Tasks

1. ✅ **Rink Component**
   - SVG rink component
   - XY positioning logic
   - Click to place XY coordinates
   - Puck/Player mode toggle

2. ✅ **Event Form**
   - Event type selector
   - Player selector
   - Zone/success indicators
   - Event details dropdowns

3. ✅ **Event Log**
   - Event list display
   - Event filtering
   - Event editing
   - Event deletion

4. ✅ **Shift Panel**
   - Shift tracking UI
   - Line presets
   - On-ice roster
   - Shift times

**Deliverables:**
- Core UI components
- Basic interactivity
- Event/shift forms working

---

## Phase 3: Logic & State (Week 3)

**Goal:** Implement tracker business logic

### Tasks

1. ✅ **Event Management**
   - Add event function
   - Edit event function
   - Delete event function
   - Event validation

2. ✅ **Shift Management**
   - Add shift function
   - Edit shift function
   - Delete shift function
   - Shift validation

3. ✅ **State Management**
   - State persistence (localStorage)
   - State synchronization
   - State loading/saving

4. ✅ **Game Management**
   - Game selection
   - Game loading
   - Game saving
   - Roster loading

**Deliverables:**
- Functional event/shift management
- State persistence working
- Game loading/saving

---

## Phase 4: Video Integration (Week 4)

**Goal:** Add video player functionality

### Tasks

1. ✅ **Video Player**
   - YouTube integration
   - Local video file support
   - Video controls (play, pause, seek)
   - Video speed control

2. ✅ **Video Sync**
   - Period markers
   - Clock synchronization
   - Time capture (Start/End buttons)
   - Video time → game time conversion

3. ✅ **Multiple Sources**
   - Multiple video sources
   - Source switching
   - Source management

**Deliverables:**
- Video player working
- Video sync functional
- Multiple sources supported

---

## Phase 5: Export & Integration (Week 5)

**Goal:** Add export and Supabase integration

### Tasks

1. ✅ **Excel Export**
   - Event export (Excel format)
   - Shift export (Excel format)
   - Export to match ETL format
   - Export validation

2. ✅ **Supabase Integration**
   - Cloud sync (save/load)
   - Authentication (use dashboard auth)
   - Real-time sync (optional)
   - Conflict resolution

3. ✅ **Dashboard Integration**
   - Navigation from dashboard
   - Shared authentication
   - Shared components
   - Unified deployment

**Deliverables:**
- Excel export working
- Cloud sync functional
- Integrated with dashboard

---

## Phase 6: Polish & Testing (Week 6)

**Goal:** Testing, polish, and documentation

### Tasks

1. ✅ **Testing**
   - Component testing
   - Integration testing
   - User testing
   - Bug fixes

2. ✅ **Polish**
   - UI improvements
   - Performance optimization
   - Error handling
   - Loading states

3. ✅ **Documentation**
   - User guide
   - Developer docs
   - API docs
   - Migration guide

4. ✅ **Deployment**
   - Production build
   - Deployment to Vercel
   - Environment variables
   - Monitoring

**Deliverables:**
- Production-ready tracker
- Documentation complete
- Deployed and tested

---

## Technology Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS (same as dashboard)
- **State:** React state (or Zustand if needed)
- **UI Components:** shadcn/ui (same as dashboard)

### Integration
- **Database:** Supabase (same as dashboard)
- **Auth:** Supabase Auth (same as dashboard)
- **Video:** YouTube IFrame API, HTML5 Video
- **Export:** SheetJS (xlsx) library

### Development
- **Linting:** ESLint (Next.js config)
- **Formatting:** Prettier
- **Testing:** Jest + React Testing Library (optional)
- **Type Checking:** TypeScript

---

## Key Features to Implement

### Core Features (Must Have)
- ✅ Event tracking (shots, goals, passes, etc.)
- ✅ XY positioning on rink
- ✅ Shift tracking
- ✅ Game clock synchronization
- ✅ Excel export (ETL format)
- ✅ Local storage persistence

### Enhanced Features (Should Have)
- ✅ Video player integration
- ✅ Cloud sync (Supabase)
- ✅ Authentication
- ✅ Multi-game support
- ✅ Roster management

### Advanced Features (Nice to Have)
- ✅ Real-time collaboration
- ✅ Offline mode
- ✅ Mobile support
- ✅ Keyboard shortcuts
- ✅ Advanced analytics

---

## Migration Strategy

### Current Tracker (v23.5)
- ✅ **Keep running** - Use while building new tracker
- ✅ **No changes** - Don't modify existing tracker
- ✅ **Reference** - Use as reference for features

### New Tracker (v24.0)
- ✅ **Build new** - Complete rebuild in Next.js
- ✅ **Feature parity** - Match core features first
- ✅ **Incremental** - Add features incrementally
- ✅ **Test thoroughly** - Test before migration

### Migration Path
1. **Build new tracker** (4-6 weeks)
2. **Feature parity** - Match core features
3. **User testing** - Test with real games
4. **Data migration** - Migrate existing data (if needed)
5. **Switch over** - Replace old tracker
6. **Deprecate old** - Keep old tracker as backup

---

## Success Criteria

### Functionality
- ✅ All core features working (events, shifts, export)
- ✅ Feature parity with current tracker
- ✅ Excel export matches ETL format
- ✅ Cloud sync working

### Quality
- ✅ TypeScript (no `any` types)
- ✅ Component-based architecture
- ✅ Clean, maintainable code
- ✅ Error handling robust

### Integration
- ✅ Integrated with dashboard
- ✅ Shared authentication
- ✅ Shared components
- ✅ Unified deployment

### Performance
- ✅ Fast load time (< 2 seconds)
- ✅ Smooth interactions
- ✅ Efficient rendering
- ✅ Optimized bundle size

---

## Risks & Mitigation

### Risk 1: Timeline Overrun
**Mitigation:** 
- Build incrementally
- Focus on core features first
- Use existing components from dashboard
- Reuse logic where possible

### Risk 2: Feature Gaps
**Mitigation:**
- Maintain feature list
- Check against current tracker regularly
- User testing early
- Prioritize must-have features

### Risk 3: Data Migration
**Mitigation:**
- Excel export format compatibility
- Test data import/export
- Keep old tracker available
- Document migration process

### Risk 4: Performance Issues
**Mitigation:**
- Optimize rendering (React.memo)
- Code splitting
- Lazy loading
- Performance testing

---

## Next Steps (Immediate)

1. ✅ **Create project structure** - Set up directories
2. ✅ **Extract TypeScript types** - From current tracker
3. ✅ **Create basic layout** - TrackerLayout component
4. ✅ **Set up state management** - State structure
5. ✅ **Start with Rink component** - Core visual component

---

## Questions & Decisions

1. **State Management:** React state or Zustand? (Start with React state, add Zustand if needed)
2. **Video Library:** YouTube IFrame API or react-player? (Start with YouTube IFrame API)
3. **Export Library:** SheetJS (xlsx) or exceljs? (Use SheetJS - already in current tracker)
4. **Testing:** Unit tests or integration tests? (Start with integration tests)
5. **Mobile:** Mobile support in v1 or v2? (v2 - focus on desktop first)

---

*Plan created: 2026-01-13*  
*Next update: After Phase 1 completion*