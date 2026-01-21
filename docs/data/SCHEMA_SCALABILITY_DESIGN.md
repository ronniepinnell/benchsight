# BenchSight Schema Scalability Design

**Multi-tenant schema design, scalability patterns, and migration strategy**

Last Updated: 2026-01-15  
Version: 1.0

---

## Overview

This document outlines the schema design for scaling BenchSight from a single-tenant prototype to a multi-tenant commercial SaaS platform supporting 100+ teams.

---

## Current Schema Analysis

### Single-Tenant Design

**Current State:**
- All data in single Supabase database
- No tenant isolation
- All tables accessible to all users
- No row-level security (RLS)

**Table Count:** 132-139 tables  
**Primary Tables:**
- `dim_player` - 337 rows
- `dim_team` - 26 rows
- `dim_schedule` - 567 rows
- `fact_events` - ~5,800 rows (per 4 games)
- `fact_shifts` - ~400 rows (per 4 games)
- `fact_player_game_stats` - ~1,400 rows (per 4 games)

**Key Relationships:**
- `fact_events.game_id` → `dim_schedule.game_id`
- `fact_events.event_player_1` → `dim_player.player_id`
- `fact_shifts.player_id` → `dim_player.player_id`
- `fact_shifts.game_id` → `dim_schedule.game_id`

**Index Strategy:**
- Primary keys on all tables
- Foreign key indexes
- No composite indexes for tenant filtering (not needed yet)

**Partition Considerations:**
- No partitioning currently
- All data in single schema

---

## Multi-Tenant Schema Design

### Tenant Isolation Strategy

**Approach: Shared Database, Tenant ID Column**

**Rationale:**
- Simpler than schema-per-tenant
- Easier to manage and scale
- Better resource utilization
- Easier cross-tenant analytics (if needed)

**Implementation:**
- Add `tenant_id` column to all tables
- Use Row-Level Security (RLS) for isolation
- Index on `tenant_id` for performance
- Foreign keys include `tenant_id`

### Schema Changes

#### 1. Add Tenant Table

```sql
CREATE TABLE dim_tenant (
    tenant_id VARCHAR(50) PRIMARY KEY,
    tenant_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    subscription_tier VARCHAR(50), -- free, team, pro, enterprise
    subscription_status VARCHAR(50), -- active, cancelled, trial
    max_teams INTEGER DEFAULT 1,
    max_games_per_season INTEGER DEFAULT 20,
    features JSONB -- Feature flags
);

CREATE INDEX idx_tenant_subscription ON dim_tenant(subscription_tier, subscription_status);
```

#### 2. Add tenant_id to All Tables

**Dimension Tables:**
```sql
-- Example: dim_player
ALTER TABLE dim_player 
ADD COLUMN tenant_id VARCHAR(50) NOT NULL DEFAULT 'default';

ALTER TABLE dim_player 
ADD CONSTRAINT fk_player_tenant 
FOREIGN KEY (tenant_id) REFERENCES dim_tenant(tenant_id);

CREATE INDEX idx_player_tenant ON dim_player(tenant_id);

-- Update primary key to include tenant_id
ALTER TABLE dim_player 
DROP CONSTRAINT dim_player_pkey;

ALTER TABLE dim_player 
ADD PRIMARY KEY (tenant_id, player_id);
```

**Fact Tables:**
```sql
-- Example: fact_events
ALTER TABLE fact_events 
ADD COLUMN tenant_id VARCHAR(50) NOT NULL DEFAULT 'default';

ALTER TABLE fact_events 
ADD CONSTRAINT fk_events_tenant 
FOREIGN KEY (tenant_id) REFERENCES dim_tenant(tenant_id);

CREATE INDEX idx_events_tenant_game ON fact_events(tenant_id, game_id);
CREATE INDEX idx_events_tenant_player ON fact_events(tenant_id, event_player_1);

-- Update primary key
ALTER TABLE fact_events 
DROP CONSTRAINT fact_events_pkey;

ALTER TABLE fact_events 
ADD PRIMARY KEY (tenant_id, event_id);
```

**Pattern for All Tables:**
1. Add `tenant_id VARCHAR(50) NOT NULL`
2. Add foreign key to `dim_tenant`
3. Add index on `tenant_id` (or composite with common filters)
4. Update primary key to include `tenant_id`

#### 3. Update Foreign Keys

**Before:**
```sql
FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
```

**After:**
```sql
FOREIGN KEY (tenant_id, game_id) REFERENCES dim_schedule(tenant_id, game_id)
```

**All foreign keys must include `tenant_id` to maintain referential integrity.**

### Row-Level Security (RLS) Design

#### RLS Policies

**Enable RLS on all tables:**
```sql
ALTER TABLE dim_player ENABLE ROW LEVEL SECURITY;
ALTER TABLE dim_team ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_events ENABLE ROW LEVEL SECURITY;
-- ... for all tables
```

**Create RLS Policies:**

**For SELECT (Read):**
```sql
-- Example: dim_player
CREATE POLICY tenant_isolation_select ON dim_player
    FOR SELECT
    USING (
        tenant_id = current_setting('app.current_tenant_id')::VARCHAR(50)
    );
```

**For INSERT (Create):**
```sql
CREATE POLICY tenant_isolation_insert ON dim_player
    FOR INSERT
    WITH CHECK (
        tenant_id = current_setting('app.current_tenant_id')::VARCHAR(50)
    );
```

**For UPDATE:**
```sql
CREATE POLICY tenant_isolation_update ON dim_player
    FOR UPDATE
    USING (
        tenant_id = current_setting('app.current_tenant_id')::VARCHAR(50)
    )
    WITH CHECK (
        tenant_id = current_setting('app.current_tenant_id')::VARCHAR(50)
    );
```

**For DELETE:**
```sql
CREATE POLICY tenant_isolation_delete ON dim_player
    FOR DELETE
    USING (
        tenant_id = current_setting('app.current_tenant_id')::VARCHAR(50)
    );
```

**Setting Tenant Context:**
```sql
-- In application code (Supabase client)
SET app.current_tenant_id = 'tenant_123';
```

**Or via Supabase Auth:**
```sql
-- Use JWT claim for tenant_id
CREATE POLICY tenant_isolation_select ON dim_player
    FOR SELECT
    USING (
        tenant_id = (auth.jwt() ->> 'tenant_id')::VARCHAR(50)
    );
```

### Index Optimization for Multi-Tenant

#### Composite Indexes

**Common Query Patterns:**
```sql
-- Query by tenant and game
SELECT * FROM fact_events 
WHERE tenant_id = ? AND game_id = ?;

-- Index:
CREATE INDEX idx_events_tenant_game ON fact_events(tenant_id, game_id);

-- Query by tenant and player
SELECT * FROM fact_player_game_stats 
WHERE tenant_id = ? AND player_id = ?;

-- Index:
CREATE INDEX idx_player_stats_tenant_player ON fact_player_game_stats(tenant_id, player_id);

-- Query by tenant and season
SELECT * FROM fact_player_season_stats 
WHERE tenant_id = ? AND season_id = ?;

-- Index:
CREATE INDEX idx_season_stats_tenant_season ON fact_player_season_stats(tenant_id, season_id);
```

**Index Strategy:**
1. Always include `tenant_id` as first column in composite indexes
2. Add indexes for common query patterns
3. Monitor query performance and add indexes as needed
4. Use partial indexes for tenant-specific data if beneficial

---

## Scalability Patterns

### Horizontal Scaling Strategies

#### Read Replicas

**Setup:**
- Configure Supabase read replicas
- Route read queries to replicas
- Route write queries to primary

**Implementation:**
```python
# Primary connection (writes)
primary_db = create_supabase_client(primary_url)

# Replica connection (reads)
replica_db = create_supabase_client(replica_url)

# Query routing
def query_db(query, is_write=False):
    if is_write:
        return primary_db.execute(query)
    else:
        return replica_db.execute(query)
```

**Benefits:**
- Distribute read load
- Improve query performance
- Scale reads independently

**Considerations:**
- Replica lag (eventual consistency)
- Connection management
- Failover procedures

#### Database Sharding (Future)

**If needed for 1000+ tenants:**
- Shard by tenant_id hash
- Each shard handles subset of tenants
- Application routes queries to correct shard

**Not needed for MVP or initial scale (100+ teams).**

### Vertical Scaling Limits

**Current Supabase Limits:**
- Free tier: 500 MB database, 2 GB bandwidth
- Pro tier: 8 GB database, 50 GB bandwidth
- Team tier: 32 GB database, 200 GB bandwidth

**Scaling Path:**
1. Start with Pro tier
2. Upgrade to Team tier at ~50 teams
3. Consider Enterprise tier at 100+ teams
4. Evaluate dedicated instance at 200+ teams

### Caching Strategies

#### Redis Caching

**Cache Layers:**

1. **Query Result Caching:**
```python
# Cache player stats queries
cache_key = f"player_stats:{tenant_id}:{player_id}:{season_id}"
cached_result = redis.get(cache_key)
if cached_result:
    return cached_result

result = db.query(...)
redis.setex(cache_key, 3600, result)  # 1 hour TTL
return result
```

2. **Dimension Table Caching:**
```python
# Cache dimension tables (rarely change)
cache_key = f"dim_player:{tenant_id}"
dim_players = redis.get(cache_key)
if not dim_players:
    dim_players = db.query("SELECT * FROM dim_player WHERE tenant_id = ?", tenant_id)
    redis.setex(cache_key, 86400, dim_players)  # 24 hour TTL
```

3. **Aggregate Statistics Caching:**
```python
# Cache league leaders (update after each game)
cache_key = f"league_leaders:{tenant_id}:{season_id}"
leaders = redis.get(cache_key)
# Invalidate on game completion
```

**Cache Invalidation:**
- Invalidate on data updates
- Use TTL for time-based invalidation
- Use cache tags for related data invalidation

#### Application-Level Caching

**Next.js Caching:**
- Static page generation (ISR)
- API route caching
- React Query caching

### Connection Pooling

**PgBouncer Configuration:**
```ini
[databases]
benchsight = host=db.example.com port=5432 dbname=benchsight

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

**Benefits:**
- Reduce connection overhead
- Improve connection reuse
- Handle connection spikes

---

## Migration Plan

### Step 1: Preparation (Week 33)

**Tasks:**
1. Create `dim_tenant` table
2. Create migration scripts
3. Test migration on dev environment
4. Backup production data

**Scripts:**
```sql
-- 1. Create tenant table
CREATE TABLE dim_tenant (...);

-- 2. Create default tenant
INSERT INTO dim_tenant (tenant_id, tenant_name, subscription_tier)
VALUES ('default', 'Default Tenant', 'free');

-- 3. Test adding tenant_id to one table
ALTER TABLE dim_player ADD COLUMN tenant_id VARCHAR(50);
UPDATE dim_player SET tenant_id = 'default';
ALTER TABLE dim_player ALTER COLUMN tenant_id SET NOT NULL;
```

### Step 2: Add tenant_id Columns (Week 33-34)

**Approach:**
- Add columns in batches (10-20 tables at a time)
- Test after each batch
- Monitor performance

**Script:**
```sql
-- Batch 1: Dimension tables
ALTER TABLE dim_player ADD COLUMN tenant_id VARCHAR(50) NOT NULL DEFAULT 'default';
ALTER TABLE dim_team ADD COLUMN tenant_id VARCHAR(50) NOT NULL DEFAULT 'default';
-- ... etc

-- Batch 2: Core fact tables
ALTER TABLE fact_events ADD COLUMN tenant_id VARCHAR(50) NOT NULL DEFAULT 'default';
ALTER TABLE fact_shifts ADD COLUMN tenant_id VARCHAR(50) NOT NULL DEFAULT 'default';
-- ... etc

-- Batch 3: Derived fact tables
-- ... etc
```

### Step 3: Update Foreign Keys (Week 34)

**Script:**
```sql
-- Drop old foreign keys
ALTER TABLE fact_events DROP CONSTRAINT fk_events_game;

-- Add new foreign keys with tenant_id
ALTER TABLE fact_events 
ADD CONSTRAINT fk_events_game_tenant 
FOREIGN KEY (tenant_id, game_id) 
REFERENCES dim_schedule(tenant_id, game_id);
```

### Step 4: Update Primary Keys (Week 34)

**Script:**
```sql
-- Drop old primary keys
ALTER TABLE dim_player DROP CONSTRAINT dim_player_pkey;

-- Add new composite primary keys
ALTER TABLE dim_player 
ADD PRIMARY KEY (tenant_id, player_id);
```

### Step 5: Add Indexes (Week 34)

**Script:**
```sql
-- Add tenant_id indexes
CREATE INDEX idx_player_tenant ON dim_player(tenant_id);
CREATE INDEX idx_events_tenant_game ON fact_events(tenant_id, game_id);
-- ... etc for all tables
```

### Step 6: Enable RLS (Week 35)

**Script:**
```sql
-- Enable RLS on all tables
ALTER TABLE dim_player ENABLE ROW LEVEL SECURITY;
-- ... etc

-- Create RLS policies
CREATE POLICY tenant_isolation_select ON dim_player
    FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant_id')::VARCHAR(50));
-- ... etc for all tables and operations
```

### Step 7: Update Application Code (Week 35-36)

**ETL Updates:**
```python
# Add tenant_id parameter
def run_etl(tenant_id: str, game_ids: List[int]):
    # All queries include tenant_id
    events = db.query(
        "SELECT * FROM fact_events WHERE tenant_id = ? AND game_id IN ?",
        tenant_id, game_ids
    )
```

**API Updates:**
```python
# Extract tenant_id from JWT or request
def get_tenant_id(request):
    return request.user.tenant_id

# All queries include tenant_id
@app.get("/api/players")
def get_players(tenant_id: str = Depends(get_tenant_id)):
    return db.query("SELECT * FROM dim_player WHERE tenant_id = ?", tenant_id)
```

**Dashboard Updates:**
```typescript
// Add tenant_id to all queries
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('*')
  .eq('tenant_id', currentTenantId)
  .eq('player_id', playerId);
```

### Step 8: Data Migration (Week 36)

**Script:**
```sql
-- Assign all existing data to default tenant
UPDATE dim_player SET tenant_id = 'default' WHERE tenant_id IS NULL;
UPDATE fact_events SET tenant_id = 'default' WHERE tenant_id IS NULL;
-- ... etc for all tables
```

### Step 9: Verification (Week 36)

**Tasks:**
1. Verify all data has tenant_id
2. Verify foreign keys work
3. Verify RLS policies work
4. Test multi-tenant queries
5. Performance testing

**Verification Script:**
```sql
-- Check for NULL tenant_id
SELECT COUNT(*) FROM dim_player WHERE tenant_id IS NULL;
-- Should return 0

-- Test RLS
SET app.current_tenant_id = 'tenant_123';
SELECT * FROM dim_player; -- Should only return tenant_123 data
```

### Step 10: Rollback Procedures

**If migration fails:**
1. Restore from backup
2. Revert schema changes
3. Investigate issues
4. Retry migration

**Rollback Script:**
```sql
-- Remove tenant_id columns (if needed)
ALTER TABLE dim_player DROP COLUMN tenant_id;
-- ... etc

-- Restore old primary keys
ALTER TABLE dim_player ADD PRIMARY KEY (player_id);
-- ... etc
```

---

## Performance Considerations

### Query Performance

**Before (Single-Tenant):**
```sql
SELECT * FROM fact_player_game_stats WHERE player_id = 'P001';
-- Index: player_id
```

**After (Multi-Tenant):**
```sql
SELECT * FROM fact_player_game_stats 
WHERE tenant_id = 'tenant_123' AND player_id = 'P001';
-- Index: (tenant_id, player_id)
```

**Performance Impact:**
- Minimal if indexes are correct
- Tenant_id filter reduces result set significantly
- Composite indexes maintain performance

### Index Maintenance

**Monitor:**
- Query execution times
- Index usage statistics
- Table sizes
- Index bloat

**Optimize:**
- Add indexes for slow queries
- Remove unused indexes
- Rebuild indexes periodically
- Use partial indexes where beneficial

### Connection Management

**Connection Pooling:**
- Use PgBouncer for connection pooling
- Configure appropriate pool sizes
- Monitor connection usage
- Scale pools as needed

---

## Security Considerations

### Data Isolation

**RLS Policies:**
- Enforce tenant isolation at database level
- Prevent cross-tenant data access
- Audit policy violations

**Application-Level:**
- Validate tenant_id in all requests
- Never trust client-provided tenant_id
- Use JWT claims for tenant_id

### Access Control

**Role-Based Access:**
- Admin: Full access to tenant data
- Coach: Access to team data
- Player: Access to own data
- Viewer: Read-only access

**RLS Policies by Role:**
```sql
-- Admin can access all tenant data
CREATE POLICY admin_access ON dim_player
    FOR ALL
    USING (
        auth.jwt() ->> 'role' = 'admin' AND
        tenant_id = (auth.jwt() ->> 'tenant_id')::VARCHAR(50)
    );

-- Coach can access team data
CREATE POLICY coach_access ON dim_player
    FOR SELECT
    USING (
        auth.jwt() ->> 'role' = 'coach' AND
        tenant_id = (auth.jwt() ->> 'tenant_id')::VARCHAR(50) AND
        team_id IN (SELECT team_id FROM coach_teams WHERE coach_id = auth.uid())
    );
```

---

## Related Documentation

- [MASTER_IMPLEMENTATION_PLAN.md](../MASTER_IMPLEMENTATION_PLAN.md) - Implementation phases
- [DATA_DICTIONARY.md](DATA_DICTIONARY.md) - Complete table documentation
- [TECH_STACK_ROADMAP.md](../TECH_STACK_ROADMAP.md) - Technology requirements

---

*Last Updated: 2026-01-15*
