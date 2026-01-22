# Supabase Development Environment Setup

**Complete guide for setting up Supabase for development**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This guide covers setting up Supabase for BenchSight development, including local and cloud options.

**Options:**
1. **Cloud Supabase** (Recommended for development) - Easy setup, free tier
2. **Local Supabase** (Advanced) - Docker-based local instance

---

## Option 1: Cloud Supabase (Recommended)

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in:
   - **Name:** `benchsight-dev`
   - **Database Password:** (save this!)
   - **Region:** Choose closest region
5. Click "Create new project"
6. Wait 2-3 minutes for project to initialize

### Step 2: Get Credentials

**From Project Settings → API:**
- **Project URL:** `https://xxxxx.supabase.co`
- **anon/public key:** `eyJhbGc...` (use for client-side)
- **service_role key:** `eyJhbGc...` (use for server-side, keep secret!)

### Step 3: Configure Local Connection

**Create `config/config_local.ini`:**
```ini
[supabase]
url = https://xxxxx.supabase.co
anon_key = eyJhbGc...your_anon_key
service_key = eyJhbGc...your_service_key
```

**Create `.env.local` (for dashboard):**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...your_anon_key
```

### Step 4: Create Schema

1. Go to SQL Editor in Supabase dashboard
2. Run `sql/reset_supabase.sql`
3. Verify tables created (should see 139+ tables)

### Step 5: Upload Data

```bash
# Run ETL first
python run_etl.py

# Upload to Supabase
python upload.py
```

---

## Option 2: Local Supabase (Docker)

### Prerequisites

- Docker installed
- Docker Compose installed

### Step 1: Install Supabase CLI

```bash
npm install -g supabase
supabase --version
```

### Step 2: Initialize Supabase

```bash
# In project root
supabase init
```

This creates:
- `supabase/config.toml` - Configuration
- `supabase/migrations/` - Database migrations

### Step 3: Start Local Supabase

```bash
supabase start
```

**Output:**
```
Started supabase local development setup.

         API URL: http://localhost:54321
     GraphQL URL: http://localhost:54321/graphql/v1
          DB URL: postgresql://postgres:postgres@localhost:54322/postgres
      Studio URL: http://localhost:54323
    Inbucket URL: http://localhost:54324
      JWT secret: super-secret-jwt-token-with-at-least-32-characters-long
        anon key: eyJhbGc...
service_role key: eyJhbGc...
```

### Step 4: Configure Local Connection

**Update `config/config_local.ini`:**
```ini
[supabase]
url = http://localhost:54321
anon_key = eyJhbGc...from_output_above
service_key = eyJhbGc...from_output_above
```

**Update `.env.local` (for dashboard):**
```bash
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...from_output_above
```

### Step 5: Create Schema

```bash
# Run SQL migrations
supabase db reset

# Or manually run schema
psql postgresql://postgres:postgres@localhost:54322/postgres -f sql/reset_supabase.sql
```

### Step 6: Stop Local Supabase

```bash
supabase stop
```

---

## Supabase Studio

### Access Studio

**Cloud:** `https://xxxxx.supabase.co` (dashboard)

**Local:** `http://localhost:54323`

### Studio Features

- **Table Editor:** View/edit table data
- **SQL Editor:** Run SQL queries
- **Authentication:** Manage users
- **Storage:** File storage
- **API Docs:** Auto-generated API docs

---

## Database Schema Setup

### Step 1: Create Tables

**Run in SQL Editor:**
```sql
-- Run sql/reset_supabase.sql
-- This creates all 139 tables
```

### Step 2: Create Views

**Run in SQL Editor:**
```sql
-- Run sql/views/99_DEPLOY_ALL_VIEWS.sql
-- This creates all 30 views
```

### Step 3: Set Up RLS Policies

**Run in SQL Editor:**
```sql
-- Run sql/fix_rls_policies.sql
-- Or disable RLS for development:
-- Run sql/disable_rls.sql
```

---

## Row Level Security (RLS)

### Development Setup

**Option 1: Disable RLS (Easier for development)**
```sql
-- Run sql/disable_rls.sql
-- All tables accessible without authentication
```

**Option 2: Configure RLS Policies**
```sql
-- Run sql/fix_rls_policies.sql
-- Tables accessible based on policies
```

### Production Setup

**Enable RLS:**
```sql
ALTER TABLE fact_events ENABLE ROW LEVEL SECURITY;
-- ... for all tables
```

**Create Policies:**
```sql
-- Public read access
CREATE POLICY "Public read access" ON fact_events
FOR SELECT USING (true);

-- Admin write access
CREATE POLICY "Admin write access" ON fact_events
FOR ALL USING (auth.role() = 'admin');
```

---

## Data Upload

### Upload All Tables

```bash
python upload.py
```

### Upload Specific Tables

```bash
python upload.py --tables dim_player dim_team
```

### Upload by Pattern

```bash
python upload.py --pattern "fact_player*"
```

### Upload Dimensions Only

```bash
python upload.py --dims
```

### Upload Facts Only

```bash
python upload.py --facts
```

---

## Testing Connection

### Python Test

```python
from supabase import create_client
import os

url = "https://your-project.supabase.co"
key = "your_anon_key"

client = create_client(url, key)

# Test query
result = client.table('dim_player').select('*').limit(1).execute()
print('✅ Connection OK')
print(result.data)
```

### JavaScript Test

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

// Test query
const { data, error } = await supabase
  .from('dim_player')
  .select('*')
  .limit(1)

if (error) {
  console.error('❌ Connection failed:', error)
} else {
  console.log('✅ Connection OK', data)
}
```

---

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to Supabase  
**Solution:**
- Verify URL and keys
- Check network connection
- Verify project is active

**Problem:** RLS blocking queries  
**Solution:**
- Disable RLS for development
- Or configure RLS policies

### Schema Issues

**Problem:** Tables not found  
**Solution:**
- Run `sql/reset_supabase.sql`
- Verify tables in Studio

**Problem:** Views not found  
**Solution:**
- Run `sql/views/99_DEPLOY_ALL_VIEWS.sql`
- Verify views in Studio

### Data Issues

**Problem:** Upload fails  
**Solution:**
- Check RLS policies
- Verify table schemas match
- Check data types

---

## Related Documentation

- [DEV_ENV_COMPLETE.md](DEV_ENV_COMPLETE.md) - Complete dev environment guide
- [DEV_ENV_VERCEL.md](DEV_ENV_VERCEL.md) - Vercel setup
- [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md) - Production deployment

---

*Last Updated: 2026-01-15*
