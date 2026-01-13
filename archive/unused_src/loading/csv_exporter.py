"""
=============================================================================
CSV EXPORTER
=============================================================================
File: src/loading/csv_exporter.py

Export DataFrames to CSV with append/deduplication logic.
=============================================================================
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List

from src.utils.logger import get_logger

logger = get_logger(__name__)


class CSVExporter:
    """
    Export DataFrames to CSV files with intelligent append/overwrite logic.
    
    Logic:
    - BLB tables: Overwrite (master data from external source)
    - Dimension tables: Overwrite (static lookups)
    - Game tracking tables: Append with deduplication by primary key
    """
    
    # Primary keys for deduplication
    PRIMARY_KEYS = {
        'fact_event_players': 'event_key',
        'fact_event_players_tracking': 'event_player_key',
        'fact_shifts': 'shift_key',
        'fact_shift_players_tracking': 'shift_player_key',
        'fact_box_score_tracking': 'player_game_key',
        'fact_linked_events_tracking': 'chain_id',
        'fact_sequences_tracking': 'sequence_key',
        'fact_plays_tracking': 'play_key',
        'dim_game_players_tracking': 'player_game_key',
    }
    
    def __init__(self, output_dir: Path):
        """
        Initialize exporter.
        
        Args:
            output_dir: Directory for CSV output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"CSVExporter initialized: {output_dir}")
    
    def export_all(self, tables: Dict[str, pd.DataFrame], 
                   append_tracking: bool = True) -> Dict[str, int]:
        """
        Export all tables.
        
        Args:
            tables: Dictionary of table name to DataFrame
            append_tracking: If True, append to tracking tables
        
        Returns:
            Dictionary of table name to row count
        """
        results = {}
        
        for name, df in tables.items():
            if len(df) == 0:
                logger.debug(f"Skipping empty table: {name}")
                continue
            
            is_tracking = 'tracking' in name
            
            if is_tracking and append_tracking:
                rows = self.append_with_dedup(name, df)
            else:
                rows = self.overwrite(name, df)
            
            results[name] = rows
        
        return results
    
    def overwrite(self, table_name: str, df: pd.DataFrame) -> int:
        """
        Overwrite a CSV file.
        
        Args:
            table_name: Name of the table
            df: DataFrame to write
        
        Returns:
            Number of rows written
        """
        filepath = self.output_dir / f"{table_name}.csv"
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"Wrote {table_name}: {len(df)} rows")
        return len(df)
    
    def append_with_dedup(self, table_name: str, df: pd.DataFrame) -> int:
        """
        Append to CSV with deduplication by primary key.
        
        Args:
            table_name: Name of the table
            df: DataFrame to append
        
        Returns:
            Number of rows in final table
        """
        filepath = self.output_dir / f"{table_name}.csv"
        pk = self.PRIMARY_KEYS.get(table_name)
        
        if filepath.exists():
            existing = pd.read_csv(filepath)
            combined = pd.concat([existing, df], ignore_index=True)
            
            if pk and pk in combined.columns:
                before = len(combined)
                combined = combined.drop_duplicates(subset=[pk], keep='last')
                dupes_removed = before - len(combined)
                
                net_new = len(df) - dupes_removed
                logger.info(f"Appended {table_name}: {len(combined)} rows ({net_new} new)")
            else:
                logger.info(f"Appended {table_name}: {len(combined)} rows")
            
            combined.to_csv(filepath, index=False, encoding='utf-8-sig')
            return len(combined)
        else:
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"Created {table_name}: {len(df)} rows")
            return len(df)
    
    def remove_game(self, game_id: int) -> int:
        """
        Remove all data for a specific game from tracking tables.
        
        Args:
            game_id: Game to remove
        
        Returns:
            Total rows removed
        """
        total_removed = 0
        
        for filepath in self.output_dir.glob("*_tracking.csv"):
            df = pd.read_csv(filepath)
            
            if 'game_id' in df.columns:
                before = len(df)
                df = df[df['game_id'] != game_id]
                after = len(df)
                
                if before != after:
                    df.to_csv(filepath, index=False, encoding='utf-8-sig')
                    removed = before - after
                    total_removed += removed
                    logger.info(f"Removed {removed} rows from {filepath.stem}")
        
        return total_removed
    
    def get_status(self) -> Dict[str, Dict]:
        """
        Get status of all CSV files.
        
        Returns:
            Dictionary of file info
        """
        status = {}
        
        for filepath in sorted(self.output_dir.glob("*.csv")):
            df = pd.read_csv(filepath)
            
            info = {
                'rows': len(df),
                'columns': len(df.columns),
                'size_kb': round(filepath.stat().st_size / 1024, 1),
            }
            
            if 'game_id' in df.columns:
                info['games'] = df['game_id'].nunique()
                info['game_ids'] = sorted(df['game_id'].unique().tolist())
            
            status[filepath.stem] = info
        
        return status
    
    def export_to_excel(self, filename: str = 'datamart.xlsx', 
                        max_sheets: int = 30) -> Path:
        """
        Export all CSVs to a single Excel file.
        
        Args:
            filename: Output Excel filename
            max_sheets: Maximum number of sheets (Excel limit)
        
        Returns:
            Path to Excel file
        """
        excel_path = self.output_dir / filename
        
        csv_files = sorted(self.output_dir.glob("*.csv"))[:max_sheets]
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for f in csv_files:
                df = pd.read_csv(f)
                sheet_name = f.stem[:31]  # Excel sheet name limit
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"Exported {len(csv_files)} tables to {excel_path}")
        return excel_path
