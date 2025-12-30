# BenchSight Portal Developer - Session Prompt

Copy and paste this prompt to start your session:

---

I'm the Portal/Admin Developer for BenchSight, a hockey analytics platform. The portal provides admin tools for managing teams, players, schedules, and system operations.

## Project Context

- **Database:** Supabase PostgreSQL (98 tables total)
- **Portal manages:** Dimension tables (CRUD) + system operations
- **Portal reads:** Fact tables (for reports/dashboards)

## Tables I Manage (CRUD Operations)

### Core Master Data
| Table | Rows | Operations | Key Columns |
|-------|------|------------|-------------|
| `dim_player` | 337 | Create, Read, Update, Deactivate | player_id, player_name, jersey_number, position, primary_team_id, is_active |
| `dim_team` | 26 | Create, Read, Update, Deactivate | team_id, team_name, team_abbrev, is_active |
| `dim_schedule` | 562 | Create, Read, Update, Delete | game_id, game_date, game_time, home_team_id, away_team_id, venue_id |
| `dim_venue` | varies | Create, Read, Update | venue_id, venue_name, address |
| `dim_season` | varies | Create, Read, Update | season_id, season_name, start_date, end_date |
| `dim_league` | varies | Create, Read, Update | league_id, league_name |

### Game Roster Management
| Table | Operations | Purpose |
|-------|------------|---------|
| `fact_gameroster` | Create, Read, Update, Delete | Assign players to games |
| `fact_registration` | Create, Read, Update | Player season registrations |
| `fact_draft` | Create, Read, Update | Draft assignments |

### Reference Data (Read-mostly, occasional updates)
| Table | Purpose |
|-------|---------|
| `dim_position` | Player positions (C, LW, RW, D, G) |
| `dim_player_role` | Player roles |
| `dim_event_type` | Event type definitions |
| `dim_event_detail` | Event detail definitions |
| `dim_shot_type` | Shot type definitions |
| `dim_pass_type` | Pass type definitions |
| `dim_zone` | Zone definitions (DZ, NZ, OZ) |
| `dim_strength` | Game strength (EV, PP, PK) |
| + 30 more dimension tables |

### System Status Tables
| Table | Purpose |
|-------|---------|
| `fact_game_status` | Track game processing status |
| `qa_suspicious_stats` | Data quality flags |
| `fact_league_leaders_snapshot` | Leaderboard snapshots |
| `fact_team_standings_snapshot` | Standings snapshots |

## Tables I Read (Reports/Dashboards)

| Table | Purpose |
|-------|---------|
| `fact_player_game_stats` | Player performance (317 columns) |
| `fact_team_game_stats` | Team performance |
| `fact_goalie_game_stats` | Goalie performance |
| `fact_events` | Event counts per game |
| `fact_shifts` | Shift counts per game |
| All 51 fact tables | Various reports |

## Portal Features

1. **Team Management** - Add/edit teams, view rosters
2. **Player Management** - Add/edit players, assign to teams
3. **Schedule Management** - Create games, set matchups
4. **Game Roster** - Assign players to specific games
5. **Standings** - View/edit standings
6. **System Health** - ETL status, data quality, table stats
7. **Reports** - League leaders, team comparisons
8. **Data Export** - Download CSVs

## Key Documentation

- UI wireframes: `docs/WIREFRAMES_AND_PAGES.md`
- Supabase CRUD: `docs/SUPABASE_INTEGRATION_GUIDE.md`
- All 98 tables: `docs/DATA_DICTIONARY.md`
- Current prototype: `portal/`

## Example Queries

```javascript
// Create new player
const { data, error } = await supabase
  .from('dim_player')
  .insert({
    player_name: 'John Smith',
    jersey_number: 17,
    position: 'C',
    primary_team_id: 5,
    is_active: true
  })

// Update team
await supabase
  .from('dim_team')
  .update({ team_name: 'Blue Thunder' })
  .eq('team_id', 5)

// Get all players with team names
const { data } = await supabase
  .from('dim_player')
  .select(`*, dim_team (team_name)`)
  .eq('is_active', true)
  .order('player_name')
```

## My Specific Task Today

[DESCRIBE YOUR TASK]
