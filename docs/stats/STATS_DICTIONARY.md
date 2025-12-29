# BenchSight Stats Dictionary

## Overview
200+ hockey statistics across 15 categories with player role attribution.

## Stats Categories

### 1. Basic Box Score
| Stat | Name | Player Role | Formula |
|------|------|-------------|---------|
| G | Goals | event_player_1 | COUNT(goals) |
| A | Assists | EP2/EP3 | A1 + A2 |
| A1 | Primary Assists | event_player_2 | COUNT(primary assists) |
| A2 | Secondary Assists | event_player_3 | COUNT(secondary assists) |
| PTS | Points | derived | G + A |
| SOG | Shots on Goal | event_player_1 | COUNT(shots on net) |
| SH_PCT | Shooting % | derived | G / SOG * 100 |
| +/- | Plus/Minus | on_ice | GF - GA at even strength |
| PIM | Penalty Minutes | event_player_1 | SUM(penalty_minutes) |
| HITS | Hits | event_player_1 | COUNT(hits delivered) |
| BLK | Blocked Shots | event_player_1 | COUNT(blocks) |

### 2. Time on Ice
| Stat | Name | Description |
|------|------|-------------|
| TOI_TOTAL | Total TOI | All time including stoppages |
| TOI_PLAYING | Playing TOI | Active playing time |
| TOI_DEAD | Dead Ice | Time during stoppages |
| TOI_EV | Even Strength | 5v5 time |
| TOI_PP | Power Play | PP time |
| TOI_PK | Penalty Kill | PK time |
| SHIFTS | Shift Count | Number of shifts |
| AVG_SHIFT | Avg Shift | TOI_PLAYING / SHIFTS |

### 3. Turnovers
| Stat | Name | Description |
|------|------|-------------|
| TAKEAWAY | Takeaways | All takeaways |
| GIVEAWAY | Giveaways | All giveaways |
| GIVEAWAY_BAD | Bad Giveaways | Costly mistakes |
| GIVEAWAY_NEUTRAL | Neutral Giveaways | Strategic dumps |
| TURNOVER_DIFF | Raw Differential | TK - GV |
| TURNOVER_DIFF_ADJ | Adjusted Diff | TK - GV_BAD |

### 4. Zone Transitions
| Stat | Name | Player Role |
|------|------|-------------|
| ZONE_ENTRY | Zone Entries | event_player_1 |
| ZONE_ENTRY_CTRL | Controlled Entries | event_player_1 |
| ZONE_ENTRY_DUMP | Dump Entries | event_player_1 |
| ZONE_ENTRY_PCT | Control % | derived |
| ZONE_EXIT | Zone Exits | event_player_1 |
| ZONE_EXIT_CTRL | Controlled Exits | event_player_1 |
| ENTRY_DENIAL | Entry Denials | opp_player_1 |
| EXIT_DENIAL | Exit Denials | opp_player_1 |
| ENTRY_ALLOWED | Entries Allowed | opp_player_1 |
| EXIT_ALLOWED | Exits Allowed | opp_player_1 |

### 5. Possession
| Stat | Name | Formula |
|------|------|---------|
| CF | Corsi For | Shot attempts for |
| CA | Corsi Against | Shot attempts against |
| CF_PCT | Corsi % | CF / (CF + CA) * 100 |
| FF | Fenwick For | Unblocked shots for |
| FA | Fenwick Against | Unblocked shots against |
| PDO | PDO | On-ice SH% + SV% |

### 6. Faceoffs
| Stat | Name | Formula |
|------|------|---------|
| FOW | Faceoff Wins | COUNT(wins) |
| FOL | Faceoff Losses | COUNT(losses) |
| FO_PCT | Faceoff % | FOW / (FOW + FOL) * 100 |

### 7. Goalie Stats
| Stat | Name | Formula |
|------|------|---------|
| SV_PCT | Save % | (SA - GA) / SA * 100 |
| GAA | Goals Against Avg | GA / TOI * 60 |
| SA | Shots Against | COUNT(shots faced) |
| GA | Goals Against | COUNT(goals allowed) |
| REBOUND_PCT | Rebound Control | No-rebound rate |
| FREEZE_PCT | Freeze % | Whistle rate |

### 8. Defender Stats (opp_player_1)
| Stat | Name | Description |
|------|------|-------------|
| SHOT_AGAINST | Shots Against | As primary defender |
| GOAL_AGAINST | Goals Against | As primary defender |
| BEAT_BY_DEKE | Beat by Deke | Times beaten |
| BEAT_BY_SPEED | Beat by Speed | Times beaten |
| BEAT_TOTAL | Total Beaten | All beat stats |

### 9. Composite Ratings
| Stat | Name | Formula |
|------|------|---------|
| OFFENSIVE_RATING | Offense Score | weighted(G, A, SOG, PASS_DANGER) |
| DEFENSIVE_RATING | Defense Score | weighted(TK, BLK, BCK) |
| HUSTLE_RATING | Effort Score | weighted(BCK, FC, BTL_W) |
| IMPACT_SCORE | Game Impact | weighted(PTS, +/-, CF%) |

## Benchmarks

| Stat | Poor | Average | Good | Elite |
|------|------|---------|------|-------|
| SH_PCT | <5% | 9% | 12% | 15%+ |
| FO_PCT | <45% | 50% | 52% | 55%+ |
| CF_PCT | <45% | 50% | 52% | 55%+ |
| ZE_PCT | <50% | 60% | 65% | 70%+ |
| SV_PCT | <88% | 91% | 92% | 93%+ |
