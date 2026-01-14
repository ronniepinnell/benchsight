# Quick Fix: Remove Large Files from Git History

## The Problem
You're getting "file too large" errors because large CSV/Excel files are in git history.

## Quick Solution

**1. Navigate to your project:**
```bash
cd ~/Documents/Documents\ -\ Ronnie\'s\ MacBook\ Pro\ -\ 1/Programming_HD/Hockey/Benchsight/git/benchsight
```

**2. Run the cleanup script:**
```bash
./scripts/clean_git_history.sh
```

**3. When prompted, type 'yes' to continue**

**4. After it finishes, force push:**
```bash
git push origin --force --all
git push origin --force --tags
```

## What It Does

1. Creates a backup branch (just in case)
2. Removes all large CSV files from git history
3. Removes all large Excel files from git history
4. Cleans up git objects to reduce size
5. Reduces .git folder from ~256MB to much smaller

## Alternative: Manual Commands

If the script doesn't work, run these commands manually:

```bash
# Navigate to project
cd ~/Documents/Documents\ -\ Ronnie\'s\ MacBook\ Pro\ -\ 1/Programming_HD/Hockey/Benchsight/git/benchsight

# Create backup
git branch backup-before-cleanup

# Remove CSV files from history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch data/output/*.csv data/output/*.json' \
  --prune-empty --tag-name-filter cat -- --all

# Remove Excel files from history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch "data/raw/games/**/*.xlsx" "data/raw/*.xlsx"' \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push origin --force --all
```

## After Cleanup

Your team members will need to:
```bash
# Re-clone the repo (safest)
git clone <your-repo-url> benchsight

# OR reset their local copy
git fetch origin
git reset --hard origin/main
```

## Prevention

The `.gitignore` file is already set up to prevent this in the future:
- `data/output/*.csv` - Excluded
- `data/raw/**/*.xlsx` - Excluded

Future commits won't include these files.
