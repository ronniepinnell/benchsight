# BenchSight Development Environment Setup

**Complete guide for setting up development environments from scratch**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This guide provides complete instructions for setting up development environments for all BenchSight components: ETL, Dashboard, API, and Portal.

**Prerequisites:** None (this guide covers everything)  
**Time Required:** 2-3 hours  
**Components:** Python ETL, Next.js Dashboard, FastAPI, Supabase, Vercel

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] macOS, Linux, or Windows
- [ ] Terminal/Command Prompt access
- [ ] Git installed
- [ ] Text editor (VS Code recommended)
- [ ] Internet connection

---

## Step 1: Install Core Tools

### Python 3.11+

**macOS (Homebrew):**
```bash
brew install python@3.11
python3 --version  # Should show 3.11+
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
python3 --version
```

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Install with "Add Python to PATH" checked
- Verify: `python --version`

### Node.js 18+ or 20+

**macOS (Homebrew):**
```bash
brew install node@20
node --version  # Should show 20.x
npm --version
```

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
```

**Windows:**
- Download from [nodejs.org](https://nodejs.org/)
- Install LTS version
- Verify: `node --version`

### Git

**macOS:**
```bash
brew install git
git --version
```

**Linux:**
```bash
sudo apt install git
git --version
```

**Windows:**
- Download from [git-scm.com](https://git-scm.com/)
- Install with default options
- Verify: `git --version`

---

## Step 2: Clone Repository

```bash
git clone https://github.com/your-username/benchsight.git
cd benchsight
```

---

## Step 3: Python Environment Setup

### Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Install Python Dependencies

```bash
# Install ETL dependencies
pip install -r requirements.txt

# Install API dependencies
cd api
pip install -r requirements.txt
cd ..
```

### Verify Python Setup

```bash
python3 -c "import pandas, fastapi, supabase; print('✅ Python packages OK')"
```

---

## Step 4: Node.js Environment Setup

### Install Dashboard Dependencies

```bash
cd ui/dashboard
npm install
cd ../..
```

### Verify Node.js Setup

```bash
cd ui/dashboard
npm run build  # Should complete without errors
cd ../..
```

---

## Step 5: Supabase Setup

### Option 1: Cloud Supabase (Recommended)

**Step 1: Create Supabase Project**

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in:
   - **Name:** `benchsight-dev`
   - **Database Password:** (save this!)
   - **Region:** Choose closest region
5. Click "Create new project"
6. Wait 2-3 minutes for project to initialize

**Step 2: Get Credentials**

**From Project Settings → API:**
- **Project URL:** `https://xxxxx.supabase.co`
- **anon/public key:** `eyJhbGc...` (use for client-side)
- **service_role key:** `eyJhbGc...` (use for server-side, keep secret!)

**Step 3: Configure Local Connection**

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

**Step 4: Create Schema**

1. Go to SQL Editor in Supabase dashboard
2. Run `sql/reset_supabase.sql`
3. Verify tables created (should see 139+ tables)

**Step 5: Upload Data**

```bash
# Run ETL first
python run_etl.py

# Upload to Supabase
python upload.py
```

### Option 2: Local Supabase (Docker)

**Prerequisites:**
- Docker installed
- Docker Compose installed

**Step 1: Install Supabase CLI**

```bash
npm install -g supabase
supabase --version
```

**Step 2: Initialize Supabase**

```bash
# In project root
supabase init
```

This creates:
- `supabase/config.toml` - Configuration
- `supabase/migrations/` - Database migrations

**Step 3: Start Local Supabase**

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

**Step 4: Configure Local Connection**

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

**Step 5: Create Schema**

```bash
# Run SQL migrations
supabase db reset

# Or manually run schema
psql postgresql://postgres:postgres@localhost:54322/postgres -f sql/reset_supabase.sql
```

**Step 6: Stop Local Supabase**

```bash
supabase stop
```

### Supabase Studio

**Access Studio:**
- **Cloud:** `https://xxxxx.supabase.co` (dashboard)
- **Local:** `http://localhost:54323`

**Studio Features:**
- **Table Editor:** View/edit table data
- **SQL Editor:** Run SQL queries
- **Authentication:** Manage users
- **Storage:** File storage
- **API Docs:** Auto-generated API docs

### Database Schema Setup

**Step 1: Create Tables**

Run in SQL Editor:
```sql
-- Run sql/reset_supabase.sql
-- This creates all 139 tables
```

**Step 2: Create Views**

Run in SQL Editor:
```sql
-- Run sql/views/99_DEPLOY_ALL_VIEWS.sql
-- This creates all 30 views
```

**Step 3: Set Up RLS Policies**

Run in SQL Editor:
```sql
-- Run sql/fix_rls_policies.sql
-- Or disable RLS for development:
-- Run sql/disable_rls.sql
```

### Row Level Security (RLS)

**Development Setup:**

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

**Production Setup:**

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

### Data Upload

**Upload All Tables:**
```bash
python upload.py
```

**Upload Specific Tables:**
```bash
python upload.py --tables dim_player dim_team
```

**Upload by Pattern:**
```bash
python upload.py --pattern "fact_player*"
```

**Upload Dimensions Only:**
```bash
python upload.py --dims
```

**Upload Facts Only:**
```bash
python upload.py --facts
```

### Testing Supabase Connection

**Python Test:**
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

**JavaScript Test:**
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

## Step 6: Vercel Setup (Dashboard)

### Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up"
3. Sign up with GitHub (recommended)
4. Authorize Vercel to access your repositories

### Install Vercel CLI

```bash
npm install -g vercel
vercel --version
```

### Local Vercel Development

**Initialize Vercel in Project:**
```bash
cd ui/dashboard
vercel
```

**Follow prompts:**
- Set up and deploy? **Yes**
- Which scope? **Your account**
- Link to existing project? **No**
- Project name? **benchsight-dashboard**
- Directory? **./** (current directory)
- Override settings? **No**

**Start Local Dev Server:**
```bash
vercel dev
```

**Access:**
- Local: `http://localhost:3000`
- Vercel preview: `https://benchsight-dashboard-xxxxx.vercel.app`

### Deploy to Vercel

**Option 1: Deploy from CLI**
```bash
cd ui/dashboard
vercel --prod
```

**Option 2: Deploy from GitHub**

1. **Import Repository:**
   - Go to Vercel dashboard
   - Click "Add New Project"
   - Select your GitHub repository
   - Click "Import"

2. **Configure Project:**
   - **Framework Preset:** Next.js
   - **Root Directory:** `ui/dashboard`
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)
   - **Install Command:** `npm install` (default)

3. **Environment Variables:**
   - Add `NEXT_PUBLIC_SUPABASE_URL`
   - Add `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - Add `NEXT_PUBLIC_API_URL` (optional)

4. **Deploy:**
   - Click "Deploy"
   - Wait for deployment (2-3 minutes)

### Configure Environment Variables

**In Vercel Dashboard:**

1. Go to Project Settings → Environment Variables
2. Add variables:

**Production:**
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

**Preview:**
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

**Development:**
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**In Local `.env.local`:**

Create `ui/dashboard/.env.local`:
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Configure Build Settings

**Vercel Configuration:**

Create `ui/dashboard/vercel.json` (optional):
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "installCommand": "npm install"
}
```

**Next.js Configuration:**

`ui/dashboard/next.config.js` already configured:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configuration
}

module.exports = nextConfig
```

### Domain Setup (Optional)

**Add Custom Domain:**

1. Go to Project Settings → Domains
2. Add domain: `dashboard.benchsight.com`
3. Follow DNS configuration instructions
4. Wait for DNS propagation (up to 24 hours)

### Deployment Workflow

**Automatic Deployments:**

Vercel automatically deploys:
- Push to `main` branch → Production deployment
- Push to other branches → Preview deployment
- Pull requests → Preview deployment

**Manual Deployment:**
```bash
cd ui/dashboard
vercel --prod
```

**Preview Deployment:**
```bash
vercel
```

### Local Development Workflow

**Standard Development:**
```bash
cd ui/dashboard
npm run dev
# Access at http://localhost:3000
```

**Vercel Dev (Recommended):**
```bash
cd ui/dashboard
vercel dev
# Access at http://localhost:3000
# Uses Vercel's environment and routing
```

---

## Step 7: API Setup (Railway/Render)

### Railway Setup

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project
4. Deploy from GitHub

**Configuration:**
- Build Command: `cd api && pip install -r requirements.txt`
- Start Command: `cd api && python main.py`
- Environment Variables:
  - `ENVIRONMENT=production`
  - `CORS_ORIGINS=https://your-dashboard.vercel.app`

### Render Setup

1. Go to [render.com](https://render.com)
2. Sign up
3. Create new Web Service
4. Connect GitHub repository

**Configuration:**
- Build Command: `cd api && pip install -r requirements.txt`
- Start Command: `cd api && python main.py`
- Environment Variables: Same as Railway

---

## Step 8: Verify Setup

### Test ETL

```bash
# Run ETL
python run_etl.py

# Should create 139 tables in data/output/
ls data/output/*.csv | wc -l  # Should show 139
```

### Test API

```bash
# Start API
cd api
python main.py

# In another terminal, test health endpoint
curl http://localhost:8000/api/health

# Should return: {"status":"healthy","version":"1.0.0",...}
```

### Test Dashboard

```bash
# Start dashboard
cd ui/dashboard
npm run dev

# Open http://localhost:3000
# Should see dashboard
```

### Test Supabase Connection

```bash
# Test Python connection
python -c "
from supabase import create_client
import os
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
client = create_client(url, key)
print('✅ Supabase connection OK')
"
```

---

## Environment Variables Reference

### ETL Environment Variables

**`config/config_local.ini`:**
```ini
[supabase]
url = https://your-project.supabase.co
anon_key = your_anon_key
service_key = your_service_key
```

### API Environment Variables

**`.env` (in `api/` directory):**
```bash
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
```

### Dashboard Environment Variables

**`.env.local` (in `ui/dashboard/` directory):**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Troubleshooting

### Python Issues

**Problem:** `python3` not found  
**Solution:** Use `python` instead, or install Python 3.11+

**Problem:** Package installation fails  
**Solution:** Upgrade pip: `pip install --upgrade pip`

**Problem:** Virtual environment not activating  
**Solution:** Use full path: `source ./venv/bin/activate`

### Node.js Issues

**Problem:** `npm install` fails  
**Solution:** Clear cache: `npm cache clean --force`

**Problem:** Build fails  
**Solution:** Delete `node_modules` and `package-lock.json`, then `npm install`

### Supabase Issues

**Problem:** Connection fails  
**Solution:** Verify URL and keys in config file

**Problem:** RLS policies blocking queries  
**Solution:** Check RLS policies in Supabase dashboard

**Problem:** Tables not found  
**Solution:** Run `sql/reset_supabase.sql`

**Problem:** Views not found  
**Solution:** Run `sql/views/99_DEPLOY_ALL_VIEWS.sql`

**Problem:** Upload fails  
**Solution:** Check RLS policies, verify table schemas match, check data types

### Vercel Issues

**Problem:** Build fails on Vercel  
**Solution:** Check build logs in Vercel dashboard, verify Node.js version (should be 18+), check for TypeScript errors, verify environment variables

**Problem:** Missing environment variables  
**Solution:** Add variables in Vercel dashboard, redeploy after adding variables

**Problem:** Deployment takes too long  
**Solution:** Check build logs, optimize build (reduce dependencies), use Vercel's build cache

**Problem:** Preview URL not working  
**Solution:** Check deployment status, verify environment variables, check build logs

**Problem:** `vercel dev` fails  
**Solution:** Run `vercel login` first, verify project is linked: `vercel link`, check `.vercel` directory exists

**Problem:** Environment variables not loading  
**Solution:** Use `.env.local` for local development, run `vercel dev` to use Vercel's env vars

---

## Quick Start Commands

### Daily Development

```bash
# Activate Python environment
source venv/bin/activate

# Run ETL
python run_etl.py

# Start API
cd api && python main.py &

# Start Dashboard
cd ui/dashboard && npm run dev
```

### Verification

```bash
# Check Python
python3 --version
python3 -c "import pandas, fastapi, supabase; print('✅ OK')"

# Check Node.js
node --version
npm --version

# Check API
curl http://localhost:8000/api/health

# Check Dashboard
curl http://localhost:3000
```

---

## Related Documentation

- [SETUP.md](SETUP.md) - Basic setup guide
- [environments/ENVIRONMENTS.md](../environments/ENVIRONMENTS.md) - Environment management
- [workflows/WORKFLOW.md](../workflows/WORKFLOW.md) - Development workflows

---

*Last Updated: 2026-01-15*
