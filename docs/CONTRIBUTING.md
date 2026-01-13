# Contributing to BenchSight

**Guidelines for contributing code, documentation, and improvements**

Last Updated: 2026-01-13

---

## Welcome!

Thank you for your interest in contributing to BenchSight! This document provides guidelines and best practices for contributing.

---

## How to Contribute

### Reporting Issues

**Before creating an issue:**
1. Check existing issues to avoid duplicates
2. Verify the issue with latest code
3. Gather relevant information (error messages, logs, etc.)

**When creating an issue, include:**
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS)
- Relevant error messages or logs

### Suggesting Features

**Feature requests should include:**
- Clear description of the feature
- Use case / problem it solves
- Proposed implementation approach (if known)
- Examples or mockups (if applicable)

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow [CODE_STANDARDS.md](CODE_STANDARDS.md)
   - Write clear, maintainable code
   - Add tests for new functionality
   - Update documentation
4. **Test your changes**
   ```bash
   # Run ETL
   python run_etl.py --wipe
   
   # Run validation
   python validate.py
   
   # Run tests (if applicable)
   pytest tests/
   ```
5. **Commit your changes**
   ```bash
   git commit -m "[TYPE] Brief description"
   # Types: FIX, FEAT, DOCS, REFACTOR, TEST
   ```
6. **Push and create Pull Request**

---

## Code Standards

**Read [CODE_STANDARDS.md](CODE_STANDARDS.md) for complete guidelines.**

### Key Principles

1. **Root-Level Solutions** - Fix actual problems, not symptoms
2. **Single Source of Truth** - One canonical implementation per calculation
3. **Explicit Over Implicit** - Named constants, clear types
4. **Document Everything** - Update data dictionary and docs

### Critical Rules

**Goal Counting:**
```python
# ALWAYS use this filter for goals
GOAL_FILTER = (
    (df['event_type'] == 'Goal') & 
    (df['event_detail'] == 'Goal_Scored')
)
```

**Player Attribution:**
```python
# event_player_1 = Primary actor (scorer, shooter, passer)
# event_player_2 = Secondary actor (assist, target)
```

**Type Safety:**
```python
# Always ensure consistent types before merging
df['player_id'] = df['player_id'].astype(str)
```

---

## Development Workflow

### Setting Up Development Environment

1. **Clone and setup** (see [SETUP.md](SETUP.md))
2. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature
   ```
3. **Make changes**
4. **Test thoroughly**
   ```bash
   # Clean rebuild
   python run_etl.py --wipe
   
   # Validate
   python validate.py
   
   # Check specific functionality
   python validate.py --goals
   ```
5. **Update documentation**
   - Update relevant docs in `docs/`
   - Update `CHANGELOG.md` if significant
   - Update `DATA_DICTIONARY.md` if tables/columns change

### Testing Guidelines

**Before submitting:**
- [ ] ETL runs without errors
- [ ] All 139 tables generated
- [ ] Validation passes (`python validate.py`)
- [ ] Goal counts verified
- [ ] No new warnings or errors
- [ ] Documentation updated

### Code Review Checklist

**Reviewers should check:**
- [ ] Follows code standards
- [ ] Solves root problem (not workaround)
- [ ] Single source of truth for calculations
- [ ] Error handling is explicit
- [ ] Documentation is updated
- [ ] Tests pass
- [ ] No breaking changes (or documented)

---

## Documentation Contributions

### Updating Documentation

**When to update docs:**
- Adding new features
- Changing existing behavior
- Fixing bugs (update known issues)
- Improving clarity

**Documentation files:**
- `README.md` - Project overview
- `docs/README.md` - Documentation index
- `docs/ARCHITECTURE.md` - System design
- `docs/ETL.md` - Pipeline details
- `docs/DATA_DICTIONARY.md` - Table definitions
- `docs/CHANGELOG.md` - Version history

### Documentation Standards

- Use clear, concise language
- Include code examples where helpful
- Keep formatting consistent
- Update "Last Updated" dates
- Cross-reference related docs

---

## Commit Message Format

```
[TYPE] Brief description

Optional longer description explaining:
- What changed
- Why it changed
- Any breaking changes
```

**Types:**
- `[FIX]` - Bug fix
- `[FEAT]` - New feature
- `[DOCS]` - Documentation only
- `[REFACTOR]` - Code restructuring
- `[TEST]` - Adding/updating tests
- `[PERF]` - Performance improvement

**Examples:**
```
[FIX] Correct goal counting to use Goal_Scored filter
[FEAT] Add player career stats table
[DOCS] Update setup instructions for Python 3.11
[REFACTOR] Extract common filtering logic to utils
```

---

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**
2. **Update documentation**
3. **Check for breaking changes**
4. **Rebase on latest main** (if needed)

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] ETL runs successfully
- [ ] Validation passes
- [ ] Manual testing completed

## Checklist
- [ ] Code follows standards
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if significant)
- [ ] No breaking changes (or documented)
```

---

## Areas for Contribution

### High Priority

- **Data Validation**: Improve validation checks
- **Performance**: Optimize ETL pipeline
- **Documentation**: Improve clarity and examples
- **Testing**: Add more test coverage

### Medium Priority

- **Error Handling**: Better error messages
- **Logging**: More detailed logging
- **UI Improvements**: Tracker and dashboard enhancements
- **New Analytics**: Additional statistical calculations

### Low Priority

- **Code Refactoring**: Clean up legacy code
- **Type Hints**: Add type annotations
- **Code Comments**: Improve inline documentation

---

## Getting Help

**Questions?**
- Check existing documentation in `docs/`
- Review [CODE_STANDARDS.md](CODE_STANDARDS.md)
- Look at similar code in the codebase
- Ask in issues (use "question" label)

**Stuck?**
- Review [HANDOFF.md](HANDOFF.md) for known issues
- Check [TODO.md](TODO.md) for current priorities
- Look at recent commits for examples

---

## Code of Conduct

### Our Standards

- **Be respectful** - Treat everyone with respect
- **Be constructive** - Provide helpful feedback
- **Be patient** - Everyone learns at different paces
- **Be collaborative** - Work together toward common goals

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or inflammatory comments
- Personal attacks
- Any other unprofessional conduct

---

## Recognition

Contributors will be:
- Listed in project documentation (with permission)
- Credited in release notes
- Appreciated by the community!

---

## Questions?

If you have questions about contributing:
1. Check the documentation
2. Review existing issues/PRs
3. Create an issue with the "question" label

Thank you for contributing to BenchSight! 🏒

---

*Last updated: 2026-01-13*
