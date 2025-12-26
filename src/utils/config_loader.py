"""
=============================================================================
CONFIGURATION LOADER
=============================================================================
File: src/utils/config_loader.py

PURPOSE:
    Load and validate configuration from config.ini files.
    Provides typed access to all settings.

USAGE:
    from src.utils.config_loader import Config
    config = Config()
    db_host = config.database.host
=============================================================================
"""

import configparser
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class DatabaseConfig:
    """Database connection settings."""
    host: str
    port: int
    database: str
    user: str
    password: str
    schema_staging: str
    schema_mart: str

@dataclass
class PathsConfig:
    """File path settings."""
    blb_tables_file: Path
    game_data_root: Path
    output_dir: Path
    processed_dir: Path
    backup_dir: Path
    log_dir: Path

@dataclass
class ProcessingConfig:
    """Processing settings."""
    batch_size: int
    parallel_workers: int
    skill_rating_min: int
    skill_rating_max: int
    default_skill_rating: int

class Config:
    """Main configuration class."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Load configuration."""
        self._project_root = Path(__file__).parent.parent.parent
        self._config_path = self._find_config(config_path)
        self._parser = configparser.ConfigParser()
        self._parser.read(self._config_path)
        
        self.database = self._load_database()
        self.paths = self._load_paths()
        self.processing = self._load_processing()
    
    def _find_config(self, explicit: Optional[str]) -> Path:
        """Find config file."""
        if explicit and Path(explicit).exists():
            return Path(explicit)
        
        config_dir = self._project_root / "config"
        for name in ["config_local.ini", "config.ini"]:
            path = config_dir / name
            if path.exists():
                return path
        
        raise FileNotFoundError("No config file found")
    
    def _get(self, section: str, key: str, fallback: str = None) -> str:
        """Get config value."""
        return self._parser.get(section, key, fallback=fallback)
    
    def _get_int(self, section: str, key: str, fallback: int = None) -> int:
        """Get integer config value."""
        return int(self._get(section, key, str(fallback)))
    
    def _get_path(self, section: str, key: str, fallback: str = None) -> Path:
        """Get path config value."""
        path = Path(self._get(section, key, fallback))
        if not path.is_absolute():
            path = self._project_root / path
        return path
    
    def _load_database(self) -> DatabaseConfig:
        """Load database config."""
        return DatabaseConfig(
            host=self._get('database', 'host', 'localhost'),
            port=self._get_int('database', 'port', 5432),
            database=self._get('database', 'database', 'hockey_analytics'),
            user=self._get('database', 'user', 'postgres'),
            password=self._get('database', 'password', ''),
            schema_staging=self._get('database', 'schema_staging', 'staging'),
            schema_mart=self._get('database', 'schema_mart', 'hockey_mart')
        )
    
    def _load_paths(self) -> PathsConfig:
        """Load paths config."""
        return PathsConfig(
            blb_tables_file=self._get_path('paths', 'blb_tables_file'),
            game_data_root=self._get_path('paths', 'game_data_root'),
            output_dir=self._get_path('paths', 'output_dir'),
            processed_dir=self._get_path('paths', 'processed_dir'),
            backup_dir=self._get_path('paths', 'backup_dir'),
            log_dir=self._get_path('paths', 'log_dir')
        )
    
    def _load_processing(self) -> ProcessingConfig:
        """Load processing config."""
        return ProcessingConfig(
            batch_size=self._get_int('processing', 'batch_size', 1000),
            parallel_workers=self._get_int('processing', 'parallel_workers', 4),
            skill_rating_min=self._get_int('processing', 'skill_rating_min', 2),
            skill_rating_max=self._get_int('processing', 'skill_rating_max', 6),
            default_skill_rating=self._get_int('processing', 'default_skill_rating', 4)
        )
    
    @property
    def project_root(self) -> Path:
        """Get project root."""
        return self._project_root
