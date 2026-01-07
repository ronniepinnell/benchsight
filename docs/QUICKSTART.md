# BenchSight Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Open the Tracker
```
Open: tracker/tracker_v22.html
```

### Step 2: Select a Game
1. Click the game dropdown in the header
2. Select a game (e.g., "18969 - Hawks vs Eagles")
3. Click **Load**

### Step 3: Start Tracking
1. **Select Team:** Click HOME or AWAY
2. **Set Period:** Click P1, P2, P3, or OT
3. **Set Time:** Edit the clock display

### Step 4: Track an Event
1. **Pick Event Type:** Press keyboard shortcut or click button
   - F = Faceoff
   - S = Shot
   - G = Goal
   - V = Save
   - P = Pass
   - etc.

2. **Click Rink:** Add puck location (up to 10 points)

3. **Add Players:** Click player chips from roster

4. **Save:** Press Enter or click Save

### Step 5: Push to Database
Click **↑ Push** to save to Supabase

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F | Faceoff |
| S | Shot |
| G | Goal |
| V | Save |
| P | Pass |
| T | Turnover |
| Z | Zone Entry |
| X | Zone Exit |
| H | Hit |
| B | Block |
| R | Retrieval |
| W | Stoppage |
| Space | Toggle Success |
| Enter | Save Event |
| 1-4 | Set Period |
| Esc | Clear Form |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |

---

## 🏒 Tracking Tips

### For Shots
1. Click rink to mark shot location
2. Click net target to mark where shot was aimed
3. Add shooter as P1
4. Shot will auto-link to Save

### For Passes
1. Mark start position on rink
2. Mark end position on rink
3. Add passer as P1, receiver as P2
4. Set success (✓ or ✗)

### For Shifts
1. Set shift start time
2. Assign players to on-ice slots (LW, C, RW, LD, RD, G)
3. Click "End Shift" when line changes
4. Click "+ New Shift"

---

## 📊 Viewing Analytics

### Open Dashboard
```
Open: dashboard/dashboard_v4.html
```

### Views Available
- **Overview:** Score, team comparison, timeline
- **Box Score:** Full player stats table
- **Shot Chart:** Interactive rink with shots
- **Players:** Player cards with stats
- **Advanced:** Corsi, Fenwick, event breakdown
- **H2H:** Compare two players

---

## 💾 Saving Your Work

### Auto-Save
- Data saves to browser localStorage automatically
- Persists between sessions

### Push to Supabase
- Click **↑ Push** to save to cloud
- Data becomes available in dashboard

### Export to Excel
- Click **📥** to download .xlsx file
- Contains events and shifts sheets

---

## ❓ Troubleshooting

### "No games in dropdown"
- Check internet connection
- Supabase may be down
- Try refreshing page

### "Events not saving"
- Make sure game is loaded
- Select event type before saving
- Check console for errors (F12)

### "Data not showing in dashboard"
- Click ↑ Push in tracker first
- Refresh dashboard
- Check game is selected

---

## 📞 Need Help?

1. Check `docs/README.md` for full documentation
2. Check `docs/GAMEPLAN.md` for development status
3. Review code comments in tracker_v22.html

---

*Quick Start Guide v1.0*
