# Production Setup Guide

Complete step-by-step guide to deploy BenchSight to production.

## Overview

This guide covers deploying:
1. **Dashboard** → Vercel
2. **ETL API** → Railway (recommended) or Render
3. **Supabase** → Already configured
4. **Authentication** → Supabase Auth

## Prerequisites

- [ ] GitHub repository with all code
- [ ] Vercel account (free tier works)
- [ ] Railway account ($5/month) or Render account (free tier)
- [ ] Supabase project with database
- [ ] Domain name (optional, but recommended)

---

## Step 1: Prepare Code for Production

### 1.1 Copy Portal Files

```bash
cd ui/dashboard
./scripts/setup-portal.sh
```

This ensures portal files are in `public/portal/` for deployment.

### 1.2 Test Build Locally

```bash
# Test dashboard build
cd ui/dashboard
npm run build

# Test API (optional)
cd ../../api
python -m uvicorn api.main:app --port 8000
```

Fix any build errors before deploying.

---

## Step 2: Deploy Dashboard to Vercel

### 2.1 Connect Repository

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure project:
   - **Framework Preset:** Next.js
   - **Root Directory:** `ui/dashboard`
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)

### 2.2 Set Environment Variables

In Vercel Dashboard → Settings → Environment Variables, add:

```bash
# Required
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Optional (for admin portal)
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

**Important:** Add these for **Production**, **Preview**, and **Development** environments.

### 2.3 Deploy

Click **Deploy** or push to main branch.

Your dashboard will be live at: `https://your-project.vercel.app`

### 2.4 Verify Deployment

1. Visit your Vercel URL
2. Test login: `/login`
3. Test protected routes: `/admin`, `/tracker`
4. Check all pages load correctly

---

## Step 3: Deploy ETL API to Railway

### 3.1 Install Railway CLI

```bash
npm i -g @railway/cli
```

### 3.2 Login and Initialize

```bash
cd api
railway login
railway init
```

Follow prompts:
- **Project name:** benchsight-api
- **Environment:** Production

### 3.3 Set Environment Variables

In Railway Dashboard → Variables, add:

```bash
# Required
ENVIRONMENT=production
CORS_ORIGINS=https://your-dashboard.vercel.app

# Supabase (if API needs direct access)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
```

**Note:** Replace `your-dashboard.vercel.app` with your actual Vercel URL.

### 3.4 Configure Build

Railway auto-detects Python. Verify settings:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### 3.5 Deploy

```bash
railway up
```

Or Railway will auto-deploy on git push if connected.

### 3.6 Get API URL

Railway provides a URL like: `https://benchsight-api.railway.app`

**Update Vercel environment variable:**
```
NEXT_PUBLIC_API_URL=https://benchsight-api.railway.app
```

Redeploy dashboard to pick up the new API URL.

---

## Step 4: Configure Supabase Auth

### 4.1 Enable Email Auth

1. Go to Supabase Dashboard → **Authentication** → **Providers**
2. Enable **Email** provider
3. Configure:
   - **Enable email signup:** ✅ (or disable for admin-only)
   - **Confirm email:** Optional (recommended for production)

### 4.2 Add Redirect URLs

1. Go to **Authentication** → **URL Configuration**
2. Set **Site URL:** `https://your-dashboard.vercel.app`
3. Add **Redirect URLs:**
   ```
   https://your-dashboard.vercel.app/auth/callback
   https://your-dashboard.vercel.app/**
   ```

### 4.3 Create Admin Users

**Option A: Via Dashboard**
1. **Authentication** → **Users** → **Add User**
2. Enter email and password
3. Check **Auto Confirm User** (skip email confirmation)

**Option B: Via SQL**
```sql
-- Create admin user
INSERT INTO auth.users (
  instance_id,
  id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at,
  raw_app_meta_data,
  raw_user_meta_data
) VALUES (
  '00000000-0000-0000-0000-000000000000',
  gen_random_uuid(),
  'authenticated',
  'authenticated',
  'admin@example.com',
  crypt('your-secure-password', gen_salt('bf')),
  now(),
  now(),
  now(),
  '{"provider": "email", "providers": ["email"]}',
  '{"role": "admin"}'
);
```

---

## Step 5: Test Production Setup

### 5.1 Test Authentication

1. Visit: `https://your-dashboard.vercel.app/login`
2. Sign in with admin credentials
3. Verify redirect to dashboard
4. Test accessing `/admin` and `/tracker`

### 5.2 Test Admin Portal

1. Go to `/admin`
2. Check API connection status
3. Try triggering a test ETL job (if configured)
4. Verify API logs in Railway dashboard

### 5.3 Test Tracker

1. Go to `/tracker`
2. Select a game
3. Verify Supabase connection
4. Test saving events

### 5.4 Test Public Pages

1. Visit `/standings`, `/leaders`, `/players`
2. Verify all load correctly
3. Check data displays properly

---

## Step 6: Production Optimizations

### 6.1 Enable Vercel Analytics

1. Vercel Dashboard → **Analytics**
2. Enable **Web Analytics** (free tier available)

### 6.2 Set Up Custom Domain (Optional)

1. Vercel Dashboard → **Settings** → **Domains**
2. Add your domain
3. Follow DNS configuration instructions
4. Update Supabase redirect URLs to include custom domain

### 6.3 Configure Error Tracking (Optional)

**Sentry Setup:**
```bash
cd ui/dashboard
npm install @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
```

Add to Vercel environment variables:
```
SENTRY_DSN=your-sentry-dsn
```

### 6.4 Set Up Monitoring

**Railway:**
- Built-in metrics in dashboard
- Set up alerts for downtime

**Vercel:**
- Built-in analytics
- Set up uptime monitoring (optional)

---

## Step 7: Security Checklist

- [ ] Environment variables set in Vercel (not in code)
- [ ] Environment variables set in Railway
- [ ] Supabase RLS policies configured
- [ ] Auth redirect URLs match production domain
- [ ] HTTPS enabled (automatic on Vercel/Railway)
- [ ] CORS configured correctly in API
- [ ] Admin users created
- [ ] Strong passwords for admin accounts
- [ ] API keys stored securely (not in git)

---

## Step 8: Backup Strategy

### 8.1 Supabase Backups

1. Go to Supabase Dashboard → **Settings** → **Database**
2. Enable **Point-in-time Recovery** (Pro plan)
3. Or set up manual backups

### 8.2 Code Backups

- Code is in GitHub (already backed up)
- Consider GitHub Actions for automated deployments

---

## Environment Variables Reference

### Vercel (Dashboard)

```bash
# Required
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Optional
NEXT_PUBLIC_API_URL=https://xxx.railway.app
```

### Railway (ETL API)

```bash
# Required
ENVIRONMENT=production
CORS_ORIGINS=https://your-dashboard.vercel.app

# Optional
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
```

---

## Troubleshooting

### Dashboard Not Loading

1. Check Vercel build logs
2. Verify environment variables are set
3. Check browser console for errors
4. Verify Supabase connection

### API Not Responding

1. Check Railway logs
2. Verify CORS origins include dashboard URL
3. Test API directly: `curl https://your-api.railway.app/api/health`
4. Check environment variables

### Auth Not Working

1. Verify Supabase redirect URLs match Vercel URL
2. Check environment variables
3. Clear browser cookies
4. Check Supabase Auth logs

### Portal Can't Connect to API

1. Verify `NEXT_PUBLIC_API_URL` is set in Vercel
2. Check CORS configuration in API
3. Test API endpoint directly
4. Check browser console for CORS errors

---

## Cost Summary

### Monthly Costs

| Service | Cost |
|---------|------|
| Vercel (Hobby) | $0/month |
| Railway (Starter) | $5/month |
| Supabase (Free) | $0/month |
| **Total** | **$5/month** |

### Optional Upgrades

- Vercel Pro: +$20/month (better analytics, more bandwidth)
- Supabase Pro: +$25/month (more database space, backups)
- Custom Domain: ~$12/year

---

## Next Steps

1. ✅ Deploy dashboard to Vercel
2. ✅ Deploy API to Railway
3. ✅ Configure Supabase Auth
4. ✅ Test everything
5. ⏳ Set up monitoring
6. ⏳ Add custom domain
7. ⏳ Set up backups

---

## Support

- **Vercel Docs:** https://vercel.com/docs
- **Railway Docs:** https://docs.railway.app
- **Supabase Docs:** https://supabase.com/docs
- **Deployment Issues:** Check logs in respective dashboards

---

## Quick Reference

**Dashboard URL:** `https://your-project.vercel.app`  
**API URL:** `https://your-api.railway.app`  
**API Docs:** `https://your-api.railway.app/docs`  
**Supabase Dashboard:** https://supabase.com/dashboard

---

*Last Updated: 2026-01-13*
