# Get Your Website Live - First Step

**The absolute first step to get BenchSight online**

## 🎯 Your First Step: Deploy Dashboard to Vercel

This will get your main website live in **10 minutes**.

---

## Step 1: Prepare (2 minutes)

### 1.1 Copy Portal Files

```bash
cd ui/dashboard
chmod +x scripts/setup-portal.sh
./scripts/setup-portal.sh
```

### 1.2 Test Build (Optional but Recommended)

```bash
cd ui/dashboard
npm install  # If you haven't already
npm run build
```

If the build succeeds, you're ready! If there are errors, fix them first.

---

## Step 2: Deploy to Vercel (5 minutes)

### Option A: Via Vercel Dashboard (EASIEST - Recommended)

1. **Go to Vercel:**
   - Visit https://vercel.com
   - Sign up or log in (free account works)

2. **Import Your Project:**
   - Click **"Add New..."** → **"Project"**
   - Click **"Import Git Repository"**
   - Connect GitHub (if not already)
   - Select your `benchsight` repository

3. **Configure Project:**
   - **Framework Preset:** Next.js (auto-detected)
   - **Root Directory:** Click "Edit" → Set to `ui/dashboard`
   - **Build Command:** `npm run build` (default - leave as is)
   - **Output Directory:** `.next` (default - leave as is)
   - **Install Command:** `npm install` (default - leave as is)

4. **Add Environment Variables:**
   - Click **"Environment Variables"**
   - Add these two (from your `config/config_local.ini`):
     ```
     NEXT_PUBLIC_SUPABASE_URL=https://uuaowslhpgyiudmbvqze.supabase.co
     NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1YW93c2xocGd5aXVkbWJ2cXplIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NTQ5ODcsImV4cCI6MjA4MjQzMDk4N30.9WjZcLzB555vKaiDeby8nYJ3Ce9L-SCkFrYH1Ts4ILU
     ```
   - Make sure to add them for **Production**, **Preview**, and **Development**

5. **Deploy:**
   - Click **"Deploy"**
   - Wait 2-3 minutes for build
   - **Done!** Your site is live at `https://your-project.vercel.app`

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to dashboard
cd ui/dashboard

# Login
vercel login

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No (first time)
# - Project name? benchsight-dashboard
# - Directory? ./ui/dashboard
# - Override settings? No

# Add environment variables
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY

# Deploy to production
vercel --prod
```

---

## Step 3: Configure Supabase Auth (3 minutes)

### 3.1 Enable Email Auth

1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Authentication** → **Providers**
4. Find **Email** and click **Enable**
5. Leave settings as default (or customize)

### 3.2 Add Redirect URLs

1. Go to **Authentication** → **URL Configuration**
2. Set **Site URL** to your Vercel URL:
   ```
   https://your-project.vercel.app
   ```
3. Add **Redirect URLs:**
   ```
   https://your-project.vercel.app/auth/callback
   https://your-project.vercel.app/**
   ```

### 3.3 Create Admin User

1. Go to **Authentication** → **Users**
2. Click **"Add User"** → **"Create New User"**
3. Enter:
   - **Email:** your-email@example.com
   - **Password:** (strong password)
   - **Auto Confirm User:** ✅ (check this)
4. Click **"Create User"**

---

## Step 4: Test Your Site (2 minutes)

1. **Visit your site:**
   - Go to `https://your-project.vercel.app`
   - You should see the dashboard!

2. **Test public pages:**
   - `/standings` - Should work without login
   - `/leaders` - Should work without login
   - `/players` - Should work without login

3. **Test login:**
   - Go to `/login`
   - Sign in with the admin user you created
   - Should redirect to dashboard

4. **Test protected routes:**
   - `/admin` - Should work when logged in
   - `/tracker` - Should work when logged in
   - Sign out and try again - should redirect to login

---

## ✅ You're Live!

Your website is now live at: `https://your-project.vercel.app`

### What Works Now:
- ✅ Public dashboard pages (standings, leaders, players, teams)
- ✅ Login system
- ✅ Protected admin portal
- ✅ Protected tracker
- ✅ All navigation

### What's Next (Optional):
- Deploy ETL API (for admin portal to trigger ETL jobs)
- Set up custom domain
- Add monitoring

---

## 🆘 Troubleshooting

### Build Fails
- Check Vercel build logs
- Verify `ui/dashboard` is the root directory
- Make sure all dependencies are in `package.json`

### Can't Login
- Check Supabase redirect URLs match your Vercel URL
- Verify environment variables are set correctly
- Check Supabase Auth is enabled

### Pages Show Errors
- Check browser console for errors
- Verify Supabase connection (test connection page)
- Check environment variables

### Portal Doesn't Load
- Run `./scripts/setup-portal.sh` to copy portal files
- Check `public/portal/index.html` exists

---

## 📚 Next Steps

After your site is live:

1. **Deploy ETL API** (optional - for admin portal):
   - See `api/DEPLOYMENT.md`
   - Deploy to Railway or Render

2. **Set Up Custom Domain** (optional):
   - Vercel Dashboard → Settings → Domains
   - Add your domain
   - Update Supabase redirect URLs

3. **Add Monitoring** (optional):
   - Enable Vercel Analytics
   - Set up Sentry for error tracking

---

## Quick Reference

**Your Supabase Credentials:**
- URL: `https://uuaowslhpgyiudmbvqze.supabase.co`
- Anon Key: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1YW93c2xocGd5aXVkbWJ2cXplIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NTQ5ODcsImV4cCI6MjA4MjQzMDk4N30.9WjZcLzB555vKaiDeby8nYJ3Ce9L-SCkFrYH1Ts4ILU`

**Vercel Dashboard:** https://vercel.com/dashboard  
**Supabase Dashboard:** https://supabase.com/dashboard

---

**That's it!** Your first step is deploying to Vercel. Everything else is optional.
