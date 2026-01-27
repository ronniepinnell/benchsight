// BenchSight Database Types - Generated from Supabase Schema

// ============================================
// VIEW TYPES - For Dashboard Queries
// ============================================

export interface VStandingsCurrent {
  team_id: string
  team_name: string
  season: number
  season_id: string
  games_played: number
  wins: number
  losses: number
  otl?: number
  points?: number
  win_pct?: number
  goals_for: number
  goals_against: number
  goal_diff: number
  goals_for_per_game: number
  goals_against_per_game: number
  standing: number
  standing_rank?: number
}

export interface VLeaderboardPoints {
  player_id: string
  player_name: string
  team_name: string
  season: number
  season_id: string
  games_played: number
  goals: number
  assists: number
  points: number
  points_per_game: number
  season_rank: number
  overall_rank: number
}

export interface VLeaderboardGoals {
  player_id: string
  player_name: string
  team_name: string
  season: number
  season_id: string
  games_played: number
  goals: number
  goals_per_game: number
  season_rank: number
  overall_rank: number
}

export interface VLeaderboardAssists {
  player_id: string
  player_name: string
  team_name: string
  season: number
  season_id: string
  games_played: number
  assists: number
  assists_per_game: number
  season_rank: number
  overall_rank: number
}

export interface VLeaderboardGoalieGAA {
  player_id: string
  player_name: string
  team_name: string
  season: number
  season_id: string
  games_played: number
  goals_against: number
  saves?: number
  shots_against?: number
  save_pct?: number
  gaa: number
  gaa_rank: number
  season_rank: number
}

export interface VLeaderboardGoalieWins {
  player_id: string
  player_name: string
  team_name: string
  season: number
  season_id: string
  games_played: number
  wins: number
  losses: number
  goals_against?: number
  shots_against?: number
  wins_rank: number
  season_rank: number
}

export interface VRankingsPlayersCurrent {
  player_id: string
  player_name: string
  team_id?: string
  team_name: string
  season_id: string
  games_played: number
  goals: number
  assists: number
  points: number
  pim: number
  points_per_game: number
  points_rank: number
  goals_rank: number
  assists_rank: number
}

export interface VRankingsGoaliesCurrent {
  player_id: string
  player_name: string
  team_name: string
  season_id: string
  games_played: number
  wins: number
  losses: number
  goals_against: number
  gaa: number
  wins_rank: number
  gaa_rank: number
}

export interface VRecentGames {
  game_id: number
  date: string
  home_team_id: string | number
  away_team_id: string | number
  home_team_name: string
  away_team_name: string
  home_total_goals: number
  away_total_goals: number
  official_home_goals?: number
  official_away_goals?: number
  season_id?: string
}

export interface VDetailPlayerGames {
  player_id: string
  player_name: string
  team_name: string
  game_id: number
  date: string
  home_team_name: string
  away_team_name: string
  goals: number
  assists: number
  points: number
  shots: number
  plus_minus_total: number
}

export interface VDetailGoalieGames {
  player_id: string
  player_name: string
  team_name: string
  game_id: number
  date: string
  saves: number
  goals_against: number
  shots_against: number
  save_pct: number
}

export interface VComparePlayers {
  player_id: string
  player_name: string
  team_name: string
  season_id: string
  games_played: number
  goals: number
  assists: number
  points: number
  pim: number
  goals_per_game: number
  assists_per_game: number
  points_per_game: number
  pim_per_game: number
}

export interface VSummaryPlayerCareer {
  player_id: string
  player_name: string
  seasons_played: number
  games_played: number
  career_games: number
  goals: number
  career_goals: number
  assists: number
  career_assists: number
  points: number
  career_points: number
  pim: number
  career_pim: number
  shots?: number
  shooting_pct?: number
  plus_minus?: number
  minor_penalties?: number
  major_penalties?: number
  points_per_game: number
  century_goals: boolean
  two_hundred_club: boolean
}

export interface VSummaryGoalieCareer {
  player_id: string
  player_name: string
  seasons_played: number
  career_games: number
  career_wins: number
  career_losses: number
  career_goals_against: number
  career_gaa: number
  fifty_wins: boolean
}

export interface VRecentHotPlayers {
  player_id: string
  player_name: string
  recent_games: number
  recent_goals: number
  recent_assists: number
  recent_points: number
  avg_points: number
}

export interface VSummaryLeague {
  season_id: string
  total_games: number
  total_goals: number
  total_teams: number
  total_players: number
  avg_goals_per_game: number
}

// ============================================
// DIMENSION TABLE TYPES
// ============================================

export interface DimTeam {
  team_id: string
  team_name: string
  norad_team: string
  league_id: string
  league: string
  long_team_name: string
  team_cd: string
  primary_color?: string
  team_color1: string
  team_color2: string
  team_color3: string
  team_color4: string
  team_logo: string
  team_url: string
}

export interface DimPlayer {
  player_id: string
  player_first_name: string
  player_last_name: string
  player_name?: string
  player_full_name: string
  player_primary_position: string
  position?: string
  team_id?: string
  team_name?: string
  jersey_number?: number
  current_skill_rating: number
  birth_year: number
  player_gender: string
  highest_beer_league: string
  player_rating_ly: number
  player_leadership: string
  player_norad: string
  player_norad_current_team: string
  player_norad_current_team_id: string
  other_url: string
  player_url: string
  player_image: string
}

export interface DimSchedule {
  schedule_id: string
  game_id?: number
  season_id: string
  date?: string
  game_date: string
  game_time: string
  home_team_id: string
  away_team_id: string
  home_team_name: string
  away_team_name: string
  venue: string
  game_number: number
}

// ============================================
// FACT TABLE TYPES
// ============================================

export interface FactPlayerGameStats {
  player_game_key: string
  player_game_id: string
  game_id: number
  season_id: string
  player_id: string
  player_name: string
  team_id: string
  team_name: string
  opponent_team_id?: string
  opponent_team_name?: string
  date?: string
  position: string
  jersey_number?: number
  goals: number
  primary_assists: number
  secondary_assists: number
  assists: number
  points: number
  shots: number
  sog: number
  shooting_pct: number
  pass_attempts: number
  pass_completed: number
  pass_pct: number
  fo_wins: number
  fo_losses: number
  fo_total: number
  fo_pct: number
  giveaways: number
  takeaways: number
  turnover_diff: number
  bad_giveaways: number
  blocks: number
  hits: number
  toi_seconds: number
  toi_minutes: number
  shift_count: number
  avg_shift: number
  plus_ev: number
  minus_ev: number
  plus_minus_ev: number
  plus_minus_total?: number
  corsi_for: number
  corsi_against: number
  cf_pct: number
  fenwick_for: number
  fenwick_against: number
  ff_pct: number
  player_rating: number
  opp_avg_rating: number
  war: number
  gar: number
  game_score: number
}

export interface FactGoalieGameStats {
  goalie_game_key: string
  game_id: number
  season_id: string
  player_id: string
  player_name: string
  team_id: string
  team_name: string
  opponent_team_name?: string
  date?: string
  shots_against: number
  saves: number
  goals_against: number
  save_pct: number
  high_danger_saves: number
  high_danger_shots: number
  high_danger_sv_pct: number
  medium_danger_saves: number
  medium_danger_shots: number
  low_danger_saves: number
  low_danger_shots: number
  rebounds_allowed: number
  rebound_control_pct: number
  win: boolean
  loss: boolean
  gaa: number
  gsaa: number
  goalie_war: number
}

export interface FactEvents {
  event_id: string
  game_id: number
  period: number
  period_id: string
  event_type: string
  event_type_id: string
  event_detail: string
  event_detail_2?: string
  event_detail_id: string
  event_successful: boolean
  event_team_zone: string
  home_team: string
  home_team_id: string
  away_team: string
  away_team_id: string
  duration: number
  event_player_ids: string
  opp_player_ids: string
  event_player_1?: string
  event_player_2?: string
  event_start_min: number
  event_start_sec: number
  event_end_min: number
  event_end_sec: number
  time_seconds?: number
  time_start_total_seconds: number
  running_video_time: number
  team_id?: string
  event_team_id?: string
  team_venue: string
  player_team: string
  player_role: string
  player_name: string
  strength?: string
  play_detail1: string
  play_detail_2?: string
  is_goal: number
  is_highlight: number
  is_rebound: number
  is_rush: number
  is_save: number
  season_id: string
  // Event linking columns
  linked_event_key?: string
  sequence_key?: string
  play_key?: string
}

export interface FactShotXY {
  shot_id: string
  game_id: number
  player_id: string
  player_name: string
  team_id: string
  team_name: string
  period: number
  x_coord: number
  y_coord: number
  shot_type: string
  shot_result: string
  is_goal: boolean
  xg: number
  danger_zone: string
  danger_level: string
  time_seconds: number
}

// ============================================
// XY COORDINATE TABLE TYPES
// ============================================

export interface FactPuckXYLong {
  puck_xy_key: string
  event_id: string
  game_id: number
  point_number: number
  x: number
  y: number
  is_start: boolean
  is_stop: boolean
  distance_to_net: number | null
  angle_to_net: number | null
}

export interface FactPlayerXYLong {
  player_xy_key: string
  event_id: string
  game_id: number
  player_id: string
  player_name: string
  player_role: string
  is_event_team: boolean
  point_number: number
  x: number
  y: number
  is_start: boolean
  is_stop: boolean
  distance_to_net: number | null
  angle_to_net: number | null
}

// ============================================
// HELPER TYPES
// ============================================

export type TeamWithStanding = DimTeam & VStandingsCurrent

export interface GameBoxScore {
  game: VRecentGames
  homeStats: FactPlayerGameStats[]
  awayStats: FactPlayerGameStats[]
  homeGoalie: FactGoalieGameStats | null
  awayGoalie: FactGoalieGameStats | null
}

export interface PlayerProfile {
  player: DimPlayer
  currentStats: VRankingsPlayersCurrent | null
  careerStats: VSummaryPlayerCareer | null
  recentGames: VDetailPlayerGames[]
}

export interface GoalieProfile {
  player: DimPlayer
  currentStats: VRankingsGoaliesCurrent | null
  careerStats: VSummaryGoalieCareer | null
  recentGames: VDetailGoalieGames[]
}
