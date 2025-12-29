# BenchSight v6.0 Handoff Document

## What Changed in v6.0

### Table Consolidation
- **REMOVED**: `fact_events_tracking`, `fact_events_long`, `fact_shifts_tracking`, `fact_shifts_long`, `fact_boxscore_*`, `fact_h2h_with_linemates`, `fact_line_vs_line`
- **NEW**: 
  - `fact_events` (wide) - One row per event
  - `fact_events_player` (long) - One row per player per event
  - `fact_shifts` (wide) - One row per shift
  - `fact_shifts_player` (long) - One row per player per shift
  - `fact_sequences` - Possession chains across zones
  - `fact_plays` - Single-zone possession segments
  - `fact_player_boxscore_all` - Basic stats from NORAD for ALL games
  - `fact_team_standings_snapshot` - W/L/T record over time
  - `fact_league_leaders_snapshot` - Player rankings over time

### Stats Fixes
- **Goals**: Properly deduplicated by event_index, only counting `event_team_player_1` role
- **Assists**: Captured from `event_team_player_2` (A1) and `event_team_player_3` (A2)
- **TOI**: Fixed venue swap issue for game 18987
- **Goalie Stats**: Now properly tracked from Save events and goals_against from goal events

### New Analytics
- **sequence_id**: Calculated at ETL time (faceoff/stoppage/turnover boundaries)
- **play_id**: Calculated at ETL time (zone entry/exit boundaries)
- **pass_targets**: Count of times player was target of pass (event_player_2)
- **defender_targets**: Count of times player was defending (opp_player_1)
- **possession_time**: Duration of possession events per player

## Table Structure

### Events Tables
| Table | Purpose | Key Columns |
|-------|---------|-------------|
| fact_events | One row per event | game_id, event_index, sequence_id, play_id, event_type, event_detail |
| fact_events_player | One row per player per event | + player_id, player_role, role_number |

### Shifts Tables  
| Table | Purpose | Key Columns |
|-------|---------|-------------|
| fact_shifts | One row per shift | game_id, shift_index, all player slots |
| fact_shifts_player | One row per player per shift | game_id, shift_index, player_id, slot, shift_duration |

### Stats Tables
| Table | Scope | Key Columns |
|-------|-------|-------------|
| fact_player_game_stats | Tracked games | 46 columns - goals, assists, shots, passes, zone, faceoffs, TOI |
| fact_goalie_game_stats | Tracked games | saves, goals_against, sv_pct, gaa |
| fact_team_game_stats | Tracked games | Team totals from player stats |
| fact_player_boxscore_all | ALL games | Basic G/A/PIM from NORAD |

### Analytics Tables
| Table | Purpose |
|-------|---------|
| fact_sequences | Possession chain summaries |
| fact_plays | Single-zone play summaries |
| fact_team_standings_snapshot | Running W/L/T record per game |
| fact_league_leaders_snapshot | Running player rankings per game |

## Validation

Run `python scripts/validate_stats.py` to verify:
- Goals match between events and stats
- TOI coverage > 80%
- Goalie stats present

## Key Domain Knowledge

### Player Roles
- `event_team_player_1`: Primary player (scorer on goals, passer on passes)
- `event_team_player_2`: Secondary player (A1 on goals, target on passes)
- `event_team_player_3`: Tertiary player (A2 on goals)
- `opp_team_player_1`: Primary opponent (goalie on goals, defender)
- `opp_team_player_2+`: Other opponents

### Sequence/Play Rules
- **New sequence**: Faceoff, Stoppage, Giveaway
- **New play**: Zone entry/exit, Turnover, Faceoff, Zone change

### Game 18987 Venue Swap
Raw tracking has home/away swapped compared to roster. ETL auto-detects and fixes.
