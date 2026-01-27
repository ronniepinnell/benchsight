---
name: dashboard-deploy
description: Deploy dashboard to Vercel (preview or production). Use when deploying dashboard changes after validation passes.
allowed-tools: Bash, Read
argument-hint: [preview|production]
---

# Dashboard Deployment

Deploy the Next.js dashboard to Vercel.

## Pre-Deployment Checks

Before deploying, ensure:

1. **Build passes:**
```bash
cd ui/dashboard && npm run build
```

2. **Type check passes:**
```bash
cd ui/dashboard && npm run type-check
```

3. **ETL data is current:**
```bash
./benchsight.sh etl validate
```

## Deploy Commands

**Preview deployment:**
```bash
cd ui/dashboard && vercel
```

**Production deployment:**
```bash
cd ui/dashboard && vercel --prod
```

## Environment Variables

Vercel must have these configured:

| Variable | Dev | Production |
|----------|-----|------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Dev URL | Prod URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Dev key | Prod key |
| `NEXT_PUBLIC_API_URL` | localhost:8000 | Railway URL |

## Post-Deployment

1. Verify deployment at Vercel dashboard
2. Test critical pages (players, games, standings)
3. Check Supabase connection
4. Monitor for errors in Vercel logs

## Rollback

If issues found:
```bash
vercel rollback
```
