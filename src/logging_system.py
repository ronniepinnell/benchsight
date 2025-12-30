"""
BenchSight Comprehensive Logging System

Provides structured logging for:
- ETL pipeline runs
- Supabase deployments
- Data loads
- Test results
- Errors and warnings

Features:
- File-based logging with rotation and subfolders
- JSON structured logs for parsing
- Console output with colors
- Supabase table logging
- Run summaries and reports
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import platform

# ============================================================
# CONFIGURATION
# ============================================================

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class OperationType(Enum):
    ETL_RUN = "etl_run"
    SUPABASE_LOAD = "supabase_load"
    TABLE_LOAD = "table_load"
    TABLE_UPSERT = "table_upsert"
    TABLE_REPLACE = "table_replace"
    SCHEMA_CREATE = "schema_create"
    SCHEMA_DROP = "schema_drop"
    TEST_RUN = "test_run"
    VALIDATION = "validation"
    BACKUP = "backup"
    RESTORE = "restore"

class Status(Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class TableLoadResult:
    """Result of loading a single table"""
    table_name: str
    operation: str
    status: str
    rows_before: int = 0
    rows_after: int = 0
    rows_inserted: int = 0
    rows_updated: int = 0
    rows_deleted: int = 0
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    csv_path: Optional[str] = None
    csv_rows: int = 0
    csv_columns: int = 0

@dataclass
class TestResult:
    """Result of a test run"""
    test_file: str
    test_name: str
    status: str  # passed, failed, skipped, error
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None

@dataclass
class RunSummary:
    """Summary of a complete run"""
    run_id: str
    run_type: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0
    tables_processed: int = 0
    tables_success: int = 0
    tables_failed: int = 0
    total_rows_loaded: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    environment: Dict[str, Any] = field(default_factory=dict)

# ============================================================
# BENCHSIGHT LOGGER CLASS
# ============================================================

class BenchSightLogger:
    """
    Comprehensive logging system for BenchSight ETL and deployment.
    
    Usage:
        logger = BenchSightLogger(run_type="etl_run")
        logger.start_run()
        
        # Log operations
        logger.log_info("Starting ETL process")
        logger.log_table_load(TableLoadResult(...))
        
        # Complete run
        summary = logger.end_run()
    """
    
    def __init__(
        self,
        run_type: str = "etl_run",
        base_log_dir: str = "logs",
        console_output: bool = True,
        json_logs: bool = True,
        supabase_client = None
    ):
        self.run_type = run_type
        self.base_log_dir = Path(base_log_dir)
        self.console_output = console_output
        self.json_logs = json_logs
        self.supabase_client = supabase_client
        
        # Generate unique run ID
        self.run_id = self._generate_run_id()
        self.started_at = datetime.now()
        self.completed_at = None
        
        # Initialize collections
        self.table_results: List[TableLoadResult] = []
        self.test_results: List[TestResult] = []
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self.info_logs: List[Dict] = []
        
        # Setup logging
        self._setup_directories()
        self._setup_file_loggers()
        self._setup_console_logger()
        
        # Environment info
        self.environment = self._capture_environment()
    
    def _generate_run_id(self) -> str:
        """Generate unique run ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{timestamp}_{self.run_type}_{os.getpid()}"
        short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"{self.run_type}_{timestamp}_{short_hash}"
    
    def _capture_environment(self) -> Dict[str, Any]:
        """Capture environment information"""
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "hostname": platform.node(),
            "user": os.environ.get("USER", "unknown"),
            "working_dir": os.getcwd(),
            "pid": os.getpid()
        }
    
    def _setup_directories(self):
        """Create log directory structure"""
        # Main log directory
        self.base_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Date-based subdirectory
        date_str = self.started_at.strftime("%Y-%m-%d")
        self.date_dir = self.base_log_dir / date_str
        self.date_dir.mkdir(exist_ok=True)
        
        # Run-specific directory
        self.run_dir = self.date_dir / self.run_id
        self.run_dir.mkdir(exist_ok=True)
        
        # Subdirectories
        (self.run_dir / "tables").mkdir(exist_ok=True)
        (self.run_dir / "errors").mkdir(exist_ok=True)
        (self.run_dir / "tests").mkdir(exist_ok=True)
    
    def _setup_file_loggers(self):
        """Setup file-based loggers"""
        # Main log file
        self.main_log_path = self.run_dir / "run.log"
        self.main_logger = logging.getLogger(f"benchsight_{self.run_id}")
        self.main_logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(self.main_log_path)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.main_logger.addHandler(file_handler)
        
        # JSON log file
        if self.json_logs:
            self.json_log_path = self.run_dir / "run.jsonl"
        
        # Error log file
        self.error_log_path = self.run_dir / "errors" / "errors.log"
    
    def _setup_console_logger(self):
        """Setup console output with colors"""
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Color formatter
            class ColorFormatter(logging.Formatter):
                COLORS = {
                    'DEBUG': '\033[36m',     # Cyan
                    'INFO': '\033[32m',      # Green
                    'WARNING': '\033[33m',   # Yellow
                    'ERROR': '\033[31m',     # Red
                    'CRITICAL': '\033[35m',  # Magenta
                    'RESET': '\033[0m'
                }
                
                def format(self, record):
                    color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
                    reset = self.COLORS['RESET']
                    record.levelname = f"{color}{record.levelname}{reset}"
                    return super().format(record)
            
            formatter = ColorFormatter('%(levelname)-17s | %(message)s')
            console_handler.setFormatter(formatter)
            self.main_logger.addHandler(console_handler)
    
    def _write_json_log(self, entry: Dict):
        """Append entry to JSON log file"""
        if self.json_logs:
            entry['timestamp'] = datetime.now().isoformat()
            entry['run_id'] = self.run_id
            with open(self.json_log_path, 'a') as f:
                f.write(json.dumps(entry) + '\n')
    
    # ============================================================
    # PUBLIC LOGGING METHODS
    # ============================================================
    
    def start_run(self):
        """Mark the start of a run"""
        self.log_info(f"{'='*60}")
        self.log_info(f"BENCHSIGHT {self.run_type.upper()} STARTED")
        self.log_info(f"Run ID: {self.run_id}")
        self.log_info(f"Started: {self.started_at.isoformat()}")
        self.log_info(f"Log Directory: {self.run_dir}")
        self.log_info(f"{'='*60}")
        
        self._write_json_log({
            "event": "run_started",
            "run_type": self.run_type,
            "environment": self.environment
        })
        
        # Log to Supabase if available
        if self.supabase_client:
            self._log_to_supabase_run_start()
    
    def end_run(self, status: str = None) -> RunSummary:
        """Mark the end of a run and generate summary"""
        self.completed_at = datetime.now()
        duration = (self.completed_at - self.started_at).total_seconds()
        
        # Determine status
        if status is None:
            if len(self.errors) > 0:
                status = Status.FAILED.value if self._has_critical_errors() else Status.PARTIAL.value
            else:
                status = Status.SUCCESS.value
        
        # Generate summary
        summary = RunSummary(
            run_id=self.run_id,
            run_type=self.run_type,
            status=status,
            started_at=self.started_at.isoformat(),
            completed_at=self.completed_at.isoformat(),
            duration_seconds=duration,
            tables_processed=len(self.table_results),
            tables_success=sum(1 for t in self.table_results if t.status == Status.SUCCESS.value),
            tables_failed=sum(1 for t in self.table_results if t.status == Status.FAILED.value),
            total_rows_loaded=sum(t.rows_inserted + t.rows_updated for t in self.table_results),
            tests_passed=sum(1 for t in self.test_results if t.status == "passed"),
            tests_failed=sum(1 for t in self.test_results if t.status == "failed"),
            errors=[e.get('message', str(e)) for e in self.errors],
            warnings=[w.get('message', str(w)) for w in self.warnings],
            environment=self.environment
        )
        
        # Write summary
        self._write_summary(summary)
        
        # Log completion
        self.log_info(f"{'='*60}")
        self.log_info(f"RUN COMPLETED: {status.upper()}")
        self.log_info(f"Duration: {duration:.2f} seconds")
        self.log_info(f"Tables: {summary.tables_success}/{summary.tables_processed} successful")
        self.log_info(f"Rows Loaded: {summary.total_rows_loaded:,}")
        if summary.tests_passed + summary.tests_failed > 0:
            self.log_info(f"Tests: {summary.tests_passed} passed, {summary.tests_failed} failed")
        self.log_info(f"Errors: {len(self.errors)}, Warnings: {len(self.warnings)}")
        self.log_info(f"{'='*60}")
        
        # Log to Supabase
        if self.supabase_client:
            self._log_to_supabase_run_end(summary)
        
        return summary
    
    def log_debug(self, message: str, **kwargs):
        """Log debug message"""
        self.main_logger.debug(message)
        self._write_json_log({"level": "DEBUG", "message": message, **kwargs})
    
    def log_info(self, message: str, **kwargs):
        """Log info message"""
        self.main_logger.info(message)
        self.info_logs.append({"message": message, "timestamp": datetime.now().isoformat(), **kwargs})
        self._write_json_log({"level": "INFO", "message": message, **kwargs})
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message"""
        self.main_logger.warning(message)
        warning_entry = {"message": message, "timestamp": datetime.now().isoformat(), **kwargs}
        self.warnings.append(warning_entry)
        self._write_json_log({"level": "WARNING", "message": message, **kwargs})
    
    def log_error(self, message: str, exception: Exception = None, **kwargs):
        """Log error message"""
        self.main_logger.error(message)
        
        error_entry = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        
        if exception:
            error_entry["exception_type"] = type(exception).__name__
            error_entry["exception_message"] = str(exception)
            error_entry["traceback"] = traceback.format_exc()
        
        self.errors.append(error_entry)
        self._write_json_log({"level": "ERROR", **error_entry})
        
        # Write to error log file
        with open(self.error_log_path, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Timestamp: {error_entry['timestamp']}\n")
            f.write(f"Message: {message}\n")
            if exception:
                f.write(f"Exception: {type(exception).__name__}: {exception}\n")
                f.write(f"Traceback:\n{traceback.format_exc()}\n")
        
        # Log to Supabase
        if self.supabase_client:
            self._log_to_supabase_error(error_entry)
    
    def log_table_start(self, table_name: str, operation: str, csv_path: str = None):
        """Log start of table operation"""
        self.log_info(f"[{table_name}] Starting {operation}...")
        if csv_path:
            self.log_debug(f"[{table_name}] Source: {csv_path}")
    
    def log_table_result(self, result: TableLoadResult):
        """Log result of table operation"""
        self.table_results.append(result)
        
        # Log to main log
        status_icon = "✓" if result.status == Status.SUCCESS.value else "✗"
        self.log_info(
            f"[{result.table_name}] {status_icon} {result.operation}: "
            f"{result.rows_inserted} inserted, {result.rows_updated} updated "
            f"({result.duration_seconds:.2f}s)"
        )
        
        if result.error_message:
            self.log_error(f"[{result.table_name}] {result.error_message}")
        
        # Write detailed result to table-specific file
        table_log_path = self.run_dir / "tables" / f"{result.table_name}.json"
        with open(table_log_path, 'w') as f:
            json.dump(asdict(result), f, indent=2)
        
        # Log to Supabase
        if self.supabase_client:
            self._log_to_supabase_table_load(result)
    
    def log_test_result(self, result: TestResult):
        """Log test result"""
        self.test_results.append(result)
        
        status_icon = "✓" if result.status == "passed" else "✗"
        self.log_debug(f"[TEST] {status_icon} {result.test_name}: {result.status}")
        
        if result.error_message:
            self.log_error(f"[TEST] {result.test_name}: {result.error_message}")
    
    def log_test_summary(self, test_file: str, passed: int, failed: int, skipped: int, duration: float):
        """Log summary of test file"""
        self.log_info(f"[TESTS] {test_file}: {passed} passed, {failed} failed, {skipped} skipped ({duration:.2f}s)")
        
        # Write test results
        test_log_path = self.run_dir / "tests" / f"{Path(test_file).stem}.json"
        results = [asdict(r) for r in self.test_results if r.test_file == test_file]
        with open(test_log_path, 'w') as f:
            json.dump({"file": test_file, "passed": passed, "failed": failed, "skipped": skipped, "results": results}, f, indent=2)
    
    # ============================================================
    # SUMMARY AND REPORTING
    # ============================================================
    
    def _has_critical_errors(self) -> bool:
        """Check if there are critical errors that should fail the run"""
        # Table load failures are critical
        failed_tables = [t for t in self.table_results if t.status == Status.FAILED.value]
        return len(failed_tables) > 0
    
    def _write_summary(self, summary: RunSummary):
        """Write run summary to files"""
        # JSON summary
        summary_path = self.run_dir / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump(asdict(summary), f, indent=2)
        
        # Human-readable summary
        report_path = self.run_dir / "SUMMARY.md"
        with open(report_path, 'w') as f:
            f.write(f"# BenchSight Run Summary\n\n")
            f.write(f"**Run ID:** `{summary.run_id}`\n\n")
            f.write(f"**Status:** {summary.status.upper()}\n\n")
            f.write(f"**Duration:** {summary.duration_seconds:.2f} seconds\n\n")
            f.write(f"## Timing\n\n")
            f.write(f"- Started: {summary.started_at}\n")
            f.write(f"- Completed: {summary.completed_at}\n\n")
            f.write(f"## Results\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| Tables Processed | {summary.tables_processed} |\n")
            f.write(f"| Tables Success | {summary.tables_success} |\n")
            f.write(f"| Tables Failed | {summary.tables_failed} |\n")
            f.write(f"| Total Rows Loaded | {summary.total_rows_loaded:,} |\n")
            f.write(f"| Tests Passed | {summary.tests_passed} |\n")
            f.write(f"| Tests Failed | {summary.tests_failed} |\n")
            f.write(f"| Errors | {len(summary.errors)} |\n")
            f.write(f"| Warnings | {len(summary.warnings)} |\n\n")
            
            if summary.errors:
                f.write(f"## Errors\n\n")
                for i, error in enumerate(summary.errors, 1):
                    f.write(f"{i}. {error}\n")
                f.write("\n")
            
            if summary.warnings:
                f.write(f"## Warnings\n\n")
                for i, warning in enumerate(summary.warnings, 1):
                    f.write(f"{i}. {warning}\n")
                f.write("\n")
            
            # Table details
            if self.table_results:
                f.write(f"## Table Load Details\n\n")
                f.write(f"| Table | Operation | Status | Inserted | Updated | Duration |\n")
                f.write(f"|-------|-----------|--------|----------|---------|----------|\n")
                for t in self.table_results:
                    f.write(f"| {t.table_name} | {t.operation} | {t.status} | {t.rows_inserted} | {t.rows_updated} | {t.duration_seconds:.2f}s |\n")
    
    # ============================================================
    # SUPABASE LOGGING METHODS
    # ============================================================
    
    def _log_to_supabase_run_start(self):
        """Log run start to Supabase"""
        try:
            self.supabase_client.table('log_etl_runs').insert({
                'run_id': self.run_id,
                'run_type': self.run_type,
                'status': Status.STARTED.value,
                'started_at': self.started_at.isoformat(),
                'environment': self.environment
            }).execute()
        except Exception as e:
            self.log_warning(f"Failed to log to Supabase: {e}")
    
    def _log_to_supabase_run_end(self, summary: RunSummary):
        """Log run completion to Supabase"""
        try:
            self.supabase_client.table('log_etl_runs').update({
                'status': summary.status,
                'completed_at': summary.completed_at,
                'duration_seconds': summary.duration_seconds,
                'tables_processed': summary.tables_processed,
                'tables_success': summary.tables_success,
                'tables_failed': summary.tables_failed,
                'total_rows_loaded': summary.total_rows_loaded,
                'tests_passed': summary.tests_passed,
                'tests_failed': summary.tests_failed,
                'error_count': len(summary.errors),
                'warning_count': len(summary.warnings)
            }).eq('run_id', self.run_id).execute()
        except Exception as e:
            self.log_warning(f"Failed to update Supabase run log: {e}")
    
    def _log_to_supabase_table_load(self, result: TableLoadResult):
        """Log table load to Supabase"""
        try:
            self.supabase_client.table('log_etl_tables').insert({
                'run_id': self.run_id,
                'table_name': result.table_name,
                'operation': result.operation,
                'status': result.status,
                'rows_before': result.rows_before,
                'rows_after': result.rows_after,
                'rows_inserted': result.rows_inserted,
                'rows_updated': result.rows_updated,
                'rows_deleted': result.rows_deleted,
                'duration_seconds': result.duration_seconds,
                'error_message': result.error_message,
                'csv_rows': result.csv_rows,
                'csv_columns': result.csv_columns
            }).execute()
        except Exception as e:
            self.log_warning(f"Failed to log table load to Supabase: {e}")
    
    def _log_to_supabase_error(self, error_entry: Dict):
        """Log error to Supabase"""
        try:
            self.supabase_client.table('log_errors').insert({
                'run_id': self.run_id,
                'error_message': error_entry.get('message'),
                'exception_type': error_entry.get('exception_type'),
                'exception_message': error_entry.get('exception_message'),
                'traceback': error_entry.get('traceback'),
                'context': json.dumps({k: v for k, v in error_entry.items() 
                                       if k not in ['message', 'exception_type', 'exception_message', 'traceback', 'timestamp']})
            }).execute()
        except Exception as e:
            pass  # Don't log errors about logging errors


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def create_logger(run_type: str = "etl_run", supabase_client=None) -> BenchSightLogger:
    """Create and initialize a logger"""
    logger = BenchSightLogger(run_type=run_type, supabase_client=supabase_client)
    logger.start_run()
    return logger


def get_latest_run_summary(log_dir: str = "logs") -> Optional[Dict]:
    """Get the most recent run summary"""
    log_path = Path(log_dir)
    if not log_path.exists():
        return None
    
    # Find latest date directory
    date_dirs = sorted([d for d in log_path.iterdir() if d.is_dir()], reverse=True)
    if not date_dirs:
        return None
    
    # Find latest run in that date
    latest_date = date_dirs[0]
    run_dirs = sorted([d for d in latest_date.iterdir() if d.is_dir()], reverse=True)
    if not run_dirs:
        return None
    
    # Read summary
    summary_path = run_dirs[0] / "summary.json"
    if summary_path.exists():
        with open(summary_path) as f:
            return json.load(f)
    
    return None


if __name__ == "__main__":
    # Demo usage
    logger = create_logger("demo_run")
    
    logger.log_info("This is an info message")
    logger.log_warning("This is a warning")
    
    # Simulate table load
    result = TableLoadResult(
        table_name="dim_player",
        operation="upsert",
        status=Status.SUCCESS.value,
        rows_inserted=100,
        rows_updated=50,
        duration_seconds=1.5
    )
    logger.log_table_result(result)
    
    # Simulate error
    try:
        raise ValueError("Demo error")
    except Exception as e:
        logger.log_error("Something went wrong", exception=e)
    
    summary = logger.end_run()
    print(f"\nSummary written to: {logger.run_dir}")
