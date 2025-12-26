# LLM Handoff Document

## For GPT, Gemini, or Other AI Systems

This document helps any LLM understand and contribute to the BLB Hockey Analytics project.

---

## Project Summary

A hockey analytics platform for tracking recreational games:
- HTML/CSS/JS dashboards (no build tools)
- Event tracker for logging plays
- Integration with NORAD Hockey League data

**User:** Ronnie Pinnell (Velodrome team, Defense)
**Primary Dev:** Claude (Anthropic)

---

## Key Files

| File | Purpose |
|------|---------|
| `dashboards/index.html` | Main portal |
| `dashboards/dashboard_game.html` | Game detail + video |
| `tracker/tracker_v15.html` | Event tracking |
| `data/teams.json` | Team colors/logos |
| `data/velodrome_stats.json` | Player stats |

---

## Current State

### Working
- All dashboards functional
- Tracker v15 with fixes
- Real data integration
- Video modal with YouTube

### Needs Work
- Import Excel alignment
- TOI calculations
- More dashboard details
- Real tracking data → dashboard pipeline

---

## Important Rules

1. Player names: "First Initial. Last Name" (e.g., "R. Pinnell")
2. Team names, not venues (e.g., "Velodrome" not "Home")
3. Stats must match BLB_Tables source
4. No plots for games without XY data
5. Admin features hidden from public view

---

## Real Stats Reference

```
R. Pinnell: 12 GP, 1 G, 2 A = 3 P (NOT 8!)
S. Downs:   14 GP, 12 G, 8 A = 20 P (top scorer)
```

---

## Priority Tasks

1. Load real tracking Excel → dashboards
2. Fix TOI calculations
3. Build zone analysis dashboard
4. Create game flow visualization
5. Test Wix embedding
