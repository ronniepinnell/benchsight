# Deployment & Authentication Summary

Quick reference for deploying BenchSight to Vercel with authentication.

## What's Been Implemented

### ✅ Authentication System
- **Login page** at `/login`
- **Protected routes:** `/admin` and `/tracker` require authentication
- **Middleware** automatically redirects unauthenticated users
- **User menu** in topbar shows login status and sign out
- **Auth callback** handles Supabase email confirmations

### ✅ Vercel Deployment
- **Vercel configuration** (`vercel.json`)
- **Environment variables** setup guide
- **Build configuration** for Next.js
- **Portal file setup** script

## Quick Start Deployment

### 1. Prepare Code

```bash
# Copy portal files
cd ui/dashboard
./scripts/setup-portal.sh

# Test build
npm run build
```

### 2. Deploy to Vercel

**Option A: Via Dashboard**
1. Go to https://vercel.com/new
2. Import GitHub repository
3. Set root directory: `ui/dashboard`
4. Add environment variables (see below)

**Option B: Via CLI**
```bash
cd ui/dashboard
vercel login
vercel --prod
```

### 3. Environment Variables

Add in Vercel Dashboard → Settings → Environment Variables:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=https://your-api.railway.app  # Optional
```

### 4. Configure Supabase Auth

1. **Enable Email Provider:**
   - Supabase Dashboard → Authentication → Providers → Enable Email

2. **Add Redirect URLs:**
   - Site URL: `https://your-project.vercel.app`
   - Redirect URLs:
     - `https://your-project.vercel.app/auth/callback`
     - `https://your-project.vercel.app/**`

3. **Create Admin User:**
   - Authentication → Users → Add User
   - Or use SQL (see AUTHENTICATION_SETUP.md)

### 5. Test

1. Visit: `https://your-project.vercel.app/login`
2. Sign in with admin credentials
3. Access `/admin` and `/tracker` (should work)
4. Sign out and try again (should redirect to login)

## File Structure

```
ui/dashboard/
├── src/
│   ├── middleware.ts              # Auth protection
│   ├── app/
│   │   ├── login/
│   │   │   └── page.tsx          # Login page
│   │   ├── auth/
│   │   │   └── callback/
│   │   │       └── route.ts      # Auth callback
│   │   └── (dashboard)/
│   │       ├── admin/            # Protected
│   │       └── tracker/          # Protected
│   └── components/
│       ├── auth/
│       │   └── user-menu.tsx    # User menu
│       └── layout/
│           └── topbar.tsx        # Updated with user menu
├── public/
│   └── portal/                   # Portal files (after setup)
├── vercel.json                   # Vercel config
└── DEPLOYMENT_CHECKLIST.md       # Quick checklist
```

## Protected Routes

These routes require authentication:
- `/admin` - Admin Portal
- `/tracker` - Game Tracker
- `/tracker/[gameId]` - Active tracking sessions

Public routes (no auth):
- `/standings`
- `/leaders`
- `/players`
- `/teams`
- `/games`
- All other dashboard pages

## Authentication Flow

```
1. User visits /admin or /tracker
   ↓
2. Middleware checks authentication
   ↓
3. If not authenticated → Redirect to /login
   ↓
4. User signs in → Supabase Auth
   ↓
5. Redirect to original destination
   ↓
6. Access granted
```

## Documentation

- **Full Deployment Guide:** `docs/DEPLOYMENT_VERCEL.md`
- **Authentication Setup:** `docs/AUTHENTICATION_SETUP.md`
- **Quick Checklist:** `ui/dashboard/DEPLOYMENT_CHECKLIST.md`
- **Unified Site Guide:** `docs/UNIFIED_SITE_INTEGRATION.md`

## Troubleshooting

### Build Fails
- Check TypeScript errors: `npm run type-check`
- Verify all dependencies installed
- Check environment variables are set

### Auth Not Working
- Verify Supabase redirect URLs match Vercel URL
- Check environment variables in Vercel
- Clear browser cookies and try again

### Portal Not Loading
- Run `./scripts/setup-portal.sh`
- Verify `public/portal/index.html` exists
- Check browser console for errors

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Configure Supabase Auth
3. ✅ Create admin users
4. ✅ Test authentication
5. ⏳ Deploy ETL API (separate service)
6. ⏳ Configure custom domain (optional)
7. ⏳ Set up monitoring (optional)

## Support

- **Vercel Docs:** https://vercel.com/docs
- **Supabase Auth:** https://supabase.com/docs/guides/auth
- **Next.js Middleware:** https://nextjs.org/docs/app/building-your-application/routing/middleware
