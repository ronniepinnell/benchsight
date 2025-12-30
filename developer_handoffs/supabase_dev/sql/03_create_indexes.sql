-- Indexes for query performance

-- dim_player
CREATE INDEX IF NOT EXISTS idx_dim_player_player_id ON dim_player(player_id);

-- dim_team
CREATE INDEX IF NOT EXISTS idx_dim_team_team_id ON dim_team(team_id);

-- dim_schedule
CREATE INDEX IF NOT EXISTS idx_dim_schedule_game_id ON dim_schedule(game_id);

-- fact_shifts
CREATE INDEX IF NOT EXISTS idx_fact_shifts_game_id ON fact_shifts(game_id);

-- fact_events
CREATE INDEX IF NOT EXISTS idx_fact_events_game_id ON fact_events(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_events_shift_key ON fact_events(shift_key);
CREATE INDEX IF NOT EXISTS idx_fact_events_event_type ON fact_events(event_type);
CREATE INDEX IF NOT EXISTS idx_fact_events_period ON fact_events(period);

-- fact_events_player
CREATE INDEX IF NOT EXISTS idx_fact_events_player_game_id ON fact_events_player(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_events_player_player_id ON fact_events_player(player_id);
CREATE INDEX IF NOT EXISTS idx_fact_events_player_event_key ON fact_events_player(event_key);
CREATE INDEX IF NOT EXISTS idx_fact_events_player_shift_key ON fact_events_player(shift_key);
CREATE INDEX IF NOT EXISTS idx_fact_events_player_event_type ON fact_events_player(event_type);
CREATE INDEX IF NOT EXISTS idx_fact_events_player_period ON fact_events_player(period);

-- fact_shifts_player
CREATE INDEX IF NOT EXISTS idx_fact_shifts_player_game_id ON fact_shifts_player(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_shifts_player_player_id ON fact_shifts_player(player_id);
CREATE INDEX IF NOT EXISTS idx_fact_shifts_player_team_id ON fact_shifts_player(team_id);
CREATE INDEX IF NOT EXISTS idx_fact_shifts_player_shift_key ON fact_shifts_player(shift_key);
CREATE INDEX IF NOT EXISTS idx_fact_shifts_player_period ON fact_shifts_player(period);

-- fact_player_game_stats
CREATE INDEX IF NOT EXISTS idx_fact_player_game_stats_game_id ON fact_player_game_stats(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_player_game_stats_player_id ON fact_player_game_stats(player_id);

-- fact_team_game_stats
CREATE INDEX IF NOT EXISTS idx_fact_team_game_stats_game_id ON fact_team_game_stats(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_team_game_stats_team_id ON fact_team_game_stats(team_id);

-- fact_goalie_game_stats
CREATE INDEX IF NOT EXISTS idx_fact_goalie_game_stats_game_id ON fact_goalie_game_stats(game_id);
CREATE INDEX IF NOT EXISTS idx_fact_goalie_game_stats_player_id ON fact_goalie_game_stats(player_id);

-- fact_h2h
CREATE INDEX IF NOT EXISTS idx_fact_h2h_game_id ON fact_h2h(game_id);

-- fact_wowy
CREATE INDEX IF NOT EXISTS idx_fact_wowy_game_id ON fact_wowy(game_id);

