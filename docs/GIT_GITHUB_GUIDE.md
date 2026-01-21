# Git & GitHub Guide for BenchSight

**A beginner-friendly guide to version control with Git and GitHub**

---

https://gist.github.com/digitaljhelms/4287848

## What is Version Control?

**Version control** is like a time machine for your code. It lets you:
- **Save snapshots** of your code at different points in time
- **Track changes** - see exactly what changed and when
- **Collaborate** - multiple people can work on the same project
- **Undo mistakes** - go back to previous versions if something breaks
- **Work on features safely** - test new ideas without breaking the main code

Think of it like Google Docs' version history, but for code.

---

## What is Git?

**Git** is the version control system that runs on your computer. It tracks changes to your files locally.

## What is GitHub?

**GitHub** is a website that hosts your Git repositories in the cloud. It's like Dropbox for code, but with powerful collaboration features.

---

## Core Concepts

### 1. Repository (Repo)
A **repository** is your project folder that Git is tracking. It contains:
- All your code files
- A hidden `.git` folder that stores the version history
- Configuration files

### 2. Commit
A **commit** is a saved snapshot of your code at a specific point in time. It's like taking a photo of your project.

**Example:**
```bash
# You made changes to fix a bug
git add .                    # Stage the changes
git commit -m "Fix goal counting bug"  # Save the snapshot
```

### 3. Branch
A **branch** is a parallel version of your code. Think of it like:
- **Main branch** = The production-ready code (the "master copy")
- **Feature branches** = Experimental copies where you try new things

**Why use branches?**
- Work on new features without breaking the main code
- Multiple people can work on different features simultaneously
- Test changes safely before merging them

**Example workflow:**
```
main branch (stable)
    │
    ├── feature/add-goalie-stats (you're working here)
    │   └── You add new goalie calculations
    │
    └── feature/fix-etl-bug (someone else working here)
        └── They fix a data processing issue
```

### 4. Pull Request (PR)
A **pull request** is a request to merge your branch into the main branch. It's like saying:
> "Hey, I finished this feature. Can you review it and add it to the main code?"

**What happens in a PR:**
1. You create a branch and make changes
2. You push the branch to GitHub
3. You create a pull request
4. Others can review your code, comment, and suggest changes
5. Once approved, the changes are merged into main

---

## Common Git Commands

### Basic Workflow

```bash
# Check status - see what files have changed
git status

# Stage changes - tell Git which files to include in the next commit
git add .                    # Add all changed files
git add specific_file.py     # Add one specific file

# Commit - save a snapshot
git commit -m "Description of what you changed"

# Push - upload your commits to GitHub
git push origin branch-name

# Pull - download the latest changes from GitHub
git pull origin main
```

### Branch Commands

```bash
# See all branches
git branch

# Create a new branch
git checkout -b feature/my-new-feature

# Switch to a different branch
git checkout main
git checkout feature/my-new-feature

# Push a new branch to GitHub
git push -u origin feature/my-new-feature
```

---

## Typical Workflow for This Project

### Scenario: Adding a New Feature

**Step 1: Start from the latest main branch**
```bash
# Make sure you're on main and it's up to date
git checkout main
git pull origin main
```

**Step 2: Create a feature branch**
```bash
# Create and switch to a new branch
git checkout -b feature/add-player-ratings

# Example branch names:
# - feature/add-player-ratings
# - fix/goal-counting-bug
# - docs/update-readme
```

**Step 3: Make your changes**
- Edit files, add new code, test it
- Make multiple commits as you work:
```bash
git add .
git commit -m "Add player rating calculation"
git commit -m "Add tests for player ratings"
```

**Step 4: Push your branch to GitHub**
```bash
git push -u origin feature/add-player-ratings
```

**Step 5: Create a Pull Request**
1. Go to your GitHub repository
2. You'll see a banner: "feature/add-player-ratings had recent pushes"
3. Click "Compare & pull request"
4. Fill in:
   - **Title**: Brief description (e.g., "Add player ratings feature")
   - **Description**: What you changed and why
5. Click "Create pull request"

**Step 6: Review and Merge**
- Others (or you) review the code
- Make any requested changes
- Once approved, click "Merge pull request"
- Your changes are now in the main branch!

**Step 7: Clean up**
```bash
# Switch back to main
git checkout main

# Pull the latest (including your merged changes)
git pull origin main

# Delete the local branch (optional)
git branch -d feature/add-player-ratings
```

---

## Branch Naming Conventions

Use clear, descriptive names:

**Good examples:**
- `feature/add-ml-predictions`
- `fix/etl-goal-counting-bug`
- `docs/update-data-dictionary`
- `refactor/cleanup-stats-calculations`

**Bad examples:**
- `test` (too vague)
- `changes` (doesn't say what changed)
- `fix` (doesn't say what was fixed)

**Common prefixes:**
- `feature/` - New functionality
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code improvements without changing behavior
- `test/` - Adding or updating tests

---

## Pull Request Best Practices

### Writing a Good PR Description

```markdown
## What Changed
- Added player rating calculations based on advanced stats
- Created new view `v_player_ratings` in Supabase
- Updated dashboard to display ratings

## Why
Players requested a way to see overall player performance ratings.

## Testing
- Ran ETL: `python run_etl.py`
- Validated output: `python validate.py`
- Tested dashboard locally

## Related Issues
Closes #42
```

### PR Checklist
- [ ] Code follows project standards
- [ ] Tests pass (if applicable)
- [ ] Documentation updated
- [ ] No linter errors
- [ ] Tested locally

---

## Common Scenarios

### 1. Starting Fresh (First Time Setup)

```bash
# Initialize Git in your project (if not already done)
git init

# Add all files
git add .

# Make your first commit
git commit -m "Initial commit"

# Connect to GitHub (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/benchsight.git

# Push to GitHub
git push -u origin main
```

### 2. Daily Workflow

```bash
# Morning: Get latest changes
git checkout main
git pull origin main

# Work on a feature
git checkout -b feature/my-feature
# ... make changes ...
git add .
git commit -m "Description"
git push origin feature/my-feature

# End of day: Create PR on GitHub
```

### 3. Someone Else Made Changes

```bash
# Get the latest changes
git checkout main
git pull origin main

# If you have uncommitted changes, stash them first
git stash
git pull origin main
git stash pop
```

### 4. Undo a Mistake

```bash
# Undo changes to a file (before committing)
git checkout -- filename.py

# Undo the last commit (keep the changes)
git reset --soft HEAD~1

# Undo the last commit (discard the changes)
git reset --hard HEAD~1
```

### 5. See What Changed

```bash
# See what files changed
git status

# See what changed in a file
git diff filename.py

# See commit history
git log

# See what changed in a specific commit
git show commit-hash
```

---

## GitHub Interface Overview

### Repository Page
- **Code tab**: Browse files and folders
- **Issues tab**: Track bugs and feature requests
- **Pull requests tab**: See all PRs (open and closed)
- **Actions tab**: See automated workflows (CI/CD)

### Pull Request Page
- **Conversation tab**: Comments and discussion
- **Files changed tab**: See the actual code changes (diff)
- **Commits tab**: See all commits in the PR

---

## Best Practices

### 1. Commit Often
Make small, frequent commits rather than one huge commit at the end.

**Good:**
```bash
git commit -m "Add goal counting function"
git commit -m "Add tests for goal counting"
git commit -m "Update documentation"
```

**Bad:**
```bash
git commit -m "Everything"
```

### 2. Write Clear Commit Messages
```bash
# Good
git commit -m "Fix goal counting for empty net situations"
git commit -m "Add player rating calculation to dashboard"

# Bad
git commit -m "fix"
git commit -m "stuff"
```

### 3. Keep Branches Small
One feature per branch. Don't mix unrelated changes.

### 4. Test Before Pushing
Make sure your code works before creating a PR.

### 5. Keep Main Branch Stable
Only merge tested, working code into main.

---

## Troubleshooting

### "Your branch is behind"
```bash
# Get the latest changes
git checkout main
git pull origin main

# Update your feature branch
git checkout feature/your-branch
git merge main
# Or: git rebase main (more advanced)
```

### "Merge conflicts"
When Git can't automatically merge changes:
1. Git will mark the conflicted files
2. Open the files and look for `<<<<<<<`, `=======`, `>>>>>>>` markers
3. Edit to resolve the conflict
4. Stage the resolved files: `git add .`
5. Complete the merge: `git commit`

### "I committed to the wrong branch"
```bash
# Undo the commit (but keep changes)
git reset --soft HEAD~1

# Switch to correct branch
git checkout correct-branch

# Commit again
git commit -m "Your message"
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Check status | `git status` |
| Stage all changes | `git add .` |
| Commit | `git commit -m "Message"` |
| Push to GitHub | `git push origin branch-name` |
| Pull from GitHub | `git pull origin main` |
| Create branch | `git checkout -b branch-name` |
| Switch branch | `git checkout branch-name` |
| See branches | `git branch` |
| See commit history | `git log` |
| See what changed | `git diff` |

---

## Next Steps

1. **Set up your repository** (if not already done)
   - See: `docs/troubleshooting/QUICK_FIX_GITHUB_AUTH.md`

2. **Make your first commit**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. **Set up dev/sandbox environments**
   - See: [DEV_SANDBOX_SETUP.md](DEV_SANDBOX_SETUP.md) - Complete guide for separate dev/prod environments
   - See: [BRANCH_STRATEGY_QUICK_REFERENCE.md](BRANCH_STRATEGY_QUICK_REFERENCE.md) - Quick reference for branch workflow

4. **Try the workflow**
   - Create a feature branch
   - Make a small change
   - Create a pull request
   - Merge it

5. **Read more**
   - [Contributing Guide](CONTRIBUTING.md) - Project-specific guidelines
   - [GitHub Docs](https://docs.github.com) - Official GitHub documentation

---

## Questions?

- Check existing documentation in `docs/troubleshooting/`
- GitHub has excellent tutorials: https://docs.github.com/en/get-started
- Git documentation: https://git-scm.com/doc

---

*Last updated: 2026-01-13*
