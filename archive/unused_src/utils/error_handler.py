"""
=============================================================================
ERROR HANDLING UTILITIES
=============================================================================
File: src/utils/error_handler.py
Version: 19.12
Created: January 9, 2026

Provides consistent error handling across the ETL pipeline.
NO SILENT ERROR SWALLOWING - all errors are logged.

Usage:
    from src.utils.error_handler import safe_execute, ETLError
    
    # Using decorator
    @safe_execute(default_return=pd.DataFrame())
    def risky_function():
        ...
    
    # Using context manager
    with error_context("loading player data"):
        df = pd.read_csv(path)
=============================================================================
"""

import logging
import traceback
from functools import wraps
from typing import Any, Callable, Optional, TypeVar
from contextlib import contextmanager

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ETLError(Exception):
    """Base exception for ETL errors."""
    
    def __init__(self, message: str, phase: str = None, table: str = None, details: dict = None):
        self.message = message
        self.phase = phase
        self.table = table
        self.details = details or {}
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        parts = [self.message]
        if self.phase:
            parts.append(f"Phase: {self.phase}")
        if self.table:
            parts.append(f"Table: {self.table}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)


class DataValidationError(ETLError):
    """Raised when data validation fails."""
    pass


class TableNotFoundError(ETLError):
    """Raised when a required table is not found."""
    pass


class ColumnMismatchError(ETLError):
    """Raised when expected columns are missing."""
    pass


def safe_execute(
    default_return: Any = None,
    log_errors: bool = True,
    reraise: bool = False,
    error_message: str = None
) -> Callable:
    """
    Decorator that catches exceptions and optionally returns a default value.
    
    IMPORTANT: This does NOT silently swallow errors. All errors are logged.
    
    Args:
        default_return: Value to return if exception occurs
        log_errors: Whether to log the exception (default True)
        reraise: Whether to re-raise the exception after logging
        error_message: Custom error message prefix
    
    Example:
        @safe_execute(default_return=pd.DataFrame())
        def load_optional_data():
            return pd.read_csv('might_not_exist.csv')
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    msg = error_message or f"Error in {func.__name__}"
                    logger.error(f"{msg}: {type(e).__name__}: {e}")
                    logger.debug(traceback.format_exc())
                
                if reraise:
                    raise
                
                return default_return
        return wrapper
    return decorator


@contextmanager
def error_context(operation: str, table: str = None, phase: str = None):
    """
    Context manager that provides detailed error context.
    
    All errors are logged with context before re-raising.
    
    Args:
        operation: Description of what operation is being performed
        table: Name of the table being processed (optional)
        phase: Name of the ETL phase (optional)
    
    Example:
        with error_context("loading player ratings", table="dim_player"):
            df = pd.read_csv(path)
            ratings = df['rating'].values
    """
    try:
        yield
    except Exception as e:
        context_parts = [f"Error during {operation}"]
        if table:
            context_parts.append(f"table={table}")
        if phase:
            context_parts.append(f"phase={phase}")
        
        context_str = " | ".join(context_parts)
        logger.error(f"{context_str}: {type(e).__name__}: {e}")
        logger.debug(traceback.format_exc())
        raise


def validate_dataframe(
    df,
    required_columns: list = None,
    min_rows: int = None,
    max_null_rate: float = None,
    name: str = "DataFrame"
):
    """
    Validate a DataFrame meets requirements.
    
    Raises DataValidationError if validation fails.
    
    Args:
        df: DataFrame to validate
        required_columns: List of column names that must be present
        min_rows: Minimum number of rows required
        max_null_rate: Maximum allowed NULL rate (0.0 to 1.0) for any column
        name: Name of the DataFrame for error messages
    
    Example:
        validate_dataframe(
            events_df,
            required_columns=['event_id', 'game_id'],
            min_rows=100,
            name='fact_events'
        )
    """
    if df is None:
        raise DataValidationError(f"{name} is None", table=name)
    
    if required_columns:
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            raise ColumnMismatchError(
                f"{name} missing required columns: {missing}",
                table=name,
                details={'missing_columns': missing, 'available_columns': list(df.columns)}
            )
    
    if min_rows is not None and len(df) < min_rows:
        raise DataValidationError(
            f"{name} has {len(df)} rows, minimum {min_rows} required",
            table=name,
            details={'actual_rows': len(df), 'min_rows': min_rows}
        )
    
    if max_null_rate is not None:
        for col in df.columns:
            null_rate = df[col].isna().sum() / len(df) if len(df) > 0 else 0
            if null_rate > max_null_rate:
                raise DataValidationError(
                    f"{name}.{col} has {null_rate:.1%} NULL rate, max {max_null_rate:.1%} allowed",
                    table=name,
                    details={'column': col, 'null_rate': null_rate, 'max_null_rate': max_null_rate}
                )


def log_operation(operation: str, table: str = None) -> Callable:
    """
    Decorator that logs the start and end of an operation.
    
    Args:
        operation: Description of the operation
        table: Name of the table being processed
    
    Example:
        @log_operation("enhancing events", table="fact_events")
        def enhance_events(df):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            table_str = f" ({table})" if table else ""
            logger.info(f"Starting: {operation}{table_str}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed: {operation}{table_str}")
                return result
            except Exception as e:
                logger.error(f"Failed: {operation}{table_str} - {e}")
                raise
        return wrapper
    return decorator
