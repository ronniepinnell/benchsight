# Fix Vercel Middleware Error

**Error:** `MIDDLEWARE_INVOCATION_FAILED` or `500: INTERNAL_SERVER_ERROR` in middleware

---

## Quick Fix

The middleware has been updated with error handling. Common causes:

1. **Missing environment variables** - Most common
2. **Supabase connection failure** - Network or config issue
3. **Unhandled errors** - Now caught and handled

---

## Check Environment Variables

### In Vercel

1. **Go to Vercel Dashboard:**
   - Your Project → Settings → Environment Variables

2. **Verify these are set:**
   - `NEXT_PUBLIC_SUPABASE_URL` - Your Supabase project/branch URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Your Supabase anon key

3. **Check environments:**
   - Make sure variables are set for **Production, Preview, Development** (all)

4. **Redeploy:**
   - Go to Deployments → Latest → "..." → Redeploy

### Locally

```bash
# Check if .env.local exists
cd ui/dashboard
ls -la .env.local

# Check contents (don't show full keys)
cat .env.local | grep SUPABASE_URL
cat .env.local | grep SUPABASE_ANON_KEY
```

**If missing, create it:**
```bash
cat > .env.local << EOF
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
EOF
```

---

## Verify Supabase Connection

### Test Connection

```bash
# In your browser console or test page
# Visit: http://localhost:3000/prototypes/test-connection
# Should show connection status
```

### Check Supabase URL Format

**Correct:**
```
https://your-project-id.supabase.co
```

**Incorrect:**
```
https://your-project-id.supabase.co/  (trailing slash)
http://your-project-id.supabase.co   (http instead of https)
```

---

## Middleware Error Handling

The middleware now includes:

1. **Environment variable checks** - Gracefully handles missing vars
2. **Try-catch blocks** - Catches and logs errors
3. **Fallback behavior** - Continues request even if auth fails

### What Changed

- ✅ Checks for env vars before creating Supabase client
- ✅ Wraps auth calls in try-catch
- ✅ Logs errors for debugging
- ✅ Allows requests to continue even if auth fails

---

## Common Issues

### Issue 1: Environment Variables Not Set

**Symptoms:**
- Middleware fails on every request
- Error mentions missing variables

**Fix:**
1. Set environment variables in Vercel
2. Redeploy
3. Verify in build logs

### Issue 2: Wrong Supabase URL

**Symptoms:**
- Connection fails
- Network errors

**Fix:**
1. Verify URL in Supabase Dashboard
2. Use branch URL if using Supabase branching
3. Check for typos or trailing slashes

### Issue 3: Supabase Project Paused

**Symptoms:**
- Connection timeouts
- 503 errors

**Fix:**
1. Check Supabase Dashboard
2. Resume project if paused
3. Check project status

### Issue 4: CORS Issues

**Symptoms:**
- Network errors
- CORS policy errors

**Fix:**
1. Check Supabase RLS policies
2. Verify anon key is correct
3. Check CORS settings in Supabase

---

## Debugging

### Check Vercel Logs

1. **Go to Vercel Dashboard:**
   - Your Project → Deployments
   - Click on failed deployment
   - Check "Build Logs" and "Function Logs"

2. **Look for:**
   - Environment variable warnings
   - Supabase connection errors
   - Middleware error messages

### Check Local Logs

```bash
# Run dev server
cd ui/dashboard
npm run dev

# Check console for middleware warnings
# Look for: "Supabase environment variables not set"
# Or: "Auth check failed in middleware"
```

### Test Middleware Directly

Create a test route:

```typescript
// src/app/test-middleware/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL ? 'Set' : 'Missing',
    supabaseKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? 'Set' : 'Missing',
  })
}
```

Visit: `http://localhost:3000/test-middleware`

---

## Verification Checklist

After fixing:

- [ ] Environment variables set in Vercel
- [ ] Variables set for all environments (Production, Preview, Development)
- [ ] Supabase URL is correct (no trailing slash)
- [ ] Supabase anon key is correct
- [ ] Redeployed after setting variables
- [ ] Middleware errors resolved
- [ ] Pages load correctly
- [ ] Auth works (if using)

---

## If Still Having Issues

### Check Next.js Version

```bash
cd ui/dashboard
npm list next
```

**Should be:** `^16.1.1` or compatible

### Check @supabase/ssr Version

```bash
npm list @supabase/ssr
```

**Should be:** `^0.8.0` or compatible

### Update Dependencies

```bash
cd ui/dashboard
npm update @supabase/ssr @supabase/supabase-js
```

---

## Related Documentation

- [SETUP_ENV.md](../../ui/dashboard/SETUP_ENV.md) - Environment setup
- [DEV_ENVIRONMENT_SETUP.md](../DEV_ENVIRONMENT_SETUP.md) - Dev environment setup
- [ENVIRONMENT_VARIABLES_EXPLAINED.md](../ENVIRONMENT_VARIABLES_EXPLAINED.md) - How env vars work

---

*Last updated: 2026-01-13*
