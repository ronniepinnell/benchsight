#!/usr/bin/env python3
"""
BenchSight Tracker API

Backend module for the game tracker to read/write tracking data to Supabase.
Handles events, shifts, player XY, puck XY, and ETL triggers.

Usage:
    # As CLI
    python tracker_api.py --action list-games
    python tracker_api.py --action get-game --game-id 18969
    python tracker_api.py --action save-tracking --game-id 18969 --file tracking.json
    python tracker_api.py --action run-etl --game-id 18969
    
    # As library
    from tracker_api import TrackerAPI
    api = TrackerAPI()
    games = api.list_games()
    api.save_events(game_id, events)

Author: BenchSight
"""

import os
import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

# Add parent to path for config
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from supabase import create_client, Client
except ImportError:
    print("Please install supabase: pip install supabase --break-system-packages")
    sys.exit(1)

# Load config
try:
    from config.config_loader import load_config
    _cfg = load_config()
    SUPABASE_URL = _cfg.supabase_url
    SUPABASE_KEY = _cfg.supabase_service_key
    DATA_DIR = _cfg.data_dir
except ImportError:
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://uuaowslhpgyiudmbvqze.supabase.co")
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
    DATA_DIR = Path(__file__).parent.parent / "data" / "output"


class TrackerAPI:
    """API for tracker read/write operations."""
    
    def __init__(self, url: str = None, key: str = None):
        self.url = url or SUPABASE_URL
        self.key = key or SUPABASE_KEY
        self.client: Client = create_client(self.url, self.key)
        
    # =========================================================================
    # READ OPERATIONS
    # =========================================================================
    
    def list_games(self, limit: int = 100) -> List[Dict]:
        """List available games from schedule."""
        result = self.client.table('dim_schedule').select(
            'game_id, game_date_str, home_team_name, away_team_name, home_team_id, away_team_id, game_status'
        ).order('game_date_str', desc=True).limit(limit).execute()
        return result.data
    
    def get_game(self, game_id: str) -> Dict:
        """Get game details including roster, videos, and existing tracking data."""
        game_info = self.client.table('dim_schedule').select('*').eq('game_id', game_id).execute()
        if not game_info.data:
            raise ValueError(f"Game {game_id} not found")
        
        # Get roster
        roster = self.client.table('fact_gameroster').select(
            'player_id, player_game_number, team_venue, team_name, player_position'
        ).eq('game_id', game_id).execute()
        
        # Get videos
        videos = self.client.table('fact_video').select('*').eq('game_id', game_id).execute()
        
        # Get existing events
        events = self.client.table('fact_events').select('*').eq('game_id', game_id).order('event_index').execute()
        
        # Get event players
        events_player = self.client.table('fact_events_player').select('*').eq('game_id', game_id).execute()
        
        # Get shifts
        shifts = self.client.table('fact_shifts').select('*').eq('game_id', game_id).order('shift_index').execute()
        
        # Get puck XY data
        puck_xy = self.client.table('fact_puck_xy_long').select('*').eq('game_id', game_id).execute()
        
        # Get player XY data
        player_xy = self.client.table('fact_player_xy_long').select('*').eq('game_id', game_id).execute()
        
        # Get shot XY data
        shot_xy = self.client.table('fact_shot_xy').select('*').eq('game_id', game_id).execute()
        
        return {
            'game': game_info.data[0],
            'roster': roster.data,
            'videos': videos.data,
            'events': events.data,
            'events_player': events_player.data,
            'shifts': shifts.data,
            'puck_xy': puck_xy.data,
            'player_xy': player_xy.data,
            'shot_xy': shot_xy.data
        }
    
    def get_players(self) -> List[Dict]:
        """Get all players."""
        result = self.client.table('dim_player').select(
            'player_id, player_full_name, player_first_name, player_last_name, player_primary_position, current_skill_rating'
        ).execute()
        return result.data
    
    def get_play_details(self) -> Tuple[List[Dict], List[Dict]]:
        """Get play detail dimension tables."""
        pd1 = self.client.table('dim_play_detail').select('*').execute()
        pd2 = self.client.table('dim_play_detail_2').select('*').execute()
        return pd1.data, pd2.data
    
    def get_event_types(self) -> List[Dict]:
        """Get event type definitions."""
        result = self.client.table('dim_event_type').select('*').execute()
        return result.data
    
    # =========================================================================
    # WRITE OPERATIONS
    # =========================================================================
    
    def save_events(self, game_id: str, events: List[Dict], replace: bool = False) -> int:
        """
        Save events to fact_events and fact_events_player tables.
        
        Args:
            game_id: Game ID
            events: List of event dictionaries from tracker
            replace: If True, delete existing events first
            
        Returns:
            Number of events saved
        """
        if replace:
            # Delete existing
            self.client.table('fact_events_player').delete().eq('game_id', game_id).execute()
            self.client.table('fact_events').delete().eq('game_id', game_id).execute()
        
        # Group events by event_index to get unique events
        unique_events = {}
        event_players = []
        
        for e in events:
            idx = e.get('event_index')
            if idx not in unique_events:
                # First row for this event - primary event data
                unique_events[idx] = {
                    'event_key': f"EVT_{game_id}_{idx}",
                    'game_id': game_id,
                    'event_index': idx,
                    'period': e.get('period'),
                    'event_start_min': e.get('event_start_min_'),
                    'event_start_sec': e.get('event_start_sec_'),
                    'event_end_min': e.get('event_end_min_'),
                    'event_end_sec': e.get('event_end_sec_'),
                    'event_type': e.get('event_type_'),
                    'event_detail': e.get('event_detail_'),
                    'event_detail_2': e.get('event_detail_2_'),
                    'event_successful': e.get('event_successful_'),
                    'play_detail1': e.get('play_detail1_'),
                    'play_detail2': e.get('play_detail2_'),
                    'play_detail_successful': e.get('play_detail_successful_'),
                    'pressured_pressurer': e.get('pressured_pressurer_'),
                    'zone': e.get('event_team_zone_'),
                    'team_venue': e.get('team_venue_'),
                    'linked_event_index': e.get('linked_event_index_') or None,
                    'running_video_time': e.get('running_video_time'),
                    'shift_index': e.get('shift_index'),
                    'x_coord': e.get('xy_x') or None,
                    'y_coord': e.get('xy_y') or None,
                    'net_location': e.get('net_location') or None
                }
            
            # Add player row
            if e.get('player_game_number_'):
                event_players.append({
                    'event_player_key': f"EP_{game_id}_{idx}_{e.get('role_number', 1)}",
                    'event_key': f"EVT_{game_id}_{idx}",
                    'game_id': game_id,
                    'event_index': idx,
                    'player_id': e.get('player_id'),
                    'player_game_number': e.get('player_game_number_'),
                    'player_role': e.get('player_role'),
                    'role_number': e.get('role_number'),
                    'team_venue': e.get('team_venue_')
                })
        
        # Insert events
        if unique_events:
            event_list = list(unique_events.values())
            self.client.table('fact_events').upsert(event_list).execute()
        
        # Insert event players
        if event_players:
            self.client.table('fact_events_player').upsert(event_players).execute()
        
        return len(unique_events)
    
    def save_shifts(self, game_id: str, shifts: List[Dict], replace: bool = False) -> int:
        """Save shifts to fact_shifts table."""
        if replace:
            self.client.table('fact_shifts').delete().eq('game_id', game_id).execute()
        
        shift_rows = []
        for s in shifts:
            shift_rows.append({
                'shift_key': f"SHF_{game_id}_{s.get('shift_index')}",
                'game_id': game_id,
                'shift_index': s.get('shift_index'),
                'period': s.get('Period'),
                'shift_start_min': s.get('shift_start_min'),
                'shift_start_sec': s.get('shift_start_sec'),
                'shift_end_min': s.get('shift_end_min'),
                'shift_end_sec': s.get('shift_end_sec'),
                'shift_start_type': s.get('shift_start_type'),
                'shift_stop_type': s.get('shift_stop_type'),
                'home_forward_1': s.get('home_forward_1'),
                'home_forward_2': s.get('home_forward_2'),
                'home_forward_3': s.get('home_forward_3'),
                'home_defense_1': s.get('home_defense_1'),
                'home_defense_2': s.get('home_defense_2'),
                'home_goalie': s.get('home_goalie'),
                'away_forward_1': s.get('away_forward_1'),
                'away_forward_2': s.get('away_forward_2'),
                'away_forward_3': s.get('away_forward_3'),
                'away_defense_1': s.get('away_defense_1'),
                'away_defense_2': s.get('away_defense_2'),
                'away_goalie': s.get('away_goalie')
            })
        
        if shift_rows:
            self.client.table('fact_shifts').upsert(shift_rows).execute()
        
        return len(shift_rows)
    
    def save_puck_xy(self, game_id: str, puck_xy_data: List[Dict], replace: bool = False) -> int:
        """
        Save puck XY tracking data (10 points per event).
        
        Args:
            game_id: Game ID
            puck_xy_data: List of {event_index, points: [{x, y, z, timestamp}]}
            replace: If True, delete existing data first
        """
        if replace:
            self.client.table('fact_puck_xy_long').delete().eq('game_id', game_id).execute()
            self.client.table('fact_puck_xy_wide').delete().eq('game_id', game_id).execute()
        
        long_rows = []
        wide_rows = []
        
        for evt in puck_xy_data:
            event_index = evt.get('event_index')
            points = evt.get('points', [])
            
            # Long format - one row per point
            for i, pt in enumerate(points[:10]):
                long_rows.append({
                    'puck_xy_key': f"PXY_{game_id}_{event_index}_{i+1}",
                    'game_id': game_id,
                    'event_index': event_index,
                    'event_key': f"EVT_{game_id}_{event_index}",
                    'point_number': i + 1,
                    'x': pt.get('x'),
                    'y': pt.get('y'),
                    'z': pt.get('z', 0),
                    'event_timestamp': pt.get('timestamp')
                })
            
            # Wide format - one row per event with columns x_1..x_10
            wide_row = {
                'puck_xy_key': f"PXYW_{game_id}_{event_index}",
                'game_id': game_id,
                'event_index': event_index,
                'event_key': f"EVT_{game_id}_{event_index}",
                'point_count': len(points)
            }
            for i in range(10):
                if i < len(points):
                    wide_row[f'x_{i+1}'] = points[i].get('x')
                    wide_row[f'y_{i+1}'] = points[i].get('y')
                    wide_row[f'z_{i+1}'] = points[i].get('z', 0)
                    wide_row[f'timestamp_{i+1}'] = points[i].get('timestamp')
                else:
                    wide_row[f'x_{i+1}'] = None
                    wide_row[f'y_{i+1}'] = None
                    wide_row[f'z_{i+1}'] = None
                    wide_row[f'timestamp_{i+1}'] = None
            wide_rows.append(wide_row)
        
        if long_rows:
            self.client.table('fact_puck_xy_long').upsert(long_rows).execute()
        if wide_rows:
            self.client.table('fact_puck_xy_wide').upsert(wide_rows).execute()
        
        return len(wide_rows)
    
    def save_player_xy(self, game_id: str, player_xy_data: List[Dict], replace: bool = False) -> int:
        """
        Save player XY tracking data (10 points per player per event).
        
        Args:
            game_id: Game ID  
            player_xy_data: List of {event_index, player_id, team_venue, points: [{x, y, timestamp}]}
        """
        if replace:
            self.client.table('fact_player_xy_long').delete().eq('game_id', game_id).execute()
            self.client.table('fact_player_xy_wide').delete().eq('game_id', game_id).execute()
        
        long_rows = []
        wide_rows = []
        
        for entry in player_xy_data:
            event_index = entry.get('event_index')
            player_id = entry.get('player_id')
            team_venue = entry.get('team_venue')
            points = entry.get('points', [])
            
            # Long format
            for i, pt in enumerate(points[:10]):
                long_rows.append({
                    'player_xy_key': f"PLXY_{game_id}_{event_index}_{player_id}_{i+1}",
                    'game_id': game_id,
                    'event_index': event_index,
                    'event_key': f"EVT_{game_id}_{event_index}",
                    'player_id': player_id,
                    'team_venue': team_venue,
                    'point_number': i + 1,
                    'x': pt.get('x'),
                    'y': pt.get('y'),
                    'event_timestamp': pt.get('timestamp')
                })
            
            # Wide format
            wide_row = {
                'player_xy_key': f"PLXYW_{game_id}_{event_index}_{player_id}",
                'game_id': game_id,
                'event_index': event_index,
                'event_key': f"EVT_{game_id}_{event_index}",
                'player_id': player_id,
                'team_venue': team_venue,
                'point_count': len(points)
            }
            for i in range(10):
                if i < len(points):
                    wide_row[f'x_{i+1}'] = points[i].get('x')
                    wide_row[f'y_{i+1}'] = points[i].get('y')
                    wide_row[f'timestamp_{i+1}'] = points[i].get('timestamp')
                else:
                    wide_row[f'x_{i+1}'] = None
                    wide_row[f'y_{i+1}'] = None
                    wide_row[f'timestamp_{i+1}'] = None
            wide_rows.append(wide_row)
        
        if long_rows:
            self.client.table('fact_player_xy_long').upsert(long_rows).execute()
        if wide_rows:
            self.client.table('fact_player_xy_wide').upsert(wide_rows).execute()
        
        return len(wide_rows)
    
    def save_shot_xy(self, game_id: str, shot_data: List[Dict], replace: bool = False) -> int:
        """Save shot XY data including net location."""
        if replace:
            self.client.table('fact_shot_xy').delete().eq('game_id', game_id).execute()
        
        shot_rows = []
        for s in shot_data:
            shot_rows.append({
                'shot_xy_key': f"SHOTXY_{game_id}_{s.get('event_index')}",
                'game_id': game_id,
                'event_index': s.get('event_index'),
                'event_key': f"EVT_{game_id}_{s.get('event_index')}",
                'player_id': s.get('player_id'),
                'team_venue': s.get('team_venue'),
                'period': s.get('period'),
                'shot_x': s.get('shot_x'),
                'shot_y': s.get('shot_y'),
                'target_x': s.get('target_x'),
                'target_y': s.get('target_y'),
                'net_location_id': s.get('net_location'),
                'shot_type': s.get('shot_type'),
                'shot_result': s.get('shot_result'),
                'is_goal': s.get('is_goal'),
                'running_video_time': s.get('running_video_time')
            })
        
        if shot_rows:
            self.client.table('fact_shot_xy').upsert(shot_rows).execute()
        
        return len(shot_rows)
    
    def save_full_tracking(self, game_id: str, data: Dict, replace: bool = True) -> Dict:
        """
        Save complete tracking data (events, shifts, XY data) in one call.
        
        Args:
            game_id: Game ID
            data: {events, shifts, puck_xy, player_xy, shot_xy}
            replace: If True, delete existing data first
            
        Returns:
            Summary of what was saved
        """
        results = {}
        
        if 'events' in data:
            results['events'] = self.save_events(game_id, data['events'], replace)
        
        if 'shifts' in data:
            results['shifts'] = self.save_shifts(game_id, data['shifts'], replace)
        
        if 'puck_xy' in data:
            results['puck_xy'] = self.save_puck_xy(game_id, data['puck_xy'], replace)
        
        if 'player_xy' in data:
            results['player_xy'] = self.save_player_xy(game_id, data['player_xy'], replace)
        
        if 'shot_xy' in data:
            results['shot_xy'] = self.save_shot_xy(game_id, data['shot_xy'], replace)
        
        # Update game status
        try:
            self.client.table('fact_game_status').upsert({
                'game_status_key': f"GS_{game_id}",
                'game_id': game_id,
                'tracking_status': 'in_progress' if replace else 'updated',
                'last_updated': datetime.now().isoformat(),
                'event_count': results.get('events', 0),
                'shift_count': results.get('shifts', 0)
            }).execute()
        except:
            pass  # Table may not exist
        
        return results
    
    # =========================================================================
    # ETL OPERATIONS  
    # =========================================================================
    
    def export_to_csv(self, game_id: str, output_dir: Path = None) -> List[str]:
        """
        Export tracking data to CSV files for ETL processing.
        
        Args:
            game_id: Game ID
            output_dir: Output directory (defaults to data/raw/games/{game_id}/)
            
        Returns:
            List of files created
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'games' / str(game_id)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        files_created = []
        
        # Get data
        data = self.get_game(game_id)
        
        # Export events
        if data['events']:
            events_file = output_dir / f"{game_id}_events.csv"
            with open(events_file, 'w', newline='') as f:
                if data['events']:
                    writer = csv.DictWriter(f, fieldnames=data['events'][0].keys())
                    writer.writeheader()
                    writer.writerows(data['events'])
            files_created.append(str(events_file))
        
        # Export shifts
        if data['shifts']:
            shifts_file = output_dir / f"{game_id}_shifts.csv"
            with open(shifts_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data['shifts'][0].keys())
                writer.writeheader()
                writer.writerows(data['shifts'])
            files_created.append(str(shifts_file))
        
        # Export puck XY
        if data['puck_xy']:
            puck_file = output_dir / f"{game_id}_puck_xy.csv"
            with open(puck_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data['puck_xy'][0].keys())
                writer.writeheader()
                writer.writerows(data['puck_xy'])
            files_created.append(str(puck_file))
        
        return files_created
    
    def trigger_etl(self, game_id: str = None, scope: str = 'game') -> bool:
        """
        Trigger ETL pipeline for game or full refresh.
        
        This calls the flexible_loader.py script to process data.
        
        Args:
            game_id: Game ID (required if scope='game')
            scope: 'game', 'stats_facts', or 'full'
        """
        import subprocess
        
        script_path = Path(__file__).parent / 'flexible_loader.py'
        
        if scope == 'game' and game_id:
            cmd = ['python3', str(script_path), '--scope', 'game', '--game-id', str(game_id), '--operation', 'upsert']
        elif scope == 'stats_facts':
            cmd = ['python3', str(script_path), '--scope', 'category', '--category', 'stats_facts', '--operation', 'upsert']
        else:
            cmd = ['python3', str(script_path), '--scope', 'full', '--operation', 'upsert']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except Exception as e:
            print(f"ETL trigger failed: {e}")
            return False


# =============================================================================
# HTTP API ENDPOINTS (for tracker JavaScript to call)
# =============================================================================

def create_api_server():
    """Create a simple HTTP API server for the tracker."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse
    
    api = TrackerAPI()
    
    class TrackerHandler(BaseHTTPRequestHandler):
        def _set_headers(self, status=200, content_type='application/json'):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
        
        def do_OPTIONS(self):
            self._set_headers()
        
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            params = urllib.parse.parse_qs(parsed.query)
            
            try:
                if path == '/api/games':
                    data = api.list_games()
                    self._set_headers()
                    self.wfile.write(json.dumps(data).encode())
                
                elif path == '/api/game':
                    game_id = params.get('id', [None])[0]
                    if not game_id:
                        self._set_headers(400)
                        self.wfile.write(json.dumps({'error': 'Missing id parameter'}).encode())
                        return
                    data = api.get_game(game_id)
                    self._set_headers()
                    self.wfile.write(json.dumps(data).encode())
                
                elif path == '/api/players':
                    data = api.get_players()
                    self._set_headers()
                    self.wfile.write(json.dumps(data).encode())
                
                elif path == '/api/play-details':
                    pd1, pd2 = api.get_play_details()
                    self._set_headers()
                    self.wfile.write(json.dumps({'play_details': pd1, 'play_details_2': pd2}).encode())
                
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Not found'}).encode())
            
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))
            
            try:
                if self.path == '/api/save':
                    game_id = post_data.get('game_id')
                    if not game_id:
                        self._set_headers(400)
                        self.wfile.write(json.dumps({'error': 'Missing game_id'}).encode())
                        return
                    
                    results = api.save_full_tracking(game_id, post_data, replace=True)
                    self._set_headers()
                    self.wfile.write(json.dumps({'success': True, 'results': results}).encode())
                
                elif self.path == '/api/etl':
                    game_id = post_data.get('game_id')
                    scope = post_data.get('scope', 'game')
                    success = api.trigger_etl(game_id, scope)
                    self._set_headers()
                    self.wfile.write(json.dumps({'success': success}).encode())
                
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Not found'}).encode())
            
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        def log_message(self, format, *args):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")
    
    return HTTPServer, TrackerHandler


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='BenchSight Tracker API')
    parser.add_argument('--action', required=True, 
                        choices=['list-games', 'get-game', 'save-tracking', 'export-csv', 'run-etl', 'serve'])
    parser.add_argument('--game-id', help='Game ID')
    parser.add_argument('--file', help='JSON file with tracking data')
    parser.add_argument('--output-dir', help='Output directory for CSV export')
    parser.add_argument('--port', type=int, default=8765, help='API server port')
    
    args = parser.parse_args()
    api = TrackerAPI()
    
    if args.action == 'list-games':
        games = api.list_games()
        print(json.dumps(games, indent=2))
    
    elif args.action == 'get-game':
        if not args.game_id:
            print("Error: --game-id required")
            sys.exit(1)
        data = api.get_game(args.game_id)
        print(json.dumps(data, indent=2))
    
    elif args.action == 'save-tracking':
        if not args.game_id or not args.file:
            print("Error: --game-id and --file required")
            sys.exit(1)
        with open(args.file) as f:
            data = json.load(f)
        results = api.save_full_tracking(args.game_id, data)
        print(f"Saved: {results}")
    
    elif args.action == 'export-csv':
        if not args.game_id:
            print("Error: --game-id required")
            sys.exit(1)
        output_dir = Path(args.output_dir) if args.output_dir else None
        files = api.export_to_csv(args.game_id, output_dir)
        print(f"Exported: {files}")
    
    elif args.action == 'run-etl':
        success = api.trigger_etl(args.game_id, 'game' if args.game_id else 'full')
        print(f"ETL {'succeeded' if success else 'failed'}")
    
    elif args.action == 'serve':
        HTTPServer, Handler = create_api_server()
        server = HTTPServer(('', args.port), Handler)
        print(f"Tracker API server running on http://localhost:{args.port}")
        print("Endpoints:")
        print("  GET  /api/games          - List games")
        print("  GET  /api/game?id=XXXXX  - Get game with tracking data")
        print("  GET  /api/players        - Get all players")
        print("  GET  /api/play-details   - Get play detail options")
        print("  POST /api/save           - Save tracking data")
        print("  POST /api/etl            - Trigger ETL")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == '__main__':
    main()
