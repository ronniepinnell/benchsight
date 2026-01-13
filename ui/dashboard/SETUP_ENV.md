# Setting Up Environment Variables

The dashboard needs your Supabase credentials to connect to the database.

## Step 1: Get Your Supabase Credentials

1. Go to https://supabase.com
2. Sign in to your account
3. Open your BenchSight project
4. Go to **Settings** → **API**
5. You'll see:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public** key (a long string starting with `eyJ...`)

## Step 2: Create .env.local File

In the `ui/dashboard` directory, create a file named `.env.local`:

```bash
cd ui/dashboard
nano .env.local
```

Or use any text editor to create the file.

## Step 3: Add Your Credentials

Copy this template and fill in your values:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

**Example:**
```env
NEXT_PUBLIC_SUPABASE_URL=https://abcdefghijklmnop.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzODk2NzI4MCwiZXhwIjoxOTU0NTQzMjgwfQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Step 4: Restart the Dev Server

After creating `.env.local`:

1. Stop the server (press `Ctrl + C` in terminal)
2. Start it again:
   ```bash
   npm run dev
   ```

## Step 5: Verify It Works

Visit: http://localhost:3000/prototypes/test-connection

This page will show you if the connection is working.

## Troubleshooting

### "Still getting errors"

- Make sure the file is named exactly `.env.local` (starts with a dot)
- Make sure it's in the `ui/dashboard` directory
- Make sure there are no extra spaces or quotes around the values
- Restart the dev server after creating/editing the file

### "Where do I find my credentials?"

1. Supabase Dashboard → Your Project
2. Settings (gear icon) → API
3. Look for "Project URL" and "anon public" key

### File Location

The `.env.local` file should be here:
```
ui/dashboard/.env.local
```

Not in the project root, but specifically in `ui/dashboard/`
