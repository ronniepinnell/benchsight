---
name: db-dev
description: Work with the development Supabase database. Use for schema changes, migrations, testing queries, and data exploration in the safe dev environment.
allowed-tools: Bash, Read, Write
---

# Development Database

Work with the BenchSight development Supabase instance.

## Connection Details

**Dev Supabase:**
- URL: https://amuisqvhhiigxetsfame.supabase.co
- Dashboard: https://supabase.com/dashboard/project/amuisqvhhiigxetsfame

## Quick Commands

**Upload ETL output to dev:**
```bash
./benchsight.sh db upload
```

**Generate TypeScript types:**
```bash
cd ui/dashboard && npx supabase gen types typescript --project-id amuisqvhhiigxetsfame > src/types/database.ts
```

**Run migration:**
```bash
npx supabase migration up --project-id amuisqvhhiigxetsfame
```

## Table Naming

| Prefix | Type | Example |
|--------|------|---------|
| `dim_` | Dimension | dim_players, dim_teams |
| `fact_` | Fact | fact_player_game, fact_goals |
| `qa_` | QA | qa_validation_summary |
| `v_` | View | v_player_stats_summary |

## Schema Changes

1. **Create migration file:**
```bash
npx supabase migration new <name>
```

2. **Write SQL in migration file**

3. **Test locally:**
```bash
npx supabase db reset
```

4. **Apply to dev:**
```bash
npx supabase migration up
```

## RLS Policies

Development database has relaxed RLS for testing.
Production requires proper policies.

## Data Exploration

Use Supabase dashboard SQL editor or:

```sql
-- Example: Check player counts
SELECT COUNT(*) FROM dim_players;

-- Example: Goal totals
SELECT SUM(goals) FROM fact_player_season;
```

## IMPORTANT

- Dev database is for testing only
- Never connect production apps to dev
- Always test migrations in dev first
- Use `/db-prod` for production operations
