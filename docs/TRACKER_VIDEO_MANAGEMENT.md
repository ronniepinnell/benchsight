# Tracker Video Management Guide

**Guide for using the dedicated video management page**

---

## 🎥 Overview

The video management page (`/tracker/videos`) is a dedicated interface for storing YouTube video links and details for games, then exporting them along with tracking data.

---

## 📍 Access

- **URL**: `/tracker/videos`
- **From Tracker**: Click "🎥 Manage Videos" button on tracker selection page
- **Direct**: Navigate to `https://your-dashboard.vercel.app/tracker/videos`

---

## ✨ Features

### 1. Game Selection
- Browse all games from Supabase
- Search by team name or game ID
- See video count for each game

### 2. Video Management
- Add multiple videos per game
- Support for YouTube, local files, and other URLs
- Add details: title, description, period, time range, notes
- Delete videos

### 3. Export
- Export tracking data (events/shifts) to Excel
- Export video links as JSON
- Combined export includes both tracking and video data

---

## 🚀 Usage

### Adding a Video

1. **Select a Game**
   - Click on a game from the left panel
   - Game details appear on the right

2. **Fill Video Form**
   - **Video URL**: Paste YouTube URL (e.g., `https://youtube.com/watch?v=...`)
   - **Video Type**: Select YouTube, Local File, or Other
   - **Title** (optional): e.g., "Period 1 Highlights"
   - **Description** (optional): Additional details
   - **Period** (optional): Which period this video covers
   - **Start Time** (optional): Video start time for trimming (e.g., "00:00")
   - **End Time** (optional): Video end time for trimming (e.g., "20:00")
   - **Notes** (optional): Additional notes

3. **Add Video**
   - Click "Add Video" button
   - Video appears in the videos list

### YouTube URL Formats Supported

The system automatically extracts YouTube video IDs from:
- `https://youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/embed/VIDEO_ID`

### Managing Videos

- **View**: Videos appear in the list below the form
- **Delete**: Click "Delete" button on any video
- **Edit**: Delete and re-add (edit functionality can be added later)

### Exporting

1. **Select a Game** with videos
2. **Click "Export"** button on the game card
3. **Two files download**:
   - Excel file: `{gameId}_tracking_{timestamp}.xlsx`
     - Contains: metadata, events, shifts, **videos** sheets
   - JSON file: `{gameId}_videos_{timestamp}.json`
     - Contains: Game info and all video links

---

## 🗄️ Database Setup

### Create Table

Run this SQL in Supabase SQL Editor:

```sql
-- See: sql/create_tracker_videos_table.sql
CREATE TABLE IF NOT EXISTS tracker_videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id TEXT NOT NULL,
  video_url TEXT NOT NULL,
  video_type TEXT NOT NULL CHECK (video_type IN ('youtube', 'local', 'other')),
  video_id TEXT,
  title TEXT,
  description TEXT,
  start_time TEXT,
  end_time TEXT,
  period INTEGER,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tracker_videos_game_id ON tracker_videos(game_id);
```

### Permissions

If using Row Level Security (RLS):

```sql
ALTER TABLE tracker_videos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read" ON tracker_videos 
  FOR SELECT USING (true);

CREATE POLICY "Allow public insert" ON tracker_videos 
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update" ON tracker_videos 
  FOR UPDATE USING (true);

CREATE POLICY "Allow public delete" ON tracker_videos 
  FOR DELETE USING (true);
```

---

## 📊 Export Format

### Excel Export

The Excel file includes a **videos sheet** with columns:
- `video_url` - Full video URL
- `video_type` - youtube, local, or other
- `video_id` - YouTube video ID (if YouTube)
- `title` - Video title
- `description` - Video description
- `start_time` - Start time for trimming
- `end_time` - End time for trimming
- `period` - Period number (1, 2, 3, 4)
- `notes` - Additional notes

### JSON Export

```json
{
  "game_id": "18969",
  "home_team": "Team A",
  "away_team": "Team B",
  "game_date": "2026-01-14",
  "videos": [
    {
      "id": "uuid",
      "game_id": "18969",
      "video_url": "https://youtube.com/watch?v=...",
      "video_type": "youtube",
      "video_id": "VIDEO_ID",
      "title": "Period 1 Highlights",
      "description": "Full period 1",
      "start_time": "00:00",
      "end_time": "20:00",
      "period": 1,
      "notes": "Great period!"
    }
  ],
  "export_date": "2026-01-14T12:00:00Z"
}
```

---

## 🔗 Integration

### With Tracker

Videos can be linked to tracking sessions:
- Store video links for reference
- Export videos along with events/shifts
- Use video timing for event synchronization (future feature)

### With Dashboard

Video links can be displayed on:
- Game detail pages
- Player highlight reels
- Team pages

---

## 🎯 Use Cases

1. **Game Highlights**
   - Store full game video
   - Store period-specific videos
   - Store highlight reels

2. **Video Analysis**
   - Link videos to specific periods
   - Add notes about key moments
   - Export for video analysis tools

3. **Archive**
   - Centralized video storage
   - Easy export for backup
   - Historical reference

---

## 🐛 Troubleshooting

### "Table does not exist" Error

**Solution**: Run the SQL script to create the table:
```sql
-- See: sql/create_tracker_videos_table.sql
```

### Videos Not Loading

**Check**:
- Table exists in Supabase
- Table has proper indexes
- RLS policies allow access (if enabled)

### Export Fails

**Check**:
- `xlsx` package is installed: `npm install xlsx`
- Browser allows downloads
- Check browser console for errors

---

## 📝 Notes

- Videos are stored per game
- Multiple videos per game are supported
- YouTube video IDs are automatically extracted
- Export includes both Excel and JSON formats
- Videos can be linked to specific periods

---

**Video management is ready to use!** 🎥
