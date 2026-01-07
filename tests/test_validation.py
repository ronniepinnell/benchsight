"""
Validation Tests for BenchSight
Runs all stats from VALIDATION_LOG.tsv
"""
import pytest
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "output"
VALIDATION_LOG = BASE_DIR / "docs" / "VALIDATION_LOG.tsv"


@pytest.fixture
def events():
    return pd.read_csv(OUTPUT_DIR / "fact_event_players.csv", dtype=str)


@pytest.fixture
def validation_log():
    return pd.read_csv(VALIDATION_LOG, sep='\t')


def count_stat(df, game_id, player_id, stat):
    """Count a stat using validated rules."""
    d = df[(df['game_id'] == str(game_id)) & (df['player_id'] == player_id)]
    
    if stat == 'goals':
        return len(d[(d['event_type'] == 'Goal') & (d['player_role'] == 'event_team_player_1')])
    elif stat == 'assists':
        return len(d[d['play_detail'].str.contains('Assist', na=False)])
    elif stat == 'pass_attempts':
        return len(d[(d['event_type'] == 'Pass') & (d['player_role'] == 'event_team_player_1')])
    elif stat == 'fo_wins':
        return len(d[(d['event_type'] == 'Faceoff') & (d['player_role'] == 'event_team_player_1')])
    elif stat == 'fo_losses':
        return len(d[(d['event_type'] == 'Faceoff') & (d['player_role'] == 'opp_team_player_1')])
    elif stat == 'zone_entries':
        return len(d[(d['event_detail'].str.contains('Entry', na=False)) & 
                     (d['player_role'] == 'event_team_player_1')])
    elif stat == 'giveaways':
        return len(d[(d['event_detail'].str.contains('Giveaway', na=False)) & 
                     (d['player_role'] == 'event_team_player_1')])
    elif stat == 'takeaways':
        return len(d[(d['event_detail'].str.contains('Takeaway', na=False)) & 
                     (d['player_role'] == 'event_team_player_1')])
    elif stat == 'saves':
        return len(d[(d['event_type'] == 'Save') & (d['player_role'] == 'event_team_player_1')])
    elif stat == 'goals_against':
        return len(d[(d['event_type'] == 'Goal') & (d['player_role'] == 'opp_team_player_1')])
    return None


class TestValidationLog:
    """Test all stats from validation log."""
    
    def test_validation_log_exists(self):
        """Check validation log exists."""
        assert VALIDATION_LOG.exists()
    
    def test_all_validated_stats(self, events, validation_log):
        """Test all implemented stats from validation log."""
        implemented = ['goals', 'assists', 'pass_attempts', 'fo_wins', 'fo_losses',
                      'zone_entries', 'giveaways', 'takeaways', 'saves', 'goals_against']
        
        errors = []
        for _, row in validation_log.iterrows():
            if row['match'] != 'TRUE':
                continue
            if row['stat'] not in implemented:
                continue
            
            calculated = count_stat(events, row['game_id'], row['player_id'], row['stat'])
            if calculated is None:
                continue
            
            try:
                expected = float(row['actual_value'])
                if abs(calculated - expected) > 0.01:
                    errors.append(f"{row['player_name']} {row['stat']}: expected {expected}, got {calculated}")
            except:
                pass
        
        assert len(errors) == 0, f"Validation failures:\n" + "\n".join(errors)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
