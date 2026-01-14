# Authentication Setup Guide

Complete guide to setting up authentication for BenchSight Dashboard, Tracker, and Admin Portal.

## Overview

BenchSight uses **Supabase Auth** for authentication. The following routes are protected:
- `/admin` - Admin Portal
- `/tracker` - Game Tracker
- `/tracker/[gameId]` - Active tracking sessions

Public routes (no auth required):
- `/standings` - League standings
- `/leaders` - Leaderboards
- `/players` - Player pages
- `/teams` - Team pages
- `/games` - Game listings

## Architecture

```
User → Login Page → Supabase Auth → Protected Routes
                    ↓
              Session Cookie
                    ↓
            Middleware Check
                    ↓
         Allow/Deny Access
```

## Step 1: Enable Supabase Auth

### 1.1 Enable Email Provider

1. Go to Supabase Dashboard → **Authentication** → **Providers**
2. Find **Email** provider
3. Click **Enable**
4. Configure settings:
   - **Enable email confirmations:** Optional (recommended for production)
   - **Secure email change:** Enabled
   - **Double confirm email changes:** Enabled (recommended)

### 1.2 Configure Email Templates (Optional)

1. Go to **Authentication** → **Email Templates**
2. Customize templates:
   - **Confirm signup** - Email confirmation
   - **Magic Link** - Passwordless login
   - **Change Email Address** - Email change confirmation
   - **Reset Password** - Password reset

## Step 2: Configure Redirect URLs

### 2.1 Add Site URL

1. Go to **Authentication** → **URL Configuration**
2. Set **Site URL** to your production URL:
   ```
   https://your-project.vercel.app
   ```

### 2.2 Add Redirect URLs

Add these redirect URLs:

```
https://your-project.vercel.app/auth/callback
https://your-project.vercel.app/**
```

The wildcard `/**` allows all routes to handle auth redirects.

### 2.3 Local Development

For local development, also add:

```
http://localhost:3000/auth/callback
http://localhost:3000/**
```

## Step 3: Create Admin Users

### Option A: Via Supabase Dashboard

1. Go to **Authentication** → **Users**
2. Click **Add User** → **Create New User**
3. Fill in:
   - **Email:** admin@example.com
   - **Password:** (strong password)
   - **Auto Confirm User:** ✅ (skip email confirmation)
4. Click **Create User**

### Option B: Via SQL

```sql
-- Create admin user
INSERT INTO auth.users (
  instance_id,
  id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at,
  raw_app_meta_data,
  raw_user_meta_data
) VALUES (
  '00000000-0000-0000-0000-000000000000',
  gen_random_uuid(),
  'authenticated',
  'authenticated',
  'admin@example.com',
  crypt('your-secure-password', gen_salt('bf')),
  now(),
  now(),
  now(),
  '{"provider": "email", "providers": ["email"]}',
  '{"role": "admin"}'
);
```

### Option C: Self-Service Sign Up

If email sign-up is enabled, users can create accounts at `/login`.

**To enable:**
1. Go to **Authentication** → **Providers** → **Email**
2. Ensure **Enable email signup** is checked

**To restrict sign-ups:**
- Disable email sign-up in Supabase
- Only create users manually
- Or add custom logic to restrict by domain/whitelist

## Step 4: Test Authentication

### 4.1 Test Login Flow

1. Visit `/login`
2. Enter email and password
3. Click **Sign In**
4. Should redirect to `/standings` (or original destination)

### 4.2 Test Protected Routes

1. While signed in:
   - Visit `/admin` → Should work
   - Visit `/tracker` → Should work

2. Sign out:
   - Click **Sign Out** in topbar
   - Try visiting `/admin` → Should redirect to `/login`

### 4.3 Test Middleware

The middleware automatically:
- Redirects unauthenticated users from `/admin` and `/tracker` to `/login`
- Preserves the original destination in `redirect` query param
- Redirects authenticated users from `/login` to dashboard

## Step 5: User Roles (Optional)

### 5.1 Add Role Metadata

When creating users, add role metadata:

```sql
UPDATE auth.users
SET raw_user_meta_data = jsonb_build_object('role', 'admin')
WHERE email = 'admin@example.com';
```

### 5.2 Check Role in Code

```typescript
// In a component
const supabase = createClient()
const { data: { user } } = await supabase.auth.getUser()
const role = user?.user_metadata?.role

if (role === 'admin') {
  // Allow admin actions
}
```

### 5.3 Protect Routes by Role

Update middleware to check roles:

```typescript
// In middleware.ts
const role = user?.user_metadata?.role

if (isProtectedRoute && (!user || role !== 'admin')) {
  return NextResponse.redirect(new URL('/login', request.url))
}
```

## Step 6: Password Reset

### 6.1 Enable Password Reset

1. Go to **Authentication** → **Providers** → **Email**
2. Ensure **Enable email signup** is enabled
3. Users can click "Forgot password" on login page

### 6.2 Custom Password Reset Page (Optional)

Create `src/app/reset-password/page.tsx`:

```typescript
'use client'

import { useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { useSearchParams } from 'next/navigation'

export default function ResetPasswordPage() {
  const searchParams = useSearchParams()
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    const supabase = createClient()
    const { error } = await supabase.auth.updateUser({
      password: password
    })
    
    if (error) {
      alert(error.message)
    } else {
      alert('Password updated!')
    }
    
    setIsLoading(false)
  }
  
  return (
    <form onSubmit={handleReset}>
      {/* Reset password form */}
    </form>
  )
}
```

## Troubleshooting

### Can't Sign In

**Issue:** "Invalid login credentials"
- Verify email and password are correct
- Check user exists in Supabase Dashboard
- Verify email is confirmed (if email confirmation enabled)

**Issue:** "Email not confirmed"
- Check email for confirmation link
- Or disable email confirmation in Supabase settings
- Or manually confirm in Supabase Dashboard

### Redirect Loop

**Issue:** Infinite redirect between `/login` and protected route
- Check redirect URLs in Supabase match your domain
- Verify `NEXT_PUBLIC_SUPABASE_URL` is correct
- Clear browser cookies and try again
- Check middleware logic

### Session Not Persisting

**Issue:** User gets logged out on page refresh
- Check cookies are enabled in browser
- Verify Supabase session cookie settings
- Check middleware cookie handling
- Ensure `@supabase/ssr` is properly configured

### Protected Route Not Working

**Issue:** Can access `/admin` without login
- Verify middleware is running (check `middleware.ts` exists)
- Check route is in `protectedRoutes` array
- Verify middleware matcher includes the route
- Check build logs for middleware errors

## Security Best Practices

1. **Strong Passwords:** Enforce minimum password requirements
2. **Email Confirmation:** Enable for production
3. **Rate Limiting:** Consider adding rate limits to login
4. **HTTPS Only:** Always use HTTPS in production
5. **Session Timeout:** Configure session expiration
6. **2FA:** Consider adding two-factor authentication
7. **Audit Logs:** Monitor authentication events

## Advanced: Custom Auth Logic

### Restrict Sign-Ups by Domain

```typescript
// In login page
const handleSignUp = async () => {
  const emailDomain = email.split('@')[1]
  const allowedDomains = ['example.com', 'admin.example.com']
  
  if (!allowedDomains.includes(emailDomain)) {
    toast('Sign-ups restricted to specific domains', 'error')
    return
  }
  
  // Proceed with sign-up
}
```

### Require Admin Approval

1. Create `pending_users` table
2. Store sign-ups as pending
3. Admin approves via portal
4. Move to `auth.users` on approval

## Next Steps

1. ✅ Enable Supabase Auth
2. ✅ Configure redirect URLs
3. ✅ Create admin users
4. ✅ Test authentication flow
5. ⏳ Add role-based access (optional)
6. ⏳ Configure password reset
7. ⏳ Add 2FA (optional)
8. ⏳ Set up audit logging (optional)

## Support

- **Supabase Auth Docs:** https://supabase.com/docs/guides/auth
- **Next.js Middleware:** https://nextjs.org/docs/app/building-your-application/routing/middleware
- **@supabase/ssr:** https://supabase.com/docs/guides/auth/server-side/nextjs
