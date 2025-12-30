# BenchSight Complete Schema & Analytics Guide

**Version:** 2.0  
**Date:** December 30, 2025  
**Tables:** 96  
**Total Columns:** ~1,900

---

## Table of Contents

1. [Complete Table Inventory (96 Tables)](#complete-table-inventory)
2. [Entity Relationship Diagram](#entity-relationship-diagram)
3. [Key Relationships](#key-relationships)
4. [WOWY Analysis (With Or Without You)](#wowy-analysis)
5. [H2H Analysis (Head to Head)](#h2h-analysis)
6. [Player Comparisons](#player-comparisons)
7. [Line Combinations](#line-combinations)
8. [Query Examples](#query-examples)

---

## Complete Table Inventory

### Dimension Tables (44 tables)

| Table | Columns | Rows | Description |
|-------|---------|------|-------------|
| dim_player | 28 | 337 | Player master data (name, position, rating, etc.) |
| dim_team | 15 | 26 | Team master data |
| dim_schedule | 44 | 562 | Game schedule with scores, video links |
| dim_season | 9 | 9 | Season definitions |
| dim_event_type | 3 | 20 | Event types (Shot, Pass, Goal, etc.) |
| dim_event_detail | 3 | 59 | Event details (Wrist Shot, Slap Shot, etc.) |
| dim_event_detail_2 | 6 | 97 | Secondary event details |
| dim_play_detail | 6 | 154 | Play context (Rush, Cycle, etc.) |
| dim_play_detail_2 | 5 | 62 | Secondary play details (2-on-1, etc.) |
| dim_zone | 4 | 3 | Zones (OZ, NZ, DZ) |
| dim_period | 7 | 5 | Periods (P1, P2, P3, OT, SO) |
| dim_situation | 3 | 5 | Situations (EV, PP, PK, etc.) |
| dim_strength | 7 | 18 | Strength states (5v5, 5v4, etc.) |
| dim_success | 4 | 1 | Success outcomes (s/u) |
| dim_venue | 4 | 2 | Home/Away |
| dim_position | 4 | 7 | Player positions |
| dim_player_role | 6 | 14 | Roles in events (Shooter, Passer, etc.) |
| dim_shot_type | 10 | 14 | Shot types |
| dim_pass_type | 8 | 16 | Pass types |
| dim_turnover_type | 9 | 21 | Turnover types |
| dim_turnover_quality | 5 | 3 | Turnover quality ratings |
| dim_takeaway_type | 8 | 10 | Takeaway types |
| dim_giveaway_type | 8 | 12 | Giveaway types |
| dim_zone_entry_type | 9 | 11 | Zone entry types |
| dim_zone_exit_type | 8 | 10 | Zone exit types |
| dim_stoppage_type | 5 | 10 | Stoppage types |
| dim_shift_start_type | 7 | 9 | Shift start types |
| dim_shift_stop_type | 9 | 27 | Shift stop types |
| dim_shift_slot | 3 | 7 | Shift slots |
| dim_net_location | 5 | 10 | Net locations for shots |
| dim_danger_zone | 5 | 4 | Shot danger zones |
| dim_rink_coord | 7 | 19 | Rink coordinates |
| dim_rinkboxcoord | 12 | 50 | Rink box coordinates |
| dim_rinkcoordzones | 14 | 198 | Coordinate zone mappings |
| dim_stat | 12 | 83 | Stat definitions |
| dim_stat_type | 6 | 57 | Stat type categories |
| dim_stat_category | 4 | 13 | Stat categories |
| dim_micro_stat | 4 | 22 | Micro stat definitions |
| dim_comparison_type | 5 | 6 | Comparison types |
| dim_composite_rating | 6 | 8 | Composite rating definitions |
| dim_league | 2 | 2 | League info |
| dim_terminology_mapping | 4 | 84 | Term mappings |
| dim_playerurlref | 3 | 548 | Player URL references |
| dim_randomnames | 5 | 486 | Random name generator |

### Fact Tables (51 tables)

| Table | Columns | Rows | Description |
|-------|---------|------|-------------|
| **Core Events & Shifts** ||||
| fact_events | 54 | 5,833 | All game events |
| fact_events_player | 63 | 11,635 | Player involvement in events |
| fact_events_long | 32 | 11,136 | Events in long format |
| fact_events_tracking | 46 | 11,918 | Event tracking details |
| fact_linked_events | 48 | 473 | Linked event chains |
| fact_shifts | 63 | 672 | All shifts |
| fact_shifts_player | 35 | 4,626 | Players on shifts |
| fact_shifts_long | 28 | 4,336 | Shifts in long format |
| fact_shifts_tracking | 58 | 476 | Shift tracking details |
| fact_shift_players | 9 | 5,513 | Shift-player junction |
| fact_shift_quality | 13 | 4,626 | Shift quality metrics |
| fact_shift_quality_logical | 10 | 105 | Logical shift quality |
| **Player Stats** ||||
| fact_player_game_stats | 317 | 107 | Comprehensive per-game stats |
| fact_player_boxscore_all | 23 | 14,473 | All player boxscores |
| fact_player_stats_long | 6 | 7,026 | Stats in long format |
| fact_player_period_stats | 10 | 321 | Per-period stats |
| fact_player_micro_stats | 6 | 212 | Micro-level stats |
| fact_player_game_position | 10 | 105 | Position by game |
| fact_player_event_chains | 22 | 5,831 | Player event chains |
| fact_playergames | 25 | 3,010 | Player-game records |
| **Team Stats** ||||
| fact_team_game_stats | 52 | 8 | Per-game team stats |
| fact_team_standings_snapshot | 14 | 1,124 | Standings over time |
| fact_team_zone_time | 18 | 8 | Zone time by team |
| **Analytics** ||||
| fact_h2h | 24 | 684 | Head-to-head matchups |
| fact_head_to_head | 16 | 572 | Alternative H2H format |
| fact_wowy | 28 | 641 | With/Without You analysis |
| fact_matchup_summary | 29 | 684 | Matchup summaries |
| fact_player_pair_stats | 12 | 475 | Player pair statistics |
| fact_line_combos | 40 | 332 | Line combination stats |
| **Sequences & Plays** ||||
| fact_sequences | 28 | 1,088 | Possession sequences |
| fact_plays | 25 | 2,714 | Individual plays |
| fact_event_chains | 15 | 295 | Event chain analysis |
| **Scoring & Shots** ||||
| fact_scoring_chances | 14 | 451 | Scoring chance quality |
| fact_shot_danger | 10 | 435 | Shot danger ratings |
| fact_shot_xy | 31 | 0 | Shot coordinates (empty) |
| fact_rush_events | 12 | 199 | Rush events |
| fact_cycle_events | 7 | 9 | Cycle events |
| **Goalie Stats** ||||
| fact_goalie_game_stats | 19 | 8 | Goalie stats per game |
| **Position Tracking** ||||
| fact_player_xy_long | 16 | 0 | Player positions (CV data) |
| fact_player_xy_wide | 50 | 0 | Player positions wide |
| fact_puck_xy_long | 12 | 0 | Puck positions (CV data) |
| fact_puck_xy_wide | 55 | 0 | Puck positions wide |
| **Other** ||||
| fact_gameroster | 29 | 14,471 | Game rosters |
| fact_game_status | 24 | 562 | Game status tracking |
| fact_possession_time | 14 | 107 | Possession time stats |
| fact_video | 15 | 10 | Video metadata |
| fact_draft | 15 | 160 | Draft data |
| fact_registration | 19 | 190 | Player registration |
| fact_leadership | 9 | 28 | Leadership stats |
| fact_league_leaders_snapshot | 13 | 14,473 | League leader snapshots |
| fact_suspicious_stats | 14 | 18 | Flagged suspicious stats |

### QA Tables (1 table)

| Table | Columns | Rows | Description |
|-------|---------|------|-------------|
| qa_suspicious_stats | 11 | 22 | Data quality flags |

---

## Entity Relationship Diagram

### Core Schema (Star Schema)

```
                              ┌─────────────────────┐
                              │     dim_player      │
                              │─────────────────────│
                              │ player_id (PK)      │
                              │ player_full_name    │
                              │ player_position     │
                              │ current_skill_rating│
                              └──────────┬──────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         │                               │                               │
         ▼                               ▼                               ▼
┌─────────────────┐            ┌─────────────────┐            ┌─────────────────┐
│ fact_events_    │            │ fact_player_    │            │ fact_shifts_    │
│ player          │            │ game_stats      │            │ player          │
│─────────────────│            │─────────────────│            │─────────────────│
│ event_player_key│            │ player_game_key │            │ shift_player_key│
│ event_key (FK)  │            │ game_id (FK)    │            │ shift_key (FK)  │
│ player_id (FK)  │            │ player_id (FK)  │            │ player_id (FK)  │
│ role_abrev      │            │ goals, assists  │            │ toi, plus_minus │
└────────┬────────┘            │ shots, hits...  │            └────────┬────────┘
         │                     └─────────────────┘                     │
         │                                                             │
         ▼                                                             ▼
┌─────────────────┐                                          ┌─────────────────┐
│  fact_events    │                                          │  fact_shifts    │
│─────────────────│                                          │─────────────────│
│ event_key (PK)  │◄─────────────────────────────────────────│ shift_key (PK)  │
│ game_id (FK)    │          shift_key (FK)                  │ game_id (FK)    │
│ shift_key (FK)  │─────────────────────────────────────────►│ period          │
│ period          │                                          │ shift_duration  │
│ event_type      │                                          │ strength        │
│ event_detail    │                                          │ situation       │
│ running_video_  │                                          │ running_video_  │
│ time            │                                          │ time            │
└────────┬────────┘                                          └────────┬────────┘
         │                                                            │
         │                     ┌─────────────────┐                    │
         │                     │  dim_schedule   │                    │
         └─────────────────────┤─────────────────├────────────────────┘
                               │ game_id (PK)    │
                               │ date            │
                               │ home_team_id(FK)│
                               │ away_team_id(FK)│
                               │ home_total_goals│
                               │ away_total_goals│
                               │ video_url       │
                               └────────┬────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
           ┌─────────────────┐                     ┌─────────────────┐
           │    dim_team     │                     │   dim_season    │
           │─────────────────│                     │─────────────────│
           │ team_id (PK)    │                     │ season_id (PK)  │
           │ team_name       │                     │ season_name     │
           │ team_color1     │                     │ start_date      │
           │ team_logo       │                     │ end_date        │
           └─────────────────┘                     └─────────────────┘
```

### Analytics Tables Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ANALYTICS LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │    fact_wowy    │     │    fact_h2h     │     │fact_line_combos │       │
│  │─────────────────│     │─────────────────│     │─────────────────│       │
│  │ wowy_key (PK)   │     │ h2h_key (PK)    │     │line_combo_key   │       │
│  │ game_id (FK)    │     │ game_id (FK)    │     │ game_id (FK)    │       │
│  │ player_1_id (FK)│     │ player_1_id (FK)│     │ venue           │       │
│  │ player_2_id (FK)│     │ player_2_id (FK)│     │ forward_combo   │       │
│  │ venue           │     │ shifts_together │     │ defense_combo   │       │
│  │ shifts_together │     │ toi_together    │     │ shifts          │       │
│  │ toi_together    │     │ goals_for       │     │ toi_together    │       │
│  │ toi_apart       │     │ goals_against   │     │ goals_for       │       │
│  │ cf_pct_together │     │ cf_pct          │     │ cf_pct          │       │
│  │ cf_pct_apart    │     │ xgf, xga        │     │ xgf, xga        │       │
│  │ cf_pct_delta    │     └─────────────────┘     │ synergy metrics │       │
│  │ relative_corsi  │                             └─────────────────┘       │
│  └─────────────────┘                                                        │
│           │                       │                        │                │
│           └───────────────────────┴────────────────────────┘                │
│                                   │                                         │
│                                   ▼                                         │
│                          ┌─────────────────┐                                │
│                          │ fact_matchup_   │                                │
│                          │ summary         │                                │
│                          │─────────────────│                                │
│                          │ Combined H2H +  │                                │
│                          │ WOWY metrics    │                                │
│                          │ synergy_score   │                                │
│                          └─────────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Relationships

### Primary Keys

| Table | Primary Key | Format | Example |
|-------|-------------|--------|---------|
| dim_player | player_id | P + 6 digits | P100023 |
| dim_team | team_id | N + 5 digits | N10008 |
| dim_schedule | game_id | 5 digits | 18969 |
| fact_events | event_key | EV + game_id + 5-digit index | EV1896900001 |
| fact_shifts | shift_key | game_id + _ + index | 18969_1 |
| fact_events_player | event_player_key | event_key + _ + index | EV1896900001_1 |
| fact_shifts_player | shift_player_key | shift_key + _ + player_id | 18969_1_P100023 |
| fact_player_game_stats | player_game_key | game_id + _ + player_id | 18969_P100023 |
| fact_h2h | h2h_key | HH + game_id + 5-digit index | HH1896900001 |
| fact_wowy | wowy_key | WY + game_id + 5-digit index | WY1896900001 |
| fact_line_combos | line_combo_key | LC + game_id + 5-digit index | LC1896900001 |

### Foreign Key Chains

```
dim_player.player_id
    ├── fact_events_player.player_id
    ├── fact_shifts_player.player_id
    ├── fact_player_game_stats.player_id
    ├── fact_h2h.player_1_id
    ├── fact_h2h.player_2_id
    ├── fact_wowy.player_1_id
    └── fact_wowy.player_2_id

dim_schedule.game_id
    ├── fact_events.game_id
    ├── fact_shifts.game_id
    ├── fact_player_game_stats.game_id
    ├── fact_team_game_stats.game_id
    ├── fact_h2h.game_id
    ├── fact_wowy.game_id
    └── fact_line_combos.game_id

fact_shifts.shift_key
    └── fact_events.shift_key

fact_events.event_key
    └── fact_events_player.event_key
```

---

## WOWY Analysis (With Or Without You)

### What is WOWY?

WOWY measures how a player performs **with** a specific teammate versus **without** them. It answers: "Does Player A play better or worse when Player B is on the ice?"

### Table: `fact_wowy`

| Column | Type | Description |
|--------|------|-------------|
| wowy_key | TEXT PK | Unique identifier |
| game_id | TEXT FK | Game reference |
| player_1_id | TEXT FK | The player being analyzed |
| player_2_id | TEXT FK | The teammate being compared |
| venue | TEXT | home/away |
| shifts_together | INT | Number of shifts together |
| p1_shifts_without_p2 | INT | Player 1's shifts without Player 2 |
| p2_shifts_without_p1 | INT | Player 2's shifts without Player 1 |
| toi_together | DECIMAL | Time on ice together (seconds) |
| toi_apart | DECIMAL | Time on ice apart (seconds) |
| **cf_pct_together** | DECIMAL | Corsi For % when together |
| **cf_pct_apart** | DECIMAL | Corsi For % when apart |
| **cf_pct_delta** | DECIMAL | Difference (together - apart) |
| gf_pct_together | DECIMAL | Goals For % when together |
| gf_pct_apart | DECIMAL | Goals For % when apart |
| gf_pct_delta | DECIMAL | Difference |
| xgf_pct_together | DECIMAL | Expected Goals For % together |
| xgf_pct_apart | DECIMAL | Expected Goals For % apart |
| xgf_pct_delta | DECIMAL | Difference |
| relative_corsi | DECIMAL | Relative Corsi impact |
| player_1_name | TEXT | Player 1 display name |
| player_2_name | TEXT | Player 2 display name |

### How WOWY Works

```
                    Player A's Ice Time
    ┌──────────────────────────────────────────────────┐
    │                                                  │
    │   ┌─────────────────┐    ┌─────────────────┐    │
    │   │   WITH          │    │   WITHOUT       │    │
    │   │   Player B      │    │   Player B      │    │
    │   │                 │    │                 │    │
    │   │  CF% = 55%      │    │  CF% = 48%      │    │
    │   │  (together)     │    │  (apart)        │    │
    │   │                 │    │                 │    │
    │   └─────────────────┘    └─────────────────┘    │
    │                                                  │
    │   DELTA = 55% - 48% = +7%                       │
    │   Player A is BETTER with Player B              │
    └──────────────────────────────────────────────────┘
```

### Interpreting WOWY

| cf_pct_delta | Interpretation |
|--------------|----------------|
| > +5% | Strong positive synergy |
| +2% to +5% | Good chemistry |
| -2% to +2% | Neutral |
| -5% to -2% | Poor chemistry |
| < -5% | Strong negative synergy |

### WOWY Query Examples

```sql
-- Find Player A's best linemates
SELECT 
    player_2_name,
    shifts_together,
    toi_together / 60 as minutes_together,
    cf_pct_together,
    cf_pct_apart,
    cf_pct_delta
FROM fact_wowy
WHERE player_1_id = 'P100023'
  AND shifts_together >= 3  -- Minimum sample size
ORDER BY cf_pct_delta DESC
LIMIT 10;

-- Find which teammates hurt a player's performance
SELECT 
    player_2_name,
    cf_pct_delta,
    gf_pct_delta
FROM fact_wowy
WHERE player_1_id = 'P100023'
  AND cf_pct_delta < -5
ORDER BY cf_pct_delta ASC;

-- Best teammate combinations on a team
SELECT 
    player_1_name,
    player_2_name,
    cf_pct_delta,
    toi_together / 60 as minutes
FROM fact_wowy
WHERE game_id = '18969'
  AND venue = 'home'
  AND cf_pct_delta > 0
ORDER BY cf_pct_delta DESC
LIMIT 20;
```

### JavaScript Query (Supabase)

```javascript
// Get WOWY data for a player
async function getPlayerWOWY(gameId, playerId) {
    const { data } = await supabase
        .from('fact_wowy')
        .select(`
            player_2_id,
            player_2_name,
            shifts_together,
            toi_together,
            cf_pct_together,
            cf_pct_apart,
            cf_pct_delta,
            gf_pct_delta
        `)
        .eq('game_id', gameId)
        .eq('player_1_id', playerId)
        .gte('shifts_together', 3)
        .order('cf_pct_delta', { ascending: false });
    
    return data;
}
```

---

## H2H Analysis (Head to Head)

### What is H2H?

H2H measures how a player performs **against** a specific opponent. It answers: "How does Player A do when facing Player B?"

### Table: `fact_h2h`

| Column | Type | Description |
|--------|------|-------------|
| h2h_key | TEXT PK | Unique identifier |
| game_id | TEXT FK | Game reference |
| player_1_id | TEXT FK | The player being analyzed |
| player_2_id | TEXT FK | The opponent faced |
| shifts_together | INT | Shifts facing each other |
| toi_together | DECIMAL | Time on ice against (seconds) |
| **goals_for** | DECIMAL | Goals scored while facing opponent |
| **goals_against** | DECIMAL | Goals allowed while facing opponent |
| **plus_minus** | DECIMAL | Net goals (for - against) |
| **corsi_for** | DECIMAL | Shot attempts for |
| **corsi_against** | DECIMAL | Shot attempts against |
| **cf_pct** | DECIMAL | Corsi For % against opponent |
| fenwick_for | DECIMAL | Unblocked shot attempts for |
| fenwick_against | DECIMAL | Unblocked shot attempts against |
| ff_pct | DECIMAL | Fenwick For % |
| xgf | DECIMAL | Expected goals for |
| xga | DECIMAL | Expected goals against |
| xg_diff | DECIMAL | xGF - xGA |
| shots_for | DECIMAL | Shots on goal for |
| shots_against | DECIMAL | Shots on goal against |
| player_1_name | TEXT | Player 1 display name |
| player_2_name | TEXT | Opponent display name |

### How H2H Works

```
              When Player A faces Player B
    ┌──────────────────────────────────────────────────┐
    │                                                  │
    │  Player A's Team          Player B's Team       │
    │       │                         │               │
    │       ▼                         ▼               │
    │   ┌───────┐                 ┌───────┐          │
    │   │ FOR   │                 │AGAINST│          │
    │   │       │                 │       │          │
    │   │ 2.9   │  Shot Attempts  │ 3.2   │          │
    │   │ Corsi │ ◄────────────── │ Corsi │          │
    │   │       │                 │       │          │
    │   └───────┘                 └───────┘          │
    │                                                  │
    │   CF% = 2.9 / (2.9 + 3.2) = 47.5%               │
    │   Player A is slightly outplayed by Player B    │
    └──────────────────────────────────────────────────┘
```

### Interpreting H2H

| CF% | Interpretation |
|-----|----------------|
| > 55% | Dominating the matchup |
| 50-55% | Winning the matchup |
| 45-50% | Losing the matchup |
| < 45% | Being dominated |

### H2H Query Examples

```sql
-- How does Player A do against each opponent?
SELECT 
    player_2_name as opponent,
    shifts_together,
    toi_together / 60 as minutes_against,
    cf_pct,
    plus_minus,
    xg_diff
FROM fact_h2h
WHERE player_1_id = 'P100022'
  AND game_id = '18969'
ORDER BY cf_pct DESC;

-- Find tough matchups (opponents who dominate a player)
SELECT 
    player_2_name as opponent,
    cf_pct,
    goals_against,
    xga
FROM fact_h2h
WHERE player_1_id = 'P100022'
  AND cf_pct < 45
ORDER BY cf_pct ASC;

-- Find favorable matchups
SELECT 
    player_2_name as opponent,
    cf_pct,
    goals_for,
    xgf
FROM fact_h2h
WHERE player_1_id = 'P100022'
  AND cf_pct > 55
ORDER BY cf_pct DESC;
```

### JavaScript Query (Supabase)

```javascript
// Get H2H matchups for a player
async function getPlayerH2H(gameId, playerId) {
    const { data } = await supabase
        .from('fact_h2h')
        .select(`
            player_2_id,
            player_2_name,
            shifts_together,
            toi_together,
            goals_for,
            goals_against,
            cf_pct,
            xgf,
            xga
        `)
        .eq('game_id', gameId)
        .eq('player_1_id', playerId)
        .order('toi_together', { ascending: false });
    
    return data;
}
```

---

## Player Comparisons

### Table: `fact_player_pair_stats`

For comparing any two players' overall stats:

| Column | Type | Description |
|--------|------|-------------|
| game_id | TEXT FK | Game reference |
| player_1_id | TEXT FK | First player |
| player_1_name | TEXT | First player name |
| player_1_rating | DECIMAL | Skill rating |
| player_2_id | TEXT FK | Second player |
| player_2_name | TEXT | Second player name |
| player_2_rating | DECIMAL | Skill rating |
| shifts_together | INT | Times on ice together |
| toi_together_seconds | DECIMAL | TOI together |
| combined_rating | DECIMAL | Sum of ratings |

### Table: `fact_head_to_head`

Alternative H2H with rating comparisons:

| Column | Type | Description |
|--------|------|-------------|
| player_1_id | TEXT | Player 1 |
| player_1_rating | DECIMAL | Rating |
| player_1_venue | TEXT | Home/Away |
| player_2_id | TEXT | Player 2 (opponent) |
| player_2_rating | DECIMAL | Rating |
| player_2_venue | TEXT | Home/Away |
| shifts_against | INT | Matchup frequency |
| toi_against_seconds | DECIMAL | Time against |
| rating_diff | DECIMAL | player_1_rating - player_2_rating |

### Building a Player Comparison Dashboard

```javascript
async function comparePlayersInGame(gameId, player1Id, player2Id) {
    // Get both players' game stats
    const { data: stats } = await supabase
        .from('fact_player_game_stats')
        .select('*')
        .eq('game_id', gameId)
        .in('player_id', [player1Id, player2Id]);
    
    // Get their WOWY with each other
    const { data: wowy } = await supabase
        .from('fact_wowy')
        .select('*')
        .eq('game_id', gameId)
        .eq('player_1_id', player1Id)
        .eq('player_2_id', player2Id);
    
    // Get their H2H (if on opposite teams)
    const { data: h2h } = await supabase
        .from('fact_h2h')
        .select('*')
        .eq('game_id', gameId)
        .eq('player_1_id', player1Id)
        .eq('player_2_id', player2Id);
    
    return {
        player1Stats: stats.find(s => s.player_id === player1Id),
        player2Stats: stats.find(s => s.player_id === player2Id),
        wowy: wowy[0],  // If teammates
        h2h: h2h[0]     // If opponents
    };
}
```

---

## Line Combinations

### Table: `fact_line_combos`

| Column | Type | Description |
|--------|------|-------------|
| line_combo_key | TEXT PK | Unique key |
| game_id | TEXT FK | Game reference |
| venue | TEXT | Home/Away |
| **forward_combo** | TEXT | F1-F2-F3 player IDs |
| **defense_combo** | TEXT | D1-D2 player IDs |
| shifts | INT | Shifts together |
| toi_together | DECIMAL | TOI in seconds |
| goals_for | INT | Goals scored |
| goals_against | INT | Goals allowed |
| plus_minus | INT | Net goals |
| corsi_for | DECIMAL | Shot attempts for |
| corsi_against | DECIMAL | Shot attempts against |
| cf_pct | DECIMAL | Corsi For % |
| xgf | DECIMAL | Expected goals for |
| xg_against | DECIMAL | Expected goals against |
| zone_entries | INT | Zone entries |
| zone_exits | INT | Zone exits |
| controlled_entry_pct | DECIMAL | % controlled entries |
| giveaways | INT | Giveaways |
| takeaways | INT | Takeaways |
| **avg_player_rating** | DECIMAL | Average line rating |
| **opp_avg_rating** | DECIMAL | Average opponent rating |
| rating_diff | DECIMAL | Rating advantage |
| pdo | DECIMAL | PDO (luck metric) |
| sh_pct | DECIMAL | Shooting % |
| sv_pct | DECIMAL | Save % |
| team_name | TEXT | Team name |

### Line Combo Query Examples

```sql
-- Best performing lines by CF%
SELECT 
    forward_combo,
    defense_combo,
    shifts,
    toi_together / 60 as minutes,
    goals_for,
    goals_against,
    cf_pct,
    xgf - xg_against as xg_diff
FROM fact_line_combos
WHERE game_id = '18969'
  AND venue = 'home'
  AND shifts >= 3
ORDER BY cf_pct DESC;

-- Lines that score the most
SELECT 
    forward_combo,
    goals_for,
    xgf,
    sh_pct
FROM fact_line_combos
WHERE game_id = '18969'
ORDER BY goals_for DESC;

-- Defensive pairings
SELECT 
    defense_combo,
    shifts,
    goals_against,
    xg_against,
    cf_pct
FROM fact_line_combos
WHERE game_id = '18969'
ORDER BY goals_against ASC;
```

---

## Query Examples

### Complete Player Analysis Dashboard

```javascript
async function getPlayerDashboard(gameId, playerId) {
    // Basic stats
    const { data: stats } = await supabase
        .from('fact_player_game_stats')
        .select('*')
        .eq('game_id', gameId)
        .eq('player_id', playerId)
        .single();
    
    // WOWY - who does this player play well with?
    const { data: wowy } = await supabase
        .from('fact_wowy')
        .select('player_2_name, cf_pct_delta, toi_together')
        .eq('game_id', gameId)
        .eq('player_1_id', playerId)
        .order('cf_pct_delta', { ascending: false })
        .limit(5);
    
    // H2H - who does this player struggle against?
    const { data: h2h } = await supabase
        .from('fact_h2h')
        .select('player_2_name, cf_pct, toi_together')
        .eq('game_id', gameId)
        .eq('player_1_id', playerId)
        .order('toi_together', { ascending: false })
        .limit(5);
    
    // Line combos this player was part of
    const { data: lines } = await supabase
        .from('fact_line_combos')
        .select('forward_combo, defense_combo, cf_pct, goals_for')
        .eq('game_id', gameId)
        .or(`forward_combo.ilike.%${playerId}%,defense_combo.ilike.%${playerId}%`);
    
    return { stats, wowy, h2h, lines };
}
```

### Team WOWY Matrix

```sql
-- Create a matrix of all teammate combinations
SELECT 
    p1.player_1_name as player,
    p1.player_2_name as with_teammate,
    p1.cf_pct_together,
    p1.cf_pct_apart,
    p1.cf_pct_delta
FROM fact_wowy p1
WHERE p1.game_id = '18969'
  AND p1.venue = 'home'
ORDER BY p1.player_1_name, p1.cf_pct_delta DESC;
```

### H2H Matchup Report

```sql
-- Full matchup report for a game
SELECT 
    h.player_1_name as player,
    h.player_2_name as opponent,
    h.toi_together / 60 as minutes,
    h.cf_pct,
    h.goals_for,
    h.goals_against,
    h.xgf - h.xga as xg_diff
FROM fact_h2h h
WHERE h.game_id = '18969'
ORDER BY h.toi_together DESC;
```

---

## Visual Dashboard Ideas

### WOWY Heatmap

```
                    PLAYER A's WOWY MATRIX
                    
              Teammate B  Teammate C  Teammate D
           ┌─────────────┬───────────┬───────────┐
 CF% Delta │    +7.2%    │   +3.1%   │   -2.4%   │
           │   (green)   │  (yellow) │   (red)   │
           └─────────────┴───────────┴───────────┘
           
 Interpretation: Player A plays best with Teammate B
```

### H2H Comparison Chart

```
         Player A vs Opponents
         
 Opponent    CF%    Minutes    Result
 ─────────────────────────────────────
 Opp 1      62%    ████████   WON
 Opp 2      55%    ██████     WON
 Opp 3      48%    ████       LOST
 Opp 4      41%    ██████     LOST
```

### Line Combo Performance

```
         Line Performance (CF%)
         
 Line 1 (F-F-F / D-D)   ████████████  58%
 Line 2 (F-F-F / D-D)   ██████████    52%
 Line 3 (F-F-F / D-D)   ████████      47%
 Line 4 (F-F-F / D-D)   ██████        44%
```

---

## Summary

| Analysis Type | Table | Key Metric | Use Case |
|--------------|-------|------------|----------|
| **WOWY** | fact_wowy | cf_pct_delta | Find best linemates |
| **H2H** | fact_h2h | cf_pct | Find tough matchups |
| **Line Combos** | fact_line_combos | cf_pct, goals | Optimize lines |
| **Player Pairs** | fact_player_pair_stats | combined_rating | Chemistry analysis |
| **Matchup Summary** | fact_matchup_summary | synergy_score | Combined analysis |

These analytics tables enable NHL-quality analysis at the recreational level!
