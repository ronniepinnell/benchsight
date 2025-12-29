# BenchSight Master Checklist
## December 2025

---

## PHASE 0: TRACKER FIXES ✅ COMPLETE

### Tracker v16 Fixes
- [x] **T0.1** Fix column mapping in `importExcel()` for events sheet
- [x] **T0.2** Fix column mapping in `importExcel()` for shifts sheet
- [x] **T0.3** Add roster import from `game_rosters` sheet
- [x] **T0.4** Handle underscore-suffixed column names (e.g., `team_` vs `team`)
- [x] **T0.5** Map video timestamps (`running_video_time`) to events
- [x] **T0.6** Add error messages for missing required columns
- [x] **T0.7** Events/Shifts display in DESC order (newest first)
- [x] **T0.8** Add XY coordinates for all players (+XY button)
- [x] **T0.9** Increase visible events (50) and shifts (30)
- [x] **T0.10** Verify import works for all 9 games ✅ Tested
- [x] **T0.11** Add exportGameData() for admin portal integration

### Import Compatibility Verified
| Game | Status | Events | Shifts |
|------|--------|--------|--------|
| 18965 | ✅ | 3,999 | 98 |
| 18969 | ✅ | 3,596 | 98 |
| 18977 | ✅ | 2,527 | 88 |
| 18981 | ✅ | 2,428 | 106 |
| 18987 | ✅ | 3,084 | 106 |
| 18991 | ✅ | 4,000 | 78 |
| 18993 | ✅ | 456 | 98 |
| 19032 | ✅ | 3,999 | 98 |

---

## PHASE 1: ADMIN PORTAL MVP ✅ COMPLETE

### Core Features
- [x] **A1.1** Flask admin portal with NORAD dark theme
- [x] **A1.2** Main dashboard with system overview
- [x] **A1.3** BLB Tables upload and viewer
- [x] **A1.4** Tracker integration via iframe
- [x] **A1.5** ETL pipeline control panel
- [x] **A1.6** Notes/Request log page
- [x] **A1.7** Output file browser and download

### Workflow Integration
- [x] **A1.8** Tracker auto-save to localStorage (every 30s)
- [x] **A1.9** Save backup button (JSON export)
- [x] **A1.10** Publish to data folder button
- [ ] **A1.11** Load roster from BLB_Tables API (in progress)

---

## PHASE 2: ETL PIPELINE 🔄 IN PROGRESS

### Stage Layer
- [x] Load BLB_Tables.xlsx
- [x] Load tracking Excel files
- [ ] Load video_times.xlsx
- [ ] Load XY data from CSVs

### Intermediate Layer
- [x] Events long → wide transformation
- [x] Shifts wide → long transformation
- [ ] Event chains (linked, sequence, play)
- [ ] XY zone classification

### Datamart Layer
- [x] dim_player (335 records)
- [x] dim_team (26 records)
- [x] dim_schedule (552 records)
- [x] fact_events
- [x] fact_shifts
- [x] fact_box_score
- [ ] fact_event_players (with XY)
- [ ] fact_shift_players (with rating context)

---

## PHASE 3: DASHBOARD VIEWS 📋 PLANNED

### Game Summary View
- [ ] ESPN-style boxscore layout
- [ ] Period breakdown
- [ ] Shot charts
- [ ] Key plays timeline

### Player Cards
- [ ] Individual player stats
- [ ] Comparison to league averages
- [ ] Trend charts

### Line Combo Analysis
- [ ] Line/pair TOI matrix
- [ ] CF%/xGF% by combo
- [ ] WOWY analysis

---

## QUICK START

### Run Admin Portal
```bash
cd benchsight_merged
pip install flask pandas openpyxl
python admin_portal.py
# Open http://localhost:5000
```

### Workflow
1. **Upload BLB_Tables** → /blb
2. **Open Tracker** → /tracker → Load game → Track events/shifts
3. **Save Backup** → Creates JSON backup
4. **Publish to Data** → Copies to data/raw/games/{game_id}/
5. **Run ETL** → /etl → Process game data
6. **View Reports** → /reports → Download CSVs

---

## FILE LOCATIONS

| Component | Location |
|-----------|----------|
| Admin Portal | `admin_portal.py` |
| Tracker | `tracker/tracker_v16.html` |
| ETL Pipeline | `src/pipeline/` |
| Raw Game Data | `data/raw/games/{game_id}/` |
| Output CSVs | `data/output/*.csv` |
| Backups | `backups/` |
| Notes | `admin_notes.json` |
| Documentation | `docs/MASTER_DOCUMENTATION.md` |

---

*Last Updated: December 26, 2025*
