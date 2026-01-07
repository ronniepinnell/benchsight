"""
=============================================================================
XY COORDINATE LOADER - MULTI-FILE SUBFOLDER SUPPORT
=============================================================================
File: src/ingestion/xy_loader.py

FOLDER STRUCTURE (Multiple CSVs per game, appended together):
============================================================

data/raw/games/{game_id}/
├── {game_id}_tracking.xlsx           # Main tracking file (REQUIRED)
│
├── xy/                               # XY coordinate data folder
│   │
│   └── event_locations/              # SUBFOLDER - all CSVs appended
│       ├── period1_events.csv        # Events from period 1
│       ├── period2_events.csv        # Events from period 2
│       ├── period3_events.csv        # Events from period 3
│       └── overtime_events.csv       # OT events (if applicable)
│
├── shots/                            # Shot net location data folder
│   │
│   └── shot_locations/               # SUBFOLDER - all CSVs appended
│       ├── period1_shots.csv
│       ├── period2_shots.csv
│       └── period3_shots.csv
│
└── video/                            # Video links folder
    └── video_links.csv


EVENT_LOCATIONS CSV STRUCTURE:
==============================
Each CSV in xy/event_locations/ contains:

REQUIRED COLUMNS:
- event_index          : Links to fact_event_players
- player_game_number   : Player who performed the action
- player_team          : Team of the player (e.g., "Platinum", "Velodrome")

LOCATION 1 - Start/Primary (where event began):
- event_x1             : X coordinate (-100 to 100, center=0, goals at ±89)
- event_y1             : Y coordinate (-42.5 to 42.5, center=0, boards at ±42.5)

LOCATION 2 - End/Secondary (where event ended, e.g., pass target):
- event_x2             : X coordinate end location
- event_y2             : Y coordinate end location

LOCATION 3 - Tertiary (optional, e.g., deflection point, rebound):
- event_x3             : X coordinate tertiary
- event_y3             : Y coordinate tertiary

PUCK TRACKING (in same file as event locations):
- puck_start_x         : Puck X at event start
- puck_start_y         : Puck Y at event start  
- puck_end_x           : Puck X at event end
- puck_end_y           : Puck Y at event end


SHOT_LOCATIONS CSV STRUCTURE:
=============================
Each CSV in shots/shot_locations/ contains:

- event_index          : Links to shot events in fact_event_players
- shot_net_x           : X on net (-3 to 3, left post to right post)
- shot_net_y           : Y on net (0 to 4, ice level to crossbar)
- shot_result          : Goal, Save, Miss, Post, Crossbar, Block


COORDINATE SYSTEMS:
==================
RINK (from shot-plotter.netlify.app/ice-hockey):
    ┌──────────────────────────────────────────────────────────────┐
    │                           +42.5 (boards)                      │
    │                                                               │
    │  -100        -25 (blue)    0 (center)    +25 (blue)     +100 │
    │   [G]          │            │              │             [G]  │
    │                │     NZ     │              │                  │
    │   DZ           │            │              │        OZ        │
    │                                                               │
    │                           -42.5 (boards)                      │
    └──────────────────────────────────────────────────────────────┘

NET (from shot-plotter.netlify.app/ice-hockey-net-nhl):
    ┌───────────────────────────┐  +4 (crossbar)
    │                           │
    │   -3       0       +3     │
    │  (left)  (center) (right) │
    │                           │
    └───────────────────────────┘  0 (ice)

=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List, Union
from dataclasses import dataclass

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RinkBounds:
    """NHL rink coordinate bounds."""
    x_min: float = -100.0
    x_max: float = 100.0
    y_min: float = -42.5
    y_max: float = 42.5
    
    offensive_blue_line: float = 25.0
    defensive_blue_line: float = -25.0
    goal_line: float = 89.0
    
    high_danger_radius: float = 20.0
    medium_danger_radius: float = 35.0


@dataclass
class NetBounds:
    """NHL net coordinate bounds."""
    x_min: float = -3.0
    x_max: float = 3.0
    y_min: float = 0.0
    y_max: float = 4.0


class XYLoader:
    """
    Load XY coordinate data from game folders.
    
    Handles multiple CSV files per subfolder - all CSVs are appended together.
    
    Usage:
        loader = XYLoader(config, game_id=18969)
        data = loader.load_all()
        
        # data['event_locations'] contains ALL event location CSVs combined
        # data['shot_net_locations'] contains ALL shot location CSVs combined
    """
    
    def __init__(self, config, game_id: int):
        """
        Initialize XY loader.
        
        Args:
            config: Configuration with paths
            game_id: Game identifier
        """
        self.config = config
        self.game_id = game_id
        self.game_dir = config.paths.game_data_root / str(game_id)
        
        self.rink = RinkBounds()
        self.net = NetBounds()
        
        logger.info(f"XYLoader initialized for game {game_id}")
        logger.info(f"Looking in: {self.game_dir}")
    
    def load_all(self) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Load all XY data for the game.
        
        Returns:
            Dictionary with:
            - event_locations: Combined from xy/event_locations/*.csv
            - shot_net_locations: Combined from shots/shot_locations/*.csv
            - video_links: From video/video_links.csv
        """
        return {
            'event_locations': self.load_event_locations(),
            'shot_net_locations': self.load_shot_net_locations(),
            'video_links': self.load_video_links(),
        }
    
    def load_event_locations(self) -> Optional[pd.DataFrame]:
        """
        Load event locations from xy/event_locations/ subfolder.
        
        ALL CSV files in the subfolder are loaded and appended together.
        Includes both event XY coordinates AND puck tracking.
        
        Expected columns per CSV:
            - event_index, player_game_number, player_team
            - event_x1, event_y1 (start/primary location)
            - event_x2, event_y2 (end/secondary location)
            - event_x3, event_y3 (tertiary location - optional)
            - puck_start_x, puck_start_y, puck_end_x, puck_end_y
        
        Returns:
            Combined DataFrame or None if no files found
        """
        # Check for subfolder structure
        subfolder_paths = [
            self.game_dir / 'xy' / 'event_locations',
            self.game_dir / 'xy' / 'events',
            self.game_dir / 'xy' / 'puck_tracking',  # Alternative name
        ]
        
        # Also check flat structure as fallback
        flat_paths = [
            self.game_dir / 'xy',
        ]
        
        df = self._load_all_csvs_from_folders(subfolder_paths + flat_paths)
        
        if df is not None and len(df) > 0:
            # Validate all coordinate pairs
            coordinate_pairs = [
                ('event_x1', 'event_y1'),
                ('event_x2', 'event_y2'),
                ('event_x3', 'event_y3'),
                ('puck_start_x', 'puck_start_y'),
                ('puck_end_x', 'puck_end_y'),
            ]
            
            for x_col, y_col in coordinate_pairs:
                df = self._validate_rink_coordinates(df, x_col, y_col)
            
            # Add calculated fields
            df = self._add_zone_from_coordinates(df)
            df = self._add_distance_to_goal(df)
            df = self._add_danger_zone(df)
            df = self._add_shot_angle(df)
            df = self._add_event_distance(df)
            df = self._add_puck_travel_distance(df)
            
            logger.info(f"Loaded event locations: {len(df)} rows from {df['_source_file'].nunique()} files")
        
        return df
    
    def load_shot_net_locations(self) -> Optional[pd.DataFrame]:
        """
        Load shot net locations from shots/shot_locations/ subfolder.
        
        ALL CSV files in the subfolder are loaded and appended together.
        
        Expected columns per CSV:
            - event_index (links to shot events)
            - shot_net_x (-3 to 3, left to right post)
            - shot_net_y (0 to 4, ice to crossbar)
            - shot_result (Goal, Save, Miss, Post, Crossbar, Block)
        
        Returns:
            Combined DataFrame or None if no files found
        """
        subfolder_paths = [
            self.game_dir / 'shots' / 'shot_locations',
            self.game_dir / 'shots' / 'shot_net',
        ]
        
        flat_paths = [
            self.game_dir / 'shots',
        ]
        
        df = self._load_all_csvs_from_folders(subfolder_paths + flat_paths)
        
        if df is not None and len(df) > 0:
            df = self._validate_net_coordinates(df, 'shot_net_x', 'shot_net_y')
            df = self._add_net_zone(df)
            
            logger.info(f"Loaded shot net locations: {len(df)} rows")
        
        return df
    
    def load_video_links(self) -> Optional[pd.DataFrame]:
        """
        Load video links from video/ folder.
        
        Expected columns:
            - event_index
            - video_url (YouTube URL)
            - video_start_time (timestamp in video)
            - video_end_time (optional)
            - camera_angle (optional)
        
        Returns:
            DataFrame or None
        """
        paths = [
            self.game_dir / 'video' / 'video_links.csv',
            self.game_dir / 'video_links.csv',
        ]
        
        for path in paths:
            if path.exists():
                df = pd.read_csv(path)
                df['_source_file'] = path.name
                logger.info(f"Loaded video links: {len(df)} rows")
                return df
        
        return None
    
    # =========================================================================
    # MULTI-FILE LOADING
    # =========================================================================
    
    def _load_all_csvs_from_folders(self, folder_paths: List[Path]) -> Optional[pd.DataFrame]:
        """
        Load and append ALL CSV files from given folders.
        
        Args:
            folder_paths: List of folders to search (in priority order)
        
        Returns:
            Combined DataFrame or None
        """
        all_dataframes = []
        files_loaded = []
        
        for folder in folder_paths:
            if not folder.exists():
                continue
            
            # Find all CSVs in folder and subfolders
            csv_files = list(folder.glob('*.csv'))
            csv_files += list(folder.glob('**/*.csv'))
            
            # Remove duplicates and temp files
            csv_files = list(set(csv_files))
            csv_files = [f for f in csv_files if not f.name.startswith('~')]
            csv_files = [f for f in csv_files if not f.name.startswith('.')]
            
            for csv_file in sorted(csv_files):
                try:
                    df = pd.read_csv(csv_file)
                    df['_source_file'] = csv_file.name
                    df['_source_folder'] = csv_file.parent.name
                    all_dataframes.append(df)
                    files_loaded.append(csv_file.name)
                    logger.debug(f"  Loaded: {csv_file.name} ({len(df)} rows)")
                except Exception as e:
                    logger.warning(f"  Failed to load {csv_file}: {e}")
        
        if not all_dataframes:
            logger.debug(f"No CSV files found in any folder")
            return None
        
        # Combine all DataFrames
        combined = pd.concat(all_dataframes, ignore_index=True)
        
        # Remove duplicate event_index (keep last/most recent)
        if 'event_index' in combined.columns:
            before = len(combined)
            combined = combined.drop_duplicates(subset=['event_index'], keep='last')
            dupes_removed = before - len(combined)
            if dupes_removed > 0:
                logger.info(f"  Removed {dupes_removed} duplicate event_index rows")
        
        logger.info(f"  Combined {len(files_loaded)} files: {', '.join(files_loaded)}")
        return combined
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    def _validate_rink_coordinates(self, df: pd.DataFrame, x_col: str, y_col: str) -> pd.DataFrame:
        """Validate and clip rink coordinates to valid bounds."""
        if x_col in df.columns:
            df[x_col] = pd.to_numeric(df[x_col], errors='coerce')
            df[x_col] = df[x_col].clip(self.rink.x_min, self.rink.x_max)
        
        if y_col in df.columns:
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df[y_col] = df[y_col].clip(self.rink.y_min, self.rink.y_max)
        
        return df
    
    def _validate_net_coordinates(self, df: pd.DataFrame, x_col: str, y_col: str) -> pd.DataFrame:
        """Validate and clip net coordinates to valid bounds."""
        if x_col in df.columns:
            df[x_col] = pd.to_numeric(df[x_col], errors='coerce')
            df[x_col] = df[x_col].clip(self.net.x_min, self.net.x_max)
        
        if y_col in df.columns:
            df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
            df[y_col] = df[y_col].clip(self.net.y_min, self.net.y_max)
        
        return df
    
    # =========================================================================
    # CALCULATED FIELDS
    # =========================================================================
    
    def _add_zone_from_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add zone based on X coordinate."""
        if 'event_x1' not in df.columns:
            return df
        
        def get_zone(x):
            if pd.isna(x):
                return None
            if x > self.rink.offensive_blue_line:
                return 'OZ'
            elif x < self.rink.defensive_blue_line:
                return 'DZ'
            else:
                return 'NZ'
        
        df['calculated_zone'] = df['event_x1'].apply(get_zone)
        
        # End zone if x2 exists
        if 'event_x2' in df.columns:
            df['calculated_end_zone'] = df['event_x2'].apply(get_zone)
        
        return df
    
    def _add_distance_to_goal(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate distance from event to goal."""
        if 'event_x1' not in df.columns or 'event_y1' not in df.columns:
            return df
        
        goal_x = self.rink.goal_line
        df['distance_to_goal'] = np.sqrt(
            (goal_x - df['event_x1'].fillna(0))**2 +
            df['event_y1'].fillna(0)**2
        ).round(1)
        
        return df
    
    def _add_danger_zone(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify shot danger based on distance."""
        if 'distance_to_goal' not in df.columns:
            return df
        
        def get_danger(dist):
            if pd.isna(dist):
                return None
            if dist <= self.rink.high_danger_radius:
                return 'HD'  # High danger
            elif dist <= self.rink.medium_danger_radius:
                return 'MD'  # Medium danger
            else:
                return 'LD'  # Low danger
        
        df['danger_zone'] = df['distance_to_goal'].apply(get_danger)
        return df
    
    def _add_shot_angle(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate shot angle (0 = straight on, 90 = from side)."""
        if 'event_x1' not in df.columns or 'event_y1' not in df.columns:
            return df
        
        goal_x = self.rink.goal_line
        df['shot_angle'] = np.degrees(np.arctan2(
            df['event_y1'].fillna(0).abs(),
            (goal_x - df['event_x1'].fillna(0)).clip(lower=0.1)
        )).round(1)
        
        return df
    
    def _add_event_distance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate distance from event start to end."""
        if not all(c in df.columns for c in ['event_x1', 'event_y1', 'event_x2', 'event_y2']):
            return df
        
        df['event_travel_distance'] = np.sqrt(
            (df['event_x2'].fillna(df['event_x1']) - df['event_x1'])**2 +
            (df['event_y2'].fillna(df['event_y1']) - df['event_y1'])**2
        ).round(1)
        
        return df
    
    def _add_puck_travel_distance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate puck travel distance."""
        cols = ['puck_start_x', 'puck_start_y', 'puck_end_x', 'puck_end_y']
        if not all(c in df.columns for c in cols):
            return df
        
        df['puck_travel_distance'] = np.sqrt(
            (df['puck_end_x'].fillna(df['puck_start_x']) - df['puck_start_x'].fillna(0))**2 +
            (df['puck_end_y'].fillna(df['puck_start_y']) - df['puck_start_y'].fillna(0))**2
        ).round(1)
        
        return df
    
    def _add_net_zone(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add net zone classification for shot locations."""
        if 'shot_net_x' not in df.columns or 'shot_net_y' not in df.columns:
            return df
        
        def get_net_zone(row):
            x, y = row.get('shot_net_x'), row.get('shot_net_y')
            if pd.isna(x) or pd.isna(y):
                return None
            
            # Horizontal
            if x < -1:
                h = 'left'
            elif x > 1:
                h = 'right'
            else:
                h = 'center'
            
            # Vertical
            if y < 1.5:
                v = 'low'
            elif y > 2.5:
                v = 'high'
            else:
                v = 'mid'
            
            return f"{v}_{h}"
        
        df['net_zone'] = df.apply(get_net_zone, axis=1)
        return df
    
    # =========================================================================
    # MERGE WITH EVENTS
    # =========================================================================
    
    def merge_with_events(self, events_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge all XY data into events DataFrame.
        
        Args:
            events_df: Events to merge XY data into
        
        Returns:
            Events DataFrame with XY columns added
        """
        result = events_df.copy()
        xy_data = self.load_all()
        
        # Merge event locations (includes puck tracking)
        if xy_data['event_locations'] is not None:
            loc_df = xy_data['event_locations'].drop(
                columns=['_source_file', '_source_folder'], 
                errors='ignore'
            )
            result = result.merge(loc_df, on='event_index', how='left', suffixes=('', '_xy'))
            logger.info(f"Merged event locations: {len(loc_df)} rows")
        
        # Merge shot net locations
        if xy_data['shot_net_locations'] is not None:
            shot_df = xy_data['shot_net_locations'].drop(
                columns=['_source_file', '_source_folder'], 
                errors='ignore'
            )
            result = result.merge(shot_df, on='event_index', how='left', suffixes=('', '_shot'))
            logger.info(f"Merged shot net locations: {len(shot_df)} rows")
        
        # Merge video links
        if xy_data['video_links'] is not None:
            video_df = xy_data['video_links'].drop(columns=['_source_file'], errors='ignore')
            result = result.merge(video_df, on='event_index', how='left', suffixes=('', '_video'))
            logger.info(f"Merged video links: {len(video_df)} rows")
        
        return result
    
    def get_status(self) -> Dict:
        """Get summary of available XY files."""
        status = {
            'game_id': self.game_id,
            'game_dir': str(self.game_dir),
            'exists': self.game_dir.exists(),
            'event_locations': {'found': False, 'files': [], 'total_rows': 0},
            'shot_locations': {'found': False, 'files': [], 'total_rows': 0},
            'video_links': {'found': False, 'files': [], 'total_rows': 0},
        }
        
        # Load and count
        xy_data = self.load_all()
        
        if xy_data['event_locations'] is not None:
            df = xy_data['event_locations']
            status['event_locations']['found'] = True
            status['event_locations']['files'] = df['_source_file'].unique().tolist()
            status['event_locations']['total_rows'] = len(df)
        
        if xy_data['shot_net_locations'] is not None:
            df = xy_data['shot_net_locations']
            status['shot_locations']['found'] = True
            status['shot_locations']['files'] = df['_source_file'].unique().tolist()
            status['shot_locations']['total_rows'] = len(df)
        
        if xy_data['video_links'] is not None:
            df = xy_data['video_links']
            status['video_links']['found'] = True
            status['video_links']['files'] = [df['_source_file'].iloc[0]]
            status['video_links']['total_rows'] = len(df)
        
        return status
    
    def print_status(self):
        """Print status of available XY files."""
        status = self.get_status()
        
        print(f"\n  XY Data Status for Game {self.game_id}")
        print(f"  " + "-" * 50)
        print(f"  Game folder: {'EXISTS' if status['exists'] else 'NOT FOUND'}")
        print(f"  Path: {status['game_dir']}")
        print()
        
        for data_type in ['event_locations', 'shot_locations', 'video_links']:
            info = status[data_type]
            if info['found']:
                print(f"  ✓ {data_type}:")
                print(f"      Files: {', '.join(info['files'])}")
                print(f"      Rows: {info['total_rows']}")
            else:
                print(f"  ○ {data_type}: Not found (optional)")


# =============================================================================
# xG CALCULATION
# =============================================================================

def calculate_xg(x: float, y: float,
                 shot_type: str = None,
                 is_rebound: bool = False,
                 is_rush: bool = False,
                 is_one_timer: bool = False,
                 shooter_skill: float = 4.0,
                 goalie_skill: float = 4.0) -> float:
    """
    Calculate expected goals (xG) from shot coordinates and context.
    
    Based on distance, angle, shot type, and situational modifiers.
    
    Args:
        x, y: Shot coordinates on rink
        shot_type: Wrist, Slap, Snap, Backhand, Tip, Wrap
        is_rebound: Rebound shot (higher xG)
        is_rush: Rush/breakaway (higher xG)
        is_one_timer: One-timer shot (higher xG)
        shooter_skill: Shooter skill rating 2-6 (default 4)
        goalie_skill: Goalie skill rating 2-6 (default 4)
    
    Returns:
        xG probability (0.0 to 1.0)
    """
    if pd.isna(x) or pd.isna(y):
        return 0.05  # Default for unknown location
    
    # Distance to goal
    goal_x = 89
    distance = np.sqrt((goal_x - x)**2 + y**2)
    
    # Angle (0 = straight on, 90 = from side)
    angle = np.degrees(np.arctan2(abs(y), max(goal_x - x, 0.1)))
    
    # Base xG from distance (exponential decay)
    base_xg = 0.35 * np.exp(-0.045 * distance)
    
    # Angle penalty (shots from center have higher xG)
    angle_factor = np.cos(np.radians(angle * 0.8))
    base_xg *= max(angle_factor, 0.3)
    
    # Shot type modifiers
    shot_type_mods = {
        'Wrist': 1.0,
        'Snap': 1.15,
        'Slap': 0.85,
        'Backhand': 0.75,
        'Tip': 1.4,
        'Wrap': 0.5,
    }
    if shot_type and shot_type in shot_type_mods:
        base_xg *= shot_type_mods[shot_type]
    
    # Situational modifiers
    if is_rebound:
        base_xg *= 1.6
    if is_rush:
        base_xg *= 1.4
    if is_one_timer:
        base_xg *= 1.3
    
    # Skill adjustment
    skill_diff = (shooter_skill - goalie_skill) * 0.05
    base_xg *= (1 + skill_diff)
    
    # Cap at reasonable range
    return round(min(max(base_xg, 0.01), 0.70), 3)
