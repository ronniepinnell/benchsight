---
name: hockey-stats
description: Consult the hockey analytics SME for stat calculations, advanced metrics methodology, or data visualization decisions. Use before implementing any hockey statistics.
---

# Hockey Analytics Expert Consultation

Get expert guidance on hockey statistics and analytics methodology.

## When to Use

- Implementing new stat calculations
- Questions about Corsi, Fenwick, xG, etc.
- Understanding micro-stats (play_detail columns)
- Comparing against industry standards (NHL Edge, MoneyPuck)
- Designing ML models for hockey
- Data visualization decisions for dashboards

## Critical Project Rules

### Goal Counting
```python
# ONLY this combination:
event_type == 'Goal' AND event_detail == 'Goal_Scored'
# NEVER: event_type == 'Shot' with event_detail == 'Goal'
```

### Faceoffs
- `event_player_1` (player_role) = faceoff WINNER
- `opp_player_1` = faceoff LOSER

### Assists
- `AssistPrimary` in play_details1/2 = primary assist (counts)
- `AssistSecondary` in play_details1/2 = secondary assist (counts)
- `AssistTertiary` = does NOT count as assist

### Micro-Stats
- Found in `play_detail1` and `play_detail2` columns
- In linked events, count ONCE per `linked_event_key`

## Task

$ARGUMENTS

Provide methodology guidance that:
1. Aligns with industry standards
2. Respects BenchSight project rules
3. References canonical calculations in `src/calculations/`
4. Documents decisions in `docs/reference/` if significant
