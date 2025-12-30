# BenchSight - Supabase Write-Back Strategy

## Overview

This document describes how the **Tracker** and **Dashboard** applications will write data back to Supabase, and the architectural considerations for real-time data flow.

---

## Architecture Options

### Option A: Direct Write (Recommended for MVP)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   TRACKER    │────►│   SUPABASE   │◄────│  DASHBOARD   │
│  (writes)    │     │  (database)  │     │  (reads)     │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   ETL/PORTAL │
                     │  (batch ops) │
                     └──────────────┘
```

**Pros:** Simple, real-time, no middleware
**Cons:** Logic duplicated between tracker and ETL

### Option B: API Gateway (Recommended for Production)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   TRACKER    │────►│  API GATEWAY │◄────│  DASHBOARD   │
└──────────────┘     │  (FastAPI)   │     └──────────────┘
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │   SUPABASE   │
                     └──────────────┘
```

**Pros:** Centralized validation, consistent logic, easier to maintain
**Cons:** Additional service to build/host

---

## Tracker → Supabase Writes

### What Tracker Writes

| Table | When | Data |
|-------|------|------|
| `fact_events` | On event save | Single event row |
| `fact_shifts` | On shift change | Shift with players |
| `dim_schedule` | On game create | New game record |

### Write Strategy

#### 1. Real-Time Event Insertion

```javascript
// Tracker writes event immediately when saved
async function saveEvent(event) {
  const eventKey = `E${event.gameId}${String(event.eventIndex).padStart(5, '0')}`;
  
  const { data, error } = await supabase
    .from('fact_events')
    .upsert({
      event_key: eventKey,
      game_id: event.gameId,
      event_index: event.eventIndex,
      period: event.period,
      event_type: event.eventType,
      event_detail: event.eventDetail,
      event_detail_2: event.eventDetail2,
      event_successful: event.successful,
      event_start_seconds: event.startSeconds,
      event_team_player_1: event.player1,
      opp_team_player_1: event.oppPlayer1,
      // ... other fields
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }, {
      onConflict: 'event_key'  // Update if exists
    });
  
  if (error) {
    // Queue for retry, save to localStorage
    queueForRetry(event);
    throw error;
  }
  
  return data;
}
```

#### 2. Batch Shift Updates

```javascript
// Update shift when players change
async function updateShift(shift) {
  const shiftKey = `S${shift.gameId}${String(shift.shiftIndex).padStart(5, '0')}`;
  
  const { error } = await supabase
    .from('fact_shifts')
    .upsert({
      shift_key: shiftKey,
      game_id: shift.gameId,
      shift_index: shift.shiftIndex,
      period: shift.period,
      shift_start_seconds: shift.startSeconds,
      shift_end_seconds: shift.endSeconds,
      home_1: shift.homePlayers[0],
      home_2: shift.homePlayers[1],
      // ... all players
      updated_at: new Date().toISOString(),
    });
  
  return !error;
}
```

#### 3. Offline Queue & Sync

```javascript
// For tracking without internet
const offlineQueue = {
  events: [],
  shifts: [],
  
  add(type, data) {
    this[type].push({ data, timestamp: Date.now() });
    localStorage.setItem('offlineQueue', JSON.stringify(this));
  },
  
  async sync() {
    const queued = JSON.parse(localStorage.getItem('offlineQueue') || '{}');
    
    for (const event of queued.events || []) {
      try {
        await saveEvent(event.data);
        this.remove('events', event);
      } catch (e) {
        console.error('Sync failed for event', event);
      }
    }
    
    // Similar for shifts
  }
};
```

### Validation Before Write

```javascript
// Validate event before sending to Supabase
function validateEvent(event) {
  const errors = [];
  
  // Required fields
  if (!event.eventType) errors.push('event_type required');
  if (!event.period) errors.push('period required');
  if (!event.gameId) errors.push('game_id required');
  
  // Business rules
  if (event.eventType === 'Faceoff') {
    if (!event.player1) errors.push('Faceoff needs event_team_player_1');
    if (!event.oppPlayer1) errors.push('Faceoff needs opp_team_player_1');
  }
  
  if (event.eventType === 'Shot' && !event.eventDetail) {
    errors.push('Shot needs event_detail');
  }
  
  // Range checks
  if (event.period < 1 || event.period > 4) {
    errors.push('Period must be 1-4');
  }
  
  return { valid: errors.length === 0, errors };
}
```

---

## Dashboard → Supabase Writes

### What Dashboard Might Write

| Table | When | Data |
|-------|------|------|
| `user_preferences` | User settings | Dashboard config |
| `saved_reports` | User saves report | Report definition |
| `annotations` | User adds note | Game/player notes |

**Note:** Dashboard primarily READS. Writes are limited to user-specific data.

### Write Strategy

```javascript
// Example: Save user's favorite players
async function saveFavoritePlayers(userId, playerIds) {
  const { error } = await supabase
    .from('user_preferences')
    .upsert({
      user_id: userId,
      preference_key: 'favorite_players',
      preference_value: JSON.stringify(playerIds),
      updated_at: new Date().toISOString(),
    });
  
  return !error;
}

// Example: Save custom report
async function saveReport(userId, report) {
  const { data, error } = await supabase
    .from('saved_reports')
    .insert({
      user_id: userId,
      report_name: report.name,
      report_config: JSON.stringify(report.config),
      created_at: new Date().toISOString(),
    });
  
  return { success: !error, reportId: data?.[0]?.id };
}
```

---

## Real-Time Subscriptions

### Dashboard Subscribes to Changes

```javascript
// Dashboard can listen for new events
const subscription = supabase
  .channel('game-events')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'fact_events',
      filter: `game_id=eq.${currentGameId}`
    },
    (payload) => {
      console.log('New event:', payload.new);
      updateEventList(payload.new);
    }
  )
  .subscribe();

// Unsubscribe when leaving page
subscription.unsubscribe();
```

### Enable Real-Time in Supabase

```sql
-- Run in Supabase SQL editor
ALTER PUBLICATION supabase_realtime ADD TABLE fact_events;
ALTER PUBLICATION supabase_realtime ADD TABLE fact_shifts;
```

---

## Aggregation Strategy

### Problem: Stats Are Aggregated

The `fact_player_game_stats` table contains aggregated data (sum of goals, assists, etc.). When tracker writes individual events, these aggregations need updating.

### Solution Options

#### Option 1: ETL Recalculation (Current)
```
Tracker writes events → Admin runs ETL → Stats recalculated
```
- **Pros:** Simple, consistent with existing flow
- **Cons:** Not real-time, requires manual trigger

#### Option 2: Supabase Functions (Recommended)

```sql
-- Create function to update player stats on event insert
CREATE OR REPLACE FUNCTION update_player_stats()
RETURNS TRIGGER AS $$
BEGIN
  -- Update goals count
  IF NEW.event_type = 'Goal' THEN
    UPDATE fact_player_game_stats
    SET goals = goals + 1,
        points = points + 1,
        updated_at = NOW()
    WHERE game_id = NEW.game_id 
      AND player_id = NEW.event_team_player_1_id;
  END IF;
  
  -- Update shots count
  IF NEW.event_type = 'Shot' THEN
    UPDATE fact_player_game_stats
    SET shots = shots + 1,
        updated_at = NOW()
    WHERE game_id = NEW.game_id 
      AND player_id = NEW.event_team_player_1_id;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
CREATE TRIGGER on_event_insert
AFTER INSERT ON fact_events
FOR EACH ROW
EXECUTE FUNCTION update_player_stats();
```

#### Option 3: Application-Level Updates

```javascript
// After saving event, update stats too
async function saveEventWithStats(event) {
  // 1. Save event
  await saveEvent(event);
  
  // 2. Update player stats
  if (event.eventType === 'Goal') {
    await supabase.rpc('increment_player_stat', {
      p_game_id: event.gameId,
      p_player_id: event.player1Id,
      p_stat: 'goals',
      p_amount: 1
    });
  }
}
```

---

## Data Integrity Considerations

### Preventing Duplicates

```javascript
// Use upsert with conflict handling
const { error } = await supabase
  .from('fact_events')
  .upsert(eventData, {
    onConflict: 'event_key',
    ignoreDuplicates: false  // Update if exists
  });
```

### Foreign Key Validation

```javascript
// Verify player exists before inserting event
async function validatePlayer(playerId) {
  const { data } = await supabase
    .from('dim_player')
    .select('player_id')
    .eq('player_id', playerId)
    .single();
  
  return data !== null;
}
```

### Optimistic Updates with Rollback

```javascript
async function saveEventOptimistic(event) {
  // 1. Update UI immediately
  addEventToUI(event);
  
  try {
    // 2. Save to Supabase
    await saveEvent(event);
  } catch (error) {
    // 3. Rollback UI on failure
    removeEventFromUI(event.eventKey);
    showError('Failed to save event');
  }
}
```

---

## Recommended Implementation Order

### Phase 1: Read-Only Dashboard
1. Dashboard reads from Supabase
2. No writes except user preferences
3. ETL handles all data updates

### Phase 2: Tracker Direct Writes
1. Tracker writes events directly to Supabase
2. Basic validation in tracker
3. ETL still runs for aggregations

### Phase 3: Real-Time Updates
1. Enable Supabase real-time
2. Dashboard subscribes to changes
3. Implement Supabase functions for aggregations

### Phase 4: Full Integration
1. API gateway for complex operations
2. Consistent validation layer
3. Offline support with sync

---

## Security Considerations

### Row Level Security (RLS)

```sql
-- Anyone can read
CREATE POLICY "Public read access" ON fact_events
  FOR SELECT USING (true);

-- Only authenticated users can write
CREATE POLICY "Authenticated write access" ON fact_events
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Only owner can update/delete
CREATE POLICY "Owner update access" ON fact_events
  FOR UPDATE USING (auth.uid() = created_by);
```

### API Key Management

```javascript
// NEVER expose service_role key in frontend
// Use anon key for client-side

// ❌ WRONG - service_role in frontend
const supabase = createClient(URL, SERVICE_ROLE_KEY);

// ✅ CORRECT - anon key in frontend
const supabase = createClient(URL, ANON_KEY);
```

---

## Summary

| Component | Writes | Reads | Real-Time |
|-----------|--------|-------|-----------|
| **Tracker** | Events, Shifts | Roster, Games | No |
| **Dashboard** | User prefs only | All tables | Yes (subscribe) |
| **Portal** | Via ETL/Upload | All tables | No |
| **ETL** | All tables (batch) | Raw files | No |

---

*Last Updated: December 2024*
