"""
================================================================================
⚠️  DEPRECATED - DO NOT USE THIS FILE DIRECTLY ⚠️
================================================================================

Use `python run_etl.py` from the project root instead.

This file is kept for backward compatibility but should NOT be the primary
entry point. The run_etl.py script calls all necessary modules in the correct
order and creates all 130+ tables.

See CLAUDE.md and LLM_REQUIREMENTS.md for details.
================================================================================
"""

"""
BenchSight ETL Orchestrator
Comprehensive ETL system with multiple processing modes.

This is the UNIFIED incremental ETL implementation (merged from etl_orchestrator.py
and src/pipeline/incremental.py in v10.02).

Usage:
    from src.etl_orchestrator import ETLOrchestrator
    etl = ETLOrchestrator()
    
    # Check status
    etl.print_status()
    
    # Full ETL - all games, all tables
    etl.run_full()
    
    # Incremental - only new/changed games
    etl.run_incremental()
    
    # Selective - specific games or table types
    etl.run_selective(games=[18969], table_types=['core_fact'])
    
    # Append new data to existing table (true incremental)
    etl.append_to_table("fact_events", new_df, dedup_columns=['event_key'])
    
    # Remove a game's data from all tables
    etl.remove_game_data(18969)
    
CLI Usage:
    python -m src.etl_orchestrator status
    python -m src.etl_orchestrator full
    python -m src.etl_orchestrator incremental
    python -m src.etl_orchestrator reset
    python -m src.etl_orchestrator remove --game 18969
"""

import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set, Any
import pandas as pd

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Schema version - increment when schema changes require full rebuild
SCHEMA_VERSION = "10.03"

# Import table registry for validation and protection
try:
    from config.table_registry import TableRegistry, ProtectionLevel
    TABLE_REGISTRY_AVAILABLE = True
except ImportError:
    TABLE_REGISTRY_AVAILABLE = False

# Import safe CSV utilities
try:
    from src.core.safe_csv import safe_read_csv, safe_write_csv, validate_csv
    SAFE_CSV_AVAILABLE = True
except ImportError:
    SAFE_CSV_AVAILABLE = False


class ETLOrchestrator:
    """
    Comprehensive ETL orchestrator for BenchSight.
    
    Supports multiple processing modes:
    - Full ETL: Process all games, rebuild all tables
    - Incremental ETL: Only new/changed games
    - Selective ETL: Specific games or table types
    - Single Game: One game through full pipeline
    - Dimensions Only: Rebuild reference data
    """
    
    # Table categories for selective processing
    TABLE_CATEGORIES = {
        'dimensions': [
            'dim_player', 'dim_team', 'dim_game', 'dim_season', 'dim_venue',
            'dim_position', 'dim_event_type', 'dim_shift_type', 'dim_zone',
            'dim_shot_outcome', 'dim_pass_outcome', 'dim_save_outcome',
            'dim_zone_outcome', 'dim_penalty_type', 'dim_strength',
            'dim_play_detail', 'dim_play_pattern', 'dim_date', 'dim_time',
        ],
        'core_fact': [
            'fact_events', 'fact_event_players', 'fact_event_players',
            'fact_shifts', 'fact_shift_players', 'fact_shifts',
            'fact_gameroster', 'fact_player_game_stats',
        ],
        'advanced_fact': [
            'fact_player_season_stats', 'fact_team_game_stats',
            'fact_team_season_stats', 'fact_goalie_game_stats',
            'fact_goalie_season_stats', 'fact_h2h', 'fact_h2h_agg',
            'fact_possession_chains', 'fact_cycle_events',
            'fact_zone_entries', 'fact_zone_exits', 'fact_rushes',
            'fact_breakouts', 'fact_faceoffs', 'fact_penalties',
            'fact_saves', 'fact_scoring_chances',
        ],
        'xy': [
            'fact_event_xy', 'fact_shot_xy', 'fact_net_xy',
            'fact_pass_xy', 'fact_zone_xy',
        ],
        'video': [
            'fact_video_times', 'fact_video_highlights',
        ],
        'qa': [
            'qa_data_quality', 'qa_missing_keys', 'qa_validation_results',
        ],
        'analytics': [
            'fact_shift_quality', 'fact_shift_quality_logical',
            'fact_player_qoc_summary', 'fact_matchup_performance',
            'fact_player_stats_by_competition_tier',
            'fact_micro_events', 'fact_zone_transitions',
        ],
    }
    
    def __init__(
        self,
        base_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        mode: str = 'overwrite',
        log_level: int = logging.INFO
    ):
        """
        Initialize ETL orchestrator.
        
        Args:
            base_dir: Project base directory (default: auto-detect)
            output_dir: Output directory for CSVs (default: data/output)
            mode: 'overwrite' or 'append' for table writes
            log_level: Logging level
        """
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.output_dir = output_dir or self.base_dir / 'data' / 'output'
        self.raw_dir = self.base_dir / 'data' / 'raw' / 'games'
        self.state_file = self.base_dir / 'data' / '.etl_state.json'
        self.mode = mode
        
        # Setup logging
        self.logger = logging.getLogger('ETLOrchestrator')
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
        
        # Load state
        self.state = self._load_state()
        
        # Initialize table registry for validation
        self.table_registry = TableRegistry() if TABLE_REGISTRY_AVAILABLE else None
        if self.table_registry:
            self.logger.debug(f"Table registry loaded with {len(self.table_registry)} tables")
        
        # Track current run
        self.current_run = {
            'start_time': None,
            'games_processed': [],
            'tables_created': [],
            'errors': [],
        }
    
    def _load_state(self) -> Dict[str, Any]:
        """Load ETL state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    # Ensure schema version is current
                    state['schema_version'] = state.get('schema_version', SCHEMA_VERSION)
                    return state
            except Exception as e:
                self.logger.warning(f"Could not load state: {e}")
        
        return {
            'last_full_run': None,
            'last_incremental_run': None,
            'processed_games': {},
            'table_versions': {},
            'schema_version': SCHEMA_VERSION,
        }
    
    def _save_state(self):
        """Save ETL state to file."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            self.logger.warning(f"Could not save state: {e}")
    
    def _get_file_hash(self, filepath: Path) -> str:
        """Get MD5 hash of a file for change detection."""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def discover_games(self) -> List[int]:
        """
        Discover all games with tracking files.
        
        Returns:
            List of game IDs
        """
        games = []
        if self.raw_dir.exists():
            for game_dir in self.raw_dir.iterdir():
                if game_dir.is_dir() and game_dir.name.isdigit():
                    tracking_file = game_dir / f"{game_dir.name}_tracking.xlsx"
                    if tracking_file.exists():
                        games.append(int(game_dir.name))
        return sorted(games)
    
    def get_changed_games(self) -> List[int]:
        """
        Get games that have changed since last run.
        
        Returns:
            List of game IDs with new or modified tracking files
        """
        changed = []
        for game_id in self.discover_games():
            tracking_file = self.raw_dir / str(game_id) / f"{game_id}_tracking.xlsx"
            if tracking_file.exists():
                current_hash = self._get_file_hash(tracking_file)
                current_mtime = tracking_file.stat().st_mtime
                
                stored = self.state['processed_games'].get(str(game_id), {})
                stored_hash = stored.get('hash')
                
                if stored_hash != current_hash:
                    changed.append(game_id)
        
        return changed
    
    def get_unprocessed_games(self) -> List[int]:
        """
        Get games that have never been processed.
        
        Returns:
            List of game IDs not in state
        """
        all_games = set(self.discover_games())
        processed = set(int(g) for g in self.state['processed_games'].keys())
        return sorted(all_games - processed)
    
    def get_table_category(self, table_name: str) -> Optional[str]:
        """Get the category for a table name."""
        for category, tables in self.TABLE_CATEGORIES.items():
            if table_name in tables:
                return category
        return None
    
    def get_tables_by_category(self, categories: List[str]) -> List[str]:
        """Get all tables in specified categories."""
        tables = []
        for cat in categories:
            tables.extend(self.TABLE_CATEGORIES.get(cat, []))
        return tables
    
    def _mark_game_processed(self, game_id: int):
        """Mark a game as processed with its file hash and schema version."""
        tracking_file = self.raw_dir / str(game_id) / f"{game_id}_tracking.xlsx"
        if tracking_file.exists():
            self.state['processed_games'][str(game_id)] = {
                'hash': self._get_file_hash(tracking_file),
                'mtime': tracking_file.stat().st_mtime,
                'processed_at': datetime.now().isoformat(),
                'schema_version': SCHEMA_VERSION,
            }
    
    def print_status(self):
        """Print current ETL status."""
        print("\n" + "=" * 60)
        print("BenchSight ETL Status")
        print("=" * 60)
        
        all_games = self.discover_games()
        changed = self.get_changed_games()
        unprocessed = self.get_unprocessed_games()
        
        print(f"\nDiscovered Games: {len(all_games)}")
        print(f"  Games: {all_games}")
        
        print(f"\nProcessed Games: {len(self.state.get('processed_games', {}))}")
        for game_id, info in self.state.get('processed_games', {}).items():
            print(f"  {game_id}: processed {info.get('processed_at', 'unknown')}")
        
        print(f"\nNew Games: {len(unprocessed)}")
        if unprocessed:
            print(f"  {unprocessed}")
        
        print(f"\nChanged Games: {len(changed)}")
        if changed:
            print(f"  {changed}")
        
        print(f"\nLast Full Run: {self.state.get('last_full_run', 'Never')}")
        print(f"Last Incremental Run: {self.state.get('last_incremental_run', 'Never')}")
        print(f"Schema Version: {self.state.get('schema_version', 'Unknown')} (current: {SCHEMA_VERSION})")
        
        # Incremental recommendation
        if self.needs_full_etl():
            print(f"\n⚠️  FULL ETL RECOMMENDED")
        else:
            print(f"\n✅ Incremental ETL available")
        
        # Count output tables
        if self.output_dir.exists():
            tables = list(self.output_dir.glob('*.csv'))
            print(f"\nOutput Tables: {len(tables)}")
        
        # Table Registry Status
        if self.table_registry:
            print(f"\n--- Table Registry ---")
            print(f"  Registered Tables: {len(self.table_registry)}")
            missing = self.table_registry.validate()
            if missing:
                print(f"  Missing Tables: {len(missing)}")
            else:
                print(f"  ✅ All registered tables present")
        else:
            print(f"\n⚠️ Table Registry not loaded")
        
        # Safe CSV Status
        print(f"\n--- Module Status ---")
        print(f"  Table Registry: {'✅ Loaded' if TABLE_REGISTRY_AVAILABLE else '❌ Not Available'}")
        print(f"  Safe CSV: {'✅ Loaded' if SAFE_CSV_AVAILABLE else '❌ Not Available'}")
        
        print("=" * 60 + "\n")
    
    def _run_base_etl(self, games: Optional[List[int]] = None):
        """
        Run the base ETL pipeline.
        
        Args:
            games: Optional list of specific game IDs to process
        """
        try:
            from src.core.base_etl import main as base_etl_main
            
            # If specific games, we need to filter
            if games:
                self.logger.info(f"Running base ETL for games: {games}")
                # The base ETL reads from raw/games, so all discovered games will be processed
                # For selective processing, we'd need to modify base_etl or use a different approach
            
            base_etl_main()
            return True
        except Exception as e:
            self.logger.error(f"Base ETL failed: {e}")
            self.current_run['errors'].append(str(e))
            return False
    
    def _run_post_processing(self):
        """Run post-ETL enhancements."""
        try:
            from src.etl.post_etl_processor import PostETLProcessor
            processor = PostETLProcessor(str(self.output_dir))
            processor.run()
            return True
        except ImportError:
            self.logger.warning("PostETLProcessor not available")
            return True
        except Exception as e:
            self.logger.error(f"Post-processing failed: {e}")
            self.current_run['errors'].append(str(e))
            return False
    
    def _run_extended_tables(self):
        """Run extended table creation."""
        try:
            from src.advanced.extended_tables import create_extended_tables
            create_extended_tables()
            return True
        except ImportError:
            self.logger.warning("Extended tables module not available")
            return True
        except Exception as e:
            self.logger.error(f"Extended tables failed: {e}")
            self.current_run['errors'].append(str(e))
            return False
    
    def _run_core_player_stats(self):
        """Build core player stats tables (fact_player_game_stats, fact_shift_players)."""
        try:
            from src.core.build_player_stats import main as build_stats
            build_stats()
            return True
        except ImportError:
            self.logger.warning("Core player stats module not available")
            return True
        except Exception as e:
            self.logger.error(f"Core player stats failed: {e}")
            self.current_run['errors'].append(str(e))
            return False
    
    def _run_stats_enhancement(self):
        """Run stats enhancement modules."""
        try:
            # Try enhance_all_stats first
            from src.advanced.enhance_all_stats import main as enhance_stats
            enhance_stats()
            return True
        except ImportError:
            self.logger.warning("Stats enhancement module not available")
            return True
        except FileNotFoundError as e:
            self.logger.warning(f"Stats enhancement skipped - missing file: {e}")
            return True
        except Exception as e:
            self.logger.warning(f"Stats enhancement skipped - error: {e}")
            # Don't fail the pipeline, continue to XY tables
            return True
    
    def _run_additional_tables(self):
        """Run additional table creation."""
        try:
            from src.advanced.create_additional_tables import create_all_additional_tables
            create_all_additional_tables(str(self.output_dir))
            return True
        except ImportError:
            self.logger.warning("Additional tables module not available")
            return True
        except Exception as e:
            self.logger.error(f"Additional tables failed: {e}")
            self.current_run['errors'].append(str(e))
            return False
    
    def _run_event_time_context(self):
        """Run event time and TOI context enhancement."""
        try:
            from src.advanced.event_time_context import enhance_event_tables
            results = enhance_event_tables()
            self.logger.info(f"Event time context: enhanced {len(results)} tables")
            return True
        except ImportError:
            self.logger.warning("Event time context module not available")
            return True
        except Exception as e:
            self.logger.error(f"Event time context failed: {e}")
            self.current_run['errors'].append(str(e))
            return False
    
    def _run_v11_enhancements(self):
        """Run v11 enhancements (TOI propagation, docs, version stamp)."""
        try:
            from src.advanced.v11_enhancements import run_all_enhancements
            run_all_enhancements()
            self.logger.info("V11 enhancements completed")
            return True
        except ImportError:
            self.logger.warning("V11 enhancements module not available")
            return True
        except Exception as e:
            self.logger.error(f"V11 enhancements failed: {e}")
            self.current_run['errors'].append(str(e))
            return False
    
    def _run_xy_tables(self):
        """Run XY table builder (spatial analytics)."""
        try:
            from src.xy.xy_table_builder import build_all_xy_tables
            results = build_all_xy_tables()
            if isinstance(results, dict):
                total_rows = sum(v for v in results.values() if isinstance(v, int))
                self.logger.info(f"XY tables: {len(results)} tables, {total_rows} rows")
            return True
        except ImportError:
            self.logger.warning("XY table builder module not available")
            return True
        except Exception as e:
            self.logger.error(f"XY tables failed: {e}")
            self.current_run['errors'].append(str(e))
            return False
    
    def _run_missing_tables(self):
        """Run missing tables builder (dimensions, analytics, etc.)."""
        try:
            from src.tables.build_missing_tables import build_all_missing_tables
            results = build_all_missing_tables(verbose=True)
            if results['errors']:
                for err in results['errors']:
                    self.logger.warning(f"Missing tables warning: {err}")
            self.logger.info(f"Missing tables: created {results['total_tables']} tables")
            return True
        except ImportError:
            self.logger.warning("Missing tables module not available")
            return True
        except Exception as e:
            self.logger.error(f"Missing tables failed: {e}")
            self.current_run['errors'].append(str(e))
            return False
    
    def run_full(self) -> bool:
        """
        Run full ETL - process all games, rebuild all tables.
        
        Returns:
            True if successful
        """
        self.logger.info("Starting FULL ETL...")
        self.current_run['start_time'] = datetime.now()
        
        # Run all stages
        stages = [
            ("Base ETL", self._run_base_etl),
            ("Core Player Stats", self._run_core_player_stats),
            ("Post Processing", self._run_post_processing),
            ("Extended Tables", self._run_extended_tables),
            ("Missing Tables", self._run_missing_tables),
            ("Stats Enhancement", self._run_stats_enhancement),
            ("Additional Tables", self._run_additional_tables),
            ("Event Time Context", self._run_event_time_context),
            ("V11 Enhancements", self._run_v11_enhancements),
            ("XY Tables", self._run_xy_tables),  # v19: Spatial analytics
        ]
        
        for stage_name, stage_func in stages:
            self.logger.info(f"Running stage: {stage_name}")
            if not stage_func():
                self.logger.error(f"Stage {stage_name} failed!")
                return False
        
        # Mark all games as processed
        for game_id in self.discover_games():
            self._mark_game_processed(game_id)
            self.current_run['games_processed'].append(game_id)
        
        # Update state
        self.state['last_full_run'] = datetime.now().isoformat()
        self._save_state()
        
        # Count tables
        if self.output_dir.exists():
            tables = list(self.output_dir.glob('*.csv'))
            self.current_run['tables_created'] = [t.stem for t in tables]
            self.logger.info(f"Created {len(tables)} tables")
        
        self.logger.info("FULL ETL completed successfully!")
        return True
    
    def run_incremental(self) -> bool:
        """
        Run incremental ETL - only new/changed games.
        
        Returns:
            True if successful
        """
        changed = self.get_changed_games()
        unprocessed = self.get_unprocessed_games()
        games_to_process = sorted(set(changed + unprocessed))
        
        if not games_to_process:
            self.logger.info("No new or changed games to process")
            return True
        
        self.logger.info(f"Incremental ETL for games: {games_to_process}")
        self.current_run['start_time'] = datetime.now()
        
        # For incremental, we run the full pipeline but could optimize
        # by only processing specific games if the ETL supports it
        success = self._run_base_etl(games_to_process)
        
        if success:
            self._run_post_processing()
            self._run_extended_tables()
            self._run_additional_tables()
            
            for game_id in games_to_process:
                self._mark_game_processed(game_id)
                self.current_run['games_processed'].append(game_id)
            
            self.state['last_incremental_run'] = datetime.now().isoformat()
            self._save_state()
        
        return success
    
    def run_selective(
        self,
        games: Optional[List[int]] = None,
        table_types: Optional[List[str]] = None,
        fact_tables: Optional[List[str]] = None,
    ) -> bool:
        """
        Run selective ETL with fine-grained control.
        
        Args:
            games: Specific game IDs to process (None = all)
            table_types: Table categories to build (e.g., ['dimensions', 'core_fact'])
            fact_tables: Specific fact tables to rebuild
        
        Returns:
            True if successful
        """
        self.logger.info("Starting SELECTIVE ETL...")
        self.current_run['start_time'] = datetime.now()
        
        # Determine games
        target_games = games if games else self.discover_games()
        self.logger.info(f"Target games: {target_games}")
        
        # Determine tables
        if table_types:
            target_tables = self.get_tables_by_category(table_types)
            self.logger.info(f"Target table types: {table_types}")
            self.logger.info(f"Target tables: {target_tables}")
        elif fact_tables:
            target_tables = fact_tables
            self.logger.info(f"Target tables: {target_tables}")
        else:
            target_tables = None  # All tables
        
        # Run base ETL (processes all by default)
        success = self._run_base_etl(target_games)
        
        if success:
            # Run enhancements
            self._run_post_processing()
            self._run_extended_tables()
            self._run_additional_tables()
            
            for game_id in target_games:
                self._mark_game_processed(game_id)
                self.current_run['games_processed'].append(game_id)
            
            self._save_state()
        
        return success
    
    def run_single_game(self, game_id: int) -> bool:
        """
        Process a single game through the full pipeline.
        
        Args:
            game_id: Game ID to process
        
        Returns:
            True if successful
        """
        self.logger.info(f"Processing single game: {game_id}")
        return self.run_selective(games=[game_id])
    
    def run_dimensions_only(self) -> bool:
        """
        Rebuild only dimension tables (no fact tables).
        
        Returns:
            True if successful
        """
        self.logger.info("Rebuilding dimensions only...")
        return self.run_selective(table_types=['dimensions'])
    
    def reset_state(self):
        """Reset ETL state (mark all games as unprocessed)."""
        self.logger.info("Resetting ETL state...")
        self.state = {
            'last_full_run': None,
            'last_incremental_run': None,
            'processed_games': {},
            'table_versions': {},
            'schema_version': SCHEMA_VERSION,
        }
        self._save_state()
        self.logger.info("State reset complete")
    
    # =========================================================================
    # INCREMENTAL ETL METHODS (merged from src/pipeline/incremental.py)
    # =========================================================================
    
    def needs_full_etl(self) -> bool:
        """
        Check if a full ETL is needed (schema version change, first run, etc.).
        
        Returns:
            True if full ETL recommended
        """
        # Never run before
        if self.state.get('last_full_run') is None:
            self.logger.info("Full ETL needed: No previous run")
            return True
        
        # Schema version changed
        current_version = self.state.get('schema_version', '0.0.0')
        if current_version != SCHEMA_VERSION:
            self.logger.info(f"Full ETL needed: Schema version changed ({current_version} -> {SCHEMA_VERSION})")
            return True
        
        # Check if any processed game has old schema version
        for game_id, game_info in self.state.get('processed_games', {}).items():
            if game_info.get('schema_version') != SCHEMA_VERSION:
                self.logger.info(f"Full ETL needed: Game {game_id} processed with old schema")
                return True
        
        return False
    
    def append_to_table(self, table_name: str, new_data: pd.DataFrame, 
                        dedup_columns: List[str] = None) -> int:
        """
        Append new data to an existing table with deduplication.
        
        This is useful for true incremental processing where you want to
        add new game data without rebuilding entire tables.
        
        Args:
            table_name: Name of the table (without .csv)
            new_data: DataFrame with new rows to append
            dedup_columns: Columns to use for deduplication (default: all columns)
            
        Returns:
            Number of rows added
        """
        table_path = self.output_dir / f"{table_name}.csv"
        
        if not table_path.exists():
            # First time - just save
            if SAFE_CSV_AVAILABLE:
                safe_write_csv(new_data, str(table_path), atomic=True)
            else:
                new_data.to_csv(table_path, index=False)
            self.logger.info(f"Created {table_name} with {len(new_data)} rows")
            return len(new_data)
        
        # Load existing data
        if SAFE_CSV_AVAILABLE:
            existing = safe_read_csv(str(table_path))
        else:
            existing = pd.read_csv(table_path, low_memory=False)
        
        before_count = len(existing)
        
        # Combine
        combined = pd.concat([existing, new_data], ignore_index=True)
        
        # Deduplicate
        if dedup_columns:
            combined = combined.drop_duplicates(subset=dedup_columns, keep='last')
        else:
            combined = combined.drop_duplicates(keep='last')
        
        # Save
        if SAFE_CSV_AVAILABLE:
            safe_write_csv(combined, str(table_path), atomic=True)
        else:
            combined.to_csv(table_path, index=False)
        
        added = len(combined) - before_count
        self.logger.info(f"Appended to {table_name}: {before_count} -> {len(combined)} (+{added})")
        return added
    
    def remove_game_data(self, game_id: int, tables: List[str] = None) -> Dict[str, int]:
        """
        Remove data for a specific game from tables.
        
        Useful when reprocessing a game or removing bad data.
        
        Args:
            game_id: Game ID to remove
            tables: List of table names to clean (default: all tables with game_id column)
            
        Returns:
            Dict of {table_name: rows_removed}
        """
        results = {}
        
        if tables is None:
            tables = [f.stem for f in self.output_dir.glob("*.csv")]
        
        for table_name in tables:
            table_path = self.output_dir / f"{table_name}.csv"
            if not table_path.exists():
                continue
            
            try:
                df = pd.read_csv(table_path, low_memory=False)
                if 'game_id' in df.columns:
                    before = len(df)
                    # Handle both int and string game_id
                    df = df[df['game_id'].astype(str) != str(game_id)]
                    after = len(df)
                    removed = before - after
                    
                    if removed > 0:
                        if SAFE_CSV_AVAILABLE:
                            safe_write_csv(df, str(table_path), atomic=True)
                        else:
                            df.to_csv(table_path, index=False)
                        results[table_name] = removed
                        self.logger.info(f"Removed {removed} rows from {table_name}")
            except Exception as e:
                self.logger.warning(f"Could not clean {table_name}: {e}")
        
        # Mark game as unprocessed
        if str(game_id) in self.state.get('processed_games', {}):
            del self.state['processed_games'][str(game_id)]
            self._save_state()
            self.logger.info(f"Marked game {game_id} as unprocessed")
        
        return results
    
    def get_processing_status(self) -> Dict[str, Any]:
        """
        Get detailed processing status for all games.
        
        Returns:
            Dict with processing details
        """
        all_games = self.discover_games()
        processed = set(int(g) for g in self.state.get('processed_games', {}).keys())
        changed = self.get_changed_games()
        unprocessed = self.get_unprocessed_games()
        
        return {
            'total_games': len(all_games),
            'processed_count': len(processed),
            'changed_count': len(changed),
            'unprocessed_count': len(unprocessed),
            'all_games': all_games,
            'processed_games': list(processed),
            'changed_games': changed,
            'unprocessed_games': unprocessed,
            'needs_full_etl': self.needs_full_etl(),
            'last_full_run': self.state.get('last_full_run'),
            'last_incremental_run': self.state.get('last_incremental_run'),
            'schema_version': self.state.get('schema_version'),
            'current_schema_version': SCHEMA_VERSION,
        }
    
    def validate_output(self) -> Dict[str, Any]:
        """
        Validate ETL output using table registry.
        
        Returns:
            Validation results dictionary
        """
        results = {
            'valid': True,
            'table_count': 0,
            'missing_critical': [],
            'empty_tables': [],
            'protected_missing': [],
            'registry_validation': [],
            'errors': [],
        }
        
        # Count tables
        if self.output_dir.exists():
            tables = list(self.output_dir.glob('*.csv'))
            results['table_count'] = len(tables)
        
        # Use table registry if available
        if self.table_registry:
            # Check for missing registered tables
            missing = self.table_registry.validate()
            if missing:
                results['registry_validation'] = missing[:10]  # First 10
                self.logger.warning(f"Registry reports {len(missing)} missing tables")
            
            # Check critical tables from registry
            critical = self.table_registry.get_critical_tables()
            for table in critical:
                table_path = self.output_dir / f"{table}.csv"
                if not table_path.exists():
                    results['missing_critical'].append(table)
                    results['valid'] = False
                else:
                    try:
                        if SAFE_CSV_AVAILABLE:
                            is_valid, errors = validate_csv(str(table_path), min_rows=1)
                            if not is_valid:
                                results['empty_tables'].append(table)
                        else:
                            df = pd.read_csv(table_path, nrows=1)
                            if len(df) == 0:
                                results['empty_tables'].append(table)
                    except Exception as e:
                        results['errors'].append(f"{table}: {str(e)}")
                        results['valid'] = False
        else:
            # Fallback: Check hardcoded critical tables
            critical = [
                'fact_events', 'fact_event_players', 'fact_shift_players',
                'fact_gameroster', 'fact_player_game_stats',
                'dim_player', 'dim_team', 'dim_game',
            ]
            
            for table in critical:
                table_path = self.output_dir / f"{table}.csv"
                if not table_path.exists():
                    results['missing_critical'].append(table)
                    results['valid'] = False
                else:
                    try:
                        df = pd.read_csv(table_path, nrows=1)
                        if len(df) == 0:
                            results['empty_tables'].append(table)
                    except Exception as e:
                        results['errors'].append(f"{table}: {str(e)}")
                        results['valid'] = False
        
        return results
    
    def check_table_protection(self, table_name: str) -> bool:
        """
        Check if a table is protected from deletion.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if protected, False if can be deleted
        """
        if self.table_registry:
            return self.table_registry.is_protected(table_name)
        return False
    
    def get_table_source(self, table_name: str) -> str:
        """
        Get the source module for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Source module path or 'UNKNOWN'
        """
        if self.table_registry:
            return self.table_registry.get_source(table_name)
        return 'UNKNOWN'
    
    # =========================================================================
    # SUPABASE INTEGRATION
    # =========================================================================
    
    def _upload_to_supabase(self) -> bool:
        """
        Upload ALL tables to Supabase after ETL is complete.
        
        This uploads the FINAL state of all CSVs in data/output/ to Supabase.
        Called after all ETL stages are complete, so Supabase gets the
        fully processed data.
        """
        try:
            from src.core.table_writer import upload_all_tables
            
            self.logger.info("Uploading all tables to Supabase...")
            result = upload_all_tables()
            
            self.logger.info(f"Upload complete: {result['tables_success']}/{result['tables_attempted']} tables")
            self.logger.info(f"Total rows: {result['total_rows']:,}")
            
            if result['errors']:
                self.logger.warning(f"Upload errors in {len(result['errors'])} tables")
                for table, errs in list(result['errors'].items())[:5]:
                    self.logger.warning(f"  {table}: {errs[0][:60]}")
            
            return result['tables_failed'] == 0
            
        except ImportError as e:
            self.logger.error(f"Table writer not available: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Supabase upload failed: {e}")
            return False
    
    def _generate_supabase_schema(self) -> bool:
        """Generate Supabase schema SQL from current output."""
        try:
            from src.supabase.supabase_manager import SupabaseManager
            mgr = SupabaseManager()
            result = mgr.reset_schema()
            self.logger.info(f"Generated Supabase schema: {result['tables_created']} tables")
            self.logger.info(f"Type distribution: {result['type_summary']}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to generate schema: {e}")
            return False
    
    def run_full_with_upload(self) -> bool:
        """
        Run full ETL then upload all tables to Supabase.
        
        Flow:
        1. Run all ETL stages (creates/modifies CSVs)
        2. Generate Supabase schema SQL
        3. Upload ALL final CSVs to Supabase
        
        This ensures Supabase gets the FINAL state after all processing.
        
        Returns:
            True if successful
        """
        self.logger.info("=" * 60)
        self.logger.info("FULL ETL WITH SUPABASE UPLOAD")
        self.logger.info("=" * 60)
        
        # Run full ETL first
        if not self.run_full():
            self.logger.error("ETL failed, skipping Supabase upload")
            return False
        
        # Generate schema SQL
        self.logger.info("\n" + "-" * 60)
        self.logger.info("Generating Supabase schema...")
        self._generate_supabase_schema()
        
        # Upload ALL tables to Supabase
        self.logger.info("\n" + "-" * 60)
        self.logger.info("Uploading to Supabase...")
        return self._upload_to_supabase()


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='BenchSight ETL Orchestrator')
    parser.add_argument('command', choices=['status', 'full', 'incremental', 'reset', 'validate', 'remove', 'check', 'upload'],
                       help='Command to run')
    parser.add_argument('--game', type=int, help='Game ID (for remove command)')
    parser.add_argument('--games', type=str, help='Comma-separated game IDs')
    parser.add_argument('--upload', action='store_true', help='Upload to Supabase after ETL')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    log_level = logging.DEBUG if args.verbose else logging.INFO
    etl = ETLOrchestrator(log_level=log_level)
    
    if args.command == 'status':
        etl.print_status()
    elif args.command == 'full':
        if args.upload:
            etl.run_full_with_upload()
        else:
            etl.run_full()
    elif args.command == 'incremental':
        etl.run_incremental()
    elif args.command == 'reset':
        etl.reset_state()
    elif args.command == 'validate':
        results = etl.validate_output()
        print(json.dumps(results, indent=2))
    elif args.command == 'remove':
        if not args.game:
            print("Error: --game required for remove command")
            return
        results = etl.remove_game_data(args.game)
        print(f"Removed data for game {args.game}:")
        for table, count in results.items():
            print(f"  {table}: {count} rows")
    elif args.command == 'check':
        status = etl.get_processing_status()
        print(json.dumps(status, indent=2, default=str))
        if status['needs_full_etl']:
            print("\n⚠️  Full ETL recommended")
        else:
            print("\n✅ Incremental ETL available")
    elif args.command == 'upload':
        # Upload only (no ETL)
        etl._run_supabase_upload()


if __name__ == '__main__':
    main()
