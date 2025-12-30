# BenchSight - Supabase Write-Back Strategy

## Overview

This document explains how the Tracker and Dashboard applications will read from and write to Supabase. Understanding this architecture is critical for all developers.

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW DIAGRAM                                  │
└─────────────────────────────────────────────────────────────────────────────┘

     TRACKER                    SUPABASE                    DASHBOARD
    ┌────────┐                 ┌────────┐                  ┌────────┐
    │  Game  │ ──WRITE──────► │ fact_  │ ◄──READ───────── │ Stats  │
    │Tracking│                 │ events │                  │ Views  │
    └────────┘                 └────────┘                  └────────┘
         │                          │                           │
         │                          ▼                           │
         │                    ┌──────────┐                      │
         │                    │   ETL    │                      │
         │                    │ Pipeline │                      │
         │                    └──────────┘                      │
         │                          │                           │
         │                          ▼                           │
         │                    ┌──────────┐                      │
         └─────READ─────────► │  fact_   │ ◄──READ──────────────┘
                              │  player_ │
                              │  game_   │
                              │  stats   │
                              └──────────┘

     ┌────────┐                                              ┌────────┐
     │ PORTAL │ ──ADMIN OPS──────────────────────────────── │ PORTAL │
     │  (Run  │   (Run ETL, View Logs, Manage Tables)       │ (View  │
     │  ETL)  │                                              │ Stats) │
     └────────┘                                              └────────┘
```

---

## Write Operations by Component

### 1. TRACKER → Supabase (Real-Time Writes)

The Tracker writes event data directly to Supabase during game tracking.

#### What Tracker Writes:
| Table | When | How |
|-------|------|-----|
| `fact_events` | Each event recorded | Direct INSERT |
| `fact_shifts` | Shift changes | Direct INSERT |
| `fact_events_player` | With each event | Direct INSERT |

#### Tracker Write Pattern:
```javascript
// Tracker writes an event
async function saveEvent(event) {
  // 1. Generate event key
  const eventKey = `E${event.game_id}${String(event.event_index).padStart(5, '0')}`;
  
  // 2. Insert event
  const { data, error } = await supabase
    .from('fact_events')
    .insert({
      event_key: eventKey,
      game_id: event.game_id,
      event_index: event.event_index,
      period: event.period,
      event_type: event.event_type,
      event_detail: event.event_detail,
      event_detail_2: event.event_detail_2,
      event_successful: event.event_successful,
      event_start_seconds: event.event_start_seconds,
      event_team_player_1: event.primaryPlayer,
      opp_team_player_1: event.opponentPlayer,
      shift_key: event.shift_key,
      // ... other columns
    });
    
  if (error) {
    // Handle error - maybe queue for retry
    await queueForRetry(event);
    throw error;
  }
  
  // 3. Insert player-event records
  for (const player of event.playersOnIce) {
    await supabase
      .from('fact_events_player')
      .insert({
        event_player_key: `EP${event.game_id}${String(event.event_index).padStart(5, '0')}`,
        event_key: eventKey,
        player_id: player.player_id,
        player_role: player.role,
        // ...
      });
  }
  
  return data;
}
```

#### Tracker Considerations:
- **Offline mode:** Queue writes locally, sync when online
- **Conflict handling:** Use event_index as sequence, don't allow duplicates
- **Validation:** Validate event_type against allowed values before write
- **FK validation:** Ensure player_id exists in dim_player

---

### 2. DASHBOARD → Supabase (Read Only + Admin Writes)

Dashboard is primarily READ-ONLY but may need some write capabilities.

#### Dashboard Reads:
```javascript
// Get league standings
const { data: standings } = await supabase
  .from('dim_schedule')
  .select('*')
  .order('game_date', { ascending: false });

// Get player stats
const { data: playerStats } = await supabase
  .from('fact_player_game_stats')
  .select(`
    *,
    dim_player(player_name, position),
    dim_schedule(game_date, home_team, away_team)
  `)
  .eq('player_id', playerId);

// Get team comparison
const { data: teamStats } = await supabase
  .from('fact_team_game_stats')
  .select('*')
  .eq('game_id', gameId);
```

#### Dashboard Writes (Limited):
| Table | What | When |
|-------|------|------|
| `user_preferences` | User settings | User saves preferences |
| `saved_views` | Saved filters/views | User saves custom view |
| `annotations` | User notes on stats | User adds comment |

**Note:** Dashboard should NOT write to fact tables directly.

---

### 3. PORTAL → Supabase (Full Admin Access)

Portal has full admin capabilities to manage the database.

#### Portal Operations:
| Operation | Method | Tables Affected |
|-----------|--------|-----------------|
| Run ETL | Execute Python scripts | All fact tables |
| Upload CSV | Bulk INSERT | Any table |
| Clear & Reload | TRUNCATE + INSERT | Specified table |
| View Logs | SELECT from logs | etl_logs |
| Validate Data | SELECT with checks | All tables |

#### Portal Write Pattern:
```javascript
// Portal: Full table reload
async function reloadTable(tableName, csvData) {
  // 1. Backup existing data
  await supabase.rpc('backup_table', { table_name: tableName });
  
  // 2. Clear table
  await supabase.from(tableName).delete().neq('id', null);
  
  // 3. Insert new data
  const { error } = await supabase.from(tableName).insert(csvData);
  
  if (error) {
    // Rollback from backup
    await supabase.rpc('restore_table', { table_name: tableName });
    throw error;
  }
  
  // 4. Log operation
  await supabase.from('etl_logs').insert({
    operation: 'reload',
    table_name: tableName,
    rows_affected: csvData.length,
    timestamp: new Date().toISOString()
  });
}
```

---

## Supabase Configuration Requirements

### Tables Needed for Write-Back

#### Core Tables (Already Defined)
- All dimension tables (dim_*)
- All fact tables (fact_*)

#### New Tables for Application Support

```sql
-- ETL operation logs
CREATE TABLE etl_logs (
  id SERIAL PRIMARY KEY,
  operation VARCHAR(50),
  table_name VARCHAR(100),
  rows_affected INTEGER,
  status VARCHAR(20),
  error_message TEXT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- User preferences (for Dashboard)
CREATE TABLE user_preferences (
  user_id VARCHAR(100) PRIMARY KEY,
  preferences JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Saved views (for Dashboard)
CREATE TABLE saved_views (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(100),
  view_name VARCHAR(100),
  view_config JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Event queue (for Tracker offline mode)
CREATE TABLE event_queue (
  id SERIAL PRIMARY KEY,
  game_id INTEGER,
  event_data JSONB,
  status VARCHAR(20) DEFAULT 'pending',
  attempts INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP
);
```

### Row Level Security (RLS)

```sql
-- Enable RLS on tables
ALTER TABLE fact_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_player_game_stats ENABLE ROW LEVEL SECURITY;

-- Policy: Public read access
CREATE POLICY "Public read access" ON fact_events
  FOR SELECT USING (true);

-- Policy: Only authenticated can write events
CREATE POLICY "Authenticated insert" ON fact_events
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Policy: Only admin can update/delete
CREATE POLICY "Admin only modify" ON fact_events
  FOR UPDATE USING (auth.role() = 'service_role');
```

---

## API Keys & Access Levels

| Component | Key Type | Permissions |
|-----------|----------|-------------|
| Dashboard | `anon` key | SELECT on all tables |
| Tracker | `anon` key + auth | SELECT, INSERT on events |
| Portal | `service_role` key | Full admin access |

**CRITICAL:** Never expose `service_role` key in client-side code!

---

## Write-Back Workflow

### Real-Time Game Tracking
```
1. Tracker records event
2. Tracker writes to fact_events (Supabase)
3. Tracker writes to fact_events_player (Supabase)
4. Dashboard can query immediately
5. After game: Portal runs ETL for aggregations
6. Dashboard shows updated player_game_stats
```

### Batch Updates (After Game)
```
1. Portal triggers ETL
2. ETL reads fact_events
3. ETL calculates aggregations
4. ETL writes fact_player_game_stats, fact_team_game_stats
5. Dashboard refreshes to show new stats
```

---

## Error Handling Strategy

### Tracker Errors
```javascript
// Retry logic for tracker
async function saveWithRetry(event, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await saveEvent(event);
    } catch (error) {
      if (i === maxRetries - 1) {
        // Queue locally for later sync
        await saveToLocalQueue(event);
        throw error;
      }
      await sleep(1000 * Math.pow(2, i)); // Exponential backoff
    }
  }
}
```

### Dashboard Errors
```javascript
// Graceful degradation
async function fetchStats(playerId) {
  try {
    return await supabase.from('fact_player_game_stats')
      .select('*').eq('player_id', playerId);
  } catch (error) {
    // Show cached data or friendly error
    return getCachedStats(playerId) || { error: 'Stats temporarily unavailable' };
  }
}
```

### Portal Errors
```javascript
// Full logging for admin operations
async function runETL() {
  const logId = await createLog('etl_start');
  try {
    // Run ETL steps
    await updateLog(logId, 'success');
  } catch (error) {
    await updateLog(logId, 'failed', error.message);
    // Show error in portal UI
    throw error;
  }
}
```

---

## Design Considerations for Developers

### For Tracker Developer
1. **Assume offline:** Build queue-based writes
2. **Validate locally:** Check event types before sending
3. **Handle conflicts:** event_index must be unique
4. **Show sync status:** User should know if data is synced

### For Dashboard Developer
1. **Cache aggressively:** Stats don't change mid-game
2. **Paginate results:** Don't load all events at once
3. **Show loading states:** Queries may take time
4. **Handle stale data:** Show "last updated" timestamps

### For Portal Developer
1. **Log everything:** All operations should be auditable
2. **Confirm destructive ops:** Require confirmation for deletes
3. **Show progress:** ETL can take minutes
4. **Provide rollback:** Keep backups before major operations

---

## Summary Table

| Component | Reads From | Writes To | Access Level |
|-----------|-----------|-----------|--------------|
| **Tracker** | dim_player, dim_team, dim_schedule | fact_events, fact_shifts, event_queue | Auth user |
| **Dashboard** | All tables | user_preferences, saved_views | Anon read |
| **Portal** | All tables + etl_logs | All tables + etl_logs | Service role |
| **ETL** | fact_events, fact_shifts | fact_*_stats, fact_h2h, fact_wowy | Service role |

---

*This document should be read by Tracker, Dashboard, and Portal developers before implementation.*
