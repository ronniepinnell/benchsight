# Documentation Archive Script

Automatically archives temporary/old documentation files to `docs/archive/`

## Quick Start

```bash
# Preview what would be archived (dry run)
python scripts/archive_docs.py

# Actually archive files
python scripts/archive_docs.py --execute

# Auto-archive without prompts
python scripts/archive_docs.py --auto
```

Or use the shell wrapper:
```bash
./scripts/archive_docs_auto.sh
```

## Auto-Run Options

### Option 1: Git Pre-commit Hook (Recommended)

Automatically archives docs before each commit:

```bash
# Enable the hook
cp .git/hooks/pre-commit.sample-archive .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Now every time you commit, old docs will be automatically archived!

### Option 2: Manual Script

Run whenever you want:
```bash
./scripts/archive_docs_auto.sh
```

### Option 3: Cron Job (Daily/Weekly)

Add to crontab for automatic daily archiving:
```bash
# Edit crontab
crontab -e

# Add line (runs daily at 2 AM)
0 2 * * * cd /path/to/benchsight && ./scripts/archive_docs_auto.sh >> logs/archive.log 2>&1
```

### Option 4: Add to Existing Workflows

Add to your `dev.sh` or other automation scripts:
```bash
# At the start of dev.sh
./scripts/archive_docs_auto.sh
```

## What Gets Archived?

The script automatically identifies:
- ✅ Versioned handoff files (keeps only latest, archives older versions)
- ✅ Temporary handoff files (`QUICK_START_NEXT_AGENT.md`, etc.)
- ✅ Old refactoring summaries
- ✅ Duplicate documentation files

**Never archives:**
- `README.md`
- `VERSION.txt`
- `requirements.txt`
- Files in `docs/` (only root-level temp files)

## Files

- `scripts/archive_docs.py` - Main archive script
- `scripts/archive_docs_auto.sh` - Auto-run wrapper
- `.git/hooks/pre-commit.sample-archive` - Git hook template
