# BenchSight Command Reference

**Complete command reference for benchsight.sh CLI**

Last Updated: 2026-01-21
Version: 2.00

---

## Overview

This document provides a complete reference for all commands available in the `benchsight.sh` unified CLI.

**Usage:** `./benchsight.sh [command] [subcommand] [options]`

---

## ETL Commands

### `etl run`

Run the ETL pipeline.

**Usage:**
```bash
./benchsight.sh etl run                    # Run full ETL
./benchsight.sh etl run --games 18969 18977  # Run for specific games
./benchsight.sh etl run --wipe             # Wipe output and rebuild
```

**Description:**
- Processes game data from BLB tables and tracking files
- Generates 145 tables (dimensions, facts, QA)
- Takes ~80 seconds for 4 games

**Options:**
- `--games GAME_ID ...` - Process specific games only
- `--wipe` - Delete output directory and rebuild

**Examples:**
```bash
# Full ETL run
./benchsight.sh etl run

# Process specific games
./benchsight.sh etl run --games 18969 18977

# Clean rebuild
./benchsight.sh etl run --wipe
```

---

### `etl validate`

Validate ETL output.

**Usage:**
```bash
./benchsight.sh etl validate
```

**Description:**
- Validates all generated tables
- Checks goal counts
- Verifies foreign key integrity
- Checks required columns

**Output:**
- Validation results
- Error messages (if any)
- Summary statistics

---

### `etl status`

Check ETL status.

**Usage:**
```bash
./benchsight.sh etl status
```

**Description:**
- Shows current ETL status
- Lists available games
- Shows table counts
- Displays last run time

---

### `etl wipe`

Wipe output directory and rebuild.

**Usage:**
```bash
./benchsight.sh etl wipe
```

**Description:**
- Deletes all output files
- Prompts for confirmation
- Rebuilds all tables

**Warning:** This will delete all generated tables!

---

## Dashboard Commands

### `dashboard dev`

Start dashboard development server.

**Usage:**
```bash
./benchsight.sh dashboard dev
```

**Description:**
- Starts Next.js dev server
- Available at http://localhost:3000
- Hot reload enabled
- Installs dependencies if needed

**Features:**
- Auto-reload on file changes
- Fast refresh
- Error overlay

---

### `dashboard build`

Build dashboard for production.

**Usage:**
```bash
./benchsight.sh dashboard build
```

**Description:**
- Builds Next.js app for production
- Optimizes assets
- Generates static pages
- Creates production bundle

**Output:**
- Production build in `.next/` directory

---

### `dashboard deploy`

Deploy dashboard to Vercel.

**Usage:**
```bash
./benchsight.sh dashboard deploy
```

**Description:**
- Deploys to Vercel production
- Requires Vercel CLI
- Uses Vercel project configuration

**Prerequisites:**
- Vercel CLI installed (`npm i -g vercel`)
- Vercel project configured

---

## API Commands

### `api dev`

Start API development server.

**Usage:**
```bash
./benchsight.sh api dev
```

**Description:**
- Starts FastAPI dev server
- Available at http://localhost:8000
- API docs at http://localhost:8000/docs
- Auto-reload on file changes
- Creates virtual environment if needed

**Features:**
- Interactive API docs
- Auto-reload
- Error handling

---

### `api test`

Run API tests.

**Usage:**
```bash
./benchsight.sh api test
```

**Description:**
- Runs pytest test suite
- Executes all tests in `api/tests/`
- Shows test results
- Reports coverage (if configured)

---

### `api deploy`

Deploy API (see documentation).

**Usage:**
```bash
./benchsight.sh api deploy
```

**Description:**
- Shows deployment instructions
- References deployment docs
- Does not actually deploy (configure via Railway/Render dashboard)

**See:** `api/DEPLOYMENT.md` for deployment instructions

---

## Database Commands

### `db upload`

Upload tables to Supabase.

**Usage:**
```bash
./benchsight.sh db upload                    # Upload all tables
./benchsight.sh db upload --tables dim_player fact_events  # Upload specific tables
./benchsight.sh db upload --pattern "fact_player*"  # Upload matching tables
```

**Description:**
- Uploads CSV files to Supabase
- Creates tables if needed
- Updates existing tables
- Validates data

**Options:**
- `--tables TABLE ...` - Upload specific tables
- `--pattern PATTERN` - Upload tables matching pattern

**Examples:**
```bash
# Upload all tables
./benchsight.sh db upload

# Upload specific tables
./benchsight.sh db upload --tables dim_player fact_events

# Upload by pattern
./benchsight.sh db upload --pattern "fact_player*"
```

---

### `db schema`

Generate Supabase schema.

**Usage:**
```bash
./benchsight.sh db schema
```

**Description:**
- Generates SQL schema file
- Creates table definitions
- Includes indexes and constraints
- Outputs to console or file

**Next Steps:**
- Run generated SQL in Supabase SQL Editor
- Creates all tables with proper schema

---

### `db reset`

Reset Supabase database (careful!).

**Usage:**
```bash
./benchsight.sh db reset
```

**Description:**
- Resets database to clean state
- Prompts for confirmation
- Shows instructions for SQL execution

**Warning:** This will delete all data!

**See:** `sql/reset_supabase.sql` for reset script

---

## Environment Commands

### `env switch`

Switch between environments.

**Usage:**
```bash
./benchsight.sh env switch dev          # Switch to dev
./benchsight.sh env switch production  # Switch to production
```

**Description:**
- Switches configuration files
- Updates `config/config_local.ini`
- Updates `ui/dashboard/.env.local`
- Supports dev, production environments

**Environments:**
- `dev` - Development environment
- `production` - Production environment

---

### `env status`

Show current environment status.

**Usage:**
```bash
./benchsight.sh env status
```

**Description:**
- Shows current environment
- Displays config file locations
- Shows dashboard env status
- Indicates environment type

---

## Project Commands

### `status`

Show project status.

**Usage:**
```bash
./benchsight.sh status
```

**Description:**
- Shows component availability
- Displays dependency status
- Lists component locations
- Provides status overview

**Output:**
- Component status (Available/Not found)
- Dependency status
- Links to detailed status

---

### `docs`

Open documentation.

**Usage:**
```bash
./benchsight.sh docs
```

**Description:**
- Opens documentation index
- Opens in default editor/viewer
- Shows documentation location

**Opens:** `docs/MASTER_INDEX.md`

---

### `help`

Show help message.

**Usage:**
```bash
./benchsight.sh help
./benchsight.sh --help
./benchsight.sh -h
```

**Description:**
- Shows complete command reference
- Lists all available commands
- Provides usage examples
- Shows documentation links

---

## Command Examples

### Daily Workflow

```bash
# Start dashboard
./benchsight.sh dashboard dev

# Run ETL (in another terminal)
./benchsight.sh etl run

# Validate output
./benchsight.sh etl validate

# Upload to Supabase
./benchsight.sh db upload
```

### Development Workflow

```bash
# Switch to dev environment
./benchsight.sh env switch dev

# Start API
./benchsight.sh api dev

# Start dashboard
./benchsight.sh dashboard dev

# Check status
./benchsight.sh status
```

### Workflow Commands

```bash
# Smart commit with checklist
./benchsight.sh commit

# Create PR with checklist
./benchsight.sh review-pr

# Generate test templates
./benchsight.sh generate-tests <file_path>

# Refactoring helpers
./benchsight.sh refactor check

# Fix TypeScript types
./benchsight.sh fix-types

# Create PRD
./benchsight.sh prd create feature feature-name
./benchsight.sh prd create refactor refactor-name
./benchsight.sh prd create bug bug-description

# List PRDs
./benchsight.sh prd list

# Documentation sync
./benchsight.sh docs sync

# Documentation check
./benchsight.sh docs check
```

### Production Workflow

```bash
# Switch to production
./benchsight.sh env switch production

# Build dashboard
./benchsight.sh dashboard build

# Deploy dashboard
./benchsight.sh dashboard deploy

# Deploy API (see docs)
./benchsight.sh api deploy
```

---

## Command Aliases

You can create aliases for convenience:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias bs='./benchsight.sh'
alias bs-etl='./benchsight.sh etl'
alias bs-dash='./benchsight.sh dashboard'
alias bs-api='./benchsight.sh api'
alias bs-db='./benchsight.sh db'
```

**Usage with aliases:**
```bash
bs etl run
bs dashboard dev
bs api dev
bs db upload
```

---

## Error Handling

### Common Errors

**"Command not found"**
- Make sure `benchsight.sh` is executable: `chmod +x benchsight.sh`
- Run from project root directory

**"Directory not found"**
- Component may not be set up
- Check component status: `./benchsight.sh status`

**"Permission denied"**
- Make script executable: `chmod +x benchsight.sh`

**"Dependencies not installed"**
- Run setup scripts
- Install dependencies manually

---

## Related Documentation

- [archive/QUICK_START.md](archive/QUICK_START.md) - Quick start guide (archived)
- [workflows/WORKFLOW.md](workflows/WORKFLOW.md) - Development workflows
- [archive/MAINTENANCE_GUIDE.md](archive/MAINTENANCE_GUIDE.md) - Maintenance guide (archived)
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Project structure

---

*Last Updated: 2026-01-15*
