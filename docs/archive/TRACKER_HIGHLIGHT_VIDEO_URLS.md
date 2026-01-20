# Tracker: Individual Highlight Video URLs

## Overview

**Each highlight has its own YouTube link.** This means:
- 1 highlight = 1 YouTube URL
- Each highlight is a separate video clip
- Highlights are NOT linked to a single game video

---

## Data Model Update

### `fact_highlights` Table

**Updated Schema:**
```sql
CREATE TABLE fact_highlights (
    highlight_key TEXT PRIMARY KEY,
    event_id TEXT,
    game_id TEXT,
    video_key TEXT,           -- Optional: FK to fact_video (for full game videos)
    video_url TEXT,           -- REQUIRED: Individual YouTube link for this highlight
    highlight_category_id TEXT,
    period TEXT,
    event_type TEXT,
    event_detail TEXT,
    video_start_time TEXT,    -- Start time in the highlight video (usually 0)
    video_end_time TEXT,      -- End time in the highlight video
    duration_seconds TEXT,
    description TEXT,
    ...
);
```

**Key Points:**
- `video_url` = Individual YouTube link for THIS highlight
- `video_key` = Optional link to full game video (if available)
- Each highlight is a standalone video clip

---

## Tracker Export Requirements

### Events Sheet

**For highlighted events (`is_highlight = 1`), export:**

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `is_highlight` | Integer | ✅ Yes | Highlight flag | `1` |
| `video_url` | Text | ✅ Yes | YouTube link for this highlight | `https://youtube.com/watch?v=abc123` |
| `running_video_time` | Number | ⚠️ Optional | Time in full game video (if available) | `125.5` |
| `event_type` | Text | ✅ Yes | Event type | `Goal` |
| `event_detail` | Text | ✅ Yes | Event detail | `Shot-OnNet` |
| `game_id` | Text | ✅ Yes | Game identifier | `19045` |
| `period` | Integer | ✅ Yes | Period number | `1` |
| `duration` | Number | ⚠️ Optional | Clip duration | `10` |

**Export Logic:**
```javascript
// In exportData() function
const base = {
  // ... existing columns ...
  'is_highlight': evt.isHighlight ? 1 : 0,
  'video_url': evt.isHighlight ? (evt.videoUrl || '') : '',  // Only for highlights
  'running_video_time': evt.videoTime || eventRunningStart,
  // ... rest of columns ...
};
```

---

## Tracker Implementation

### Step 1: Add Video URL Field to Event Object

When logging an event, allow user to add video URL for highlights:

```javascript
const evt = {
  idx: S.evtIdx++,
  game_id: S.gameId,
  period: S.period,
  // ... existing fields ...
  isHighlight: document.getElementById('isHighlight').checked,
  videoUrl: evt.isHighlight ? document.getElementById('evtVideoUrl').value : '',  // NEW
  // ... rest of fields ...
};
```

### Step 2: Add UI Input for Video URL

Add input field in event form (only show when highlight is checked):

```html
<input type="checkbox" id="isHighlight" onchange="toggleHighlightFields()"> ⭐ Highlight

<div id="highlightFields" style="display:none;">
  <label>YouTube URL for this highlight:</label>
  <input type="text" id="evtVideoUrl" placeholder="https://youtube.com/watch?v=...">
</div>

<script>
function toggleHighlightFields() {
  const isHighlight = document.getElementById('isHighlight').checked;
  document.getElementById('highlightFields').style.display = isHighlight ? 'block' : 'none';
}
</script>
```

### Step 3: Export Video URL in Events Sheet

```javascript
// In exportData() function
S.events.forEach((evt, i) => {
  const base = {
    // ... existing columns ...
    'is_highlight': evt.isHighlight ? 1 : 0,
    'video_url': evt.isHighlight && evt.videoUrl ? evt.videoUrl : '',  // Individual highlight URL
    'running_video_time': evt.videoTime || eventRunningStart,
    // ... rest of columns ...
  };
  
  rows.push(base);
});
```

---

## Example Export

### Events Sheet

| game_id | event_index | is_highlight | video_url                          | running_video_time | event_type | event_detail | ... |
|---------|-------------|--------------|------------------------------------|-------------------|------------|--------------|-----|
| 19045   | 1001        | 1            | https://youtube.com/watch?v=abc123 | 125.5             | Goal       | Shot-OnNet   | ... |
| 19045   | 1002        | 0            |                                    | 150.2             | Pass       | Forehand      | ... |
| 19045   | 1003        | 1            | https://youtube.com/watch?v=xyz789 | 450.8             | Save       | Save-Glove    | ... |

**Note:** 
- Only highlighted events have `video_url` populated
- Each highlight has its own unique YouTube link
- `running_video_time` is optional (for full game video sync)

---

## ETL Processing

The ETL will:

1. **Read events** where `is_highlight = 1`
2. **Extract `video_url`** from each highlighted event
3. **Create `fact_highlights` records** with:
   - `video_url` = Individual YouTube link from event
   - `video_key` = Optional link to full game video (if `fact_video` exists)
   - All other highlight metadata

---

## Updated fact_highlights Structure

```python
{
    'highlight_key': 'H19045EV001',
    'event_id': 'EV19045001',
    'game_id': '19045',
    'video_key': 'V19045FULL',  # Optional: full game video
    'video_url': 'https://youtube.com/watch?v=abc123',  # REQUIRED: individual highlight
    'highlight_category_id': 'HC0001',
    'period': '1',
    'event_type': 'Goal',
    'event_detail': 'Shot-OnNet',
    'video_start_time': '0',  # Usually 0 for individual clips
    'video_end_time': '10',   # Clip duration
    'duration_seconds': '10',
    'description': 'Goal - Shot-OnNet - by John Smith',
    ...
}
```

---

## Summary

### Key Changes

1. **`fact_highlights.video_url`** - Individual YouTube link per highlight ✅ Added
2. **Tracker export** - Add `video_url` column to events sheet for highlights ⚠️ Needs implementation
3. **Event object** - Add `videoUrl` field to event when `isHighlight = true` ⚠️ Needs implementation

### Export Columns for Highlights

**Required:**
- `is_highlight` = 1
- `video_url` = Individual YouTube link
- `event_type` = Event type
- `event_detail` = Event detail
- `game_id` = Game identifier

**Optional:**
- `running_video_time` = Time in full game video (if available)
- `duration` = Clip duration

---

## Implementation Checklist

### Tracker Changes
- [ ] Add `videoUrl` field to event object
- [ ] Add UI input for video URL (shown when highlight checked)
- [ ] Export `video_url` column in events sheet (only for highlights)

### ETL Changes
- [x] Add `video_url` column to `fact_highlights` table
- [x] Extract `video_url` from events when creating highlights
- [x] Update SQL schema

### Database
- [x] `fact_highlights.video_url` column added
- [x] Schema updated

---

## Notes

- **Each highlight = 1 YouTube link** - This is the key requirement
- **Full game videos** - Still supported via `fact_video` table (optional)
- **Video timing** - For individual clips, `video_start_time` is usually 0
- **Clip duration** - Can be extracted from YouTube or specified manually
