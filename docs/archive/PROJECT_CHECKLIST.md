# BenchSight Project Checklist

**Pre-flight checklists for common tasks**

Last Updated: 2026-01-15  
Version: 29.0

---

## Overview

This document provides checklists for common tasks to ensure nothing is missed and everything is done correctly.

---

## Before Starting Development

### Environment Setup

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Supabase account configured
- [ ] Vercel account configured (for dashboard)
- [ ] Environment variables set up
- [ ] Dependencies installed
  - [ ] ETL: `pip install -r requirements.txt`
  - [ ] Dashboard: `cd ui/dashboard && npm install`
  - [ ] API: `cd api && pip install -r requirements.txt`
- [ ] Dev environment switched: `./benchsight.sh env switch dev`
- [ ] Environment status checked: `./benchsight.sh env status`

### Project Status

- [ ] Project status checked: `./benchsight.sh status`
- [ ] Documentation reviewed: `./benchsight.sh docs`
- [ ] Current phase understood (see [MASTER_ROADMAP.md](MASTER_ROADMAP.md))
- [ ] Project scope reviewed (see [PROJECT_SCOPE.md](PROJECT_SCOPE.md))

---

## Before Committing Code

### Code Quality

- [ ] Code follows [MASTER_RULES.md](MASTER_RULES.md)
- [ ] No TypeScript errors
- [ ] No Python syntax errors
- [ ] No console errors
- [ ] Code is readable and well-formatted
- [ ] Functions are < 300 lines
- [ ] Files are < 1000 lines
- [ ] No `.iterrows()` used (use vectorized operations)
- [ ] Goal counting uses correct filter (see [MASTER_RULES.md](MASTER_RULES.md))

### Testing

- [ ] Manual testing completed
- [ ] ETL validation passes (if ETL changes): `./benchsight.sh etl validate`
- [ ] API tests pass (if API changes): `./benchsight.sh api test`
- [ ] Dashboard pages load correctly (if dashboard changes)
- [ ] No regressions introduced

### Documentation

- [ ] Code comments added where needed
- [ ] Docstrings added to new functions
- [ ] Type hints added (Python)
- [ ] Interfaces defined (TypeScript)
- [ ] Relevant documentation updated
- [ ] [MASTER_INDEX.md](MASTER_INDEX.md) updated (if new docs added)

### Git

- [ ] Changes staged: `git add .`
- [ ] Commit message follows format: `[TYPE] Description`
- [ ] Commit message is descriptive
- [ ] Related files committed together
- [ ] No sensitive data in commits
- [ ] `.env` files not committed

---

## Before Creating Pull Request

### Code Review (Self-Review)

- [ ] Code reviewed for quality
- [ ] Logic reviewed for correctness
- [ ] Performance implications considered
- [ ] Security implications considered
- [ ] Error handling reviewed
- [ ] Edge cases considered

### Testing

- [ ] All tests pass
- [ ] Validation passes
- [ ] Manual testing completed
- [ ] Edge cases tested
- [ ] Error cases tested

### Documentation

- [ ] PR description written
- [ ] Changes documented
- [ ] Related issues linked
- [ ] Screenshots added (if UI changes)
- [ ] Breaking changes documented

### Git

- [ ] Feature branch created
- [ ] Changes committed
- [ ] Branch pushed to remote
- [ ] Branch is up to date with develop

---

## Before Deploying to Dev

### Pre-Deployment

- [ ] Dev environment switched: `./benchsight.sh env switch dev`
- [ ] Environment status checked: `./benchsight.sh env status`
- [ ] All tests pass
- [ ] Validation passes
- [ ] Code reviewed and approved

### ETL Deployment

- [ ] ETL run completed: `./benchsight.sh etl run`
- [ ] ETL validated: `./benchsight.sh etl validate`
- [ ] Goal counts verified
- [ ] Table counts verified (139 tables)
- [ ] Data integrity checked

### Database Deployment

- [ ] Schema generated (if schema changes): `./benchsight.sh db schema`
- [ ] Schema applied in Supabase SQL Editor
- [ ] Tables uploaded: `./benchsight.sh db upload`
- [ ] Data verified in Supabase

### Dashboard Deployment

- [ ] Dashboard builds: `./benchsight.sh dashboard build`
- [ ] No build errors
- [ ] Environment variables set
- [ ] Deployed: `./benchsight.sh dashboard deploy`
- [ ] Dashboard accessible and working

### API Deployment

- [ ] API tests pass: `./benchsight.sh api test`
- [ ] Environment variables set
- [ ] Deployed via Railway/Render
- [ ] Health check passes
- [ ] API docs accessible

---

## Before Deploying to Production

### Pre-Deployment

- [ ] Production environment switched: `./benchsight.sh env switch production`
- [ ] Environment status checked: `./benchsight.sh env status`
- [ ] All tests pass
- [ ] Validation passes
- [ ] Code reviewed and approved
- [ ] Backup created (if applicable)

### ETL Deployment

- [ ] ETL run completed: `./benchsight.sh etl run`
- [ ] ETL validated: `./benchsight.sh etl validate`
- [ ] Goal counts verified
- [ ] Table counts verified
- [ ] Data integrity checked
- [ ] Performance acceptable

### Database Deployment

- [ ] Backup created
- [ ] Schema reviewed
- [ ] Schema applied (if changes)
- [ ] Tables uploaded: `./benchsight.sh db upload`
- [ ] Data verified
- [ ] Views deployed (if changes)

### Dashboard Deployment

- [ ] Dashboard builds: `./benchsight.sh dashboard build`
- [ ] Production build tested
- [ ] Environment variables verified
- [ ] Deployed: `./benchsight.sh dashboard deploy`
- [ ] Dashboard accessible and working
- [ ] Performance acceptable

### API Deployment

- [ ] API tests pass
- [ ] Environment variables verified
- [ ] Deployed via Railway/Render
- [ ] Health check passes
- [ ] API docs accessible
- [ ] Performance acceptable

### Post-Deployment

- [ ] All components working
- [ ] Data loading correctly
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Monitoring set up (if applicable)

---

## Weekly Maintenance

### Data Quality

- [ ] ETL validation run: `./benchsight.sh etl validate`
- [ ] Goal counts verified
- [ ] Data integrity checked
- [ ] Table counts verified

### Code Quality

- [ ] Dependencies updated (if needed)
- [ ] Security vulnerabilities checked
- [ ] Code review completed
- [ ] Documentation reviewed

### System Health

- [ ] Logs reviewed
- [ ] Error logs checked
- [ ] Performance metrics reviewed
- [ ] Database size checked
- [ ] Backup verified (if applicable)

### Documentation

- [ ] Documentation updated (if needed)
- [ ] Status documents updated
- [ ] Roadmap reviewed
- [ ] Next steps reviewed

---

## Monthly Maintenance

### Comprehensive Review

- [ ] Full ETL validation
- [ ] All tests run
- [ ] Code quality review
- [ ] Documentation review
- [ ] Performance review
- [ ] Security review

### Updates

- [ ] Dependencies updated
- [ ] Security patches applied
- [ ] Documentation updated
- [ ] Roadmap updated
- [ ] Status updated

### Planning

- [ ] Next month priorities set
- [ ] Roadmap reviewed
- [ ] Technical debt assessed
- [ ] Improvements planned

---

## Emergency Procedures

### When ETL Fails

- [ ] Check logs: `tail -f logs/etl_v5.log`
- [ ] Check data files
- [ ] Verify configuration
- [ ] Run validation: `./benchsight.sh etl validate`
- [ ] Check error messages
- [ ] Review recent changes

### When Dashboard Breaks

- [ ] Check browser console
- [ ] Check server logs
- [ ] Verify environment variables
- [ ] Check Supabase connection
- [ ] Review recent changes
- [ ] Check build errors

### When API Fails

- [ ] Check API logs
- [ ] Check health endpoint
- [ ] Verify database connection
- [ ] Check environment variables
- [ ] Review recent changes
- [ ] Check deployment status

### When Data is Corrupted

- [ ] Stop all operations
- [ ] Check backup availability
- [ ] Review recent changes
- [ ] Check validation results
- [ ] Restore from backup (if needed)
- [ ] Re-run ETL (if needed)

---

## Related Documentation

- [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) - Development workflows
- [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md) - Maintenance guide
- [MASTER_RULES.md](MASTER_RULES.md) - Rules and standards
- [COMMANDS.md](COMMANDS.md) - Command reference

---

*Last Updated: 2026-01-15*
