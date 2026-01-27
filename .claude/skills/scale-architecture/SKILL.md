---
name: scale-architecture
description: Plan architecture for scaling BenchSight to support multiple leagues, high traffic, and enterprise features. Use when planning infrastructure and multi-tenancy.
allowed-tools: Read, Write, WebSearch
argument-hint: [multi-tenancy|infrastructure|performance|security]
---

# Scale Architecture

Plan BenchSight's architecture for scale.

## Current Architecture

```
[Tracker] → [ETL] → [Supabase] → [Dashboard]
                         ↑
                      [API]
```

**Limitations:**
- Single tenant
- Manual ETL
- No real-time
- Limited caching

## Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CDN (Vercel Edge)                       │
├─────────────────────────────────────────────────────────────┤
│  Dashboard (Next.js)  │  Tracker (Next.js)  │  Portal        │
├─────────────────────────────────────────────────────────────┤
│                    API Gateway (FastAPI)                     │
│           Rate Limiting │ Auth │ Routing │ Caching          │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   ETL        │   ML/CV      │   Real-time  │   Background   │
│   Workers    │   Pipeline   │   WebSocket  │   Jobs         │
├──────────────┴──────────────┴──────────────┴────────────────┤
│                    Message Queue (Redis)                     │
├─────────────────────────────────────────────────────────────┤
│   Supabase (Primary)  │  Redis (Cache)  │  S3 (Files)       │
└─────────────────────────────────────────────────────────────┘
```

## Multi-Tenancy

### Data Isolation
```sql
-- Every table has league_id
ALTER TABLE fact_player_game ADD COLUMN league_id UUID;

-- RLS policies
CREATE POLICY tenant_isolation ON fact_player_game
  USING (league_id = current_setting('app.current_league')::uuid);
```

### Configuration
```python
# Per-league configuration
LEAGUE_CONFIG = {
    "norad": {
        "periods": 3,
        "period_length": 12,
        "overtime": True,
    },
    "custom_league": {
        "periods": 2,
        "period_length": 25,
        "overtime": False,
    }
}
```

## Performance Scaling

### Caching Strategy

**Layer 1: Edge (Vercel)**
- Static pages: 1 hour
- API responses: 5 minutes

**Layer 2: Application (Redis)**
- Query results: 1-5 minutes
- Session data: 24 hours

**Layer 3: Database**
- Materialized views
- Pre-aggregated tables
- Proper indexing

### Database Scaling

**Read Replicas:**
- Dashboard queries → replica
- API reads → replica
- Writes → primary

**Partitioning:**
```sql
-- Partition by season
CREATE TABLE fact_events (
    ...
) PARTITION BY RANGE (season_id);
```

## Security

### Authentication
- Supabase Auth (current)
- OAuth providers (Google, GitHub)
- API keys for integrations
- JWT tokens

### Authorization
- Row Level Security (RLS)
- Role-based access control
- API rate limiting
- Audit logging

## Infrastructure

### Development
- Local Docker setup
- Supabase local
- Hot reload

### Staging
- Vercel preview
- Supabase dev project
- Automated testing

### Production
- Vercel production
- Supabase production
- Redis cluster
- Monitoring (Datadog)

## Output

Architecture plans go to:
```
docs/architecture/scale-architecture.md
```
