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

### Changed
- Reorganized docs folder structure (moved 14 files to subfolders)
- Updated MASTER_INDEX.md with new paths
- Enhanced QUICK_REFERENCE.md with maintenance scripts section
- `/github-workflow commit` now requires version/changelog/log updates
- `/pm` skill now includes environment and session management guidance

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
