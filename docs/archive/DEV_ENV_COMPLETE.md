# BenchSight Complete Dev Environment Setup

**Complete guide to setting up development environments from scratch**

Last Updated: 2026-01-15  
Version: 29.0

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

### Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in
3. Create new project
4. Note your project URL and API keys

### Get Supabase Credentials

**From Supabase Dashboard:**
- Project URL: `https://your-project.supabase.co`
- Anon Key: `eyJhbGc...` (public key)
- Service Key: `eyJhbGc...` (secret key)

### Configure Local Supabase Connection

**Option 1: Local Supabase (Docker)**

```bash
# Install Supabase CLI
npm install -g supabase

# Initialize Supabase locally
supabase init

# Start local Supabase
supabase start
```

**Option 2: Use Cloud Supabase**

- Use your cloud project URL and keys
- No local setup needed

### Create Configuration File

**Create `config/config_local.ini`:**
```ini
[supabase]
url = https://your-project.supabase.co
anon_key = your_anon_key_here
service_key = your_service_key_here
```

**Create `.env.local` (for dashboard):**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
```

---

## Step 6: Vercel Setup (Dashboard)

### Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import your repository

### Configure Vercel Project

1. **Import Repository:**
   - Select your GitHub repository
   - Framework: Next.js
   - Root Directory: `ui/dashboard`

2. **Environment Variables:**
   - Add `NEXT_PUBLIC_SUPABASE_URL`
   - Add `NEXT_PUBLIC_SUPABASE_ANON_KEY`

3. **Deploy:**
   - Click "Deploy"
   - Wait for deployment

### Local Vercel Development

```bash
cd ui/dashboard
npm install -g vercel
vercel dev
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

### Vercel Issues

**Problem:** Deployment fails  
**Solution:** Check build logs, verify environment variables

**Problem:** Dashboard not loading  
**Solution:** Verify Supabase environment variables

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

- [DEV_ENV_SUPABASE.md](DEV_ENV_SUPABASE.md) - Supabase-specific setup
- [DEV_ENV_VERCEL.md](DEV_ENV_VERCEL.md) - Vercel-specific setup
- [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md) - Production deployment

---

*Last Updated: 2026-01-15*
