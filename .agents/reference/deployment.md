# Deployment Rules

**Deployment patterns and requirements**

Last Updated: 2026-01-21

---

## Deployment Architecture

### Environments

- **Development** - `develop` branch → Dev Supabase + Vercel
- **Production** - `main` branch → Prod Supabase + Vercel

### Services

- **Dashboard** - Vercel
- **API** - Railway/Render
- **Database** - Supabase

---

## Deployment Patterns

### Environment Configuration

**Use environment-specific configs:**
- `config_local.dev.ini` - Development
- `config_local.ini` - Production

**Switch environments:**
```bash
./scripts/switch_env.sh dev
./scripts/switch_env.sh production
```

---

## CI/CD

### GitHub Actions

**Workflows:**
- CI - Run tests on PR
- Code Quality - Check code quality
- Deploy Dev - Auto-deploy `develop` branch

### Deployment Process

1. Push to branch
2. CI runs
3. Tests pass
4. Deploy to environment
5. Verify deployment

---

## Related Rules

- `core.md` - Core rules
- `git.md` - Git workflow

---

*Last Updated: 2026-01-15*
