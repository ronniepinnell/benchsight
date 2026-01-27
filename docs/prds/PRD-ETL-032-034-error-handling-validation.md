# PRD: ETL-032/034 - Error Handling & Phase Validation

**Product Requirements Document**

Created: 2026-01-22
Status: Approved
Owner: Developer
Related Issues: #37 (ETL-032), #38 (ETL-034)

---

## Problem Statement

**What problem are we solving?**

The ETL pipeline lacks comprehensive error handling and validation:
1. **Error Handling (#37)**: Errors cause cryptic failures; no graceful degradation
2. **Phase Validation (#38)**: No validation between ETL phases; errors cascade

**Why is this important?**

- Hard to debug ETL failures
- Silent data corruption possible
- Errors discovered late (after all phases complete)
- No visibility into where things went wrong

**Who is affected?**

- Developers debugging ETL issues
- Portal users running ETL jobs
- Data quality for all downstream consumers

---

## Solution Approach

**Two-Part Solution:**

1. **Error Handling Framework**: Structured exceptions, logging, recovery
2. **Phase Validation Gates**: Validate output at each ETL phase before proceeding

**Design Principles:**
- Fail fast on critical errors
- Warn but continue on non-critical issues
- Clear, actionable error messages
- Validation gates between phases

---

## Technical Design

### Part 1: Error Handling Framework

**Exception Hierarchy:**

```python
class ETLError(Exception):
    """Base exception for all ETL errors."""
    pass

class ETLDataError(ETLError):
    """Data quality or integrity error."""
    pass

class ETLConfigError(ETLError):
    """Configuration or setup error."""
    pass

class ETLValidationError(ETLError):
    """Validation check failure."""
    pass

class ETLDependencyError(ETLError):
    """Missing dependency (file, table, etc.)."""
    pass
```

**Error Handling Wrapper:**

```python
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar('T')

def etl_phase(phase_name: str, critical: bool = True):
    """Decorator for ETL phase functions with error handling."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            log.info(f"Starting phase: {phase_name}")
            try:
                result = func(*args, **kwargs)
                log.info(f"Completed phase: {phase_name}")
                return result
            except ETLError as e:
                log.error(f"ETL error in {phase_name}: {e}")
                if critical:
                    raise
                log.warning(f"Continuing despite error in {phase_name}")
                return None
            except Exception as e:
                log.error(f"Unexpected error in {phase_name}: {e}")
                raise ETLError(f"Phase {phase_name} failed: {e}") from e
        return wrapper
    return decorator
```

**Usage:**

```python
@etl_phase("Build Event Players", critical=True)
def _build_event_players(self) -> pd.DataFrame:
    if self.raw_events is None:
        raise ETLDependencyError("raw_events not loaded")
    # ... rest of function
```

### Part 2: Phase Validation Gates

**Validation Gate Structure:**

```python
class PhaseValidation:
    """Validation checks to run after each ETL phase."""

    @staticmethod
    def validate_loading_phase(etl: 'BaseETL') -> ValidationResult:
        """Validate after loading raw data."""
        checks = [
            Check("raw_events loaded", etl.raw_events is not None),
            Check("raw_events not empty", len(etl.raw_events) > 0),
            Check("raw_shifts loaded", etl.raw_shifts is not None),
            Check("required columns present",
                  all(c in etl.raw_events.columns for c in REQUIRED_COLS)),
        ]
        return ValidationResult(checks)

    @staticmethod
    def validate_event_building_phase(etl: 'BaseETL') -> ValidationResult:
        """Validate after building events."""
        checks = [
            Check("event_players created", 'event_players' in etl.tables),
            Check("events have game_id",
                  'game_id' in etl.tables['event_players'].columns),
            Check("no duplicate event_keys",
                  etl.tables['event_players']['event_key'].is_unique),
        ]
        return ValidationResult(checks)

    @staticmethod
    def validate_calculations_phase(etl: 'BaseETL') -> ValidationResult:
        """Validate after calculations."""
        checks = [
            Check("goals count reasonable",
                  0 < len(etl.tables.get('fact_goals', [])) < 1000),
            Check("no negative TOI values",
                  (etl.tables['fact_player_game_stats']['toi'] >= 0).all()),
        ]
        return ValidationResult(checks)
```

**Validation Runner:**

```python
def run_with_validation(self):
    """Run ETL with validation gates between phases."""

    # Phase 1: Loading
    self._load_data()
    result = PhaseValidation.validate_loading_phase(self)
    if not result.passed:
        raise ETLValidationError(f"Loading phase failed: {result.failures}")

    # Phase 2: Event Building
    self._build_events()
    result = PhaseValidation.validate_event_building_phase(self)
    if not result.passed:
        raise ETLValidationError(f"Event building failed: {result.failures}")

    # Phase 3: Calculations
    self._run_calculations()
    result = PhaseValidation.validate_calculations_phase(self)
    if not result.passed:
        raise ETLValidationError(f"Calculations failed: {result.failures}")

    # ... continue with remaining phases
```

---

## Implementation Phases

### Phase 1: Error Handling Infrastructure

**Description:** Create error handling framework.

**Tasks:**
- [ ] Create `src/core/exceptions.py` with ETL exception hierarchy
- [ ] Create `src/core/decorators.py` with `@etl_phase` decorator
- [ ] Apply decorator to all major ETL functions
- [ ] Improve error messages in existing code

**Success Criteria:**
- All ETL phases wrapped with decorator
- Clear error messages on failure
- Errors logged with context

### Phase 2: Validation Framework

**Description:** Create validation gate system.

**Tasks:**
- [ ] Create `src/validation/phase_validation.py`
- [ ] Define validation checks for each phase
- [ ] Create `ValidationResult` class with reporting
- [ ] Integrate into `run_etl.py`

**Success Criteria:**
- Validation runs after each phase
- Clear failure messages
- ETL stops on critical validation failures

### Phase 3: Integration & Testing

**Description:** Integrate into workflow and test.

**Tasks:**
- [ ] Add `--validate` flag to ETL (enabled by default)
- [ ] Add validation summary to ETL output
- [ ] Create tests for error handling
- [ ] Test with intentionally broken data

**Success Criteria:**
- Validation runs by default
- Can skip with `--no-validate` flag
- Clear reporting of validation status

---

## Success Criteria

**How do we know this is complete and successful?**

- [ ] All ETL phases have error handling
- [ ] Validation runs between each phase
- [ ] Clear error messages for all failure modes
- [ ] Errors caught early, not at end of pipeline
- [ ] Logging shows phase progress and validation results

**Acceptance Tests:**
- Introduce data error → caught at appropriate phase
- Remove required file → clear dependency error
- Create invalid FK → validation catches it

---

## Dependencies

**What needs to exist or be completed first?**

- [ ] Basic ETL pipeline working
- [ ] Logging infrastructure (already exists)

**Blocking Issues:**
- None

---

## Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Too strict validation | Medium | Medium | Start with critical checks only |
| Performance impact | Low | Low | Validation is fast (in-memory) |
| False positives | Medium | Low | Tune thresholds carefully |

---

## Related Documents

- [ETL Architecture](../etl/ETL_ARCHITECTURE.md)
- [ETL Code Walkthrough](../walkthrough/etl/05-etl-code-walkthrough.md)

---

## Notes

**Validation Levels:**

| Level | Behavior | Example |
|-------|----------|---------|
| CRITICAL | Stop ETL | Missing required data |
| ERROR | Log + continue | FK violation |
| WARNING | Log only | Low row count |

**Error Message Format:**

```
ETLValidationError: Phase 'Build Events' failed validation

Failures:
  ✗ [CRITICAL] event_players table empty (expected >0 rows)
  ✗ [ERROR] 3 events missing game_id

Context:
  - Game files loaded: 4
  - Total raw events: 15,234
  - Phase runtime: 2.3s

Suggestion: Check that game files contain valid event data
```

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-22 | Initial PRD | Claude |

---

*Status: Approved*
