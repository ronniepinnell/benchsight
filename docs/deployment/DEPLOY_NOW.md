# 🚀 Deploy to Vercel - Ready Now!

**Your dashboard and tracker are ready to deploy!**

---

## Quick Start (2 Options)

### ✅ Option 1: Web Dashboard (Easiest - Recommended)

**No CLI needed!**

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Ready for Vercel deployment"
   git push
   ```

2. **Deploy Dashboard:**
   - Go to: https://vercel.com/new
   - Import your GitHub repo
   - **Root Directory**: `ui/dashboard`
   - Click **Deploy**

3. **Add Environment Variables:**
   - Go to project → Settings → Environment Variables
   - Add:
     ```
     NEXT_PUBLIC_SUPABASE_URL = https://your-project.supabase.co
     NEXT_PUBLIC_SUPABASE_ANON_KEY = your-anon-key
     ```
   - Redeploy

4. **Deploy Tracker:**
   - Go to: https://vercel.com/new
   - Import same repo
   - **Root Directory**: `ui/tracker`
   - Click **Deploy**

---

### ✅ Option 2: CLI (Using npx - No Install)

**No installation needed! npx comes with Node.js**

#### Deploy Dashboard

```bash
cd ui/dashboard
npx vercel
```

**Answer the prompts:**
- Set up and deploy? → **Yes**
- Which scope? → **Your account** (or create one)
- Link to existing project? → **No**
- Project name? → **benchsight-dashboard**
- Directory? → **./** (press Enter)
- Override settings? → **No**

#### Add Environment Variables

After first deployment:

1. Go to: https://vercel.com/dashboard
2. Click on **benchsight-dashboard**
3. **Settings** → **Environment Variables**
4. Add:
   - `NEXT_PUBLIC_SUPABASE_URL` = `https://your-project.supabase.co`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = `your-anon-key`
5. **Redeploy:**
   ```bash
   npx vercel --prod
   ```

#### Deploy Tracker

```bash
cd ui/tracker
npx vercel
```

**Answer the prompts:**
- Project name? → **benchsight-tracker**
- Directory? → **./**

---

## Get Your Supabase Credentials

If you need them:

1. Go to: https://supabase.com/dashboard
2. Select your BenchSight project
3. **Settings** (⚙️) → **API**
4. Copy:
   - **Project URL** → Use for `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public** key → Use for `NEXT_PUBLIC_SUPABASE_ANON_KEY`

---

## What I've Prepared

✅ **Fixed build errors** - Dashboard builds successfully  
✅ **Created vercel.json** - Configuration files ready  
✅ **Created deploy scripts** - Easy deployment helpers  
✅ **TypeScript errors fixed** - Ready for production  

---

## Verification Checklist

After deployment:

### Dashboard ✅
- [ ] Visit: `https://benchsight-dashboard.vercel.app`
- [ ] Check: Standings page loads
- [ ] Verify: Data from Supabase appears
- [ ] Test: Navigation works

### Tracker ✅
- [ ] Visit: `https://benchsight-tracker.vercel.app`
- [ ] Check: Page loads correctly
- [ ] Test: Supabase connection (if applicable)

---

## Troubleshooting

### "npx: command not found"
- Make sure Node.js is installed: `node --version`
- Install Node.js: https://nodejs.org

### "Build failed"
- Test locally first: `cd ui/dashboard && npm run build`
- Fix any errors before deploying

### "Environment variables not working"
- Make sure you added them in Vercel dashboard
- Redeploy after adding: `npx vercel --prod`
- Variable names must match exactly (case-sensitive)

### "Can't connect to Supabase"
- Verify Supabase URL is correct
- Check anon key is correct
- Ensure Supabase project is active
- Check RLS policies allow public access

---

## Next Steps After Deployment

1. ✅ **Test both sites** - Make sure everything works
2. ✅ **Set up custom domains** (optional)
   - Dashboard: `benchsight.noradhockey.com`
   - Tracker: `tracker.noradhockey.com`
3. ✅ **Monitor performance** - Check Vercel Analytics
4. ✅ **Share your URLs!** - Show off your work

---

## Quick Commands Reference

```bash
# Deploy Dashboard
cd ui/dashboard && npx vercel

# Deploy Dashboard (Production)
cd ui/dashboard && npx vercel --prod

# Deploy Tracker
cd ui/tracker && npx vercel

# Deploy Tracker (Production)
cd ui/tracker && npx vercel --prod
```

---

## Cost

**Free!** Vercel's hobby tier is free and includes:
- Unlimited deployments
- 100GB bandwidth/month
- Automatic HTTPS
- Global CDN
- Preview deployments

---

**Ready to deploy? Choose Option 1 (Web) or Option 2 (CLI) above!** 🚀
