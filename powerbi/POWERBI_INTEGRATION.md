# 📊 POWER BI INTEGRATION GUIDE
## Connecting BenchSight to Power BI

---

## 🔌 CONNECTION OPTIONS

### Option 1: CSV Files (Recommended for Starting)
1. Open Power BI Desktop
2. Click **Get Data** → **Text/CSV**
3. Navigate to `benchsight_merged/data/output/`
4. Select CSV files to import

**Key files to import:**
```
dim_player.csv          - Player dimension
dim_team.csv            - Team dimension  
dim_schedule.csv        - Game schedule with scores
fact_events.csv         - All tracked events
fact_shifts.csv         - Shift data
fact_gameroster.csv     - Player stats per game
fact_box_score.csv      - Game summaries
```

### Option 2: PostgreSQL (Production)
1. Click **Get Data** → **PostgreSQL database**
2. Enter connection details:
   - Server: `localhost` (or your server)
   - Database: `benchsight`
   - Username: `postgres`
3. Select tables from `hockey_mart` schema

### Option 3: Excel Files
1. Click **Get Data** → **Excel**
2. Import `data/output/hockey_datamart.xlsx`

---

## 🔗 DATA MODEL RELATIONSHIPS

Create these relationships in Power BI:

```
fact_events[player_id] → dim_player[player_id]
fact_events[team_id] → dim_team[team_id]
fact_events[game_id] → dim_schedule[game_id]
fact_shifts[player_id] → dim_player[player_id]
fact_shifts[game_id] → dim_schedule[game_id]
fact_gameroster[player_id] → dim_player[player_id]
fact_gameroster[game_id] → dim_schedule[game_id]
```

---

## 📐 DAX MEASURES

### Basic Counting
```dax
// Total Goals
Total Goals = CALCULATE(
    COUNTROWS(fact_events),
    fact_events[event_type] = "goal"
)

// Total Shots
Total Shots = CALCULATE(
    COUNTROWS(fact_events),
    fact_events[event_type] IN {"shot", "goal"}
)

// Total Assists
Total Assists = CALCULATE(
    COUNTROWS(fact_events),
    fact_events[event_type] = "goal",
    NOT(ISBLANK(fact_events[secondary_player_id]))
)

// Games Played
Games Played = DISTINCTCOUNT(fact_events[game_id])
```

### Per Game Stats
```dax
// Goals Per Game
Goals Per Game = DIVIDE([Total Goals], [Games Played], 0)

// Points Per Game
Points Per Game = DIVIDE([Total Goals] + [Total Assists], [Games Played], 0)

// Shots Per Game
Shots Per Game = DIVIDE([Total Shots], [Games Played], 0)
```

### Shooting Stats
```dax
// Shooting Percentage
Shooting % = DIVIDE([Total Goals], [Total Shots], 0) * 100

// Shot Attempts (Corsi For)
Corsi For = CALCULATE(
    COUNTROWS(fact_events),
    fact_events[event_type] IN {"shot", "goal", "block", "miss"}
)

// Corsi %
Corsi % = DIVIDE(
    [Corsi For],
    [Corsi For] + [Corsi Against],
    0.5
) * 100
```

### Advanced Metrics
```dax
// Fenwick For (unblocked shot attempts)
Fenwick For = CALCULATE(
    COUNTROWS(fact_events),
    fact_events[event_type] IN {"shot", "goal", "miss"}
)

// Fenwick %
Fenwick % = DIVIDE(
    [Fenwick For],
    [Fenwick For] + [Fenwick Against],
    0.5
) * 100

// PDO (Shooting% + Save%)
PDO = [Shooting %] + [Save %]

// Expected Goals (simplified)
xG = SUMX(
    fact_events,
    SWITCH(
        fact_events[shot_type],
        "wrist", 0.08,
        "slap", 0.06,
        "snap", 0.07,
        "backhand", 0.05,
        "tip", 0.12,
        "wrap", 0.03,
        0.05
    )
)
```

### Zone Stats
```dax
// Offensive Zone Entries
OZ Entries = CALCULATE(
    COUNTROWS(fact_events),
    fact_events[event_type] = "zone_entry",
    fact_events[zone] = "OZ"
)

// Controlled Entry %
Controlled Entry % = DIVIDE(
    CALCULATE(COUNTROWS(fact_events), fact_events[entry_type] = "carry"),
    [OZ Entries],
    0
) * 100

// High Danger Shots
High Danger Shots = CALCULATE(
    COUNTROWS(fact_events),
    fact_events[event_type] IN {"shot", "goal"},
    fact_events[danger_zone] = "high"
)
```

### Time-Based
```dax
// First Period Goals
P1 Goals = CALCULATE([Total Goals], fact_events[period] = 1)

// Power Play Goals
PP Goals = CALCULATE(
    [Total Goals],
    fact_events[strength] = "PP"
)

// Power Play %
PP % = DIVIDE([PP Goals], [PP Opportunities], 0) * 100
```

---

## 📊 SUGGESTED VISUALIZATIONS

### Player Dashboard
1. **Card visuals:** Goals, Assists, Points, +/-
2. **Bar chart:** Points by game
3. **Scatter plot:** Goals vs Assists
4. **Table:** Game log with stats

### Team Dashboard
1. **Card visuals:** Wins, Losses, Goal Diff
2. **Line chart:** Points over season
3. **Stacked bar:** Goals For vs Against by period
4. **Gauge:** Power Play %

### Game Summary
1. **Card visuals:** Final score
2. **Timeline:** Events by period
3. **Shot chart:** Shot locations (if coordinates available)
4. **Table:** Box score

### League Overview
1. **Table:** Standings with conditional formatting
2. **Bar chart:** Top scorers
3. **Pie chart:** Goals by team
4. **Map:** (if venue coordinates available)

---

## 🎨 THEME JSON

Save as `benchsight_theme.json`:
```json
{
  "name": "BenchSight NORAD",
  "dataColors": [
    "#00d4ff",
    "#00ff88",
    "#ff8800",
    "#ff4466",
    "#aa66ff",
    "#ffdd00"
  ],
  "background": "#0a0a0f",
  "foreground": "#e0e0e0",
  "tableAccent": "#00d4ff",
  "visualStyles": {
    "*": {
      "*": {
        "fontSize": {"solid": {"color": "#e0e0e0"}},
        "background": {"solid": {"color": "#12121a"}},
        "border": {"solid": {"color": "#2a2a3a"}}
      }
    }
  }
}
```

To apply: View → Themes → Browse for themes → Select file

---

## 📁 SAMPLE QUERIES

### Power Query M - Load All CSVs
```m
let
    Source = Folder.Files("C:\path\to\benchsight_merged\data\output"),
    FilterCSV = Table.SelectRows(Source, each [Extension] = ".csv"),
    AddContent = Table.AddColumn(FilterCSV, "Data", each Csv.Document([Content])),
    ExpandData = Table.ExpandTableColumn(AddContent, "Data", Table.ColumnNames(AddContent{0}[Data]))
in
    ExpandData
```

### Filter to Current Season
```m
let
    Source = Csv.Document(File.Contents("dim_schedule.csv")),
    Promoted = Table.PromoteHeaders(Source),
    FilterSeason = Table.SelectRows(Promoted, each [season] = "20252026")
in
    FilterSeason
```

---

## ✅ QUICK START CHECKLIST

1. [ ] Install Power BI Desktop
2. [ ] Export data: `python export_all_data.py`
3. [ ] Import CSV files into Power BI
4. [ ] Create relationships between tables
5. [ ] Add DAX measures
6. [ ] Build visualizations
7. [ ] Apply BenchSight theme
8. [ ] Publish to Power BI Service (optional)

---

## 🔄 REFRESH SCHEDULE

For automatic updates:
1. Publish to Power BI Service
2. Set up Gateway for local files
3. Configure scheduled refresh

Or use PostgreSQL for direct connection refresh.

---

*Last Updated: December 2025*
