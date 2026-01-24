# Git Worktree Workflow

> **CRITICAL: Claude must read this before ANY git branch operations**

## Setup

Two parallel worktrees for concurrent development:

| Directory | Purpose |
|-----------|---------|
| `benchsight/` | Feature branch work |
| `benchsight-dev/` | Feature branch work |

## ABSOLUTE RULES

### 1. NEVER checkout `develop` or `main` directly
- Both directories should ALWAYS be on feature branches
- Use `origin/develop` as the base for new branches
- If stuck on main/develop, hooks will break

### 2. Branch naming follows GitHub issues
```
feature/{issue#}-{short-description}
fix/{issue#}-{short-description}
```

Examples:
- `feature/121-pre-etl-validation`
- `fix/64-duplicate-event-player-keys`

### 3. Creating a new feature branch
```bash
git fetch origin
git checkout -b feature/{issue#}-description origin/develop
```

### 4. Merging workflow
```
feature/* ──PR──> develop ──PR──> main (releases only)
```

- PRs always target `develop`
- NEVER push directly to `main`
- NEVER push directly to `develop`

### 5. NEVER suggest removing worktrees
The worktree setup is intentional for parallel work.

### 6. If stuck on main (hooks broken)
```bash
git stash
git checkout -f -b feature/temp origin/develop
```

## Common Commands

### Start new work (in either directory)
```bash
git fetch origin
git checkout -b feature/{issue#}-description origin/develop
```

### After PR is merged
```bash
git fetch origin
git checkout -b feature/{next-issue#}-description origin/develop
git branch -D feature/old-branch  # delete old branch
```

### Check current state
```bash
git worktree list
git branch -vv
```

## Troubleshooting

### "branch already used by worktree"
You're trying to checkout a branch that's checked out in the other directory.
Solution: Create a NEW feature branch with a different name.

### Stuck on main/develop (hooks failing)
```bash
git stash
git checkout -f -b feature/temp origin/develop
```

### Git LFS file blocking checkout
```bash
git checkout -f -b feature/branch-name origin/develop
```

## What NOT to do

- ❌ `git checkout develop`
- ❌ `git checkout main`
- ❌ `git worktree remove`
- ❌ Push directly to develop or main
- ❌ Create branches not tied to issues
- ❌ Use placeholder branch names like `feature/{issue#}-description`
