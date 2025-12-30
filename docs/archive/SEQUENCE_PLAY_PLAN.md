# SEQUENCE/PLAY AUTO-GENERATION - PROPOSED PLAN

## Summary

I've built and tested auto-generation logic for `sequence_index` and `play_index`.

### Results from 4 Complete Games (18969, 18977, 18981, 18987)

| Metric | Auto-Generated | TXT File Reference |
|--------|---------------|-------------------|
| Sequences | 376 | 946 |
| Plays | 2,744 | 3,390 |
| Goals (sequences with) | 16 | - |
| Shots (plays with) | 400 | - |

**Note:** TXT file had 8 games; I have 4 complete games. Games 18965, 18991, 19032 have incomplete tracking data (mostly NaN event types).

---

## CURRENT TRIGGER LOGIC

### SEQUENCE (New sequence starts when:)
```
- Faceoff (any type)
- Goal
- GameStart
- Stoppage
- Intermission/Period change
```

### PLAY (New play starts when:)
```
- Zone change (o → n → d)
- Possession change (Turnover_Giveaway, Turnover_Takeaway, Pass_Intercepted)
- Team changes
```

---

## QUESTIONS FOR YOU

1. **Sequence Triggers** - Is this list correct?
   - Faceoff = YES (always new sequence)
   - Goal = YES (ends sequence, new one starts after faceoff)
   - Stoppage = YES (whistle = break)
   - **What about Turnover?** Should Turnover_Giveaway/Takeaway start a NEW SEQUENCE or just a new PLAY?
   
2. **Play Triggers** - Current logic:
   - Zone change = new play
   - Turnover = new play
   - **Is this granular enough?** The current avg is 2.1 events per play.

3. **Goal Attribution** - Currently a sequence containing a goal is marked `has_goal=True`. But:
   - Should the goal END that sequence?
   - Or should the goal be the START of a new sequence (since faceoff follows)?
   - **Current behavior:** Goal triggers new sequence, so goal is in its own 1-event sequence

4. **Incomplete Games** - Games 18965, 18991, 19032 have incomplete event types. Should I:
   - Exclude them from processing
   - Flag them in output
   - Try to infer from other columns

---

## WHAT THE AUTO-GENERATOR PRODUCES

### fact_events (enhanced)
| Column | Description |
|--------|-------------|
| sequence_index_auto | Auto-generated sequence number |
| play_index_auto | Auto-generated play number |

### fact_sequences
| Column | Description |
|--------|-------------|
| sequence_id | `SQ{game_id:05d}{seq:05d}` |
| game_id | Game identifier |
| first_event | First event_index in sequence |
| last_event | Last event_index in sequence |
| event_count | Number of events |
| start_team | Team at sequence start |
| end_team | Team at sequence end |
| start_zone | Zone at start |
| end_zone | Zone at end |
| has_goal | Did sequence result in goal? |
| duration_seconds | Time span |

### fact_plays
| Column | Description |
|--------|-------------|
| play_id | `PL{game_id:05d}{play:05d}` |
| sequence_id | Parent sequence |
| game_id | Game identifier |
| first_event | First event_index |
| last_event | Last event_index |
| event_count | Number of events |
| team | Team with possession |
| zone | Zone (o/n/d) |
| has_shot | Did play result in shot? |
| duration_seconds | Time span |

---

## PROPOSED NEXT STEPS

### Option A: Minimal Changes
1. Integrate current logic into ETL pipeline
2. Add `sequence_index_auto` and `play_index_auto` to fact_events
3. Generate fact_sequences and fact_plays tables
4. Remove manual `sequence_index_flag_` from tracking requirement

### Option B: Refine Triggers (Recommended)
1. Review trigger logic with you
2. Adjust based on your feedback
3. Test on one game, verify visually
4. Then integrate into ETL

### Option C: Full Implementation
1. Refine triggers
2. Integrate into ETL
3. Add derived analytics:
   - Turnovers leading to goals (sequence analysis)
   - Zone time per team
   - Possession chains
   - Shot generation by play type

---

## FILES CREATED

| File | Purpose |
|------|---------|
| `src/sequence_play_generator.py` | Auto-generation logic |

---

## YOUR INPUT NEEDED

1. **Confirm sequence triggers** - Is Turnover a sequence break or just play break?
2. **Confirm play triggers** - Zone + possession change correct?
3. **Goal handling** - Goal ends sequence (current) vs goal starts new sequence?
4. **Which option** (A/B/C) do you want to proceed with?

---

*Generated: 2024-12-28*
