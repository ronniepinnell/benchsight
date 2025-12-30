# ⚠️ Supabase Schema Issues - BLOCKING

**Last Tested**: December 30, 2024
**Status**: 18 of 25 missing tables failed to load
**Blocker For**: All frontend development

---

## Summary

When running `python scripts/bulletproof_loader.py --load missing`, only 7 of 25 tables loaded successfully. The failures fall into 3 categories:

| Category | Count | Issue |
|----------|-------|-------|
| Schema Mismatch | 15 | Primary key column doesn't exist in Supabase |
| Missing CSV | 2 | CSV file not generated (new tables) |
| Missing Constraint | 1 | No primary key constraint for upsert |

---

## Category 1: Schema Mismatch (15 tables)

These tables exist in Supabase but are missing their primary key column.

**The loader expects a PK column, but Supabase tables don't have it.**

| Table | Expected PK Column | Error |
|-------|-------------------|-------|
| `fact_events_long` | `event_long_key` | column does not exist |
| `fact_events_tracking` | `tracking_key` | column does not exist |
| `fact_linked_events` | `link_key` | column does not exist |
| `fact_player_stats_long` | `stat_long_key` | column does not exist |
| `fact_player_boxscore_all` | `boxscore_key` | column does not exist |
| `fact_gameroster` | `roster_key` | column does not exist |
| `fact_head_to_head` | `matchup_key` | column does not exist |
| `fact_player_pair_stats` | `pair_key` | column does not exist |
| `fact_shift_quality` | `quality_key` | column does not exist |
| `fact_rush_events` | `rush_key` | column does not exist |
| `fact_registration` | `registration_key` | column does not exist |
| `fact_league_leaders_snapshot` | `leader_key` | column does not exist |
| `fact_team_standings_snapshot` | `standing_key` | column does not exist |
| `fact_suspicious_stats` | `suspicious_key` | column does not exist |
| `qa_suspicious_stats` | `qa_key` | column does not exist |

### Fix Options

**Option A: Add PK columns to Supabase tables**
```sql
-- Example for fact_events_long
ALTER TABLE fact_events_long ADD COLUMN event_long_key TEXT PRIMARY KEY;

-- Or if table has data, add column then set as PK
ALTER TABLE fact_events_long ADD COLUMN event_long_key TEXT;
UPDATE fact_events_long SET event_long_key = CONCAT(game_id, '_', event_index, '_', row_number);
ALTER TABLE fact_events_long ADD PRIMARY KEY (event_long_key);
```

**Option B: Update loader to use existing PKs**
Check what columns actually exist in Supabase tables and update `TABLE_DEFINITIONS` in `bulletproof_loader.py` to match.

**Option C: Recreate tables from SQL**
Drop and recreate tables using `sql/01_CREATE_ALL_TABLES.sql` which has correct schemas.

---

## Category 2: Missing CSV (2 tables)

These are new tables that don't have CSV files generated yet.

| Table | Issue |
|-------|-------|
| `dim_highlight_type` | CSV not found - video feature not implemented |
| `fact_video_highlights` | CSV not found - video feature not implemented |

### Fix

1. Create the tables in Supabase using `sql/04_VIDEO_HIGHLIGHTS.sql`
2. Create empty CSV templates or seed data:

```bash
# Create dim_highlight_type.csv with seed data
cat > data/output/dim_highlight_type.csv << 'CSV'
highlight_type_id,highlight_type,display_name,icon,color
1,goal,Goal,🎯,#22c55e
2,save,Save,🧤,#3b82f6
3,hit,Hit,💥,#ef4444
4,fight,Fight,🥊,#f97316
5,penalty,Penalty,🚨,#eab308
6,skill,Skill Play,✨,#a855f7
7,team_play,Team Play,🤝,#06b6d4
8,defensive,Defensive Play,🛡️,#6366f1
9,other,Other,📹,#6b7280
CSV

# Create empty fact_video_highlights.csv
echo "highlight_key,game_id,event_index,player_id,team_id,video_url,start_timestamp,end_timestamp,highlight_type,title,description,is_featured,is_approved" > data/output/fact_video_highlights.csv
```

---

## Category 3: Missing Constraint (1 table)

| Table | Issue |
|-------|-------|
| `fact_game_status` | No unique constraint for ON CONFLICT (upsert) |

### Fix

```sql
-- Add primary key constraint
ALTER TABLE fact_game_status ADD PRIMARY KEY (game_id);

-- Or if game_id isn't unique, create a composite key
ALTER TABLE fact_game_status ADD COLUMN status_key TEXT;
UPDATE fact_game_status SET status_key = CONCAT(game_id, '_', status);
ALTER TABLE fact_game_status ADD PRIMARY KEY (status_key);
```

---

## Verification Steps

After fixing, run:

```bash
# Check status
python scripts/bulletproof_loader.py --status

# Load missing
python scripts/bulletproof_loader.py --load missing

# Expected: 0 failures
```

---

## Tables That Loaded Successfully

These 7 tables loaded fine (though some had 0 rows):

| Table | Rows |
|-------|------|
| `fact_player_xy_long` | 0 |
| `fact_player_xy_wide` | 0 |
| `fact_puck_xy_long` | 0 |
| `fact_puck_xy_wide` | 0 |
| `fact_shot_xy` | 0 |
| `fact_plays` | 2714 |
| `fact_sequences` | 1088 |

---

## Full Error Log

```
[08:38:00] Connected to Supabase
[08:38:10] Found 25 empty/missing tables
[08:38:10] Loading dim_highlight_type...
[08:38:10]   ✗ FAILED: ['CSV not found: data/output/dim_highlight_type.csv']
[08:38:10] Loading fact_events_long...
[08:38:11]   ✗ FAILED: ['Schema mismatch: column "event_long_key" does not exist']
[08:38:11] Loading fact_events_tracking...
[08:38:11]   ✗ FAILED: ['Schema mismatch: column "tracking_key" does not exist']
[08:38:11] Loading fact_linked_events...
[08:38:11]   ✗ FAILED: ['Schema mismatch: column "link_key" does not exist']
[08:38:11] Loading fact_player_stats_long...
[08:38:12]   ✗ FAILED: ['Schema mismatch: column "stat_long_key" does not exist']
[08:38:12] Loading fact_player_boxscore_all...
[08:38:12]   ✗ FAILED: ['Schema mismatch: column "boxscore_key" does not exist']
[08:38:12] Loading fact_gameroster...
[08:38:12]   ✗ FAILED: ['Schema mismatch: column "roster_key" does not exist']
[08:38:12] Loading fact_game_status...
[08:38:12]   ✗ FAILED: ['no unique or exclusion constraint matching ON CONFLICT']
[08:38:12] Loading fact_head_to_head...
[08:38:13]   ✗ FAILED: ['Schema mismatch: column "matchup_key" does not exist']
[08:38:13] Loading fact_player_pair_stats...
[08:38:13]   ✗ FAILED: ['Schema mismatch: column "pair_key" does not exist']
[08:38:13] Loading fact_shift_quality...
[08:38:13]   ✗ FAILED: ['Schema mismatch: column "quality_key" does not exist']
[08:38:13] Loading fact_rush_events...
[08:38:13]   ✗ FAILED: ['Schema mismatch: column "rush_key" does not exist']
[08:38:16] Loading fact_registration...
[08:38:16]   ✗ FAILED: ['Schema mismatch: column "registration_key" does not exist']
[08:38:16] Loading fact_league_leaders_snapshot...
[08:38:16]   ✗ FAILED: ['Schema mismatch: column "leader_key" does not exist']
[08:38:16] Loading fact_team_standings_snapshot...
[08:38:16]   ✗ FAILED: ['Schema mismatch: column "standing_key" does not exist']
[08:38:16] Loading fact_suspicious_stats...
[08:38:16]   ✗ FAILED: ['Schema mismatch: column "suspicious_key" does not exist']
[08:38:16] Loading fact_video_highlights...
[08:38:16]   ✗ FAILED: ['CSV not found: data/output/fact_video_highlights.csv']
[08:38:16] Loading qa_suspicious_stats...
[08:38:16]   ✗ FAILED: ['Schema mismatch: column "qa_key" does not exist']

Tables: 7/25 successful
Failed: 18
```

---

## Priority

**This must be fixed before any frontend work begins.**

The Tracker needs to write to these tables. The Dashboard needs to read from them. Until Supabase is fully operational, frontend development is blocked.

### Recommended Approach

1. **Quick Win**: Focus on the tables that are actually needed for MVP
   - `fact_events` (already working)
   - `fact_shifts` (already working) 
   - `fact_player_game_stats` (already working)
   - `dim_*` tables (mostly working)
   - `fact_video_highlights` (new, needs creation)

2. **Defer**: Some tables may not be needed immediately
   - `fact_events_long`, `fact_player_stats_long` (denormalized views)
   - `fact_*_snapshot` (reporting tables)
   - `fact_registration` (future feature)

3. **Fix Core**: Ensure the 20-30 most important tables work perfectly before moving on.
