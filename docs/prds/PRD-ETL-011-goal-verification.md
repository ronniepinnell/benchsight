# PRD: ETL-011 - Verify Goal Counting Matches Official Counts

**Product Requirements Document**

Created: 2026-01-22
Status: Approved
Owner: Developer
Related Issues: #13

---

## Problem Statement

**What problem are we solving?**

Goal counting is the most critical stat in hockey analytics. The ETL pipeline must produce goal counts that **exactly** match official game records. Currently, there's no systematic verification that our counts are correct.

**Why is this important?**

- Goals are the foundation of all hockey analytics (xG, WAR, standings, etc.)
- Incorrect goal counts undermine trust in the entire platform
- CLAUDE.md has explicit rules about goal counting that must be enforced
- This is the #1 data integrity concern

**Who is affected?**

- All dashboard users viewing any stats
- Coaches making decisions based on data
- Players evaluating their performance

---

## Solution Approach

**How will we solve this problem?**

1. Create a verification test that compares ETL goal counts to official scoresheet totals
2. Add this verification to ETL validation suite
3. Fail the build if counts don't match exactly

**The Critical Rule (from CLAUDE.md):**

```python
# Goals are ONLY counted when BOTH conditions are true:
GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')

# NEVER count: event_type == 'Shot' with event_detail == 'Goal' (that's a shot attempt)
```

**What alternatives were considered?**

| Alternative | Decision |
|-------------|----------|
| Manual spot checks | Too error-prone, not scalable |
| Automated verification | **Selected** - reliable, repeatable |
| Accept small variance | Rejected - goals must be exact |

---

## Technical Design

### Architecture

**Verification Flow:**

```
Official Scores (scoresheets)
        ↓
  [Verification Script]
        ↓
  Compare to ETL Output
        ↓
   PASS (exact match) or FAIL (any difference)
```

### Implementation Details

**Key files/modules affected:**

| File | Change |
|------|--------|
| `tests/test_goal_verification.py` | Create/enhance verification tests |
| `data/validation/official_scores.json` | Official goal counts per game |
| `src/core/etl_phases/validation.py` | Add goal count validation |

**Official Scores Data Structure:**

```json
{
  "games": [
    {
      "game_id": "18969",
      "date": "2025-01-15",
      "home_team": "Team A",
      "away_team": "Team B",
      "home_goals": 5,
      "away_goals": 3,
      "source": "official_scoresheet"
    }
  ]
}
```

**Verification Logic:**

```python
def verify_goal_counts(etl_output_dir: Path, official_scores: dict) -> bool:
    """Verify ETL goal counts match official scores exactly."""
    fact_goals = pd.read_csv(etl_output_dir / 'fact_goals.csv')

    for game in official_scores['games']:
        game_id = game['game_id']

        # Count goals from ETL output
        game_goals = fact_goals[fact_goals['game_id'] == game_id]
        home_goals = len(game_goals[game_goals['is_home'] == True])
        away_goals = len(game_goals[game_goals['is_home'] == False])

        # Compare to official
        assert home_goals == game['home_goals'], \
            f"Game {game_id}: Home goals {home_goals} != official {game['home_goals']}"
        assert away_goals == game['away_goals'], \
            f"Game {game_id}: Away goals {away_goals} != official {game['away_goals']}"

    return True
```

---

## Implementation Phases

### Phase 1: Create Official Scores Reference

**Description:** Build the source of truth for goal verification.

**Tasks:**
- [ ] Create `data/validation/official_scores.json`
- [ ] Enter official scores for all tracked games (4 games initially)
- [ ] Document source of official scores (scoresheets, league records)

**Success Criteria:**
- JSON file with all game scores
- Scores verified against original scoresheets

### Phase 2: Create Verification Test

**Description:** Build automated test that compares ETL to official.

**Tasks:**
- [ ] Create/update `tests/test_goal_verification.py`
- [ ] Test loads official scores and compares to ETL output
- [ ] Test fails immediately on any discrepancy
- [ ] Clear error message showing expected vs actual

**Success Criteria:**
- Test passes with current ETL output (if correct)
- Test fails clearly if goals are wrong
- Test runs as part of `pytest`

### Phase 3: Integrate into Validation Suite

**Description:** Make goal verification part of standard ETL validation.

**Tasks:**
- [ ] Add to `./benchsight.sh etl validate`
- [ ] Add to CI pipeline
- [ ] Block merges if goal counts fail

**Success Criteria:**
- Cannot merge code that breaks goal counting
- Clear CI failure message

---

## Success Criteria

**How do we know this is complete and successful?**

- [ ] Official scores documented for all 4 test games
- [ ] Automated test verifies goal counts
- [ ] Test is part of standard validation
- [ ] Zero tolerance for goal count discrepancies

**Acceptance Tests:**
- Manually introduce goal counting bug → test catches it
- Run ETL → test passes with correct counts

---

## Dependencies

**What needs to exist or be completed first?**

- [ ] Access to official scoresheets for verification
- [ ] ETL must be generating fact_goals table

**Blocking Issues:**
- None

---

## Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Official scores entered incorrectly | High | Low | Double-check against multiple sources |
| Edge cases (OT goals, shootout) | Medium | Medium | Document handling rules clearly |
| Test not catching all issues | High | Low | Test multiple goal-related tables |

---

## Testing Strategy

**How will we test this?**

- [ ] Unit test with known correct data
- [ ] Unit test with intentionally wrong data (should fail)
- [ ] Integration with full ETL run

**Test scenarios:**
- Game with many goals
- Low-scoring game
- Game with OT/shootout (if applicable)

---

## Documentation

**What documentation needs to be updated?**

- [ ] ETL validation docs
- [ ] Goal counting rules in CLAUDE.md (verify current)

---

## Related Documents

- [CLAUDE.md - Goal Counting Rules](../../CLAUDE.md)
- [ETL Validation](../etl/ETL_ARCHITECTURE.md)

---

## Notes

**Important Edge Cases:**

1. **Own Goals** - Still count as a goal for the opposing team
2. **Disallowed Goals** - Should NOT be counted
3. **Shootout Goals** - May have different handling (verify league rules)
4. **Empty Net Goals** - Count normally

**Verification Query:**

```sql
-- Verify goal counts per game
SELECT
    game_id,
    SUM(CASE WHEN is_home THEN 1 ELSE 0 END) as home_goals,
    SUM(CASE WHEN NOT is_home THEN 1 ELSE 0 END) as away_goals
FROM fact_goals
GROUP BY game_id
ORDER BY game_id;
```

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-22 | Initial PRD | Claude |

---

*Status: Approved*
