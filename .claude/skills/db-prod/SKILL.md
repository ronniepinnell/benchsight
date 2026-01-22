---
name: db-prod
description: Work with the production Supabase database. Use CAREFULLY for production deployments, migrations, and data verification. Requires explicit confirmation.
allowed-tools: Bash, Read
---

# Production Database

Work with the BenchSight production Supabase instance.

## ⚠️ PRODUCTION WARNING

This is the PRODUCTION database. All changes affect live users.
Double-check all operations before executing.

## Connection Details

**Prod Supabase:**
- URL: https://uuaowslhpgyiudmbvqze.supabase.co
- Dashboard: https://supabase.com/dashboard/project/uuaowslhpgyiudmbvqze

## Pre-Production Checklist

Before ANY production operation:

1. ✅ Changes tested in dev first
2. ✅ ETL validation passes
3. ✅ Dashboard build succeeds
4. ✅ Backup exists (if data modification)
5. ✅ Rollback plan ready

## Switch to Production

```bash
./benchsight.sh env switch production
```

Verify:
```bash
./benchsight.sh env status
```

## Production Operations

**Upload to production (CAREFUL):**
```bash
./benchsight.sh db upload
```

**Run migration (CAREFUL):**
```bash
npx supabase migration up --project-id uuaowslhpgyiudmbvqze
```

## RLS Policies

Production MUST have proper RLS policies:

```sql
-- Example: Public read access
CREATE POLICY "public_read" ON dim_players
  FOR SELECT USING (true);

-- Example: Authenticated write
CREATE POLICY "auth_write" ON dim_players
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');
```

## Backup Before Changes

```bash
# Export critical tables
pg_dump --data-only --table=fact_player_game > backup.sql
```

## Rollback Plan

1. Keep previous migration file
2. Write rollback SQL
3. Test rollback in dev first
4. Execute if needed:
```bash
npx supabase migration repair --status reverted
```

## NEVER Do These in Production

- ❌ DROP TABLE without backup
- ❌ TRUNCATE without backup
- ❌ DELETE without WHERE clause
- ❌ Schema changes without testing
- ❌ Direct data edits without logging
