# BenchSight Maintenance Guide

**Guide for maintaining and updating the BenchSight project**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This guide provides instructions for maintaining, updating, and troubleshooting the BenchSight project.

**Scope:** ETL Pipeline, Dashboard, Tracker, Portal, API  
**Audience:** Developers, maintainers, contributors

---

## Regular Maintenance Tasks

### Daily

- [ ] Check API logs for errors
- [ ] Monitor ETL job status
- [ ] Verify dashboard is accessible
- [ ] Check Supabase connection

### Weekly

- [ ] Review error logs
- [ ] Check data quality (run validation)
- [ ] Review performance metrics
- [ ] Update dependencies (if needed)

### Monthly

- [ ] Review and update documentation
- [ ] Run full ETL validation
- [ ] Check for security updates
- [ ] Review and archive old data
- [ ] Update roadmap and status documents

---

## ETL Maintenance

### Running ETL

```bash
# Using unified CLI (recommended)
./benchsight.sh etl run                    # Full ETL run
./benchsight.sh etl run --games 18969 18977 # Specific games
./benchsight.sh etl run --wipe             # Clean rebuild

# Or using Python directly
python run_etl.py
python run_etl.py --games 18969 18977
python run_etl.py --wipe
```

### Validating ETL Output

```bash
# Using unified CLI (recommended)
./benchsight.sh etl validate

# Or using Python directly
python validate.py --quick        # Quick validation
python validate.py                # Full validation
python validate.py --table dim_player  # Specific table
```

### Common ETL Issues

**Issue: "No games found"**
- **Check:** Verify game directories exist in `data/raw/games/`
- **Fix:** Ensure tracking files are in correct format

**Issue: "Table count mismatch"**
- **Check:** Run `python run_etl.py --status`
- **Fix:** Clean and rebuild: `python run_etl.py --wipe && python run_etl.py`

**Issue: "Validation errors"**
- **Check:** Run `python validate.py` for detailed errors
- **Fix:** Review error messages and fix data issues

**Issue: "Performance degradation"**
- **Check:** Review ETL logs for slow operations
- **Fix:** Optimize pandas operations, remove `iterrows()`

### ETL Performance Optimization

```bash
# Profile ETL performance
python -m cProfile -o etl_profile.prof run_etl.py

# Analyze profile
python -m pstats etl_profile.prof
```

**Optimization Tips:**
- Use vectorized pandas operations
- Avoid `.iterrows()` (use `.apply()` or vectorized operations)
- Cache intermediate results
- Parallelize game processing (if applicable)

---

## Dashboard Maintenance

### Local Development

```bash
# Using unified CLI (recommended)
./benchsight.sh dashboard dev    # Start dev server
./benchsight.sh dashboard build  # Build for production

# Or using npm directly
cd ui/dashboard
npm run dev      # Start dev server
npm run build    # Build for production
npm start        # Run production server
```

### Common Dashboard Issues

**Issue: "Cannot connect to Supabase"**
- **Check:** Verify `.env.local` has correct Supabase credentials
- **Fix:** Update environment variables

**Issue: "Data not loading"**
- **Check:** Verify Supabase tables have data
- **Fix:** Run ETL and upload data to Supabase

**Issue: "Build errors"**
- **Check:** Review build logs for TypeScript errors
- **Fix:** Fix TypeScript errors, update dependencies

**Issue: "Performance issues"**
- **Check:** Review browser console for errors
- **Fix:** Optimize queries, add loading states, implement caching

### Dashboard Updates

```bash
# Update dependencies
cd ui/dashboard
npm update

# Check for security vulnerabilities
npm audit

# Fix security issues
npm audit fix
```

---

## API Maintenance

### Running the API

```bash
# Using unified CLI (recommended)
./benchsight.sh api dev    # Start dev server

# Or using uvicorn directly
cd api
uvicorn main:app --reload                    # Development mode
uvicorn main:app --host 0.0.0.0 --port 8000  # Production mode
```

### API Health Checks

```bash
# Check API health
curl http://localhost:8000/api/health

# Check ETL job status
curl http://localhost:8000/api/etl/status/{job_id}
```

### Common API Issues

**Issue: "API not responding"**
- **Check:** Verify API server is running
- **Fix:** Restart API server, check logs

**Issue: "Database connection errors"**
- **Check:** Verify database credentials in `.env`
- **Fix:** Update database connection string

**Issue: "Job failures"**
- **Check:** Review job logs in API
- **Fix:** Fix underlying ETL issues, retry job

### API Updates

```bash
# Update dependencies
cd api
pip install -r requirements.txt --upgrade

# Check for security vulnerabilities
pip list --outdated
```

---

## Database Maintenance

### Supabase Maintenance

**Backup:**
- Supabase handles automatic backups
- Manual backup: Export data via Supabase dashboard

**Migration:**
- Run migrations via Supabase SQL Editor
- Test migrations in development first

**Monitoring:**
- Monitor database size and performance
- Review query performance
- Check for slow queries

### Data Quality

```bash
# Run validation
python validate.py

# Check data integrity
python validate.py --fk

# Verify goal counts
python validate.py --goals
```

---

## Dependency Management

### Python Dependencies

```bash
# Update requirements
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Check for updates
pip list --outdated
```

### Node.js Dependencies

```bash
# Update package.json
npm update

# Check for security issues
npm audit

# Fix security issues
npm audit fix
```

### Rust Dependencies (Future)

```bash
# Update Cargo.toml
cargo update

# Check for updates
cargo outdated
```

---

## Logging and Monitoring

### ETL Logs

```bash
# View ETL logs
tail -f logs/etl_v5.log

# Search logs
grep "ERROR" logs/etl_v5.log
```

### API Logs

```bash
# View API logs (if using file logging)
tail -f logs/api.log

# View API logs (if using stdout)
# Check terminal output or deployment logs
```

### Dashboard Logs

- Browser console (F12)
- Server logs (if using server-side logging)
- Vercel logs (if deployed)

---

## Security Maintenance

### Environment Variables

- **Never commit** `.env` files
- **Rotate** API keys and secrets regularly
- **Use** environment-specific configs
- **Review** `.env.example` for required variables

### Dependencies

- **Update** dependencies regularly
- **Check** for security vulnerabilities
- **Fix** security issues promptly
- **Review** dependency licenses

### Access Control

- **Review** Supabase RLS policies
- **Limit** API access (if applicable)
- **Monitor** user access (future)
- **Audit** permissions regularly

---

## Documentation Maintenance

### Updating Documentation

1. **Update** relevant documentation files
2. **Update** `MASTER_INDEX.md` if adding new docs
3. **Update** `PROJECT_STATUS.md` for status changes
4. **Update** `MASTER_ROADMAP.md` for roadmap changes
5. **Review** all docs for consistency

### Documentation Standards

- Use consistent formatting
- Include last updated date
- Link to related documentation
- Keep examples up to date

---

## Troubleshooting

### Common Issues

**Issue: "ETL fails with memory error"**
- **Fix:** Process games in batches, optimize memory usage

**Issue: "Dashboard shows no data"**
- **Fix:** Verify Supabase connection, check data exists

**Issue: "API returns 500 errors"**
- **Fix:** Check API logs, verify database connection

**Issue: "Build fails"**
- **Fix:** Check dependencies, fix TypeScript errors

### Getting Help

1. **Check** documentation first
2. **Review** error logs
3. **Search** existing issues
4. **Ask** for help with specific error messages

---

## Backup and Recovery

### Data Backup

- **Supabase:** Automatic backups (daily)
- **Local Data:** Backup `data/raw/` and `data/output/`
- **Code:** Git repository (version control)

### Recovery Procedures

1. **Restore** from Supabase backup (if needed)
2. **Re-run** ETL if data is corrupted
3. **Restore** code from Git if needed
4. **Verify** recovery with validation

---

## Performance Monitoring

### ETL Performance

- Monitor ETL execution time
- Track table generation counts
- Review memory usage
- Optimize slow operations

### Dashboard Performance

- Monitor page load times
- Track query performance
- Review bundle sizes
- Optimize images and assets

### API Performance

- Monitor response times
- Track request rates
- Review database query performance
- Optimize slow endpoints

---

## Version Control

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Commit changes
git add .
git commit -m "Description of changes"

# Push to remote
git push origin feature/new-feature

# Merge to main (after review)
git checkout main
git merge feature/new-feature
```

### Branch Strategy

- **main:** Production-ready code
- **develop:** Development branch
- **feature/***: Feature branches
- **hotfix/***: Hotfix branches

---

## Related Documentation

- [PROJECT_STATUS.md](../PROJECT_STATUS.md) - Current project status
- [MASTER_ROADMAP.md](../MASTER_ROADMAP.md) - Project roadmap
- [MASTER_NEXT_STEPS.md](MASTER_NEXT_STEPS.md) - Next steps
- [DEV_ENV_COMPLETE.md](DEV_ENV_COMPLETE.md) - Development environment setup
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [COMMANDS.md](../COMMANDS.md) - Complete command reference
- [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) - Development workflows
- [PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md) - Pre-flight checklists

---

*Last Updated: 2026-01-15*
