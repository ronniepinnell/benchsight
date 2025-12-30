-- ============================================
-- VIDEO HIGHLIGHTS FEATURE
-- Run after 01_CREATE_ALL_TABLES.sql
-- ============================================

-- Dimension table for highlight types
CREATE TABLE IF NOT EXISTS dim_highlight_type (
    highlight_type_id SERIAL PRIMARY KEY,
    highlight_type TEXT UNIQUE NOT NULL,
    display_name TEXT,
    description TEXT,
    icon TEXT,
    color TEXT,
    sort_order INTEGER
);

-- Seed highlight types
INSERT INTO dim_highlight_type (highlight_type, display_name, description, icon, color, sort_order) VALUES
('goal', 'Goal', 'Goal scored', 'goal', '#e74c3c', 1),
('save', 'Save', 'Goalie save', 'save', '#3498db', 2),
('hit', 'Hit', 'Body check', 'hit', '#f39c12', 3),
('fight', 'Fight', 'Player fight', 'fight', '#9b59b6', 4),
('penalty', 'Penalty', 'Penalty call', 'penalty', '#e67e22', 5),
('skill', 'Skill Play', 'Deke, dangle, or skill move', 'skill', '#2ecc71', 6),
('team_play', 'Team Play', 'Nice passing or team effort', 'team', '#1abc9c', 7),
('defensive', 'Defensive', 'Block, stick check, or defensive play', 'defense', '#34495e', 8),
('other', 'Other', 'Other notable moment', 'star', '#95a5a6', 9)
ON CONFLICT (highlight_type) DO NOTHING;

-- Main highlights table
CREATE TABLE IF NOT EXISTS fact_video_highlights (
    highlight_key TEXT PRIMARY KEY,
    game_id INTEGER NOT NULL,
    event_index INTEGER,
    player_id INTEGER,
    team_id INTEGER,
    video_source TEXT,
    video_url TEXT NOT NULL,
    video_id TEXT,
    start_timestamp DECIMAL(10,3) NOT NULL,
    end_timestamp DECIMAL(10,3) NOT NULL,
    duration_seconds DECIMAL(10,3),
    highlight_type TEXT NOT NULL,
    highlight_subtype TEXT,
    title TEXT,
    description TEXT,
    camera_angle TEXT DEFAULT 'broadcast',
    video_quality TEXT DEFAULT 'hd',
    quality_rating INTEGER,
    is_featured BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by TEXT,
    updated_at TIMESTAMP,
    updated_by TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_highlights_game ON fact_video_highlights(game_id);
CREATE INDEX IF NOT EXISTS idx_highlights_player ON fact_video_highlights(player_id);
CREATE INDEX IF NOT EXISTS idx_highlights_team ON fact_video_highlights(team_id);
CREATE INDEX IF NOT EXISTS idx_highlights_type ON fact_video_highlights(highlight_type);
CREATE INDEX IF NOT EXISTS idx_highlights_featured ON fact_video_highlights(is_featured) WHERE is_featured = TRUE;
CREATE INDEX IF NOT EXISTS idx_highlights_event ON fact_video_highlights(game_id, event_index);

-- Add highlight columns to fact_events (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fact_events' AND column_name = 'is_highlight_candidate') THEN
        ALTER TABLE fact_events ADD COLUMN is_highlight_candidate BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fact_events' AND column_name = 'highlight_score') THEN
        ALTER TABLE fact_events ADD COLUMN highlight_score INTEGER DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fact_events' AND column_name = 'has_video_highlight') THEN
        ALTER TABLE fact_events ADD COLUMN has_video_highlight BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'fact_events' AND column_name = 'highlight_count') THEN
        ALTER TABLE fact_events ADD COLUMN highlight_count INTEGER DEFAULT 0;
    END IF;
END $$;

-- Populate highlight candidates
UPDATE fact_events
SET is_highlight_candidate = TRUE,
    highlight_score = CASE
        WHEN event_type = 'Goal' THEN 90
        WHEN event_detail IN ('Shot Goal', 'Goal Scored') THEN 90
        WHEN event_type = 'Save' AND event_detail LIKE '%Big%' THEN 80
        WHEN event_type = 'Hit' AND event_detail LIKE '%Big%' THEN 70
        WHEN event_detail LIKE '%Breakaway%' THEN 85
        WHEN event_detail LIKE '%Penalty Shot%' THEN 95
        WHEN event_type = 'Fight' THEN 75
        WHEN event_detail LIKE '%Dangle%' THEN 65
        WHEN event_detail LIKE '%Deke%' THEN 60
        ELSE 50
    END
WHERE event_type IN ('Goal', 'Save', 'Hit', 'Fight')
   OR event_detail LIKE '%Goal%'
   OR event_detail LIKE '%Big%'
   OR event_detail LIKE '%Breakaway%';

-- View for highlight candidates without clips
CREATE OR REPLACE VIEW v_highlight_candidates AS
SELECT 
    e.game_id,
    e.event_index,
    e.event_type,
    e.event_detail,
    e.highlight_score,
    p.player_name,
    t.team_name,
    s.game_date
FROM fact_events e
LEFT JOIN dim_player p ON e.event_player_1 = p.player_id
LEFT JOIN dim_team t ON e.team_id = t.team_id
LEFT JOIN dim_schedule s ON e.game_id = s.game_id
WHERE e.is_highlight_candidate = TRUE
  AND e.has_video_highlight = FALSE
ORDER BY e.highlight_score DESC, e.game_id DESC;
