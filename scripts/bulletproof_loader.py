#!/usr/bin/env python3
"""
BenchSight Bulletproof Data Loader

A robust, production-ready loader for Supabase with:
- Explicit primary key definitions for all 96 tables
- Proper truncate support via RPC
- Comprehensive error handling
- Transaction-like batching
- Detailed logging

Usage:
    python bulletproof_loader.py --load all
    python bulletproof_loader.py --load dims
    python bulletproof_loader.py --load table dim_player
    python bulletproof_loader.py --status
    python bulletproof_loader.py --missing
"""

import os
import sys
import csv
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import configparser

try:
    from supabase import create_client, Client
except ImportError:
    print("ERROR: supabase package not installed. Run: pip install supabase")
    sys.exit(1)

# =============================================================================
# TABLE DEFINITIONS - Primary keys for all 96 tables
# =============================================================================

TABLE_DEFINITIONS = {
    # DIMENSIONS (44 tables)
    "dim_comparison_type": {"pk": "comparison_type_id", "category": "dims"},
    "dim_composite_rating": {"pk": "rating_id", "category": "dims"},
    "dim_danger_zone": {"pk": "danger_zone_id", "category": "dims"},
    "dim_event_detail": {"pk": "event_detail_id", "category": "dims"},
    "dim_event_detail_2": {"pk": "event_detail_2_id", "category": "dims"},
    "dim_event_type": {"pk": "event_type_id", "category": "dims"},
    "dim_giveaway_type": {"pk": "giveaway_type_id", "category": "dims"},
    "dim_league": {"pk": "league_id", "category": "dims"},
    "dim_micro_stat": {"pk": "micro_stat_id", "category": "dims"},
    "dim_net_location": {"pk": "net_location_id", "category": "dims"},
    "dim_pass_type": {"pk": "pass_type_id", "category": "dims"},
    "dim_period": {"pk": "period_id", "category": "dims"},
    "dim_play_detail": {"pk": "play_detail_id", "category": "dims"},
    "dim_play_detail_2": {"pk": "play_detail_2_id", "category": "dims"},
    "dim_player": {"pk": "player_id", "category": "dims"},
    "dim_player_role": {"pk": "player_role_id", "category": "dims"},
    "dim_playerurlref": {"pk": "player_id", "category": "dims"},
    "dim_position": {"pk": "position_id", "category": "dims"},
    "dim_randomnames": {"pk": "id", "category": "dims"},
    "dim_rink_coord": {"pk": "coord_id", "category": "dims"},
    "dim_rinkboxcoord": {"pk": "box_id", "category": "dims"},
    "dim_rinkcoordzones": {"pk": "zone_coord_id", "category": "dims"},
    "dim_schedule": {"pk": "game_id", "category": "dims"},
    "dim_season": {"pk": "season_id", "category": "dims"},
    "dim_shift_slot": {"pk": "shift_slot_id", "category": "dims"},
    "dim_shift_start_type": {"pk": "start_type_id", "category": "dims"},
    "dim_shift_stop_type": {"pk": "stop_type_id", "category": "dims"},
    "dim_shot_type": {"pk": "shot_type_id", "category": "dims"},
    "dim_situation": {"pk": "situation_id", "category": "dims"},
    "dim_stat": {"pk": "stat_id", "category": "dims"},
    "dim_stat_category": {"pk": "stat_category_id", "category": "dims"},
    "dim_stat_type": {"pk": "stat_type_id", "category": "dims"},
    "dim_stoppage_type": {"pk": "stoppage_type_id", "category": "dims"},
    "dim_strength": {"pk": "strength_id", "category": "dims"},
    "dim_success": {"pk": "success_id", "category": "dims"},
    "dim_takeaway_type": {"pk": "takeaway_type_id", "category": "dims"},
    "dim_team": {"pk": "team_id", "category": "dims"},
    "dim_terminology_mapping": {"pk": "mapping_id", "category": "dims"},
    "dim_turnover_quality": {"pk": "turnover_quality_id", "category": "dims"},
    "dim_turnover_type": {"pk": "turnover_type_id", "category": "dims"},
    "dim_venue": {"pk": "venue_id", "category": "dims"},
    "dim_zone": {"pk": "zone_id", "category": "dims"},
    "dim_zone_entry_type": {"pk": "entry_type_id", "category": "dims"},
    "dim_zone_exit_type": {"pk": "exit_type_id", "category": "dims"},
    
    # FACTS - Core (11 tables)
    "fact_events": {"pk": "event_key", "category": "core"},
    "fact_events_long": {"pk": "event_long_key", "category": "core"},
    "fact_events_player": {"pk": "event_player_key", "category": "core"},
    "fact_events_tracking": {"pk": "tracking_key", "category": "core"},
    "fact_shifts": {"pk": "shift_key", "category": "core"},
    "fact_shifts_long": {"pk": "shift_long_key", "category": "core"},
    "fact_shifts_player": {"pk": "shift_player_key", "category": "core"},
    "fact_shifts_tracking": {"pk": "shift_tracking_key", "category": "core"},
    "fact_linked_events": {"pk": "link_key", "category": "core"},
    "fact_event_chains": {"pk": "chain_key", "category": "core"},
    "fact_player_event_chains": {"pk": "player_chain_key", "category": "core"},
    
    # FACTS - Stats (11 tables)
    "fact_player_game_stats": {"pk": "player_game_key", "category": "stats"},
    "fact_team_game_stats": {"pk": "team_game_key", "category": "stats"},
    "fact_goalie_game_stats": {"pk": "goalie_game_key", "category": "stats"},
    "fact_player_period_stats": {"pk": "player_period_key", "category": "stats"},
    "fact_player_stats_long": {"pk": "stat_long_key", "category": "stats"},
    "fact_player_micro_stats": {"pk": "micro_stat_key", "category": "stats"},
    "fact_player_boxscore_all": {"pk": "boxscore_key", "category": "stats"},
    "fact_player_game_position": {"pk": "position_key", "category": "stats"},
    "fact_gameroster": {"pk": "roster_key", "category": "stats"},
    "fact_playergames": {"pk": "playergame_key", "category": "stats"},
    "fact_game_status": {"pk": "game_id", "category": "stats"},
    
    # FACTS - Analytics (9 tables)
    "fact_h2h": {"pk": "h2h_key", "category": "analytics"},
    "fact_wowy": {"pk": "wowy_key", "category": "analytics"},
    "fact_head_to_head": {"pk": "matchup_key", "category": "analytics"},
    "fact_line_combos": {"pk": "combo_key", "category": "analytics"},
    "fact_matchup_summary": {"pk": "summary_key", "category": "analytics"},
    "fact_player_pair_stats": {"pk": "pair_key", "category": "analytics"},
    "fact_shift_quality": {"pk": "quality_key", "category": "analytics"},
    "fact_shift_quality_logical": {"pk": "logical_quality_key", "category": "analytics"},
    "fact_shift_players": {"pk": "shift_players_key", "category": "analytics"},
    
    # FACTS - Zone (7 tables)
    "fact_cycle_events": {"pk": "cycle_key", "category": "zone"},
    "fact_rush_events": {"pk": "rush_key", "category": "zone"},
    "fact_possession_time": {"pk": "possession_key", "category": "zone"},
    "fact_team_zone_time": {"pk": "zone_time_key", "category": "zone"},
    "fact_scoring_chances": {"pk": "chance_key", "category": "zone"},
    "fact_shot_danger": {"pk": "shot_danger_key", "category": "zone"},
    
    # FACTS - Tracking/XY (5 tables)
    "fact_player_xy_long": {"pk": "xy_long_key", "category": "tracking"},
    "fact_player_xy_wide": {"pk": "xy_wide_key", "category": "tracking"},
    "fact_puck_xy_long": {"pk": "puck_xy_key", "category": "tracking"},
    "fact_puck_xy_wide": {"pk": "puck_wide_key", "category": "tracking"},
    "fact_shot_xy": {"pk": "shot_xy_key", "category": "tracking"},
    
    # FACTS - Other (8 tables)
    "fact_plays": {"pk": "play_key", "category": "other"},
    "fact_sequences": {"pk": "sequence_key", "category": "other"},
    "fact_video": {"pk": "video_key", "category": "other"},
    "fact_draft": {"pk": "draft_key", "category": "other"},
    "fact_registration": {"pk": "registration_key", "category": "other"},
    "fact_leadership": {"pk": "leadership_key", "category": "other"},
    "fact_league_leaders_snapshot": {"pk": "leader_key", "category": "other"},
    "fact_team_standings_snapshot": {"pk": "standing_key", "category": "other"},
    "fact_suspicious_stats": {"pk": "suspicious_key", "category": "other"},
    
    # VIDEO HIGHLIGHTS (2 tables) - PENDING IMPLEMENTATION
    "dim_highlight_type": {"pk": "highlight_type_id", "category": "dims"},
    "fact_video_highlights": {"pk": "highlight_key", "category": "other"},
    
    # QA (1 table)
    "qa_suspicious_stats": {"pk": "qa_key", "category": "qa"},
}

# Load order (dims first, then facts)
LOAD_ORDER = [t for t, d in TABLE_DEFINITIONS.items() if d["category"] == "dims"] + \
             [t for t, d in TABLE_DEFINITIONS.items() if d["category"] != "dims"]

# =============================================================================
# LOADER CLASS
# =============================================================================

class BulletproofLoader:
    def __init__(self, data_dir: str = "data/output", config_path: str = "config/config_local.ini"):
        self.data_dir = Path(data_dir)
        self.config_path = Path(config_path)
        self.batch_size = 500
        self.supabase: Optional[Client] = None
        self.log_file = None
        
        self._load_config()
        self._connect()
    
    def _load_config(self):
        """Load Supabase credentials from config file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        config = configparser.ConfigParser()
        config.read(self.config_path)
        
        self.url = config.get('supabase', 'url')
        self.key = config.get('supabase', 'service_key', fallback=config.get('supabase', 'key', fallback=None))
        
        if not self.url or not self.key:
            raise ValueError("Missing supabase url or key in config")
    
    def _connect(self):
        """Connect to Supabase."""
        self.supabase = create_client(self.url, self.key)
        self.log("Connected to Supabase")
    
    def log(self, msg: str):
        """Print timestamped log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {msg}")
    
    def get_csv_path(self, table_name: str) -> Path:
        """Get path to CSV file for a table."""
        return self.data_dir / f"{table_name}.csv"
    
    def read_csv(self, csv_path: Path) -> List[Dict]:
        """Read CSV file and return list of dicts."""
        records = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Clean up values
                clean_row = {}
                for k, v in row.items():
                    if v == '' or v is None:
                        clean_row[k] = None
                    elif v.lower() == 'true':
                        clean_row[k] = True
                    elif v.lower() == 'false':
                        clean_row[k] = False
                    else:
                        # Try to convert to number
                        try:
                            if '.' in v:
                                clean_row[k] = float(v)
                            else:
                                clean_row[k] = int(v)
                        except (ValueError, TypeError):
                            clean_row[k] = v
                records.append(clean_row)
        return records
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for a table in Supabase."""
        try:
            result = self.supabase.table(table_name).select('*', count='exact').limit(0).execute()
            return result.count or 0
        except Exception as e:
            return -1  # Table doesn't exist or error
    
    def truncate_table(self, table_name: str) -> bool:
        """Truncate a table using delete with the actual primary key."""
        if table_name not in TABLE_DEFINITIONS:
            self.log(f"  WARNING: Unknown table {table_name}")
            return False
        
        pk = TABLE_DEFINITIONS[table_name]["pk"]
        
        try:
            # Delete all rows by filtering on PK not being null
            # This is safer than neq with a magic value
            self.supabase.table(table_name).delete().neq(pk, None).execute()
            return True
        except Exception as e:
            # If that fails, try with a magic value approach
            try:
                self.supabase.table(table_name).delete().neq(pk, "___NEVER_MATCH___").execute()
                return True
            except Exception as e2:
                self.log(f"  ERROR truncating {table_name}: {e2}")
                return False
    
    def load_table(self, table_name: str, mode: str = "upsert") -> Dict[str, Any]:
        """
        Load a single table.
        
        Args:
            table_name: Name of table
            mode: "upsert" (safe), "replace" (truncate first), "append" (insert only)
        
        Returns:
            Result dict with success, rows, errors
        """
        result = {"table": table_name, "success": False, "rows": 0, "errors": []}
        
        # Check table definition exists
        if table_name not in TABLE_DEFINITIONS:
            result["errors"].append(f"Unknown table: {table_name}")
            return result
        
        # Check CSV exists
        csv_path = self.get_csv_path(table_name)
        if not csv_path.exists():
            result["errors"].append(f"CSV not found: {csv_path}")
            return result
        
        # Read data
        try:
            records = self.read_csv(csv_path)
        except Exception as e:
            result["errors"].append(f"CSV read error: {e}")
            return result
        
        if not records:
            result["success"] = True
            result["message"] = "No records in CSV"
            return result
        
        # Truncate if replace mode
        if mode == "replace":
            self.log(f"  Truncating {table_name}...")
            self.truncate_table(table_name)
        
        # Load in batches
        pk = TABLE_DEFINITIONS[table_name]["pk"]
        total_loaded = 0
        
        for i in range(0, len(records), self.batch_size):
            batch = records[i:i + self.batch_size]
            try:
                if mode == "upsert" or mode == "replace":
                    # Upsert handles both insert and update
                    self.supabase.table(table_name).upsert(batch, on_conflict=pk).execute()
                else:  # append
                    self.supabase.table(table_name).insert(batch).execute()
                total_loaded += len(batch)
            except Exception as e:
                error_msg = str(e)
                # Check if it's a column mismatch
                if "column" in error_msg.lower() and "does not exist" in error_msg.lower():
                    result["errors"].append(f"Schema mismatch: {error_msg}")
                    break
                else:
                    result["errors"].append(f"Batch {i//self.batch_size + 1}: {error_msg}")
        
        result["success"] = len(result["errors"]) == 0
        result["rows"] = total_loaded
        return result
    
    def load_category(self, category: str, mode: str = "upsert") -> Dict[str, Any]:
        """Load all tables in a category."""
        if category == "all":
            tables = LOAD_ORDER
        elif category == "facts":
            tables = [t for t, d in TABLE_DEFINITIONS.items() if d["category"] != "dims"]
        else:
            tables = [t for t, d in TABLE_DEFINITIONS.items() if d["category"] == category]
        
        results = {"total_tables": len(tables), "loaded": 0, "failed": 0, "details": []}
        
        for table in tables:
            self.log(f"Loading {table}...")
            result = self.load_table(table, mode)
            results["details"].append(result)
            
            if result["success"]:
                results["loaded"] += 1
                self.log(f"  ✓ {result['rows']} rows")
            else:
                results["failed"] += 1
                self.log(f"  ✗ FAILED: {result['errors']}")
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all tables in Supabase."""
        status = {"tables": {}, "summary": {"total": 0, "populated": 0, "empty": 0, "missing": 0}}
        
        for table in LOAD_ORDER:
            count = self.get_table_count(table)
            csv_path = self.get_csv_path(table)
            csv_rows = len(self.read_csv(csv_path)) if csv_path.exists() else 0
            
            status["tables"][table] = {
                "supabase_rows": count,
                "csv_rows": csv_rows,
                "status": "OK" if count == csv_rows else ("MISSING" if count < 0 else "MISMATCH")
            }
            
            status["summary"]["total"] += 1
            if count < 0:
                status["summary"]["missing"] += 1
            elif count == 0:
                status["summary"]["empty"] += 1
            else:
                status["summary"]["populated"] += 1
        
        return status
    
    def get_missing_tables(self) -> List[str]:
        """Get list of tables that are empty or missing in Supabase."""
        missing = []
        for table in LOAD_ORDER:
            count = self.get_table_count(table)
            if count <= 0:
                missing.append(table)
        return missing
    
    def load_missing(self, mode: str = "upsert") -> Dict[str, Any]:
        """Load only tables that are empty or missing."""
        missing = self.get_missing_tables()
        self.log(f"Found {len(missing)} empty/missing tables")
        
        results = {"total": len(missing), "loaded": 0, "failed": 0, "details": []}
        
        for table in missing:
            self.log(f"Loading {table}...")
            result = self.load_table(table, mode)
            results["details"].append(result)
            
            if result["success"]:
                results["loaded"] += 1
                self.log(f"  ✓ {result['rows']} rows")
            else:
                results["failed"] += 1
                self.log(f"  ✗ FAILED: {result['errors']}")
        
        return results


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="BenchSight Bulletproof Loader")
    parser.add_argument("--load", choices=["all", "dims", "facts", "core", "stats", "analytics", "zone", "tracking", "other", "qa", "missing"],
                        help="Load tables by category")
    parser.add_argument("--table", type=str, help="Load a specific table")
    parser.add_argument("--mode", choices=["upsert", "replace", "append"], default="upsert",
                        help="Load mode: upsert (default), replace, append")
    parser.add_argument("--status", action="store_true", help="Show status of all tables")
    parser.add_argument("--missing", action="store_true", help="List empty/missing tables")
    parser.add_argument("--data-dir", type=str, default="data/output", help="Data directory")
    parser.add_argument("--config", type=str, default="config/config_local.ini", help="Config file path")
    
    args = parser.parse_args()
    
    try:
        loader = BulletproofLoader(data_dir=args.data_dir, config_path=args.config)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    if args.status:
        status = loader.get_status()
        print("\n" + "=" * 70)
        print("TABLE STATUS")
        print("=" * 70)
        print(f"\nSummary: {status['summary']['populated']} populated, {status['summary']['empty']} empty, {status['summary']['missing']} missing")
        print("\nDetails:")
        for table, info in status["tables"].items():
            status_icon = "✓" if info["status"] == "OK" else "✗"
            print(f"  {status_icon} {table}: {info['supabase_rows']}/{info['csv_rows']} rows [{info['status']}]")
    
    elif args.missing:
        missing = loader.get_missing_tables()
        print(f"\nEmpty/Missing Tables ({len(missing)}):")
        for table in missing:
            print(f"  - {table}")
        print(f"\nTo load these: python bulletproof_loader.py --load missing")
    
    elif args.table:
        result = loader.load_table(args.table, args.mode)
        print(f"\nResult: {'SUCCESS' if result['success'] else 'FAILED'}")
        print(f"Rows loaded: {result['rows']}")
        if result.get("errors"):
            print(f"Errors: {result['errors']}")
    
    elif args.load:
        if args.load == "missing":
            results = loader.load_missing(args.mode)
        else:
            results = loader.load_category(args.load, args.mode)
        
        print("\n" + "=" * 70)
        print("LOAD COMPLETE")
        print("=" * 70)
        print(f"Tables: {results.get('loaded', 0)}/{results.get('total_tables', results.get('total', 0))} successful")
        if results.get("failed", 0) > 0:
            print(f"Failed: {results['failed']}")
            for detail in results.get("details", []):
                if not detail["success"]:
                    print(f"  - {detail['table']}: {detail['errors']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
