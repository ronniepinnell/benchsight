# Deployment Steps - Dashboard & Tracker

**Follow these steps to deploy to Vercel**

---

## Prerequisites

1. ✅ Vercel account: https://vercel.com/signup (free)
2. ✅ Vercel CLI installed: `npm i -g vercel`
3. ✅ Supabase credentials ready

---

## Step 1: Deploy Dashboard

```bash
# Navigate to dashboard
cd ui/dashboard

# Login to Vercel (if not already)
vercel login

# Deploy
vercel

# Follow the prompts:
# - Set up and deploy? → Yes
# - Which scope? → Your account
# - Link to existing project? → No
# - Project name? → benchsight-dashboard
# - Directory? → ./
# - Override settings? → No
```

### Add Environment Variables

After deployment, add your Supabase credentials:

1. Go to: https://vercel.com/dashboard
2. Select your project: `benchsight-dashboard`
3. Go to: **Settings** → **Environment Variables**
4. Add these variables:

```
NEXT_PUBLIC_SUPABASE_URL = https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = your-anon-key-here
```

5. **Redeploy** to apply environment variables:
```bash
vercel --prod
```

**Your dashboard is now live!** 🎉

Visit: `https://benchsight-dashboard.vercel.app`

---

## Step 2: Deploy Tracker

```bash
# Navigate to tracker
cd ui/tracker

# Deploy to Vercel
vercel

# Follow the prompts:
# - Set up and deploy? → Yes
# - Which scope? → Your account
# - Link to existing project? → No
# - Project name? → benchsight-tracker
# - Directory? → ./
# - Override settings? → No
```

### Add Environment Variables (if tracker needs Supabase)

If your tracker uses Supabase, add the same environment variables:

1. Go to: https://vercel.com/dashboard
2. Select your project: `benchsight-tracker`
3. Go to: **Settings** → **Environment Variables**
4. Add:

```
NEXT_PUBLIC_SUPABASE_URL = https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = your-anon-key-here
```

5. **Redeploy**:
```bash
vercel --prod
```

**Your tracker is now live!** 🎉

Visit: `https://benchsight-tracker.vercel.app`

---

## Quick Deploy Script

You can also use this one-liner to deploy both:

```bash
# Deploy Dashboard
cd ui/dashboard && vercel --prod && cd ../..

# Deploy Tracker  
cd ui/tracker && vercel --prod && cd ../..
```

---

## Verification

After deployment, verify:

### Dashboard ✅
- [ ] Visit dashboard URL
- [ ] Check standings page loads
- [ ] Verify data appears from Supabase
- [ ] Test navigation

### Tracker ✅
- [ ] Visit tracker URL
- [ ] Verify page loads
- [ ] Test Supabase connection (if applicable)

---

## Troubleshooting

### Build Errors
- Make sure you're in the correct directory
- Run `npm install` if dependencies are missing
- Check that `.env.local` exists (for local dev only)

### Environment Variables Not Working
- Make sure you added them in Vercel dashboard
- Redeploy after adding variables: `vercel --prod`
- Check variable names match exactly (case-sensitive)

### Supabase Connection Issues
- Verify Supabase URL is correct
- Check anon key is correct
- Ensure Supabase project is active
- Check RLS policies if data doesn't load

---

## Next Steps

1. **Set up custom domains** (optional)
   - Dashboard: `benchsight.noradhockey.com`
   - Tracker: `tracker.noradhockey.com`

2. **Monitor performance**
   - Check Vercel Analytics
   - Monitor Supabase usage

3. **Deploy Admin Portal** (when backend is ready)
   - Same process as tracker
   - Connect to backend API

---

**You're done!** Both dashboard and tracker are now live! 🚀
