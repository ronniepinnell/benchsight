# Event Tracking Priority Guide

**Purpose:** Maximize analytics value while minimizing tracking time. Track Tier 1 events live, add Tier 2+ details later.

**Version:** 1.0
**Last Updated:** 2026-01-26

---

## Quick Reference: What to Track First

| Tier | Time Investment | Analytics Return | Track When |
|------|----------------|------------------|------------|
| **Tier 1** | ~15-20 min/game | 80% of stats value | LIVE - during game |
| **Tier 2** | +10-15 min/game | +15% stats value | POST-GAME - first pass |
| **Tier 3** | +15-20 min/game | +5% stats value | POST-GAME - detail pass |

**Total for full detail:** ~40-55 minutes per game

---

## Tier 1: Critical Events (TRACK LIVE)

### Why These Matter
These events enable **all core advanced stats** that differentiate BenchSight from basic hockey stats:
- **Corsi/Fenwick** - Possession metrics
- **xG (Expected Goals)** - Shot quality models
- **Zone Entry/Exit Analysis** - Transition game
- **Goals/Assists** - Traditional scoring

### Events to Track

#### 1. Goals ⭐⭐⭐ (HIGHEST PRIORITY)
**What to track:**
- Event Type: `Goal`
- Event Detail: `Goal_Scored`
- Event Player 1: Goal scorer
- Event Player 2: Primary assist (if applicable)
- Event Player 3: Secondary assist (if applicable)
- XY coordinates (goal location)
- Time/Period

**Stats enabled:**
- Goals, Assists, Points
- Plus/Minus
- Shooting percentage
- Shot location analysis
- Goal timing patterns

**Critical rule:** Both `event_type == 'Goal'` AND `event_detail == 'Goal_Scored'` are required. Missing either = goal not counted!

**play_detail tracking (Tier 1 only):**
- `AssistPrimary` - on event_player_2's row (if assist occurred)
- `AssistSecondary` - on event_player_3's row (if assist occurred)

#### 2. Shot Attempts ⭐⭐⭐
**What to track:**
- Event Type: `Shot`
- Event Detail:
  - `Shot_OnNetSaved` (shot on goal - saved)
  - `Shot_Goal` (shot that scores - counts as SOG, not Goal_Scored)
  - `Shot_Blocked` (blocked by defender)
  - `Shot_Missed` (missed net)
  - `Shot_MissedPost` (hit post/crossbar)
- Event Player 1: Shooter
- Opp Player 1: Blocker (for blocked shots)
- XY coordinates (critical for xG model!)

**Stats enabled:**
- **Corsi** = All shot attempts (SOG + blocked + missed)
- **Fenwick** = Unblocked shots (SOG + missed)
- **Shots on Goal (SOG)** = Shot_OnNetSaved + Shot_Goal
- **xG (Expected Goals)** - Requires shot location XY data!
- Shooting efficiency metrics

**Why critical:** Corsi/Fenwick are the foundation of modern hockey analytics. xG models predict goal probability from shot characteristics.

#### 3. Zone Entries ⭐⭐⭐
**What to track:**
- Event Type: `ZoneEntry` (or similar)
- Event Detail: `Zone_Entry`
- Event Player 1: Player entering zone
- Opp Player 1: Nearest defender (optional but helpful)
- XY coordinates (where entry occurred)
- Success flag (derive later if needed)

**Stats enabled:**
- Zone entry counts
- Zone entry success rate (if tracking success/failure)
- Transition game analysis
- Offensive zone time
- Shot chains (entry → shot sequences)

**Why critical:** Zone entries are the start of offensive possession. Teams that control zone entries control the game. Shot chains track "entry → shot" sequences - critical for offensive system analysis.

#### 4. Zone Exits ⭐⭐
**What to track:**
- Event Type: `ZoneExit` (or similar)
- Event Detail: `Zone_Exit`
- Event Player 1: Player exiting zone
- Opp Player 1: Forechecking opponent (optional)
- XY coordinates (where exit occurred)

**Stats enabled:**
- Zone exit counts
- Breakout efficiency
- Defensive zone time
- Defensive transition metrics

**Why important:** Clean exits prevent sustained pressure. Poor exits = more defensive zone time = more goals against.

#### 5. Faceoffs ⭐⭐
**What to track:**
- Event Type: `Faceoff`
- Event Detail: `Faceoff_Win` or `Faceoff_Loss`
- Event Player 1: **Faceoff WINNER** (CRITICAL!)
- Opp Player 1: Faceoff LOSER
- Zone (offensive/defensive/neutral)

**Stats enabled:**
- Faceoff win percentage
- Zone-specific faceoff performance
- Possession starts
- WDBE (Win/Draw/Ball/Exit) faceoff value

**Critical rule:** `event_player_1` = winner, `opp_player_1` = loser. Don't swap these!

---

## Tier 2: High-Impact Events (ADD POST-GAME)

### Why These Matter
These events add **significant analytical depth** without being critical live:
- **Passing networks** - Playmaking analysis
- **Possession tracking** - Who controls the puck
- **Defensive metrics** - Hits, blocks, takeaways
- **Transition details** - Dump-ins vs carry-ins

### Events to Track

#### 1. Passes ⭐⭐
**What to track:**
- Event Type: `Pass`
- Event Detail: `Pass_Completed`, `Pass_Failed`, `Pass_Intercepted`
- Event Player 1: Passer
- Event Player 2: Receiver (for completed passes)
- Opp Player 1: Interceptor (for interceptions)

**Stats enabled:**
- Pass completion percentage
- Passing networks (who plays with whom)
- Shot assists (pass that leads to shot)
- Playmaking metrics

**play_detail enhancements (optional):**
- PassStretch, PassBank, PassRim, PassCross (pass types)
- ReceiverMissed (failed reception)

#### 2. Takeaways/Giveaways ⭐⭐
**What to track:**
- Event Type: `Turnover`
- Event Detail: `Turnover_Takeaway` or `Turnover_Giveaway`
- Event Player 1: Player who gained/lost puck
- Opp Player 1: Opponent involved (for takeaways)

**Stats enabled:**
- Turnover differential
- Puck possession metrics
- Defensive playmaking
- Forced turnovers (if tracking defender proximity)

#### 3. Blocked Shots (Defensive Credit) ⭐
**What to track:**
- Event Type: `Shot`
- Event Detail: `Shot_Blocked`
- Event Player 1: Shooter
- Opp Player 1: **Blocker** (gets defensive credit)

**Stats enabled:**
- Shot blocks (defensive metric)
- Shot suppression
- Defensive involvement
- Sacrifice plays

**Note:** This is tracked in Tier 1 for the shooter (Corsi), but the defensive credit for the blocker is Tier 2 detail.

#### 4. Hits ⭐
**What to track:**
- Event Type: `Hit`
- Event Detail: `Hit` (or more specific)
- Event Player 1: Player delivering hit
- Opp Player 1: Player receiving hit

**Stats enabled:**
- Physical play metrics
- Forechecking intensity
- Intimidation factor
- Possession battle analysis

#### 5. Penalties ⭐⭐
**What to track:**
- Event Type: `Penalty`
- Event Detail: Penalty type (tripping, hooking, etc.)
- Event Player 1: Player taking penalty
- Duration (2 min, 4 min, etc.)

**Stats enabled:**
- Penalty differential
- Discipline metrics
- Power play/penalty kill opportunities
- Game flow analysis

---

## Tier 3: Detail Events (ADD FOR FULL DEPTH)

### Why These Matter
These micro-stats add **granular detail** for elite-level analysis:
- **Player style analysis** - How does a player play?
- **Situational performance** - Under pressure, in traffic, etc.
- **Advanced positioning** - Screens, cycles, net-front presence
- **Skill moves** - Dekes, one-timers, tips

### Micro-Stats (play_detail1/play_detail_2)

#### Offensive Micro-Stats
- **Deke** - Puck handling move to beat defender
- **OneTimer** - Shot without stopping puck
- **Deflection** - Tipping shot on net
- **Screen** - Screening goalie
- **CrashNet** - Driving to net for rebound
- **Cycle** - Cycling puck in offensive zone

#### Defensive Micro-Stats
- **Forecheck** - Pressuring puck carrier in offensive zone
- **Backcheck** - Tracking back on defense
- **PokeCheck** - Stick check to dislodge puck
- **BlockPassingLane** - Positioning to block pass
- **CededZoneEntry** - Defender gave up zone entry (>20ft away)
- **CededZoneExit** - Defender gave up zone exit (>18ft away)
- **ForcedTurnover** - Forced turnover within 2ft

#### Situational Micro-Stats
- **UnderPressure** - Event while closely defended
- **InTraffic** - Event in congested area
- **Rush** - Event on rush play (speeds up xG)
- **Rebound** - Shot off rebound (speeds up xG significantly)
- **Breakaway** - 1-on-0 or 1-on-goalie (2.5x xG!)

#### Passing Details
- **PassStretch** - Long pass up ice
- **PassBank** - Pass off boards
- **PassRim** - Pass around boards
- **PassCross** - Cross-ice pass
- **ReceiverMissed** - Receiver failed to handle pass
- **PassIntercepted** - Pass picked off by opponent

#### Special Events
- **GiveAndGo** - Pass and immediate return pass
- **QuickUp** - Fast transition pass
- **ShotAssist** - Pass that directly leads to shot (BIG playmaking credit)

---

## Event Success Tracking (s/u Flags)

Many events have success/failure flags in play_detail columns:
- **s** = successful
- **u** = unsuccessful

### Auto-Derived Success (You Don't Need to Track)
The ETL automatically derives success flags for:
- Zone entries (based on next event)
- Zone exits (based on next event)
- Passes (from event_detail)
- Some defensive plays (CededZone*, ForcedTurnover)

### Manual Success Tracking (If Desired)
For events not auto-derived, you can add:
- `Deke=s` - Successful deke
- `Deke=u` - Failed deke
- `Forecheck=s` - Successful forecheck
- `Forecheck=u` - Failed forecheck

---

## xG Model Input Requirements

The Expected Goals (xG) model requires these inputs (prioritize in Tier 1):

### Essential (Tier 1)
- **Shot location (X, Y)** - Distance and angle to goal
- **Shot type** - Wrist, slap, snap, backhand, tip, deflection
- **Shot result** - Goal, save, block, miss
- **Event detail** - Goal_Scored, Shot_OnNetSaved, Shot_Blocked, etc.

### High-Impact Modifiers (Tier 2)
- **Rush** - 1.3x xG multiplier
- **Rebound** - 1.5x xG multiplier
- **OneTimer** - 1.4x xG multiplier
- **Breakaway** - 2.5x xG multiplier (huge!)
- **Screen** - 1.2x xG multiplier
- **Deflection** - 1.3x xG multiplier

### Detail Modifiers (Tier 3)
- **Traffic** - In front of net
- **Pre-shot movement** - Deke before shot
- **Pass type leading to shot** - Shot assist

**Bottom line:** Track shot XY coordinates in Tier 1, add modifiers in Tier 2/3.

---

## Possession Time Tracking

Possession time is tracked per zone:
- Offensive zone possession time
- Defensive zone possession time
- Neutral zone possession time

**How it works:**
- Possession starts when player gains puck (pass received, turnover won, faceoff win)
- Possession ends when player loses puck (pass, shot, turnover, faceoff)
- Time is calculated from event timestamps

**Tracking tips:**
- Don't need to track possession explicitly - ETL derives from event sequences
- Just track events accurately with timestamps
- Possession chains are built automatically

---

## Statistical Impact Summary

### Without Tier 1 Events
❌ **Cannot calculate:**
- Corsi, Fenwick (no shot attempts)
- xG (no shot locations)
- Zone entry/exit metrics
- Plus/Minus (no goals)
- Shooting percentage (no shots/goals)
- Faceoff win percentage

⚠️ **Result:** Dashboard shows only basic counting stats (goals, assists, TOI)

### With Tier 1 Only
✅ **Can calculate:**
- All core advanced stats (Corsi, Fenwick, xG)
- Zone transition metrics
- Shot quality analysis
- Faceoff performance
- Goals, assists, points, plus/minus
- Per-60 rates for all above

⚠️ **Missing:**
- Playmaking depth (passing networks)
- Defensive detail (hits, blocks as defensive credit)
- Micro-stat analysis (dekes, forechecks, screens)

### With Tier 1 + Tier 2
✅ **Can calculate everything above, plus:**
- Pass completion percentage
- Shot assists / playmaking metrics
- Takeaway/giveaway differential
- Blocked shots (defensive credit)
- Physical play metrics (hits)
- Penalty differential
- Turnover metrics

⚠️ **Missing:**
- Style analysis (how player plays)
- Situational performance (under pressure)
- Elite-level detail

### With Tier 1 + Tier 2 + Tier 3 (FULL DETAIL)
✅ **Can calculate everything:**
- All stats from Tiers 1-2
- Player style fingerprints
- Situational performance
- Advanced xG modifiers
- Micro-stat per-60 rates
- Pressure performance
- Traffic performance
- Complete tactical analysis

---

## Practical Workflow

### Live Game Tracking (Tier 1 - 15-20 minutes)
1. **Start shifts tracking** - Who's on ice (enables TOI, plus/minus)
2. **Track all shots** - Including XY location (Corsi, Fenwick, xG)
3. **Track all goals** - With assists in play_detail (Goals, Assists, Points)
4. **Track zone entries/exits** - Offensive transitions
5. **Track faceoffs** - Winner = event_player_1!

**Goal:** Get 80% of analytics value while game is live.

### First Post-Game Pass (Tier 2 - 10-15 minutes)
1. **Add passes** - Especially passes leading to shots (shot assists)
2. **Add turnovers** - Takeaways/giveaways
3. **Add hits** - Physical play
4. **Add penalties** - Game flow
5. **Verify Tier 1 accuracy** - Fix any mistakes

**Goal:** Get to 95% of analytics value.

### Detail Pass (Tier 3 - 15-20 minutes) - OPTIONAL
1. **Add micro-stats to key events:**
   - Dekes, screens, cycles on offensive plays
   - Forechecks, backchecks, poke checks on defensive plays
   - Shot modifiers (rush, rebound, one-timer, breakaway)
2. **Add situational context:**
   - UnderPressure flags
   - InTraffic flags
3. **Review linked events** - Ensure play_details aren't duplicated

**Goal:** Elite-level detail for advanced analysis.

---

## Common Mistakes to Avoid

### 1. Goal Counting Mistake
❌ **WRONG:** `event_type = 'Shot'` + `event_detail = 'Goal'`
✅ **RIGHT:** `event_type = 'Goal'` + `event_detail = 'Goal_Scored'`

**Why:** BenchSight requires BOTH conditions. Missing either = goal not counted!

### 2. Faceoff Winner Mistake
❌ **WRONG:** `event_player_1` = loser, `opp_player_1` = winner
✅ **RIGHT:** `event_player_1` = winner, `opp_player_1` = loser

**Why:** BenchSight counts faceoff wins for `event_player_1` only.

### 3. Stat Attribution Mistake
❌ **WRONG:** Counting events for all player_roles
✅ **RIGHT:** Only count events for `player_role = 'event_player_1'`

**Why:** Each event has multiple rows (event_player_1, event_player_2, opp_player_1, etc.). Counting all rows = duplicate stats!

### 4. Assist Tracking Mistake
❌ **WRONG:** Relying on player_role for assists
✅ **RIGHT:** Using `play_detail1/play_detail_2` with 'AssistPrimary' or 'AssistSecondary'

**Why:** Assists are tracked via play_detail columns, not player_role.

**Important:** AssistTertiary is NOT counted as an assist! Only Primary and Secondary.

### 5. Micro-Stat Duplication Mistake
❌ **WRONG:** Counting 'ReceiverMissed' on all 3 events in a linked chain (pass → zone_exit → turnover)
✅ **RIGHT:** Count 'ReceiverMissed' only ONCE per `linked_event_key` for that `player_id`

**Why:** Linked events duplicate player rows. Only count each micro-stat once per player per linked event.

### 6. Missing XY Coordinates
❌ **WRONG:** Tracking shots without location
✅ **RIGHT:** Always capture shot X/Y coordinates

**Why:** xG model requires shot location. No location = no xG = major analytics gap!

---

## Quick Decision Guide

### "Should I track this live or post-game?"

**Track LIVE if:**
- It's a shot attempt (any type)
- It's a goal
- It's a zone entry/exit
- It's a faceoff
- It's easy to capture in real-time

**Track POST-GAME if:**
- It's a micro-stat (deke, screen, forecheck)
- It requires review to confirm
- It's a pass (unless shot assist is obvious)
- It slows down your live tracking

### "How much detail is enough?"

**Tier 1 only:**
- Good for: League-wide stats, team comparisons, core analytics
- Not good for: Player development, tactical analysis, style profiling

**Tier 1 + Tier 2:**
- Good for: Everything above + playmaking analysis, defensive metrics
- Not good for: Elite-level tactical breakdowns

**Tier 1 + Tier 2 + Tier 3:**
- Good for: EVERYTHING. Professional-grade analytics.
- Trade-off: Takes 2-3x longer per game

---

## Analytics Return on Investment

| Tracking Effort | Time per Game | Stats Coverage | Best For |
|----------------|---------------|----------------|----------|
| Tier 1 only | 15-20 min | 80% | Fast tracking, league-wide data |
| Tier 1 + Tier 2 | 25-35 min | 95% | Most use cases, player evaluation |
| Tier 1 + Tier 2 + Tier 3 | 40-55 min | 100% | Professional-grade, elite analysis |

**Recommendation:** Start with Tier 1 live tracking. Add Tier 2 post-game for important games. Add Tier 3 only for playoffs or key player evaluations.

---

## References

- **Corsi Calculation:** `src/calculations/corsi.py`
- **xG Model Constants:** `src/tables/core_facts.py` (lines 56-60)
- **Player Stats Formulas:** `src/formulas/player_stats_formulas.py`
- **Goal Counting Rule:** `src/tables/core_facts.py` (lines 42-47)
- **Shot Chain Builder:** `src/chains/shot_chain_builder.py`
- **Play Detail Automation:** `src/advanced/play_detail_automation.py`
- **Event Success Logic:** `docs/reference/EVENT_SUCCESS_LOGIC.md`

---

## Changelog

- **v1.0 (2026-01-26):** Initial guide based on BenchSight ETL v26.1 codebase analysis
