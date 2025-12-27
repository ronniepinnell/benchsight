# 🏒 BenchSight Hockey Analytics
## Complete Project Status & Implementation Plan
### December 26, 2025

---

## 📋 Executive Summary

BenchSight is an end-to-end hockey analytics platform combining:
- **Manual tracking data** (events, shifts, XY coordinates, video timestamps)
- **League box scores** from NORAD website (goals, assists, PIM, standings)
- **Power BI** and **web dashboards** for visualization

### Current State at a Glance

| Component | Status | Notes |
|-----------|--------|-------|
| **Tracked Games** | ✅ 9 games | 11,167 events, 770 shifts |
| **Video Links** | ✅ 7/9 games | YouTube integration ready |
| **BLB Master Data** | ✅ Complete | 14 tables, 335 players, 17 teams |
| **Tracker HTML** | ⚠️ Partial | Excel import has bugs |
| **Dashboard HTML** | ⚠️ Needs rebuild | Data loading issues |
| **ETL Pipeline** | ⚠️ Partial | Python code exists, not tested |
| **Power BI** | 📝 Designed | Schema ready, not connected |

---

## 🎯 YOUR TOP PRIORITIES (Per Your Request)

1. **🔥 P0: Game data loaded into dashboards**
   - Dashboard must read tracking Excel/JSON and display events/shifts/video
   
2. **🔥 P0: Perfect the Tracker**
   - Fix Excel import error
   - Ensure data saves correctly
   - Polish UI
   
3. **🔥 P0: Basic ETL working**
   - Python pipeline: read tracking → transform → output JSON
   
4. **🔥 P0: Videos linked to plays/shifts**
   - Click event → opens YouTube at correct timestamp
   
5. **📌 P1: Hosted on Wix**
   - Static HTML files for Wix embedding

---

## 📦 Data Inventory

### BLB_Tables.xlsx (Master Dimensions)

| Table | Rows | Key Fields |
|-------|------|------------|
| dim_player | 335 | player_id, player_full_name, current_skill_rating, player_norad_current_team, player_image |
| dim_team | 26 | team_id, team_name, team_color1, team_color2 |
| dim_schedule | 552 | game_id, date, home_team_name, away_team_name |
| fact_gameroster | 14,239 | game_id, player_id, goals, assist, pim |
| dim_season | 9 | season_id, season, start_date |
| fact_leadership | 28 | player_id, leadership, team_name |
| fact_draft | 160 | player_id, round, overall_draft_position |
| dim_rinkcoordzones | 297 | zone_id, danger (for XY classification) |
| dim_rinkboxcoord | 50 | Net grid for shot location |

### Tracked Games (data.zip)

| Game ID | Home Team | Away Team | Events | Shifts | Video |
|---------|-----------|-----------|--------|--------|-------|
| 18969 | Platinum | Velodrome | 3,141 | 98 | ✅ |
| 18977 | Velodrome | HollowBrook | 2,527 | 88 | ✅ |
| 18981 | Nelson | Velodrome | 2,425 | 106 | ✅ |
| 18987 | Velodrome | Outlaws | 3,064 | 106 | ✅ |
| 18965 | OS Offices | Velodrome | 2 | 98 | ❌ |
| 18991 | Triple J | Velodrome | 3 | 78 | ✅ |
| 18993 | Platinum | Velodrome | 2 | 98 | ❌ |
| 19032 | Outcan | Velodrome | 3 | 98 | ✅ |
| 18955 | Velodrome | Orphans | 0 | 0 | ✅ |

**Totals: 11,167 events | 770 shifts | 7 games with video**

### Free Agents / Subs
Players with `player_norad_current_team = 'Free Agent'` in dim_player are substitutes.
- Example: **Francis Forte** (P100202) is a Free Agent who subs into games

---

## 🏗️ Data Architecture

### Data Source Strategy

**MACRO Stats (from NORAD/BLB_Tables):**
- Goals, Assists, Points, PIM, Games Played
- Standings, Schedule, Team rosters
- Player ratings (2-6 scale), positions, images

**MICRO/Advanced Stats (from Tracking Data):**
- Corsi, Fenwick, Zone entries/exits
- Time on Ice (detailed), Shift-level analytics
- XY coordinates, Play sequences, Video timestamps
- Takeaways, Giveaways, Passes, Possession time

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES (RAW)                       │
├─────────────────────────────────────────────────────────────┤
│  BLB_Tables.xlsx  │  Game Tracking    │   NORAD Website     │
│  (Master dims)    │  (events/shifts)  │   (Box scores)      │
└─────────┬─────────┴─────────┬─────────┴─────────┬───────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                 ETL PIPELINE (Python)                       │
│  extract.py → transform.py → load.py → orchestrator.py     │
└─────────────────────────────┬───────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 DATAMART (JSON/CSV/PostgreSQL)              │
│  fact_events_long │ fact_shifts_long │ fact_player_boxscore │
└─────────┬─────────────────┬─────────────────┬───────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│   Dashboard     │ │    Tracker      │ │      Power BI       │
│   (HTML/JS)     │ │    (HTML/JS)    │ │    (DAX/Visuals)    │
└─────────────────┘ └─────────────────┘ └─────────────────────┘
```

---

## 📊 Stats Catalog Summary

### Basic Stats (from NORAD/Box Score)

| Stat ID | Name | Description |
|---------|------|-------------|
| BS01 | Goals | Non-empty-net goals scored |
| BS02 | Assists | Primary + Secondary assists |
| BS03 | Points | Goals + Assists |
| BS04 | Shots on Goal | Goals + Saved shots |
| BS07 | Plus-Minus | EV goals for minus against while on ice |
| BS08 | TOI (Seconds) | Time on ice from shift data |

### Advanced/On-Ice Stats (from Tracking)

| Stat ID | Name | Description |
|---------|------|-------------|
| BS05 | Corsi For | Shot attempts for while on ice |
| BS06 | Fenwick For | Unblocked shot attempts while on ice |
| BS11 | CF% | Corsi For / (CF + CA) |
| BS13 | xG | Expected goals from shot location/type |
| BS16 | Zone Entry Rate | Carry-in vs dump-in success |
| BS24 | Giveaways | Turnovers (excl. dumps/clears) |
| BS25 | Takeaways | Puck stolen from opponent |

**Full catalog: 60+ metrics defined with formulas**

---

## 📅 Implementation Timeline

### Phase 1: Core Fixes (This Week)

| Task | Effort | Priority | Status |
|------|--------|----------|--------|
| Fix Tracker Excel import error | Medium | P0 | TODO |
| Dashboard loads tracking data from JSON | Medium | P0 | TODO |
| Video links work (click → YouTube) | Low | P0 | Partial |
| All 9 games selectable in dashboard | Low | P0 | TODO |
| Events/Shifts display correctly | Medium | P0 | TODO |
| Player stats from fact_gameroster | Low | P1 | TODO |

### Phase 2: ETL & Integration (Week 2)

| Task | Effort | Priority | Status |
|------|--------|----------|--------|
| ETL reads all 9 game folders | Medium | P1 | Partial |
| Transform to fact_events_long format | High | P1 | Partial |
| Transform to fact_shifts_long format | Medium | P1 | Partial |
| Generate JSON for dashboard | Low | P1 | TODO |
| Video timestamps joined to events | Medium | P1 | Partial |
| Player boxscore aggregation | Medium | P2 | TODO |

### Phase 3: Polish & Deploy (Week 3)

| Task | Effort | Priority | Status |
|------|--------|----------|--------|
| Wix hosting setup | Low | P1 | TODO |
| Team pages with NORAD colors | Low | P2 | Partial |
| Player pages with images + stats | Medium | P2 | Partial |
| Admin portal features | Medium | P2 | Partial |
| Free Agent handling in rosters | Low | P2 | TODO |
| Documentation finalized | Medium | P2 | In Progress |

---

## 📁 Tracking File Format

Each game folder (e.g., `18969/`) contains:

### {game_id}_tracking.xlsx
- **events** sheet: 72 columns
  - event_type, event_detail, player_game_number
  - timestamps, zone info, play details
- **shifts** sheet: 55 columns
  - home/away players by position (F1, F2, F3, D1, D2, G)
  - strength, zone starts, duration
- **game_rosters** sheet: Player roster with jersey numbers
- **Lists/Rules** sheets: Dropdown values and definitions

### {game_id}_video_times.xlsx
- **video** sheet: Url_1 (YouTube), Video_Type, Game_ID
- Used to link events/shifts via `running_video_time` column

---

## ✅ Strengths of Current Design

1. Comprehensive stats catalog with 60+ metrics well-defined
2. Clear separation of macro (NORAD) vs micro (tracking) data
3. Robust BLB_Tables with proper dimension/fact structure
4. Video integration concept is solid (running_video_time → YouTube)
5. XY coordinate tracking ready for future heatmaps/xG
6. Rating system (2-6 scale) enables quality-adjusted stats

## ⚠️ Areas to Improve

1. Tracker Excel import needs robust error handling
2. Dashboard and Tracker should share data layer
3. No automated refresh mechanism
4. Free Agent handling needs explicit logic
5. Some tracked games have minimal events (quality varies)

---

## 🚀 Immediate Next Steps

1. **Fix Tracker Excel Import** - Debug column mapping, add error messages
2. **Create data.json** - Run ETL to generate consolidated JSON
3. **Rebuild Dashboard** - Single HTML that loads data.json properly
4. **Test Video Links** - Verify click → YouTube timestamp works
5. **Deploy to Wix** - Upload static HTML/JS/CSS files

---

## 📚 Appendix: NORAD Teams

| Team ID | Team Name | Abbrev | Primary Color |
|---------|-----------|--------|---------------|
| N10001 | Amos | AMO | #FF6B6B |
| N10002 | Ace | ACE | #4ECDC4 |
| N10003 | HollowBrook | HBK | #2ECC71 |
| N10004 | Nelson | NEL | #3498DB |
| N10005 | OS Offices | OSO | #9B59B6 |
| N10006 | Orphans | ORP | #E74C3C |
| N10007 | Outlaws | OUT | #F39C12 |
| N10008 | Platinum | PLT | #95A5A6 |
| N10009 | Triple J | TRJ | #1ABC9C |
| N10010 | Velodrome | VEL | #E91E63 |

---

## 📂 Recommended File Structure

```
benchsight/
├── data/
│   ├── raw/games/{game_id}/        # Tracking Excel files
│   ├── raw/master/BLB_Tables.xlsx  # Master dimensions
│   └── processed/                   # ETL outputs (CSV/JSON)
├── frontend/
│   ├── index.html                   # Main dashboard
│   └── tracker.html                 # Event tracker
├── backend/etl/
│   ├── extract.py                   # Read raw files
│   ├── transform.py                 # Process to mart format
│   └── orchestrator.py              # Run pipeline
└── docs/                            # This documentation
```
