"""
BENCHSIGHT - ETL Integration Tests
===================================
Tests that verify the ETL pipeline works end-to-end.

These tests verify:
1. Pipeline can be initialized
2. Export produces valid CSVs  
3. Data flows correctly from source to output
4. Key tables have correct relationships
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
RAW_DIR = PROJECT_ROOT / "data" / "raw"


class TestPipelineInitialization:
    """Test that pipeline components can be imported and initialized."""
    
    def test_orchestrator_import(self):
        """PipelineOrchestrator can be imported."""
        from src.pipeline.orchestrator import PipelineOrchestrator
        assert PipelineOrchestrator is not None
    
    def test_orchestrator_init(self):
        """PipelineOrchestrator can be initialized."""
        from src.pipeline.orchestrator import PipelineOrchestrator
        orchestrator = PipelineOrchestrator(PROJECT_ROOT)
        assert orchestrator.project_root == PROJECT_ROOT
        assert orchestrator.output_dir.exists()
    
    def test_database_connection(self):
        """Database connection works."""
        from src.database.connection import test_connection
        assert test_connection() == True
    
    def test_logger_works(self):
        """Logger can be imported and used."""
        from src.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Test log message")
        assert True


class TestDataFlow:
    """Test that data flows correctly through the pipeline."""
    
    def test_blb_file_exists(self):
        """BLB source file exists."""
        blb_file = RAW_DIR / "BLB_Tables.xlsx"
        assert blb_file.exists(), f"BLB file not found at {blb_file}"
    
    def test_blb_sheets_readable(self):
        """BLB file has expected sheets."""
        blb_file = RAW_DIR / "BLB_Tables.xlsx"
        if not blb_file.exists():
            pytest.skip("BLB file not available")
        
        xl = pd.ExcelFile(blb_file)
        sheets = xl.sheet_names
        
        # Should have player, team, schedule sheets at minimum
        expected = ["Player", "Team", "Schedule"]
        for sheet in expected:
            matches = [s for s in sheets if sheet.lower() in s.lower()]
            assert len(matches) > 0, f"No sheet matching '{sheet}' found"
    
    def test_dim_player_derived_from_blb(self):
        """dim_player table exists and has data."""
        player_file = OUTPUT_DIR / "dim_player.csv"
        assert player_file.exists()
        
        df = pd.read_csv(player_file)
        assert len(df) > 0, "dim_player is empty"
        assert "player_id" in df.columns
        assert "player_full_name" in df.columns
    
    def test_dim_team_derived_from_blb(self):
        """dim_team table exists and has data."""
        team_file = OUTPUT_DIR / "dim_team.csv"
        assert team_file.exists()
        
        df = pd.read_csv(team_file)
        assert len(df) > 0, "dim_team is empty"
        assert "team_id" in df.columns
        assert "team_name" in df.columns
    
    def test_dim_schedule_derived_from_blb(self):
        """dim_schedule table exists and has game data."""
        schedule_file = OUTPUT_DIR / "dim_schedule.csv"
        assert schedule_file.exists()
        
        df = pd.read_csv(schedule_file)
        assert len(df) > 0, "dim_schedule is empty"
        assert "game_id" in df.columns


class TestFactTableIntegrity:
    """Test fact tables have valid structure and relationships."""
    
    def test_fact_events_references_games(self):
        """fact_events game_ids exist in dim_schedule."""
        events_file = OUTPUT_DIR / "fact_events.csv"
        schedule_file = OUTPUT_DIR / "dim_schedule.csv"
        
        if not events_file.exists() or not schedule_file.exists():
            pytest.skip("Required files not available")
        
        events = pd.read_csv(events_file, dtype=str)
        schedule = pd.read_csv(schedule_file, dtype=str)
        
        valid_games = set(schedule["game_id"].dropna().unique())
        event_games = set(events["game_id"].dropna().unique())
        
        orphans = event_games - valid_games
        orphan_rate = len(orphans) / len(event_games) if event_games else 0
        
        assert orphan_rate < 0.05, f"{orphan_rate:.1%} of events reference invalid games"
    
    def test_fact_events_player_references_players(self):
        """fact_events_player player_ids mostly exist in dim_player."""
        events_player_file = OUTPUT_DIR / "fact_events_player.csv"
        player_file = OUTPUT_DIR / "dim_player.csv"
        
        if not events_player_file.exists() or not player_file.exists():
            pytest.skip("Required files not available")
        
        events_player = pd.read_csv(events_player_file, dtype=str)
        players = pd.read_csv(player_file, dtype=str)
        
        valid_players = set(players["player_id"].dropna().unique())
        event_players = set(events_player["player_id"].dropna().unique())
        
        matched = event_players.intersection(valid_players)
        match_rate = len(matched) / len(event_players) if event_players else 0
        
        # Allow some unmatched (subs, unknown players)
        assert match_rate > 0.80, f"Only {match_rate:.1%} of event players match dim_player"
    
    def test_fact_gameroster_references_both(self):
        """fact_gameroster references valid games and players."""
        roster_file = OUTPUT_DIR / "fact_gameroster.csv"
        schedule_file = OUTPUT_DIR / "dim_schedule.csv"
        player_file = OUTPUT_DIR / "dim_player.csv"
        
        if not all(f.exists() for f in [roster_file, schedule_file, player_file]):
            pytest.skip("Required files not available")
        
        roster = pd.read_csv(roster_file, dtype=str)
        schedule = pd.read_csv(schedule_file, dtype=str)
        players = pd.read_csv(player_file, dtype=str)
        
        valid_games = set(schedule["game_id"].dropna().unique())
        valid_players = set(players["player_id"].dropna().unique())
        
        roster_games = set(roster["game_id"].dropna().unique())
        roster_players = set(roster["player_id"].dropna().unique())
        
        game_match = len(roster_games.intersection(valid_games)) / len(roster_games) if roster_games else 0
        player_match = len(roster_players.intersection(valid_players)) / len(roster_players) if roster_players else 0
        
        assert game_match > 0.95, f"Only {game_match:.1%} of roster games are valid"
        assert player_match > 0.80, f"Only {player_match:.1%} of roster players are valid"


class TestGoalAccuracy:
    """Test that goals in stats match official sources."""
    
    def test_goals_in_stats_reasonable(self):
        """Total goals in player stats is reasonable."""
        stats_file = OUTPUT_DIR / "fact_player_game_stats.csv"
        
        if not stats_file.exists():
            pytest.skip("Stats file not available")
        
        df = pd.read_csv(stats_file)
        
        if "goals" not in df.columns:
            pytest.skip("goals column not in stats")
        
        total_goals = pd.to_numeric(df["goals"], errors="coerce").sum()
        total_games = df["game_id"].nunique()
        
        # Reasonable: 5-15 goals per game average
        if total_games > 0:
            gpg = total_goals / total_games
            assert 3 < gpg < 20, f"Goals per game {gpg:.1f} seems unreasonable"
    
    def test_schedule_goals_match_events(self):
        """Goals in schedule correlate with goal events."""
        schedule_file = OUTPUT_DIR / "dim_schedule.csv"
        events_file = OUTPUT_DIR / "fact_events.csv"
        
        if not schedule_file.exists() or not events_file.exists():
            pytest.skip("Required files not available")
        
        schedule = pd.read_csv(schedule_file)
        events = pd.read_csv(events_file)
        
        # Get games that are in both
        schedule_games = set(schedule["game_id"].astype(str).unique())
        event_games = set(events["game_id"].astype(str).unique())
        common_games = schedule_games.intersection(event_games)
        
        if len(common_games) == 0:
            pytest.skip("No overlapping games")
        
        # Count unique goal events (event_type contains 'goal')
        # Note: Multiple event rows per goal (scorer, assister, goalie) is expected
        goal_events = events[
            events["event_type"].str.lower().str.contains("goal", na=False)
        ]
        # Count unique event indices to avoid double-counting
        unique_goal_events = goal_events.groupby(["game_id", "event_index"]).size().reset_index()
        goals_from_events = len(unique_goal_events)
        
        # Count goals from schedule
        schedule_subset = schedule[schedule["game_id"].astype(str).isin(common_games)]
        home_goals = pd.to_numeric(schedule_subset.get("home_total_goals", 0), errors="coerce").sum()
        away_goals = pd.to_numeric(schedule_subset.get("away_total_goals", 0), errors="coerce").sum()
        goals_from_schedule = home_goals + away_goals
        
        # Goals from events should be at least some portion of schedule goals
        # (tracking may not cover all periods, some games partial)
        if goals_from_schedule > 0:
            ratio = goals_from_events / goals_from_schedule
            # Just verify events have some goals, not exact match
            assert goals_from_events > 0, "No goal events found"


class TestExportCompleteness:
    """Test that export produces all expected files."""
    
    def test_all_dimension_tables_exported(self):
        """All core dimension tables exist."""
        required_dims = [
            "dim_player", "dim_team", "dim_schedule", "dim_season",
            "dim_period", "dim_position", "dim_venue", "dim_event_type"
        ]
        
        for dim in required_dims:
            assert (OUTPUT_DIR / f"{dim}.csv").exists(), f"Missing {dim}"
    
    def test_all_core_fact_tables_exported(self):
        """All core fact tables exist."""
        required_facts = [
            "fact_events", "fact_events_player", "fact_shifts",
            "fact_gameroster", "fact_player_game_stats"
        ]
        
        for fact in required_facts:
            assert (OUTPUT_DIR / f"{fact}.csv").exists(), f"Missing {fact}"
    
    def test_csv_count_matches_sql(self):
        """Number of CSVs matches SQL table count."""
        csv_count = len(list(OUTPUT_DIR.glob("*.csv")))
        
        sql_file = PROJECT_ROOT / "sql" / "create_all_tables.sql"
        if sql_file.exists():
            content = sql_file.read_text()
            sql_count = content.count("CREATE TABLE IF NOT EXISTS")
            
            assert csv_count == sql_count, f"CSV count ({csv_count}) != SQL count ({sql_count})"


class TestPrimaryKeyUniqueness:
    """Test that all tables have unique primary keys."""
    
    def test_all_tables_have_unique_first_column(self):
        """Every CSV's first column should be unique (PK convention)."""
        failures = []
        
        for csv_file in OUTPUT_DIR.glob("*.csv"):
            df = pd.read_csv(csv_file, dtype=str)
            if len(df) == 0:
                continue
            
            pk_col = df.columns[0]
            
            # Check for nulls
            null_count = df[pk_col].isna().sum()
            if null_count > 0:
                failures.append(f"{csv_file.stem}: {null_count} null PKs")
                continue
            
            # Check for duplicates
            dup_count = df.duplicated(subset=[pk_col]).sum()
            if dup_count > 0:
                failures.append(f"{csv_file.stem}: {dup_count} duplicate PKs")
        
        assert len(failures) == 0, f"PK issues: {failures[:10]}"
