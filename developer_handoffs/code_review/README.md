# Code Review Package

This folder contains everything needed for a senior engineer code review.

## Contents

| File | Purpose |
|------|---------|
| `CODE_REVIEW_HANDOFF.md` | Main handoff document with architecture, issues, recommendations |
| `TECHNICAL_DIAGRAMS.md` | ASCII diagrams of system architecture, data flow, etc. |
| `CODE_REVIEW_CHECKLIST.md` | Checklist for the review process |
| `NEXT_PROMPT.md` | Prompt to start Claude session |

## Quick Start

1. Read `CODE_REVIEW_HANDOFF.md` for full context
2. Use `NEXT_PROMPT.md` to start your Claude session
3. Work through `CODE_REVIEW_CHECKLIST.md`
4. Reference `TECHNICAL_DIAGRAMS.md` as needed

## Key Files to Review

```
scripts/bulletproof_loader.py  # Priority 1 - Supabase loader
src/main.py                    # Priority 2 - ETL entry point
src/pipeline/orchestrator.py   # Priority 3 - ETL coordinator
tests/                         # Priority 4 - Test coverage
sql/                           # Priority 5 - Schema definitions
```

## Running Tests

```bash
python -m pytest tests/ -v           # All tests
python -m pytest tests/ -v --tb=short # With tracebacks
python -m pytest tests/ --cov=src    # With coverage
```

## Checking Supabase Status

```bash
python scripts/bulletproof_loader.py --status
python scripts/bulletproof_loader.py --missing
```
