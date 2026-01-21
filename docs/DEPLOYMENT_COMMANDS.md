# Deployment Commands Reference

**Quick reference for deploying to dev or production**

---

## Quick Commands

### Deploy to Development
```bash
./scripts/deploy_to_dev.sh
```

### Deploy to Production
```bash
./scripts/deploy_to_production.sh
```

### Switch Environment (Manual)
```bash
./scripts/switch_env.sh dev         # Switch to dev
./scripts/switch_env.sh production  # Switch to production
```

---

## Setup (First Time)

### 1. Set Up Environment Configs

```bash
./scripts/setup_environments.sh
```

This will:
- Create `config/config_local.develop.ini` (dev config)
- Production uses `config/config_local.ini` directly (no separate file needed)
- Prompt you to edit with correct Supabase credentials

### 2. Edit Config Files

**Dev Config:**
```bash
nano config/config_local.develop.ini
```

Update with your **dev Supabase project** credentials:
```ini
[supabase]
url = https://your-dev-project.supabase.co
service_key = your-dev-service-key
anon_key = your-dev-anon-key
```

**Production Config:**
```bash
nano config/config_local.ini  # Production config (default)
```

Update with your **production Supabase project** credentials:
```ini
[supabase]
url = https://your-prod-project.supabase.co
service_key = your-prod-service-key
anon_key = your-prod-anon-key
```

---

## Deployment Workflows

### Development Deployment

```bash
# Full dev deployment
./scripts/deploy_to_dev.sh
```

**What it does:**
1. ✅ Switches to dev environment
2. ✅ Verifies dev Supabase config
3. ✅ Runs ETL (optional)
4. ✅ Uploads to dev Supabase (optional)
5. ✅ Pushes to `develop` branch → triggers Vercel dev deploy

**Manual steps:**
```bash
# 1. Switch to dev
./scripts/switch_env.sh dev

# 2. Run ETL
python3 run_etl.py

# 3. Upload to dev Supabase
python3 upload.py

# 4. Push to develop (triggers Vercel)
git checkout develop
git add .
git commit -m "chore: dev update"
git push origin develop
```

### Production Deployment

```bash
# Full production deployment
./scripts/deploy_to_production.sh
```

**⚠️ WARNING:** This deploys to production! Requires confirmation.

**What it does:**
1. ✅ Asks for confirmation (safety check)
2. ✅ Switches to production environment
3. ✅ Verifies production Supabase config
4. ✅ Runs ETL (optional)
5. ✅ Uploads to production Supabase (optional)
6. ✅ Pushes to `main` branch → triggers Vercel production deploy

**Manual steps:**
```bash
# 1. Switch to production (careful!)
./scripts/switch_env.sh production

# 2. Run ETL
python3 run_etl.py

# 3. Upload to production Supabase
python3 upload.py

# 4. Push to main (triggers Vercel)
git checkout main
git merge develop
git push origin main
```

---

## Environment Mapping

| Environment | Config File | Supabase Project | Vercel Project | Git Branch |
|------------|-------------|------------------|-----------------|------------|
| **Dev** | `config_local.develop.ini` | Dev Supabase | `benchsight-dev` | `develop` |
| **Production** | `config_local.ini` | Prod Supabase | `benchsight` | `main` |

---

## Common Tasks

### Run ETL to Dev Only

```bash
./scripts/switch_env.sh dev
python3 run_etl.py
python3 upload.py
```

### Run ETL to Production Only

```bash
# Production uses config_local.ini directly (no switching needed)
# Just make sure config_local.ini has production credentials
python3 run_etl.py
python3 upload.py
```

### Deploy Code to Dev (No ETL)

```bash
git checkout develop
git add .
git commit -m "feat: new feature"
git push origin develop
# Vercel auto-deploys
```

### Deploy Code to Production (No ETL)

```bash
git checkout main
git merge develop
git push origin main
# Vercel auto-deploys
```

### Check Current Environment

```bash
cat config/config_local.ini | grep "url ="
# Shows which Supabase project you're connected to
```

---

## Safety Features

### Production Deployment

- ✅ Requires typing "yes" to confirm
- ✅ Shows Supabase URL before proceeding
- ✅ Multiple confirmation prompts
- ✅ Reminds you to switch back to dev

### Environment Verification

- ✅ Checks config file exists
- ✅ Shows Supabase URL for verification
- ✅ Confirms before proceeding

---

## Troubleshooting

### "Config file not found"

**Fix:**
```bash
./scripts/setup_environments.sh
# Then edit the config files with your credentials
```

### "Wrong Supabase project"

**Check:**
```bash
cat config/config_local.ini | grep "url ="
```

**Fix:**
```bash
# Switch to correct environment
./scripts/switch_env.sh dev        # For dev
./scripts/switch_env.sh production # For production
```

### "Vercel not deploying"

**Check:**
1. Is the correct branch pushed?
   - Dev: `develop` branch
   - Production: `main` branch

2. Check Vercel project settings:
   - Dev project → Production Branch = `develop`
   - Prod project → Production Branch = `main`

3. Check Vercel dashboard for deployment status

---

## Quick Reference

| Task | Command |
|------|---------|
| Setup environments | `./scripts/setup_environments.sh` |
| Deploy to dev | `./scripts/deploy_to_dev.sh` |
| Deploy to production | `./scripts/deploy_to_production.sh` |
| Switch to dev | `./scripts/switch_env.sh dev` |
| Switch to production | `./scripts/switch_env.sh production` |
| Run ETL | `python3 run_etl.py` |
| Upload to Supabase | `python3 upload.py` |
| Check environment | `cat config/config_local.ini \| grep url` |

---

## Best Practices

### ✅ Do This

1. **Always test in dev first**
   - Deploy to dev
   - Test thoroughly
   - Then deploy to production

2. **Use deployment scripts**
   - They include safety checks
   - They verify configurations
   - They guide you through the process

3. **Verify environment before deploying**
   - Check which Supabase you're connected to
   - Confirm it's the right one

4. **Switch back to dev after production work**
   - Prevents accidental production changes
   - Keeps you safe

### ❌ Don't Do This

1. **Don't deploy to production without testing**
   - Always test in dev first
   - Verify everything works

2. **Don't skip confirmations**
   - They're there for safety
   - Double-check before proceeding

3. **Don't forget to switch back to dev**
   - After production work
   - Prevents accidents

---

*Last updated: 2026-01-13*
