# BenchSight View Catalog

## Total Views: 30

### Leaderboard Views (8)
| View | Description | Key Columns |
|------|-------------|-------------|
| v_leaderboard_points | Points leaders with rank | player_name, points, season_rank |
| v_leaderboard_goals | Goals leaders | player_name, goals, season_rank |
| v_leaderboard_assists | Assists leaders | player_name, assists, season_rank |
| v_leaderboard_ppg | Points per game (min 5 GP) | player_name, points_per_game |
| v_leaderboard_career_points | All-time points leaders | player_name, career_points, rank |
| v_leaderboard_goalie_wins | Goalie wins leaders | player_name, wins, gaa |
| v_leaderboard_goalie_gaa | Goalie GAA leaders (min 5 GP) | player_name, gaa, season_rank |
| v_leaderboard_pim | PIM leaders | player_name, pim, season_rank |

### Standings Views (4)
| View | Description | Key Columns |
|------|-------------|-------------|
| v_standings_current | Current season standings | team_name, wins, losses, standing |
| v_standings_all_seasons | All seasons standings | team_name, season, standing |
| v_standings_team_history | Team historical performance | team_name, total_wins, all_time_win_pct |
| v_standings_h2h | Head-to-head records | team1, team2, games_played, team1_wins |

### Rankings Views (7)
| View | Description | Key Columns |
|------|-------------|-------------|
| v_rankings_players | Full player rankings | player_name, points_rank, goals_rank |
| v_rankings_players_current | Current season only | player_name, ppg_rank |
| v_rankings_goalies | Full goalie rankings | player_name, wins_rank, gaa_rank |
| v_rankings_goalies_current | Current season only | player_name, win_pct_rank |
| v_rankings_goalies_advanced | Advanced tracking metrics | player_name, rush_sv_pct, war_rank |
| v_rankings_career | Career rankings | player_name, points_rank, goals_rank |
| v_rankings_by_position | Position-specific rankings | position, position_rank |

### Summary Views (6)
| View | Description | Key Columns |
|------|-------------|-------------|
| v_summary_league | League-wide totals | season, total_players, total_goals |
| v_summary_team_season | Team season summary | team_name, roster_size, top_scorer_points |
| v_summary_player_career | Player career summary | player_name, career_points |
| v_summary_goalie_career | Goalie career summary | player_name, career_wins |
| v_summary_game | Game summaries | game_id, winner, score |
| v_summary_by_position | Stats by position | position, player_count, avg_ppg |

### Recent Views (6)
| View | Description | Key Columns |
|------|-------------|-------------|
| v_recent_games | Last 20 games | date, home_team, away_team, score |
| v_recent_player_games | Recent player performances | player_name, date, points |
| v_recent_goalie_games | Recent goalie performances | player_name, date, save_pct |
| v_recent_hot_players | Hot players (recent form) | player_name, points, avg_game_score |
| v_recent_high_scoring | Highest scoring games | game_id, total_goals |
| v_recent_team_form | Team last 5 results | team_name, last_5_form (WWLWL) |

### Comparison Views (7)
| View | Description | Key Columns |
|------|-------------|-------------|
| v_compare_players | Player comparison data | player_name, all basic stats |
| v_compare_goalies | Goalie comparison data | player_name, all goalie stats |
| v_compare_goalies_advanced | Advanced goalie comparison | player_name, tracking stats |
| v_compare_teams | Team comparison data | team_name, all team stats |
| v_compare_player_vs_league | Player vs league average | player_name, ppg_vs_avg |
| v_compare_teammates | Same-team comparisons | player1, player2, points |
| v_compare_goalies_career | Career goalie comparison | player_name, career stats |

### Detail Views (9)
| View | Description | Key Columns |
|------|-------------|-------------|
| v_detail_player_game_log | Player game log | player_name, date, G, A, P |
| v_detail_goalie_game_log | Goalie game log | player_name, date, SV%, rating |
| v_detail_team_game_log | Team game log | team_name, date, result |
| v_detail_player_periods | Player period splits | player_name, p1/p2/p3 stats |
| v_detail_goalie_periods | Goalie period performance | player_name, p1/p2/p3_sv_pct |
| v_detail_goalie_shot_context | Rush vs set play | player_name, rush_sv_pct |
| v_detail_goalie_pressure | Pressure handling | player_name, multi_shot_sv_pct |
| v_detail_player_vs_opponent | Player vs opponent history | player_name, opponent, points |
| v_detail_game_roster | Game rosters | game_id, player_name, G, A, P |

### Tracking Views (8)
| View | Description | Key Columns |
|------|-------------|-------------|
| v_tracking_event_summary | Event type counts | game_id, event_type, count |
| v_tracking_shot_locations | Shot locations | game_id, danger_zone, count |
| v_tracking_zone_entries | Zone entry success | entry_type, success_rate |
| v_tracking_player_micro | Player micro stats | player_name, zone_entries, takeaways |
| v_tracking_faceoffs | Faceoff summary | player_id, fo_pct |
| v_tracking_scoring_chances | Scoring chance summary | team_name, conversion_rate |
| v_tracking_shift_quality | Shift quality summary | player_id, avg_shift_quality |
| v_tracking_save_types | Save type breakdown | player_id, save_type, count |

---

## View Usage by Dashboard Page

| Page | Primary Views |
|------|---------------|
| Home | v_standings_current, v_leaderboard_points, v_recent_games |
| Standings | v_standings_current, v_standings_team_history |
| Leaderboards | v_leaderboard_* |
| Player Profile | v_summary_player_career, v_detail_player_game_log |
| Goalie Profile | v_summary_goalie_career, v_detail_goalie_game_log |
| Team Profile | v_compare_teams, v_compare_players (filtered) |
| Compare | v_compare_players, v_compare_goalies, v_compare_teams |
| Game Detail | v_summary_game, v_detail_game_roster |
