#!/usr/bin/env python3
"""
BenchSight Enhanced Data Loader with Comprehensive Logging

This is an enhanced version of flexible_loader.py that integrates with
the BenchSight logging system for complete audit trails.

Features:
- All operations logged to files (logs/ directory)
- Optional logging to Supabase logging tables
- Detailed per-table tracking
- Error capture with tracebacks
- Run summaries
- Dry-run mode

Usage:
    # Full load with logging
    python flexible_loader_with_logging.py --scope full --operation replace
    
    # Single game with dry run
    python flexible_loader_with_logging.py --scope game --game-id 18969 --operation replace --dry-run
    
    # Load with Supabase logging enabled
    python flexible_loader_with_logging.py --scope full --operation replace --log-to-supabase
    
    # Show previous run summary
    python flexible_loader_with_logging.py --show-last-run

Environment:
    SUPABASE_URL: Your Supabase project URL
    SUPABASE_SERVICE_KEY: Service role key (not anon key)
"""

import os
import sys
import csv
import argparse
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: supabase package not installed. Install with: pip install supabase")

try:
    from src.logging_system import (
        BenchSightLogger, 
        TableLoadResult, 
        Status, 
        create_logger,
        get_latest_run_summary
    )
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    print("Warning: logging_system not found. Basic logging will be used.")

try:
    from config.config_loader import load_config, BenchSightConfig
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# ============================================================
# CONFIGURATION
# ============================================================

def get_config():
    """Load configuration from config files or environment"""
    if CONFIG_AVAILABLE:
        return load_config()
    else:
        # Fallback to environment variables
        from dataclasses import dataclass
        @dataclass
        class FallbackConfig:
            supabase_url: str = os.environ.get("SUPABASE_URL", "")
            supabase_service_key: str = os.environ.get("SUPABASE_SERVICE_KEY", "")
            data_dir: Path = Path(__file__).parent.parent / "data" / "output"
            log_dir: Path = Path(__file__).parent.parent / "logs"
            batch_size: int = 500
            verbose: bool = True
            is_configured: bool = property(lambda s: bool(s.supabase_url and s.supabase_service_key))
        return FallbackConfig()

# Load config
_cfg = get_config()
DATA_DIR = _cfg.data_dir
LOGS_DIR = _cfg.log_dir
SUPABASE_URL = _cfg.supabase_url
SUPABASE_KEY = _cfg.supabase_service_key

# Table definitions with dependencies
TABLE_CONFIG = {
    "dim_player": {"category": "dims", "pk": "player_id", "has_game_id": False},
    "dim_team": {"category": "dims", "pk": "team_id", "has_game_id": False},
    "dim_schedule": {"category": "dims", "pk": "game_id", "has_game_id": True},
    "fact_shifts": {"category": "core_facts", "pk": "shift_key", "has_game_id": True},
    "fact_events": {"category": "core_facts", "pk": "event_key", "has_game_id": True},
    "fact_events_player": {"category": "core_facts", "pk": "event_player_key", "has_game_id": True},
    "fact_shifts_player": {"category": "core_facts", "pk": "shift_player_key", "has_game_id": True},
    "fact_player_game_stats": {"category": "stats_facts", "pk": "player_game_key", "has_game_id": True},
    "fact_team_game_stats": {"category": "stats_facts", "pk": "team_game_key", "has_game_id": True},
    "fact_goalie_game_stats": {"category": "stats_facts", "pk": "goalie_game_key", "has_game_id": True},
    "fact_h2h": {"category": "analytics_facts", "pk": "h2h_key", "has_game_id": True},
    "fact_wowy": {"category": "analytics_facts", "pk": "wowy_key", "has_game_id": True},
}

# Load order (respects FK dependencies)
LOAD_ORDER = [
    "dim_player", "dim_team", "dim_schedule",
    "fact_shifts", "fact_events", "fact_events_player", "fact_shifts_player",
    "fact_player_game_stats", "fact_team_game_stats", "fact_goalie_game_stats",
    "fact_h2h", "fact_wowy",
]

DELETE_ORDER = list(reversed(LOAD_ORDER))


# ============================================================
# ENHANCED LOADER CLASS
# ============================================================

class EnhancedBenchSightLoader:
    """
    Enhanced data loader with comprehensive logging.
    """
    
    def __init__(
        self,
        url: str = SUPABASE_URL,
        key: str = SUPABASE_KEY,
        data_dir: Path = DATA_DIR,
        log_to_supabase: bool = False,
        dry_run: bool = False,
        verbose: bool = True
    ):
        self.url = url
        self.key = key
        self.data_dir = data_dir
        self.dry_run = dry_run
        self.verbose = verbose
        self.batch_size = 500
        
        # Initialize Supabase client if available
        self.supabase: Optional[Client] = None
        if SUPABASE_AVAILABLE and key:
            try:
                self.supabase = create_client(url, key)
            except Exception as e:
                print(f"Warning: Could not connect to Supabase: {e}")
        
        # Initialize logger
        supabase_for_logging = self.supabase if log_to_supabase else None
        if LOGGING_AVAILABLE:
            self.logger = BenchSightLogger(
                run_type="supabase_load",
                base_log_dir=str(LOGS_DIR),
                console_output=verbose,
                supabase_client=supabase_for_logging
            )
        else:
            self.logger = None
        
        # Track results
        self.table_results: List[TableLoadResult] = []
    
    def log(self, message: str, level: str = "info"):
        """Log message to logger and/or console"""
        if self.logger:
            if level == "debug":
                self.logger.log_debug(message)
            elif level == "warning":
                self.logger.log_warning(message)
            elif level == "error":
                self.logger.log_error(message)
            else:
                self.logger.log_info(message)
        elif self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def read_csv(self, filepath: Path) -> tuple[List[Dict[str, Any]], int, int]:
        """Read CSV file and return records, row count, column count."""
        records = []
        column_count = 0
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            column_count = len(reader.fieldnames) if reader.fieldnames else 0
            
            for row in reader:
                cleaned = {}
                for k, v in row.items():
                    if v == '' or v == 'nan' or v == 'NaN' or v == 'None':
                        cleaned[k] = None
                    elif v.lower() == 'true':
                        cleaned[k] = True
                    elif v.lower() == 'false':
                        cleaned[k] = False
                    else:
                        try:
                            if '.' in v:
                                cleaned[k] = float(v)
                            else:
                                cleaned[k] = int(v)
                        except (ValueError, TypeError):
                            cleaned[k] = v
                records.append(cleaned)
        
        return records, len(records), column_count
    
    def get_table_count(self, table_name: str) -> int:
        """Get current row count from Supabase table"""
        if not self.supabase:
            return 0
        try:
            # Use count query
            result = self.supabase.table(table_name).select("*", count="exact").limit(0).execute()
            return result.count if result.count else 0
        except Exception:
            return 0
    
    def delete_table_data(self, table_name: str, game_id: Optional[int] = None) -> int:
        """Delete data from table"""
        if self.dry_run:
            self.log(f"[DRY RUN] Would delete from {table_name}" + (f" where game_id={game_id}" if game_id else ""))
            return 0
        
        if not self.supabase:
            return 0
        
        try:
            if game_id and TABLE_CONFIG.get(table_name, {}).get('has_game_id', True):
                result = self.supabase.table(table_name).delete().eq('game_id', game_id).execute()
            else:
                # Delete all by matching impossible condition's opposite
                pk = TABLE_CONFIG.get(table_name, {}).get('pk', 'id')
                result = self.supabase.table(table_name).delete().neq(pk, '__IMPOSSIBLE__').execute()
            return len(result.data) if result.data else 0
        except Exception as e:
            self.log(f"Error deleting from {table_name}: {e}", "error")
            return 0
    
    def load_table(
        self,
        table_name: str,
        operation: str = 'upsert',
        game_id: Optional[int] = None
    ) -> TableLoadResult:
        """Load a single table with full logging"""
        start_time = datetime.now()
        
        csv_path = self.data_dir / f"{table_name}.csv"
        
        # Initialize result
        result = TableLoadResult(
            table_name=table_name,
            operation=operation,
            status=Status.STARTED.value,
            csv_path=str(csv_path)
        )
        
        # Check CSV exists
        if not csv_path.exists():
            result.status = Status.FAILED.value
            result.error_message = f"CSV not found: {csv_path}"
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            self.log(f"[{table_name}] ✗ CSV not found", "error")
            return result
        
        # Read CSV
        try:
            records, csv_rows, csv_columns = self.read_csv(csv_path)
            result.csv_rows = csv_rows
            result.csv_columns = csv_columns
        except Exception as e:
            result.status = Status.FAILED.value
            result.error_message = f"Error reading CSV: {e}"
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            if self.logger:
                self.logger.log_error(f"[{table_name}] Error reading CSV", exception=e)
            return result
        
        # Filter by game_id if specified
        if game_id and TABLE_CONFIG.get(table_name, {}).get('has_game_id', True):
            records = [r for r in records if r.get('game_id') == game_id]
        
        # Get count before
        result.rows_before = self.get_table_count(table_name)
        
        # Log start
        self.log(f"[{table_name}] Starting {operation} ({len(records)} records)...")
        
        # Handle dry run
        if self.dry_run:
            result.status = Status.SKIPPED.value
            result.rows_inserted = len(records) if operation != 'upsert' else 0
            result.rows_updated = len(records) if operation == 'upsert' else 0
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            self.log(f"[{table_name}] [DRY RUN] Would load {len(records)} records")
            return result
        
        # Check Supabase connection
        if not self.supabase:
            result.status = Status.FAILED.value
            result.error_message = "Supabase client not initialized"
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            return result
        
        # Handle replace operation
        actual_operation = operation
        if operation == 'replace':
            deleted = self.delete_table_data(table_name, game_id)
            result.rows_deleted = deleted
            actual_operation = 'insert'
        
        # Load data in batches
        rows_loaded = 0
        errors = []
        
        for i in range(0, len(records), self.batch_size):
            batch = records[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(records) + self.batch_size - 1) // self.batch_size
            
            try:
                if actual_operation == 'upsert':
                    self.supabase.table(table_name).upsert(batch).execute()
                else:
                    self.supabase.table(table_name).insert(batch).execute()
                rows_loaded += len(batch)
                
                if self.verbose and total_batches > 1:
                    self.log(f"[{table_name}] Batch {batch_num}/{total_batches} complete", "debug")
                    
            except Exception as e:
                error_msg = f"Batch {batch_num}: {str(e)}"
                errors.append(error_msg)
                if self.logger:
                    self.logger.log_error(f"[{table_name}] {error_msg}", exception=e)
        
        # Get count after
        result.rows_after = self.get_table_count(table_name)
        
        # Calculate inserted/updated
        if operation == 'upsert':
            # Estimate: new rows are inserted, existing are updated
            result.rows_inserted = max(0, result.rows_after - result.rows_before)
            result.rows_updated = rows_loaded - result.rows_inserted
        else:
            result.rows_inserted = rows_loaded
            result.rows_updated = 0
        
        # Set final status
        result.duration_seconds = (datetime.now() - start_time).total_seconds()
        if errors:
            result.status = Status.PARTIAL.value if rows_loaded > 0 else Status.FAILED.value
            result.error_message = "; ".join(errors)
        else:
            result.status = Status.SUCCESS.value
        
        # Log result
        status_icon = "✓" if result.status == Status.SUCCESS.value else "⚠" if result.status == Status.PARTIAL.value else "✗"
        self.log(f"[{table_name}] {status_icon} {rows_loaded} rows loaded ({result.duration_seconds:.2f}s)")
        
        return result
    
    def load_full(self, operation: str = 'replace') -> Dict[str, Any]:
        """Load all tables in dependency order"""
        if self.logger:
            self.logger.start_run()
        
        self.log(f"{'='*60}")
        self.log(f"FULL LOAD STARTED ({operation})")
        self.log(f"{'='*60}")
        
        start_time = datetime.now()
        
        for table_name in LOAD_ORDER:
            result = self.load_table(table_name, operation)
            self.table_results.append(result)
            
            # Log to logger
            if self.logger:
                self.logger.log_table_result(result)
        
        # Generate summary
        duration = (datetime.now() - start_time).total_seconds()
        success_count = sum(1 for r in self.table_results if r.status == Status.SUCCESS.value)
        failed_count = sum(1 for r in self.table_results if r.status == Status.FAILED.value)
        total_rows = sum(r.rows_inserted + r.rows_updated for r in self.table_results)
        
        summary = {
            'success': failed_count == 0,
            'tables_processed': len(self.table_results),
            'tables_success': success_count,
            'tables_failed': failed_count,
            'total_rows_loaded': total_rows,
            'duration_seconds': duration,
            'results': {r.table_name: {
                'status': r.status,
                'rows_inserted': r.rows_inserted,
                'rows_updated': r.rows_updated,
                'error': r.error_message
            } for r in self.table_results}
        }
        
        # End run
        if self.logger:
            run_summary = self.logger.end_run()
            summary['run_id'] = run_summary.run_id
            summary['log_directory'] = str(self.logger.run_dir)
        
        return summary
    
    def load_game(self, game_id: int, operation: str = 'replace') -> Dict[str, Any]:
        """Load data for a specific game"""
        if self.logger:
            self.logger.start_run()
        
        self.log(f"{'='*60}")
        self.log(f"GAME {game_id} LOAD STARTED ({operation})")
        self.log(f"{'='*60}")
        
        start_time = datetime.now()
        
        # Load only tables that have game_id
        for table_name in LOAD_ORDER:
            if TABLE_CONFIG.get(table_name, {}).get('has_game_id', True) or table_name.startswith('dim_'):
                result = self.load_table(table_name, operation, game_id)
                self.table_results.append(result)
                
                if self.logger:
                    self.logger.log_table_result(result)
        
        duration = (datetime.now() - start_time).total_seconds()
        success_count = sum(1 for r in self.table_results if r.status == Status.SUCCESS.value)
        
        summary = {
            'success': success_count == len(self.table_results),
            'game_id': game_id,
            'tables_processed': len(self.table_results),
            'duration_seconds': duration
        }
        
        if self.logger:
            run_summary = self.logger.end_run()
            summary['run_id'] = run_summary.run_id
        
        return summary
    
    def load_category(self, category: str, operation: str = 'upsert') -> Dict[str, Any]:
        """Load tables by category"""
        tables = [t for t, c in TABLE_CONFIG.items() if c['category'] == category]
        
        if not tables:
            return {'success': False, 'error': f'Invalid category: {category}'}
        
        if self.logger:
            self.logger.start_run()
        
        self.log(f"Loading category '{category}' ({len(tables)} tables)...")
        
        for table_name in tables:
            if table_name in LOAD_ORDER:
                result = self.load_table(table_name, operation)
                self.table_results.append(result)
                
                if self.logger:
                    self.logger.log_table_result(result)
        
        if self.logger:
            self.logger.end_run()
        
        return {
            'success': all(r.status == Status.SUCCESS.value for r in self.table_results),
            'category': category,
            'tables_loaded': len(self.table_results)
        }
    
    def get_counts(self) -> Dict[str, int]:
        """Get row counts for all tables"""
        counts = {}
        total = 0
        
        self.log("Fetching table counts...")
        
        for table_name in LOAD_ORDER:
            count = self.get_table_count(table_name)
            counts[table_name] = count
            total += count
            self.log(f"  {table_name}: {count:,}")
        
        counts['_total'] = total
        self.log(f"  TOTAL: {total:,}")
        
        return counts
    
    def test_connection(self) -> bool:
        """Test Supabase connection"""
        if not self.supabase:
            self.log("No Supabase client configured", "error")
            return False
        
        try:
            self.supabase.table('dim_player').select("player_id").limit(1).execute()
            self.log("✓ Supabase connection successful")
            return True
        except Exception as e:
            self.log(f"✗ Connection failed: {e}", "error")
            return False


# ============================================================
# CLI INTERFACE
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="BenchSight Enhanced Data Loader with Logging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Full load:     python %(prog)s --scope full --operation replace
  Single game:   python %(prog)s --scope game --game-id 18969 --operation replace
  Category:      python %(prog)s --scope category --category dims --operation upsert
  Table:         python %(prog)s --scope table --table fact_events --operation append
  Dry run:       python %(prog)s --scope full --operation replace --dry-run
  Show counts:   python %(prog)s --counts
  Test conn:     python %(prog)s --test-connection
  Last run:      python %(prog)s --show-last-run
        """
    )
    
    # Scope options
    parser.add_argument('--scope', choices=['full', 'game', 'category', 'table'],
                        help='Scope of the load operation')
    parser.add_argument('--game-id', type=int, help='Game ID (for game scope)')
    parser.add_argument('--category', choices=['dims', 'core_facts', 'stats_facts', 'analytics_facts'],
                        help='Category name (for category scope)')
    parser.add_argument('--table', help='Table name (for table scope)')
    
    # Operation
    parser.add_argument('--operation', choices=['replace', 'append', 'upsert'],
                        default='upsert', help='Load operation (default: upsert)')
    
    # Options
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview without making changes')
    parser.add_argument('--log-to-supabase', action='store_true',
                        help='Also log to Supabase logging tables')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress console output')
    
    # Utility commands
    parser.add_argument('--counts', action='store_true',
                        help='Show row counts for all tables')
    parser.add_argument('--test-connection', action='store_true',
                        help='Test Supabase connection')
    parser.add_argument('--show-last-run', action='store_true',
                        help='Show summary of last run')
    parser.add_argument('--show-config', action='store_true',
                        help='Show current configuration')
    
    args = parser.parse_args()
    
    # Handle utility commands
    if args.show_config:
        print("=" * 60)
        print("BENCHSIGHT CONFIGURATION")
        print("=" * 60)
        cfg = get_config()
        print(f"\nConfig Source: {'config/config_local.ini' if CONFIG_AVAILABLE else 'environment variables'}")
        print(f"Data Directory: {cfg.data_dir}")
        print(f"  Exists: {cfg.data_dir.exists() if hasattr(cfg.data_dir, 'exists') else 'N/A'}")
        print(f"Log Directory: {cfg.log_dir}")
        print(f"\nSupabase URL: {cfg.supabase_url[:50]}..." if cfg.supabase_url else "\nSupabase URL: NOT SET")
        key_preview = f"{'*' * 20}...{cfg.supabase_service_key[-10:]}" if cfg.supabase_service_key else "NOT SET"
        print(f"Service Key: {key_preview}")
        print(f"\nBatch Size: {cfg.batch_size}")
        print(f"Verbose: {cfg.verbose}")
        
        if hasattr(cfg, 'validate'):
            valid, errors = cfg.validate()
            print(f"\n{'✓ Configuration Valid' if valid else '✗ Configuration Invalid'}")
            for err in errors:
                print(f"  - {err}")
        return
    
    if args.show_last_run:
        if LOGGING_AVAILABLE:
            summary = get_latest_run_summary(str(LOGS_DIR))
            if summary:
                print(json.dumps(summary, indent=2))
            else:
                print("No previous runs found")
        else:
            print("Logging system not available")
        return
    
    # Check environment
    if not SUPABASE_KEY and not args.dry_run:
        print("ERROR: Supabase credentials not configured")
        print("")
        print("Option 1: Edit config/config_local.ini")
        print("  [supabase]")
        print("  url = https://YOUR_PROJECT_ID.supabase.co")
        print("  service_key = your-service-role-key-here")
        print("")
        print("Option 2: Set environment variables")
        print("  export SUPABASE_URL='https://YOUR_PROJECT_ID.supabase.co'")
        print("  export SUPABASE_SERVICE_KEY='your-service-role-key'")
        print("")
        print("To get your credentials:")
        print("  1. Go to https://supabase.com/dashboard")
        print("  2. Select your project > Settings > API")
        print("  3. Copy Project URL and service_role key")
        sys.exit(1)
    
    # Initialize loader
    loader = EnhancedBenchSightLoader(
        dry_run=args.dry_run,
        log_to_supabase=args.log_to_supabase,
        verbose=not args.quiet
    )
    
    # Handle utility commands
    if args.test_connection:
        success = loader.test_connection()
        sys.exit(0 if success else 1)
    
    if args.counts:
        loader.get_counts()
        return
    
    # Handle load operations
    if not args.scope:
        parser.print_help()
        return
    
    if args.scope == 'full':
        result = loader.load_full(args.operation)
    elif args.scope == 'game':
        if not args.game_id:
            print("ERROR: --game-id required for game scope")
            sys.exit(1)
        result = loader.load_game(args.game_id, args.operation)
    elif args.scope == 'category':
        if not args.category:
            print("ERROR: --category required for category scope")
            sys.exit(1)
        result = loader.load_category(args.category, args.operation)
    elif args.scope == 'table':
        if not args.table:
            print("ERROR: --table required for table scope")
            sys.exit(1)
        table_result = loader.load_table(args.table, args.operation)
        result = {
            'success': table_result.status == Status.SUCCESS.value,
            'table': table_result.table_name,
            'rows_loaded': table_result.rows_inserted + table_result.rows_updated
        }
    
    # Print summary
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(json.dumps(result, indent=2, default=str))
    
    # Exit with appropriate code
    sys.exit(0 if result.get('success', False) else 1)


if __name__ == "__main__":
    main()
