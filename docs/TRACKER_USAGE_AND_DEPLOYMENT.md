# Tracker Usage and Deployment Guide

**Complete guide for using and deploying the BenchSight Game Tracker**

---

## 📖 Table of Contents

1. [How to Use the Tracker](#how-to-use-the-tracker)
2. [Local Development](#local-development)
3. [Deployment](#deployment)
4. [Access and URLs](#access-and-urls)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## 🎮 How to Use the Tracker

### Starting a Tracking Session

1. **Navigate to Tracker**
   - Go to `/tracker` in your dashboard
   - Or visit: `https://your-dashboard.vercel.app/tracker`

2. **Select a Game**
   - Browse recent games from the list
   - Search by team name or game ID
   - Click on a game to start tracking
   - Or click "New Tracking Session" and enter a game ID

3. **Tracker Loads Automatically**
   - Game data loads from Supabase
   - Rosters load automatically
   - Existing tracking data loads (if any)

### Tracking Events

#### Quick Event Entry (Keyboard Shortcuts)

- **F** - Faceoff
- **S** - Shot
- **P** - Pass
- **G** - Goal
- **T** - Turnover
- **Z** - Zone Entry/Exit
- **N** - Penalty
- **X** - Stoppage
- **O** - Possession
- **V** - Save
- **R** - Rebound
- **D** - Dead Ice
- **Y** - Play
- **I** - Intermission
- **C** - Clockstop

#### Manual Event Entry

1. **Select Event Type**
   - Click event type button in right panel
   - Or use keyboard shortcut

2. **Select Team**
   - Click "Home" or "Away" button
   - Or press **H** (home) / **A** (away)

3. **Enter Time**
   - Start time auto-fills from clock
   - Edit if needed (format: MM:SS)

4. **Add Details**
   - Select Detail 1 from dropdown
   - Select Detail 2 (if available)
   - Set zone, success, strength

5. **Add Players**
   - Click "Add Player" in player section
   - Select from roster
   - Players appear as chips
   - Click X to remove

6. **Place XY Coordinates**
   - Click on rink to place puck XY
   - Toggle XY mode: **M** (puck) / **Shift+M** (player)
   - Multiple XY points supported

7. **Submit Event**
   - Click "Log Event" button
   - Or press **Enter**
   - Event appears in event list

### Tracking Shifts

1. **Set Lineup**
   - Click empty slot in Shift Panel
   - Select player from roster
   - Click filled slot to remove player

2. **Enter Shift Times**
   - Start time (defaults to current clock)
   - End time

3. **Set Shift Types**
   - Start type (GameStart, PeriodStart, OnTheFly, etc.)
   - Stop type (OnTheFly, PeriodEnd, GoalScored, etc.)

4. **Log Shift**
   - Click "Log Shift" button
   - Or press **L**
   - Shift appears in shift log

### Editing Events/Shifts

1. **Edit Event**
   - Click event in event list
   - Edit modal opens
   - Make changes
   - Click "Save Changes"
   - Or click "Delete" to remove

2. **Edit Shift**
   - Click shift in shift log
   - Edit modal opens
   - Modify lineup, times, types
   - Save or delete

### Syncing to Cloud

- **Automatic**: Auto-saves to localStorage every 30 seconds
- **Manual**: Click "☁️ Sync" button in header
- **On Load**: Automatically loads from Supabase if available

### Exporting Data

1. Click "📥 Export" button in header
2. Excel file downloads automatically
3. File format: `{gameId}_tracking_{timestamp}.xlsx`
4. Contains:
   - Metadata sheet (game info)
   - Events sheet (LONG format - one row per player)
   - Shifts sheet (shift data with lineups)

---

## 💻 Local Development

### Prerequisites

- Node.js 18+ installed
- npm or pnpm
- Supabase credentials

### Setup

```bash
# Navigate to dashboard directory
cd ui/dashboard

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local
```

### Environment Variables

Edit `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Run Development Server

```bash
# Start dev server
npm run dev

# Open browser
# http://localhost:3000/tracker
```

### Build for Production

```bash
# Test build
npm run build

# Start production server
npm start
```

---

## 🚀 Deployment

### Option 1: Vercel (Recommended - Easiest)

#### Using Vercel Dashboard (No CLI)

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push
   ```

2. **Deploy Dashboard:**
   - Go to: https://vercel.com/new
   - Import your GitHub repository
   - **Root Directory**: `ui/dashboard`
   - Click **Deploy**

3. **Add Environment Variables:**
   - Go to project → Settings → Environment Variables
   - Add:
     ```
     NEXT_PUBLIC_SUPABASE_URL = https://your-project.supabase.co
     NEXT_PUBLIC_SUPABASE_ANON_KEY = your-anon-key
     ```
   - Redeploy (automatic or manual)

4. **Your tracker is live!**
   - Access at: `https://your-project.vercel.app/tracker`

#### Using Vercel CLI

```bash
# Navigate to dashboard
cd ui/dashboard

# Install Vercel CLI (if needed)
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? → Yes
# - Project name? → benchsight-dashboard
# - Directory? → ./
# - Override settings? → No

# Add environment variables in Vercel dashboard
# Then redeploy:
vercel --prod
```

### Option 2: Other Platforms

#### Netlify

```bash
# Build command
npm run build

# Publish directory
.next

# Environment variables
# Add in Netlify dashboard
```

#### Self-Hosted (Docker)

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 🌐 Access and URLs

### Development

- **Local**: http://localhost:3000/tracker
- **Game Selection**: http://localhost:3000/tracker
- **Specific Game**: http://localhost:3000/tracker/{gameId}

### Production (Vercel)

- **Base URL**: `https://your-project.vercel.app`
- **Tracker**: `https://your-project.vercel.app/tracker`
- **Game**: `https://your-project.vercel.app/tracker/{gameId}`

### Integration with Dashboard

The tracker is part of the dashboard application:

- **Standings**: `/standings`
- **Leaders**: `/leaders`
- **Games**: `/games`
- **Players**: `/players`
- **Tracker**: `/tracker` ← **Tracker is here**

---

## ⚙️ Configuration

### Supabase Tables Required

The tracker uses these Supabase tables:

1. **Game Data**
   - `stage_dim_schedule` (or `fact_game_status`)
   - Contains: game_id, home_team, away_team, game_date

2. **Rosters**
   - `fact_gameroster` (or `stage_fact_gameroster`)
   - Contains: game_id, player_game_number, player_full_name, team_name

3. **Tracking Data**
   - `stage_events_tracking`
   - `stage_shifts_tracking`

### Table Schema

#### stage_events_tracking

```sql
CREATE TABLE stage_events_tracking (
  id SERIAL PRIMARY KEY,
  game_id TEXT NOT NULL,
  event_index INTEGER,
  period INTEGER,
  type TEXT,
  team TEXT,
  start_time TEXT,
  end_time TEXT,
  zone TEXT,
  success BOOLEAN,
  strength TEXT,
  detail1 TEXT,
  detail2 TEXT,
  is_highlight BOOLEAN,
  puck_xy JSONB,
  net_xy JSONB,
  players JSONB,
  linked_event_idx INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### stage_shifts_tracking

```sql
CREATE TABLE stage_shifts_tracking (
  id SERIAL PRIMARY KEY,
  game_id TEXT NOT NULL,
  shift_index INTEGER,
  period INTEGER,
  start_time TEXT,
  end_time TEXT,
  start_type TEXT,
  stop_type TEXT,
  strength TEXT,
  home_lineup JSONB,
  away_lineup JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Environment Variables

Required in production:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

Optional (for development):

```env
NODE_ENV=development
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "No game loaded" Error

**Problem**: Tracker shows "No game loaded"

**Solutions**:
- Make sure you're on `/tracker/{gameId}` route
- Check that gameId is a valid number
- Verify Supabase connection

#### 2. Rosters Not Loading

**Problem**: No players appear in roster

**Solutions**:
- Check `fact_gameroster` table has data for game_id
- Verify Supabase credentials are correct
- Check browser console for errors
- Try refreshing the page

#### 3. Sync Fails

**Problem**: "Sync failed" error

**Solutions**:
- Check Supabase tables exist (`stage_events_tracking`, `stage_shifts_tracking`)
- Verify table permissions (INSERT, SELECT, DELETE)
- Check network connection
- Review browser console for detailed errors

#### 4. Excel Export Fails

**Problem**: Export button doesn't work

**Solutions**:
- Install `xlsx` package: `npm install xlsx`
- If using TypeScript, install types: `npm install --save-dev @types/xlsx` (if available)
- Verify browser allows downloads
- Check browser console for errors
- Note: Export uses dynamic import, so package must be in dependencies

#### 5. Build Errors

**Problem**: `npm run build` fails

**Solutions**:
- Run `npm install` to ensure dependencies are installed
- Check TypeScript errors: `npm run type-check`
- Verify all environment variables are set
- Check for missing imports or type errors

### Debug Mode

Enable debug logging:

```typescript
// In browser console
localStorage.setItem('tracker_debug', 'true')
```

This will log detailed information about:
- State changes
- API calls
- Sync operations
- Error details

---

## 📚 Additional Resources

- **Status Document**: `docs/TRACKER_REBUILD_STATUS.md`
- **Completion Summary**: `docs/TRACKER_REBUILD_COMPLETE.md`
- **Logic Extraction**: `docs/TRACKER_LOGIC_EXTRACTION.md`
- **Functions Index**: `docs/TRACKER_FUNCTIONS_INDEX.md`

---

## 🆘 Support

If you encounter issues:

1. Check browser console for errors
2. Verify Supabase connection
3. Check environment variables
4. Review this documentation
5. Check deployment logs (Vercel dashboard)

---

**The tracker is production-ready and fully functional!** 🎉
