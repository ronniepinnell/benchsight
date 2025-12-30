# Claude Prompt: Tracker Developer

Copy this entire prompt when starting a new Claude chat for Tracker development.

---

## Context

I'm working on BenchSight, a hockey analytics platform for the NORAD recreational hockey league. I need help developing the Game Tracker application.

## Current State

- Database: Supabase PostgreSQL with 96 tables
- Schema: Star schema with dim_* (44) and fact_* (51) tables
- Data: 4 games fully tracked and validated
- Prototype: `dashboard/tracker_v4_final_WORKING.html` exists but needs Supabase integration

## My Role

I'm the Tracker Developer. I need to build an interactive game tracking interface that:
1. Loads existing game data from Supabase
2. Allows real-time event and shift tracking
3. Saves drafts and publishes final data to Supabase
4. Validates data quality before publishing

## Key Technical Details

### Supabase Connection
```javascript
const supabase = createClient(
  'https://uuaowslhpgyiudmbvqze.supabase.co',
  'ANON_KEY_FOR_READS'  // service key for writes
);
```

### Key Tables I Write To
- `fact_events` (event_key PK) - Individual plays
- `fact_shifts` (shift_key PK) - Time periods
- `fact_events_player` (event_player_key PK) - Player involvement
- `fact_shifts_player` (shift_player_key PK) - Players on shifts
- `staging_events` / `staging_shifts` - Draft storage

### Key Generation
```javascript
const eventKey = `EV${gameId}${String(eventIndex).padStart(5, '0')}`;
const shiftKey = `${gameId}_${shiftIndex}`;
```

### Dimension Tables I Need
- dim_event_type, dim_event_detail, dim_event_detail_2
- dim_play_detail, dim_play_detail_2
- dim_shot_type, dim_pass_type
- dim_zone, dim_period, dim_situation, dim_strength
- dim_success, dim_player_role
- dim_player, dim_team

### Linked Events Logic
- Shot → Save → Rebound chains use `linked_event_index`
- Shot: event_player_1 = shooter, opp_player_1 = goalie
- Save: event_player_1 = goalie, opp_player_1 = shooter (swap!)
- Rebound: event_player_1 = goalie only
- Stoppage: assign to last event's event_player_1

### Video Integration
- Each event has `running_video_time` column
- Build URL: `${video_url}&t=${Math.floor(seconds)}s`

## What I Need Help With

[Describe your specific task here]

## Files Available
- Full handoff: `docs/handoffs/TRACKER_DEV_HANDOFF.md`
- Prototype: `dashboard/tracker_v4_final_WORKING.html`
- Schema: `sql/05_FINAL_COMPLETE_SCHEMA.sql`
- Sample data: `data/output/fact_events.csv`
