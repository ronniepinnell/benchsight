#!/usr/bin/env python3
"""
BenchSight ETL Pipeline - Complete Data Processing

This script processes raw tracking data from the game tracker into the full
111-table dimensional data warehouse structure.

Usage:
    python etl_pipeline.py --game-id 18969           # Process single game
    python etl_pipeline.py --all                      # Process all games
    python etl_pipeline.py --refresh-stats           # Recalculate all stats
    python etl_pipeline.py --validate                # Run validation checks

Author: BenchSight
"""

import os
import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from collections import defaultdict

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from supabase import create_client, Client
except ImportError:
    print("Install supabase: pip install supabase --break-system-packages")
    sys.exit(1)

# Load config
try:
    from config.config_loader import load_config
    cfg = load_config()
    SUPABASE_URL = cfg.supabase_url
    SUPABASE_KEY = cfg.supabase_service_key
except:
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://uuaowslhpgyiudmbvqze.supabase.co")
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


class ETLPipeline:
    """Complete ETL pipeline for BenchSight data warehouse."""
    
    def __init__(self):
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.stats = {'processed': 0, 'errors': 0, 'tables_updated': []}
    
    # =========================================================================
    # DATA EXTRACTION
    # =========================================================================
    
    def get_games_to_process(self, game_id: str = None) -> List[str]:
        """Get list of games that need processing."""
        if game_id:
            return [game_id]
        
        # Get all games with tracking data
        result = self.client.table('fact_events').select('game_id').execute()
        return list(set(r['game_id'] for r in result.data))
    
    def extract_game_data(self, game_id: str) -> Dict:
        """Extract all raw data for a game."""
        print(f"  Extracting data for game {game_id}...")
        
        data = {
            'game_id': game_id,
            'schedule': self.client.table('dim_schedule').select('*').eq('game_id', game_id).execute().data,
            'events': self.client.table('fact_events').select('*').eq('game_id', game_id).order('event_index').execute().data,
            'events_player': self.client.table('fact_events_player').select('*').eq('game_id', game_id).execute().data,
            'shifts': self.client.table('fact_shifts').select('*').eq('game_id', game_id).order('shift_index').execute().data,
            'roster': self.client.table('fact_gameroster').select('*').eq('game_id', game_id).execute().data,
            'puck_xy': self.client.table('fact_puck_xy_long').select('*').eq('game_id', game_id).execute().data,
            'shot_xy': self.client.table('fact_shot_xy').select('*').eq('game_id', game_id).execute().data,
        }
        
        print(f"    Events: {len(data['events'])}, Shifts: {len(data['shifts'])}, XY: {len(data['puck_xy'])}")
        return data
    
    # =========================================================================
    # TRANSFORMATIONS
    # =========================================================================
    
    def calculate_player_game_stats(self, data: Dict) -> List[Dict]:
        """Calculate player statistics for a game."""
        game_id = data['game_id']
        events = data['events']
        events_player = data['events_player']
        roster = data['roster']
        
        # Initialize stats per player
        player_stats = {}
        for r in roster:
            pid = r['player_id']
            player_stats[pid] = {
                'player_game_stats_key': f"PGS_{game_id}_{pid}",
                'game_id': game_id,
                'player_id': pid,
                'player_name': r.get('player_name', ''),
                'team_venue': r['team_venue'],
                'team_name': r.get('team_name', ''),
                'player_position': r.get('player_position', ''),
                'goals': 0, 'assists': 0, 'primary_assists': 0, 'secondary_assists': 0,
                'shots': 0, 'shots_on_goal': 0, 'shots_blocked': 0, 'shots_missed': 0,
                'hits': 0, 'hits_taken': 0,
                'blocked_shots': 0,
                'faceoff_wins': 0, 'faceoff_losses': 0,
                'giveaways': 0, 'takeaways': 0,
                'zone_entries': 0, 'zone_exits': 0,
                'passes_completed': 0, 'passes_attempted': 0,
                'plus_minus': 0,
                'toi_seconds': 0, 'toi_minutes': ''
            }
        
        # Process events
        for evt in events:
            event_type = evt.get('event_type', '')
            team_venue = evt.get('team_venue', '')
            successful = evt.get('event_successful', '') == 's'
            
            # Get players involved
            evt_players = [ep for ep in events_player if ep['event_index'] == evt['event_index']]
            primary_player = next((ep for ep in evt_players if ep.get('role_number') == 1), None)
            
            if primary_player and primary_player['player_id'] in player_stats:
                pid = primary_player['player_id']
                ps = player_stats[pid]
                
                if event_type == 'Goal':
                    ps['goals'] += 1
                    # Plus/minus for all on-ice players
                    for r in roster:
                        if r['team_venue'] == team_venue:
                            player_stats[r['player_id']]['plus_minus'] += 1
                        else:
                            player_stats[r['player_id']]['plus_minus'] -= 1
                    
                    # Assists
                    for ep in evt_players[1:3]:
                        if ep['player_id'] in player_stats:
                            player_stats[ep['player_id']]['assists'] += 1
                            if ep.get('role_number') == 2:
                                player_stats[ep['player_id']]['primary_assists'] += 1
                            else:
                                player_stats[ep['player_id']]['secondary_assists'] += 1
                
                elif event_type == 'Shot':
                    ps['shots'] += 1
                    detail = evt.get('event_detail', '') or ''
                    if 'OnNet' in detail or 'Goal' in detail:
                        ps['shots_on_goal'] += 1
                    elif 'Blocked' in detail:
                        ps['shots_blocked'] += 1
                    elif 'Missed' in detail:
                        ps['shots_missed'] += 1
                
                elif event_type == 'Faceoff':
                    if successful:
                        ps['faceoff_wins'] += 1
                    else:
                        ps['faceoff_losses'] += 1
                
                elif event_type == 'Hit':
                    ps['hits'] += 1
                    # Hit taken by opponent
                    for ep in evt_players:
                        if ep.get('player_role', '').startswith('opp') and ep['player_id'] in player_stats:
                            player_stats[ep['player_id']]['hits_taken'] += 1
                
                elif event_type == 'Block':
                    ps['blocked_shots'] += 1
                
                elif event_type == 'Turnover':
                    detail = evt.get('event_detail', '') or ''
                    if 'Giveaway' in detail:
                        ps['giveaways'] += 1
                    elif 'Takeaway' in detail:
                        ps['takeaways'] += 1
                
                elif event_type == 'Zone_Entry':
                    ps['zone_entries'] += 1
                
                elif event_type == 'Zone_Exit':
                    ps['zone_exits'] += 1
                
                elif event_type == 'Pass':
                    ps['passes_attempted'] += 1
                    if successful:
                        ps['passes_completed'] += 1
        
        # Calculate TOI from shifts
        shifts = data['shifts']
        for shift in shifts:
            # Calculate shift duration
            start_sec = (int(shift.get('shift_start_min') or 0) * 60) + int(shift.get('shift_start_sec') or 0)
            end_sec = (int(shift.get('shift_end_min') or 0) * 60) + int(shift.get('shift_end_sec') or 0)
            duration = start_sec - end_sec  # Clock counts down
            if duration < 0:
                duration = 0
            
            # Add to each player on ice
            for slot in ['home_forward_1', 'home_forward_2', 'home_forward_3', 'home_defense_1', 'home_defense_2', 'home_goalie',
                        'away_forward_1', 'away_forward_2', 'away_forward_3', 'away_defense_1', 'away_defense_2', 'away_goalie']:
                player_num = shift.get(slot)
                if player_num:
                    # Find player by number
                    team = 'Home' if 'home' in slot else 'Away'
                    for r in roster:
                        if r['team_venue'] == team and str(r.get('player_game_number')) == str(player_num):
                            if r['player_id'] in player_stats:
                                player_stats[r['player_id']]['toi_seconds'] += duration
        
        # Format TOI
        for pid, ps in player_stats.items():
            mins = ps['toi_seconds'] // 60
            secs = ps['toi_seconds'] % 60
            ps['toi_minutes'] = f"{mins}:{secs:02d}"
        
        return list(player_stats.values())
    
    def calculate_team_game_stats(self, data: Dict) -> List[Dict]:
        """Calculate team statistics for a game."""
        game_id = data['game_id']
        events = data['events']
        schedule = data['schedule'][0] if data['schedule'] else {}
        
        teams = {'Home': {}, 'Away': {}}
        
        for team_venue in ['Home', 'Away']:
            team_events = [e for e in events if e.get('team_venue') == team_venue]
            
            goals = len([e for e in team_events if e.get('event_type') == 'Goal'])
            shots = len([e for e in team_events if e.get('event_type') in ['Shot', 'Goal']])
            
            teams[team_venue] = {
                'team_game_stats_key': f"TGS_{game_id}_{team_venue}",
                'game_id': game_id,
                'team_venue': team_venue,
                'team_name': schedule.get(f'{team_venue.lower()}_team_name', ''),
                'goals': goals,
                'shots': shots,
                'shots_on_goal': len([e for e in team_events if e.get('event_type') == 'Shot' and 'OnNet' in (e.get('event_detail') or '')]) + goals,
                'faceoff_wins': len([e for e in team_events if e.get('event_type') == 'Faceoff' and e.get('event_successful') == 's']),
                'hits': len([e for e in team_events if e.get('event_type') == 'Hit']),
                'blocks': len([e for e in team_events if e.get('event_type') == 'Block']),
                'giveaways': len([e for e in team_events if e.get('event_type') == 'Turnover' and 'Giveaway' in (e.get('event_detail') or '')]),
                'takeaways': len([e for e in team_events if e.get('event_type') == 'Turnover' and 'Takeaway' in (e.get('event_detail') or '')]),
                'zone_entries': len([e for e in team_events if e.get('event_type') == 'Zone_Entry']),
                'zone_exits': len([e for e in team_events if e.get('event_type') == 'Zone_Exit']),
                'power_play_goals': 0,  # TODO: Calculate from strength
                'short_handed_goals': 0,
                'penalty_minutes': 0
            }
            
            # Shooting percentage
            if teams[team_venue]['shots'] > 0:
                teams[team_venue]['shooting_pct'] = round(teams[team_venue]['goals'] / teams[team_venue]['shots'] * 100, 1)
            else:
                teams[team_venue]['shooting_pct'] = 0.0
        
        return list(teams.values())
    
    def calculate_linked_events(self, data: Dict) -> List[Dict]:
        """Create linked events fact table."""
        events = data['events']
        game_id = data['game_id']
        
        linked = []
        for evt in events:
            if evt.get('linked_event_index'):
                linked.append({
                    'linked_events_key': f"LE_{game_id}_{evt['event_index']}_{evt['linked_event_index']}",
                    'game_id': game_id,
                    'event_index': evt['event_index'],
                    'linked_event_index': evt['linked_event_index'],
                    'event_type': evt.get('event_type'),
                    'linked_event_type': next((e.get('event_type') for e in events if e['event_index'] == evt['linked_event_index']), None)
                })
        
        return linked
    
    def calculate_event_chains(self, data: Dict) -> List[Dict]:
        """Identify event chains (sequences of linked events)."""
        events = data['events']
        game_id = data['game_id']
        
        # Build graph of linked events
        links = {}
        for evt in events:
            if evt.get('linked_event_index'):
                links[evt['event_index']] = evt['linked_event_index']
        
        # Find chains
        chains = []
        chain_id = 1
        visited = set()
        
        for evt in events:
            if evt['event_index'] in visited:
                continue
            
            # Trace chain backwards
            chain = [evt['event_index']]
            current = evt['event_index']
            while current in links:
                prev = links[current]
                if prev in chain:
                    break  # Cycle detection
                chain.insert(0, prev)
                current = prev
            
            if len(chain) > 1:
                for i, idx in enumerate(chain):
                    chains.append({
                        'event_chain_key': f"EC_{game_id}_{chain_id}_{i+1}",
                        'game_id': game_id,
                        'chain_id': chain_id,
                        'chain_position': i + 1,
                        'chain_length': len(chain),
                        'event_index': idx,
                        'event_type': next((e.get('event_type') for e in events if e['event_index'] == idx), None)
                    })
                    visited.add(idx)
                chain_id += 1
        
        return chains
    
    def calculate_scoring_chances(self, data: Dict) -> List[Dict]:
        """Identify scoring chances based on shot location."""
        shot_xy = data['shot_xy']
        events = data['events']
        game_id = data['game_id']
        
        chances = []
        for shot in shot_xy:
            x = float(shot.get('shot_x') or 0)
            y = float(shot.get('shot_y') or 0)
            
            # Danger zone classification
            # High danger: slot area (x > 175 or x < 25, y between 25-60)
            # Medium danger: outside slot but inside circles
            # Low danger: outside circles
            
            danger = 'low'
            if (x > 170 or x < 30) and 20 < y < 65:
                danger = 'high'
            elif (x > 155 or x < 45) and 15 < y < 70:
                danger = 'medium'
            
            chances.append({
                'scoring_chance_key': f"SC_{game_id}_{shot['event_index']}",
                'game_id': game_id,
                'event_index': shot['event_index'],
                'player_id': shot.get('player_id'),
                'team_venue': shot.get('team_venue'),
                'period': shot.get('period'),
                'shot_x': x,
                'shot_y': y,
                'danger_zone': danger,
                'is_goal': shot.get('is_goal') == '1',
                'net_location': shot.get('net_location_id'),
                'xg': 0.05 if danger == 'low' else (0.15 if danger == 'medium' else 0.30)  # Simple xG model
            })
        
        return chances
    
    def calculate_puck_xy_wide(self, data: Dict) -> List[Dict]:
        """Convert puck XY long to wide format."""
        puck_xy = data['puck_xy']
        game_id = data['game_id']
        
        # Group by event
        by_event = defaultdict(list)
        for p in puck_xy:
            by_event[p['event_index']].append(p)
        
        wide = []
        for event_index, points in by_event.items():
            row = {
                'puck_xy_key': f"PXYW_{game_id}_{event_index}",
                'game_id': game_id,
                'event_index': event_index,
                'event_key': f"EVT_{game_id}_{event_index}",
                'point_count': len(points)
            }
            
            # Sort by point number
            points.sort(key=lambda p: p.get('point_number', 0))
            
            for i in range(10):
                if i < len(points):
                    row[f'x_{i+1}'] = points[i].get('x')
                    row[f'y_{i+1}'] = points[i].get('y')
                    row[f'z_{i+1}'] = points[i].get('z', 0)
                    row[f'timestamp_{i+1}'] = points[i].get('event_timestamp')
                else:
                    row[f'x_{i+1}'] = None
                    row[f'y_{i+1}'] = None
                    row[f'z_{i+1}'] = None
                    row[f'timestamp_{i+1}'] = None
            
            wide.append(row)
        
        return wide
    
    # =========================================================================
    # LOADING
    # =========================================================================
    
    def upsert(self, table: str, data: List[Dict]) -> int:
        """Upsert data to Supabase table."""
        if not data:
            return 0
        
        try:
            self.client.table(table).upsert(data).execute()
            self.stats['tables_updated'].append(table)
            return len(data)
        except Exception as e:
            print(f"    Error upserting to {table}: {e}")
            self.stats['errors'] += 1
            return 0
    
    def delete_game_data(self, game_id: str, tables: List[str]):
        """Delete existing data for a game from specified tables."""
        for table in tables:
            try:
                self.client.table(table).delete().eq('game_id', game_id).execute()
            except:
                pass
    
    # =========================================================================
    # MAIN PIPELINE
    # =========================================================================
    
    def process_game(self, game_id: str):
        """Process a single game through the ETL pipeline."""
        print(f"\nProcessing game {game_id}...")
        
        # Extract
        data = self.extract_game_data(game_id)
        
        if not data['events']:
            print(f"  No events found for game {game_id}, skipping.")
            return
        
        # Transform and Load
        print("  Calculating player stats...")
        player_stats = self.calculate_player_game_stats(data)
        count = self.upsert('fact_player_game_stats', player_stats)
        print(f"    Loaded {count} player stat rows")
        
        print("  Calculating team stats...")
        team_stats = self.calculate_team_game_stats(data)
        count = self.upsert('fact_team_game_stats', team_stats)
        print(f"    Loaded {count} team stat rows")
        
        print("  Processing linked events...")
        linked = self.calculate_linked_events(data)
        count = self.upsert('fact_linked_events', linked)
        print(f"    Loaded {count} linked event rows")
        
        print("  Processing event chains...")
        chains = self.calculate_event_chains(data)
        count = self.upsert('fact_event_chains', chains)
        print(f"    Loaded {count} event chain rows")
        
        print("  Calculating scoring chances...")
        chances = self.calculate_scoring_chances(data)
        count = self.upsert('fact_scoring_chances', chances)
        print(f"    Loaded {count} scoring chance rows")
        
        print("  Processing puck XY wide format...")
        puck_wide = self.calculate_puck_xy_wide(data)
        count = self.upsert('fact_puck_xy_wide', puck_wide)
        print(f"    Loaded {count} puck XY wide rows")
        
        # Update game status
        self.upsert('fact_game_status', [{
            'game_status_key': f"GS_{game_id}",
            'game_id': game_id,
            'tracking_status': 'processed',
            'events_tracked': len(data['events']),
            'shifts_tracked': len(data['shifts']),
            'xy_tracked': len(data['puck_xy']),
            'last_etl_run': datetime.now().isoformat()
        }])
        
        self.stats['processed'] += 1
        print(f"  ✓ Game {game_id} processed successfully")
    
    def run(self, game_id: str = None, all_games: bool = False, refresh_stats: bool = False):
        """Run the ETL pipeline."""
        print("=" * 60)
        print("BenchSight ETL Pipeline")
        print("=" * 60)
        
        start = datetime.now()
        
        if game_id:
            games = [game_id]
        elif all_games:
            games = self.get_games_to_process()
        else:
            print("Specify --game-id or --all")
            return
        
        print(f"Games to process: {len(games)}")
        
        for gid in games:
            try:
                self.process_game(gid)
            except Exception as e:
                print(f"  Error processing game {gid}: {e}")
                self.stats['errors'] += 1
        
        # Summary
        elapsed = (datetime.now() - start).total_seconds()
        print("\n" + "=" * 60)
        print("ETL Summary")
        print("=" * 60)
        print(f"Games processed: {self.stats['processed']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Tables updated: {len(set(self.stats['tables_updated']))}")
        print(f"Time elapsed: {elapsed:.1f}s")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='BenchSight ETL Pipeline')
    parser.add_argument('--game-id', help='Process single game')
    parser.add_argument('--all', action='store_true', help='Process all games')
    parser.add_argument('--refresh-stats', action='store_true', help='Recalculate all stats')
    parser.add_argument('--validate', action='store_true', help='Run validation')
    
    args = parser.parse_args()
    
    pipeline = ETLPipeline()
    
    if args.validate:
        print("Validation not yet implemented")
    else:
        pipeline.run(game_id=args.game_id, all_games=args.all, refresh_stats=args.refresh_stats)


if __name__ == '__main__':
    main()
