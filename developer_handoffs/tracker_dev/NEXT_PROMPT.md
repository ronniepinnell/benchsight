# BenchSight Tracker Developer - Session Prompt

Copy and paste this prompt to start your session:

---

I'm the Tracker Developer for BenchSight, a hockey analytics platform. The tracker records live game events and writes directly to Supabase.

## Project Context

- **Database:** Supabase PostgreSQL (98 tables total)
- **Tracker writes to:** 4 main tables (events, shifts, XY coords, video highlights)
- **Tracker reads from:** 15+ dimension tables for dropdowns/lookups

## Tables I Write To

### 1. fact_events (PRIMARY - game events)
```
PK: event_key = "{game_id}_{event_index}"
Required: game_id, event_index, period_number, game_time, event_type, event_player_1, team_id
Optional: event_detail, event_detail_2, event_player_2, event_player_3, success, x_coord, y_coord, zone, strength
```

### 2. fact_shifts (player shifts)
```
PK: shift_key = "{game_id}_{player_id}_{shift_number}"
Required: game_id, player_id, shift_number, period_number, start_time, end_time
Optional: duration, team_id, shift_start_type, shift_stop_type
```

### 3. fact_player_xy_long (XY coordinates)
```
PK: xy_long_key = "{game_id}_{timestamp}_{player_id}"
Required: game_id, period_number, game_time, player_id, x_coord, y_coord
```

### 4. fact_video_highlights (video clips) - NEW
```
PK: highlight_key = "{game_id}_{event_index}_{clip_number}"
Required: game_id, video_url, start_timestamp, end_timestamp, highlight_type
Optional: event_index, player_id, team_id, title, description, is_featured
```

## Tables I Read From (Lookups)

**Core lookups:**
- `dim_player` - player_id, player_name, jersey_number, position (337 rows)
- `dim_team` - team_id, team_name, team_abbrev (26 rows)
- `dim_schedule` - game_id, game_date, home_team_id, away_team_id (562 rows)

**Event type lookups:**
- `dim_event_type` - event types (Shot, Pass, Goal, Faceoff, Hit, etc.)
- `dim_event_detail` - event details (Wrist Shot, Slap Shot, etc.)
- `dim_event_detail_2` - secondary details
- `dim_shot_type` - shot types
- `dim_pass_type` - pass types

**Other lookups:**
- `dim_zone` - DZ, NZ, OZ
- `dim_period` - 1, 2, 3, OT, SO
- `dim_strength` - EV, PP, PK, 4v4, etc.
- `dim_success` - s (success), u (unsuccessful)
- `dim_highlight_type` - goal, save, hit, skill, etc. (NEW)

**Roster for game:**
- `fact_gameroster` - players assigned to each game

## Critical Data Rules

1. **event_player_1** = PRIMARY player who gets the stat credit
2. **Goals detected TWO ways:**
   - `event_type = 'Goal'`
   - `event_detail IN ('Shot Goal', 'Goal Scored')`
3. **success** = 's' (successful) or 'u' (unsuccessful)
4. **Coordinates:** x: 0-100, y: 0-42.5 (rink dimensions)

## Key Documentation

- **MUST READ:** `docs/TRACKER_DATA_FORMAT.md` - All columns, types, examples
- Supabase queries: `docs/SUPABASE_INTEGRATION_GUIDE.md`
- UI wireframes: `docs/WIREFRAMES_AND_PAGES.md`
- Video feature: `docs/VIDEO_HIGHLIGHTS_SPEC.md`
- Current prototype: `tracker/tracker_v19.html`

## Dependencies (Must be complete first)

- ✅ Supabase schema fixed (all 98 tables loading)
- ✅ Video tables created (`dim_highlight_type`, `fact_video_highlights`)
- ✅ `fact_events` has highlight columns (`is_highlight_candidate`, `highlight_score`, etc.)

## My Specific Task Today

[DESCRIBE YOUR TASK]
