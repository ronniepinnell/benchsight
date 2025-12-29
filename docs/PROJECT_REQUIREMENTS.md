# BenchSight Project Requirements
**Last Updated:** 2024-12-28
**Version:** 2.0

---

## 🎯 Project Overview

BenchSight is a comprehensive hockey analytics platform for the NORAD recreational hockey league. The system processes game tracking data from Excel files, transforms it through an ETL pipeline, and produces analytics-ready data for Power BI dashboards.

### Core Components
1. **Tracker App** - Data entry during games
2. **ETL Pipeline** - Data processing and transformation
3. **Data Warehouse** - Star schema storage
4. **Power BI Dashboard** - Visualization and reporting

---

## 📊 Data Pipeline Requirements

### Source Data
| Source | Description |
|--------|-------------|
| BLB_Tables.xlsx | Master dimensional tables (players, teams, etc.) |
| {game_id}_tracking.xlsx | Per-game tracking (events, shifts sheets) |
| NORAD Website | Official stats for cross-reference |

### ETL Process
1. Extract from Excel tracking files
2. Stage in PostgreSQL
3. Transform to star schema
4. Load to output CSVs / Power BI

### Output Tables
| Table | Description |
|-------|-------------|
| fact_events | Base event table |
| fact_events_player | Event-player (long format) |
| fact_shifts_player | Player shift data with logical shifts |
| fact_gameroster | Player-game stats from NORAD |
| fact_player_game_stats | Aggregated player stats (TO REBUILD) |
| dim_* | Dimensional tables |

---

## 📏 Stat Calculation Rules

### Scoring Stats
| Stat | Calculation |
|------|-------------|
| goals | event_type='Goal' AND player_role='event_team_player_1' |
| assists | play_detail LIKE 'Assist%' |
| points | goals + assists |

### Shot Stats
| Stat | Calculation |
|------|-------------|
| shots_total | event_type='Shot' AND player_role='event_team_player_1' |
| sog | Shots on net INCLUDING goals |
| shots_blocked | event_detail='Shot_Blocked' |
| shots_missed | event_detail LIKE '%Missed%' |
| shooting_pct | goals / shots * 100 |

### Passing Stats
| Stat | Calculation |
|------|-------------|
| pass_attempts | event_type='Pass' AND player_role='event_team_player_1' |
| pass_completed | event_detail='Pass_Completed' |
| pass_missed | event_detail='Pass_Missed' |
| pass_deflected | event_detail='Pass_Deflected' |
| pass_pct | pass_completed / pass_attempts * 100 (ignore nulls) |
| pass_targets | event_type='Pass' AND player_role='event_team_player_2' |
| pass_received | pass_targets with event_detail='Pass_Completed' |

### Faceoff Stats
| Stat | Calculation |
|------|-------------|
| fo_wins | event_type='Faceoff' AND player_role='event_team_player_1' |
| fo_losses | event_type='Faceoff' AND player_role='opp_team_player_1' |
| fo_total | fo_wins + fo_losses |
| fo_pct | fo_wins / fo_total * 100 |

### Zone Stats
| Stat | Calculation |
|------|-------------|
| zone_entries | event_detail LIKE '%Entry%' AND player_role='event_team_player_1' |
| zone_entries_controlled | Map via dim_zone_entry_type.control_level='controlled' |
| zone_entries_uncontrolled | Map via dim_zone_entry_type.control_level='uncontrolled' |
| zone_exits | event_detail LIKE '%Exit%' AND player_role='event_team_player_1' |
| zone_exits_controlled | Map via dim_zone_exit_type.control_level='controlled' |

### Turnover Stats
| Stat | Calculation |
|------|-------------|
| giveaways | event_detail LIKE '%Giveaway%' AND player_role='event_team_player_1' |
| takeaways | event_detail LIKE '%Takeaway%' AND player_role='event_team_player_1' |

### Possession Stats
| Stat | Calculation |
|------|-------------|
| puck_retrievals | event_type='Possession' AND event_detail='PuckRetrieval' |
| puck_recoveries | event_type='Possession' AND event_detail='PuckRecovery' |
| breakaways | event_type='Possession' AND event_detail='Breakaway' |
| loose_puck_battles | event_type='LoosePuck' (any role) |
| loose_puck_wins | event_type='LoosePuck' AND player_role='event_team_player_1' |
| loose_puck_losses | event_type='LoosePuck' AND player_role LIKE 'opp_team_player%' |

### Defensive Plays (from play_detail columns)
| Stat | Calculation |
|------|-------------|
| blocks | play_detail='BlockedShot' OR play_detail_2='BlockedShot' |
| stick_checks | play_detail='StickCheck' OR play_detail_2='StickCheck' |
| poke_checks | play_detail='PokeCheck' OR play_detail_2='PokeCheck' |
| in_shot_pass_lane | play_detail='InShotPassLane' OR play_detail_2='InShotPassLane' |
| backchecks | play_detail='Backcheck' OR play_detail_2='Backcheck' |

### Time on Ice Stats
| Stat | Calculation |
|------|-------------|
| shift_segments | COUNT from fact_shifts_player |
| logical_shifts | MAX(logical_shift_number) |
| toi_seconds | SUM(shift_duration) |
| toi_minutes | toi_seconds / 60 |
| stoppage_time | SUM(stoppage_time) |
| playing_toi_seconds | SUM(playing_duration) |
| avg_logical_shift | toi_seconds / logical_shifts |

### Plus/Minus Stats (from SHIFTS, not events)
| Stat | Calculation |
|------|-------------|
| plus_es | SUM(home_team_plus) from shifts where player on ice |
| minus_es | SUM(ABS(home_team_minus)) from shifts |
| plus_minus_es | plus_es - minus_es |
| plus_all | COUNT(Team Goal shifts) |
| minus_all | COUNT(Opp Goal shifts) |
| plus_minus_all | plus_all - minus_all |
| plus_en | COUNT(Team Goal AND opp_team_en=1) |
| minus_en | COUNT(Opp Goal AND team_en=1) |
| plus_minus_en | plus_en - minus_en |

### Corsi/Fenwick Stats (via shift_index matching)
| Stat | Calculation |
|------|-------------|
| corsi_for | Shot/Goal events during player shifts (same team) |
| corsi_against | Shot/Goal events during player shifts (opp team) |
| corsi | corsi_for - corsi_against |
| corsi_pct | corsi_for / (corsi_for + corsi_against) * 100 |
| fenwick_for | corsi_for - blocked_for |
| fenwick_against | corsi_against - blocked_against |
| fenwick | fenwick_for - fenwick_against |
| fenwick_pct | fenwick_for / (fenwick_for + fenwick_against) * 100 |

### Goalie Stats
| Stat | Calculation |
|------|-------------|
| saves | event_type='Save' AND player_role='event_team_player_1' |
| save_freeze | event_detail='Save_Freeze' |
| save_rebound | event_detail='Save_Rebound' |
| goals_against | event_type='Goal' AND player_role='opp_team_player_1' |
| shots_faced | saves + goals_against |
| save_pct | saves / shots_faced * 100 |
| gaa | (goals_against / toi_minutes) * 60 |
| rebounds | event_type='Rebound' |
| rebound_team_recovered | event_detail='Rebound_TeamRecovered' |
| rebound_opp_recovered | event_detail='Rebound_OppTeamRecovered' |

---

## 📐 Calculation Rules

### Success Rate Calculation
- Only count rows where event_successful is NOT blank
- Ignore blank/null values in denominator
- Example: 3 successful, 3 unsuccessful, 4 blank = 50% (not 30%)

### Linked Event Deduplication
- If events are linked (linked_event_index), player may appear multiple times
- Count play_detail only ONCE per linked event chain

### play_detail Column Handling
- play_detail and play_detail_2 are treated equally
- Any stat appearing in either column counts
- Same value in both columns for same event = count once

### Case Sensitivity
- team_venue may be "Home" or "home" - use case-insensitive comparison
- All string comparisons should handle case variations

### Goalie Plus/Minus
- Goalies do NOT receive plus/minus stats
- Identified via shifts where slot='goalie'

---

## 🔧 Shift Tracking

### Logical Shift Columns (fact_shifts_player)
| Column | Description |
|--------|-------------|
| logical_shift_number | Increments on shift_index gap OR period change |
| shift_segment | Segment number within logical shift (1,2,3...) |
| cumulative_shift_duration | Running total within logical shift |
| cumulative_playing_duration | Running playing time within logical shift |
| stoppage_time | Stoppage seconds during shift |
| playing_duration | shift_duration - stoppage_time |
| running_toi | Running total across ALL shifts |
| running_playing_toi | Running playing time across ALL shifts |

### Logical Shift Logic
- Consecutive shift_indices in same period = same logical shift
- Gap in shift_index = new logical shift
- Period change = new logical shift
- Use case: Identify extended shifts when team pinned in zone

---

## ✅ Automated Validation for New Games

### NORAD Cross-Check
| Check | Expected |
|-------|----------|
| Goals | SUM(goals) from tracking = NORAD website |
| Assists | SUM(assists) from tracking = NORAD website |
| PIM | SUM(penalties) * 3 = NORAD pim |

### Event Sanity Checks
| Check | Flag If |
|-------|---------|
| Total events | Outside 800-1200 per game |
| Faceoffs | Outside 50-80 per game |
| Goals without saves | Imbalanced |

### Shift Sanity Checks
- All shift durations > 0
- No overlapping shifts for same player
- Shifts exist in all periods played

### Suspicious Stat Flags
| Stat | Flag If |
|------|---------|
| TOI | > 30 min or = 0 |
| Goals | > 5 in single game |
| Assists | > 5 in single game |
| Faceoffs | > 40 for non-center |
| Giveaways | > 15 in single game |
| Pass % | < 30% or > 95% |
| Shot % | > 50% (on 5+ shots) |

---

## 🎮 Tracker App Requirements (Future)

### Data Quality Features
1. ML-powered edge case detection
2. Suspicious activity flags
3. Unit tests for data validation
4. Automated NORAD cross-reference

### shift_stop_type Requirements
- Must indicate which team scored
- Must indicate strength (5v5, PP, PK, etc.)
- Must flag empty net situations

### Suggested Improvements
- Real-time validation during tracking
- Pattern learning from corrections
- Anomaly detection for unusual events

---

## 📋 Request History

| Date | Request | Status |
|------|---------|--------|
| 2024-12-28 | Summarize all requests before proceeding | ✓ |
| 2024-12-28 | Create running request log | ✓ |
| 2024-12-28 | Systematic validation - data looks inaccurate | ✓ |
| 2024-12-28 | Create validation training dataset | ✓ |
| 2024-12-28 | Add logical shift tracking | ✓ |
| 2024-12-28 | Add stoppage time and playing TOI | ✓ |
| 2024-12-28 | Success rate ignores blanks | ✓ |
| 2024-12-28 | Handoff every 2 messages with context prompts | ✓ |
| 2024-12-28 | Systematic checks for new games | ✓ |
| 2024-12-28 | Tracker should do ML data quality checks | ✓ Documented |
| 2024-12-28 | Flag suspicious activity in tracker | ✓ Documented |
| 2024-12-28 | Unit tests for data validation | ✓ Documented |
| 2024-12-28 | Running project requirements list | ✓ |
| 2024-12-28 | Plus/minus from shifts | ✓ |
| 2024-12-28 | Empty net plus/minus columns | ✓ |
| 2024-12-28 | Corsi/Fenwick calculation | ✓ |
| 2024-12-28 | Full project wrap-up with comprehensive docs | ✓ |

---

## ⚠️ Known Issues

| Issue | Description | Status |
|-------|-------------|--------|
| Tipped goals | Scorer sometimes player_2 not player_1 | Open |
| Missing goals | Some games have fewer goals than NORAD | Open |
| Verbiage differences | Older games use different event_detail | Needs normalization |
| Games with 0 goals | 18965, 18991, 18993, 19032 incomplete | Open |

---

## 🗂️ Game-Specific Notes

| Game | Format | Notes |
|------|--------|-------|
| 18969 | Full | Complete tracking with play_details - REFERENCE |
| 18977 | Older | No play_details, verbiage may differ |
| 18965, 18991, 18993, 19032 | Unknown | May be incomplete |

---

*End of Project Requirements*
