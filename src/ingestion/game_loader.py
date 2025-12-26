"""
=============================================================================
GAME DATA LOADER - WITH XY COORDINATE SUPPORT
=============================================================================
File: src/ingestion/game_loader.py

PURPOSE:
    Load all game data from game-specific folders:
    - Tracking file (events, shifts) - REQUIRED
    - XY coordinates (event locations on rink) - OPTIONAL
    - Shot locations (where shots hit net) - OPTIONAL
    - Video links (YouTube URLs with timestamps) - OPTIONAL

FILE STRUCTURE:
    data/raw/games/{game_id}/
    ├── {game_id}_tracking.xlsx    # Events and shifts (REQUIRED)
    ├── xy/                        # XY coordinates (OPTIONAL)
    │   ├── event_locations.csv
    │   ├── puck_tracking.csv
    │   └── player_positions.csv
    ├── shots/                     # Shot locations (OPTIONAL)
    │   └── shot_net_locations.csv
    └── video/                     # Video links (OPTIONAL)
        └── video_links.csv

USAGE:
    from src.ingestion.game_loader import GameLoader
    
    loader = GameLoader(config, game_id=18969)
    data = loader.load_all()
    
    # data contains:
    # - events: DataFrame
    # - shifts: DataFrame
    # - xy_data: Dict with event_locations, shot_net_locations, etc. (if available)

=============================================================================
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass

from src.utils.logger import get_logger
from src.ingestion.xy_loader import XYLoader

logger = get_logger(__name__)


@dataclass
class GameFiles:
    """Tracks which files were found for a game."""
    tracking: bool = False
    event_locations: bool = False
    shot_net_locations: bool = False
    puck_tracking: bool = False
    player_positions: bool = False
    video_links: bool = False


class GameLoader:
    """
    Load all data for a specific game.
    
    This loader handles:
    1. Main tracking file (events and shifts) - REQUIRED
    2. XY coordinate files - OPTIONAL, loaded if present
    3. Shot location files - OPTIONAL, loaded if present
    4. Video link files - OPTIONAL, loaded if present
    
    Attributes:
        config: Configuration object
        game_id: Game identifier
        game_dir: Path to game folder
    """
    
    def __init__(self, config, game_id: int):
        """
        Initialize the game loader.
        
        Args:
            config: Configuration with paths
            game_id: Game identifier (e.g., 18969)
        """
        self.config = config
        self.game_id = game_id
        self.game_dir = config.paths.game_data_root / str(game_id)
        
        # Track which files are found
        self.files_found = GameFiles()
        
        # XY loader for coordinate files
        self.xy_loader = XYLoader(config, game_id)
        
        logger.info(f"GameLoader initialized for game {game_id}")
    
    def find_tracking_file(self) -> Optional[Path]:
        """
        Find the main tracking Excel file.
        
        Searches in order:
        1. {game_dir}/{game_id}_tracking.xlsx
        2. {game_dir}/*.xlsx (any xlsx file)
        3. {raw_dir}/{game_id}_tracking.xlsx (alternate location)
        
        Returns:
            Path to tracking file or None if not found
        """
        # Primary location
        tracking_file = self.game_dir / f"{self.game_id}_tracking.xlsx"
        if tracking_file.exists():
            return tracking_file
        
        # Look for any xlsx in game directory
        if self.game_dir.exists():
            xlsx_files = list(self.game_dir.glob("*.xlsx"))
            xlsx_files = [f for f in xlsx_files if not f.name.startswith('~')]  # Skip temp files
            if xlsx_files:
                return xlsx_files[0]
        
        # Alternate location (directly in raw folder)
        alt_file = self.config.paths.blb_tables_file.parent / f"{self.game_id}_tracking.xlsx"
        if alt_file.exists():
            return alt_file
        
        return None
    
    def check_files(self) -> GameFiles:
        """
        Check which files are available for this game.
        
        Returns:
            GameFiles dataclass with boolean flags
        """
        self.files_found.tracking = self.find_tracking_file() is not None
        
        # Check XY files
        xy_data = self.xy_loader.load_all()
        self.files_found.event_locations = xy_data['event_locations'] is not None
        self.files_found.shot_net_locations = xy_data['shot_net_locations'] is not None
        self.files_found.puck_tracking = xy_data['puck_tracking'] is not None
        self.files_found.player_positions = xy_data['player_positions'] is not None
        self.files_found.video_links = xy_data['video_links'] is not None
        
        return self.files_found
    
    def load_all(self, include_xy: bool = True) -> Optional[Dict]:
        """
        Load all game data.
        
        Args:
            include_xy: Whether to load XY coordinate files
        
        Returns:
            Dictionary with:
            - events: DataFrame
            - shifts: DataFrame
            - xy_data: Dict with coordinate DataFrames (if include_xy=True)
            - video_links: DataFrame (if available)
            
            Returns None if tracking file not found.
        """
        # Load main tracking file
        tracking_file = self.find_tracking_file()
        
        if tracking_file is None:
            logger.error(f"No tracking file found for game {self.game_id}")
            print(f"  ✗ Tracking file not found for game {self.game_id}")
            print(f"    Expected: {self.game_dir / f'{self.game_id}_tracking.xlsx'}")
            return None
        
        logger.info(f"Loading tracking file: {tracking_file}")
        print(f"  ✓ Found tracking file: {tracking_file.name}")
        
        xlsx = pd.ExcelFile(tracking_file)
        
        data = {
            'events': None,
            'shifts': None,
            'xy_data': {},
        }
        
        # Load events
        if 'events' in xlsx.sheet_names:
            data['events'] = pd.read_excel(xlsx, sheet_name='events')
            print(f"    Events: {len(data['events'])} rows")
            logger.info(f"Loaded events: {len(data['events'])} rows")
        else:
            logger.warning("No 'events' sheet found in tracking file")
        
        # Load shifts
        if 'shifts' in xlsx.sheet_names:
            data['shifts'] = pd.read_excel(xlsx, sheet_name='shifts')
            print(f"    Shifts: {len(data['shifts'])} rows")
            logger.info(f"Loaded shifts: {len(data['shifts'])} rows")
        else:
            logger.warning("No 'shifts' sheet found in tracking file")
        
        # Load XY data if requested
        if include_xy:
            xy_data = self.xy_loader.load_all()
            
            for key, df in xy_data.items():
                if df is not None:
                    data['xy_data'][key] = df
                    print(f"    {key}: {len(df)} rows")
            
            if not data['xy_data']:
                print(f"    XY data: Not found (optional)")
        
        return data
    
    def load_specific(self, 
                      load_events: bool = True,
                      load_shifts: bool = True,
                      load_event_locations: bool = False,
                      load_shot_locations: bool = False,
                      load_video_links: bool = False) -> Dict:
        """
        Load specific components of game data.
        
        Useful when you only need to reload certain data types.
        
        Args:
            load_events: Load events sheet
            load_shifts: Load shifts sheet
            load_event_locations: Load XY event locations
            load_shot_locations: Load shot net locations
            load_video_links: Load video links
        
        Returns:
            Dictionary with requested data
        """
        data = {}
        
        tracking_file = self.find_tracking_file()
        
        if tracking_file and (load_events or load_shifts):
            xlsx = pd.ExcelFile(tracking_file)
            
            if load_events and 'events' in xlsx.sheet_names:
                data['events'] = pd.read_excel(xlsx, sheet_name='events')
            
            if load_shifts and 'shifts' in xlsx.sheet_names:
                data['shifts'] = pd.read_excel(xlsx, sheet_name='shifts')
        
        if load_event_locations:
            data['event_locations'] = self.xy_loader.load_event_locations()
        
        if load_shot_locations:
            data['shot_net_locations'] = self.xy_loader.load_shot_net_locations()
        
        if load_video_links:
            data['video_links'] = self.xy_loader.load_video_links()
        
        return data
    
    def merge_xy_into_events(self, events_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge all available XY data into events DataFrame.
        
        Args:
            events_df: Events DataFrame
        
        Returns:
            Events DataFrame with XY columns added
        """
        return self.xy_loader.merge_with_events(events_df)
    
    def print_status(self):
        """Print status of available files."""
        files = self.check_files()
        
        print(f"\n  Game {self.game_id} Files:")
        print(f"  " + "-" * 40)
        print(f"    Tracking file:      {'✓' if files.tracking else '✗'} (required)")
        print(f"    Event locations:    {'✓' if files.event_locations else '○'} (optional)")
        print(f"    Shot net locations: {'✓' if files.shot_net_locations else '○'} (optional)")
        print(f"    Puck tracking:      {'✓' if files.puck_tracking else '○'} (optional)")
        print(f"    Player positions:   {'✓' if files.player_positions else '○'} (optional)")
        print(f"    Video links:        {'✓' if files.video_links else '○'} (optional)")
