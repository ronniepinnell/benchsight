# BenchSight Knowledge Log

## CRITICAL DOMAIN KNOWLEDGE - DO NOT FORGET

### Event Structure
- **event_player_1**: The player making the play (shooter scores goal, passer makes pass)
- **event_player_2**: Secondary player (first assist on goal, receiver of pass)
- **event_player_3**: Tertiary player (second assist)
- **event_successful**: 's' = success, 'u' = unsuccessful, blank = N/A

### Event Type Mapping (from actual data)
| ID | Name | Detail Examples |
|----|------|-----------------|
| ET0003 | Faceoff | Faceoff_GameStart, Faceoff_AfterStoppage |
| ET0006 | Goal | Goal_Scored |
| ET0009 | Pass | Pass_Completed, Pass_Missed, Pass_Intercepted |
| ET0015 | Save | Save_Freeze, Save_Rebound |
| ET0016 | Shot | Shot_OnNetSaved, Shot_Blocked, Shot_Missed, Shot_Goal |
| ET0019 | Turnover | Turnover_Giveaway, Turnover_Takeaway |
| ET0020 | Zone | Zone_Entry, Zone_Exit, Zone_Keepin |

### Rating System
- Player ratings are in dim_player
- Shift-level ratings should show: home_avg_rating, away_avg_rating, rating_diff
- Event-level should include opponent_avg_rating for context
- Goals against higher-rated opponents are more valuable

### Key Tables Structure
- dim_* = Dimension tables (lookups, reference data)
- fact_* = Fact tables (transactional data)
- All fact tables should include:
  - FK columns (e.g., event_type_id)
  - Readable names (e.g., event_type_name)
  - player_game_number where players referenced

### Excel Source Files
- BLB_Tables.xlsx: Master dimension data
- Game tracking files: Individual game events

### Net Location Coordinates
- Net is 6 feet wide (72") x 4 feet tall (48")
- Origin (0,0) at center of goal line
- Positive X = blocker side, Negative X = glove side
- Positive Y = up

## LESSONS LEARNED

### 2024-12-28: Stats Calculation Failure
- Problem: Goals showing 0 in stats despite 158 goals in events
- Root cause: Event type mapping was wrong (ET0002 vs ET0006)
- Fix: Mapped actual event types from data, not assumed values

### 2024-12-28: Missing Context
- Problem: Removed analytical columns during "cleanup"
- Fix: NEVER remove columns without explicit approval
- Rule: Always ADD, never REMOVE without discussion

## USER PREFERENCES

- Wants both FK IDs AND readable names in fact tables
- Wants player_game_number visible in all player references
- Prefers incremental improvement over complete rewrites
- Values domain expertise over just code output
