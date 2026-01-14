# Environment Variables Reference

Complete reference for all environment variables needed for BenchSight production.

## Dashboard (Vercel)

Location: Vercel Dashboard → Settings → Environment Variables

### Required

```bash
# Supabase Connection
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Optional

```bash
# ETL API URL (for admin portal)
NEXT_PUBLIC_API_URL=https://your-api.railway.app

# Sentry Error Tracking (optional)
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx
```

### How to Get Supabase Credentials

1. Go to Supabase Dashboard → Your Project
2. Settings → API
3. Copy:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public** key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`

---

## ETL API (Railway/Render)

Location: Railway/Render Dashboard → Environment Variables

### Required

```bash
# Environment
ENVIRONMENT=production

# CORS Origins (comma-separated)
# Add your Vercel dashboard URL
CORS_ORIGINS=https://your-dashboard.vercel.app
```

### Optional

```bash
# Supabase (if API needs direct database access)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database (if using separate database)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Redis (if using Celery for job queue)
REDIS_URL=redis://localhost:6379
```

### How to Get Supabase Service Key

1. Go to Supabase Dashboard → Your Project
2. Settings → API
3. Copy **service_role** key → `SUPABASE_SERVICE_KEY`
4. ⚠️ **Keep this secret!** Never expose in client-side code.

---

## Local Development

### Dashboard

Create `ui/dashboard/.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### ETL API

Create `api/.env`:

```bash
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
```

---

## Environment-Specific Values

### Development

```bash
# Dashboard
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000

# API
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Production

```bash
# Dashboard (Vercel)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=https://your-api.railway.app

# API (Railway)
ENVIRONMENT=production
CORS_ORIGINS=https://your-dashboard.vercel.app
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
```

---

## Security Best Practices

1. **Never commit `.env` files** to git
2. **Use `.env.example`** files for documentation
3. **Set variables in platform dashboards** (Vercel, Railway)
4. **Rotate keys regularly** (especially service keys)
5. **Use different keys** for development and production
6. **Limit CORS origins** to specific domains
7. **Never expose service keys** in client-side code

---

## Troubleshooting

### "Environment variable not found"

- Check variable name (case-sensitive)
- Verify it's set in the correct environment (Production/Preview/Development)
- Redeploy after adding variables

### "CORS error"

- Verify `CORS_ORIGINS` includes your dashboard URL
- Check for trailing slashes
- Ensure protocol matches (http vs https)

### "Supabase connection failed"

- Verify URL format: `https://xxx.supabase.co` (no trailing slash)
- Check key is correct (anon key for dashboard, service key for API)
- Verify Supabase project is active

---

## Quick Reference

| Variable | Where | Required | Purpose |
|----------|-------|----------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | Vercel | ✅ | Dashboard → Supabase |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Vercel | ✅ | Dashboard → Supabase |
| `NEXT_PUBLIC_API_URL` | Vercel | ⚠️ | Admin portal → API |
| `ENVIRONMENT` | Railway | ✅ | API environment |
| `CORS_ORIGINS` | Railway | ✅ | API CORS config |
| `SUPABASE_URL` | Railway | ⚠️ | API → Supabase |
| `SUPABASE_SERVICE_KEY` | Railway | ⚠️ | API → Supabase |

---

## Example Setup

### Step 1: Get Supabase Credentials

```bash
# From Supabase Dashboard → Settings → API
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzODk2NzI4MCwiZXhwIjoxOTU0NTQzMjgwfQ.xxx
SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjM4OTY3MjgwLCJleHAiOjE5NTQ1NDMyODB9.xxx
```

### Step 2: Set Vercel Variables

```bash
NEXT_PUBLIC_SUPABASE_URL=https://abcdefghijklmnop.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzODk2NzI4MCwiZXhwIjoxOTU0NTQzMjgwfQ.xxx
```

### Step 3: Deploy API and Get URL

```bash
# After deploying to Railway
API_URL=https://benchsight-api.railway.app
```

### Step 4: Update Vercel with API URL

```bash
NEXT_PUBLIC_API_URL=https://benchsight-api.railway.app
```

### Step 5: Set Railway Variables

```bash
ENVIRONMENT=production
CORS_ORIGINS=https://your-dashboard.vercel.app
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjM4OTY3MjgwLCJleHAiOjE5NTQ1NDMyODB9.xxx
```

---

*Last Updated: 2026-01-13*
