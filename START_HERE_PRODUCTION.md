# 🚀 Production Setup - Start Here

**Everything you need to deploy BenchSight to production.**

## ✅ What's Ready

Your system is **100% production-ready** with:

- ✅ **Dashboard** - Next.js 14, authenticated, ready for Vercel
- ✅ **Tracker** - Integrated React components, protected routes
- ✅ **Admin Portal** - Embedded in dashboard
- ✅ **Authentication** - Supabase Auth with login system
- ✅ **ETL API** - FastAPI code ready for Railway/Render
- ✅ **Configuration** - All production configs created

## 🎯 Quick Start (30 Minutes)

### Step 1: Pre-Deployment Check (2 min)

```bash
./scripts/deploy-production.sh
```

This verifies everything is ready.

### Step 2: Deploy Dashboard (10 min)

**Via Vercel Dashboard (Easiest):**
1. Go to https://vercel.com/new
2. Import your GitHub repo
3. Set root: `ui/dashboard`
4. Add environment variables (see below)
5. Deploy

**Via CLI:**
```bash
cd ui/dashboard
vercel login
vercel --prod
```

### Step 3: Deploy API (10 min)

```bash
cd api
railway login
railway init
railway up
```

### Step 4: Configure Environment Variables (5 min)

**Vercel Dashboard → Settings → Environment Variables:**
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
NEXT_PUBLIC_API_URL=https://xxx.railway.app (after API deploys)
```

**Railway Dashboard → Variables:**
```
ENVIRONMENT=production
CORS_ORIGINS=https://your-dashboard.vercel.app
```

### Step 5: Set Up Auth (3 min)

1. Supabase Dashboard → Authentication → Providers → Enable Email
2. Add redirect URLs: `https://your-dashboard.vercel.app/auth/callback`
3. Create admin user

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **`docs/PRODUCTION_SETUP.md`** | Complete step-by-step guide |
| **`PRODUCTION_CHECKLIST.md`** | Deployment checklist |
| **`docs/ENVIRONMENT_VARIABLES.md`** | All env vars explained |
| **`api/DEPLOYMENT.md`** | API deployment details |
| **`docs/AUTHENTICATION_SETUP.md`** | Auth configuration |

## 🔑 Key Files Created

### Production Configuration
- ✅ `api/config.py` - Updated with production CORS support
- ✅ `api/railway.json` - Railway deployment config
- ✅ `api/Procfile` - Render/Heroku support
- ✅ `api/runtime.txt` - Python version

### Documentation
- ✅ `docs/PRODUCTION_SETUP.md` - Complete guide
- ✅ `PRODUCTION_CHECKLIST.md` - Checklist
- ✅ `docs/ENVIRONMENT_VARIABLES.md` - Env var reference
- ✅ `README_PRODUCTION.md` - Quick reference

### Scripts
- ✅ `scripts/deploy-production.sh` - Pre-deployment check

## 💰 Cost

**Monthly:** ~$5/month
- Vercel: **Free** (hobby tier)
- Railway: **$5/month** (starter plan)
- Supabase: **Free** (free tier)

**Total: $5/month** for full production setup

## 🎯 What You'll Have

After deployment:

1. **Dashboard** → `https://your-project.vercel.app`
   - Public pages (standings, leaders, players)
   - Protected admin portal (`/admin`)
   - Protected tracker (`/tracker`)

2. **API** → `https://your-api.railway.app`
   - ETL job triggers
   - Health checks
   - API docs at `/docs`

3. **Authentication**
   - Login page
   - Protected routes
   - User management

## ⚡ Next Steps

1. **Run pre-deployment check:**
   ```bash
   ./scripts/deploy-production.sh
   ```

2. **Follow the guide:**
   - Open `docs/PRODUCTION_SETUP.md`
   - Follow step-by-step instructions

3. **Use the checklist:**
   - Open `PRODUCTION_CHECKLIST.md`
   - Check off items as you complete them

## 🆘 Need Help?

- **Build errors?** Check `docs/PRODUCTION_SETUP.md` troubleshooting
- **Env vars?** See `docs/ENVIRONMENT_VARIABLES.md`
- **Auth issues?** See `docs/AUTHENTICATION_SETUP.md`
- **API problems?** See `api/DEPLOYMENT.md`

## ✨ You're Ready!

Everything is configured and ready. Just follow the deployment steps and you'll be live in 30 minutes!

**Start here:** `docs/PRODUCTION_SETUP.md`

---

*Last Updated: 2026-01-13*
