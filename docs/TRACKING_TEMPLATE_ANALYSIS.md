# BenchSight Tracking Template Documentation

**Version:** 16.08  
**Updated:** January 8, 2026


**File:** `_tracking.xlsx`  
**Purpose:** Manual game event and shift tracking from video  
**Generated:** 2026-01-07

---

## Table of Contents

1. [Sheet Overview](#sheet-overview)
2. [Events Sheet - Deep Dive](#events-sheet---deep-dive)
3. [Shifts Sheet - Deep Dive](#shifts-sheet---deep-dive)
4. [Lists Sheet - Data Validation Sources](#lists-sheet---data-validation-sources)
5. [Named Ranges](#named-ranges)
6. [Cross-Sheet Interactions](#cross-sheet-interactions)
7. [Formula Logic Analysis](#formula-logic-analysis)
8. [Data Entry Workflow](#data-entry-workflow)

---

## Sheet Overview

| Sheet | Rows | Cols | Purpose |
|-------|------|------|---------|
| **events** | 860 | 72 | Main event tracking - shots, passes, goals, etc. |
| **shifts** | 202 | 55 | Line change tracking with player assignments |
| **Lists** | 139 | 69 | Dropdown validation lists for all event types |
| **Rules** | 147 | 73 | Event type definitions and relationships |
| **game_rosters** | 57 | 54 | Player roster data (linked from external BLB_Tables.xlsx) |
| **examples** | 66 | 51 | Sample tracking data |
| **Sheet1** | 72 | 3 | Misc |

---

## Events Sheet - Deep Dive

### Column Classification

The events sheet has **72 columns** divided into:

#### INPUT COLUMNS (User enters these - suffix `_`)

| Col | Header | Purpose | Data Validation |
|-----|--------|---------|-----------------|
| A | `event_index_flag_` | Flag to create new event (1 or blank) | Manual |
| B | `sequence_index_flag_` | Flag for new sequence | Manual |
| C | `play_index_flag_` | Flag for new play | Manual |
| D | `linked_event_index_flag_` | Flag for linked event | Manual |
| E | `event_start_min_` | Event start minute (0-20) | Manual |
| F | `event_start_sec_` | Event start second (0-59) | Manual |
| G | `event_end_min_` | Event end minute | Manual |
| H | `event_end_sec_` | Event end second | Manual |
| **I** | **`player_game_number_`** | **Jersey number of player** | Manual |
| **J** | **`event_team_zone_`** | **Zone: o/d/n** | Manual: o=offensive, d=defensive, n=neutral |
| **K** | **`event_type_`** | **Primary event type** | Dropdown: `EventType` named range |
| **L** | **`event_detail_`** | **Event detail/subtype** | Cascading dropdown based on K |
| **M** | **`event_detail_2_`** | **Secondary detail (shot type, etc.)** | Cascading dropdown based on L |
| N | `event_successful_` | Success flag (s/u) | Formula-calculated |
| O | `play_detail1_` | Play detail | Dropdown |
| P | `play_detail2_` | Secondary play detail | Dropdown |
| Q | `play_detail_successful_` | Play success | Manual |
| R | `pressured_pressurer_` | Pressure indicator | Manual |
| S | `event_index_` | Manual event index override | Manual |
| T | `linked_event_index_` | Manual linked event index | Manual |
| U | `sequence_index_` | Manual sequence index | Manual |
| V | `play_index_` | Manual play index | Manual |
| **W** | **`team_`** | **Team: h=home, a=away** | Manual: h/a |
| X | `player_game_number` | Duplicate of I | Reference |
| Y | `role_abrev_binary_` | Role: 1=event team, 2=opp, x=system | Manual |

#### CALCULATED COLUMNS (Formulas - no suffix)

| Col | Header | Formula Logic |
|-----|--------|---------------|
| Z | `period` | `=IF(K="Intermission",Z_prev+1,Z_prev)` - Increments on intermission |
| AA | `event_index` | `=S+1000` - Adds 1000 offset to manual index |
| AB | `linked_event_index` | `=IF(T<>"",9000+T,"")` - Adds 9000 offset |
| AC | `tracking_event_index` | `=IF(AB<>"",AB,S+1000)` - Uses linked or event index |
| AD | `event_start_min` | Copied from E or carried forward |
| AE | `event_start_sec` | Copied from F or carried forward |
| AF | `event_end_min` | `=IF(G<>"",G,IF(S=S_prev,AF_prev,""))` - Carries forward within event |
| AG | `event_end_sec` | Same pattern as AF |
| AH | `role_abrev` | `=IF(Y="x","",IF(Y=1,"e","o"))` - Converts binary to e/o |
| AI | `event_team_zone2_` | Zone with carryforward |
| AJ | `event_team_zone` | Zone with carryforward |
| AK | `home_team_zone_` | **Complex zone flip logic** (see below) |
| AL | `away_team_zone_` | Inverse of home zone |
| AM | `team_venue_` | "Home" or "Away" from abrev |
| AN | `team_venue_abv_` | h/a with carryforward |
| AO | `home_team_zone` | Zone with carryforward |
| AP | `away_team_zone` | Zone with carryforward |
| AQ | `team_venue` | Full name with carryforward |
| AR | `team_venue_abv` | Abbreviation with carryforward |
| AS | `side_of_puck` | **"Offensive"/"Defensive" based on role and event type** |
| AT | `sequence_index` | `=IF(U<>"",U+5000,"")` - Adds 5000 offset |
| AU | `play_index` | `=IF(V<>"",V+6000,"")` - Adds 6000 offset |
| AV | `play_detail1` | **Array formula - FILTER lookup for linked events** |
| AW | `play_detail_2` | Array formula |
| AX | `play_detail_successful` | Array formula |
| AY | `pressured_pressurer` | Array formula |
| AZ | `zone_change_index` | Manual/calculated |
| BA | `game_id` | From game setup |
| BB | `home_team` | From game setup |
| BC | `away_team` | From game setup |
| BD | `Type` | `=IF(K<>"",K,IF(S=S_prev,K,""))` - event_type with carryforward |
| BE | `event_detail` | Calculated detail |
| BF | `event_detail_2` | Calculated detail2 |
| BG | `event_successful` | Calculated success |
| BH | `shift_index` | Link to shifts sheet |
| BI | `duration` | Event duration in seconds |
| BJ | `time_start_total_seconds` | Start time as total seconds |
| BK | `time_end_total_seconds` | End time as total seconds |
| BL | `running_intermission_duration` | Accumulated intermission time |
| BM | `period_start_total_running_seconds` | Period start in video time |
| BN | `running_video_time` | Current video timestamp |
| BO | `event_running_start` | `=IF(BN<5,0,BN-5)` - Video start minus 5 sec buffer |
| BP | `event_running_end` | `=BO+BI+5` - End plus 5 sec buffer |
| BQ | `player_role` | Full role name |
| BR | `role_number` | Numeric role |
| BS | `player_id` | **VLOOKUP to game_rosters** |
| BT | `player_team` | **Derived from venue + role** |

### Key Formula Details

#### Event Index Auto-Increment (S column)
```excel
=IF(A3=1,MAX($S$2:$S2)+1,IF($I3<>"",$S2,""))
```
- If flag A=1: Creates new event with next index
- If jersey number entered: Carries forward same event index (multi-player event)
- Otherwise: Blank

#### Zone Flip Logic (AK column - home_team_zone_)
```excel
=IF($W2="",
    "",
    IF($AI2="",
        "",
        IF($W2="h",
            $AI2,
            IF($AI2="n",
                "n",
                IF(AND($W2="a",$AI2="d"),
                    "o",
                    IF(AND($W2="a",$AI2="o"),
                        "d"
                    )
                )
            )
        )
    )
)
```
- If team is home (h): Zone is as entered
- If team is away (a): Zone is flipped (o↔d, n stays n)

#### Side of Puck Logic (AS column)
```excel
=IF(AND(AH2="e",OR(BD2="Save",BE2="Turnover_Takeaway",BE2="Play_Defensive")),
    "Defensive",
    IF(AND(AH2="o",OR(BD2="Save",BE2="Turnover_Takeaway",BE2="Play_Defensive")),
        "Offensive",
        IF(OR(BD2="Deadice",BD2="Stoppage",BD2="Intermission"),
            "",
            IF(AH2="e",
                "Offensive",
                IF(AH2="o",
                    "Defensive",
                    ""
                )
            )
        )
    )
)
```
- Determines if player is on offensive or defensive side of puck
- Considers event type (saves, takeaways are defensive)
- Uses role (e=event team, o=opposing)

#### Event Success Auto-Calculation (N column)
```excel
=IF(K="",
    "",
    IF(K="Goal",
        "s",
        IF(AND(K="Zone_Entry_Exit",OR(SEARCH("fail",L),SEARCH("FromExitClear",M),SEARCH("miss",M))),
            "u",
            IF(AND(K="Zone_Entry_Exit",...),
                "s",
                IF(AND(OR(K="Shot",K="Pass"),OR(SEARCH("complete",L),SEARCH("goal",L),SEARCH("OnNet",L))),
                    "s",
                    IF(L="Turnover_Giveaway",
                        "u",
                        IF(AND(OR(K="Shot",K="Pass"),...),
                            "u",
                            ""
                        )
                    )
                )
            )
        )
    )
)
```
- Goals always successful ("s")
- Zone entries: Check for "fail" in detail → unsuccessful
- Shots/Passes: Check for "complete", "goal", "OnNet" → successful
- Giveaways always unsuccessful ("u")

#### Player ID Lookup (BS column)
```excel
=IFERROR(VLOOKUP(BA2&BT2&I2,game_rosters!U:W,3,FALSE),"")
```
- Concatenates: game_id + player_team + jersey_number
- Looks up in game_rosters column U (composite key)
- Returns player_id from column W

#### Player Team Derivation (BT column)
```excel
=IF(AQ2="",
    "",
    IF(AND(AQ2="Away",AH2="e"),
        BC2,
        IF(AND(AQ2="Home",AH2="e"),
            BB2,
            IF(AND(AQ2="Away",AH2="o"),
                BB2,
                IF(AND(AQ2="Home",AH2="o"),
                    BC2
                )
            )
        )
    )
)
```
- If venue=Away and role=event team (e): away_team name
- If venue=Home and role=event team (e): home_team name
- If venue=Away and role=opposing (o): home_team name
- If venue=Home and role=opposing (o): away_team name

---

## Shifts Sheet - Deep Dive

### Column Classification

#### INPUT COLUMNS (User enters these)

| Col | Header | Purpose |
|-----|--------|---------|
| A | `shift_index` | Sequential shift number |
| B | `Period` | Period number |
| C | `shift_start_min` | Start minute (0-20) |
| D | `shift_start_sec` | Start second (0-59) |
| E | `shift_end_min` | End minute |
| F | `shift_end_sec` | End second |
| G | `shift_start_type` | How shift started (dropdown) |
| H | `shift_stop_type` | How shift ended (dropdown) |
| I-N | `home_forward_1` thru `home_xtra` | Home team skater jersey numbers |
| O | `home_goalie` | Home goalie jersey number |
| P-U | `away_forward_1` thru `away_xtra` | Away team skater jersey numbers |
| V | `away_goalie` | Away goalie jersey number |
| X-AC | Zone time tracking | Zone start/end tracking |

#### CALCULATED COLUMNS

| Col | Header | Formula |
|-----|--------|---------|
| W | `stoppage_time` | SUMIFS for DeadIce/Timeout events during shift |
| AD | `game_id` | `=events!BA2` |
| AE | `home_team` | `=events!BB2` |
| AF | `away_team` | `=events!BC2` |
| AG | `shift_start_total_seconds` | `=(C*60)+D` |
| AH | `shift_end_total_seconds` | `=(E*60)+F` |
| AI | `shift_duration` | `=ROUND(AG-AH,0)` |
| AJ | `home_team_strength` | `=COUNTIF(I:N,">0")` - Count non-empty skaters |
| AK | `away_team_strength` | `=COUNTIF(P:U,">0")` |
| AL | `home_team_en` | `=IF(O="",1,0)` - Empty net flag |
| AM | `away_team_en` | `=IF(V="",1,0)` |
| AN | `home_team_pk` | Penalty kill flag |
| AO | `home_team_pp` | Power play flag |
| AP | `away_team_pp` | Power play flag |
| AQ | `away_team_pk` | Penalty kill flag |
| AR | `situation` | "Full Strength", "Home PowerPlay", etc. |
| AS | `strength` | "5v5", "5v4 Home EN", etc. |
| AT | `home_goals` | Running home goal count |
| AU | `away_goals` | Running away goal count |
| AV-AY | Plus/Minus | Goal differential flags |
| AZ | `period_start_total_running_seconds` | VLOOKUP to events |
| BA | `running_video_time` | Video timestamp |
| BB | `shift_start_running_time` | `=IF(BA<5,0,BA-5)` |
| BC | `shift_end_running_time` | `=BB+AI+3` |

### Key Formula Details

#### Stoppage Time Calculation (W column)
```excel
=SUMIFS(events!BI:BI,events!K:K,"=DeadIce",events!BJ:BJ,"<="&shifts!AG2,events!BK:BK,">"&shifts!AH2,events!Z:Z,"="&shifts!B3)
+SUMIFS(events!BI:BI,events!K:K,"=Timeout",events!BJ:BJ,"<="&shifts!AG2,events!BK:BK,">"&shifts!AH2,events!Z:Z,"="&shifts!B3)
```
- Sums duration of DeadIce and Timeout events
- Within the time range of current shift
- Within same period

#### Strength Calculation (AJ column)
```excel
=COUNTIF(I2:N2,">0")
```
- Counts non-empty player cells
- Result: Number of skaters (typically 5, fewer during penalties)

#### Situation Logic (AR column)
```excel
=IF(AND(AJ2=5,AK2=5,AL2=0,AM2=0),
    "Full Strength",
    IF(AP2=1,
        "Away PowerPlay",
        IF(AO2=1,
            "Home PowerPlay",
            IF(AL2=1,
                "Home EmptyNet",
                IF(AM2=1,
                    "Away EmptyNet",
                    ""
                )
            )
        )
    )
)
```

#### Strength String (AS column)
```excel
=IF(AND(AL2=0,AM2=0),
    AJ2&"v"&AK2,
    IF(AL2=1,
        AJ2&"v"&AK2&" Home EN",
        IF(AM2=1,
            AJ2&"v"&AK2&" Away EN",
            ""
        )
    )
)
```
- Generates strings like "5v5", "5v4", "4v4 Home EN"

---

## Lists Sheet - Data Validation Sources

### Event Type Hierarchy

The dropdowns use a **cascading hierarchy**:

```
event_type_ (K) → event_detail_ (L) → event_detail_2_ (M)
```

#### Level 1: Event Types (Column A)
| EventType |
|-----------|
| Faceoff |
| Shot |
| Pass |
| Goal |
| Turnover |
| Zone_Entry_Exit |
| Penalty |
| PenaltyShot_Shootout |
| Stoppage |
| Hit |
| Possession |
| LoosePuck |
| Save |
| TeamPossessionChange |
| Rebound |
| DeadIce |
| Play |
| Timeout |
| Intermission |
| GameStart |
| GameEnd |

#### Level 2: Event Details (varies by type)

**Shot details:**
- Shot_OnNetSaved
- Shot_Missed
- Shot_Blocked
- Shot_BlockedSameTeam
- Shot_Deflected
- Shot_DeflectedOnNetSaved
- Shot_Tipped
- Shot_TippedOnNetSaved

**Pass details:**
- Pass_Completed
- Pass_Missed
- Pass_Deflected
- Pass_Intercepted

**Goal details:**
- Goal_Scored
- Goal_Shootout
- Goal_PenaltyShot

**Turnover details:**
- Turnover_Giveaway
- Turnover_Takeaway

**Zone Entry/Exit details:**
- Zone_Entry
- Zone_Exit
- Zone_Keepin
- Zone_Entryfailed
- Zone_ExitFailed
- Zone_KeepinFailed

#### Level 3: Secondary Details (shot types, pass types, etc.)

**Shot types (for Shot_OnNetSaved, etc.):**
- Shot-Wrist
- Shot-Slap
- Shot-Backhand
- Shot-Tip
- Shot-Snap
- Shot-WrapAround
- Shot-Bat
- Shot-Cradle
- Shot-Poke

**Pass types (for Pass_Completed, etc.):**
- Pass-Stretch
- Pass-Rim/Wrap
- Pass-Backhand
- Pass-Forehand
- Pass-Bank
- Pass-Dump
- Pass-Tipped
- Pass-Lob

**Zone Entry types:**
- ZoneEntry-Rush
- ZoneEntry-Pass
- ZoneEntry-DumpIn
- ZoneEntry-Chip
- ZoneEntry-FromExitClear
- ZoneEntry-PassMiss/Misplay
- ZoneEntry-OppTeam
- ZoneEntry-Lob

**Zone Exit types:**
- ZoneExit-Rush
- ZoneExit-Pass
- ZoneExit-Clear
- ZoneExit-Chip
- ZoneExit-PassMiss/Misplay
- ZoneExit-OppTeam
- ZoneExit-Lob
- ZoneExit-CausedTurnover

---

## Named Ranges

The workbook uses **59 named ranges** for data validation:

| Named Range | References | Purpose |
|-------------|------------|---------|
| EventType | Lists!$A$2:$A$16 | Main event type dropdown |
| Shot | Lists!$H$2:$H$1048576 | Shot detail options |
| Pass | Lists!$I$2:$I$1048576 | Pass detail options |
| Goal | Lists!$J$2:$J$1048576 | Goal detail options |
| Turnover | Lists!$K$2:$K$1048576 | Turnover detail options |
| Zone_Entry_Exit | Lists!$L$2:$L$1048576 | Zone entry/exit options |
| Faceoff | Lists!$G$2:$G$1048576 | Faceoff detail options |
| Save | Lists!$Q$2:$Q$1048576 | Save detail options |
| Stoppage | Lists!$O$2:$O$1048576 | Stoppage detail options |
| Shot_OnNetSaved | Lists!$AO$2:$AO$1048576 | Shot type when saved |
| Shot_Missed | Lists!$AP$2:$AP$1048576 | Shot type when missed |
| Shot_Blocked | Lists!$AQ$2:$AQ$1048576 | Shot type when blocked |
| Goal_Scored | Lists!$AY$2:$AY$1048576 | Goal type details |
| Pass_Completed | Lists!$R$2:$R$1048576 | Pass type when completed |
| Pass_Missed | Lists!$S$2:$S$1048576 | Pass type when missed |
| Zone_Entry | Lists!$X$2:$X$1048576 | Zone entry method |
| Zone_Exit | Lists!$Y$2:$Y$1048576 | Zone exit method |
| Turnover_Giveaway | Lists!$V$2:$V$1048576 | Giveaway type |
| Turnover_Takeaway | Lists!$W$2:$W$1048576 | Takeaway type |
| ... | ... | (59 total) |

---

## Cross-Sheet Interactions

### Events ↔ Shifts

1. **shift_index lookup**: Events can reference which shift they occurred during
2. **Stoppage time**: Shifts calculate total stoppage time from DeadIce/Timeout events
3. **Period sync**: Both sheets track period number

### Events ↔ game_rosters

1. **Player ID lookup**: `=VLOOKUP(game_id&team&jersey, game_rosters!U:W, 3, FALSE)`
2. **Roster filter**: game_rosters is populated via FILTER from external BLB_Tables.xlsx

### Events ↔ Lists

1. **Primary dropdown**: event_type_ uses `EventType` named range
2. **Cascading dropdowns**: event_detail_ uses INDIRECT to reference named range matching event_type_
3. **Secondary details**: event_detail_2_ similarly cascades

---

## Formula Logic Analysis

### Key Patterns

#### 1. Carryforward Pattern
Many columns use this pattern to carry values forward within the same event:
```excel
=IF(input<>"", input, IF(current_event=previous_event, previous_value, ""))
```

#### 2. Index Offset Pattern
Different index types have different offsets to ensure uniqueness:
- event_index: +1000
- linked_event_index: +9000
- sequence_index: +5000
- play_index: +6000

#### 3. Array Formula Pattern (Linked Events)
```excel
=IFERROR(
    IF(O2<>"",
        O2,
        IF(OR($S2="",$T2=""),
            "",
            IF($T2<>"",
                FILTER(O:O, ($BT:$BT=$BT2)*($I:$I=$I2)*($T:$T=$T2)*($S:$S=MINIFS($S:$S,$T:$T,"="&$T2)),
                "")
            )
        )
    ),
    IF(O2="","","")
)&""
```
This copies play details from the primary event to linked events.

#### 4. Zone Perspective Flip
When tracking from away team perspective, zones are flipped:
- Away team in "o" (offensive) zone → Home team in "d" (defensive) zone

---

## Data Entry Workflow

### Typical Event Entry Sequence

1. **Set period start** (usually GameStart or PeriodStart event)
2. **For each event:**
   - Enter `1` in column A to create new event
   - Enter jersey number (I)
   - Enter team (W): h or a
   - Enter zone (J): o, d, or n
   - Select event type (K) from dropdown
   - Select event detail (L) from cascading dropdown
   - Select secondary detail (M) if applicable
   - Formulas auto-calculate: event_index, player_id, success, zones

3. **For multi-player events (e.g., goal with assists):**
   - First row: Scorer with event_index_flag_=1
   - Second row: Primary assist (same event_index, different jersey)
   - Third row: Secondary assist (same event_index, different jersey)
   - All share same event_index via carryforward

4. **Linked events:**
   - Enter linked_event_index_ (T) to reference another event
   - Array formulas copy play details from primary event

### Shift Entry Sequence

1. **For each line change:**
   - Enter shift_index (A)
   - Enter period (B)
   - Enter start/end times (C-F)
   - Enter start/stop types (G-H)
   - Enter all player jersey numbers (I-V)
   - Formulas auto-calculate: duration, strength, situation

---

## Summary of Auto-Calculated Values

### Events Sheet - Automatic

| Value | Source |
|-------|--------|
| period | Increments on Intermission |
| event_index | From flag + MAX |
| player_id | VLOOKUP from roster |
| player_team | Derived from venue + role |
| event_successful | Based on event type/detail patterns |
| home/away zones | Flipped based on team perspective |
| side_of_puck | Offensive/Defensive based on role |
| video timestamps | From running_video_time |

### Shifts Sheet - Automatic

| Value | Source |
|-------|--------|
| shift_duration | End - Start seconds |
| team_strength | COUNTIF of player cells |
| empty_net flags | Based on goalie cell empty |
| situation | Based on strength comparison |
| stoppage_time | SUMIFS of DeadIce/Timeout events |

---

## Identified Pain Points for Tracker

Based on this analysis, likely pain points:

1. **Many columns to fill** - 72 columns, though ~20 are user input
2. **Multi-row events** - Goals require 3-4 rows for scorer + assists
3. **Manual index management** - Must set flags correctly
4. **Cascading dropdowns** - Three-level selection for each event
5. **Cross-referencing** - Linked events require manual index entry
6. **No video integration** - Video time must be manually tracked
7. **Shift tracking separate** - Must switch sheets for line changes
8. **No undo** - Excel mistakes require manual cleanup
9. **Zone tracking** - Must mentally flip zones for away team

---

*Document generated for BenchSight tracker development*
