# BenchSight View Architecture

## Overview

This document outlines the Supabase view layer that sits between ETL tables and dashboards.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DASHBOARD LAYER                              │
│  (React/HTML pages consuming data via Supabase JS client)           │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         VIEW LAYER (Supabase)                        │
│  v_leaderboard_*, v_rankings_*, v_standings_*, v_summary_*          │
│  - Always fresh (computed on query)                                  │
│  - No storage cost                                                   │
│  - Easy to modify                                                    │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         TABLE LAYER (ETL)                            │
│  fact_player_game_stats, fact_goalie_game_stats, dim_*, etc.        │
│  - Source of truth                                                   │
│  - Validated in ETL                                                  │
│  - Updated on ETL run                                                │
└─────────────────────────────────────────────────────────────────────┘
```

## View Naming Convention

| Prefix | Purpose | Example |
|--------|---------|---------|
| `v_leaderboard_` | Ranked lists for display | v_leaderboard_points |
| `v_rankings_` | Position rankings | v_rankings_goalies |
| `v_standings_` | Team standings | v_standings_current |
| `v_summary_` | Aggregated summaries | v_summary_team_season |
| `v_recent_` | Recent activity | v_recent_games |
| `v_compare_` | Comparison helpers | v_compare_players |
| `v_trend_` | Trends/rolling stats | v_trend_player_form |
| `v_detail_` | Detailed breakdowns | v_detail_player_splits |

## Dashboard Connection Pattern

```javascript
// supabase-client.js
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://your-project.supabase.co',
  'your-anon-key'
)

// Fetch from view (same as table)
const { data, error } = await supabase
  .from('v_leaderboard_points')
  .select('*')
  .limit(10)

// With filters
const { data, error } = await supabase
  .from('v_standings_current')
  .select('*')
  .eq('season_id', 'N20252026F')
```

## Tables That Can Be DROPPED After Views

| Table | Rows | Why Droppable | Replaced By |
|-------|------|---------------|-------------|
| fact_league_leaders_snapshot | 20 | Redundant with view | v_leaderboard_* |
| fact_team_standings_snapshot | 5 | Redundant with view | v_standings_current |
| fact_season_summary | 1 | Simple aggregation | v_summary_season |
| fact_player_career_stats | 63 | Can compute from season | v_summary_player_career |
| fact_team_season_stats | 5 | Duplicate of _basic | v_summary_team_season |

**Keep these ETL tables** (too complex/validated for views):
- fact_player_game_stats (444 cols, micro-level)
- fact_goalie_game_stats (128 cols, micro-level)
- fact_player_season_stats (435 cols, advanced)
- All _basic tables (official data)
- All dimension tables
- All event-level tables

## View Categories

### 1. LEADERBOARD VIEWS
Season leaders for key stats (top N)

### 2. RANKINGS VIEWS  
Full rankings with rank numbers

### 3. STANDINGS VIEWS
Team standings, division views

### 4. SUMMARY VIEWS
Aggregated totals (replace ETL snapshots)

### 5. RECENT VIEWS
Latest games, recent performance

### 6. COMPARISON VIEWS
Side-by-side player/team comparisons

### 7. TREND VIEWS
Rolling averages, form guides

### 8. DETAIL VIEWS
Breakdowns by period, situation, opponent
