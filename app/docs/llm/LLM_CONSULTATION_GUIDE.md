# BenchSight - LLM Consultation Guide
## Instructions for GPT, Gemini, and Other AI Assistants

---

## Project Context

**BenchSight** is a hockey analytics platform for beer league and junior hockey that aims to provide NHL-level analytics to recreational players.

### Key Points
- Data comes from **manual tracking** via Excel spreadsheets
- Architecture: Raw → Stage → Intermediate → Mart data pipeline
- PostgreSQL for persistent storage
- Python ETL (pandas, SQLAlchemy)
- HTML/JS portal with interactive dashboards
- Power BI for advanced visualizations

### Three Project Goals
1. **Near-term**: Team game viewing for teammates
2. **Mid-term**: Resume/portfolio showcase
3. **Long-term**: Commercial product

---

## Data Schema Overview

### Dimension Tables
```
dim_player
├── player_id (PK)
├── player_full_name
├── current_skill_rating (1-6 scale)
├── player_primary_position
├── player_image
└── random_player_full_name (for privacy)

dim_team
├── team_id (PK)
├── team_name
├── team_color1-4
└── team_logo

dim_game
├── game_id (PK)
├── date
├── home_team_id, away_team_id
├── home_total_goals, away_total_goals
└── video_url
```

### Fact Tables
```
fact_playbyplay
├── event_id (PK)
├── game_id (FK)
├── sequence_index, play_index
├── event_type, event_detail_1, event_detail_2
├── event_start_running_sec, event_duration_sec
├── is_goal, is_shot, is_zone_entry, etc.
└── x_coord, y_coord

fact_player_game_stats
├── game_id, player_id
├── goals, assists, points
├── corsi_for, corsi_against, corsi_pct
├── zone_entries, true_giveaways, takeaways
└── avg_opponent_rating (rating context)

fact_shifts
├── shift_id
├── game_id, period
├── shift_duration_sec
├── on-ice player positions
└── rating_differential
```

---

## Statistics Catalog (Key Stats)

### Basic Stats
| Stat | Formula |
|------|---------|
| Goals | Count where event_type='shot' AND event_detail_1='goal' |
| Assists | Count goal events where player is assist_1_id or assist_2_id |
| SOG | Count shots on goal (not blocked/missed) |
| TOI | Sum of shift durations |

### Advanced Stats (On-Ice)
| Stat | Formula |
|------|---------|
| CF (Corsi For) | Shot attempts while player on ice |
| CA (Corsi Against) | Opponent shot attempts while player on ice |
| CF% | CF / (CF + CA) |
| FF% | Fenwick (unblocked shots) percentage |

### Micro Stats (BenchSight Unique)
| Stat | Formula |
|------|---------|
| Possession Time | SUM(event_duration_sec) where team has puck |
| Zone Entry Success | Successful entries / total entries |
| True Giveaways | Turnovers that are misplays (NOT dumps) |
| Pass Completion % | Successful passes / total passes |

### Rating-Adjusted Stats
| Stat | Description |
|------|-------------|
| Rating-Weighted CF | CF adjusted by opponent rating |
| Quality of Competition | Avg rating of opponents faced |
| Rating Differential | Team rating - opponent rating |

---

## Current Data Inventory

### 9 Tracked Games
- 18955, 18965, 18969, 18977, 18981, 18987, 18991, 18993, 19032
- ~24,000 total events
- ~870 shifts
- Video timestamps for 7 games

### Master Tables (BenchSight_Tables.xlsx)
- 100+ players with ratings and images
- 15 teams with colors and logos
- Full season schedule
- Rink coordinate zones

---

## How to Help This Project

### If Asked About Stats
1. Check the stats catalog for existing definitions
2. Suggest new stats that hockey analytics uses
3. Consider the data available (events, shifts, XY coords)

### If Asked About Architecture
1. Respect the Raw → Stage → Intermediate → Mart flow
2. Suggest optimizations for the ETL pipeline
3. Consider Power BI integration requirements

### If Asked About UI/UX
1. Reference NHL Edge, Natural Stat Trick, Evolving Hockey for inspiration
2. Prioritize click-through drill-downs
3. Remember privacy mode requirement

### If Asked About ML
1. xG models are planned but not implemented
2. Player similarity (BLB ↔ NHL) is in the ETL plan
3. Computer vision for puck tracking is future work

---

## Common Questions & Answers

**Q: What makes BenchSight different from NHL analytics?**
A: BenchSight uses manual tracking for beer league games where no automatic tracking exists. It also includes player skill ratings (1-6 scale) for context.

**Q: How is possession calculated?**
A: By summing event_duration_sec for events where the team has the puck, NOT just counting possession events.

**Q: What's a "true giveaway"?**
A: A turnover caused by a player misplay (bad pass, lost puck). Dumps and clears are NOT counted as giveaways.

**Q: How does rating context work?**
A: Each event/shift tracks the average rating of opponents on ice, allowing stats to be adjusted for quality of competition.

---

## Files to Reference

1. **BENCHSIGHT_MASTER_STATUS.md** - Complete project status and triage
2. **stats_catalog_master_ultimate.csv** - All stat definitions
3. **tables_catalog.csv** - Database schema reference
4. **create_schema.sql** - PostgreSQL DDL

---

## Example Prompts for This Project

```
"Review the stats catalog and suggest what hockey analytics stats are missing"

"How would you implement an xG model given events with XY coordinates?"

"What's the best way to calculate zone entry success rate from this data?"

"Design a player comparison feature matching BLB players to NHL players"

"Optimize the ETL pipeline for near-real-time updates"
```

---

*This guide helps AI assistants understand BenchSight context for effective consultation.*
