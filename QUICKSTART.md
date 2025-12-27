# 🏒 BENCHSIGHT QUICKSTART GUIDE

## Overview

BenchSight is a hockey analytics platform with three main components:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BENCHSIGHT SYSTEM                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐ │
│   │  DATA SOURCE │    │     ETL      │    │      OUTPUTS         │ │
│   │              │───▶│   PIPELINE   │───▶│                      │ │
│   │ BLB_Tables   │    │  (Python)    │    │ • 47 CSV files       │ │
│   │   .xlsx      │    │              │    │ • games_config.json  │ │
│   │              │    │ orchestrator │    │ • roster.json files  │ │
│   └──────────────┘    │     .py      │    └──────────────────────┘ │
│                       └──────────────┘                              │
│          │                                         │                │
│          ▼                                         ▼                │
│   ┌──────────────┐                    ┌──────────────────────────┐ │
│   │   TRACKER    │                    │      DASHBOARDS          │ │
│   │              │                    │                          │ │
│   │ tracker_v18  │─────exports───────▶│ • dashboard_static.html  │ │
│   │    .html     │   *_tracking.xlsx  │ • games_browser.html     │ │
│   │              │                    │ • standings.html         │ │
│   │ (standalone) │                    │ • team_profile.html      │ │
│   └──────────────┘                    │ • player_comparison.html │ │
│                                       │ • game_summary.html      │ │
│                                       └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (No Python Required)

### Option 1: Just Use the Tracker
1. Open `html/tracker_v18.html` in your browser
2. Select a game from dropdown (8 tracked games embedded)
3. Click "+ New" to pick any game from 552 BLB schedule games
4. Start tracking events and shifts

### Option 2: View Dashboards
Open any HTML file in the `html/` folder directly in your browser:
- `dashboard_static.html` - League leaderboards
- `games_browser.html` - All 552 games
- `standings.html` - Team standings
- `tracker_v18.html` - Game event tracker

---

## 🔧 Full Setup (With Python)

### 1. Install Dependencies
```bash
pip install pandas openpyxl flask
```

### 2. Run the Orchestrator (Main UI)
```bash
cd benchsight_merged
python orchestrator.py
```
Opens http://localhost:5001 with web UI for:
- Viewing BLB_Tables status
- Listing all games
- Extracting rosters
- Running data export
- Opening tracker

### 3. Export Data to CSV
```bash
python export_all_data.py
```
Creates 47 CSV files in `data/output/`

### 4. Generate Game Configs
```bash
python src/roster_loader.py
```
Creates `games_config.json` and roster files

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `data/BLB_Tables.xlsx` | Master data (552 games, 335 players, 14K roster entries) |
| `html/tracker_v18.html` | Game tracker (standalone, no server needed) |
| `data/output/games_config.json` | Tracked game configurations |
| `data/raw/games/{gid}/` | Game folders with tracking Excel files |
| `orchestrator.py` | Web UI for all operations |

---

## 🎮 Tracker Workflow

1. **Open tracker** - `html/tracker_v18.html`
2. **Select game** - Pick from 8 tracked games OR create new from 552 schedule games
3. **Load existing data** - Tracker auto-imports from `{gid}_tracking.xlsx` if exists
4. **Track events** - Click event buttons or use keyboard shortcuts
5. **Track shifts** - Assign players to positions (F1, F2, F3, D1, D2, G)
6. **Export** - Click 📥 to download Excel with events + shifts sheets
7. **Save** - Files go to `data/raw/games/{gid}/`

### Keyboard Shortcuts
- `S` = Shot, `G` = Goal, `P` = Pass
- `T` = Turnover, `F` = Faceoff
- `1/2/3` = Period, `Space` = Confirm
- `Z` = Undo last event

---

## 🌐 GitHub Pages Deployment

1. Push to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/benchsight.git
git push -u origin main
```

2. Enable GitHub Pages (Settings → Pages → main branch)

3. Access at: `https://YOUR_USERNAME.github.io/benchsight/html/`

### Wix Embedding
```html
<iframe src="https://YOUR_USERNAME.github.io/benchsight/html/dashboard_static.html" 
        width="100%" height="800px" frameborder="0"></iframe>
```

---

## 📊 Data Summary

| Category | Count |
|----------|-------|
| Total games | 552 |
| Tracked games | 8 |
| Total events | 24,089 |
| Total shifts | 770 |
| Players | 335 |
| Teams | 26 |
| CSV outputs | 47 |

---

## 🔄 Typical Workflow

```
1. Update BLB_Tables.xlsx with new game data
         │
         ▼
2. Run: python src/roster_loader.py
   (generates games_config.json + roster files)
         │
         ▼
3. Open tracker_v18.html
   Select new game from schedule picker
         │
         ▼
4. Track events during game
   Export to {gid}_tracking.xlsx
         │
         ▼
5. Run: python export_all_data.py
   (generates updated CSV files)
         │
         ▼
6. Push to GitHub for dashboard updates
```

---

## ❓ Troubleshooting

**Tracker shows no games?**
- Use `tracker_v18.html` (not v17) - data is embedded, no fetch needed

**Player names showing "Unknown"?**
- Run `python src/roster_loader.py` to regenerate configs from BLB_Tables

**Dashboards not updating?**
- Run `python export_all_data.py` to refresh CSV files
- Clear browser cache

**Need more games in tracker?**
- Click "+ New" and pick from 552 BLB schedule games

---

*Last Updated: December 27, 2025 | Version 1.4.0*
