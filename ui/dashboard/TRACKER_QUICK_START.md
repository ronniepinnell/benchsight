# Tracker Quick Start Guide

**Get the tracker running in 5 minutes**

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd ui/dashboard
npm install
```

**Important**: Make sure `xlsx` is installed for Excel export:

```bash
npm install xlsx
```

### 2. Set Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### 3. Run Development Server

```bash
npm run dev
```

### 4. Open Tracker

Navigate to: http://localhost:3000/tracker

---

## 📝 Basic Usage

### Start Tracking a Game

1. Go to `/tracker`
2. Select a game from the list
3. Or click "New Tracking Session" and enter game ID

### Track an Event

1. Press **S** (Shot) or click event type button
2. Press **H** (Home) or **A** (Away) for team
3. Click rink to place XY coordinates
4. Press **Enter** to log event

### Track a Shift

1. Click empty slots to add players to lineup
2. Enter start/end times
3. Press **L** to log shift

### Sync to Cloud

- Click **☁️ Sync** button in header
- Or wait for auto-save (every 30 seconds)

### Export Data

- Click **📥 Export** button
- Excel file downloads automatically

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **F** | Faceoff |
| **S** | Shot |
| **P** | Pass |
| **G** | Goal |
| **T** | Turnover |
| **Z** | Zone Entry/Exit |
| **N** | Penalty |
| **X** | Stoppage |
| **H** | Home team |
| **A** | Away team |
| **L** | Log shift |
| **M** | Toggle XY mode |
| **Enter** | Submit event |
| **Escape** | Clear current event |

---

## 🐛 Quick Troubleshooting

**No rosters loading?**
- Check Supabase connection
- Verify `fact_gameroster` has data for your game_id

**Sync failing?**
- Check `stage_events_tracking` and `stage_shifts_tracking` tables exist
- Verify table permissions

**Export not working?**
- Run: `npm install xlsx`
- Check browser console for errors

---

## 📚 Full Documentation

See `docs/TRACKER_USAGE_AND_DEPLOYMENT.md` for complete guide.

---

**Ready to track!** 🏒
