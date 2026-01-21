# CodeRabbit Integration Guide

**Automated AI-powered code reviews for BenchSight pull requests**

---

## What is CodeRabbit?

**CodeRabbit** is an AI-powered code review tool that:
- ✅ Automatically reviews pull requests
- ✅ Provides detailed feedback on code quality
- ✅ Checks for bugs, security issues, and best practices
- ✅ Suggests improvements and optimizations
- ✅ Helps maintain code standards

**Benefits for BenchSight:**
- Enforces [CODE_STANDARDS.md](CODE_STANDARDS.md) principles
- Catches common patterns (goal counting, type safety, etc.)
- Reviews Python, TypeScript, and SQL code
- Provides consistent feedback on every PR

---

## Setup Steps

### Step 1: Install CodeRabbit GitHub App

1. **Go to CodeRabbit:**
   - Visit: https://coderabbit.ai
   - Click **"Get Started"** or **"Sign Up"**

2. **Connect to GitHub:**
   - Click **"Install GitHub App"**
   - Select your GitHub account
   - Choose **"Only select repositories"**
   - Select **"benchsight"** repository
   - Click **"Install"**

3. **Authorize CodeRabbit:**
   - Grant necessary permissions
   - CodeRabbit needs:
     - Read access to code
     - Write access to comments (for reviews)
     - Read access to pull requests

### Step 2: Configure CodeRabbit

**Option A: Use Configuration File (Recommended)**

The project already includes `.coderabbit.yaml` with BenchSight-specific settings:

```yaml
# Already configured for:
# - Python code review (ETL, API)
# - TypeScript/React review (Dashboard)
# - SQL review (Views, migrations)
# - BenchSight-specific patterns (GOAL_FILTER, etc.)
```

**Option B: Configure via Web Interface**

1. Go to: https://app.coderabbit.ai
2. Select your repository
3. Go to **Settings**
4. Configure review preferences

### Step 3: Verify Setup

1. **Create a test PR:**
   ```bash
   git checkout -b test/coderabbit-setup
   # Make a small change
   git commit -m "Test CodeRabbit integration"
   git push origin test/coderabbit-setup
   ```

2. **Create Pull Request:**
   - Go to GitHub → Your repo
   - Create PR: `test/coderabbit-setup` → `main`
   - CodeRabbit should automatically start reviewing

3. **Check for CodeRabbit comments:**
   - Look for comments from `coderabbit[bot]`
   - Should appear within 1-2 minutes

---

## How It Works

### Automatic Reviews

**When CodeRabbit reviews:**
- ✅ New pull requests (automatically)
- ✅ New commits pushed to PR
- ✅ PR is reopened
- ✅ PR is updated

**What CodeRabbit checks:**
- Code quality and best practices
- BenchSight-specific patterns (GOAL_FILTER, etc.)
- Security vulnerabilities
- Performance issues
- Documentation completeness
- Type safety
- Error handling

### Review Process

1. **PR Created** → CodeRabbit detects it
2. **Code Analysis** → Scans all changed files
3. **Review Comments** → Posts detailed feedback
4. **Summary** → Provides high-level overview
5. **Follow-up** → Reviews new commits automatically

---

## Configuration Details

### Current Configuration (`.coderabbit.yaml`)

**Python Reviews:**
- Reviews all Python files (`src/`, `api/`, `scripts/`)
- Checks for BenchSight patterns:
  - GOAL_FILTER usage
  - Single source of truth
  - Type consistency
  - Error handling

**TypeScript Reviews:**
- Reviews dashboard code (`ui/dashboard/`)
- Checks for:
  - Type safety
  - Component structure
  - Supabase client patterns

**SQL Reviews:**
- Reviews SQL files (`sql/`)
- Checks for:
  - Query performance
  - Correctness
  - Schema consistency

**Ignored Paths:**
- `node_modules/`, `.next/`, `__pycache__/`
- `data/raw/`, `data/output/` (large files)
- `archive/`, `logs/`

---

## BenchSight-Specific Rules

CodeRabbit is configured to check for:

### 1. Goal Counting Pattern
```python
# ✅ GOOD - CodeRabbit will approve
GOAL_FILTER = (
    (df['event_type'] == 'Goal') & 
    (df['event_detail'] == 'Goal_Scored')
)

# ❌ BAD - CodeRabbit will flag
goals = df[df['event_type'] == 'Goal']  # Missing Goal_Scored check
```

### 2. Single Source of Truth
```python
# ❌ BAD - CodeRabbit will suggest refactoring
def count_goals_v1():
    return events[events.event_type == 'Goal']

def count_goals_v2():
    return events[events.event_detail == 'Goal_Scored']
```

### 3. Type Consistency
```python
# ❌ BAD - CodeRabbit will flag
merged = df1.merge(df2, on='player_id')  # Types might not match

# ✅ GOOD
df1['player_id'] = df1['player_id'].astype(str)
df2['player_id'] = df2['player_id'].astype(str)
merged = df1.merge(df2, on='player_id')
```

### 4. Error Handling
```python
# ❌ BAD - CodeRabbit will suggest improvement
try:
    result = risky_operation()
except:
    pass  # Silent failure

# ✅ GOOD
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
```

---

## Workflow Integration

### Typical Workflow with CodeRabbit

```bash
# 1. Create feature branch
git checkout -b feature/add-player-ratings

# 2. Make changes
# ... edit files ...

# 3. Commit and push
git add .
git commit -m "[FEAT] Add player ratings"
git push origin feature/add-player-ratings

# 4. Create PR on GitHub
# CodeRabbit automatically reviews

# 5. Address CodeRabbit feedback
# ... make improvements ...

# 6. Push updates
git push origin feature/add-player-ratings
# CodeRabbit reviews new commits automatically

# 7. Merge when ready
```

### Reviewing CodeRabbit Feedback

**Types of comments:**
- 🔴 **Errors** - Must fix (e.g., type mismatches, security issues)
- 🟡 **Warnings** - Should fix (e.g., code duplication, missing error handling)
- 🔵 **Suggestions** - Nice to have (e.g., performance improvements, documentation)

**How to respond:**
- ✅ **Fix it** - If the suggestion is valid
- 💬 **Explain** - If you have a good reason to keep it as-is
- 🔕 **Dismiss** - If not applicable (rare)

---

## Customizing CodeRabbit

### Update Configuration

Edit `.coderabbit.yaml`:

```yaml
# Add custom rules
rules:
  - name: "custom_rule"
    description: "Your custom check"
    pattern: "your_pattern"
    severity: "warning"
```

### Adjust Review Settings

```yaml
# Make reviews more/less strict
review:
  focus_areas:
    - "code_quality"  # Always check
    - "performance"    # Always check
    - "documentation"  # Always check
```

### Ignore Specific Files

```yaml
ignore:
  paths:
    - "specific/file.py"  # Don't review this file
    - "generated/**"       # Don't review generated code
```

---

## Best Practices

### ✅ Do This

1. **Read CodeRabbit feedback** - It catches real issues
2. **Fix critical issues** - Errors and security problems
3. **Consider suggestions** - They often improve code quality
4. **Use as learning tool** - Understand why suggestions are made
5. **Keep configuration updated** - Adjust as project evolves

### ❌ Don't Do This

1. **Ignore all feedback** - CodeRabbit finds real issues
2. **Dismiss without reading** - Understand the suggestion first
3. **Disable for entire PR** - Use sparingly, only if needed
4. **Skip manual review** - CodeRabbit complements, doesn't replace human review

---

## Troubleshooting

### "CodeRabbit isn't reviewing my PR"

**Check:**
1. Is CodeRabbit app installed? (GitHub → Settings → Applications)
2. Is the repository selected? (CodeRabbit dashboard)
3. Did you push to the branch? (CodeRabbit reviews on push)
4. Check PR comments for CodeRabbit status

**Fix:**
- Reinstall CodeRabbit app if needed
- Check CodeRabbit dashboard for errors
- Try creating a new PR

### "CodeRabbit is too strict/lenient"

**Adjust settings:**
- Edit `.coderabbit.yaml`
- Change `severity` levels
- Add/remove `focus_areas`
- Adjust `rules` configuration

### "CodeRabbit is reviewing too many files"

**Update ignore paths:**
```yaml
ignore:
  paths:
    - "path/to/ignore/**"
```

### "CodeRabbit suggestions don't apply"

**Options:**
- Reply to comment explaining why
- Dismiss the suggestion (if truly not applicable)
- Update configuration to exclude pattern

---

## Integration with Other Tools

### GitHub Actions

CodeRabbit works alongside GitHub Actions:
- CodeRabbit: Code quality review
- GitHub Actions: Automated tests, linting, etc.

**Both run automatically on PRs!**

### Branch Protection

Use CodeRabbit with branch protection:
1. Set up branch protection rules (require PR reviews)
2. CodeRabbit provides automated review
3. Human reviewer provides final approval

---

## CodeRabbit Features

### Automatic Reviews
- Reviews every PR automatically
- Re-reviews on new commits
- Provides detailed line-by-line feedback

### Smart Suggestions
- Context-aware recommendations
- BenchSight-specific pattern detection
- Performance optimizations

### Summary Reports
- High-level overview of changes
- Focus on critical issues
- Actionable feedback

### Chat Interface
- Ask questions about code
- Get explanations
- Interactive code review

---

## Example Review

**What CodeRabbit might say:**

```markdown
## 🤖 CodeRabbit Review

### Summary
Found 3 issues in this PR:
- 1 error (must fix)
- 2 warnings (should fix)

### Issues Found

#### 🔴 Error: Goal Counting Pattern
**File:** `src/tables/macro_stats.py:45`

```python
# Current code
goals = df[df['event_type'] == 'Goal']
```

**Issue:** Missing `Goal_Scored` check. Should use GOAL_FILTER pattern.

**Fix:**
```python
GOAL_FILTER = (
    (df['event_type'] == 'Goal') & 
    (df['event_detail'] == 'Goal_Scored')
)
goals = df[GOAL_FILTER]
```

#### 🟡 Warning: Type Consistency
**File:** `src/tables/macro_stats.py:120`

**Issue:** Potential type mismatch before merge. Ensure consistent types.

**Suggestion:** Add type conversion before merge.
```

---

## Cost

**CodeRabbit Pricing:**
- **Free tier:** Limited reviews (check current limits)
- **Pro tier:** Unlimited reviews (paid)

**For BenchSight:**
- Start with free tier
- Upgrade if needed for more reviews
- Most small teams can use free tier

---

## Next Steps

1. **Install CodeRabbit** - Follow Step 1 above
2. **Create test PR** - Verify it works
3. **Review feedback** - See what CodeRabbit catches
4. **Adjust configuration** - Customize `.coderabbit.yaml` as needed
5. **Integrate into workflow** - Use for all PRs

**For complete setup including GitHub, environments, and CodeRabbit together, see: [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)**

---

## Resources

- **CodeRabbit Docs:** https://docs.coderabbit.ai
- **Configuration Reference:** https://docs.coderabbit.ai/configuration
- **GitHub App:** https://github.com/apps/coderabbitai

---

## Questions?

- Check CodeRabbit dashboard: https://app.coderabbit.ai
- Review configuration: `.coderabbit.yaml`
- See example reviews on test PRs

---

*Last updated: 2026-01-13*
