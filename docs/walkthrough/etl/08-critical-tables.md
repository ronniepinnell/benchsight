# 08 - Critical Tables Deep Dive

**Learning Objectives:**
- Understand fact_events column by column
- Understand fact_player_game_stats (317 columns!)
- Know how to query these tables effectively

---

## Table 1: fact_events

📍 **Location:** `data/output/fact_events.csv`
📍 **Builder:** `src/builders/events.py`
**Grain:** One row per event
**Rows:** ~5,800 per 4 games

### Key Columns

#### Identity Columns
| Column | Type | Example | Purpose |
|--------|------|---------|---------|
| event_id | VARCHAR | E19001_P2_0845_001 | Unique event identifier |
| game_id | INTEGER | 19001 | Which game |
| period | INTEGER | 2 | Which period (1-5) |
| event_sequence | INTEGER | 1 | Sequence within timestamp |

#### Event Classification
| Column | Type | Example | Purpose |
|--------|------|---------|---------|
| event_type | VARCHAR | Goal, Shot, Pass, Faceoff | Major event category |
| event_detail | VARCHAR | Goal_Scored, Shot_OnNet | Specific event type |
| event_detail_2 | VARCHAR | WristShot | Additional detail |
| play_detail | VARCHAR | AssistPrimary | Context (for assists) |

🔑 **Critical Rule:**
```
Goals are ONLY: event_type='Goal' AND event_detail='Goal_Scored'
Shot_Goal is a SHOT that scored, not the goal event!
```

#### Player Columns
| Column | Type | Example | Purpose |
|--------|------|---------|---------|
| event_player_1 | VARCHAR | P001 | Primary actor (scorer, shooter, passer) |
| event_player_2 | VARCHAR | P002 | Secondary (primary assist) |
| event_player_3 | VARCHAR | P003 | Tertiary (secondary assist) |
| team_id | VARCHAR | T_Blue | Which team |
| team_venue | VARCHAR | home | Home or away |

#### Time Columns
| Column | Type | Example | Purpose |
|--------|------|---------|---------|
| event_start_min | INTEGER | 8 | Minutes into period |
| event_start_sec | INTEGER | 45 | Seconds |
| time_start_total_seconds | INTEGER | 525 | Total seconds (8*60+45) |
| event_running_start | INTEGER | 1725 | Cumulative from game start |

**Time calculation:**
```python
time_start_total_seconds = event_start_min * 60 + event_start_sec
event_running_start = (period - 1) * 1200 + time_start_total_seconds
```

#### Location Columns
| Column | Type | Example | Purpose |
|--------|------|---------|---------|
| x_coord | INTEGER | 172 | X position on rink (0-200) |
| y_coord | INTEGER | 42 | Y position on rink (0-85) |
| zone | VARCHAR | O | Offensive/Neutral/Defensive |
| home_team_zone | VARCHAR | O | Zone from home team perspective |
| away_team_zone | VARCHAR | D | Zone from away team perspective |

**Rink coordinate system:**
```
       ┌─────────────────────────────────────────┐
       │              RINK (200ft x 85ft)        │
  0,85 │    ↓Home Goal       ↓Away Goal         │ 200,85
       │    x=11             x=189               │
       │                                         │
       │  ←─────── Defensive ──────→            │
       │          (Home perspective)             │
       │                                         │
  0,0  └─────────────────────────────────────────┘ 200,0
```

#### Flag Columns (Boolean)
| Column | Type | Purpose |
|--------|------|---------|
| is_goal | BOOL | True if goal scored |
| is_shot_on_goal | BOOL | True if SOG (includes goals) |
| is_corsi_event | BOOL | True if counts for Corsi |
| is_fenwick_event | BOOL | True if counts for Fenwick |
| is_rush | BOOL | True if rush play |
| is_rebound | BOOL | True if rebound shot |

#### Foreign Keys
| Column | References | Purpose |
|--------|------------|---------|
| shift_id | fact_shifts | Which shift this event occurred during |
| period_id | dim_period | Period lookup |
| event_type_id | dim_event_type | Event type lookup |
| event_detail_id | dim_event_detail | Event detail lookup |

### Common Queries

**Get all goals in a game:**
```sql
SELECT *
FROM fact_events
WHERE game_id = 19001
  AND is_goal = true;
```

**Get shots by a player:**
```sql
SELECT *
FROM fact_events
WHERE event_player_1 = 'P001'
  AND event_type = 'Shot';
```

**Get high-danger shots:**
```sql
SELECT *
FROM fact_events
WHERE event_type = 'Shot'
  AND x_coord > 170  -- Close to goal
  AND y_coord BETWEEN 30 AND 55;  -- Slot area
```

---

## Table 2: fact_player_game_stats

📍 **Location:** `data/output/fact_player_game_stats.csv`
📍 **Builder:** `src/builders/player_stats.py`
**Grain:** One row per player per game (skaters only)
**Rows:** ~350 per 4 games
**Columns:** 317 (!)

This is the most important analytics table. It contains every stat for every player in every game.

### Column Categories

The 317 columns are organized into categories:

#### 1. Identity (5 columns)
| Column | Example | Purpose |
|--------|---------|---------|
| player_game_key | PG19001P001 | Primary key |
| player_id | P001 | Player identifier |
| game_id | 19001 | Game identifier |
| team_id | T_Blue | Team identifier |
| player_rating | 4.5 | Player skill rating |

#### 2. Basic Counting Stats (~15 columns)
| Column | Calculation | Filter Context |
|--------|-------------|----------------|
| goals | COUNT | event_type='Goal' AND event_detail='Goal_Scored' AND event_player_1=player_id |
| primary_assists | COUNT | play_detail='AssistPrimary' AND event_player_1=player_id |
| secondary_assists | COUNT | play_detail='AssistSecondary' AND event_player_1=player_id |
| assists | goals + secondary_assists | - |
| points | goals + assists | - |
| shots | COUNT | event_type='Shot' AND event_player_1=player_id |
| sog | COUNT | is_shot_on_goal=true AND event_player_1=player_id |
| shooting_pct | goals / sog * 100 | WHERE sog > 0 |

#### 3. Time on Ice (~10 columns)
| Column | Calculation | Purpose |
|--------|-------------|---------|
| toi_seconds | SUM(shift_duration) | Total ice time |
| toi_minutes | toi_seconds / 60 | Ice time in minutes |
| shift_count | COUNT(DISTINCT shifts) | Number of shifts |
| avg_shift | toi_seconds / shift_count | Average shift length |
| toi_5v5 | SUM WHERE strength='5v5' | Even strength TOI |
| toi_pp | SUM WHERE strength LIKE '%PP%' | Power play TOI |
| toi_pk | SUM WHERE strength LIKE '%PK%' | Penalty kill TOI |

#### 4. Faceoffs (~5 columns)
| Column | Calculation |
|--------|-------------|
| fo_wins | COUNT WHERE event_type='Faceoff' AND event_player_1=player_id |
| fo_losses | COUNT WHERE event_type='Faceoff' AND opp_player_1=player_id |
| fo_total | fo_wins + fo_losses |
| fo_pct | fo_wins / fo_total * 100 |

#### 5. Turnovers (~10 columns)
| Column | Calculation |
|--------|-------------|
| giveaways | COUNT WHERE event_detail LIKE '%Giveaway%' |
| takeaways | COUNT WHERE event_detail LIKE '%Takeaway%' |
| turnover_diff | takeaways - giveaways |
| bad_giveaways | COUNT WHERE is_bad_giveaway=true |

#### 6. Corsi/Fenwick (~20 columns)
| Column | Definition |
|--------|------------|
| corsi_for | Shot attempts FOR (SOG + missed + blocked) |
| corsi_against | Shot attempts AGAINST while on ice |
| cf_pct | corsi_for / (corsi_for + corsi_against) * 100 |
| fenwick_for | Shot attempts FOR (SOG + missed, excludes blocked) |
| fenwick_against | Shot attempts AGAINST while on ice |
| ff_pct | fenwick_for / (fenwick_for + fenwick_against) * 100 |
| cf_60 | corsi_for per 60 minutes |
| ca_60 | corsi_against per 60 minutes |

#### 7. Expected Goals (~15 columns)
| Column | Calculation |
|--------|-------------|
| xg_for | SUM(shot_xg) for player's shots |
| xg_against | SUM(shot_xg) for opponent shots while on ice |
| goals_above_xg | goals - xg_for |
| xg_per_shot | xg_for / shots |
| xg_for_60 | xg_for per 60 minutes |

#### 8. WAR/GAR (~15 columns)
| Column | Components |
|--------|------------|
| gar_offense | Goals × 1.0 + primary_assists × 0.7 + ... |
| gar_defense | takeaways × 0.05 + blocks × 0.02 + ... |
| gar_possession | (cf_pct - 50) × factor × toi |
| gar_transition | zone_entry_controlled × 0.04 |
| gar_poise | pressure_success × 0.02 |
| gar_total | Sum of all GAR components |
| war | gar_total / 4.5 |

#### 9. Game Score (~15 columns)
| Column | Components |
|--------|------------|
| gs_scoring | goals × 1.0 + assists × 0.8 |
| gs_shots | sog × 0.1 + high_danger_shots × 0.15 |
| gs_playmaking | entries × 0.08 + second_touch × 0.02 |
| gs_defense | takeaways × 0.15 + blocks × 0.08 |
| gs_hustle | (fo_wins - fo_losses) × 0.03 |
| game_score | Sum of components |

#### 10. Rate Stats (~30 columns)
All "per 60 minutes" versions:
- goals_per_60, assists_per_60, points_per_60
- shots_per_60, sog_per_60
- corsi_per_60, fenwick_per_60
- xg_per_60, etc.

**Rate calculation:**
```python
stat_per_60 = stat / toi_hours * 60
# where toi_hours = toi_seconds / 3600
```

#### 11. Strength Splits (~50 columns)
All stats broken down by game situation:
- `*_5v5` - Even strength
- `*_pp` - Power play
- `*_pk` - Penalty kill
- `*_en` - Empty net

#### 12. Shot Type Breakdown (~20 columns)
| Column | Purpose |
|--------|---------|
| shots_wrist | Wrist shots |
| shots_slap | Slap shots |
| shots_snap | Snap shots |
| shots_backhand | Backhand shots |
| shots_tip | Tip-ins |
| shots_deflection | Deflections |

#### 13. Pass Analysis (~25 columns)
| Column | Purpose |
|--------|---------|
| pass_attempts | Total passes |
| pass_completed | Successful passes |
| pass_pct | Completion percentage |
| pass_stretch | Long stretch passes |
| pass_bank | Bank passes |
| pass_rim | Rim passes |
| pass_slot | Passes to slot |

#### 14. Zone Entry/Exit (~20 columns)
| Column | Purpose |
|--------|---------|
| zone_entries | Total entries |
| zone_entry_controlled | Carry-ins |
| zone_entry_dump | Dump-ins |
| zone_exits | Total exits |
| zone_exit_controlled | Controlled exits |

#### 15. Danger Zone Stats (~20 columns)
| Column | Purpose |
|--------|---------|
| high_danger_shots | Shots from high-danger area |
| high_danger_goals | Goals from high-danger area |
| medium_danger_shots | Shots from medium area |
| low_danger_shots | Perimeter shots |

#### 16. Competition Analysis (~20 columns)
| Column | Purpose |
|--------|---------|
| avg_opp_rating | Average opponent rating |
| avg_teammate_rating | Average linemate rating |
| qoc | Quality of competition |
| qot | Quality of teammates |

#### 17. Game State (~20 columns)
| Column | Purpose |
|--------|---------|
| goals_leading | Goals while leading |
| goals_trailing | Goals while trailing |
| goals_tied | Goals while tied |
| toi_leading | TOI while leading |
| toi_trailing | TOI while trailing |

#### 18. Period Splits (~30 columns)
| Column | Purpose |
|--------|---------|
| goals_p1, goals_p2, goals_p3 | Goals by period |
| toi_p1, toi_p2, toi_p3 | TOI by period |
| shots_p1, shots_p2, shots_p3 | Shots by period |

### Common Queries

**Get top scorers in a game:**
```sql
SELECT player_id, goals, assists, points
FROM fact_player_game_stats
WHERE game_id = 19001
ORDER BY points DESC, goals DESC
LIMIT 10;
```

**Get advanced stats for a player:**
```sql
SELECT
    player_id,
    cf_pct,
    xg_for,
    goals_above_xg,
    war,
    game_score
FROM fact_player_game_stats
WHERE player_id = 'P001' AND game_id = 19001;
```

**Compare rate stats:**
```sql
SELECT
    player_id,
    goals_per_60,
    points_per_60,
    corsi_per_60,
    xg_per_60
FROM fact_player_game_stats
WHERE toi_seconds > 300  -- At least 5 minutes
ORDER BY points_per_60 DESC;
```

---

## Table 3: fact_shifts

📍 **Location:** `data/output/fact_shifts.csv`
**Grain:** One row per shift
**Rows:** ~400 per 4 games

### Key Columns

| Column | Type | Example | Purpose |
|--------|------|---------|---------|
| shift_id | VARCHAR | S19001_P2_001 | Unique shift identifier |
| game_id | INTEGER | 19001 | Which game |
| period | INTEGER | 2 | Which period |
| player_id | VARCHAR | P001 | Which player |
| team_id | VARCHAR | T_Blue | Which team |
| shift_start | INTEGER | 1180 | Start time (descending from 1200) |
| shift_end | INTEGER | 1120 | End time |
| shift_duration | INTEGER | 60 | Duration in seconds |
| strength | VARCHAR | 5v5 | Game situation |
| logical_shift_number | INTEGER | 1 | Shift number for this player |

### Time Note

⚠️ Shift times count DOWN (1200 → 0), unlike event times which count UP (0 → 1200).

```
Period start: shift_start = 1200
Period end:   shift_start = 0

To convert: event_time = 1200 - shift_time
```

---

## Querying Tips

### Joining Tables

**Events with player info:**
```sql
SELECT
    e.event_id,
    e.event_type,
    p.player_name
FROM fact_events e
JOIN dim_player p ON e.event_player_1 = p.player_id
WHERE e.game_id = 19001;
```

**Game stats with team info:**
```sql
SELECT
    t.team_name,
    SUM(s.goals) as team_goals,
    SUM(s.assists) as team_assists
FROM fact_player_game_stats s
JOIN dim_team t ON s.team_id = t.team_id
WHERE s.game_id = 19001
GROUP BY t.team_name;
```

### Filtering Patterns

**Goals only (correct):**
```sql
WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored'
-- Or use the pre-computed flag:
WHERE is_goal = true
```

**Shots on goal:**
```sql
WHERE is_shot_on_goal = true
```

**Corsi events:**
```sql
WHERE is_corsi_event = true
```

---

## Key Takeaways

1. **fact_events** has ~50 columns describing each event
2. **fact_player_game_stats** has 317 columns covering every stat
3. **Use flags** (`is_goal`, `is_corsi_event`) for filtering
4. **Shift times count DOWN**, event times count UP
5. **Rate stats** are per-60-minutes (`stat / toi_hours * 60`)
6. **Join on player_id, game_id, team_id** to combine tables

---

**Next:** [09-calculations.md](09-calculations.md) - All formulas explained
