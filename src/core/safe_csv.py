#!/usr/bin/env python3
"""
SAFE CSV I/O - Protected Read/Write Operations
===============================================

This module wraps all CSV operations with proper error handling,
logging, and atomic writes to prevent data corruption.

Features:
1. Atomic writes (write to temp, then rename)
2. Automatic backups before overwrite
3. Comprehensive error logging
4. File locking to prevent concurrent writes
5. Validation before save

Usage:
    from src.core.safe_csv import safe_read_csv, safe_write_csv, SafeCSVWriter
    
    # Simple read with error handling
    df = safe_read_csv("data/output/fact_events.csv")
    
    # Simple write with atomic operation
    safe_write_csv(df, "data/output/fact_events.csv")
    
    # Context manager for multiple operations
    with SafeCSVWriter("data/output/fact_events.csv") as writer:
        writer.write(df)
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Any
from datetime import datetime
import pandas as pd
import logging
import fcntl  # File locking (Unix)

logger = logging.getLogger(__name__)


class CSVError(Exception):
    """Custom exception for CSV operations."""
    pass


class CSVReadError(CSVError):
    """Error reading CSV file."""
    pass


class CSVWriteError(CSVError):
    """Error writing CSV file."""
    pass


def safe_read_csv(path: str, **kwargs) -> pd.DataFrame:
    """
    Safely read a CSV file with error handling.
    
    Args:
        path: Path to CSV file
        **kwargs: Additional arguments for pd.read_csv
        
    Returns:
        DataFrame
        
    Raises:
        CSVReadError: If file cannot be read
    """
    path = Path(path)
    
    if not path.exists():
        raise CSVReadError(f"File not found: {path}")
    
    if not path.suffix.lower() == '.csv':
        logger.warning(f"File {path} is not a .csv file")
    
    try:
        # Set sensible defaults
        kwargs.setdefault('low_memory', False)
        
        df = pd.read_csv(path, **kwargs)
        logger.debug(f"Read {path}: {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except pd.errors.EmptyDataError:
        logger.warning(f"Empty CSV file: {path}")
        return pd.DataFrame()
        
    except pd.errors.ParserError as e:
        raise CSVReadError(f"Parse error in {path}: {e}")
        
    except UnicodeDecodeError as e:
        raise CSVReadError(f"Encoding error in {path}: {e}")
        
    except PermissionError:
        raise CSVReadError(f"Permission denied: {path}")
        
    except Exception as e:
        raise CSVReadError(f"Failed to read {path}: {e}")


def safe_write_csv(df: pd.DataFrame, path: str, 
                   backup: bool = False,
                   atomic: bool = True,
                   validate: bool = True,
                   **kwargs) -> bool:
    """
    Safely write a DataFrame to CSV with error handling.
    
    Args:
        df: DataFrame to write
        path: Output path
        backup: Create backup before overwriting
        atomic: Use atomic write (temp file + rename)
        validate: Validate data before writing
        **kwargs: Additional arguments for df.to_csv
        
    Returns:
        True if successful
        
    Raises:
        CSVWriteError: If write fails
    """
    path = Path(path)
    
    # Validation
    if validate:
        if df is None:
            raise CSVWriteError("Cannot write None DataFrame")
        if not isinstance(df, pd.DataFrame):
            raise CSVWriteError(f"Expected DataFrame, got {type(df)}")
    
    # Create directory if needed
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Backup if requested and file exists
    if backup and path.exists():
        backup_path = path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        try:
            shutil.copy2(path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
    
    # Set defaults
    kwargs.setdefault('index', False)
    
    try:
        if atomic:
            # Atomic write: write to temp file, then rename
            fd, temp_path = tempfile.mkstemp(suffix='.csv', dir=path.parent)
            try:
                os.close(fd)
                df.to_csv(temp_path, **kwargs)
                
                # Verify temp file was written correctly
                temp_df = pd.read_csv(temp_path)
                if len(temp_df) != len(df):
                    raise CSVWriteError(f"Row count mismatch: wrote {len(df)}, read {len(temp_df)}")
                
                # Atomic rename
                shutil.move(temp_path, path)
                
            except Exception as e:
                # Clean up temp file on error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise
        else:
            # Direct write
            df.to_csv(path, **kwargs)
        
        logger.debug(f"Wrote {path}: {len(df)} rows, {len(df.columns)} columns")
        return True
        
    except PermissionError:
        raise CSVWriteError(f"Permission denied: {path}")
        
    except OSError as e:
        if "No space left" in str(e):
            raise CSVWriteError(f"Disk full: {path}")
        raise CSVWriteError(f"OS error writing {path}: {e}")
        
    except Exception as e:
        raise CSVWriteError(f"Failed to write {path}: {e}")


class SafeCSVWriter:
    """
    Context manager for safe CSV writing with file locking.
    
    Usage:
        with SafeCSVWriter("data/output/fact_events.csv") as writer:
            writer.write(df)
    """
    
    def __init__(self, path: str, backup: bool = True):
        self.path = Path(path)
        self.backup = backup
        self.lock_file = None
        self.lock_path = self.path.with_suffix('.lock')
    
    def __enter__(self):
        # Acquire file lock
        self.lock_file = open(self.lock_path, 'w')
        try:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, BlockingIOError):
            self.lock_file.close()
            raise CSVWriteError(f"File is locked by another process: {self.path}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Release lock
        if self.lock_file:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            self.lock_file.close()
            
            # Clean up lock file
            try:
                self.lock_path.unlink()
            except Exception:
                pass
        
        return False  # Don't suppress exceptions
    
    def write(self, df: pd.DataFrame, **kwargs):
        """Write DataFrame to CSV."""
        safe_write_csv(df, self.path, backup=self.backup, **kwargs)


def batch_read_csvs(paths: List[str], **kwargs) -> dict:
    """
    Read multiple CSV files with error handling.
    
    Args:
        paths: List of file paths
        **kwargs: Arguments for pd.read_csv
        
    Returns:
        Dict of {path: DataFrame} for successful reads
    """
    results = {}
    errors = []
    
    for path in paths:
        try:
            results[path] = safe_read_csv(path, **kwargs)
        except CSVReadError as e:
            errors.append((path, str(e)))
            logger.warning(f"Failed to read {path}: {e}")
    
    if errors:
        logger.warning(f"Failed to read {len(errors)} files")
    
    return results


def validate_csv(path: str, 
                 required_columns: List[str] = None,
                 min_rows: int = 0,
                 max_rows: int = None) -> tuple:
    """
    Validate a CSV file.
    
    Args:
        path: Path to CSV
        required_columns: List of required column names
        min_rows: Minimum row count
        max_rows: Maximum row count (optional)
        
    Returns:
        (is_valid: bool, errors: List[str])
    """
    errors = []
    
    try:
        df = safe_read_csv(path)
    except CSVReadError as e:
        return (False, [str(e)])
    
    # Check columns
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            errors.append(f"Missing columns: {missing}")
    
    # Check row count
    if len(df) < min_rows:
        errors.append(f"Too few rows: {len(df)} < {min_rows}")
    
    if max_rows and len(df) > max_rows:
        errors.append(f"Too many rows: {len(df)} > {max_rows}")
    
    return (len(errors) == 0, errors)


if __name__ == "__main__":
    # Test the module
    print("Testing safe_csv module...")
    
    # Create test DataFrame
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie']
    })
    
    test_path = "data/output/_test_safe_csv.csv"
    
    # Test write
    safe_write_csv(df, test_path)
    print(f"✅ Write successful")
    
    # Test read
    df2 = safe_read_csv(test_path)
    assert len(df2) == len(df)
    print(f"✅ Read successful")
    
    # Test validation
    is_valid, errors = validate_csv(test_path, required_columns=['id', 'name'])
    assert is_valid
    print(f"✅ Validation successful")
    
    # Clean up
    Path(test_path).unlink()
    print(f"✅ All tests passed")
