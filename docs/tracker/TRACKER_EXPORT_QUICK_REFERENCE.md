# Tracker Export Quick Reference

**Quick lookup for tracker export columns and requirements**

---

## File Structure

```
{game_id}_tracking.xlsx
├── metadata (1 row) - Game config
├── events (LONG format) - One row per player per event
├── shifts (1 row per shift) - Shift tracking
├── xy_puck (optional) - Puck coordinates
├── xy_player (optional) - Player coordinates
├── video (optional) - Video metadata
└── video_timing (optional) - Calibration
```

---

## Events Sheet - Minimum Required Columns

| Column | Type | Example | Notes |
|--------|------|---------|-------|
| `game_id` | str | "18969" | Game identifier |
| `period` | int | 1 | Period number |
| `event_index` | int | 1000 | Event counter (1000-based) |
| `event_start_min` | int | 18 | Minutes remaining |
| `event_start_sec` | int | 0 | Seconds remaining |
| `home_team` | str | "Platinum" | Home team name |
| `away_team` | str | "Velodrome" | Away team name |
| `event_type_code` | str | "Shot" | Event type |
| `event_type_id` | str | "ET0001" | Event type ID |
| `player_game_number` | int | 12 | Jersey number |
| `player_role` | str | "event_player_1" | Player role |

**Note:** Underscore columns (`event_index_flag_`, `event_start_min_`, etc.) are optional input hints that ETL drops after reading.

---

## Events Sheet - Full Column Count

**Total: 91 columns**

**Breakdown:**
- 23 input columns (with `_` suffix) - optional
- 10 core columns - required
- 8 event type columns - required
- 15 time columns - some required, most derived
- 6 player columns - required
- 16 XY puck columns - optional
- 8 XY player columns - optional
- 2 net XY columns - optional
- 3 assist/link columns - optional

---

## Shifts Sheet - Minimum Required Columns

| Column | Type | Example | Notes |
|--------|------|---------|-------|
| `shift_index` | int | 1 | Shift counter (1-based) |
| `Period` | int | 1 | Period number |
| `game_id` | str | "18969" | Game identifier |
| `home_team` | str | "Platinum" | Home team name |
| `away_team` | str | "Velodrome" | Away team name |
| `shift_start_min` | int | 18 | Minutes remaining |
| `shift_start_sec` | int | 0 | Seconds remaining |
| `shift_end_min` | int | 16 | Minutes remaining |
| `shift_end_sec` | int | 30 | Seconds remaining |
| `shift_start_type` | str | "Faceoff" | Start type |
| `shift_stop_type` | str | "Stoppage" | End type |
| `home_forward_1` | int | 12 | Jersey number |
| `home_forward_2` | int | 7 | Jersey number |
| `home_forward_3` | int | 19 | Jersey number |
| `home_defense_1` | int | 5 | Jersey number |
| `home_defense_2` | int | 22 | Jersey number |
| `home_goalie` | int | 35 | Jersey number |
| `away_forward_1` | int | 9 | Jersey number |
| `away_forward_2` | int | 11 | Jersey number |
| `away_forward_3` | int | 17 | Jersey number |
| `away_defense_1` | int | 2 | Jersey number |
| `away_defense_2` | int | 4 | Jersey number |
| `away_goalie` | int | 31 | Jersey number |

**Note:** DeadIce and Intermission shifts can have blank player columns.

---

## Shifts Sheet - Full Column Count

**Total: 66 columns**

**Breakdown:**
- 5 core columns - required
- 12 time columns - some required, most derived
- 14 player columns - required (unless DeadIce/Intermission)
- 11 strength/situation columns - derived
- 6 goal/plus-minus columns - derived
- 12 zone start/end columns - derived
- 5 puck location columns - optional

---

## Metadata Sheet

**Single row with:**
- `game_id` - Game identifier
- `home_team` - Home team name
- `away_team` - Away team name
- `period_length_minutes` - Period length (18 for NORAD)
- `home_attacks_right_p1` - 0 (left) or 1 (right)
- `export_timestamp` - ISO 8601 timestamp
- `tracker_version` - Version (e.g., "v28.0")
- `total_videos` - Video count

---

## XY Coordinate Sheets (Optional)

### xy_puck
- `event_index`, `game_id`, `period`
- `event_type`, `event_detail`
- `xy_slot` (sequence: 1, 2, 3...)
- `x`, `y`, `x_adjusted`, `y_adjusted`
- `is_xy_adjusted`, `needs_xy_adjustment`
- `is_start`, `is_stop`

### xy_player
- Same as xy_puck, plus:
- `player_number`, `player_name`, `player_role`

**XY Range:** X: -100 to 100, Y: -42.5 to 42.5

---

## Critical Rules

### Goal Counting
```
GOAL = event_type = 'Goal'
       AND event_detail = 'Goal_Scored'
       AND player_role = 'event_player_1'
```

**NOT a goal:** `event_type = 'Shot'` with `event_detail = 'Goal'` (shot attempt only)

### Player Roles
- **Event team:** `event_player_1` (primary), `event_player_2`, `event_player_3`, `event_player_4`, `event_player_5`
- **Opposing team:** `opp_player_1`, `opp_player_2`, `opp_player_3`, `opp_player_4`, `opp_player_5`

### Stat Counting
- Only count for `player_role = 'event_player_1'` to avoid duplicates
- For linked events, only count once per `linked_event_key`

### Assists
- **Primary:** `play_detail1` or `play_detail2` contains "AssistPrimary"
- **Secondary:** Contains "AssistSecondary"
- **Tertiary:** Contains "AssistTertiary" (NOT counted as official assist in hockey)

### Faceoffs
- **Winner:** `event_player_1` (player_role)
- **Loser:** `opp_player_1` (player_role)

### Micro-Stats Counting
For linked events (Pass > Zone Exit > Turnover):
- If `play_detail1 = 'ReceiverMissed'` appears in all 3 events
- Only count once for the entire `linked_event_key`

---

## Valid Values - Quick Lookup

### Event Types (23)
Shot, Save, Pass, Faceoff, Turnover, Zone_Entry_Exit, Possession, Penalty, Hit, Block, Stoppage, Goal, PenaltyShot_Shootout, LoosePuck, Rebound, DeadIce, Play, Timeout, Intermission, Clockstop, GameStart, GameEnd, Penalty_Delayed

### Common Event Details
- **Goals:** Goal_Scored
- **Shots:** Shot_OnNet, Shot_Missed, Shot_Blocked
- **Passes:** Pass_Completed, Pass_Intercepted, Pass_Missed, Pass_Deflected
- **Faceoffs:** Faceoff, Faceoff_AfterGoal, Faceoff_PeriodStart
- **Penalties:** Penalty_Minor, Penalty_Major, Penalty_Misconduct
- **Zone Entry/Exit:** ZE_Carried, ZE_Dumped, ZE_Passed, ZX_Carried, ZX_Cleared

### Common Play Details
- **Assists:** AssistPrimary, AssistSecondary, AssistTertiary
- **Offensive:** Deke, BeatWide, BeatMiddle, BeatSpeed, CrashNet
- **Defensive:** Backcheck, Forecheck, BoxOut, Contain
- **Passing:** ReceiverCompleted, ReceiverMissed, AttemptedPass
- **Shooting:** AttemptedShot, BlockedShot, AttemptedBlockedShot

### Shift Start/Stop Types
- **Start:** Faceoff, OnTheFly, PeriodStart, DeadIce, Intermission
- **Stop:** Faceoff, OnTheFly, Stoppage, PeriodEnd

---

## Time Calculation Logic

**Clock counts DOWN from period length:**
- Period 1 starts at 18:00, ends at 0:00
- `time_start_total_seconds` = `period_length_sec - (start_min * 60 + start_sec)`

**Example:** Period 1 (18:00 length), event at 15:30
- Remaining = 15*60 + 30 = 930 seconds
- Elapsed = 18*60 - 930 = 1080 - 930 = **150 seconds**

---

## ETL Processing Summary

### What ETL Needs (Minimum)
1. **events** sheet with required columns
2. **shifts** sheet with required columns
3. **metadata** sheet

### What ETL Derives
1. All `*_key` columns (event_id, shift_id, sequence_key, etc.)
2. All foreign key `*_id` columns (period_id, event_type_id, etc.)
3. `player_id` from jersey numbers via fact_gameroster lookup
4. All time calculations (if missing)
5. All flags (is_goal, is_shot, is_corsi, etc.)

### What ETL Drops
- All columns with `_` suffix (after using as input hints)
- Duplicate columns (Type, team, play_detail2)

---

## Common Export Scenarios

### Scenario 1: Full Export (91 events columns, 66 shifts columns)
Tracker exports all columns including XY, time calculations, and derived values.

### Scenario 2: Minimal Export (11 events columns, 23 shifts columns)
Tracker exports only required columns. ETL derives everything else.

### Scenario 3: No XY Export
Tracker exports events/shifts without XY coordinates. XY sheets are omitted.

**All scenarios work with ETL - it's designed to be robust!**

---

## Troubleshooting

### Events not loading?
- Check `event_index` is present and numeric
- Check `game_id`, `period`, `event_type_code`, `event_type_id` are present
- Check player_game_number is numeric

### Goals not counting?
- Verify `event_type = 'Goal'` AND `event_detail = 'Goal_Scored'`
- Check `player_role = 'event_player_1'` for the scorer
- Assists are in `play_detail1/2`, not as separate event_player_2/3

### Shifts not loading?
- Check `shift_index` is present and numeric
- Check player columns are numeric (jersey numbers)
- DeadIce/Intermission shifts can have blank player columns

### Player_id not linking?
- Check jersey numbers match fact_gameroster
- Verify `team_venue` (h/a) is correct
- Check player is in fact_gameroster for this game

---

## Quick Links

- **Full Specification:** `TRACKER_EXPORT_SPECIFICATION.md`
- **Tracker Logic:** `TRACKER_LOGIC_DOCUMENTATION.md`
- **Data Dictionary:** `../data/DATA_DICTIONARY.md`
- **ETL Loader:** `src/core/base_etl.py` (line 554)
- **Dimension Tables:** `data/raw/BLB_Tables.xlsx`
