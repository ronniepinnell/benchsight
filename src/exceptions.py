"""
=============================================================================
BENCHSIGHT EXCEPTION HIERARCHY
=============================================================================
File: src/exceptions.py
Created: 2024-12-30
Author: Production Hardening Sprint

PURPOSE:
    Centralized exception classes for the BenchSight ETL pipeline.
    Enables structured error handling, monitoring, and retry logic.

USAGE:
    from src.exceptions import ETLGameProcessingError, SchemaValidationError
    
    try:
        process_game(game_id)
    except ETLGameProcessingError as e:
        logger.error(f"Game {e.game_id} failed", extra={"cause": str(e.cause)})
        if e.is_retryable:
            retry_queue.add(e.game_id)

EXCEPTION HIERARCHY:
    BenchSightError (base)
    ├── ConfigurationError
    ├── ETLError
    │   ├── ETLGameProcessingError
    │   ├── ETLBatchFailureError
    │   ├── ETLValidationError
    │   │   ├── SchemaValidationError
    │   │   └── DataIntegrityError
    │   └── ETLTimeoutError
    └── LoaderError
        ├── ConnectionError
        ├── RetryableError
        └── NonRetryableError

=============================================================================
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


class BenchSightError(Exception):
    """
    Base exception for all BenchSight errors.
    
    All custom exceptions inherit from this class, enabling:
    - Catch-all handling: except BenchSightError
    - Structured error info via to_dict()
    - Timestamp tracking
    
    Attributes:
        message: Human-readable error description
        timestamp: When the error occurred
        context: Additional structured data about the error
    """
    
    def __init__(self, message: str, context: Dict[str, Any] = None):
        self.message = message
        self.timestamp = datetime.utcnow()
        self.context = context or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }
    
    def __str__(self) -> str:
        if self.context:
            ctx_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({ctx_str})"
        return self.message


class ConfigurationError(BenchSightError):
    """
    Configuration or environment setup errors.
    
    Raised when:
    - Missing required config files
    - Invalid configuration values
    - Missing environment variables
    - Database connection string issues
    
    Example:
        raise ConfigurationError(
            "Missing Supabase credentials",
            context={"config_path": "config/config_local.ini", "missing": ["url", "key"]}
        )
    """
    pass


# =============================================================================
# ETL PIPELINE ERRORS
# =============================================================================

class ETLError(BenchSightError):
    """
    Base class for ETL pipeline errors.
    
    Attributes:
        is_retryable: Whether this error is safe to retry
        stage: Which ETL stage failed (stage/intermediate/datamart)
    """
    
    def __init__(self, message: str, stage: str = None, is_retryable: bool = False, 
                 context: Dict[str, Any] = None):
        self.stage = stage
        self.is_retryable = is_retryable
        ctx = context or {}
        if stage:
            ctx["stage"] = stage
        ctx["is_retryable"] = is_retryable
        super().__init__(message, ctx)


class ETLGameProcessingError(ETLError):
    """
    Single game processing failure.
    
    Raised when processing a specific game fails at any stage.
    Captures the game_id and root cause for debugging.
    
    Attributes:
        game_id: The game that failed
        cause: The underlying exception
        stage: Where in the pipeline it failed
        partial_data: Whether partial data was written (requires cleanup)
    
    Example:
        try:
            transform_game(18969)
        except ValueError as e:
            raise ETLGameProcessingError(
                game_id=18969,
                cause=e,
                stage="intermediate",
                partial_data=True
            )
    """
    
    def __init__(self, game_id: int, cause: Exception, stage: str = None,
                 partial_data: bool = False, is_retryable: bool = None):
        self.game_id = game_id
        self.cause = cause
        self.partial_data = partial_data
        
        # Determine if retryable based on cause if not specified
        if is_retryable is None:
            is_retryable = self._is_cause_retryable(cause)
        
        message = f"Failed to process game {game_id}: {cause}"
        super().__init__(
            message=message,
            stage=stage,
            is_retryable=is_retryable,
            context={
                "game_id": game_id,
                "cause_type": type(cause).__name__,
                "cause_message": str(cause),
                "partial_data": partial_data
            }
        )
    
    def _is_cause_retryable(self, cause: Exception) -> bool:
        """Determine if the underlying cause is retryable."""
        cause_str = str(cause).lower()
        retryable_patterns = [
            "timeout", "connection", "network", "503", "502", "429",
            "rate limit", "too many requests", "temporarily unavailable"
        ]
        return any(p in cause_str for p in retryable_patterns)


class ETLBatchFailureError(ETLError):
    """
    Batch processing failure threshold exceeded.
    
    Raised when too many games in a batch fail (e.g., >20% failure rate).
    This indicates a systemic issue rather than individual game problems.
    
    Attributes:
        failed_games: List of game IDs that failed
        total_games: Total games in the batch
        failure_rate: Percentage that failed
        threshold: The threshold that was exceeded
    
    Example:
        if failure_rate > 0.2:
            raise ETLBatchFailureError(
                failed_games=[18969, 18970, 18971],
                total_games=10,
                threshold=0.2
            )
    """
    
    def __init__(self, failed_games: List[int], total_games: int, 
                 threshold: float = 0.2, errors: Dict[int, str] = None):
        self.failed_games = failed_games
        self.total_games = total_games
        self.failure_rate = len(failed_games) / total_games if total_games > 0 else 1.0
        self.threshold = threshold
        self.errors = errors or {}
        
        message = (
            f"Batch failure rate {self.failure_rate:.1%} exceeds threshold {threshold:.1%}. "
            f"Failed {len(failed_games)}/{total_games} games: {failed_games[:5]}"
            f"{'...' if len(failed_games) > 5 else ''}"
        )
        
        super().__init__(
            message=message,
            stage="batch",
            is_retryable=False,  # Systemic issues shouldn't auto-retry
            context={
                "failed_games": failed_games,
                "total_games": total_games,
                "failure_rate": self.failure_rate,
                "threshold": threshold,
                "sample_errors": dict(list(self.errors.items())[:3])
            }
        )


class ETLTimeoutError(ETLError):
    """
    ETL operation timed out.
    
    Raised when an operation exceeds its allowed time limit.
    Always retryable as timeouts are usually transient.
    
    Attributes:
        operation: What operation timed out
        timeout_seconds: The timeout limit
        elapsed_seconds: How long it actually ran
    """
    
    def __init__(self, operation: str, timeout_seconds: float, 
                 elapsed_seconds: float = None, game_id: int = None):
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        self.elapsed_seconds = elapsed_seconds
        
        message = f"Operation '{operation}' timed out after {timeout_seconds}s"
        if elapsed_seconds:
            message += f" (elapsed: {elapsed_seconds:.1f}s)"
        
        super().__init__(
            message=message,
            stage=None,
            is_retryable=True,
            context={
                "operation": operation,
                "timeout_seconds": timeout_seconds,
                "elapsed_seconds": elapsed_seconds,
                "game_id": game_id
            }
        )


# =============================================================================
# VALIDATION ERRORS
# =============================================================================

class ETLValidationError(ETLError):
    """Base class for validation errors."""
    
    def __init__(self, message: str, validation_type: str = None, 
                 context: Dict[str, Any] = None):
        ctx = context or {}
        if validation_type:
            ctx["validation_type"] = validation_type
        super().__init__(message, stage="validation", is_retryable=False, context=ctx)


class SchemaValidationError(ETLValidationError):
    """
    CSV schema doesn't match database schema.
    
    Raised during pre-load validation when:
    - CSV has columns not in database
    - Required database columns missing from CSV
    - Column type mismatches detected
    
    Attributes:
        table_name: The table being validated
        missing_in_db: Columns in CSV but not in DB
        missing_in_csv: Required columns not in CSV
        type_mismatches: Columns with wrong types
    
    Example:
        raise SchemaValidationError(
            table_name="fact_events",
            missing_in_db=["new_column"],
            missing_in_csv=["required_col"],
            type_mismatches={"goals": "expected INTEGER, got TEXT"}
        )
    """
    
    def __init__(self, table_name: str, missing_in_db: List[str] = None,
                 missing_in_csv: List[str] = None, type_mismatches: Dict[str, str] = None):
        self.table_name = table_name
        self.missing_in_db = missing_in_db or []
        self.missing_in_csv = missing_in_csv or []
        self.type_mismatches = type_mismatches or {}
        
        issues = []
        if self.missing_in_db:
            issues.append(f"Extra CSV columns: {self.missing_in_db}")
        if self.missing_in_csv:
            issues.append(f"Missing required columns: {self.missing_in_csv}")
        if self.type_mismatches:
            issues.append(f"Type mismatches: {list(self.type_mismatches.keys())}")
        
        message = f"Schema validation failed for {table_name}: {'; '.join(issues)}"
        
        super().__init__(
            message=message,
            validation_type="schema",
            context={
                "table_name": table_name,
                "missing_in_db": self.missing_in_db,
                "missing_in_csv": self.missing_in_csv,
                "type_mismatches": self.type_mismatches
            }
        )


class DataIntegrityError(ETLValidationError):
    """
    Post-load data integrity check failed.
    
    Raised when loaded data fails integrity checks:
    - Null primary keys
    - Duplicate primary keys
    - Orphaned foreign keys
    - Out-of-range values
    - Constraint violations
    
    Attributes:
        table_name: The table that failed validation
        check_name: Which check failed
        violation_count: How many rows violated
        sample_violations: Example bad data
    
    Example:
        raise DataIntegrityError(
            table_name="fact_player_game_stats",
            check_name="pk_not_null",
            violation_count=5,
            sample_violations=["row 10", "row 25"]
        )
    """
    
    def __init__(self, table_name: str, check_name: str, violation_count: int,
                 sample_violations: List[Any] = None, details: str = None):
        self.table_name = table_name
        self.check_name = check_name
        self.violation_count = violation_count
        self.sample_violations = sample_violations or []
        
        message = f"Data integrity check '{check_name}' failed for {table_name}: {violation_count} violations"
        if details:
            message += f" - {details}"
        
        super().__init__(
            message=message,
            validation_type="integrity",
            context={
                "table_name": table_name,
                "check_name": check_name,
                "violation_count": violation_count,
                "sample_violations": self.sample_violations[:5]
            }
        )


# =============================================================================
# LOADER ERRORS
# =============================================================================

class LoaderError(BenchSightError):
    """
    Base class for data loader errors.
    
    Attributes:
        table_name: The table being loaded
        operation: insert/upsert/delete/truncate
        batch_number: Which batch failed (if applicable)
    """
    
    def __init__(self, message: str, table_name: str = None, operation: str = None,
                 batch_number: int = None, context: Dict[str, Any] = None):
        self.table_name = table_name
        self.operation = operation
        self.batch_number = batch_number
        
        ctx = context or {}
        if table_name:
            ctx["table_name"] = table_name
        if operation:
            ctx["operation"] = operation
        if batch_number is not None:
            ctx["batch_number"] = batch_number
        
        super().__init__(message, ctx)


class LoaderConnectionError(LoaderError):
    """
    Failed to connect to database/Supabase.
    
    Always retryable as connection issues are usually transient.
    """
    
    def __init__(self, message: str, host: str = None, context: Dict[str, Any] = None):
        ctx = context or {}
        ctx["host"] = host
        ctx["is_retryable"] = True
        super().__init__(message, context=ctx)


class RetryableError(LoaderError):
    """
    Loader error that is safe to retry.
    
    Examples:
    - Connection timeouts
    - Rate limiting (429)
    - Temporary unavailability (503)
    - Network issues
    """
    
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        self.retry_after = retry_after
        ctx = kwargs.pop("context", {}) or {}
        ctx["is_retryable"] = True
        if retry_after:
            ctx["retry_after_seconds"] = retry_after
        super().__init__(message, context=ctx, **kwargs)


class NonRetryableError(LoaderError):
    """
    Loader error that should NOT be retried.
    
    Examples:
    - Schema mismatches
    - Primary key violations
    - Permission denied
    - Invalid data format
    """
    
    def __init__(self, message: str, **kwargs):
        ctx = kwargs.pop("context", {}) or {}
        ctx["is_retryable"] = False
        super().__init__(message, context=ctx, **kwargs)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is safe to retry.
    
    Args:
        error: Any exception
    
    Returns:
        True if the error is transient and safe to retry
    
    Example:
        try:
            load_data()
        except Exception as e:
            if is_retryable_error(e):
                retry_with_backoff()
            else:
                raise
    """
    # Check if it's a BenchSight error with is_retryable attribute
    if hasattr(error, "is_retryable"):
        return error.is_retryable
    
    # Check known retryable exception types
    if isinstance(error, RetryableError):
        return True
    if isinstance(error, NonRetryableError):
        return False
    
    # Heuristic based on error message
    error_str = str(error).lower()
    retryable_patterns = [
        "timeout", "timed out", "connection", "network",
        "503", "502", "504", "429", "rate limit",
        "too many requests", "temporarily unavailable",
        "connection reset", "broken pipe", "eof occurred"
    ]
    
    non_retryable_patterns = [
        "permission denied", "access denied", "unauthorized",
        "not found", "does not exist", "invalid", "malformed",
        "duplicate key", "unique constraint", "foreign key"
    ]
    
    if any(p in error_str for p in non_retryable_patterns):
        return False
    
    return any(p in error_str for p in retryable_patterns)


def wrap_external_error(error: Exception, operation: str = None, 
                        game_id: int = None) -> BenchSightError:
    """
    Wrap an external exception in a BenchSight exception.
    
    Useful for converting third-party library errors into our hierarchy.
    
    Args:
        error: The original exception
        operation: What operation was being performed
        game_id: Game ID if applicable
    
    Returns:
        Appropriate BenchSightError subclass
    
    Example:
        try:
            supabase.table("x").insert(data).execute()
        except Exception as e:
            raise wrap_external_error(e, operation="insert", game_id=18969)
    """
    if isinstance(error, BenchSightError):
        return error
    
    error_str = str(error).lower()
    
    # Determine the right exception type
    if "timeout" in error_str or "timed out" in error_str:
        return ETLTimeoutError(
            operation=operation or "unknown",
            timeout_seconds=0,
            game_id=game_id
        )
    
    if "connection" in error_str or "network" in error_str:
        return LoaderConnectionError(str(error))
    
    if is_retryable_error(error):
        return RetryableError(
            str(error),
            table_name=None,
            operation=operation,
            context={"original_type": type(error).__name__, "game_id": game_id}
        )
    
    return NonRetryableError(
        str(error),
        table_name=None,
        operation=operation,
        context={"original_type": type(error).__name__, "game_id": game_id}
    )
