"""
=============================================================================
GAME MANAGEMENT - OVERWRITE, DELETE, AND REPROCESS WITH SAFEGUARDS
=============================================================================
File: src/pipeline/game_management.py

PURPOSE:
    Provide safe operations for managing game data with proper safeguards
    to prevent accidental data loss.

SAFEGUARDS:
    - Shows current data before overwrite
    - Requires explicit confirmation
    - Double confirmation for multiple games
    - Backup option before destructive operations
    - Detailed logging of all operations

=============================================================================
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

from src.database.connection import execute_sql
from src.database.table_operations import (
    table_exists,
    get_row_count,
    read_query,
    drop_table
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GameManagementError(Exception):
    """Exception for game management operations."""
    pass


def get_game_data_summary(game_id: int) -> Dict:
    """
    Get summary of all data for a specific game across all layers.
    
    WHY THIS FUNCTION:
        Before overwriting, show what exists.
        Help users understand impact of operation.
    
    Args:
        game_id: Game identifier.
    
    Returns:
        Dictionary with data counts per layer/table.
    """
    summary = {
        'game_id': game_id,
        'exists_in_any_layer': False,
        'stage': {},
        'intermediate': {},
        'datamart': {},
        'total_rows': 0
    }
    
    # Stage layer tables
    stage_tables = [
        f'stg_events_{game_id}',
        f'stg_shifts_{game_id}',
        f'stg_xy_events_{game_id}',
        f'stg_xy_shots_{game_id}'
    ]
    
    for table in stage_tables:
        if table_exists(table):
            count = get_row_count(table)
            summary['stage'][table] = count
            summary['total_rows'] += count
            summary['exists_in_any_layer'] = True
    
    # Intermediate layer tables
    int_tables = [
        f'int_events_{game_id}',
        f'int_event_players_{game_id}',
        f'int_shifts_{game_id}',
        f'int_game_players_{game_id}'
    ]
    
    for table in int_tables:
        if table_exists(table):
            count = get_row_count(table)
            summary['intermediate'][table] = count
            summary['total_rows'] += count
            summary['exists_in_any_layer'] = True
    
    # Datamart layer (rows in shared tables)
    if table_exists('fact_box_score'):
        df = read_query(f"SELECT COUNT(*) as cnt FROM fact_box_score WHERE game_id = {game_id}")
        count = df['cnt'].iloc[0]
        if count > 0:
            summary['datamart']['fact_box_score'] = count
            summary['total_rows'] += count
            summary['exists_in_any_layer'] = True
    
    if table_exists('fact_events'):
        df = read_query(f"SELECT COUNT(*) as cnt FROM fact_events WHERE game_id = {game_id}")
        count = df['cnt'].iloc[0]
        if count > 0:
            summary['datamart']['fact_events'] = count
            summary['total_rows'] += count
            summary['exists_in_any_layer'] = True
    
    return summary


def format_game_summary(summary: Dict) -> str:
    """
    Format game data summary for display.
    
    Args:
        summary: Dictionary from get_game_data_summary().
    
    Returns:
        Formatted string for display.
    """
    lines = []
    lines.append(f"\nGame {summary['game_id']} Data Summary:")
    lines.append("-" * 40)
    
    if not summary['exists_in_any_layer']:
        lines.append("  No data found for this game.")
        return "\n".join(lines)
    
    if summary['stage']:
        lines.append("  STAGE LAYER:")
        for table, count in summary['stage'].items():
            lines.append(f"    {table}: {count:,} rows")
    
    if summary['intermediate']:
        lines.append("  INTERMEDIATE LAYER:")
        for table, count in summary['intermediate'].items():
            lines.append(f"    {table}: {count:,} rows")
    
    if summary['datamart']:
        lines.append("  DATAMART LAYER:")
        for table, count in summary['datamart'].items():
            lines.append(f"    {table}: {count:,} rows")
    
    lines.append("-" * 40)
    lines.append(f"  TOTAL: {summary['total_rows']:,} rows")
    
    return "\n".join(lines)


def remove_game_all_layers(
    game_id: int,
    confirm: bool = False,
    dry_run: bool = False
) -> Dict:
    """
    Remove all data for a game from all layers.
    
    SAFEGUARDS:
        - Requires confirm=True to execute
        - dry_run=True shows what would be deleted without doing it
        - Logs all operations
    
    Args:
        game_id: Game to remove.
        confirm: Must be True to actually delete.
        dry_run: If True, only show what would be deleted.
    
    Returns:
        Dictionary with removal results.
    
    Raises:
        GameManagementError: If confirm is False.
    """
    summary = get_game_data_summary(game_id)
    
    if not summary['exists_in_any_layer']:
        return {
            'game_id': game_id,
            'status': 'no_data',
            'message': f'No data found for game {game_id}'
        }
    
    if dry_run:
        return {
            'game_id': game_id,
            'status': 'dry_run',
            'would_remove': summary,
            'message': f'Would remove {summary["total_rows"]:,} rows'
        }
    
    if not confirm:
        raise GameManagementError(
            f"Confirmation required to remove game {game_id}. "
            f"This would delete {summary['total_rows']:,} rows. "
            f"Set confirm=True to proceed."
        )
    
    logger.warning(f"REMOVING ALL DATA for game {game_id} ({summary['total_rows']:,} rows)")
    
    result = {
        'game_id': game_id,
        'status': 'removed',
        'removed': {},
        'timestamp': datetime.now().isoformat()
    }
    
    # Remove stage tables
    for table in summary['stage'].keys():
        if drop_table(table):
            result['removed'][table] = summary['stage'][table]
            logger.info(f"  Dropped {table}")
    
    # Remove intermediate tables
    for table in summary['intermediate'].keys():
        if drop_table(table):
            result['removed'][table] = summary['intermediate'][table]
            logger.info(f"  Dropped {table}")
    
    # Remove from datamart tables (DELETE rows, not DROP table)
    if 'fact_box_score' in summary['datamart']:
        execute_sql("DELETE FROM fact_box_score WHERE game_id = :gid", {'gid': game_id})
        result['removed']['fact_box_score'] = summary['datamart']['fact_box_score']
        logger.info(f"  Deleted {summary['datamart']['fact_box_score']} rows from fact_box_score")
    
    if 'fact_events' in summary['datamart']:
        execute_sql("DELETE FROM fact_events WHERE game_id = :gid", {'gid': game_id})
        result['removed']['fact_events'] = summary['datamart']['fact_events']
        logger.info(f"  Deleted {summary['datamart']['fact_events']} rows from fact_events")
    
    # Record in metadata
    _record_removal_metadata(game_id, result)
    
    result['total_removed'] = sum(result['removed'].values())
    logger.warning(f"COMPLETED: Removed {result['total_removed']:,} total rows for game {game_id}")
    
    return result


def remove_games_batch(
    game_ids: List[int],
    confirm: bool = False,
    double_confirm: bool = False,
    dry_run: bool = False
) -> Dict:
    """
    Remove multiple games with extra safeguards.
    
    SAFEGUARDS:
        - Requires confirm=True
        - For 5+ games, requires double_confirm=True
        - Shows summary of all games before operation
        - dry_run option to preview
    
    Args:
        game_ids: List of game IDs to remove.
        confirm: Must be True to proceed.
        double_confirm: Required for 5+ games.
        dry_run: Preview without executing.
    
    Returns:
        Dictionary with batch results.
    """
    if len(game_ids) == 0:
        return {'status': 'no_games', 'message': 'No game IDs provided'}
    
    # Get summaries for all games
    summaries = {}
    total_rows = 0
    
    for game_id in game_ids:
        summary = get_game_data_summary(game_id)
        summaries[game_id] = summary
        total_rows += summary['total_rows']
    
    if dry_run:
        return {
            'status': 'dry_run',
            'game_count': len(game_ids),
            'total_rows': total_rows,
            'games': summaries,
            'message': f'Would remove {total_rows:,} rows across {len(game_ids)} games'
        }
    
    if not confirm:
        raise GameManagementError(
            f"Confirmation required to remove {len(game_ids)} games. "
            f"This would delete {total_rows:,} total rows. "
            f"Set confirm=True to proceed."
        )
    
    if len(game_ids) >= 5 and not double_confirm:
        raise GameManagementError(
            f"DOUBLE CONFIRMATION required for batch removal of {len(game_ids)} games. "
            f"This would delete {total_rows:,} total rows. "
            f"Set both confirm=True AND double_confirm=True to proceed."
        )
    
    logger.warning(f"BATCH REMOVAL: Starting removal of {len(game_ids)} games ({total_rows:,} rows)")
    
    results = {
        'status': 'completed',
        'games_removed': [],
        'games_failed': [],
        'total_removed': 0,
        'timestamp': datetime.now().isoformat()
    }
    
    for game_id in game_ids:
        try:
            result = remove_game_all_layers(game_id, confirm=True)
            results['games_removed'].append(game_id)
            results['total_removed'] += result.get('total_removed', 0)
        except Exception as e:
            logger.error(f"Failed to remove game {game_id}: {e}")
            results['games_failed'].append({'game_id': game_id, 'error': str(e)})
    
    logger.warning(
        f"BATCH REMOVAL COMPLETED: "
        f"{len(results['games_removed'])} removed, "
        f"{len(results['games_failed'])} failed, "
        f"{results['total_removed']:,} rows deleted"
    )
    
    return results


def overwrite_game(
    game_id: int,
    tracking_file: Path,
    confirm: bool = False,
    backup: bool = True
) -> Dict:
    """
    Overwrite an existing game with new data.
    
    SAFEGUARDS:
        - Shows existing data before overwrite
        - Requires confirm=True
        - Optional backup before overwrite
        - Full audit trail
    
    Args:
        game_id: Game to overwrite.
        tracking_file: New tracking file to load.
        confirm: Must be True to proceed.
        backup: If True, backup existing data first.
    
    Returns:
        Dictionary with overwrite results.
    """
    from src.pipeline.stage.load_game_tracking import load_game_to_stage
    from src.pipeline.intermediate.transform_game import transform_game_to_intermediate
    from src.pipeline.datamart.build_box_score import build_box_score_for_game
    from src.pipeline.datamart.build_events import build_events_for_game
    
    # Get current state
    summary = get_game_data_summary(game_id)
    
    if not confirm:
        raise GameManagementError(
            f"Confirmation required to overwrite game {game_id}. "
            f"Existing data: {summary['total_rows']:,} rows. "
            f"Set confirm=True to proceed."
        )
    
    if not tracking_file.exists():
        raise FileNotFoundError(f"Tracking file not found: {tracking_file}")
    
    result = {
        'game_id': game_id,
        'status': 'overwritten',
        'previous_data': summary,
        'backup_created': False,
        'new_data': {},
        'timestamp': datetime.now().isoformat()
    }
    
    # Backup if requested and data exists
    if backup and summary['exists_in_any_layer']:
        backup_result = _backup_game_data(game_id)
        result['backup_created'] = True
        result['backup_location'] = backup_result.get('backup_file')
        logger.info(f"Created backup for game {game_id}")
    
    # Remove existing data
    if summary['exists_in_any_layer']:
        logger.info(f"Removing existing data for game {game_id}")
        remove_game_all_layers(game_id, confirm=True)
    
    # Load new data
    logger.info(f"Loading new data for game {game_id} from {tracking_file}")
    
    # Stage
    stage_result = load_game_to_stage(game_id, tracking_file, force_reload=True)
    result['new_data']['stage'] = stage_result
    
    # Intermediate
    int_result = transform_game_to_intermediate(game_id)
    result['new_data']['intermediate'] = int_result
    
    # Datamart
    box_rows = build_box_score_for_game(game_id)
    event_rows = build_events_for_game(game_id)
    result['new_data']['datamart'] = {
        'fact_box_score': box_rows,
        'fact_events': event_rows
    }
    
    # Record metadata
    _record_overwrite_metadata(game_id, result)
    
    logger.info(f"Game {game_id} overwritten successfully")
    return result


def _backup_game_data(game_id: int) -> Dict:
    """
    Create a backup of game data before overwrite.
    
    Args:
        game_id: Game to backup.
    
    Returns:
        Dictionary with backup info.
    """
    from src.database.table_operations import read_query
    
    backup_dir = Path(__file__).parent.parent.parent.parent / 'backups' / 'games'
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'game_{game_id}_{timestamp}.json'
    
    backup_data = {
        'game_id': game_id,
        'backup_timestamp': datetime.now().isoformat(),
        'tables': {}
    }
    
    # Backup datamart data (most important)
    if table_exists('fact_box_score'):
        df = read_query(f"SELECT * FROM fact_box_score WHERE game_id = {game_id}")
        if len(df) > 0:
            backup_data['tables']['fact_box_score'] = df.to_dict(orient='records')
    
    if table_exists('fact_events'):
        df = read_query(f"SELECT * FROM fact_events WHERE game_id = {game_id}")
        if len(df) > 0:
            backup_data['tables']['fact_events'] = df.to_dict(orient='records')
    
    # Write backup file
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    logger.info(f"Backup created: {backup_file}")
    
    return {
        'backup_file': str(backup_file),
        'tables_backed_up': list(backup_data['tables'].keys()),
        'rows_backed_up': sum(len(v) for v in backup_data['tables'].values())
    }


def _record_removal_metadata(game_id: int, result: Dict) -> None:
    """Record game removal in metadata table."""
    execute_sql("""
        CREATE TABLE IF NOT EXISTS _game_removal_log (
            removal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            removal_timestamp TEXT NOT NULL,
            rows_removed INTEGER,
            tables_removed TEXT
        )
    """)
    
    execute_sql("""
        INSERT INTO _game_removal_log 
        (game_id, removal_timestamp, rows_removed, tables_removed)
        VALUES (:game_id, :timestamp, :rows, :tables)
    """, {
        'game_id': game_id,
        'timestamp': result['timestamp'],
        'rows': result.get('total_removed', 0),
        'tables': json.dumps(list(result.get('removed', {}).keys()))
    })


def _record_overwrite_metadata(game_id: int, result: Dict) -> None:
    """Record game overwrite in metadata table."""
    execute_sql("""
        CREATE TABLE IF NOT EXISTS _game_overwrite_log (
            overwrite_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            overwrite_timestamp TEXT NOT NULL,
            previous_rows INTEGER,
            new_rows INTEGER,
            backup_created INTEGER
        )
    """)
    
    previous_rows = result.get('previous_data', {}).get('total_rows', 0)
    new_rows = sum(
        sum(v.values()) if isinstance(v, dict) else v 
        for v in result.get('new_data', {}).values()
    )
    
    execute_sql("""
        INSERT INTO _game_overwrite_log 
        (game_id, overwrite_timestamp, previous_rows, new_rows, backup_created)
        VALUES (:game_id, :timestamp, :prev, :new, :backup)
    """, {
        'game_id': game_id,
        'timestamp': result['timestamp'],
        'prev': previous_rows,
        'new': new_rows,
        'backup': 1 if result.get('backup_created') else 0
    })


def list_game_backups(game_id: int = None) -> List[Dict]:
    """
    List available game backups.
    
    Args:
        game_id: Optional filter by game ID.
    
    Returns:
        List of backup info dictionaries.
    """
    backup_dir = Path(__file__).parent.parent.parent.parent / 'backups' / 'games'
    
    if not backup_dir.exists():
        return []
    
    backups = []
    
    pattern = f'game_{game_id}_*.json' if game_id else 'game_*.json'
    
    for backup_file in backup_dir.glob(pattern):
        try:
            with open(backup_file, 'r') as f:
                data = json.load(f)
            
            backups.append({
                'file': str(backup_file),
                'game_id': data.get('game_id'),
                'timestamp': data.get('backup_timestamp'),
                'tables': list(data.get('tables', {}).keys()),
                'rows': sum(len(v) for v in data.get('tables', {}).values())
            })
        except Exception as e:
            logger.warning(f"Could not read backup file {backup_file}: {e}")
    
    return sorted(backups, key=lambda x: x['timestamp'], reverse=True)


def restore_game_from_backup(backup_file: Path, confirm: bool = False) -> Dict:
    """
    Restore game data from a backup file.
    
    SAFEGUARDS:
        - Requires confirm=True
        - Shows what will be restored
    
    Args:
        backup_file: Path to backup JSON file.
        confirm: Must be True to proceed.
    
    Returns:
        Dictionary with restore results.
    """
    from src.database.table_operations import load_dataframe_to_table
    import pandas as pd
    
    if not backup_file.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_file}")
    
    with open(backup_file, 'r') as f:
        backup_data = json.load(f)
    
    game_id = backup_data.get('game_id')
    
    if not confirm:
        raise GameManagementError(
            f"Confirmation required to restore game {game_id} from backup. "
            f"Backup contains {sum(len(v) for v in backup_data.get('tables', {}).values())} rows. "
            f"Set confirm=True to proceed."
        )
    
    result = {
        'game_id': game_id,
        'status': 'restored',
        'backup_file': str(backup_file),
        'restored_tables': {},
        'timestamp': datetime.now().isoformat()
    }
    
    for table_name, records in backup_data.get('tables', {}).items():
        if records:
            df = pd.DataFrame(records)
            
            # For fact tables, we need to append (not replace entire table)
            if table_name.startswith('fact_'):
                # First remove existing rows for this game
                execute_sql(f"DELETE FROM {table_name} WHERE game_id = :gid", {'gid': game_id})
            
            # Then insert the backup data
            row_count = load_dataframe_to_table(df, table_name, if_exists='append')
            result['restored_tables'][table_name] = row_count
            logger.info(f"Restored {row_count} rows to {table_name}")
    
    logger.info(f"Game {game_id} restored from backup")
    return result
