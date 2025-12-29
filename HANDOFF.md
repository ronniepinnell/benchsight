# BenchSight v6.1 Handoff Document
**Last Updated:** 2024-12-29
**Session:** ETL Fix + Supabase Setup

## What Changed in v6.1

### Critical Bug Fixes
- **TOI Bug Fixed**: Was matching shifts on `player_number` (jersey) instead of `player_id` - all TOI was 0
- **fact_events_player Fixed**: Was re-saving existing file instead of building from tracking data
- **Column Normalization**: Added mapping for raw column names (Type → event_type, etc.)
- **Game 18987 Venue Swap**: Added handling for games where tracking has home/away reversed

### New Files
- `sql/00_drop_all.sql` - Clean DROP script for Supabase reset
- `sql/01_create_tables_generated.sql` - Auto-generated CREATE statements (58 tables)
- `src/supabase_upload_clean.py` - Upload script with hybrid credential handling
- `src/generate_schema.py` - Script to regenerate SQL from CSVs
- `docs/SESSION_LOG.md` - Session tracking
- `docs/BACKLOG.md` - Future tasks

### Configuration
- Credentials: Environment variable OR config/config_local.ini
- Template: config/config_local.ini.template

## Current Status

### Games Processed
| Game | Status | Notes |
|------|--------|-------|
| 18969 | ✅ Complete | Reference game - full validation |
| 18977 | ✅ Complete | Older format |
| 18981 | ✅ Complete | |
| 18987 | ✅ Complete | Venue swap handled |
| 18955 | ❌ Excluded | No tracking file |
| 18965 | ❌ Excluded | Incomplete |
| 18991 | ❌ Excluded | Incomplete |
| 18993 | ❌ Excluded | Incomplete |
| 19032 | ❌ Excluded | Incomplete |

### Data Quality
- **107 player-game rows** with stats
- **98.1% TOI coverage** (105/107 players)
- **46/46 validation tests passed**
- **8 goalie-game rows** with stats

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
