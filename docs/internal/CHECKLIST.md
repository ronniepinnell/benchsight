# BenchSight Development Checklist

## PRE-COMMIT CHECKLIST - MUST VERIFY BEFORE EVERY DELIVERY

### Data Integrity
- [ ] All fact tables have FK columns WITH readable names (both ID and name)
- [ ] All fact tables have player_game_number where players are referenced
- [ ] Stats are calculated from event_player_1 (the player making the play)
- [ ] Success/unsuccessful (s/u) flags are used for microstat calculations
- [ ] TOI is calculated and > 0 for players with shifts
- [ ] Goals match between fact_events_tracking and fact_player_game_stats
- [ ] Assists properly tracked (A1, A2)
- [ ] Rating context preserved (own rating, opponent rating, rating diff)

### Dimension Tables
- [ ] All dimension tables have analytical columns (not just IDs/names)
- [ ] dim_net_location has XY coordinates
- [ ] Zone entry/exit have control levels and expected values
- [ ] Shot types have xG modifiers
- [ ] All tables from previous versions still exist (no deletions without discussion)

### Analytics Context
- [ ] Shift-level skill ratings (home avg, away avg, skill diff)
- [ ] Event-level opponent context
- [ ] WOWY/H2H tables present and populated
- [ ] Boxscore stats match event counts

### Documentation
- [ ] CHANGELOG.md updated with version changes
- [ ] HANDOFF.md reflects current state
- [ ] KNOWLEDGE_LOG.md updated with new learnings

## STAT CALCULATION RULES

### Event Attribution
- event_player_1 = Player making the play (shooter, passer, etc.)
- event_player_2 = Secondary player (assist, defender, etc.)  
- event_player_3 = Tertiary player (second assist)

### Success Flags
- 's' = successful (pass completed, shot on goal, etc.)
- 'u' = unsuccessful (pass missed, shot blocked, etc.)
- blank = neutral/not applicable

### TOI Calculation
- Sum shift durations where player appears in any slot
- Shift duration = shift_end_sec - shift_start_sec

### Goals
- Event type ET0006 with event_detail containing "Goal"
- OR event_detail_id containing "Goal_Scored" or "Shot_Goal"
