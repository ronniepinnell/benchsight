# BenchSight Tech Stack Requirements

**Complete list of technologies and tools needed for BenchSight**

Last Updated: 2026-01-13

---

## 🎯 Quick Summary

**Core Stack:**
- **Python 3.11+** (ETL + API)
- **Node.js 18+** (Dashboard)
- **Supabase** (Database + Auth)
- **FastAPI** (API - NEW)
- **Next.js 14** (Dashboard)

---

## 📦 Required Software

### 1. Python Environment

**Version:** Python 3.11 or higher

**Check version:**
```bash
python3 --version
# Should show: Python 3.11.x or higher
```

**Install Python:**
- **macOS:** `brew install python@3.11`
- **Linux:** `sudo apt install python3.11`
- **Windows:** Download from [python.org](https://www.python.org/downloads/)

---

## 🔧 Python Dependencies

### Existing ETL System

**File:** `requirements.txt` (project root)

```bash
pip install -r requirements.txt
```

**Packages:**
- `flask>=2.0.0` (legacy - not actively used)
- `pandas>=1.5.0` (data processing)
- `openpyxl>=3.0.0` (Excel file handling)

**Additional packages (if not installed):**
```bash
# Supabase integration
pip install supabase

# PostgreSQL (for Supabase)
pip install psycopg2-binary

# Testing (optional)
pip install pytest
```

### NEW: ETL API (Just Built)

**File:** `api/requirements.txt`

```bash
pip install -r api/requirements.txt
```

**Packages:**
- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `pydantic==2.5.0` - Data validation
- `python-dotenv==1.0.0` - Environment variables
- `httpx==0.25.2` - HTTP client

**Optional (for production):**
- `celery==5.3.4` - Task queue (future)
- `redis==5.0.1` - Cache/queue (future)

---

## 🌐 Node.js & Dashboard

### Node.js

**Version:** Node.js 18.x or higher (20.x recommended)

**Check version:**
```bash
node --version
# Should show: v18.x.x or v20.x.x
npm --version
# Should show: 9.x.x or 10.x.x
```

**Install Node.js:**
- **macOS:** `brew install node@20`
- **Linux:** `sudo apt install nodejs npm`
- **Windows:** Download from [nodejs.org](https://nodejs.org/)
- **All:** Use [nvm](https://github.com/nvm-sh/nvm) (recommended)

### Dashboard Dependencies

**Location:** `ui/dashboard/`

**Install:**
```bash
cd ui/dashboard
npm install
```

**Key Packages (auto-installed):**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Supabase client
- shadcn/ui components

---

## 🗄️ Database & Services

### Supabase (Required)

**What it provides:**
- PostgreSQL database
- Authentication
- Real-time subscriptions
- Storage (future)

**Free tier includes:**
- 500MB database
- 2GB bandwidth
- 50,000 monthly active users

**Get account:**
1. Go to [supabase.com](https://supabase.com)
2. Sign up (free)
3. Create project
4. Get credentials:
   - Project URL: `https://xxxxx.supabase.co`
   - Anon key: `eyJ...` (public key)
   - Service key: `eyJ...` (private key - keep secret!)

**Configuration:**
- Store in `config/config_local.ini`
- Dashboard uses `.env.local` in `ui/dashboard/`

---

## 🚀 API Server (NEW)

### Development

**Run locally:**
```bash
cd api
python main.py

# Or with uvicorn directly:
uvicorn api.main:app --reload --port 8000
```

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs (Swagger UI)
- ReDoc: http://localhost:8000/redoc

### Production Deployment (Future)

**Recommended platforms:**
- **Railway** ($5/month) - Easy Python deployment
- **Render** (Free tier) - Good for MVP
- **Fly.io** - Good performance
- **Heroku** - Classic option

---

## 📊 Complete Tech Stack Overview

### Backend

| Component | Technology | Purpose | Status |
|-----------|-----------|---------|--------|
| ETL Pipeline | Python 3.11+ | Data processing | ✅ Active |
| ETL API | FastAPI + Uvicorn | Web API for ETL | ✅ NEW |
| Database | Supabase (PostgreSQL) | Data storage | ✅ Active |
| Upload Script | Python (pandas) | Upload to Supabase | ✅ Active |

### Frontend

| Component | Technology | Purpose | Status |
|-----------|-----------|---------|--------|
| Dashboard | Next.js 14 + React | Public stats | ✅ Active |
| Admin Portal | HTML/JS (vanilla) | Admin controls | ⚠️ Needs API |
| Tracker | HTML/JS (vanilla) | Game tracking | ✅ Active |

### Development Tools

| Tool | Purpose | Required? |
|------|---------|-----------|
| Git | Version control | ✅ Yes |
| Python venv | Virtual environments | ✅ Recommended |
| npm | Node package manager | ✅ Yes (for dashboard) |
| pip | Python package manager | ✅ Yes |

### Infrastructure (Current)

| Service | Provider | Cost | Status |
|---------|----------|------|--------|
| Database | Supabase | Free tier | ✅ Active |
| Dashboard Hosting | Vercel (future) | Free tier | ⏳ Not deployed |
| API Hosting | Local (future: Railway) | $0 now, $5/mo later | ✅ Local |
| Tracker Hosting | Local | $0 | ✅ Local |

---

## 📥 Installation Checklist

### 1. Python Setup

```bash
# Check Python version
python3 --version  # Should be 3.11+

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Install ETL dependencies
pip install -r requirements.txt

# Install API dependencies (NEW)
pip install -r api/requirements.txt

# Verify installations
python -c "import pandas, fastapi; print('✅ Python packages OK')"
```

### 2. Node.js Setup

```bash
# Check Node version
node --version  # Should be 18+ or 20+
npm --version

# Install dashboard dependencies
cd ui/dashboard
npm install

# Verify
npm run build  # Should complete without errors
```

### 3. Supabase Setup

```bash
# 1. Create Supabase account (free)
# 2. Create project
# 3. Get credentials from Settings → API
# 4. Add to config/config_local.ini:
#    [supabase]
#    url = https://xxxxx.supabase.co
#    service_key = eyJ...

# 5. For dashboard, create ui/dashboard/.env.local:
#    NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
#    NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

### 4. Verify Everything Works

```bash
# Test ETL
python run_etl.py --status

# Test API (NEW)
cd api
python main.py
# Visit http://localhost:8000/api/health

# Test Dashboard
cd ui/dashboard
npm run dev
# Visit http://localhost:3000
```

---

## 🔍 Version Compatibility

### Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.11+ | Language |
| pandas | >=1.5.0 | Data processing |
| fastapi | 0.104.1 | API framework |
| uvicorn | 0.24.0 | ASGI server |
| pydantic | 2.5.0 | Validation |
| supabase | Latest | Database client |

### Node.js Packages

| Package | Version | Purpose |
|---------|---------|---------|
| Node.js | 18+ or 20+ | Runtime |
| Next.js | 14.x | Framework |
| React | 18.x | UI library |
| TypeScript | Latest | Type safety |

---

## 🛠️ Development Workflow

### Typical Development Setup

**Terminal 1 - Dashboard (runs continuously):**
```bash
cd ui/dashboard
npm run dev
# → http://localhost:3000
```

**Terminal 2 - API (NEW - runs continuously):**
```bash
cd api
python main.py
# → http://localhost:8000
```

**Terminal 3 - ETL (run when needed):**
```bash
python run_etl.py
python upload.py
```

**Terminal 4 - Admin Portal (static HTML):**
```bash
# Serve via any static server, or open directly
open ui/portal/index.html
```

---

## 💰 Cost Summary

### Current (Development)

| Service | Cost |
|---------|------|
| Supabase (free tier) | $0/month |
| Local development | $0 |
| **Total** | **$0/month** |

### Production (Future)

| Service | Cost |
|---------|------|
| Supabase (free tier) | $0/month |
| Vercel (dashboard) | $0/month (free tier) |
| Railway (API) | $5/month |
| Domain | $12/year |
| **Total** | **~$6/month** |

---

## 🚨 Common Issues & Solutions

### "Python version too old"
```bash
# macOS: Install via Homebrew
brew install python@3.11

# Or use pyenv
pyenv install 3.11.0
pyenv local 3.11.0
```

### "pip install fails"
```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### "Node.js not found"
```bash
# macOS: Install via Homebrew
brew install node@20

# Or use nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

### "FastAPI not found"
```bash
# Make sure you installed API dependencies
pip install -r api/requirements.txt

# Verify
python -c "import fastapi; print('OK')"
```

### "Dashboard won't start"
```bash
# Clean install
cd ui/dashboard
rm -rf node_modules package-lock.json
npm install

# Check Node version (needs 18+)
node --version
```

---

## 📚 Additional Resources

- **Python:** [python.org](https://www.python.org/)
- **Node.js:** [nodejs.org](https://nodejs.org/)
- **FastAPI:** [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- **Next.js:** [nextjs.org](https://nextjs.org/)
- **Supabase:** [supabase.com/docs](https://supabase.com/docs)

---

## ✅ Quick Verification

Run these commands to verify your setup:

```bash
# Python
python3 --version  # Should be 3.11+
python3 -c "import pandas, fastapi, supabase; print('✅ Python packages OK')"

# Node.js
node --version  # Should be 18+ or 20+
npm --version

# API (NEW)
cd api && python main.py &
sleep 2
curl http://localhost:8000/api/health
# Should return: {"status":"healthy","version":"1.0.0",...}

# Dashboard
cd ui/dashboard && npm run build
# Should complete without errors
```

---

*Last Updated: 2026-01-13*
