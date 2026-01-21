# Testing Rules

**Testing patterns and requirements**

Last Updated: 2026-01-15

---

## Testing Requirements

### Unit Tests

**Required for:**
- Calculation functions
- Utility functions
- Data transformations

**Location:** `tests/test_*.py`

### Integration Tests

**Required for:**
- ETL execution
- API endpoints
- End-to-end flows

---

## Test Patterns

### Unit Test Pattern

```python
import pytest
from src.calculations.goals import count_goals

def test_count_goals():
    """Test goal counting."""
    events = pd.DataFrame({
        'event_type': ['Goal', 'Shot', 'Goal'],
        'event_detail': ['Goal_Scored', 'Shot_On_Goal', 'Goal_Scored']
    })
    
    result = count_goals(events)
    assert result == 2
```

### Integration Test Pattern

```python
def test_etl_execution():
    """Test ETL execution."""
    result = run_etl(['game1', 'game2'])
    assert result['status'] == 'success'
    assert result['tables_created'] > 0
```

---

## Test Organization

### Test Structure

```
tests/
├── test_calculations.py
├── test_tables.py
├── test_etl.py
└── test_integration.py
```

---

## Related Rules

- `core.md` - Core rules (testing requirements)
- `etl.md` - ETL testing patterns
- `api.md` - API testing patterns

---

*Last Updated: 2026-01-15*
