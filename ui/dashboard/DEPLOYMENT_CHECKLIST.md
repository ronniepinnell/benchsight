# Vercel Deployment Checklist

Quick checklist for deploying BenchSight to Vercel with authentication.

## Pre-Deployment

- [ ] Code is pushed to GitHub
- [ ] Build works locally: `npm run build`
- [ ] Portal files copied: `./scripts/setup-portal.sh`
- [ ] All TypeScript errors fixed: `npm run type-check`

## Vercel Setup

- [ ] Vercel account created
- [ ] Project connected to GitHub repository
- [ ] Root directory set to `ui/dashboard`
- [ ] Framework preset: Next.js

## Environment Variables

Add in Vercel Dashboard → Settings → Environment Variables:

- [ ] `NEXT_PUBLIC_SUPABASE_URL` (Production)
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` (Production)
- [ ] `NEXT_PUBLIC_API_URL` (Production, optional)

## Supabase Auth Configuration

- [ ] Email provider enabled in Supabase
- [ ] Site URL set: `https://your-project.vercel.app`
- [ ] Redirect URLs added:
  - [ ] `https://your-project.vercel.app/auth/callback`
  - [ ] `https://your-project.vercel.app/**`
- [ ] Admin user created (via dashboard or SQL)

## First Deployment

- [ ] Deploy to production: `vercel --prod` or push to main
- [ ] Verify deployment URL works
- [ ] Check build logs for errors

## Testing

- [ ] Visit `/login` page
- [ ] Sign up or sign in
- [ ] Access `/admin` (should work when authenticated)
- [ ] Access `/tracker` (should work when authenticated)
- [ ] Sign out and verify redirect to login
- [ ] Try accessing `/admin` while signed out (should redirect)

## ETL API (Separate Deployment)

- [ ] ETL API deployed (Railway/Render)
- [ ] API URL updated in environment variables
- [ ] CORS configured in ETL API
- [ ] Test portal can connect to API

## Post-Deployment

- [ ] Custom domain configured (optional)
- [ ] Monitoring/analytics enabled (optional)
- [ ] Error tracking set up (optional)

## Troubleshooting

If something doesn't work:

1. **Check build logs** in Vercel Dashboard
2. **Verify environment variables** are set correctly
3. **Check Supabase redirect URLs** match your Vercel URL
4. **Test authentication** in browser console
5. **Review middleware logs** for auth issues

## Quick Commands

```bash
# Local build test
cd ui/dashboard
npm run build

# Deploy to Vercel
vercel --prod

# Check environment variables
vercel env ls

# View deployment logs
vercel logs
```

## Support

- See `docs/DEPLOYMENT_VERCEL.md` for detailed guide
- Vercel Docs: https://vercel.com/docs
- Supabase Auth: https://supabase.com/docs/guides/auth
