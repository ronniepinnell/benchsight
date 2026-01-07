"""
=============================================================================
BLB TABLES LOADER
=============================================================================
File: src/ingestion/blb_loader.py

PURPOSE:
    Load reference tables from BLB_Tables.xlsx.
    These are relatively static dimension tables.

TABLES LOADED:
    - dim_player: Player master data
    - dim_team: Team information
    - dim_season: Season definitions
    - dim_schedule: Game schedule
    - fact_gameroster: Game rosters
    - dim_rink_zone: Rink zone coordinates
    - dim_rink_zone: Detailed rink zones
    - And others...
=============================================================================
"""

import pandas as pd
from pathlib import Path
from typing import Dict
from src.utils.logger import get_logger

logger = get_logger(__name__)

class BLBLoader:
    """Load BLB reference tables."""
    
    # Tables to load from BLB_Tables.xlsx
    TABLES = [
        'dim_player',
        'dim_team',
        'dim_season',
        'dim_schedule',
        'dim_league',
        'dim_rink_zone',
        'dim_rink_zone',
        'dim_randomnames',
        'dim_playerurlref',
        'fact_gameroster',
        'fact_leadership',
        'fact_registration',
        'fact_draft',
        'Fact_PlayerGames'
    ]
    
    def __init__(self, file_path: str):
        """Initialize loader."""
        self.file_path = Path(file_path)
        logger.info(f"BLBLoader initialized: {self.file_path}")
    
    def load_all(self) -> Dict[str, pd.DataFrame]:
        """
        Load all BLB tables.
        
        Returns:
            Dictionary mapping table name to DataFrame
        """
        logger.info("Loading BLB tables...")
        
        xlsx = pd.ExcelFile(self.file_path)
        available_sheets = xlsx.sheet_names
        
        tables = {}
        
        for sheet_name in available_sheets:
            try:
                df = pd.read_excel(xlsx, sheet_name=sheet_name)
                
                # Clean column names
                df.columns = df.columns.str.strip()
                
                # Store with standardized name
                table_name = sheet_name.lower().replace(' ', '_')
                tables[table_name] = df
                
                logger.debug(f"Loaded {table_name}: {len(df)} rows")
                
            except Exception as e:
                logger.warning(f"Failed to load sheet {sheet_name}: {e}")
        
        logger.info(f"Loaded {len(tables)} tables from BLB_Tables.xlsx")
        return tables
    
    def load_table(self, table_name: str) -> pd.DataFrame:
        """Load a specific table."""
        xlsx = pd.ExcelFile(self.file_path)
        
        # Find matching sheet (case insensitive)
        for sheet in xlsx.sheet_names:
            if sheet.lower() == table_name.lower():
                return pd.read_excel(xlsx, sheet_name=sheet)
        
        raise ValueError(f"Table not found: {table_name}")
