# BenchSight Supabase Setup Guide

**Version:** 1.0  
**Date:** 2026-01-07  
**Purpose:** Step-by-step guide to set up Supabase for BenchSight Tracker

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Create Supabase Project](#create-supabase-project)
3. [Required Tables](#required-tables)
4. [Sample Data Setup](#sample-data-setup)
5. [API Configuration](#api-configuration)
6. [Testing Connection](#testing-connection)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

**Do you need to set up Supabase first?** YES, before the tracker can pull real data.

**What you need:**
1. Supabase account (free tier works)
2. Project URL: `https://xxxx.supabase.co`
3. Anon Key: `eyJhbGc...` (public, safe to expose)

**Time estimate:** 30-60 minutes for full setup

---

## Create Supabase Project

### Step 1: Create Account

1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub (recommended) or email

### Step 2: Create New Project

1. Click "New Project"
2. Settings:
   - **Name:** `benchsight` or `norad-hockey`
   - **Database Password:** Save this somewhere secure!
   - **Region:** Choose closest to you (e.g., `us-east-1`)
3. Click "Create new project"
4. Wait 2-3 minutes for provisioning

### Step 3: Get Your Credentials

1. Go to **Settings → API**
2. Copy these values:
   - **Project URL:** `https://xxxxxx.supabase.co`
   - **anon/public key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

Save these - you'll enter them in the tracker settings.

---

## Required Tables

The tracker needs these tables at minimum. Run these SQL commands in the Supabase SQL Editor.

### Core Tables (REQUIRED)

```sql
-- ============================================================
-- dim_games: Game schedule and basic info
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_games (
    game_id SERIAL PRIMARY KEY,
    game_date DATE NOT NULL,
    season_id INT,
    home_team_id INT,
    away_team_id INT,
    home_team_name VARCHAR(100),
    away_team_name VARCHAR(100),
    home_team_color VARCHAR(20) DEFAULT '#3b82f6',
    away_team_color VARCHAR(20) DEFAULT '#ef4444',
    venue VARCHAR(200),
    game_time VARCHAR(20),
    home_score INT,
    away_score INT,
    game_status VARCHAR(50) DEFAULT 'scheduled',
    norad_game_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- dim_teams: Team reference data
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_teams (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    team_short_name VARCHAR(20),
    team_color VARCHAR(20),
    team_alt_color VARCHAR(20),
    league VARCHAR(50) DEFAULT 'NORAD',
    division VARCHAR(50),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- dim_players: Player master data
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_players (
    player_id SERIAL PRIMARY KEY,
    norad_player_id VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    jersey_number VARCHAR(10),
    position VARCHAR(10),  -- F, D, G
    skill_level INT,
    shoots VARCHAR(5),     -- L, R
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- dim_game_rosters: Which players played in which games
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_game_rosters (
    roster_id SERIAL PRIMARY KEY,
    game_id INT REFERENCES dim_games(game_id),
    player_id INT REFERENCES dim_players(player_id),
    team_id INT REFERENCES dim_teams(team_id),
    team_venue VARCHAR(10) NOT NULL,  -- 'home' or 'away'
    jersey_number VARCHAR(10),
    player_name VARCHAR(200),
    position VARCHAR(10),
    is_starter BOOLEAN DEFAULT false,
    is_goalie BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(game_id, player_id)
);

-- ============================================================
-- dim_youtube_videos: Video links per game
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_youtube_videos (
    video_id SERIAL PRIMARY KEY,
    game_id INT REFERENCES dim_games(game_id),
    angle_name VARCHAR(50) DEFAULT 'Main',
    youtube_url VARCHAR(500),
    youtube_video_id VARCHAR(50),  -- Extracted from URL
    start_offset_seconds INT DEFAULT 0,
    duration_seconds INT,
    is_primary BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_game_rosters_game ON dim_game_rosters(game_id);
CREATE INDEX IF NOT EXISTS idx_game_rosters_player ON dim_game_rosters(player_id);
CREATE INDEX IF NOT EXISTS idx_games_date ON dim_games(game_date DESC);
CREATE INDEX IF NOT EXISTS idx_videos_game ON dim_youtube_videos(game_id);
```

### Dimension Tables for Dropdowns

```sql
-- ============================================================
-- dim_event_types: Event type definitions
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_event_types (
    event_type_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100),
    hotkey VARCHAR(5),
    sort_order INT,
    active BOOLEAN DEFAULT true
);

INSERT INTO dim_event_types (event_type, display_name, hotkey, sort_order) VALUES
('Shot', 'Shot', 'S', 1),
('Pass', 'Pass', 'P', 2),
('Faceoff', 'Faceoff', 'F', 3),
('Goal', 'Goal', 'G', 4),
('Zone', 'Zone Entry/Exit', 'Z', 5),
('Turnover', 'Turnover', 'T', 6),
('Possession', 'Possession', 'O', 7),
('Save', 'Save', 'V', 8),
('Rebound', 'Rebound', 'R', 9),
('DeadIce', 'Dead Ice', 'D', 10),
('Stoppage', 'Stoppage', 'X', 11),
('Penalty', 'Penalty', 'N', 12)
ON CONFLICT (event_type) DO NOTHING;

-- ============================================================
-- dim_event_details: Detail options per event type
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_event_details (
    detail_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    detail_level INT NOT NULL,  -- 1 or 2
    detail_value VARCHAR(100) NOT NULL,
    display_name VARCHAR(100),
    parent_detail VARCHAR(100),  -- For cascading (detail2 depends on detail1)
    sort_order INT,
    active BOOLEAN DEFAULT true,
    UNIQUE(event_type, detail_level, detail_value)
);

-- Shot details
INSERT INTO dim_event_details (event_type, detail_level, detail_value, sort_order) VALUES
('Shot', 1, 'OnNetSaved', 1),
('Shot', 1, 'Missed', 2),
('Shot', 1, 'Blocked', 3),
('Shot', 1, 'Goal', 4),
('Shot', 2, 'Wrist', 1),
('Shot', 2, 'Slap', 2),
('Shot', 2, 'Snap', 3),
('Shot', 2, 'Backhand', 4),
('Shot', 2, 'Tip', 5),
('Shot', 2, 'Deflection', 6)
ON CONFLICT DO NOTHING;

-- Pass details
INSERT INTO dim_event_details (event_type, detail_level, detail_value, sort_order) VALUES
('Pass', 1, 'Completed', 1),
('Pass', 1, 'Missed', 2),
('Pass', 1, 'Intercepted', 3),
('Pass', 2, 'Tape', 1),
('Pass', 2, 'Saucer', 2),
('Pass', 2, 'Bank', 3),
('Pass', 2, 'Cross_Ice', 4),
('Pass', 2, 'Backhand', 5)
ON CONFLICT DO NOTHING;

-- Goal details
INSERT INTO dim_event_details (event_type, detail_level, detail_value, sort_order) VALUES
('Goal', 1, 'Even', 1),
('Goal', 1, 'PP', 2),
('Goal', 1, 'SH', 3),
('Goal', 1, 'EN', 4),
('Goal', 2, 'Wrist', 1),
('Goal', 2, 'Slap', 2),
('Goal', 2, 'Snap', 3),
('Goal', 2, 'Backhand', 4),
('Goal', 2, 'Tip', 5),
('Goal', 2, 'Rebound', 6)
ON CONFLICT DO NOTHING;

-- Turnover details
INSERT INTO dim_event_details (event_type, detail_level, detail_value, sort_order) VALUES
('Turnover', 1, 'Giveaway', 1),
('Turnover', 1, 'Takeaway', 2),
('Turnover', 2, 'Pass', 1),
('Turnover', 2, 'Poke', 2),
('Turnover', 2, 'Lost_Battle', 3),
('Turnover', 2, 'Bad_Clear', 4)
ON CONFLICT DO NOTHING;

-- Faceoff details
INSERT INTO dim_event_details (event_type, detail_level, detail_value, sort_order) VALUES
('Faceoff', 1, 'Won', 1),
('Faceoff', 1, 'Lost', 2),
('Faceoff', 2, 'Clean', 1),
('Faceoff', 2, 'Tie_Back', 2),
('Faceoff', 2, 'Tie_Forward', 3)
ON CONFLICT DO NOTHING;

-- Zone details
INSERT INTO dim_event_details (event_type, detail_level, detail_value, sort_order) VALUES
('Zone', 1, 'Entry', 1),
('Zone', 1, 'Exit', 2),
('Zone', 1, 'Clear', 3),
('Zone', 2, 'Carry', 1),
('Zone', 2, 'Dump', 2),
('Zone', 2, 'Pass', 3),
('Zone', 2, 'Chip', 4)
ON CONFLICT DO NOTHING;

-- Save details
INSERT INTO dim_event_details (event_type, detail_level, detail_value, sort_order) VALUES
('Save', 1, 'Rebound', 1),
('Save', 1, 'Freeze', 2),
('Save', 1, 'Played', 3),
('Save', 1, 'Cover', 4),
('Save', 2, 'Blocker', 1),
('Save', 2, 'Glove', 2),
('Save', 2, 'Pad', 3),
('Save', 2, 'Stick', 4),
('Save', 2, 'Body', 5)
ON CONFLICT DO NOTHING;

-- Possession details
INSERT INTO dim_event_details (event_type, detail_level, detail_value, sort_order) VALUES
('Possession', 1, 'PuckRetrieval', 1),
('Possession', 1, 'PuckRecovery', 2),
('Possession', 1, 'LoosePuck', 3)
ON CONFLICT DO NOTHING;

-- Rebound details
INSERT INTO dim_event_details (event_type, detail_level, detail_value, sort_order) VALUES
('Rebound', 1, 'TeamRecovered', 1),
('Rebound', 1, 'OppTeamRecovered', 2),
('Rebound', 1, 'ShotGenerated', 3)
ON CONFLICT DO NOTHING;

-- DeadIce details
INSERT INTO dim_event_details (event_type, detail_level, detail_value, sort_order) VALUES
('DeadIce', 1, 'Icing', 1),
('DeadIce', 1, 'Offside', 2),
('DeadIce', 1, 'Puck_Out', 3),
('DeadIce', 1, 'Net_Off', 4),
('DeadIce', 1, 'Other', 5)
ON CONFLICT DO NOTHING;

-- Stoppage details
INSERT INTO dim_event_details (event_type, detail_level, detail_value, sort_order) VALUES
('Stoppage', 1, 'Play', 1),
('Stoppage', 1, 'Penalty', 2),
('Stoppage', 1, 'Goal', 3),
('Stoppage', 1, 'Period_End', 4),
('Stoppage', 1, 'TV_Timeout', 5)
ON CONFLICT DO NOTHING;

-- Penalty details
INSERT INTO dim_event_details (event_type, detail_level, detail_value, sort_order) VALUES
('Penalty', 1, 'Minor', 1),
('Penalty', 1, 'Major', 2),
('Penalty', 1, 'Misconduct', 3),
('Penalty', 2, 'Tripping', 1),
('Penalty', 2, 'Hooking', 2),
('Penalty', 2, 'Slashing', 3),
('Penalty', 2, 'Interference', 4),
('Penalty', 2, 'Holding', 5),
('Penalty', 2, 'Roughing', 6),
('Penalty', 2, 'High_Sticking', 7),
('Penalty', 2, 'Cross_Check', 8),
('Penalty', 2, 'Boarding', 9),
('Penalty', 2, 'Other', 10)
ON CONFLICT DO NOTHING;

-- ============================================================
-- dim_zones: Zone reference
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_zones (
    zone_id SERIAL PRIMARY KEY,
    zone_code VARCHAR(5) NOT NULL UNIQUE,
    zone_name VARCHAR(50),
    sort_order INT
);

INSERT INTO dim_zones (zone_code, zone_name, sort_order) VALUES
('o', 'Offensive', 1),
('n', 'Neutral', 2),
('d', 'Defensive', 3)
ON CONFLICT DO NOTHING;

-- ============================================================
-- dim_shift_types: Shift start/stop types
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_shift_types (
    type_id SERIAL PRIMARY KEY,
    type_code VARCHAR(50) NOT NULL,
    type_category VARCHAR(20) NOT NULL,  -- 'start' or 'stop'
    display_name VARCHAR(100),
    sort_order INT,
    UNIQUE(type_code, type_category)
);

INSERT INTO dim_shift_types (type_code, type_category, display_name, sort_order) VALUES
('On_Fly', 'start', 'On the Fly', 1),
('Faceoff', 'start', 'Faceoff', 2),
('Period_Start', 'start', 'Period Start', 3),
('On_Fly', 'stop', 'On the Fly', 1),
('Whistle', 'stop', 'Whistle', 2),
('Period_End', 'stop', 'Period End', 3),
('Goal', 'stop', 'Goal', 4)
ON CONFLICT DO NOTHING;
```

### NORAD Official Data (For Validation)

```sql
-- ============================================================
-- fact_norad_goals: Official goal records from noradhockey.com
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_norad_goals (
    norad_goal_id SERIAL PRIMARY KEY,
    game_id INT REFERENCES dim_games(game_id),
    norad_game_id VARCHAR(50),
    period INT,
    time_min INT,
    time_sec INT,
    scoring_team VARCHAR(100),
    scoring_team_venue VARCHAR(10),  -- 'home' or 'away'
    goal_scorer VARCHAR(200),
    goal_scorer_number VARCHAR(10),
    assist_1 VARCHAR(200),
    assist_1_number VARCHAR(10),
    assist_2 VARCHAR(200),
    assist_2_number VARCHAR(10),
    goal_type VARCHAR(50),  -- 'Even', 'PP', 'SH', 'EN'
    home_score_after INT,
    away_score_after INT,
    scraped_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_norad_goals_game ON fact_norad_goals(game_id);
```

### Tracker Output Tables (Where tracker saves data)

```sql
-- ============================================================
-- stage_tracker_events: Raw events from tracker (before ETL)
-- ============================================================
CREATE TABLE IF NOT EXISTS stage_tracker_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(50) NOT NULL,
    game_id INT REFERENCES dim_games(game_id),
    period INT,
    team_venue VARCHAR(10),
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_detail_2 VARCHAR(100),
    event_start_min INT,
    event_start_sec INT,
    event_end_min INT,
    event_end_sec INT,
    event_zone VARCHAR(5),
    event_successful VARCHAR(5),
    is_highlight BOOLEAN DEFAULT false,
    linked_event_key VARCHAR(50),
    
    -- Players (JSON arrays)
    event_players JSONB,  -- [{num, name, pos, id}]
    opp_players JSONB,
    
    -- XY data (JSON)
    puck_xy JSONB,        -- [{seq, x, y}]
    player_xy JSONB,      -- [{player_id, num, positions: [{seq, x, y}]}]
    shot_net_xy JSONB,    -- {x, y}
    
    -- Metadata
    tracker_idx INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- stage_tracker_shifts: Raw shifts from tracker (before ETL)
-- ============================================================
CREATE TABLE IF NOT EXISTS stage_tracker_shifts (
    id SERIAL PRIMARY KEY,
    shift_id VARCHAR(50) NOT NULL,
    game_id INT REFERENCES dim_games(game_id),
    shift_index INT,
    period INT,
    shift_start_type VARCHAR(50),
    shift_stop_type VARCHAR(50),
    shift_start_min INT,
    shift_start_sec INT,
    shift_end_min INT,
    shift_end_sec INT,
    
    -- Home lineup
    home_f1 VARCHAR(10),
    home_f2 VARCHAR(10),
    home_f3 VARCHAR(10),
    home_d1 VARCHAR(10),
    home_d2 VARCHAR(10),
    home_g VARCHAR(10),
    home_x VARCHAR(10),
    
    -- Away lineup
    away_f1 VARCHAR(10),
    away_f2 VARCHAR(10),
    away_f3 VARCHAR(10),
    away_d1 VARCHAR(10),
    away_d2 VARCHAR(10),
    away_g VARCHAR(10),
    away_x VARCHAR(10),
    
    -- Video times
    video_start_seconds INT,
    video_end_seconds INT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tracker_events_game ON stage_tracker_events(game_id);
CREATE INDEX IF NOT EXISTS idx_tracker_shifts_game ON stage_tracker_shifts(game_id);
```

---

## Sample Data Setup

### Add Sample Teams

```sql
INSERT INTO dim_teams (team_name, team_short_name, team_color) VALUES
('Velodrome', 'VEL', '#9C47E4'),
('Orphans', 'ORP', '#000000'),
('OS Offices', 'OSO', '#2C8A5E'),
('Platinum', 'PLT', '#919294'),
('HollowBrook', 'HBK', '#4D2640'),
('Nelson', 'NEL', '#F3C323'),
('Outlaws', 'OUT', '#02007B'),
('Triple J', 'TJJ', '#4EB9E5'),
('Ace', 'ACE', '#CA0527'),
('Amos', 'AMS', '#641C28');
```

### Add Sample Game

```sql
INSERT INTO dim_games (game_id, game_date, home_team_name, away_team_name, home_team_color, away_team_color, norad_game_id)
VALUES (18969, '2025-09-07', 'Platinum', 'Velodrome', '#919294', '#9C47E4', '18969');
```

### Add Sample Rosters

```sql
-- Velodrome roster for game 18969
INSERT INTO dim_game_rosters (game_id, player_id, team_venue, jersey_number, player_name, position) VALUES
(18969, 1, 'away', '9', 'Pinnell', 'D'),
(18969, 2, 'away', '14', 'Ciampoli', 'F'),
(18969, 3, 'away', '22', 'Mayfield', 'D'),
(18969, 4, 'away', '39', 'Crandall', 'G'),
(18969, 5, 'away', '42', 'Ashcroft', 'F'),
(18969, 6, 'away', '70', 'S.Downs', 'F'),
(18969, 7, 'away', '75', 'N.Downs', 'F'),
(18969, 8, 'away', '84', 'Donaty', 'D'),
(18969, 9, 'away', '91', 'White', 'F');

-- Platinum roster for game 18969
INSERT INTO dim_game_rosters (game_id, player_id, team_venue, jersey_number, player_name, position) VALUES
(18969, 101, 'home', '3', 'Considine', 'D'),
(18969, 102, 'home', '8', 'Chambless', 'D'),
(18969, 103, 'home', '21', 'Marshall', 'F'),
(18969, 104, 'home', '34', 'Dube', 'F'),
(18969, 105, 'home', '45', 'Mantaro', 'D'),
(18969, 106, 'home', '53', 'Premo', 'F'),
(18969, 107, 'home', '99', 'Forte', 'G');
```

---

## API Configuration

### Row Level Security (RLS)

For public read access (tracker needs this):

```sql
-- Enable RLS
ALTER TABLE dim_games ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_players ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_game_rosters ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_event_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_event_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_youtube_videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_norad_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE stage_tracker_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE stage_tracker_shifts ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Public read access" ON dim_games FOR SELECT USING (true);
CREATE POLICY "Public read access" ON dim_teams FOR SELECT USING (true);
CREATE POLICY "Public read access" ON dim_players FOR SELECT USING (true);
CREATE POLICY "Public read access" ON dim_game_rosters FOR SELECT USING (true);
CREATE POLICY "Public read access" ON dim_event_types FOR SELECT USING (true);
CREATE POLICY "Public read access" ON dim_event_details FOR SELECT USING (true);
CREATE POLICY "Public read access" ON dim_youtube_videos FOR SELECT USING (true);
CREATE POLICY "Public read access" ON fact_norad_goals FOR SELECT USING (true);

-- Allow public insert/update for tracker data
CREATE POLICY "Public write access" ON stage_tracker_events FOR ALL USING (true);
CREATE POLICY "Public write access" ON stage_tracker_shifts FOR ALL USING (true);
```

---

## Testing Connection

### Test in Browser Console

```javascript
const { createClient } = supabase;

const sb = createClient(
  'https://YOUR_PROJECT.supabase.co',
  'YOUR_ANON_KEY'
);

// Test games
const { data: games, error } = await sb
  .from('dim_games')
  .select('*')
  .limit(5);

console.log('Games:', games);
console.log('Error:', error);
```

### Test in Tracker

1. Open tracker HTML
2. Click ⚙️ Settings
3. Enter Supabase URL and Key
4. Click Save
5. Click 🔄 Refresh
6. Check console for "Loaded X games from Supabase"

---

## Troubleshooting

### "Failed to fetch" error
- Check URL is correct (https://xxxx.supabase.co)
- Check anon key is correct
- Check CORS settings in Supabase dashboard

### "Permission denied" error
- RLS policies not set up
- Run the RLS commands above

### "Table not found" error
- Table doesn't exist
- Run the CREATE TABLE commands

### No games showing
- No data in dim_games
- Run the sample data INSERT commands

### Rosters not loading
- No data in dim_game_rosters for that game_id
- Add roster data for the specific game

---

## Next Steps After Supabase Setup

1. **Import your existing data**
   - Games from your tracking Excel files
   - Rosters from NORAD scraper
   
2. **Configure tracker**
   - Enter Supabase URL and key
   - Test connection
   
3. **Start tracking!**
   - Select game
   - Track events
   - Export to Excel for ETL

---

## Support

If you have issues:
1. Check browser console (F12) for errors
2. Test SQL queries directly in Supabase SQL Editor
3. Verify RLS policies are applied
