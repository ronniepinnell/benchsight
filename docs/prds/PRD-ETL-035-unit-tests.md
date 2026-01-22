# PRD: ETL-035 - Create Unit Tests for Critical Calculations

**Product Requirements Document**

Created: 2026-01-22
Status: Approved
Owner: Developer
Related Issues: #36

---

## Problem Statement

**What problem are we solving?**

The ETL pipeline has complex calculations (goals, assists, Corsi, xG, WAR) but minimal test coverage. When refactoring code (like vectorization #5), we have no safety net to catch regressions.

**Why is this important?**

- Calculation errors propagate to all downstream data
- Refactoring without tests is risky
- No way to verify hockey-specific business rules
- Technical debt accumulates without test coverage

**Who is affected?**

- Developers making changes (fear of breaking things)
- Users relying on accurate stats
- Data integrity of entire platform

---

## Solution Approach

**How will we solve this problem?**

Create comprehensive unit tests for all critical calculation modules:
1. Goal counting (most critical)
2. Assist attribution
3. Corsi/Fenwick
4. Time on ice
5. xG model inputs
6. WAR/GAR calculations

**Testing Philosophy:**
- Test the business rules, not just code paths
- Use realistic test fixtures from actual game data
- Tests document expected behavior
- Fast tests that run on every commit

---

## Technical Design

### Architecture

**Test Structure:**

```
tests/
├── unit/
│   ├── calculations/
│   │   ├── test_goals.py           # Goal counting rules
│   │   ├── test_assists.py         # Assist attribution
│   │   ├── test_corsi.py           # Corsi/Fenwick
│   │   ├── test_time.py            # TOI calculations
│   │   ├── test_xg.py              # xG inputs
│   │   └── test_war.py             # WAR/GAR
│   ├── etl/
│   │   ├── test_event_builders.py
│   │   └── test_shift_builders.py
│   └── conftest.py                 # Shared fixtures
├── integration/
│   └── test_etl_pipeline.py        # Full ETL run
└── fixtures/
    ├── sample_events.csv
    ├── sample_shifts.csv
    └── expected_outputs/
```

### Implementation Details

**Critical Test Cases:**

**1. Goal Counting (test_goals.py):**
```python
class TestGoalCounting:
    """Tests for CLAUDE.md goal counting rules."""

    def test_goal_filter_both_conditions(self, sample_events):
        """Goal counted ONLY when event_type='Goal' AND event_detail='Goal_Scored'"""
        goals = filter_goals(sample_events)
        # Verify correct filter applied
        assert all(goals['event_type'] == 'Goal')
        assert all(goals['event_detail'] == 'Goal_Scored')

    def test_shot_goal_not_counted(self, sample_events):
        """event_type='Shot' with event_detail='Goal' is NOT a goal"""
        # This is the most common mistake
        goals = filter_goals(sample_events)
        shot_goals = sample_events[
            (sample_events['event_type'] == 'Shot') &
            (sample_events['event_detail'] == 'Goal')
        ]
        # None of these should be in goals
        for idx in shot_goals.index:
            assert idx not in goals.index

    def test_goal_count_matches_official(self, game_18969_events):
        """Goal count matches official scoresheet for game 18969"""
        goals = count_goals_by_team(game_18969_events)
        assert goals['home'] == 5  # Official home score
        assert goals['away'] == 3  # Official away score
```

**2. Assist Attribution (test_assists.py):**
```python
class TestAssistAttribution:
    """Tests for CLAUDE.md assist rules."""

    def test_primary_assist_counted(self, goal_event):
        """AssistPrimary in play_details counts as assist"""
        assists = get_assists(goal_event)
        assert any(a['type'] == 'primary' for a in assists)

    def test_secondary_assist_counted(self, goal_event):
        """AssistSecondary in play_details counts as assist"""
        assists = get_assists(goal_event)
        assert any(a['type'] == 'secondary' for a in assists)

    def test_tertiary_assist_not_counted(self, goal_event):
        """AssistTertiary does NOT count (hockey only counts 2 assists)"""
        assists = get_assists(goal_event)
        assert not any(a['type'] == 'tertiary' for a in assists)
        assert len(assists) <= 2
```

**3. Stat Counting Rules (test_stat_counting.py):**
```python
class TestStatCounting:
    """Tests for CLAUDE.md stat counting rules."""

    def test_only_event_player_1_counts(self, multi_player_event):
        """Stats only counted for player_role='event_player_1'"""
        shots = count_shots(multi_player_event)
        # Should be 1, not count for event_player_2
        assert shots == 1

    def test_linked_event_micro_stat_once(self, linked_events):
        """Micro-stats in linked events only counted once"""
        # e.g., 'receivermissed' appears in pass->zone exit->turnover
        # Should only count once, not 3 times
        micro_stats = count_micro_stats(linked_events)
        assert micro_stats['receivermissed'] == 1
```

---

## Implementation Phases

### Phase 1: Test Infrastructure Setup

**Description:** Set up testing framework and fixtures.

**Tasks:**
- [ ] Create test directory structure
- [ ] Set up pytest configuration
- [ ] Create sample data fixtures from real games
- [ ] Create conftest.py with shared fixtures
- [ ] Add pytest to requirements.txt

**Success Criteria:**
- `pytest` runs successfully
- Fixtures load correctly
- Test discovery works

### Phase 2: Critical Calculation Tests

**Description:** Tests for highest-priority calculations.

**Tasks:**
- [ ] test_goals.py - Goal counting rules
- [ ] test_assists.py - Assist attribution
- [ ] test_stat_counting.py - Event player rules
- [ ] test_faceoffs.py - Faceoff winner/loser

**Success Criteria:**
- All CLAUDE.md rules have corresponding tests
- Tests pass with current implementation
- Tests catch intentional bugs

### Phase 3: Advanced Calculation Tests

**Description:** Tests for complex calculations.

**Tasks:**
- [ ] test_corsi.py - Corsi/Fenwick calculations
- [ ] test_time.py - Time on ice
- [ ] test_xg.py - xG model inputs
- [ ] test_war.py - WAR/GAR calculations

**Success Criteria:**
- All calculation modules have tests
- Edge cases covered
- Performance acceptable (<30s total)

### Phase 4: CI Integration

**Description:** Integrate tests into development workflow.

**Tasks:**
- [ ] Add to GitHub Actions
- [ ] Add to pre-commit hooks (optional)
- [ ] Add coverage reporting
- [ ] Block PR merge on test failure

**Success Criteria:**
- Tests run on every PR
- Coverage visible in PRs
- Cannot merge with failing tests

---

## Success Criteria

**How do we know this is complete and successful?**

- [ ] >80% coverage of `src/calculations/`
- [ ] All CLAUDE.md business rules have tests
- [ ] Tests run in <30 seconds
- [ ] Tests integrated into CI
- [ ] Tests catch intentional bugs

**Acceptance Tests:**
- Introduce goal counting bug → test fails
- Change assist logic → test fails
- Refactor code → tests still pass (no regression)

---

## Dependencies

**What needs to exist or be completed first?**

- [ ] pytest installed and configured
- [ ] Sample test data from real games

**Blocking Issues:**
- None - can start immediately

---

## Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Tests too slow | Medium | Medium | Use small fixtures, profile tests |
| Flaky tests | Medium | Low | Avoid time-dependent tests |
| Low coverage | Medium | Medium | Track coverage, enforce minimums |
| Tests don't catch real bugs | High | Medium | Write tests based on past bugs |

---

## Testing Strategy

**Test Types:**

| Type | Purpose | Speed |
|------|---------|-------|
| Unit | Individual functions | Fast (<1s each) |
| Integration | Full calculation flow | Medium (<10s) |
| Regression | Known bug scenarios | Fast |

**Test Data:**
- Small, focused fixtures
- Real data extracts (anonymized if needed)
- Edge case data (empty, nulls, etc.)

---

## Documentation

**What documentation needs to be updated?**

- [ ] README with test running instructions
- [ ] Test file docstrings explaining rules being tested

---

## Related Documents

- [CLAUDE.md - Business Rules](../../CLAUDE.md)
- [Calculations Module](../../src/calculations/)

---

## Notes

**Test Fixture Example:**

```python
# conftest.py
import pytest
import pandas as pd

@pytest.fixture
def sample_goal_event():
    """A single goal event with all required fields."""
    return pd.DataFrame([{
        'event_type': 'Goal',
        'event_detail': 'Goal_Scored',
        'player_role': 'event_player_1',
        'player_id': 'P001',
        'game_id': 'G18969',
        'period': 2,
        'time': '10:30',
        'play_details1': 'AssistPrimary',
        'play_details2': 'AssistSecondary'
    }])

@pytest.fixture
def sample_shot_with_goal_detail():
    """A shot event that should NOT be counted as goal."""
    return pd.DataFrame([{
        'event_type': 'Shot',  # Not 'Goal'!
        'event_detail': 'Goal',  # Misleading but not a goal
        'player_role': 'event_player_1',
        'player_id': 'P002',
    }])
```

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-22 | Initial PRD | Claude |

---

*Status: Approved*
