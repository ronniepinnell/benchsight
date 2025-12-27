#!/usr/bin/env python3
"""
BenchSight Tracker Backend
==========================
Handles file operations for the tracker including:
- Loading game configurations
- Saving tracking data to backup folders
- Loading existing tracking data

This can run as a local server or be used as a CLI tool.

Usage:
    # Generate game configs and prepare tracker
    python src/tracker_backend.py --prepare
    
    # Save tracking data for a game
    python src/tracker_backend.py --save 18969 tracking_data.json
    
    # Load tracking data for a game  
    python src/tracker_backend.py --load 18969
    
    # Run local server for tracker integration
    python src/tracker_backend.py --serve
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

import pandas as pd


class TrackerBackend:
    """Handles all file operations for the tracker"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / 'data'
        self.games_dir = self.data_dir / 'raw' / 'games'
        self.output_dir = self.data_dir / 'output'
        self.xlsx_path = self.data_dir / 'BLB_Tables.xlsx'
        
    def prepare_games(self) -> dict:
        """Generate all game configurations from BLB tables"""
        from roster_loader import load_blb_tables, build_game_config, save_game_roster_json
        
        if not self.xlsx_path.exists():
            raise FileNotFoundError(f"BLB_Tables.xlsx not found at {self.xlsx_path}")
        
        tables = load_blb_tables(str(self.xlsx_path))
        schedule = tables['schedule']
        gameroster = tables['gameroster']
        
        # Get current season games
        current_season = '20252026'
        game_ids = schedule[schedule['season'] == current_season]['game_id'].unique().tolist()
        
        games_config = {}
        for gid in game_ids:
            try:
                config = build_game_config(schedule, gameroster, gid)
                games_config[str(gid)] = config
                save_game_roster_json(config, self.games_dir)
                print(f"  ✓ Prepared game {gid}")
            except Exception as e:
                print(f"  ✗ Game {gid}: {e}")
        
        # Save combined config
        config_path = self.output_dir / 'games_config.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(games_config, f, indent=2)
        
        print(f"\nSaved games config to {config_path}")
        return games_config
    
    def load_game(self, game_id: str) -> dict:
        """Load all data for a game including tracking data"""
        game_folder = self.games_dir / str(game_id)
        
        if not game_folder.exists():
            raise FileNotFoundError(f"Game folder not found: {game_folder}")
        
        result = {
            'game_id': game_id,
            'roster': None,
            'tracking': None,
            'events': [],
            'shifts': []
        }
        
        # Load roster
        roster_file = game_folder / 'roster.json'
        if roster_file.exists():
            with open(roster_file) as f:
                result['roster'] = json.load(f)
        
        # Load tracking data from backup
        bkups_dir = game_folder / 'bkups'
        if bkups_dir.exists():
            # Get most recent backup
            backups = sorted(bkups_dir.glob('tracking_*.json'), reverse=True)
            if backups:
                with open(backups[0]) as f:
                    result['tracking'] = json.load(f)
        
        # Load events
        events_dir = game_folder / 'events'
        if events_dir.exists():
            for evt_file in events_dir.glob('*.json'):
                with open(evt_file) as f:
                    result['events'].extend(json.load(f) if isinstance(json.load(open(evt_file)), list) else [])
        
        return result
    
    def save_tracking(self, game_id: str, data: dict) -> str:
        """Save tracking data to game folder with backup"""
        game_folder = self.games_dir / str(game_id)
        game_folder.mkdir(parents=True, exist_ok=True)
        
        bkups_dir = game_folder / 'bkups'
        bkups_dir.mkdir(exist_ok=True)
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = bkups_dir / f'tracking_{timestamp}.json'
        
        # Save backup
        with open(backup_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Also save as current
        current_file = game_folder / 'tracking_current.json'
        with open(current_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Clean old backups (keep last 10)
        backups = sorted(bkups_dir.glob('tracking_*.json'), reverse=True)
        for old in backups[10:]:
            old.unlink()
        
        print(f"Saved tracking to {backup_file}")
        return str(backup_file)
    
    def export_csvs(self, game_id: str, data: dict) -> dict:
        """Export tracking data to CSV files"""
        game_folder = self.games_dir / str(game_id)
        
        # Export events
        if data.get('events'):
            events_df = pd.json_normalize(data['events'])
            events_path = game_folder / 'events' / f'events_{game_id}.csv'
            events_path.parent.mkdir(exist_ok=True)
            events_df.to_csv(events_path, index=False)
        
        # Export shifts
        if data.get('shifts'):
            shifts_df = pd.json_normalize(data['shifts'])
            shifts_path = game_folder / f'shifts_{game_id}.csv'
            shifts_df.to_csv(shifts_path, index=False)
        
        return {'events': str(events_path), 'shifts': str(shifts_path)}
    
    def get_games_with_tracking(self) -> list:
        """Get list of games that have tracking data"""
        games = []
        if self.games_dir.exists():
            for game_folder in self.games_dir.iterdir():
                if game_folder.is_dir() and game_folder.name.isdigit():
                    has_tracking = (game_folder / 'tracking_current.json').exists()
                    has_roster = (game_folder / 'roster.json').exists()
                    
                    roster_info = None
                    if has_roster:
                        with open(game_folder / 'roster.json') as f:
                            roster_info = json.load(f)
                    
                    games.append({
                        'game_id': game_folder.name,
                        'has_tracking': has_tracking,
                        'has_roster': has_roster,
                        'home_team': roster_info.get('homeTeam') if roster_info else None,
                        'away_team': roster_info.get('awayTeam') if roster_info else None,
                        'date': roster_info.get('date') if roster_info else None
                    })
        
        return sorted(games, key=lambda x: x['game_id'], reverse=True)


class TrackerHTTPHandler(SimpleHTTPRequestHandler):
    """HTTP handler for tracker API"""
    
    def __init__(self, *args, backend: TrackerBackend, **kwargs):
        self.backend = backend
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == '/api/games':
            self.send_json(self.backend.get_games_with_tracking())
        elif parsed.path.startswith('/api/game/'):
            game_id = parsed.path.split('/')[-1]
            try:
                data = self.backend.load_game(game_id)
                self.send_json(data)
            except FileNotFoundError as e:
                self.send_error(404, str(e))
        elif parsed.path == '/api/config':
            config_path = self.backend.output_dir / 'games_config.json'
            if config_path.exists():
                with open(config_path) as f:
                    self.send_json(json.load(f))
            else:
                self.send_error(404, "Games config not found")
        else:
            super().do_GET()
    
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path.startswith('/api/save/'):
            game_id = parsed.path.split('/')[-1]
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length))
            
            try:
                path = self.backend.save_tracking(game_id, data)
                self.send_json({'success': True, 'path': path})
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def run_server(backend: TrackerBackend, port: int = 8080):
    """Run local HTTP server for tracker"""
    handler = lambda *args, **kwargs: TrackerHTTPHandler(*args, backend=backend, **kwargs)
    
    os.chdir(backend.project_root)
    server = HTTPServer(('localhost', port), handler)
    print(f"Tracker server running at http://localhost:{port}")
    print(f"Open http://localhost:{port}/tracker/tracker_v17.html")
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description='BenchSight Tracker Backend')
    parser.add_argument('--prepare', action='store_true', help='Prepare all game configs')
    parser.add_argument('--load', type=str, help='Load tracking data for game ID')
    parser.add_argument('--save', type=str, nargs=2, metavar=('GAME_ID', 'FILE'), 
                       help='Save tracking data from JSON file')
    parser.add_argument('--serve', action='store_true', help='Run local server')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    parser.add_argument('--list', action='store_true', help='List games with tracking data')
    
    args = parser.parse_args()
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    backend = TrackerBackend(project_root)
    
    if args.prepare:
        backend.prepare_games()
    elif args.load:
        data = backend.load_game(args.load)
        print(json.dumps(data, indent=2))
    elif args.save:
        game_id, file_path = args.save
        with open(file_path) as f:
            data = json.load(f)
        backend.save_tracking(game_id, data)
    elif args.list:
        games = backend.get_games_with_tracking()
        print(f"\n{'Game ID':<10} {'Teams':<30} {'Date':<12} {'Has Data':<10}")
        print("-" * 65)
        for g in games:
            teams = f"{g['home_team'] or '?'} vs {g['away_team'] or '?'}"
            has_data = '✓' if g['has_tracking'] else ''
            print(f"{g['game_id']:<10} {teams:<30} {g['date'] or '':<12} {has_data:<10}")
    elif args.serve:
        run_server(backend, args.port)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
