# Running ETL to Dev Environment

**Step-by-step guide to run ETL against your Supabase develop branch**

---

## Quick Answer

```bash
# 1. Switch to dev environment (uses Supabase develop branch)
./scripts/switch_env.sh sandbox

# 2. Verify you're on develop branch
cat config/config_local.ini | grep url
# Should show your Supabase develop branch URL

# 3. Run ETL
python run_etl.py

# 4. Upload to Supabase develop branch
python upload.py
```

**Note:** This assumes you've set up a Supabase `develop` branch. See [DEV_ENV.md](../setup/DEV_ENV.md) for setup.

---

## Detailed Steps

### Step 1: Set Up Dev Configuration

**First time setup - Create dev config file for Supabase develop branch:**

```bash
# 1. Copy your current config as a template
cp config/config_local.ini config/config_local.develop.ini
# Or: cp config/config_local.ini config/config_local_sandbox.ini

# 2. Edit the dev config with Supabase develop branch credentials
nano config/config_local.develop.ini
# Or use your preferred editor
```

**Update the Supabase section with develop branch credentials:**
```ini
[supabase]
url = https://your-project-branch-ref.supabase.co
service_key = your-develop-service-key
anon_key = your-develop-anon-key
```

**Get Supabase develop branch credentials:**
1. Go to Supabase Dashboard
2. Go to **Branches** → Select **develop** branch
3. Go to **Settings** → **API**
4. Copy:
   - **Project URL** (this is the branch-specific URL) → `url`
   - **service_role** key → `service_key`
   - **anon public** key → `anon_key`

**Important:** Use the branch URL, not the main project URL!

### Step 2: Switch to Dev Environment

```bash
# Switch to sandbox/dev environment
./scripts/switch_env.sh sandbox
```

**What this does:**
- Copies `config_local_sandbox.ini` → `config_local.ini`
- Updates dashboard `.env.local` if configured
- ETL will now use dev Supabase credentials

**Verify it worked:**
```bash
# Check the config file
cat config/config_local.ini | grep -A 3 "\[supabase\]"
# Should show your dev Supabase URL
```

### Step 3: Run ETL

```bash
# Run full ETL (generates CSV files)
python run_etl.py

# Or with options:
python run_etl.py --wipe          # Clean slate first
python run_etl.py --games 18969   # Specific games
python run_etl.py --status        # Check status
```

**What happens:**
- ETL reads from `config/config_local.ini`
- Uses dev Supabase credentials
- Generates CSV files in `data/output/`
- **Does NOT upload to Supabase yet** (that's step 4)

### Step 4: Upload to Dev Supabase

```bash
# Upload all tables to dev Supabase
python upload.py

# Or with options:
python upload.py --dims           # Dimension tables only
python upload.py --facts          # Fact tables only
python upload.py --tables dim_player fact_events  # Specific tables
python upload.py --list           # List available tables
python upload.py --dry-run        # Preview without uploading
```

**What happens:**
- Reads CSV files from `data/output/`
- Uses dev Supabase credentials from config
- Uploads data to dev Supabase project
- Creates/updates tables in dev database

---

## Complete Workflow Example

```bash
# 1. Switch to dev
./scripts/switch_env.sh sandbox

# 2. Verify you're on dev
cat config/config_local.ini | grep url
# Should show dev Supabase URL

# 3. Run ETL
python run_etl.py --wipe

# 4. Validate output
python validate.py

# 5. Upload to dev Supabase
python upload.py

# 6. Verify in Supabase
# Go to Supabase Dashboard → Table Editor
# Check that tables have data
```

---

## Using Supabase Develop Branch

**This workflow uses Supabase branching (recommended):**

```bash
# 1. Get develop branch URL
# In Supabase Dashboard → Branches → develop
# Copy the branch-specific URL (not main project URL)

# 2. Update config_local.develop.ini with branch URL
nano config/config_local.develop.ini
# Update url to develop branch URL

# 3. Switch to dev environment
./scripts/switch_env.sh sandbox
# This copies config_local.develop.ini → config_local.ini

# 4. Verify you're on develop branch
cat config/config_local.ini | grep url
# Should show develop branch URL

# 5. Run ETL
python run_etl.py

# 6. Upload to develop branch
python upload.py
```

**Benefits of using Supabase branches:**
- ✅ Isolated database for development
- ✅ Easy to merge schema changes
- ✅ Can test schema changes safely
- ✅ One project to manage (not separate projects)

---

## Verification

### Check Which Environment You're Using

```bash
# Check config file
cat config/config_local.ini | grep -A 3 "\[supabase\]"

# Should show:
# [supabase]
# url = https://your-dev-project.supabase.co
# service_key = eyJ... (your dev key)
```

### Verify Data in Supabase Develop Branch

1. **Go to Supabase Dashboard:**
   - Go to **Branches** → Select **develop** branch
   - Go to **Table Editor**

2. **Check tables:**
   - Look for your tables (e.g., `dim_player`, `fact_events`)
   - Verify they have data
   - Check row counts

3. **Test queries:**
   ```sql
   -- In Supabase SQL Editor (make sure you're on develop branch)
   SELECT COUNT(*) FROM dim_player;
   SELECT COUNT(*) FROM fact_events;
   ```

**Important:** Make sure you're viewing the **develop branch**, not the main branch!

---

## Troubleshooting

### "Config file not found"

**Problem:** `config_local_sandbox.ini` doesn't exist

**Solution:**
```bash
# Create it
cp config/config_local.ini config/config_local_sandbox.ini
# Edit with dev credentials
nano config/config_local_sandbox.ini
```

### "Wrong Supabase project"

**Problem:** ETL uploaded to production instead of dev

**Solution:**
```bash
# Check current config
cat config/config_local.ini | grep url

# Switch to dev
./scripts/switch_env.sh sandbox

# Verify
cat config/config_local.ini | grep url
# Should show dev URL
```

### "Connection failed"

**Problem:** Can't connect to Supabase

**Check:**
1. Is the URL correct? (no typos)
2. Is the service_key correct?
3. Is the Supabase project active?
4. Are you using the right branch URL (if using branches)?

**Solution:**
```bash
# Test connection
python -c "
from config.config_loader import config
print(f'URL: {config.supabase_url}')
print(f'Key: {config.supabase_service_key[:20]}...')
"
```

### "Tables don't exist in Supabase"

**Problem:** Upload fails because tables don't exist

**Solution:**
1. **Create schema in dev Supabase:**
   - Go to Supabase Dashboard → SQL Editor
   - Run `sql/setup_supabase.sql` (or your schema SQL)
   - Or run: `python upload.py --schema` (if supported)

2. **Then upload data:**
   ```bash
   python upload.py
   ```

---

## Environment Switching

### Switch to Dev
```bash
./scripts/switch_env.sh sandbox
```

### Switch to Production (⚠️ Be Careful!)
```bash
./scripts/switch_env.sh production
```

### Check Current Environment
```bash
cat config/config_local.ini | grep -A 1 "\[supabase\]"
```

---

## Best Practices

### ✅ Do This

1. **Always verify environment before running ETL:**
   ```bash
   cat config/config_local.ini | grep url
   ```

2. **Use switch script:**
   - Don't manually edit `config_local.ini`
   - Use `switch_env.sh` to switch environments

3. **Test in dev first:**
   - Always test ETL in dev
   - Verify data looks correct
   - Then run to production

4. **Keep config files separate:**
   - `config_local.ini` - Production config (default)
   - `config_local.develop.ini` - Dev config (switch to this for dev)

### ❌ Don't Do This

1. **Don't run ETL to production without testing:**
   - Always test in dev first
   - Verify data is correct
   - Check for errors

2. **Don't manually edit active config:**
   - Use switch script instead
   - Keeps backups intact

3. **Don't forget to switch back:**
   - After production work, switch back to dev
   - Prevents accidental production changes

---

## Quick Reference

### Commands

```bash
# Switch to dev
./scripts/switch_env.sh dev

# Run ETL
python run_etl.py

# Upload to dev
python upload.py

# Check environment
cat config/config_local.ini | grep url

# Production uses config_local.ini directly (no switching needed)
# Just make sure config_local.ini has production credentials
```

### File Locations

```
config/
├── config_local.ini          # Production config (default)
└── config_local.develop.ini  # Dev config (switch to this for dev)
```

### Config Structure

```ini
[supabase]
url = https://your-project.supabase.co
service_key = your-service-role-key
anon_key = your-anon-key

[loader]
batch_size = 500
verbose = true
default_operation = upsert

[paths]
data_dir = data/output
log_dir = logs
```

---

## Example: First Time Setup

```bash
# 1. Create dev config
cp config/config_local.ini config/config_local_sandbox.ini

# 2. Edit with dev credentials
nano config/config_local_sandbox.ini
# Update [supabase] section with dev URL and keys

# 3. Switch to dev
./scripts/switch_env.sh sandbox

# 4. Verify
cat config/config_local.ini | grep url
# Should show dev URL

# 5. Run ETL
python run_etl.py

# 6. Upload
python upload.py

# 7. Verify in Supabase Dashboard
# Check that tables have data
```

---

*Last updated: 2026-01-13*
