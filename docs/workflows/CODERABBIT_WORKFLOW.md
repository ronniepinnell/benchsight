# CodeRabbit Workflow

**CodeRabbit integration into PR process**

Last Updated: 2026-01-21

---

## Overview

CodeRabbit provides automated AI-powered code reviews for every pull request. This document outlines how CodeRabbit fits into the PR process.

---

## CodeRabbit in PR Process

### Automatic Reviews

**CodeRabbit automatically:**
- Reviews new pull requests
- Reviews new commits pushed to PR
- Reviews PR updates
- Reviews reopened PRs

**No action needed** - CodeRabbit runs automatically.

---

## PR Workflow with CodeRabbit

### Step 1: Create PR

**Create pull request:**
- Push branch to GitHub
- Create PR using template
- CodeRabbit automatically starts reviewing

### Step 2: Review CodeRabbit Feedback

**Types of feedback:**
- 🔴 **Errors** - Must fix (e.g., type mismatches, security issues)
- 🟡 **Warnings** - Should fix (e.g., code duplication, missing error handling)
- 🔵 **Suggestions** - Nice to have (e.g., performance improvements, documentation)

### Step 3: Address Feedback

**How to respond:**
- ✅ **Fix it** - If the suggestion is valid
- 💬 **Explain** - If you have a good reason to keep it as-is
- 🔕 **Dismiss** - If not applicable (rare)

### Step 4: Push Updates

**After addressing feedback:**
- Push new commits
- CodeRabbit automatically reviews new commits
- Continue until all feedback addressed

### Step 5: Merge

**When ready:**
- All CodeRabbit feedback addressed
- Human review approved
- Merge PR

---

## CodeRabbit Configuration

### BenchSight-Specific Rules

**CodeRabbit checks for:**
- Goal counting pattern (GOAL_FILTER)
- Single source of truth
- Type consistency
- Performance patterns (.iterrows() usage)
- Error handling
- Documentation

**Configuration:** `.coderabbit.yaml`

---

## Responding to CodeRabbit Feedback

### Fix It

**When to fix:**
- Errors (must fix)
- Valid warnings
- Good suggestions

**How:**
1. Read the feedback
2. Understand the issue
3. Make the fix
4. Push the update

### Explain

**When to explain:**
- You have a good reason
- The suggestion doesn't apply
- Context matters

**How:**
1. Reply to CodeRabbit comment
2. Explain your reasoning
3. Provide context

### Dismiss

**When to dismiss:**
- Truly not applicable
- False positive
- Not relevant

**How:**
1. Dismiss the suggestion
2. Add note if needed

---

## CodeRabbit Best Practices

### ✅ Do:

- Read all CodeRabbit feedback
- Fix critical issues
- Consider suggestions
- Learn from feedback
- Use as learning tool

### ❌ Don't:

- Ignore all feedback
- Dismiss without reading
- Skip manual review
- Disable CodeRabbit

---

## CodeRabbit and Human Review

### Both Are Important

**CodeRabbit:**
- Automated code quality checks
- Pattern detection
- Consistency checks
- BenchSight-specific rules

**Human Review:**
- Business logic review
- Architecture decisions
- Design review
- Final approval

**Both complement each other.**

---

## Customizing CodeRabbit

### Update Configuration

**Edit:** `.coderabbit.yaml`

**Common updates:**
- Add custom rules
- Adjust severity levels
- Add/remove focus areas
- Update ignore paths

### BenchSight-Specific Rules

**Add rules for:**
- New patterns
- Common issues
- Project-specific checks

---

## Troubleshooting

### CodeRabbit Not Reviewing

**Check:**
1. Is CodeRabbit app installed?
2. Is repository selected?
3. Did you push to branch?
4. Check PR comments for status

**Fix:**
- Reinstall CodeRabbit app if needed
- Check CodeRabbit dashboard
- Try creating new PR

### CodeRabbit Too Strict/Lenient

**Adjust:**
- Edit `.coderabbit.yaml`
- Change severity levels
- Add/remove focus areas
- Adjust rules configuration

---

## Related Documentation

- `.coderabbit.yaml` - Configuration
- [WORKFLOW.md](WORKFLOW.md) - Development workflow
- [DOCUMENTATION_MAINTENANCE.md](DOCUMENTATION_MAINTENANCE.md) - Documentation maintenance

---

*Last Updated: 2026-01-15*
