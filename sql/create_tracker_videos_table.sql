-- Tracker Videos Table
-- Stores YouTube video links and details for games

CREATE TABLE IF NOT EXISTS tracker_videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id TEXT NOT NULL,
  video_url TEXT NOT NULL,
  video_type TEXT NOT NULL CHECK (video_type IN ('youtube', 'local', 'other')),
  video_id TEXT, -- YouTube video ID (extracted from URL)
  title TEXT,
  description TEXT,
  start_time TEXT, -- Video start time (for trimming)
  end_time TEXT, -- Video end time (for trimming)
  period INTEGER, -- Which period this video covers (1, 2, 3, 4)
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_tracker_videos_game_id ON tracker_videos(game_id);
CREATE INDEX IF NOT EXISTS idx_tracker_videos_video_type ON tracker_videos(video_type);
CREATE INDEX IF NOT EXISTS idx_tracker_videos_period ON tracker_videos(period);

-- RLS (if needed)
-- ALTER TABLE tracker_videos ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow public read" ON tracker_videos FOR SELECT USING (true);
-- CREATE POLICY "Allow public insert" ON tracker_videos FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow public update" ON tracker_videos FOR UPDATE USING (true);
-- CREATE POLICY "Allow public delete" ON tracker_videos FOR DELETE USING (true);
