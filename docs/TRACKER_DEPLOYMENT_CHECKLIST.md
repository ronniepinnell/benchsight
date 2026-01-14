# Tracker Deployment Checklist

**Pre-deployment checklist to ensure smooth deployment**

---

## ✅ Pre-Deployment Checklist

### Dependencies

- [ ] Node.js 18+ installed
- [ ] All npm packages installed (`npm install`)
- [ ] `xlsx` package installed (for Excel export)
- [ ] No build errors (`npm run build` succeeds)
- [ ] TypeScript compiles (`npm run type-check`)

### Environment Variables

- [ ] `.env.local` created (for local development)
- [ ] `NEXT_PUBLIC_SUPABASE_URL` set
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` set
- [ ] Environment variables ready for production

### Supabase Setup

- [ ] `stage_dim_schedule` table exists (or `fact_game_status`)
- [ ] `fact_gameroster` table exists (or `stage_fact_gameroster`)
- [ ] `stage_events_tracking` table exists
- [ ] `stage_shifts_tracking` table exists
- [ ] Tables have proper indexes
- [ ] Row Level Security (RLS) configured (if needed)

### Testing

- [ ] Tracker page loads (`/tracker`)
- [ ] Game selection works
- [ ] Can load a game
- [ ] Rosters load from Supabase
- [ ] Can create events
- [ ] Can create shifts
- [ ] Can edit events
- [ ] Can edit shifts
- [ ] XY placement works
- [ ] Keyboard shortcuts work
- [ ] Sync to Supabase works
- [ ] Export to Excel works
- [ ] Auto-save works

### Code Quality

- [ ] No linting errors (`npm run lint`)
- [ ] No TypeScript errors
- [ ] All imports resolved
- [ ] No console errors in browser

---

## 🚀 Deployment Steps

### 1. Final Build Test

```bash
cd ui/dashboard
npm run build
```

**Must succeed before deploying!**

### 2. Deploy to Vercel

#### Option A: Vercel Dashboard

1. Go to https://vercel.com/new
2. Import GitHub repository
3. Set **Root Directory**: `ui/dashboard`
4. Click **Deploy**

#### Option B: Vercel CLI

```bash
cd ui/dashboard
npx vercel
```

### 3. Add Environment Variables

In Vercel dashboard:
- Go to project → Settings → Environment Variables
- Add:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Redeploy

### 4. Verify Deployment

- [ ] Visit deployed URL
- [ ] Tracker page loads
- [ ] Can select a game
- [ ] Rosters load
- [ ] Can create events
- [ ] Sync works
- [ ] Export works

---

## 🔍 Post-Deployment Verification

### Test Checklist

1. **Game Selection**
   - [ ] Page loads
   - [ ] Games list appears
   - [ ] Can search games
   - [ ] Can select a game

2. **Tracker Interface**
   - [ ] Header displays correctly
   - [ ] Three panels visible
   - [ ] Rink renders
   - [ ] Event form works
   - [ ] Shift panel works

3. **Data Operations**
   - [ ] Rosters load from Supabase
   - [ ] Can create events
   - [ ] Can create shifts
   - [ ] Events save to Supabase
   - [ ] Shifts save to Supabase
   - [ ] Can export to Excel

4. **User Experience**
   - [ ] Keyboard shortcuts work
   - [ ] Toast notifications appear
   - [ ] Auto-save works
   - [ ] Editing works
   - [ ] No console errors

---

## 🐛 Common Deployment Issues

### Build Fails

**Error**: Build fails with TypeScript errors

**Fix**:
```bash
npm run type-check
# Fix all TypeScript errors
npm run build
```

### Missing Dependencies

**Error**: Module not found

**Fix**:
```bash
npm install
npm install xlsx  # If Excel export fails
```

### Environment Variables Not Set

**Error**: Supabase connection fails

**Fix**:
- Add environment variables in Vercel dashboard
- Redeploy after adding variables

### Supabase Tables Missing

**Error**: "Table does not exist"

**Fix**:
- Create tables in Supabase SQL editor
- See `docs/TRACKER_USAGE_AND_DEPLOYMENT.md` for schema

---

## 📝 Deployment Notes

### Vercel Configuration

The `vercel.json` file is already configured:
- Build command: `npm run build`
- Output directory: `.next`
- Framework: Next.js

### Custom Domain

To add a custom domain:
1. Go to Vercel project → Settings → Domains
2. Add your domain
3. Update DNS records as instructed

### Environment Variables

**Important**: Environment variables must be set in Vercel dashboard, not just `.env.local`

---

## ✅ Success Criteria

Deployment is successful when:

1. ✅ Tracker page loads without errors
2. ✅ Can select and load games
3. ✅ Rosters load from Supabase
4. ✅ Can create and edit events/shifts
5. ✅ Sync to Supabase works
6. ✅ Excel export works
7. ✅ No console errors
8. ✅ All features functional

---

**Ready to deploy!** 🚀
