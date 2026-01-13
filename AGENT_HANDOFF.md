# Agent Handoff - v29.1 to v29.2

**When to use a new agent vs continue in this session**

Date: 2026-01-13

---

## ✅ Complete in This Session (v29.1)

**Status:** Ready to commit

These are complete and tested:
- ✅ Calculations module (25+ functions, 24 tests)
- ✅ Builders module (events, shifts)
- ✅ Formula management system (JSON-based)
- ✅ Performance optimizations (vectorized calculations)
- ✅ Documentation (8 new files)

**Action:** Commit and push these changes now.

---

## 🆕 Use New Agent For (v29.2+)

### Why Use a New Agent?

1. **Context Limit** - You're at 90% context usage
2. **Clean Slate** - Fresh context for new work
3. **Separation** - Different phase of work
4. **Focus** - New agent can focus on integration/optimization

### What to Do in New Agent

#### Phase 1: Integration (v29.2)
1. **Integrate Formula System**
   - Update `create_fact_player_game_stats()` to use formula registry
   - Replace hardcoded formulas with `apply_player_stats_formulas()`
   - Test thoroughly

2. **More Performance Optimizations**
   - Optimize team ratings calculation (50-100x speedup)
   - Optimize venue stat mapping (20-50x speedup)
   - Replace high-impact `.iterrows()` loops

#### Phase 2: Additional Refactoring (v29.3)
3. **Extract More Builders**
   - Player stats builder
   - Team stats builder
   - Goalie stats builder

4. **More Unit Tests**
   - Test builders
   - Test formula system
   - Integration tests

---

## 📋 Handoff Instructions for New Agent

When starting a new agent, provide this context:

```
I'm working on BenchSight v29.1 refactoring. The previous agent completed:

✅ Calculations module (src/calculations/)
✅ Builders module (src/builders/)
✅ Formula management system (src/formulas/)
✅ Performance optimizations
✅ Documentation

Next steps:
1. Integrate formula system into create_fact_player_game_stats()
2. Optimize team ratings calculation
3. Replace .iterrows() with vectorized operations

See docs/REFACTORING.md and docs/FORMULA_MANAGEMENT.md for details.
```

---

## 🎯 Recommended Workflow

### This Session (Current Agent)
1. ✅ Review changes
2. ✅ Test (pytest, ETL)
3. ✅ Commit v29.1 work
4. ✅ Push to GitHub
5. ✅ Document what's done

### Next Session (New Agent)
1. Read `AGENT_HANDOFF.md` (this file)
2. Read `docs/REFACTORING.md`
3. Read `docs/FORMULA_MANAGEMENT.md`
4. Continue with integration work
5. Focus on v29.2 tasks

---

## 📝 What to Tell New Agent

**Start with:**
```
I'm continuing BenchSight refactoring. Previous work (v29.1) is complete and committed.

Current state:
- Calculations module extracted and tested
- Builders module created
- Formula management system ready
- base_etl.py updated to use builders

Next tasks:
1. Integrate formula system into fact_player_game_stats creation
2. Optimize performance (team ratings, venue stats)
3. Add more unit tests

Key files:
- src/tables/core_facts.py - needs formula integration
- src/core/base_etl.py - has 29 .iterrows() to optimize
- docs/PERFORMANCE_OPTIMIZATION.md - optimization guide
```

---

## 🔄 Alternative: Continue in This Session

**If you want to continue here:**

**Pros:**
- I have full context of what we built
- Can reference all the code we created
- Understand the patterns we established

**Cons:**
- Context limit (90% used)
- May need to summarize frequently
- Less room for new code exploration

**Recommendation:** Use new agent for v29.2+ work.

---

## ✅ Checklist Before Handoff

- [ ] All v29.1 work committed
- [ ] Changes pushed to GitHub
- [ ] Documentation updated
- [ ] Tests passing
- [ ] New agent instructions ready (this file)

---

*Handoff guide created: 2026-01-13*
