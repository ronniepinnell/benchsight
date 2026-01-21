# BenchSight Master Rules & Standards

**Unified rules, standards, and conventions for the entire project**

Last Updated: 2026-01-15  
Version: 29.0

---

## Overview

This document consolidates all rules, standards, and conventions for BenchSight. It covers coding standards, data rules, naming conventions, git workflow, and testing requirements.

**Source Documents:**
- [CODE_STANDARDS.md](CODE_STANDARDS.md) - Coding standards
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- Critical rules from README.md

---

## Core Principles

### 1. Root-Level Solutions (Not Patchwork)

**Rule:** Fix actual problems, not symptoms.

**❌ BAD:**
- Quick fixes that don't address root cause
- Workarounds that add complexity
- "It works" without understanding why

**✅ GOOD:**
- Fix the actual problem
- Understand the full data flow
- Clean, maintainable code

### 2. Single Source of Truth

**Rule:** One canonical implementation per calculation.

**❌ BAD:**
```python
# Duplicated logic
def count_goals_v1():
    return events[events.event_type == 'Goal']

def count_goals_v2():  # Different logic!
    return events[events.event_detail == 'Goal_Scored']
```

**✅ GOOD:**
```python
# Single source of truth
GOAL_FILTER = (
    (events.event_type == 'Goal') & 
    (events.event_detail == 'Goal_Scored')
)

def count_goals():
    return events[GOAL_FILTER]
```

### 3. Explicit Over Implicit

**Rule:** Named constants, clear types, explicit logic.

**❌ BAD:**
```python
df = df[df.col > 5]  # Magic number, unclear intent
```

**✅ GOOD:**
```python
MIN_GAMES_FOR_STATS = 5
df = df[df.games_played > MIN_GAMES_FOR_STATS]
```

---

## Critical Data Rules

### Goal Counting Rule (CRITICAL)

**Rule:** Goals are ONLY counted when:
```python
event_type == 'Goal' AND event_detail == 'Goal_Scored'
```

**NOT counted:**
- `event_type == 'Shot'` with `event_detail == 'Goal'` (this is a shot attempt, not a goal)
- Other event types

**Implementation:**
```python
# ALWAYS use this filter for goals
GOAL_FILTER = (
    (df['event_type'] == 'Goal') & 
    (df['event_detail'] == 'Goal_Scored')
)

goals = df[GOAL_FILTER]
```

**Location:** `src/calculations/goals.py`

---

### Player Attribution Rules

**Rule:** Consistent player attribution across all events.

**Event Player Roles:**
- `event_player_1`: Primary actor (scorer, shooter, passer, faceoff winner)
- `event_player_2`: Secondary actor (assist, receiver, faceoff loser)
- `event_player_3`: Tertiary actor (second assist, etc.)

**Examples:**
- **Goal:** `event_player_1` = scorer, `event_player_2` = primary assist, `event_player_3` = secondary assist
- **Shot:** `event_player_1` = shooter
- **Pass:** `event_player_1` = passer, `event_player_2` = receiver
- **Faceoff:** `event_player_1` = winner, `event_player_2` = loser

---

### Time Format Rules

**Rule:** Consistent time formats across all tables.

**Period Time:**
- Format: `MM:SS` (e.g., `18:00`, `15:30`, `00:45`)
- Direction: Countdown (18:00 = period start, 00:00 = period end)
- Total Seconds: Elapsed from period start (0 = period start, 1080 = period end for 18-min period)

**Game Time:**
- Format: Total seconds from game start
- Calculation: `(period - 1) * period_length + period_time`

---

## Coding Standards

### Python Standards

**Style:** Follow PEP 8

**Key Rules:**
- Use type hints
- Use docstrings (Google style)
- Maximum line length: 100 characters
- Use meaningful variable names
- Avoid magic numbers

**Example:**
```python
def calculate_corsi_for_player(
    events_df: pd.DataFrame,
    player_id: str,
    team_id: str
) -> Dict[str, int]:
    """
    Calculate Corsi stats for a player.
    
    Args:
        events_df: DataFrame with events
        player_id: Player ID
        team_id: Team ID
    
    Returns:
        Dictionary with CF, CA, CF%
    """
    # Implementation
```

### TypeScript Standards

**Style:** Follow TypeScript best practices

**Key Rules:**
- Use strict mode
- Use interfaces for types
- Use async/await (not promises)
- Use React Server Components by default
- Use Client Components only when needed

**Example:**
```typescript
interface Player {
  id: string
  name: string
  team: string
}

export default async function PlayerPage({ 
  params 
}: { 
  params: { playerId: string } 
}) {
  const player = await getPlayer(params.playerId)
  return <PlayerProfile player={player} />
}
```

---

## Naming Conventions

### Table Names

**Pattern:** `{type}_{entity}_{qualifier}`

**Types:**
- `dim_*` - Dimension tables
- `fact_*` - Fact tables
- `qa_*` - QA tables
- `lookup_*` - Lookup tables
- `v_*` - Views

**Examples:**
- `dim_player` - Player dimension
- `fact_events` - Events fact table
- `fact_player_game_stats` - Player game stats
- `v_leaderboard_points` - Points leaderboard view

### Column Names

**Pattern:** `{entity}_{property}`

**Examples:**
- `player_id` - Player identifier
- `game_id` - Game identifier
- `event_type` - Event type
- `time_start_total_seconds` - Time in total seconds

### Function Names

**Python:**
- `snake_case` for functions
- `create_*` for table creation
- `calculate_*` for calculations
- `get_*` for data retrieval

**TypeScript:**
- `camelCase` for functions
- `get*` for data retrieval
- `use*` for React hooks

---

## Command Conventions

### Unified CLI

**Use `benchsight.sh` for all operations:**

```bash
# ETL
./benchsight.sh etl run
./benchsight.sh etl validate
./benchsight.sh etl status

# Dashboard
./benchsight.sh dashboard dev
./benchsight.sh dashboard build

# API
./benchsight.sh api dev
./benchsight.sh api test

# Database
./benchsight.sh db upload
./benchsight.sh db schema

# Environment
./benchsight.sh env switch dev
./benchsight.sh env status

# Project
./benchsight.sh status
./benchsight.sh docs
./benchsight.sh help
```

**See [COMMANDS.md](COMMANDS.md) for complete command reference.**

---

## Git Workflow

### Branch Strategy

**Main Branches:**
- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches

### Commit Messages

**Format:**
```
[TYPE] Brief description

Detailed explanation (if needed)
```

**Types:**
- `FEAT` - New feature
- `FIX` - Bug fix
- `DOCS` - Documentation
- `REFACTOR` - Code refactoring
- `TEST` - Tests
- `CHORE` - Maintenance

**Examples:**
```
[FEAT] Add player comparison page

- Added comparison component
- Added comparison API endpoint
- Added tests
```

### Pull Request Process

1. Create feature branch
2. Make changes
3. Test changes
4. Update documentation
5. Create pull request
6. Code review
7. Merge to develop
8. Deploy to staging
9. Merge to main

---

## Testing Requirements

### Unit Tests

**Coverage:** Calculation functions must have unit tests

**Location:** `tests/test_*.py`

**Example:**
```python
def test_calculate_cf_pct():
    assert calculate_cf_pct(cf=10, ca=5) == 66.67
    assert calculate_cf_pct(cf=0, ca=0) is None
```

### Integration Tests

**Coverage:** End-to-end ETL execution

**Location:** `tests/test_etl.py`

**Requirements:**
- Test full ETL execution
- Validate table creation
- Validate data quality

### Validation

**Coverage:** All 139 tables

**Location:** `validate.py`

**Requirements:**
- Goal count verification
- Foreign key integrity
- Required column checks

---

## Documentation Standards

### Code Documentation

**Python:**
- Docstrings for all functions
- Type hints for parameters and returns
- Module-level docstrings

**TypeScript:**
- JSDoc comments for functions
- Type definitions for all interfaces
- Component prop documentation

### Documentation Files

**Format:** Markdown

**Structure:**
- Overview section
- Table of contents
- Detailed sections
- Examples
- Related documentation links

---

## Performance Standards

### ETL Performance

**Targets:**
- Full ETL: < 90 seconds for 4 games
- Single game: < 30 seconds
- Table creation: < 5 seconds per table

### Dashboard Performance

**Targets:**
- Page load: < 2 seconds
- Query response: < 500ms
- Chart rendering: < 100ms

### API Performance

**Targets:**
- Endpoint response: < 200ms
- ETL trigger: < 1 second (async)
- Status check: < 50ms

---

## Security Standards

### Authentication

**Current:** None (development)

**Future:**
- API key authentication
- JWT tokens
- Role-based access control

### Data Security

**Rules:**
- No hardcoded credentials
- Use environment variables
- Encrypt sensitive data
- Validate all inputs

---

## Related Documentation

- [CODE_STANDARDS.md](CODE_STANDARDS.md) - Detailed coding standards
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [COMMANDS.md](COMMANDS.md) - Command reference
- [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) - Development workflows
- [PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md) - Pre-flight checklists
- [README.md](../README.md) - Project overview

---

*Last Updated: 2026-01-15*
