"""
Parallel Processing Utilities

Utilities for parallelizing game loading and processing.
Designed to work with the ETL pipeline while maintaining data integrity.

Version: 29.7
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Callable, Any
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import multiprocessing
import logging

log = logging.getLogger('ParallelProcessing')

# Determine optimal worker count
CPU_COUNT = multiprocessing.cpu_count()
OPTIMAL_WORKERS = min(CPU_COUNT, 8)  # Cap at 8 to avoid overhead


def load_single_game(
    game_id: str,
    games_dir: Path,
    player_lookup: Dict,
    schedule_df: pd.DataFrame
) -> Tuple[str, Dict[str, pd.DataFrame], Optional[str]]:
    """
    Load a single game's tracking data.
    
    This function is designed to be called in parallel.
    It loads one game independently and returns its data.
    
    Args:
        game_id: Game ID to load
        games_dir: Directory containing game folders
        player_lookup: Player lookup dictionary (read-only)
        schedule_df: Schedule DataFrame for venue correction (read-only)
        
    Returns:
        Tuple of (game_id, {'events': df, 'shifts': df}, error_message)
    """
    # Import functions here to avoid pickling issues
    from src.core.base_etl import drop_underscore_columns, correct_venue_from_schedule
    
    game_dir = games_dir / game_id
    result = {'events': None, 'shifts': None}
    error = None
    
    if not game_dir.exists():
        error = f"Game directory not found: {game_dir}"
        return game_id, result, error
    
    # Find tracking file
    tracking_files = list(game_dir.glob("*_tracking.xlsx"))
    tracking_files = [f for f in tracking_files if 'bkup' not in str(f).lower()]
    
    if not tracking_files:
        error = f"No tracking file for game {game_id}"
        return game_id, result, error
    
    xlsx_path = tracking_files[0]
    
    try:
        xl = pd.ExcelFile(xlsx_path)
        
        # Load events
        if 'events' in xl.sheet_names:
            df = pd.read_excel(xlsx_path, sheet_name='events', dtype=str)
            df['game_id'] = game_id
            
            # Drop underscore columns
            df, dropped = drop_underscore_columns(df)
            
            # Filter valid rows
            index_col = 'tracking_event_index' if 'tracking_event_index' in df.columns else 'event_index'
            if index_col in df.columns:
                df = df[df[index_col].apply(
                    lambda x: pd.notna(x) and str(x).replace('.', '').replace('-', '').isdigit()
                )]
            
            # Venue correction (create a dummy logger for parallel execution)
            class DummyLogger:
                def info(self, msg): pass
                def warning(self, msg): pass
                def error(self, msg): pass
            dummy_log = DummyLogger()
            df = correct_venue_from_schedule(df, game_id, schedule_df, dummy_log)
            
            result['events'] = df
        
        # Load shifts
        if 'shifts' in xl.sheet_names:
            df = pd.read_excel(xlsx_path, sheet_name='shifts', dtype=str)
            df['game_id'] = game_id
            
            df, dropped = drop_underscore_columns(df)
            
            # Filter valid rows
            if 'shift_index' in df.columns:
                df = df[df['shift_index'].apply(
                    lambda x: pd.notna(x) and str(x).replace('.', '').isdigit()
                )]
            
            result['shifts'] = df
            
    except Exception as e:
        error = f"Error loading game {game_id}: {str(e)}"
        return game_id, result, error
    
    return game_id, result, None


def load_games_parallel(
    game_ids: List[str],
    games_dir: Path,
    player_lookup: Dict,
    schedule_df: pd.DataFrame,
    max_workers: Optional[int] = None,
    use_threading: bool = True
) -> Tuple[List[pd.DataFrame], List[pd.DataFrame], List[str]]:
    """
    Load multiple games in parallel.
    
    Args:
        game_ids: List of game IDs to load
        games_dir: Directory containing game folders
        player_lookup: Player lookup dictionary
        schedule_df: Schedule DataFrame for venue correction
        drop_underscore_columns: Function to drop underscore columns
        correct_venue_from_schedule: Function to correct venue
        max_workers: Maximum number of workers (default: OPTIMAL_WORKERS)
        use_threading: Use threading instead of multiprocessing (for I/O-bound tasks)
        
    Returns:
        Tuple of (events_list, shifts_list, errors_list)
    """
    if max_workers is None:
        max_workers = OPTIMAL_WORKERS
    
    if len(game_ids) == 0:
        return [], [], []
    
    # For small numbers of games, sequential may be faster due to overhead
    if len(game_ids) <= 2:
        log.info(f"  Only {len(game_ids)} games, using sequential loading")
        use_threading = False
        max_workers = 1
    
    all_events = []
    all_shifts = []
    errors = []
    
    executor_class = ThreadPoolExecutor if use_threading else ProcessPoolExecutor
    
    log.info(f"  Loading {len(game_ids)} games in parallel ({max_workers} workers, {'threading' if use_threading else 'multiprocessing'})...")
    
    with executor_class(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(
                load_single_game,
                game_id,
                games_dir,
                player_lookup,
                schedule_df
            ): game_id
            for game_id in game_ids
        }
        
        # Collect results as they complete
        completed = 0
        for future in as_completed(futures):
            game_id = futures[future]
            completed += 1
            
            try:
                result_game_id, result_data, error = future.result()
                
                if error:
                    errors.append(f"Game {result_game_id}: {error}")
                    log.warning(f"  [{completed}/{len(game_ids)}] Game {result_game_id}: {error}")
                else:
                    if result_data['events'] is not None:
                        all_events.append(result_data['events'])
                    if result_data['shifts'] is not None:
                        all_shifts.append(result_data['shifts'])
                    log.info(f"  [{completed}/{len(game_ids)}] Game {result_game_id}: loaded")
                    
            except Exception as e:
                errors.append(f"Game {game_id}: Exception: {str(e)}")
                log.error(f"  [{completed}/{len(game_ids)}] Game {game_id}: Exception: {str(e)}")
    
    log.info(f"  Parallel loading complete: {len(all_events)} event sets, {len(all_shifts)} shift sets, {len(errors)} errors")
    
    return all_events, all_shifts, errors


def process_games_parallel(
    game_ids: List[str],
    process_func: Callable[[str], Any],
    max_workers: Optional[int] = None,
    use_threading: bool = False
) -> List[Any]:
    """
    Process multiple games in parallel using a custom processing function.
    
    Args:
        game_ids: List of game IDs to process
        process_func: Function that takes game_id and returns result
        max_workers: Maximum number of workers
        use_threading: Use threading instead of multiprocessing
        
    Returns:
        List of results from process_func
    """
    if max_workers is None:
        max_workers = OPTIMAL_WORKERS
    
    if len(game_ids) == 0:
        return []
    
    if len(game_ids) <= 2:
        # Sequential for small batches
        return [process_func(game_id) for game_id in game_ids]
    
    executor_class = ThreadPoolExecutor if use_threading else ProcessPoolExecutor
    
    results = []
    with executor_class(max_workers=max_workers) as executor:
        futures = {executor.submit(process_func, game_id): game_id for game_id in game_ids}
        
        for future in as_completed(futures):
            game_id = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                log.error(f"Error processing game {game_id}: {e}")
                results.append(None)
    
    return results
