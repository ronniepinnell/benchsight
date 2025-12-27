# BenchSight Wix Deployment Guide

## Overview

This guide explains how to deploy BenchSight dashboards to your Wix website.

---

## Option 1: Embed Static HTML (Recommended for MVP)

The `/html/` folder contains standalone HTML files that work anywhere:

| File | Purpose |
|------|---------|
| `dashboard_static.html` | Main dashboard with stats, games, players |
| `game_summary.html` | Individual game view (ESPN-style) |
| `player_card.html` | Player profile card |
| `tracker_v16.html` | Game tracker (copy from /tracker/) |

### Steps:

1. **Host the HTML files** somewhere accessible:
   - GitHub Pages (free)
   - Netlify (free)
   - Your own server
   - Wix's file manager (limited)

2. **In Wix Editor:**
   - Add an **HTML iframe** element
   - Set the iframe source to your hosted URL
   - Adjust size and positioning

```html
<!-- Example Wix HTML embed -->
<iframe 
    src="https://yoursite.github.io/benchsight/dashboard_static.html" 
    width="100%" 
    height="800px" 
    frameborder="0">
</iframe>
```

### Using GitHub Pages (Free Hosting):

1. Create a GitHub repo (e.g., `benchsight-dashboard`)
2. Upload the `/html/` folder contents
3. Go to Settings → Pages → Enable from main branch
4. Your URL: `https://yourusername.github.io/benchsight-dashboard/`

---

## Option 2: Wix Velo (JavaScript Backend)

For dynamic data, use Wix Velo to fetch from an API:

### Setup:

1. In Wix Editor, enable **Dev Mode** (toggle in top bar)
2. Add a **Custom Element** or use **Repeaters**
3. Create a backend file to fetch data

### Example Backend Code (`/backend/dashboardApi.jsw`):

```javascript
// Wix Velo backend module
import { fetch } from 'wix-fetch';

export async function getDashboardData() {
    // Option A: Fetch from your hosted JSON
    const response = await fetch('https://yoursite.com/data/dashboard.json');
    return response.json();
    
    // Option B: Return static data
    return {
        stats: { players: 335, teams: 26, games: 9 },
        games: [
            { id: 18987, home: 'Velociraptors', away: 'Black Widows', events: 3084 }
        ]
    };
}
```

### Frontend Code (Page Code):

```javascript
import { getDashboardData } from 'backend/dashboardApi';

$w.onReady(async function () {
    const data = await getDashboardData();
    
    // Update text elements
    $w('#statPlayers').text = data.stats.players.toString();
    $w('#statTeams').text = data.stats.teams.toString();
    
    // Populate repeater for games
    $w('#gamesRepeater').data = data.games;
});
```

---

## Option 3: External API + Wix

Run a simple API server and have Wix fetch from it:

### Flask API (add to `admin_portal.py`):

```python
@app.route('/api/dashboard')
def api_dashboard():
    # Enable CORS for Wix
    response = jsonify({
        'stats': get_dashboard_stats(),
        'games': get_game_list(),
        'players': get_top_players()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
```

### Host Options:
- **Render.com** (free tier available)
- **Railway.app** (free tier)
- **Heroku** (paid)
- **PythonAnywhere** (free tier)

---

## Data Flow for Wix

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Admin Portal  │     │  JSON/API Host  │     │    Wix Site     │
│   (local/server)│────►│ (GitHub/Render) │────►│   (embedded)    │
│                 │     │                 │     │                 │
│ • Track games   │     │ • dashboard.json│     │ • iframe embeds │
│ • Run ETL       │     │ • game_xxx.json │     │ • Velo fetches  │
│ • Export JSON   │     │ • player_xxx.json│    │ • Dynamic views │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Recommended Workflow

### For MVP:

1. **Run admin portal locally** → Track games, run ETL
2. **Export data to JSON** → Copy to GitHub repo
3. **Embed static HTML** in Wix → Dashboard shows latest data
4. **Update periodically** → Push new JSON, Wix auto-updates

### Export JSON Script (add to admin_portal.py):

```python
@app.route('/api/export-json')
def export_json():
    """Export all data to JSON for static hosting"""
    import json
    
    output = {
        'stats': {
            'players': count_players(),
            'teams': count_teams(),
            'games': count_games()
        },
        'games': get_game_list(),
        'players': get_all_players(),
        'updated': datetime.now().isoformat()
    }
    
    # Save to file
    with open('html/dashboard_data.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    return jsonify({'message': 'Exported to dashboard_data.json'})
```

---

## File Checklist for Wix

Upload these to your hosting:

```
html/
├── dashboard_static.html    # Main dashboard
├── game_summary.html        # Game view
├── player_card.html         # Player cards
├── dashboard_data.json      # Data file (exported from admin)
└── assets/                  # Any images/icons
```

---

## Troubleshooting

### iframe not loading in Wix:
- Make sure your host uses HTTPS
- Check Wix's iframe restrictions
- Try using Wix's HTML Component instead

### Data not updating:
- Clear browser cache
- Check JSON file was uploaded
- Verify fetch URL is correct

### CORS errors:
- Add CORS headers to your API
- Use a CORS proxy for testing
- Host everything on same domain

---

## Quick Start Commands

```bash
# 1. Start admin portal locally
cd benchsight_merged
python admin_portal.py

# 2. Track some games, run ETL

# 3. Export JSON for Wix
# (visit http://localhost:5000/api/export-json)

# 4. Copy html/ folder to GitHub repo
# 5. Enable GitHub Pages
# 6. Embed URL in Wix
```

---

## Support

- Documentation: `docs/MASTER_DOCUMENTATION.md`
- Notes/Requests: Use the `/notes` page in admin portal
- Issues: Track in your notes log

---

*Last Updated: December 2025*
