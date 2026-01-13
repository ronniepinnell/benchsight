# BenchSight - NORAD Hockey Analytics Dashboard

A modern, production-ready analytics dashboard for the NORAD recreational hockey league.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Vercel

## Getting Started

### Prerequisites

- Node.js 18+
- npm or pnpm
- Supabase account with BenchSight database

### 1. Clone and Install

```bash
# Clone the repo (or copy files)
git clone https://github.com/yourusername/benchsight-dashboard.git
cd benchsight-dashboard

# Install dependencies
npm install
```

### 2. Environment Variables

Copy `.env.example` to `.env.local` and fill in your Supabase credentials:

```bash
cp .env.example .env.local
```

Edit `.env.local`:
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### 3. Generate Database Types

```bash
# Login to Supabase CLI
npx supabase login

# Generate types from your database
npx supabase gen types typescript --project-id YOUR_PROJECT_ID > src/types/database.ts
```

### 4. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── (dashboard)/        # Dashboard route group
│   │   ├── standings/
│   │   ├── leaders/
│   │   ├── teams/
│   │   ├── players/
│   │   └── games/
│   └── layout.tsx
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── layout/             # Sidebar, Topbar
│   ├── teams/              # Team-related components
│   ├── players/            # Player-related components
│   ├── games/              # Game-related components
│   └── hockey/             # Hockey-specific (Rink, etc.)
├── lib/
│   ├── supabase/           # Supabase client & queries
│   └── utils/              # Helper functions
└── types/                  # TypeScript types
```

## Deployment

### Deploy to Vercel

1. Push to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy!

```bash
# Or use Vercel CLI
npx vercel
```

## Key Features

- 📊 **Standings** - Live league standings with team colors
- 👑 **Leaders** - Points, goals, assists leaders (tabbed interface)
- 🧤 **Goalie Stats** - GAA, wins, save percentage leaderboards
- 👥 **Team Pages** - Rosters, stats, history
- 👤 **Player Profiles** - Career stats, game log
- 🔄 **Player Compare** - Side-by-side stat comparison
- 🏒 **Game Summaries** - Box scores, scoring summary, goalie stats
- 📅 **Schedule** - Upcoming games and recent results

## Pages

| Route | Status | Description |
|-------|--------|-------------|
| `/standings` | ✅ | League standings table |
| `/leaders` | ✅ | Scoring leaders (tabs: points, goals, assists) |
| `/goalies` | ✅ | Goalie leaderboards (tabs: GAA, wins, all stats) |
| `/games` | ✅ | Recent game results |
| `/games/[id]` | ✅ | Game box score and scoring summary |
| `/players` | ✅ | Player rankings table |
| `/players/[id]` | ✅ | Player profile with game log |
| `/players/compare` | ✅ | Compare two players side-by-side |
| `/teams` | ✅ | All teams grid |
| `/teams/[id]` | ✅ | Team roster and season stats |
| `/schedule` | ✅ | Upcoming games and recent results |

## Supabase Views (Recommended)

Create these views in Supabase for better performance:

```sql
-- v_standings
CREATE VIEW v_standings AS
SELECT 
  t.team_id,
  t.team_name,
  t.team_abbrev,
  t.team_logo_url,
  t.primary_color,
  t.secondary_color,
  -- Calculate standings from fact_game
  ...
FROM dim_team t;

-- v_player_season_stats
CREATE VIEW v_player_season_stats AS
SELECT 
  p.player_id,
  p.player_name,
  -- Aggregate stats
  ...
FROM dim_player p
JOIN fact_player_game_stats pgs ON ...;
```

## License

MIT
