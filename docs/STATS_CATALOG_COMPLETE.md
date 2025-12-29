# BenchSight Stats Catalog - Complete Reference
## Status: December 29, 2024

---

## 1. CORE BOX SCORE STATS ✅ COMPLETE

| ID | Name | Player Role | Formula | Status |
|----|------|-------------|---------|--------|
| G | Goals | event_player_1 | COUNT(Goal events) | ✅ |
| A | Assists | EP2/EP3 | A1 + A2 | ✅ |
| A1 | Primary Assists | event_player_2 | Closest assist to goal | ✅ |
| A2 | Secondary Assists | event_player_3 | Second assist | ✅ |
| PTS | Points | derived | G + A | ✅ |
| SOG | Shots on Goal | event_player_1 | On-net shots | ✅ |
| SH_BLK | Blocked Shots | event_player_1 | Shots blocked by opp | ✅ |
| SH_MISS | Missed Shots | event_player_1 | Shots off target | ✅ |
| SH% | Shooting % | derived | G / SOG * 100 | ✅ |
| HITS | Hits | event_player_1 | Physical hits | ✅ |
| BLK | Blocks | event_player_1 | Shots blocked by player | ✅ |
| +/- | Plus/Minus | on_ice | ES: GF - GA | ✅ |

---

## 2. TIME ON ICE STATS ✅ COMPLETE

| ID | Name | Description | Status |
|----|------|-------------|--------|
| TOI | Total TOI | All time including stoppages | ✅ |
| TOI_PLAY | Playing TOI | Active playing time only | ✅ |
| TOI_STOP | Stoppage Time | Dead puck time | ✅ |
| SHIFTS | Shift Count | Total shifts | ✅ |
| SHIFTS_LOG | Logical Shifts | Actual shift changes | ✅ |
| AVG_SHIFT | Avg Shift Length | TOI / SHIFTS | ✅ |
| AVG_SHIFT_PLAY | Avg Playing Shift | TOI_PLAY / SHIFTS | ✅ |

---

## 3. FACEOFF STATS ✅ COMPLETE

| ID | Name | Description | Status |
|----|------|-------------|--------|
| FOW | Faceoff Wins | Faceoffs won | ✅ |
| FOL | Faceoff Losses | Faceoffs lost | ✅ |
| FO_TOT | Faceoff Total | FOW + FOL | ✅ |
| FO% | Faceoff % | FOW / FO_TOT * 100 | ✅ |

---

## 4. PASSING STATS ⚠️ PARTIAL

| ID | Name | Description | Status |
|----|------|-------------|--------|
| PASS_ATT | Pass Attempts | Total passes | ✅ |
| PASS_CMP | Pass Completed | Successful passes | ✅ |
| PASS% | Pass Completion % | CMP / ATT * 100 | ✅ |
| PASS_REC | Pass Received | Times targeted | ❌ TODO |
| PASS_DNG | Danger Passes | Passes to slot | ❌ TODO |
| PASS_ZN | Passes by Zone | O/N/D breakdowns | ❌ TODO |

---

## 5. ZONE TRANSITION STATS ⚠️ PARTIAL

| ID | Name | Description | Status |
|----|------|-------------|--------|
| ZE | Zone Entries | Total entries | ✅ |
| ZX | Zone Exits | Total exits | ✅ |
| ZE_CTRL | Controlled Entries | Carry + Pass entries | ❌ TODO |
| ZE_DUMP | Dump Entries | Dump and chase | ❌ TODO |
| ZE% | Entry Control % | ZE_CTRL / ZE | ❌ TODO |
| ZX_CTRL | Controlled Exits | Carry + Pass exits | ❌ TODO |
| ZE_DEN | Entry Denials | Defender stopped entry | ❌ TODO |
| ZX_DEN | Exit Denials | Defender stopped exit | ❌ TODO |
| ZE_ALLOW | Entries Allowed | Defender gave up entry | ❌ TODO |

**Data Available:** event_detail_2 has ZoneEntry-Carry, ZoneEntry-Pass, ZoneEntry-Dump

---

## 6. TURNOVER STATS ⚠️ PARTIAL

| ID | Name | Description | Status |
|----|------|-------------|--------|
| GIVE | Giveaways | All giveaways | ✅ |
| TAKE | Takeaways | All takeaways | ✅ |
| GIVE_BAD | Bad Giveaways | Costly mistakes | ❌ TODO |
| GIVE_NEUT | Neutral Giveaways | Strategic turnovers | ❌ TODO |
| TO_DIFF | Turnover Differential | TAKE - GIVE_BAD | ❌ TODO |
| TO_RATE | Turnover Rate | Per 60 min | ❌ TODO |
| GIVE_OZ | OZ Giveaways | By zone | ❌ TODO |

**Data Available:** dim_turnover_quality has BAD/NEUTRAL/GOOD

---

## 7. PLUS/MINUS STATS ✅ COMPLETE

| ID | Name | Description | Status |
|----|------|-------------|--------|
| PLUS_EV | Plus (ES) | Goals for at even strength | ✅ |
| MINUS_EV | Minus (ES) | Goals against at ES | ✅ |
| PM_EV | +/- (ES) | PLUS_EV - MINUS_EV | ✅ |
| PLUS_ALL | Plus (All) | Goals for all situations | ✅ |
| MINUS_ALL | Minus (All) | Goals against all sit | ✅ |
| PM_ALL | +/- (All) | PLUS_ALL - MINUS_ALL | ✅ |
| PM_EN | EN-Adjusted +/- | Excludes empty net | ✅ |

---

## 8. ON-ICE POSSESSION (CORSI/FENWICK) ✅ COMPLETE

| ID | Name | Description | Status |
|----|------|-------------|--------|
| CF | Corsi For | Shot attempts for | ✅ |
| CA | Corsi Against | Shot attempts against | ✅ |
| CF% | Corsi % | CF / (CF + CA) * 100 | ✅ |
| FF | Fenwick For | Unblocked shots for | ✅ |
| FA | Fenwick Against | Unblocked shots against | ✅ |
| FF% | Fenwick % | FF / (FF + FA) * 100 | ✅ |
| PDO | PDO (Luck) | On-ice SH% + SV% | ❌ TODO |
| CF_REL | Relative Corsi | vs team average | ❌ TODO |

---

## 9. PER-60 RATES ✅ COMPLETE

| ID | Name | Formula | Status |
|----|------|---------|--------|
| G/60 | Goals Per 60 | G * 3600 / TOI | ✅ |
| A/60 | Assists Per 60 | A * 3600 / TOI | ✅ |
| P/60 | Points Per 60 | PTS * 3600 / TOI | ✅ |
| SOG/60 | Shots Per 60 | SOG * 3600 / TOI | ✅ |
| All playing variants | ... | Uses TOI_PLAY | ✅ |

---

## 10. GOALIE STATS ⚠️ PARTIAL

| ID | Name | Description | Status |
|----|------|-------------|--------|
| SV | Saves | Shots stopped | ✅ |
| GA | Goals Against | Goals allowed | ✅ |
| SA | Shots Against | Shots faced | ✅ |
| SV% | Save % | SV / SA * 100 | ✅ |
| GAA | GAA | GA * 60 / TOI_min | ✅ |
| GAA_PLAY | Playing GAA | Uses TOI_PLAY | ✅ |
| RB% | Rebound Control | No-rebound rate | ❌ TODO |
| FRZ% | Freeze % | Freeze rate | ❌ TODO |
| HDSV% | High Danger SV% | Slot shots | ❌ TODO |
| xSV | Expected Saves | Based on xG | ❌ TODO |
| GSAx | Goals Saved Above Exp | xSV - GA | ❌ TODO |

**Data Available:** event_detail has Save_Rebound, Save_Freeze

---

## 11. DEFENDER STATS ❌ NOT IMPLEMENTED

| ID | Name | Description | Status |
|----|------|-------------|--------|
| D_SA | Shots Against | As primary defender | ❌ TODO |
| D_GA | Goals Against | As primary defender | ❌ TODO |
| D_ZE_ALLOW | Entries Allowed | opp_player_1 on entries | ❌ TODO |
| D_ZX_DEN | Exits Denied | opp_player_1 on exits | ❌ TODO |
| D_BEAT_DK | Beat by Deke | Times beaten by deke | ❌ TODO |
| D_BEAT_SP | Beat by Speed | Times beaten by speed | ❌ TODO |
| D_IMPACT | Defensive Impact | Composite rating | ❌ TODO |

**Data Available:** opp_player_1 role tracked in fact_events_player

---

## 12. MICRO-STATS (PLAY DETAILS) ⚠️ TRACKED NOT AGGREGATED

| ID | Name | Category | Status |
|----|------|----------|--------|
| DEKE | Dekes | Offensive | 🔄 Data exists |
| DEKE_S | Successful Dekes | Offensive | 🔄 Data exists |
| SCREEN | Screens | Offensive | 🔄 Data exists |
| BCK | Backchecks | Defensive | 🔄 Data exists |
| POKE | Poke Checks | Defensive | 🔄 Data exists |
| STICK | Stick Checks | Defensive | 🔄 Data exists |
| IN_LANE | In Shot/Pass Lane | Defensive | 🔄 Data exists |
| SEP_PUCK | Separate from Puck | Defensive | 🔄 Data exists |
| LPB_W | Loose Puck Win | Puck Battles | 🔄 Data exists |
| LPB_L | Loose Puck Loss | Puck Battles | 🔄 Data exists |
| RECOV | Puck Recoveries | Transition | 🔄 Data exists |
| DRIVE | Drive Attempts | Offensive | 🔄 Data exists |
| CRASH | Crash Net | Offensive | 🔄 Data exists |
| CYCLE | Cycle Plays | Offensive | 🔄 Data exists |
| FCHK | Forechecks | Transition | 🔄 Data exists |
| BKOUT | Breakouts | Transition | 🔄 Data exists |

**154 play_detail codes tracked in dim_play_detail**
**Need to aggregate from fact_events_player to fact_player_game_stats**

---

## 13. RATING-AWARE STATS ⚠️ PARTIAL

| ID | Name | Description | Status |
|----|------|-------------|--------|
| QoC | Quality of Competition | Avg opp rating faced | ✅ (opp_avg_rating) |
| QoT | Quality of Teammates | Avg teammate rating | ❌ TODO |
| SKILL_DIFF | Skill Differential | Player vs opp | ✅ (skill_diff) |
| G_ADJ | Rating-Adj Goals | Weighted for opp quality | ❌ TODO |
| PM_ADJ | Rating-Adj +/- | Weighted for opp quality | ❌ TODO |
| xPERF | Expected Performance | Based on rating matchup | ❌ TODO |

---

## 14. H2H / WOWY STATS ⚠️ PARTIAL

### Head-to-Head (fact_h2h)
| ID | Name | Status |
|----|------|--------|
| SHIFTS_TOG | Shifts Together | ✅ |
| TOI_TOG | TOI Together | ❌ TODO |
| GF_TOG | Goals For Together | ❌ TODO |
| GA_TOG | Goals Against Together | ❌ TODO |
| CF_TOG | Corsi For Together | ❌ TODO |
| CA_TOG | Corsi Against Together | ❌ TODO |

### WOWY (fact_wowy)
| ID | Name | Status |
|----|------|--------|
| SHIFTS_W | Shifts With | ✅ |
| SHIFTS_WO | Shifts Without | ✅ |
| GF%_W | GF% With | ❌ TODO |
| GF%_WO | GF% Without | ❌ TODO |
| CF%_W | CF% With | ❌ TODO |
| CF%_WO | CF% Without | ❌ TODO |
| DELTA | Performance Delta | ❌ TODO |

---

## 15. LINE COMBO STATS ✅ MOSTLY COMPLETE

| ID | Name | Status |
|----|------|--------|
| LC_SHIFTS | Shifts Together | ✅ |
| LC_TOI | TOI Together | ✅ |
| LC_GF | Goals For | ✅ |
| LC_GA | Goals Against | ✅ |
| LC_PM | Plus/Minus | ✅ |
| LC_CF | Corsi For | ✅ |
| LC_CA | Corsi Against | ✅ |
| LC_xGF | Expected Goals For | ✅ (placeholder) |

---

## 16. xG MODEL COMPONENTS ❌ NOT IMPLEMENTED

| ID | Name | Description | Status |
|----|------|-------------|--------|
| DIST | Shot Distance | From XY coordinates | ❌ TODO |
| ANGLE | Shot Angle | From XY coordinates | ❌ TODO |
| RUSH | Rush Shot | Within 4s of entry | ❌ TODO |
| REB | Rebound Shot | Within 3s of prior shot | ❌ TODO |
| 1T | One-Timer | Quick release pass | ❌ TODO |
| xG | Expected Goal | Probability model | ❌ TODO |
| xGF | Expected Goals For | Sum(xG) for team | ❌ TODO |
| xGA | Expected Goals Against | Sum(xG) against | ❌ TODO |
| GAE | Goals Above Expected | Actual - xG | ❌ TODO |

**Data Available:** fact_shot_xy has coordinates

---

## 17. COMPOSITE RATINGS ❌ NOT IMPLEMENTED

| ID | Name | Components | Status |
|----|------|------------|--------|
| OFF_RTG | Offensive Rating | G, A, SOG, xGF | ❌ TODO |
| DEF_RTG | Defensive Rating | TK, BLK, BCK, -xGA | ❌ TODO |
| HUSTLE | Hustle Rating | BCK, FCHK, LPB_W | ❌ TODO |
| IMPACT | Impact Score | PTS, +/-, CF% | ❌ TODO |
| WAR | Wins Above Replacement | Full model | ❌ TODO |

---

## 18. BEER LEAGUE SPECIFIC ❌ NOT IMPLEMENTED

| ID | Name | Description | Status |
|----|------|-------------|--------|
| FATIGUE | Fatigue Indicator | Performance by period | ❌ TODO |
| SHIFT_WARN | Long Shift Warning | Shifts > 90s | ❌ TODO |
| SUB_EQ | Substitution Equity | TOI fairness | ❌ TODO |
| BENCH_MIN | Bench Minors | Too many men | ❌ TODO |
| P3_DROP | Period 3 Dropoff | Late game fatigue | ❌ TODO |

---

## Summary: Implementation Status

| Category | Total | Done | Partial | Missing |
|----------|-------|------|---------|---------|
| Core Box Score | 12 | 12 | 0 | 0 |
| Time Stats | 7 | 7 | 0 | 0 |
| Faceoffs | 4 | 4 | 0 | 0 |
| Passing | 6 | 3 | 0 | 3 |
| Zone Transition | 9 | 2 | 0 | 7 |
| Turnovers | 7 | 2 | 0 | 5 |
| Plus/Minus | 7 | 7 | 0 | 0 |
| Corsi/Fenwick | 8 | 6 | 0 | 2 |
| Per-60 | 5 | 5 | 0 | 0 |
| Goalie | 11 | 6 | 0 | 5 |
| Defender | 7 | 0 | 0 | 7 |
| Micro-Stats | 16+ | 0 | 16 | 0 |
| Rating-Aware | 6 | 2 | 0 | 4 |
| H2H/WOWY | 12 | 3 | 0 | 9 |
| Line Combos | 8 | 8 | 0 | 0 |
| xG Model | 9 | 0 | 1 | 8 |
| Composites | 5 | 0 | 0 | 5 |
| Beer League | 5 | 0 | 0 | 5 |
| **TOTAL** | **144** | **67** | **17** | **60** |

**Implementation Rate: 67/144 = 47% fully done**
**Partial Data Exists: 84/144 = 58% (can be completed with aggregation)**

---

*Last Updated: December 29, 2024*
