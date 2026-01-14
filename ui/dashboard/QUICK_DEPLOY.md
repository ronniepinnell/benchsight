# Quick Deploy to Vercel

## 5-Minute Setup

### 1. Prepare
```bash
cd ui/dashboard
./scripts/setup-portal.sh
npm run build  # Test it works
```

### 2. Deploy
```bash
vercel login
vercel --prod
```

Or use Vercel Dashboard: https://vercel.com/new

### 3. Environment Variables
In Vercel Dashboard → Settings → Environment Variables:

```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

### 4. Supabase Auth
1. Enable Email provider
2. Add redirect URL: `https://your-app.vercel.app/auth/callback`
3. Create admin user

### 5. Test
- Visit `/login`
- Sign in
- Access `/admin` and `/tracker`

## Protected Routes
- `/admin` - Requires login
- `/tracker` - Requires login

## Full Docs
- `docs/DEPLOYMENT_VERCEL.md` - Complete guide
- `docs/AUTHENTICATION_SETUP.md` - Auth setup
- `DEPLOYMENT_CHECKLIST.md` - Checklist
