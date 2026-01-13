# Removing Large Files from Git History

## The Problem

Large files (CSV, Excel, etc.) are in your git history, causing "file too large" errors when pushing to GitHub.

## Solution Options

### Option 1: BFG Repo-Cleaner (Recommended - Easier & Faster)

BFG is a simpler, faster alternative to git filter-branch.

**1. Install BFG:**
```bash
brew install bfg
# Or download from: https://rtyley.github.io/bfg-repo-cleaner/
```

**2. Run the script:**
```bash
./scripts/remove_large_files_bfg.sh
```

**Or manually:**
```bash
# Remove files larger than 5MB
bfg --strip-blobs-bigger-than 5M

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push origin --force --all
```

### Option 2: Git Filter-Branch (Built-in, but slower)

**1. Run the script:**
```bash
./scripts/remove_large_files_from_history.sh
```

**Or manually:**
```bash
# Remove specific files
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch 'data/output/*.csv' 'data/raw/**/*.xlsx'" \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Option 3: Remove Specific Files

If you know exactly which files to remove:

```bash
# Remove specific files from all history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch \
    'data/output/fact_event_players.csv' \
    'data/output/fact_events.csv' \
    'data/raw/games/**/*.xlsx'" \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## After Cleaning History

**1. Verify files are gone:**
```bash
# Check repository size
du -sh .git

# Should be much smaller now (was 256MB, should be <50MB)
```

**2. Force push to remote:**
```bash
git push origin --force --all
git push origin --force --tags
```

**⚠️ WARNING:**
- This rewrites remote history
- All team members must re-clone or reset their repos
- Coordinate with your team first!

**3. Team members need to:**
```bash
# Option A: Re-clone (safest)
cd ..
rm -rf benchsight
git clone <repo-url> benchsight

# Option B: Reset local repo
git fetch origin
git reset --hard origin/main
git clean -fd
```

## Current Large Files in History

Based on analysis, these files are in history:
- `data/output/fact_event_players.csv` (6.8MB)
- `data/output/fact_events.csv` (4.8MB)
- `data/raw/games/*/tracking.xlsx` (4-5MB each)
- Various other CSV/XLSX files

## Quick Fix (Recommended)

**Use BFG to remove all files >5MB:**

```bash
# 1. Install BFG
brew install bfg

# 2. Run cleanup
./scripts/remove_large_files_bfg.sh

# 3. Force push
git push origin --force --all
```

This will remove all files larger than 5MB from git history.

## Prevention

Make sure `.gitignore` is set up (already done):
- `data/output/*.csv` - Excluded
- `data/raw/**/*.xlsx` - Excluded
- `node_modules/` - Excluded

Future commits won't include these files.
