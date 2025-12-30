# BenchSight Dashboard Developer Handoff

## 🎯 Your Mission

Build interactive dashboards for BenchSight hockey analytics. Data is stored in Supabase PostgreSQL and ready for visualization. Your dashboards will serve players, coaches, and league administrators.

---

## 📖 Required Reading (In Order)

### 1. Start Here (This README)
You're reading it. Continue for architecture and data access.

### 2. Dashboard Developer Guide (`docs/DASHBOARD_DEV_COMPLETE_GUIDE.md`)
**CRITICAL** - 24KB comprehensive guide covering:
- Dashboard hierarchy (macro to micro)
- All dashboard specifications with mockups
- KPIs, visualizations, and layouts
- XY coordinate visualizations
- Data aggregation patterns

### 3. Schema & ERD (`docs/SCHEMA_AND_ERD.md`)
Understand the data model:
- Which tables to query for which dashboards
- Join relationships
- Primary/foreign keys

### 4. Data Dictionaries (`data_dictionary/`)
Column definitions for all tables:
- `dd_fact_player_game_stats.csv` - Player dashboard source
- `dd_fact_team_game_stats.csv` - Team dashboard source
- `dd_fact_goalie_game_stats.csv` - Goalie dashboard source
- `dd_fact_events.csv` - Event timeline source

### 5. Master Instructions (`docs/MASTER_INSTRUCTIONS.md`)
Business rules and stat definitions.

---

## 🔌 Supabase Connection

### Connection Details
```
Project URL: https://uuaowslhpgyiudmbvqze.supabase.co
API URL: https://uuaowslhpgyiudmbvqze.supabase.co/rest/v1/
```

### Getting API Keys
1. Go to Supabase Dashboard → Project Settings → API
2. Copy `anon` key for client-side access
3. Copy `service_role` key for server-side only (NEVER expose)

### JavaScript Client Setup
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://uuaowslhpgyiudmbvqze.supabase.co',
  'your-anon-key'
)
```

### Example Queries
```javascript
// Get league leaders (top 10 scorers)
const { data: leaders } = await supabase
  .from('fact_player_game_stats')
  .select('player_name, goals, assists, points')
  .order('points', { ascending: false })
  .limit(10)

// Get team stats for a game
const { data: teamStats } = await supabase
  .from('fact_team_game_stats')
  .select('*')
  .eq('game_id', 18969)

// Get player's game log
const { data: gameLog } = await supabase
  .from('fact_player_game_stats')
  .select('*, dim_schedule(game_date, home_team, away_team)')
  .eq('player_id', 'P100192')
  .order('game_id', { ascending: false })
```

---

## 📊 Dashboard Hierarchy

Build dashboards in this order (dependencies noted):

### Level 1: League Overview (No Dependencies)
- **Standings Table:** W-L-OTL-PTS by team
- **League Leaders:** Goals, Assists, Points, +/-
- **Quick Stats Cards:** Total games, goals, avg per game

### Level 2: Team Analytics (Needs Level 1)
- **Team Overview:** Record, GF/GA, PP%, PK%
- **Team Offense:** Shots, SOG, shooting%, zone entries
- **Team Defense:** Shots against, blocks, takeaways
- **Line Combinations:** Performance by line grouping

### Level 3: Player Analytics (Needs Level 1-2)
- **Player Card:** Photo, bio, season totals
- **Detailed Stats:** Per game, per 60, league rank
- **Game Log:** Game-by-game performance
- **Trends:** Rolling averages, charts

### Level 4: Game Analytics (Needs Level 1-3)
- **Game Summary:** Score, three stars, team comparison
- **Game Flow:** Cumulative shot chart, momentum
- **Event Timeline:** Filterable event log
- **Shift Breakdown:** Line performance by shift

### Level 5: Goalie Analytics (Needs Level 1-2)
- **Goalie Card:** Record, SV%, GAA
- **Micro Stats:** Save location breakdown
- **Shot Maps:** Visual save/goal locations

### Level 6: Advanced Analytics (Needs All Above)
- **H2H Matchups:** Player vs player when on ice together
- **WOWY:** Impact of linemates
- **Zone Analysis:** Entry/exit effectiveness
- **Expected Goals:** xG model results

---

## 🗄️ Data Sources by Dashboard

| Dashboard | Primary Table | Supporting Tables |
|-----------|--------------|-------------------|
| Standings | dim_schedule | dim_team |
| Leaders | fact_player_game_stats | dim_player |
| Team Overview | fact_team_game_stats | dim_schedule |
| Player Stats | fact_player_game_stats | dim_player, dim_schedule |
| Game Summary | fact_team_game_stats | fact_player_game_stats |
| Event Timeline | fact_events | fact_events_player |
| Goalie Stats | fact_goalie_game_stats | dim_player |
| H2H | fact_h2h | dim_player |
| WOWY | fact_wowy | dim_player |

---

## 📐 Key Calculations

### Season Totals (Aggregate)
```sql
SELECT 
  player_id,
  player_name,
  COUNT(*) as games_played,
  SUM(goals) as total_goals,
  SUM(assists) as total_assists,
  SUM(points) as total_points,
  ROUND(SUM(goals)::numeric / NULLIF(SUM(shots), 0) * 100, 1) as shooting_pct
FROM fact_player_game_stats
GROUP BY player_id, player_name
ORDER BY total_points DESC
```

### Per-60 Stats
```sql
SELECT 
  player_id,
  ROUND(SUM(goals) * 3600.0 / NULLIF(SUM(toi_seconds), 0), 2) as goals_per_60,
  ROUND(SUM(points) * 3600.0 / NULLIF(SUM(toi_seconds), 0), 2) as points_per_60
FROM fact_player_game_stats
GROUP BY player_id
```

### Team Standings
```sql
SELECT 
  CASE WHEN home_score > away_score THEN home_team ELSE away_team END as winner,
  COUNT(*) as wins
FROM dim_schedule
GROUP BY winner
ORDER BY wins DESC
```

### Rolling Average (5-game)
```javascript
// Calculate client-side after fetching game log
const rolling5 = gameLog.map((game, i) => {
  const window = gameLog.slice(Math.max(0, i-4), i+1);
  return {
    ...game,
    rolling_points: window.reduce((sum, g) => sum + g.points, 0) / window.length
  };
});
```

---

## ⚠️ Known Issues & Considerations

### Data Gaps
- **Pass completion:** Missing in games 18977, 18981, 18987
- **Assists:** ~83% match rate vs ground truth (tracking gaps)
- **Zone time:** Not yet calculated per player

### Performance Tips
1. **Use pagination:** Limit large result sets
2. **Select specific columns:** Don't `SELECT *` for lists
3. **Cache standings:** Update hourly, not per request
4. **Aggregate server-side:** Use Supabase functions for complex calcs

### Mobile Considerations
- Design mobile-first
- Collapse tables to cards on small screens
- Use horizontal scroll for wide tables
- Touch-friendly filters

---

## 🎨 Design Guidelines

### Color Palette
```css
--primary: #1a365d;      /* Dark blue - headers */
--secondary: #3182ce;    /* Blue - links, accents */
--success: #38a169;      /* Green - positive stats */
--warning: #d69e2e;      /* Yellow - neutral */
--danger: #e53e3e;       /* Red - negative stats */
--background: #f7fafc;   /* Light gray */
--card: #ffffff;         /* White cards */
--text: #2d3748;         /* Dark gray text */
```

### Typography
- Headers: System font stack, bold
- Body: 16px base, 1.6 line height
- Stats: Monospace for numbers

### Component Patterns
- **Cards:** White background, subtle shadow, 8px radius
- **Tables:** Striped rows, sticky headers
- **Charts:** Consistent colors, clear legends
- **Filters:** Dropdowns above content, chips for active filters

---

## 📁 Files in This Handoff

```
dashboard_dev/
├── README.md                           # This file
├── NEXT_PROMPT.md                      # Prompt for continuing
├── docs/
│   ├── DASHBOARD_DEV_COMPLETE_GUIDE.md # Full specifications
│   ├── SCHEMA_AND_ERD.md               # Database schema
│   └── MASTER_INSTRUCTIONS.md          # Business rules
├── data_dictionary/
│   ├── dd_fact_player_game_stats.csv
│   ├── dd_fact_team_game_stats.csv
│   ├── dd_fact_goalie_game_stats.csv
│   ├── dd_fact_events.csv
│   ├── dd_fact_h2h.csv
│   └── dd_fact_wowy.csv
└── examples/
    └── sample_queries.sql              # Example Supabase queries
```

---

## ✅ Success Criteria

### MVP (Phase 1)
- [ ] League standings page
- [ ] League leaders (top 10 per category)
- [ ] Team overview dashboard
- [ ] Player stats page with game log
- [ ] Game summary page

### Full Release (Phase 2)
- [ ] All Level 1-5 dashboards complete
- [ ] Mobile responsive
- [ ] <3 second load times
- [ ] Filters work correctly
- [ ] Charts render properly

### Advanced (Phase 3)
- [ ] H2H matchup tool
- [ ] WOWY analysis
- [ ] Shot maps / heat maps
- [ ] xG visualizations

---

## 🆘 Getting Help

- **Data questions:** Check data dictionaries
- **Supabase issues:** Contact Supabase dev
- **Business rules:** See `MASTER_INSTRUCTIONS.md`
- **Design specs:** See `DASHBOARD_DEV_COMPLETE_GUIDE.md`

---

*Last Updated: December 2024*
