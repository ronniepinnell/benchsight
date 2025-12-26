"""
BenchSight ETL - Orchestrator
Main entry point for running the complete ETL pipeline
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
import logging
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.extract import BenchSightExtractor
from etl.transform import BenchSightTransformer, StatisticsCalculator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BenchSightOrchestrator:
    """Orchestrate the complete ETL pipeline"""
    
    def __init__(self, data_path: str = None):
        self.data_path = data_path or os.path.join(
            os.path.dirname(__file__), '../../data'
        )
        self.extractor = BenchSightExtractor(self.data_path)
        self.transformer = None  # Initialize after loading master tables
        
        # Output paths
        self.stage_path = os.path.join(self.data_path, 'processed/stage')
        self.int_path = os.path.join(self.data_path, 'processed/intermediate')
        self.mart_path = os.path.join(self.data_path, 'processed/mart')
        self.export_path = os.path.join(self.data_path, 'exports')
        
        # Ensure directories exist
        for path in [self.stage_path, self.int_path, self.mart_path, self.export_path]:
            os.makedirs(path, exist_ok=True)
            
        # ETL run metadata
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.run_log = []
        
    def log(self, message: str, level: str = 'info'):
        """Log message and store in run log"""
        self.run_log.append({
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        })
        
        if level == 'error':
            logger.error(message)
        elif level == 'warning':
            logger.warning(message)
        else:
            logger.info(message)
            
    def run_full_etl(self, game_ids: list = None) -> dict:
        """Run complete ETL pipeline for all or specified games"""
        self.log(f"Starting full ETL run: {self.run_id}")
        results = {
            'run_id': self.run_id,
            'start_time': datetime.now().isoformat(),
            'games_processed': [],
            'errors': [],
            'stage_files': [],
            'int_files': [],
            'mart_files': []
        }
        
        try:
            # 1. Extract master tables
            self.log("Extracting master tables...")
            master_tables = self.extractor.extract_master_tables()
            self.transformer = BenchSightTransformer(master_tables)
            
            # Save master tables to stage
            for name, df in master_tables.items():
                file_path = os.path.join(self.stage_path, f'{name}.csv')
                df.to_csv(file_path, index=False)
                results['stage_files'].append(file_path)
                self.log(f"  Saved {name}: {len(df)} rows")
                
            # 2. Get game IDs to process
            if game_ids is None:
                game_ids = self.extractor.get_game_ids()
            self.log(f"Processing {len(game_ids)} games: {game_ids}")
            
            # Collect all data for aggregation
            all_events = []
            all_shifts = []
            all_video_times = []
            
            # 3. Process each game
            for game_id in game_ids:
                try:
                    self.log(f"Processing game {game_id}...")
                    game_result = self._process_game(game_id)
                    results['games_processed'].append(game_result)
                    
                    if game_result.get('events') is not None:
                        all_events.append(game_result['events'])
                    if game_result.get('shifts') is not None:
                        all_shifts.append(game_result['shifts'])
                    if game_result.get('video_times') is not None:
                        all_video_times.append(game_result['video_times'])
                        
                except Exception as e:
                    self.log(f"Error processing game {game_id}: {e}", 'error')
                    results['errors'].append({'game_id': game_id, 'error': str(e)})
                    
            # 4. Create combined mart tables
            if all_events:
                combined_events = pd.concat(all_events, ignore_index=True)
                
                # Mart: Combined play-by-play
                mart_pbp = self.transformer.mart_fact_playbyplay(combined_events)
                pbp_path = os.path.join(self.mart_path, 'fact_playbyplay.csv')
                mart_pbp.to_csv(pbp_path, index=False)
                results['mart_files'].append(pbp_path)
                self.log(f"Saved fact_playbyplay: {len(mart_pbp)} rows")
                
                # Mart: Player game stats
                player_stats = self.transformer.mart_player_game_stats(combined_events)
                player_path = os.path.join(self.mart_path, 'fact_player_game_stats.csv')
                player_stats.to_csv(player_path, index=False)
                results['mart_files'].append(player_path)
                self.log(f"Saved fact_player_game_stats: {len(player_stats)} rows")
                
                # Mart: Team game stats
                team_stats = self.transformer.mart_team_game_stats(combined_events)
                team_path = os.path.join(self.mart_path, 'fact_team_game_stats.csv')
                team_stats.to_csv(team_path, index=False)
                results['mart_files'].append(team_path)
                self.log(f"Saved fact_team_game_stats: {len(team_stats)} rows")
                
            # 5. Video times fact table
            if all_video_times:
                combined_video = pd.concat(all_video_times, ignore_index=True)
                video_path = os.path.join(self.mart_path, 'fact_video_times.csv')
                combined_video.to_csv(video_path, index=False)
                results['mart_files'].append(video_path)
                self.log(f"Saved fact_video_times: {len(combined_video)} rows")
                
            # 6. Export for Power BI
            self._export_for_powerbi(results)
            
            results['end_time'] = datetime.now().isoformat()
            results['success'] = True
            
        except Exception as e:
            self.log(f"ETL pipeline failed: {e}", 'error')
            results['success'] = False
            results['fatal_error'] = str(e)
            
        # Save run log
        log_path = os.path.join(self.data_path, f'etl_log_{self.run_id}.json')
        with open(log_path, 'w') as f:
            json.dump({'results': results, 'log': self.run_log}, f, indent=2)
            
        return results
    
    def _process_game(self, game_id: int) -> dict:
        """Process a single game through all ETL layers"""
        result = {'game_id': game_id}
        
        # Extract
        game_data = self.extractor.extract_game_tracking(game_id)
        
        # Stage
        if game_data['events'] is not None:
            stg_events = self.transformer.stage_events(game_data['events'], game_id)
            stg_path = os.path.join(self.stage_path, f'stg_events_{game_id}.csv')
            stg_events.to_csv(stg_path, index=False)
            result['stage_events'] = stg_path
            
            # Intermediate
            int_events = self.transformer.int_events_enriched(stg_events)
            int_path = os.path.join(self.int_path, f'int_events_{game_id}.csv')
            int_events.to_csv(int_path, index=False)
            result['int_events'] = int_path
            result['events'] = int_events
            
        if game_data['shifts'] is not None:
            stg_shifts = self.transformer.stage_shifts(game_data['shifts'], game_id)
            stg_path = os.path.join(self.stage_path, f'stg_shifts_{game_id}.csv')
            stg_shifts.to_csv(stg_path, index=False)
            result['shifts'] = stg_shifts
            
        if game_data['video_times'] is not None:
            stg_video = self.transformer.stage_video_times(game_data['video_times'], game_id)
            stg_path = os.path.join(self.stage_path, f'stg_video_{game_id}.csv')
            stg_video.to_csv(stg_path, index=False)
            result['video_times'] = stg_video
            
        self.log(f"  Game {game_id}: events={len(result.get('events', []))}, "
                f"shifts={len(result.get('shifts', []))}")
        
        return result
    
    def _export_for_powerbi(self, results: dict):
        """Export mart tables in Power BI-friendly format"""
        self.log("Exporting for Power BI...")
        
        # Copy mart files to export folder
        for mart_file in results.get('mart_files', []):
            if os.path.exists(mart_file):
                filename = os.path.basename(mart_file)
                export_path = os.path.join(self.export_path, filename)
                df = pd.read_csv(mart_file)
                df.to_csv(export_path, index=False)
                self.log(f"  Exported {filename}")
                
    def run_single_game_etl(self, game_id: int) -> dict:
        """Run ETL for a single game"""
        return self.run_full_etl(game_ids=[game_id])
    
    def get_etl_status(self) -> dict:
        """Get current ETL status and available data"""
        status = {
            'available_games': self.extractor.get_game_ids(),
            'stage_files': [],
            'int_files': [],
            'mart_files': [],
            'export_files': []
        }
        
        for path, key in [
            (self.stage_path, 'stage_files'),
            (self.int_path, 'int_files'),
            (self.mart_path, 'mart_files'),
            (self.export_path, 'export_files')
        ]:
            if os.path.exists(path):
                status[key] = [f for f in os.listdir(path) if f.endswith('.csv')]
                
        return status


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='BenchSight ETL Pipeline')
    parser.add_argument('--games', nargs='+', type=int, help='Specific game IDs to process')
    parser.add_argument('--status', action='store_true', help='Show ETL status')
    parser.add_argument('--data-path', type=str, help='Path to data directory')
    
    args = parser.parse_args()
    
    orchestrator = BenchSightOrchestrator(args.data_path)
    
    if args.status:
        status = orchestrator.get_etl_status()
        print(json.dumps(status, indent=2))
    else:
        results = orchestrator.run_full_etl(game_ids=args.games)
        print(json.dumps({
            'success': results.get('success'),
            'games_processed': len(results.get('games_processed', [])),
            'errors': len(results.get('errors', []))
        }, indent=2))


if __name__ == '__main__':
    main()
