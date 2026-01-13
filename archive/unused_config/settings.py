"""
=============================================================================
CONFIGURATION MANAGEMENT
=============================================================================
File: config/settings.py

Central configuration for the hockey analytics pipeline.
=============================================================================
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import os


@dataclass
class PathConfig:
    """Path configuration."""
    
    # Project root
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    
    # Data directories
    @property
    def data_root(self) -> Path:
        return self.project_root / 'data'
    
    @property
    def raw_data_root(self) -> Path:
        return self.data_root / 'raw'
    
    @property
    def game_data_root(self) -> Path:
        return self.raw_data_root / 'games'
    
    @property
    def output_dir(self) -> Path:
        return self.data_root / 'output'
    
    @property
    def blb_tables_file(self) -> Path:
        return self.raw_data_root / 'BLB_Tables.xlsx'
    
    def get_game_dir(self, game_id: int) -> Path:
        return self.game_data_root / str(game_id)
    
    def get_tracking_file(self, game_id: int) -> Path:
        return self.get_game_dir(game_id) / f"{game_id}_tracking.xlsx"
    
    def get_xy_dir(self, game_id: int) -> Path:
        return self.get_game_dir(game_id) / 'xy'
    
    def get_shots_dir(self, game_id: int) -> Path:
        return self.get_game_dir(game_id) / 'shots'


@dataclass
class ProcessingConfig:
    """Processing configuration."""
    
    # Append mode for tracking tables
    append_mode: bool = True
    
    # Include XY data if available
    include_xy: bool = True
    
    # Default skill rating when not found
    default_skill_rating: float = 4.0
    
    # Time bucket size (minutes)
    time_bucket_size: int = 5
    
    # Periods
    periods: list = field(default_factory=lambda: [1, 2, 3, 'OT', 'SO'])


@dataclass
class Config:
    """Main configuration class."""
    
    paths: PathConfig = field(default_factory=PathConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    
    def __post_init__(self):
        # Create directories if they don't exist
        self.paths.output_dir.mkdir(parents=True, exist_ok=True)
        self.paths.game_data_root.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables."""
        config = cls()
        
        # Override paths from environment if set
        if os.getenv('HOCKEY_DATA_ROOT'):
            config.paths.project_root = Path(os.getenv('HOCKEY_DATA_ROOT'))
        
        return config
