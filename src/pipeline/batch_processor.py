"""
=============================================================================
BATCH GAME PROCESSOR
=============================================================================
File: src/pipeline/batch_processor.py

PURPOSE:
    Process multiple games through the full ETL pipeline including:
    - Stage: events, shifts, xy data, shots, video times
    - Intermediate: transformations with standardized keys
    - Datamart: fact tables with FK relationships
    - Quality checks and logging

=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import traceback

from src.database.connection import execute_sql
from src.database.table_operations import (
    load_dataframe_to_table,
    table_exists,
    get_row_count,
    read_query,
    drop_table
)
from src.pipeline.stage.load_blb_tables import load_blb_to_stage
from src.pipeline.stage.load_game_tracking import load_game_to_stage
from src.pipeline.stage.load_xy_data import (
    load_xy_data_for_game,
    transform_xy_to_intermediate,
    publish_xy_to_datamart
)
from src.pipeline.stage.load_video_times import process_video_for_game
from src.pipeline.intermediate.transform_blb import transform_blb_to_intermediate
from src.pipeline.intermediate.transform_game import transform_game_to_intermediate
from src.pipeline.datamart.publish_dimensions import (
    publish_blb_to_datamart,
    publish_static_dimensions
)
from src.pipeline.datamart.build_box_score import build_box_score_for_game
from src.pipeline.datamart.build_events import build_events_for_game
from src.pipeline.datamart.build_enhanced_data import publish_rink_dimensions
from src.pipeline.data_quality import run_quality_checks_for_game

from src.utils.logger import get_logger

logger = get_logger(__name__)


def discover_games(games_dir: Path) -> List[int]:
    """
    Discover all games in the games directory.
    
    Args:
        games_dir: Path to games directory
    
    Returns:
        List of game IDs found
    """
    game_ids = []
    
    for game_folder in games_dir.iterdir():
        if game_folder.is_dir() and game_folder.name.isdigit():
            game_id = int(game_folder.name)
            # Check for tracking file
            tracking_file = game_folder / f'{game_id}_tracking.xlsx'
            if not tracking_file.exists():
                # Try alternate name
                tracking_file = game_folder / '_tracking.xlsx'
            
            if tracking_file.exists():
                game_ids.append(game_id)
    
    return sorted(game_ids)


def process_single_game(game_id: int, game_dir: Path, force: bool = False) -> Dict:
    """
    Process a single game through the full pipeline.
    
    Args:
        game_id: Game identifier
        game_dir: Path to game folder
        force: Force reprocessing even if exists
    
    Returns:
        Dictionary with processing results
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"PROCESSING GAME {game_id}")
    logger.info(f"{'='*60}")
    
    result = {
        'game_id': game_id,
        'start_time': datetime.now().isoformat(),
        'status': 'started',
        'errors': [],
        'stages': {}
    }
    
    # Find tracking file
    tracking_file = game_dir / f'{game_id}_tracking.xlsx'
    if not tracking_file.exists():
        tracking_file = game_dir / '_tracking.xlsx'
    
    if not tracking_file.exists():
        result['status'] = 'error'
        result['errors'].append(f"No tracking file found in {game_dir}")
        return result
    
    try:
        # 1. Run quality checks first
        logger.info("Step 1: Running quality checks...")
        quality_result = run_quality_checks_for_game(game_id, tracking_file)
        result['stages']['quality_check'] = quality_result.get('tracking_status')
        result['quality_issues'] = len(quality_result.get('anomalies', []))
        
        # 2. Stage: Load tracking data
        logger.info("Step 2: Loading to stage...")
        stage_result = load_game_to_stage(game_id, tracking_file, force_reload=force)
        result['stages']['stage'] = stage_result
        
        # 3. Intermediate: Transform
        logger.info("Step 3: Transforming to intermediate...")
        int_result = transform_game_to_intermediate(game_id)
        result['stages']['intermediate'] = int_result
        
        # 4. Datamart: Build box score
        logger.info("Step 4: Building box score...")
        box_rows = build_box_score_for_game(game_id)
        result['stages']['box_score'] = box_rows
        
        # 5. Datamart: Build events
        logger.info("Step 5: Building events...")
        event_rows = build_events_for_game(game_id)
        result['stages']['events'] = event_rows
        
        # 6. Load XY data if present
        logger.info("Step 6: Loading XY data...")
        xy_result = load_xy_data_for_game(game_id, game_dir)
        result['stages']['xy_load'] = xy_result
        
        if xy_result.get('xy_events', 0) > 0 or xy_result.get('xy_shots', 0) > 0:
            logger.info("Step 6b: Transforming XY to intermediate...")
            xy_int = transform_xy_to_intermediate(game_id)
            result['stages']['xy_intermediate'] = xy_int
            
            logger.info("Step 6c: Publishing XY to datamart...")
            xy_dm = publish_xy_to_datamart(game_id)
            result['stages']['xy_datamart'] = xy_dm
        
        # 7. Process video times
        logger.info("Step 7: Processing video times...")
        video_result = process_video_for_game(game_id, game_dir)
        result['stages']['video'] = video_result
        
        result['status'] = 'completed'
        result['end_time'] = datetime.now().isoformat()
        
        logger.info(f"✓ Game {game_id} processed successfully")
        
    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(str(e))
        result['traceback'] = traceback.format_exc()
        logger.error(f"Error processing game {game_id}: {e}")
    
    return result


def process_all_games(games_dir: Path, force: bool = False) -> Dict:
    """
    Process all games found in the games directory.
    
    Args:
        games_dir: Path to games directory
        force: Force reprocessing
    
    Returns:
        Dictionary with all results
    """
    logger.info("=" * 70)
    logger.info("BATCH GAME PROCESSING")
    logger.info("=" * 70)
    
    results = {
        'start_time': datetime.now().isoformat(),
        'games': {},
        'summary': {
            'total': 0,
            'completed': 0,
            'errors': 0,
            'skipped': 0
        }
    }
    
    # Discover games
    game_ids = discover_games(games_dir)
    results['summary']['total'] = len(game_ids)
    logger.info(f"Found {len(game_ids)} games to process: {game_ids}")
    
    # Process each game
    for game_id in game_ids:
        game_dir = games_dir / str(game_id)
        try:
            game_result = process_single_game(game_id, game_dir, force=force)
            results['games'][game_id] = game_result
            
            if game_result['status'] == 'completed':
                results['summary']['completed'] += 1
            else:
                results['summary']['errors'] += 1
                
        except Exception as e:
            results['games'][game_id] = {
                'status': 'error',
                'errors': [str(e)]
            }
            results['summary']['errors'] += 1
    
    results['end_time'] = datetime.now().isoformat()
    
    # Log summary
    logger.info("\n" + "=" * 70)
    logger.info("BATCH PROCESSING COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Total games: {results['summary']['total']}")
    logger.info(f"Completed: {results['summary']['completed']}")
    logger.info(f"Errors: {results['summary']['errors']}")
    
    return results


def initialize_pipeline(blb_file: Path, force_blb: bool = False) -> Dict:
    """
    Initialize the pipeline by loading BLB tables and dimensions.
    
    Args:
        blb_file: Path to BLB_Tables.xlsx
        force_blb: Force reload of BLB tables
    
    Returns:
        Dictionary with initialization results
    """
    logger.info("=" * 70)
    logger.info("INITIALIZING PIPELINE")
    logger.info("=" * 70)
    
    results = {}
    
    # Load BLB to stage
    logger.info("Loading BLB tables to stage...")
    stage_results = load_blb_to_stage(blb_file, force_reload=force_blb)
    results['blb_stage'] = stage_results
    
    # Transform to intermediate
    logger.info("Transforming BLB to intermediate...")
    int_results = transform_blb_to_intermediate()
    results['blb_intermediate'] = int_results
    
    # Publish dimensions
    logger.info("Publishing dimensions to datamart...")
    dm_results = publish_blb_to_datamart()
    results['blb_datamart'] = dm_results
    
    # Static dimensions
    logger.info("Creating static dimensions...")
    publish_static_dimensions()
    results['static_dimensions'] = 'created'
    
    # Rink dimensions
    logger.info("Publishing rink dimensions...")
    rink_results = publish_rink_dimensions()
    results['rink_dimensions'] = rink_results
    
    logger.info("✓ Pipeline initialized")
    
    return results


def run_full_batch_pipeline(
    data_dir: Path,
    force_blb: bool = False,
    force_games: bool = False
) -> Dict:
    """
    Run the complete batch pipeline.
    
    Args:
        data_dir: Path to data/raw directory
        force_blb: Force reload BLB tables
        force_games: Force reprocess all games
    
    Returns:
        Complete results dictionary
    """
    results = {
        'pipeline_start': datetime.now().isoformat()
    }
    
    # Initialize
    blb_file = data_dir / 'BLB_Tables.xlsx'
    if blb_file.exists():
        results['initialization'] = initialize_pipeline(blb_file, force_blb)
    else:
        logger.warning(f"BLB file not found: {blb_file}")
    
    # Process games
    games_dir = data_dir / 'games'
    if games_dir.exists():
        results['games'] = process_all_games(games_dir, force_games)
    else:
        logger.warning(f"Games directory not found: {games_dir}")
    
    results['pipeline_end'] = datetime.now().isoformat()
    
    return results


if __name__ == '__main__':
    # Run batch processing
    data_dir = Path('data/raw')
    results = run_full_batch_pipeline(data_dir, force_blb=True, force_games=True)
    
    # Print summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    if 'games' in results and 'summary' in results['games']:
        summary = results['games']['summary']
        print(f"Games processed: {summary['completed']}/{summary['total']}")
        print(f"Errors: {summary['errors']}")
