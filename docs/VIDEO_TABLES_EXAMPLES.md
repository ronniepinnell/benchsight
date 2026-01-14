# Video Tables Examples

This document provides examples of the video and highlights table structure, data formats, and usage.

## Table of Contents
1. [Excel File Format Examples](#excel-file-format-examples)
2. [fact_video Table Examples](#fact_video-table-examples)
3. [fact_highlights Table Examples](#fact_highlights-table-examples)
4. [SQL Query Examples](#sql-query-examples)
5. [Use Case Examples](#use-case-examples)

---

## Excel File Format Examples

### Example 1: Simple Video File (`19045_video.xlsx`)

**Sheet: "video"**

| game_id | video_type | video_url | duration_seconds | period_1_start | period_2_start | period_3_start | description |
|---------|------------|-----------|------------------|----------------|----------------|----------------|-------------|
| 19045 | Full_Ice | https://youtube.com/watch?v=abc123 | 3600 | 0 | 1200 | 2400 | Full ice camera view of entire game |
| 19045 | Broadcast | https://youtube.com/watch?v=xyz789 | 3600 | 0 | 1200 | 2400 | Television broadcast feed |

### Example 2: Video Times File (`video_times.xlsx`)

**Sheet: "video_times"**

| Game_ID | Video_Type | URL_1 | Duration | P1_Start | P2_Start | P3_Start | Notes |
|---------|------------|-------|----------|----------|----------|----------|-------|
| 19045 | Full_Ice | https://youtube.com/watch?v=abc123 | 3600 | 0 | 1200 | 2400 | Main game feed |
| 19046 | Broadcast | https://youtube.com/watch?v=def456 | 3300 | 0 | 1100 | 2200 | TV broadcast |

### Example 3: Video Sheet in Tracking File (`19045_tracking.xlsx`)

**Sheet: "video"**

| video_type | url | duration | period1 | period2 | period3 | desc |
|------------|-----|----------|---------|---------|---------|------|
| Full_Ice | https://youtube.com/watch?v=abc123 | 3600 | 0 | 1200 | 2400 | Full game recording |

---

## fact_video Table Examples

### Example Data

```csv
video_key,game_id,video_type,video_description,video_url,duration_seconds,period_1_start,period_2_start,period_3_start,_export_timestamp
V19045FULL,19045,Full_Ice,Full ice camera view of entire game,https://youtube.com/watch?v=abc123,3600,0,1200,2400,2024-01-15T10:30:00
V19045BROA,19045,Broadcast,Television broadcast feed,https://youtube.com/watch?v=xyz789,3600,0,1200,2400,2024-01-15T10:30:00
V19046FULL,19046,Full_Ice,Full ice camera view of entire game,https://youtube.com/watch?v=def456,3300,0,1100,2200,2024-01-15T10:30:00
V19047HIGH,19047,Highlights,Compilation of game highlights,https://youtube.com/watch?v=ghi789,600,,,2024-01-15T10:30:00
```

### Example: Multiple Video Types Per Game

For game 19045, you might have:
- **V19045FULL**: Full ice camera (primary video for highlights)
- **V19045BROA**: Broadcast feed (alternative view)
- **V19045GOAL**: Goalie camera (specialty view)

---

## fact_highlights Table Examples

### Example Data

```csv
highlight_key,event_id,game_id,video_key,period,event_type,event_detail,video_start_time,video_end_time,duration_seconds,event_time_display,description,event_player_1,event_player_2,team_id,_export_timestamp
H19045EV001,EV19045001,19045,V19045FULL,1,Goal,Shot-OnNet,125,135,10,P1 5:25,Goal - Shot-OnNet - by John Smith - assist Mike Jones,John Smith,Mike Jones,TEAM001,2024-01-15T10:30:00
H19045EV002,EV19045015,19045,V19045FULL,1,Save,Save-Glove,450,460,10,P1 12:30,Save - Save-Glove - by Goalie Name,,Goalie Name,TEAM002,2024-01-15T10:30:00
H19045EV003,EV19045042,19045,V19045FULL,2,Goal,Shot-OnNet,1325,1335,10,P2 8:05,Goal - Shot-OnNet - by Jane Doe,,Jane Doe,TEAM001,2024-01-15T10:30:00
H19045EV004,EV19045058,19045,V19045FULL,2,Hit,Body-Check,1450,1455,5,P2 10:10,Hit - Body-Check - by Player Name,,Player Name,TEAM002,2024-01-15T10:30:00
H19045EV005,EV19045089,19045,V19045FULL,3,Goal,Shot-OnNet,2525,2535,10,P3 6:05,Goal - Shot-OnNet - by Bob Wilson - assist Tom Brown,Bob Wilson,Tom Brown,TEAM001,2024-01-15T10:30:00
```

### Example: Highlight Description Generation

The system auto-generates descriptions based on event details:

| Event Type | Event Detail | Player 1 | Player 2 | Generated Description |
|------------|--------------|----------|----------|----------------------|
| Goal | Shot-OnNet | John Smith | Mike Jones | Goal - Shot-OnNet - by John Smith - assist Mike Jones |
| Save | Save-Glove | | Goalie Name | Save - Save-Glove - by Goalie Name |
| Hit | Body-Check | Player Name | | Hit - Body-Check - by Player Name |
| Goal | Shot-OnNet | Jane Doe | | Goal - Shot-OnNet - by Jane Doe |

---

## SQL Query Examples

### 1. Get All Videos for a Game

```sql
SELECT 
    video_key,
    video_type,
    video_description,
    video_url,
    duration_seconds,
    period_1_start,
    period_2_start,
    period_3_start
FROM fact_video
WHERE game_id = '19045'
ORDER BY 
    CASE video_type 
        WHEN 'Full_Ice' THEN 1 
        WHEN 'Broadcast' THEN 2 
        ELSE 3 
    END;
```

**Result:**
```
video_key    | video_type | video_description                    | video_url                          | duration_seconds | period_1_start | period_2_start | period_3_start
-------------|------------|-------------------------------------|------------------------------------|------------------|----------------|----------------|---------------
V19045FULL   | Full_Ice   | Full ice camera view of entire game | https://youtube.com/watch?v=abc123 | 3600             | 0              | 1200           | 2400
V19045BROA   | Broadcast  | Television broadcast feed          | https://youtube.com/watch?v=xyz789 | 3600             | 0              | 1200           | 2400
```

### 2. Get All Highlights for a Game with Video Info

```sql
SELECT 
    h.highlight_key,
    h.event_time_display,
    h.description,
    h.event_type,
    h.event_player_1,
    h.video_start_time,
    h.video_end_time,
    v.video_url,
    v.video_type,
    v.video_description
FROM fact_highlights h
JOIN fact_video v ON h.video_key = v.video_key
WHERE h.game_id = '19045'
ORDER BY CAST(h.video_start_time AS INTEGER);
```

**Result:**
```
highlight_key | event_time_display | description                                    | event_type | event_player_1 | video_start_time | video_end_time | video_url                          | video_type | video_description
--------------|-------------------|------------------------------------------------|------------|----------------|------------------|----------------|------------------------------------|------------|-------------------
H19045EV001   | P1 5:25           | Goal - Shot-OnNet - by John Smith - assist... | Goal       | John Smith     | 125              | 135            | https://youtube.com/watch?v=abc123 | Full_Ice   | Full ice camera view...
H19045EV002   | P1 12:30          | Save - Save-Glove - by Goalie Name            | Save       |                | 450              | 460            | https://youtube.com/watch?v=abc123 | Full_Ice   | Full ice camera view...
H19045EV003   | P2 8:05           | Goal - Shot-OnNet - by Jane Doe               | Goal       | Jane Doe       | 1325             | 1335           | https://youtube.com/watch?v=abc123 | Full_Ice   | Full ice camera view...
```

### 3. Create Highlight Reel with YouTube Timestamps

```sql
SELECT 
    h.description,
    h.event_time_display,
    CONCAT(
        v.video_url,
        '&t=',
        h.video_start_time,
        's'
    ) AS youtube_url_with_timestamp,
    h.video_start_time,
    h.video_end_time,
    h.duration_seconds
FROM fact_highlights h
JOIN fact_video v ON h.video_key = v.video_key
WHERE h.game_id = '19045'
  AND h.event_type = 'Goal'
ORDER BY CAST(h.video_start_time AS INTEGER);
```

**Result:**
```
description                          | event_time_display | youtube_url_with_timestamp                    | video_start_time | video_end_time | duration_seconds
-------------------------------------|-------------------|-----------------------------------------------|------------------|----------------|-----------------
Goal - Shot-OnNet - by John Smith... | P1 5:25           | https://youtube.com/watch?v=abc123&t=125s     | 125              | 135            | 10
Goal - Shot-OnNet - by Jane Doe      | P2 8:05           | https://youtube.com/watch?v=abc123&t=1325s    | 1325             | 1335           | 10
Goal - Shot-OnNet - by Bob Wilson... | P3 6:05           | https://youtube.com/watch?v=abc123&t=2525s   | 2525             | 2535           | 10
```

### 4. Get Highlights by Player

```sql
SELECT 
    h.event_time_display,
    h.description,
    h.event_type,
    h.video_start_time,
    v.video_url
FROM fact_highlights h
JOIN fact_video v ON h.video_key = v.video_key
WHERE h.event_player_1 = 'John Smith'
   OR h.event_player_2 = 'John Smith'
ORDER BY h.game_id, CAST(h.video_start_time AS INTEGER);
```

### 5. Get Video Statistics

```sql
SELECT 
    v.video_type,
    COUNT(DISTINCT v.game_id) AS games_with_video,
    COUNT(DISTINCT h.highlight_key) AS total_highlights,
    AVG(CAST(h.duration_seconds AS INTEGER)) AS avg_highlight_duration
FROM fact_video v
LEFT JOIN fact_highlights h ON v.video_key = h.video_key
GROUP BY v.video_type
ORDER BY games_with_video DESC;
```

### 6. Find Games with Video but No Highlights

```sql
SELECT 
    v.game_id,
    v.video_type,
    v.video_url,
    COUNT(h.highlight_key) AS highlight_count
FROM fact_video v
LEFT JOIN fact_highlights h ON v.video_key = h.video_key
GROUP BY v.game_id, v.video_type, v.video_url
HAVING COUNT(h.highlight_key) = 0;
```

---

## Use Case Examples

### Use Case 1: Generate Highlight Reel Script

```python
# Python example to generate highlight reel
import pandas as pd

# Load highlights
highlights = pd.read_csv('data/output/fact_highlights.csv')
videos = pd.read_csv('data/output/fact_video.csv')

# Filter for specific game
game_id = '19045'
game_highlights = highlights[highlights['game_id'] == game_id]
game_video = videos[(videos['game_id'] == game_id) & 
                    (videos['video_type'] == 'Full_Ice')].iloc[0]

# Generate script
print(f"Highlight Reel for Game {game_id}")
print(f"Video: {game_video['video_url']}\n")

for idx, highlight in game_highlights.iterrows():
    start_time = int(highlight['video_start_time'])
    end_time = int(highlight['video_end_time'])
    minutes = start_time // 60
    seconds = start_time % 60
    
    print(f"{highlight['event_time_display']} - {highlight['description']}")
    print(f"  Clip: {minutes}:{seconds:02d} to {end_time // 60}:{end_time % 60:02d}")
    print(f"  URL: {game_video['video_url']}&t={start_time}s\n")
```

**Output:**
```
Highlight Reel for Game 19045
Video: https://youtube.com/watch?v=abc123

P1 5:25 - Goal - Shot-OnNet - by John Smith - assist Mike Jones
  Clip: 2:05 to 2:15
  URL: https://youtube.com/watch?v=abc123&t=125s

P1 12:30 - Save - Save-Glove - by Goalie Name
  Clip: 7:30 to 7:40
  URL: https://youtube.com/watch?v=abc123&t=450s
...
```

### Use Case 2: Dashboard Display

```typescript
// TypeScript/React example for dashboard
interface Highlight {
  highlight_key: string;
  event_time_display: string;
  description: string;
  video_start_time: number;
  video_end_time: number;
  video_url: string;
}

function GameHighlights({ gameId }: { gameId: string }) {
  const highlights = useQuery(`
    SELECT 
      h.highlight_key,
      h.event_time_display,
      h.description,
      h.video_start_time,
      h.video_end_time,
      v.video_url
    FROM fact_highlights h
    JOIN fact_video v ON h.video_key = v.video_key
    WHERE h.game_id = $1
    ORDER BY CAST(h.video_start_time AS INTEGER)
  `, [gameId]);

  return (
    <div>
      <h2>Game Highlights</h2>
      {highlights.map(hl => (
        <HighlightCard
          key={hl.highlight_key}
          time={hl.event_time_display}
          description={hl.description}
          videoUrl={`${hl.video_url}&t=${hl.video_start_time}s`}
          startTime={hl.video_start_time}
          endTime={hl.video_end_time}
        />
      ))}
    </div>
  );
}
```

### Use Case 3: Export Highlights for Video Editor

```sql
-- Export highlights in format for video editing software
SELECT 
    h.highlight_key AS 'Clip Name',
    h.description AS 'Description',
    h.video_start_time AS 'Start (seconds)',
    h.video_end_time AS 'End (seconds)',
    h.duration_seconds AS 'Duration (seconds)',
    h.event_time_display AS 'Game Time',
    v.video_url AS 'Source Video'
FROM fact_highlights h
JOIN fact_video v ON h.video_key = v.video_key
WHERE h.game_id = '19045'
ORDER BY CAST(h.video_start_time AS INTEGER)
INTO OUTFILE '/tmp/highlights_19045.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

### Use Case 4: Video Type Analysis

```sql
-- Analyze which video types are most common
SELECT 
    v.video_type,
    COUNT(DISTINCT v.game_id) AS games,
    COUNT(DISTINCT h.highlight_key) AS highlights_linked,
    ROUND(
        COUNT(DISTINCT h.highlight_key)::NUMERIC / 
        NULLIF(COUNT(DISTINCT v.game_id), 0), 
        2
    ) AS avg_highlights_per_game
FROM fact_video v
LEFT JOIN fact_highlights h ON v.video_key = h.video_key
GROUP BY v.video_type
ORDER BY games DESC;
```

**Result:**
```
video_type | games | highlights_linked | avg_highlights_per_game
-----------|-------|-------------------|------------------------
Full_Ice   | 150   | 450               | 3.00
Broadcast  | 120   | 360               | 3.00
Highlights | 50    | 0                 | 0.00
Goalie     | 10    | 25                | 2.50
```

---

## Data Relationships Diagram

```
dim_schedule (game_id)
    │
    ├── fact_video (game_id → video_key)
    │       │
    │       └── fact_highlights (video_key)
    │               │
    │               └── fact_events (event_id)
    │
    └── fact_events (game_id, is_highlight = 1)
            │
            └── fact_highlights (event_id)
```

**Key Relationships:**
- `fact_highlights.video_key` → `fact_video.video_key` (FK)
- `fact_highlights.event_id` → `fact_events.event_id` (FK)
- `fact_highlights.game_id` → `dim_schedule.game_id` (FK)
- `fact_video.game_id` → `dim_schedule.game_id` (FK)

---

## Notes

1. **Video Key Format**: `V{game_id}{video_type_abbrev}`
   - Example: `V19045FULL` = Game 19045, Full_Ice type

2. **Highlight Key Format**: `H{game_id}{event_id_suffix}`
   - Example: `H19045EV001` = Game 19045, Event 001

3. **Video Types**: Common types include:
   - `Full_Ice`: Primary game video (used for highlights)
   - `Broadcast`: TV/streaming broadcast
   - `Highlights`: Pre-made highlight reel
   - `Goalie`: Goalie camera view
   - `Overhead`: Overhead camera
   - `Other`: Other video types

4. **Period Start Times**: Stored in seconds from video start
   - Period 1 typically starts at 0
   - Period 2 starts after P1 + intermission (usually ~1200 seconds)
   - Period 3 starts after P2 + intermission (usually ~2400 seconds)

5. **Highlight Duration**: Defaults to 10 seconds if not specified
   - Goals: Usually 10-15 seconds
   - Saves: Usually 5-10 seconds
   - Other events: Varies by importance
