---
name: pr-workflow
description: Complete PR creation workflow including validation, documentation, and proper formatting. Use when ready to create a pull request.
allowed-tools: Bash, Read, Write, Task
argument-hint: [title]
---

# PR Workflow

Create a properly validated pull request.

## Pre-PR Checklist

Before creating a PR, this workflow ensures:

1. ✅ All code compiles/builds
2. ✅ Tests pass
3. ✅ ETL validation passes (if applicable)
4. ✅ CLAUDE.md compliance verified
5. ✅ Documentation updated
6. ✅ No merge conflicts
7. ✅ Commit messages follow format

## Workflow Steps

### Step 1: Run Post-Code Validation
```bash
/post-code
```

Must pass before continuing.

### Step 2: Check Branch Status
```bash
# Ensure on feature branch
git branch --show-current

# Check for uncommitted changes
git status

# Check if up to date with develop
git fetch origin develop
git log develop..HEAD --oneline
```

### Step 3: Prepare Commits
```bash
# Stage changes
git add -A

# Commit with proper format
git commit -m "[TYPE] Brief description

Detailed explanation if needed.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Commit Types:**
- `[FEAT]` - New feature
- `[FIX]` - Bug fix
- `[DOCS]` - Documentation
- `[REFACTOR]` - Code refactoring
- `[TEST]` - Tests
- `[CHORE]` - Maintenance

### Step 4: Push Branch
```bash
git push -u origin $(git branch --show-current)
```

### Step 5: Create PR
```bash
gh pr create \
  --title "[TYPE] Brief description" \
  --body "$(cat <<'EOF'
## Summary
- Change 1
- Change 2
- Change 3

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] ETL validation passes
- [ ] Dashboard builds successfully

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings

## Related Issues
Closes #XXX

---
🤖 Generated with Claude Code
EOF
)" \
  --base develop
```

### Step 6: Post-PR Actions
```bash
# Get PR URL
gh pr view --web

# Add reviewers (optional)
gh pr edit --add-reviewer @username

# Add labels
gh pr edit --add-label "feature"
```

## PR Template

```markdown
## Summary
<!-- Brief description of changes -->

## Type of Change
- [ ] 🐛 Bug fix (non-breaking change fixing an issue)
- [ ] ✨ New feature (non-breaking change adding functionality)
- [ ] 💥 Breaking change (fix or feature causing existing functionality to change)
- [ ] 📚 Documentation update
- [ ] 🔧 Refactoring (no functional changes)
- [ ] 🧪 Tests (adding or updating tests)

## Changes Made
<!-- List specific changes -->
-
-
-

## Testing
<!-- Describe testing performed -->
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] ETL validation passes (if applicable)

## Screenshots
<!-- If UI changes, add screenshots -->

## Checklist
- [ ] Code follows CLAUDE.md guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] All CI checks pass

## Related Issues
<!-- Link related issues -->
Closes #

---
🤖 Generated with [Claude Code](https://claude.ai/code)
```

## CodeRabbit Integration

PR will be automatically reviewed by CodeRabbit:
- Checks CLAUDE.md compliance
- Reviews code quality
- Suggests improvements

Address CodeRabbit comments before merging.

## Merge Checklist

Before merging:
1. ✅ All CI checks pass
2. ✅ CodeRabbit approved or comments addressed
3. ✅ At least 1 approval (if required)
4. ✅ No merge conflicts
5. ✅ Branch is up to date with base

## Post-Merge

```bash
# Delete feature branch
git checkout develop
git pull
git branch -d feature/xxx
git push origin --delete feature/xxx
```
