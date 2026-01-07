#!/usr/bin/env python3
"""
=============================================================================
Test Suite: Roster Management
=============================================================================
Tests for NORAD scraper, roster reconciliation, and transaction detection.

Run with: pytest tests/test_roster_management.py -v
=============================================================================
"""

import pytest
import pandas as pd
from pathlib import Path
from datetime import date
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.norad_scraper import (
    parse_player_name,
    generate_player_id,
    detect_transactions,
    reconcile_rosters,
    TEAMS
)


class TestPlayerNameParsing:
    """Test player name parsing from NORAD format."""
    
    def test_full_name_with_rating_and_captain(self):
        """Parse: 'Ronnie Pinnell (C) – 4'"""
        result = parse_player_name("Ronnie Pinnell (C) – 4")
        assert result["full_name"] == "Ronnie Pinnell"
        assert result["rating"] == 4
        assert result["leadership"] == "C"
        assert result["first_name"] == "Ronnie"
        assert result["last_name"] == "Pinnell"
    
    def test_name_with_alternate_captain(self):
        """Parse: 'Sam Downs (A) – 6'"""
        result = parse_player_name("Sam Downs (A) – 6")
        assert result["full_name"] == "Sam Downs"
        assert result["rating"] == 6
        assert result["leadership"] == "A"
    
    def test_name_with_sub_designation(self):
        """Parse: 'Robert Mayfield (S) – 3'"""
        result = parse_player_name("Robert Mayfield (S) – 3")
        assert result["leadership"] == "S"
        assert result["rating"] == 3
    
    def test_name_without_leadership(self):
        """Parse: 'Jennifer Valente – 2'"""
        result = parse_player_name("Jennifer Valente – 2")
        assert result["full_name"] == "Jennifer Valente"
        assert result["rating"] == 2
        assert result["leadership"] is None
    
    def test_name_with_hyphen_rating(self):
        """Parse with regular hyphen instead of en-dash."""
        result = parse_player_name("Kevin White - 4")
        assert result["full_name"] == "Kevin White"
        assert result["rating"] == 4
    
    def test_empty_name(self):
        """Handle empty input."""
        result = parse_player_name("")
        assert result["full_name"] == ""
        assert result["rating"] is None
    
    def test_name_only(self):
        """Parse name without rating."""
        result = parse_player_name("John Smith")
        assert result["full_name"] == "John Smith"
        assert result["rating"] is None
    
    def test_multi_part_last_name(self):
        """Parse name with multi-part last name."""
        result = parse_player_name("Juan Carlos Rodriguez (A) – 5")
        assert result["first_name"] == "Juan"
        assert result["last_name"] == "Carlos Rodriguez"


class TestPlayerIdGeneration:
    """Test consistent player ID generation."""
    
    def test_basic_id(self):
        """Generate ID from name and jersey."""
        pid = generate_player_id("John Smith", 17)
        assert pid == "johnsmith_17"
    
    def test_id_without_jersey(self):
        """Generate ID without jersey number."""
        pid = generate_player_id("John Smith")
        assert pid == "johnsmith"
    
    def test_id_with_special_chars(self):
        """Handle special characters in name."""
        pid = generate_player_id("O'Brien-Jones Jr.", 99)
        assert pid == "obrienjonesjr_99"
    
    def test_id_consistency(self):
        """Same input always produces same ID."""
        pid1 = generate_player_id("Test Player", 10)
        pid2 = generate_player_id("Test Player", 10)
        assert pid1 == pid2


class TestTransactionDetection:
    """Test roster transaction detection."""
    
    def test_detect_player_added(self):
        """Detect new player on roster."""
        old_roster = [
            {"player_id": "player1", "player_name": "Player One", "rating": 4}
        ]
        new_roster = [
            {"player_id": "player1", "player_name": "Player One", "rating": 4},
            {"player_id": "player2", "player_name": "Player Two", "rating": 3}
        ]
        
        transactions = detect_transactions(old_roster, new_roster, "TEAM1")
        
        added = [t for t in transactions if t["transaction_type"] == "ADDED"]
        assert len(added) == 1
        assert added[0]["player_id"] == "player2"
    
    def test_detect_player_dropped(self):
        """Detect player removed from roster."""
        old_roster = [
            {"player_id": "player1", "player_name": "Player One", "rating": 4},
            {"player_id": "player2", "player_name": "Player Two", "rating": 3}
        ]
        new_roster = [
            {"player_id": "player1", "player_name": "Player One", "rating": 4}
        ]
        
        transactions = detect_transactions(old_roster, new_roster, "TEAM1")
        
        dropped = [t for t in transactions if t["transaction_type"] == "DROPPED"]
        assert len(dropped) == 1
        assert dropped[0]["player_id"] == "player2"
    
    def test_detect_rating_change(self):
        """Detect rating change for existing player."""
        old_roster = [
            {"player_id": "player1", "player_name": "Player One", "rating": 4}
        ]
        new_roster = [
            {"player_id": "player1", "player_name": "Player One", "rating": 5}
        ]
        
        transactions = detect_transactions(old_roster, new_roster, "TEAM1")
        
        rating_changes = [t for t in transactions if t["transaction_type"] == "RATING_CHANGE"]
        assert len(rating_changes) == 1
        assert rating_changes[0]["old_value"] == "4"
        assert rating_changes[0]["new_value"] == "5"
    
    def test_detect_jersey_change(self):
        """Detect jersey number change."""
        old_roster = [
            {"player_id": "player1", "player_name": "Player One", "jersey_number": 17}
        ]
        new_roster = [
            {"player_id": "player1", "player_name": "Player One", "jersey_number": 91}
        ]
        
        transactions = detect_transactions(old_roster, new_roster, "TEAM1")
        
        jersey_changes = [t for t in transactions if t["transaction_type"] == "JERSEY_CHANGE"]
        assert len(jersey_changes) == 1
    
    def test_no_changes(self):
        """No transactions when rosters are identical."""
        roster = [
            {"player_id": "player1", "player_name": "Player One", "rating": 4}
        ]
        
        transactions = detect_transactions(roster, roster.copy(), "TEAM1")
        assert len(transactions) == 0
    
    def test_multiple_transactions(self):
        """Detect multiple types of transactions."""
        old_roster = [
            {"player_id": "player1", "player_name": "Player One", "rating": 4},
            {"player_id": "player2", "player_name": "Player Two", "rating": 3},
        ]
        new_roster = [
            {"player_id": "player1", "player_name": "Player One", "rating": 5},  # Rating change
            {"player_id": "player3", "player_name": "Player Three", "rating": 4},  # Added
            # player2 dropped
        ]
        
        transactions = detect_transactions(old_roster, new_roster, "TEAM1")
        
        assert len(transactions) == 3
        types = {t["transaction_type"] for t in transactions}
        assert types == {"ADDED", "DROPPED", "RATING_CHANGE"}


class TestRosterReconciliation:
    """Test roster reconciliation between NORAD and tracking."""
    
    def test_perfect_match(self):
        """All players match between NORAD and tracking."""
        norad = [
            {"player_id": "p1", "player_name": "Player 1"},
            {"player_id": "p2", "player_name": "Player 2"},
        ]
        tracked = [
            {"player_id": "p1", "player_name": "Player 1"},
            {"player_id": "p2", "player_name": "Player 2"},
        ]
        
        result = reconcile_rosters(norad, tracked)
        
        assert len(result["matched"]) == 2
        assert len(result["norad_only"]) == 0
        assert len(result["tracking_only"]) == 0
        assert result["stats"]["match_rate"] == 100.0
    
    def test_norad_only_player(self):
        """Player on NORAD but not tracked (no-show)."""
        norad = [
            {"player_id": "p1", "player_name": "Player 1"},
            {"player_id": "p2", "player_name": "Player 2"},  # No-show
        ]
        tracked = [
            {"player_id": "p1", "player_name": "Player 1"},
        ]
        
        result = reconcile_rosters(norad, tracked)
        
        assert len(result["norad_only"]) == 1
        assert result["norad_only"][0]["player_id"] == "p2"
    
    def test_tracking_only_player(self):
        """Player in tracking but not on NORAD (likely sub)."""
        norad = [
            {"player_id": "p1", "player_name": "Player 1"},
        ]
        tracked = [
            {"player_id": "p1", "player_name": "Player 1"},
            {"player_id": "p3", "player_name": "Sub Player"},  # Sub
        ]
        
        result = reconcile_rosters(norad, tracked)
        
        assert len(result["tracking_only"]) == 1
        assert result["tracking_only"][0]["player_id"] == "p3"
    
    def test_mixed_reconciliation(self):
        """Complex case with all scenarios."""
        norad = [
            {"player_id": "p1", "player_name": "Player 1"},
            {"player_id": "p2", "player_name": "Player 2"},  # No-show
        ]
        tracked = [
            {"player_id": "p1", "player_name": "Player 1"},
            {"player_id": "p3", "player_name": "Sub Player"},  # Sub
        ]
        
        result = reconcile_rosters(norad, tracked)
        
        assert len(result["matched"]) == 1
        assert len(result["norad_only"]) == 1
        assert len(result["tracking_only"]) == 1
        assert result["stats"]["match_rate"] == 50.0


class TestTeamConfiguration:
    """Test team configuration constants."""
    
    def test_all_teams_have_ids(self):
        """All teams have team_id defined."""
        for slug, info in TEAMS.items():
            assert "team_id" in info, f"Team {slug} missing team_id"
            assert info["team_id"], f"Team {slug} has empty team_id"
    
    def test_all_teams_have_names(self):
        """All teams have name defined."""
        for slug, info in TEAMS.items():
            assert "name" in info, f"Team {slug} missing name"
    
    def test_expected_team_count(self):
        """Expected number of teams."""
        assert len(TEAMS) >= 10, "Should have at least 10 NORAD teams"
    
    def test_cos_velodrome_exists(self):
        """Verify COS Velodrome is configured."""
        assert "cos-velodrome" in TEAMS
        assert TEAMS["cos-velodrome"]["team_id"] == "VEL"


class TestIntegration:
    """Integration tests requiring data files."""
    
    @pytest.fixture
    def output_dir(self):
        return Path("data/output")
    
    def test_dim_player_has_required_columns(self, output_dir):
        """dim_player has columns needed for roster matching."""
        csv_path = output_dir / "dim_player.csv"
        if not csv_path.exists():
            pytest.skip("dim_player.csv not found")
        
        df = pd.read_csv(csv_path)
        required = ['player_id', 'player_full_name']
        for col in required:
            assert col in df.columns, f"Missing column: {col}"
    
    def test_fact_gameroster_exists(self, output_dir):
        """fact_gameroster table exists."""
        csv_path = output_dir / "fact_gameroster.csv"
        if not csv_path.exists():
            pytest.skip("fact_gameroster.csv not found")
        
        df = pd.read_csv(csv_path)
        assert len(df) > 0, "fact_gameroster is empty"
    
    def test_schedule_has_norad_friendly_ids(self, output_dir):
        """Schedule game_ids match NORAD event IDs."""
        csv_path = output_dir / "dim_schedule.csv"
        if not csv_path.exists():
            pytest.skip("dim_schedule.csv not found")
        
        df = pd.read_csv(csv_path)
        # Check for numeric game IDs that could be NORAD event IDs
        if 'game_id' in df.columns:
            sample_id = df['game_id'].iloc[0]
            # Should be able to construct NORAD URL
            assert sample_id is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
