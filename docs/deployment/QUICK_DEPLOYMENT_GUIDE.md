# Quick Deployment Guide

**Deploy your dashboard, tracker, and portal in under 30 minutes**

Last Updated: 2026-01-13

---

## Prerequisites

- ✅ Vercel account (free): https://vercel.com/signup
- ✅ GitHub account (if not using Vercel CLI)
- ✅ Supabase credentials (already have these)

---

## Step 1: Deploy Dashboard (15 minutes)

### Option A: Using Vercel CLI (Recommended)

```bash
# 1. Navigate to dashboard
cd ui/dashboard

# 2. Test build first (important!)
npm run build

# If build succeeds, continue. If errors, fix them first.

# 3. Install Vercel CLI (if not installed)
npm i -g vercel

# 4. Login to Vercel
vercel login

# 5. Deploy
vercel

# Follow prompts:
# - Set up and deploy? → Yes
# - Which scope? → Your account
# - Link to existing project? → No
# - Project name? → benchsight-dashboard
# - Directory? → ./
# - Override settings? → No

# 6. Add environment variables
# Go to: https://vercel.com/dashboard
# Select your project → Settings → Environment Variables
# Add:
#   NEXT_PUBLIC_SUPABASE_URL = https://your-project.supabase.co
#   NEXT_PUBLIC_SUPABASE_ANON_KEY = your-anon-key

# 7. Redeploy with environment variables
vercel --prod
```

### Option B: Using GitHub + Vercel Dashboard

```bash
# 1. Push to GitHub (if not already)
cd ui/dashboard
git init  # if not already a git repo
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/yourusername/benchsight-dashboard.git
git push -u origin main

# 2. Go to Vercel Dashboard
# https://vercel.com/new

# 3. Import from GitHub
# - Select your repository
# - Framework: Next.js (auto-detected)
# - Root Directory: ui/dashboard (or move dashboard to root)
# - Build Command: npm run build (auto)
# - Output Directory: .next (auto)

# 4. Add Environment Variables
# NEXT_PUBLIC_SUPABASE_URL = https://your-project.supabase.co
# NEXT_PUBLIC_SUPABASE_ANON_KEY = your-anon-key

# 5. Deploy!
# Click "Deploy"
```

**Your dashboard is now live!** 🎉

Visit: `https://benchsight-dashboard.vercel.app` (or your custom URL)

---

## Step 2: Deploy Tracker (5 minutes)

```bash
# 1. Navigate to tracker
cd ui/tracker

# 2. Deploy to Vercel
vercel

# Follow prompts:
# - Project name? → benchsight-tracker
# - Directory? → ./
# - Override settings? → No

# 3. If tracker needs Supabase connection, add env vars:
# NEXT_PUBLIC_SUPABASE_URL = https://your-project.supabase.co
# NEXT_PUBLIC_SUPABASE_ANON_KEY = your-anon-key

# 4. Deploy to production
vercel --prod
```

**Your tracker is now live!** 🎉

Visit: `https://benchsight-tracker.vercel.app`

---

## Step 3: Deploy Admin Portal Frontend (5 minutes)

```bash
# 1. Navigate to portal
cd ui/portal

# 2. Deploy to Vercel
vercel

# Follow prompts:
# - Project name? → benchsight-portal
# - Directory? → ./
# - Override settings? → No

# 3. Add environment variables (for future API connection):
# NEXT_PUBLIC_API_URL = https://your-api.railway.app (when backend is ready)
# NEXT_PUBLIC_SUPABASE_URL = https://your-project.supabase.co
# NEXT_PUBLIC_SUPABASE_ANON_KEY = your-anon-key

# 4. Deploy to production
vercel --prod
```

**Your portal UI is now live!** 🎉

Note: Buttons won't work until backend API is built (Step 4).

---

## Step 4: Build & Deploy Backend API (2-3 days)

### Create Backend Structure

```bash
# 1. Create API directory
mkdir api
cd api

# 2. Create FastAPI app
cat > main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BenchSight API")

# CORS for portal frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "BenchSight API"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}
EOF

# 3. Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
EOF
```

### Deploy to Railway

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add environment variables
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_SERVICE_KEY=your-service-key

# 5. Deploy
railway up
```

### Connect Portal to Backend

Update `ui/portal/index.html` to call your Railway API:

```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-api.railway.app';

// Example API call
async function triggerETL() {
  const response = await fetch(`${API_URL}/api/etl/trigger`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode: 'full' })
  });
  return response.json();
}
```

---

## Verification Checklist

After deployment, verify:

### Dashboard ✅
- [ ] Visit dashboard URL
- [ ] Check standings page loads
- [ ] Verify data from Supabase appears
- [ ] Test navigation between pages

### Tracker ✅
- [ ] Visit tracker URL
- [ ] Verify page loads
- [ ] Test Supabase connection (if applicable)

### Portal ✅
- [ ] Visit portal URL
- [ ] Verify UI loads
- [ ] Check that buttons show (even if not functional yet)

### Backend API ✅ (After Step 4)
- [ ] Visit API health endpoint
- [ ] Test ETL trigger from portal
- [ ] Verify status polling works

---

## Troubleshooting

### Build Errors

**Error:** `Module not found`
```bash
# Solution: Install dependencies
cd ui/dashboard
npm install
npm run build
```

**Error:** `TypeScript errors`
```bash
# Solution: Generate types from Supabase
npx supabase gen types typescript --project-id YOUR_PROJECT_ID > src/types/database.ts
```

### Environment Variables

**Error:** `NEXT_PUBLIC_SUPABASE_URL is not defined`
- Go to Vercel Dashboard → Project → Settings → Environment Variables
- Add the variable
- Redeploy: `vercel --prod`

### Supabase Connection

**Error:** `Failed to fetch` or connection errors
- Verify Supabase URL is correct
- Check anon key is correct
- Ensure Supabase project is active
- Check RLS (Row Level Security) policies if data doesn't load

---

## Custom Domains (Optional)

### Add Custom Domain to Dashboard

1. Go to Vercel Dashboard → Project → Settings → Domains
2. Add domain: `benchsight.noradhockey.com`
3. Follow DNS instructions
4. Wait for DNS propagation (5-60 minutes)

### Add Custom Domain to Tracker

Same process, different domain: `tracker.noradhockey.com`

---

## Cost Summary

| Service | Cost |
|--------|------|
| Vercel (Dashboard) | Free (hobby) |
| Vercel (Tracker) | Free (static) |
| Vercel (Portal) | Free (static) |
| Railway (Backend) | $5/month |
| Supabase | Free (hobby) |
| **Total** | **$5/month** |

---

## Next Steps After Deployment

1. **Monitor Performance**
   - Check Vercel Analytics
   - Monitor Supabase usage
   - Watch Railway logs

2. **Set Up Custom Domains**
   - Add custom domains for better branding
   - Configure SSL (automatic with Vercel)

3. **Add Monitoring**
   - Set up Sentry for error tracking
   - Configure Vercel Analytics
   - Set up uptime monitoring

4. **Optimize**
   - Enable Vercel caching
   - Optimize images
   - Add loading states

---

## Quick Reference

### Dashboard URLs
- Local: http://localhost:3000
- Production: https://benchsight-dashboard.vercel.app

### Tracker URLs
- Local: Open `ui/tracker/index.html` in browser
- Production: https://benchsight-tracker.vercel.app

### Portal URLs
- Local: Open `ui/portal/index.html` in browser
- Production: https://benchsight-portal.vercel.app

### API URLs (After Step 4)
- Production: https://your-api.railway.app

---

**You're done!** 🎉

All components are now live and accessible. The only remaining work is building the backend API for full portal functionality.

---

*Guide created: 2026-01-13*
