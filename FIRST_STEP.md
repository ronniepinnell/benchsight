# 🚀 First Step: Get Your Website Live

## The One Thing You Need to Do

**Deploy your dashboard to Vercel** - This gets your entire website online in 10 minutes.

---

## Quick Steps

### 1. Go to Vercel
https://vercel.com/new

### 2. Import Your GitHub Repo
- Connect GitHub
- Select your `benchsight` repository

### 3. Configure
- **Root Directory:** `ui/dashboard`
- **Framework:** Next.js (auto-detected)

### 4. Add Environment Variables
Click "Environment Variables" and add:

```
NEXT_PUBLIC_SUPABASE_URL=https://uuaowslhpgyiudmbvqze.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1YW93c2xocGd5aXVkbWJ2cXplIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NTQ5ODcsImV4cCI6MjA4MjQzMDk4N30.9WjZcLzB555vKaiDeby8nYJ3Ce9L-SCkFrYH1Ts4ILU
```

### 5. Deploy
Click "Deploy" → Wait 2 minutes → **Done!**

---

## Then Configure Auth (3 minutes)

1. **Supabase Dashboard** → Authentication → Providers → Enable Email
2. **Add Redirect URL:** `https://your-project.vercel.app/auth/callback`
3. **Create Admin User** → Authentication → Users → Add User

---

## That's It!

Your site is live at: `https://your-project.vercel.app`

**Full guide:** `GET_WEBSITE_LIVE.md`
