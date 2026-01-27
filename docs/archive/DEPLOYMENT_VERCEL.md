# Vercel Deployment Guide

Complete guide to deploying BenchSight Dashboard, Tracker, and Admin Portal to Vercel.

## Prerequisites

1. **Vercel Account** - Sign up at https://vercel.com
2. **GitHub Repository** - Code pushed to GitHub
3. **Supabase Project** - Database and auth configured
4. **ETL API** - Deployed separately (Railway/Render) or run locally

## Step 1: Prepare Your Code

### 1.1 Ensure Portal Files Are Copied

```bash
cd ui/dashboard
./scripts/setup-portal.sh
```

This copies `ui/portal/*` to `public/portal/` so they're included in the build.

### 1.2 Verify Build Works Locally

```bash
cd ui/dashboard
npm run build
```

Fix any build errors before deploying.

## Step 2: Connect to Vercel

### Option A: Via Vercel Dashboard (Recommended)

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure project:
   - **Framework Preset:** Next.js
   - **Root Directory:** `ui/dashboard`
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)
   - **Install Command:** `npm install` (default)

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Navigate to dashboard
cd ui/dashboard

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No (first time)
# - Project name? benchsight-dashboard
# - Directory? ./ui/dashboard
# - Override settings? No
```

## Step 3: Configure Environment Variables

In Vercel Dashboard → Your Project → Settings → Environment Variables:

### Required Variables

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Optional Variables

```bash
NEXT_PUBLIC_API_URL=https://your-api.railway.app  # For admin portal
```

### How to Add Variables

1. Go to **Settings** → **Environment Variables**
2. Click **Add New**
3. Add each variable for:
   - **Production**
   - **Preview** (optional, for PR previews)
   - **Development** (optional, for local dev)

## Step 4: Configure Supabase Auth

### 4.1 Enable Email Auth in Supabase

1. Go to Supabase Dashboard → **Authentication** → **Providers**
2. Enable **Email** provider
3. Configure email templates (optional)

### 4.2 Add Redirect URLs

1. Go to **Authentication** → **URL Configuration**
2. Add Site URL: `https://your-project.vercel.app`
3. Add Redirect URLs:
   - `https://your-project.vercel.app/auth/callback`
   - `https://your-project.vercel.app/**` (wildcard for all routes)

### 4.3 Create Admin Users

**Option A: Via Supabase Dashboard**

1. Go to **Authentication** → **Users**
2. Click **Add User** → **Create New User**
3. Enter email and password
4. Set user metadata (optional):
   ```json
   {
     "role": "admin"
   }
   ```

**Option B: Via SQL**

```sql
-- Create admin user (replace with your email)
INSERT INTO auth.users (
  instance_id,
  id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at
) VALUES (
  '00000000-0000-0000-0000-000000000000',
  gen_random_uuid(),
  'authenticated',
  'authenticated',
  'admin@example.com',
  crypt('your-password', gen_salt('bf')),
  now(),
  now(),
  now()
);
```

## Step 5: Deploy

### First Deployment

```bash
# If using CLI
vercel --prod

# Or push to main branch (if connected to GitHub)
git push origin main
```

Vercel will automatically:
1. Install dependencies
2. Run build
3. Deploy to production

### View Deployment

- **Production URL:** `https://your-project.vercel.app`
- **Deployment Logs:** Available in Vercel Dashboard

## Step 6: Test Authentication

1. Visit: `https://your-project.vercel.app/login`
2. Sign up or sign in
3. Try accessing `/admin` or `/tracker` (should work if authenticated)
4. Sign out and try again (should redirect to login)

## Step 7: Deploy ETL API (Separate Service)

The admin portal needs the ETL API. Deploy it separately:

### Option A: Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
cd api
railway init

# Deploy
railway up
```

### Option B: Render

1. Go to https://render.com
2. Create new **Web Service**
3. Connect GitHub repo
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3

### Update API URL

After deploying ETL API, update the environment variable:

```bash
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

Or update `public/portal/js/config.js` to use the production API URL.

## Troubleshooting

### Build Fails

**Error: Missing environment variables**
- Add all required env vars in Vercel Dashboard
- Redeploy after adding variables

**Error: TypeScript errors**
- Fix TypeScript errors locally first
- Run `npm run type-check` before deploying

**Error: Portal files not found**
- Run `./scripts/setup-portal.sh` before committing
- Ensure `public/portal/` is in git

### Auth Not Working

**Redirect loop**
- Check redirect URLs in Supabase match Vercel URL
- Verify `NEXT_PUBLIC_SUPABASE_URL` is correct

**Can't sign in**
- Check Supabase Auth is enabled
- Verify email provider is enabled
- Check email confirmation settings

**Can't access protected routes**
- Verify middleware is working
- Check user is authenticated in browser console
- Ensure cookies are enabled

### Portal Not Loading

**Blank iframe**
- Check `public/portal/index.html` exists
- Verify portal files were copied
- Check browser console for errors

**API connection fails**
- Verify `NEXT_PUBLIC_API_URL` is set
- Check CORS settings in ETL API
- Ensure ETL API is deployed and running

## Environment-Specific Configuration

### Production

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

### Preview (PR Deployments)

Use same variables as production, or create separate Supabase project for testing.

### Development

Create `ui/dashboard/.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Custom Domain (Optional)

1. Go to Vercel Dashboard → **Settings** → **Domains**
2. Add your domain
3. Follow DNS configuration instructions
4. Update Supabase redirect URLs to include custom domain

## Continuous Deployment

Once connected to GitHub:

- **Main branch** → Production deployment
- **Other branches** → Preview deployments
- **Pull requests** → Preview deployments with unique URLs

## Monitoring

### Vercel Analytics

Enable in **Settings** → **Analytics** to track:
- Page views
- Performance metrics
- User behavior

### Error Tracking

Consider adding:
- Sentry for error tracking
- LogRocket for session replay
- Vercel Analytics for performance

## Security Checklist

- [ ] Environment variables set in Vercel (not in code)
- [ ] Supabase RLS policies configured
- [ ] Auth redirect URLs configured
- [ ] Admin users created
- [ ] HTTPS enabled (automatic on Vercel)
- [ ] CORS configured for ETL API
- [ ] Rate limiting considered (if needed)

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Configure environment variables
3. ✅ Set up Supabase Auth
4. ✅ Test authentication
5. ✅ Deploy ETL API
6. ⏳ Set up custom domain (optional)
7. ⏳ Configure monitoring (optional)
8. ⏳ Add error tracking (optional)

## Support

- **Vercel Docs:** https://vercel.com/docs
- **Supabase Auth:** https://supabase.com/docs/guides/auth
- **Next.js Deployment:** https://nextjs.org/docs/deployment
