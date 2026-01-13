# BenchSight Validation Plan

**Version:** v22.2  
**Updated:** 2026-01-10

---

## Overview

This document defines the field-level validation methodology for all BenchSight tables. Each table is validated for:

1. **Row Count** - Expected vs actual
2. **Column Inventory** - All fields, purpose, data type
3. **Field Logic** - Calculation/derivation correctness
4. **Null Analysis** - Unexpected nulls
5. **Referential Integrity** - FK relationships
6. **Business Rules** - Domain-specific checks
7. **Cross-Table Consistency** - Matching counts

---

## Quick Start

Run automated validation:
```bash
python scripts/validate_tables.py
```

---

## Table Tiers

### Tier 1: Core (Must Be Perfect)
| Table | Priority | Purpose |
|-------|----------|---------|
| dim_player | 1 | Player master |
| dim_team | 1 | Team master |
| dim_schedule | 1 | Game schedule |
| dim_event_type | 1 | Event taxonomy |
| fact_events | 1 | Raw events |
| fact_shifts | 1 | Shift tracking |
| fact_gameroster | 1 | Who played |
| fact_player_game_stats | 1 | Player stats |
| fact_team_game_stats | 1 | Team stats |
| fact_goalie_game_stats | 1 | Goalie stats |

### Tier 2: Important
| Table | Purpose |
|-------|---------|
| dim_event_detail | Event detail taxonomy |
| dim_event_detail_2 | Secondary details |
| dim_play_detail | Play classifications |
| fact_faceoffs | Faceoff results |
| fact_shot_event | Shot tracking |
| fact_penalties | Penalty tracking |
| fact_zone_entries | Zone entry tracking |
| fact_zone_exits | Zone exit tracking |
| fact_player_season_stats | Season aggregates |
| fact_team_season_stats | Team season aggregates |

### Tier 3: Nice to Have
All other tables - validate if time permits.

---

## Field-Level Validation Checklists

### dim_player
| Field | Type | Validation |
|-------|------|------------|
| player_id | PK | Unique, format P+digits |
| player_first_name | text | No nulls |
| player_last_name | text | No nulls |
| player_full_name | text | = first + " " + last |
| player_primary_position | text | In (Forward, Defense, Goalie) |
| current_skill_rating | int | Range 1-10 |

### dim_team
| Field | Type | Validation |
|-------|------|------------|
| team_id | PK | Unique |
| team_name | text | No nulls |
| norad_team | text | Y or N |

### dim_schedule
| Field | Type | Validation |
|-------|------|------------|
| game_id | PK | Unique |
| home_team_id | FK | Exists in dim_team |
| away_team_id | FK | Exists in dim_team, ≠ home_team_id |
| home_total_goals | int | >= 0 |
| away_total_goals | int | >= 0 |
| date | datetime | Valid date |

### fact_events
| Field | Type | Validation |
|-------|------|------------|
| event_id | PK | Unique |
| game_id | FK | Exists in dim_schedule |
| event_type | text | Exists in dim_event_type |
| period | int | In (1, 2, 3, OT) |
| is_goal | bool | True ONLY when event_type='Goal' AND event_detail='Goal_Scored' |

### fact_player_game_stats
| Field | Type | Validation |
|-------|------|------------|
| player_game_key | PK | Unique |
| game_id | FK | Exists in dim_schedule |
| player_id | FK | Exists in dim_player |
| goals | int | >= 0 |
| assists | int | >= 0 |
| points | int | = goals + assists |
| shooting_pct | float | = goals / sog * 100 |
| toi_minutes | float | = toi_seconds / 60 |

### fact_goalie_game_stats
| Field | Type | Validation |
|-------|------|------------|
| goalie_game_key | PK | Unique |
| player_id | FK | Exists in dim_player, position=Goalie |
| saves | int | >= 0 |
| goals_against | int | >= 0 |
| shots_against | int | = saves + goals_against |
| save_pct | float | = saves / shots_against * 100 |

### fact_shifts
| Field | Type | Validation |
|-------|------|------------|
| shift_id | PK | Unique |
| game_id | FK | Exists in dim_schedule |
| period | int | In (1, 2, 3) |
| shift_duration | float | = (start_min*60+start_sec) - (end_min*60+end_sec) [hockey clock] |

---

## Cross-Table Validation Rules

| Rule | Tables | Check |
|------|--------|-------|
| Goal Count | dim_schedule, fact_events, fact_player_game_stats | All must match |
| Player FK | fact_*, dim_player | All player_ids exist |
| Team FK | fact_*, dim_team | All team_ids exist |
| Event Type | fact_events, dim_event_type | All event_type values exist |
| Game Coverage | dim_schedule, fact_events | Tracked games have events |

---

## Known Issues (Current)

| Table | Issue | Severity | Status |
|-------|-------|----------|--------|
| fact_events | Game 18977 missing 1 goal | Medium | Data entry fix needed |
| fact_goalie_game_stats | Both goalies have identical stats | High | ETL bug |
| fact_goalie_game_stats | Non-goalie (P100096) in stats | Medium | Position or logic fix |
| fact_team_game_stats | fo_wins = 0 for all | Low | Investigate tracking |

---

## Validation Execution Order

1. **Dimensions First** (no dependencies)
   ```
   dim_player → dim_team → dim_event_type → dim_schedule
   ```

2. **Core Facts** (depend on dimensions)
   ```
   fact_events → fact_shifts → fact_gameroster
   ```

3. **Derived Facts** (depend on core facts)
   ```
   fact_player_game_stats → fact_team_game_stats → fact_goalie_game_stats
   ```

4. **Aggregates** (depend on game stats)
   ```
   fact_player_season_stats → fact_team_season_stats
   ```

---

## Automated Validation Script

Location: `scripts/validate_tables.py`

Checks:
- [x] dim_player integrity
- [x] dim_team integrity
- [x] dim_schedule integrity
- [x] fact_events goal counting
- [x] fact_player_game_stats calculations
- [x] fact_goalie_game_stats calculations

Output:
```
✅ dim_player: VALID (337 rows)
✅ dim_team: VALID (26 rows)
✅ dim_schedule: VALID (567 rows)
⚠️ fact_events: WARNING (5823 rows)
✅ fact_player_game_stats: VALID (105 rows)
⚠️ fact_goalie_game_stats: WARNING (8 rows)
```

---

## Adding New Validations

```python
def validate_new_table():
    df = pd.read_csv(f'{OUTPUT_DIR}/new_table.csv')
    results = {
        'table': 'new_table',
        'rows': len(df),
        'status': 'VALID',
        'issues': []
    }
    
    # Add checks here
    if some_check_fails:
        results['issues'].append('Description of issue')
        results['status'] = 'WARNING'  # or 'INVALID'
    
    return results
```

---

*Run validation after each ETL, document all findings*
