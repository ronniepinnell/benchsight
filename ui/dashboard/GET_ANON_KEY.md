# Getting Your Supabase Anon Key

Your `.env.local` file has been created with your Supabase URL, but you need to add the **anon key**.

## Why Two Different Keys?

- **Service Key** (in config_local.ini): Full access, server-side only
- **Anon Key** (needed for dashboard): Public key, safe for client-side use

## Steps to Get Your Anon Key

1. **Go to Supabase Dashboard:**
   - https://supabase.com/dashboard/project/uuaowslhpgyiudmbvqze/settings/api

2. **Find the "anon public" key:**
   - Look for a section labeled "Project API keys"
   - Find the key labeled **"anon public"** (NOT "service_role")
   - It will be a long string starting with `eyJ...`

3. **Add it to `.env.local`:**
   - Open `ui/dashboard/.env.local`
   - Replace `REPLACE_WITH_YOUR_ANON_KEY` with your actual anon key
   - Save the file

4. **Restart the dev server:**
   ```bash
   # Press Ctrl+C to stop
   npm run dev
   ```

## Quick Edit Command

```bash
cd ui/dashboard
nano .env.local
```

Then replace `REPLACE_WITH_YOUR_ANON_KEY` with your actual key.

## Verify It Works

After adding the anon key and restarting, visit:
- http://localhost:3000/prototypes/test-connection

This page will confirm if the connection is working.
