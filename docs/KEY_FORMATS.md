# Key Format Reference

**Last Updated:** January 7, 2026  
**Version:** 12.03

## Key Format Standard

All composite keys follow the pattern:
```
{PREFIX}{game_id}{index:05d}
```

- `PREFIX` = 2-letter type identifier
- `game_id` = 5-digit game ID from noradhockey.com
- `index` = 5-digit zero-padded sequential number

Example: `EV1896901234` = Event #1234 in game 18969

## Complete Key Reference

| Prefix | Key Name | Table(s) | Example | Description |
|--------|----------|----------|---------|-------------|
| `EV` | event_id | fact_events, fact_event_players | EV1896901000 | Unique event. One per game event. |
| `SH` | shift_id | fact_shifts, fact_shift_players | SH1896900001 | Unique shift. One per line change. |
| `SQ` | sequence_key | fact_sequences | SQ1896905001 | Possession sequence. |
| `PL` | play_key | fact_plays | PL1896906001 | Offensive/defensive play grouping. |
| `TV` | tracking_event_key | fact_event_players | TV1896901000 | Tracking-level event. |
| `LV` | linked_event_key | fact_linked_events | LV1896909001 | Links causally related events. |
| `ZC` | zone_change_key | fact_zone_entries | ZC1896900001 | Zone transition identifier. |
| `EP` | event_player_key | fact_event_players | EP1896901000_1 | Player-event combination. |
| `CH` | chain_id | fact_event_chains | CH1896900001 | Event chain linking. |
| `SC` | scoring_chance_key | fact_scoring_chances | SC1896900001 | Scoring chance grouping. |

## Dimension Key Formats

| Dimension | Key Column | Format | Examples |
|-----------|------------|--------|----------|
| dim_player | player_id | P_LASTNAME_N | P_SMITH_1, P_JONES_2 |
| dim_team | team_id | Team code | TEAM1, BLAZERS |
| dim_season | season_id | NORAD_YYYY_SS | NORAD_2024_FA |
| dim_period | period_id | P{N} | P1, P2, P3, POT |
| dim_zone | zone_id | Z_{zone} | Z_O, Z_D, Z_N |
| dim_position | position_id | Position code | C, LW, RW, D, G |

## Key Generation Code

Source: `src/core/key_utils.py`

```python
def format_key(prefix: str, game_id, index) -> str:
    """Generate composite key: {prefix}{game_id}{index:05d}"""
    return f"{prefix}{game_id}{int(index):05d}"

# Usage:
event_id = format_key('EV', 18969, 1000)  # → EV1896901000
shift_id = format_key('SH', 18969, 1)     # → SH1896900001

def generate_player_id(last_name: str, suffix: int = 1) -> str:
    """Generate player_id: P_LASTNAME_N"""
    clean = last_name.upper().replace(' ', '_')
    return f"P_{clean}_{suffix}"
```

## Key Lookup Rules

**Player Lookup:** To find player_id from jersey number:
```sql
SELECT player_id FROM fact_gameroster 
WHERE game_id = 18969 AND team = 'HOME' AND jersey_number = 10
```

**Event Grouping:** Multiple rows in `fact_event_players` share the same `event_id`. The `fact_events` table has one row per unique `event_id`.

---

See also: [HTML Version](html/KEY_FORMATS.html)
