# 🚀 Deploy to Vercel - Web Dashboard Guide

**Step-by-step guide using Vercel's web interface (no CLI needed!)**

---

## Step 1: Push to GitHub (If Not Already Done)

### Check if you have a GitHub repo

1. **Do you already have this code on GitHub?**
   - ✅ Yes → Skip to Step 2
   - ❌ No → Follow steps below

### Create GitHub Repository

1. Go to: https://github.com/new
2. **Repository name:** `benchsight` (or your preferred name)
3. **Visibility:** Public or Private (your choice)
4. **Don't** initialize with README (we already have code)
5. Click **"Create repository"**

### Push Your Code

```bash
# In your project directory
cd /Users/ronniepinnell/Documents/Documents\ -\ Ronnie\'s\ MacBook\ Pro\ -\ 1/Programming_HD/Hockey/Benchsight/git/benchsight

# Check if git is initialized
git status

# If not initialized, run:
git init
git add .
git commit -m "Ready for Vercel deployment"

# Add your GitHub repo
git remote add origin https://github.com/YOUR_USERNAME/benchsight.git

# Push to GitHub
git push -u origin main
```

**Replace `YOUR_USERNAME` with your GitHub username!**

---

## Step 2: Deploy Dashboard to Vercel

### 2.1: Sign Up / Login to Vercel

1. Go to: https://vercel.com/signup
2. Click **"Continue with GitHub"** (easiest)
3. Authorize Vercel to access your GitHub

### 2.2: Import Your Repository

1. After logging in, click **"Add New..."** → **"Project"**
2. You'll see your GitHub repositories
3. Find **"benchsight"** (or your repo name)
4. Click **"Import"**

### 2.3: Configure Dashboard Project

**Important settings:**

1. **Project Name:** `benchsight-dashboard` (or your choice)
2. **Framework Preset:** Should auto-detect **Next.js** ✅
3. **Root Directory:** 
   - Click **"Edit"** next to Root Directory
   - Enter: `ui/dashboard`
   - Click **"Continue"**
4. **Build Settings:**
   - Build Command: `npm run build` (should auto-fill) ✅
   - Output Directory: `.next` (should auto-fill) ✅
   - Install Command: `npm install` (should auto-fill) ✅

5. Click **"Deploy"** 🚀

### 2.4: Wait for Deployment

- Vercel will build and deploy your dashboard
- This takes 1-2 minutes
- You'll see progress in real-time
- ✅ Success when you see "Ready" status

---

## Step 3: Add Environment Variables (Important!)

### 3.1: Get Your Supabase Credentials

If you don't have them handy:

1. Go to: https://supabase.com/dashboard
2. Select your BenchSight project
3. Click **Settings** (gear icon ⚙️) → **API**
4. Copy:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public** key (long string starting with `eyJ...`)

### 3.2: Add to Vercel

1. In Vercel, go to your **benchsight-dashboard** project
2. Click **Settings** (top menu)
3. Click **Environment Variables** (left sidebar)
4. Add these two variables:

   **Variable 1:**
   - **Name:** `NEXT_PUBLIC_SUPABASE_URL`
   - **Value:** `https://your-project-id.supabase.co` (paste your URL)
   - **Environment:** Select all (Production, Preview, Development)
   - Click **"Save"**

   **Variable 2:**
   - **Name:** `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **Value:** `your-anon-key-here` (paste your key)
   - **Environment:** Select all (Production, Preview, Development)
   - Click **"Save"**

### 3.3: Redeploy with Environment Variables

1. Go to **Deployments** tab (top menu)
2. Click the **"..."** (three dots) on the latest deployment
3. Click **"Redeploy"**
4. Confirm redeploy
5. Wait for it to finish (~1 minute)

---

## Step 4: Verify Dashboard Works

1. Click on your deployment URL (looks like: `benchsight-dashboard.vercel.app`)
2. Test these pages:
   - ✅ Homepage loads
   - ✅ `/standings` page shows data
   - ✅ `/leaders` page works
   - ✅ Data from Supabase appears

**🎉 Your dashboard is live!**

---

## Step 5: Deploy Tracker

### 5.1: Create New Project for Tracker

1. In Vercel dashboard, click **"Add New..."** → **"Project"**
2. Select the same **"benchsight"** repository
3. Click **"Import"**

### 5.2: Configure Tracker Project

1. **Project Name:** `benchsight-tracker`
2. **Framework Preset:** 
   - Click dropdown
   - Select **"Other"** (it's static HTML)
3. **Root Directory:**
   - Click **"Edit"**
   - Enter: `ui/tracker`
   - Click **"Continue"**
4. **Build Settings:**
   - Build Command: Leave empty or delete
   - Output Directory: `.` (just a dot)
   - Install Command: Leave empty

5. Click **"Deploy"**

### 5.3: Wait for Deployment

- Should deploy quickly (it's just static files)
- ✅ Success when you see "Ready"

### 5.4: Add Environment Variables (If Tracker Uses Supabase)

If your tracker connects to Supabase:

1. Go to **Settings** → **Environment Variables**
2. Add the same two variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
3. **Redeploy**

---

## Step 6: Test Everything

### Dashboard ✅
- Visit: `https://benchsight-dashboard.vercel.app`
- [ ] Homepage loads
- [ ] Standings page shows data
- [ ] Leaders page works
- [ ] Navigation works

### Tracker ✅
- Visit: `https://benchsight-tracker.vercel.app`
- [ ] Page loads
- [ ] UI displays correctly
- [ ] Supabase connection works (if applicable)

---

## Troubleshooting

### "Build Failed"

**Check:**
1. Root directory is correct (`ui/dashboard` or `ui/tracker`)
2. Build command is correct (`npm run build` for dashboard)
3. Check build logs in Vercel dashboard

**Fix:**
- Go to **Deployments** → Click failed deployment → Check **"Build Logs"**
- Look for error messages
- Common issues:
  - Missing dependencies → Add to package.json
  - TypeScript errors → Fix before deploying
  - Missing environment variables → Add them

### "Environment Variables Not Working"

**Check:**
1. Variable names match exactly (case-sensitive)
2. Variables are set for correct environment (Production/Preview/Development)
3. You redeployed after adding variables

**Fix:**
- Double-check variable names
- Make sure you selected all environments when adding
- Redeploy after adding variables

### "Can't Connect to Supabase"

**Check:**
1. Supabase URL is correct (no extra spaces)
2. Anon key is correct (complete, no truncation)
3. Supabase project is active
4. RLS policies allow public access

**Fix:**
- Copy credentials directly from Supabase dashboard
- Verify project is not paused
- Check Supabase logs for connection attempts

### "Page Shows But No Data"

**Check:**
1. Environment variables are set correctly
2. Supabase tables/views exist
3. RLS policies allow access

**Fix:**
- Verify environment variables in Vercel
- Test Supabase connection locally first
- Check Supabase dashboard for data

---

## Next Steps After Deployment

### 1. Custom Domains (Optional)

1. Go to project → **Settings** → **Domains**
2. Add your domain:
   - Dashboard: `benchsight.noradhockey.com`
   - Tracker: `tracker.noradhockey.com`
3. Follow DNS instructions
4. Wait for DNS propagation (5-60 minutes)

### 2. Monitor Performance

- Check **Analytics** tab in Vercel
- Monitor Supabase usage
- Set up alerts if needed

### 3. Share Your URLs

- Dashboard: `https://benchsight-dashboard.vercel.app`
- Tracker: `https://benchsight-tracker.vercel.app`

---

## Quick Reference

### Dashboard URL
`https://benchsight-dashboard.vercel.app`

### Tracker URL
`https://benchsight-tracker.vercel.app`

### Vercel Dashboard
https://vercel.com/dashboard

### Environment Variables Needed
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

---

## Checklist

### Dashboard Deployment
- [ ] Pushed code to GitHub
- [ ] Created Vercel account
- [ ] Imported repository
- [ ] Set root directory to `ui/dashboard`
- [ ] Configured build settings
- [ ] Deployed successfully
- [ ] Added environment variables
- [ ] Redeployed with env vars
- [ ] Tested dashboard works

### Tracker Deployment
- [ ] Created new Vercel project
- [ ] Set root directory to `ui/tracker`
- [ ] Configured as static site
- [ ] Deployed successfully
- [ ] Added environment variables (if needed)
- [ ] Tested tracker works

---

**You're all set! Both dashboard and tracker are now live on Vercel!** 🎉

---

*Guide created: 2026-01-13*
