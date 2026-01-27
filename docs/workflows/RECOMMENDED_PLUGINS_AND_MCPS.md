# BenchSight Recommended Plugins, MCPs & Advanced Automation

A comprehensive guide to plugins, MCP servers, and automation patterns that would supercharge the BenchSight hockey analytics platform.

---

## Table of Contents

1. [Essential MCPs (Install Now)](#1-essential-mcps-install-now)
2. [Recommended MCPs (High Value)](#2-recommended-mcps-high-value)
3. [Advanced MCPs (Dream Big)](#3-advanced-mcps-dream-big)
4. [Suggested Skills (Not Yet Implemented)](#4-suggested-skills-not-yet-implemented)
5. [Suggested Hooks (Not Yet Implemented)](#5-suggested-hooks-not-yet-implemented)
6. [Plugin Marketplace Items](#6-plugin-marketplace-items)
7. [Integration Architecture](#7-integration-architecture)
8. [Installation Commands](#8-installation-commands)

---

## 1. Essential MCPs (Install Now)

These directly support your current stack.

### Supabase MCP
**Why:** Direct database interaction, schema management, RLS policies, migrations.

```bash
claude mcp add supabase --scope project
```

**Capabilities:**
- Query data with natural language
- Generate and run migrations
- Manage RLS policies
- Create database functions
- Debug query performance
- Pull TypeScript types automatically

**Use cases for BenchSight:**
- "Show me all players with more than 5 goals this season"
- "Create a migration to add expected_goals column to fact_shots"
- "Generate RLS policy for team-based data access"

**Source:** [Supabase MCP Docs](https://supabase.com/docs/guides/getting-started/mcp)

---

### PostgreSQL MCP (crystaldba)
**Why:** Deep Postgres performance analysis beyond what Supabase MCP offers.

```bash
claude mcp add postgres -- npx -y @crystaldba/postgres-mcp
```

**Capabilities:**
- Performance analysis and tuning
- Index recommendations
- Query plan analysis
- Health monitoring
- Bloat detection

**Use cases for BenchSight:**
- "Analyze slow queries on fact_player_game"
- "Recommend indexes for the dashboard queries"
- "Check for table bloat in dimension tables"

**Source:** [crystaldba/postgres-mcp](https://github.com/crystaldba/postgres-mcp)

---

### GitHub MCP
**Why:** PR management, issue tracking, code review automation.

```bash
claude mcp add github --scope project
```

**Capabilities:**
- Create/manage PRs and issues
- Review code changes
- Manage branches
- Search code across repos
- Automate releases

**Use cases for BenchSight:**
- "Create a PR for the goal counting fix"
- "List all open issues labeled 'ETL'"
- "Generate release notes from merged PRs"

**Source:** [GitHub MCP](https://github.com/modelcontextprotocol/servers)

---

### Filesystem MCP
**Why:** Structured file operations, bulk processing, directory analysis.

```bash
claude mcp add filesystem --scope project -- \
  npx -y @modelcontextprotocol/server-filesystem /path/to/project
```

**Capabilities:**
- Recursive file operations
- Pattern-based file discovery
- Bulk transformations
- Directory tree analysis

**Use cases for BenchSight:**
- "Find all Python files importing pandas"
- "List all CSV files in data/output larger than 1MB"
- "Show directory structure of src/calculations"

---

### Playwright MCP (Microsoft)
**Why:** Browser automation for dashboard testing, visual regression.

```bash
claude mcp add playwright -- npx -y @anthropic/mcp-playwright
```

**Capabilities:**
- Interact with web pages via accessibility tree
- Fill forms, click buttons
- Screenshot capture
- Network monitoring
- Cross-browser testing

**Use cases for BenchSight:**
- "Test the player stats page loads correctly"
- "Fill out the game filter form and verify results"
- "Take screenshots of all dashboard pages"

**Source:** [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp)

---

## 2. Recommended MCPs (High Value)

### Vercel MCP
**Why:** Deploy dashboard directly from Claude, monitor deployments.

```bash
claude mcp add vercel --scope project
```

**Capabilities:**
- Deploy to preview/production
- Check deployment status
- Manage environment variables
- View deployment logs
- Rollback deployments

**Use cases for BenchSight:**
- "Deploy dashboard to preview"
- "Show me the last 5 deployment logs"
- "Rollback to previous production deployment"

**Source:** [vercel/vercel-deploy-claude-code-plugin](https://github.com/vercel/vercel-deploy-claude-code-plugin)

---

### Next.js DevTools MCP
**Why:** Deep integration with Next.js development workflow.

```bash
claude mcp add nextjs -- npx -y @vercel/next-devtools-mcp
```

**Capabilities:**
- Component tree inspection
- Route analysis
- Server/Client component detection
- Performance profiling
- Build error analysis

**Use cases for BenchSight:**
- "Analyze why this page is slow"
- "Show all server components in the dashboard"
- "Find components that should be server components"

**Source:** [vercel/next-devtools-mcp](https://github.com/vercel/next-devtools-mcp)

---

### Memory/Knowledge Graph MCP
**Why:** Persistent memory across sessions, learn from past work.

```bash
claude mcp add memory -- npx -y @anthropic/mcp-memory
```

**Capabilities:**
- Store entities and observations
- Retrieve context from past sessions
- Build project knowledge graph
- Track decisions and rationale

**Use cases for BenchSight:**
- Remember past ETL debugging sessions
- Track architectural decisions
- Build institutional knowledge about hockey stat calculations

**Source:** [Knowledge Graph Memory MCP](https://www.pulsemcp.com/servers/modelcontextprotocol-knowledge-graph-memory)

---

### Linear MCP
**Why:** Issue tracking integration for development workflow.

```bash
claude mcp add linear --scope project
```

**Capabilities:**
- Create/update issues
- Track project progress
- Manage cycles and milestones
- Link commits to issues

**Use cases for BenchSight:**
- "Create an issue for the Corsi calculation bug"
- "Show all issues in the current cycle"
- "Update issue BS-123 to 'In Review'"

**Source:** [Linear MCP Docs](https://linear.app/docs/mcp)

---

## 3. Advanced MCPs (Dream Big)

### Data Visualization MCPs

#### ECharts MCP
**Why:** Generate charts dynamically for analytics dashboards.

```bash
claude mcp add echarts -- npx -y mcp-echarts
```

**Use cases:**
- "Generate a shot heatmap for player X"
- "Create a line comparison chart for team Corsi"
- "Build an interactive goal timeline"

#### VegaLite MCP
**Why:** Declarative visualization grammar for data exploration.

```bash
claude mcp add vegalite -- npx -y @anthropic/mcp-vegalite
```

**Use cases:**
- "Visualize goal distribution by period"
- "Create a scatter plot of TOI vs points"

---

### Analytics MCPs

#### Dune Analytics MCP
**Why:** If you ever want blockchain/web3 analytics for sports betting data.

#### Google Data Commons MCP
**Why:** Access vast public datasets for context (demographics, economics).

```bash
claude mcp add datacommons -- npx -y @google/datacommons-mcp
```

**Use cases:**
- "Compare hockey participation rates across states"
- "Get population data for NHL market cities"

**Source:** [Google Data Commons MCP](https://developers.googleblog.com/en/datacommonsmcp/)

---

### Vector Database MCPs

#### Pinecone MCP
**Why:** Semantic search over hockey documentation, similar play retrieval.

```bash
claude mcp add pinecone -- uvx mcp-pinecone \
  --index-name benchsight-docs \
  --api-key $PINECONE_API_KEY
```

**Use cases:**
- "Find similar plays to this zone entry"
- "Search documentation for 'expected goals'"
- "Retrieve plays with similar micro-stat patterns"

**Source:** [Pinecone MCP Docs](https://docs.pinecone.io/guides/operations/mcp-server)

#### Neo4j MCP
**Why:** Graph database for player relationships, line combinations, trade networks.

```bash
claude mcp add neo4j -- npx -y @neo4j/mcp-neo4j
```

**Use cases:**
- "Show the relationship graph for line combinations"
- "Find all players who played with Player X"
- "Visualize the assist network for this season"

**Source:** [Neo4j MCP Blog](https://neo4j.com/blog/developer/claude-converses-neo4j-via-mcp/)

---

### Communication MCPs

#### Slack MCP
**Why:** Notify team of ETL completions, dashboard deployments.

```bash
claude mcp add slack -- npx -y @anthropic/mcp-slack
```

**Use cases:**
- "Post ETL completion summary to #data-updates"
- "Notify team of new dashboard deployment"
- "Create a thread summarizing today's data quality issues"

#### Notion MCP
**Why:** Sync documentation, PRDs, research notes.

```bash
claude mcp add notion -- npx -y @anthropic/mcp-notion
```

**Use cases:**
- "Update the ETL documentation page"
- "Create a page for the new xG model research"
- "Search Notion for hockey analytics references"

**Source:** [Notion MCP](https://www.mintmcp.com/notion)

---

### Monitoring MCPs

#### Sentry MCP
**Why:** Error tracking, performance monitoring for dashboard.

```bash
claude mcp add sentry -- npx -y mcp-sentry
```

**Use cases:**
- "Show recent errors from the dashboard"
- "Find the root cause of the 500 errors"
- "Track error rate over the last week"

#### Datadog MCP
**Why:** Infrastructure monitoring, APM, logs.

```bash
claude mcp add datadog -- npx -y mcp-datadog
```

**Use cases:**
- "Show API latency metrics"
- "Alert me when ETL takes longer than 2 minutes"
- "Correlate slow dashboard pages with database queries"

---

## 4. Suggested Skills (Not Yet Implemented)

### `/deploy`
Auto-deploy with validation checks.

```yaml
---
name: deploy
description: Deploy dashboard to Vercel after running full validation suite
allowed-tools: Bash, Task
---

# Deploy to Vercel

1. Run `/validate` to ensure data quality
2. Run `npm run build` to verify dashboard builds
3. Run `npm run type-check` for TypeScript validation
4. Deploy to Vercel preview
5. Run `/ui-test` on preview URL
6. If all pass, promote to production

Only deploy if ALL checks pass.
```

---

### `/generate-changelog`
Auto-generate changelog from commits.

```yaml
---
name: generate-changelog
description: Generate changelog entry from recent commits
allowed-tools: Bash, Read, Write
---

# Generate Changelog

1. Get commits since last tag: `git log $(git describe --tags --abbrev=0)..HEAD`
2. Group by type (FEAT, FIX, etc.)
3. Format as markdown
4. Prepend to CHANGELOG.md
5. Suggest version bump (major/minor/patch)
```

---

### `/sync-docs`
Auto-update documentation from code.

```yaml
---
name: sync-docs
description: Synchronize documentation with code changes
allowed-tools: Bash, Read, Write, Task
---

# Sync Documentation

1. Extract docstrings from `src/calculations/*.py`
2. Generate API docs from `api/routes/*.py`
3. Update table documentation from `data/output/*.csv` schemas
4. Update config documentation from `config/*.json`
5. Flag any outdated documentation
```

---

### `/pr-ready`
Comprehensive pre-PR validation.

```yaml
---
name: pr-ready
description: Run all checks before creating a PR
allowed-tools: Bash, Task
---

# PR Readiness Check

Run in sequence:
1. `/validate` - ETL data quality
2. `/compliance-check` - CLAUDE.md rules
3. `pytest` - Python tests
4. `npm run build` - Dashboard build
5. `npm run type-check` - TypeScript
6. `/reality-check` - Verify completions

Report: READY or BLOCKED with specific failures.
```

---

### `/analyze-game`
Deep analysis of a specific game.

```yaml
---
name: analyze-game
description: Generate comprehensive analysis for a specific game
allowed-tools: Bash, Read, Task
argument-hint: "[game_id]"
---

# Game Analysis

For game $ARGUMENTS:

1. Load game data from fact tables
2. Generate summary statistics
3. Create shot charts and heat maps
4. Identify key moments (goals, penalties)
5. Calculate advanced metrics (xG, Corsi, etc.)
6. Compare to season averages
7. Output markdown report
```

---

### `/backfill`
Backfill missing data or recalculate stats.

```yaml
---
name: backfill
description: Backfill missing data or recalculate specific stats
allowed-tools: Bash, Read
argument-hint: "[stat_name] [date_range]"
---

# Backfill Data

1. Identify missing data points
2. Run targeted ETL for affected games
3. Recalculate derived statistics
4. Validate against expected totals
5. Report discrepancies
```

---

## 5. Suggested Hooks (Not Yet Implemented)

### Session State Persistence

**File: `.claude/hooks/save-session-state.py`**

```python
#!/usr/bin/env python3
"""Save session state for continuity."""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

try:
    data = json.load(sys.stdin)
except:
    sys.exit(0)

state_file = Path.home() / '.claude' / 'benchsight-state.json'

state = {
    'timestamp': datetime.now().isoformat(),
    'branch': os.popen('git rev-parse --abbrev-ref HEAD').read().strip(),
    'last_etl': os.popen('ls -t data/output/*.csv | head -1').read().strip(),
    'session_id': data.get('session_id', 'unknown')
}

state_file.parent.mkdir(exist_ok=True)
with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)

sys.exit(0)
```

**Hook config:**
```json
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/save-session-state.py\""
          }
        ]
      }
    ]
  }
}
```

---

### Auto-Format on Save

**File: `.claude/hooks/auto-format.sh`**

```bash
#!/bin/bash
# Auto-format files after edit

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
[ -z "$FILE_PATH" ] && exit 0

case "$FILE_PATH" in
  *.py)
    black "$FILE_PATH" 2>/dev/null
    isort "$FILE_PATH" 2>/dev/null
    ;;
  *.ts|*.tsx|*.js|*.jsx)
    npx prettier --write "$FILE_PATH" 2>/dev/null
    ;;
  *.json)
    npx prettier --write "$FILE_PATH" 2>/dev/null
    ;;
esac

exit 0
```

---

### Commit Message Validator

**File: `.claude/hooks/commit-validator.py`**

```python
#!/usr/bin/env python3
"""Validate commit messages follow [TYPE] format."""
import json
import sys
import re

try:
    data = json.load(sys.stdin)
except:
    sys.exit(0)

if data.get('tool_name') != 'Bash':
    sys.exit(0)

command = data.get('tool_input', {}).get('command', '')
if 'git commit' not in command:
    sys.exit(0)

# Extract message
match = re.search(r'-m\s+["\']([^"\']+)["\']', command)
if not match:
    sys.exit(0)

msg = match.group(1)
pattern = r'^\[(FEAT|FIX|DOCS|REFACTOR|TEST|CHORE)\]\s+.{10,}'

if not re.match(pattern, msg):
    print(json.dumps({
        "decision": "block",
        "reason": f"Invalid commit format. Use: [TYPE] Description\nTypes: FEAT, FIX, DOCS, REFACTOR, TEST, CHORE"
    }))

sys.exit(0)
```

---

### ETL Performance Tracker

**File: `.claude/hooks/etl-perf-tracker.py`**

```python
#!/usr/bin/env python3
"""Track ETL performance over time."""
import json
import sys
import re
import os
from datetime import datetime
from pathlib import Path

try:
    data = json.load(sys.stdin)
except:
    sys.exit(0)

if data.get('tool_name') != 'Bash':
    sys.exit(0)

result = data.get('tool_result', {})
stdout = result.get('stdout', '')

# Look for ETL timing in output
match = re.search(r'ETL completed in (\d+\.?\d*) seconds', stdout)
if not match:
    sys.exit(0)

duration = float(match.group(1))
log_file = Path.home() / '.claude' / 'etl-performance.jsonl'

record = {
    'timestamp': datetime.now().isoformat(),
    'duration_seconds': duration,
    'status': 'pass' if duration < 90 else 'slow'
}

log_file.parent.mkdir(exist_ok=True)
with open(log_file, 'a') as f:
    f.write(json.dumps(record) + '\n')

if duration > 90:
    print(json.dumps({
        "message": f"WARNING: ETL took {duration}s (target: <90s)"
    }))

sys.exit(0)
```

---

### Documentation Drift Detector

**File: `.claude/hooks/doc-drift-detector.sh`**

```bash
#!/bin/bash
# Detect when code changes but docs don't

CHANGED_FILES=$(git diff --name-only HEAD~1 2>/dev/null)

# Check if calculations changed without doc updates
if echo "$CHANGED_FILES" | grep -q "src/calculations/"; then
    if ! echo "$CHANGED_FILES" | grep -q "docs/"; then
        echo '{"message": "WARNING: Calculation files changed but no documentation updated. Consider updating docs/."}'
    fi
fi

exit 0
```

---

## 6. Plugin Marketplace Items

### From Claude Code Plugin Directory

Install via `/plugin` command or npx:

```bash
# Next.js + Vercel Pro
npx claude-code-templates@latest --plugin nextjs-vercel-pro

# DevOps Automation
npx claude-code-templates@latest --plugin devops-automation

# Database Tools
npx claude-code-templates@latest --plugin database-toolkit

# Testing Suite
npx claude-code-templates@latest --plugin testing-automation
```

**Source:** [Claude Code Plugin Directory](https://claudecodeplugins.net/)

### From AI Templates

```bash
# Supabase full stack
npx claude-code-templates@latest --agent database/supabase-schema-architect
npx claude-code-templates@latest --mcp database/supabase

# Next.js development
npx claude-code-templates@latest --agent frontend/nextjs-specialist
```

**Source:** [Claude Code Templates](https://www.aitmpl.com/plugins)

---

## 7. Integration Architecture

### Recommended Stack for BenchSight

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code                              │
├─────────────────────────────────────────────────────────────┤
│  Skills                    │  Hooks                         │
│  ├── /etl                  │  ├── bash-validator            │
│  ├── /validate             │  ├── goal-counting-guard       │
│  ├── /deploy               │  ├── commit-validator          │
│  ├── /pr-ready             │  ├── auto-format               │
│  ├── /hockey-stats         │  ├── etl-perf-tracker          │
│  └── /analyze-game         │  └── session-state             │
├─────────────────────────────────────────────────────────────┤
│                        MCP Servers                           │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   Database   │   DevOps     │   Testing    │   Analytics    │
│  ┌────────┐  │  ┌────────┐  │  ┌────────┐  │  ┌──────────┐  │
│  │Supabase│  │  │ GitHub │  │  │Playwright│ │  │ ECharts  │  │
│  │Postgres│  │  │ Vercel │  │  │ Puppeteer│ │  │ VegaLite │  │
│  │ Neo4j  │  │  │ Linear │  │  │  Sentry  │ │  │ Pinecone │  │
│  └────────┘  │  └────────┘  │  └────────┘  │  └──────────┘  │
├──────────────┴──────────────┴──────────────┴────────────────┤
│                     Communication                            │
│              Slack  •  Notion  •  Memory                     │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Game Tracking Excel
        │
        ▼
   ETL Pipeline ──────► Supabase MCP ──────► PostgreSQL
        │                     │
        ▼                     ▼
   Validation ◄──────── Postgres MCP (perf analysis)
        │
        ▼
   Dashboard ──────────► Vercel MCP ──────► Deployment
        │                     │
        ▼                     ▼
   Playwright MCP ────► UI Testing ────► Slack Notification
```

---

## 8. Installation Commands

### Essential (Install First)

```bash
# Supabase - database integration
claude mcp add supabase --scope project

# GitHub - PR and issue management
claude mcp add github --scope project

# Filesystem - file operations
claude mcp add filesystem --scope project

# Playwright - browser testing
claude mcp add playwright -- npx -y @anthropic/mcp-playwright
```

### Recommended (Install Next)

```bash
# Vercel - deployment
claude mcp add vercel --scope project

# Postgres deep analysis
claude mcp add postgres -- npx -y @crystaldba/postgres-mcp

# Memory persistence
claude mcp add memory -- npx -y @anthropic/mcp-memory

# Next.js devtools
claude mcp add nextjs -- npx -y @vercel/next-devtools-mcp
```

### Advanced (When Ready)

```bash
# Visualization
claude mcp add echarts -- npx -y mcp-echarts
claude mcp add vegalite -- npx -y @anthropic/mcp-vegalite

# Communication
claude mcp add slack -- npx -y @anthropic/mcp-slack
claude mcp add notion -- npx -y @anthropic/mcp-notion

# Issue tracking
claude mcp add linear --scope project

# Vector search
claude mcp add pinecone -- uvx mcp-pinecone \
  --index-name benchsight \
  --api-key $PINECONE_API_KEY

# Graph database
claude mcp add neo4j -- npx -y @neo4j/mcp-neo4j
```

### Verify Installation

```bash
# List all installed MCPs
claude mcp list

# Test a specific MCP
claude mcp test supabase
```

---

## Summary: Priority Installation Order

### Phase 1: Core Development (Week 1)
1. ✅ Supabase MCP - Database operations
2. ✅ GitHub MCP - Version control
3. ✅ Filesystem MCP - File operations
4. ✅ Playwright MCP - Testing

### Phase 2: DevOps (Week 2)
5. Vercel MCP - Deployments
6. Next.js DevTools MCP - Dashboard dev
7. Postgres MCP - Performance tuning

### Phase 3: Productivity (Week 3)
8. Memory MCP - Session persistence
9. Linear MCP - Issue tracking
10. Slack MCP - Notifications

### Phase 4: Advanced Analytics (Month 2)
11. ECharts/VegaLite MCP - Visualization
12. Pinecone MCP - Semantic search
13. Neo4j MCP - Graph analytics

---

## Sources

- [Supabase MCP Docs](https://supabase.com/docs/guides/getting-started/mcp)
- [GitHub modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
- [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp)
- [crystaldba/postgres-mcp](https://github.com/crystaldba/postgres-mcp)
- [vercel/next-devtools-mcp](https://github.com/vercel/next-devtools-mcp)
- [Linear MCP Docs](https://linear.app/docs/mcp)
- [Pinecone MCP Docs](https://docs.pinecone.io/guides/operations/mcp-server)
- [Neo4j MCP Blog](https://neo4j.com/blog/developer/claude-converses-neo4j-via-mcp/)
- [Google Data Commons MCP](https://developers.googleblog.com/en/datacommonsmcp/)
- [Awesome MCP Servers](https://github.com/appcypher/awesome-mcp-servers)
- [Claude Code Plugin Directory](https://claudecodeplugins.net/)
- [Claude Code Templates](https://www.aitmpl.com/plugins)
- [Best MCP Servers 2026](https://www.builder.io/blog/best-mcp-servers-2026)
