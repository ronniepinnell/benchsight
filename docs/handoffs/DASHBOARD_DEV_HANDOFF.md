# Dashboard Developer Handoff

**Role:** Dashboard Developer  
**Version:** 2.0  
**Date:** December 30, 2025

---

## Your Mission

Build an interactive hockey analytics dashboard that provides:
1. Real-time stats and visualizations from Supabase
2. Video integration for every play, event, and shift
3. Deep drill-down from team → line → player → individual events
4. Comparative analytics (H2H, WOWY, line combos)

---

## Quick Start

### 1. Get the Codebase
```bash
unzip benchsight_COMPLETE_FULL.zip
cd benchsight_COMPLETE_FULL
```

### 2. Review Existing Prototypes
```
dashboard/
├── dashboard_v1.html          # Basic stats
├── dashboard_v2_game_select.html
├── power_bi_dashboard.html    # Power BI style
├── shot_chart.html            # Shot visualization
└── game_review_*.html         # Game review prototypes
```

### 3. Connect to Supabase
```javascript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'https://uuaowslhpgyiudmbvqze.supabase.co',
  'YOUR_ANON_KEY'  // Public read-only key
);
```

---

## Data Architecture Overview

### Fact Tables (Metrics & Events)

| Table | Rows | Purpose | Key Columns |
|-------|------|---------|-------------|
| `fact_player_game_stats` | 107 | Per-game player stats | goals, assists, shots, toi |
| `fact_team_game_stats` | 8 | Per-game team stats | shots, goals, possession |
| `fact_goalie_game_stats` | 8 | Goalie performance | saves, ga, sv_pct |
| `fact_events` | 5,833 | Individual plays | event_type, timing, zone |
| `fact_events_player` | 11,635 | Player involvement | player_id, role |
| `fact_shifts` | 672 | Ice time periods | duration, strength |
| `fact_shifts_player` | 4,626 | Players on shifts | toi, plus_minus |
| `fact_h2h` | 684 | Head-to-head matchups | player pairs |
| `fact_wowy` | 641 | With/Without analysis | on/off splits |
| `fact_player_boxscore_all` | 14,473 | Complete boxscores | all stats |
| `fact_line_combos` | 332 | Line combinations | toi, goals |
| `fact_sequences` | 1,088 | Possession sequences | duration, result |
| `fact_plays` | 2,714 | Play-by-play | sequence context |
| `fact_scoring_chances` | 451 | Scoring chances | danger level |
| `fact_shot_danger` | 435 | Shot quality | xG potential |

### Dimension Tables (Lookups)

| Table | Purpose |
|-------|---------|
| `dim_player` | Player info (337 players) |
| `dim_team` | Team info (26 teams) |
| `dim_schedule` | Game schedule (562 games) |
| `dim_season` | Season info |
| `dim_event_type` | Event type lookups |
| `dim_zone` | Zone definitions |
| `dim_situation` | Game situations (PP, PK, EV) |
| `dim_strength` | Strength states (5v5, 5v4, etc.) |

---

## Key Queries

### Player Stats for a Game

```javascript
async function getPlayerGameStats(gameId) {
  const { data, error } = await supabase
    .from('fact_player_game_stats')
    .select(`
      player_id,
      player_name,
      goals,
      assists,
      points,
      shots,
      sog,
      shooting_pct,
      toi_minutes,
      fo_pct,
      hits,
      blocks,
      giveaways,
      takeaways,
      plus_minus
    `)
    .eq('game_id', gameId)
    .order('points', { ascending: false });
    
  return data;
}
```

### Team Stats Comparison

```javascript
async function getTeamComparison(gameId) {
  const { data } = await supabase
    .from('fact_team_game_stats')
    .select('*')
    .eq('game_id', gameId);
    
  // Returns home and away team stats
  return {
    home: data.find(t => t.venue === 'Home'),
    away: data.find(t => t.venue === 'Away')
  };
}
```

### Events with Video Timing

```javascript
async function getEventsWithVideo(gameId) {
  // Get game video info
  const { data: game } = await supabase
    .from('dim_schedule')
    .select('video_url, video_start_time')
    .eq('game_id', gameId)
    .single();
    
  // Get events
  const { data: events } = await supabase
    .from('fact_events')
    .select(`
      event_key,
      event_index,
      period,
      event_type,
      event_detail,
      event_successful,
      running_video_time,
      time_start_total_seconds,
      home_team,
      away_team,
      zone_id
    `)
    .eq('game_id', gameId)
    .order('event_index');
    
  // Add video URLs
  return events.map(e => ({
    ...e,
    videoUrl: buildVideoUrl(game.video_url, e.running_video_time)
  }));
}

function buildVideoUrl(baseUrl, seconds) {
  // YouTube format
  if (baseUrl.includes('youtube')) {
    return `${baseUrl}&t=${Math.floor(seconds)}s`;
  }
  // Vimeo format
  if (baseUrl.includes('vimeo')) {
    return `${baseUrl}#t=${Math.floor(seconds)}s`;
  }
  return baseUrl;
}
```

### Player Head-to-Head

```javascript
async function getH2H(gameId, playerId) {
  const { data } = await supabase
    .from('fact_h2h')
    .select(`
      player_id,
      opp_player_id,
      player_name,
      opp_player_name,
      toi_together,
      goals_for,
      goals_against,
      shots_for,
      shots_against,
      xg_for,
      xg_against
    `)
    .eq('game_id', gameId)
    .eq('player_id', playerId);
    
  return data;
}
```

### WOWY (With Or Without You)

```javascript
async function getWOWY(gameId, playerId) {
  const { data } = await supabase
    .from('fact_wowy')
    .select(`
      player_id,
      teammate_id,
      player_name,
      teammate_name,
      toi_with,
      toi_without,
      goals_with,
      goals_without,
      cf_pct_with,
      cf_pct_without
    `)
    .eq('game_id', gameId)
    .eq('player_id', playerId);
    
  return data;
}
```

### Line Combinations

```javascript
async function getLineCombos(gameId) {
  const { data } = await supabase
    .from('fact_line_combos')
    .select(`
      line_id,
      player_1_name,
      player_2_name,
      player_3_name,
      toi_minutes,
      goals_for,
      goals_against,
      shots_for,
      shots_against,
      cf_pct
    `)
    .eq('game_id', gameId)
    .order('toi_minutes', { ascending: false });
    
  return data;
}
```

---

## Video Integration

### CRITICAL: Video Pop-up Component

Every event, shift, and play should have a video link:

```javascript
// Video Player Component
function VideoPopup({ videoUrl, startTime, endTime, title }) {
  const [isOpen, setIsOpen] = useState(false);
  
  const url = buildVideoUrl(videoUrl, startTime);
  
  return (
    <>
      <button onClick={() => setIsOpen(true)}>▶ Watch</button>
      
      {isOpen && (
        <div className="video-modal">
          <h3>{title}</h3>
          <iframe 
            src={url}
            width="800" 
            height="450"
            allowFullScreen
          />
          <div className="video-controls">
            <button onClick={() => seekTo(startTime)}>Start</button>
            <button onClick={() => seekTo(endTime)}>End</button>
          </div>
          <button onClick={() => setIsOpen(false)}>Close</button>
        </div>
      )}
    </>
  );
}
```

### Multiple Camera Angles

```javascript
async function getVideoAngles(gameId) {
  const { data } = await supabase
    .from('fact_video')
    .select('*')
    .eq('game_id', gameId);
    
  // Returns multiple angles: Main, Goal Cam, Blue Line, etc.
  return data;
}

// In your video popup
function MultiAngleVideoPopup({ gameId, startTime }) {
  const [angles, setAngles] = useState([]);
  const [selectedAngle, setSelectedAngle] = useState(0);
  
  useEffect(() => {
    getVideoAngles(gameId).then(setAngles);
  }, [gameId]);
  
  return (
    <div className="multi-angle-video">
      <div className="angle-selector">
        {angles.map((angle, i) => (
          <button 
            key={i}
            className={i === selectedAngle ? 'active' : ''}
            onClick={() => setSelectedAngle(i)}
          >
            {angle.angle_name}
          </button>
        ))}
      </div>
      <iframe src={buildVideoUrl(angles[selectedAngle]?.url, startTime)} />
    </div>
  );
}
```

---

## Dashboard Layout Recommendations

### Main Dashboard Hierarchy

```
LEVEL 1: LEAGUE OVERVIEW
├── Season standings
├── League leaders
├── Recent games
└── Upcoming schedule

LEVEL 2: GAME DASHBOARD
├── Score & Game Info
├── Team comparison (shots, possession, etc.)
├── Period-by-period breakdown
├── Key events timeline
└── Drill down to...

LEVEL 3: TEAM GAME VIEW
├── Player stats table
├── Line combinations
├── Special teams
├── Shot chart
└── Drill down to...

LEVEL 4: PLAYER GAME VIEW
├── Individual stats
├── Shift-by-shift
├── Event log
├── H2H matchups
├── WOWY splits
└── Drill down to...

LEVEL 5: EVENT/SHIFT DETAIL
├── Full event info
├── Players involved
├── Video clip
├── Linked events
└── Context (sequence, play)
```

### Component Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER: Game Selector | Team Logos | Score | Period/Time      │
├───────────────────────────────┬─────────────────────────────────┤
│                               │                                 │
│     TEAM COMPARISON           │      SHOT CHART                 │
│     (Side-by-side stats)      │      (Interactive rink)         │
│                               │                                 │
├───────────────────────────────┼─────────────────────────────────┤
│                               │                                 │
│     PLAYER STATS TABLE        │      EVENT TIMELINE             │
│     (Sortable, clickable)     │      (Goals, penalties, etc.)   │
│                               │                                 │
├───────────────────────────────┴─────────────────────────────────┤
│                                                                 │
│     DETAIL PANEL (expands on click)                            │
│     Player card | Shift log | Video | H2H | WOWY               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Visualization Components

### Shot Chart

```javascript
// Shot locations from fact_shot_xy (if populated)
// Or derive from fact_events with zone info

async function getShotData(gameId) {
  const { data } = await supabase
    .from('fact_events')
    .select(`
      event_key,
      event_type,
      event_detail,
      event_successful,
      zone_id,
      running_video_time,
      home_team,
      away_team
    `)
    .eq('game_id', gameId)
    .in('event_type', ['Shot', 'Goal']);
    
  return data;
}

// Render on SVG rink
function ShotChart({ shots }) {
  return (
    <svg viewBox="0 0 200 85" className="rink">
      {/* Rink outline */}
      <rect x="0" y="0" width="200" height="85" fill="#fff" stroke="#000"/>
      {/* Center line */}
      <line x1="100" y1="0" x2="100" y2="85" stroke="red"/>
      {/* Goal creases */}
      <circle cx="11" cy="42.5" r="6" fill="lightblue"/>
      <circle cx="189" cy="42.5" r="6" fill="lightblue"/>
      
      {/* Shots */}
      {shots.map(shot => (
        <circle
          key={shot.event_key}
          cx={shot.x}
          cy={shot.y}
          r={shot.event_type === 'Goal' ? 5 : 3}
          fill={shot.event_type === 'Goal' ? 'green' : 'gray'}
          onClick={() => showShotDetail(shot)}
        />
      ))}
    </svg>
  );
}
```

### Event Timeline

```javascript
function EventTimeline({ events, periodLength = 1200 }) {
  const periods = [1, 2, 3];
  
  return (
    <div className="timeline">
      {periods.map(period => (
        <div key={period} className="period-track">
          <span>P{period}</span>
          <div className="track">
            {events
              .filter(e => e.period === period)
              .map(event => (
                <div
                  key={event.event_key}
                  className={`event-marker ${event.event_type.toLowerCase()}`}
                  style={{
                    left: `${(event.time_start_total_seconds / periodLength) * 100}%`
                  }}
                  title={`${event.event_type}: ${event.event_detail}`}
                  onClick={() => showEventDetail(event)}
                />
              ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

### Player Comparison Radar

```javascript
function PlayerRadar({ player1Stats, player2Stats }) {
  const categories = [
    { key: 'goals_per_60', label: 'Goals/60' },
    { key: 'assists_per_60', label: 'Assists/60' },
    { key: 'shots_per_60', label: 'Shots/60' },
    { key: 'hits_per_60', label: 'Hits/60' },
    { key: 'cf_pct', label: 'CF%' },
    { key: 'xgf_pct', label: 'xGF%' }
  ];
  
  // Normalize to 0-100 scale
  // Draw radar chart with both players
  // Use Chart.js or D3 for rendering
}
```

---

## Dashboard Features Checklist

### Must Have ✅

- [ ] Game selector dropdown
- [ ] Team stats comparison
- [ ] Player stats table (sortable)
- [ ] Shot chart visualization
- [ ] Goal/penalty timeline
- [ ] Video links for all events
- [ ] Period-by-period breakdown

### Should Have 🔶

- [ ] Player drill-down panels
- [ ] H2H matchup view
- [ ] WOWY splits display
- [ ] Line combination stats
- [ ] Shift-by-shift view
- [ ] Goalie stats card
- [ ] Scoring chance quality

### Nice to Have 💫

- [ ] Animated play sequences
- [ ] Heat maps
- [ ] Expected goals (xG) display
- [ ] Zone entry/exit tracking
- [ ] Momentum charts
- [ ] Predictive analytics
- [ ] Export to PDF/image

---

## Data Refresh Strategy

### Real-time Updates (if tracking live)

```javascript
// Subscribe to changes
const subscription = supabase
  .channel('game-updates')
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'fact_events',
    filter: `game_id=eq.${gameId}`
  }, payload => {
    // Add new event to state
    addEvent(payload.new);
  })
  .subscribe();

// Cleanup
return () => supabase.removeChannel(subscription);
```

### Polling (simpler approach)

```javascript
useEffect(() => {
  const interval = setInterval(() => {
    refreshData();
  }, 30000); // Every 30 seconds
  
  return () => clearInterval(interval);
}, []);
```

---

## Inspiration & Reference

### NHL-style dashboards to emulate:
- Natural Stat Trick (naturalstattrick.com)
- Evolving Hockey (evolving-hockey.com)
- Money Puck (moneypuck.com)
- Hockey Reference (hockey-reference.com)

### Key Features from Pros:

**Natural Stat Trick:**
- Clean data tables
- Shot attempt charts
- Line combination tool
- H2H matchup finder

**Evolving Hockey:**
- Player cards with radar charts
- RAPM breakdowns
- Contract projections
- WAR calculations

**Money Puck:**
- Real-time win probability
- Expected goals charts
- Shot quality breakdowns
- Goalie performance

---

## Performance Tips

### 1. Aggregate on Server

```javascript
// BAD: Fetch all events, calculate in browser
const events = await supabase.from('fact_events').select('*');
const shots = events.filter(e => e.event_type === 'Shot').length;

// GOOD: Use database aggregation
const { data } = await supabase
  .from('fact_events')
  .select('event_type', { count: 'exact' })
  .eq('game_id', gameId)
  .eq('event_type', 'Shot');
```

### 2. Use Views for Complex Queries

Create Supabase views for commonly used aggregations:

```sql
-- In Supabase SQL Editor
CREATE VIEW v_game_summary AS
SELECT 
  game_id,
  COUNT(*) FILTER (WHERE event_type = 'Shot') as total_shots,
  COUNT(*) FILTER (WHERE event_type = 'Goal') as total_goals,
  COUNT(*) FILTER (WHERE event_type = 'Hit') as total_hits
FROM fact_events
GROUP BY game_id;
```

### 3. Lazy Load Details

```javascript
// Load summary first
const summary = await getGameSummary(gameId);

// Load details only when user clicks
const loadPlayerDetails = async (playerId) => {
  setLoading(true);
  const details = await getPlayerDetails(gameId, playerId);
  setPlayerDetails(details);
  setLoading(false);
};
```

---

## Testing Your Dashboard

### Test Games

| Game ID | Description | Events | Shifts |
|---------|-------------|--------|--------|
| 18969 | Full game, validated | 5,833 | 672 |
| 18977 | Full game | Similar | Similar |
| 18981 | Full game | Similar | Similar |
| 18987 | Full game | Similar | Similar |

### Validation Checks

```javascript
// Verify goals match official score
async function validateGoals(gameId) {
  const { data: events } = await supabase
    .from('fact_events')
    .select('*')
    .eq('game_id', gameId)
    .eq('event_type', 'Goal');
    
  const { data: schedule } = await supabase
    .from('dim_schedule')
    .select('home_total_goals, away_total_goals')
    .eq('game_id', gameId)
    .single();
    
  const homeGoals = events.filter(e => e.team_venue === 'Home').length;
  const awayGoals = events.filter(e => e.team_venue === 'Away').length;
  
  console.assert(homeGoals === schedule.home_total_goals);
  console.assert(awayGoals === schedule.away_total_goals);
}
```

---

## Resources

- Prototype Dashboards: `dashboard/` folder
- Schema: `sql/05_FINAL_COMPLETE_SCHEMA.sql`
- Sample Data: All `data/output/*.csv` files
- Inspiration: `docs/INSPIRATION_AND_RESEARCH.md`
- Supabase JS Docs: https://supabase.com/docs/reference/javascript

---

## Questions?

See `prompts/dashboard_dev_prompt.md` for a prompt to start a new Claude chat with full context.
