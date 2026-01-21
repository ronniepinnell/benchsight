# Production Deployment Checklist

Use this checklist to ensure everything is set up correctly for production.

## Pre-Deployment

- [ ] Code pushed to GitHub
- [ ] All tests passing (if any)
- [ ] Build works locally: `npm run build` in `ui/dashboard`
- [ ] Portal files copied: `./scripts/setup-portal.sh`
- [ ] No TypeScript errors: `npm run type-check`
- [ ] Environment variables documented

## Vercel (Dashboard)

- [ ] Account created
- [ ] Repository connected
- [ ] Root directory set to `ui/dashboard`
- [ ] Environment variables set:
  - [ ] `NEXT_PUBLIC_SUPABASE_URL`
  - [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - [ ] `NEXT_PUBLIC_API_URL` (after API deployment)
- [ ] Deployed successfully
- [ ] Dashboard accessible at Vercel URL
- [ ] All pages load correctly

## Railway (ETL API)

- [ ] Account created
- [ ] Project initialized: `railway init`
- [ ] Environment variables set:
  - [ ] `ENVIRONMENT=production`
  - [ ] `CORS_ORIGINS` (includes Vercel URL)
  - [ ] `SUPABASE_URL` (if needed)
  - [ ] `SUPABASE_SERVICE_KEY` (if needed)
- [ ] Deployed successfully
- [ ] API accessible at Railway URL
- [ ] Health check works: `/api/health`
- [ ] API docs accessible: `/docs`

## Supabase

- [ ] Project created
- [ ] Database tables deployed
- [ ] Views deployed
- [ ] Email auth enabled
- [ ] Redirect URLs configured:
  - [ ] Site URL set
  - [ ] Callback URL added
  - [ ] Wildcard URL added
- [ ] Admin users created
- [ ] RLS policies configured (if needed)

## Testing

- [ ] Login page works
- [ ] Can sign in with admin credentials
- [ ] Protected routes require auth (`/admin`, `/tracker`)
- [ ] Public routes accessible without auth
- [ ] Admin portal loads
- [ ] Admin portal can connect to API
- [ ] Tracker loads and connects to Supabase
- [ ] All dashboard pages load correctly
- [ ] Data displays properly

## Security

- [ ] Environment variables not in code
- [ ] HTTPS enabled (automatic)
- [ ] CORS configured correctly
- [ ] Strong admin passwords
- [ ] Supabase RLS policies set (if needed)
- [ ] API keys stored securely

## Monitoring (Optional)

- [ ] Vercel Analytics enabled
- [ ] Error tracking set up (Sentry)
- [ ] Uptime monitoring configured
- [ ] Alerts configured

## Documentation

- [ ] Deployment guide reviewed
- [ ] Environment variables documented
- [ ] Admin credentials stored securely
- [ ] Team members have access

## Post-Deployment

- [ ] Custom domain configured (optional)
- [ ] DNS configured (if using custom domain)
- [ ] SSL certificate active (automatic)
- [ ] Backups configured
- [ ] Team notified of production URL

---

## Quick Commands

```bash
# Test dashboard build
cd ui/dashboard && npm run build

# Test API locally
cd api && uvicorn api.main:app --port 8000

# Deploy dashboard
cd ui/dashboard && vercel --prod

# Deploy API
cd api && railway up

# Check API health
curl https://your-api.railway.app/api/health
```

---

## Environment Variables Quick Reference

### Vercel
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_API_URL=https://xxx.railway.app
```

### Railway
```
ENVIRONMENT=production
CORS_ORIGINS=https://your-dashboard.vercel.app
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
```

---

## Support Resources

- **Full Guide:** `docs/PRODUCTION_SETUP.md`
- **API Deployment:** `api/DEPLOYMENT.md`
- **Vercel Deployment:** `docs/DEPLOYMENT_VERCEL.md`
- **Auth Setup:** `docs/AUTHENTICATION_SETUP.md`

---

**Status:** ⏳ Ready to deploy when all items checked
