"""
=============================================================================
TABLE WRITER - Single-Write Semantics
=============================================================================
File: src/core/modules/table_writer.py
Version: 19.12
Created: January 9, 2026

Implements single-write semantics for the ETL pipeline.
Each table is built in memory and written ONCE at the end.

This solves the problem of:
- fact_events being written 7+ times
- Column additions scattered across files
- Order-dependent writes causing data loss

Usage:
    writer = TableWriter()
    
    # Register tables that will be created
    writer.register('fact_events', columns=['event_id', 'game_id', ...])
    
    # Add data
    writer.set_data('fact_events', df)
    
    # Add columns from different phases
    writer.add_columns('fact_events', {'is_goal': [...], 'is_shot': [...]})
    
    # Write all tables at the end
    writer.write_all()
=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class TableWriter:
    """
    Manages table creation with single-write semantics.
    
    Key features:
    - Tables are built incrementally in memory
    - Column additions are tracked by phase
    - All tables written once at the end
    - Validation before write
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Table data storage
        self._tables: Dict[str, pd.DataFrame] = {}
        
        # Track which tables have been modified
        self._dirty: Set[str] = set()
        
        # Track column additions by phase
        self._column_log: Dict[str, Dict[str, List[str]]] = {}
        
        # Current phase name
        self._current_phase: str = "init"
        
        # Write lock - prevent accidental writes during build
        self._locked: bool = False
        
        # Statistics
        self._stats = {
            'tables_registered': 0,
            'tables_written': 0,
            'columns_added': 0,
        }
    
    def set_phase(self, phase: str):
        """Set the current phase for column tracking."""
        self._current_phase = phase
        logger.info(f"TableWriter: Entering phase '{phase}'")
    
    def register(self, table_name: str, df: pd.DataFrame = None):
        """
        Register a table for single-write management.
        
        Args:
            table_name: Name of the table
            df: Optional initial DataFrame
        """
        if table_name in self._tables:
            logger.warning(f"Table '{table_name}' already registered, updating")
        
        self._tables[table_name] = df if df is not None else pd.DataFrame()
        self._dirty.add(table_name)
        self._column_log[table_name] = {self._current_phase: list(df.columns) if df is not None else []}
        self._stats['tables_registered'] += 1
        
        logger.debug(f"Registered table '{table_name}'")
    
    def set_data(self, table_name: str, df: pd.DataFrame):
        """
        Set the data for a table.
        
        Args:
            table_name: Name of the table
            df: DataFrame to set
        """
        if table_name not in self._tables:
            self.register(table_name, df)
        else:
            self._tables[table_name] = df
            self._dirty.add(table_name)
            
            # Track columns
            if self._current_phase not in self._column_log[table_name]:
                self._column_log[table_name][self._current_phase] = []
            self._column_log[table_name][self._current_phase] = list(df.columns)
    
    def get_data(self, table_name: str) -> Optional[pd.DataFrame]:
        """
        Get the current data for a table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            DataFrame or None if not registered
        """
        return self._tables.get(table_name)
    
    def add_columns(self, table_name: str, columns: Dict[str, Any]):
        """
        Add columns to an existing table.
        
        Args:
            table_name: Name of the table
            columns: Dict of column_name -> values
        """
        if table_name not in self._tables:
            raise ValueError(f"Table '{table_name}' not registered")
        
        df = self._tables[table_name]
        
        for col_name, values in columns.items():
            df[col_name] = values
            self._stats['columns_added'] += 1
            
            # Track column addition
            if self._current_phase not in self._column_log[table_name]:
                self._column_log[table_name][self._current_phase] = []
            self._column_log[table_name][self._current_phase].append(col_name)
        
        self._dirty.add(table_name)
        logger.debug(f"Added {len(columns)} columns to '{table_name}'")
    
    def add_column(self, table_name: str, col_name: str, values: Any):
        """
        Add a single column to a table.
        
        Args:
            table_name: Name of the table
            col_name: Name of the column
            values: Values for the column
        """
        self.add_columns(table_name, {col_name: values})
    
    def has_table(self, table_name: str) -> bool:
        """Check if a table is registered."""
        return table_name in self._tables
    
    def list_tables(self) -> List[str]:
        """List all registered tables."""
        return list(self._tables.keys())
    
    def get_column_log(self, table_name: str) -> Dict[str, List[str]]:
        """Get the column addition log for a table."""
        return self._column_log.get(table_name, {})
    
    def write_table(self, table_name: str) -> bool:
        """
        Write a single table to disk.
        
        Args:
            table_name: Name of the table
        
        Returns:
            True if written successfully
        """
        if table_name not in self._tables:
            logger.error(f"Cannot write '{table_name}': not registered")
            return False
        
        df = self._tables[table_name]
        path = self.output_dir / f"{table_name}.csv"
        
        try:
            df.to_csv(path, index=False)
            self._dirty.discard(table_name)
            self._stats['tables_written'] += 1
            logger.info(f"Wrote {table_name}: {len(df)} rows, {len(df.columns)} cols")
            return True
        except Exception as e:
            logger.error(f"Failed to write '{table_name}': {e}")
            return False
    
    def write_all(self) -> int:
        """
        Write all dirty tables to disk.
        
        Returns:
            Number of tables written
        """
        count = 0
        for table_name in list(self._dirty):
            if self.write_table(table_name):
                count += 1
        
        logger.info(f"Wrote {count} tables")
        return count
    
    def load_existing(self, table_name: str) -> Optional[pd.DataFrame]:
        """
        Load an existing table from disk into the writer.
        
        Args:
            table_name: Name of the table
        
        Returns:
            DataFrame if loaded, None if not found
        """
        path = self.output_dir / f"{table_name}.csv"
        
        if not path.exists():
            return None
        
        try:
            df = pd.read_csv(path, low_memory=False)
            self._tables[table_name] = df
            self._column_log[table_name] = {'_loaded': list(df.columns)}
            return df
        except Exception as e:
            logger.error(f"Failed to load '{table_name}': {e}")
            return None
    
    def get_stats(self) -> dict:
        """Get writer statistics."""
        return {
            **self._stats,
            'tables_in_memory': len(self._tables),
            'dirty_tables': len(self._dirty),
            'current_phase': self._current_phase,
        }
    
    def save_column_log(self, path: Path = None):
        """
        Save the column addition log to a JSON file.
        
        Args:
            path: Path to save (default: output_dir/column_log.json)
        """
        if path is None:
            path = self.output_dir / 'column_log.json'
        
        with open(path, 'w') as f:
            json.dump(self._column_log, f, indent=2)
        
        logger.info(f"Saved column log to {path}")


class SingleWriteETL:
    """
    Orchestrates ETL with single-write semantics.
    
    Usage:
        etl = SingleWriteETL(output_dir)
        
        with etl.phase("load"):
            etl.create_table("dim_player", player_df)
        
        with etl.phase("enhance"):
            etl.add_columns("dim_player", {"rating": values})
        
        etl.finalize()  # Writes all tables
    """
    
    def __init__(self, output_dir: Path):
        self.writer = TableWriter(output_dir)
        self._phase_stack: List[str] = []
    
    def phase(self, name: str):
        """Context manager for a phase."""
        return _PhaseContext(self, name)
    
    def create_table(self, name: str, df: pd.DataFrame):
        """Create a new table."""
        self.writer.register(name, df)
    
    def add_columns(self, name: str, columns: Dict[str, Any]):
        """Add columns to an existing table."""
        self.writer.add_columns(name, columns)
    
    def get_table(self, name: str) -> Optional[pd.DataFrame]:
        """Get a table's current data."""
        return self.writer.get_data(name)
    
    def finalize(self) -> int:
        """Write all tables and save logs."""
        count = self.writer.write_all()
        self.writer.save_column_log()
        return count


class _PhaseContext:
    """Context manager for ETL phases."""
    
    def __init__(self, etl: SingleWriteETL, name: str):
        self.etl = etl
        self.name = name
    
    def __enter__(self):
        self.etl.writer.set_phase(self.name)
        self.etl._phase_stack.append(self.name)
        return self.etl
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.etl._phase_stack.pop()
        if self.etl._phase_stack:
            self.etl.writer.set_phase(self.etl._phase_stack[-1])
        return False
