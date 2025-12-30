# BenchSight Data Loading & Integration Strategy

## Executive Summary

This document outlines the strategy for implementing flexible data loading capabilities for BenchSight's Supabase database. The loading system will support various granularities (full, partial, by game, by table type) and operations (replace, append, upsert) - eventually exposed through the Admin Portal.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         BENCHSIGHT DATA ECOSYSTEM                                │
└─────────────────────────────────────────────────────────────────────────────────┘

     DATA SOURCES                    SUPABASE                      CONSUMERS
     ────────────                    ────────                      ─────────

┌──────────────┐                ┌─────────────────┐
│  CSV Files   │───────────────►│  DIMENSION      │
│  (ETL Output)│   BULK LOAD    │  TABLES         │◄───────────────┐
└──────────────┘                │  dim_player     │                │
                                │  dim_team       │                │
┌──────────────┐                │  dim_schedule   │                │
│   TRACKER    │                └────────┬────────┘           ┌────┴────────┐
│  (Live Entry)│                         │                    │  DASHBOARD  │
└──────┬───────┘                         │ FKs                │  (Read-only)│
       │                                 ▼                    └─────────────┘
       │              ┌──────────────────────────────────┐
       │              │         STAGING TABLES           │
       ├─────────────►│  staging_events                  │
       │              │  staging_shifts                  │
       │              │  etl_queue                       │
       │              └──────────────┬───────────────────┘
       │                             │
       │                             │ ETL Process
       │                             ▼
       │              ┌──────────────────────────────────┐
       │              │          FACT TABLES             │
       │              │  fact_events                     │◄───────────────┐
       │              │  fact_events_player              │                │
       │              │  fact_shifts                     │                │
       │              │  fact_shifts_player              │           ┌────┴────────┐
       │              │  fact_player_game_stats (317col) │           │   PORTAL    │
       │              │  fact_team_game_stats            │           │  (Admin UI) │
       │              │  fact_goalie_game_stats          │           └─────────────┘
       │              │  fact_h2h                        │
       └─────────────►│  fact_wowy                       │  ◄── Direct writes possible
                      └──────────────────────────────────┘
```

---

## 📊 Flexible Loading Operations Matrix

### By Table Type

| Operation | Dimensions | Core Facts | Stats Facts | Analytics Facts |
|-----------|------------|------------|-------------|-----------------|
| **Tables** | dim_player, dim_team, dim_schedule | fact_events, fact_shifts | fact_player_game_stats, fact_team_game_stats, fact_goalie_game_stats | fact_h2h, fact_wowy |
| **Load Order** | 1st (no deps) | 2nd (dims required) | 3rd (core facts used) | 4th (everything used) |
| **Typical Op** | UPSERT | UPSERT by game | REPLACE by game | REPLACE by game |
| **Frequency** | Rarely | Per game | Per ETL run | Per ETL run |

### By Scope

| Scope | Description | Use Case |
|-------|-------------|----------|
| **Full Refresh** | Drop all, reload everything | Schema changes, fresh start |
| **All Games** | Reload all game data, keep dims | Data corrections across league |
| **Single Game** | Load/reload one game's data | New game tracked, corrections |
| **Single Table** | Load/reload one table | Testing, targeted fixes |
| **Append Only** | Add new rows, keep existing | New games, no corrections |

### By Operation Type

| Operation | SQL Behavior | When to Use |
|-----------|--------------|-------------|
| **REPLACE** | TRUNCATE + INSERT | Full refresh, start fresh |
| **APPEND** | INSERT (fail on dupe PK) | Adding new data only |
| **UPSERT** | INSERT ON CONFLICT UPDATE | Updates + additions |
| **MERGE** | Complex: update some, insert others | Selective updates |

---

## 🔧 Implementation: Supabase Functions

### Core Loading Functions

```sql
-- ================================================
-- FUNCTION: Load single table with operation choice
-- ================================================
CREATE OR REPLACE FUNCTION load_table(
    p_table_name TEXT,
    p_operation TEXT DEFAULT 'upsert',  -- 'replace', 'append', 'upsert'
    p_game_id INTEGER DEFAULT NULL       -- NULL = all games
)
RETURNS JSON AS $$
DECLARE
    v_rows_affected INTEGER;
    v_start_time TIMESTAMP := NOW();
BEGIN
    -- Validate table name
    IF p_table_name NOT IN (
        'dim_player', 'dim_team', 'dim_schedule',
        'fact_events', 'fact_events_player', 'fact_shifts', 'fact_shifts_player',
        'fact_player_game_stats', 'fact_team_game_stats', 'fact_goalie_game_stats',
        'fact_h2h', 'fact_wowy'
    ) THEN
        RETURN json_build_object('success', false, 'error', 'Invalid table name');
    END IF;
    
    -- Handle REPLACE operation
    IF p_operation = 'replace' THEN
        IF p_game_id IS NOT NULL THEN
            EXECUTE format('DELETE FROM %I WHERE game_id = $1', p_table_name) USING p_game_id;
        ELSE
            EXECUTE format('TRUNCATE TABLE %I CASCADE', p_table_name);
        END IF;
    END IF;
    
    -- Log the operation
    INSERT INTO load_history (table_name, operation, game_id, started_at)
    VALUES (p_table_name, p_operation, p_game_id, v_start_time);
    
    RETURN json_build_object(
        'success', true,
        'table', p_table_name,
        'operation', p_operation,
        'game_id', p_game_id,
        'duration_ms', EXTRACT(EPOCH FROM (NOW() - v_start_time)) * 1000
    );
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- FUNCTION: Load by table category
-- ================================================
CREATE OR REPLACE FUNCTION load_category(
    p_category TEXT,  -- 'dims', 'core_facts', 'stats_facts', 'analytics_facts', 'all'
    p_operation TEXT DEFAULT 'upsert',
    p_game_id INTEGER DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
    v_tables TEXT[];
    v_table TEXT;
    v_results JSON[] := '{}';
BEGIN
    -- Define table categories
    CASE p_category
        WHEN 'dims' THEN
            v_tables := ARRAY['dim_player', 'dim_team', 'dim_schedule'];
        WHEN 'core_facts' THEN
            v_tables := ARRAY['fact_shifts', 'fact_events', 'fact_events_player', 'fact_shifts_player'];
        WHEN 'stats_facts' THEN
            v_tables := ARRAY['fact_player_game_stats', 'fact_team_game_stats', 'fact_goalie_game_stats'];
        WHEN 'analytics_facts' THEN
            v_tables := ARRAY['fact_h2h', 'fact_wowy'];
        WHEN 'all_facts' THEN
            v_tables := ARRAY['fact_shifts', 'fact_events', 'fact_events_player', 'fact_shifts_player',
                              'fact_player_game_stats', 'fact_team_game_stats', 'fact_goalie_game_stats',
                              'fact_h2h', 'fact_wowy'];
        WHEN 'all' THEN
            v_tables := ARRAY['dim_player', 'dim_team', 'dim_schedule',
                              'fact_shifts', 'fact_events', 'fact_events_player', 'fact_shifts_player',
                              'fact_player_game_stats', 'fact_team_game_stats', 'fact_goalie_game_stats',
                              'fact_h2h', 'fact_wowy'];
        ELSE
            RETURN json_build_object('success', false, 'error', 'Invalid category');
    END CASE;
    
    -- Process each table
    FOREACH v_table IN ARRAY v_tables LOOP
        v_results := v_results || load_table(v_table, p_operation, p_game_id);
    END LOOP;
    
    RETURN json_build_object(
        'success', true,
        'category', p_category,
        'tables_processed', array_length(v_tables, 1),
        'results', v_results
    );
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- FUNCTION: Delete game data across all tables
-- ================================================
CREATE OR REPLACE FUNCTION delete_game(p_game_id INTEGER)
RETURNS JSON AS $$
DECLARE
    v_tables TEXT[] := ARRAY[
        'fact_wowy', 'fact_h2h',
        'fact_goalie_game_stats', 'fact_team_game_stats', 'fact_player_game_stats',
        'fact_shifts_player', 'fact_events_player',
        'fact_events', 'fact_shifts'
    ];
    v_table TEXT;
    v_total_deleted INTEGER := 0;
    v_rows INTEGER;
BEGIN
    -- Delete in reverse dependency order
    FOREACH v_table IN ARRAY v_tables LOOP
        EXECUTE format('DELETE FROM %I WHERE game_id = $1', v_table) USING p_game_id;
        GET DIAGNOSTICS v_rows = ROW_COUNT;
        v_total_deleted := v_total_deleted + v_rows;
    END LOOP;
    
    RETURN json_build_object(
        'success', true,
        'game_id', p_game_id,
        'total_rows_deleted', v_total_deleted
    );
END;
$$ LANGUAGE plpgsql;
```

### Tracking & History Tables

```sql
-- ================================================
-- TABLE: Load operation history
-- ================================================
CREATE TABLE IF NOT EXISTS load_history (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    game_id INTEGER,
    rows_affected INTEGER,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'started',
    error_message TEXT,
    initiated_by VARCHAR(50) DEFAULT 'api'
);

CREATE INDEX idx_load_history_table ON load_history(table_name);
CREATE INDEX idx_load_history_status ON load_history(status);

-- ================================================
-- TABLE: ETL queue for async processing
-- ================================================
CREATE TABLE IF NOT EXISTS etl_queue (
    id SERIAL PRIMARY KEY,
    game_id INTEGER,
    operation VARCHAR(50) NOT NULL,
    tables TEXT[],
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    requested_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    requested_by VARCHAR(50)
);

CREATE INDEX idx_etl_queue_status ON etl_queue(status);
CREATE INDEX idx_etl_queue_priority ON etl_queue(priority DESC, requested_at);
```

---

## 🖥️ Portal API Endpoints

The Admin Portal will expose these loading capabilities through a REST API:

### Endpoint Design

```yaml
# Data Loading Endpoints
POST /api/load/table
  body: { table: "fact_events", operation: "upsert", game_id: 18969 }
  
POST /api/load/category
  body: { category: "dims", operation: "replace" }
  
POST /api/load/game
  body: { game_id: 18969, operation: "replace" }
  
POST /api/load/full-refresh
  body: { confirm: true }

DELETE /api/data/game/{game_id}

# ETL Queue Endpoints  
POST /api/etl/queue
  body: { game_id: 18969, priority: 10 }
  
GET /api/etl/queue
  response: [{ id, game_id, status, requested_at }]

POST /api/etl/run
  body: { queue_id: 123 }

# Upload Endpoints
POST /api/upload/csv
  multipart: { file, table, operation }
  
POST /api/upload/bulk
  multipart: { files[], operation }

# Status Endpoints
GET /api/load/history
GET /api/tables/counts
GET /api/health
```

### Portal UI Components

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ADMIN PORTAL - DATA MANAGEMENT                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │  QUICK ACTIONS                                                              ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    ││
│  │  │ Full Refresh │  │ Load All CSV │  │ Run ETL      │  │ Validate All │    ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │  LOAD BY SCOPE                                                              ││
│  │                                                                             ││
│  │  Scope:    [▼ Single Game    ]    Game: [▼ 18969 - Puck Hogs vs Blades ]  ││
│  │                                                                             ││
│  │  Tables:   [✓] All  [ ] Dims Only  [ ] Facts Only  [ ] Custom...          ││
│  │                                                                             ││
│  │  Operation: (•) Replace Game  ( ) Append  ( ) Upsert                       ││
│  │                                                                             ││
│  │  [  Execute Load  ]                                                        ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │  UPLOAD CSV FILES                                                           ││
│  │                                                                             ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐   ││
│  │  │  Drop CSV files here or click to browse                             │   ││
│  │  │                                                                     │   ││
│  │  │  📄 fact_player_game_stats.csv (ready)                              │   ││
│  │  │  📄 fact_events.csv (ready)                                         │   ││
│  │  └─────────────────────────────────────────────────────────────────────┘   ││
│  │                                                                             ││
│  │  Target:  [▼ Auto-detect from filename ]     Operation: [▼ Upsert ]        ││
│  │                                                                             ││
│  │  [  Upload & Process  ]                                                    ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │  RECENT OPERATIONS                                            [ View All ] ││
│  │  ──────────────────────────────────────────────────────────────────────────││
│  │  ✓ 12:45 PM  Load fact_events (game 18969)      Replace    2,341 rows      ││
│  │  ✓ 12:44 PM  Load dim_player                    Upsert       337 rows      ││
│  │  ✗ 12:30 PM  Load fact_h2h (game 18977)         Replace    FK Error        ││
│  │  ✓ 11:00 AM  Full ETL Run                       Complete   24,654 rows     ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Integration with Other Systems

### Tracker → Supabase

```javascript
// Tracker writes to staging tables
async function saveTrackerEvent(event) {
    const { data, error } = await supabase
        .from('staging_events')  // Staging, not fact_events directly
        .upsert({
            event_key: generateEventKey(event),
            game_id: event.game_id,
            ...event,
            processed: false,  // ETL will set to true
            created_at: new Date().toISOString()
        });
    
    // Queue ETL if this completes a game
    if (event.event_type === 'GameEnd') {
        await supabase.from('etl_queue').insert({
            game_id: event.game_id,
            operation: 'process_game',
            priority: 10  // High priority for game end
        });
    }
}
```

### Dashboard → Supabase

```javascript
// Dashboard reads from fact tables (read-only)
async function getLeaderboard() {
    const { data } = await supabase
        .from('fact_player_game_stats')
        .select('player_id, player_name, goals, assists, points')
        .order('points', { ascending: false })
        .limit(20);
    return data;
}

// Real-time subscription for live games
const subscription = supabase
    .channel('live-events')
    .on('postgres_changes', 
        { event: 'INSERT', schema: 'public', table: 'fact_events', filter: 'game_id=eq.18969' },
        (payload) => updateLiveEventFeed(payload.new)
    )
    .subscribe();
```

### Portal → ETL Orchestration

```python
# Portal backend triggers ETL
from fastapi import FastAPI, BackgroundTasks
import subprocess

app = FastAPI()

@app.post("/api/etl/run")
async def run_etl(game_id: int = None, background_tasks: BackgroundTasks):
    """Queue ETL run as background task"""
    background_tasks.add_task(execute_etl_pipeline, game_id)
    return {"status": "queued", "game_id": game_id}

async def execute_etl_pipeline(game_id: int = None):
    """Execute full ETL pipeline"""
    commands = [
        ["python", "etl.py"] + (["--game-id", str(game_id)] if game_id else []),
        ["python", "scripts/fix_data_integrity.py"],
        ["python", "scripts/fix_final_data.py"],
        ["python", "scripts/etl_validation.py"]
    ]
    
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Log error, update queue status
            break
```

---

## 📅 Implementation Roadmap

### Phase 1: Foundation (Week 1) - CURRENT
**Focus:** Get data into Supabase with basic loading

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Create tables in Supabase | All 12 tables created |
| 2 | Load dimension tables | dims loaded, validated |
| 3 | Load fact tables | facts loaded, validated |
| 4 | Add indexes and FKs | Performance optimized |
| 5 | Create staging tables | Tracker write targets ready |

**Exit Criteria:**
- [ ] All 12 production tables + 3 staging tables created
- [ ] All CSV data loaded
- [ ] load_history table tracking operations
- [ ] Basic validation queries pass

### Phase 2: Flexible Loading (Week 2)
**Focus:** Build loading functions and API

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Create Supabase functions | load_table, load_category, delete_game |
| 2 | Build Python loader script | CLI tool with all options |
| 3 | Create Portal API endpoints | /api/load/* routes |
| 4 | Build upload handlers | CSV upload processing |
| 5 | Add operation history | Audit trail complete |

**Exit Criteria:**
- [ ] Can load any scope (game, table, category) via API
- [ ] Can choose operation (replace, append, upsert)
- [ ] Upload CSV files via API
- [ ] Full history of all operations

### Phase 3: Portal UI (Week 3)
**Focus:** Build admin interface for loading

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Quick actions panel | One-click operations |
| 2 | Scope selector UI | Game/table/category picker |
| 3 | CSV upload UI | Drag-drop upload |
| 4 | History viewer | Operation log display |
| 5 | Status dashboard | Real-time feedback |

**Exit Criteria:**
- [ ] Non-technical users can load data
- [ ] Visual feedback on operations
- [ ] Error handling and recovery

### Phase 4: Integration (Week 4)
**Focus:** Connect all systems

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Tracker → Staging writes | Live event capture |
| 2 | ETL queue processing | Async game processing |
| 3 | Dashboard real-time | Live subscriptions |
| 4 | End-to-end testing | Full flow verified |
| 5 | Documentation | All handoffs updated |

**Exit Criteria:**
- [ ] Track game → ETL → Dashboard flow works
- [ ] All 4 roles can work independently
- [ ] No manual SQL required for operations

---

## 🎯 Quick Reference: Loading Scenarios

| Scenario | Command / Action |
|----------|------------------|
| Fresh start (new season) | `load_category('all', 'replace')` |
| Add new game | Upload CSVs, `load_category('all_facts', 'append', game_id)` |
| Fix game data | `delete_game(game_id)`, re-upload, `load_category('all_facts', 'append', game_id)` |
| Update player master | Upload dim_player.csv, `load_table('dim_player', 'upsert')` |
| Just reload stats | `load_category('stats_facts', 'replace', game_id)` |
| Test single table | `load_table('fact_h2h', 'replace', game_id)` |
| Emergency rollback | Restore from backup, `load_category('all', 'replace')` |

---

## 📁 Files to Create

```
supabase_deployment/
├── sql/
│   ├── 06_create_staging_tables.sql    # NEW: Staging + queue tables
│   ├── 07_create_loading_functions.sql  # NEW: PL/pgSQL functions
│   └── 08_create_history_tables.sql     # NEW: Audit logging
├── scripts/
│   ├── flexible_loader.py               # NEW: Python CLI loader
│   └── upload_handler.py                # NEW: CSV upload processing
├── api/
│   └── load_endpoints.py                # NEW: FastAPI routes
└── LOADING_STRATEGY.md                  # THIS DOCUMENT
```

---

## ❓ Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| All 317 columns | Keep all | Future-proof, can create views to simplify |
| FK enforcement | After load (flexible) | Allows partial loads, easier debugging |
| RLS | Not now | Add later when auth implemented |
| Staging tables | Yes | Cleaner tracker writes, ETL control |
| Load history | Yes | Audit trail, debugging, monitoring |

---

*Document Version: 1.0 | Created: December 2024*
