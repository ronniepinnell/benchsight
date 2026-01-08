# BenchSight Video, XY, and Highlight Data Roadmap

**Version:** 16.08  
**Updated:** January 8, 2026


## Current State (v16.08)

### NEW: Video Timing Modal (🎬 button)

The tracker now has a **Video Timing** modal that allows you to configure:

1. **Video Start Offset** - Seconds to skip at beginning (warmups, pre-game)
2. **Period Length** - Default 20 minutes, adjustable
3. **Intermission 1** - Duration after Period 1 (in seconds)
4. **Intermission 2** - Duration after Period 2 (in seconds)
5. **Timeouts/Stoppages** - Add any in-game stoppages that extend video time
6. **YouTube URL** - Optional link to game video

### Video Time Formula (Updated)

```javascript
// OLD formula (fixed 15 min intermissions):
running_video_time = (period-1)*1200 + (1200 - time_remaining) + (period-1)*900

// NEW formula (variable everything):
running_video_time = 
    videoStartOffset                           // Skip intro
  + elapsed_in_period                          // Time elapsed in current period
  + (period >= 2 ? periodLength*60 + int1 : 0) // P1 + Int1 if P2+
  + (period >= 3 ? periodLength*60 + int2 : 0) // P2 + Int2 if P3+
  + sum(timeouts before current time)          // All earlier timeouts
```

### Example: Your Scenario

```
Period 1: 0 to 1200 (20 min)
Intermission 1: 30 sec
Period 2: 1230 to 2430 (20 min) 
Intermission 2: 45 sec
Period 3: 2475 to 3675 (20 min)
Timeout at P3 10:00 (1000 sec elapsed): +60 sec

Event at P3 5:00 (15:00 remaining = 300 sec remaining):
- elapsed in P3 = 1200 - 300 = 900 sec
- But timeout happened at 1000 elapsed, which is BEFORE 900
- Wait, higher game time = earlier. So 10:00 > 5:00, timeout is earlier
- running_video_time = 0 + 900 + (1200+30) + (1200+45) + 60 = 3435 sec
```

### Existing Columns in ETL Output

**fact_events** already has:
| Column | Purpose | Status |
|--------|---------|--------|
| `puck_x_start` | Puck X at event start (0-200 ft) | ✅ In schema |
| `puck_y_start` | Puck Y at event start (0-85 ft) | ✅ In schema |
| `puck_x_end` | Puck X at event end | ✅ In schema |
| `puck_y_end` | Puck Y at event end | ✅ In schema |
| `player_x` | Primary player X position | ✅ In schema |
| `player_y` | Primary player Y position | ✅ In schema |
| `is_highlight` | 1 = highlight, 0 = normal | ✅ In schema |
| `running_video_time` | Seconds from video start | ✅ In schema |
| `event_running_start` | Game running seconds | ✅ In schema |

**fact_event_players** already has:
| Column | Purpose | Status |
|--------|---------|--------|
| `player_x` | Player X position | ✅ In schema |
| `player_y` | Player Y position | ✅ In schema |
| `puck_x_start/end` | Copied from event | ✅ In schema |
| `puck_y_start/end` | Copied from event | ✅ In schema |

---

## Data Flow: Tracker → ETL → Supabase

```
┌─────────────────────┐
│   TRACKER (UI)      │
│                     │
│ • Click rink → XY   │
│ • Press H → highlight│
│ • Enter time → sync │
└─────────┬───────────┘
          │ Export XLSX
          ▼
┌─────────────────────┐
│   RAW DATA          │
│   data/raw/games/   │
│   {id}/{id}_tracking│
│                     │
│ events sheet:       │
│ • puck_x_start_     │
│ • puck_y_start_     │
│ • is_highlight_     │
│ • start_time_       │
│                     │
│ event_players sheet:│
│ • player_x_         │
│ • player_y_         │
└─────────┬───────────┘
          │ ETL Process
          ▼
┌─────────────────────┐
│   ETL OUTPUT        │
│   data/output/      │
│                     │
│ fact_events.csv     │
│ • All XY columns    │
│ • is_highlight      │
│ • running_video_time│
│                     │
│ fact_event_players  │
│ • player XY data    │
└─────────┬───────────┘
          │ sync_to_supabase.py
          ▼
┌─────────────────────┐
│   SUPABASE          │
│                     │
│ Same schema as CSV  │
│ All columns present │
└─────────────────────┘
```

---

## Video Time Calculation

### Formula
```
event_running_start = (period - 1) * 1200 + (1200 - time_remaining_seconds)
running_video_time = event_running_start + intermission_offset

Where:
- 1200 = 20 minutes per period in seconds
- intermission_offset = (period - 1) * intermission_duration
- Default intermission = 900 seconds (15 min)
```

### Example
```
Period 2, Time 15:30 (930 seconds remaining):
event_running_start = (2-1) * 1200 + (1200 - 930) = 1200 + 270 = 1470 sec
running_video_time = 1470 + 900 = 2370 sec (39:30 in video)
```

### Do I Need to Cut Stoppages?

**NO.** The tracker calculates running time INCLUDING stoppages. The video file should be the full uncut game video.

If you DO cut stoppages:
1. Track cumulative stoppage duration per period
2. Subtract from running_video_time
3. Or adjust intermission_duration in settings

---

## Highlight Workflow

### 1. Mark Highlights in Tracker
- Press `H` while recording event
- Goals auto-marked as highlights
- Edit any event → set `is_highlight = Y`

### 2. Export Contains Highlight Data
```excel
events sheet:
| event_index_ | event_type_ | is_highlight_ | start_time_ | running_video_time_ |
|--------------|-------------|---------------|-------------|---------------------|
| 1            | Shot        | 0             | 18:45       | 75                  |
| 2            | Goal        | 1             | 18:30       | 90                  | ← AUTO HIGHLIGHT
| 3            | Hit         | 1             | 17:00       | 180                 | ← MANUAL HIGHLIGHT
```

### 3. Query Highlights from Supabase
```sql
SELECT 
    game_id,
    event_index,
    event_type,
    event_detail,
    running_video_time,
    player_name,
    team
FROM fact_events 
WHERE is_highlight = 1 
ORDER BY game_id, running_video_time;
```

### 4. Create Highlight Reel
```python
# Python example with moviepy
from moviepy.editor import VideoFileClip, concatenate_videoclips

highlights = supabase.table('fact_events').select('*').eq('is_highlight', 1).execute()

clips = []
video = VideoFileClip("game_video.mp4")
for h in highlights.data:
    start = h['running_video_time']
    end = start + 10  # 10 second clips
    clips.append(video.subclip(start, end))

final = concatenate_videoclips(clips)
final.write_videofile("highlights.mp4")
```

---

## XY Data Structure

### Coordinate System
```
NHL Rink: 200 ft × 85 ft
Origin (0,0) = Top-left corner (behind left goal)

            ← 200 ft →
    ┌─────────────────────────┐
    │ LEFT     │  CENTER  │ RIGHT │  ↑
    │ ZONE     │  ICE     │ ZONE  │  85 ft
    │          │          │       │  ↓
    └─────────────────────────────┘
    x=0      x=75      x=125    x=200
              Blue lines

Goal lines at x=11 (left) and x=189 (right)
```

### XY in fact_events
- `puck_x_start`, `puck_y_start` = Puck position at event start
- `puck_x_end`, `puck_y_end` = Puck position at event end (for shots, passes)
- `player_x`, `player_y` = Primary player position (event_team_player_1)

### XY in fact_event_players
- `player_x`, `player_y` = Each player's individual position
- One row per player per event
- Enables heat maps, positioning analysis

### Raw XY Files (if capturing detailed paths)
```
data/raw/games/{id}/xy/event_locations/{id}_1.csv

Columns:
- game_id
- link_event_index (ties to event)
- Player (jersey number)
- X, Y (position 1)
- X2, Y2 (position 2 - for movement)
- X3, Y3 (position 3)
- Distance (total movement)
```

---

## YouTube Integration

### Current: Manual Reference
```
Store YouTube URL in dim_schedule or separate table:
| game_id | youtube_url                              | video_offset |
|---------|------------------------------------------|--------------|
| 18987   | https://youtube.com/watch?v=xyz123       | 30           |

video_offset = seconds to skip (intro, warmups before period 1)
```

### Embedding in Dashboard
```html
<iframe 
  src="https://www.youtube.com/embed/{VIDEO_ID}?start={running_video_time}"
  width="640" height="360">
</iframe>
```

### Deep Link to Specific Play
```
https://youtube.com/watch?v={VIDEO_ID}&t={running_video_time}s
```

### Future Enhancement: YouTube API
```javascript
// Create highlight clip playlist
const playlistItems = highlights.map(h => ({
  videoId: gameYoutubeId,
  startAt: h.running_video_time,
  endAt: h.running_video_time + 10
}));
```

---

## Sync to Supabase

### Upload All Data
```bash
cd /path/to/benchsight
python supabase/sync_to_supabase.py --wipe
```

### Upload Specific Tables
```bash
python supabase/sync_to_supabase.py --tables fact_events fact_event_players
```

### Upload Specific Games
```bash
python supabase/sync_to_supabase.py --games 18969 18977 18981 18987
```

### Verify Upload
```sql
-- In Supabase SQL Editor
SELECT game_id, COUNT(*) as events 
FROM fact_events 
GROUP BY game_id 
ORDER BY game_id;
```

---

## Missing Columns to Add

### dim_schedule (for video integration)
```sql
ALTER TABLE dim_schedule ADD COLUMN youtube_url TEXT;
ALTER TABLE dim_schedule ADD COLUMN video_offset_seconds INTEGER DEFAULT 0;
ALTER TABLE dim_schedule ADD COLUMN video_duration_seconds INTEGER;
```

### fact_events (already present, verify)
```sql
-- These should already exist:
-- puck_x_start, puck_y_start, puck_x_end, puck_y_end
-- player_x, player_y
-- is_highlight
-- running_video_time
```

### New table: dim_highlight_clips (optional)
```sql
CREATE TABLE dim_highlight_clips (
    clip_id SERIAL PRIMARY KEY,
    game_id INTEGER,
    event_id INTEGER,
    clip_title TEXT,
    clip_description TEXT,
    start_time_seconds INTEGER,
    end_time_seconds INTEGER,
    youtube_clip_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Complete Checklist

### Data Capture (Tracker)
- [ ] XY data captured on rink clicks
- [ ] Highlights marked with H key
- [ ] Video time synced to period/time
- [ ] Export includes all XY columns

### ETL Processing
- [ ] XY columns populated in fact_events
- [ ] XY columns populated in fact_event_players
- [ ] is_highlight column populated
- [ ] running_video_time calculated correctly

### Supabase Upload
- [ ] Run: `python supabase/sync_to_supabase.py --wipe`
- [ ] Verify all games present
- [ ] Verify XY data populated
- [ ] Verify highlights flagged

### Video Integration
- [ ] YouTube URLs in dim_schedule
- [ ] Dashboard links to video timestamps
- [ ] Highlight reel generation script

---

## Quick Reference Commands

```bash
# Run full ETL
python -m src.etl_orchestrator full

# Sync to Supabase (all tables)
python supabase/sync_to_supabase.py --wipe

# Sync specific game
python supabase/sync_to_supabase.py --games 18987

# Verify in Supabase
SELECT game_id, COUNT(*) FROM fact_events GROUP BY game_id;
SELECT * FROM fact_events WHERE is_highlight = 1;
SELECT * FROM fact_events WHERE puck_x_start IS NOT NULL LIMIT 10;
```
