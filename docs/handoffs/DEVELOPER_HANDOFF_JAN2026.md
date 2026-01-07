# BenchSight Developer Handoff - January 2026

## Executive Summary

BenchSight is a hockey analytics platform in active development. This handoff covers the current state, what's working, what needs work, and how to continue development.

---

## What Was Delivered

### 1. Tracker v22 (`tracker/tracker_v22.html`)
Production-ready game tracking interface with:
- Full Supabase integration (read/write)
- 12 event types with keyboard shortcuts
- Puck XY tracking (10 points per event)
- Player XY tracking
- Net location picker for shots
- 6+6 player slots per event
- Undo/redo (50 steps)
- Import/export Excel
- Auto-linking (Shot → Save)
- Local storage persistence

### 2. Dashboard v4 (`dashboard/dashboard_v4.html`)
NHL-style analytics dashboard with:
- 6 views (Overview, Box Score, Shot Chart, Players, Advanced, H2H)
- Real-time Supabase data loading
- Team comparison visualizations
- Interactive shot chart with filtering
- Player cards and stat tables

### 3. Backend API (`scripts/tracker_api.py`)
Python API for tracker operations:
- CLI interface for all operations
- HTTP server mode for JavaScript integration
- Full CRUD for events, shifts, XY data
- ETL trigger support
- CSV export functionality

### 4. Documentation
- `docs/README.md` - Complete project overview
- `docs/GAMEPLAN.md` - Development roadmap
- `docs/QUICKSTART.md` - User quick start guide
- `docs/handoffs/` - Previous handoff documents

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
├──────────────────────────┬──────────────────────────────────┤
│    Tracker v22 (HTML)    │      Dashboard v4 (HTML)         │
│    - Event entry         │      - Analytics views           │
│    - XY tracking         │      - Shot charts               │
│    - Shift management    │      - Player stats              │
└───────────┬──────────────┴────────────────┬─────────────────┘
            │                                │
            ▼                                ▼
┌─────────────────────────────────────────────────────────────┐
│                     SUPABASE REST API                        │
│    - fact_events         - fact_puck_xy_long                │
│    - fact_events_player  - fact_player_xy_long              │
│    - fact_shifts         - fact_shot_xy                     │
│    - dim_schedule        - dim_player                       │
└───────────┬─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND SCRIPTS                          │
│    tracker_api.py    - API for tracker operations           │
│    flexible_loader.py - Data loading/ETL                    │
│    qa_comprehensive.py - Data validation                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| `tracker/tracker_v22.html` | ~2200 | Production tracker |
| `dashboard/dashboard_v4.html` | ~800 | Analytics dashboard |
| `scripts/tracker_api.py` | ~700 | Backend API |
| `scripts/flexible_loader.py` | ~600 | Supabase loader |
| `docs/README.md` | ~300 | Documentation |

---

## Supabase Configuration

```javascript
const SUPABASE_URL = 'https://uuaowslhpgyiudmbvqze.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'; // Service role
```

### Key Tables
- `dim_schedule` - Game list
- `dim_player` - Player master
- `fact_gameroster` - Game rosters
- `fact_events` - Tracking events
- `fact_events_player` - Player-event links
- `fact_shifts` - Shift tracking
- `fact_puck_xy_long` - Puck positions
- `fact_shot_xy` - Shot details
- `fact_video` - Video links

---

## Known Issues

### 1. ETL Pipeline Incomplete
Previous developer deleted substantial code. Stat aggregation tables are not being populated:
- `fact_player_game_stats` - Needs calculation logic
- `fact_team_game_stats` - Needs calculation logic
- `fact_player_micro_stats` - Needs calculation logic

**Workaround:** Stats shown in dashboard are calculated client-side from raw events.

### 2. Video Sync Limitations
YouTube iframe API has restrictions. Current implementation:
- Time sync via offset calculation
- No programmatic play/pause control

### 3. XY Data Untested in Production
Puck and player XY tracking is new. Needs validation:
- Test with real game tracking
- Verify Supabase storage
- Check dashboard visualization

---

## Continuing Development

### Immediate Priorities
1. **Test tracker with real game** - Track game 18969
2. **Validate Supabase integration** - Push/pull cycle
3. **Check stat accuracy** - Compare to noradhockey.com

### Week 2 Priorities
1. Restore stat calculation ETL
2. Add QA validation suite
3. Test with multiple games

### Future Enhancements
- Mobile responsive tracker
- xG model implementation
- Real-time collaboration
- Advanced analytics (WAR, RAPM)

---

## Running Locally

```bash
# 1. Open tracker
open tracker/tracker_v22.html

# 2. Open dashboard
open dashboard/dashboard_v4.html

# 3. Run API server (optional)
pip install supabase --break-system-packages
python scripts/tracker_api.py --action serve --port 8765
```

---

## Code Patterns

### Tracker State Management
```javascript
const S = {
  gameId: null,
  events: [],
  shifts: [],
  evt: {
    type: null,
    puckXYPoints: [],
    playerXYPoints: [],
    eventPlayers: [null,null,null,null,null,null],
    // ...
  }
};
```

### Supabase API Calls
```javascript
async function sbFetch(table, query = '') {
  const resp = await fetch(`${SUPABASE_URL}/rest/v1/${table}?${query}`, {
    headers: { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}` }
  });
  return resp.json();
}
```

### Event Data Format
```javascript
{
  event_index: 1001,
  period: 1,
  event_type_: 'Shot',
  event_detail_: 'Shot_Wrist',
  event_successful_: 's',
  player_game_number_: 17,
  xy_x: 175.5,
  xy_y: 42.0,
  net_location: 'GH'
}
```

---

## Delivery Checklist

- [x] tracker_v22.html - Production tracker
- [x] dashboard_v4.html - Analytics dashboard
- [x] tracker_api.py - Backend API
- [x] README.md - Documentation
- [x] GAMEPLAN.md - Development roadmap
- [x] QUICKSTART.md - User guide
- [x] All files in /mnt/user-data/outputs/

---

## Contact

For questions:
1. Review documentation first
2. Check code comments
3. Test with sample data
4. Document any issues found

---

*Handoff Date: January 1, 2026*
*Version: v22*
