# BenchSight Dashboard - Production Setup Guide

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        VERCEL                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Next.js 14 App Router                   │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │    │
│  │  │  Server  │  │  Client  │  │   API Routes     │   │    │
│  │  │Components│  │Components│  │  (if needed)     │   │    │
│  │  └────┬─────┘  └────┬─────┘  └────────┬─────────┘   │    │
│  │       │             │                  │             │    │
│  │       └─────────────┼──────────────────┘             │    │
│  │                     │                                │    │
│  └─────────────────────┼────────────────────────────────┘    │
│                        │                                     │
└────────────────────────┼─────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │      SUPABASE       │
              │  ┌───────────────┐  │
              │  │  PostgreSQL   │  │
              │  │  - dim_team   │  │
              │  │  - dim_player │  │
              │  │  - fact_game  │  │
              │  │  - fact_event │  │
              │  └───────────────┘  │
              │  ┌───────────────┐  │
              │  │    Storage    │  │
              │  │  (logos/pics) │  │
              │  └───────────────┘  │
              └─────────────────────┘
```

## 📁 Project Structure

```
benchsight-dashboard/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── layout.tsx                # Root layout (nav, theme)
│   │   ├── page.tsx                  # Home → redirects to /standings
│   │   ├── globals.css               # Global styles
│   │   │
│   │   ├── (dashboard)/              # Dashboard route group
│   │   │   ├── layout.tsx            # Dashboard layout with sidebar
│   │   │   ├── standings/
│   │   │   │   └── page.tsx
│   │   │   ├── leaders/
│   │   │   │   └── page.tsx
│   │   │   ├── goalies/
│   │   │   │   └── page.tsx
│   │   │   ├── schedule/
│   │   │   │   └── page.tsx
│   │   │   ├── teams/
│   │   │   │   ├── page.tsx          # All teams grid
│   │   │   │   └── [teamId]/
│   │   │   │       └── page.tsx      # Individual team
│   │   │   ├── players/
│   │   │   │   ├── page.tsx          # Player search
│   │   │   │   ├── [playerId]/
│   │   │   │   │   └── page.tsx      # Individual player
│   │   │   │   └── compare/
│   │   │   │       └── page.tsx      # Compare players
│   │   │   ├── games/
│   │   │   │   ├── page.tsx          # Recent games
│   │   │   │   └── [gameId]/
│   │   │   │       ├── page.tsx      # Game summary
│   │   │   │       ├── play-by-play/
│   │   │   │       │   └── page.tsx
│   │   │   │       └── shots/
│   │   │   │           └── page.tsx
│   │   │   └── analytics/
│   │   │       ├── shifts/
│   │   │       │   └── page.tsx
│   │   │       └── trends/
│   │   │           └── page.tsx
│   │   │
│   │   └── api/                      # API routes (optional)
│   │       └── revalidate/
│   │           └── route.ts          # On-demand revalidation
│   │
│   ├── components/
│   │   ├── ui/                       # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── table.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── badge.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/                   # Layout components
│   │   │   ├── sidebar.tsx
│   │   │   ├── topbar.tsx
│   │   │   ├── nav-item.tsx
│   │   │   └── theme-provider.tsx
│   │   │
│   │   ├── hockey/                   # Hockey-specific components
│   │   │   ├── rink.tsx              # SVG hockey rink
│   │   │   ├── shot-chart.tsx
│   │   │   ├── shift-timeline.tsx
│   │   │   ├── momentum-chart.tsx
│   │   │   └── event-marker.tsx
│   │   │
│   │   ├── teams/                    # Team components
│   │   │   ├── team-logo.tsx
│   │   │   ├── team-card.tsx
│   │   │   ├── team-header.tsx
│   │   │   └── standings-table.tsx
│   │   │
│   │   ├── players/                  # Player components
│   │   │   ├── player-photo.tsx
│   │   │   ├── player-card.tsx
│   │   │   ├── player-stats.tsx
│   │   │   ├── career-table.tsx
│   │   │   └── radar-chart.tsx
│   │   │
│   │   ├── games/                    # Game components
│   │   │   ├── scoreboard.tsx
│   │   │   ├── scoring-summary.tsx
│   │   │   ├── three-stars.tsx
│   │   │   ├── box-score.tsx
│   │   │   └── play-by-play-list.tsx
│   │   │
│   │   └── charts/                   # Chart components
│   │       ├── bar-chart.tsx
│   │       ├── line-chart.tsx
│   │       ├── stat-comparison.tsx
│   │       └── trend-chart.tsx
│   │
│   ├── lib/
│   │   ├── supabase/
│   │   │   ├── client.ts             # Supabase client setup
│   │   │   ├── server.ts             # Server-side client
│   │   │   └── queries/
│   │   │       ├── teams.ts          # Team queries
│   │   │       ├── players.ts        # Player queries
│   │   │       ├── games.ts          # Game queries
│   │   │       ├── standings.ts      # Standings queries
│   │   │       └── stats.ts          # Stats aggregations
│   │   │
│   │   ├── utils/
│   │   │   ├── format.ts             # formatTime, formatDate, etc.
│   │   │   ├── calculations.ts       # GAA, PPG, etc.
│   │   │   └── cn.ts                 # className helper
│   │   │
│   │   └── constants/
│   │       ├── theme.ts              # Colors, fonts
│   │       ├── navigation.ts         # Nav structure
│   │       └── hockey.ts             # Rink dimensions, etc.
│   │
│   └── types/
│       ├── database.ts               # Supabase generated types
│       ├── team.ts
│       ├── player.ts
│       ├── game.ts
│       └── stats.ts
│
├── public/
│   ├── norad-logo.png                # Downloaded NORAD logo
│   └── fonts/                        # Self-hosted fonts (optional)
│
├── .env.local                        # Environment variables
├── .env.example                      # Example env file
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

## 🚀 Step-by-Step Setup

### Step 1: Create Next.js Project

```bash
# Create new Next.js project with TypeScript, Tailwind, ESLint, App Router
npx create-next-app@latest benchsight-dashboard --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

cd benchsight-dashboard
```

### Step 2: Install Dependencies

```bash
# Core dependencies
npm install @supabase/supabase-js @supabase/ssr

# UI Components (shadcn/ui)
npx shadcn-ui@latest init
# Choose: New York style, Slate color, CSS variables: yes

# Add shadcn components
npx shadcn-ui@latest add button card table tabs badge skeleton
npx shadcn-ui@latest add dropdown-menu navigation-menu avatar
npx shadcn-ui@latest add select input label separator

# Charts
npm install recharts

# Utilities
npm install clsx tailwind-merge
npm install date-fns              # Date formatting
npm install lucide-react          # Icons

# Dev dependencies
npm install -D @types/node
```

### Step 3: Environment Variables

```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Optional: For server-side operations
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Step 4: Supabase Client Setup

```typescript
// src/lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr'
import { Database } from '@/types/database'

export function createClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

```typescript
// src/lib/supabase/server.ts
import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { Database } from '@/types/database'

export function createClient() {
  const cookieStore = cookies()

  return createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value
        },
      },
    }
  )
}
```

### Step 5: Generate TypeScript Types from Supabase

```bash
# Install Supabase CLI
npm install -D supabase

# Login to Supabase
npx supabase login

# Generate types from your database
npx supabase gen types typescript --project-id your-project-id > src/types/database.ts
```

### Step 6: Tailwind Configuration

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // NORAD Theme
        background: "hsl(222, 47%, 5%)",      // #0a0e17
        foreground: "hsl(210, 40%, 96%)",     // #f1f5f9
        card: {
          DEFAULT: "hsl(222, 47%, 7%)",       // #0f1629
          foreground: "hsl(210, 40%, 96%)",
        },
        primary: {
          DEFAULT: "hsl(215, 20%, 65%)",      // #94a3b8
          foreground: "hsl(222, 47%, 5%)",
        },
        muted: {
          DEFAULT: "hsl(217, 33%, 17%)",      // #1a2744
          foreground: "hsl(215, 16%, 47%)",   // #64748b
        },
        accent: {
          DEFAULT: "hsl(220, 40%, 8%)",       // #0c1220
          foreground: "hsl(210, 40%, 96%)",
        },
        border: "hsl(213, 50%, 24%)",         // #1e3a5f
        
        // Hockey colors
        goal: "hsl(0, 84%, 60%)",             // #ef4444
        assist: "hsl(45, 93%, 58%)",          // #fbbf24
        save: "hsl(142, 71%, 45%)",           // #22c55e
        shot: "hsl(217, 91%, 60%)",           // #3b82f6
        hit: "hsl(330, 81%, 60%)",            // #ec4899
        penalty: "hsl(25, 95%, 53%)",         // #f97316
        faceoff: "hsl(258, 90%, 66%)",        // #8b5cf6
      },
      fontFamily: {
        display: ["var(--font-rajdhani)", "sans-serif"],
        body: ["var(--font-inter)", "sans-serif"],
        mono: ["var(--font-jetbrains)", "monospace"],
      },
      borderRadius: {
        lg: "0.75rem",
        md: "0.5rem",
        sm: "0.375rem",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

export default config
```

### Step 7: Root Layout with Fonts

```typescript
// src/app/layout.tsx
import type { Metadata } from "next"
import { Inter, Rajdhani, JetBrains_Mono } from "next/font/google"
import "./globals.css"
import { cn } from "@/lib/utils"

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
})

const rajdhani = Rajdhani({ 
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-rajdhani",
})

const jetbrains = JetBrains_Mono({ 
  subsets: ["latin"],
  variable: "--font-jetbrains",
})

export const metadata: Metadata = {
  title: "BenchSight - NORAD Hockey Analytics",
  description: "Advanced analytics for the NORAD recreational hockey league",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={cn(
        inter.variable,
        rajdhani.variable,
        jetbrains.variable,
        "font-body bg-background text-foreground antialiased"
      )}>
        {children}
      </body>
    </html>
  )
}
```

## 📊 Data Fetching Pattern

### Server Components (Recommended)

```typescript
// src/app/(dashboard)/standings/page.tsx
import { createClient } from "@/lib/supabase/server"
import { StandingsTable } from "@/components/teams/standings-table"

export const revalidate = 300 // Revalidate every 5 minutes

export default async function StandingsPage() {
  const supabase = createClient()
  
  const { data: standings } = await supabase
    .from('v_standings')  // Use a view for complex queries
    .select('*')
    .order('points', { ascending: false })
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-wider uppercase">
          League Standings
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          2025-2026 Regular Season
        </p>
      </div>
      
      <StandingsTable standings={standings ?? []} />
    </div>
  )
}
```

### Dynamic Routes

```typescript
// src/app/(dashboard)/players/[playerId]/page.tsx
import { createClient } from "@/lib/supabase/server"
import { notFound } from "next/navigation"
import { PlayerHeader } from "@/components/players/player-header"
import { PlayerStats } from "@/components/players/player-stats"

interface Props {
  params: { playerId: string }
}

export default async function PlayerPage({ params }: Props) {
  const supabase = createClient()
  
  const { data: player } = await supabase
    .from('dim_player')
    .select(`
      *,
      team:dim_team(*)
    `)
    .eq('player_id', params.playerId)
    .single()
  
  if (!player) notFound()
  
  const { data: stats } = await supabase
    .from('v_player_season_stats')
    .select('*')
    .eq('player_id', params.playerId)
  
  return (
    <div className="space-y-6">
      <PlayerHeader player={player} />
      <PlayerStats stats={stats ?? []} />
    </div>
  )
}
```

## 🎨 Component Pattern

```typescript
// src/components/teams/team-logo.tsx
import Image from "next/image"
import { cn } from "@/lib/utils"

interface TeamLogoProps {
  src: string | null
  name: string
  primaryColor?: string
  secondaryColor?: string
  size?: "sm" | "md" | "lg"
  className?: string
}

const sizes = {
  sm: "w-6 h-6",
  md: "w-10 h-10",
  lg: "w-20 h-20",
}

export function TeamLogo({
  src,
  name,
  primaryColor = "#1e40af",
  secondaryColor = "#3b82f6",
  size = "md",
  className,
}: TeamLogoProps) {
  return (
    <div
      className={cn(
        "rounded-lg flex items-center justify-center p-1",
        sizes[size],
        className
      )}
      style={{
        background: `linear-gradient(135deg, ${primaryColor}, ${secondaryColor})`,
      }}
    >
      {src ? (
        <Image
          src={src}
          alt={name}
          width={size === "lg" ? 64 : size === "md" ? 32 : 20}
          height={size === "lg" ? 64 : size === "md" ? 32 : 20}
          className="object-contain"
        />
      ) : (
        <span className="font-display text-white font-bold">
          {name.substring(0, 2).toUpperCase()}
        </span>
      )}
    </div>
  )
}
```

## 🚀 Deployment

### Vercel (Recommended)

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/benchsight-dashboard.git
git push -u origin main

# 2. Connect to Vercel
# Go to vercel.com, import your GitHub repo

# 3. Add environment variables in Vercel dashboard:
# NEXT_PUBLIC_SUPABASE_URL
# NEXT_PUBLIC_SUPABASE_ANON_KEY

# 4. Deploy!
# Vercel auto-deploys on every push to main
```

### Custom Domain (Optional)

1. In Vercel dashboard → Settings → Domains
2. Add `benchsight.noradhockey.com`
3. Update DNS records as instructed

## 📋 Development Workflow

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Run production build locally
npm start

# Type check
npm run lint

# Generate Supabase types (after schema changes)
npx supabase gen types typescript --project-id your-project-id > src/types/database.ts
```

## 🔄 Caching Strategy

```typescript
// Page-level caching
export const revalidate = 300 // 5 minutes for standings

// Or use on-demand revalidation
// src/app/api/revalidate/route.ts
import { revalidatePath } from 'next/cache'
import { NextRequest } from 'next/server'

export async function POST(request: NextRequest) {
  const { path, secret } = await request.json()
  
  if (secret !== process.env.REVALIDATION_SECRET) {
    return Response.json({ error: 'Invalid secret' }, { status: 401 })
  }
  
  revalidatePath(path)
  return Response.json({ revalidated: true })
}
```

## ✅ Pre-Launch Checklist

- [ ] Supabase connection working
- [ ] All pages load without errors
- [ ] TypeScript types generated
- [ ] Environment variables set in Vercel
- [ ] Images loading (team logos, player photos)
- [ ] Responsive design tested
- [ ] Performance audit (Lighthouse)
- [ ] Error boundaries in place
- [ ] 404 page styled
- [ ] Loading states implemented
