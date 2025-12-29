#!/usr/bin/env python3
"""
BenchSight Supabase Loader
==========================
Flexible tool for uploading data to Supabase with multiple modes and options.

Usage:
    python scripts/supabase_loader.py --help
    python scripts/supabase_loader.py --all                    # Upload all tables
    python scripts/supabase_loader.py --dims                   # Upload only dimension tables
    python scripts/supabase_loader.py --facts                  # Upload only fact tables
    python scripts/supabase_loader.py --tables dim_player,dim_team  # Specific tables
    python scripts/supabase_loader.py --games 18969,18977      # Specific games only
    python scripts/supabase_loader.py --all --mode append      # Append mode
    python scripts/supabase_loader.py --all --mode replace     # Replace mode (default)
    python scripts/supabase_loader.py --rebuild                # Drop all, recreate, upload all
    python scripts/supabase_loader.py --teardown               # Drop all tables
    python scripts/supabase_loader.py --create-only            # Create tables without data

Author: BenchSight Team
Version: 1.0.0
"""

import argparse
import pandas as pd
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Setup paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "data" / "output"
SQL_DIR = PROJECT_DIR / "sql"
LOG_DIR = PROJECT_DIR / "logs"
CONFIG_DIR = PROJECT_DIR / "config"

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)

# Setup logging
log_file = LOG_DIR / f"supabase_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# TABLE CONFIGURATION
# ============================================================================

DIM_TABLES = [
    'dim_player', 'dim_team', 'dim_schedule', 'dim_league', 'dim_season',
    'dim_position', 'dim_venue', 'dim_period', 'dim_player_role',
    'dim_playerurlref', 'dim_rinkboxcoord', 'dim_rinkcoordzones',
    'dim_randomnames', 'dim_composite_rating', 'dim_stat_type',
    'dim_situation', 'dim_strength', 'dim_event_type', 'dim_rink_coord',
    'dim_shot_type', 'dim_pass_type', 'dim_turnover_type', 'dim_giveaway_type',
    'dim_takeaway_type', 'dim_zone'
]

FACT_TABLES = [
    'fact_player_game_stats', 'fact_events', 'fact_events_player',
    'fact_shifts_player', 'fact_gameroster', 'fact_goalie_game_stats',
    'fact_team_game_stats', 'fact_h2h', 'fact_wowy', 'fact_line_combos',
    'fact_event_chains', 'fact_team_zone_time', 'fact_rush_events',
    'fact_cycle_events', 'fact_possession_time', 'fact_shift_quality',
    'fact_matchup_summary', 'fact_leadership', 'fact_registration',
    'fact_draft', 'fact_playergames'
]

QA_TABLES = [
    'fact_game_status', 'fact_suspicious_stats', 'fact_player_game_position'
]

# Load order (dims first, then facts)
LOAD_ORDER = DIM_TABLES + FACT_TABLES + QA_TABLES


# ============================================================================
# SUPABASE CONNECTION
# ============================================================================

class SupabaseConnection:
    """Manages Supabase connection with error handling."""
    
    def __init__(self):
        self.client = None
        self.url = None
        self.key = None
        self.connected = False
        
    def connect(self) -> bool:
        """Establish connection to Supabase."""
        try:
            # Try to import supabase
            try:
                from supabase import create_client, Client
            except ImportError:
                logger.error("Supabase not installed. Run: pip install supabase")
                return False
            
            # Load credentials from environment or config
            self.url = os.environ.get('SUPABASE_URL')
            self.key = os.environ.get('SUPABASE_KEY')
            
            if not self.url or not self.key:
                # Try config file
                config_file = CONFIG_DIR / "config_local.ini"
                if config_file.exists():
                    import configparser
                    config = configparser.ConfigParser()
                    config.read(config_file)
                    self.url = config.get('supabase', 'url', fallback=None)
                    self.key = config.get('supabase', 'key', fallback=None)
            
            if not self.url or not self.key:
                logger.error("Supabase credentials not found!")
                logger.error("Set SUPABASE_URL and SUPABASE_KEY environment variables")
                logger.error("Or add them to config/config_local.ini")
                return False
            
            self.client = create_client(self.url, self.key)
            self.connected = True
            logger.info(f"✓ Connected to Supabase: {self.url[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def execute_sql(self, sql: str) -> Tuple[bool, str]:
        """Execute raw SQL."""
        try:
            # Use RPC for raw SQL execution
            result = self.client.rpc('exec_sql', {'query': sql}).execute()
            return True, "OK"
        except Exception as e:
            return False, str(e)
    
    def get_table_count(self, table: str) -> int:
        """Get row count for a table."""
        try:
            result = self.client.table(table).select('*', count='exact').execute()
            return result.count if result.count else 0
        except:
            return -1


# ============================================================================
# UPLOAD OPERATIONS
# ============================================================================

class SupabaseLoader:
    """Handles all Supabase upload operations."""
    
    def __init__(self, connection: SupabaseConnection):
        self.conn = connection
        self.stats = {
            'tables_processed': 0,
            'tables_success': 0,
            'tables_failed': 0,
            'rows_uploaded': 0,
            'errors': []
        }
    
    def upload_table(self, table_name: str, mode: str = 'replace', 
                     game_filter: Optional[List[int]] = None) -> bool:
        """
        Upload a single table to Supabase.
        
        Args:
            table_name: Name of table to upload
            mode: 'replace' (truncate + insert) or 'append' (insert only)
            game_filter: Optional list of game_ids to filter by
        """
        csv_file = OUTPUT_DIR / f"{table_name}.csv"
        
        if not csv_file.exists():
            logger.warning(f"⚠️  {table_name}: CSV file not found, skipping")
            return False
        
        try:
            # Load data
            df = pd.read_csv(csv_file, dtype=str)
            original_rows = len(df)
            
            # Apply game filter if specified
            if game_filter and 'game_id' in df.columns:
                df = df[df['game_id'].astype(str).isin([str(g) for g in game_filter])]
                logger.info(f"  Filtered to {len(df)}/{original_rows} rows for games {game_filter}")
            
            if len(df) == 0:
                logger.warning(f"⚠️  {table_name}: No data to upload")
                return True
            
            # Replace mode: truncate first
            if mode == 'replace':
                try:
                    self.conn.client.table(table_name).delete().neq('id', -999999).execute()
                    logger.info(f"  Truncated existing data")
                except Exception as e:
                    # Table might not have 'id' column, try different approach
                    pass
            
            # Convert to records
            records = df.to_dict('records')
            
            # Clean NaN values
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
            
            # Upload in batches of 1000
            batch_size = 1000
            uploaded = 0
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                try:
                    self.conn.client.table(table_name).insert(batch).execute()
                    uploaded += len(batch)
                except Exception as e:
                    logger.error(f"  Batch {i//batch_size + 1} failed: {e}")
                    self.stats['errors'].append(f"{table_name}: {e}")
                    return False
            
            self.stats['rows_uploaded'] += uploaded
            logger.info(f"✓ {table_name}: {uploaded} rows uploaded")
            return True
            
        except Exception as e:
            logger.error(f"✗ {table_name}: {e}")
            self.stats['errors'].append(f"{table_name}: {e}")
            return False
    
    def upload_tables(self, tables: List[str], mode: str = 'replace',
                      game_filter: Optional[List[int]] = None) -> Dict:
        """Upload multiple tables."""
        logger.info(f"\n{'='*60}")
        logger.info(f"UPLOADING {len(tables)} TABLES (mode={mode})")
        logger.info(f"{'='*60}\n")
        
        for table in tables:
            self.stats['tables_processed'] += 1
            if self.upload_table(table, mode, game_filter):
                self.stats['tables_success'] += 1
            else:
                self.stats['tables_failed'] += 1
        
        return self.stats
    
    def execute_sql_file(self, sql_file: Path) -> bool:
        """Execute a SQL file."""
        if not sql_file.exists():
            logger.error(f"SQL file not found: {sql_file}")
            return False
        
        try:
            with open(sql_file, 'r') as f:
                sql = f.read()
            
            # Split by semicolons and execute each statement
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            
            for i, stmt in enumerate(statements):
                if not stmt:
                    continue
                try:
                    success, msg = self.conn.execute_sql(stmt)
                    if not success:
                        logger.warning(f"  Statement {i+1} warning: {msg}")
                except Exception as e:
                    logger.warning(f"  Statement {i+1} error: {e}")
            
            logger.info(f"✓ Executed {len(statements)} statements from {sql_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"✗ SQL file error: {e}")
            return False
    
    def teardown(self) -> bool:
        """Drop all tables."""
        logger.info("\n⚠️  TEARDOWN: Dropping all tables...")
        sql_file = SQL_DIR / "00_drop_all_tables.sql"
        return self.execute_sql_file(sql_file)
    
    def create_tables(self) -> bool:
        """Create all tables from DDL."""
        logger.info("\n📋 Creating tables from DDL...")
        sql_file = SQL_DIR / "01_create_tables_generated.sql"
        return self.execute_sql_file(sql_file)
    
    def rebuild(self, game_filter: Optional[List[int]] = None) -> Dict:
        """Full rebuild: teardown + create + upload all."""
        logger.info("\n🔄 FULL REBUILD STARTED")
        logger.info("="*60)
        
        # Step 1: Teardown
        self.teardown()
        
        # Step 2: Create tables
        self.create_tables()
        
        # Step 3: Upload all
        all_tables = [t for t in LOAD_ORDER if (OUTPUT_DIR / f"{t}.csv").exists()]
        return self.upload_tables(all_tables, mode='replace', game_filter=game_filter)


# ============================================================================
# VERIFICATION
# ============================================================================

def verify_upload(conn: SupabaseConnection) -> Dict:
    """Verify uploaded data matches local files."""
    logger.info("\n📊 VERIFICATION")
    logger.info("="*60)
    
    results = {}
    
    for table in LOAD_ORDER:
        csv_file = OUTPUT_DIR / f"{table}.csv"
        if not csv_file.exists():
            continue
        
        try:
            local_count = len(pd.read_csv(csv_file))
            remote_count = conn.get_table_count(table)
            
            match = "✓" if local_count == remote_count else "✗"
            results[table] = {
                'local': local_count,
                'remote': remote_count,
                'match': local_count == remote_count
            }
            
            logger.info(f"  {match} {table}: local={local_count}, remote={remote_count}")
            
        except Exception as e:
            logger.warning(f"  ? {table}: verification failed - {e}")
            results[table] = {'error': str(e)}
    
    return results


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='BenchSight Supabase Loader - Flexible data upload tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all                     Upload all tables
  %(prog)s --dims                    Upload only dimension tables  
  %(prog)s --facts                   Upload only fact tables
  %(prog)s --tables dim_player,dim_team  Upload specific tables
  %(prog)s --games 18969,18977       Upload data for specific games only
  %(prog)s --all --mode append       Append instead of replace
  %(prog)s --rebuild                 Drop all, recreate, upload all
  %(prog)s --teardown                Drop all tables
  %(prog)s --create-only             Create tables without uploading data
  %(prog)s --verify                  Verify uploaded data matches local
        """
    )
    
    # What to upload
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true', help='Upload all tables')
    group.add_argument('--dims', action='store_true', help='Upload dimension tables only')
    group.add_argument('--facts', action='store_true', help='Upload fact tables only')
    group.add_argument('--qa', action='store_true', help='Upload QA tables only')
    group.add_argument('--tables', type=str, help='Comma-separated list of tables')
    group.add_argument('--rebuild', action='store_true', help='Full rebuild (drop + create + upload)')
    group.add_argument('--teardown', action='store_true', help='Drop all tables')
    group.add_argument('--create-only', action='store_true', help='Create tables only')
    group.add_argument('--verify', action='store_true', help='Verify upload matches local')
    
    # Options
    parser.add_argument('--mode', choices=['replace', 'append'], default='replace',
                        help='Upload mode: replace (default) or append')
    parser.add_argument('--games', type=str, help='Comma-separated list of game IDs to filter')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without doing it')
    
    args = parser.parse_args()
    
    # Header
    logger.info("="*60)
    logger.info("BENCHSIGHT SUPABASE LOADER")
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log file: {log_file}")
    logger.info("="*60)
    
    # Parse game filter
    game_filter = None
    if args.games:
        game_filter = [int(g.strip()) for g in args.games.split(',')]
        logger.info(f"Game filter: {game_filter}")
    
    # Dry run mode
    if args.dry_run:
        logger.info("\n🔍 DRY RUN MODE - No changes will be made\n")
        if args.all:
            tables = [t for t in LOAD_ORDER if (OUTPUT_DIR / f"{t}.csv").exists()]
        elif args.dims:
            tables = [t for t in DIM_TABLES if (OUTPUT_DIR / f"{t}.csv").exists()]
        elif args.facts:
            tables = [t for t in FACT_TABLES if (OUTPUT_DIR / f"{t}.csv").exists()]
        elif args.qa:
            tables = [t for t in QA_TABLES if (OUTPUT_DIR / f"{t}.csv").exists()]
        elif args.tables:
            tables = [t.strip() for t in args.tables.split(',')]
        else:
            tables = []
        
        logger.info(f"Would upload {len(tables)} tables in {args.mode} mode:")
        for t in tables:
            csv_file = OUTPUT_DIR / f"{t}.csv"
            if csv_file.exists():
                rows = len(pd.read_csv(csv_file))
                logger.info(f"  - {t}: {rows} rows")
        return
    
    # Connect
    conn = SupabaseConnection()
    if not conn.connect():
        logger.error("\n❌ Could not connect to Supabase. Exiting.")
        sys.exit(1)
    
    loader = SupabaseLoader(conn)
    
    # Execute requested operation
    if args.teardown:
        loader.teardown()
        
    elif args.create_only:
        loader.create_tables()
        
    elif args.rebuild:
        stats = loader.rebuild(game_filter)
        verify_upload(conn)
        
    elif args.verify:
        verify_upload(conn)
        
    else:
        # Determine tables to upload
        if args.all:
            tables = [t for t in LOAD_ORDER if (OUTPUT_DIR / f"{t}.csv").exists()]
        elif args.dims:
            tables = [t for t in DIM_TABLES if (OUTPUT_DIR / f"{t}.csv").exists()]
        elif args.facts:
            tables = [t for t in FACT_TABLES if (OUTPUT_DIR / f"{t}.csv").exists()]
        elif args.qa:
            tables = [t for t in QA_TABLES if (OUTPUT_DIR / f"{t}.csv").exists()]
        elif args.tables:
            tables = [t.strip() for t in args.tables.split(',')]
        else:
            logger.info("\nNo action specified. Use --help for options.")
            return
        
        stats = loader.upload_tables(tables, args.mode, game_filter)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("UPLOAD SUMMARY")
        logger.info("="*60)
        logger.info(f"Tables processed: {stats['tables_processed']}")
        logger.info(f"Tables success:   {stats['tables_success']}")
        logger.info(f"Tables failed:    {stats['tables_failed']}")
        logger.info(f"Rows uploaded:    {stats['rows_uploaded']}")
        
        if stats['errors']:
            logger.info("\nErrors:")
            for err in stats['errors']:
                logger.error(f"  - {err}")
        
        # Verify
        verify_upload(conn)
    
    logger.info(f"\n✓ Complete. Log saved to: {log_file}")


if __name__ == '__main__':
    main()
