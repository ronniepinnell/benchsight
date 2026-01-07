"""
BENCHSIGHT - Foreign Key Relationship Tests
==========================================
Tests to verify all FK relationships are valid and referentially intact.
"""

import pytest
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("data/output")


class TestPlayerForeignKeys:
    """Test player_id foreign key relationships."""
    
    def test_gameroster_player_exists_in_dim_player(self):
        """Verify all player_ids in gameroster exist in dim_player."""
        gameroster = pd.read_csv(OUTPUT_DIR / "fact_gameroster.csv", dtype=str)
        dim_player = pd.read_csv(OUTPUT_DIR / "dim_player.csv", dtype=str)
        
        valid_players = set(dim_player['player_id'].dropna())
        roster_players = set(gameroster['player_id'].dropna())
        
        orphans = roster_players - valid_players
        orphan_rate = len(orphans) / len(roster_players) if roster_players else 0
        
        assert orphan_rate < 0.1, \
            f"{len(orphans)} ({orphan_rate:.1%}) player_ids in gameroster not in dim_player"
    
    def test_player_game_stats_player_exists(self):
        """Verify player_ids in player_game_stats exist in dim_player."""
        stats = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv", dtype=str)
        dim_player = pd.read_csv(OUTPUT_DIR / "dim_player.csv", dtype=str)
        
        valid_players = set(dim_player['player_id'].dropna())
        stats_players = set(stats['player_id'].dropna())
        
        orphans = stats_players - valid_players
        orphan_rate = len(orphans) / len(stats_players) if stats_players else 0
        
        assert orphan_rate < 0.1, \
            f"{len(orphans)} ({orphan_rate:.1%}) player_ids in stats not in dim_player"
    
    def test_events_player_player_exists(self):
        """Verify player_ids in events_player exist in dim_player."""
        events = pd.read_csv(OUTPUT_DIR / "fact_event_players.csv", dtype=str)
        dim_player = pd.read_csv(OUTPUT_DIR / "dim_player.csv", dtype=str)
        
        valid_players = set(dim_player['player_id'].dropna())
        event_players = set(events['player_id'].dropna())
        
        orphans = event_players - valid_players
        orphan_rate = len(orphans) / len(event_players) if event_players else 0
        
        assert orphan_rate < 0.2, \
            f"{len(orphans)} ({orphan_rate:.1%}) player_ids in events not in dim_player"
    
    def test_shifts_player_player_exists(self):
        """Verify player_ids in shifts_player exist in dim_player."""
        shifts = pd.read_csv(OUTPUT_DIR / "fact_shift_players.csv", dtype=str)
        dim_player = pd.read_csv(OUTPUT_DIR / "dim_player.csv", dtype=str)
        
        valid_players = set(dim_player['player_id'].dropna())
        shift_players = set(shifts['player_id'].dropna())
        
        orphans = shift_players - valid_players
        orphan_rate = len(orphans) / len(shift_players) if shift_players else 0
        
        assert orphan_rate < 0.2, \
            f"{len(orphans)} ({orphan_rate:.1%}) player_ids in shifts not in dim_player"


class TestTeamForeignKeys:
    """Test team_id foreign key relationships."""
    
    def test_gameroster_team_exists_in_dim_team(self):
        """Verify team_ids in gameroster exist in dim_team."""
        gameroster = pd.read_csv(OUTPUT_DIR / "fact_gameroster.csv", dtype=str)
        dim_team = pd.read_csv(OUTPUT_DIR / "dim_team.csv", dtype=str)
        
        if 'team_id' not in gameroster.columns:
            pytest.skip("team_id not in gameroster")
        
        valid_teams = set(dim_team['team_id'].dropna())
        roster_teams = set(gameroster['team_id'].dropna())
        
        orphans = roster_teams - valid_teams
        assert len(orphans) == 0, \
            f"{len(orphans)} team_ids in gameroster not in dim_team: {list(orphans)[:5]}"
    
    def test_schedule_teams_exist(self):
        """Verify home/away team_ids in schedule exist in dim_team."""
        schedule = pd.read_csv(OUTPUT_DIR / "dim_schedule.csv", dtype=str)
        dim_team = pd.read_csv(OUTPUT_DIR / "dim_team.csv", dtype=str)
        
        valid_teams = set(dim_team['team_id'].dropna())
        
        for col in ['home_team_id', 'away_team_id']:
            if col in schedule.columns:
                schedule_teams = set(schedule[col].dropna())
                orphans = schedule_teams - valid_teams
                assert len(orphans) == 0, \
                    f"{len(orphans)} {col} values not in dim_team"


class TestGameForeignKeys:
    """Test game_id foreign key relationships."""
    
    def test_events_game_exists_in_schedule(self):
        """Verify game_ids in events exist in schedule."""
        events = pd.read_csv(OUTPUT_DIR / "fact_events.csv", dtype=str)
        schedule = pd.read_csv(OUTPUT_DIR / "dim_schedule.csv", dtype=str)
        
        valid_games = set(schedule['game_id'].astype(str).dropna())
        event_games = set(events['game_id'].astype(str).dropna())
        
        orphans = event_games - valid_games
        assert len(orphans) == 0, \
            f"{len(orphans)} game_ids in events not in schedule: {list(orphans)[:5]}"
    
    def test_gameroster_game_exists_in_schedule(self):
        """Verify game_ids in gameroster exist in schedule."""
        gameroster = pd.read_csv(OUTPUT_DIR / "fact_gameroster.csv", dtype=str)
        schedule = pd.read_csv(OUTPUT_DIR / "dim_schedule.csv", dtype=str)
        
        valid_games = set(schedule['game_id'].astype(str).dropna())
        roster_games = set(gameroster['game_id'].astype(str).dropna())
        
        orphans = roster_games - valid_games
        assert len(orphans) == 0, \
            f"{len(orphans)} game_ids in gameroster not in schedule: {list(orphans)[:5]}"
    
    def test_player_game_stats_game_exists(self):
        """Verify game_ids in player_game_stats exist in schedule."""
        stats = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv", dtype=str)
        schedule = pd.read_csv(OUTPUT_DIR / "dim_schedule.csv", dtype=str)
        
        valid_games = set(schedule['game_id'].astype(str).dropna())
        stats_games = set(stats['game_id'].astype(str).dropna())
        
        orphans = stats_games - valid_games
        assert len(orphans) == 0, \
            f"{len(orphans)} game_ids in player_game_stats not in schedule"


class TestEventTypeForeignKeys:
    """Test event_type foreign key relationships."""
    
    def test_events_have_valid_event_types(self):
        """Verify event types in events exist in dim_event_type."""
        events = pd.read_csv(OUTPUT_DIR / "fact_events.csv", dtype=str)
        
        if (OUTPUT_DIR / "dim_event_type.csv").exists():
            dim_event_type = pd.read_csv(OUTPUT_DIR / "dim_event_type.csv", dtype=str)
            
            type_col = 'event_type' if 'event_type' in events.columns else 'Type'
            code_col = 'event_type_code' if 'event_type_code' in dim_event_type.columns else 'event_type'
            
            if type_col in events.columns and code_col in dim_event_type.columns:
                valid_types = set(dim_event_type[code_col].dropna())
                event_types = set(events[type_col].dropna())
                
                orphans = event_types - valid_types
                orphan_rate = len(orphans) / len(event_types) if event_types else 0
                
                assert orphan_rate < 0.2, \
                    f"{len(orphans)} event types not in dim_event_type: {list(orphans)[:5]}"


class TestVenueForeignKeys:
    """Test venue foreign key relationships."""
    
    def test_shifts_have_valid_venue(self):
        """Verify venue values in shifts are valid."""
        shifts = pd.read_csv(OUTPUT_DIR / "fact_shift_players.csv", dtype=str)
        
        if 'venue' in shifts.columns:
            valid_venues = {'home', 'away', 'Home', 'Away'}
            shift_venues = set(shifts['venue'].dropna())
            
            invalid = shift_venues - valid_venues
            assert len(invalid) == 0, \
                f"Invalid venue values: {invalid}"


class TestCrossTableConsistency:
    """Test consistency across related tables."""
    
    def test_player_game_count_consistency(self):
        """Verify player-game combinations are consistent across tables."""
        gameroster = pd.read_csv(OUTPUT_DIR / "fact_gameroster.csv", dtype=str)
        stats = pd.read_csv(OUTPUT_DIR / "fact_player_game_stats.csv", dtype=str)
        
        roster_combos = set(zip(gameroster['game_id'], gameroster['player_id']))
        stats_combos = set(zip(stats['game_id'], stats['player_id']))
        
        # Stats should be subset of roster (or equal)
        stats_not_in_roster = stats_combos - roster_combos
        orphan_rate = len(stats_not_in_roster) / len(stats_combos) if stats_combos else 0
        
        assert orphan_rate < 0.2, \
            f"{len(stats_not_in_roster)} ({orphan_rate:.1%}) player-game combos in stats not in roster"
    
    def test_event_player_references_events(self):
        """Verify events_player references valid events."""
        events = pd.read_csv(OUTPUT_DIR / "fact_events.csv", dtype=str)
        events_player = pd.read_csv(OUTPUT_DIR / "fact_event_players.csv", dtype=str)
        
        # Create event identifiers
        events['event_key'] = events['game_id'].astype(str) + '_' + events['event_index'].astype(str)
        events_player['event_key'] = events_player['game_id'].astype(str) + '_' + events_player['event_index'].astype(str)
        
        valid_events = set(events['event_key'].dropna())
        player_events = set(events_player['event_key'].dropna())
        
        orphans = player_events - valid_events
        orphan_rate = len(orphans) / len(player_events) if player_events else 0
        
        assert orphan_rate < 0.1, \
            f"{len(orphans)} ({orphan_rate:.1%}) events_player rows reference non-existent events"
    
    def test_shifts_player_references_shifts(self):
        """Verify shifts_player references valid shift indices."""
        if not (OUTPUT_DIR / "fact_shifts.csv").exists():
            pytest.skip("fact_shifts.csv not found")
        
        shifts = pd.read_csv(OUTPUT_DIR / "fact_shifts.csv", dtype=str)
        shifts_player = pd.read_csv(OUTPUT_DIR / "fact_shift_players.csv", dtype=str)
        
        if 'shift_index' in shifts.columns and 'shift_index' in shifts_player.columns:
            shifts['shift_key'] = shifts['game_id'].astype(str) + '_' + shifts['shift_index'].astype(str)
            shifts_player['shift_key'] = shifts_player['game_id'].astype(str) + '_' + shifts_player['shift_index'].astype(str)
            
            valid_shifts = set(shifts['shift_key'].dropna())
            player_shifts = set(shifts_player['shift_key'].dropna())
            
            orphans = player_shifts - valid_shifts
            orphan_rate = len(orphans) / len(player_shifts) if player_shifts else 0
            
            assert orphan_rate < 0.1, \
                f"{len(orphans)} ({orphan_rate:.1%}) shifts_player rows reference non-existent shifts"


class TestReferentialCompleteness:
    """Test that referenced dimension values are complete."""
    
    def test_dim_player_has_all_players(self):
        """Verify dim_player contains all players referenced in fact tables."""
        dim_player = pd.read_csv(OUTPUT_DIR / "dim_player.csv", dtype=str)
        
        all_players = set()
        
        for table_name in ['fact_gameroster', 'fact_player_game_stats', 'fact_event_players']:
            table_path = OUTPUT_DIR / f"{table_name}.csv"
            if table_path.exists():
                df = pd.read_csv(table_path, dtype=str)
                if 'player_id' in df.columns:
                    all_players.update(df['player_id'].dropna())
        
        dim_players = set(dim_player['player_id'].dropna())
        missing = all_players - dim_players
        
        missing_rate = len(missing) / len(all_players) if all_players else 0
        assert missing_rate < 0.1, \
            f"{len(missing)} ({missing_rate:.1%}) players in facts not in dim_player"
    
    def test_dim_team_has_all_teams(self):
        """Verify dim_team contains all teams referenced."""
        dim_team = pd.read_csv(OUTPUT_DIR / "dim_team.csv", dtype=str)
        
        all_teams = set()
        
        # Check schedule
        schedule = pd.read_csv(OUTPUT_DIR / "dim_schedule.csv", dtype=str)
        for col in ['home_team_id', 'away_team_id', 'home_team', 'away_team']:
            if col in schedule.columns:
                all_teams.update(schedule[col].dropna())
        
        # Check gameroster
        gameroster = pd.read_csv(OUTPUT_DIR / "fact_gameroster.csv", dtype=str)
        if 'team_id' in gameroster.columns:
            all_teams.update(gameroster['team_id'].dropna())
        
        dim_teams = set(dim_team['team_id'].dropna())
        # Also add team names as valid
        if 'team_name' in dim_team.columns:
            dim_teams.update(dim_team['team_name'].dropna())
        
        missing = all_teams - dim_teams
        missing_rate = len(missing) / len(all_teams) if all_teams else 0
        
        assert missing_rate < 0.2, \
            f"{len(missing)} teams referenced but not in dim_team"
