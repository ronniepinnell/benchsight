# Next Session Prompt for BenchSight V3

## 📋 COPY EVERYTHING BELOW THIS LINE:

---

I'm continuing work on **BenchSight**, a hockey analytics ETL project for the NORAD recreational hockey league.

## 📊 Project Status: 98% Complete

### What's Working:
- Full ETL pipeline: Excel → 88 CSV tables (44 dim + 44 fact)
- **317 player stat columns** in fact_player_game_stats
- 54 validations passing, 0 failed
- FK population at 77.8%

### Recent Session (Dec 29, 2024) - Major Enhancement:
Added 252 new stat columns total (65 → 317):

**Phase 1 (+161 columns):**
- Micro-stats: dekes, screens, poke checks, stick checks, backchecks, forechecks
- Zone transitions: entry/exit types, controlled %, denials
- Defender perspective: opp_player_1 stats (shots against, beat by deke)
- Composites: offensive/defensive/hustle ratings, WAR estimate
- xG placeholders (ready for XY data)
- Beer league metrics: shift warnings, fatigue, sub equity

**Phase 2 (+91 columns):**
- **Game Score**: single-number performance metric per game
- **Performance vs Rating**: Is a 3-rated player playing at 3.5 level?
- **Success Flags**: Using s=success, u=unsuccessful (blanks ignored)
- **Pass Targets**: event_player_2 stats (times targeted, reception rate)
- **Rush Types**: odd man rushes, breakaways, transition plays
- **Opponent Targeting**: How often opponents attack this player
- **Secondary Roles**: EP3/EP4, support plays, involvement rate
- **Contextual**: Points by period, clutch factor
- **Advanced Derived**: two-way rating, efficiency score, complete player score

### What's NOT Done (2%):
- Supabase deployment (DDL ready, not executed)
- Real xG model (needs XY coordinates)
- RAPM/WAR full models
- Power BI dashboards
- Only 4 of 10 games loaded

## 🔑 Key Technical Details

```python
# Goal detection
event_type == 'Goal' OR event_detail in ['Goal_Scored', 'Shot_Goal']

# Player roles
event_player_1 = primary (shooter/passer)
event_player_2 = secondary (assist/pass target)
opp_player_1 = primary defender

# Success flags
's' = success, 'u' = unsuccessful, blank = ignore

# Game Score formula
game_score = G*0.75 + A1*0.7 + A2*0.55 + SOG*0.075 + BLK*0.05 + ...

# Performance vs Rating
effective_game_rating = calculated from performance (2-6 scale)
rating_performance_delta = effective - actual (positive = above rating)
```

## 🧠 Memory Notes
```
BenchSight delivery checklist: Run scripts/verify_delivery.py before packaging; 
include ALL files; verify goals match noradhockey.com.
Always provide complete project zip with updated docs.
317 player stat columns, 88 tables, 54 validations.
```

## 📁 Key Files to Read:
1. `docs/handoff/HANDOFF_COMPLETE_V4.md` - Full overview (THIS SESSION)
2. `docs/STATS_CATALOG_COMPLETE.md` - All 317 stats documented
3. `src/final_stats_enhancement.py` - New stats code

## What I Need Help With Today:
[INSERT YOUR REQUEST HERE]

---

## 🚀 ALTERNATIVE SHORT PROMPT:

---

Continuing BenchSight hockey analytics. **98% complete**, 88 tables, **317 player stats**, 54 validations passing.

Key new features this session:
- `game_score` - single-number performance metric
- `rating_performance_delta` - playing above/below rating
- `times_pass_target` - when player is pass recipient
- `times_targeted_by_opp` - defensive pressure stats
- `odd_man_rushes`, `breakaway_goals` - rush types
- Success flag aggregations (s/u, ignore blanks)

Technical: Goals via event_type='Goal' OR event_detail='Shot_Goal'. Player roles: event_player_1=primary, opp_player_1=defender.

Today I need: [YOUR REQUEST]

---

## ⚡ Quick Commands Reference

```bash
# Run ETL
python etl.py

# Run stats enhancement (both phases)
python src/enhance_all_stats.py
python src/final_stats_enhancement.py

# Run validations
python scripts/test_validations.py

# Create package
zip -r benchsight_combined.zip benchsight_combined -x "*.pyc" -x "*__pycache__*"
```

## 📊 Table Quick Reference

| Table | Rows | Columns |
|-------|------|---------|
| fact_player_game_stats | 107 | **317** |
| fact_events_player | 11,635 | 64 |
| fact_events | 5,833 | 50+ |
| fact_shifts_player | 4,626 | 30+ |
| fact_h2h | 684 | 21 |
| fact_wowy | 641 | 25 |
| fact_line_combos | 200+ | 38 |
| fact_goalie_game_stats | 4 | 35 |

## 📋 Priority Tasks for Next Session

### P0 - Immediate
1. **Supabase Deployment** - Run DDL, upload CSVs
2. **Test with Real Data** - Verify stats accuracy

### P1 - Short Term
1. **More Games** - Load remaining 6 games
2. **Power BI** - Build dashboards
3. **Season Aggregates** - Create fact_player_season_stats

### P2 - Long Term
1. **Real xG** - When XY data available
2. **RAPM Model** - Ridge regression
3. **API Development** - REST endpoints

## 📈 New Stat Categories Explained

### Game Score (3 stats)
- `game_score` - Raw performance score
- `game_score_per_60` - Normalized to 60 min
- `game_score_rating` - 0-100 scale (50=avg)

### Performance vs Rating (7 stats)
- `effective_game_rating` - Calculated 2-6 rating
- `rating_performance_delta` - +0.5 = playing half-rating above
- `performance_tier` - 'exceptional'/'overperforming'/'struggling'/etc
- `performance_index` - 100 = at rating

### Success Flags (16 stats)
- `shots_successful/unsuccessful` - With flags
- `overall_success_rate` - All plays %
- `play_success_rate` - Micro-plays %

### Pass Targets (8 stats)
- `times_pass_target` - As recipient
- `pass_reception_rate` - Success %
- `times_target_oz/nz/dz` - By zone

### Rush Types (13 stats)
- `odd_man_rushes`, `breakaway_attempts/goals`
- `rush_entries/shots/goals`
- `transition_plays`

### Opponent Targeting (10 stats)
- `times_targeted_by_opp` - Total attacks
- `defensive_success_rate` - % stopped

### Advanced (12 stats)
- `offensive_contribution` - Weighted offense
- `defensive_contribution` - Weighted defense
- `complete_player_score` - All-around rating
