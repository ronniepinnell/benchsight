# BenchSight Hockey Analytics Platform
## Master Documentation - December 2025

> **For LLMs**: Start with `README_FOR_LLM.txt` for navigation guidance
> **For Humans**: Start with `README_FOR_HUMANS.txt` for project overview

---

# Table of Contents

1. [Project Vision](#1-project-vision)
2. [Architecture Overview](#2-architecture-overview)
3. [Stats Catalog Summary](#3-stats-catalog-summary)
4. [Table Catalog Summary](#4-table-catalog-summary)
5. [Tracker Import Reference](#5-tracker-import-reference)
6. [Roadmap & Phases](#6-roadmap--phases)
7. [Inspiration & Research Links](#7-inspiration--research-links)
8. [Implementation Status](#8-implementation-status)
9. [Power BI & DAX Reference](#9-power-bi--dax-reference)
10. [ML & Future Ideas](#10-ml--future-ideas)
11. [Known Issues & Notes](#11-known-issues--notes)
12. [File Reference](#12-file-reference)

---

# 1. Project Vision

## What Is BenchSight?

BenchSight is a **"Moneyball for beer league and junior hockey"** platform:
- Manually (or semi-automatically) track detailed events and shifts
- Combine tracking with league boxscore data and player ratings
- Produce NHL-style advanced stats, microstats, and visual reports for:
  - Individual players (player cards)
  - Lines / pairings (WOWY analysis)
  - Full teams (game summaries)
  - Head-to-head matchups over time

## Audience Ladder

| Phase | Audience | Features |
|-------|----------|----------|
| **1** | Your team/league | Prove value with own games |
| **2** | Local/junior clubs | White-glove onboarding, simple subscription |
| **3** | Regional/national | Automation, APIs, self-serve dashboards |
| **4** | Pro | Computer vision, full pipeline, custom models |

## Differentiation

- **Depth of tracking**: Microstats most leagues cannot see
- **Flexibility**: Works with fully tracked games AND boxscore-only games
- **Storytelling**: ESPN/NHL-style summaries, player cards, line dashboards
- **Roadmap**: Path toward computer-vision powered auto-tracking

---

# 2. Architecture Overview

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA SOURCES                           │
├─────────────────────────────────────────────────────────────┤
│ BLB_Tables.xlsx    │ *_tracking.xlsx  │ *_video_times.xlsx │
│ (dims, rosters,    │ (events, shifts, │ (YouTube links,    │
│  schedule)         │  rosters)        │  timestamps)       │
└─────────┬───────────────────┬─────────────────┬────────────┘
          │                   │                 │
          ▼                   ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                     STAGE LAYER (stg_*)                     │
│ Raw to cleaned, one-to-one with sources                     │
│ - stg_events, stg_shifts, stg_game_rosters, stg_xy          │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 INTERMEDIATE LAYER (int_*)                  │
│ Heavy transformations:                                      │
│ - Events long → wide                                        │
│ - Shifts wide → long → logical player shifts                │
│ - Event chains: linked_event, sequence, play indices        │
│ - Attach XY + rink zones                                    │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATAMART LAYER (fact_/dim_)              │
│ Star/snowflake schema for all games:                        │
│ - dim_player, dim_team, dim_schedule, dim_rink_zones        │
│ - fact_events, fact_event_players, fact_shifts              │
│ - fact_shift_players, fact_box_score, fact_gameroster       │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        OUTPUTS                              │
├─────────────────────────────────────────────────────────────┤
│ Power BI     │ Python Dashboards │ ML Models │ CSV Export   │
│ (star schema)│ (Dash/Streamlit)  │ (xG, etc) │ (for sharing)│
└─────────────────────────────────────────────────────────────┘
```

## Key Tables

### Dimensions
| Table | Grain | Key | Purpose |
|-------|-------|-----|---------|
| dim_player | One row per player | player_id | Central player dimension with ratings (2-6) |
| dim_team | One row per team | team_id | Team colors, codes, leagues |
| dim_schedule | One row per game | game_id | Game header, scores, tracking metadata |
| dim_rink_zones | One row per zone | zone_id | Map XY to meaningful zones |
| dim_game_players | One row per player-game | game_player_id | Bridge between player and schedule |

### Facts
| Table | Grain | Key | Purpose |
|-------|-------|-----|---------|
| fact_events | One row per event | event_id | Main event table with all plays |
| fact_event_players | One row per event-role-player | event_player_id | Who did what in each event |
| fact_shifts | One row per logical shift | shift_id | Shift context for teams |
| fact_shift_players | One row per player-shift | shift_player_id | Detailed TOI by shift |
| fact_box_score | One row per player-game | composite | Aggregated microstats per game |
| fact_gameroster | One row per player-game | composite | Official league stats |

---

# 3. Stats Catalog Summary

## Stats by Category

### Core Boxscore (8 stats)
| ID | Name | Description | Status |
|----|------|-------------|--------|
| G | Goals | Goals scored | ✅ Implemented |
| A1/A2 | Primary/Secondary Assists | Assists by type | ✅ Implemented |
| PTS | Points | G + A1 + A2 | ✅ Implemented |
| SOG | Shots on Goal | Shots reaching net | ✅ Implemented |
| PIM | Penalty Minutes | Penalty time | ✅ Implemented |
| TOI | Time on Ice | Total ice time | ✅ Implemented |
| PLUS_MINUS | Plus/Minus | EV goal differential on ice | ✅ Implemented |

### On-Ice / Possession (12 stats)
| ID | Name | Description | Status |
|----|------|-------------|--------|
| CF | Corsi For | Shot attempts for while on ice | ✅ Implemented |
| CA | Corsi Against | Shot attempts against while on ice | ✅ Implemented |
| CF% | Corsi For % | CF / (CF + CA) | ✅ Implemented |
| FF | Fenwick For | Unblocked shot attempts for | ✅ Implemented |
| FA | Fenwick Against | Unblocked shot attempts against | ✅ Implemented |
| FF% | Fenwick For % | FF / (FF + FA) | ✅ Implemented |
| GF | Goals For | Goals for while on ice | ✅ Implemented |
| GA | Goals Against | Goals against while on ice | ✅ Implemented |
| GF% | Goals For % | GF / (GF + GA) | ✅ Implemented |
| SF | Shots For | Shots for while on ice | ✅ Implemented |
| SA | Shots Against | Shots against while on ice | ✅ Implemented |
| PDO | PDO | Sh% + Sv% (luck indicator) | 🔄 Planned |

### Expected Goals (6 stats)
| ID | Name | Description | Status |
|----|------|-------------|--------|
| xG_SHOT | Shot xG | Per-shot expected goals | 📍 Needs XY |
| xGF | xG For | Sum of xG for team while on ice | 📍 Needs XY |
| xGA | xG Against | Sum of xG against while on ice | 📍 Needs XY |
| xGF% | xG For % | xGF / (xGF + xGA) | 📍 Needs XY |
| ixG | Individual xG | xG of player's own shots | 📍 Needs XY |
| GSAx | Goals Saved Above Expected | Goalie xG performance | 📍 Needs XY |

### Micro-Offense (15 stats)
| ID | Name | Description | Status |
|----|------|-------------|--------|
| PASS_ATTEMPT | Pass Attempts | All pass attempts | ✅ Tracking |
| PASS_COMPLETED | Passes Completed | Successful passes | ✅ Tracking |
| PASS_PCT | Pass % | Completion percentage | ✅ Tracking |
| ZONE_ENTRY | Zone Entries | Entries into OZ | ✅ Tracking |
| ZONE_ENTRY_CTRL | Controlled Entries | Entries with control | ✅ Tracking |
| CARRY_IN | Carry-Ins | Entries via carrying puck | ✅ Tracking |
| DUMP_IN | Dump-Ins | Entries via dump | ✅ Tracking |
| OZ_POSS_TIME | OZ Possession Time | Time controlling puck in OZ | 🔄 Planned |
| CYCLE_LENGTH | Cycle Length | Passes per OZ sequence | 🔄 Planned |
| SLOT_PASS | Slot Passes | Passes into slot area | 📍 Needs XY |
| ROYAL_ROAD | Royal Road Passes | Cross-slot passes | 📍 Needs XY |
| RUSH_CHANCE | Rush Chances | Quick chances off rush | ✅ Tracking |
| REBOUND_CREATED | Rebounds Created | Shots generating rebounds | ✅ Tracking |
| SCREEN | Screens | Net-front screens | ✅ Tracking |

### Micro-Defense (12 stats)
| ID | Name | Description | Status |
|----|------|-------------|--------|
| BLOCK | Blocked Shots | Shots blocked | ✅ Tracking |
| TAKEAWAY | Takeaways | Pucks taken from opponent | ✅ Tracking |
| GIVEAWAY | Giveaways | Pucks given to opponent | ✅ Tracking |
| ZONE_EXIT | Zone Exits | Exits from DZ | ✅ Tracking |
| ZONE_EXIT_CTRL | Controlled Exits | Exits with control | ✅ Tracking |
| BREAKUP | Pass Breakups | Passes disrupted | ✅ Tracking |
| DENIAL | Denials | Entry denials | ✅ Tracking |
| CLEAR | Clears | Puck cleared from DZ | ✅ Tracking |
| RETRIEVAL | Retrievals | Puck battles won | ✅ Tracking |
| GAP_CONTROL | Gap Control | Defensive gap quality | 📍 Needs Tracking |

### Transition (8 stats)
| ID | Name | Description | Status |
|----|------|-------------|--------|
| FORECHECK_PRESS | Forecheck Pressure | Pressure in OZ | ✅ Tracking |
| TURNOVER_FORCED | Turnovers Forced | Caused giveaways | ✅ Tracking |
| BREAKOUT_CTRL | Controlled Breakouts | Clean zone exits | ✅ Tracking |
| RUSH_SHOTS | Rush Shots | Shots off rush | ✅ Tracking |
| COUNTER_ATTACK | Counter Attacks | Quick transitions | 🔄 Planned |

### Goalie (10 stats)
| ID | Name | Description | Status |
|----|------|-------------|--------|
| SV% | Save Percentage | Saves / Shots | ✅ Implemented |
| GAA | Goals Against Average | GA per 60 | ✅ Implemented |
| HD_SV% | High-Danger Save % | Saves on HD shots | 📍 Needs XY |
| REBOUND_CTRL | Rebound Control | Rebound rate | ✅ Tracking |
| FREEZE% | Freeze % | Puck frozen rate | ✅ Tracking |

### Lineup / WOWY (6 stats)
| ID | Name | Description | Status |
|----|------|-------------|--------|
| QoC | Quality of Competition | Opponent rating context | ✅ Tracking |
| QoT | Quality of Teammates | Teammate rating context | ✅ Tracking |
| WOWY_GF_DIFF | WOWY GF Diff | GF% with vs without player | 🔄 Planned |
| LINE_CF60 | Line Corsi/60 | Line combo shot rate | ✅ Tracking |
| PAIR_TOI | Pairing TOI | D-pair ice time together | ✅ Tracking |

### Rating-Aware (5 stats)
| ID | Name | Description | Status |
|----|------|-------------|--------|
| RATING_PLUSMINUS | Rating-Adj +/- | +/- with opponent ratings | ✅ Tracking |
| GIVEAWAY_VS_ELITE | Giveaways vs Elite | Turnovers vs top players | ✅ Tracking |
| OZ_TIME_VS_WEAK | OZ Time vs Weak | OZ time vs weaker lines | ✅ Tracking |

**Total: 80+ stats defined** (see `benchsight_stats_catalog_master_ultimate.csv` for complete list)

---

# 4. Table Catalog Summary

## Current Tables (in data/output/)

### Dimensions (18 tables)
- dim_player.csv (335 records)
- dim_team.csv (26 records)
- dim_schedule.csv (552 records)
- dim_season.csv
- dim_dates.csv
- dim_period.csv
- dim_position.csv
- dim_event_type.csv
- dim_event_detail.csv
- dim_play_detail.csv
- dim_zone.csv
- dim_strength.csv
- dim_situation.csv
- dim_rinkboxcoord.csv (50 records)
- dim_rinkcoordzones.csv (297 records)
- dim_danger_zone.csv
- dim_skill_tier.csv
- dim_player_role.csv

### Facts (16 tables)
- fact_events.csv
- fact_events_tracking.csv
- fact_event_players_tracking.csv
- fact_shifts_tracking.csv
- fact_shift_players_tracking.csv
- fact_plays_tracking.csv
- fact_sequences_tracking.csv
- fact_linked_events_tracking.csv
- fact_box_score.csv
- fact_box_score_tracking.csv
- fact_gameroster.csv (14,239 records)
- fact_playergames.csv
- fact_registration.csv
- fact_leadership.csv
- fact_draft.csv
- dim_game_players_tracking.csv

---

# 5. Tracker Import Reference

## Supported File Formats

### Tracking Excel Files
Pattern: `{game_id}_tracking.xlsx` or `_tracking.xlsx`

**Required Sheets:**
- `events` - Play-by-play events
- `shifts` - Shift data with on-ice players
- `game_rosters` (optional) - Roster info

### Event Sheet Columns (72+ columns)
Key columns used by importer:
| Column | Variants | Description |
|--------|----------|-------------|
| event_index | tracking_event_index | Unique event ID |
| period | Period | 1, 2, or 3 |
| event_type | Type, event_type_ | Pass, Shot, Faceoff, etc. |
| event_detail | event_detail_, detail_1 | Primary detail |
| event_detail_2 | event_detail_2_, detail_2 | Secondary detail |
| event_successful | event_successful_ | S/U or 1/0 |
| event_team_zone | event_team_zone2_ | o/n/d |
| team_venue | team_venue_abv | home/away |
| event_start_min | event_start_min_ | Clock minutes |
| event_start_sec | event_start_sec_ | Clock seconds |
| shift_index | | Associated shift |
| player_game_number | player_game_number_ | Jersey number |
| player_role | role_abrev | evt_1, opp_1, etc. |
| running_video_time | | Video timestamp |

### Shift Sheet Columns (55 columns)
| Column | Description |
|--------|-------------|
| shift_index | Unique shift ID |
| Period | 1, 2, or 3 |
| shift_start_min/sec | Start time |
| shift_end_min/sec | End time |
| shift_start_type | OtherFaceoff, etc. |
| shift_stop_type | Goal, Whistle, etc. |
| home_forward_1/2/3 | Home forwards |
| home_defense_1/2 | Home defensemen |
| home_goalie | Home goalie |
| home_xtra | Extra attacker |
| away_forward_1/2/3 | Away forwards |
| away_defense_1/2 | Away defensemen |
| away_goalie | Away goalie |
| away_xtra | Extra attacker |

## Game Tracking Status

| Game | Home | Away | Events | Shifts | Video | Status |
|------|------|------|--------|--------|-------|--------|
| 18955 | Velodrome | Orphans | CSV only | None | ✅ | Partial |
| 18965 | OS Offices | Velodrome | 2 | 98 | ❌ | Minimal |
| 18969 | Platinum | Velodrome | 3,141 | 98 | ✅ | **FULL** |
| 18977 | Velodrome | HollowBrook | 2,527 | 88 | ✅ | **FULL** |
| 18981 | Nelson | Velodrome | 2,425 | 106 | ✅ | **FULL** |
| 18987 | Velodrome | Outlaws | 3,064 | 106 | ✅ | **FULL** |
| 18991 | Triple J | Velodrome | 3 | 78 | ✅ | Minimal |
| 18993 | Platinum | Velodrome | 2 | 98 | ❌ | Minimal |
| 19032 | Outcan | Velodrome | 3 | 98 | ✅ | Minimal |

---

# 6. Roadmap & Phases

## SHORT TERM (0-3 months) – TEAM & RESUME

### Goals
- Stable ETL + datamart
- Meaningful reports for your team
- Strong portfolio project

### Key Features
- [x] Clean project structure: src/, sql/, data/, docs/, tracker/
- [x] Main orchestrator Python script
- [x] Tracker v16 with fixed Excel import
- [ ] Power BI model with game summary, player cards, line combos
- [ ] Python dashboard (Dash/Streamlit)
- [ ] Core stats from catalog: G, A, SOG, CF/CA, FF/FA, TOI

## MID TERM (3-12 months) – BENCH TOOL / LIGHT COMMERCIAL

### Goals
- Make tracking faster and more pleasant
- Turn system into something a whole team/club can use

### Key Features
- [ ] Web-based tracker UI with login/multi-team
- [ ] Roster selection from dim_player
- [ ] Integrated XY clicker for rink/net
- [ ] Per-game logging QA
- [ ] Simple subscription-ready structure

## LONG TERM (1-3 years) – VISION PLATFORM & PRO USE

### Goals
- Reduce manual tracking using computer vision
- Offer pro-level insights (xG, xPlay, route analysis)

### Key Features
- [ ] Vision pipeline (video ingestion, pose/tracking models)
- [ ] xG and xPlay models trained on own data
- [ ] Bench/iPad UI with live feedback

---

# 7. Inspiration & Research Links

## Analytics Sites

| Site | Focus | Inspiration |
|------|-------|-------------|
| [Evolving Hockey](https://evolving-hockey.com) | NHL advanced stats | xG models, RAPM, player cards |
| [Money Puck](https://moneypuck.com) | xG, predictions | Shot maps, game predictions |
| [Natural Stat Trick](https://naturalstattrick.com) | On-ice stats | Shift charts, line combos |
| [JFresh Hockey](https://jfresh.substack.com) | Visualizations | Player cards, team charts |
| [All Three Zones](https://allthreezones.com) | Microstats | Zone entries/exits |
| [HockeyViz](https://hockeyviz.com) | Heat maps | Shot location viz |

## NHL Edge / Tracking

| Resource | Focus |
|----------|-------|
| [NHL Edge](https://www.nhl.com/stats/edge) | Official tracking data |
| [Big Data Cup](https://www.stathletes.com/big-data-cup/) | Public tracking datasets |
| [Sportlogiq](https://sportlogiq.com) | Pro tracking provider |

## Design Inspiration

| Type | Examples |
|------|----------|
| Game Summaries | ESPN box scores, NHL.com game center |
| Player Cards | NHL Edge player pages, CapFriendly |
| Shot Charts | HockeyViz, Money Puck shot maps |
| Line Combos | Left Wing Lock, Daily Faceoff |

## Research Papers

| Topic | Notes |
|-------|-------|
| xG Models | Logistic regression on shot features |
| RAPM | Regularized Adjusted Plus-Minus |
| WAR | Wins Above Replacement frameworks |
| Computer Vision | Pose estimation, object tracking |

---

# 8. Implementation Status

## Completed ✅

- [x] Project structure (src/, sql/, data/, docs/)
- [x] BLB_Tables ingestion (335 players, 26 teams, 552 games)
- [x] Tracker v16 with fixed Excel import
- [x] DESC order for events/shifts display
- [x] XY coordinates for all players (+XY button)
- [x] Column mapping for all tracking file variants
- [x] Video timestamp integration
- [x] 40+ dimension and fact CSV outputs
- [x] Basic stats implementation (G, A, TOI, CF, FF)
- [x] Master checklist with 45+ tasks

## In Progress 🔄

- [ ] Power BI model with star schema
- [ ] Dashboard with game summary view
- [ ] Player card pages
- [ ] ETL consolidation to single JSON
- [ ] Wix deployment

## Planned 📋

- [ ] xG model (needs XY data)
- [ ] WOWY analysis
- [ ] Line combo optimizer
- [ ] Video clip auto-generation
- [ ] Computer vision tracking

---

# 9. Known Issues & Notes

## Import Considerations

1. **File naming**: Tracker handles both `{gameID}_tracking.xlsx` and `_tracking.xlsx`
2. **Column variants**: Import handles underscore suffixes (`event_type_` vs `event_type`)
3. **Empty games**: 18955 has CSVs only, no tracking.xlsx
4. **Video times**: Separate file `{gameID}_video_times.xlsx`

## Data Quality Notes

- Some games have minimal event tracking (just 2-3 events)
- Full games have 2,400-3,100+ events
- Shifts are generally complete across all games
- XY data is sparse (needs consistent tracking workflow)

## Contradictions Resolved

| Topic | Resolution |
|-------|------------|
| Column names | Use `getVal()` helper to try multiple variants |
| Event ordering | Now sorts by idx DESC (newest first) |
| Player XY | Added +XY button for unlimited coordinates |
| Display limits | Increased to 50 events, 30 shifts |

---

*Document Version: 1.0*
*Generated: December 2025*
*Project: BenchSight Hockey Analytics*

---

# 9. Power BI & DAX Reference

## Recommended Star Schema

```
                    ┌─────────────┐
                    │  dim_date   │
                    └──────┬──────┘
                           │
┌─────────────┐     ┌──────┴──────┐     ┌─────────────┐
│  dim_player │────►│ dim_schedule│◄────│  dim_team   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│                     FACT TABLES                         │
├─────────────────────────────────────────────────────────┤
│ fact_events │ fact_shifts │ fact_box_score │ fact_roster│
└─────────────────────────────────────────────────────────┘
```

## Key Relationships

| From | To | Key | Type |
|------|-----|-----|------|
| dim_schedule.game_id | fact_events.game_id | game_id | 1:Many |
| dim_schedule.game_id | fact_shifts.game_id | game_id | 1:Many |
| dim_schedule.game_id | fact_box_score.game_id | game_id | 1:Many |
| dim_player.player_id | fact_event_players.player_id | player_id | 1:Many |
| dim_player.player_id | fact_shift_players.player_id | player_id | 1:Many |
| dim_player.player_id | fact_box_score.player_id | player_id | 1:Many |
| dim_team.team_id | fact_events.team_id_for | team_id | 1:Many |
| dim_date.date | dim_schedule.game_date | date | 1:Many |

## Example DAX Measures

### Game Summary (ESPN/NHL Style)

```dax
// Goals - Home Team
Goals Home = 
CALCULATE(
    SUM(fact_box_score[goals]),
    TREATAS(VALUES(dim_schedule[home_team_id]), fact_box_score[team_id])
)

// Shots on Goal - Home
Shots Home = 
CALCULATE(
    SUM(fact_box_score[shots_on_goal]),
    TREATAS(VALUES(dim_schedule[home_team_id]), fact_box_score[team_id])
)

// Corsi For % - 5v5
CF% 5v5 = 
VAR CF = CALCULATE(SUM(fact_box_score[corsi_for]), fact_box_score[strength] = "5v5")
VAR CA = CALCULATE(SUM(fact_box_score[corsi_against]), fact_box_score[strength] = "5v5")
RETURN DIVIDE(CF, CF + CA)
```

### Player Card Stats

```dax
// TOI in Minutes
TOI Minutes = DIVIDE(SUM(fact_box_score[toi_seconds_total]), 60.0)

// Points per 60
Points/60 = 
VAR Pts = SUM(fact_box_score[goals]) + SUM(fact_box_score[assists])
VAR TOI = SUM(fact_box_score[toi_seconds_total])
RETURN DIVIDE(Pts * 3600, TOI)

// Zone Entry Success %
Zone Entry % = 
DIVIDE(
    SUM(fact_box_score[zone_entries_successful]),
    SUM(fact_box_score[zone_entries_attempted])
)
```

### WOWY Analysis

```dax
// With Player GF%
GF% With Player = 
CALCULATE(
    DIVIDE(SUM(fact_shifts[goals_for]), SUM(fact_shifts[goals_for]) + SUM(fact_shifts[goals_against])),
    fact_shift_players[player_id] = SELECTEDVALUE(dim_player[player_id])
)
```

---

# 10. ML & Future Ideas

## xG Model Architecture

```
INPUTS                          MODEL                    OUTPUT
───────                         ─────                    ──────
• Shot distance (ft)            
• Shot angle (deg)              ┌─────────────────┐
• Shot type (wrist/slap/etc)    │                 │      
• Time since last event   ───►  │ Logistic Reg /  │ ───► xG (0-1)
• Rebound flag                  │ XGBoost / NN    │
• Rush flag                     │                 │
• Shooter handedness            └─────────────────┘
• Strength state
• Score state
```

## Player Similarity Model

```python
# Concept: Compare beer league players to NHL archetypes
player_vector = [
    goals_per_60, assists_per_60, shots_per_60,
    cf_pct, zone_entry_pct, takeaways_per_60,
    giveaways_per_60, toi_pct, rating
]
similarity = cosine_similarity(player_vector, nhl_reference_vectors)
# Output: "Plays like a budget Cale Makar"
```

## Vision Pipeline (Future)

```
VIDEO INPUT ──► Frame Extraction ──► Pose Detection ──► Player Tracking
                                           │
                                           ▼
                                    Puck Detection ──► Event Classification
                                           │
                                           ▼
                                    XY Coordinates ──► Auto-Stats
```

## Research Priorities

1. **xG Model**: Train on tracked games (need ~500+ shots with outcomes)
2. **Line Optimizer**: Suggest optimal line combinations from WOWY data
3. **Opponent Tendency**: Pre-game scouting reports from historical data
4. **Auto-Highlight**: Generate player highlight reels from video timestamps

---

# 11. Known Issues & Notes

## Import Compatibility (Verified ✅)

| Game | File | Status | Events | Shifts |
|------|------|--------|--------|--------|
| 18955 | CSVs only | ⚠️ No tracking.xlsx | 0 | 0 |
| 18965 | 18965_tracking.xlsx | ✅ OK | 3,999 | 98 |
| 18969 | 18969_tracking.xlsx | ✅ OK | 3,596 | 98 |
| 18977 | 18977_tracking.xlsx | ✅ OK | 2,527 | 88 |
| 18981 | 18981_tracking.xlsx | ✅ OK | 2,428 | 106 |
| 18987 | 18987_tracking.xlsx | ✅ OK | 3,084 | 106 |
| 18991 | 18991_tracking.xlsx | ✅ OK | 4,000 | 78 |
| 18993 | _tracking.xlsx | ✅ OK | 456 | 98 |
| 19032 | 19032_tracking.xlsx | ✅ OK | 3,999 | 98 |

**Note**: Game 18993 has unusual filename `_tracking.xlsx` - tracker handles this correctly.

## Column Mapping Notes

The tracker's `getVal()` helper handles these variations:
- `event_type` vs `event_type_` vs `Type`
- `event_successful` vs `event_successful_`
- `team` vs `team_` vs `team_venue`
- `event_detail` vs `event_detail_` vs `detail_1`

## Data Quality Considerations

- Some games have minimal tracking (18993: 456 events) vs full (18987: 3,084 events)
- XY data is sparse - needs consistent tracking workflow
- Video timestamps require matching `_video_times.xlsx` file
- Rating context (2-6 scale) should be maintained in dim_player

## Contradictions Resolved

| Issue | Old Approach | New Approach |
|-------|--------------|--------------|
| Event order display | Chronological (oldest first) | DESC order (newest first) |
| Player XY slots | Fixed 3 slots | Unlimited (+XY button) |
| Display limits | 20 events, 10 shifts | 50 events, 30 shifts |
| Column names | Hardcoded | Flexible with fallbacks |

---

# 12. File Reference

## Documentation Files

| File | Purpose |
|------|---------|
| `MASTER_DOCUMENTATION.md` | This file - comprehensive reference |
| `README_FOR_LLM.txt` | LLM-specific navigation guide |
| `README_FOR_HUMANS.txt` | Human-readable project overview |
| `benchsight_stats_catalog_master_ultimate.csv` | Complete stats catalog (80+ stats) |
| `benchsight_tables_catalog.csv` | Table definitions and relationships |
| `BLB_Datamart_Overview.md` | Detailed datamart architecture |
| `benchsight_stats_catalog_v4.md` | Extended stats documentation |
| `benchsight_feature_backlog_and_roadmap.txt` | Full roadmap |
| `benchsight_commercial_summary.txt` | Commercial strategy |
| `ml_ideas.md` | Machine learning concepts |

## Key Project Files

| Location | Contents |
|----------|----------|
| `tracker/tracker_v16.html` | Latest tracker with all fixes |
| `data/BLB_Tables.xlsx` | Master dimension/fact source |
| `data/raw/games/*/` | 9 tracked game folders |
| `data/output/*.csv` | 40+ processed output files |
| `src/pipeline/` | ETL pipeline code |
| `powerbi/` | DAX formulas and viz guides |
| `checklists/` | Task tracking |

## Stats Catalog Quick Reference

See `benchsight_stats_catalog_master_ultimate.csv` for full definitions. Key columns:
- `stat_id`: Unique identifier (BS01, BS02, etc.)
- `name`: Full stat name
- `level`: Event / Shift / Game / Season / Player / Team / Line
- `category`: Shot / xG / Micro-Offense / Micro-Defense / Transition / Goalie
- `formula_or_logic`: Implementation-ready formula
- `implementation_status`: now / needs_xy / needs_tracking / needs_vision
- `requires_detailed_tracking`: Y/N

---

*Document Version: 2.0*
*Last Updated: December 26, 2025*
*Project: BenchSight Hockey Analytics Platform*
*Stats Defined: 80+*
*Tables Defined: 16*
*Games Tracked: 9*
