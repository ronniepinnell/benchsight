"""
BenchSight Configuration Loader

Centralized configuration management for all BenchSight scripts.
Loads settings from config files and environment variables.

Priority order (highest to lowest):
1. Environment variables (SUPABASE_URL, SUPABASE_SERVICE_KEY)
2. BENCHSIGHT_ENV-specific config (config.dev.ini or config.prod.ini)
3. config_local.ini (legacy fallback - not committed to git)
4. config.ini (default settings)

Environment Selection:
    export BENCHSIGHT_ENV=dev   # Use config.dev.ini
    export BENCHSIGHT_ENV=prod  # Use config.prod.ini
    (unset)                     # Use config_local.ini (legacy)

Usage:
    from config.config_loader import config
    
    # Get Supabase credentials
    url = config.supabase_url
    key = config.supabase_service_key
    
    # Get paths
    data_dir = config.data_dir
    
    # Get loader settings
    batch_size = config.batch_size
"""

import os
import configparser
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class BenchSightConfig:
    """Configuration container for BenchSight"""
    
    # Supabase
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_anon_key: str = ""
    
    # Paths
    project_root: Path = Path(".")
    data_dir: Path = Path("data/output")
    raw_dir: Path = Path("data/raw")
    log_dir: Path = Path("logs")
    
    # Loader settings
    batch_size: int = 500
    verbose: bool = True
    default_operation: str = "upsert"
    
    # ETL settings
    games: list = None
    process_tracking: bool = True
    enhance_stats: bool = True
    
    def __post_init__(self):
        if self.games is None:
            self.games = []
    
    @property
    def is_configured(self) -> bool:
        """Check if Supabase credentials are configured"""
        return bool(self.supabase_url and self.supabase_service_key)
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration and return (valid, errors)"""
        errors = []
        
        if not self.supabase_url:
            errors.append("Supabase URL not configured")
        elif not self.supabase_url.startswith("https://"):
            errors.append("Supabase URL must start with https://")
        
        if not self.supabase_service_key:
            errors.append("Supabase service key not configured")
        elif len(self.supabase_service_key) < 100:
            errors.append("Supabase service key appears invalid (too short)")
        
        if not self.data_dir.exists():
            errors.append(f"Data directory not found: {self.data_dir}")
        
        return len(errors) == 0, errors


def find_project_root() -> Path:
    """Find the project root directory"""
    # Start from this file's location
    current = Path(__file__).resolve().parent
    
    # Look for markers that indicate project root
    markers = ['etl.py', 'README.md', 'config', 'src']
    
    for _ in range(5):  # Max 5 levels up
        if all((current / marker).exists() for marker in ['config', 'src']):
            return current
        current = current.parent
    
    # Fallback to current working directory
    return Path.cwd()


def load_config(config_path: Optional[Path] = None) -> BenchSightConfig:
    """
    Load configuration from files and environment.
    
    Args:
        config_path: Optional explicit path to config file
    
    Returns:
        BenchSightConfig instance
    """
    config = BenchSightConfig()
    project_root = find_project_root()
    config.project_root = project_root
    
    # Determine config file paths
    config_dir = project_root / "config"
    
    if config_path:
        config_files = [config_path]
    else:
        # Check for BENCHSIGHT_ENV to determine which config to load
        env_name = os.environ.get('BENCHSIGHT_ENV', '').lower()

        config_files = [config_dir / "config.ini"]  # Base defaults

        if env_name in ('dev', 'development'):
            # Development environment
            env_config = config_dir / "config.dev.ini"
            if env_config.exists():
                config_files.append(env_config)
            else:
                print(f"⚠️  BENCHSIGHT_ENV=dev but config.dev.ini not found")
        elif env_name in ('prod', 'production'):
            # Production environment
            env_config = config_dir / "config.prod.ini"
            if env_config.exists():
                config_files.append(env_config)
            else:
                print(f"⚠️  BENCHSIGHT_ENV=prod but config.prod.ini not found")
        else:
            # Legacy fallback: use config_local.ini
            config_files.append(config_dir / "config_local.ini")

    # Check if any config exists, if not, warn user
    local_config = config_dir / "config_local.ini"
    example_config = config_dir / "config_local.ini.example"
    env_name = os.environ.get('BENCHSIGHT_ENV', '').lower()

    if not env_name and not local_config.exists() and example_config.exists():
        print(f"⚠️  Config file not found: {local_config}")
        print(f"   Option 1: Set BENCHSIGHT_ENV=dev or BENCHSIGHT_ENV=prod")
        print(f"   Option 2: Copy the example: cp {example_config} {local_config}")
        print()
    
    # Load from config files
    parser = configparser.ConfigParser()
    
    for cf in config_files:
        if cf.exists():
            parser.read(cf)
    
    # Extract Supabase settings
    if parser.has_section('supabase'):
        config.supabase_url = parser.get('supabase', 'url', fallback='')
        config.supabase_service_key = parser.get('supabase', 'service_key', fallback='')
        if not config.supabase_service_key:
            config.supabase_service_key = parser.get('supabase', 'key', fallback='')
        config.supabase_anon_key = parser.get('supabase', 'anon_key', fallback='')
    
    # Extract path settings
    if parser.has_section('paths'):
        config.data_dir = project_root / parser.get('paths', 'data_dir', fallback='data/output')
        config.raw_dir = project_root / parser.get('paths', 'raw_dir', fallback='data/raw')
        config.log_dir = project_root / parser.get('paths', 'log_dir', fallback='logs')
    else:
        config.data_dir = project_root / "data" / "output"
        config.raw_dir = project_root / "data" / "raw"
        config.log_dir = project_root / "logs"
    
    # Extract loader settings
    if parser.has_section('loader'):
        config.batch_size = parser.getint('loader', 'batch_size', fallback=500)
        config.verbose = parser.getboolean('loader', 'verbose', fallback=True)
        config.default_operation = parser.get('loader', 'default_operation', fallback='upsert')
    
    # Extract ETL settings
    if parser.has_section('etl'):
        games_str = parser.get('etl', 'games', fallback='')
        if games_str and games_str.lower() != 'all':
            config.games = [int(g.strip()) for g in games_str.split(',') if g.strip()]
        config.process_tracking = parser.getboolean('etl', 'process_tracking', fallback=True)
        config.enhance_stats = parser.getboolean('etl', 'enhance_stats', fallback=True)
    
    # Override with environment variables (highest priority)
    env_url = os.environ.get('SUPABASE_URL')
    env_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if env_url:
        config.supabase_url = env_url
    if env_key:
        config.supabase_service_key = env_key
    
    return config


def get_config() -> BenchSightConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config() -> BenchSightConfig:
    """Force reload of configuration"""
    global _config
    _config = load_config()
    return _config


# Global config instance
_config: Optional[BenchSightConfig] = None

# Convenience access
config = property(lambda self: get_config())


# ============================================================
# CLI for testing configuration
# ============================================================

def main():
    """Test configuration loading"""
    import sys
    
    print("=" * 60)
    print("BENCHSIGHT CONFIGURATION")
    print("=" * 60)
    
    cfg = load_config()
    
    print(f"\nProject Root: {cfg.project_root}")
    print(f"Data Directory: {cfg.data_dir}")
    print(f"  Exists: {cfg.data_dir.exists()}")
    print(f"Log Directory: {cfg.log_dir}")
    
    print(f"\nSupabase URL: {cfg.supabase_url[:50]}..." if cfg.supabase_url else "\nSupabase URL: NOT SET")
    print(f"Service Key: {'*' * 20}...{cfg.supabase_service_key[-10:]}" if cfg.supabase_service_key else "Service Key: NOT SET")
    
    print(f"\nLoader Settings:")
    print(f"  Batch Size: {cfg.batch_size}")
    print(f"  Verbose: {cfg.verbose}")
    print(f"  Default Operation: {cfg.default_operation}")
    
    print(f"\nETL Settings:")
    print(f"  Games: {cfg.games or 'all'}")
    print(f"  Process Tracking: {cfg.process_tracking}")
    print(f"  Enhance Stats: {cfg.enhance_stats}")
    
    # Validate
    valid, errors = cfg.validate()
    print(f"\n{'✓ Configuration Valid' if valid else '✗ Configuration Invalid'}")
    if errors:
        for err in errors:
            print(f"  - {err}")
    
    return 0 if valid else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
