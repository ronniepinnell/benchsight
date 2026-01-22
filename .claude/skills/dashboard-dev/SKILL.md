---
name: dashboard-dev
description: Start dashboard development server and prepare development environment. Use when working on dashboard features, debugging UI issues, or testing local changes.
allowed-tools: Bash, Read, Grep
---

# Dashboard Development

Start the Next.js dashboard in development mode.

## Quick Start

```bash
cd ui/dashboard && npm run dev
```

Dashboard runs at: http://localhost:3000

## Development Environment

**Supabase (Dev):**
- URL: https://amuisqvhhiigxetsfame.supabase.co
- Uses development database (safe for testing)

**Key Paths:**
- Pages: `ui/dashboard/src/app/`
- Components: `ui/dashboard/src/components/`
- Lib: `ui/dashboard/src/lib/`
- Types: `ui/dashboard/src/types/`

## Common Tasks

**Type checking:**
```bash
cd ui/dashboard && npm run type-check
```

**Linting:**
```bash
cd ui/dashboard && npm run lint
```

**Build test:**
```bash
cd ui/dashboard && npm run build
```

## Architecture Rules

1. **Server Components by default** - Only use Client Components for interactivity
2. **TypeScript strict mode** - All types required
3. **shadcn/ui components** - Use existing component library
4. **Recharts for visualization** - Consistent charting
5. **Supabase queries** - Use pre-aggregated views for performance

## After Changes

Run `/validate` to ensure data integrity.
Run `/compliance-check` to verify CLAUDE.md rules.
