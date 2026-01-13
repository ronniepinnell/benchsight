# BenchSight Tracking Errors Log

**Version:** v23.1  
**Updated:** 2026-01-11

This document logs data quality issues that originate from tracking data, NOT ETL bugs.

---

## Duplicate Player-Event Combinations (43 rows)

Same player tracked multiple times in the same event. These are tracking entry errors - a player should only appear once per event with one role.

| game_id | event_id | player_id | player_name | roles | event_type |
|---------|----------|-----------|-------------|-------|------------|
| 18977 | EV1897701498 | P100016 | Wyatt Crandall | event_player_1\|event_player_2\|event_player_3 | Save |
| 18987 | EV1898701440 | P100009 | Graham Peters | event_player_1\|event_player_2 | Zone_Entry_Exit |
| 18987 | EV1898701667 | P100201 | Garrett Ashcroft | event_player_1\|event_player_2 | Possession |
| 18977 | EV1897702122 | NULL | Unknown | event_player_1\|event_player_2 | Possession |
| 18977 | EV1897701880 | P100038 | Kevin Moore | event_player_1\|event_player_2 | Zone_Entry_Exit |
| 18969 | EV1896901589 | P100001 | Sam Downs | event_player_3\|event_player_2 | Zone_Entry_Exit |
| 18969 | EV1896902064 | P100064 | James Rynearson | event_player_2\|event_player_1 | Possession |
| 18987 | EV1898702228 | P100232 | Philip Kerchner | opp_player_1\|event_player_1 | Play |
| 18981 | EV1898101830 | P100002 | Kevin White | event_player_1\|event_player_2 | Possession |
| 18977 | EV1897701173 | NULL | Unknown | opp_player_3\|event_player_1 | Zone_Entry_Exit |
| 18977 | EV1897702081 | P100001 | Sam Downs | opp_player_1\|opp_player_2 | Possession |
| 18969 | EV1896902064 | P100023 | Alex Considine | opp_player_2\|opp_player_1 | Possession |
| 18977 | EV1897701689 | NULL | Unknown | event_player_1\|event_player_2 | Pass |
| 18977 | EV1897701690 | P100108 | Robert Mayfield | event_player_1\|event_player_3 | Pass |
| 18987 | EV1898702294 | P100064 | James Rynearson | event_player_1\|event_player_2 | Stoppage |
| 18977 | EV1897701421 | P100108 | Robert Mayfield | event_player_1\|opp_player_1 | Turnover |
| 18969 | EV1896901713 | P100117 | Keegan Mantaro | event_player_1\|event_player_2 | Turnover |
| 18977 | EV1897701437 | P100097 | Steve Smith | event_player_2\|opp_player_3 | Zone_Entry_Exit |
| 18977 | EV1897701352 | P100084 | Ty Smith | event_player_1\|event_player_2 | Possession |
| 18987 | EV1898701810 | P100214 | Ryan Kiehl | opp_player_1\|event_player_2 | Pass |
| 18987 | EV1898701471 | P100201 | Garrett Ashcroft | event_player_1\|opp_player_1 | Possession |
| 18987 | EV1898701808 | P100232 | Philip Kerchner | opp_player_1\|event_player_4 | Possession |
| 18977 | EV1897702080 | P100084 | Ty Smith | event_player_1\|event_player_2 | Possession |
| 18987 | EV1898701368 | P100232 | Philip Kerchner | event_player_1\|opp_player_1 | Play |
| 18981 | EV1898101863 | P100093 | Pat Major | event_player_1\|event_player_4 | Zone_Entry_Exit |
| 18981 | EV1898101863 | P100161 | Galen Wood | event_player_2\|event_player_3 | Zone_Entry_Exit |
| 18981 | EV1898101864 | P100093 | Pat Major | event_player_1\|event_player_2 | Zone_Entry_Exit |
| 18969 | EV1896901948 | P100110 | JoLyn Maly | event_player_1\|event_player_3 | Pass |
| 18977 | EV1897701368 | P100161 | Galen Wood | event_player_1\|event_player_1 | Shot |
| 18987 | EV1898701396 | P100002 | Kevin White | event_player_1\|opp_player_1 | Possession |
| 18969 | EV1896901305 | P100030 | Jesse Chambless | event_player_2\|event_player_1 | Possession |
| 18987 | EV1898702422 | P100002 | Kevin White | event_player_1\|opp_player_1 | Zone_Entry_Exit |
| 18977 | EV1897702351 | P100002 | Kevin White | event_player_2\|event_player_1 | Stoppage |
| 18977 | EV1897702028 | P100097 | Steve Smith | event_player_2\|opp_player_2 | Zone_Entry_Exit |
| 18977 | EV1897701422 | P100097 | Steve Smith | opp_player_1\|event_player_1 | Possession |
| 18977 | EV1897701730 | P100086 | Beau Kelly | event_player_1\|event_player_2 | Stoppage |
| 18969 | EV1896901546 | P100093 | Pat Major | event_player_1\|event_player_2 | Zone_Entry_Exit |
| 18977 | EV1897701642 | P100123 | Todd Heffner | event_player_1\|event_player_2 | Possession |
| 18977 | EV1897701424 | P100097 | Steve Smith | opp_player_1\|event_player_1 | Turnover |
| 18987 | EV1898702230 | P100232 | Philip Kerchner | opp_player_1\|event_player_2 | Pass |
| 18987 | EV1898702403 | P100002 | Kevin White | event_player_1\|opp_player_1 | Pass |
| 18977 | EV1897701382 | P100105 | Ronnie Pinnell | event_player_2\|event_player_3 | Pass |
| 18977 | EV1897701026 | P100159 | Josh Cronk | event_player_1\|event_player_2 | Possession |

**Action:** Fix in tracking files - ensure each player only has one role per event.

**Note:** Until fixed, ETL keeps first occurrence per game+event+player.

---

## Null player_id (177 rows in fact_event_players)

Jersey numbers tracked that don't exist in game roster.

| Game | Jersey | Team(s) | Count | Notes |
|------|--------|---------|-------|-------|
| 18977 | #84 | Both (H:71, A:40) | 111 | Not in roster |
| 18977 | #33 | Both (H:22, A:19) | 41 | Not in roster |
| 18969 | #41 | Platinum (H) | 1 | Not in roster |
| 18969 | #48 | Velodrome (A) | 1 | Not in roster |
| Various | N/A | - | ~23 | System events (GameStart, etc.) - Expected |

**Action:** Add missing players to roster OR correct jersey numbers in tracking files.

---

## Duplicate Rows (1 confirmed)

| Game | Event | Player | Issue |
|------|-------|--------|-------|
| 18977 | EV1897701368 | Galen Wood (P100161) | Listed as event_player_1 TWICE |

**Action:** Remove duplicate row from tracking file.

---

## Missing Goal (1 confirmed)

| Game | Expected | Tracked | Missing |
|------|----------|---------|---------|
| 18977 | 6 | 5 | 1 home goal |

**Action:** Add missing goal to tracking file.

---

## Taxonomy Sync Gaps

Values in tracking data that don't exist in dimension tables. These cause null FK IDs but don't break analytics.

### event_detail (13 values, 1,290 rows affected)

| Value | Count |
|-------|-------|
| PuckRetrieval | 498 |
| Faceoff_AfterStoppage | 329 |
| PuckRecovery | 309 |
| Regroup | 35 |
| Shot_BlockedSameTeam | 28 |
| Zone_ExitFailed | 22 |
| Zone_Entryfailed | 22 |
| Zone_KeepinFailed | 16 |
| Breakaway | 14 |
| Stoppage_Period | 8 |
| Shot_OnNet | 3 |
| Possession | 3 |
| Shot_MissedPost | 3 |

### event_detail_2 (15 values, 776 rows affected)

| Value | Count |
|-------|-------|
| Pass_Rim_Wrap | 218 |
| Giveaway_AttemptedZoneClear_Dump | 161 |
| Giveaway_ZoneClear_Dump | 154 |
| ZoneEntry_PassMiss_Misplay | 111 |
| Save_Shoulder | 33 |
| Play_SeparateFromPuck | 20 |
| Giveaway_ZoneEntry_ExitMisplay | 20 |
| Play_Dump_RimInZone | 15 |
| PokeCheck | 14 |
| Pass_Deflected_TippedShot | 10 |
| Shot_Tipped | 7 |
| Deke | 4 |
| DumpChase | 4 |
| Save_Skate | 3 |
| DriveMiddle | 2 |

### play_detail1 (84 values, 1,399 rows affected)

Top values:
- Defensive_PlayPossession_StickCheck: 162
- OffensivePlay_Pass_SecondTouch: 97
- OffensivePlay_Zone_PuckRetreivalTurnover: 97
- Defensive_PlayPass_InShotPassLane: 80
- Defensive_PlayPossession_PokeCheck: 65
- (79 more values - see full list in validation session)

### play_detail_2 (34 values, 121 rows affected)

Top values:
- OffensivePlay_Pass_SecondTouch: 16
- Defensive_Zone_AttemptedBreakOutPass: 15
- OffensivePlay_Possession_Deke: 12
- (31 more values)

**Action Options:**
1. Add values to BLB_TABLES.xlsx dimension sheets (recommended)
2. Standardize tracking data to use existing values
3. Accept null FKs (analytics still work, just can't filter by these)

---

*This log is updated during validation sessions*
