# BenchSight Tracker Development Plan

**Version**: v16.08  
**Date**: January 8, 2026  
**Status**: Active Development

---

## 📋 Issues Identified (Current State)

### Critical Bugs
| Issue | Description | Priority |
|-------|-------------|----------|
| Player duplicates | Multiple #3s showing for same team (19032 Outlaws) | P0 |
| Middle column no resize | Only left/right panels resize, center is fixed | P1 |
| Team colors not loading | Should load from dim_team hex column | P1 |
| Play details wrong | Not using dim tables for dropdowns | P1 |
| No shift log | Shifts are logged but not displayed | P1 |
| XY edit missing | No way to edit player XY in edit modal | P2 |

### Missing Features
| Feature | Description | Priority |
|---------|-------------|----------|
| Save/Resume | Pick up where you left off | P0 |
| Edit tracked games | Load and modify existing event data | P1 |
| Box score | Live game summary during tracking | P1 |
| Verification panel | Compare tracked vs official data | P2 |
| Team logos | Load from dim_team if available | P3 |

### Logic Issues
| Issue | Correct Behavior |
|-------|------------------|
| Strength | Derive from # of players on ice per team |
| Pressured by | Auto-detect any opp player within X feet |
| Team dropdown | Show team name, not "Home"/"Away" |
| Edit defaults | Play details blank, success blank → then derive |

---

## 🏗️ Development Phases

### Phase 1: Data Fixes (Immediate)

#### 1.1 Fix Player Duplicates
```javascript
// Problem: Same jersey number appears multiple times
// Solution: Query unique players, handle multi-position players
const { data } = await sb.from('fact_gameroster')
  .select('player_id,player_game_number,player_full_name,player_position,team_venue')
  .eq('game_id', gid)
  .order('player_game_number');

// Group by player_id to avoid duplicates
const unique = {};
data.forEach(p => {
  if (!unique[p.player_id]) unique[p.player_id] = p;
});
```

#### 1.2 Load Team Colors
```javascript
// Add to selectGame()
const { data: teamData } = await sb.from('dim_team')
  .select('team_name,hex')
  .in('team_name', [g.home_team_name, g.away_team_name]);

// Apply colors
const homeTeam = teamData.find(t => t.team_name === g.home_team_name);
const awayTeam = teamData.find(t => t.team_name === g.away_team_name);
S.homeColor = homeTeam?.hex || '#3b82f6';
S.awayColor = awayTeam?.hex || '#ef4444';
```

#### 1.3 Load Play Details from Dim Tables
```javascript
// On init, fetch:
const { data: playDetails } = await sb.from('dim_play_detail').select('*');
const { data: playDetails2 } = await sb.from('dim_play_detail_2').select('*');
const { data: eventDetails } = await sb.from('dim_event_detail').select('*');
// Store in S.dims for dropdown population
```

#### 1.4 Show Team Names (not H/A)
```html
<!-- Change team toggle -->
<button class="home active" id="evtHomeLbl" onclick="setEvtTeam('home')">Velodrome</button>
<button class="away" id="evtAwayLbl" onclick="setEvtTeam('away')">Outlaws</button>
```

---

### Phase 2: Core Features

#### 2.1 Save/Resume Game State

**Data Structure:**
```javascript
const gameState = {
  gameId: 19032,
  version: '14.05',
  savedAt: '2026-01-07T22:45:00Z',
  period: 2,
  clock: '14:32',
  events: [...],
  shifts: [...],
  slots: { home: {...}, away: {...} },
  lastEventIdx: 45,
  lastShiftIdx: 12
};
```

**Storage Options:**
1. **localStorage** (current) - Works offline, per-browser
2. **Supabase** (new) - Sync across devices, backup

**UI:**
- "Resume" button if saved state exists
- "New Game" clears state
- Auto-save every 30 seconds
- Manual "Save" button

#### 2.2 Edit Existing Tracked Games

**Workflow:**
1. Load game from Supabase `fact_events` + `fact_event_players`
2. Convert to tracker format
3. Allow edits
4. Re-export to tracking file format

**Challenges:**
- Matching player roles to tracker structure
- Reconstructing XY data
- Preserving original event indices

#### 2.3 Shift Log Display

**Add to left panel:**
```html
<div class="shift-log" id="shiftLog">
  <div class="shift-log-header">
    <span>#</span><span>Period</span><span>Start</span><span>End</span>
  </div>
  <div id="shiftLogBody"></div>
</div>
```

**Display format:**
| # | Period | Start | End | Type |
|---|--------|-------|-----|------|
| 1 | P1 | 20:00 | 18:32 | GameStart |
| 2 | P1 | 18:32 | 17:45 | OnTheFly |

#### 2.4 Box Score Panel

**Live stats during tracking:**
```
╔════════════════════════════════════╗
║         Velodrome vs Outlaws       ║
╠════════════════════════════════════╣
║  SCORE      2  -  1                ║
║  SHOTS     12  -  8                ║
║  FACEOFFS  6W - 4W (60%)           ║
║  HITS       3  -  5                ║
║  TURNOVERS  2  -  3                ║
╚════════════════════════════════════╝
```

---

### Phase 3: Smart Logic

#### 3.1 Auto-Derive Strength
```javascript
function deriveStrength() {
  const homeOnIce = Object.values(S.slots.home).filter(Boolean).length;
  const awayOnIce = Object.values(S.slots.away).filter(Boolean).length;
  
  // Standard situations
  if (homeOnIce === 6 && awayOnIce === 6) return '5v5';
  if (homeOnIce === 6 && awayOnIce === 5) return '5v4'; // Home PP
  if (homeOnIce === 5 && awayOnIce === 6) return '4v5'; // Home PK
  if (homeOnIce === 5 && awayOnIce === 5) return '4v4';
  
  // Check for empty net (no goalie)
  if (!S.slots.home.G && homeOnIce === 6) return 'ENG';
  if (!S.slots.away.G && awayOnIce === 6) return 'ENA';
  
  return `${homeOnIce-1}v${awayOnIce-1}`;
}
```

#### 3.2 Auto-Detect Pressure
```javascript
function detectAllPressure() {
  const threshold = parseInt(document.getElementById('pressureDist').value) || 10;
  const evtPlayers = S.curr.players.filter(p => p.role.startsWith('event'));
  const oppPlayers = S.curr.players.filter(p => p.role.startsWith('opp'));
  
  evtPlayers.forEach(ep => {
    if (!ep.xy?.length) return;
    const epPos = ep.xy[ep.xy.length - 1];
    
    // Find closest opponent
    let closestOpp = null;
    let closestDist = Infinity;
    
    oppPlayers.forEach(op => {
      if (!op.xy?.length) return;
      const opPos = op.xy[op.xy.length - 1];
      const dist = Math.sqrt(Math.pow(epPos.x - opPos.x, 2) + Math.pow(epPos.y - opPos.y, 2));
      if (dist < threshold && dist < closestDist) {
        closestDist = dist;
        closestOpp = op;
      }
    });
    
    ep.pressure = closestOpp?.num || '';
    ep.pressureDist = closestDist < Infinity ? Math.round(closestDist) : null;
  });
}
```

#### 3.3 Success Logic by Event Type
```javascript
const SUCCESS_RULES = {
  Shot: {
    's': ['Shot_OnNetSaved', 'Shot_OnNetGoal', 'Shot_Tipped', 'Shot_Deflected'],
    'u': ['Shot_Missed', 'Shot_Blocked', 'Shot_BlockedSameTeam']
  },
  Pass: {
    's': ['Pass_Completed'],
    'u': ['Pass_Missed', 'Pass_Deflected', 'Pass_Intercepted']
  },
  Zone_Entry_Exit: {
    's': ['Zone_Entry', 'Zone_Exit', 'Zone_Keepin'],
    'u': ['Zone_EntryFailed', 'Zone_ExitFailed', 'Zone_KeepinFailed']
  },
  Turnover: {
    's': ['Turnover_Takeaway'],
    'u': ['Turnover_Giveaway']
  },
  Faceoff: {
    's': ['Won'],
    'u': ['Lost']
  }
};
```

---

### Phase 4: UI Improvements

#### 4.1 Center Column Resize
```javascript
// Add resize handles to center panel
function setupCenterResize() {
  const leftHandle = document.createElement('div');
  leftHandle.className = 'resize-handle left';
  leftHandle.onmousedown = (e) => startResize(e, 'center-left');
  
  const rightHandle = document.createElement('div');
  rightHandle.className = 'resize-handle right';
  rightHandle.onmousedown = (e) => startResize(e, 'center-right');
  
  document.querySelector('.center').appendChild(leftHandle);
  document.querySelector('.center').appendChild(rightHandle);
}
```

#### 4.2 XY Edit in Modal
```html
<!-- Add to edit modal -->
<div class="section-title">Player XY Locations (click rink to edit)</div>
<div id="editPlayerXYList">
  <!-- For each player: -->
  <div class="edit-player-xy">
    <span>#9 Pinnell</span>
    <div class="xy-mini-grid">
      <button class="xy-pt" data-idx="0">1: (45.2, 32.1)</button>
      <button class="xy-pt" data-idx="1">2: (50.3, 28.4)</button>
      <button class="xy-del">✕</button>
    </div>
  </div>
</div>
```

#### 4.3 Home/Away Indicator
```html
<!-- Add to header -->
<div class="matchup">
  <span class="team home">
    <span class="team-dot" style="background:#9C47E4"></span>
    Velodrome (HOME)
  </span>
  <span class="vs">vs</span>
  <span class="team away">
    <span class="team-dot" style="background:#02007B"></span>
    Outlaws (AWAY)
  </span>
</div>
```

---

### Phase 5: Verification & QA

#### 5.1 Box Score Verification
Compare tracked stats vs official:
```
╔════════════════════════════════════════════════╗
║            VERIFICATION REPORT                 ║
╠════════════════════════════════════════════════╣
║ Metric      Tracked   Official   Status        ║
╠════════════════════════════════════════════════╣
║ Home Goals    3         3        ✅ MATCH      ║
║ Away Goals    2         2        ✅ MATCH      ║
║ Total Shots  24        26        ⚠️ -2         ║
║ Penalties     4         4        ✅ MATCH      ║
╚════════════════════════════════════════════════╝
```

#### 5.2 Event Validation Rules
- Goals must have netXY
- Shots must have puckXY
- Faceoffs need 2 players (one per team)
- Zone entries need prior neutral zone puckXY

---

## 📅 Implementation Schedule

### Week 1: Data Fixes
- [ ] Fix player duplicates
- [ ] Load team colors from dim_team
- [ ] Load play details from dim tables
- [ ] Team names in dropdowns
- [ ] Shift log display

### Week 2: Save/Resume
- [ ] Implement gameState structure
- [ ] localStorage save/load
- [ ] Supabase sync option
- [ ] Resume UI

### Week 3: Edit Features
- [ ] XY edit in modal
- [ ] Player picker in edit
- [ ] Load existing games
- [ ] Re-export capability

### Week 4: Smart Logic
- [ ] Auto-derive strength
- [ ] Pressure detection
- [ ] Success derivation
- [ ] Center column resize

### Week 5: Verification
- [ ] Box score panel
- [ ] Verification comparison
- [ ] Event validation
- [ ] Export validation

---

## 🗄️ Database Dependencies

### Tables Needed
| Table | Use |
|-------|-----|
| dim_team | Team colors, logos, names |
| dim_play_detail | Play detail dropdown options |
| dim_play_detail_2 | Play detail 2 dropdown options |
| dim_event_detail | Event detail dropdown options |
| dim_event_detail_2 | Event detail 2 dropdown options |
| fact_gameroster | Player rosters (fix duplicates) |
| dim_schedule | Game list |
| fact_events | Existing tracked events (for editing) |
| fact_event_players | Player-level event data |

### New Table: tracking_sessions
```sql
CREATE TABLE tracking_sessions (
  session_id UUID PRIMARY KEY,
  game_id INT REFERENCES dim_schedule(game_id),
  user_id TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  state JSONB,
  status TEXT -- 'in_progress', 'completed', 'abandoned'
);
```

---

## ✅ Definition of Done

A tracker version is "complete" when:
1. All games in dim_schedule are selectable
2. Rosters load without duplicates
3. Team colors display correctly
4. All event/play details use dim tables
5. Events can be saved, resumed, and edited
6. Box score matches official stats
7. Export produces valid ETL input

---

*Last Updated: January 8, 2026*
