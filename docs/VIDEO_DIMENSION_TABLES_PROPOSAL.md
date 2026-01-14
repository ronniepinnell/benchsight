# Video & Highlights Dimension Tables Proposal

## Overview

This proposal adds dimension tables for video types and highlight categories to improve data integrity, maintainability, and queryability.

## Problem Statement

Currently, video types and highlight categories are stored as text strings in fact tables:
- `fact_video.video_type` = "Full_Ice", "Broadcast", etc. (free text)
- `fact_highlights` has no category field (only event_type)

**Issues:**
- No data validation (typos, inconsistent naming)
- No metadata (descriptions, icons, priorities)
- Hard to filter/group by type
- No referential integrity

## Solution

### 1. `dim_video_type` Table

**Purpose:** Define all valid video types with metadata.

**Schema:**
```sql
CREATE TABLE dim_video_type (
    video_type_id TEXT PRIMARY KEY,        -- VT0001, VT0002, etc.
    video_type_code TEXT UNIQUE,            -- Full_Ice, Broadcast, etc.
    video_type_name TEXT,                   -- Display name
    description TEXT,                       -- What this video type is
    is_primary BOOLEAN,                     -- Primary video type for game
    sort_order INTEGER,                      -- Display order
    use_for_highlights BOOLEAN              -- Use this type for highlight linking
);
```

**Data:**
| video_type_id | video_type_code | video_type_name | description | is_primary | sort_order | use_for_highlights |
|---------------|-----------------|-----------------|-------------|------------|------------|-------------------|
| VT0001 | Full_Ice | Full Ice | Full ice camera view of entire game | TRUE | 1 | TRUE |
| VT0002 | Broadcast | Broadcast | Television/streaming broadcast feed | TRUE | 2 | FALSE |
| VT0003 | Highlights | Highlights | Compilation of game highlights | FALSE | 3 | FALSE |
| VT0004 | Goalie | Goalie Camera | Goalie camera view | FALSE | 4 | FALSE |
| VT0005 | Overhead | Overhead | Overhead camera view | FALSE | 5 | FALSE |
| VT0006 | Wide | Wide Angle | Wide angle camera view | FALSE | 6 | FALSE |
| VT0007 | Tight | Tight Shot | Tight/close-up camera view | FALSE | 7 | FALSE |
| VT0008 | Replay | Replay | Replay/instant replay footage | FALSE | 8 | FALSE |
| VT0009 | Other | Other | Other video type | FALSE | 9 | FALSE |

### 2. `dim_highlight_category` Table

**Purpose:** Categorize highlights for filtering and organization.

**Schema:**
```sql
CREATE TABLE dim_highlight_category (
    highlight_category_id TEXT PRIMARY KEY,     -- HC0001, HC0002, etc.
    highlight_category_code TEXT UNIQUE,         -- Goal, Save, Hit, etc.
    highlight_category_name TEXT,                -- Display name
    description TEXT,                            -- What this category means
    priority INTEGER,                            -- Display/sort priority
    icon TEXT                                    -- Icon/emoji for UI
);
```

**Data:**
| highlight_category_id | highlight_category_code | highlight_category_name | description | priority | icon |
|----------------------|------------------------|-------------------------|-------------|----------|------|
| HC0001 | Goal | Goal | Goals scored | 1 | 🏒 |
| HC0002 | Save | Save | Outstanding saves | 2 | 🥅 |
| HC0003 | Hit | Hit | Big hits/body checks | 3 | 💥 |
| HC0004 | Fight | Fight | Fights | 4 | 👊 |
| HC0005 | Breakaway | Breakaway | Breakaway chances | 5 | ⚡ |
| HC0006 | Penalty_Shot | Penalty Shot | Penalty shots | 6 | 🎯 |
| HC0007 | Sequence | Sequence | Multi-event sequences | 7 | 🔄 |
| HC0008 | Momentum | Momentum Shift | Momentum-changing plays | 8 | 📈 |
| HC0009 | Skill | Skill Play | Exceptional skill displays | 9 | ⭐ |
| HC0010 | Other | Other | Other highlights | 10 | 📹 |

## Updated Fact Tables

### `fact_video` Changes

**Added:**
- `video_type_id` (FK to `dim_video_type.video_type_id`)

**Kept:**
- `video_type` (text, for backward compatibility and raw data)

**Example:**
```sql
SELECT 
    v.video_key,
    v.game_id,
    vt.video_type_name,
    vt.description,
    v.video_url
FROM fact_video v
JOIN dim_video_type vt ON v.video_type_id = vt.video_type_id
WHERE vt.use_for_highlights = TRUE;
```

### `fact_highlights` Changes

**Added:**
- `highlight_category_id` (FK to `dim_highlight_category.highlight_category_id`)

**Auto-mapping:**
- Goal events → HC0001 (Goal)
- Save events → HC0002 (Save)
- Hit events → HC0003 (Hit)
- Other events → HC0010 (Other)

**Example:**
```sql
SELECT 
    h.highlight_key,
    h.description,
    hc.highlight_category_name,
    hc.icon,
    h.video_start_time
FROM fact_highlights h
JOIN dim_highlight_category hc ON h.highlight_category_id = hc.highlight_category_id
WHERE hc.priority <= 3  -- Top 3 categories
ORDER BY hc.priority, h.video_start_time;
```

## Benefits

### 1. Data Integrity
- ✅ Validated video types (no typos)
- ✅ Consistent naming across all games
- ✅ Foreign key constraints

### 2. Better Queries
- ✅ Filter by video type properties (`use_for_highlights`, `is_primary`)
- ✅ Group highlights by category
- ✅ Sort by priority/importance

### 3. UI/UX Improvements
- ✅ Icons for highlight categories
- ✅ Descriptive names for video types
- ✅ Priority-based sorting

### 4. Maintainability
- ✅ Add new video types in one place
- ✅ Update descriptions without touching fact tables
- ✅ Centralized metadata

## Data Model

```
dim_video_type (video_type_id)
    ↑
    │ (FK)
    │
fact_video (video_type_id)
    │
    │ (video_key)
    │
    ↓
fact_highlights (video_key, highlight_category_id)
    │
    │ (FK)
    │
    ↓
dim_highlight_category (highlight_category_id)
```

## Migration Strategy

### Phase 1: Add Dimension Tables
1. Create `dim_video_type` and `dim_highlight_category`
2. Populate with initial data
3. No changes to fact tables yet

### Phase 2: Update Fact Tables
1. Add `video_type_id` to `fact_video`
2. Add `highlight_category_id` to `fact_highlights`
3. Populate FK columns from existing text values
4. Keep text columns for backward compatibility

### Phase 3: Validation
1. Verify all videos have valid `video_type_id`
2. Verify all highlights have valid `highlight_category_id`
3. Test queries using dimension tables

### Phase 4: Optional Cleanup
1. Remove text columns if no longer needed
2. Update ETL to use dimension tables

## Example Queries

### Get Primary Videos for Highlights
```sql
SELECT 
    v.game_id,
    vt.video_type_name,
    v.video_url,
    COUNT(h.highlight_key) AS highlight_count
FROM fact_video v
JOIN dim_video_type vt ON v.video_type_id = vt.video_type_id
LEFT JOIN fact_highlights h ON v.video_key = h.video_key
WHERE vt.use_for_highlights = TRUE
GROUP BY v.game_id, vt.video_type_name, v.video_url;
```

### Get Highlights by Category
```sql
SELECT 
    hc.highlight_category_name,
    hc.icon,
    COUNT(*) AS count,
    AVG(CAST(h.duration_seconds AS INTEGER)) AS avg_duration
FROM fact_highlights h
JOIN dim_highlight_category hc ON h.highlight_category_id = hc.highlight_category_id
GROUP BY hc.highlight_category_name, hc.icon, hc.priority
ORDER BY hc.priority;
```

### Get Video Types Available Per Game
```sql
SELECT 
    v.game_id,
    STRING_AGG(vt.video_type_name, ', ' ORDER BY vt.sort_order) AS available_videos
FROM fact_video v
JOIN dim_video_type vt ON v.video_type_id = vt.video_type_id
GROUP BY v.game_id;
```

## Implementation Status

✅ **Completed:**
- `dim_video_type` table creation function
- `dim_highlight_category` table creation function
- Updated `fact_video` to include `video_type_id`
- Updated `fact_highlights` to include `highlight_category_id`
- Auto-mapping logic for highlight categories
- SQL schema updates

🔄 **Next Steps:**
- Run ETL to populate dimension tables
- Test FK relationships
- Update dashboard queries to use dimension tables
- Add validation in ETL

## Notes

- **Backward Compatibility:** Text columns (`video_type`) are kept for compatibility
- **Auto-Mapping:** Highlight categories are automatically assigned based on event_type
- **Extensibility:** Easy to add new video types or highlight categories
- **Performance:** FK indexes improve join performance
