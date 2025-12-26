"""
BenchSight ETL - Extract Module
Extracts data from raw Excel tracking files and master tables
"""

import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BenchSightExtractor:
    """Extract data from BenchSight raw files"""
    
    def __init__(self, data_path: str = None):
        self.data_path = data_path or os.path.join(os.path.dirname(__file__), '../../data')
        self.raw_path = os.path.join(self.data_path, 'raw')
        self.master_path = os.path.join(self.raw_path, 'master')
        self.games_path = os.path.join(self.raw_path, 'games')
        
    def extract_master_tables(self) -> dict:
        """Extract all dimension tables from BenchSight_Tables.xlsx"""
        master_file = os.path.join(self.master_path, 'BenchSight_Tables.xlsx')
        
        if not os.path.exists(master_file):
            # Try legacy name
            master_file = os.path.join(self.master_path, 'BLB_Tables.xlsx')
            
        if not os.path.exists(master_file):
            raise FileNotFoundError(f"Master tables file not found: {master_file}")
            
        logger.info(f"Loading master tables from: {master_file}")
        
        xl = pd.ExcelFile(master_file)
        tables = {}
        
        for sheet in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet)
            # Rename BLB references to BenchSight
            table_name = sheet.replace('BLB_', 'benchsight_')
            tables[table_name] = df
            logger.info(f"  Loaded {table_name}: {len(df)} rows, {len(df.columns)} cols")
            
        return tables
    
    def get_game_ids(self) -> list:
        """Get list of all game IDs with tracking data"""
        if not os.path.exists(self.games_path):
            return []
            
        game_ids = []
        for item in os.listdir(self.games_path):
            item_path = os.path.join(self.games_path, item)
            if os.path.isdir(item_path) and item.isdigit():
                game_ids.append(int(item))
                
        return sorted(game_ids)
    
    def extract_game_tracking(self, game_id: int) -> dict:
        """Extract tracking data for a single game"""
        game_path = os.path.join(self.games_path, str(game_id))
        
        if not os.path.exists(game_path):
            raise FileNotFoundError(f"Game folder not found: {game_path}")
            
        result = {
            'game_id': game_id,
            'events': None,
            'shifts': None,
            'game_rosters': None,
            'video_times': None,
            'shots': [],
            'xy_data': [],
            'metadata': {}
        }
        
        # Find tracking file
        tracking_file = None
        for f in os.listdir(game_path):
            if f.endswith('_tracking.xlsx') and not f.startswith('~$'):
                tracking_file = os.path.join(game_path, f)
                break
                
        if tracking_file and os.path.exists(tracking_file):
            logger.info(f"Loading tracking file: {tracking_file}")
            xl = pd.ExcelFile(tracking_file)
            
            # Extract events
            if 'events' in xl.sheet_names:
                events_df = pd.read_excel(xl, sheet_name='events')
                # Clean column names (remove trailing underscores)
                events_df.columns = [c.rstrip('_') for c in events_df.columns]
                result['events'] = events_df
                logger.info(f"  Events: {len(events_df)} rows")
                
            # Extract shifts
            if 'shifts' in xl.sheet_names:
                shifts_df = pd.read_excel(xl, sheet_name='shifts')
                shifts_df.columns = [c.rstrip('_') for c in shifts_df.columns]
                result['shifts'] = shifts_df
                logger.info(f"  Shifts: {len(shifts_df)} rows")
                
            # Extract game rosters
            if 'game_rosters' in xl.sheet_names:
                rosters_df = pd.read_excel(xl, sheet_name='game_rosters')
                result['game_rosters'] = rosters_df
                logger.info(f"  Rosters: {len(rosters_df)} rows")
                
        # Find video times file
        for f in os.listdir(game_path):
            if 'video_times' in f and f.endswith('.xlsx') and not f.startswith('~$'):
                video_file = os.path.join(game_path, f)
                try:
                    video_df = pd.read_excel(video_file)
                    result['video_times'] = video_df
                    logger.info(f"  Video times: {len(video_df)} rows")
                except Exception as e:
                    logger.warning(f"  Could not load video times: {e}")
                break
                
        # Load shot files from shots/ folder
        shots_path = os.path.join(game_path, 'shots')
        if os.path.exists(shots_path):
            for f in os.listdir(shots_path):
                if f.endswith('.csv'):
                    shot_df = pd.read_csv(os.path.join(shots_path, f))
                    result['shots'].append({'file': f, 'data': shot_df})
                    
        # Load XY data from xy/ folder
        xy_path = os.path.join(game_path, 'xy')
        if os.path.exists(xy_path):
            for root, dirs, files in os.walk(xy_path):
                for f in files:
                    if f.endswith('.csv'):
                        xy_df = pd.read_csv(os.path.join(root, f))
                        result['xy_data'].append({'file': f, 'data': xy_df})
                        
        return result
    
    def extract_all_games(self) -> list:
        """Extract tracking data for all games"""
        game_ids = self.get_game_ids()
        logger.info(f"Found {len(game_ids)} games to extract")
        
        all_games = []
        for game_id in game_ids:
            try:
                game_data = self.extract_game_tracking(game_id)
                all_games.append(game_data)
            except Exception as e:
                logger.error(f"Failed to extract game {game_id}: {e}")
                
        return all_games
    
    def get_extraction_summary(self) -> dict:
        """Get summary of available data"""
        summary = {
            'master_tables': {},
            'games': []
        }
        
        # Check master tables
        try:
            tables = self.extract_master_tables()
            for name, df in tables.items():
                summary['master_tables'][name] = {
                    'rows': len(df),
                    'columns': list(df.columns)
                }
        except Exception as e:
            summary['master_tables_error'] = str(e)
            
        # Check games
        for game_id in self.get_game_ids():
            game_path = os.path.join(self.games_path, str(game_id))
            game_info = {
                'game_id': game_id,
                'has_tracking': False,
                'has_video_times': False,
                'has_shots': False,
                'has_xy': False
            }
            
            for f in os.listdir(game_path):
                if '_tracking.xlsx' in f and not f.startswith('~$'):
                    game_info['has_tracking'] = True
                if 'video_times' in f:
                    game_info['has_video_times'] = True
                    
            if os.path.exists(os.path.join(game_path, 'shots')):
                game_info['has_shots'] = True
            if os.path.exists(os.path.join(game_path, 'xy')):
                game_info['has_xy'] = True
                
            summary['games'].append(game_info)
            
        return summary


def main():
    """Test extraction"""
    extractor = BenchSightExtractor()
    
    # Get summary
    summary = extractor.get_extraction_summary()
    print("\n=== EXTRACTION SUMMARY ===")
    print(f"Master Tables: {len(summary.get('master_tables', {}))}")
    print(f"Games Found: {len(summary.get('games', []))}")
    
    for game in summary.get('games', []):
        print(f"  Game {game['game_id']}: Tracking={game['has_tracking']}, "
              f"Video={game['has_video_times']}, Shots={game['has_shots']}, XY={game['has_xy']}")
        
    # Extract one game as test
    if summary.get('games'):
        game_id = summary['games'][0]['game_id']
        print(f"\n=== TEST EXTRACTION: Game {game_id} ===")
        game_data = extractor.extract_game_tracking(game_id)
        if game_data['events'] is not None:
            print(f"Events columns: {list(game_data['events'].columns)[:10]}")
            

if __name__ == '__main__':
    main()
