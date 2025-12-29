# BenchSight ETL - Complete Handoff Document
**Last Updated:** 2024-12-28
**Session:** Validation & ETL Rebuild  
**Stats Validated:** 115

---

## 🚀 Quick Start for Next Session

### Context Prompt (Copy This)

```
Pretend you are a senior data engineer specializing in hockey analytics. You are 
working on BenchSight, a comprehensive analytics platform for the NORAD recreational 
hockey league. You're helping me rebuild the ETL pipeline that processes game tracking 
data from Excel files into a star schema data warehouse.

KEY CONTEXT:
- We just completed a validation session where we validated 115+ stat calculations
- The validation log (docs/VALIDATION_LOG.tsv) is our "training data" for correct stat rules
- Critical bugs we fixed:
  * Goals: Use event_type='Goal' only (NOT Shot_Goal which double-counts)
  * Assists: Come from play_detail column (not event roles)
  * Plus/Minus: Calculated from SHIFTS not events
  * Faceoff winner = event_team_player_1, loser = opp_team_player_1
  * Success rates ignore blank values in denominator

BEFORE MAKING CHANGES:
1. Read docs/HANDOFF.md (this file)
2. Read docs/PROJECT_REQUIREMENTS.md for full requirements
3. Read docs/VALIDATION_LOG.tsv for correct stat calculation rules
4. Run scripts/validate_stats.py to verify calculations

The goal is to rebuild fact_player_game_stats using all validated counting rules.
```

### Key Files to Load First

| Priority | File | Purpose |
|----------|------|---------|
| 1 | `docs/HANDOFF.md` | This file - session context |
| 2 | `docs/PROJECT_REQUIREMENTS.md` | Full requirements & request history |
| 3 | `docs/VALIDATION_LOG.tsv` | 115 validated stat calculations |
| 4 | `scripts/validate_stats.py` | Validation test script |
| 5 | `docs/SCHEMA.md` | Database schema reference |

---

## 📊 What We Accomplished This Session

### Validation Training Set Created
- **115 stats validated** across 2 players and 2 games
- Player 1: Keegan Mantaro (game 18969) - full tracking with play_details
- Player 2: Hayden Smith (game 18977) - older format, no play_details
- Goalie: Wyatt Crandall (game 18969)

### Critical Bugs Fixed

| Bug | Root Cause | Solution |
|-----|------------|----------|
| Goal double-counting | Shot_Goal + Goal_Scored both counted | Use event_type='Goal' only |
| Missing assists | Looked in event roles | Use play_detail LIKE 'Assist%' |
| Wrong pass counts | Used role_number | Use player_role='event_team_player_1' |
| Faceoff wins/losses | event_successful is NaN | Winner=event_team_player_1, Loser=opp_team_player_1 |
| Avg shift wrong | Per segment, not logical | toi_seconds / logical_shifts |

### New Features Added

1. **Logical Shift Tracking** (fact_shifts_player)
   - logical_shift_number: Breaks on gap or period change
   - shift_segment: Segment within logical shift
   - stoppage_time, playing_duration
   - running_toi, running_playing_toi

2. **Plus/Minus Columns**
   - Even strength: plus_es, minus_es, plus_minus_es
   - All situations: plus_all, minus_all, plus_minus_all
   - Empty net: plus_en, minus_en, plus_minus_en

3. **Corsi/Fenwick**
   - Calculated via shift_index matching
   - CF, CA, Corsi, CF%
   - FF, FA, Fenwick, FF%

---

## 📋 Validated Counting Rules (Quick Reference)

### Scoring
| Stat | Filter |
|------|--------|
| Goals | event_type='Goal' AND player_role='event_team_player_1' |
| Assists | play_detail LIKE 'Assist%' |
| Points | goals + assists |

### Shots
| Stat | Filter |
|------|--------|
| Shots Total | event_type='Shot' AND player_role='event_team_player_1' |
| SOG | Includes goals (shots that reached net) |
| Shots Blocked | event_detail='Shot_Blocked' |
| Shots Missed | event_detail LIKE '%Missed%' |

### Passing
| Stat | Filter |
|------|--------|
| Pass Attempts | event_type='Pass' AND player_role='event_team_player_1' |
| Pass Completed | event_detail='Pass_Completed' |
| Pass Targets (received) | event_type='Pass' AND player_role='event_team_player_2' |

### Faceoffs
| Stat | Filter |
|------|--------|
| FO Wins | event_type='Faceoff' AND player_role='event_team_player_1' |
| FO Losses | event_type='Faceoff' AND player_role='opp_team_player_1' |

### Zone Play
| Stat | Filter |
|------|--------|
| Zone Entries | event_detail LIKE '%Entry%' AND player_role='event_team_player_1' |
| Controlled Entries | Map event_detail_2 via dim_zone_entry_type.control_level |
| Zone Exits | event_detail LIKE '%Exit%' AND player_role='event_team_player_1' |

### Turnovers & Possession
| Stat | Filter |
|------|--------|
| Giveaways | event_detail LIKE '%Giveaway%' |
| Takeaways | event_detail LIKE '%Takeaway%' |
| Loose Puck Win | event_type='LoosePuck' AND player_role='event_team_player_1' |
| Loose Puck Loss | event_type='LoosePuck' AND player_role LIKE 'opp_team_player%' |

### Defensive Plays (from play_detail)
| Stat | Filter |
|------|--------|
| Blocks | play_detail='BlockedShot' OR play_detail_2='BlockedShot' |
| Stick Checks | play_detail='StickCheck' OR play_detail_2='StickCheck' |
| Poke Checks | play_detail='PokeCheck' OR play_detail_2='PokeCheck' |

### Goalie Stats
| Stat | Filter |
|------|--------|
| Saves | event_type='Save' AND player_role='event_team_player_1' |
| Goals Against | event_type='Goal' AND player_role='opp_team_player_1' |
| Rebounds | event_type='Rebound' |
| Shots Faced | saves + goals_against |
| Save % | saves / shots_faced * 100 |
| GAA | (goals_against / toi_minutes) * 60 |

### Plus/Minus (from SHIFTS)
| Stat | Source |
|------|--------|
| plus_es | SUM(home_team_plus) from shifts |
| minus_es | SUM(ABS(home_team_minus)) from shifts |
| plus_all | COUNT(Team Goal shifts) |
| minus_all | COUNT(Opp Goal shifts) |
| plus_en | Team Goal AND opp_team_en=1 |
| minus_en | Opp Goal AND team_en=1 |

### Corsi/Fenwick (via shift_index)
| Stat | Calculation |
|------|-------------|
| CF | Shot/Goal events during player shifts (same team) |
| CA | Shot/Goal events during player shifts (opp team) |
| FF | CF minus blocked shots |
| FA | CA minus blocked shots |

### Important Rules
1. **Success Rate**: Ignore blank/null values in denominator
2. **play_detail/play_detail_2**: Treat equally - count from either column
3. **Linked Events**: Count play_details only ONCE per linked event chain
4. **Goalies**: Do NOT receive plus/minus stats
5. **Case Sensitivity**: team_venue may be "Home" or "home" - use case-insensitive compare

---

## 📁 Project Structure

```
benchsight_github/
├── docs/                          # Documentation
│   ├── HANDOFF.md                 # This file - session handoff
│   ├── PROJECT_REQUIREMENTS.md    # Full requirements & history
│   ├── VALIDATION_LOG.tsv         # 115 validated stats (training data)
│   ├── REQUEST_LOG.md             # Running request log
│   ├── SCHEMA.md                  # Database schema
│   ├── DATA_DICTIONARY.md         # Column definitions
│   └── diagrams/                  # Visual diagrams
│
├── scripts/                       # Utility scripts
│   ├── validate_stats.py          # Stat validation tests
│   └── verify_delivery.py         # Package verification
│
├── src/                           # Source code
│   ├── etl/                       # ETL modules
│   └── utils/                     # Utilities
│
├── data/
│   ├── raw/                       # Raw tracking data
│   │   ├── BLB_Tables.xlsx        # Dimensional tables
│   │   └── games/                 # Game tracking files
│   │       ├── 18969/             # Full tracking (reference)
│   │       ├── 18977/             # Older format
│   │       └── ...
│   └── output/                    # Processed output
│       ├── fact_events.csv
│       ├── fact_events_player.csv
│       ├── fact_shifts_player.csv
│       ├── fact_gameroster.csv
│       └── dim_*.csv
│
├── config/                        # Configuration
├── dashboard/                     # Dashboard files
├── sql/                           # SQL scripts
├── tests/                         # Test files
└── tracker/                       # Tracker app files
```

---

## 🎯 Roadmap

### Short Term (Next Session)
- [ ] Rebuild `fact_player_game_stats` with all validated rules
- [ ] Apply validation rules to all 8 tracked games
- [ ] Run automated NORAD cross-reference
- [ ] Build `fact_goalie_game_stats`
- [ ] Create automated validation script for new games

### Mid Term (1-2 Sessions)
- [ ] Build normalization mapping for older game verbiage
- [ ] Build `fact_team_game_stats` aggregations
- [ ] Create sequences/plays from tracking data
- [ ] Integrate with Power BI dashboard
- [ ] Add xG model integration

### Long Term (Future)
- [ ] Tracker app with ML data quality checks
- [ ] Real-time validation during tracking
- [ ] Rush type detection (odd-man, even strength)
- [ ] Cycle detection
- [ ] Event chains (entry → shot → goal timing)
- [ ] Video URL integration with coordinates

---

## ⚠️ Known Issues

| Issue | Description | Status |
|-------|-------------|--------|
| Tipped goals | Scorer sometimes player_2 not player_1 | Open |
| Missing goals | Some games have fewer goals than NORAD | Open - data completeness |
| Verbiage differences | Older games use different event_detail values | Needs normalization |
| Games with 0 goals | 18965, 18991, 18993, 19032 may be incomplete | Open |
| 1 goal mismatch | Hayden Smith: NORAD=2, tracking=1 | Data completeness |

---

## 🎮 Game-Specific Notes

| Game | Format | Notes |
|------|--------|-------|
| 18969 | Full | Complete tracking with play_details - USE AS REFERENCE |
| 18977 | Older | No play_details, verbiage may differ |
| 18965, 18991, 18993, 19032 | Unknown | May be incomplete (0 goals in tracking) |

---

## 🔧 Tracker App Requirements (Future)

### Data Quality Features
1. **ML-powered edge case detection**
   - Learn from historical corrections
   - Flag unusual patterns during tracking
   - Prompt user for potential issues

2. **Suspicious activity flags**
   - Stats outside normal ranges
   - Missing expected events
   - Inconsistent player roles

3. **Unit tests for validation**
   - Event sequence logic
   - Player counts per event type
   - Shift continuity
   - NORAD cross-reference

4. **shift_stop_type requirements**
   - Must clarify which team scored
   - Must indicate strength (5v5, PP, etc.)
   - Must flag empty net situations

### Suspicious Stat Thresholds
| Stat | Flag If |
|------|---------|
| TOI | > 30 min or = 0 |
| Goals | > 5 in single game |
| Faceoffs | > 40 for non-center |
| Pass % | < 30% or > 95% |
| Shot % | > 50% (on 5+ shots) |

---

## 📦 Zip Package Contents

Each delivery should include:

```
benchsight_[date]_[description].zip
├── docs/                    # All documentation
├── scripts/                 # All scripts
├── src/                     # Source code
├── data/output/             # Processed CSV files
├── config/                  # Configuration
├── sql/                     # SQL scripts
├── tests/                   # Test files
└── README.md                # Quick start
```

**Before packaging, run:**
```bash
python scripts/verify_delivery.py
python scripts/validate_stats.py
```

---

## 📞 Quick Reference

### Event Types
```
Pass, Zone_Entry_Exit, Possession, Turnover, Shot, Save, Faceoff, 
Stoppage, DeadIce, Play, Rebound, Goal, LoosePuck, Penalty, 
GameStart, Intermission, Penalty_Delayed, GameEnd, Timeout, Clockstop
```

### Player Roles
```
event_team_player_1  - Primary actor (shooter, passer, FO winner)
event_team_player_2  - Secondary actor (pass target, A1)
event_team_player_3  - Tertiary actor (A2)
opp_team_player_1    - Primary opponent (blocker, FO loser)
opp_team_player_2    - Secondary opponent
```

### Tracked Games
```
18965, 18969, 18977, 18981, 18987, 18991, 18993, 19032
```

---

*End of Handoff Document*
