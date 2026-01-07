# BenchSight Tracker - Developer Handoff Document

**Version:** 1.0  
**Date:** 2026-01-07  
**Author:** Claude (AI Assistant)  
**For:** Future developer continuing tracker development

---

## CRITICAL: Read This First

This document contains everything you need to continue developing the BenchSight Tracker application. If the conversation with the original developer was cut off, this document serves as the complete handoff.

### Project Status

| Component | Status | Priority |
|-----------|--------|----------|
| MVP HTML Tracker | ✅ Working | - |
| Supabase Integration | 🔶 Needs Setup | HIGH |
| XY Visualization | 🔶 Basic, needs enhancement | HIGH |
| Video Integration | ❌ Not started | HIGH |
| Resizable Panels | ❌ Not started | MEDIUM |
| NORAD Validation | ❌ Not started | MEDIUM |
| Electron Wrapper | ❌ Not started | LOW |

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Cascading Dropdown Logic](#cascading-dropdown-logic)
4. [XY Coordinate System](#xy-coordinate-system)
5. [Linked Event Logic](#linked-event-logic)
6. [Video Integration Plan](#video-integration-plan)
7. [NORAD Validation](#norad-validation)
8. [Batch Edit Mode](#batch-edit-mode)
9. [Electron Wrapper Plan](#electron-wrapper-plan)
10. [Implementation Checklist](#implementation-checklist)
11. [Known Issues & TODOs](#known-issues--todos)

---

## Project Overview

### What is BenchSight Tracker?

A desktop application for tracking detailed hockey game events. The tracker:
1. Pulls game/roster data from Supabase
2. Allows manual event tracking with XY coordinates
3. Exports data matching the existing ETL input format
4. Validates against official NORAD league records

### The User (Ronnie)

- Tracks his own team (Velodrome) games
- Currently backlogged on tracking
- Needs SPEED over perfection
- Wants minimal clicks, maximum hotkey usage
- Has YouTube videos of games for reference

### Output Requirements

**CRITICAL:** Output must match existing ETL format exactly:
- Events → `{gameid}_tracking.xlsx` Events tab
- Shifts → `{gameid}_tracking.xlsx` Shifts tab

See `/docs/TRACKING_TEMPLATE_ANALYSIS.md` for full column specs.

---

## Architecture

### Current (MVP)

```
┌─────────────────────────────────────────┐
│  Single HTML File                        │
│  ├── Inline CSS                         │
│  ├── Inline JavaScript                  │
│  ├── Supabase JS SDK (CDN)              │
│  └── SheetJS XLSX (CDN)                 │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  localStorage (auto-save)               │
│  - benchsight_{gameId}                  │
│  - benchsight_settings                  │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Supabase (optional)                    │
│  - dim_games                            │
│  - dim_game_rosters                     │
│  - dim_event_types                      │
│  - dim_event_details                    │
└─────────────────────────────────────────┘
```

### Target (Electron)

```
┌─────────────────────────────────────────┐
│  Electron App                            │
│  ├── React Frontend                     │
│  │   ├── Resizable Panels               │
│  │   ├── Video Player (YouTube + Local) │
│  │   ├── SVG Rink with XY               │
│  │   └── Event/Shift Forms              │
│  ├── Local SQLite (fast saves)          │
│  └── File System (video files, backups) │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Supabase (cloud sync)                  │
│  - All dim tables                       │
│  - stage_tracker_events                 │
│  - stage_tracker_shifts                 │
└─────────────────────────────────────────┘
```

---

## Cascading Dropdown Logic

### The Problem

When user selects an event type, the detail dropdowns should:
1. Show only relevant options for that event type
2. Detail 2 may depend on Detail 1 selection (cascading)

### Data Source

Pull from Supabase `dim_event_details` table:

```javascript
// Load dropdown options from Supabase
async function loadEventOptions() {
  const { data: eventTypes } = await supabase
    .from('dim_event_types')
    .select('*')
    .eq('active', true)
    .order('sort_order');
  
  const { data: eventDetails } = await supabase
    .from('dim_event_details')
    .select('*')
    .eq('active', true)
    .order('sort_order');
  
  // Build lookup structure
  const detailsByType = {};
  eventDetails.forEach(d => {
    if (!detailsByType[d.event_type]) {
      detailsByType[d.event_type] = { d1: [], d2: {} };
    }
    if (d.detail_level === 1) {
      detailsByType[d.event_type].d1.push(d);
    } else {
      // d2 can be filtered by parent_detail if set
      if (!detailsByType[d.event_type].d2[d.parent_detail || '*']) {
        detailsByType[d.event_type].d2[d.parent_detail || '*'] = [];
      }
      detailsByType[d.event_type].d2[d.parent_detail || '*'].push(d);
    }
  });
  
  return { eventTypes, detailsByType };
}
```

### Implementation

```javascript
function setEventType(type) {
  STATE.eventType = type;
  
  // Get options for this type
  const opts = STATE.detailsByType[type] || { d1: [], d2: {} };
  
  // Populate Detail 1
  const d1Select = document.getElementById('evtDetail1');
  d1Select.innerHTML = '<option value="">--</option>' + 
    opts.d1.map(o => `<option value="${o.detail_value}">${o.display_name || o.detail_value}</option>`).join('');
  
  // Clear Detail 2 (will populate on d1 change)
  document.getElementById('evtDetail2').innerHTML = '<option value="">--</option>';
}

function onDetail1Change() {
  const type = STATE.eventType;
  const d1Value = document.getElementById('evtDetail1').value;
  
  const opts = STATE.detailsByType[type] || { d1: [], d2: {} };
  
  // Get d2 options - check for parent-specific first, then wildcard
  const d2Opts = opts.d2[d1Value] || opts.d2['*'] || [];
  
  const d2Select = document.getElementById('evtDetail2');
  d2Select.innerHTML = '<option value="">--</option>' + 
    d2Opts.map(o => `<option value="${o.detail_value}">${o.display_name || o.detail_value}</option>`).join('');
}
```

### Example Cascade

For Penalty:
- Detail 1: Minor, Major, Misconduct
- Detail 2: Tripping, Hooking, etc. (same for all d1 values, parent_detail = null)

For Shot (if we wanted cascade):
- Detail 1: OnNetSaved, Missed, Blocked, Goal
- Detail 2 for OnNetSaved: Rebound, Freeze
- Detail 2 for Missed: Wide, High, Post
- (Currently we don't cascade Shot d2, but the structure supports it)

---

## XY Coordinate System

### Current State (MVP)

- Click on rink → stores puck position
- Single color dots
- Up to 5 positions per event
- No player positions

### Required Enhancements

#### 1. Team Colors

```javascript
// Get team colors from game data
const colors = {
  home: STATE.homeColor,  // e.g., '#3b82f6'
  away: STATE.awayColor   // e.g., '#ef4444'
};

function renderMarker(player, position, opacity) {
  const color = player.team === 'home' ? colors.home : colors.away;
  
  // Circle with team color
  const circle = createSVGElement('circle', {
    cx: position.x,
    cy: position.y,
    r: 3,
    fill: color,
    stroke: '#fff',
    'stroke-width': 0.5,
    opacity: opacity
  });
  
  // Jersey number inside
  const text = createSVGElement('text', {
    x: position.x,
    y: position.y + 1,
    fill: '#fff',
    'font-size': '3',
    'text-anchor': 'middle',
    opacity: opacity
  });
  text.textContent = player.num;
  
  return [circle, text];
}
```

#### 2. Multiple Events Visible

```javascript
const EVENT_HISTORY_COUNT = 5;
const OPACITY_SCALE = [0.15, 0.3, 0.5, 0.7, 1.0];  // Oldest → newest

function renderEventHistory() {
  const layer = document.getElementById('markersLayer');
  layer.innerHTML = '';
  
  const recentEvents = STATE.events.slice(-EVENT_HISTORY_COUNT);
  
  recentEvents.forEach((evt, eventIdx) => {
    const opacity = OPACITY_SCALE[eventIdx];
    const eventColor = evt.team === 'home' ? STATE.homeColor : STATE.awayColor;
    
    // Puck positions
    renderPuckPath(evt.puckXY, opacity, layer);
    
    // Event player positions
    evt.players?.forEach(player => {
      const xy = evt.playerXY?.find(p => p.num === player.num);
      if (xy) {
        renderPlayerPath(player, xy.positions, eventColor, opacity, layer);
      }
    });
    
    // Opposing player positions
    evt.oppPlayers?.forEach(player => {
      const oppColor = evt.team === 'home' ? STATE.awayColor : STATE.homeColor;
      const xy = evt.playerXY?.find(p => p.num === player.num);
      if (xy) {
        renderPlayerPath(player, xy.positions, oppColor, opacity, layer);
      }
    });
  });
}
```

#### 3. Lines Connecting Positions

```javascript
function renderPlayerPath(player, positions, color, opacity, layer) {
  if (!positions || positions.length === 0) return;
  
  // Sort by sequence
  const sorted = [...positions].sort((a, b) => a.seq - b.seq);
  
  // Draw connecting lines first (behind dots)
  for (let i = 0; i < sorted.length - 1; i++) {
    const line = createSVGElement('line', {
      x1: sorted[i].x,
      y1: sorted[i].y,
      x2: sorted[i + 1].x,
      y2: sorted[i + 1].y,
      stroke: color,
      'stroke-width': 1,
      'stroke-dasharray': '2,1',
      opacity: opacity * 0.7
    });
    layer.appendChild(line);
  }
  
  // Draw dots on top
  sorted.forEach((pos, idx) => {
    const isLatest = idx === sorted.length - 1;
    
    const circle = createSVGElement('circle', {
      cx: pos.x,
      cy: pos.y,
      r: isLatest ? 3.5 : 2.5,
      fill: color,
      stroke: '#fff',
      'stroke-width': isLatest ? 0.8 : 0.4,
      opacity: opacity
    });
    layer.appendChild(circle);
    
    // Player number (only on latest position)
    if (isLatest) {
      const text = createSVGElement('text', {
        x: pos.x,
        y: pos.y + 1,
        fill: '#fff',
        'font-size': '3',
        'font-weight': 'bold',
        'text-anchor': 'middle',
        opacity: opacity
      });
      text.textContent = player.num;
      layer.appendChild(text);
    }
  });
}
```

#### 4. XY Data Structure

```javascript
// Per-event XY storage
{
  puckXY: [
    { seq: 1, x: 45.2, y: 32.1 },
    { seq: 2, x: 62.8, y: 28.4 }
  ],
  playerXY: [
    {
      num: '42',      // Jersey number
      name: 'Ashcroft',
      role: 'event_player_1',  // or 'opp_player_1'
      positions: [
        { seq: 1, x: 38.1, y: 40.2 },
        { seq: 2, x: 55.3, y: 35.1 }
      ]
    },
    {
      num: '9',
      name: 'Pinnell',
      role: 'event_player_2',
      positions: [
        { seq: 1, x: 42.0, y: 22.5 }
      ]
    }
  ],
  netXY: { x: 3, y: 2 }  // Grid position for shots
}
```

#### 5. XY Mode Selection

```javascript
// XY entry modes
const XY_MODES = {
  puck: { label: '🏒 Puck', maxSlots: 5 },
  event: { label: '👤 Event Player', maxSlots: 10 },
  opp: { label: '👥 Opp Player', maxSlots: 10 }
};

let currentXYMode = 'puck';
let currentXYSlot = 1;
let currentPlayerForXY = null;  // Which player we're placing

function handleRinkClick(e) {
  const pos = getClickPosition(e);
  
  if (currentXYMode === 'puck') {
    STATE.currentEvent.puckXY.push({ seq: currentXYSlot, ...pos });
    currentXYSlot++;
  } else {
    // Player XY - need to know which player
    if (!currentPlayerForXY) {
      toast('Select a player first', 'warn');
      return;
    }
    
    let playerEntry = STATE.currentEvent.playerXY.find(p => p.num === currentPlayerForXY.num);
    if (!playerEntry) {
      playerEntry = {
        num: currentPlayerForXY.num,
        name: currentPlayerForXY.name,
        role: currentXYMode === 'event' ? 'event_player' : 'opp_player',
        positions: []
      };
      STATE.currentEvent.playerXY.push(playerEntry);
    }
    
    playerEntry.positions.push({ seq: playerEntry.positions.length + 1, ...pos });
  }
  
  renderRinkMarkers();
}
```

---

## Linked Event Logic

### Auto-Link Rules

| Primary Event | Auto-Creates | Confidence |
|---------------|--------------|------------|
| Shot (OnNetSaved) | Save | 99% |
| Save (Freeze) | Stoppage → DeadIce | 91% |
| Goal | Stoppage | 100% |
| Stoppage | DeadIce | 80% |

### Implementation

```javascript
const AUTO_LINK_RULES = {
  'Shot_OnNetSaved': {
    creates: 'Save',
    autoCreate: true,  // Don't ask, just do it
    transform: (shotEvt) => ({
      type: 'Save',
      detail1: 'Rebound',  // Default, user can change
      team: flipTeam(shotEvt.team),
      zone: flipZone(shotEvt.zone),
      // Flip players
      players: shotEvt.oppPlayers.filter(p => p.pos === 'G'),
      oppPlayers: shotEvt.players,
      // Copy XY
      puckXY: shotEvt.puckXY,
      playerXY: shotEvt.playerXY
    })
  },
  
  'Save_Freeze': {
    creates: 'Stoppage',
    autoCreate: true,
    transform: (saveEvt) => ({
      type: 'Stoppage',
      detail1: 'Play',
      team: saveEvt.team,
      zone: saveEvt.zone,
      puckXY: saveEvt.puckXY
    }),
    chain: 'DeadIce'  // Also creates DeadIce after Stoppage
  },
  
  'Goal': {
    creates: 'Stoppage',
    autoCreate: false,  // Prompt first
    transform: (goalEvt) => ({
      type: 'Stoppage',
      detail1: 'Goal',
      team: goalEvt.team,
      zone: goalEvt.zone,
      puckXY: goalEvt.puckXY
    })
  }
};

function checkAutoLinks(evt) {
  const key = `${evt.type}_${evt.detail1}` || evt.type;
  const rule = AUTO_LINK_RULES[key];
  
  if (!rule) return;
  
  if (rule.autoCreate) {
    createLinkedEvent(evt, rule);
  } else {
    // Prompt user
    showLinkedEventPrompt(evt, rule);
  }
}

function createLinkedEvent(originalEvt, rule) {
  const linkedEvt = {
    idx: ++STATE.evtIdx,
    gameId: STATE.gameId,
    period: originalEvt.period,
    startTime: originalEvt.startTime,
    endTime: originalEvt.endTime,
    linkedTo: originalEvt.idx,
    timestamp: new Date().toISOString(),
    ...rule.transform(originalEvt)
  };
  
  STATE.events.push(linkedEvt);
  
  // Chain if needed
  if (rule.chain) {
    const chainRule = AUTO_LINK_RULES[linkedEvt.type];
    if (chainRule) {
      createLinkedEvent(linkedEvt, chainRule);
    }
  }
  
  renderEventList();
  toast(`Created linked ${linkedEvt.type}`, 'success');
}
```

### Manual Linked Event

When user presses `L`:
1. Copy all data from last event
2. Clear event type (user must select new type)
3. Keep players, XY, times

---

## Video Integration Plan

### Phase 1: YouTube Embed

```javascript
// YouTube IFrame API
function initYouTubePlayer(videoId, startOffset) {
  return new YT.Player('videoPlayer', {
    videoId: videoId,
    playerVars: {
      start: startOffset,  // Offset to game start
      controls: 1,
      modestbranding: 1
    },
    events: {
      onStateChange: onPlayerStateChange,
      onReady: onPlayerReady
    }
  });
}

function syncVideoToGameTime(gameMinutes, gameSeconds, period) {
  // Calculate video time
  // Period 1: 0 offset
  // Period 2: +1152 sec (18 min period + ~72 sec intermission)
  // Period 3: +2296 sec
  
  const periodOffsets = {
    1: 0,
    2: 18 * 60 + 72,   // ~1152
    3: 36 * 60 + 136   // ~2296
  };
  
  const periodOffset = periodOffsets[period] || 0;
  const gameTime = (18 - gameMinutes) * 60 + (60 - gameSeconds);  // Convert countdown to elapsed
  const videoTime = STATE.videoStartOffset + periodOffset + gameTime;
  
  player.seekTo(videoTime);
}
```

### Phase 2: Local Video Files

```javascript
// Electron only - local file access
const videoElement = document.getElementById('localVideo');

function loadLocalVideo(filePath) {
  videoElement.src = `file://${filePath}`;
  videoElement.load();
}

// Multi-angle support
const videoAngles = [
  { name: 'Main', element: document.getElementById('video1') },
  { name: 'Alt', element: document.getElementById('video2') }
];

function switchAngle(idx) {
  videoAngles.forEach((v, i) => {
    v.element.style.display = i === idx ? 'block' : 'none';
  });
}
```

### Phase 3: Video ↔ Event Sync

```javascript
// Store video time with each event
function logEvent() {
  const evt = {
    ...eventData,
    videoTimeSeconds: getCurrentVideoTime()
  };
  
  STATE.events.push(evt);
}

// Jump to event in video
function jumpToEvent(evt) {
  if (evt.videoTimeSeconds) {
    player.seekTo(evt.videoTimeSeconds);
  }
}

// Generate YouTube deep link
function getEventYouTubeLink(evt) {
  const videoId = STATE.youtubeVideoId;
  const time = evt.videoTimeSeconds;
  return `https://youtube.com/watch?v=${videoId}&t=${time}s`;
}
```

---

## NORAD Validation

### What It Does

Compares tracked goals against official NORAD league records to catch:
- Missing goals
- Extra goals (tracking errors)
- Wrong scorer
- Wrong period/time

### Implementation

```javascript
async function loadNoradGoals(gameId) {
  const { data, error } = await supabase
    .from('fact_norad_goals')
    .select('*')
    .eq('game_id', gameId);
  
  return data || [];
}

function validateGoals() {
  const noradGoals = STATE.noradGoals;
  const trackedGoals = STATE.events.filter(e => e.type === 'Goal');
  
  const warnings = [];
  
  // Check count
  if (trackedGoals.length !== noradGoals.length) {
    warnings.push({
      type: 'count_mismatch',
      message: `Tracked ${trackedGoals.length} goals, NORAD has ${noradGoals.length}`,
      severity: 'error'
    });
  }
  
  // Check each NORAD goal
  noradGoals.forEach(ng => {
    const matching = trackedGoals.find(tg => 
      tg.period == ng.period &&
      Math.abs(timeToSeconds(tg.startTime) - (ng.time_min * 60 + ng.time_sec)) < 30 &&
      tg.team === ng.scoring_team_venue
    );
    
    if (!matching) {
      warnings.push({
        type: 'missing_goal',
        message: `NORAD: ${ng.goal_scorer} (#${ng.goal_scorer_number}) at ${ng.time_min}:${ng.time_sec} P${ng.period}`,
        severity: 'error',
        noradGoal: ng
      });
    } else if (matching.players?.[0]?.num !== ng.goal_scorer_number) {
      warnings.push({
        type: 'scorer_mismatch',
        message: `Tracked #${matching.players?.[0]?.num}, NORAD says #${ng.goal_scorer_number}`,
        severity: 'warning',
        trackedEvent: matching,
        noradGoal: ng
      });
    }
  });
  
  // Check for extra tracked goals
  trackedGoals.forEach(tg => {
    const matching = noradGoals.find(ng =>
      ng.period == tg.period &&
      Math.abs((ng.time_min * 60 + ng.time_sec) - timeToSeconds(tg.startTime)) < 30
    );
    
    if (!matching) {
      warnings.push({
        type: 'extra_goal',
        message: `Tracked goal not in NORAD: ${tg.players?.[0]?.num} at ${tg.startTime} P${tg.period}`,
        severity: 'warning',
        trackedEvent: tg
      });
    }
  });
  
  return warnings;
}

function showValidationWarnings(warnings) {
  if (warnings.length === 0) {
    toast('✅ Goals match NORAD records', 'success');
    return;
  }
  
  // Show warning panel
  const panel = document.getElementById('validationPanel');
  panel.innerHTML = `
    <h4>⚠️ Validation Warnings (${warnings.length})</h4>
    ${warnings.map(w => `
      <div class="warning-item ${w.severity}">
        <span class="type">${w.type}</span>
        <span class="message">${w.message}</span>
      </div>
    `).join('')}
  `;
  panel.style.display = 'block';
}
```

---

## Batch Edit Mode

### What It Is

Batch edit allows selecting multiple events and changing a field on all of them at once.

### Use Cases

1. **Wrong team** - Accidentally tracked 10 events as home instead of away
2. **Wrong period** - Started tracking before changing period
3. **Add highlight** - Flag multiple events as highlights
4. **Fix zone** - Change zone on multiple events

### Implementation

```javascript
let batchSelectedEvents = [];

function toggleBatchSelect(eventIdx) {
  const idx = batchSelectedEvents.indexOf(eventIdx);
  if (idx >= 0) {
    batchSelectedEvents.splice(idx, 1);
  } else {
    batchSelectedEvents.push(eventIdx);
  }
  renderEventList();
}

function selectAllVisible() {
  // Select all events currently visible in list
  const visible = STATE.events.slice(-20);
  batchSelectedEvents = visible.map(e => STATE.events.indexOf(e));
  renderEventList();
}

function batchEdit(field, value) {
  batchSelectedEvents.forEach(idx => {
    STATE.events[idx][field] = value;
  });
  
  batchSelectedEvents = [];
  renderEventList();
  autoSave();
  toast(`Updated ${batchSelectedEvents.length} events`, 'success');
}

// UI
function showBatchEditModal() {
  const modal = document.getElementById('batchEditModal');
  modal.innerHTML = `
    <h3>Batch Edit ${batchSelectedEvents.length} Events</h3>
    <div class="form-group">
      <label>Field to Change</label>
      <select id="batchField">
        <option value="team">Team</option>
        <option value="period">Period</option>
        <option value="zone">Zone</option>
        <option value="highlight">Highlight</option>
        <option value="type">Event Type</option>
      </select>
    </div>
    <div class="form-group">
      <label>New Value</label>
      <select id="batchValue"></select>
    </div>
    <button onclick="applyBatchEdit()">Apply to All</button>
  `;
  modal.style.display = 'block';
}
```

---

## Electron Wrapper Plan

### Project Structure

```
benchsight-tracker/
├── package.json
├── main.js           # Electron main process
├── preload.js        # Context bridge
├── src/
│   ├── index.html    # Main window
│   ├── renderer.js   # React app entry
│   ├── components/
│   │   ├── App.jsx
│   │   ├── Header.jsx
│   │   ├── ShiftPanel.jsx
│   │   ├── RinkCanvas.jsx
│   │   ├── VideoPlayer.jsx
│   │   ├── EventEntry.jsx
│   │   └── EventList.jsx
│   ├── hooks/
│   │   ├── useSupabase.js
│   │   ├── useLocalStorage.js
│   │   └── useHotkeys.js
│   ├── store/
│   │   └── gameStore.js  # Zustand
│   └── utils/
│       ├── timeUtils.js
│       ├── xyUtils.js
│       └── exportUtils.js
├── assets/
│   └── icons/
└── dist/             # Build output
```

### package.json

```json
{
  "name": "benchsight-tracker",
  "version": "1.0.0",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder",
    "build:mac": "electron-builder --mac",
    "build:win": "electron-builder --win"
  },
  "dependencies": {
    "@supabase/supabase-js": "^2.x",
    "better-sqlite3": "^9.x",
    "react": "^18.x",
    "react-dom": "^18.x",
    "zustand": "^4.x",
    "xlsx": "^0.18.x"
  },
  "devDependencies": {
    "electron": "^28.x",
    "electron-builder": "^24.x",
    "vite": "^5.x"
  },
  "build": {
    "appId": "com.benchsight.tracker",
    "productName": "BenchSight Tracker",
    "mac": {
      "category": "public.app-category.sports"
    },
    "win": {
      "target": "nsis"
    }
  }
}
```

### main.js (Electron Main Process)

```javascript
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const Database = require('better-sqlite3');

let mainWindow;
let db;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.loadFile('src/index.html');
}

app.whenReady().then(() => {
  // Initialize local SQLite
  db = new Database(path.join(app.getPath('userData'), 'benchsight.db'));
  initDatabase();
  
  createWindow();
});

function initDatabase() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS events (
      id INTEGER PRIMARY KEY,
      game_id INTEGER,
      data TEXT,
      created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS shifts (
      id INTEGER PRIMARY KEY,
      game_id INTEGER,
      data TEXT,
      created_at TEXT
    );
  `);
}

// IPC handlers for renderer
ipcMain.handle('db:save-event', (event, gameId, eventData) => {
  const stmt = db.prepare('INSERT INTO events (game_id, data, created_at) VALUES (?, ?, ?)');
  return stmt.run(gameId, JSON.stringify(eventData), new Date().toISOString());
});

ipcMain.handle('db:get-events', (event, gameId) => {
  const stmt = db.prepare('SELECT * FROM events WHERE game_id = ?');
  return stmt.all(gameId).map(row => ({ ...row, data: JSON.parse(row.data) }));
});
```

---

## Implementation Checklist

### Immediate (This Session)
- [x] MVP HTML tracker
- [x] Basic event entry
- [x] Basic shift tracking
- [x] localStorage auto-save
- [x] Excel export
- [x] Supabase setup guide

### Next Session
- [ ] Supabase integration (games, rosters)
- [ ] Cascading dropdowns from dim tables
- [ ] Enhanced XY visualization
- [ ] Video player (YouTube)
- [ ] Resizable panels
- [ ] NORAD validation

### Future
- [ ] Electron wrapper
- [ ] Local SQLite
- [ ] Batch edit mode
- [ ] Local video files
- [ ] Hotkey editor
- [ ] ML suggestions improvement

---

## Known Issues & TODOs

### Bugs
1. XY dots don't show player numbers correctly
2. Net popup doesn't save to last event
3. Period change doesn't update shift times

### Missing Features
1. Multi-select for batch edit
2. Copy/paste events
3. Event search/filter
4. Undo history (only 1 level currently)
5. Export to JSON backup

### Performance
1. Large event lists (500+) slow down rendering
   - Solution: Virtual scrolling
2. SVG markers accumulate
   - Solution: Clear and re-render, not append

---

## Contact

If continuing this work, the user (Ronnie) can provide:
- Supabase credentials
- Sample tracking data
- YouTube video links
- NORAD game IDs for validation

Check `/mnt/transcripts/` for conversation history if needed.
