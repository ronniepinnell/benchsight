# Vercel Deployment Checklist

**Project:** BenchSight Dashboard  
**Framework:** Next.js 16  
**Date:** 2026-01-15

---

## Pre-Deployment

### Environment Variables

Verify these are set in Vercel dashboard:

**Required:**
- [ ] `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anonymous key
- [ ] `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key (for server-side)
- [ ] `NEXT_PUBLIC_APP_URL` - Production URL (e.g., `https://your-app.vercel.app`)

**Optional:**
- [ ] `NODE_ENV` - Should be `production` (auto-set by Vercel)
- [ ] Any other custom environment variables

### Build Configuration

**Verify `vercel.json`:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "installCommand": "npm install --legacy-peer-deps"
}
```

**Verify `next.config.js`:**
- [ ] Image domains configured correctly
- [ ] TypeScript errors ignored (for now)
- [ ] Turbopack config present
- [ ] React strict mode setting appropriate

### Local Build Test

Before deploying, test production build locally:

```bash
cd ui/dashboard
npm run build
npm run start
```

**Check:**
- [ ] Build completes without errors
- [ ] All pages load correctly
- [ ] Images load properly
- [ ] API routes work
- [ ] Database connections work
- [ ] No console errors

---

## Deployment Steps

### 1. Connect Repository to Vercel

- [ ] Link GitHub/GitLab repository to Vercel
- [ ] Select correct project directory: `ui/dashboard`
- [ ] Set root directory to `ui/dashboard` in Vercel settings

### 2. Configure Build Settings

**In Vercel Dashboard:**
- [ ] Framework Preset: Next.js
- [ ] Build Command: `npm run build` (or leave default)
- [ ] Output Directory: `.next` (default)
- [ ] Install Command: `npm install --legacy-peer-deps`
- [ ] Node.js Version: 18.x or higher

### 3. Set Environment Variables

**In Vercel Dashboard → Settings → Environment Variables:**
- [ ] Add all required environment variables
- [ ] Set for Production, Preview, and Development environments
- [ ] Verify no typos in variable names

### 4. Deploy

- [ ] Trigger deployment (push to main branch or manual deploy)
- [ ] Monitor build logs for errors
- [ ] Wait for deployment to complete

---

## Post-Deployment Verification

### Basic Functionality

**Test these pages:**
- [ ] `/norad/standings` - Standings page loads
- [ ] `/norad/teams` - Teams list loads
- [ ] `/norad/team/[teamName]` - Team pages load
- [ ] `/norad/players` - Players list loads
- [ ] `/norad/players/[playerId]` - Player pages load
- [ ] `/norad/games/[gameId]` - Game pages load
- [ ] `/norad/leaders` - Leaders pages load

**Test functionality:**
- [ ] Season selector works
- [ ] Game type filter works
- [ ] Tables are sortable
- [ ] Links navigate correctly
- [ ] Images load (team logos, player photos)
- [ ] Search/filter dropdowns work

### Database & API

- [ ] Database queries execute successfully
- [ ] Supabase connection works
- [ ] API routes respond correctly
- [ ] External API calls work (NORAD schedule API)
- [ ] No database timeout errors

### Performance

- [ ] Page load times acceptable (< 3s)
- [ ] Images optimize correctly
- [ ] No excessive bundle size warnings
- [ ] No memory leaks
- [ ] API response times reasonable

### Error Handling

- [ ] 404 pages work correctly
- [ ] Error boundaries catch errors
- [ ] Missing data handled gracefully
- [ ] No console errors in production
- [ ] Error monitoring set up (if applicable)

---

## Monitoring & Maintenance

### Set Up Monitoring

- [ ] Configure Vercel Analytics (if desired)
- [ ] Set up error tracking (Sentry, LogRocket, etc.)
- [ ] Configure uptime monitoring
- [ ] Set up performance monitoring

### Post-Deployment Tasks

- [ ] Test all major user flows
- [ ] Verify mobile responsiveness
- [ ] Check browser compatibility
- [ ] Test with different screen sizes
- [ ] Verify SEO meta tags
- [ ] Check social media previews

### Documentation

- [ ] Update deployment documentation
- [ ] Document any production-specific configurations
- [ ] Note any known issues or limitations
- [ ] Document rollback procedure

---

## Rollback Procedure

If deployment fails or issues arise:

1. **Via Vercel Dashboard:**
   - Go to Deployments
   - Find last working deployment
   - Click "..." → "Promote to Production"

2. **Via Git:**
   - Revert problematic commit
   - Push to trigger new deployment

3. **Emergency:**
   - Disable deployment in Vercel
   - Fix issues locally
   - Re-enable and redeploy

---

## Common Issues & Solutions

### Build Fails

**Issue:** TypeScript errors
- **Solution:** Currently ignored in `next.config.js`, but should fix eventually

**Issue:** Missing dependencies
- **Solution:** Check `package.json`, ensure all deps are listed

**Issue:** Environment variables missing
- **Solution:** Verify all env vars are set in Vercel dashboard

### Runtime Errors

**Issue:** Database connection fails
- **Solution:** Check Supabase URL and keys, verify network access

**Issue:** Images don't load
- **Solution:** Verify `next.config.js` image domains, check image URLs

**Issue:** API routes fail
- **Solution:** Check server-side code, verify environment variables

### Performance Issues

**Issue:** Slow page loads
- **Solution:** Check bundle size, optimize queries, add caching

**Issue:** High memory usage
- **Solution:** Check for memory leaks, optimize data fetching

---

## Next Steps After Deployment

1. **Monitor for 24-48 hours:**
   - Watch for errors
   - Monitor performance
   - Check user feedback

2. **Collect tracking data:**
   - Begin collecting more game tracking data
   - Validate data quality
   - Prepare for Phase 2 features

3. **Plan Phase 2:**
   - Review roadmap
   - Prioritize features
   - Begin advanced stats integration

---

## Notes

- Keep this checklist updated as deployment process evolves
- Document any production-specific quirks
- Maintain a changelog of deployments
- Track performance metrics over time

---

**Last Updated:** 2026-01-15
