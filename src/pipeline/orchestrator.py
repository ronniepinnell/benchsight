"""
=============================================================================
PIPELINE ORCHESTRATOR
=============================================================================
File: src/pipeline/orchestrator.py

PURPOSE:
    Coordinate the full ETL pipeline across all layers.
    Handle single or multiple game processing.

USAGE:
    from src.pipeline.orchestrator import PipelineOrchestrator
    
    orchestrator = PipelineOrchestrator()
    orchestrator.run_full_pipeline([18969, 18970, 18971])

=============================================================================
"""

from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime

from src.database.connection import get_engine, test_connection
from src.database.table_operations import (
    get_tables_by_layer,
    get_row_count,
    table_exists
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineOrchestrator:
    """
    Coordinates the full ETL pipeline.
    
    WHY THIS CLASS:
        - Single entry point for all pipeline operations
        - Manages dependencies between layers
        - Tracks processing status
        - Handles errors gracefully
    
    Attributes:
        project_root: Path to project root directory.
        blb_file: Path to BLB_Tables.xlsx.
        games_dir: Path to games folder.
        output_dir: Path for CSV exports.
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize the orchestrator.
        
        Args:
            project_root: Path to project root. Auto-detected if None.
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        
        self.project_root = project_root
        self.blb_file = project_root / 'data' / 'raw' / 'BLB_Tables.xlsx'
        self.games_dir = project_root / 'data' / 'raw' / 'games'
        self.output_dir = project_root / 'data' / 'output'
        
        # Ensure directories exist
        self.games_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        get_engine()
    
    def run_full_pipeline(
        self,
        game_ids: Union[int, List[int]] = None,
        reload_blb: bool = False,
        export_csv: bool = True
    ) -> Dict:
        """
        Run the complete ETL pipeline.
        
        WHY THIS METHOD:
            Single call to process everything.
            Handles dependencies automatically.
        
        Args:
            game_ids: Single game ID or list of game IDs to process.
                      If None, processes all available games.
            reload_blb: Force reload of BLB tables.
            export_csv: Export results to CSV files.
        
        Returns:
            Dictionary with processing results and statistics.
        """
        start_time = datetime.now()
        results = {
            'start_time': start_time.isoformat(),
            'stages': {},
            'games_processed': [],
            'errors': []
        }
        
        # Normalize game_ids to list
        if game_ids is None:
            game_ids = self.get_available_games()
        elif isinstance(game_ids, int):
            game_ids = [game_ids]
        
        logger.info(f"Starting pipeline for {len(game_ids)} game(s): {game_ids}")
        
        try:
            # Stage 1: Load BLB tables
            logger.info("=" * 60)
            logger.info("STAGE 1: Loading BLB tables...")
            blb_results = self._run_stage_blb(reload_blb)
            results['stages']['blb_stage'] = blb_results
            
            # Stage 2: Load game tracking data
            logger.info("=" * 60)
            logger.info(f"STAGE 2: Loading {len(game_ids)} game(s)...")
            game_stage_results = self._run_stage_games(game_ids)
            results['stages']['games_stage'] = game_stage_results
            
            # Stage 3: Transform BLB to intermediate
            logger.info("=" * 60)
            logger.info("STAGE 3: Transforming BLB tables...")
            blb_int_results = self._run_intermediate_blb()
            results['stages']['blb_intermediate'] = blb_int_results
            
            # Stage 4: Transform games to intermediate
            logger.info("=" * 60)
            logger.info(f"STAGE 4: Transforming {len(game_ids)} game(s)...")
            game_int_results = self._run_intermediate_games(game_ids)
            results['stages']['games_intermediate'] = game_int_results
            
            # Stage 5: Build datamart
            logger.info("=" * 60)
            logger.info("STAGE 5: Building datamart...")
            datamart_results = self._run_datamart(game_ids)
            results['stages']['datamart'] = datamart_results
            
            # Stage 6: Export (optional)
            if export_csv:
                logger.info("=" * 60)
                logger.info("STAGE 6: Exporting to CSV...")
                export_results = self._run_export()
                results['stages']['export'] = export_results
            
            results['games_processed'] = game_ids
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            results['errors'].append(str(e))
        
        # Calculate duration
        end_time = datetime.now()
        results['end_time'] = end_time.isoformat()
        results['duration_seconds'] = (end_time - start_time).total_seconds()
        
        # Summary
        logger.info("=" * 60)
        logger.info(f"Pipeline completed in {results['duration_seconds']:.1f} seconds")
        logger.info(f"Games processed: {len(results['games_processed'])}")
        if results['errors']:
            logger.warning(f"Errors: {len(results['errors'])}")
        
        return results
    
    def process_games(
        self,
        game_ids: Union[int, List[int]],
        force_reload: bool = False
    ) -> Dict:
        """
        Process one or more games (stage + intermediate + datamart).
        
        WHY THIS METHOD:
            Process games without reloading BLB.
            Faster for incremental updates.
        
        Args:
            game_ids: Single game ID or list of game IDs.
            force_reload: Reload even if already processed.
        
        Returns:
            Dictionary with results per game.
        """
        if isinstance(game_ids, int):
            game_ids = [game_ids]
        
        results = {
            'games': {},
            'success': [],
            'failed': []
        }
        
        for game_id in game_ids:
            logger.info(f"\nProcessing game {game_id}...")
            
            try:
                game_result = self._process_single_game(game_id, force_reload)
                results['games'][game_id] = game_result
                results['success'].append(game_id)
                logger.info(f"  ✓ Game {game_id} completed")
                
            except Exception as e:
                logger.error(f"  ✗ Game {game_id} failed: {e}")
                results['games'][game_id] = {'error': str(e)}
                results['failed'].append(game_id)
        
        logger.info(f"\nProcessed {len(results['success'])} games successfully")
        if results['failed']:
            logger.warning(f"Failed: {results['failed']}")
        
        return results
    
    def _process_single_game(self, game_id: int, force_reload: bool) -> Dict:
        """Process a single game through all layers."""
        from src.pipeline.stage.load_game_tracking import load_game_to_stage
        from src.pipeline.intermediate.transform_game import transform_game_to_intermediate
        from src.pipeline.datamart.build_box_score import build_box_score_for_game
        from src.pipeline.datamart.build_events import build_events_for_game
        
        result = {'game_id': game_id}
        
        # Find tracking file
        game_folder = self.games_dir / str(game_id)
        tracking_file = game_folder / f'{game_id}_tracking.xlsx'
        
        if not tracking_file.exists():
            # Try alternate locations
            alt_paths = [
                self.games_dir / f'{game_id}_tracking.xlsx',
                game_folder / 'tracking.xlsx'
            ]
            for alt in alt_paths:
                if alt.exists():
                    tracking_file = alt
                    break
        
        if not tracking_file.exists():
            raise FileNotFoundError(f"Tracking file not found for game {game_id}")
        
        # Stage
        stage_result = load_game_to_stage(game_id, tracking_file, force_reload)
        result['stage'] = stage_result
        
        # Intermediate
        int_result = transform_game_to_intermediate(game_id)
        result['intermediate'] = int_result
        
        # Datamart
        box_rows = build_box_score_for_game(game_id)
        event_rows = build_events_for_game(game_id)
        result['datamart'] = {
            'box_score_rows': box_rows,
            'event_rows': event_rows
        }
        
        return result
    
    def _run_stage_blb(self, force_reload: bool) -> Dict:
        """Run BLB stage loading."""
        from src.pipeline.stage.load_blb_tables import load_blb_to_stage
        
        if not self.blb_file.exists():
            raise FileNotFoundError(f"BLB file not found: {self.blb_file}")
        
        return load_blb_to_stage(self.blb_file, force_reload)
    
    def _run_stage_games(self, game_ids: List[int]) -> Dict:
        """Run game stage loading for multiple games."""
        from src.pipeline.stage.load_game_tracking import load_game_to_stage
        
        results = {}
        
        for game_id in game_ids:
            game_folder = self.games_dir / str(game_id)
            tracking_file = game_folder / f'{game_id}_tracking.xlsx'
            
            if tracking_file.exists():
                try:
                    result = load_game_to_stage(game_id, tracking_file, force_reload=True)
                    results[game_id] = result
                except Exception as e:
                    logger.warning(f"Failed to stage game {game_id}: {e}")
                    results[game_id] = {'error': str(e)}
            else:
                logger.warning(f"Tracking file not found for game {game_id}")
                results[game_id] = {'error': 'File not found'}
        
        return results
    
    def _run_intermediate_blb(self) -> Dict:
        """Run BLB intermediate transformation."""
        from src.pipeline.intermediate.transform_blb import transform_blb_to_intermediate
        return transform_blb_to_intermediate()
    
    def _run_intermediate_games(self, game_ids: List[int]) -> Dict:
        """Run game intermediate transformation for multiple games."""
        from src.pipeline.intermediate.transform_game import transform_game_to_intermediate
        
        results = {}
        
        for game_id in game_ids:
            # Check if stage tables exist
            if not table_exists(f'stg_events_{game_id}'):
                logger.warning(f"Stage tables not found for game {game_id}, skipping")
                continue
            
            try:
                result = transform_game_to_intermediate(game_id)
                results[game_id] = result
            except Exception as e:
                logger.warning(f"Failed to transform game {game_id}: {e}")
                results[game_id] = {'error': str(e)}
        
        return results
    
    def _run_datamart(self, game_ids: List[int]) -> Dict:
        """Build datamart tables."""
        from src.pipeline.datamart.publish_dimensions import (
            publish_blb_to_datamart,
            publish_static_dimensions
        )
        from src.pipeline.datamart.build_box_score import build_box_score_for_game
        from src.pipeline.datamart.build_events import build_events_for_game
        
        results = {
            'dimensions': {},
            'box_scores': {},
            'events': {}
        }
        
        # Publish dimensions
        results['dimensions'] = publish_blb_to_datamart()
        publish_static_dimensions()
        
        # Build box scores and events for each game
        for game_id in game_ids:
            if not table_exists(f'int_events_{game_id}'):
                continue
            
            try:
                results['box_scores'][game_id] = build_box_score_for_game(game_id)
                results['events'][game_id] = build_events_for_game(game_id)
            except Exception as e:
                logger.warning(f"Failed to build datamart for game {game_id}: {e}")
        
        return results
    
    def _run_export(self) -> Dict:
        """Export datamart to CSV."""
        from src.pipeline.datamart.export_to_csv import export_datamart_to_csv
        
        count = export_datamart_to_csv(self.output_dir)
        return {'tables_exported': count, 'output_dir': str(self.output_dir)}
    
    def get_available_games(self) -> List[int]:
        """
        Get list of available game IDs from games directory.
        
        Returns:
            List of game IDs that have tracking files.
        """
        game_ids = []
        
        if not self.games_dir.exists():
            return game_ids
        
        # Check subfolders
        for folder in self.games_dir.iterdir():
            if folder.is_dir() and folder.name.isdigit():
                tracking_file = folder / f'{folder.name}_tracking.xlsx'
                if tracking_file.exists():
                    game_ids.append(int(folder.name))
        
        # Check files directly in games dir
        for f in self.games_dir.glob('*_tracking.xlsx'):
            try:
                game_id = int(f.stem.replace('_tracking', ''))
                if game_id not in game_ids:
                    game_ids.append(game_id)
            except ValueError:
                continue
        
        return sorted(game_ids)
    
    def get_processed_games(self) -> List[int]:
        """
        Get list of games that have been processed to datamart.
        
        Returns:
            List of game IDs in fact_box_score.
        """
        from src.database.table_operations import read_query
        
        if not table_exists('fact_box_score'):
            return []
        
        df = read_query("SELECT DISTINCT game_id FROM fact_box_score")
        return sorted(df['game_id'].tolist())
    
    def get_unprocessed_games(self) -> List[int]:
        """
        Get games that are available but not yet processed.
        
        Returns:
            List of unprocessed game IDs.
        """
        available = set(self.get_available_games())
        processed = set(self.get_processed_games())
        return sorted(available - processed)
    
    def get_status(self) -> Dict:
        """
        Get current pipeline status.
        
        Returns:
            Dictionary with table counts by layer.
        """
        status = {}
        
        for layer in ['stage', 'intermediate', 'datamart']:
            tables = get_tables_by_layer(layer)
            total_rows = sum(get_row_count(t) for t in tables)
            status[layer] = {
                'tables': len(tables),
                'rows': total_rows,
                'table_names': tables
            }
        
        status['available_games'] = self.get_available_games()
        status['processed_games'] = self.get_processed_games()
        status['unprocessed_games'] = self.get_unprocessed_games()
        
        return status
