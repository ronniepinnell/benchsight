# How to Figure Out What Stats to Add to Player Pages

## Step 1: Check What's Currently Displayed

### Currently Shown on Player Pages:
1. **Basic Stats** (Top Cards):
   - Games Played (GP)
   - Goals
   - Assists
   - Points
   - Points per Game (P/G)

2. **Advanced Stats Section** (Collapsible Cards):
   - **Possession**: CF%, FF%, Corsi For/Against, Fenwick For/Against, Expected Goals, Goals - xG
   - **Zone Play**: Zone Entry %, Zone Exit %, Entries/Exits
   - **WAR/GAR**: Total WAR, Total GAR, Avg Game Score, Avg Rating
   - **Physical**: Hits, Blocks, Takeaways, Giveaways, TO Differential
   - **Shooting**: Shooting %, Shot Accuracy, Total Shots, SOG, Shots/Game
   - **Per-60 Rates**: Goals/60, Assists/60, Points/60, Avg TOI
   - **Faceoffs**: Faceoff %, Wins, Losses, Total, Wins/Game
   - **Passing**: Pass %, Attempts, Completed, Per Game
   - **Situational**: 5v5 TOI/Goals, PP TOI/Goals, PK TOI/Goals

3. **Additional Stats**:
   - **Shooting**: Shots, Shooting %, +/-
   - **Discipline**: PIM, Minor Penalties, Major Penalties

4. **Game Log**:
   - Date, Opponent, G, A, P, S, +/-, TOI, CF%

## Step 2: Explore Available Stats in Database

### Method 1: Query the Database Directly

Run this SQL query in Supabase to see ALL available columns:

```sql
-- See all columns in fact_player_game_stats
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'fact_player_game_stats'
ORDER BY ordinal_position;
```

### Method 2: Check TypeScript Types

Look at `ui/dashboard/src/types/database.ts` - the `FactPlayerGameStats` interface shows what's available.

### Method 3: Query Sample Data

```sql
-- Get a sample row to see what data exists
SELECT * 
FROM fact_player_game_stats 
WHERE player_id = 'P100001' 
LIMIT 1;
```

## Step 3: Identify Missing Stats

Based on the database schema, here are stats that might be available but NOT currently displayed:

### Potential Missing Stats:

1. **Time on Ice Details**:
   - Average shift length
   - Total shifts
   - TOI per game average

2. **Shot Details**:
   - Shots blocked
   - Shots missed
   - Shot accuracy breakdown

3. **Plus/Minus Variants**:
   - Even strength +/- (plus_minus_ev)
   - Plus events (plus_ev)
   - Minus events (minus_ev)

4. **Assist Breakdown**:
   - Primary assists
   - Secondary assists

5. **Penalty Details**:
   - Penalty minutes per game
   - Penalty types breakdown

6. **Relative Stats**:
   - CF% Relative (cf_pct_rel)
   - FF% Relative (ff_pct_rel)
   - GF% (goals for %)
   - GF% Relative

7. **Performance Metrics**:
   - Performance index
   - Adjusted rating
   - Rating vs competition
   - Rating differential

8. **Situational Breakdown**:
   - More detailed 5v5, PP, PK stats
   - Empty net situations
   - 4v4, 3v3 situations

## Step 4: Prioritize Stats to Add

### Questions to Ask:

1. **What do users need most?**
   - What questions are they trying to answer?
   - What comparisons do they make?

2. **What's the data quality?**
   - Are the stats consistently populated?
   - Are they reliable?

3. **What's the visual priority?**
   - Should it be in the main cards?
   - Advanced stats section?
   - Game log?

4. **What's standard in hockey analytics?**
   - What do other sites show?
   - What do coaches/GMs care about?

## Step 5: Test and Validate

1. **Check Data Availability**:
   ```sql
   -- See how many players have data for a specific stat
   SELECT 
     COUNT(*) as total_players,
     COUNT(primary_assists) as has_primary_assists,
     COUNT(secondary_assists) as has_secondary_assists
   FROM fact_player_game_stats
   WHERE player_id IN (SELECT player_id FROM dim_player LIMIT 100);
   ```

2. **Check Data Quality**:
   ```sql
   -- See if stats make sense (e.g., assists = primary + secondary)
   SELECT 
     player_id,
     assists,
     primary_assists,
     secondary_assists,
     (primary_assists + secondary_assists) as calculated_assists
   FROM fact_player_game_stats
   WHERE assists != (primary_assists + secondary_assists)
   LIMIT 10;
   ```

## Step 6: Implementation Checklist

When adding a new stat:

- [ ] Verify the stat exists in the database
- [ ] Check data quality (not all null/zero)
- [ ] Decide where to display it (main cards, advanced section, game log)
- [ ] Add to TypeScript types if needed
- [ ] Update the query to fetch the stat
- [ ] Add to the UI component
- [ ] Format appropriately (percentage, per-60, etc.)
- [ ] Add tooltip/description
- [ ] Test with multiple players
- [ ] Handle null/zero values gracefully

## Quick Reference: Common Hockey Stats

### Basic Offensive:
- Goals, Assists, Points
- Points per Game
- Goals per Game
- Assists per Game

### Shooting:
- Shots on Goal (SOG)
- Shooting Percentage
- Shot Accuracy
- Shots per Game

### Possession:
- Corsi For % (CF%)
- Fenwick For % (FF%)
- Expected Goals (xG)
- Goals Above Expected

### Time on Ice:
- Total TOI
- Average TOI per Game
- TOI per 60 minutes
- Shift Count
- Average Shift Length

### Situational:
- 5v5 stats
- Power Play stats
- Penalty Kill stats
- Empty Net stats

### Advanced:
- WAR (Wins Above Replacement)
- GAR (Goals Above Replacement)
- Game Score
- Player Rating
