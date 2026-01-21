# Troubleshooting Guide

**Quick fixes and solutions for common BenchSight issues**

Last Updated: 2026-01-20

---

## ETL Issues

### ETL Processing Issues
- **[ETL_ISSUES_AND_FIXES.md](ETL_ISSUES_AND_FIXES.md)** - Common ETL problems and solutions
  - Games not processing
  - Empty tables
  - Column errors
  - Data validation issues

### Quick Fixes
- **[QUICK_FIX.md](QUICK_FIX.md)** - Quick fix for ETL merge errors
- **[MANUAL_FIX_INSTRUCTIONS.md](MANUAL_FIX_INSTRUCTIONS.md)** - Manual fix for rating column errors
- **[FIX_RATING_COLUMNS.md](FIX_RATING_COLUMNS.md)** - Fix for rating column KeyError
- **[FIX_EMPTY_TABLES.md](FIX_EMPTY_TABLES.md)** - Troubleshooting empty tables
- **[FIND_EXCLUDED_GAMES.md](FIND_EXCLUDED_GAMES.md)** - Finding and managing excluded games

---

## Deployment Issues

### Vercel Deployment
- **[FIX_VERCEL_SERVERLESS_SIZE.md](FIX_VERCEL_SERVERLESS_SIZE.md)** - Fix for Vercel serverless function size errors
- **[FIX_MIDDLEWARE_ERROR.md](FIX_MIDDLEWARE_ERROR.md)** - Fix for Vercel middleware errors

---

## Common Issues

### "How do I fix..."

**ETL errors:**
- Check [ETL_ISSUES_AND_FIXES.md](ETL_ISSUES_AND_FIXES.md) for common problems
- Verify game files exist and are properly formatted
- Check excluded games list

**Deployment errors:**
- Check environment variables are set correctly
- Verify Vercel project settings
- Check build logs for specific errors

**Data issues:**
- Verify Supabase connection
- Check table schemas match code
- Run validation scripts

---

## Getting Help

If these guides don't solve your issue:

1. **Check the main documentation:**
   - [docs/README.md](../README.md) - Complete documentation index
   - [docs/COMPLETE_SETUP_GUIDE.md](../COMPLETE_SETUP_GUIDE.md) - Setup guide

2. **Review error messages:**
   - Check build logs
   - Check application logs
   - Check browser console

3. **Verify configuration:**
   - Environment variables
   - Config files
   - Database connections

---

*Last updated: 2026-01-20*
