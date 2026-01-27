# Database Migrations Workflow

## Overview

We use **incremental migrations** instead of dropping/recreating tables. This is safer, faster, and works in both dev and production.

## Directory Structure

```
supabase/
├── config.toml           # Supabase project config
└── migrations/           # Numbered migration files
    ├── 00000000000000_baseline.sql
    ├── 20260126123456_add_xg_column.sql
    └── 20260127093000_add_player_metrics.sql

sql/
├── views/
│   └── 99_DEPLOY_ALL_VIEWS.sql   # Views (safe to re-run anytime)
└── reset_supabase.sql            # EMERGENCY ONLY - full reset
```

## Daily Workflow

### When ETL Adds New Columns

```bash
# 1. Run ETL to generate new CSVs
./benchsight.sh etl run

# 2. Generate migration from changes
python scripts/generate_migration.py "add xg metrics"

# 3. Review the generated migration
cat supabase/migrations/20260126*_add_xg_metrics.sql

# 4. Apply to dev
supabase db push
# OR run in Supabase SQL Editor (dev)

# 5. Test in dev
./benchsight.sh db upload

# 6. Apply to prod (same migration file)
# Switch to prod in Supabase SQL Editor and run the migration
```

### When Adding a New Table

```bash
# 1. Create migration manually or via script
python scripts/generate_migration.py "add fact_xg_model table"

# 2. Or write manually:
cat > supabase/migrations/20260126_add_xg_table.sql << 'EOF'
CREATE TABLE IF NOT EXISTS fact_xg_model (
    shot_id TEXT PRIMARY KEY,
    game_id BIGINT,
    player_id TEXT,
    xg_value DOUBLE PRECISION,
    _export_timestamp TEXT
);
EOF

# 3. Apply and test
```

### When Updating Views

Views are safe to re-run anytime (CREATE OR REPLACE):

```bash
# Just run in Supabase SQL Editor:
sql/views/99_DEPLOY_ALL_VIEWS.sql
```

## Migration Best Practices

### DO ✅

```sql
-- Safe: Add column if not exists
ALTER TABLE fact_player_game_stats
ADD COLUMN IF NOT EXISTS xg DOUBLE PRECISION;

-- Safe: Create table if not exists
CREATE TABLE IF NOT EXISTS new_table (...);

-- Safe: Create or replace view
CREATE OR REPLACE VIEW v_my_view AS ...;

-- Safe: Add index
CREATE INDEX IF NOT EXISTS idx_player_game
ON fact_player_game_stats(player_id, game_id);
```

### DON'T ❌

```sql
-- DANGEROUS: Drops all data!
DROP TABLE fact_player_game_stats;

-- DANGEROUS: Loses column data!
ALTER TABLE fact_player_game_stats DROP COLUMN old_column;

-- DANGEROUS: Truncates data!
TRUNCATE TABLE fact_player_game_stats;
```

### If You Must Remove a Column

```sql
-- Step 1: Rename to deprecated (keeps data, stops new writes)
ALTER TABLE my_table RENAME COLUMN old_col TO _deprecated_old_col;

-- Step 2: After confirming no issues (weeks later), actually drop
-- ALTER TABLE my_table DROP COLUMN _deprecated_old_col;
```

## Supabase CLI Commands

```bash
# Login (one time)
supabase login

# Link to project
supabase link --project-ref amuisqvhhiigxetsfame  # dev
supabase link --project-ref uuaowslhpgyiudmbvqze  # prod

# Create new migration
supabase migration new add_new_feature

# Push migrations to linked project
supabase db push

# Pull current schema from remote
supabase db pull

# See migration status
supabase migration list

# Diff local vs remote
supabase db diff
```

## Syncing Dev → Prod

```bash
# 1. All migrations in supabase/migrations/ are source of truth

# 2. Apply to dev first
supabase link --project-ref amuisqvhhiigxetsfame
supabase db push

# 3. Test thoroughly

# 4. Apply same migrations to prod
supabase link --project-ref uuaowslhpgyiudmbvqze
supabase db push

# 5. Upload data to prod
./benchsight.sh env switch production
./benchsight.sh db upload
```

## Emergency: Full Schema Reset

Only use if migrations are corrupted or you need a clean slate:

```bash
# 1. Backup data first!
supabase db dump > backup_$(date +%Y%m%d).sql

# 2. Run full reset (DESTROYS ALL DATA)
# In Supabase SQL Editor:
sql/reset_supabase.sql

# 3. Re-run views
sql/views/99_DEPLOY_ALL_VIEWS.sql

# 4. Re-upload data
./benchsight.sh db upload

# 5. Mark migrations as applied
supabase migration repair --status applied 00000000000000
```

## Troubleshooting

### "Column already exists"

Migration was partially applied. Add `IF NOT EXISTS`:

```sql
ALTER TABLE my_table ADD COLUMN IF NOT EXISTS col_name TYPE;
```

### "Table doesn't exist"

Run migrations in order, or check if baseline was applied.

### "Migration already applied"

```bash
# Check status
supabase migration list

# Force re-apply if needed
supabase migration repair --status reverted MIGRATION_ID
supabase db push
```

### Schema Drift (dev ≠ prod)

```bash
# Compare schemas
supabase db diff --linked  # Compare local to remote

# Or manually compare
supabase db pull --file current_schema.sql
diff current_schema.sql supabase/migrations/...
```

## Migration Naming Convention

```
YYYYMMDDHHMMSS_description.sql

Examples:
- 20260126143000_add_xg_columns.sql
- 20260126150000_create_fact_line_combos.sql
- 20260127090000_fix_column_types.sql
```

## Quick Reference

| Task | Command |
|------|---------|
| Generate migration | `python scripts/generate_migration.py "description"` |
| Create empty migration | `supabase migration new description` |
| Apply migrations | `supabase db push` |
| View migration status | `supabase migration list` |
| Update views | Run `sql/views/99_DEPLOY_ALL_VIEWS.sql` in SQL Editor |
| Full reset (emergency) | `sql/reset_supabase.sql` |
