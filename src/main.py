#!/usr/bin/env python3
"""
=============================================================================
HOCKEY ANALYTICS ETL PIPELINE - MAIN ENTRY POINT
=============================================================================
File: main.py

PURPOSE:
    Interactive CLI for running the hockey analytics ETL pipeline.
    Provides menu-driven interface for all pipeline operations.

USAGE:
    python main.py                    # Interactive menu
    python main.py --game 18969       # Process single game
    python main.py --games 18969,18970,18971  # Process multiple games
    python main.py --reload-blb       # Force reload BLB tables
    python main.py --status           # Show pipeline status
    python main.py --export           # Export datamart to CSV
    python main.py --process-all      # Process all unprocessed games

=============================================================================
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.orchestrator import PipelineOrchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)


def parse_game_ids(game_str: str) -> List[int]:
    """
    Parse game IDs from string input.
    
    Accepts formats:
        - "18969"           -> [18969]
        - "18969,18970"     -> [18969, 18970]
        - "18969 18970"     -> [18969, 18970]
        - "18969-18972"     -> [18969, 18970, 18971, 18972]
    
    Args:
        game_str: String containing game ID(s).
    
    Returns:
        List of game IDs.
    """
    game_ids = []
    
    # Replace common separators with comma
    game_str = game_str.replace(' ', ',').replace(';', ',')
    
    for part in game_str.split(','):
        part = part.strip()
        if not part:
            continue
        
        # Check for range (e.g., "18969-18972")
        if '-' in part and part.count('-') == 1:
            try:
                start, end = part.split('-')
                start_id = int(start.strip())
                end_id = int(end.strip())
                game_ids.extend(range(start_id, end_id + 1))
            except ValueError:
                # Not a valid range, try as single ID
                try:
                    game_ids.append(int(part))
                except ValueError:
                    logger.warning(f"Invalid game ID: {part}")
        else:
            try:
                game_ids.append(int(part))
            except ValueError:
                logger.warning(f"Invalid game ID: {part}")
    
    return sorted(set(game_ids))  # Remove duplicates and sort


def show_menu():
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("HOCKEY ANALYTICS ETL PIPELINE")
    print("=" * 60)
    print("\n  1. Run full pipeline (BLB + all available games)")
    print("  2. Process specific game(s)")
    print("  3. Process all unprocessed games")
    print("  4. Show pipeline status")
    print("  5. Reload BLB tables")
    print("  6. Export datamart to CSV")
    print("  7. List available games")
    print("  8. Clear layer (stage/intermediate/datamart)")
    print("  9. Overwrite/Reprocess existing game(s)")
    print("  10. Exit")
    print("\n" + "-" * 60)


def get_user_choice() -> str:
    """Get menu choice from user."""
    return input("Enter choice (1-10): ").strip()


def handle_process_games(orchestrator: PipelineOrchestrator):
    """Handle processing specific games."""
    print("\n" + "-" * 40)
    print("PROCESS SPECIFIC GAME(S)")
    print("-" * 40)
    
    # Show available games
    available = orchestrator.get_available_games()
    processed = orchestrator.get_processed_games()
    
    print(f"\nAvailable games: {len(available)}")
    if available:
        print(f"  IDs: {', '.join(map(str, available[:20]))}")
        if len(available) > 20:
            print(f"  ... and {len(available) - 20} more")
    
    print(f"\nAlready processed: {len(processed)}")
    if processed:
        print(f"  IDs: {', '.join(map(str, processed[:20]))}")
    
    print("\nEnter game ID(s) to process:")
    print("  Examples:")
    print("    18969              - Single game")
    print("    18969, 18970       - Multiple games (comma-separated)")
    print("    18969 18970 18971  - Multiple games (space-separated)")
    print("    18969-18975        - Range of games")
    print("    all                - All available games")
    print("    unprocessed        - All unprocessed games")
    
    user_input = input("\nGame ID(s): ").strip().lower()
    
    if not user_input:
        print("No games specified.")
        return
    
    if user_input == 'all':
        game_ids = available
    elif user_input in ['unprocessed', 'new']:
        game_ids = orchestrator.get_unprocessed_games()
    else:
        game_ids = parse_game_ids(user_input)
    
    if not game_ids:
        print("No valid game IDs found.")
        return
    
    # Confirm
    print(f"\nWill process {len(game_ids)} game(s): {game_ids[:10]}")
    if len(game_ids) > 10:
        print(f"  ... and {len(game_ids) - 10} more")
    
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Process games
    print("\nProcessing...")
    results = orchestrator.process_games(game_ids, force_reload=True)
    
    # Show results
    print(f"\n✓ Successfully processed: {len(results['success'])}")
    if results['failed']:
        print(f"✗ Failed: {len(results['failed'])} - {results['failed']}")


def handle_show_status(orchestrator: PipelineOrchestrator):
    """Show pipeline status."""
    print("\n" + "-" * 40)
    print("PIPELINE STATUS")
    print("-" * 40)
    
    status = orchestrator.get_status()
    
    print("\nTABLE COUNTS BY LAYER:")
    for layer in ['stage', 'intermediate', 'datamart']:
        info = status[layer]
        print(f"  {layer.upper():15} {info['tables']:3} tables, {info['rows']:>10,} rows")
    
    print(f"\nGAMES:")
    print(f"  Available:    {len(status['available_games']):3} games")
    print(f"  Processed:    {len(status['processed_games']):3} games")
    print(f"  Unprocessed:  {len(status['unprocessed_games']):3} games")
    
    if status['unprocessed_games']:
        print(f"\n  Unprocessed IDs: {status['unprocessed_games'][:10]}")
        if len(status['unprocessed_games']) > 10:
            print(f"    ... and {len(status['unprocessed_games']) - 10} more")


def handle_reload_blb(orchestrator: PipelineOrchestrator):
    """Reload BLB tables."""
    print("\n" + "-" * 40)
    print("RELOAD BLB TABLES")
    print("-" * 40)
    
    confirm = input("\nThis will reload all BLB tables. Proceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    from src.pipeline.stage.load_blb_tables import load_blb_to_stage
    from src.pipeline.intermediate.transform_blb import transform_blb_to_intermediate
    from src.pipeline.datamart.publish_dimensions import publish_blb_to_datamart
    
    print("\nReloading...")
    
    # Stage
    blb_file = orchestrator.blb_file
    stage_results = load_blb_to_stage(blb_file, force_reload=True)
    print(f"  ✓ Staged {len(stage_results)} tables")
    
    # Intermediate
    int_results = transform_blb_to_intermediate()
    print(f"  ✓ Transformed {len(int_results)} tables")
    
    # Datamart
    dm_results = publish_blb_to_datamart()
    print(f"  ✓ Published {len(dm_results)} tables")
    
    print("\n✓ BLB tables reloaded successfully")


def handle_export(orchestrator: PipelineOrchestrator):
    """Export datamart to CSV."""
    print("\n" + "-" * 40)
    print("EXPORT TO CSV")
    print("-" * 40)
    
    from src.pipeline.datamart.export_to_csv import export_datamart_to_csv
    
    output_dir = orchestrator.output_dir
    print(f"\nExporting to: {output_dir}")
    
    count = export_datamart_to_csv(output_dir)
    print(f"\n✓ Exported {count} CSV files")


def handle_list_games(orchestrator: PipelineOrchestrator):
    """List available games."""
    print("\n" + "-" * 40)
    print("AVAILABLE GAMES")
    print("-" * 40)
    
    available = orchestrator.get_available_games()
    processed = orchestrator.get_processed_games()
    unprocessed = orchestrator.get_unprocessed_games()
    
    print(f"\nTotal available: {len(available)}")
    if available:
        for i, gid in enumerate(available):
            status = "✓" if gid in processed else " "
            print(f"  [{status}] {gid}")
            if i >= 49:
                print(f"  ... and {len(available) - 50} more")
                break
    
    print(f"\nLegend: [✓] = processed, [ ] = unprocessed")


def handle_clear_layer(orchestrator: PipelineOrchestrator):
    """Clear a specific layer."""
    print("\n" + "-" * 40)
    print("CLEAR LAYER")
    print("-" * 40)
    
    print("\nSelect layer to clear:")
    print("  1. Stage (stg_* tables)")
    print("  2. Intermediate (int_* tables)")
    print("  3. Datamart (final tables)")
    print("  4. Cancel")
    
    choice = input("\nChoice (1-4): ").strip()
    
    layer_map = {'1': 'stage', '2': 'intermediate', '3': 'datamart'}
    
    if choice not in layer_map:
        print("Cancelled.")
        return
    
    layer = layer_map[choice]
    
    from src.database.table_operations import clear_layer, get_tables_by_layer
    
    tables = get_tables_by_layer(layer)
    print(f"\nThis will drop {len(tables)} tables in the {layer} layer.")
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    count = clear_layer(layer)
    print(f"\n✓ Cleared {count} tables from {layer} layer")


def handle_overwrite_games(orchestrator: PipelineOrchestrator):
    """Handle overwriting/reprocessing existing games with safeguards."""
    from src.pipeline.game_management import (
        get_game_data_summary,
        format_game_summary,
        overwrite_game,
        remove_game_all_layers,
        list_game_backups
    )
    
    print("\n" + "=" * 60)
    print("OVERWRITE / REPROCESS EXISTING GAME(S)")
    print("=" * 60)
    
    print("\n⚠️  WARNING: This will DELETE existing data and reload from source files.")
    print("    A backup will be created before deletion.\n")
    
    print("Options:")
    print("  1. Overwrite specific game(s)")
    print("  2. Delete game data (without reloading)")
    print("  3. View game data summary")
    print("  4. List available backups")
    print("  5. Restore from backup")
    print("  6. Cancel")
    
    choice = input("\nChoice (1-6): ").strip()
    
    if choice == '1':
        _handle_overwrite_specific(orchestrator)
    elif choice == '2':
        _handle_delete_game(orchestrator)
    elif choice == '3':
        _handle_view_summary(orchestrator)
    elif choice == '4':
        _handle_list_backups()
    elif choice == '5':
        _handle_restore_backup()
    else:
        print("Cancelled.")


def _handle_overwrite_specific(orchestrator: PipelineOrchestrator):
    """Handle overwriting specific games."""
    from src.pipeline.game_management import (
        get_game_data_summary,
        format_game_summary,
        overwrite_game
    )
    
    # Show processed games
    processed = orchestrator.get_processed_games()
    print(f"\nCurrently processed games: {len(processed)}")
    if processed:
        print(f"  IDs: {', '.join(map(str, processed[:20]))}")
        if len(processed) > 20:
            print(f"  ... and {len(processed) - 20} more")
    
    user_input = input("\nEnter game ID(s) to overwrite (comma-separated): ").strip()
    
    if not user_input:
        print("No games specified.")
        return
    
    game_ids = parse_game_ids(user_input)
    
    if not game_ids:
        print("No valid game IDs found.")
        return
    
    # Show what will be overwritten
    print("\n" + "-" * 40)
    print("DATA THAT WILL BE OVERWRITTEN:")
    print("-" * 40)
    
    total_rows = 0
    for game_id in game_ids:
        summary = get_game_data_summary(game_id)
        print(format_game_summary(summary))
        total_rows += summary['total_rows']
    
    if total_rows == 0:
        print("\nNo existing data found. These are new games.")
        confirm = input("Process as new? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return
        # Process as new
        orchestrator.process_games(game_ids, force_reload=True)
        print("\n✓ Games processed successfully")
        return
    
    # Serious warning for existing data
    print("\n" + "!" * 60)
    print("⚠️  DESTRUCTIVE OPERATION WARNING")
    print("!" * 60)
    print(f"\nYou are about to OVERWRITE {len(game_ids)} game(s)")
    print(f"This will DELETE {total_rows:,} existing rows")
    print("A backup will be created before deletion.")
    
    # First confirmation
    confirm1 = input("\nType 'OVERWRITE' to confirm: ").strip()
    if confirm1 != 'OVERWRITE':
        print("Cancelled. (You must type 'OVERWRITE' exactly)")
        return
    
    # Extra confirmation for multiple games
    if len(game_ids) >= 3:
        print(f"\n⚠️  You are overwriting {len(game_ids)} games.")
        confirm2 = input("Type the number of games to double-confirm: ").strip()
        if confirm2 != str(len(game_ids)):
            print("Cancelled. Number did not match.")
            return
    
    # Process overwrites
    print("\nProcessing overwrites...")
    success = []
    failed = []
    
    for game_id in game_ids:
        try:
            # Find tracking file
            game_folder = orchestrator.games_dir / str(game_id)
            tracking_file = game_folder / f'{game_id}_tracking.xlsx'
            
            if not tracking_file.exists():
                # Try alternate location
                tracking_file = orchestrator.games_dir / f'{game_id}_tracking.xlsx'
            
            if not tracking_file.exists():
                print(f"  ✗ Tracking file not found for game {game_id}")
                failed.append(game_id)
                continue
            
            result = overwrite_game(game_id, tracking_file, confirm=True, backup=True)
            print(f"  ✓ Game {game_id} overwritten")
            if result.get('backup_created'):
                print(f"    Backup: {result.get('backup_location', 'created')}")
            success.append(game_id)
            
        except Exception as e:
            print(f"  ✗ Game {game_id} failed: {e}")
            failed.append(game_id)
    
    print(f"\n{'='*40}")
    print(f"OVERWRITE COMPLETE")
    print(f"  Success: {len(success)}")
    print(f"  Failed:  {len(failed)}")
    if failed:
        print(f"  Failed IDs: {failed}")


def _handle_delete_game(orchestrator: PipelineOrchestrator):
    """Handle deleting game data without reloading."""
    from src.pipeline.game_management import (
        get_game_data_summary,
        format_game_summary,
        remove_game_all_layers
    )
    
    processed = orchestrator.get_processed_games()
    print(f"\nCurrently processed games: {len(processed)}")
    if processed:
        print(f"  IDs: {', '.join(map(str, processed[:20]))}")
    
    user_input = input("\nEnter game ID(s) to DELETE (comma-separated): ").strip()
    
    if not user_input:
        print("No games specified.")
        return
    
    game_ids = parse_game_ids(user_input)
    
    if not game_ids:
        print("No valid game IDs found.")
        return
    
    # Show what will be deleted
    print("\n" + "-" * 40)
    print("DATA THAT WILL BE DELETED:")
    print("-" * 40)
    
    total_rows = 0
    for game_id in game_ids:
        summary = get_game_data_summary(game_id)
        print(format_game_summary(summary))
        total_rows += summary['total_rows']
    
    if total_rows == 0:
        print("\nNo data found for these games.")
        return
    
    print("\n" + "!" * 60)
    print("⚠️  PERMANENT DELETION WARNING")
    print("!" * 60)
    print(f"\nYou are about to DELETE {len(game_ids)} game(s)")
    print(f"This will permanently remove {total_rows:,} rows")
    print("This action CANNOT be undone (no backup will be created).")
    
    confirm = input("\nType 'DELETE' to confirm: ").strip()
    if confirm != 'DELETE':
        print("Cancelled.")
        return
    
    # Delete
    for game_id in game_ids:
        try:
            result = remove_game_all_layers(game_id, confirm=True)
            print(f"  ✓ Game {game_id}: {result.get('total_removed', 0):,} rows deleted")
        except Exception as e:
            print(f"  ✗ Game {game_id} failed: {e}")
    
    print("\n✓ Deletion complete")


def _handle_view_summary(orchestrator: PipelineOrchestrator):
    """View summary of game data."""
    from src.pipeline.game_management import (
        get_game_data_summary,
        format_game_summary
    )
    
    user_input = input("\nEnter game ID: ").strip()
    
    if not user_input:
        return
    
    try:
        game_id = int(user_input)
    except ValueError:
        print("Invalid game ID")
        return
    
    summary = get_game_data_summary(game_id)
    print(format_game_summary(summary))


def _handle_list_backups():
    """List available game backups."""
    from src.pipeline.game_management import list_game_backups
    
    backups = list_game_backups()
    
    if not backups:
        print("\nNo backups found.")
        return
    
    print(f"\nFound {len(backups)} backup(s):\n")
    for b in backups[:20]:
        print(f"  Game {b['game_id']} | {b['timestamp']} | {b['rows']} rows")
        print(f"    File: {b['file']}")
    
    if len(backups) > 20:
        print(f"\n  ... and {len(backups) - 20} more")


def _handle_restore_backup():
    """Restore game from backup."""
    from src.pipeline.game_management import list_game_backups, restore_game_from_backup
    
    user_input = input("\nEnter game ID to restore: ").strip()
    
    if not user_input:
        return
    
    try:
        game_id = int(user_input)
    except ValueError:
        print("Invalid game ID")
        return
    
    backups = list_game_backups(game_id)
    
    if not backups:
        print(f"\nNo backups found for game {game_id}")
        return
    
    print(f"\nAvailable backups for game {game_id}:")
    for i, b in enumerate(backups, 1):
        print(f"  {i}. {b['timestamp']} | {b['rows']} rows")
    
    choice = input("\nSelect backup number (or 'cancel'): ").strip()
    
    if choice.lower() == 'cancel' or not choice:
        return
    
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(backups):
            print("Invalid selection")
            return
    except ValueError:
        print("Invalid selection")
        return
    
    backup = backups[idx]
    print(f"\nWill restore from: {backup['timestamp']}")
    print(f"  Tables: {', '.join(backup['tables'])}")
    print(f"  Rows: {backup['rows']}")
    
    confirm = input("\nType 'RESTORE' to confirm: ").strip()
    if confirm != 'RESTORE':
        print("Cancelled.")
        return
    
    result = restore_game_from_backup(Path(backup['file']), confirm=True)
    print(f"\n✓ Game {game_id} restored successfully")
    for table, count in result.get('restored_tables', {}).items():
        print(f"  {table}: {count} rows")


def handle_full_pipeline(orchestrator: PipelineOrchestrator):
    """Run full pipeline."""
    print("\n" + "-" * 40)
    print("RUN FULL PIPELINE")
    print("-" * 40)
    
    available = orchestrator.get_available_games()
    
    print(f"\nThis will:")
    print(f"  - Load BLB tables (if not already loaded)")
    print(f"  - Process {len(available)} available game(s)")
    print(f"  - Build datamart tables")
    print(f"  - Export to CSV")
    
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    results = orchestrator.run_full_pipeline(
        game_ids=available,
        reload_blb=False,
        export_csv=True
    )
    
    print(f"\n✓ Pipeline completed in {results['duration_seconds']:.1f} seconds")
    print(f"  Games processed: {len(results['games_processed'])}")


def handle_process_unprocessed(orchestrator: PipelineOrchestrator):
    """Process all unprocessed games."""
    print("\n" + "-" * 40)
    print("PROCESS UNPROCESSED GAMES")
    print("-" * 40)
    
    unprocessed = orchestrator.get_unprocessed_games()
    
    if not unprocessed:
        print("\nNo unprocessed games found.")
        return
    
    print(f"\n{len(unprocessed)} unprocessed game(s): {unprocessed[:10]}")
    if len(unprocessed) > 10:
        print(f"  ... and {len(unprocessed) - 10} more")
    
    confirm = input("\nProcess all? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    results = orchestrator.process_games(unprocessed, force_reload=True)
    
    print(f"\n✓ Processed {len(results['success'])} games")
    if results['failed']:
        print(f"✗ Failed: {results['failed']}")


def run_interactive():
    """Run interactive menu."""
    orchestrator = PipelineOrchestrator(PROJECT_ROOT)
    
    while True:
        show_menu()
        choice = get_user_choice()
        
        if choice == '1':
            handle_full_pipeline(orchestrator)
        elif choice == '2':
            handle_process_games(orchestrator)
        elif choice == '3':
            handle_process_unprocessed(orchestrator)
        elif choice == '4':
            handle_show_status(orchestrator)
        elif choice == '5':
            handle_reload_blb(orchestrator)
        elif choice == '6':
            handle_export(orchestrator)
        elif choice == '7':
            handle_list_games(orchestrator)
        elif choice == '8':
            handle_clear_layer(orchestrator)
        elif choice == '9':
            handle_overwrite_games(orchestrator)
        elif choice == '10':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please enter 1-10.")


def main():
    """Main entry point with CLI argument handling."""
    parser = argparse.ArgumentParser(
        description='Hockey Analytics ETL Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Interactive menu
  python main.py --game 18969              # Process single game
  python main.py --games 18969,18970,18971 # Process multiple games
  python main.py --games 18969-18975       # Process range of games
  python main.py --process-all             # Process all unprocessed games
  python main.py --reload-blb              # Reload BLB tables
  python main.py --status                  # Show pipeline status
  python main.py --export                  # Export to CSV
  
Overwrite/Reprocess (with safeguards):
  python main.py --overwrite 18969                 # Overwrite single game
  python main.py --overwrite 18969,18970 --confirm # Overwrite multiple (requires --confirm)
  python main.py --delete 18969 --confirm          # Delete game data
  python main.py --game-info 18969                 # Show game data summary
        """
    )
    
    parser.add_argument(
        '--game', '-g',
        type=str,
        help='Single game ID to process'
    )
    
    parser.add_argument(
        '--games', '-G',
        type=str,
        help='Multiple game IDs (comma-separated, space-separated, or range)'
    )
    
    parser.add_argument(
        '--process-all', '-a',
        action='store_true',
        help='Process all unprocessed games'
    )
    
    parser.add_argument(
        '--reload-blb', '-r',
        action='store_true',
        help='Force reload BLB tables'
    )
    
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Show pipeline status'
    )
    
    parser.add_argument(
        '--export', '-e',
        action='store_true',
        help='Export datamart to CSV'
    )
    
    parser.add_argument(
        '--list-games', '-l',
        action='store_true',
        help='List available games'
    )
    
    parser.add_argument(
        '--overwrite', '-O',
        type=str,
        help='Overwrite/reprocess existing game(s) - requires --confirm'
    )
    
    parser.add_argument(
        '--delete', '-D',
        type=str,
        help='Delete game data (without reloading) - requires --confirm'
    )
    
    parser.add_argument(
        '--game-info', '-i',
        type=str,
        help='Show data summary for a game'
    )
    
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Confirm destructive operations (required for --overwrite and --delete)'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup before overwrite (not recommended)'
    )
    
    args = parser.parse_args()
    
    # If no arguments, run interactive mode
    if len(sys.argv) == 1:
        run_interactive()
        return
    
    # Initialize orchestrator
    orchestrator = PipelineOrchestrator(PROJECT_ROOT)
    
    # Handle arguments
    if args.status:
        handle_show_status(orchestrator)
    
    if args.list_games:
        handle_list_games(orchestrator)
    
    if args.game_info:
        from src.pipeline.game_management import get_game_data_summary, format_game_summary
        try:
            game_id = int(args.game_info)
            summary = get_game_data_summary(game_id)
            print(format_game_summary(summary))
        except ValueError:
            print(f"Invalid game ID: {args.game_info}")
    
    if args.reload_blb:
        from src.pipeline.stage.load_blb_tables import load_blb_to_stage
        from src.pipeline.intermediate.transform_blb import transform_blb_to_intermediate
        from src.pipeline.datamart.publish_dimensions import publish_blb_to_datamart
        
        print("Reloading BLB tables...")
        load_blb_to_stage(orchestrator.blb_file, force_reload=True)
        transform_blb_to_intermediate()
        publish_blb_to_datamart()
        print("✓ BLB tables reloaded")
    
    if args.overwrite:
        from src.pipeline.game_management import (
            get_game_data_summary,
            format_game_summary,
            overwrite_game
        )
        
        game_ids = parse_game_ids(args.overwrite)
        
        if not game_ids:
            print("No valid game IDs found.")
            return
        
        if not args.confirm:
            print("\n⚠️  OVERWRITE REQUIRES CONFIRMATION")
            print(f"Game(s) to overwrite: {game_ids}")
            
            for gid in game_ids:
                summary = get_game_data_summary(gid)
                print(format_game_summary(summary))
            
            print("\nTo proceed, add --confirm flag:")
            print(f"  python main.py --overwrite {args.overwrite} --confirm")
            return
        
        # Confirmed - proceed with overwrite
        print(f"\nOverwriting {len(game_ids)} game(s)...")
        
        for game_id in game_ids:
            game_folder = orchestrator.games_dir / str(game_id)
            tracking_file = game_folder / f'{game_id}_tracking.xlsx'
            
            if not tracking_file.exists():
                tracking_file = orchestrator.games_dir / f'{game_id}_tracking.xlsx'
            
            if not tracking_file.exists():
                print(f"✗ Tracking file not found for game {game_id}")
                continue
            
            try:
                result = overwrite_game(
                    game_id, 
                    tracking_file, 
                    confirm=True, 
                    backup=not args.no_backup
                )
                print(f"✓ Game {game_id} overwritten")
            except Exception as e:
                print(f"✗ Game {game_id} failed: {e}")
    
    if args.delete:
        from src.pipeline.game_management import (
            get_game_data_summary,
            format_game_summary,
            remove_game_all_layers
        )
        
        game_ids = parse_game_ids(args.delete)
        
        if not game_ids:
            print("No valid game IDs found.")
            return
        
        if not args.confirm:
            print("\n⚠️  DELETE REQUIRES CONFIRMATION")
            print(f"Game(s) to delete: {game_ids}")
            
            for gid in game_ids:
                summary = get_game_data_summary(gid)
                print(format_game_summary(summary))
            
            print("\nTo proceed, add --confirm flag:")
            print(f"  python main.py --delete {args.delete} --confirm")
            return
        
        # Confirmed - proceed with delete
        print(f"\nDeleting {len(game_ids)} game(s)...")
        
        for game_id in game_ids:
            try:
                result = remove_game_all_layers(game_id, confirm=True)
                print(f"✓ Game {game_id}: {result.get('total_removed', 0):,} rows deleted")
            except Exception as e:
                print(f"✗ Game {game_id} failed: {e}")
    
    if args.game:
        game_ids = parse_game_ids(args.game)
        if game_ids:
            print(f"Processing game(s): {game_ids}")
            orchestrator.process_games(game_ids, force_reload=True)
    
    if args.games:
        game_ids = parse_game_ids(args.games)
        if game_ids:
            print(f"Processing {len(game_ids)} game(s): {game_ids}")
            orchestrator.process_games(game_ids, force_reload=True)
    
    if args.process_all:
        unprocessed = orchestrator.get_unprocessed_games()
        if unprocessed:
            print(f"Processing {len(unprocessed)} unprocessed game(s)...")
            orchestrator.process_games(unprocessed, force_reload=True)
        else:
            print("No unprocessed games found.")
    
    if args.export:
        handle_export(orchestrator)


if __name__ == '__main__':
    main()
