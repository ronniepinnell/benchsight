---
name: schema-design
description: Design and document database schemas for BenchSight tables, relationships, and data models. Use when adding new tables or modifying existing schema.
allowed-tools: Read, Write, Bash
argument-hint: [table|relationship|migration]
---

# Schema Design

Design database schemas for BenchSight.

## Naming Conventions

| Type | Prefix | Example |
|------|--------|---------|
| Dimension | `dim_` | dim_players, dim_teams |
| Fact | `fact_` | fact_player_game, fact_shots |
| QA | `qa_` | qa_validation_summary |
| View | `v_` | v_player_stats_summary |
| Staging | `stg_` | stg_tracking_raw |

## Key Formatting

Format: `{XX}{ID}{5D}`

- No underscores in keys (except multi-entity)
- Zero-padded IDs
- Examples:
  - `PL00123` (player)
  - `GM00456` (game)
  - `TM00007` (team)
  - `PG_00123_00456` (player-game combination)

## Core Tables (139 total)

### Dimensions (50)
```sql
-- dim_players
CREATE TABLE dim_players (
    player_key VARCHAR(10) PRIMARY KEY,  -- PL{5D}
    player_id INTEGER NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    position VARCHAR(10),
    shoots VARCHAR(1),
    team_key VARCHAR(10) REFERENCES dim_teams(team_key),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- dim_teams
CREATE TABLE dim_teams (
    team_key VARCHAR(10) PRIMARY KEY,  -- TM{5D}
    team_id INTEGER NOT NULL,
    team_name VARCHAR(100),
    abbreviation VARCHAR(5),
    league_id UUID REFERENCES dim_leagues(league_id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- dim_games
CREATE TABLE dim_games (
    game_key VARCHAR(10) PRIMARY KEY,  -- GM{5D}
    game_id INTEGER NOT NULL,
    game_date DATE,
    home_team_key VARCHAR(10) REFERENCES dim_teams(team_key),
    away_team_key VARCHAR(10) REFERENCES dim_teams(team_key),
    season_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Facts (81)
```sql
-- fact_player_game
CREATE TABLE fact_player_game (
    player_game_key VARCHAR(20) PRIMARY KEY,  -- PG_{player_id}_{game_id}
    player_key VARCHAR(10) REFERENCES dim_players(player_key),
    game_key VARCHAR(10) REFERENCES dim_games(game_key),
    team_key VARCHAR(10) REFERENCES dim_teams(team_key),
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    shots INTEGER DEFAULT 0,
    toi_seconds INTEGER DEFAULT 0,
    -- ... many more columns
    created_at TIMESTAMP DEFAULT NOW()
);

-- fact_shots
CREATE TABLE fact_shots (
    shot_key VARCHAR(20) PRIMARY KEY,
    game_key VARCHAR(10) REFERENCES dim_games(game_key),
    shooter_key VARCHAR(10) REFERENCES dim_players(player_key),
    goalie_key VARCHAR(10) REFERENCES dim_players(player_key),
    period INTEGER,
    time_seconds INTEGER,
    x_coord DECIMAL(5,2),
    y_coord DECIMAL(5,2),
    shot_type VARCHAR(20),
    result VARCHAR(20),  -- Goal, Save, Miss, Block
    xg DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### QA Tables (8)
```sql
-- qa_validation_summary
CREATE TABLE qa_validation_summary (
    validation_key VARCHAR(20) PRIMARY KEY,
    run_timestamp TIMESTAMP,
    table_name VARCHAR(100),
    check_name VARCHAR(100),
    status VARCHAR(20),  -- PASS, FAIL, WARNING
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Relationships

```
dim_players ─┬─< fact_player_game >─┬─ dim_games
             │                       │
             └───< fact_shots >──────┘
                        │
                        └─── dim_teams
```

## Indexes

```sql
-- Performance indexes
CREATE INDEX idx_player_game_player ON fact_player_game(player_key);
CREATE INDEX idx_player_game_game ON fact_player_game(game_key);
CREATE INDEX idx_shots_game ON fact_shots(game_key);
CREATE INDEX idx_shots_coords ON fact_shots(x_coord, y_coord);
```

## Migration Template

```sql
-- migrations/YYYYMMDD_description.sql

-- Up
ALTER TABLE fact_player_game ADD COLUMN expected_goals DECIMAL(4,3);

-- Down (in separate file or comment)
-- ALTER TABLE fact_player_game DROP COLUMN expected_goals;
```

## Output

Schema documentation goes to:
```
docs/data/schema/{table_name}.md
```
