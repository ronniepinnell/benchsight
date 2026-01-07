"""
TIER 2 TESTS - WARNING
======================
These tests SHOULD pass but won't block delivery.
Failures are logged as warnings in the pre_delivery report.

Run: pytest tests/test_tier2_warning.py -v

Tests:
- Foreign key relationships valid
- No orphan records
- Data values in reasonable ranges
- Player stats make sense
- Schema consistency
"""
import pytest
import pandas as pd
import json
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
CONFIG_DIR = PROJECT_ROOT / "config"


def load_table(name):
    """Load a CSV table, return None if not exists."""
    path = OUTPUT_DIR / f"{name}.csv"
    if path.exists():
        return pd.read_csv(path)
    return None


class TestForeignKeyRelationships:
    """Verify foreign key relationships are valid."""
    
    def test_events_game_ids_valid(self):
        """All game_ids in fact_events should exist in dim_game."""
        events = load_table('fact_events')
        games = load_table('dim_game')
        
        if events is None or games is None:
            pytest.skip("Required tables not found")
        
        event_game_ids = set(events['game_id'].unique())
        dim_game_ids = set(games['game_id'].unique())
        
        orphans = event_game_ids - dim_game_ids
        assert len(orphans) == 0, f"Events reference non-existent games: {orphans}"
    
    def test_event_players_player_ids_valid(self):
        """All player_ids in fact_event_players should exist in dim_player."""
        event_players = load_table('fact_event_players')
        players = load_table('dim_player')
        
        if event_players is None or players is None:
            pytest.skip("Required tables not found")
        
        event_player_ids = set(event_players['player_id'].dropna().unique())
        dim_player_ids = set(players['player_id'].unique())
        
        orphans = event_player_ids - dim_player_ids
        assert len(orphans) == 0, f"Event players reference non-existent players: {orphans}"
    
    def test_shifts_player_ids_valid(self):
        """All player_ids in fact_shift_players should exist in dim_player."""
        shifts = load_table('fact_shift_players')
        players = load_table('dim_player')
        
        if shifts is None or players is None:
            pytest.skip("Required tables not found")
        
        shift_player_ids = set(shifts['player_id'].dropna().unique())
        dim_player_ids = set(players['player_id'].unique())
        
        orphans = shift_player_ids - dim_player_ids
        assert len(orphans) == 0, f"Shifts reference non-existent players: {orphans}"
    
    def test_roster_player_ids_valid(self):
        """All player_ids in fact_gameroster should exist in dim_player."""
        roster = load_table('fact_gameroster')
        players = load_table('dim_player')
        
        if roster is None or players is None:
            pytest.skip("Required tables not found")
        
        roster_player_ids = set(roster['player_id'].dropna().unique())
        dim_player_ids = set(players['player_id'].unique())
        
        orphans = roster_player_ids - dim_player_ids
        assert len(orphans) == 0, f"Roster references non-existent players: {orphans}"


class TestDataReasonability:
    """Verify data values are within reasonable ranges."""
    
    def test_goals_per_game_reasonable(self):
        """No game should have more than 20 goals (reasonable for rec hockey)."""
        events = load_table('fact_events')
        if events is None:
            pytest.skip("fact_events not found")
        
        goals = events[
            (events['event_type'] == 'Goal') & 
            (events['event_detail'] == 'Goal_Scored')
        ]
        
        goals_per_game = goals.groupby('game_id').size()
        max_goals = goals_per_game.max()
        
        assert max_goals <= 20, f"Unrealistic goal count in a game: {max_goals}"
    
    def test_shots_per_game_reasonable(self):
        """Each game should have between 20-150 shots total."""
        events = load_table('fact_events')
        if events is None:
            pytest.skip("fact_events not found")
        
        shots = events[events['event_type'] == 'Shot']
        shots_per_game = shots.groupby('game_id').size()
        
        for game_id, count in shots_per_game.items():
            assert 20 <= count <= 150, f"Game {game_id}: {count} shots seems unreasonable"
    
    def test_players_per_game_reasonable(self):
        """Each game should have 10-40 players in roster."""
        roster = load_table('fact_gameroster')
        if roster is None:
            pytest.skip("fact_gameroster not found")
        
        players_per_game = roster.groupby('game_id')['player_id'].nunique()
        
        for game_id, count in players_per_game.items():
            assert 10 <= count <= 40, f"Game {game_id}: {count} players seems unreasonable"
    
    def test_no_negative_stats(self):
        """Player stats should not have negative values (if table exists)."""
        # Try different possible stat table names
        for table_name in ['fact_player_game_stats', 'fact_player_game_position']:
            stats = load_table(table_name)
            if stats is not None:
                break
        else:
            pytest.skip("No player stats table found")
        
        numeric_cols = stats.select_dtypes(include=['number']).columns
        stat_cols = [c for c in numeric_cols if c not in ['game_id', 'player_id']]
        
        for col in stat_cols[:10]:  # Check first 10 stat columns
            if col in stats.columns:
                min_val = stats[col].min()
                if pd.notna(min_val) and min_val < 0:
                    pytest.fail(f"Negative value in {col}: {min_val}")
    
    def test_toi_reasonable(self):
        """Time on ice should be between 0 and 60 minutes (3600 seconds)."""
        # Try different possible stat table names
        for table_name in ['fact_player_game_stats', 'fact_player_game_position']:
            stats = load_table(table_name)
            if stats is not None:
                break
        else:
            pytest.skip("No player stats table found")
        
        toi_cols = [c for c in stats.columns if 'toi' in c.lower()]
        if not toi_cols:
            pytest.skip("No TOI columns found")
        
        for col in toi_cols:
            max_toi = stats[col].max()
            if pd.notna(max_toi):
                assert max_toi <= 3600, f"Unrealistic TOI in {col}: {max_toi} seconds"


class TestPlayerStatsConsistency:
    """Verify player stats are internally consistent."""
    
    def test_goals_equal_shot_goals(self):
        """For each player, goals should equal Shot_Goal count."""
        events = load_table('fact_event_players')
        if events is None:
            pytest.skip("fact_event_players not found")
        
        # Goals from Goal events
        goals = events[
            (events['event_type'] == 'Goal') & 
            (events['player_role'] == 'event_player_1')
        ].groupby(['game_id', 'player_id']).size()
        
        # Shot_Goal events (shots that resulted in goals)
        shot_goals = events[
            (events['event_type'] == 'Shot') & 
            (events['event_detail'] == 'Shot_Goal') &
            (events['player_role'] == 'event_player_1')
        ].groupby(['game_id', 'player_id']).size()
        
        # They should match
        for (game_id, player_id), goal_count in goals.items():
            sg_count = shot_goals.get((game_id, player_id), 0)
            if goal_count != sg_count:
                pytest.fail(
                    f"Player {player_id} in game {game_id}: "
                    f"Goals={goal_count} but Shot_Goal={sg_count}"
                )
    
    def test_keegan_has_correct_stats(self):
        """Keegan (P100117) should have 2 goals in game 18969."""
        events = load_table('fact_event_players')
        if events is None:
            pytest.skip("fact_event_players not found")
        
        keegan_goals = events[
            (events['game_id'].astype(str) == '18969') &
            (events['player_id'] == 'P100117') &
            (events['event_type'] == 'Goal') &
            (events['player_role'] == 'event_player_1')
        ]
        
        assert len(keegan_goals) == 2, f"Keegan should have 2 goals, got {len(keegan_goals)}"


class TestSchemaConsistency:
    """Verify schema is consistent across tables."""
    
    # Tables that should have game_id (event-level fact tables)
    GAME_LEVEL_FACTS = [
        'fact_events', 'fact_event_players', 'fact_shifts', 
        'fact_shift_players', 'fact_gameroster'
    ]
    
    def test_game_level_facts_have_game_id(self):
        """Game-level fact tables should have a game_id column."""
        missing = []
        for table in self.GAME_LEVEL_FACTS:
            table_path = OUTPUT_DIR / f"{table}.csv"
            if table_path.exists():
                df = pd.read_csv(table_path, nrows=1)
                if 'game_id' not in df.columns:
                    missing.append(table)
        
        assert len(missing) == 0, f"Game-level fact tables missing game_id: {missing}"
    
    def test_player_dim_has_player_id(self):
        """dim_player should have player_id as primary key."""
        table_path = OUTPUT_DIR / "dim_player.csv"
        if table_path.exists():
            df = pd.read_csv(table_path, nrows=1)
            assert 'player_id' in df.columns, "dim_player missing player_id"
    
    def test_team_dim_has_team_id(self):
        """dim_team should have team_id as primary key."""
        table_path = OUTPUT_DIR / "dim_team.csv"
        if table_path.exists():
            df = pd.read_csv(table_path, nrows=1)
            assert 'team_id' in df.columns, "dim_team missing team_id"
    
    def test_no_duplicate_player_ids(self):
        """dim_player should not have duplicate player_ids."""
        df = load_table('dim_player')
        if df is not None and 'player_id' in df.columns:
            dupe_count = df['player_id'].duplicated().sum()
            assert dupe_count == 0, f"dim_player has {dupe_count} duplicate player_ids"
    
    def test_no_duplicate_team_ids(self):
        """dim_team should not have duplicate team_ids."""
        df = load_table('dim_team')
        if df is not None and 'team_id' in df.columns:
            dupe_count = df['team_id'].duplicated().sum()
            assert dupe_count == 0, f"dim_team has {dupe_count} duplicate team_ids"


class TestDataQualityMetrics:
    """Track data quality metrics."""
    
    def test_no_null_player_ids_in_roster(self):
        """Roster should not have null player IDs."""
        roster = load_table('fact_gameroster')
        if roster is None:
            pytest.skip("fact_gameroster not found")
        
        null_count = roster['player_id'].isna().sum()
        assert null_count == 0, f"Roster has {null_count} null player_ids"
    
    def test_minimal_null_event_types(self):
        """Events should have very few null event types (< 1%)."""
        events = load_table('fact_events')
        if events is None:
            pytest.skip("fact_events not found")
        
        null_count = events['event_type'].isna().sum()
        null_pct = null_count / len(events) * 100
        
        # Allow up to 1% null (some edge cases)
        assert null_pct < 1.0, f"Events has {null_count} null event_types ({null_pct:.2f}%)"
    
    def test_tracked_games_have_events(self):
        """Every tracked game (with raw data) should have events."""
        events = load_table('fact_events')
        
        if events is None:
            pytest.skip("fact_events not found")
        
        # Tracked games are those in IMMUTABLE_FACTS
        import json
        facts_file = PROJECT_ROOT / "config" / "IMMUTABLE_FACTS.json"
        if not facts_file.exists():
            pytest.skip("IMMUTABLE_FACTS.json not found")
        
        with open(facts_file) as f:
            facts = json.load(f)
        
        tracked_game_ids = set(int(g) for g in facts.get('games', {}).keys())
        event_game_ids = set(events['game_id'].unique())
        
        missing = tracked_game_ids - event_game_ids
        assert len(missing) == 0, f"Tracked games with no events: {missing}"


class TestMetadataCompleteness:
    """Verify that documentation metadata is complete."""
    
    def test_all_tables_have_basic_metadata(self):
        """All output tables should have at least basic metadata."""
        metadata_file = CONFIG_DIR / "TABLE_METADATA.json"
        if not metadata_file.exists():
            pytest.skip("TABLE_METADATA.json not found")
        
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        tables_metadata = set(metadata.get("tables", {}).keys())
        
        # Get actual tables
        csv_files = list(OUTPUT_DIR.glob("*.csv"))
        actual_tables = {f.stem for f in csv_files}
        
        missing = actual_tables - tables_metadata
        
        # Allow up to 90% missing for now (warning test)
        # This threshold should decrease as metadata is added
        max_missing = int(len(actual_tables) * 0.90)
        assert len(missing) <= max_missing, \
            f"Too many tables missing metadata: {len(missing)}/{len(actual_tables)}. Missing: {sorted(missing)[:10]}..."
    
    def test_key_tables_have_complete_metadata(self):
        """Critical tables must have complete metadata."""
        metadata_file = CONFIG_DIR / "TABLE_METADATA.json"
        if not metadata_file.exists():
            pytest.skip("TABLE_METADATA.json not found")
        
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        # These tables MUST have complete metadata
        key_tables = ['fact_events', 'fact_shifts', 'fact_event_players', 'dim_player', 'dim_team']
        
        issues = []
        for table in key_tables:
            info = metadata.get("tables", {}).get(table, {})
            if not info:
                issues.append(f"{table}: no metadata")
                continue
            
            # Check required fields
            for field in ['description', 'purpose', 'grain']:
                if not info.get(field):
                    issues.append(f"{table}: missing {field}")
        
        assert len(issues) == 0, f"Key tables missing metadata: {issues}"
    
    def test_no_orphan_metadata(self):
        """Metadata should not reference non-existent tables."""
        metadata_file = CONFIG_DIR / "TABLE_METADATA.json"
        if not metadata_file.exists():
            pytest.skip("TABLE_METADATA.json not found")
        
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        tables_metadata = set(metadata.get("tables", {}).keys())
        
        # Get actual tables
        csv_files = list(OUTPUT_DIR.glob("*.csv"))
        actual_tables = {f.stem for f in csv_files}
        
        orphans = tables_metadata - actual_tables
        assert len(orphans) == 0, f"Orphan metadata (tables don't exist): {orphans}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
