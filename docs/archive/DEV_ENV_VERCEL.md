# Vercel Development Environment Setup

**Complete guide for setting up Vercel for dashboard development and deployment**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This guide covers setting up Vercel for the BenchSight dashboard, including local development and production deployment.

**Vercel Role:** Dashboard hosting and deployment  
**Dashboard Location:** `ui/dashboard/`  
**Framework:** Next.js 14

---

## Prerequisites

- Node.js 18+ or 20+ installed
- GitHub account
- Vercel account (free tier available)

---

## Step 1: Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up"
3. Sign up with GitHub (recommended)
4. Authorize Vercel to access your repositories

---

## Step 2: Install Vercel CLI

```bash
npm install -g vercel
vercel --version
```

---

## Step 3: Local Vercel Development

### Initialize Vercel in Project

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

### Start Local Dev Server

```bash
vercel dev
```

**Access:**
- Local: `http://localhost:3000`
- Vercel preview: `https://benchsight-dashboard-xxxxx.vercel.app`

---

## Step 4: Deploy to Vercel

### Option 1: Deploy from CLI

```bash
cd ui/dashboard
vercel --prod
```

### Option 2: Deploy from GitHub

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

---

## Step 5: Configure Environment Variables

### In Vercel Dashboard

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

### In Local `.env.local`

**Create `ui/dashboard/.env.local`:**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Step 6: Configure Build Settings

### Vercel Configuration

**Create `ui/dashboard/vercel.json` (optional):**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "installCommand": "npm install"
}
```

### Next.js Configuration

**`ui/dashboard/next.config.js` already configured:**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configuration
}

module.exports = nextConfig
```

---

## Step 7: Domain Setup (Optional)

### Add Custom Domain

1. Go to Project Settings → Domains
2. Add domain: `dashboard.benchsight.com`
3. Follow DNS configuration instructions
4. Wait for DNS propagation (up to 24 hours)

---

## Deployment Workflow

### Automatic Deployments

**Vercel automatically deploys:**
- Push to `main` branch → Production deployment
- Push to other branches → Preview deployment
- Pull requests → Preview deployment

### Manual Deployment

```bash
cd ui/dashboard
vercel --prod
```

### Preview Deployment

```bash
vercel
```

---

## Local Development Workflow

### Standard Development

```bash
cd ui/dashboard
npm run dev
# Access at http://localhost:3000
```

### Vercel Dev (Recommended)

```bash
cd ui/dashboard
vercel dev
# Access at http://localhost:3000
# Uses Vercel's environment and routing
```

---

## Troubleshooting

### Build Failures

**Problem:** Build fails on Vercel  
**Solution:**
- Check build logs in Vercel dashboard
- Verify Node.js version (should be 18+)
- Check for TypeScript errors
- Verify environment variables

**Problem:** Missing environment variables  
**Solution:**
- Add variables in Vercel dashboard
- Redeploy after adding variables

### Deployment Issues

**Problem:** Deployment takes too long  
**Solution:**
- Check build logs
- Optimize build (reduce dependencies)
- Use Vercel's build cache

**Problem:** Preview URL not working  
**Solution:**
- Check deployment status
- Verify environment variables
- Check build logs

### Local Development Issues

**Problem:** `vercel dev` fails  
**Solution:**
- Run `vercel login` first
- Verify project is linked: `vercel link`
- Check `.vercel` directory exists

**Problem:** Environment variables not loading  
**Solution:**
- Use `.env.local` for local development
- Run `vercel dev` to use Vercel's env vars

---

## Performance Optimization

### Build Optimization

**Next.js automatically optimizes:**
- Code splitting
- Image optimization
- Static generation
- Server components

### Vercel Features

**Automatic:**
- Edge caching
- CDN distribution
- Automatic HTTPS
- Analytics

---

## Related Documentation

- [DEV_ENV_COMPLETE.md](DEV_ENV_COMPLETE.md) - Complete dev environment guide
- [DEV_ENV_SUPABASE.md](DEV_ENV_SUPABASE.md) - Supabase setup
- [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md) - Production deployment
- [QUICK_DEPLOYMENT_GUIDE.md](../deployment/QUICK_DEPLOYMENT_GUIDE.md) - Quick deployment guide

---

*Last Updated: 2026-01-15*
