# BenchSight Development Workflow

**Standard development workflows for BenchSight**

Last Updated: 2026-01-15  
Version: 29.0

---

## Overview

This document outlines standard development workflows for working on BenchSight, including daily workflows, feature development, bug fixes, testing, and deployment.

---

## Daily Workflow

### Starting Your Day

1. **Check project status**
   ```bash
   ./benchsight.sh status
   ```

2. **Switch to dev environment** (if needed)
   ```bash
   ./benchsight.sh env switch dev
   ```

3. **Start dashboard** (Terminal 1)
   ```bash
   ./benchsight.sh dashboard dev
   ```

4. **Start API** (Terminal 2, if needed)
   ```bash
   ./benchsight.sh api dev
   ```

5. **Check documentation** (if needed)
   ```bash
   ./benchsight.sh docs
   ```

### During Development

- Keep dashboard dev server running
- Make changes to code
- Test changes in browser
- Check console for errors
- Review logs if needed

### Ending Your Day

- Stop dev servers (Ctrl+C)
- Commit changes (if ready)
- Update documentation (if needed)

---

## Feature Development Workflow

### 1. Planning (PRD-First)

1. **Create PRD**
   ```bash
   ./benchsight.sh prd create feature feature-name
   ```
   - Use PRD template: `docs/prds/template.md`
   - Document problem, solution, technical design
   - Break into phases
   - See [PLANNING_WORKFLOW.md](PLANNING_WORKFLOW.md)

2. **Review requirements**
   - Check [PROJECT_SCOPE.md](PROJECT_SCOPE.md)
   - Review [MASTER_ROADMAP.md](MASTER_ROADMAP.md)
   - Check [PROJECT_STATUS.md](PROJECT_STATUS.md)

3. **Design feature**
   - Plan component structure
   - Design data flow
   - Identify dependencies

4. **Context Reset**
   - After planning, start new conversation
   - Reference PRD in execution
   - See [CONTEXT_RESET_STRATEGY.md](CONTEXT_RESET_STRATEGY.md)

5. **Create feature branch**
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
   - Follow [MASTER_RULES.md](MASTER_RULES.md)
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
   git commit -m "[FEAT] Add feature description

   - Detail 1
   - Detail 2
   - Detail 3"
   ```

3. **Push to remote**
   ```bash
   git push origin feature/feature-name
   ```

### 5. Integration

1. **Create pull request**
   - Describe changes
   - Link related issues
   - Request review

2. **Address feedback**
   - Make requested changes
   - Update documentation
   - Re-test

3. **Merge to develop**
   - After approval
   - Merge via PR
   - Delete feature branch

---

## Bug Fix Workflow

### 1. Identify Bug

1. **Reproduce bug**
   - Document steps to reproduce
   - Note expected vs actual behavior
   - Capture error messages

2. **Investigate**
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
   - Follow [MASTER_RULES.md](MASTER_RULES.md)
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
   git commit -m "[FIX] Fix bug description

   - Root cause
   - Solution
   - Testing"
   ```

### 4. Deploy Fix

1. **Push and create PR**
   ```bash
   git push origin fix/bug-description
   ```

2. **Merge after review**
   - Get approval
   - Merge to develop
   - Test in dev environment

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
   - Update [API_REFERENCE.md](API_REFERENCE.md)
   - Document new endpoints
   - Update examples

3. **Project documentation**
   - Update [PROJECT_STATUS.md](PROJECT_STATUS.md)
   - Update [MASTER_ROADMAP.md](MASTER_ROADMAP.md)
   - Update relevant component docs

4. **Update index**
   - Update [MASTER_INDEX.md](MASTER_INDEX.md) if new docs added

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

## Code Review Checklist

### Before Submitting PR

- [ ] Code follows [MASTER_RULES.md](MASTER_RULES.md)
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

## Troubleshooting Workflow

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

---

## Best Practices

### Code Quality

- Follow [MASTER_RULES.md](MASTER_RULES.md)
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

- [MASTER_RULES.md](MASTER_RULES.md) - Rules and standards
- [PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md) - Pre-flight checklist
- [COMMANDS.md](COMMANDS.md) - Command reference
- [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md) - Maintenance guide
- [COMPLETE_WORKFLOW_GUIDE.md](COMPLETE_WORKFLOW_GUIDE.md) - Complete workflow for Supabase, GitHub, Vercel, agents, MCPs
- [PRE_RESTRUCTURING_CHECKLIST.md](PRE_RESTRUCTURING_CHECKLIST.md) - Pre-restructuring preparation checklist
- [PLANNING_WORKFLOW.md](PLANNING_WORKFLOW.md) - PRD-first development
- [CONTEXT_RESET_STRATEGY.md](CONTEXT_RESET_STRATEGY.md) - Context management strategy

---

*Last Updated: 2026-01-15*
