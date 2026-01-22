---
name: env-switch
description: Switch between development and production environments for Supabase and Vercel. Use when changing deployment targets.
allowed-tools: Bash, Read
argument-hint: [dev|production]
---

# Environment Switching

Switch BenchSight between development and production environments.

## Current Environment

Check current environment:
```bash
./benchsight.sh env status
```

## Switch Environment

**To Development:**
```bash
./benchsight.sh env switch dev
```

**To Production:**
```bash
./benchsight.sh env switch production
```

## Environment Details

### Development

| Service | URL/Config |
|---------|------------|
| Supabase | amuisqvhhiigxetsfame.supabase.co |
| Dashboard | localhost:3000 |
| API | localhost:8000 |
| Portal | localhost:8080 |

**Safe for:**
- Testing new features
- Schema changes
- Data experiments
- Breaking things

### Production

| Service | URL/Config |
|---------|------------|
| Supabase | uuaowslhpgyiudmbvqze.supabase.co |
| Dashboard | Vercel deployment |
| API | Railway/cloud deployment |

**Requires:**
- Tested changes
- Passing validation
- Backup plan
- Careful execution

## Files Affected

Switching updates:
- `config/config_local.ini` - Supabase connection
- `ui/dashboard/.env.local` - Dashboard env vars
- `api/.env` - API env vars

## Verification

After switching, verify:

1. **Check config:**
```bash
cat config/config_local.ini | grep url
```

2. **Test connection:**
```bash
./benchsight.sh status
```

3. **Verify dashboard:**
```bash
cd ui/dashboard && npm run dev
# Check data loads correctly
```

## Warning

Production changes require:
- Prior testing in dev
- Passing validation suite
- Explicit confirmation
- Monitoring after deployment
