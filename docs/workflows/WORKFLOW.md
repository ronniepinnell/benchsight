# BenchSight Workflow Guide

**Complete development workflows: daily operations, Git, GitHub, Supabase, Vercel, agents, and MCPs**

Last Updated: 2026-01-15  
Version: 1.0

---

## Table of Contents

1. [Daily Workflow](#daily-workflow)
2. [Feature Development](#feature-development)
3. [Bug Fix Workflow](#bug-fix-workflow)
4. [Git Workflow](#git-workflow)
5. [GitHub Workflow](#github-workflow)
6. [Supabase Workflow](#supabase-workflow)
7. [Vercel Workflow](#vercel-workflow)
8. [Testing Workflow](#testing-workflow)
9. [Documentation Workflow](#documentation-workflow)
10. [Deployment Workflow](#deployment-workflow)
11. [Agent Usage Guide](#agent-usage-guide)
12. [Troubleshooting](#troubleshooting)
13. [Quick Reference](#quick-reference)

---

## Daily Workflow

### Morning Routine

```bash
# 1. Check current branch
git branch

# 2. Pull latest changes
git checkout develop
git pull origin develop

# 3. Check project status
./benchsight.sh status

# 4. Switch to dev environment
./benchsight.sh env switch dev

# 5. Verify environment
./benchsight.sh env status

# 6. Start dashboard (Terminal 1)
./benchsight.sh dashboard dev

# 7. Start API if needed (Terminal 2)
./benchsight.sh api dev

# 8. Check documentation (if needed)
./benchsight.sh docs
```

### During Development

- Keep dashboard dev server running
- Make changes to code
- Test changes in browser
- Check console for errors
- Review logs if needed
- Commit frequently (after logical units of work)

### End of Day

```bash
# 1. Commit changes
./benchsight.sh commit

# 2. Push to remote
git push origin feature/your-branch

# 3. Stop dev servers (Ctrl+C)

# 4. Update documentation (if needed)
```

---

## Feature Development

### 1. Planning (PRD-First)

1. **Create PRD**
   ```bash
   ./benchsight.sh prd create feature feature-name
   ```
   - Use PRD template: `docs/prds/template.md`
   - Document problem, solution, technical design
   - Break into phases
   - See [PLANNING_WORKFLOW.md](PLANNING_WORKFLOW.md)

2. **Create GitHub Issue**
   - Go to GitHub → Issues → New Issue
   - Choose feature template
   - Link PRD
   - Assign labels

3. **Review requirements**
   - Check [PROJECT_SCOPE.md](../PROJECT_SCOPE.md)
   - Review [MASTER_ROADMAP.md](../MASTER_ROADMAP.md)
   - Check [PROJECT_STATUS.md](../PROJECT_STATUS.md)

4. **Design feature**
   - Plan component structure
   - Design data flow
   - Identify dependencies

5. **Context Reset**
   - After planning, start new conversation
   - Reference PRD in execution
   - See [CONTEXT_RESET_STRATEGY.md](CONTEXT_RESET_STRATEGY.md)

6. **Create feature branch**
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/feature-name
   ```

### 2. Development

1. **Set up environment**
   ```bash
   ./benchsight.sh env switch dev
   ./benchsight.sh dashboard dev
   ```

2. **Implement feature**
   - Write code
   - Follow [MASTER_RULES.md](../MASTER_RULES.md)
   - Use existing patterns
   - Test as you go

3. **Test feature**
   - Manual testing
   - Check browser console
   - Verify data flow
   - Test edge cases

4. **Update documentation**
   - Update relevant docs
   - Add code comments
   - Update API docs (if API changes)

### 3. Validation

1. **Run validation**
   ```bash
   ./benchsight.sh etl validate  # If ETL changes
   ./benchsight.sh api test      # If API changes
   ```

2. **Check for errors**
   - Review logs
   - Check console
   - Verify data integrity

3. **Code review** (self-review)
   - Check code quality
   - Verify naming conventions
   - Ensure documentation updated

### 4. Commit

1. **Stage changes**
   ```bash
   git add .
   ```

2. **Commit with proper format**
   ```bash
   ./benchsight.sh commit
   # Or: git commit -m "[FEAT] Add feature description
   #
   # - Detail 1
   # - Detail 2
   # - Detail 3"
   ```

3. **Push to remote**
   ```bash
   git push origin feature/feature-name
   ```

### 5. Integration

1. **Create pull request**
   ```bash
   ./benchsight.sh review-pr
   # Or: Go to GitHub → New Pull Request
   ```
   - Describe changes
   - Link related issues
   - Link PRD
   - Request review

2. **PR Process**
   - CodeRabbit reviews automatically
   - Address CodeRabbit feedback
   - Human reviewer reviews
   - Address feedback
   - Get approval

3. **Merge to develop**
   - After approval
   - Merge via PR
   - Delete feature branch
   - Update issue status
   - Update PRD status

---

## Bug Fix Workflow

### 1. Identify Bug

1. **Reproduce bug**
   - Document steps to reproduce
   - Note expected vs actual behavior
   - Capture error messages

2. **Create GitHub Issue**
   - Use bug report template
   - Document reproduction steps
   - Assign labels

3. **Investigate**
   - Check logs
   - Review code
   - Trace data flow
   - Check related components

### 2. Fix Bug

1. **Create fix branch**
   ```bash
   git checkout develop
   git pull
   git checkout -b fix/bug-description
   ```

2. **Implement fix**
   - Fix root cause (not symptoms)
   - Follow [MASTER_RULES.md](../MASTER_RULES.md)
   - Test fix thoroughly

3. **Test fix**
   - Verify bug is fixed
   - Test related functionality
   - Check for regressions

### 3. Document Fix

1. **Update documentation**
   - Document fix in commit message
   - Update relevant docs
   - Add comments if needed

2. **Commit fix**
   ```bash
   git commit -m "[FIX] Fix bug description (#issue-number)

   - Root cause
   - Solution
   - Testing"
   ```

### 4. Deploy Fix

1. **Push and create PR**
   ```bash
   git push origin fix/bug-description
   ./benchsight.sh review-pr
   ```

2. **Merge after review**
   - Get approval
   - Merge to develop
   - Test in dev environment
   - Update issue status

---

## Git Workflow

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

## GitHub Workflow

### Issues

#### When to Create Issue

- Before starting work (always)
- When reporting bugs
- When requesting features
- When asking questions

#### Issue Creation

1. Go to GitHub → Issues → New Issue
2. Choose template (bug, feature, question, refactor)
3. Fill out template
4. Link PRD if applicable
5. Assign labels
6. Submit

#### Issue Lifecycle

```
New → Triage → In Progress → Review → Done
```

#### Linking Issues

- In PR description: `Closes #issue-number`
- In commits: `[FIX] Fix goal counting (#42)`
- In PRDs: Reference issue number

### Pull Requests

#### Before Creating PR

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

#### Create PR

```bash
# 1. Push branch
git push origin feature/your-branch

# 2. Create PR
./benchsight.sh review-pr
# Or: Go to GitHub → New Pull Request
```

#### PR Process

1. CodeRabbit reviews automatically
2. Address CodeRabbit feedback
3. Human reviewer reviews
4. Address feedback
5. Get approval
6. Merge to `develop`

#### After Merge

- Delete feature branch
- Update issue status
- Update PRD status

---

## Supabase Workflow

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

## Vercel Workflow

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

## Testing Workflow

### Unit Tests

1. **Write tests**
   - Location: `tests/test_*.py`
   - Test calculation functions
   - Test utility functions

2. **Run tests**
   ```bash
   pytest tests/
   ```

3. **Check coverage**
   ```bash
   pytest --cov=src tests/
   ```

### Integration Tests

1. **ETL tests**
   ```bash
   ./benchsight.sh etl run
   ./benchsight.sh etl validate
   ```

2. **API tests**
   ```bash
   ./benchsight.sh api test
   ```

3. **Dashboard tests**
   - Manual testing
   - Check all pages
   - Verify data loading

### Validation

1. **Data validation**
   ```bash
   ./benchsight.sh etl validate
   ```

2. **Check goal counts**
   - Verify goal counting
   - Check data integrity
   - Verify foreign keys

---

## Documentation Workflow

### When to Update Documentation

- New features added
- API changes
- Configuration changes
- Workflow changes
- Bug fixes (if significant)

### Documentation Files

1. **Code documentation**
   - Docstrings for functions
   - Comments for complex logic
   - Type hints

2. **API documentation**
   - Update [API.md](../api/API.md)
   - Document new endpoints
   - Update examples

3. **Project documentation**
   - Update [PROJECT_STATUS.md](../PROJECT_STATUS.md)
   - Update [MASTER_ROADMAP.md](../MASTER_ROADMAP.md)
   - Update relevant component docs

4. **Update index**
   - Update [MASTER_INDEX.md](../MASTER_INDEX.md) if new docs added

---

## Deployment Workflow

### Development Deployment

1. **Switch to dev**
   ```bash
   ./benchsight.sh env switch dev
   ```

2. **Run ETL**
   ```bash
   ./benchsight.sh etl run
   ```

3. **Upload to dev database**
   ```bash
   ./benchsight.sh db upload
   ```

4. **Deploy dashboard**
   ```bash
   ./benchsight.sh dashboard deploy
   ```

### Production Deployment

1. **Switch to production**
   ```bash
   ./benchsight.sh env switch production
   ```

2. **Verify environment**
   ```bash
   ./benchsight.sh env status
   ```

3. **Run ETL**
   ```bash
   ./benchsight.sh etl run
   ```

4. **Validate output**
   ```bash
   ./benchsight.sh etl validate
   ```

5. **Upload to production**
   ```bash
   ./benchsight.sh db upload
   ```

6. **Deploy dashboard**
   ```bash
   ./benchsight.sh dashboard build
   ./benchsight.sh dashboard deploy
   ```

7. **Deploy API**
   - See `api/DEPLOYMENT.md`
   - Deploy via Railway/Render dashboard

---

## Agent Usage Guide

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

### Sub-Agents and Specialized Tools

**Planning Agent:**
- **Purpose:** Create PRDs, plan features
- **Context:** PRD template, planning workflow
- **Output:** Complete PRD document

**Execution Agent:**
- **Purpose:** Implement features
- **Context:** PRD, relevant rules
- **Output:** Working code

**Review Agent:**
- **Purpose:** Code review, quality checks
- **Context:** Code standards, rules
- **Output:** Review feedback

**Documentation Agent:**
- **Purpose:** Update documentation
- **Context:** Code changes, existing docs
- **Output:** Updated documentation

### Model Performance Optimization

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

**Agent Selection:**

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

---

## Troubleshooting

### When Things Break

1. **Check logs**
   ```bash
   tail -f logs/etl_v5.log
   tail -f logs/api.log
   ```

2. **Check status**
   ```bash
   ./benchsight.sh status
   ./benchsight.sh env status
   ```

3. **Validate data**
   ```bash
   ./benchsight.sh etl validate
   ```

4. **Check documentation**
   ```bash
   ./benchsight.sh docs
   ```

5. **Review recent changes**
   - Check git log
   - Review recent commits
   - Check for breaking changes

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

## Quick Reference

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
git push origin feature/name          # Push branch
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

## Workflow Decision Trees

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

## Code Review Checklist

### Before Submitting PR

- [ ] Code follows [MASTER_RULES.md](../MASTER_RULES.md)
- [ ] Tests pass
- [ ] Validation passes
- [ ] Documentation updated
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] Code is readable
- [ ] Comments added where needed
- [ ] Commit message follows format

### Review Points

- Code quality
- Performance implications
- Security considerations
- Error handling
- Documentation completeness
- Test coverage

---

## Best Practices

### Code Quality

- Follow [MASTER_RULES.md](../MASTER_RULES.md)
- Write clean, readable code
- Use meaningful names
- Add comments for complex logic
- Keep functions small (< 300 lines)

### Testing

- Test before committing
- Run validation after ETL changes
- Test in dev before production
- Verify data integrity

### Documentation

- Update docs with code changes
- Keep docs in sync with code
- Document decisions
- Add examples

### Git Workflow

- Use descriptive commit messages
- Commit often
- Create feature branches
- Review before merging

---

## Related Documentation

- [MASTER_RULES.md](../MASTER_RULES.md) - Rules and standards
- [CHECKLISTS.md](../checklists/CHECKLISTS.md) - Pre-flight checklists
- [COMMANDS.md](../COMMANDS.md) - Command reference
- [MAINTENANCE_GUIDE.md](../MAINTENANCE_GUIDE.md) - Maintenance guide
- [PLANNING_WORKFLOW.md](PLANNING_WORKFLOW.md) - PRD-first development
- [CONTEXT_RESET_STRATEGY.md](CONTEXT_RESET_STRATEGY.md) - Context management strategy
- [CODERABBIT_WORKFLOW.md](CODERABBIT_WORKFLOW.md) - CodeRabbit integration

---

*Last Updated: 2026-01-15*
