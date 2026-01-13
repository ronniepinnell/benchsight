"""
=============================================================================
TABLE MANAGER - Single Write Semantics
=============================================================================
File: src/utils/table_manager.py
Version: 19.10
Created: January 9, 2026

Centralized table loading and saving with:
- Lazy loading (load once, cache in memory)
- Single write per table (build complete, write once)
- Column tracking (know what columns were added by which phase)
- Validation before write

Usage:
    from src.utils.table_manager import TableManager
    
    tm = TableManager()
    
    # Load table (cached)
    events = tm.load('fact_events')
    
    # Modify in memory
    events['new_col'] = values
    
    # Mark as dirty (will be written at end)
    tm.mark_dirty('fact_events', events)
    
    # Write all dirty tables at end of phase
    tm.flush_all()
=============================================================================
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional, Set, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Default output directory
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent.parent / 'data' / 'output'


class TableManager:
    """
    Manages table loading and saving with single-write semantics.
    
    Key features:
    - Tables are loaded once and cached
    - Modifications are tracked
    - All writes happen at flush time
    - Column additions are tracked per phase
    """
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache of loaded tables
        self._cache: Dict[str, pd.DataFrame] = {}
        
        # Tables that have been modified and need to be written
        self._dirty: Set[str] = set()
        
        # Track what columns each phase added
        self._column_log: Dict[str, Dict[str, List[str]]] = {}
        
        # Current phase name
        self._current_phase: str = "unknown"
    
    def set_phase(self, phase_name: str):
        """Set the current phase name for column tracking."""
        self._current_phase = phase_name
        logger.info(f"TableManager: Phase set to '{phase_name}'")
    
    def load(self, table_name: str, force_reload: bool = False) -> Optional[pd.DataFrame]:
        """
        Load a table from disk or cache.
        
        Args:
            table_name: Name of the table (without .csv)
            force_reload: If True, reload from disk even if cached
        
        Returns:
            DataFrame or None if table doesn't exist
        """
        if table_name in self._cache and not force_reload:
            return self._cache[table_name]
        
        path = self.output_dir / f"{table_name}.csv"
        if not path.exists():
            logger.debug(f"Table not found: {table_name}")
            return None
        
        try:
            df = pd.read_csv(path, low_memory=False)
            self._cache[table_name] = df
            
            # Initialize column log for this table
            if table_name not in self._column_log:
                self._column_log[table_name] = {'_original': list(df.columns)}
            
            logger.debug(f"Loaded {table_name}: {len(df)} rows, {len(df.columns)} cols")
            return df
        except Exception as e:
            logger.error(f"Failed to load {table_name}: {e}")
            return None
    
    def get(self, table_name: str) -> Optional[pd.DataFrame]:
        """Alias for load()."""
        return self.load(table_name)
    
    def mark_dirty(self, table_name: str, df: pd.DataFrame, added_columns: List[str] = None):
        """
        Mark a table as modified and needing to be written.
        
        Args:
            table_name: Name of the table
            df: The modified DataFrame
            added_columns: Optional list of columns added in this modification
        """
        # Track new columns
        if added_columns and table_name in self._column_log:
            if self._current_phase not in self._column_log[table_name]:
                self._column_log[table_name][self._current_phase] = []
            self._column_log[table_name][self._current_phase].extend(added_columns)
        
        self._cache[table_name] = df
        self._dirty.add(table_name)
        logger.debug(f"Marked {table_name} as dirty ({len(df)} rows)")
    
    def save(self, table_name: str, df: pd.DataFrame):
        """
        Immediately save a table to disk.
        
        Use this for new tables that don't exist yet.
        For existing tables, prefer mark_dirty() + flush_all().
        """
        path = self.output_dir / f"{table_name}.csv"
        df.to_csv(path, index=False)
        self._cache[table_name] = df
        logger.info(f"Saved {table_name}: {len(df)} rows, {len(df.columns)} cols")
    
    def flush(self, table_name: str) -> bool:
        """
        Write a single dirty table to disk.
        
        Returns:
            True if written, False if not dirty or failed
        """
        if table_name not in self._dirty:
            return False
        
        if table_name not in self._cache:
            logger.warning(f"Table {table_name} marked dirty but not in cache")
            return False
        
        try:
            df = self._cache[table_name]
            path = self.output_dir / f"{table_name}.csv"
            df.to_csv(path, index=False)
            self._dirty.discard(table_name)
            logger.info(f"Flushed {table_name}: {len(df)} rows, {len(df.columns)} cols")
            return True
        except Exception as e:
            logger.error(f"Failed to flush {table_name}: {e}")
            return False
    
    def flush_all(self) -> int:
        """
        Write all dirty tables to disk.
        
        Returns:
            Number of tables written
        """
        count = 0
        for table_name in list(self._dirty):
            if self.flush(table_name):
                count += 1
        
        logger.info(f"Flushed {count} tables")
        return count
    
    def get_column_log(self, table_name: str) -> Dict[str, List[str]]:
        """
        Get the column addition log for a table.
        
        Shows which columns were added by which phase.
        """
        return self._column_log.get(table_name, {})
    
    def list_tables(self) -> List[str]:
        """List all tables in output directory."""
        return [f.stem for f in self.output_dir.glob('*.csv')]
    
    def clear_cache(self):
        """Clear the cache (but don't delete files)."""
        self._cache.clear()
        self._dirty.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Get statistics about the table manager."""
        return {
            'cached_tables': len(self._cache),
            'dirty_tables': len(self._dirty),
            'total_tables_on_disk': len(self.list_tables()),
            'current_phase': self._current_phase
        }


# Global instance for convenience
_global_tm: Optional[TableManager] = None


def get_table_manager() -> TableManager:
    """Get the global TableManager instance."""
    global _global_tm
    if _global_tm is None:
        _global_tm = TableManager()
    return _global_tm


def load_table(table_name: str) -> Optional[pd.DataFrame]:
    """Convenience function to load a table using global manager."""
    return get_table_manager().load(table_name)


def save_table(table_name: str, df: pd.DataFrame):
    """Convenience function to save a table using global manager."""
    get_table_manager().save(table_name, df)
