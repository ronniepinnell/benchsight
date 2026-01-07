# Tracker Integration Guide

**For developers building the BenchSight game tracking interface**

---

## Overview

The Tracker is used during live games to record:
- Play-by-play events (shots, goals, faceoffs, etc.)
- Player shifts and line changes
- Penalties and stoppages
- Export data for ETL processing

**Data Source:** ETL API (for uploads/processing) + Supabase (for reference data)  
**Tech Stack:** HTML/JS (offline-capable)  
**Key Operations:** Event recording, file export, ETL upload

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      TRACKER UI                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Event      │  │   Shift     │  │   Export    │     │
│  │  Recording  │  │   Tracking  │  │   Upload    │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
└─────────┼────────────────┼────────────────┼─────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────┐
│                  LOCAL STORAGE                           │
│         (IndexedDB / localStorage for offline)           │
└────────────────────────┬────────────────────────────────┘
                         │ On sync/export
                         ▼
┌─────────────────────────────────────────────────────────┐
│                     ETL API                              │
│    POST /api/upload     POST /api/games/{id}/process    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    SUPABASE                              │
│              (Final data warehouse)                      │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Load Reference Data from Supabase

```javascript
// Load players for roster selection
async function loadRosterData(homeTeamId, awayTeamId) {
  const { data: players } = await supabase
    .from('dim_player')
    .select('player_id, player_full_name, jersey_number, primary_position, team_id')
    .in('team_id', [homeTeamId, awayTeamId])
    .eq('is_active', '1')
    .order('jersey_number')

  return {
    homePlayers: players.filter(p => p.team_id === homeTeamId),
    awayPlayers: players.filter(p => p.team_id === awayTeamId)
  }
}

// Load event types for dropdown
async function loadEventTypes() {
  const { data } = await supabase
    .from('dim_event_type')
    .select('event_type_id, event_type_name, category')
    .order('category')

  return data
}
```

### 2. Event Recording Structure

```javascript
// Event data structure
const event = {
  event_index: 1,              // Sequential number
  game_id: '18969',            // Game identifier
  period: '1',                 // 1, 2, 3, OT
  event_time: '15:30',         // MM:SS (counting down)
  event_type: 'Shot',          // From dim_event_type
  event_detail: 'Wrist Shot',  // Shot type, etc.
  team_id: 'T001',             // Team making play
  players: [
    { player_id: 'P001', role: 'shooter' },
    { player_id: 'P050', role: 'goalie' }
  ],
  zone: 'offensive',           // offensive, defensive, neutral
  x_coord: 75,                 // Rink coordinates
  y_coord: 25,
  success: true,               // For shots: on goal?
  result: 'save'               // save, goal, miss, block
}
```

### 3. Upload to ETL API

```javascript
const ETL_API = 'http://localhost:5000/api'

// Export game data as CSV/Excel and upload
async function exportAndUpload(gameId, events, shifts) {
  // 1. Generate tracking file (CSV or Excel)
  const blob = generateTrackingFile(events, shifts)
  
  // 2. Upload to ETL API
  const formData = new FormData()
  formData.append('file', blob, `${gameId}_tracking.csv`)
  formData.append('game_id', gameId)

  const uploadResponse = await fetch(`${ETL_API}/upload`, {
    method: 'POST',
    body: formData
  })

  if (!uploadResponse.ok) {
    throw new Error('Upload failed')
  }

  // 3. Trigger processing
  const processResponse = await fetch(`${ETL_API}/games/${gameId}/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ force: true })
  })

  return processResponse.json()
}
```

---

## Core Components

### Event Recorder

```jsx
// components/EventRecorder.jsx
import { useState, useCallback } from 'react'

export function EventRecorder({ gameId, period, players, onEventRecorded }) {
  const [eventType, setEventType] = useState('Shot')
  const [selectedPlayer, setSelectedPlayer] = useState(null)
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [eventTime, setEventTime] = useState('20:00')

  const EVENT_TYPES = [
    { type: 'Shot', details: ['Wrist Shot', 'Slap Shot', 'Snap Shot', 'Backhand'] },
    { type: 'Goal', details: ['Wrist Shot', 'Slap Shot', 'Tip-In', 'Deflection'] },
    { type: 'Faceoff', details: ['Won', 'Lost'] },
    { type: 'Hit', details: ['Body Check', 'Board Check'] },
    { type: 'Penalty', details: ['Tripping', 'Hooking', 'Slashing', 'Interference'] },
    { type: 'Turnover', details: ['Giveaway', 'Takeaway'] },
    { type: 'Block', details: ['Shot Block'] }
  ]

  const recordEvent = useCallback(() => {
    const event = {
      game_id: gameId,
      period,
      event_time: eventTime,
      event_type: eventType,
      team_id: selectedTeam,
      player_id: selectedPlayer,
      timestamp: new Date().toISOString()
    }

    onEventRecorded(event)

    // Reset for next event
    setSelectedPlayer(null)
  }, [gameId, period, eventTime, eventType, selectedTeam, selectedPlayer])

  return (
    <div className="event-recorder">
      <div className="time-input">
        <label>Time:</label>
        <input 
          type="text" 
          value={eventTime} 
          onChange={e => setEventTime(e.target.value)}
          pattern="[0-9]{1,2}:[0-9]{2}"
        />
      </div>

      <div className="event-type-selector">
        {EVENT_TYPES.map(et => (
          <button
            key={et.type}
            className={eventType === et.type ? 'active' : ''}
            onClick={() => setEventType(et.type)}
          >
            {et.type}
          </button>
        ))}
      </div>

      <div className="team-selector">
        <button onClick={() => setSelectedTeam('home')}>Home</button>
        <button onClick={() => setSelectedTeam('away')}>Away</button>
      </div>

      <div className="player-grid">
        {players
          .filter(p => p.team === selectedTeam)
          .map(player => (
            <button
              key={player.player_id}
              className={selectedPlayer === player.player_id ? 'selected' : ''}
              onClick={() => setSelectedPlayer(player.player_id)}
            >
              #{player.jersey_number} {player.player_full_name.split(' ')[1]}
            </button>
          ))
        }
      </div>

      <button className="record-btn" onClick={recordEvent} disabled={!selectedPlayer}>
        Record Event
      </button>
    </div>
  )
}
```

### Shift Tracker

```jsx
// components/ShiftTracker.jsx
export function ShiftTracker({ gameId, players, onShiftChange }) {
  const [onIce, setOnIce] = useState({
    home: { forwards: [], defense: [], goalie: null },
    away: { forwards: [], defense: [], goalie: null }
  })
  const [shiftStartTime, setShiftStartTime] = useState('20:00')

  const togglePlayer = (team, playerId, position) => {
    setOnIce(prev => {
      const current = [...prev[team][position]]
      const idx = current.indexOf(playerId)
      
      if (idx >= 0) {
        current.splice(idx, 1)
      } else {
        current.push(playerId)
      }

      return {
        ...prev,
        [team]: { ...prev[team], [position]: current }
      }
    })
  }

  const recordLineChange = (team) => {
    const currentTime = getCurrentGameTime() // Your time tracking logic
    
    // End current shifts
    const endingShifts = [...onIce[team].forwards, ...onIce[team].defense]
      .map(playerId => ({
        game_id: gameId,
        player_id: playerId,
        end_time: currentTime,
        start_time: shiftStartTime
      }))

    onShiftChange(endingShifts)
    setShiftStartTime(currentTime)
  }

  return (
    <div className="shift-tracker">
      <div className="team-panel home">
        <h3>Home - On Ice</h3>
        <PlayerPositionGrid 
          players={players.filter(p => p.team === 'home')}
          onIce={onIce.home}
          onToggle={(id, pos) => togglePlayer('home', id, pos)}
        />
        <button onClick={() => recordLineChange('home')}>Line Change</button>
      </div>

      <div className="team-panel away">
        <h3>Away - On Ice</h3>
        <PlayerPositionGrid 
          players={players.filter(p => p.team === 'away')}
          onIce={onIce.away}
          onToggle={(id, pos) => togglePlayer('away', id, pos)}
        />
        <button onClick={() => recordLineChange('away')}>Line Change</button>
      </div>
    </div>
  )
}
```

### Rink Visualization (Click to Record)

```jsx
// components/RinkInput.jsx
export function RinkInput({ onLocationSelect }) {
  const handleClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = Math.round(((e.clientX - rect.left) / rect.width) * 200 - 100) // -100 to 100
    const y = Math.round(((e.clientY - rect.top) / rect.height) * 85 - 42.5)  // -42.5 to 42.5
    
    const zone = x > 25 ? 'offensive' : x < -25 ? 'defensive' : 'neutral'
    
    onLocationSelect({ x, y, zone })
  }

  return (
    <div className="rink-container" onClick={handleClick}>
      <svg viewBox="-100 -42.5 200 85" className="rink-svg">
        {/* Rink outline */}
        <rect x="-100" y="-42.5" width="200" height="85" rx="28" fill="#fff" stroke="#000"/>
        
        {/* Center line */}
        <line x1="0" y1="-42.5" x2="0" y2="42.5" stroke="red" strokeWidth="1"/>
        
        {/* Blue lines */}
        <line x1="-25" y1="-42.5" x2="-25" y2="42.5" stroke="blue" strokeWidth="1"/>
        <line x1="25" y1="-42.5" x2="25" y2="42.5" stroke="blue" strokeWidth="1"/>
        
        {/* Goal lines */}
        <line x1="-89" y1="-42.5" x2="-89" y2="42.5" stroke="red" strokeWidth="0.5"/>
        <line x1="89" y1="-42.5" x2="89" y2="42.5" stroke="red" strokeWidth="0.5"/>
        
        {/* Faceoff circles */}
        <circle cx="-69" cy="-22" r="15" fill="none" stroke="red"/>
        <circle cx="-69" cy="22" r="15" fill="none" stroke="red"/>
        <circle cx="69" cy="-22" r="15" fill="none" stroke="red"/>
        <circle cx="69" cy="22" r="15" fill="none" stroke="red"/>
        <circle cx="0" cy="0" r="15" fill="none" stroke="blue"/>
        
        {/* Goals */}
        <rect x="-100" y="-3" width="4" height="6" fill="none" stroke="red"/>
        <rect x="96" y="-3" width="4" height="6" fill="none" stroke="red"/>
      </svg>
    </div>
  )
}
```

---

## Offline Support

### Using IndexedDB

```javascript
// lib/offlineStorage.js
const DB_NAME = 'benchsight_tracker'
const DB_VERSION = 1

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)
    
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)
    
    request.onupgradeneeded = (e) => {
      const db = e.target.result
      
      // Events store
      if (!db.objectStoreNames.contains('events')) {
        const eventsStore = db.createObjectStore('events', { keyPath: 'id', autoIncrement: true })
        eventsStore.createIndex('game_id', 'game_id')
        eventsStore.createIndex('synced', 'synced')
      }
      
      // Shifts store
      if (!db.objectStoreNames.contains('shifts')) {
        const shiftsStore = db.createObjectStore('shifts', { keyPath: 'id', autoIncrement: true })
        shiftsStore.createIndex('game_id', 'game_id')
      }
    }
  })
}

// Save event locally
export async function saveEventOffline(event) {
  const db = await openDB()
  const tx = db.transaction('events', 'readwrite')
  const store = tx.objectStore('events')
  
  await store.add({
    ...event,
    synced: false,
    created_at: new Date().toISOString()
  })
}

// Get all events for a game
export async function getGameEvents(gameId) {
  const db = await openDB()
  const tx = db.transaction('events', 'readonly')
  const store = tx.objectStore('events')
  const index = store.index('game_id')
  
  return new Promise((resolve, reject) => {
    const request = index.getAll(gameId)
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

// Sync all unsynced events
export async function syncEvents(gameId) {
  const events = await getGameEvents(gameId)
  const unsynced = events.filter(e => !e.synced)
  
  // Generate CSV and upload
  const csv = eventsToCSV(unsynced)
  const blob = new Blob([csv], { type: 'text/csv' })
  
  const formData = new FormData()
  formData.append('file', blob, `${gameId}_tracking.csv`)
  formData.append('game_id', gameId)
  
  const response = await fetch('http://localhost:5000/api/upload', {
    method: 'POST',
    body: formData
  })
  
  if (response.ok) {
    // Mark as synced
    const db = await openDB()
    const tx = db.transaction('events', 'readwrite')
    const store = tx.objectStore('events')
    
    for (const event of unsynced) {
      await store.put({ ...event, synced: true })
    }
  }
  
  return response.json()
}
```

---

## Export Formats

### CSV Format (Recommended)

```javascript
function eventsToCSV(events) {
  const headers = [
    'event_index', 'game_id', 'period', 'event_time', 
    'event_type', 'event_detail', 'team_id', 'player_id',
    'zone', 'x_coord', 'y_coord', 'success'
  ]
  
  const rows = events.map(e => [
    e.event_index, e.game_id, e.period, e.event_time,
    e.event_type, e.event_detail || '', e.team_id, e.player_id || '',
    e.zone || '', e.x_coord || '', e.y_coord || '', e.success ? '1' : '0'
  ])
  
  return [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
}
```

### Excel Format

```javascript
import * as XLSX from 'xlsx'

function eventsToExcel(events, shifts) {
  const wb = XLSX.utils.book_new()
  
  // Events sheet
  const eventsWs = XLSX.utils.json_to_sheet(events)
  XLSX.utils.book_append_sheet(wb, eventsWs, 'Events')
  
  // Shifts sheet
  const shiftsWs = XLSX.utils.json_to_sheet(shifts)
  XLSX.utils.book_append_sheet(wb, shiftsWs, 'Shifts')
  
  // Generate blob
  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  return new Blob([wbout], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
}
```

---

## ETL API Reference

### Upload File

```javascript
POST /api/upload
Content-Type: multipart/form-data

file: <tracking file>
game_id: "18969"

Response: {
  "success": true,
  "data": {
    "filename": "18969_tracking.csv",
    "path": "/data/raw/uploads/18969_tracking.csv",
    "size": 12345
  }
}
```

### Process Game

```javascript
POST /api/games/18969/process
Content-Type: application/json

{ "force": true }

Response: {
  "success": true,
  "data": {
    "game_id": 18969,
    "processed": true,
    "result": {
      "stages": {...},
      "duration_seconds": 15.2
    }
  }
}
```

### Check Status

```javascript
GET /api/status

Response: {
  "success": true,
  "data": {
    "games": {
      "available": 25,
      "processed": 20,
      "unprocessed": 5
    }
  }
}
```

---

## Event Type Reference

| Event Type | Details | Players Involved |
|------------|---------|------------------|
| Shot | Wrist, Slap, Snap, Backhand | Shooter, Goalie |
| Goal | Shot type + Assists | Scorer, Assist1, Assist2, Goalie |
| Faceoff | Won/Lost | Player1, Player2 |
| Hit | Body, Board | Hitter, Hittee |
| Penalty | Type (Tripping, etc.) | Penalized player |
| Block | Shot Block | Blocker, Shooter |
| Turnover | Giveaway/Takeaway | Player |
| Save | Shot type | Goalie |

---

## Testing

```javascript
// Test ETL API connection
async function testConnection() {
  try {
    const response = await fetch('http://localhost:5000/api/health')
    const data = await response.json()
    console.log('ETL API:', data.data.status)
    return data.success
  } catch (e) {
    console.error('ETL API not available:', e)
    return false
  }
}

// Test upload
async function testUpload() {
  const testData = 'event_index,game_id,period,event_time,event_type\n1,TEST,1,20:00,Shot'
  const blob = new Blob([testData], { type: 'text/csv' })
  
  const formData = new FormData()
  formData.append('file', blob, 'test_tracking.csv')
  formData.append('game_id', 'TEST')
  
  const response = await fetch('http://localhost:5000/api/upload', {
    method: 'POST',
    body: formData
  })
  
  console.log('Upload test:', await response.json())
}
```
