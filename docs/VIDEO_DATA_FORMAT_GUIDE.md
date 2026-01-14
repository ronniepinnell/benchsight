# Video Data Format Guide

This guide explains how to format raw video Excel files for the ETL process.

## Table of Contents
1. [File Naming](#file-naming)
2. [File Location](#file-location)
3. [Sheet Structure](#sheet-structure)
4. [Column Formats](#column-formats)
5. [Data Examples](#data-examples)
6. [Best Practices](#best-practices)
7. [Common Issues](#common-issues)

---

## File Naming

### Option 1: Standalone Video File (Recommended)
```
data/raw/games/{game_id}/{game_id}_video.xlsx
data/raw/games/{game_id}/video.xlsx
data/raw/games/{game_id}/video_times.xlsx
```

**Examples:**
- `data/raw/games/19045/19045_video.xlsx`
- `data/raw/games/19045/video.xlsx`
- `data/raw/games/19045/video_times.xlsx`

### Option 2: Video Sheet in Tracking File
```
data/raw/games/{game_id}/{game_id}_tracking.xlsx
```
- Must have a sheet named: `video`, `Video`, `video_times`, or `Video_Times`

---

## File Location

```
data/raw/games/
├── 19045/
│   ├── 19045_tracking.xlsx  (events, shifts)
│   └── 19045_video.xlsx      (video data) ← Put video file here
├── 19046/
│   ├── 19046_tracking.xlsx
│   └── 19046_video.xlsx
└── 19047/
    ├── 19047_tracking.xlsx
    └── video.xlsx            (also works)
```

---

## Sheet Structure

### Sheet Name Options
The ETL will look for sheets in this order:
1. `video` (preferred)
2. `video_times`
3. `Video` (case-insensitive)
4. `Video_Times`
5. First sheet in workbook (if no video sheet found)

### Sheet Layout
- **One row per video** (if multiple video types per game)
- **Header row** in first row
- **Data rows** starting from row 2

---

## Column Formats

### Required Columns (at least one of these)

| Column Name Options | Description | Example |
|---------------------|-------------|---------|
| `game_id`, `Game_ID`, `game_id_num` | Game identifier | `19045` |
| `video_url`, `url_1`, `url`, `URL`, `youtube_url`, `video_link` | Video URL | `https://youtube.com/watch?v=abc123` |
| `period_1_start`, `p1_start`, `period1_start`, `P1`, `period1` | Period 1 start time (seconds) | `0` |
| `period_2_start`, `p2_start`, `period2_start`, `P2`, `period2` | Period 2 start time (seconds) | `1200` |
| `period_3_start`, `p3_start`, `period3_start`, `P3`, `period3` | Period 3 start time (seconds) | `2400` |

### Optional Columns

| Column Name Options | Description | Example |
|---------------------|-------------|---------|
| `video_type`, `Video_Type`, `type` | Type of video | `Full_Ice`, `Broadcast`, `Highlights` |
| `description`, `video_description`, `desc`, `notes`, `comment` | Video description | `Full ice camera view of entire game` |
| `duration_seconds`, `duration`, `video_duration`, `total_duration`, `length_seconds` | Total video duration | `3600` |
| `url_2`, `url_3`, `url_4` | Additional video URLs | `https://youtube.com/watch?v=xyz789` |
| `video_id`, `Video_ID` | YouTube video ID | `abc123` |
| `extension` | Video extension/parameters | `v=abc123` |

---

## Data Examples

### Example 1: Minimal Format (Just Period Times)

**File:** `19045_video.xlsx`  
**Sheet:** `video`

| game_id | period_1_start | period_2_start | period_3_start |
|---------|----------------|---------------|---------------|
| 19045   | 0              | 1200          | 2400          |

**Result:** Creates video record with period start times only.

---

### Example 2: Complete Format (Recommended)

**File:** `19045_video.xlsx`  
**Sheet:** `video`

| game_id | video_type | video_url                          | duration_seconds | period_1_start | period_2_start | period_3_start | description                    |
|---------|------------|------------------------------------|------------------|----------------|----------------|----------------|--------------------------------|
| 19045   | Full_Ice   | https://youtube.com/watch?v=abc123 | 3600             | 0              | 1200          | 2400          | Full ice camera view of entire game |
| 19045   | Broadcast  | https://youtube.com/watch?v=xyz789 | 3600             | 0              | 1200          | 2400          | Television broadcast feed     |

**Result:** Creates two video records with full metadata.

---

### Example 3: Alternative Column Names

**File:** `19045_video.xlsx`  
**Sheet:** `video`

| Game_ID | Video_Type | URL_1                              | Duration | P1_Start | P2_Start | P3_Start | Notes                          |
|---------|------------|------------------------------------|----------|----------|----------|----------|--------------------------------|
| 19045    | Full_Ice   | https://youtube.com/watch?v=abc123 | 3600     | 0        | 1200     | 2400     | Main game feed                 |

**Result:** Works! The ETL normalizes column names (case-insensitive, handles spaces/underscores).

---

### Example 4: Video Sheet in Tracking File

**File:** `19045_tracking.xlsx`  
**Sheets:** `events`, `shifts`, `video` ← Add video sheet here

**Sheet: `video`**

| game_id | video_type | url                                | period1 | period2 | period3 | desc                    |
|---------|------------|------------------------------------|---------|---------|---------|-------------------------|
| 19045   | Full_Ice   | https://youtube.com/watch?v=abc123 | 0       | 1200    | 2400    | Full ice camera view    |

**Result:** Video data extracted from tracking file.

---

### Example 5: Multiple Videos Per Game

**File:** `19045_video.xlsx`  
**Sheet:** `video`

| game_id | video_type | video_url                          | period_1_start | period_2_start | period_3_start | description                    |
|---------|------------|------------------------------------|----------------|----------------|----------------|--------------------------------|
| 19045   | Full_Ice   | https://youtube.com/watch?v=abc123 | 0              | 1200          | 2400          | Full ice camera view           |
| 19045   | Broadcast  | https://youtube.com/watch?v=xyz789 | 0              | 1200          | 2400          | Television broadcast           |
| 19045   | Goalie     | https://youtube.com/watch?v=def456 | 0              | 1200          | 2400          | Goalie camera view             |

**Result:** Creates three video records, each with unique `video_key`:
- `V19045FULL` (Full_Ice)
- `V19045BROA` (Broadcast)
- `V19045GOAL` (Goalie)

---

## Best Practices

### 1. Use Consistent File Names
✅ **Good:**
```
19045_video.xlsx
19046_video.xlsx
19047_video.xlsx
```

❌ **Avoid:**
```
game_19045_video.xlsx
video_19045.xlsx
19045_vid.xlsx
```

### 2. Use Standard Column Names
✅ **Preferred:**
- `game_id`
- `video_type`
- `video_url` or `url_1`
- `period_1_start`, `period_2_start`, `period_3_start`
- `description`

### 3. Include Video Type
Always include `video_type` column:
- `Full_Ice` (primary, used for highlights)
- `Broadcast`
- `Highlights`
- `Goalie`
- `Overhead`
- `Other`

### 4. Include Descriptions
Add `description` column for clarity:
- `"Full ice camera view of entire game"`
- `"Television broadcast feed"`
- `"Goalie camera view"`

### 5. Period Times in Seconds
✅ **Correct:**
- Period 1: `0`
- Period 2: `1200` (20 minutes = 1200 seconds)
- Period 3: `2400` (40 minutes = 2400 seconds)

❌ **Incorrect:**
- Period 2: `20:00` (use seconds, not MM:SS)
- Period 2: `20` (use total seconds from video start)

### 6. Video URLs
✅ **Supported formats:**
- `https://youtube.com/watch?v=abc123`
- `https://youtu.be/abc123`
- `https://youtube.com/embed/abc123`
- Any valid URL

---

## Template Files

### Template 1: Minimal (Period Times Only)

**File:** `{game_id}_video.xlsx`  
**Sheet:** `video`

| game_id | period_1_start | period_2_start | period_3_start |
|---------|----------------|---------------|---------------|
|         |                |               |               |

**Copy this template and fill in values.**

---

### Template 2: Complete (Recommended)

**File:** `{game_id}_video.xlsx`  
**Sheet:** `video`

| game_id | video_type | video_url | duration_seconds | period_1_start | period_2_start | period_3_start | description |
|---------|------------|-----------|------------------|----------------|----------------|----------------|-------------|
|         |            |           |                  |                |                |                |             |

**Copy this template and fill in values.**

---

### Template 3: Multiple Videos

**File:** `{game_id}_video.xlsx`  
**Sheet:** `video`

| game_id | video_type | video_url | duration_seconds | period_1_start | period_2_start | period_3_start | description |
|---------|------------|-----------|------------------|----------------|----------------|----------------|-------------|
|         | Full_Ice   |           |                  |                |                |                |             |
|         | Broadcast  |           |                  |                |                |                |             |

**Add one row per video type.**

---

## Common Issues

### Issue 1: File Not Found

**Problem:** ETL doesn't find video file.

**Solutions:**
- ✅ Place file in: `data/raw/games/{game_id}/`
- ✅ Name file: `{game_id}_video.xlsx` or `video.xlsx`
- ✅ Check file extension is `.xlsx` (not `.xls`)

### Issue 2: Sheet Not Found

**Problem:** ETL doesn't find video sheet.

**Solutions:**
- ✅ Name sheet: `video` or `video_times`
- ✅ Case doesn't matter: `Video`, `VIDEO` also work
- ✅ If using tracking file, add `video` sheet

### Issue 3: Column Names Not Recognized

**Problem:** Data not extracted from columns.

**Solutions:**
- ✅ Use standard names: `game_id`, `video_url`, `period_1_start`
- ✅ Or use alternatives: `Game_ID`, `URL_1`, `P1_Start`
- ✅ Check for typos in column names
- ✅ Ensure first row is header row

### Issue 4: Period Times Wrong Format

**Problem:** Period times not extracted correctly.

**Solutions:**
- ✅ Use seconds (numbers): `0`, `1200`, `2400`
- ❌ Don't use time format: `00:00:00`, `20:00`
- ✅ Calculate: Period 2 = Period 1 duration + intermission

### Issue 5: Multiple Rows, Only One Processed

**Problem:** Only first video row processed.

**Solutions:**
- ✅ Each video type should be on separate row
- ✅ Include `video_type` column to differentiate
- ✅ All rows will be processed (one record per row)

### Issue 6: Video Key Conflicts

**Problem:** Duplicate `video_key` values.

**Solutions:**
- ✅ Include `video_type` column (creates unique keys)
- ✅ Each video type gets unique key: `V{game_id}{type_abbrev}`
- ✅ Example: `V19045FULL`, `V19045BROA`

---

## Quick Reference

### Minimum Required Data
```
game_id + (video_url OR period_1_start OR period_2_start OR period_3_start)
```

### Recommended Data
```
game_id + video_type + video_url + period_1_start + period_2_start + period_3_start + description
```

### File Structure
```
data/raw/games/
└── {game_id}/
    ├── {game_id}_tracking.xlsx  (events, shifts)
    └── {game_id}_video.xlsx      (video data) ← Required
```

### Column Flexibility
The ETL is flexible with column names:
- Case-insensitive: `game_id` = `Game_ID` = `GAME_ID`
- Spaces/underscores: `period_1_start` = `period 1 start` = `Period 1 Start`
- Common variations: `url_1` = `url` = `video_url` = `youtube_url`

---

## Example: Complete Workflow

### Step 1: Create Video File
1. Create Excel file: `19045_video.xlsx`
2. Create sheet: `video`
3. Add headers: `game_id`, `video_type`, `video_url`, `period_1_start`, `period_2_start`, `period_3_start`, `description`
4. Add data row with game information

### Step 2: Place File
```
data/raw/games/19045/19045_video.xlsx
```

### Step 3: Run ETL
The ETL will:
1. Find file: `19045_video.xlsx`
2. Read sheet: `video`
3. Extract data with flexible column matching
4. Create record in `fact_video` table
5. Generate `video_key`: `V19045FULL`

### Step 4: Verify
```sql
SELECT * FROM fact_video WHERE game_id = '19045';
```

---

## Need Help?

If you encounter issues:
1. Check file location and naming
2. Verify sheet name is `video` or `video_times`
3. Ensure column names match examples above
4. Check data types (period times should be numbers)
5. Review error messages in ETL log
