# Environment Mapping Reference

**Quick reference for how environments map to configs and deployments**

---

## Environment Structure

```
Production (Default)
├── Config: config_local.ini (default, no switching)
├── Supabase: Main project/branch
├── Vercel: benchsight
└── Git Branch: main

Development
├── Config: config_local.develop.ini (switch to this)
├── Supabase: Develop branch
├── Vercel: benchsight-dev
└── Git Branch: develop
```

---

## Quick Reference

| Environment | Config File | Supabase | Vercel | Git Branch |
|------------|-------------|----------|--------|------------|
| **Production** | `config_local.ini` | Main project | `benchsight` | `main` |
| **Dev** | `config_local.develop.ini` | Develop branch | `benchsight-dev` | `develop` |

---

## Key Points

### Production
- ✅ Uses `config_local.ini` directly (default)
- ✅ No switching needed - this is the production config
- ✅ Vercel project: `benchsight`
- ✅ Git branch: `main`

### Development
- ✅ Uses `config_local.develop.ini` (must switch to this)
- ✅ Switch with: `./scripts/switch_env.sh dev`
- ✅ Vercel project: `benchsight-dev`
- ✅ Git branch: `develop`

---

## Switching Environments

### To Dev
```bash
./scripts/switch_env.sh dev
# Copies config_local.develop.ini → config_local.ini
```

### To Production
```bash
# Production uses config_local.ini directly
# No switching needed - it's already the production config
# Just make sure config_local.ini has production credentials
```

---

## URLs

**Production:**
- Vercel: `https://benchsight.vercel.app`
- Supabase: Your main project URL

**Development:**
- Vercel: `https://benchsight-dev.vercel.app`
- Supabase: Your develop branch URL

---

*Last updated: 2026-01-13*
