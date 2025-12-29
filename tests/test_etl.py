"""
ETL Tests for BenchSight
Tests the ETL orchestrator and data transformations.
"""
import pytest
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl_orchestrator import ETLOrchestrator

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "output"


class TestETLOrchestrator:
    """Tests for ETL orchestrator."""
    
    def test_orchestrator_init(self, tmp_path):
        """Test orchestrator initialization."""
        orch = ETLOrchestrator(output_dir=tmp_path)
        assert orch.output_dir == tmp_path
        assert orch.mode == 'overwrite'
    
    def test_orchestrator_append_mode(self, tmp_path):
        """Test append mode."""
        orch = ETLOrchestrator(output_dir=tmp_path, mode='append')
        assert orch.mode == 'append'


class TestDataIntegrity:
    """Tests for data integrity."""
    
    def test_fact_events_player_exists(self):
        """Check fact_events_player.csv exists."""
        assert (OUTPUT_DIR / "fact_events_player.csv").exists()
    
    def test_fact_shifts_player_exists(self):
        """Check fact_shifts_player.csv exists."""
        assert (OUTPUT_DIR / "fact_shifts_player.csv").exists()
    
    def test_fact_events_has_required_columns(self):
        """Check required columns in fact_events_player."""
        df = pd.read_csv(OUTPUT_DIR / "fact_events_player.csv", nrows=5, dtype=str)
        required = ['game_id', 'event_index', 'event_type', 'player_id', 'player_role']
        for col in required:
            assert col in df.columns, f"Missing column: {col}"
    
    def test_fact_shifts_has_logical_shift_columns(self):
        """Check logical shift columns exist."""
        df = pd.read_csv(OUTPUT_DIR / "fact_shifts_player.csv", nrows=5)
        required = ['logical_shift_number', 'shift_segment', 'running_toi']
        for col in required:
            assert col in df.columns, f"Missing column: {col}"
    
    def test_no_negative_shift_durations(self):
        """Shift durations should be non-negative."""
        df = pd.read_csv(OUTPUT_DIR / "fact_shifts_player.csv")
        assert (df['shift_duration'] >= 0).all(), "Found negative shift durations"
    
    def test_logical_shifts_increment(self):
        """Logical shift numbers should only increment."""
        df = pd.read_csv(OUTPUT_DIR / "fact_shifts_player.csv")
        for (game_id, player), group in df.groupby(['game_id', 'player_id']):
            group = group.sort_values('shift_index')
            prev = 0
            for _, row in group.iterrows():
                assert row['logical_shift_number'] >= prev, f"Logical shift decreased for {player}"
                prev = row['logical_shift_number']


class TestValidatedRules:
    """Tests based on validated counting rules."""
    
    @pytest.fixture
    def events(self):
        return pd.read_csv(OUTPUT_DIR / "fact_events_player.csv", dtype=str)
    
    @pytest.fixture
    def keegan_events(self, events):
        return events[(events['game_id'] == '18969') & (events['player_id'] == 'P100117')]
    
    def test_keegan_goals_count(self, keegan_events):
        """Keegan should have 2 goals in game 18969."""
        goals = keegan_events[(keegan_events['event_type'] == 'Goal') & 
                              (keegan_events['player_role'] == 'event_team_player_1')]
        assert len(goals) == 2, f"Expected 2 goals, got {len(goals)}"
    
    def test_keegan_assists_count(self, keegan_events):
        """Keegan should have 1 assist in game 18969."""
        assists = keegan_events[keegan_events['play_detail'].str.contains('Assist', na=False)]
        assert len(assists) == 1, f"Expected 1 assist, got {len(assists)}"
    
    def test_keegan_fo_wins(self, keegan_events):
        """Keegan should have 11 FO wins in game 18969."""
        fo_wins = keegan_events[(keegan_events['event_type'] == 'Faceoff') & 
                                (keegan_events['player_role'] == 'event_team_player_1')]
        assert len(fo_wins) == 11, f"Expected 11 FO wins, got {len(fo_wins)}"
    
    def test_keegan_fo_losses(self, keegan_events):
        """Keegan should have 11 FO losses in game 18969."""
        fo_losses = keegan_events[(keegan_events['event_type'] == 'Faceoff') & 
                                  (keegan_events['player_role'] == 'opp_team_player_1')]
        assert len(fo_losses) == 11, f"Expected 11 FO losses, got {len(fo_losses)}"
    
    def test_keegan_pass_attempts(self, keegan_events):
        """Keegan should have 17 pass attempts in game 18969."""
        passes = keegan_events[(keegan_events['event_type'] == 'Pass') & 
                               (keegan_events['player_role'] == 'event_team_player_1')]
        assert len(passes) == 17, f"Expected 17 passes, got {len(passes)}"


class TestGoalieStats:
    """Tests for goalie stats."""
    
    @pytest.fixture
    def wyatt_events(self):
        events = pd.read_csv(OUTPUT_DIR / "fact_events_player.csv", dtype=str)
        return events[(events['game_id'] == '18969') & (events['player_id'] == 'P100016')]
    
    def test_wyatt_saves(self, wyatt_events):
        """Wyatt should have 37 saves in game 18969."""
        saves = wyatt_events[(wyatt_events['event_type'] == 'Save') & 
                             (wyatt_events['player_role'] == 'event_team_player_1')]
        assert len(saves) == 37, f"Expected 37 saves, got {len(saves)}"
    
    def test_wyatt_goals_against(self, wyatt_events):
        """Wyatt should have 4 goals against in game 18969."""
        ga = wyatt_events[(wyatt_events['event_type'] == 'Goal') & 
                          (wyatt_events['player_role'] == 'opp_team_player_1')]
        assert len(ga) == 4, f"Expected 4 GA, got {len(ga)}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
