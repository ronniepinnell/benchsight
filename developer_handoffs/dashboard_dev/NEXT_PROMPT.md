# BenchSight Dashboard Developer - Session Prompt

Copy and paste this prompt to start your session:

---

I'm the Dashboard Developer for BenchSight, a hockey analytics platform. The dashboard displays stats from Supabase (read-only).

## Project Context

- **Database:** Supabase PostgreSQL (98 tables total)
- **Dashboard reads from:** 40+ tables
- **Player stats:** 317 columns per player per game
- **Display:** React web app

## Primary Tables to Query

### Player Stats
| Table | Rows | Key Columns |
|-------|------|-------------|
| `fact_player_game_stats` | 107 | **317 columns** - goals, assists, points, shots, sog, toi_seconds, cf_pct, ff_pct, xg_for, etc. |
| `fact_player_period_stats` | ~300 | Per-period breakdown |
| `fact_player_micro_stats` | ~100 | Dekes, screens, backchecks, forechecks, poke_checks |
| `fact_goalie_game_stats` | ~20 | saves, goals_against, save_pct, saves_glove, saves_blocker |

### Team Stats
| Table | Rows | Key Columns |
|-------|------|-------------|
| `fact_team_game_stats` | 18 | goals, shots, sog, fo_pct, shooting_pct, hits, blocks |
| `fact_team_standings_snapshot` | varies | wins, losses, ties, points, position |

### Game Data
| Table | Rows | Key Columns |
|-------|------|-------------|
| `fact_events` | 5,833 | event_type, event_detail, period, game_time, event_player_1 |
| `fact_shifts` | 672 | player_id, period, start_time, end_time, duration |
| `fact_plays` | 2,714 | play sequences |

### Advanced Analytics
| Table | Description |
|-------|-------------|
| `fact_h2h` | Head-to-head when two players on ice together |
| `fact_wowy` | With-or-without-you for linemates |
| `fact_head_to_head` | Matchup summary |
| `fact_line_combos` | Line combination stats |
| `fact_player_pair_stats` | Pair performance |
| `fact_shift_quality` | Shift quality metrics |

### Zone Analytics
| Table | Description |
|-------|-------------|
| `fact_scoring_chances` | Scoring chance tracking |
| `fact_shot_danger` | Shot danger zones |
| `fact_possession_time` | Zone possession |
| `fact_cycle_events` | Cycle plays |
| `fact_rush_events` | Rush plays |

### XY Visualizations
| Table | Description |
|-------|-------------|
| `fact_shot_xy` | Shot locations for shot maps |
| `fact_player_xy_long` | Player positions |
| `fact_puck_xy_long` | Puck tracking |

### Video Highlights (NEW)
| Table | Description |
|-------|-------------|
| `fact_video_highlights` | Video clip metadata |
| `dim_highlight_type` | Highlight categories |

## Dimension Tables (Lookups)

| Table | Rows | Purpose |
|-------|------|---------|
| `dim_player` | 337 | Player names, positions, jersey numbers |
| `dim_team` | 26 | Team names, abbreviations |
| `dim_schedule` | 562 | Game dates, scores, matchups |
| `dim_season` | varies | Season info |
| `dim_event_type` | ~20 | Event type labels |
| `dim_position` | 5 | C, LW, RW, D, G |
| `dim_zone` | 3 | DZ, NZ, OZ |

## Dashboard Pages (from wireframes)

1. **Home/Landing** - Recent games, stats snapshot, leaders, highlights
2. **Player Profile** - Season stats, game log, shot map, trends
3. **Game Box Score** - Scoring summary, player stats, team totals
4. **Team Page** - Roster, standings, line combos
5. **Leaderboards** - Points, goals, assists, advanced stats

## Key Documentation

- UI wireframes: `docs/WIREFRAMES_AND_PAGES.md`
- Supabase queries: `docs/SUPABASE_INTEGRATION_GUIDE.md`
- All 317 stats explained: `docs/STATS_REFERENCE_COMPLETE.md`
- All 98 tables: `docs/DATA_DICTIONARY.md`
- Current prototype: `dashboard/dashboard.html`

## Example Queries

```javascript
// Get player game stats with names
const { data } = await supabase
  .from('fact_player_game_stats')
  .select(`
    *,
    dim_player (player_name, position, jersey_number),
    dim_team (team_name, team_abbrev)
  `)
  .eq('game_id', 18969)
  .order('points', { ascending: false })

// Get league leaders
const { data } = await supabase
  .from('fact_player_game_stats')
  .select('player_id, goals, assists, points')
  .order('points', { ascending: false })
  .limit(20)
```

## My Specific Task Today

[DESCRIBE YOUR TASK]
