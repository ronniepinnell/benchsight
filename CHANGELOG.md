# Changelog

All notable changes to BenchSight will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Usage logging hook for skills/agents/commands (`usage-logger.py`)
- Usage analysis script (`scripts/analyze-usage.py`)
- Dead code cleanup tracking in `/pm improve`
- GitHub issue #50 for dead code cleanup
- Component logs structure (`logs/*.log.md`) for tracking changes per component
- Version/changelog/log update requirements at commit time
- Environment management docs (dev vs prod Supabase/Vercel)
- Context/token usage monitoring guidance
- Session handoff checklists
- `/audit` skill - full codebase audit (full/quick/security/quality/compliance)
- `code-explainer` agent - line-by-line, flow, architecture, ETL, changes explanations
- Interactive mode for code-explainer (prompts for target, follow-up Q&A, session logging)
- `logs/explanations/` folder for storing code explanation sessions
- Documentation drift warning in `/pm` skill
- **Living Documentation System:**
  - `docs/code-docs/` - auto-updating code explanations
  - `docs/table-docs/` - auto-updating table documentation
  - Living docs persist across reviews and auto-sync with code changes
- **Issue Detection & Auto-Escalation:**
  - Code-explainer now scans for issues during reviews
  - CRITICAL issues auto-create/update GitHub issues
  - HIGH/MEDIUM/LOW issues logged to `logs/issues/detected.jsonl`
  - `docs/backlog/auto-detected.md` tracks all detected issues
- `table-explainer` agent - schema, ETL path, lineage, QA rules, relationships
- `component-explainer` agent - dashboard, portal, tracker, API, ML/CV explanation
- `feature-template-generator` agent - create new explainer templates for features
- `docs/component-docs/` - living component documentation
- GitHub issue creation from all explainer agents
- **Q&A Mode for Key Agents:**
  - `/pm ask "question"` - PM decision Q&A with logging
  - `/mentor ask "question"` - Workflow Q&A with logging
  - `hockey-analytics-sme` Q&A mode with research logging
- **Unified Logging:** All Q&A, decisions, and issues log to `logs/issues/detected.jsonl`
- `data-dictionary-specialist` agent - maintains docs/data/, traces lineage, updates ERDs

### Changed
- Reorganized docs folder structure (moved 14 files to subfolders)
- Updated MASTER_INDEX.md with new paths and living docs sections
- Enhanced QUICK_REFERENCE.md with maintenance scripts section and new agents
- `/github-workflow commit` now requires version/changelog/log updates
- `/pm` skill now includes environment and session management guidance
- AGENTS_GUIDE.md updated with code-explainer and table-explainer
- Simplified logging structure (removed separate logs/pm/, consolidated to logs/issues/)
- logs/issues/README.md updated for unified log format

## [1.0.0-alpha.2] - 2026-01-22

### Added
- `/github-workflow` skill - complete issue-to-merge workflow
- `/pm` skill enhancements - continuous improvement, reorg, improve commands
- `/mentor` skill - best practices guidance
- `/post-code` skill - 10-step validation workflow
- `/validate` skill - ETL-specific validation with hockey SME
- `/doc-sync` skill - documentation synchronization
- GitHub milestones (M1-M5)
- Enhanced P0 issues with execution order, dependencies, acceptance criteria
- QUICK_REFERENCE.md - one-page essential reference
- COMPLETE_DEVELOPMENT_GUIDE.md - full workflow documentation

### Changed
- Consolidated dashboard docs (33 → 6 files, 27 archived)
- Updated all P0 issues with consistent detail level
- Fixed base_etl.py line count references (was 4,400+, now ~1,065)

### Fixed
- Documentation line count inaccuracies
- Tracker version references (v27.0 → v28.0)

## [1.0.0-alpha.1] - 2026-01-20

### Added
- ETL modularization (`src/core/etl_phases/`)
- Initial skill collection (29 skills)
- Hook system (6 hooks)
- Project structure documentation

### Changed
- Refactored base_etl.py from 4,400+ lines to ~1,065 lines
- Moved table generation logic to etl_phases modules

---

## Version Numbering

- **1.0.0** - First production release (target: end of M1)
- **alpha.N** - Development builds during Phase 2
- **beta.N** - Testing builds during Phase 3-4
- **rc.N** - Release candidates before 1.0.0
