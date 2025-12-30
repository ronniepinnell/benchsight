#!/usr/bin/env python3
"""
BenchSight Flexible Data Loader

CLI tool and library for loading data into Supabase with various
scopes (game, table, category) and operations (replace, append, upsert).

Usage:
    python flexible_loader.py --scope game --game-id 18969 --operation replace
    python flexible_loader.py --scope category --category dims --operation upsert
    python flexible_loader.py --scope table --table fact_events --operation append
    python flexible_loader.py --scope full --operation replace

Environment:
    SUPABASE_URL: Your Supabase project URL
    SUPABASE_SERVICE_KEY: Service role key (not anon key)
"""

import os
import sys
import csv
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

try:
    from supabase import create_client, Client
except ImportError:
    print("Please install supabase: pip install supabase")
    sys.exit(1)

# Try to load from config file
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config.config_loader import load_config
    _cfg = load_config()
    DATA_DIR = _cfg.data_dir
    SUPABASE_URL = _cfg.supabase_url
    SUPABASE_KEY = _cfg.supabase_service_key
except ImportError:
    # Fallback to defaults/environment
    DATA_DIR = Path(__file__).parent.parent / "data" / "output"
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Table definitions - ALL 96 TABLES
TABLE_CATEGORIES = {
    "dims": [
        "dim_comparison_type", "dim_composite_rating", "dim_danger_zone", "dim_event_detail",
        "dim_event_detail_2", "dim_event_type", "dim_giveaway_type", "dim_league",
        "dim_micro_stat", "dim_net_location", "dim_pass_type", "dim_period",
        "dim_play_detail", "dim_play_detail_2", "dim_player", "dim_player_role",
        "dim_playerurlref", "dim_position", "dim_randomnames", "dim_rink_coord",
        "dim_rinkboxcoord", "dim_rinkcoordzones", "dim_schedule", "dim_season",
        "dim_shift_slot", "dim_shift_start_type", "dim_shift_stop_type", "dim_shot_type",
        "dim_situation", "dim_stat", "dim_stat_category", "dim_stat_type",
        "dim_stoppage_type", "dim_strength", "dim_success", "dim_takeaway_type",
        "dim_team", "dim_terminology_mapping", "dim_turnover_quality", "dim_turnover_type",
        "dim_venue", "dim_zone", "dim_zone_entry_type", "dim_zone_exit_type",
    ],
    "core_facts": [
        "fact_shifts", "fact_events", "fact_events_player", "fact_shifts_player",
        "fact_events_long", "fact_shifts_long", "fact_events_tracking", "fact_shifts_tracking",
        "fact_linked_events", "fact_event_chains", "fact_player_event_chains",
    ],
    "stats_facts": [
        "fact_player_game_stats", "fact_team_game_stats", "fact_goalie_game_stats",
        "fact_player_period_stats", "fact_player_stats_long", "fact_player_micro_stats",
        "fact_player_boxscore_all", "fact_player_game_position", "fact_gameroster",
        "fact_playergames", "fact_game_status",
    ],
    "analytics_facts": [
        "fact_h2h", "fact_wowy", "fact_head_to_head", "fact_line_combos",
        "fact_matchup_summary", "fact_player_pair_stats", "fact_shift_quality",
        "fact_shift_quality_logical", "fact_shift_players",
    ],
    "zone_facts": [
        "fact_cycle_events", "fact_rush_events", "fact_possession_time",
        "fact_team_zone_time", "fact_scoring_chances", "fact_shot_danger",
    ],
    "tracking_facts": [
        "fact_player_xy_long", "fact_player_xy_wide", "fact_puck_xy_long",
        "fact_puck_xy_wide", "fact_shot_xy",
    ],
    "other_facts": [
        "fact_plays", "fact_sequences", "fact_video", "fact_draft",
        "fact_registration", "fact_leadership", "fact_league_leaders_snapshot",
        "fact_team_standings_snapshot", "fact_suspicious_stats",
    ],
    "qa": [
        "qa_suspicious_stats",
    ],
}

# Load order (respects FK dependencies)
LOAD_ORDER = [
    # Dimensions first (44 tables) - no dependencies
    "dim_comparison_type", "dim_composite_rating", "dim_danger_zone", "dim_event_detail",
    "dim_event_detail_2", "dim_event_type", "dim_giveaway_type", "dim_league",
    "dim_micro_stat", "dim_net_location", "dim_pass_type", "dim_period",
    "dim_play_detail", "dim_play_detail_2", "dim_player", "dim_player_role",
    "dim_playerurlref", "dim_position", "dim_randomnames", "dim_rink_coord",
    "dim_rinkboxcoord", "dim_rinkcoordzones", "dim_schedule", "dim_season",
    "dim_shift_slot", "dim_shift_start_type", "dim_shift_stop_type", "dim_shot_type",
    "dim_situation", "dim_stat", "dim_stat_category", "dim_stat_type",
    "dim_stoppage_type", "dim_strength", "dim_success", "dim_takeaway_type",
    "dim_team", "dim_terminology_mapping", "dim_turnover_quality", "dim_turnover_type",
    "dim_venue", "dim_zone", "dim_zone_entry_type", "dim_zone_exit_type",
    # Core facts - shifts and events
    "fact_shifts", "fact_events", "fact_events_player", "fact_shifts_player",
    "fact_events_long", "fact_shifts_long", "fact_events_tracking", "fact_shifts_tracking",
    "fact_linked_events", "fact_event_chains", "fact_player_event_chains",
    # Stats facts
    "fact_player_game_stats", "fact_team_game_stats", "fact_goalie_game_stats",
    "fact_player_period_stats", "fact_player_stats_long", "fact_player_micro_stats",
    "fact_player_boxscore_all", "fact_player_game_position", "fact_gameroster",
    "fact_playergames", "fact_game_status",
    # Analytics facts
    "fact_h2h", "fact_wowy", "fact_head_to_head", "fact_line_combos",
    "fact_matchup_summary", "fact_player_pair_stats", "fact_shift_quality",
    "fact_shift_quality_logical", "fact_shift_players",
    # Zone/possession facts
    "fact_cycle_events", "fact_rush_events", "fact_possession_time",
    "fact_team_zone_time", "fact_scoring_chances", "fact_shot_danger",
    # Tracking/XY facts
    "fact_player_xy_long", "fact_player_xy_wide", "fact_puck_xy_long",
    "fact_puck_xy_wide", "fact_shot_xy",
    # Other facts
    "fact_plays", "fact_sequences", "fact_video", "fact_draft",
    "fact_registration", "fact_leadership", "fact_league_leaders_snapshot",
    "fact_team_standings_snapshot", "fact_suspicious_stats",
    # QA tables
    "qa_suspicious_stats",
]

# Delete order (reverse of load order)
DELETE_ORDER = list(reversed(LOAD_ORDER))


class BenchSightLoader:
    """Flexible data loader for BenchSight Supabase database."""
    
    def __init__(self, url: str = SUPABASE_URL, key: str = SUPABASE_KEY):
        if not key:
            raise ValueError("SUPABASE_SERVICE_KEY environment variable not set")
        self.supabase: Client = create_client(url, key)
        self.data_dir = DATA_DIR
        self.batch_size = 500
        self.verbose = True
    
    def log(self, message: str):
        """Print log message if verbose mode is on."""
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def read_csv(self, filepath: Path) -> List[Dict[str, Any]]:
        """Read CSV file and return list of dictionaries."""
        records = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Clean up values
                cleaned = {}
                for k, v in row.items():
                    if v == '' or v == 'nan' or v == 'NaN':
                        cleaned[k] = None
                    elif v.lower() == 'true':
                        cleaned[k] = True
                    elif v.lower() == 'false':
                        cleaned[k] = False
                    else:
                        # Try to convert to number
                        try:
                            if '.' in v:
                                cleaned[k] = float(v)
                            else:
                                cleaned[k] = int(v)
                        except (ValueError, TypeError):
                            cleaned[k] = v
                records.append(cleaned)
        return records
    
    def get_csv_path(self, table_name: str) -> Path:
        """Get the CSV file path for a table."""
        return self.data_dir / f"{table_name}.csv"
    
    def delete_table_data(self, table_name: str, game_id: Optional[int] = None) -> int:
        """Delete data from a table, optionally for a specific game."""
        if game_id:
            result = self.supabase.table(table_name).delete().eq('game_id', game_id).execute()
        else:
            # Get the first column (primary key) from CSV to use for delete filter
            csv_path = self.data_dir / f"{table_name}.csv"
            if csv_path.exists():
                import csv
                with open(csv_path, 'r') as f:
                    reader = csv.reader(f)
                    first_col = next(reader)[0]
                # Delete all by filtering on first column not being an impossible value
                result = self.supabase.table(table_name).delete().neq(first_col, '___IMPOSSIBLE_VALUE___').execute()
            else:
                # Fallback: try common primary key patterns
                for pk_col in [f'{table_name}_key', f'{table_name.replace("fact_", "").replace("dim_", "")}_id', 'id']:
                    try:
                        result = self.supabase.table(table_name).delete().neq(pk_col, '___IMPOSSIBLE___').execute()
                        break
                    except:
                        continue
                else:
                    result = type('obj', (object,), {'data': []})()
        return len(result.data) if result.data else 0
    
    def delete_game_data(self, game_id: int) -> Dict[str, int]:
        """Delete all data for a specific game across all tables."""
        self.log(f"Deleting game {game_id} from all tables...")
        results = {}
        for table in DELETE_ORDER:
            if table.startswith('dim_'):
                continue  # Don't delete dimensions
            try:
                count = self.delete_table_data(table, game_id)
                results[table] = count
                self.log(f"  {table}: {count} rows deleted")
            except Exception as e:
                results[table] = f"ERROR: {str(e)}"
        return results
    
    def load_table(
        self, 
        table_name: str, 
        operation: str = 'upsert',
        game_id: Optional[int] = None,
        records: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Load data into a single table.
        
        Args:
            table_name: Name of the table to load
            operation: 'replace', 'append', or 'upsert'
            game_id: If specified, only load/replace data for this game
            records: If provided, use these records instead of CSV
        """
        start_time = datetime.now()
        
        # Get records from CSV if not provided
        if records is None:
            csv_path = self.get_csv_path(table_name)
            if not csv_path.exists():
                return {'success': False, 'error': f'CSV not found: {csv_path}'}
            records = self.read_csv(csv_path)
        
        # Filter by game_id if specified
        if game_id and 'game_id' in (records[0] if records else {}):
            records = [r for r in records if r.get('game_id') == game_id]
        
        if not records:
            return {
                'success': True, 
                'table': table_name, 
                'rows': 0, 
                'message': 'No records to load'
            }
        
        # Handle operation
        if operation == 'replace':
            if game_id:
                self.delete_table_data(table_name, game_id)
            else:
                self.delete_table_data(table_name)
            operation = 'append'  # After delete, we append
        
        # Load in batches
        total_loaded = 0
        errors = []
        
        for i in range(0, len(records), self.batch_size):
            batch = records[i:i + self.batch_size]
            try:
                if operation == 'upsert':
                    self.supabase.table(table_name).upsert(batch).execute()
                else:  # append
                    self.supabase.table(table_name).insert(batch).execute()
                total_loaded += len(batch)
            except Exception as e:
                errors.append(f"Batch {i//self.batch_size}: {str(e)}")
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': len(errors) == 0,
            'table': table_name,
            'rows': total_loaded,
            'duration_seconds': duration,
            'errors': errors if errors else None
        }
    
    def load_category(
        self, 
        category: str, 
        operation: str = 'upsert',
        game_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Load all tables in a category.
        
        Args:
            category: 'dims', 'core_facts', 'stats_facts', 'analytics_facts', 'all_facts', 'all'
            operation: 'replace', 'append', or 'upsert'
            game_id: If specified, only load/replace data for this game
        """
        if category == 'all':
            tables = LOAD_ORDER
        elif category == 'all_facts':
            tables = [t for t in LOAD_ORDER if t.startswith('fact_')]
        elif category in TABLE_CATEGORIES:
            tables = TABLE_CATEGORIES[category]
        else:
            return {'success': False, 'error': f'Invalid category: {category}'}
        
        self.log(f"Loading category '{category}' ({len(tables)} tables)...")
        
        results = {}
        for table in tables:
            if table in LOAD_ORDER:  # Respect load order
                self.log(f"  Loading {table}...")
                result = self.load_table(table, operation, game_id)
                results[table] = result
                if result.get('success'):
                    self.log(f"    ✓ {result.get('rows', 0)} rows")
                else:
                    self.log(f"    ✗ Error: {result.get('error', result.get('errors', 'Unknown'))}")
        
        success = all(r.get('success', False) for r in results.values())
        total_rows = sum(r.get('rows', 0) for r in results.values())
        
        return {
            'success': success,
            'category': category,
            'tables_loaded': len(results),
            'total_rows': total_rows,
            'results': results
        }
    
    def load_game(
        self, 
        game_id: int, 
        operation: str = 'replace',
        include_dims: bool = False
    ) -> Dict[str, Any]:
        """
        Load all data for a specific game.
        
        Args:
            game_id: The game ID to load
            operation: 'replace' or 'append'
            include_dims: If True, also reload dimension tables
        """
        self.log(f"Loading game {game_id}...")
        
        if operation == 'replace':
            self.delete_game_data(game_id)
        
        category = 'all' if include_dims else 'all_facts'
        return self.load_category(category, 'append', game_id)
    
    def full_refresh(self) -> Dict[str, Any]:
        """
        Complete refresh of all data.
        Drops all data and reloads from CSVs.
        """
        self.log("Starting full refresh...")
        
        # Delete in reverse order
        for table in DELETE_ORDER:
            self.log(f"  Clearing {table}...")
            self.delete_table_data(table)
        
        # Load in forward order
        return self.load_category('all', 'append')
    
    def get_table_counts(self) -> Dict[str, int]:
        """Get row counts for all tables."""
        counts = {}
        for table in LOAD_ORDER:
            try:
                result = self.supabase.table(table).select('*', count='exact').limit(0).execute()
                counts[table] = result.count
            except Exception as e:
                counts[table] = f"ERROR: {str(e)}"
        return counts
    
    def validate_fks(self, table_name: str) -> Dict[str, Any]:
        """Validate foreign key relationships for a table."""
        # This would check for orphaned records
        # Implementation depends on specific FK relationships
        pass


def main():
    parser = argparse.ArgumentParser(description='BenchSight Flexible Data Loader')
    parser.add_argument('--scope', choices=['table', 'category', 'game', 'full'], required=True,
                        help='Scope of the load operation')
    parser.add_argument('--table', help='Table name (for scope=table)')
    parser.add_argument('--category', choices=['dims', 'core_facts', 'stats_facts', 'analytics_facts', 'zone_facts', 'tracking_facts', 'other_facts', 'qa', 'all_facts', 'all'],
                        help='Category name (for scope=category)')
    parser.add_argument('--game-id', type=int, help='Game ID (for scope=game or to filter other scopes)')
    parser.add_argument('--operation', choices=['replace', 'append', 'upsert'], default='upsert',
                        help='Load operation type')
    parser.add_argument('--data-dir', type=Path, help='Override data directory')
    parser.add_argument('--quiet', action='store_true', help='Suppress output')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--counts', action='store_true', help='Just show table row counts')
    
    args = parser.parse_args()
    
    # Initialize loader
    try:
        loader = BenchSightLoader()
        loader.verbose = not args.quiet
        if args.data_dir:
            loader.data_dir = args.data_dir
    except ValueError as e:
        print(f"Error: {e}")
        print("Set SUPABASE_SERVICE_KEY environment variable")
        sys.exit(1)
    
    # Just show counts
    if args.counts:
        counts = loader.get_table_counts()
        print("\nTable Row Counts:")
        print("-" * 40)
        for table, count in counts.items():
            print(f"  {table}: {count}")
        print("-" * 40)
        print(f"  TOTAL: {sum(c for c in counts.values() if isinstance(c, int))}")
        sys.exit(0)
    
    # Dry run
    if args.dry_run:
        print(f"\nDRY RUN - Would execute:")
        print(f"  Scope: {args.scope}")
        print(f"  Operation: {args.operation}")
        if args.table:
            print(f"  Table: {args.table}")
        if args.category:
            print(f"  Category: {args.category}")
        if args.game_id:
            print(f"  Game ID: {args.game_id}")
        sys.exit(0)
    
    # Execute based on scope
    if args.scope == 'full':
        if args.operation == 'replace':
            # Full replace: delete all then load
            result = loader.full_refresh()
        else:
            # Append or upsert: just load all tables without deleting
            result = loader.load_category('all', args.operation)
    elif args.scope == 'game':
        if not args.game_id:
            print("Error: --game-id required for scope=game")
            sys.exit(1)
        result = loader.load_game(args.game_id, args.operation)
    elif args.scope == 'category':
        if not args.category:
            print("Error: --category required for scope=category")
            sys.exit(1)
        result = loader.load_category(args.category, args.operation, args.game_id)
    elif args.scope == 'table':
        if not args.table:
            print("Error: --table required for scope=table")
            sys.exit(1)
        result = loader.load_table(args.table, args.operation, args.game_id)
    
    # Print result
    print("\n" + "=" * 60)
    print("RESULT:")
    print(json.dumps(result, indent=2, default=str))
    
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
