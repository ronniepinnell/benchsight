# Production Deployment - Quick Start

**Get BenchSight running in production in 30 minutes.**

## 🚀 Quick Deploy

### 1. Run Pre-Deployment Check

```bash
./scripts/deploy-production.sh
```

This verifies everything is ready.

### 2. Deploy Dashboard (Vercel)

**Option A: Via CLI**
```bash
cd ui/dashboard
vercel login
vercel --prod
```

**Option B: Via Dashboard**
1. Go to https://vercel.com/new
2. Import GitHub repo
3. Set root directory: `ui/dashboard`
4. Add environment variables (see below)
5. Deploy

### 3. Deploy API (Railway)

```bash
cd api
railway login
railway init
railway up
```

### 4. Configure Environment Variables

**Vercel:**
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
NEXT_PUBLIC_API_URL=https://xxx.railway.app
```

**Railway:**
```
ENVIRONMENT=production
CORS_ORIGINS=https://your-dashboard.vercel.app
```

### 5. Set Up Supabase Auth

1. Enable Email provider
2. Add redirect URLs
3. Create admin user

## 📚 Full Documentation

- **Complete Guide:** `docs/PRODUCTION_SETUP.md`
- **Checklist:** `PRODUCTION_CHECKLIST.md`
- **Environment Variables:** `docs/ENVIRONMENT_VARIABLES.md`
- **API Deployment:** `api/DEPLOYMENT.md`

## ✅ What's Included

- ✅ Dashboard (Next.js) → Vercel
- ✅ Tracker (React) → Integrated
- ✅ Admin Portal → Embedded
- ✅ Authentication → Supabase Auth
- ✅ ETL API → Railway/Render
- ✅ Production configs → Ready

## 💰 Cost

**Monthly:** ~$5/month
- Vercel: Free
- Railway: $5/month
- Supabase: Free tier

## 🎯 Next Steps

1. Deploy dashboard
2. Deploy API
3. Configure auth
4. Test everything
5. Go live! 🎉

---

**Need help?** See `docs/PRODUCTION_SETUP.md` for detailed instructions.
