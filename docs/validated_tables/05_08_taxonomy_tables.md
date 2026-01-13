# Taxonomy Tables - Validation Documentation

**Status:** ⚠️ PARTIAL - Sync needed between tracking and BLB  
**Date:** 2026-01-10  
**Reviewers:** Ronnie + Claude

---

## Summary

| Table | Rows | Source | Cross-Check Status |
|-------|------|--------|-------------------|
| dim_event_type | 23 | BLB_Tables.xlsx | ✅ Valid |
| dim_event_detail | 55 | BLB_Tables.xlsx | ⚠️ 13 tracking values not in dim |
| dim_event_detail_2 | 176 | BLB_Tables.xlsx | ⚠️ 15 tracking values not in dim |
| dim_play_detail | 111 | BLB_Tables.xlsx | ⚠️ 57 tracking values not in dim |
| dim_play_detail_2 | 111 | BLB_Tables.xlsx | ⚠️ 32 tracking values not in dim |

---

## dim_event_type ✅ VALIDATED

- 23 event types defined
- All fact_events types exist in dim
- Corsi/Fenwick flags correct
- See `04_dim_event_type.md` for full details

---

## dim_event_detail ⚠️ NEEDS SYNC

**Rows:** 55  
**Columns:** 11  
**Source:** BLB_Tables.xlsx → dim_event_detail

### Missing from dim (13 values in tracking):
- Breakaway
- Faceoff_AfterStoppage
- Possession
- PuckRecovery
- PuckRetrieval
- Rebound_FlurryGenerated (exists as different name?)
- Regroup
- Shot_BlockedSameTeam
- Shot_MissedPost
- Shot_OnNet
- Stoppage_Period
- Zone_Entryfailed (typo - should be Zone_Entry_Failed)
- Zone_ExitFailed (typo)
- Zone_KeepinFailed (typo)

### Action Required
Add missing values to BLB dim_event_detail sheet OR update tracker to use existing codes.

---

## dim_event_detail_2 ⚠️ NEEDS SYNC

**Rows:** 176  
**Columns:** 12  
**Source:** BLB_Tables.xlsx → dim_event_detail_2

### Missing from dim (15 values in tracking):
- Deke
- DriveMiddle
- DumpChase
- Giveaway_AttemptedZoneClear_Dump (underscore vs slash)
- Giveaway_ZoneClear_Dump
- Giveaway_ZoneEntry_ExitMisplay
- Pass_Deflected_TippedShot
- Pass_Rim_Wrap
- Play_Dump_RimInZone
- Play_SeparateFromPuck (typo: SeperateFromPuck in dim)
- PokeCheck
- Save_Shoulder
- Save_Skate
- Shot_Tipped
- ZoneEntry_PassMiss_Misplay

### Action Required
Many are underscore/slash format differences. Standardize in BLB or tracker.

---

## dim_play_detail ⚠️ NEEDS MAJOR SYNC

**Rows:** 111  
**Columns:** 6  
**Source:** BLB_Tables.xlsx → dim_play_detail

### Issue: Different naming conventions
- **Tracking uses:** `OffensivePlay_Zone_Cycle`, `Defensive_PlayPossession_PokeCheck`
- **Dim uses:** `Cycle`, `PokeCheck`

### Missing from dim: 57 values
The tracking data uses a new prefix convention:
- `OffensivePlay_Pass_*`
- `OffensivePlay_Possession_*`
- `OffensivePlay_Zone_*`
- `Offensive_Zone_*`
- `Defensive_Play*`
- `Defensive_Zone_*`

### Action Required
Either:
1. Add all prefixed versions to dim, OR
2. Strip prefixes in tracker before recording, OR
3. Add fuzzy matching in ETL to map new→old

---

## dim_play_detail_2 ⚠️ NEEDS SYNC

**Rows:** 111  
**Columns:** 6  
**Source:** BLB_Tables.xlsx → dim_play_detail_2

### Missing from dim: 32 values
Same issue as dim_play_detail - prefixed naming convention.

---

## Columns Filled In

The following previously-null columns were auto-populated:

| Table | Column | Logic |
|-------|--------|-------|
| dim_event_detail | description | Generated from event_detail_code |
| dim_event_detail_2 | description | Generated from category + code |
| dim_play_detail | skill_level | High/Medium/Low based on play complexity |
| dim_play_detail | description | Generated from category + name |
| dim_play_detail_2 | skill_level | Same as dim_play_detail |
| dim_play_detail_2 | description | Same as dim_play_detail |

---

## Recommended Resolution

**Option A: Update BLB dim tables**
- Add all 117 missing values (13+15+57+32)
- Most robust but tedious

**Option B: Standardize tracker output**
- Strip prefixes like `OffensivePlay_` before recording
- Requires tracker code change

**Option C: ETL fuzzy matching**
- Map new prefixed values to existing dim codes
- ETL handles translation

**Recommended:** Option B or C - less maintenance burden on BLB

---

## Sign-Off

| Reviewer | Date | Verdict |
|----------|------|---------|
| Ronnie | 2026-01-10 | ⚠️ Acknowledged - will fix at source |
| Claude | 2026-01-10 | ⚠️ Documented for future sync |

---

**Next Steps:** 
1. Decide on sync strategy (A, B, or C)
2. Implement chosen approach
3. Re-validate taxonomy tables
