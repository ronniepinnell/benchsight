# Agent Handoff Prompt - BenchSight Refactoring v29.2-29.6

**Copy this entire prompt to give to the next agent:**

---

```
I'm continuing BenchSight refactoring. Previous work (v29.2-29.6) is complete and ready to commit.

✅ Completed in v29.2-29.6:
- Performance optimizations: 2.9x speedup (115s → 39.16s for 4 games)
- Builder extraction: PlayerStatsBuilder, TeamStatsBuilder, GoalieStatsBuilder
- Formula system integration: Centralized, maintainable, configurable
- Testing: 16 builder unit tests, formula integration tests (all passing)
- Data type optimization: Automatic optimization in table writer (30-50% memory reduction expected)
- Bug fixes: KeyError in shift enhancement, missing columns in shift_players

📝 Key Files Modified:
- src/tables/core_facts.py - Formula system integration, now uses builders
- src/core/base_etl.py - Performance optimizations, bug fixes
- src/core/table_writer.py - Data type optimization
- src/builders/player_stats.py - NEW: PlayerStatsBuilder
- src/builders/team_stats.py - NEW: TeamStatsBuilder
- src/builders/goalie_stats.py - NEW: GoalieStatsBuilder
- src/utils/data_type_optimizer.py - NEW: Data type optimization utility
- tests/test_builders.py - NEW: Builder unit tests
- tests/test_formulas_integration.py - NEW: Formula integration tests

📚 Documentation:
- docs/V29.2_OPTIMIZATIONS.md - Complete optimization summary
- docs/FORMULA_MANAGEMENT.md - Formula system guide
- docs/PERFORMANCE_OPTIMIZATION.md - Optimization guide
- docs/HONEST_CODEBASE_ASSESSMENT_V29.md - Comprehensive codebase assessment
- AGENT_HANDOFF_V29.2.md through AGENT_HANDOFF_V29.6.md - Phase handoffs
- REFACTORING_V29_SUMMARY.md - Complete summary

✅ Status: 
- All tests passing (16/16 builder tests)
- All validation checks passing (10/10)
- ETL produces 139 tables correctly
- 16 goals validated correctly
- Performance: 2.9x speedup validated
- Ready for commit

📊 Performance Results:
- 4 games: 39.16s (vs 115s baseline) = 2.9x speedup
- Extrapolated 100 games: ~16.3min (vs ~48min baseline)
- Data type optimization: Expected additional 1.5-2x speedup (not yet measured)

🎯 Next Steps (v29.7+):
1. Test data type optimization (run ETL, measure memory/performance)
2. Implement parallel processing for games (2-4x additional speedup expected)
3. Continue builder extraction (break down base_etl.py further)
4. Add calculation function unit tests (target 80% coverage)
5. Extract goalie calculation logic into methods
6. Extract calculation functions to src/calculations/ modules

📋 Current Codebase State:
- Overall Grade: B+ (78-82%) - Solid, functional, improving
- Production Readiness: ~80% (ready for 4-10 games, needs work for 100+ games)
- Technical Debt: 2-3 weeks of focused refactoring remaining
- Main Issues: base_etl.py still large (~4,800 lines), some test coverage gaps

🔍 Key Patterns to Follow:
- Builder pattern: See src/builders/events.py, shifts.py, player_stats.py
- Formula system: See src/formulas/formula_applier.py
- Single source of truth: See src/utils/game_type_aggregator.py
- Data type optimization: See src/utils/data_type_optimizer.py

⚠️ Important Notes:
- All optimizations maintain backward compatibility
- No breaking changes to output schema
- Formulas can be updated via JSON config
- Data type optimization is automatic (can be disabled per table)

🚀 Quick Start:
1. Review REFACTORING_V29_SUMMARY.md for complete overview
2. Review docs/HONEST_CODEBASE_ASSESSMENT_V29.md for codebase state
3. Run validation: python validate.py (should pass all checks)
4. Run benchmark: python scripts/benchmark_etl.py (should show ~39s for 4 games)
5. Start next phase work (see recommendations above)

See AGENT_HANDOFF_V29.6.md for complete details on latest phase.
```

---

**Additional Context for Next Agent:**

The codebase is in good shape and improving. Recent refactoring (v29.2-29.6) shows excellent architectural thinking:
- Builder pattern extraction
- Performance optimizations (vectorized operations)
- Formula system integration
- Comprehensive testing

The main remaining work is:
1. Continue breaking down large files (base_etl.py)
2. Add more unit tests (calculation functions)
3. Implement parallel processing (for scale)
4. Test with larger datasets

The foundation is solid. Continue the refactoring pattern established in v29.2-29.6.
