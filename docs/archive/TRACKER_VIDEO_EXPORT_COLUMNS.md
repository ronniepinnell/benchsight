# Tracker Video & Highlights Export Columns

This document specifies the exact columns the tracker needs to export for video and highlights functionality.

---

## Current Export Status

### ✅ Already Exported (in `events` sheet)

The tracker **already exports** these columns in the events sheet:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `is_highlight` | Integer | Highlight flag (1 = highlight, 0 = not) | `1` |
| `running_video_time` | Number | Video timestamp in seconds | `125.5` |

**Location:** `ui/tracker/index.html` line ~7136

### ⚠️ Needs to be Added: `video_url` Column

**IMPORTANT:** Each highlight needs its own YouTube link!

Add `video_url` column to events sheet for highlighted events:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `video_url` | Text | YouTube URL for this specific highlight | `https://youtube.com/watch?v=abc123` |

**When to include:**
- Only export `video_url` when `is_highlight = 1`
- Each highlight gets its own unique YouTube link
- Can be empty for highlights without individual videos

---

## Required: New Video Sheet Export

The tracker should **also export** a separate `video` sheet with video metadata.

### Video Sheet Columns

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `game_id` | Text | ✅ Yes | Game identifier | `19045` |
| `video_type` | Text | ✅ Yes | Type of video | `Full_Ice`, `Broadcast`, `Highlights` |
| `video_url` | Text | ⚠️ Optional | Video URL (YouTube, etc.) | `https://youtube.com/watch?v=abc123` |
| `duration_seconds` | Number | ⚠️ Optional | Total video duration | `3600` |
| `period_1_start` | Number | ✅ Yes | Period 1 start time (seconds) | `0` |
| `period_2_start` | Number | ⚠️ Optional | Period 2 start time (seconds) | `1200` |
| `period_3_start` | Number | ⚠️ Optional | Period 3 start time (seconds) | `2400` |
| `description` | Text | ⚠️ Optional | Video description | `Full ice camera view` |

**Minimum Required:** `game_id` + `video_type` + at least one `period_X_start`

---

## Export Structure

### Sheet 1: `events` (Already Exists)

**Key columns for highlights:**
- `is_highlight` - Already exported ✅
- `running_video_time` - Already exported ✅
- `event_type` - For highlight category mapping
- `event_detail` - For highlight description
- `event_player_1` - For highlight description
- `event_player_2` - For highlight description

### Sheet 2: `video` (NEW - Needs to be Added)

**One row per video type per game:**

```javascript
{
  game_id: S.gameId,
  video_type: 'Full_Ice',  // or 'Broadcast', 'Highlights', etc.
  video_url: S.videoTiming.youtubeUrl || '',
  duration_seconds: calculatedDuration || '',
  period_1_start: calculatePeriod1Start(),
  period_2_start: calculatePeriod2Start(),
  period_3_start: calculatePeriod3Start(),
  description: 'Full ice camera view of entire game'
}
```

---

## Implementation Guide

### Step 1: Add Video Sheet to Export

In the tracker's `exportData()` function, add a video sheet:

```javascript
// After creating events sheet
const videoSheet = [{
  game_id: S.gameId,
  video_type: 'Full_Ice',  // Default or from S.videoTiming
  video_url: S.videoTiming?.youtubeUrl || '',
  duration_seconds: calculateVideoDuration(),
  period_1_start: calculatePeriodStart(1),
  period_2_start: calculatePeriodStart(2),
  period_3_start: calculatePeriodStart(3),
  description: 'Full ice camera view of entire game'
}];

XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(videoSheet), 'video');
```

### Step 2: Calculate Period Start Times

```javascript
function calculatePeriodStart(period) {
  const periodLength = S.periodLength || 18; // minutes
  const intermission1 = S.videoTiming?.intermission1 || 900; // seconds
  const intermission2 = S.videoTiming?.intermission2 || 900; // seconds
  
  if (period === 1) return 0;
  if (period === 2) return (periodLength * 60) + intermission1;
  if (period === 3) return (periodLength * 60 * 2) + intermission1 + intermission2;
  
  return 0;
}
```

### Step 3: Get Video URL

```javascript
const videoUrl = S.videoTiming?.youtubeUrl || 
                 S.videoPlayer?.sources?.[0]?.url || 
                 '';
```

---

## Complete Column Reference

### Events Sheet (for Highlights)

**Required for highlights:**
- ✅ `is_highlight` - Already exported
- ✅ `running_video_time` - Already exported
- ✅ `event_type` - Already exported
- ✅ `event_detail` - Already exported
- ✅ `event_player_1` - Already exported (via player rows)
- ✅ `event_player_2` - Already exported (via player rows)
- ✅ `game_id` - Already exported
- ✅ `period` - Already exported
- ✅ `event_start_min` - Already exported
- ✅ `event_start_sec` - Already exported
- ✅ `duration` - Already exported
- ⚠️ `video_url` - **NEEDS TO BE ADDED** - Individual YouTube link per highlight

**Status:** ⚠️ **Need to add `video_url` column for individual highlight links**

### Video Sheet (NEW)

**Required columns:**
- `game_id` - Game identifier
- `video_type` - Type of video (Full_Ice, Broadcast, etc.)
- `period_1_start` - Period 1 start time in video (seconds)

**Optional but recommended:**
- `video_url` - YouTube/streaming URL
- `duration_seconds` - Total video duration
- `period_2_start` - Period 2 start time
- `period_3_start` - Period 3 start time
- `description` - Video description

**Status:** ⚠️ **Needs to be added to tracker export**

---

## Example Export

### Events Sheet (Existing)

| game_id | event_index | is_highlight | running_video_time | event_type | event_detail | ... |
|---------|-------------|--------------|-------------------|------------|--------------|-----|
| 19045   | 1001        | 1            | 125.5             | Goal       | Shot-OnNet   | ... |
| 19045   | 1002        | 0            | 150.2             | Pass       | Forehand      | ... |
| 19045   | 1003        | 1            | 450.8             | Save       | Save-Glove    | ... |

### Video Sheet (NEW)

| game_id | video_type | video_url                          | duration_seconds | period_1_start | period_2_start | period_3_start | description                    |
|---------|------------|------------------------------------|------------------|----------------|----------------|----------------|--------------------------------|
| 19045   | Full_Ice   | https://youtube.com/watch?v=abc123 | 3600             | 0              | 1200          | 2400          | Full ice camera view of entire game |

---

## Tracker State Variables

The tracker already has these video-related state variables:

```javascript
S.videoTiming = {
  videoStartOffset: 0,
  intermission1: 900,      // Seconds after P1
  intermission2: 900,      // Seconds after P2
  intermission3: 300,      // Seconds after P3 if OT
  timeouts: [],            // Array of timeout objects
  youtubeUrl: ''           // YouTube URL
}

S.videoPlayer = {
  sources: [],             // Array of video sources
  currentSourceIdx: 0,
  gameMarkers: {           // Video timestamps
    P1Start: null,
    P1End: null,
    P2Start: null,
    P2End: null,
    P3Start: null,
    P3End: null
  }
}
```

**These should be used to populate the video sheet!**

---

## Implementation Checklist

### For Events Sheet (Highlights)
- [x] `is_highlight` column - ✅ Already exported
- [x] `running_video_time` column - ✅ Already exported
- [x] All other event columns - ✅ Already exported

### For Video Sheet (NEW)
- [ ] Add `video` sheet to export
- [ ] Export `game_id`
- [ ] Export `video_type` (default: 'Full_Ice')
- [ ] Export `video_url` (from `S.videoTiming.youtubeUrl`)
- [ ] Calculate and export `period_1_start`
- [ ] Calculate and export `period_2_start` (if available)
- [ ] Calculate and export `period_3_start` (if available)
- [ ] Export `duration_seconds` (if available)
- [ ] Export `description` (optional)

---

## Quick Reference

### Minimum Video Export

```javascript
// Minimum required for ETL to work
{
  game_id: S.gameId,
  video_type: 'Full_Ice',
  period_1_start: 0
}
```

### Recommended Video Export

```javascript
// Full video metadata
{
  game_id: S.gameId,
  video_type: 'Full_Ice',
  video_url: S.videoTiming?.youtubeUrl || '',
  duration_seconds: calculateDuration(),
  period_1_start: 0,
  period_2_start: calculatePeriodStart(2),
  period_3_start: calculatePeriodStart(3),
  description: 'Full ice camera view of entire game'
}
```

---

## Notes

1. **Events sheet is complete** - All highlight columns already exported ✅
2. **Video sheet needs to be added** - New sheet with video metadata ⚠️
3. **Period start times** - Can be calculated from `S.videoTiming` and period lengths
4. **Video URL** - Available in `S.videoTiming.youtubeUrl`
5. **Multiple videos** - Can export multiple rows (one per video type) if needed

---

## Summary

### ✅ Already Working
- Highlights: `is_highlight` and `running_video_time` are exported in events sheet

### ⚠️ Needs Implementation
- Video sheet: Add new `video` sheet to tracker export with video metadata

### 📋 Required Columns for Video Sheet
1. `game_id` (required)
2. `video_type` (required, default: 'Full_Ice')
3. `period_1_start` (required, default: 0)
4. `video_url` (optional but recommended)
5. `period_2_start` (optional)
6. `period_3_start` (optional)
7. `duration_seconds` (optional)
8. `description` (optional)
