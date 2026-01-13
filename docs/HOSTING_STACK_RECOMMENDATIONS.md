# BenchSight Hosting Stack Recommendations

**Complete hosting strategy for Dashboard, Tracker, and Admin Portal**

Last Updated: 2026-01-13  
Version: 29.0

---

## Executive Summary

This document provides hosting recommendations for all three BenchSight components:
- **Dashboard** (Next.js 14)
- **Tracker** (HTML/JS)
- **Admin Portal** (HTML/JS + FastAPI backend)

---

## Recommended Stack (Production-Ready)

### Option 1: Unified Platform (Recommended for MVP)

**Best for:** Getting to production quickly, single vendor management, cost-effective scaling

| Component | Platform | Why |
|-----------|----------|-----|
| **Dashboard** | **Vercel** | Native Next.js support, zero-config deployment, free tier, excellent DX |
| **Tracker** | **Vercel** (Static) | Can host as static HTML/JS, same domain/CDN, free tier |
| **Admin Portal** | **Vercel** (Static) | Same as tracker, unified deployment |
| **Backend API** | **Railway** | Python/FastAPI support, easy Redis setup, $5/month starter |
| **Database** | **Supabase** | Already in use, PostgreSQL, real-time, free tier |
| **Storage** | **Cloudflare R2** | S3-compatible, no egress fees, $0.015/GB storage |

**Total Monthly Cost (MVP):** ~$5-10/month
- Vercel: Free (hobby tier)
- Railway: $5/month (starter)
- Supabase: Free tier
- Cloudflare R2: Pay-as-you-go (likely <$1/month initially)

**Pros:**
- ✅ Single deployment workflow for frontend
- ✅ Excellent developer experience
- ✅ Auto-scaling
- ✅ Built-in CDN
- ✅ Easy CI/CD integration

**Cons:**
- ⚠️ Multiple vendors to manage
- ⚠️ Railway pricing can scale up

---

### Option 2: All-in-One Platform

**Best for:** Simplified operations, single vendor, enterprise needs

| Component | Platform | Why |
|-----------|----------|-----|
| **Dashboard** | **Vercel** | Best Next.js hosting |
| **Tracker** | **Vercel** (Static) | Static hosting |
| **Admin Portal** | **Vercel** (Static) | Static hosting |
| **Backend API** | **Render** | Python support, free tier available, easier than Railway |
| **Database** | **Supabase** | Current choice |
| **Storage** | **Cloudflare R2** | Cost-effective |

**Alternative: AWS Amplify + Lambda**
- Dashboard: AWS Amplify (Next.js support)
- Tracker/Portal: Amplify Static Hosting
- Backend: AWS Lambda (serverless FastAPI)
- Database: Supabase (or RDS)
- Storage: S3

**Total Monthly Cost:** $0-20/month (depending on traffic)

**Pros:**
- ✅ AWS ecosystem integration
- ✅ Enterprise-grade reliability
- ✅ Extensive free tier
- ✅ Serverless scaling

**Cons:**
- ⚠️ More complex setup
- ⚠️ AWS learning curve
- ⚠️ Can get expensive at scale

---

### Option 3: Cost-Optimized (Free Tier Focus)

**Best for:** Early development, minimal budget, proof of concept

| Component | Platform | Why |
|-----------|----------|-----|
| **Dashboard** | **Vercel** | Free hobby tier |
| **Tracker** | **Netlify** | Free static hosting, 100GB bandwidth |
| **Admin Portal** | **Netlify** | Free static hosting |
| **Backend API** | **Render** | Free tier (spins down after inactivity) |
| **Database** | **Supabase** | Free tier (500MB, 2GB bandwidth) |
| **Storage** | **Supabase Storage** | Included in free tier (1GB) |

**Total Monthly Cost:** $0/month (free tiers)

**Pros:**
- ✅ Completely free
- ✅ Good for development/testing
- ✅ Easy to upgrade later

**Cons:**
- ⚠️ Render free tier spins down (cold starts)
- ⚠️ Limited bandwidth/storage
- ⚠️ Not suitable for production traffic

---

## Detailed Component Breakdown

### 1. Dashboard (Next.js 14)

#### Recommended: Vercel

**Why Vercel:**
- Native Next.js optimization
- Zero-config deployment
- Automatic HTTPS
- Global CDN
- Preview deployments
- Analytics included

**Deployment:**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd ui/dashboard
vercel

# Production deploy
vercel --prod
```

**Configuration:**
- Framework: Next.js
- Build Command: `npm run build`
- Output Directory: `.next`
- Environment Variables: Set in Vercel dashboard

**Cost:** Free (hobby) or $20/month (pro)

**Alternatives:**
- **Netlify**: Good Next.js support, free tier
- **AWS Amplify**: Enterprise option
- **Railway**: Can host Next.js but not optimized

---

### 2. Tracker (HTML/JS)

#### Recommended: Vercel Static Hosting

**Why Vercel:**
- Same platform as dashboard
- Unified deployment
- Free tier
- Global CDN
- Easy custom domain

**Deployment:**
```bash
# Option 1: Deploy as static site
cd ui/tracker
vercel

# Option 2: Include in dashboard monorepo
# Deploy tracker at /tracker route
```

**Configuration:**
- Framework: Other (Static)
- Build Command: None (or copy files)
- Output Directory: `ui/tracker`

**Cost:** Free (hobby tier)

**Alternatives:**
- **Netlify**: Excellent static hosting, free tier
- **Cloudflare Pages**: Free, fast CDN
- **GitHub Pages**: Free but limited features

---

### 3. Admin Portal (HTML/JS + FastAPI Backend)

#### Frontend: Vercel Static Hosting
#### Backend: Railway or Render

**Why This Split:**
- Frontend is static (HTML/JS)
- Backend needs Python runtime
- Separate scaling concerns

**Backend Options:**

##### Option A: Railway (Recommended)

**Why Railway:**
- Easy Python/FastAPI setup
- Built-in Redis support
- Simple deployment
- Good developer experience
- $5/month starter plan

**Deployment:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

**Configuration:**
- Runtime: Python 3.11+
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment Variables: Set in Railway dashboard

**Cost:** $5/month (starter) or $20/month (pro)

##### Option B: Render

**Why Render:**
- Free tier available
- Easy setup
- Auto-deploy from GitHub
- Built-in SSL

**Deployment:**
1. Connect GitHub repo
2. Select "Web Service"
3. Choose Python environment
4. Set build/start commands

**Cost:** Free (spins down) or $7/month (always-on)

##### Option C: Fly.io

**Why Fly.io:**
- Generous free tier
- Global edge deployment
- Good for low traffic

**Cost:** Free tier (3 shared VMs)

---

### 4. Database (Supabase)

**Current Choice:** Supabase (PostgreSQL)

**Why Supabase:**
- Already integrated
- Free tier: 500MB database, 2GB bandwidth
- Real-time subscriptions
- Built-in auth (for future)
- Auto-scaling

**Cost:** Free (hobby) or $25/month (pro)

**Alternatives:**
- **Neon**: Serverless Postgres, free tier
- **Railway Postgres**: $5/month, simple setup
- **AWS RDS**: Enterprise option

---

### 5. Storage (Video/Media)

#### Recommended: Cloudflare R2

**Why Cloudflare R2:**
- S3-compatible API
- No egress fees (unlike S3)
- $0.015/GB storage
- Fast global access
- Free tier: 10GB storage, 1M Class A operations

**Cost:** ~$0-5/month (depending on usage)

**Alternatives:**
- **Supabase Storage**: Included in free tier (1GB), then $0.021/GB
- **AWS S3**: Standard option, egress fees apply
- **Backblaze B2**: Cheap storage, S3-compatible

---

## Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
└───────────────┬─────────────────────────────────────────────┘
                │
                ├─────────────────┬─────────────────┬──────────┐
                ▼                 ▼                 ▼          ▼
    ┌───────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐
    │   Dashboard   │  │   Tracker    │  │ Admin Portal │  │   API    │
    │   (Vercel)    │  │   (Vercel)   │  │   (Vercel)   │  │ (Railway)│
    │  Next.js 14   │  │  Static HTML │  │  Static HTML │  │ FastAPI  │
    └───────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────┬─────┘
            │                 │                 │              │
            └─────────────────┴─────────────────┴──────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │    Supabase     │
                    │  (PostgreSQL)   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Cloudflare R2  │
                    │  (Video Storage) │
                    └─────────────────┘
```

---

## Deployment Workflow

### Initial Setup

1. **Dashboard**
   ```bash
   cd ui/dashboard
   vercel login
   vercel
   ```

2. **Tracker**
   ```bash
   cd ui/tracker
   vercel
   ```

3. **Admin Portal Frontend**
   ```bash
   cd ui/portal
   vercel
   ```

4. **Backend API**
   ```bash
   cd api
   railway login
   railway init
   railway up
   ```

### CI/CD Integration

**GitHub Actions Example:**
```yaml
name: Deploy Dashboard
on:
  push:
    branches: [main]
    paths:
      - 'ui/dashboard/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: cd ui/dashboard && npm install && npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

---

## Environment Variables

### Dashboard (Vercel)
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
```

### Tracker (Vercel)
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
```

### Admin Portal (Vercel)
```
NEXT_PUBLIC_API_URL=https://api.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
```

### Backend API (Railway)
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
API_KEY=xxx
```

---

## Cost Breakdown (Monthly)

### MVP/Development (Free Tier)
- Vercel: $0 (hobby)
- Railway: $0 (free tier, spins down)
- Supabase: $0 (free tier)
- Cloudflare R2: $0 (10GB free)
- **Total: $0/month**

### Small Production (~1000 users)
- Vercel: $0 (hobby) or $20 (pro)
- Railway: $5 (starter)
- Supabase: $0 (free tier) or $25 (pro)
- Cloudflare R2: ~$2 (100GB storage)
- **Total: $7-47/month**

### Medium Production (~10,000 users)
- Vercel: $20 (pro)
- Railway: $20 (pro)
- Supabase: $25 (pro)
- Cloudflare R2: ~$10 (500GB storage)
- **Total: $75/month**

### Large Production (~100,000 users)
- Vercel: $20 (pro) or Enterprise
- Railway: $100+ (scale)
- Supabase: $25 (pro) or Enterprise
- Cloudflare R2: ~$50 (2TB storage)
- **Total: $95-200+/month**

---

## Migration Path

### Phase 1: MVP (Current)
- Dashboard: Vercel (free)
- Tracker: Vercel (free)
- Portal: Vercel (free)
- API: Render (free tier, spins down)
- Database: Supabase (free)
- **Cost: $0/month**

### Phase 2: Early Production
- Upgrade API to Railway ($5/month)
- Upgrade Supabase if needed ($25/month)
- **Cost: $30/month**

### Phase 3: Growth
- Upgrade Vercel to Pro ($20/month)
- Scale Railway as needed
- Add Cloudflare R2 for videos
- **Cost: $50-100/month**

---

## Security Considerations

### All Platforms
- ✅ HTTPS enforced (automatic)
- ✅ Environment variables encrypted
- ✅ DDoS protection (built-in)
- ✅ Regular security updates

### Additional Recommendations
- Use Supabase Auth for portal authentication
- Implement API rate limiting
- Use API keys for backend access
- Enable CORS properly
- Regular dependency updates

---

## Monitoring & Analytics

### Recommended Tools
- **Vercel Analytics**: Built-in, free
- **Sentry**: Error tracking (free tier)
- **Supabase Dashboard**: Database monitoring
- **Railway Metrics**: Built-in monitoring

---

## Recommendation Summary

**For MVP/Development:**
✅ **Option 3 (Free Tier Focus)**
- Vercel (Dashboard, Tracker, Portal)
- Render (Backend API - free tier)
- Supabase (Database - free tier)
- **Cost: $0/month**

**For Production:**
✅ **Option 1 (Unified Platform)**
- Vercel (all frontends)
- Railway (Backend API)
- Supabase (Database)
- Cloudflare R2 (Storage)
- **Cost: $5-30/month**

**For Enterprise:**
✅ **Option 2 (AWS Amplify + Lambda)**
- AWS ecosystem
- Enterprise support
- Advanced features
- **Cost: $50-200+/month**

---

## ⚠️ Important: ML/CV Architecture (Future)

**Vercel cannot host ML/CV workloads.** For future ML/CV integration (Phase 3), use **hybrid architecture**:

### Hybrid ML/CV Stack (Phase 3+)

| Component | Platform | Why |
|-----------|----------|-----|
| **Frontend** | **Vercel** | ✅ Current - Keep this |
| **ML/CV Service** | **Replicate** (MVP) or **RunPod** (Custom) | GPU access, video processing |
| **Video Storage** | **Cloudflare R2** | No egress fees, S3-compatible |
| **API Gateway** | **Railway** | Routes requests to ML service |

**Architecture Pattern:**
```
Frontend (Vercel) → API Gateway (Railway) → ML Service (Replicate/RunPod) → Video Storage (R2)
```

**See:** `docs/ML_CV_ARCHITECTURE_PLAN.md` for detailed planning

**Cost (with ML):** $5/month (base) + $0-200/month (ML service)

---

## Next Steps

1. **Choose your stack** based on budget and needs
2. **Set up accounts** on chosen platforms
3. **Deploy Dashboard** to Vercel
4. **Deploy Tracker** to Vercel
5. **Deploy Admin Portal** frontend to Vercel
6. **Deploy Backend API** to Railway/Render
7. **Configure environment variables**
8. **Set up custom domains** (optional)
9. **Enable monitoring** and analytics
10. **Test end-to-end** workflow

---

## Support & Resources

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Cloudflare R2 Docs**: https://developers.cloudflare.com/r2

---

*Last Updated: 2026-01-13*
