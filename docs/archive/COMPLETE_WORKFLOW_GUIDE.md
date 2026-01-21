# Complete Workflow Guide

**Exact steps for Supabase, GitHub, Vercel, agents, and MCPs**

Last Updated: 2026-01-15  
Version: 29.0

---

## Overview

This guide provides exact steps for working with all BenchSight tools and services: Supabase (dev and prod), GitHub (issues, PRs, branches), Vercel (dev and prod), AI agents, and MCPs.

**Use this guide for:**
- Daily development workflow
- Environment management
- Git operations
- Deployment procedures
- Agent selection and optimization

---

## Part 1: Daily Workflow

### Morning Routine

```bash
# 1. Check current branch
git branch

# 2. Pull latest changes
git checkout develop
git pull origin develop

# 3. Switch to dev environment
./benchsight.sh env switch dev

# 4. Verify environment
./benchsight.sh env status

# 5. Start dashboard (Terminal 1)
./benchsight.sh dashboard dev

# 6. Start API if needed (Terminal 2)
./benchsight.sh api dev
```

### During Development

- Make changes to code
- Test in browser
- Check console/logs
- Commit frequently (after logical units of work)

### End of Day

```bash
# 1. Commit changes
./benchsight.sh commit

# 2. Push to remote
git push origin feature/your-branch

# 3. Stop dev servers (Ctrl+C)
```

---

## Part 2: Git Workflow

### Branch Strategy

- `main` - Production (protected)
- `develop` - Development (default)
- `feature/*` - Features
- `fix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### When to Pull

- **Start of day** - Get latest changes
- **Before creating branch** - Start from latest
- **Before merging** - Resolve conflicts early
- **After long breaks** - Catch up on changes

### When to Commit

- **After logical unit of work** - Complete feature, fix, or refactor
- **Before switching tasks** - Save progress
- **Before pulling** - Avoid merge conflicts
- **End of day** - Don't lose work

### Commit Workflow

```bash
# 1. Check status
git status

# 2. Stage changes
git add <files>
# Or: git add .

# 3. Commit with message
./benchsight.sh commit
# Or: git commit -m "[TYPE] Description"

# 4. Push to remote
git push origin <branch>
```

### Commit Message Format

```
[TYPE] Brief description

Optional longer description
```

**Types:** `FEAT`, `FIX`, `DOCS`, `REFACTOR`, `TEST`, `DEPLOY`

---

## Part 3: GitHub Issues Workflow

### When to Create Issue

- Before starting work (always)
- When reporting bugs
- When requesting features
- When asking questions

### Issue Creation

1. Go to GitHub → Issues → New Issue
2. Choose template (bug, feature, question, refactor)
3. Fill out template
4. Link PRD if applicable
5. Assign labels
6. Submit

### Issue Lifecycle

```
New → Triage → In Progress → Review → Done
```

### Linking Issues

- In PR description: `Closes #issue-number`
- In commits: `[FIX] Fix goal counting (#42)`
- In PRDs: Reference issue number

---

## Part 4: Pull Request Workflow

### Before Creating PR

```bash
# 1. Ensure branch is up to date
git checkout develop
git pull origin develop
git checkout feature/your-branch
git merge develop  # Or rebase

# 2. Run tests/validation
./benchsight.sh etl validate
./benchsight.sh docs check

# 3. Self-review
# - Check code follows standards
# - Verify tests pass
# - Update documentation
```

### Create PR

```bash
# 1. Push branch
git push origin feature/your-branch

# 2. Create PR
./benchsight.sh review-pr
# Or: Go to GitHub → New Pull Request
```

### PR Process

1. CodeRabbit reviews automatically
2. Address CodeRabbit feedback
3. Human reviewer reviews
4. Address feedback
5. Get approval
6. Merge to `develop`

### After Merge

- Delete feature branch
- Update issue status
- Update PRD status

---

## Part 5: Supabase Workflow

### Environment Setup

**Production:**
- Project: Main Supabase project
- Config: `config/config_local.ini` (production credentials)
- Branch: `main` (Git)
- Vercel: `benchsight` project

**Development:**
- Project: Dev Supabase project (or develop branch)
- Config: `config/config_local.dev.ini` (dev credentials)
- Branch: `develop` (Git)
- Vercel: `benchsight-dev` project

### Switching Environments

```bash
# To Dev
./benchsight.sh env switch dev

# To Production (careful!)
./benchsight.sh env switch production
```

### ETL to Supabase

```bash
# 1. Switch to correct environment
./benchsight.sh env switch dev  # or production

# 2. Run ETL
./benchsight.sh etl run

# 3. Validate
./benchsight.sh etl validate

# 4. Upload to Supabase
./benchsight.sh db upload
```

### Supabase Branching (if available)

- Create branch in Supabase dashboard
- Use branch URL in config
- Merge branch when ready

---

## Part 6: Vercel Workflow

### Project Setup

**Production:**
- Project: `benchsight`
- Branch: `main`
- Environment Variables: Production Supabase credentials
- Auto-deploy: On push to `main`

**Development:**
- Project: `benchsight-dev`
- Branch: `develop`
- Environment Variables: Dev Supabase credentials
- Auto-deploy: On push to `develop`

### Deployment

**Automatic:**
- Push to `main` → Production deployment
- Push to `develop` → Dev deployment
- Push to `feature/*` → Preview deployment

**Manual:**
```bash
cd ui/dashboard
vercel --prod  # Production
vercel        # Preview
```

### Environment Variables

- Set in Vercel dashboard (per project)
- Production: Production Supabase URL/key
- Dev: Dev Supabase URL/key
- Never commit to git

---

## Part 7: Agent Usage Guide

### Cursor AI (Primary Agent)

- **Use for:** Code editing, implementation, file operations
- **When:** Daily development work
- **Context:** Auto-loads based on files you're editing
- **Optimization:** Use modular rules, reference PRDs

### Claude (via Cursor)

- **Use for:** Planning, architecture, complex problems
- **When:** Starting new features, making design decisions
- **Context:** Reference PRDs, planning docs
- **Optimization:** Use context reset strategy

### CodeRabbit

- **Use for:** Automated code review
- **When:** On every PR (automatic)
- **Context:** Reads `.coderabbit.yaml` config
- **Optimization:** Update config with BenchSight-specific rules

### MCPs (Model Context Protocol)

**Browser Extension MCP:**
- **Use for:** Testing dashboard UI, web interactions
- **When:** Testing frontend changes, debugging UI
- **How:** Use browser tools to navigate, test, screenshot

**IDE Browser MCP:**
- **Use for:** Frontend development, testing
- **When:** Working on dashboard, testing components
- **How:** Use browser tools integrated with IDE

---

## Part 8: Sub-Agents and Specialized Tools

### Planning Agent

- **Purpose:** Create PRDs, plan features
- **Context:** PRD template, planning workflow
- **Output:** Complete PRD document

### Execution Agent

- **Purpose:** Implement features
- **Context:** PRD, relevant rules
- **Output:** Working code

### Review Agent

- **Purpose:** Code review, quality checks
- **Context:** Code standards, rules
- **Output:** Review feedback

### Documentation Agent

- **Purpose:** Update documentation
- **Context:** Code changes, existing docs
- **Output:** Updated documentation

---

## Part 9: Workflow Decision Trees

### Starting New Work

```
New Task
  ↓
Is it a feature/refactor?
  ├─ Yes → Create PRD first
  │         ↓
  │      Create GitHub issue
  │         ↓
  │      Create feature branch
  │         ↓
  │      Start planning conversation
  │         ↓
  │      Complete PRD
  │         ↓
  │      Context reset
  │         ↓
  │      Start implementation
  │
  └─ No → Create GitHub issue
            ↓
         Create fix branch
            ↓
         Fix and test
            ↓
         Create PR
```

### Daily Workflow Decision

```
Start of Day
  ↓
Pull latest changes
  ↓
Switch to dev environment
  ↓
Start dev servers
  ↓
Work on current task
  ↓
Commit frequently
  ↓
End of Day
  ↓
Commit and push
  ↓
Stop dev servers
```

### PR Workflow Decision

```
Code Complete
  ↓
Self-review
  ↓
Run tests/validation
  ↓
Push to remote
  ↓
Create PR
  ↓
CodeRabbit reviews
  ↓
Address feedback
  ↓
Human review
  ↓
Address feedback
  ↓
Merge to develop
```

---

## Part 10: Model Performance Optimization

### Context Management

**Best Practices:**
1. **Use PRDs** - Single source of truth
2. **Modular rules** - Load only what's needed
3. **Context reset** - Fresh start for execution
4. **Reference docs** - Link to documentation, don't duplicate

**Avoid:**
- Long conversations without reset
- Loading all rules at once
- Duplicating context in conversation
- Mixing planning and execution

### Agent Selection

**For Planning:**
- Use Claude (via Cursor)
- Reference PRD template
- Use planning conversation template
- Focus on design and architecture

**For Implementation:**
- Use Cursor AI
- Reference PRD
- Use modular rules
- Focus on code

**For Review:**
- Use CodeRabbit (automatic)
- Use human review
- Check against standards

**For Testing:**
- Use MCP browser tools
- Test in actual browser
- Verify functionality

### MCP Usage

**Browser Extension MCP:**
- Navigate to dashboard
- Test UI interactions
- Take screenshots
- Check console errors

**IDE Browser MCP:**
- Test components
- Debug frontend
- Verify API calls

---

## Part 11: Environment-Specific Workflows

### Development Environment

**Supabase:**
- Project: Dev project or develop branch
- Config: `config_local.dev.ini`
- Switch: `./benchsight.sh env switch dev`

**Vercel:**
- Project: `benchsight-dev`
- Branch: `develop`
- Auto-deploy: On push to `develop`

**Git:**
- Branch: `develop` or `feature/*`
- Workflow: Normal development

### Production Environment

**Supabase:**
- Project: Production project
- Config: `config_local.ini`
- Switch: `./benchsight.sh env switch production` (careful!)

**Vercel:**
- Project: `benchsight`
- Branch: `main`
- Auto-deploy: On push to `main`

**Git:**
- Branch: `main` (protected)
- Workflow: PR required, approvals needed

---

## Part 12: Quick Reference Commands

### Environment Management
```bash
./benchsight.sh env switch dev         # Switch to dev
./benchsight.sh env switch production  # Switch to production
./benchsight.sh env status             # Check current environment
```

### Git Operations
```bash
git checkout develop                   # Switch to develop
git pull origin develop                # Pull latest
git checkout -b feature/name           # Create feature branch
./benchsight.sh commit                 # Smart commit
git push origin feature/name           # Push branch
./benchsight.sh review-pr              # Create PR
```

### Development
```bash
./benchsight.sh dashboard dev          # Start dashboard
./benchsight.sh api dev                # Start API
./benchsight.sh etl run                # Run ETL
./benchsight.sh etl validate           # Validate ETL
./benchsight.sh db upload              # Upload to Supabase
```

### Documentation
```bash
./benchsight.sh docs                   # Open docs
./benchsight.sh docs check             # Check docs
./benchsight.sh prd create feature x    # Create PRD
./benchsight.sh prd list               # List PRDs
```

---

## Part 13: Troubleshooting

### Common Issues

**Environment not switching:**
- Check config files exist
- Verify script permissions
- Check file paths

**Vercel not deploying:**
- Check branch configuration
- Verify environment variables
- Check build logs

**Supabase connection fails:**
- Verify credentials
- Check environment variables
- Test connection manually

**CodeRabbit not reviewing:**
- Check app installation
- Verify repository selection
- Check PR status

---

## Related Documentation

- [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) - Development workflows
- [PLANNING_WORKFLOW.md](PLANNING_WORKFLOW.md) - PRD-first development
- [CONTEXT_RESET_STRATEGY.md](CONTEXT_RESET_STRATEGY.md) - Context management
- [CODERABBIT_WORKFLOW.md](CODERABBIT_WORKFLOW.md) - CodeRabbit integration
- [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) - Complete setup

---

*Last Updated: 2026-01-15*
