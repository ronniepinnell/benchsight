// Stat definitions with formulas, calculations, and descriptions
export interface StatDefinition {
  name: string
  formula: string
  description: string
  calculation: string
  context: string
  category: 'possession' | 'shooting' | 'defense' | 'offense' | 'goaltending' | 'advanced' | 'physical' | 'situational'
  examples?: string
  benchmarks?: string
  interpretation?: string
  similarStats?: string[]
}

export const STAT_DEFINITIONS: Record<string, StatDefinition> = {
  // Possession Stats
  'CF%': {
    name: 'Corsi For Percentage',
    formula: 'CF% = (CF / (CF + CA)) × 100',
    description: 'Percentage of shot attempts (shots, blocks, misses) for vs against when player is on ice. Measures puck possession and shot generation.',
    calculation: 'Corsi For / (Corsi For + Corsi Against) × 100\nExample: If CF=60 and CA=40, then CF% = (60/(60+40))×100 = 60%',
    context: 'Higher is better. 50% = even, >50% = outshooting opponent. Strong predictor of future goal differential.',
    examples: '60% CF% means team generated 60 shot attempts for every 40 against when player was on ice. This suggests strong offensive pressure and possession control.',
    benchmarks: 'Elite: >55% | Excellent: 52-55% | Good: 50-52% | Average: 48-50% | Below Average: <48%',
    interpretation: 'A 55% CF% player typically outshoots opponents by about 22% more shot attempts. Over a season, this translates to roughly +15-20 goals per 82 games. CF% is more stable than goal percentage and better predicts future performance.',
    similarStats: ['FF%', 'GF%', 'xGF%'],
    category: 'possession'
  },
  'CF': {
    name: 'Corsi For',
    formula: 'CF = Shots + Blocked Shots + Missed Shots',
    description: 'Total shot attempts (shots on goal, blocked shots, missed shots) when player is on ice',
    calculation: 'Sum of all shot attempts (shots + blocks + misses)',
    context: 'Raw count of shot attempts. Higher CF with lower CA = better possession.',
    category: 'possession'
  },
  'CA': {
    name: 'Corsi Against',
    formula: 'CA = Opponent Shots + Opponent Blocks + Opponent Misses',
    description: 'Total shot attempts against when player is on ice',
    calculation: 'Sum of opponent shot attempts',
    context: 'Lower is better. Lower CA with higher CF = better defensive play.',
    category: 'possession'
  },
  'FF%': {
    name: 'Fenwick For Percentage',
    formula: 'FF% = (FF / (FF + FA)) × 100',
    description: 'Percentage of unblocked shot attempts (shots + misses) for vs against when player is on ice. Measures puck possession excluding blocked shots.',
    calculation: 'Fenwick For / (Fenwick For + Fenwick Against) × 100\nExample: If FF=55 and FA=45, then FF% = (55/(55+45))×100 = 55%',
    context: 'Similar to CF% but excludes blocked shots. Better predictor of future goals than CF% because it focuses on shots that reached or missed the net.',
    examples: '55% FF% means team generated 55 unblocked shot attempts for every 45 against. This is more predictive than CF% because blocked shots are somewhat random.',
    benchmarks: 'Elite: >55% | Excellent: 52-55% | Good: 50-52% | Average: 48-50% | Below Average: <48%',
    interpretation: 'FF% is generally 2-3% higher than CF% because blocked shots reduce CF but not FF. A player with 55% FF% typically outperforms their CF% and is better at generating unblocked attempts.',
    similarStats: ['CF%', 'xGF%', 'GF%'],
    category: 'possession'
  },
  'FF': {
    name: 'Fenwick For',
    formula: 'FF = Shots + Missed Shots',
    description: 'Unblocked shot attempts (shots on goal + missed shots) when player is on ice',
    calculation: 'Shots on goal + Missed shots (excludes blocked shots)',
    context: 'Measures shot attempts that reached or missed the net. Better predictor than Corsi.',
    category: 'possession'
  },
  'FA': {
    name: 'Fenwick Against',
    formula: 'FA = Opponent Shots + Opponent Misses',
    description: 'Unblocked shot attempts against when player is on ice',
    calculation: 'Opponent shots + Opponent misses',
    context: 'Lower is better. Measures unblocked attempts against.',
    category: 'possession'
  },
  'CF% Rel': {
    name: 'Corsi For % Relative',
    formula: 'CF% Rel = Player CF% - Team CF% (without player)',
    description: 'Corsi For % relative to team average when player is off ice',
    calculation: 'Player CF% minus team CF% when player is not on ice',
    context: 'Measures player impact. Positive = player improves team possession. >+2% is excellent.',
    category: 'possession'
  },
  'FF% Rel': {
    name: 'Fenwick For % Relative',
    formula: 'FF% Rel = Player FF% - Team FF% (without player)',
    description: 'Fenwick For % relative to team average when player is off ice',
    calculation: 'Player FF% minus team FF% when player is not on ice',
    context: 'Measures player impact on unblocked shots. >+2% is excellent.',
    category: 'possession'
  },
  'GF%': {
    name: 'Goals For Percentage',
    formula: 'GF% = (GF / (GF + GA)) × 100',
    description: 'Percentage of goals for vs goals against when player is on ice',
    calculation: 'Goals For / (Goals For + Goals Against) × 100',
    context: 'Ultimate result metric. >50% = outscoring opponent. Small sample sizes can be misleading.',
    category: 'possession'
  },
  
  // Expected Goals
  'xG': {
    name: 'Expected Goals',
    formula: 'xG = Σ(shot_xg) where shot_xg = base_rate × modifiers',
    description: 'Expected goals based on shot quality, location, and context',
    calculation: 'Sum of individual shot xG values. Base rates: High danger=0.25, Medium=0.08, Low=0.03, Default=0.06. Modifiers: Rush=1.3x, Rebound=1.5x, Screen=1.2x, One-timer=1.4x, Breakaway=2.5x',
    context: 'Measures shot quality. Goals - xG shows finishing ability. Positive = finishing above expected.',
    category: 'advanced'
  },
  'Goals - xG': {
    name: 'Goals Above Expected',
    formula: 'Goals - xG = Actual Goals - Expected Goals',
    description: 'Difference between actual goals and expected goals',
    calculation: 'Goals scored minus xG generated',
    context: 'Positive = finishing above expected (good shooter). Negative = finishing below expected. Small samples can be noisy.',
    category: 'advanced'
  },
  
  // WAR/GAR
  'WAR': {
    name: 'Wins Above Replacement',
    formula: 'WAR = GAR / 4.5',
    description: 'Wins added above a replacement-level player',
    calculation: 'Goals Above Replacement divided by 4.5 (goals per win in rec hockey)',
    context: 'Higher is better. 1.0 WAR = 1 additional win per season. 2.0+ WAR = elite player.',
    category: 'advanced'
  },
  'GAR': {
    name: 'Goals Above Replacement',
    formula: 'GAR = GAR_offense + GAR_defense + GAR_possession + GAR_transition',
    description: 'Total goals added above replacement level',
    calculation: 'GAR_offense = G×1.0 + A1×0.7 + A2×0.4 + SOG×0.015 + xG×0.8\nGAR_defense = TK×0.05 + BLK×0.02 + ZE×0.03\nGAR_possession = (CF% - 50) / 100 × 0.02 × TOI_hours × 60\nGAR_transition = Controlled entries × 0.04',
    context: 'Comprehensive value metric. 4.5 GAR = 1 WAR. Combines offense, defense, possession, and transition.',
    category: 'advanced'
  },
  'Game Score': {
    name: 'Game Score',
    formula: 'Game Score = Scoring + Shots + Playmaking + Defense + Faceoffs + Hustle',
    description: 'Single-game performance rating',
    calculation: 'Scoring = G×1.0 + A1×0.8 + A2×0.5\nShots = SOG×0.1 + HD_shots×0.15\nPlaymaking = Controlled entries×0.08 + Second touch×0.02\nDefense = TK×0.15 + BLK×0.08 + Poke checks×0.05\nFaceoffs = (FO_wins - FO_losses) × 0.03',
    context: 'Game-by-game performance metric. 5.0+ = excellent game, 3.0+ = good game.',
    category: 'advanced'
  },
  'Rating': {
    name: 'Player Rating',
    formula: 'Rating = Skill-based performance score (1-10 scale)',
    description: 'Overall player performance rating',
    calculation: 'Based on skill rating system. Accounts for competition level and game context.',
    context: '1-10 scale. 7+ = strong performance, 5 = average, <4 = below average.',
    category: 'advanced'
  },
  'Performance Index': {
    name: 'Performance Index',
    formula: 'Composite metric of overall impact',
    description: 'Overall performance index combining multiple factors',
    calculation: 'Weighted combination of scoring, possession, defense, and intangibles',
    context: 'Higher is better. Measures overall game impact.',
    category: 'advanced'
  },
  'Adjusted Rating': {
    name: 'Adjusted Rating',
    formula: 'Rating adjusted for competition quality',
    description: 'Player rating adjusted for opponent strength',
    calculation: 'Base rating adjusted by opponent average rating and game context',
    context: 'Accounts for competition level. More accurate than raw rating.',
    category: 'advanced'
  },
  
  // Shooting
  'Shooting %': {
    name: 'Shooting Percentage',
    formula: 'SH% = (Goals / Shots on Goal) × 100',
    description: 'Percentage of shots on goal that result in goals',
    calculation: 'Goals divided by Shots on Goal, multiplied by 100',
    context: 'Higher is better. League average ~10-15%. Can vary significantly in small samples.',
    category: 'shooting'
  },
  'Shot Accuracy': {
    name: 'Shot Accuracy',
    formula: 'Shot Accuracy = (SOG / Total Shots) × 100',
    description: 'Percentage of shot attempts that reach the net',
    calculation: 'Shots on Goal divided by Total Shot Attempts, multiplied by 100',
    context: 'Higher is better. Measures ability to get shots on net vs missing/blocked.',
    category: 'shooting'
  },
  
  // Zone Play
  'Zone Entry %': {
    name: 'Zone Entry Success Rate',
    formula: 'ZE% = (Successful Entries / Total Entry Attempts) × 100',
    description: 'Percentage of zone entry attempts that result in possession',
    calculation: 'Successful zone entries divided by total zone entry attempts',
    context: 'Higher is better. Controlled entries (with possession) are more valuable than dump-ins.',
    category: 'advanced'
  },
  'Zone Exit %': {
    name: 'Zone Exit Success Rate',
    formula: 'ZX% = (Successful Exits / Total Exit Attempts) × 100',
    description: 'Percentage of zone exit attempts that maintain possession',
    calculation: 'Successful zone exits divided by total zone exit attempts',
    context: 'Higher is better. Controlled exits maintain possession better than clearing attempts.',
    category: 'advanced'
  },
  
  // Per-60 Rates
  'Goals/60': {
    name: 'Goals Per 60 Minutes',
    formula: 'G/60 = (Goals / TOI_minutes) × 60',
    description: 'Goals scored per 60 minutes of ice time',
    calculation: 'Goals divided by time on ice in minutes, multiplied by 60',
    context: 'Rate stat that accounts for ice time. 1.0+ G/60 = excellent, 0.5+ = good.',
    category: 'offense'
  },
  'Assists/60': {
    name: 'Assists Per 60 Minutes',
    formula: 'A/60 = (Assists / TOI_minutes) × 60',
    description: 'Assists per 60 minutes of ice time',
    calculation: 'Assists divided by time on ice in minutes, multiplied by 60',
    context: 'Rate stat for playmaking. 1.0+ A/60 = excellent playmaker.',
    category: 'offense'
  },
  'Points/60': {
    name: 'Points Per 60 Minutes',
    formula: 'P/60 = (Points / TOI_minutes) × 60',
    description: 'Points (goals + assists) per 60 minutes of ice time',
    calculation: 'Points divided by time on ice in minutes, multiplied by 60',
    context: 'Overall offensive rate. 2.0+ P/60 = elite offensive player.',
    category: 'offense'
  },
  
  // Physical
  'Hits': {
    name: 'Hits',
    formula: 'Hits = Total body checks delivered',
    description: 'Total hits (body checks) delivered',
    calculation: 'Count of hit events',
    context: 'Physical play metric. Higher = more physical presence.',
    category: 'physical'
  },
  'Blocks': {
    name: 'Blocked Shots',
    formula: 'Blocks = Shots blocked by player',
    description: 'Total shots blocked',
    calculation: 'Count of blocked shot events',
    context: 'Defensive metric. Higher = more shot blocking. Important for defensemen.',
    category: 'defense'
  },
  'Takeaways': {
    name: 'Takeaways',
    formula: 'Takeaways = Puck takeaways',
    description: 'Puck takeaways (steals)',
    calculation: 'Count of takeaway events',
    context: 'Defensive skill metric. Higher = better at stealing puck.',
    category: 'defense'
  },
  'Giveaways': {
    name: 'Giveaways',
    formula: 'Giveaways = Puck giveaways',
    description: 'Puck giveaways (turnovers)',
    calculation: 'Count of giveaway events',
    context: 'Lower is better. Measures puck control. High giveaways = poor puck management.',
    category: 'defense'
  },
  'TO Differential': {
    name: 'Turnover Differential',
    formula: 'TO Diff = Takeaways - Giveaways',
    description: 'Takeaway minus giveaway differential',
    calculation: 'Takeaways minus Giveaways',
    context: 'Positive = more takeaways than giveaways (good). Negative = more giveaways (bad).',
    category: 'defense'
  },
  
  // Faceoffs
  'FO%': {
    name: 'Faceoff Win Percentage',
    formula: 'FO% = (FO Wins / (FO Wins + FO Losses)) × 100',
    description: 'Percentage of faceoffs won',
    calculation: 'Faceoff wins divided by total faceoffs, multiplied by 100',
    context: 'Higher is better. 50% = even, >55% = excellent, <45% = poor.',
    category: 'situational'
  },
  
  // Passing
  'Pass %': {
    name: 'Pass Completion Percentage',
    formula: 'Pass% = (Completed Passes / Attempted Passes) × 100',
    description: 'Percentage of pass attempts completed',
    calculation: 'Completed passes divided by attempted passes, multiplied by 100',
    context: 'Higher is better. Measures passing accuracy. >80% = good passer.',
    category: 'offense'
  },
  
  // Situational
  'TOI (5v5)': {
    name: 'Time on Ice - Even Strength',
    formula: 'TOI 5v5 = Total ice time at even strength',
    description: 'Total time on ice at 5-on-5 (even strength)',
    calculation: 'Sum of all 5v5 shift durations',
    context: 'Most common game situation. Most important TOI metric.',
    category: 'situational'
  },
  'TOI (PP)': {
    name: 'Time on Ice - Power Play',
    formula: 'TOI PP = Total ice time on power play',
    description: 'Total time on ice on power play',
    calculation: 'Sum of all power play shift durations',
    context: 'Offensive opportunity. Higher TOI PP = more power play usage.',
    category: 'situational'
  },
  'TOI (PK)': {
    name: 'Time on Ice - Penalty Kill',
    formula: 'TOI PK = Total ice time on penalty kill',
    description: 'Total time on ice while shorthanded',
    calculation: 'Sum of all penalty kill shift durations',
    context: 'Defensive responsibility. Higher TOI PK = trusted penalty killer.',
    category: 'situational'
  },
  
  // Even Strength +/-
  '+/- (EV)': {
    name: 'Plus/Minus - Even Strength',
    formula: '+/- (EV) = Goals For (5v5) - Goals Against (5v5)',
    description: 'Plus/minus at even strength only',
    calculation: 'Goals for at 5v5 minus goals against at 5v5',
    context: 'More accurate than total +/-. Excludes power play and shorthanded goals.',
    category: 'advanced'
  },
  'Plus Events': {
    name: 'Plus Events (Even Strength)',
    formula: 'Plus Events = Goals for while on ice at 5v5',
    description: 'Goals for while on ice at even strength',
    calculation: 'Count of goals scored by team when player is on ice at 5v5',
    context: 'Offensive contribution at even strength.',
    category: 'advanced'
  },
  'Minus Events': {
    name: 'Minus Events (Even Strength)',
    formula: 'Minus Events = Goals against while on ice at 5v5',
    description: 'Goals against while on ice at even strength',
    calculation: 'Count of goals allowed when player is on ice at 5v5',
    context: 'Defensive events at even strength. Lower is better.',
    category: 'advanced'
  },
  
  // Shifts
  'Total Shifts': {
    name: 'Total Shifts',
    formula: 'Total Shifts = Count of all shifts',
    description: 'Total number of shifts taken',
    calculation: 'Count of shift events',
    context: 'Usage metric. More shifts = more ice time and trust from coach.',
    category: 'advanced'
  },
  'Shifts/Game': {
    name: 'Shifts Per Game',
    formula: 'Shifts/Game = Total Shifts / Games Played',
    description: 'Average shifts per game',
    calculation: 'Total shifts divided by games played',
    context: 'Usage rate. Higher = more frequent shifts.',
    category: 'advanced'
  },
  'Avg Shift Length': {
    name: 'Average Shift Length',
    formula: 'Avg Shift = Total TOI / Total Shifts',
    description: 'Average length of each shift in minutes',
    calculation: 'Total time on ice divided by total shifts',
    context: 'Shift management. Optimal is 45-60 seconds. Too long = fatigue, too short = inefficient.',
    category: 'advanced'
  },
  
  // Assist Breakdown
  'Primary Assists': {
    name: 'Primary Assists',
    formula: 'Primary Assists = First assist on a goal',
    description: 'First assist on a goal (direct pass to scorer)',
    calculation: 'Count of primary assist events',
    context: 'More valuable than secondary assists. Direct playmaking contribution.',
    category: 'offense'
  },
  'Secondary Assists': {
    name: 'Secondary Assists',
    formula: 'Secondary Assists = Second assist on a goal',
    description: 'Second assist on a goal (pass before the primary assist)',
    calculation: 'Count of secondary assist events',
    context: 'Less directly involved than primary assists. Still shows playmaking involvement.',
    category: 'offense'
  },
  'Primary %': {
    name: 'Primary Assist Percentage',
    formula: 'Primary% = (Primary Assists / Total Assists) × 100',
    description: 'Percentage of assists that are primary',
    calculation: 'Primary assists divided by total assists, multiplied by 100',
    context: 'Higher = more direct playmaking. >60% = excellent primary playmaker.',
    category: 'offense'
  },
  
  // Shot Breakdown
  'Shots Blocked': {
    name: 'Shots Blocked',
    formula: 'Shots Blocked = Shots blocked by opponents',
    description: 'Total shots blocked by opponents',
    calculation: 'Count of blocked shot events',
    context: 'Defensive metric. Shows shot blocking ability.',
    category: 'defense'
  },
  'Shots Missed': {
    name: 'Shots Missed',
    formula: 'Shots Missed = Shots that missed the net',
    description: 'Total shots that missed the net',
    calculation: 'Count of missed shot events',
    context: 'Lower is better. Measures shot accuracy.',
    category: 'shooting'
  },
  
  // Micro Stats
  'Dekes': {
    name: 'Dekes',
    formula: 'Dekes = Deke attempts',
    description: 'Total dekes (puck handling moves) attempted',
    calculation: 'Count of deke events',
    context: 'Skill metric. Shows puck handling ability.',
    category: 'advanced'
  },
  'Drives': {
    name: 'Drives to Net',
    formula: 'Drives = Drives to the net',
    description: 'Total drives to the net',
    calculation: 'Count of drive events (middle, wide, corner)',
    context: 'Offensive aggression. Higher = more net drives.',
    category: 'advanced'
  },
  'Forechecks': {
    name: 'Forechecks',
    formula: 'Forechecks = Forechecking plays',
    description: 'Forechecking plays in offensive zone',
    calculation: 'Count of forecheck events',
    context: 'Defensive pressure. Higher = more aggressive forechecking.',
    category: 'defense'
  },
  'Backchecks': {
    name: 'Backchecks',
    formula: 'Backchecks = Backchecking plays',
    description: 'Backchecking plays (defensive hustle)',
    calculation: 'Count of backcheck events',
    context: 'Defensive effort. Higher = more backchecking effort.',
    category: 'defense'
  },
  'Puck Battles': {
    name: 'Puck Battles',
    formula: 'Puck Battles = Total puck battles',
    description: 'Total puck battles engaged',
    calculation: 'Count of puck battle events',
    context: 'Physical engagement. Higher = more battles.',
    category: 'physical'
  },
  'Primary Def Events': {
    name: 'Primary Defensive Events',
    formula: 'Primary Def = Primary defensive involvement',
    description: 'Primary defensive involvement (main defender)',
    calculation: 'Count of primary defensive events',
    context: 'Defensive responsibility. Higher = more primary defensive plays.',
    category: 'defense'
  },
  'Support Def Events': {
    name: 'Support Defensive Events',
    formula: 'Support Def = Support defensive plays',
    description: 'Support defensive plays (helping defender)',
    calculation: 'Count of support defensive events',
    context: 'Defensive support. Shows defensive awareness.',
    category: 'defense'
  },
  'Def Involvement': {
    name: 'Defensive Involvement',
    formula: 'Def Involvement = Total defensive involvement',
    description: 'Total defensive involvement (primary + support)',
    calculation: 'Primary def events + Support def events',
    context: 'Overall defensive activity. Higher = more defensive engagement.',
    category: 'defense'
  },
}

// Get stat definition
export function getStatDefinition(statKey: string): StatDefinition | null {
  return STAT_DEFINITIONS[statKey] || null
}

// Get all stats in a category
export function getStatsByCategory(category: StatDefinition['category']): StatDefinition[] {
  return Object.values(STAT_DEFINITIONS).filter(s => s.category === category)
}
