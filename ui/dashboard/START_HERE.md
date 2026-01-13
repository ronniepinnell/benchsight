# Start Here - Running the Dashboard

## Quick Start (3 Steps)

### Step 1: Open Terminal

Open Terminal on your Mac (Applications → Utilities → Terminal, or press `Cmd + Space` and type "Terminal")

### Step 2: Navigate to Dashboard Directory

```bash
# From your project root (benchsight directory)
cd ui/dashboard

# OR if you're already in the project, just:
cd ui/dashboard
```

**Full path should be:**
```
/Users/ronniepinnell/Documents/Documents - Ronnie's MacBook Pro - 1/Programming_HD/Hockey/Benchsight/git/benchsight/ui/dashboard
```

### Step 3: Start Dev Server

```bash
# First time only - install dependencies
npm install

# Then start the server
npm run dev
```

You should see:
```
▲ Next.js 14.1.0
- Local:        http://localhost:3000
- Ready in 2.3s
```

### Step 4: Open in Browser

Visit: **http://localhost:3000**

---

## Troubleshooting

### "Command not found: npm"

You need to install Node.js:
1. Go to https://nodejs.org
2. Download and install Node.js 18+ (LTS version)
3. Restart terminal
4. Try again

### "Cannot find module"

Run `npm install` first (one time only)

### "Port 3000 already in use"

```bash
# Use a different port
PORT=3001 npm run dev
# Then visit http://localhost:3001
```

### "Missing environment variables"

Create `.env.local` file in `ui/dashboard/`:

```bash
cd ui/dashboard
cat > .env.local << 'EOF'
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
EOF
```

---

## What You'll See

Once running, you can visit:

- **Home**: http://localhost:3000 (redirects to standings)
- **Standings**: http://localhost:3000/standings
- **Leaders**: http://localhost:3000/leaders
- **Macro Overview**: http://localhost:3000/prototypes/macro/league-overview
- **Macro Stats**: http://localhost:3000/prototypes/macro/league-stats
- **Team Comparison**: http://localhost:3000/prototypes/macro/team-comparison

---

## Quick Reference

**Start server:**
```bash
cd ui/dashboard
npm run dev
```

**Stop server:**
Press `Ctrl + C` in the terminal

**Restart server:**
Press `Ctrl + C`, then run `npm run dev` again
