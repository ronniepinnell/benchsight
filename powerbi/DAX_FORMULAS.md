# Power BI DAX Formulas

## Table of Contents
1. [Basic Measures](#basic-measures)
2. [Rate Stats (Per 60 Minutes)](#rate-stats)
3. [Advanced Metrics](#advanced-metrics)
4. [Line Combo Analysis](#line-combo-analysis)
5. [Head-to-Head Matchups](#head-to-head-matchups)
6. [Expected Goals (xG)](#expected-goals)
7. [Player Scorecards](#player-scorecards)
8. [Team Over Time](#team-over-time)
9. [With/Without Analysis](#withwithout-analysis)
10. [Goalie Analysis](#goalie-analysis)
11. [Lineup Skill Analysis](#lineup-skill-analysis)
12. [NHL Edge Style Stats](#nhl-edge-style-stats)

---

## Basic Measures

### Points
```dax
Total Points = SUM(fact_box_score_tracking[points])

Goals = SUM(fact_box_score_tracking[goals])

Assists = SUM(fact_box_score_tracking[assists])

Primary Assists = SUM(fact_box_score_tracking[assists_primary])

Secondary Assists = SUM(fact_box_score_tracking[assists_secondary])
```

### Time on Ice
```dax
TOI (Minutes) = SUM(fact_box_score_tracking[toi_seconds]) / 60

TOI (Formatted) = 
VAR TotalSeconds = SUM(fact_box_score_tracking[toi_seconds])
VAR Minutes = INT(TotalSeconds / 60)
VAR Seconds = MOD(TotalSeconds, 60)
RETURN Minutes & ":" & FORMAT(Seconds, "00")

Average TOI Per Game = 
AVERAGEX(
    VALUES(fact_box_score_tracking[game_id]),
    CALCULATE(SUM(fact_box_score_tracking[toi_seconds]))
) / 60
```

### Shooting
```dax
Shots = SUM(fact_box_score_tracking[shots])

Shots on Goal = SUM(fact_box_score_tracking[shots_on_goal])

Shooting % = 
DIVIDE(
    SUM(fact_box_score_tracking[goals]),
    SUM(fact_box_score_tracking[shots_on_goal]),
    0
) * 100
```

### Plus/Minus
```dax
Plus Minus = SUM(fact_box_score_tracking[plus_minus])

Plus Minus Per Game = 
AVERAGEX(
    VALUES(fact_box_score_tracking[game_id]),
    CALCULATE(SUM(fact_box_score_tracking[plus_minus]))
)
```

---

## Rate Stats

### Per 60 Minutes Rates
```dax
Goals Per 60 = 
VAR TotalGoals = SUM(fact_box_score_tracking[goals])
VAR TotalTOI = SUM(fact_box_score_tracking[toi_seconds])
RETURN DIVIDE(TotalGoals * 3600, TotalTOI, 0)

Assists Per 60 = 
VAR TotalAssists = SUM(fact_box_score_tracking[assists])
VAR TotalTOI = SUM(fact_box_score_tracking[toi_seconds])
RETURN DIVIDE(TotalAssists * 3600, TotalTOI, 0)

Points Per 60 = 
VAR TotalPoints = SUM(fact_box_score_tracking[points])
VAR TotalTOI = SUM(fact_box_score_tracking[toi_seconds])
RETURN DIVIDE(TotalPoints * 3600, TotalTOI, 0)

Shots Per 60 = 
VAR TotalShots = SUM(fact_box_score_tracking[shots])
VAR TotalTOI = SUM(fact_box_score_tracking[toi_seconds])
RETURN DIVIDE(TotalShots * 3600, TotalTOI, 0)
```

### Micro-Stat Rates
```dax
Takeaways Per 60 = 
DIVIDE(SUM(fact_box_score_tracking[takeaways]) * 3600, 
       SUM(fact_box_score_tracking[toi_seconds]), 0)

Giveaways Per 60 = 
DIVIDE(SUM(fact_box_score_tracking[giveaways]) * 3600, 
       SUM(fact_box_score_tracking[toi_seconds]), 0)

Stick Checks Per 60 = 
DIVIDE(SUM(fact_box_score_tracking[stick_checks]) * 3600, 
       SUM(fact_box_score_tracking[toi_seconds]), 0)
```

---

## Advanced Metrics

### Corsi (Shot Attempts)
```dax
Corsi For (CF) = 
CALCULATE(
    COUNTROWS(fact_events_tracking),
    fact_events_tracking[Type] = "Shot",
    dim_event_type[is_corsi] = TRUE()
)

Corsi Against (CA) = 
// Requires knowing opposing team
CALCULATE(
    COUNTROWS(fact_events_tracking),
    fact_events_tracking[Type] = "Shot",
    dim_event_type[is_corsi] = TRUE(),
    fact_events_tracking[event_team] <> SELECTEDVALUE(dim_team[team_name])
)

Corsi % = 
VAR CF = [Corsi For (CF)]
VAR CA = [Corsi Against (CA)]
RETURN DIVIDE(CF, CF + CA, 0.5) * 100
```

### Fenwick (Unblocked Shot Attempts)
```dax
Fenwick For = 
CALCULATE(
    COUNTROWS(fact_events_tracking),
    fact_events_tracking[Type] = "Shot",
    dim_event_type[is_fenwick] = TRUE()
)

Fenwick % = 
VAR FF = [Fenwick For]
VAR FA = [Fenwick Against]
RETURN DIVIDE(FF, FF + FA, 0.5) * 100
```

### PDO (Luck Indicator)
```dax
PDO = 
VAR ShootPct = [Shooting %]
VAR SavePct = [Save %]
RETURN ShootPct + SavePct

// PDO around 100 is average, >100 is lucky, <100 is unlucky
```

### Zone Starts
```dax
Offensive Zone Starts = 
CALCULATE(
    COUNTROWS(fact_shifts_tracking),
    fact_shifts_tracking[shift_start_type] = "faceoff",
    // Need zone info from faceoff
)

OZ Start % = 
DIVIDE([Offensive Zone Starts], 
       [Offensive Zone Starts] + [Defensive Zone Starts], 0.5) * 100
```

---

## Line Combo Analysis

### Line Combination Performance
```dax
// First, create a calculated table for line combos
LineComboTable = 
SUMMARIZE(
    fact_shift_players_tracking,
    fact_shift_players_tracking[shift_key],
    "Forward1", MINX(FILTER(fact_shift_players_tracking, 
                    fact_shift_players_tracking[position_type] = "forward"), 
                    [player_game_number]),
    "Forward2", MAXX(FILTER(fact_shift_players_tracking,
                    fact_shift_players_tracking[position_type] = "forward"),
                    [player_game_number]),
    "Defense1", MINX(FILTER(fact_shift_players_tracking,
                    fact_shift_players_tracking[position_type] = "defense"),
                    [player_game_number])
)

// Goals For per Line
Line Goals For = 
VAR CurrentShifts = SELECTEDVALUE(LineComboTable[shift_key])
RETURN
CALCULATE(
    COUNTROWS(fact_events_tracking),
    fact_events_tracking[event_detail] = "Goal_Scored",
    fact_events_tracking[shift_key] IN VALUES(LineComboTable[shift_key])
)

// TOI Together
Line TOI Together = 
SUMX(
    VALUES(LineComboTable[shift_key]),
    CALCULATE(SUM(fact_shifts_tracking[shift_duration]))
) / 60
```

### Players Together Stats
```dax
// Create measure with player pair as parameter
Players Together Goals = 
VAR Player1 = SELECTEDVALUE(PlayerPairTable[Player1])
VAR Player2 = SELECTEDVALUE(PlayerPairTable[Player2])
VAR SharedShifts = 
    CALCULATETABLE(
        VALUES(fact_shift_players_tracking[shift_key]),
        fact_shift_players_tracking[player_game_number] = Player1
    ) ∩ 
    CALCULATETABLE(
        VALUES(fact_shift_players_tracking[shift_key]),
        fact_shift_players_tracking[player_game_number] = Player2
    )
RETURN
CALCULATE(
    COUNTROWS(fact_events_tracking),
    fact_events_tracking[event_detail] = "Goal_Scored",
    fact_events_tracking[shift_key] IN SharedShifts
)
```

---

## Head-to-Head Matchups

### Player vs Player
```dax
H2H Goals Scored = 
VAR MyPlayer = SELECTEDVALUE(dim_game_players_tracking[player_game_number])
VAR Opponent = SELECTEDVALUE(OpponentPlayerTable[player_game_number])
VAR MatchupShifts = 
    CALCULATETABLE(
        VALUES(fact_shift_players_tracking[shift_key]),
        fact_shift_players_tracking[player_game_number] = MyPlayer
    ) ∩ 
    CALCULATETABLE(
        VALUES(fact_shift_players_tracking[shift_key]),
        fact_shift_players_tracking[player_game_number] = Opponent
    )
RETURN
CALCULATE(
    COUNTROWS(fact_events_tracking),
    fact_events_tracking[event_detail] = "Goal_Scored",
    fact_events_tracking[shift_key] IN MatchupShifts,
    fact_event_players_tracking[player_game_number] = MyPlayer
)

H2H Shots Against = 
// Similar logic, but count opponent's shots
```

### Team vs Team
```dax
vs Opponent Goals = 
CALCULATE(
    SUM(fact_box_score_tracking[goals]),
    USERELATIONSHIP(dim_schedule[away_team], dim_team[team_name])
)

vs Opponent Record = 
VAR Wins = CALCULATE(COUNTROWS(fact_gameroster), [Result] = "W")
VAR Losses = CALCULATE(COUNTROWS(fact_gameroster), [Result] = "L")
RETURN Wins & "-" & Losses
```

---

## Expected Goals

### xG Calculation
```dax
xG = 
SUMX(
    fact_events_tracking,
    VAR Distance = fact_events_tracking[distance_to_goal]
    VAR Angle = fact_events_tracking[shot_angle]
    VAR BaseXG = 0.35 * EXP(-0.045 * Distance)
    VAR AngleFactor = COS(RADIANS(Angle * 0.8))
    RETURN BaseXG * MAX(AngleFactor, 0.3)
)

xG Per Shot = DIVIDE([xG], [Shots], 0)

Goals Above Expected = [Goals] - [xG]
```

### xG by Zone
```dax
High Danger xG = 
CALCULATE(
    [xG],
    fact_events_tracking[danger_zone] = "HD"
)

High Danger Shot % = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_events_tracking), 
              fact_events_tracking[danger_zone] = "HD"),
    COUNTROWS(fact_events_tracking),
    0
) * 100
```

---

## Player Scorecards

### Overall Rating
```dax
Player Game Score = 
// Based on hockey-reference game score formula
VAR G = [Goals]
VAR A1 = [Primary Assists]
VAR A2 = [Secondary Assists]
VAR SOG = [Shots on Goal]
VAR BLK = [Blocked Shots]
VAR PIM = [Penalty Minutes]
VAR GV = [Giveaways]
VAR TK = [Takeaways]
VAR FOW = [Faceoff Wins]
VAR FOL = [Faceoffs] - [Faceoff Wins]
RETURN
G * 0.75 + A1 * 0.7 + A2 * 0.55 + SOG * 0.075 + 
BLK * 0.05 - PIM * 0.15 - GV * 0.1 + TK * 0.1 +
FOW * 0.01 - FOL * 0.01

Player Rating vs Avg = 
VAR PlayerScore = [Player Game Score]
VAR AvgScore = AVERAGEX(ALL(fact_box_score_tracking), [Player Game Score])
RETURN PlayerScore - AvgScore
```

### Defensive Rating
```dax
Defensive Score = 
VAR TK = [Takeaways Per 60]
VAR BLK = [Blocked Shots Per 60]
VAR SC = [Stick Checks Per 60]
VAR GV = [Giveaways Per 60]
RETURN (TK * 2 + BLK * 1.5 + SC * 0.5 - GV * 1.5)
```

### Offensive Rating  
```dax
Offensive Score = 
VAR PPG = [Points Per 60]
VAR SPG = [Shots Per 60]
VAR DK = [Dekes Per 60]
VAR ZE = [Zone Entries Per 60]
RETURN (PPG * 3 + SPG * 0.5 + DK * 0.3 + ZE * 0.5)
```

---

## Team Over Time

### Rolling Averages
```dax
Goals Last 5 Games = 
VAR CurrentGame = SELECTEDVALUE(dim_schedule[game_id])
VAR Last5Games = 
    TOPN(5,
        FILTER(
            ALL(dim_schedule),
            dim_schedule[game_id] < CurrentGame &&
            dim_schedule[home_team] = SELECTEDVALUE(dim_team[team_name])
        ),
        dim_schedule[game_id], DESC
    )
RETURN
CALCULATE(
    SUM(fact_box_score_tracking[goals]),
    dim_schedule[game_id] IN Last5Games
)

Win % Last 10 = 
// Similar rolling window calculation
```

### Cumulative Stats
```dax
Cumulative Goals = 
CALCULATE(
    SUM(fact_box_score_tracking[goals]),
    FILTER(
        ALL(dim_schedule),
        dim_schedule[game_date] <= MAX(dim_schedule[game_date])
    )
)

Cumulative Points = 
// Track points (wins/losses) over season
```

---

## With/Without Analysis

### Team With Player
```dax
Team Goals With Player = 
VAR SelectedPlayer = SELECTEDVALUE(dim_player[player_id])
VAR GamesWithPlayer = 
    CALCULATETABLE(
        VALUES(dim_schedule[game_id]),
        FILTER(fact_gameroster, fact_gameroster[player_id] = SelectedPlayer)
    )
RETURN
CALCULATE(
    SUM(fact_box_score_tracking[goals]),
    dim_schedule[game_id] IN GamesWithPlayer
)

Team Goals Without Player = 
VAR SelectedPlayer = SELECTEDVALUE(dim_player[player_id])
VAR GamesWithPlayer = 
    CALCULATETABLE(
        VALUES(dim_schedule[game_id]),
        FILTER(fact_gameroster, fact_gameroster[player_id] = SelectedPlayer)
    )
VAR AllTeamGames = VALUES(dim_schedule[game_id])
VAR GamesWithoutPlayer = EXCEPT(AllTeamGames, GamesWithPlayer)
RETURN
CALCULATE(
    SUM(fact_box_score_tracking[goals]),
    dim_schedule[game_id] IN GamesWithoutPlayer
)

With/Without Differential = 
[Team Goals With Player] / [Games With Player] - 
[Team Goals Without Player] / [Games Without Player]
```

### Impact Score
```dax
Player Impact Score = 
VAR WithAvg = DIVIDE([Team Goals With Player], [Games With Player], 0)
VAR WithoutAvg = DIVIDE([Team Goals Without Player], [Games Without Player], 0)
VAR Diff = WithAvg - WithoutAvg
RETURN 
IF(ISBLANK(WithoutAvg), BLANK(),
   Diff / WithoutAvg * 100)  // % impact
```

---

## Goalie Analysis

### Save Percentage
```dax
Save % = 
VAR Saves = SUM(fact_box_score_tracking[saves])
VAR ShotsAgainst = Saves + SUM(fact_box_score_tracking[goals_against])
RETURN DIVIDE(Saves, ShotsAgainst, 0) * 100

High Danger Save % = 
CALCULATE(
    [Save %],
    fact_events_tracking[danger_zone] = "HD"
)
```

### Goals Against Average
```dax
GAA = 
VAR GoalsAgainst = SUM(fact_box_score_tracking[goals_against])
VAR MinutesPlayed = SUM(fact_box_score_tracking[toi_seconds]) / 60
RETURN DIVIDE(GoalsAgainst * 60, MinutesPlayed, 0)
```

### Goalie vs Team
```dax
Save % vs Team = 
CALCULATE(
    [Save %],
    USERELATIONSHIP(dim_schedule[away_team], dim_team[team_name])
)
```

### Quality Start %
```dax
Quality Start = 
// QS = Save% > 91.7% or GAA < 2.33
IF([Save %] > 91.7 || [GAA] < 2.33, 1, 0)

Quality Start % = 
DIVIDE(
    SUMX(VALUES(dim_schedule[game_id]), [Quality Start]),
    COUNTROWS(VALUES(dim_schedule[game_id])),
    0
) * 100
```

---

## Lineup Skill Analysis

### Average Lineup Skill
```dax
Avg Lineup Skill = 
AVERAGEX(
    FILTER(fact_gameroster, NOT(ISBLANK(fact_gameroster[skill_rating]))),
    fact_gameroster[skill_rating]
)

Lineup Skill by Position = 
CALCULATE(
    AVERAGE(fact_gameroster[skill_rating]),
    fact_gameroster[player_position] = "F"  // or "D", "G"
)
```

### Skill Matchup
```dax
Skill Advantage = 
VAR HomeSkill = CALCULATE([Avg Lineup Skill], 
                          fact_gameroster[team_venue] = "home")
VAR AwaySkill = CALCULATE([Avg Lineup Skill],
                          fact_gameroster[team_venue] = "away")
RETURN HomeSkill - AwaySkill

Win % When Skill Advantage = 
VAR WinsWithAdvantage = 
    CALCULATE(
        COUNTROWS(dim_schedule),
        [Skill Advantage] > 0,
        [Result] = "W"
    )
VAR GamesWithAdvantage = 
    CALCULATE(COUNTROWS(dim_schedule), [Skill Advantage] > 0)
RETURN DIVIDE(WinsWithAdvantage, GamesWithAdvantage, 0) * 100
```

---

## NHL Edge Style Stats

### Speed & Distance
```dax
// If XY tracking available
Distance Skated = 
// Calculate from player position changes
SUMX(
    fact_events_tracking,
    SQRT(
        POWER(fact_events_tracking[event_x2] - fact_events_tracking[event_x1], 2) +
        POWER(fact_events_tracking[event_y2] - fact_events_tracking[event_y1], 2)
    )
)

Top Speed = 
// Requires more granular tracking
```

### Shot Speed
```dax
Avg Shot Distance = 
AVERAGEX(
    FILTER(fact_events_tracking, fact_events_tracking[Type] = "Shot"),
    fact_events_tracking[distance_to_goal]
)
```

### Puck Possession
```dax
Possession Time = 
VAR TeamEvents = 
    COUNTROWS(FILTER(fact_events_tracking, 
                     fact_events_tracking[event_team] = SELECTEDVALUE(dim_team[team_name])))
VAR TotalEvents = COUNTROWS(fact_events_tracking)
RETURN DIVIDE(TeamEvents, TotalEvents, 0.5) * 100
```

### Zone Time
```dax
OZ Time % = 
CALCULATE(
    COUNT(fact_events_tracking[event_index]),
    fact_events_tracking[event_team_zone] = "OZ"
) / COUNT(fact_events_tracking[event_index]) * 100

DZ Time % = 
// Similar for defensive zone
```

---

## Utility Measures

### Conditional Formatting Values
```dax
Performance Color = 
SWITCH(
    TRUE(),
    [Player Game Score] > 2, "#28a745",  // Green - Excellent
    [Player Game Score] > 0, "#17a2b8",  // Blue - Above Avg
    [Player Game Score] > -1, "#ffc107", // Yellow - Below Avg
    "#dc3545"  // Red - Poor
)
```

### Ranking
```dax
Goals Rank = 
RANKX(
    ALL(dim_player),
    [Goals],
    ,
    DESC,
    Dense
)
```

### Season-to-Date
```dax
STD Goals = 
CALCULATE(
    SUM(fact_box_score_tracking[goals]),
    DATESYTD(dim_schedule[game_date])
)
```
