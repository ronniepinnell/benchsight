# BenchSight Complete Installation Guide

A comprehensive guide to installing and configuring all tools, MCPs, plugins, agents, and skills for BenchSight development.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Core Tools Installation](#2-core-tools-installation)
3. [MCP Server Installation](#3-mcp-server-installation)
4. [Skills Setup](#4-skills-setup)
5. [Hooks Configuration](#5-hooks-configuration)
6. [Agent Configuration](#6-agent-configuration)
7. [Environment Setup](#7-environment-setup)
8. [Verification](#8-verification)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | macOS 12+, Ubuntu 20.04+ | macOS 14+, Ubuntu 22.04+ |
| RAM | 8GB | 16GB+ |
| Storage | 10GB free | 50GB+ SSD |
| Node.js | 18.x | 20.x LTS |
| Python | 3.10 | 3.11+ |
| Git | 2.30+ | Latest |

### Install Prerequisites

```bash
# macOS (using Homebrew)
brew install node python@3.11 git

# Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm python3.11 python3.11-venv git

# Verify installations
node --version    # Should be 18.x or higher
python3 --version # Should be 3.10 or higher
git --version     # Should be 2.30 or higher
```

### Install Claude Code CLI

```bash
# Install Claude Code globally
npm install -g @anthropic/claude-code

# Verify installation
claude --version

# Login to Claude
claude login
```

---

## 2. Core Tools Installation

### 2.1 GitHub CLI

```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Authenticate
gh auth login
```

### 2.2 Supabase CLI

```bash
# macOS
brew install supabase/tap/supabase

# npm (all platforms)
npm install -g supabase

# Verify
supabase --version
```

### 2.3 Vercel CLI

```bash
# Install
npm install -g vercel

# Login
vercel login

# Verify
vercel --version
```

### 2.4 Python Dependencies

```bash
# Navigate to project
cd /path/to/benchsight

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install black isort pytest pytest-cov
```

### 2.5 Node.js Dependencies (Dashboard)

```bash
cd ui/dashboard
npm install
```

### 2.6 API Dependencies

```bash
cd api
pip install -r requirements.txt
```

---

## 3. MCP Server Installation

### Essential MCPs (Install First)

```bash
# 1. Supabase MCP - Database operations
claude mcp add supabase --scope project

# 2. GitHub MCP - Version control
claude mcp add github --scope project

# 3. Filesystem MCP - File operations
claude mcp add filesystem --scope project -- \
  npx -y @modelcontextprotocol/server-filesystem "$(pwd)"

# 4. Playwright MCP - Browser testing
claude mcp add playwright -- npx -y @anthropic/mcp-playwright
```

### Recommended MCPs

```bash
# 5. Vercel MCP - Deployments
claude mcp add vercel --scope project

# 6. PostgreSQL MCP - Database analysis
claude mcp add postgres -- npx -y @crystaldba/postgres-mcp

# 7. Memory MCP - Session persistence
claude mcp add memory -- npx -y @anthropic/mcp-memory

# 8. Next.js DevTools MCP
claude mcp add nextjs -- npx -y @vercel/next-devtools-mcp
```

### Advanced MCPs (When Ready)

```bash
# Visualization
claude mcp add echarts -- npx -y mcp-echarts
claude mcp add vegalite -- npx -y @anthropic/mcp-vegalite

# Communication
claude mcp add slack -- npx -y @anthropic/mcp-slack
claude mcp add notion -- npx -y @anthropic/mcp-notion

# Issue tracking
claude mcp add linear --scope project

# Vector database (requires API key)
export PINECONE_API_KEY="your-key"
claude mcp add pinecone -- uvx mcp-pinecone \
  --index-name benchsight \
  --api-key $PINECONE_API_KEY

# Graph database (requires connection)
claude mcp add neo4j -- npx -y @neo4j/mcp-neo4j
```

### Verify MCP Installation

```bash
# List all installed MCPs
claude mcp list

# Test specific MCP
claude mcp test supabase
```

---

## 4. Skills Setup

Skills are already included in the repository at `.claude/skills/`. To verify:

```bash
# List all skills
ls -la .claude/skills/
```

### Available Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| ETL | `/etl` | Run ETL pipeline |
| Validate | `/validate` | Validate ETL output |
| ETL Issue | `/etl-issue` | Create GitHub issue for ETL failure |
| Dashboard Dev | `/dashboard-dev` | Start dashboard development |
| Dashboard Deploy | `/dashboard-deploy` | Deploy to Vercel |
| Portal Dev | `/portal-dev` | Start portal development |
| Tracker Dev | `/tracker-dev` | Start tracker development |
| API Dev | `/api-dev` | Start API development |
| DB Dev | `/db-dev` | Work with dev database |
| DB Prod | `/db-prod` | Work with prod database |
| Env Switch | `/env-switch` | Switch environments |
| Hockey Stats | `/hockey-stats` | Hockey analytics SME |
| Reality Check | `/reality-check` | Call Karen agent |
| Compliance Check | `/compliance-check` | CLAUDE.md compliance |
| Competitive Research | `/competitive-research` | Research competitors |
| UI/UX Design | `/ui-ux-design` | Design assistance |
| Monetization | `/monetization` | Revenue planning |
| Go to Market | `/go-to-market` | Launch strategy |
| Scale Architecture | `/scale-architecture` | Scaling plans |
| Schema Design | `/schema-design` | Database design |
| ML Pipeline | `/ml-pipeline` | Machine learning |
| CV Tracking | `/cv-tracking` | Computer vision |
| xG Model | `/xg-model` | Expected goals model |
| Post Code | `/post-code` | Post-code workflow |
| Doc Sync | `/doc-sync` | Documentation sync |
| PR Workflow | `/pr-workflow` | Pull request workflow |

### Test a Skill

```bash
claude "/validate"
```

---

## 5. Hooks Configuration

Hooks are configured in `.claude/settings.json`. The following hooks are already set up:

### Pre-Tool Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| `bash-validator.py` | Before Bash | Blocks dangerous commands |
| `goal-counting-guard.py` | Before Edit/Write | Goal counting reminder |

### Post-Tool Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| `post-etl-reminder.py` | After Bash | ETL validation reminder |
| `etl-failure-handler.py` | After Bash | Detects ETL failures, creates GitHub issues |

### Make Hooks Executable

```bash
chmod +x .claude/hooks/*.py
chmod +x .claude/hooks/*.sh
```

### Add Additional Hooks (Optional)

To add more hooks, edit `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/your-hook.py\""
          }
        ]
      }
    ]
  }
}
```

---

## 6. Agent Configuration

Agents are defined in `.claude/agents/`. Available agents:

### Project-Specific Agents

| Agent | File | Purpose |
|-------|------|---------|
| hockey-analytics-sme | `hockey-analytics-sme.md` | Hockey domain expert |
| github-integration-expert | `github-integration-expert.md` | GitHub/CI/CD |
| Jenny | `jenny.md` | Spec verification |
| Karen | `karen.md` | Reality check |
| task-completion-validator | `task-completion-validator.md` | Completion validation |
| claude-md-compliance-checker | `claude-md-compliance-checker.md` | Rule compliance |
| code-quality-pragmatist | `code-quality-pragmatist.md` | Code quality |
| ui-comprehensive-tester | `ui-comprehensive-tester.md` | UI testing |

### Built-in Agents (Always Available)

| Agent | Purpose |
|-------|---------|
| Explore | Codebase exploration |
| Plan | Implementation planning |
| Bash | Command execution |
| code-reviewer | Code review |
| debugger | Debugging |
| postgres-pro | PostgreSQL expertise |
| nextjs-developer | Next.js development |
| python-pro | Python development |
| typescript-pro | TypeScript development |
| rust-engineer | Rust development |
| ml-engineer | Machine learning |
| data-engineer | Data engineering |

---

## 7. Environment Setup

### 7.1 Supabase Configuration

**Development Environment:**

Create `config/config_local.ini`:
```ini
[supabase]
url = https://amuisqvhhiigxetsfame.supabase.co
anon_key = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_key = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Dashboard Environment:**

Create `ui/dashboard/.env.local`:
```bash
NEXT_PUBLIC_SUPABASE_URL=https://amuisqvhhiigxetsfame.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**API Environment:**

Create `api/.env`:
```bash
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:8080
SUPABASE_URL=https://amuisqvhhiigxetsfame.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 7.2 Git Configuration

```bash
# Set user info
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Set default branch
git config init.defaultBranch main

# Enable helpful aliases
git config alias.co checkout
git config alias.br branch
git config alias.st status
```

### 7.3 Vercel Configuration

```bash
# Link project
cd ui/dashboard
vercel link

# Set environment variables (Vercel dashboard or CLI)
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
```

---

## 8. Verification

Run these commands to verify everything is installed correctly:

### 8.1 Quick Health Check

```bash
# Project status
./benchsight.sh status

# Environment check
./benchsight.sh env status
```

### 8.2 Full Verification Script

```bash
#!/bin/bash
echo "=== BenchSight Installation Verification ==="

# Core tools
echo -n "Claude Code: "
claude --version 2>/dev/null && echo "✅" || echo "❌"

echo -n "Node.js: "
node --version 2>/dev/null && echo "✅" || echo "❌"

echo -n "Python: "
python3 --version 2>/dev/null && echo "✅" || echo "❌"

echo -n "Git: "
git --version 2>/dev/null && echo "✅" || echo "❌"

echo -n "GitHub CLI: "
gh --version 2>/dev/null | head -1 && echo "✅" || echo "❌"

echo -n "Supabase CLI: "
supabase --version 2>/dev/null && echo "✅" || echo "❌"

echo -n "Vercel CLI: "
vercel --version 2>/dev/null && echo "✅" || echo "❌"

# MCP servers
echo ""
echo "=== MCP Servers ==="
claude mcp list

# Skills
echo ""
echo "=== Skills ==="
ls .claude/skills/ | wc -l | xargs -I {} echo "{} skills installed"

# Hooks
echo ""
echo "=== Hooks ==="
ls .claude/hooks/*.py 2>/dev/null | wc -l | xargs -I {} echo "{} hooks configured"

# Agents
echo ""
echo "=== Agents ==="
ls .claude/agents/*.md 2>/dev/null | wc -l | xargs -I {} echo "{} agents defined"

echo ""
echo "=== Verification Complete ==="
```

### 8.3 Test Key Workflows

```bash
# Test ETL
./benchsight.sh etl validate

# Test dashboard build
cd ui/dashboard && npm run build

# Test API
cd api && python -m pytest tests/ -v
```

---

## 9. Troubleshooting

### Common Issues

#### Claude Code not found
```bash
# Reinstall
npm uninstall -g @anthropic/claude-code
npm install -g @anthropic/claude-code

# Check PATH
echo $PATH
which claude
```

#### MCP connection failed
```bash
# Check MCP status
claude mcp list

# Remove and re-add
claude mcp remove supabase
claude mcp add supabase --scope project

# Check for errors
claude mcp test supabase --debug
```

#### Hooks not triggering
```bash
# Check permissions
ls -la .claude/hooks/

# Make executable
chmod +x .claude/hooks/*.py

# Test hook manually
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | \
  python3 .claude/hooks/bash-validator.py
```

#### Skills not found
```bash
# Check skill files exist
ls -la .claude/skills/*/SKILL.md

# Verify YAML frontmatter
head -10 .claude/skills/validate/SKILL.md

# Restart Claude Code session
# (Skills load at session start)
```

#### Supabase connection issues
```bash
# Test connection
curl -s https://amuisqvhhiigxetsfame.supabase.co/rest/v1/ \
  -H "apikey: YOUR_ANON_KEY"

# Check config file
cat config/config_local.ini

# Verify environment
./benchsight.sh env status
```

#### Dashboard build fails
```bash
# Clear cache
cd ui/dashboard
rm -rf .next node_modules
npm install
npm run build

# Check for TypeScript errors
npm run type-check
```

### Getting Help

1. **Documentation:** `docs/MASTER_INDEX.md`
2. **Project Status:** `docs/PROJECT_STATUS.md`
3. **GitHub Issues:** Create issue with error details
4. **Claude Code Help:** `claude /help`

---

## Quick Start Summary

After installation, your typical workflow:

```bash
# 1. Start development
/dashboard-dev          # or /api-dev, /portal-dev, /tracker-dev

# 2. After writing code
/post-code              # Run full validation

# 3. If ETL changes
/etl --wipe && /validate

# 4. Before PR
/pr-workflow "Feature description"

# 5. For analytics questions
/hockey-stats "How do we calculate Corsi?"

# 6. Reality check on progress
/reality-check "Is the player stats page complete?"
```

---

## Agent/Skill Quick Reference

### For Current Development

| Task | Skill/Agent |
|------|-------------|
| Dashboard work | `/dashboard-dev`, `nextjs-developer` |
| ETL work | `/etl`, `/validate`, `python-pro` |
| API work | `/api-dev`, `backend-developer` |
| Database | `/db-dev`, `postgres-pro` |
| Testing | `ui-comprehensive-tester`, `test-automator` |
| Code review | `code-reviewer`, `code-quality-pragmatist` |

### For Commercial Scale

| Task | Skill/Agent |
|------|-------------|
| ML features | `/ml-pipeline`, `/xg-model`, `ml-engineer` |
| CV tracking | `/cv-tracking`, `ai-engineer` |
| Architecture | `/scale-architecture`, `architect-reviewer` |
| Business | `/monetization`, `/go-to-market`, `product-manager` |
| Design | `/ui-ux-design`, `/competitive-research`, `ui-designer` |
| Security | `security-auditor`, `penetration-tester` |
| DevOps | `devops-engineer`, `kubernetes-specialist` |

### Post-Code Workflow (Critical!)

After ANY code changes:
```
/post-code
```

This runs (in order):
1. Build check
2. `task-completion-validator`
3. `code-quality-pragmatist`
4. `claude-md-compliance-checker`
5. `Jenny`
6. Tests
7. `/doc-sync`
