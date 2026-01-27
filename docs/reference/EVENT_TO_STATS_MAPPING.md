# Event-to-Stats Mapping: What Can We Calculate?

**Purpose:** Complete reference showing which statistics are enabled by each event type. Use this to understand the analytical value of tracking specific events.

**Version:** 1.0
**Last Updated:** 2026-01-26
**Based on:** BenchSight ETL v26.1

---

## Quick Reference Matrix

| Event Type | Core Stats | Advanced Stats | Micro Stats | xG Impact |
|-----------|-----------|----------------|-------------|-----------|
| **Goals** | Goals, Assists, Points | Plus/Minus, Goal timing, Shot location | Goal type, Second chance | Direct xG validation |
| **Shots** | SOG, Shots, Shot% | Corsi, Fenwick, xG | Shot type, Rush shots, Rebounds | Primary xG input |
| **Zone Entries** | Entries, Entry% | Shot chains, Offensive zone time | Entry type, Controlled vs dump | Chain analysis |
| **Zone Exits** | Exits, Exit% | Defensive zone time, Breakouts | Exit type, Pressure exits | Transition quality |
| **Faceoffs** | FO%, Zone FO% | WDBE faceoff value | Faceoff location | Possession starts |
| **Passes** | Pass%, Pass attempts | Passing networks, Shot assists | Pass type, Creative passes | Shot creation |
| **Takeaways/Giveaways** | Turnover diff | Possession metrics | Forced turnovers | Defensive impact |
| **Hits** | Hit count | Physical play index | Forecheck hits, Finish checks | Intimidation |
| **Blocked Shots** | Blocks (defensive) | Shot suppression | Block location | Defense quality |
| **Penalties** | PIM, Penalty diff | Discipline score | Penalty type, Zone | Game flow |

---

## Tier 1 Events: Core Advanced Stats

### 1. Goals (event_type='Goal', event_detail='Goal_Scored')

#### Traditional Stats
- **Goals** - Goal count for player
- **Assists** - Primary and secondary assists (via play_detail)
- **Points** - Goals + Assists
- **Plus/Minus** - Goal differential while on ice

#### Advanced Stats
- **Shooting Percentage** - Goals / SOG × 100
- **Goals per 60** - Goals per 60 minutes TOI
- **Points per 60** - Points per 60 minutes TOI
- **Goal Timing Analysis** - Goals by period, game state
- **Goal Location Analysis** - Where goals are scored from
- **Goal Type Analysis** - Wrist, one-timer, tip, backhand, etc.

#### Micro Stats (from play_detail)
- **AssistPrimary** - Primary assist credit
- **AssistSecondary** - Secondary assist credit
- **Goal Context** - Rush goal, rebound goal, PP goal, etc.

#### xG Impact
- **xG Validation** - Compare actual goals to expected goals
- **Goal Quality** - High-danger vs low-danger goals
- **Finish Rate** - Goals vs xG (finishing ability)

#### Strength Splits
- **EV Goals** - Even strength goals
- **PP Goals** - Power play goals
- **PK Goals** - Shorthanded goals (rare but impactful)
- **EN Goals** - Empty net goals

#### Game State Splits
- **Goals Leading** - Scoring when ahead
- **Goals Trailing** - Scoring from behind (clutch goals)
- **Goals Tied** - Scoring in tied games

#### WAR/GAR Components
- **Goal Value** - Direct contribution to wins (1.0 weight in GAR)
- **Assist Value** - Primary (0.7), Secondary (0.4) weights

---

### 2. Shot Attempts (event_type='Shot')

#### Shot Result Categories
- **SOG (Shots on Goal)** - Shot_OnNetSaved, Shot_Goal
- **Blocked Shots** - Shot_Blocked
- **Missed Shots** - Shot_Missed, Shot_MissedPost

#### Traditional Stats
- **Shots** - Total shot attempts (SOG + Blocked + Missed)
- **SOG** - Shots on goal only
- **Shooting %** - Goals / SOG × 100
- **Shots per 60** - Shot rate per 60 minutes
- **SOG per 60** - SOG rate per 60 minutes

#### Advanced Possession Metrics
- **Corsi For (CF)** - All shot attempts by player's team
- **Corsi Against (CA)** - All shot attempts by opponent
- **Corsi For % (CF%)** - CF / (CF + CA) × 100
- **Fenwick For (FF)** - Unblocked shot attempts by team
- **Fenwick Against (FA)** - Unblocked shot attempts by opponent
- **Fenwick For % (FF%)** - FF / (FF + FA) × 100
- **Corsi Differential** - CF - CA
- **Fenwick Differential** - FF - FA
- **CF per 60** - Corsi For rate per 60 minutes
- **CA per 60** - Corsi Against rate per 60 minutes

#### Expected Goals (xG) - REQUIRES XY COORDINATES
- **xG (Expected Goals)** - Probability of goal based on shot characteristics
- **xGA (Expected Goals Against)** - xG for opponent while on ice
- **xGF%** - xG share (offensive efficiency)
- **xG Differential** - xG - xGA
- **xG vs Goals** - Actual goals vs expected (luck/skill measure)
- **Shot Quality** - Average xG per shot

#### Shot Type Analysis (from event_detail_2)
- **Wrist Shots** - Count and shooting %
- **Slap Shots** - Count and shooting %
- **Snap Shots** - Count and shooting %
- **Backhand Shots** - Count and shooting %
- **One-Timers** - Count and shooting %
- **Tip/Deflection Shots** - Count and shooting %
- **Wraparound Shots** - Count
- **Poke/Bat Shots** - Count
- **Primary Shot Type** - Most common shot type
- **Shot Variety** - Number of different shot types used

#### Shot Location Analysis (requires XY)
- **Distance to Net** - Average shot distance
- **Angle to Net** - Average shot angle
- **High-Danger Shots** - Shots from slot (close + centered)
- **Medium-Danger Shots** - Shots from mid-range
- **Low-Danger Shots** - Shots from perimeter
- **HD Shooting %** - Conversion rate on high-danger shots

#### Situational Shot Metrics (from play_detail)
- **Rush Shots** - Shots on rush (1.3x xG modifier)
- **Rebound Shots** - Shots off rebounds (1.5x xG modifier)
- **One-Timer Shots** - Quick-release shots (1.4x xG modifier)
- **Breakaway Shots** - 1-on-0 or 1-on-goalie (2.5x xG modifier!)
- **Screened Shots** - Shots with screen (1.2x xG modifier)
- **Deflection Shots** - Tipped shots (1.3x xG modifier)
- **Shots Under Pressure** - Shots while closely defended
- **Shots in Traffic** - Shots from congested areas

#### Shot Quality Metrics
- **Average xG per Shot** - Shot quality measure
- **HD Shot %** - Percentage of shots that are high-danger
- **Shot Type Distribution** - Mix of shot types used

#### Strength Splits
- **EV Shots** - Even strength shot attempts
- **PP Shots** - Power play shot attempts
- **PK Shots** - Shorthanded shot attempts

#### WAR/GAR Components
- **Shots Generated** - 0.015 weight per shot
- **xG Generated** - 0.8 weight per xG point

---

### 3. Zone Entries (event_detail='Zone_Entry')

#### Basic Entry Stats
- **Zone Entries** - Total entries into offensive zone
- **Zone Entry %** - Success rate (if tracking success/failure)
- **Entries per 60** - Entry rate per 60 minutes
- **Zone Entries Successful** - Successful entries (maintained possession)
- **Zone Entries Failed** - Failed entries (lost possession)

#### Entry Type Analysis (from event_detail_2 or play_detail)
- **Controlled Entries** - Carrying puck into zone
- **Dump-Ins** - Chipping puck deep
- **Pass Entries** - Passing into zone
- **Entry Success by Type** - Which entry types work best

#### Advanced Zone Entry Metrics
- **Shot Chains** - Entry → Shot sequences
- **Time to Shot after Entry** - How quickly shots follow entries
- **Entries Leading to Shots** - Percentage of entries that generate shots
- **Entries Leading to Goals** - Percentage that result in goals
- **Entry Quality Score** - Based on outcomes after entry

#### Offensive Zone Time
- **OZ Possession Time** - Time spent with puck in offensive zone
- **OZ Possession % of Total** - Offensive possession rate
- **OZ Time per Entry** - Average possession time per entry

#### Entry Context (from play_detail)
- **Entries on Rush** - Transition entries
- **Entries vs Neutral Zone Forecheck** - Against pressure
- **Entries with Speed** - High-speed entries
- **Entries off Faceoff Win** - Direct entries

#### Defensive Metrics (for defenders)
- **Ceded Zone Entries** - Entries allowed without pressure (>20ft away)
- **Entry Denials** - Entries stopped at blue line
- **Entry Pressure** - Close defense on entries

#### WAR/GAR Components
- **Zone Entry Value** - 0.04 weight per successful entry

---

### 4. Zone Exits (event_detail='Zone_Exit')

#### Basic Exit Stats
- **Zone Exits** - Total exits from defensive zone
- **Zone Exit %** - Success rate (clean exits)
- **Exits per 60** - Exit rate per 60 minutes
- **Zone Exits Successful** - Clean breakouts (maintained possession)
- **Zone Exits Failed** - Failed breakouts (lost possession)

#### Exit Type Analysis
- **Controlled Exits** - Carrying puck out
- **Pass Exits** - Passing out of zone
- **Chip Exits** - Chipping puck out
- **Rim Exits** - Around-the-boards exits
- **Exit Success by Type** - Which exit types work best

#### Advanced Exit Metrics
- **Breakout Efficiency** - Clean exit percentage
- **Defensive Zone Time** - Time spent in defensive zone
- **DZ Possession Time** - Time with puck in defensive zone
- **Exits Under Pressure** - Exits against forecheck
- **Exits Leading to Offense** - Exits that lead to zone entry

#### Exit Context (from play_detail)
- **Exits on Rush** - Quick transition exits
- **Exits vs Forecheck** - Against aggressive pressure
- **Exits with Support** - Supported breakouts
- **Stretch Pass Exits** - Long pass breakouts

#### Defensive Pressure (for forecheckers)
- **Ceded Zone Exits** - Exits allowed without pressure (>18ft away)
- **Exit Denials** - Exits stopped/turned over
- **Forecheck Pressure** - Close pressure on exits

#### WAR/GAR Components
- **Defensive Zone Exits** - 0.03 weight per clean exit

---

### 5. Faceoffs (event_type='Faceoff')

#### Basic Faceoff Stats
- **Faceoff Wins** - FO wins (event_player_1)
- **Faceoff Losses** - FO losses (opp_player_1)
- **FO Win %** - Wins / (Wins + Losses) × 100
- **Faceoffs Taken** - Total FO attempts
- **FO per 60** - Faceoff rate per 60 minutes

#### Zone-Specific Faceoff Stats
- **Offensive Zone FO%** - Win rate in offensive zone
- **Defensive Zone FO%** - Win rate in defensive zone
- **Neutral Zone FO%** - Win rate in neutral zone
- **OZ FO Wins** - Count of offensive zone wins
- **DZ FO Wins** - Count of defensive zone wins
- **NZ FO Wins** - Count of neutral zone wins

#### Advanced Faceoff Metrics
- **WDBE Value** - Win/Draw/Ball/Exit faceoff outcome value
- **FO Win Impact** - Goals/shots following FO wins
- **FO Loss Impact** - Goals/shots following FO losses
- **Clean Wins** - FO wins leading to possession
- **WDBE per 60** - Faceoff value rate per 60 minutes

#### Faceoff Context
- **PP Faceoffs** - Power play faceoff performance
- **PK Faceoffs** - Penalty kill faceoff performance
- **Clutch Faceoffs** - FO% in close games, late periods
- **vs Elite Opponents** - FO% against top centers

#### Possession Impact
- **Possession Starts from FO** - Possessions gained via FO
- **FO Win to Shot %** - Shots generated after FO wins
- **FO Win to Goal %** - Goals generated after FO wins

---

## Tier 2 Events: Playmaking & Defense

### 6. Passes (event_type='Pass')

#### Basic Pass Stats
- **Pass Attempts** - Total passes attempted
- **Pass Completions** - Successful passes
- **Pass Completion %** - Completions / Attempts × 100
- **Passes per 60** - Pass rate per 60 minutes
- **Pass Targets** - Unique players passed to

#### Pass Type Analysis (from event_detail_2)
- **Forehand Passes** - Standard forehand passes
- **Backhand Passes** - Backhand passes
- **Stretch Passes** - Long passes up ice
- **Bank Passes** - Passes off boards
- **Rim Passes** - Around-the-boards passes
- **Drop Passes** - Drop passes
- **Lob Passes** - High lob passes
- **One-Touch Passes** - Quick redirects
- **Creative Passes** - Sum of high-skill passes
- **Pass Type Diversity** - Number of different pass types used

#### Advanced Playmaking Metrics
- **Shot Assists** - Passes directly leading to shots (0.3 GAR weight)
- **Secondary Shot Assists** - Pass before shot assist
- **Passing Networks** - Who plays with whom
- **Pass Completion % by Type** - Success rate per pass type
- **Stretch Pass Success %** - Long pass completion rate
- **Passes Leading to Chances** - High-danger pass outcomes

#### Pass Quality Metrics
- **Dangerous Passes** - Passes creating scoring chances
- **Passes to Slot** - Passes into high-danger areas
- **Cross-Ice Passes** - Lateral passes (high risk/reward)
- **Passes Under Pressure** - Completion rate while defended

#### Playmaking Context (from play_detail)
- **Give-and-Go Passes** - Pass and immediate return
- **Quick-Up Passes** - Fast transition passes
- **Intercepted Passes** - Passes picked off
- **Receiver Missed** - Target failed to receive pass
- **Pass-Shot Sequences** - Pass chains ending in shots

#### WAR/GAR Components
- **Shot Assists** - 0.3 weight per shot assist
- **Playmaking Value** - Indirect goal creation

---

### 7. Takeaways/Giveaways (event_type='Turnover')

#### Basic Turnover Stats
- **Takeaways** - Pucks stolen from opponent
- **Giveaways** - Turnovers committed
- **Turnover Differential** - Takeaways - Giveaways
- **Takeaways per 60** - Takeaway rate per 60 minutes
- **Giveaways per 60** - Giveaway rate per 60 minutes

#### Turnover Context
- **Forced Turnovers** - Turnovers forced by defensive pressure (opp within 2ft)
- **Unforced Giveaways** - Self-inflicted turnovers
- **Turnovers by Zone** - Where turnovers occur
- **Turnovers Under Pressure** - Turnovers while defended
- **Turnovers Leading to Goals Against** - High-cost turnovers

#### Possession Metrics
- **Possession Changes** - Total possession changes
- **Possession Gained** - From takeaways
- **Possession Lost** - From giveaways
- **Net Possession Impact** - Takeaways - Giveaways

#### Defensive Playmaking
- **Takeaways in DZ** - Defensive zone takeaways
- **Takeaways in NZ** - Neutral zone takeaways
- **Takeaways in OZ** - Offensive zone takeaways (forechecking)
- **Stick Checks Leading to Takeaways** - Active stick work

#### WAR/GAR Components
- **Takeaway Value** - 0.05 weight per takeaway

---

### 8. Blocked Shots (Shot with event_detail='Shot_Blocked')

#### Shot Block Stats (Defensive Credit to opp_player_1)
- **Blocked Shots** - Shots blocked (defensive stat)
- **Blocks per 60** - Block rate per 60 minutes
- **Blocks by Zone** - Where blocks occur
- **High-Danger Blocks** - Blocks in slot/crease
- **Blocks Leading to Breakouts** - Blocks → clean exits

#### Shot Suppression Metrics
- **Shot Attempts Against** - Corsi Against (includes blocks)
- **Shot Block %** - Blocks / Shot Attempts Against
- **Shots Prevented** - Blocks + denials
- **HD Shots Prevented** - High-danger shots blocked

#### Sacrifice Play Metrics
- **Shot Block Locations** - Where player blocks shots
- **Shot Block Timing** - PK blocks, late-game blocks
- **Shot Block Context** - Blocks under pressure, crease blocks

#### WAR/GAR Components
- **Blocked Shots** - 0.02 weight per block

---

### 9. Hits (event_type='Hit')

#### Basic Hit Stats
- **Hits** - Total hits delivered (event_player_1)
- **Hits Taken** - Hits received (opp_player_1)
- **Hit Differential** - Hits delivered - Hits taken
- **Hits per 60** - Hit rate per 60 minutes

#### Hit Context
- **Hits by Zone** - OZ (forechecking), NZ (neutral zone), DZ (finishing checks)
- **Hits Leading to Turnovers** - Impactful hits
- **Hits on Rush** - Transition hits
- **Finishing Checks** - Hits in defensive zone

#### Physical Play Metrics
- **Physical Play Index** - Hit rate + intensity
- **Intimidation Factor** - Impact on opponent behavior
- **Forechecking Intensity** - OZ hits per 60
- **Backcheck Intensity** - DZ hits per 60

#### Possession Impact
- **Hits Leading to Possession** - Hits → takeaways
- **Hits Disrupting Breakouts** - DZ hits preventing exits
- **Hits Creating Turnovers** - Forced errors from hits

---

### 10. Penalties (event_type='Penalty')

#### Basic Penalty Stats
- **Penalties Taken** - Infractions committed
- **Penalties Drawn** - Penalties drawn on opponent
- **Penalty Differential** - Drawn - Taken
- **PIM (Penalty Minutes)** - Total penalty time
- **Penalties per 60** - Penalty rate per 60 minutes

#### Penalty Type Analysis
- **Minor Penalties** - 2-minute penalties
- **Major Penalties** - 5-minute penalties
- **Misconduct Penalties** - 10-minute penalties
- **Penalty Types** - Tripping, hooking, slashing, etc.

#### Discipline Metrics
- **Discipline Score** - Inverse of penalty rate
- **Unnecessary Penalties** - Offensive zone penalties, away-from-play
- **Defensive Penalties** - Preventing scoring chances
- **Penalty Timing** - Late-game penalties, clutch situations

#### Power Play/Penalty Kill Impact
- **PP Opportunities Created** - Penalties drawn
- **PK Situations Created** - Penalties taken
- **Net PP Advantage** - PP opportunities vs PK situations
- **Penalty Impact on Game Flow** - Momentum shifts

---

## Tier 3 Events: Micro-Stats & Style Analysis

### 11. Offensive Micro-Stats (from play_detail1/play_detail_2)

#### Skill Moves
- **Dekes** - Puck handling moves (s/u for success/fail)
- **Dekes per 60** - Deke rate per 60 minutes
- **Deke Success Rate** - Successful dekes / Total dekes
- **One-Timers** - Quick-release shots
- **Deflections** - Tipping shots on net

#### Net-Front Presence
- **Screens** - Screening goalie
- **Screens per 60** - Screen rate per 60 minutes
- **Crash Net Events** - Driving to net for rebounds
- **Net-Front Goals** - Goals from crease/slot
- **Garbage Goals** - Rebound/scramble goals

#### Offensive Zone Play
- **Cycles** - Cycling puck in offensive zone
- **Cycles per 60** - Cycle rate per 60 minutes
- **Cycle Possession Time** - Time spent cycling
- **Offensive Zone Retrievals** - Puck retrievals in OZ

---

### 12. Defensive Micro-Stats (from play_detail1/play_detail_2)

#### Pressure Stats
- **Forechecks** - Pressuring puck in offensive zone
- **Forechecks per 60** - Forecheck rate per 60 minutes
- **Forechecks Successful** - Forechecks leading to turnovers
- **Backcheck** - Tracking back on defense
- **Backchecks per 60** - Backcheck rate per 60 minutes

#### Active Stick Work
- **Poke Checks** - Stick checks to dislodge puck
- **Poke Checks per 60** - Poke check rate per 60 minutes
- **Stick Check Success Rate** - Poke checks leading to turnovers
- **Block Passing Lanes** - Positioning to intercept passes
- **Pass Interceptions** - Passes picked off

#### Gap Control
- **Ceded Zone Entries** - Entries allowed without pressure (>20ft)
- **Ceded Zone Exits** - Exits allowed without pressure (>18ft)
- **Forced Turnovers** - Turnovers forced within 2ft
- **Tight Coverage Events** - Close defense (<5ft)

---

### 13. Situational Micro-Stats (from play_detail1/play_detail_2)

#### Under Pressure Performance
- **Events Under Pressure** - Events while closely defended
- **Shots Under Pressure** - Shooting while defended
- **Passes Under Pressure** - Passing while defended
- **Pressure Success Rate** - Success % of pressured events
- **Poise Under Pressure Score** - Performance quality under pressure

#### Traffic Performance
- **Events in Traffic** - Events in congested areas
- **Shots in Traffic** - Shooting from congested areas
- **Goals in Traffic** - Finishing in traffic
- **Traffic Success Rate** - Success % in traffic

#### Rush Play
- **Rush Events** - Events on rush plays
- **Rush Shots** - Shots on rush (1.3x xG)
- **Rush Goals** - Goals on rush
- **Rush Entries** - Zone entries on rush
- **Rush Success Rate** - Effectiveness on rush

---

### 14. Advanced Possession Metrics (Derived from Events)

#### Possession Time by Zone
- **Offensive Zone Possession** - Time with puck in OZ
- **Defensive Zone Possession** - Time with puck in DZ
- **Neutral Zone Possession** - Time with puck in NZ
- **Total Possession Time** - Total time controlling puck
- **Possession % of TOI** - Possession time / Total TOI

#### Possession Chains
- **Possession Chain Length** - Average events per possession
- **Possession Chain Success** - Possessions ending in shot/goal
- **Possession Gained From** - FO, Takeaway, Zone Entry, etc.
- **Possession Lost To** - Shot, Turnover, Zone Exit, etc.

---

## Composite Metrics (Derived from Multiple Events)

### WAR/GAR (Wins Above Replacement / Goals Above Replacement)

**Formula Components:**
```
GAR = (Goals × 1.0) +
      (Primary Assists × 0.7) +
      (Secondary Assists × 0.4) +
      (Shots Generated × 0.015) +
      (xG Generated × 0.8) +
      (Takeaways × 0.05) +
      (Blocked Shots × 0.02) +
      (Defensive Zone Exits × 0.03) +
      (CF Above Average × 0.02) +
      (Zone Entry Value × 0.04) +
      (Shot Assists × 0.3) +
      (Pressure Success × 0.02)
```

**WAR = GAR / GOALS_PER_WIN (4.5)**

**Events Required:**
- Goals, Assists (via play_detail)
- Shots (for Corsi, xG)
- Takeaways
- Blocked Shots (opp_player_1)
- Zone Exits
- Zone Entries
- Passes (for shot assists)

---

### Game Score (Performance Rating)

**Formula Components:**
```
Game Score = (Goals × 0.75) +
             (Primary Assists × 0.7) +
             (Secondary Assists × 0.55) +
             (SOG × 0.075) +
             (Blocked Shots × 0.05) +
             (Faceoff Wins × 0.01) -
             (Faceoff Losses × 0.01) +
             (Corsi For × 0.005) -
             (Corsi Against × 0.005) +
             (Takeaways × 0.15) -
             (Giveaways × 0.15) -
             (Penalties × 0.15)
```

**Offensive Game Score** - Offensive components only
**Defensive Game Score** - Defensive components only

**Events Required:**
- Goals, Assists
- Shots (SOG, Corsi)
- Blocked Shots
- Faceoffs
- Takeaways, Giveaways
- Penalties

---

### Adjusted Rating (Performance vs Expected)

**Concept:** A player rated 4 who scores Game Score = 7.1 "played like a 6"

**Rating-to-Game-Score Map:**
```
Rating 1  → GS 1.0
Rating 2  → GS 2.3
Rating 3  → GS 3.5
Rating 4  → GS 4.7
Rating 5  → GS 5.9
Rating 6  → GS 7.1
Rating 7  → GS 8.3
Rating 8  → GS 9.5
Rating 9  → GS 10.7
Rating 10 → GS 12.0
```

**Events Required:** All events for Game Score calculation

---

### Shot Chains (Zone Entry → Shot Sequences)

**Metrics Tracked:**
- **Chain ID** - Unique chain identifier
- **Entry Event** - Zone entry that started chain
- **Shot Event** - Shot that ended chain
- **Time to Shot** - Seconds from entry to shot
- **Pass Count** - Passes in the chain
- **Events to Shot** - Total events from entry to shot
- **Touch Count** - Unique players involved
- **Entry Type** - Controlled, dump-in, pass entry
- **Shot Result** - Goal, save, block, miss
- **Is Goal** - Boolean for goal scored
- **Event Types Chain** - Sequence of events
- **Event Details Chain** - Detailed event sequence

**Analysis Enabled:**
- Which entry types lead to most shots?
- Which entry types lead to most goals?
- Optimal time to shot after entry
- Optimal pass count before shot
- Team offensive system effectiveness

**Events Required:**
- Zone Entries
- Shots/Goals
- All events in between (passes, etc.)

---

### Linemate Analysis

**Metrics Tracked:**
- **Unique Linemates** - Number of different linemates
- **Top Linemate** - Most frequent linemate
- **Time with Top Linemate** - TOI together
- **Chemistry Score** - Performance with top linemate vs without
- **Linemate Impact** - Goals/assists with specific linemates

**Events Required:**
- Shifts (who's on ice together)
- Goals, Assists (performance together)

---

### Time Bucket Analysis

**Metrics by Time Period:**
- **Early Period** (0:00-10:00) - Stats in first 10 min
- **Mid Period** (10:00-15:00) - Stats in middle 5 min
- **Late Period** (15:00-20:00) - Stats in last 5 min
- **First Period** - P1 stats
- **Second Period** - P2 stats
- **Third Period** - P3 stats

**Analysis:**
- Stamina (early vs late period)
- Clutch performance (late period)
- Period-specific tendencies

**Events Required:** All events with timestamps

---

### Rebound/Second Chance Analysis

**Metrics Tracked:**
- **Rebounds Created** - Shots generating rebounds
- **Rebound Shots** - Shots off rebounds (1.5x xG!)
- **Rebound Goals** - Goals off rebounds
- **Crash Net Events** - Driving to net for rebounds
- **Second Chance Points** - Points from second opportunities
- **Garbage Goals** - Scramble/rebound goals

**Events Required:**
- Shots (with timestamps for rebound detection)
- play_detail: Rebound, CrashNet
- XY data (for rebound location)

---

## Event Linking & Chains

### Linked Events (shared linked_event_key)

**Purpose:** Track multi-part plays that should be analyzed together

**Examples:**
- Pass → Zone Exit → Turnover (failed breakout)
- Pass → Shot → Rebound → Goal
- Zone Entry → Pass → Shot

**Critical Rule:** Micro-stats in linked events are only counted ONCE per player_id per linked_event_key

**Without Linking:** Would count 'ReceiverMissed' 3 times if player appears in all 3 events
**With Linking:** Counts 'ReceiverMissed' only once for that player

---

## Missing Events = Missing Analytics

### If You Don't Track Shots:
❌ Cannot calculate: Corsi, Fenwick, xG, Shooting %, Shot Quality, Shot Chains
❌ Impact: Lose 50%+ of advanced analytics value

### If You Don't Track XY Coordinates:
❌ Cannot calculate: xG, Shot Distance, Shot Angle, High-Danger Chances, Shot Location Analysis
❌ Impact: Lose all shot quality metrics

### If You Don't Track Zone Entries:
❌ Cannot calculate: Entry Stats, Shot Chains, Offensive Zone Time, Breakout Analysis
❌ Impact: Lose all transition game analytics

### If You Don't Track Passes:
❌ Cannot calculate: Pass Completion %, Passing Networks, Shot Assists, Playmaking Metrics
❌ Impact: Lose all playmaking analytics

### If You Don't Track Micro-Stats:
❌ Cannot calculate: Player Style Profiles, Situational Performance, Pressure Stats
❌ Impact: Lose elite-level detail, but core stats remain

---

## Analytics Stack: Bottom-Up View

### Level 1: Raw Events
- Goals, Shots, Zone Entries, Zone Exits, Faceoffs, Passes, Turnovers, Hits, Blocks, Penalties

### Level 2: Basic Counting Stats
- Goals, Assists, Points, SOG, Shots, Blocks, Hits, FO%, Passes, Turnovers

### Level 3: Rate Stats (per 60)
- Goals/60, Points/60, Shots/60, CF/60, CA/60, Pass/60

### Level 4: Possession Metrics
- Corsi (CF, CA, CF%), Fenwick (FF, FA, FF%), Shot Share

### Level 5: Expected Metrics
- xG, xGA, xGF%, xG vs Goals, Shot Quality

### Level 6: Advanced Context
- Strength Splits (EV/PP/PK), Zone Stats, Game State, Period Splits

### Level 7: Micro-Stats
- Dekes, Screens, Forechecks, Poke Checks, Pressure Stats

### Level 8: Composite Metrics
- WAR/GAR, Game Score, Adjusted Rating, Shot Chains

### Level 9: Comparative Analytics
- Percentile Rankings, League-Relative Stats, Linemate Effects

---

## Summary: Event Value Hierarchy

### Tier 1 Events (80% of Value)
1. **Shots** → Corsi, Fenwick, xG (foundation of modern analytics)
2. **Goals** → Points, Plus/Minus, Goal Quality (traditional + advanced)
3. **Zone Entries/Exits** → Transition game, Shot Chains (elite-level insight)
4. **Faceoffs** → Possession starts, WDBE value (situational impact)

### Tier 2 Events (+15% of Value)
5. **Passes** → Playmaking, Shot Assists, Networks (offensive creativity)
6. **Takeaways/Giveaways** → Possession, Defensive playmaking (turnover impact)
7. **Blocked Shots** → Shot suppression, Sacrifice plays (defensive credit)
8. **Hits** → Physical play, Forechecking (intimidation factor)
9. **Penalties** → Discipline, PP/PK opportunities (game flow)

### Tier 3 Events (+5% of Value)
10. **Micro-Stats** → Player style, Situational performance (granular detail)

---

## Code References

- **Player Game Stats Builder:** `src/tables/core_facts.py`
- **Corsi/Fenwick Calculations:** `src/calculations/corsi.py`
- **Player Stats Formulas:** `src/formulas/player_stats_formulas.py`
- **Goal Calculations:** `src/calculations/goals.py`
- **xG Calculation:** `src/tables/event_analytics.py` (calculate_xg_from_xy)
- **Shot Chain Builder:** `src/chains/shot_chain_builder.py`
- **Event Analytics:** `src/tables/event_analytics.py`

---

## Changelog

- **v1.0 (2026-01-26):** Initial mapping based on BenchSight ETL v26.1 (325+ columns in fact_player_game_stats)
