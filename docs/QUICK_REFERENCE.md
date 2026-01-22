# BenchSight Quick Reference

**Your single page for everything. Print this.**

---

## The Only Workflow You Need

```
/github-workflow next    → Get issue, create branch
[implement]              → Write code
/github-workflow commit  → Validate + commit
/github-workflow pr      → Create PR
/github-workflow merge   → Merge + cleanup
```

---

## Essential Commands

| What You Need | Command |
|---------------|---------|
| **Start working** | `/github-workflow next` |
| **Validate code** | `/post-code` |
| **Quick validate** | `/post-code quick` |
| **Commit ready** | `/github-workflow commit` |
| **Create PR** | `/github-workflow pr` |
| **Merge PR** | `/github-workflow merge` |
| **What's next** | `/pm next` |
| **Best practices** | `/mentor` |
| **ETL validation** | `/validate` |
| **Hockey stats help** | `/hockey-stats` |
| **Reality check** | `/reality-check` |

---

## Current Priority (P0 Execution Order)

| Do | Issue | Title |
|----|-------|-------|
| 1 | #31 | Investigate missing 7 tables |
| 2 | #35 | Table verification framework |
| 3 | #36 | Unit tests for calculations |
| 4 | #13 | Goal counting verification |
| 5 | #37 | Error handling |
| 6 | #38 | Phase validation |
| 7 | #5 | Vectorization |

---

## When to Commit

Commit after ANY of these:
- ✓ Function implemented and working
- ✓ Test written and passing
- ✓ Bug fixed and verified
- ✓ 3+ files changed
- ✓ 30+ minutes since last commit
- ✓ Before taking a break

**Rule:** If you'd be upset losing it, commit it.

---

## Critical CLAUDE.md Rules

### Goal Counting
```python
# ONLY valid pattern
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
```

### No .iterrows()
```python
# WRONG
for idx, row in df.iterrows():

# RIGHT
df.groupby('x').apply(func)
```

### Stat Attribution
```python
# Only count for event_player_1
stats = df[df['player_role'] == 'event_player_1']
```

---

## Skill Quick Guide

### Development Flow
| Skill | Use When |
|-------|----------|
| `/github-workflow` | Start/commit/PR flow |
| `/post-code` | After writing code |
| `/validate` | After ETL changes |
| `/mentor` | Need guidance |

### Specialists
| Skill | Use When |
|-------|----------|
| `/hockey-stats` | Calculation questions |
| `/db-dev` | Database work |
| `/dashboard-dev` | Dashboard work |
| `/etl` | Run ETL pipeline |

### Quality
| Skill | Use When |
|-------|----------|
| `/post-code` | Full validation |
| `/audit` | Full codebase audit |
| `/compliance-check` | CLAUDE.md rules |
| `/reality-check` | Verify completion |
| `/pm improve` | After fixes |

### Code Understanding (Subagents)
| Agent | Use When |
|-------|----------|
| `code-explainer` | Understand code, get line-by-line explanations |
| `table-explainer` | Understand tables, ETL paths, data lineage |

> **Tip:** These agents create living docs in `docs/code-docs/` and `docs/table-docs/` that auto-update on review.

---

## Git Commands

```bash
# Start work
git checkout develop && git pull
git checkout -b fix/description

# Commit
git add -A
git commit -m "[TYPE] Description (#N)"

# Push + PR
git push -u origin branch-name
gh pr create --body "Closes #N"

# Merge
gh pr merge --squash --delete-branch
git checkout develop && git pull
```

---

## Milestones

| Milestone | Phases | Current |
|-----------|--------|---------|
| M1: MVP Foundation | 1-4 | ← HERE |
| M2: Tracker Modernization | 5 | |
| M3: ML/CV Integration | 6 | |
| M4: Commercial Ready | 7-8 | |
| M5: AI Coaching Platform | 9-12 | |

---

## Key Documents

| Document | Purpose |
|----------|---------|
| `CLAUDE.md` | Project rules (CRITICAL) |
| `CHANGELOG.md` | Version history |
| `logs/*.log.md` | Component change logs |
| `logs/issues/detected.jsonl` | Auto-detected issues |
| `docs/MASTER_INDEX.md` | All documentation |
| `docs/code-docs/` | Living code explanations |
| `docs/table-docs/` | Living table documentation |
| `docs/backlog/auto-detected.md` | Auto-detected issue backlog |
| `docs/workflows/COMPLETE_DEVELOPMENT_GUIDE.md` | Full workflow guide |
| `.claude/skills/*/SKILL.md` | Skill documentation |
| `.claude/agents/*.md` | Subagent definitions |

---

## Maintenance Scripts

| Script | Purpose |
|--------|---------|
| `python scripts/analyze-usage.py` | See skill/agent usage stats |
| `python scripts/analyze-usage.py --unused` | Find unused skills/agents |
| `./scripts/sync-github-issues.sh` | Sync issues with backlog |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Wrong branch | `git checkout develop && git pull` |
| Merge conflicts | `git fetch origin && git merge origin/develop` |
| Tests failing | Fix before commit, never skip |
| Lost work | Check `git stash list`, `git reflog` |
| Stuck | `/mentor` or ask |

---

## Daily Checklist

### Start of Day
- [ ] `git checkout develop && git pull`
- [ ] `/github-workflow next`

### During Work
- [ ] Commit every 30 min or after milestones
- [ ] `/post-code quick` after changes
- [ ] Stay on current issue (no scope creep)

### End of Day
- [ ] All work committed
- [ ] `logs/*.log.md` updated
- [ ] Issue updated with progress
- [ ] `/pm status` to check state

---

## The 4 Rules

1. **Every change has an issue** - No exceptions
2. **Validate before commit** - `/post-code`
3. **Commit often** - Small, focused commits
4. **Update logs at commit** - `logs/*.log.md` + CHANGELOG

---

*When in doubt: `/mentor`*
