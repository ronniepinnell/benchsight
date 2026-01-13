# Validated Tables

This folder contains detailed validation documentation for each table reviewed during collaborative validation sessions.

## Validation Status

| # | Table | Status | Date | Notes |
|---|-------|--------|------|-------|
| 1 | dim_player | ✅ Validated | 2026-01-10 | Remove 7 CSAH columns |
| 2 | dim_team | ✅ Validated | 2026-01-10 | Remove 9 CSAHA teams + csah_team column |
| 3 | dim_schedule | ✅ Validated | 2026-01-10 | Remove video + team_game_id columns |
| 4 | dim_event_type | ✅ Validated | 2026-01-10 | Clean, no changes |
| 5-8 | Taxonomy tables | ⚠️ Sync needed | 2026-01-10 | 117 values need sync between tracker/BLB |

## Validated Tables
- `01_dim_player.md` - ✅ Complete
- `02_dim_team.md` - ✅ Complete  
- `03_dim_schedule.md` - ✅ Complete
- `04_dim_event_type.md` - ✅ Complete
- `05_08_taxonomy_tables.md` - ⚠️ Needs sync

## Session Progress
- **Completed:** 4 tables fully validated
- **Partial:** 4 taxonomy tables (need source sync)
- **Remaining:** fact_events, fact_shifts, fact_gameroster, fact_player_game_stats, fact_team_game_stats, fact_goalie_game_stats, and more

## Key Findings

### Action Items from Validation
1. **dim_player:** Remove 7 CSAH columns
2. **dim_team:** Filter to norad_team='Y', remove csah_team column
3. **dim_schedule:** Remove 7 columns (video + team_game_id)
4. **Taxonomy tables:** Sync naming convention between tracker and BLB

### Source Data Fixed
- ✅ AMOS spelling standardized
- ✅ Season values fixed (removed 2025XXXX test data)
- ✅ Null description/skill_level columns populated
