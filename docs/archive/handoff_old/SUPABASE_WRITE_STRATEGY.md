# BenchSight Supabase Write-Back Strategy

## Overview

This document describes how the Tracker and Dashboard applications will write data back to Supabase, and how the ETL pipeline fits into the overall data flow.

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BENCHSIGHT DATA FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

                    WRITE PATH                      READ PATH
                    ──────────                      ─────────

┌──────────────┐                               ┌──────────────┐
│   TRACKER    │                               │  DASHBOARD   │
│  (HTML/JS)   │                               │  (React/Vue) │
└──────┬───────┘                               └──────▲───────┘
       │                                              │
       │ WRITES                                       │ READS
       │ (Real-time)                                  │ (Real-time)
       ▼                                              │
┌──────────────────────────────────────────────────────────────┐
│                     SUPABASE PostgreSQL                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │ RAW EVENTS  │  │   SHIFTS    │  │  AGGREGATED STATS   │   │
│  │ (tracker    │  │ (tracker    │  │  (ETL calculated)   │   │
│  │  writes)    │  │  writes)    │  │                     │   │
│  └──────┬──────┘  └──────┬──────┘  └──────────▲──────────┘   │
└─────────┼────────────────┼────────────────────┼──────────────┘
          │                │                    │
          │                │                    │
          ▼                ▼                    │
    ┌─────────────────────────────────────┐    │
    │           ETL PIPELINE              │    │
    │  (Batch processing - scheduled)     │────┘
    │  - Transforms raw → aggregated      │
    │  - Calculates derived stats         │
    │  - Validates data quality           │
    └─────────────────────────────────────┘
```

---

## Two Write Strategies

### Strategy A: Tracker Writes Raw → ETL Aggregates (Recommended)

**How it works:**
1. Tracker writes raw events to `staging_events` table
2. Tracker writes shifts to `staging_shifts` table
3. ETL runs periodically (or on-demand) to:
   - Transform staging → fact tables
   - Calculate aggregated stats
   - Validate data quality
4. Dashboard reads from fact tables

**Pros:**
- Clean separation of concerns
- ETL handles all complex calculations
- Easier to fix/reprocess data
- Dashboard always shows validated stats

**Cons:**
- Stats not immediately visible (wait for ETL)
- Requires ETL orchestration

**Tables for Strategy A:**
```sql
-- Tracker writes to staging tables
staging_events (raw tracker input)
staging_shifts (raw tracker input)

-- ETL reads staging, writes to fact tables
fact_events (transformed)
fact_shifts (transformed)
fact_player_game_stats (calculated)
fact_team_game_stats (calculated)
fact_goalie_game_stats (calculated)
```

---

### Strategy B: Tracker Writes Direct + Real-time Aggregates

**How it works:**
1. Tracker writes directly to fact_events/fact_shifts
2. Supabase triggers/functions calculate aggregates in real-time
3. Dashboard sees updates immediately

**Pros:**
- Real-time stats
- Simpler architecture (no separate ETL)

**Cons:**
- Complex Supabase functions needed
- Harder to validate/fix data
- Database does heavy computation

**Tables for Strategy B:**
```sql
-- Tracker writes directly to fact tables
fact_events
fact_shifts

-- Supabase functions update aggregates on insert
fact_player_game_stats (trigger-updated)
fact_team_game_stats (trigger-updated)
```

---

## Recommended Approach: Hybrid

**Use Strategy A (ETL) for:**
- Player/Team/Goalie game stats (complex calculations)
- H2H and WOWY analysis
- Historical data reprocessing

**Use Strategy B (Direct) for:**
- Raw event viewing in dashboard
- Live game tracking display
- Shift timeline

```
┌──────────────┐
│   TRACKER    │
└──────┬───────┘
       │
       ├──────► staging_events ──► ETL ──► fact_player_game_stats
       │                                   fact_team_game_stats
       │                                   fact_goalie_game_stats
       │
       └──────► fact_events (direct) ◄──── Dashboard reads live
               fact_shifts (direct)
```

---

## Tracker Write Requirements

### What Tracker Must Write

**To staging_events (or fact_events):**
```javascript
{
  // Required
  game_id: 18969,
  event_index: 1001,
  period: 1,
  event_start_seconds: 1080,
  event_type: 'Shot',
  event_team_player_1: 53,  // PRIMARY - gets stat credit
  
  // Strongly recommended
  event_detail: 'Shot_OnNetSaved',
  event_detail_2: 'Shot-Wrist',
  event_successful: 's',
  shift_index: 5,
  
  // Optional but valuable
  linked_event_index: null,
  play_detail1: null,
  event_team_zone: 'ozone',
  opp_team_player_1: null,
  
  // Future (XY)
  puck_x: 145.5,
  puck_y: 38.2,
}
```

**To staging_shifts (or fact_shifts):**
```javascript
{
  game_id: 18969,
  shift_index: 1,
  period: 1,
  shift_start_seconds: 1200,
  shift_end_seconds: 1118,
  shift_duration: 82,
  home_1: 53, home_2: 20, home_3: 12, home_4: 8, home_5: 21,
  away_1: 70, away_2: 75, away_3: 49, away_4: 52, away_5: 22,
  home_goalie: 99,
  away_goalie: 39,
  situation: 'Full Strength',
  strength: '5v5',
}
```

### Primary Key Generation (Client-Side)

Tracker generates PKs before insert:
```javascript
// Event key: E{game_id}{5-digit index}
const eventKey = `E${gameId}${String(eventIndex).padStart(5, '0')}`;
// Example: E1896900001

// Shift key: S{game_id}{5-digit index}
const shiftKey = `S${gameId}${String(shiftIndex).padStart(5, '0')}`;
// Example: S1896900001
```

### Supabase Insert Code (Tracker)

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Insert event
async function saveEvent(event) {
  const eventKey = `E${event.game_id}${String(event.event_index).padStart(5, '0')}`;
  
  const { data, error } = await supabase
    .from('staging_events')  // or 'fact_events' for direct
    .insert({
      event_key: eventKey,
      game_id: event.game_id,
      event_index: event.event_index,
      period: event.period,
      event_start_seconds: event.event_start_seconds,
      event_type: event.event_type,
      event_detail: event.event_detail,
      event_successful: event.event_successful,
      event_team_player_1: event.event_team_player_1,
      opp_team_player_1: event.opp_team_player_1,
      shift_index: event.shift_index,
      // ... other fields
      created_at: new Date().toISOString(),
    });
  
  if (error) {
    console.error('Insert error:', error);
    throw error;
  }
  
  return data;
}

// Update event
async function updateEvent(eventKey, updates) {
  const { data, error } = await supabase
    .from('staging_events')
    .update(updates)
    .eq('event_key', eventKey);
  
  if (error) throw error;
  return data;
}

// Delete event
async function deleteEvent(eventKey) {
  const { data, error } = await supabase
    .from('staging_events')
    .delete()
    .eq('event_key', eventKey);
  
  if (error) throw error;
  return data;
}
```

---

## Dashboard Read Requirements

### What Dashboard Reads

**For League Standings:**
```javascript
const { data } = await supabase
  .from('dim_schedule')
  .select('*')
  .order('game_date', { ascending: false });
```

**For Player Stats:**
```javascript
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('*')
  .order('points', { ascending: false });
```

**For Live Event Feed:**
```javascript
// Subscribe to real-time updates
const subscription = supabase
  .channel('events')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'fact_events' },
    (payload) => {
      console.log('New event:', payload.new);
      updateEventFeed(payload.new);
    }
  )
  .subscribe();
```

### Dashboard Write Requirements

**Dashboard typically only reads.** But may write for:

1. **User preferences** (if implemented)
```javascript
await supabase
  .from('user_preferences')
  .upsert({ user_id, favorite_team, favorite_players });
```

2. **Game notes/comments** (if implemented)
```javascript
await supabase
  .from('game_notes')
  .insert({ game_id, user_id, note_text });
```

---

## ETL Integration

### When ETL Runs

**Option 1: On-Demand (Portal triggers)**
```bash
# Portal admin clicks "Run ETL" button
python etl.py
python scripts/fix_data_integrity.py
python scripts/fix_final_data.py
```

**Option 2: After Game Complete**
```javascript
// Tracker signals game complete
await supabase
  .from('etl_queue')
  .insert({ game_id, status: 'pending', requested_at: new Date() });

// ETL worker picks up and processes
```

**Option 3: Scheduled (Cron)**
```bash
# Every hour, process any pending games
0 * * * * cd /app && python etl.py --pending-only
```

### ETL Input/Output

```
INPUT (from staging tables):
├── staging_events
├── staging_shifts
└── dim_player, dim_team, dim_schedule

OUTPUT (to fact tables):
├── fact_events (transformed)
├── fact_events_player (exploded)
├── fact_shifts (with calculations)
├── fact_shifts_player (exploded)
├── fact_player_game_stats (aggregated)
├── fact_team_game_stats (aggregated)
├── fact_goalie_game_stats (aggregated)
├── fact_h2h (calculated)
└── fact_wowy (calculated)
```

---

## Staging Tables Schema (New)

Add these tables for Tracker writes:

```sql
-- Staging table for tracker event writes
CREATE TABLE staging_events (
    event_key VARCHAR(20) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    event_index INTEGER NOT NULL,
    period INTEGER,
    event_start_seconds INTEGER,
    event_end_seconds INTEGER,
    event_type VARCHAR(50),
    event_detail VARCHAR(100),
    event_detail_2 VARCHAR(100),
    event_successful CHAR(1),
    event_team_player_1 INTEGER,
    event_team_player_2 INTEGER,
    event_team_player_3 INTEGER,
    event_team_player_4 INTEGER,
    event_team_player_5 INTEGER,
    event_team_player_6 INTEGER,
    opp_team_player_1 INTEGER,
    opp_team_player_2 INTEGER,
    opp_team_player_3 INTEGER,
    opp_team_player_4 INTEGER,
    opp_team_player_5 INTEGER,
    opp_team_player_6 INTEGER,
    shift_index INTEGER,
    linked_event_index INTEGER,
    play_detail1 VARCHAR(100),
    play_detail2 VARCHAR(100),
    event_team_zone VARCHAR(20),
    puck_x DECIMAL(6,2),
    puck_y DECIMAL(6,2),
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Staging table for tracker shift writes
CREATE TABLE staging_shifts (
    shift_key VARCHAR(20) PRIMARY KEY,
    game_id INTEGER NOT NULL,
    shift_index INTEGER NOT NULL,
    period INTEGER,
    shift_start_seconds INTEGER,
    shift_end_seconds INTEGER,
    shift_duration INTEGER,
    shift_start_type VARCHAR(50),
    shift_stop_type VARCHAR(100),
    home_1 INTEGER, home_2 INTEGER, home_3 INTEGER,
    home_4 INTEGER, home_5 INTEGER, home_6 INTEGER,
    away_1 INTEGER, away_2 INTEGER, away_3 INTEGER,
    away_4 INTEGER, away_5 INTEGER, away_6 INTEGER,
    home_goalie INTEGER,
    away_goalie INTEGER,
    situation VARCHAR(50),
    strength VARCHAR(10),
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ETL processing queue
CREATE TABLE etl_queue (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
    requested_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Indexes
CREATE INDEX idx_staging_events_game ON staging_events(game_id);
CREATE INDEX idx_staging_events_processed ON staging_events(processed);
CREATE INDEX idx_staging_shifts_game ON staging_shifts(game_id);
CREATE INDEX idx_etl_queue_status ON etl_queue(status);
```

---

## Summary: Who Writes What

| Component | Tables Written | Tables Read |
|-----------|---------------|-------------|
| **Tracker** | staging_events, staging_shifts | dim_player, dim_schedule |
| **ETL** | fact_* tables (all) | staging_*, dim_* |
| **Dashboard** | (none typically) | fact_*, dim_* |
| **Portal** | Can write anywhere (admin) | All tables |

---

## Implementation Order

1. **Supabase Dev:** Create staging tables (see schema above)
2. **Tracker Dev:** Implement write functions with PK generation
3. **Portal Dev:** Build "Run ETL" button that triggers processing
4. **Dashboard Dev:** Connect to fact tables for display
5. **Integration:** Test full flow: Track → ETL → Display

---

*Document Version: 1.0 | Last Updated: December 2024*
