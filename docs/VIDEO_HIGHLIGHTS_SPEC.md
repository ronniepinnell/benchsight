# Video Highlights Feature Specification

## Overview

Add video highlight clipping functionality to BenchSight, linking highlight clips to tracked events for easy retrieval and playback.

---

## New Table: `fact_video_highlights`

### Purpose
Store video highlight clips with timestamps, linking them to specific game events.

### Schema

```sql
CREATE TABLE IF NOT EXISTS fact_video_highlights (
    -- Primary Key
    highlight_key TEXT PRIMARY KEY,  -- Format: {game_id}_{event_index}_{clip_num}
    
    -- Foreign Keys
    game_id INTEGER NOT NULL,
    event_index INTEGER,  -- Links to fact_events.event_index (nullable for game-level highlights)
    player_id INTEGER,    -- Primary player featured
    team_id INTEGER,      -- Team featured
    
    -- Video Source
    video_source TEXT,           -- 'youtube', 'vimeo', 'local', 's3'
    video_url TEXT NOT NULL,     -- Full URL or S3 key
    video_id TEXT,               -- Platform-specific ID (YouTube video ID, etc.)
    
    -- Timestamps (in seconds from video start)
    start_timestamp DECIMAL(10,3) NOT NULL,
    end_timestamp DECIMAL(10,3) NOT NULL,
    duration_seconds DECIMAL(10,3) GENERATED ALWAYS AS (end_timestamp - start_timestamp) STORED,
    
    -- Highlight Metadata
    highlight_type TEXT NOT NULL,  -- 'goal', 'save', 'hit', 'fight', 'penalty', 'skill', 'team_play', 'other'
    highlight_subtype TEXT,        -- More specific: 'snipe', 'one_timer', 'breakaway_save', etc.
    title TEXT,                    -- Display title
    description TEXT,              -- Longer description
    
    -- Camera/Quality
    camera_angle TEXT DEFAULT 'broadcast',  -- 'broadcast', 'goal_cam', 'overhead', 'bench', 'fan'
    video_quality TEXT DEFAULT 'hd',        -- 'sd', 'hd', '4k'
    
    -- Ratings & Flags
    quality_rating INTEGER CHECK (quality_rating BETWEEN 1 AND 5),  -- 1-5 stars
    is_featured BOOLEAN DEFAULT FALSE,      -- Featured on homepage
    is_approved BOOLEAN DEFAULT FALSE,      -- Admin approved
    is_public BOOLEAN DEFAULT TRUE,         -- Visible to public
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    created_by TEXT,
    updated_at TIMESTAMP,
    updated_by TEXT,
    
    -- Constraints
    CONSTRAINT valid_timestamps CHECK (end_timestamp > start_timestamp),
    CONSTRAINT valid_highlight_type CHECK (highlight_type IN (
        'goal', 'save', 'hit', 'fight', 'penalty', 'skill', 'team_play', 'defensive', 'other'
    ))
);

-- Indexes for common queries
CREATE INDEX idx_highlights_game ON fact_video_highlights(game_id);
CREATE INDEX idx_highlights_player ON fact_video_highlights(player_id);
CREATE INDEX idx_highlights_team ON fact_video_highlights(team_id);
CREATE INDEX idx_highlights_type ON fact_video_highlights(highlight_type);
CREATE INDEX idx_highlights_featured ON fact_video_highlights(is_featured) WHERE is_featured = TRUE;
CREATE INDEX idx_highlights_event ON fact_video_highlights(game_id, event_index);
```

---

## Modify: `fact_events` - Add Highlight Flags

### New Columns

```sql
ALTER TABLE fact_events ADD COLUMN is_highlight_candidate BOOLEAN DEFAULT FALSE;
ALTER TABLE fact_events ADD COLUMN highlight_score INTEGER DEFAULT 0;
ALTER TABLE fact_events ADD COLUMN has_video_highlight BOOLEAN DEFAULT FALSE;
ALTER TABLE fact_events ADD COLUMN highlight_count INTEGER DEFAULT 0;
```

### Column Descriptions

| Column | Type | Description |
|--------|------|-------------|
| `is_highlight_candidate` | BOOLEAN | Auto-flagged as potential highlight (goal, save, etc.) |
| `highlight_score` | INTEGER | Calculated importance score (0-100) |
| `has_video_highlight` | BOOLEAN | At least one highlight clip exists |
| `highlight_count` | INTEGER | Number of highlight clips for this event |

### Auto-Flag Logic

```sql
-- Update highlight candidates based on event type
UPDATE fact_events
SET is_highlight_candidate = TRUE,
    highlight_score = CASE
        WHEN event_type = 'Goal' THEN 90
        WHEN event_detail IN ('Shot Goal', 'Goal Scored') THEN 90
        WHEN event_type = 'Save' AND event_detail = 'Big Save' THEN 80
        WHEN event_type = 'Hit' AND event_detail = 'Big Hit' THEN 70
        WHEN event_detail = 'Breakaway' THEN 85
        WHEN event_detail = 'Penalty Shot' THEN 95
        WHEN event_type = 'Fight' THEN 75
        WHEN event_detail LIKE '%Dangle%' THEN 65
        WHEN event_detail LIKE '%Deke%' THEN 60
        ELSE 50
    END
WHERE event_type IN ('Goal', 'Save', 'Hit', 'Fight')
   OR event_detail IN ('Shot Goal', 'Goal Scored', 'Big Save', 'Big Hit', 
                       'Breakaway', 'Penalty Shot', 'Dangle', 'Deke');
```

---

## New Dimension: `dim_highlight_type`

```sql
CREATE TABLE IF NOT EXISTS dim_highlight_type (
    highlight_type_id SERIAL PRIMARY KEY,
    highlight_type TEXT UNIQUE NOT NULL,
    display_name TEXT,
    description TEXT,
    icon TEXT,           -- Icon name for UI
    color TEXT,          -- Hex color for UI
    sort_order INTEGER
);

-- Seed data
INSERT INTO dim_highlight_type (highlight_type, display_name, description, icon, color, sort_order) VALUES
('goal', 'Goal', 'Goal scored', 'goal', '#e74c3c', 1),
('save', 'Save', 'Goalie save', 'save', '#3498db', 2),
('hit', 'Hit', 'Body check', 'hit', '#f39c12', 3),
('fight', 'Fight', 'Player fight', 'fight', '#9b59b6', 4),
('penalty', 'Penalty', 'Penalty call', 'penalty', '#e67e22', 5),
('skill', 'Skill Play', 'Deke, dangle, or skill move', 'skill', '#2ecc71', 6),
('team_play', 'Team Play', 'Nice passing or team effort', 'team', '#1abc9c', 7),
('defensive', 'Defensive', 'Block, stick check, or defensive play', 'defense', '#34495e', 8),
('other', 'Other', 'Other notable moment', 'star', '#95a5a6', 9);
```

---

## Usage Examples

### Find All Goal Highlights for a Player
```sql
SELECT h.*, e.event_detail, p.player_name
FROM fact_video_highlights h
JOIN fact_events e ON h.game_id = e.game_id AND h.event_index = e.event_index
JOIN dim_player p ON h.player_id = p.player_id
WHERE h.player_id = 123
  AND h.highlight_type = 'goal'
ORDER BY h.created_at DESC;
```

### Get Featured Highlights for Homepage
```sql
SELECT h.*, g.game_date, ht.team_name AS home_team, at.team_name AS away_team
FROM fact_video_highlights h
JOIN dim_schedule g ON h.game_id = g.game_id
JOIN dim_team ht ON g.home_team_id = ht.team_id
JOIN dim_team at ON g.away_team_id = at.team_id
WHERE h.is_featured = TRUE
  AND h.is_approved = TRUE
ORDER BY g.game_date DESC
LIMIT 10;
```

### Get Events with Highlight Candidates Not Yet Clipped
```sql
SELECT e.*, p.player_name
FROM fact_events e
JOIN dim_player p ON e.event_player_1 = p.player_id
WHERE e.is_highlight_candidate = TRUE
  AND e.has_video_highlight = FALSE
  AND e.highlight_score >= 70
ORDER BY e.highlight_score DESC, e.game_id DESC;
```

### Build Highlight Reel for a Game
```sql
SELECT h.title, h.video_url, h.start_timestamp, h.end_timestamp,
       h.highlight_type, e.period_number, e.game_time
FROM fact_video_highlights h
LEFT JOIN fact_events e ON h.game_id = e.game_id AND h.event_index = e.event_index
WHERE h.game_id = 18969
ORDER BY COALESCE(e.period_number, 0), COALESCE(e.game_time, h.start_timestamp);
```

---

## Integration with Tracker

### Tracker UI Additions

1. **Highlight Button** on event row
   - Click to mark event as highlight candidate
   - Opens clip editor modal

2. **Clip Editor Modal**
   - Video player with timestamp controls
   - Set start/end timestamps
   - Select highlight type
   - Add title/description
   - Preview clip
   - Save highlight

3. **Highlight Indicator**
   - 🎬 icon on events with highlights
   - Badge showing highlight count

### Tracker Data Flow

```
User clicks "Create Highlight" on event
    ↓
Modal opens with video at event timestamp
    ↓
User adjusts start/end, adds metadata
    ↓
POST to /api/highlights
    ↓
Insert into fact_video_highlights
    ↓
Update fact_events (has_video_highlight = TRUE)
```

---

## API Endpoints (Suggested)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/highlights` | List highlights (with filters) |
| GET | `/api/highlights/:id` | Get single highlight |
| POST | `/api/highlights` | Create highlight |
| PUT | `/api/highlights/:id` | Update highlight |
| DELETE | `/api/highlights/:id` | Delete highlight |
| GET | `/api/games/:id/highlights` | Get game highlights |
| GET | `/api/players/:id/highlights` | Get player highlights |
| GET | `/api/events/:game_id/:event_index/highlights` | Get event highlights |
| POST | `/api/highlights/:id/feature` | Toggle featured status |

---

## Implementation Checklist

- [ ] Create `fact_video_highlights` table
- [ ] Create `dim_highlight_type` dimension
- [ ] Add columns to `fact_events`
- [ ] Update ETL to populate `is_highlight_candidate`
- [ ] Add to `flexible_loader.py` TABLE_CATEGORIES
- [ ] Create CSV generator script
- [ ] Update DATA_DICTIONARY.md
- [ ] Add to ERD
- [ ] Build Tracker UI components
- [ ] Build API endpoints
- [ ] Add validation tests
