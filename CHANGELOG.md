# BenchSight Changelog

All notable changes to BenchSight are documented in this file.

---

## v17.00 - January 8, 2026

### BenchSight Tracker v17.00 - Keyboard & Shift Modal Fixes

**Critical Fix - Opponent Player Selection:**
- FIXED: Added Alt+1-6 as alternative to Ctrl+1-6 for opponent players
- Alt+1-6 works reliably across all browsers (Ctrl+1-6 intercepted by browsers)
- Both Alt+1-6 and Ctrl+1-6 now supported (Alt recommended)
- Updated help section to show Alt+1-6 as primary method

**Critical Fix - Shift Edit Dropdown:**
- FIXED: Shift type dropdowns now match saved values
- Added 'OnTheFly' to shiftStart list (was missing)
- Changed default from 'On The Fly' to 'OnTheFly' (matching LISTS format)
- Dropdowns now show correct selection when editing shifts

**New Feature - Event Log Toggle:**
- Added toggle button (📝) to event log header
- Click to show/hide event log section
- Improves screen real estate when needed

**Updated Documentation:**
- Updated TODO.md with completed fixes
- Updated help text for keyboard shortcuts

---

## v16.08 - January 8, 2026

### BenchSight Tracker v16.08 - Event Detail 2 Fix & Strategic Planning

**Critical Fix - Event Detail 2 Dropdown:**
- FIXED: Event detail 2 now properly loads from `dim_event_detail_2`
- Changed from category filter to **code prefix** filter
- Example: `Zone_Entry` → filters for codes starting with `ZoneEntry_`
- Now includes code field in eventDetails2: `{ id, code, name, category }`
- Console logging added for debugging: "Detail2 filter: ZoneEntry_ → 15 options"

**Code Prefix Mapping:**
| Detail 1 Contains | Code Prefix |
|-------------------|-------------|
| Shot_ | Shot_ |
| Pass_ | Pass_ |
| Goal_ | Goal_ |
| Save_ | Save_ |
| Penalty_ | Penalty_ |
| Giveaway | Giveaway_ |
| Takeaway | Takeaway_ |
| Entry | ZoneEntry_ |
| Exit, Keepin | ZoneExit_ |
| Stoppage_Play | Stoppage_ |
| Play_Offensive | PlayOffensive_ |
| Play_Defensive | PlayDefensive_ |
| Faceoff_ | Faceoff_ |
| Possession_ | Possession_ |
| Rebound_ | Rebound_ |

**Documentation:**
- Added `docs/STRATEGIC_PLAN.md` - Full rebuild plan, hosting, API design
- Updated `docs/HONEST_ASSESSMENT.md` - Current 70-75% status
- Updated `docs/TODO.md` - Complete issue tracking

---

## v16.07 - January 8, 2026

### BenchSight Tracker v16.07 - Keyboard Fixes & Auto-Calc Features

**Critical Keyboard Fix:**
- FIXED: 1-6 keys now select Event Players (was conflicting with old team selection)
- Removed conflicting 1/2 → team mapping from legacy handler
- Use H/A keys for Home/Away team selection instead
- Use ` (backtick) to switch back to Puck XY mode
- Ctrl+1-6 selects Opponent Players (may still conflict with browser tabs)

**Auto-Calculate Features:**
- Added ⚡ button on Success field - auto-derives player success from event success
- Added ⚡ button on Pressure field - auto-calculates pressure from XY positions
- `derivePlayerSuccess()` - Event P1 gets event success, opponents get inverse for turnovers
- `autoCalcPressure()` - Uses configurable pressure distance setting

**XY Marker Improvements:**
- Reduced marker sizes: current last=2.5, current other=1.5, history=2/1.2
- Added `pointer-events: none` so clicks pass through to add new points
- Can now click on rink even when markers are present

**Hotkey Reference:**
- ` (backtick) = Switch to Puck XY mode
- 1-6 = Select Event Player 1-6
- Ctrl+1-6 = Select Opponent Player 1-6 (browser may intercept)
- H = Home team, A = Away team
- Tab = Toggle Puck/Player XY mode

---

## v16.06 - January 8, 2026

### BenchSight Tracker v16.06 - Event Details from Supabase & Center-Relative XY

**Event Details from Supabase:**
- Detail 1 (event_detail) now pulls from `dim_event_detail` table
- Detail 2 (event_detail_2) now pulls from `dim_event_detail_2` table
- Falls back to hardcoded LISTS.details if Supabase not connected
- Loaded at startup via `loadReferenceData()`
- Category matching: Shot_, Pass_, Goal_, Save_, Penalty_, Giveaway, Takeaway, Entry, Exit, Stoppage, Play_Offensive, Play_Defensive

**XY Coordinates - Center-Relative System:**
- All rink coordinates now stored as center-relative (0,0 = center ice)
- Rink SVG is 200x85, center at (100, 42.5)
- Coordinate ranges: x: -100 to +100, y: -42.5 to +42.5
- Tooltip shows center-relative coords on hover
- Updated: handleRinkClick, drawPath, handleRinkHover

**Play Details Dropdown Fix:**
- Options now built per-player with proper `selected` attribute
- Missing values added dynamically if not in dim_play_detail tables

---

## v16.02 - January 8, 2026

### BenchSight Tracker v16.02 - Period Length, Play Details Debug, UI Improvements

**Period Length Default Changed to 18 Minutes:**
- Default period length changed from 20 min to 18 min (NORAD standard)
- Updated: clock, shift start, settings, video timing modal, all fallbacks
- Video formula now displays variable period calculation (period_seconds × 60)

**Play Details Debug Logging:**
- Added extensive console logging to diagnose why play_detail1/play_detail_2 aren't loading
- Logs column names from Supabase response
- Logs sample player with play_detail data
- Logs raw and mapped values during conversion

**Box Score Relocated:**
- Added prominent box score below event list in center panel
- Shows team names, goals, and SOG at a glance
- Original box score in left panel still functional

**Searchable Play Detail Dropdowns:**
- Play Detail 1 and Play Detail 2 now use input + datalist
- Type to search/filter instead of scrolling long list

**Notes:**
- If play_details still not loading, check browser console after loading a game
- Console will show exact column names and values from Supabase

---

## v16.01 - January 8, 2026

### BenchSight Tracker v16 - Critical Bug Fixes & Side of Puck

**Critical Bug Fixes:**
- **Event log display fixed**: Fixed `renderEventLog()` and `renderEventList()` calling non-existent functions. Now correctly calls `renderEvents()`. This was causing the event log to not display properly.
- **Period filter fixed**: Event log now properly shows events when filtering by period (ALL, P1, P2, P3, OT).

**SOG (Shots on Goal) Calculation:**
- **Consistent SOG logic** across all UI components (box score, quick stats, full box score modal)
- SOG = shots reaching net (`shot_onnetsaved`, `shot_onnetgoal`) + goals (`goal_scored`, `goal_shootout`, `goal_penaltyshot`)
- Excludes blocked shots, missed shots

**Team Colors & Logos:**
- Team colors loaded from `dim_team.team_color1` and applied to CSS `--home`/`--away` variables
- Team logos loaded from `dim_team.team_logo` and displayed in team headers
- Team dots color updated to match team colors

**Side of Puck (New Feature):**
- Added "Side of Puck" dropdown to player details panel
- Auto-calculate button (⚡) determines Offensive/Defensive based on zone and player team
- Logic: Event team players match zone directly; opponent players get inverted zone
- Value preserved from fact_event_players.side_of_puck when loading existing data
- Exported in data output as `side_of_puck`

**UI Improvements:**
- Team names shown instead of "Home"/"Away" in all UI elements
- Logo images auto-hide if URL fails to load

---

## v15.03 - January 8, 2026

### BenchSight Tracker v15 - Event Filter, Play Details, Team Logos

**Critical Bug Fixes:**
- **Event log filter**: Fixed bug where events only showed when "OT" was selected. Now properly shows all events when "ALL" is selected. Added case-insensitive period matching.
- **Official score loading**: Added better error handling and console logging to debug score loading from dim_schedule.

**Play Detail Dropdowns:**
- Play Detail 1 dropdown now populated from `dim_play_detail` table
- Play Detail 2 dropdown now populated from `dim_play_detail_2` table
- Both dropdowns show all available options regardless of selection in other dropdown

**Team Branding:**
- Team logos now display in team headers (loaded from `dim_team.team_logo`)
- Logo images auto-hide if URL fails to load
- Team colors applied via CSS variables `--home` and `--away`

**SOG Calculation:**
- SOG now correctly counts only shots that reached the net:
  - `Shot_OnNetSaved` (goalie saved)
  - `Shot_OnNetGoal` (redirected in)
  - `Goal_Scored`, `Goal_Shootout`, `Goal_PenaltyShot`

**Notes on Assists:**
- Assists in box score come from `fact_gameroster.assist` (official data)
- Tracking data doesn't have "AssistPrimary/Secondary" in play_detail columns
- To get accurate assists in tracker, they need to be manually entered

---

## v15.02 - January 8, 2026

### BenchSight Tracker v15 - Play Details, SOG, and Team Data Fixes

**Play Detail Fixes:**
- Play Detail 1 dropdown now uses **dim_play_detail** table (was using hardcoded LISTS)
- Play Detail 2 dropdown now uses **dim_play_detail_2** table
- Edit modal already was using these tables, now consistent throughout

**SOG (Shots on Goal) Calculation Fix:**
- SOG now only counts shots that reached the net:
  - `Shot_OnNetSaved` (goalie saved it)
  - `Shot_OnNetGoal` (redirected in)
  - `Goal_Scored` / `Goal_Shootout` / `Goal_PenaltyShot` (it went in)
- Previously was counting ALL shots including missed and blocked (incorrect)

**Team Data Fixes:**
- Team colors loaded from `dim_team.team_color1` 
- Team logos loaded from `dim_team.team_logo`
- Teams data cached on startup for faster game switching
- CSS variables `--home` and `--away` updated with team colors

**Notes:**
- `side_of_puck` in fact_event_players is **EXPLICIT**, not calculated (values: Offensive, Defensive, event_team, opp_team)
- Video integration is on the roadmap but not implemented in this version

---

## v15.01 - January 8, 2026

### BenchSight Tracker v15 - Team and Data Mapping Fixes

**Critical Bug Fixes:**
- **Team roster loading** - Fixed case-insensitive check for team_venue ('Home' vs 'home')
- **play_detail1 column mapping** - Now checks `play_detail1` first (no underscore before 1), fixing issue where player 8's 'Delay' showed in wrong column
- **Event log headers** - Column headers now match body columns (was showing misaligned data)
- **Event edit modal** - Now shows event_id and event_index for debugging

**Data Preservation:**
- `side_of_puck` from fact_event_players now preserved when loading events (explicit values: Offensive/Defensive/event_team/opp_team)
- `team_venue` from fact_event_players preserved for each player

**Notes on side_of_puck:**
- Values are explicit in the data (not calculated)
- Values: Offensive, Defensive, event_team, opp_team

---

## v15.00 - January 8, 2026

### BenchSight Tracker v15 - Critical Team Loading Fixes

**Critical Bug Fixes:**
- **Team labels now update when loading existing tracked games** - Previously, confirmLoadGame() set S.homeTeam/S.awayTeam but never updated the DOM labels (homeLbl, awayLbl, evtHomeLbl, evtAwayLbl), causing wrong team names to display
- **Event team determination fixed** - Now uses `player_team` from fact_event_players compared to `home_team`, instead of unreliable `team_venue` column from fact_events (which was 'Away' for all events)

**Box Score Fixes (from v14.22):**
- Now ONLY counts event_player_1 for goals/shots (fixed overcounting)
- Organized by team (HOME section → AWAY section)
- FO logic fixed: event_player_1 = WIN, opp_player_1 = LOSS
- Assists detected by '%assist%' in play_detail1 OR play_detail2
- FO column shows W/Total format (e.g., "3/5")

**Verification Panel Fixes (from v14.22):**
- Purple circle auto-populates from dim_schedule (read-only)
- Scorer # and Assist # shown in goal breakdown
- Period goals verified vs dim_schedule (P1/P2/P3)
- Roster G/A warnings when fact_gameroster doesn't match tracked events

---

## v14.22 - January 8, 2026

### BenchSight Tracker v7 - Box Score & Verification Fixes

**Critical Box Score Fixes:**
- Fixed stats counting - now ONLY counts event_player_1 for goals/shots (was counting all players in event)
- Box score now organized by team (HOME section, AWAY section) instead of mixed list
- Fixed FO win/loss logic:
  - event_player_1 on Faceoff = FO WIN (event team won)
  - opp_player_1 on Faceoff = FO LOSS (event team won, so opponent lost)
- Fixed assists - now detected by '%assist%' in play_detail1 OR play_detail2
- FO column now shows W/Total (e.g., "3/5") instead of percentage

**Verification Panel Fixes:**
- Purple circle (official score) now auto-populated from dim_schedule - NOT manual entry
- Blue circle shows scorer # and assist # in goal breakdown table
- Goals verified by period (P1/P2/P3) against dim_schedule period goals
- Roster verification checks fact_gameroster G/A columns against tracked events
- Warning popup if goal scorer/assister doesn't have G/A in gameroster

**UI Improvements:**
- Fixed noradhockey.com link format (now uses /event/{gameId}/)
- Time nudge ± seconds now uses variable amount from input (was fixed at 5)

**Documentation:**
- Backlogged all Tracker v5 and v6 changes to CHANGELOG
- Updated all docs timestamps

---

## v14.21 - January 8, 2026

### BenchSight Tracker v6 - Major Enhancements

**Critical Bug Fixes:**
- Fixed team loading from fact_events (case-insensitive check for 'home'/'Home'/'h')
- Fixed shift start/stop type defaulting to "On The Fly" instead of null
- Fixed box score stats - now only counts event_player_1 for goals/shots/FO

**Line Presets (NEW):**
- Save F-lines (F1, F2, F3) and D-pairs (D1, D2) per team
- Quick-load buttons in shift panel
- W = cycle forward presets, Shift+W = cycle defense presets
- Presets stored in localStorage

**Period Filtering (NEW):**
- P1/P2/P3/OT/ALL tabs in both event log and shift log
- Filter to view events/shifts from specific periods
- Increased log visibility: 50 items (up from 15) with scrolling

**Player Selection Hotkeys (NEW):**
- 1-6 = Select event player 1-6 for XY/details
- Ctrl+1-6 = Select opponent player 1-6
- Removed 1-3 period hotkeys (use buttons instead)

**Quick Line Change (NEW):**
- Press Q to end current shift and start new one in single action

**Time Nudge Buttons (NEW):**
- Variable +/- seconds (configurable 1-60s)
- -S/+S = nudge start time
- -E/+E = nudge end time

**Compact Mode (NEW):**
- Toggle ⊟ button to reduce UI padding/sizes
- Better for smaller screens

**Box Score Improvements:**
- Stats now organized by team (Home section, Away section)
- Fixed FO win/loss counting:
  - event_player_1 on FO = FO taken, win if success=s
  - opp_player_1 on FO = opposing center, inverse result
- Assists now detected by '%assist%' in play_detail1 or play_detail2

**Enhanced Verification Modal:**
- Official score auto-populated from dim_schedule (purple section, read-only)
- Period breakdowns shown (P1/P2/P3 goals for both tracked and official)
- Goal breakdown shows scorer # and assist # (from %assist% in play_details)
- Roster verification: warns if scorer/assister not in fact_gameroster with G/A
- Warnings section for period mismatches and roster discrepancies

**Updated Hotkey Reference:**
| Key | Action |
|-----|--------|
| 1-6 | Select Event Player 1-6 |
| Ctrl+1-6 | Select Opp Player 1-6 |
| Q | Quick Line Change |
| W | Cycle Forward presets |
| Shift+W | Cycle Defense presets |

---

## v14.20 - January 8, 2026

### Major Edit Modal Improvements

**Play Details from Supabase:**
- Play Details 1 & 2 dropdowns now load from `dim_play_detail` (138 options) and `dim_play_detail_2` (72 options)
- Player roles load from `dim_player_role` (14 options)
- Reference data loads automatically on Supabase connect

**Enhanced Event Edit Modal:**
- NEW: Player role dropdown (Event P1-6, Opp P1-6, Goalies)
- NEW: Two play detail dropdowns per player (Play D1, Play D2)
- NEW: Editable Linked Event # field
- NEW: Sequence Key and Play Key display
- NEW: Navigation arrows (← Prev / Next →) to move between events
- Each player row shows: #num Name | Role | Play D1 | Play D2 | Success | ✕

**Enhanced Shift Edit Modal:**
- NEW: Navigation arrows (← Prev / Next →) to move between shifts  
- NEW: Full player editing with dropdowns grouped by position
- NEW: Forwards (F1, F2, F3), Defense (D1, D2), Goalie/Extra (G, X)
- NEW: Strength auto-calculates from player counts

**Improved Event Log (Bottom):**
- New columns: Seq | Link | Tm | Type | Detail | Z | ✓ | EvtP | OppP | PD1 | S | XY | HL
- Hover tooltips show full event details
- Shows event players and opponent players separately

**Clear Functions:**
- NEW: Clear All Events button
- NEW: Clear All Shifts button

**Bug Fixes:**
- Fixed shift log to ascending order (oldest → newest)
- Fixed shift player positions (were all showing as forwards)

---

## v14.19 - January 8, 2026

### Tracker UI Improvements

**Edit Event Modal Updates:**
- Navigation arrows to move between events
- Linked Event # now editable
- Sequence Key and Play Key displayed
- Player role selection per player

**Edit Shift Modal Updates:**
- Navigation arrows to move between shifts
- Full player editing with dropdowns
- Grouped by position: Forwards, Defense, Goalie

---

## v14.15 - January 8, 2026

### Tracker Shift and Event Enhancements

**Shift Editing:**
- Click any shift in log to edit
- All player positions editable via dropdowns
- Strength auto-derives from player counts

**Event Log Improvements:**
- More columns visible (seq, link, team, players)
- Better hover tooltips
- Ascending order option

---

## v14.10 - January 8, 2026

### Tracker Data Loading Fixes

**Load Game Improvements:**
- Fixed play details not populating from loaded data
- Fixed event_detail_2 not loading
- Reference data loads from Supabase on connect

**New State Variables:**
- `S.playDetails1` - dim_play_detail data
- `S.playDetails2` - dim_play_detail_2 data  
- `S.playerRoles` - dim_player_role data

---

## v14.05 - January 7, 2026

### Tracker Workflow Improvements

**Keyboard Shortcuts:**
- ← → Arrow keys navigate events/shifts in edit modals
- 1/2/3/4 - Period selection
- F/G/T/X/O/V/R/D/Y - Event type hotkeys
- Enter - Log event
- L - Log shift
- E - Edit last event
- W - Edit last shift
- Tab - Toggle team
- Q - Toggle XY mode

**UI Improvements:**
- Shift log shows in ascending order
- More info in event log rows
- Better tooltips with full event details

---

## v14.01 - January 7, 2026

### Tracker v3 Complete Delivery

**New Features:**
- Tracker v3 at `ui/tracker/index.html`
- Complete ETL-aligned export format (LONG format)
- Cascading dropdowns from Lists tab
- XY tracking: 10 points per player, 10 per puck per event
- Per-player play details with s/u logic
- Auto zone calculation from event_player_1 XY
- Intermission handling with duration for video sync
- Full shift tracking with start/stop types
- Event/shift editing with all fields
- Keyboard shortcuts for all actions

**Documentation:**
- `docs/TRACKER_ETL_SPECIFICATION.md` - Export format
- `docs/TRACKER_V3_SPECIFICATION.md` - Feature spec
- `docs/html/tracker/index.html` - Documentation portal

---

## v13.17 - January 7, 2026

### Documentation Registry System

**Created `config/DOC_REGISTRY.json`** - central index tracking:
- Tables (auto-discovered from data/output/*.csv)
- Scripts (auto-discovered from scripts/**/*.py)
- Config files (auto-discovered from config/*.json)
- Features (from changelog)

**Created `scripts/utilities/doc_registry.py`** with commands:
```bash
--audit      # Check documentation completeness
--discover   # Find new undocumented items
--changelog  # Check changelog vs documentation
--update     # Update registry with discoveries
--report     # Generate full status report
```

**Integrated into pre_delivery.py Phase 8**

---

## v13.15 - January 7, 2026

### Metadata Completeness Verification

- New `--metadata` flag for doc_sync.py
- Integrated into pre_delivery.py Phase 8
- Added Tier 2 tests for metadata completeness
- Checks for tables without metadata, incomplete metadata, orphan metadata

---

## v13.13 - January 7, 2026

### Rich Documentation Format

**Fixed HTML table documentation with:**
- Table Overview: Description, Purpose, Source Module, Logic, Grain
- Column Documentation: Name, Type, Description, Context, Calculation, Type badge, Non-Null, Null %
- Color-coded badges and null percentage highlighting

**Created `docs/roles/` with guides:**
- `ETL_ENGINEER.md` - Build new tables, fix transformations
- `TRACKER.md` - Build event tracking UI
- `FRONTEND.md` - React components, Supabase integration
- `PM.md` - Project coordination, status tracking

---

## v13.12 - January 7, 2026

### Rich Documentation + Supabase Integration

**Documentation:**
- Created `config/TABLE_METADATA.json` with rich metadata
- Data dictionary includes critical rules, stat formulas
- HTML table pages show descriptions, sources, relationships

**Supabase Integration:**
- `supabase/schema.sql` - Complete PostgreSQL DDL
- `supabase/sync_to_supabase.py` - Sync CSV to Supabase
- `supabase/generate_schema.py` - Regenerate schema
- Useful views: v_goals, v_player_game_summary, v_game_summary

---

## v13.10 - January 7, 2026

### Automatic Documentation Sync System

**New: `scripts/utilities/doc_sync.py`**

Syncs automatically:
- Table counts (total, dim, fact, qa)
- Goal counts (total and per game)
- Test counts (tier 1 and tier 2)
- Version numbers

**Fixed:** 107 hardcoded values across 21 files

---

## v13.07 - January 7, 2026

### Complete Safeguard System

**Tiered Test System:**
- `tests/test_tier1_blocking.py` - 32 tests that MUST pass
- `tests/test_tier2_warning.py` - 17 tests (warnings only)
- `tests/test_tier3_future.py` - Skipped tests

**Schema Snapshot System:**
- `scripts/utilities/schema_snapshot.py` - Tracks columns
- `config/SCHEMA_SNAPSHOT.json` - Auto-generated
- Detects removed/added columns

**Input Validation:**
- `scripts/utilities/validate_input.py` - Validates Excel files

---

## v13.05 - January 7, 2026

### Complete BS-Proof Delivery System

**Master Pipeline: `scripts/pre_delivery.py`**
- Single command for all deliveries
- Runs fresh ETL from scratch
- Verifies against IMMUTABLE_FACTS.json
- Auto-bumps version and fixes docs

**New Config Files:**
- `config/IMMUTABLE_FACTS.json` - Human-verified goals
- `config/GROUND_TRUTH.json` - Auto-computed from ETL
- `config/FILE_SIZES.json` - Truncation detection

---

## v9.01 - January 7, 2026

### ETL Orchestrator

- ETL Orchestrator (`src/etl_orchestrator.py`) - Unified entry point
- `run_full()`, `run_incremental()`, `run_selective()` methods
- CLI: `python -m src.etl_orchestrator [status|full|incremental|reset]`

---

## v6.5 - January 6, 2026

### Rating-Adjusted Analytics

- Player season stats with 116 columns
- Rating-adjusted goals, Corsi, expected performance
- Competition tier analysis (CT01-CT04)
- 3 new analytics tables

---

## v6.4 - January 5, 2026

### Major Fixes

- Fixed dim_schedule period_length corruption
- Fixed dim_season CSAHA removal
- Complete rewrite of fact_shift_quality
- ID format standardization (venue, zone)
- Hockey countdown clock fix in dim_time_bucket

---

## v6.2 - January 5, 2026

### Code Standardization

- All hyphens/slashes → underscores in dimension codes
- dim_event_detail consolidated from 59 to 46 rows
- Period dimension updates (P01, P02, P03 format)

---

## v6.1 - January 5, 2026

### Data Quality Fixes

- Fixed Game 18977 goal count
- Fixed team code swap
- Standardized team names
- Removed CSAHA teams and columns

---

## v6.0 - December 30, 2025

### Initial Release

- 111-table dimensional data warehouse
- 317 player statistics metrics
- 4 tracked games (18969, 18977, 18981, 18987)
- Supabase deployment ready
- Goal counts verified: 18969(7), 18977(6), 18981(3), 18987(1) = 17 total

---

## Version Naming Convention

Format: `benchsight_v{CHAT}.{OUTPUT}`
- Chat increments each new Claude session
- Output increments within same session
- Example: v14.20 = Chat 14, Output 20
