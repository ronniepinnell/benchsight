# Claude Prompt: Dashboard Developer

Copy this entire prompt when starting a new Claude chat for Dashboard development.

---

## Context

I'm working on BenchSight, a hockey analytics platform for the NORAD recreational hockey league. I need help developing the Analytics Dashboard.

## Current State

- Database: Supabase PostgreSQL with 96 tables
- Data: ~120,000 rows across all tables
- Prototype dashboards exist in `dashboard/` folder

## My Role

I'm the Dashboard Developer. I need to build an interactive analytics dashboard that:
1. Displays player/team/game statistics from Supabase
2. Provides video links for every play, event, shift
3. Enables deep drill-down from team → line → player → event
4. Shows visualizations (shot charts, timelines, comparisons)

## Key Technical Details

### Supabase Connection
```javascript
const supabase = createClient(
  'https://uuaowslhpgyiudmbvqze.supabase.co',
  'YOUR_ANON_KEY'  // Read-only public key
);
```

### Key Tables for Stats
- `fact_player_game_stats` - Per-game player stats (107 rows)
- `fact_team_game_stats` - Per-game team stats (8 rows)
- `fact_goalie_game_stats` - Goalie stats (8 rows)
- `fact_events` - All events with video timing (5,833 rows)
- `fact_h2h` - Head-to-head matchups (684 rows)
- `fact_wowy` - With/Without analysis (641 rows)
- `fact_line_combos` - Line combination stats (332 rows)
- `fact_scoring_chances` - Shot quality (451 rows)

### Video Integration
```javascript
// Every event has running_video_time
const videoUrl = `${game.video_url}&t=${Math.floor(event.running_video_time)}s`;
```

### Dashboard Hierarchy
1. League Overview → Game Selection
2. Game Dashboard → Team Comparison
3. Team View → Player Stats
4. Player View → Individual Events
5. Event Detail → Video Popup

### Inspirations to Emulate
- Natural Stat Trick (naturalstattrick.com)
- Evolving Hockey (evolving-hockey.com)
- Money Puck (moneypuck.com)

## What I Need Help With

[Describe your specific task here]

## Files Available
- Full handoff: `docs/handoffs/DASHBOARD_DEV_HANDOFF.md`
- Prototypes: `dashboard/` folder
- Schema: `sql/05_FINAL_COMPLETE_SCHEMA.sql`
