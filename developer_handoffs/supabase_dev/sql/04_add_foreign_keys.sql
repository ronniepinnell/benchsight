-- Foreign Key Constraints
-- Run AFTER data is loaded

-- fact_shifts
ALTER TABLE fact_shifts 
    ADD CONSTRAINT fk_fact_shifts_game_id 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
    ON DELETE SET NULL;

-- fact_events
ALTER TABLE fact_events 
    ADD CONSTRAINT fk_fact_events_game_id 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
    ON DELETE SET NULL;

ALTER TABLE fact_events 
    ADD CONSTRAINT fk_fact_events_shift_key 
    FOREIGN KEY (shift_key) REFERENCES fact_shifts(shift_key)
    ON DELETE SET NULL;

-- fact_events_player
ALTER TABLE fact_events_player 
    ADD CONSTRAINT fk_fact_events_player_event_key 
    FOREIGN KEY (event_key) REFERENCES fact_events(event_key)
    ON DELETE SET NULL;

ALTER TABLE fact_events_player 
    ADD CONSTRAINT fk_fact_events_player_game_id 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
    ON DELETE SET NULL;

ALTER TABLE fact_events_player 
    ADD CONSTRAINT fk_fact_events_player_player_id 
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id)
    ON DELETE SET NULL;

-- fact_shifts_player
ALTER TABLE fact_shifts_player 
    ADD CONSTRAINT fk_fact_shifts_player_shift_key 
    FOREIGN KEY (shift_key) REFERENCES fact_shifts(shift_key)
    ON DELETE SET NULL;

ALTER TABLE fact_shifts_player 
    ADD CONSTRAINT fk_fact_shifts_player_game_id 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
    ON DELETE SET NULL;

ALTER TABLE fact_shifts_player 
    ADD CONSTRAINT fk_fact_shifts_player_player_id 
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id)
    ON DELETE SET NULL;

-- fact_player_game_stats
ALTER TABLE fact_player_game_stats 
    ADD CONSTRAINT fk_fact_player_game_stats_game_id 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
    ON DELETE SET NULL;

ALTER TABLE fact_player_game_stats 
    ADD CONSTRAINT fk_fact_player_game_stats_player_id 
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id)
    ON DELETE SET NULL;

-- fact_team_game_stats
ALTER TABLE fact_team_game_stats 
    ADD CONSTRAINT fk_fact_team_game_stats_game_id 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
    ON DELETE SET NULL;

ALTER TABLE fact_team_game_stats 
    ADD CONSTRAINT fk_fact_team_game_stats_team_id 
    FOREIGN KEY (team_id) REFERENCES dim_team(team_id)
    ON DELETE SET NULL;

-- fact_goalie_game_stats
ALTER TABLE fact_goalie_game_stats 
    ADD CONSTRAINT fk_fact_goalie_game_stats_game_id 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
    ON DELETE SET NULL;

ALTER TABLE fact_goalie_game_stats 
    ADD CONSTRAINT fk_fact_goalie_game_stats_player_id 
    FOREIGN KEY (player_id) REFERENCES dim_player(player_id)
    ON DELETE SET NULL;

-- fact_h2h
ALTER TABLE fact_h2h 
    ADD CONSTRAINT fk_fact_h2h_game_id 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
    ON DELETE SET NULL;

ALTER TABLE fact_h2h 
    ADD CONSTRAINT fk_fact_h2h_player_1_id 
    FOREIGN KEY (player_1_id) REFERENCES dim_player(player_id)
    ON DELETE SET NULL;

ALTER TABLE fact_h2h 
    ADD CONSTRAINT fk_fact_h2h_player_2_id 
    FOREIGN KEY (player_2_id) REFERENCES dim_player(player_id)
    ON DELETE SET NULL;

-- fact_wowy
ALTER TABLE fact_wowy 
    ADD CONSTRAINT fk_fact_wowy_game_id 
    FOREIGN KEY (game_id) REFERENCES dim_schedule(game_id)
    ON DELETE SET NULL;

ALTER TABLE fact_wowy 
    ADD CONSTRAINT fk_fact_wowy_player_1_id 
    FOREIGN KEY (player_1_id) REFERENCES dim_player(player_id)
    ON DELETE SET NULL;

ALTER TABLE fact_wowy 
    ADD CONSTRAINT fk_fact_wowy_player_2_id 
    FOREIGN KEY (player_2_id) REFERENCES dim_player(player_id)
    ON DELETE SET NULL;

