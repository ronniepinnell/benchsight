# Next Session Prompt for BenchSight

## Copy everything below this line and paste as your first message:

---

I'm continuing work on **BenchSight**, a hockey analytics ETL project. Here's the context:

## Project Status: 92% Complete

**What's Working:**
- Full ETL pipeline: Excel → 88 CSV tables (44 dim + 44 fact)
- 226 player stat columns including micro-stats, defender stats, composites
- 54 validations passing
- FK population at 77.8%

**Recent Session (Dec 29, 2024):**
- Added 161 new stat columns to fact_player_game_stats (65 → 226)
- Added micro-stats: dekes, screens, checks, breakouts, puck battles
- Added zone transitions: entry/exit types, controlled %, denials
- Added defender perspective: opp_player_1 stats
- Added composites: offensive/defensive/hustle ratings, WAR estimate
- Added xG placeholders (ready for XY data)
- Created 11 new tables including fact_shot_danger, fact_scoring_chances

**What's NOT Done:**
- Supabase deployment (DDL ready, not executed)
- Real xG model (needs XY coordinates)
- RAPM/WAR full models
- Power BI dashboards
- Only 4 of 10 games loaded

## Key Technical Details

```python
# Goal detection
event_type == 'Goal' OR event_detail in ['Goal_Scored', 'Shot_Goal']

# Player roles
event_player_1 = primary (shooter/passer)
event_player_2 = secondary (assist/target)
opp_player_1 = primary defender

# Success flags: 's'=success, 'u'=unsuccessful, blank=ignore
```

## Memory Notes
```
BenchSight delivery checklist: Run scripts/verify_delivery.py before packaging; 
include ALL files; verify goals match noradhockey.com.
Always provide complete project zip with updated docs.
```

## What I Need Help With Today:
[INSERT YOUR REQUEST HERE]

## Key Files to Read:
1. `docs/handoff/HANDOFF_COMPLETE_V3.md` - Full overview
2. `docs/STATS_CATALOG_COMPLETE.md` - All 226 stats
3. `docs/handoff/STATS_GAP_ANALYSIS.md` - Gap analysis

---

## Alternative Short Prompt:

---

Continuing BenchSight hockey analytics. Status: 92% complete, 88 tables, 226 player stats, 54 validations passing.

Recent: Added 161 stat columns (micro-stats, defender stats, composites, xG placeholders).

Key files in docs/handoff/. Goals detected via event_type='Goal' OR event_detail='Shot_Goal'/'Goal_Scored'.

Today I need: [YOUR REQUEST]

---

## Quick Commands Reference

```bash
# Run ETL
python etl.py

# Run stats enhancement
python src/enhance_all_stats.py

# Run validations
python scripts/test_validations.py

# Create package
zip -r benchsight_combined.zip benchsight_combined
```

## Table Quick Reference

| Table | Rows | Columns |
|-------|------|---------|
| fact_player_game_stats | 107 | 226 |
| fact_events_player | 11,635 | 64 |
| fact_events | 5,833 | 50+ |
| fact_shifts_player | 4,626 | 30+ |
| fact_h2h | 684 | 21 |
| fact_wowy | 641 | 25 |
| fact_line_combos | 200+ | 38 |
| fact_goalie_game_stats | 4 | 35 |

## Priority Tasks for Next Session

1. **P0: Supabase** - Deploy DDL, upload CSVs
2. **P1: More Games** - Load remaining 6 games
3. **P1: Power BI** - Build dashboards
4. **P2: Real xG** - When XY data available
5. **P3: RAPM/WAR** - Advanced models
