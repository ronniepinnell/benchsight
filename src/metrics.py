"""
=============================================================================
ETL METRICS COLLECTION
=============================================================================
File: src/metrics.py
Created: 2024-12-30
Author: Production Hardening Sprint

PURPOSE:
    Track and persist ETL run statistics for monitoring, debugging, and
    performance analysis.

WHAT IT TRACKS:
    - Run start/end times and duration
    - Rows processed per stage (stage/intermediate/datamart)
    - Success/failure status per game
    - Error counts and types
    - Table-level statistics
    - Historical trends

USAGE:
    from src.metrics import ETLMetricsCollector, ETLRunMetrics
    
    collector = ETLMetricsCollector()
    
    with collector.track_run(game_id=18969) as metrics:
        # Do ETL work
        metrics.rows_staged = 1500
        metrics.rows_transformed = 1500
        metrics.rows_loaded = 1500
    
    # Run is automatically saved on context exit

WHY THIS EXISTS:
    Without metrics, you can't answer:
    - "How long does game processing take on average?"
    - "What's our failure rate over the past week?"
    - "Which tables take longest to load?"
    - "Are there performance regressions?"

=============================================================================
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
from enum import Enum
import csv

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RunStatus(Enum):
    """ETL run status values."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"  # Some games succeeded, some failed
    CANCELLED = "cancelled"


@dataclass
class TableMetrics:
    """Metrics for a single table load."""
    table_name: str
    rows_read: int = 0
    rows_loaded: int = 0
    rows_skipped: int = 0
    rows_errored: int = 0
    duration_seconds: float = 0.0
    started_at: str = ""
    completed_at: str = ""
    success: bool = True
    error_message: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class StageMetrics:
    """Metrics for an ETL stage."""
    stage_name: str  # stage, intermediate, datamart
    tables_processed: int = 0
    total_rows: int = 0
    duration_seconds: float = 0.0
    success: bool = True
    table_metrics: List[TableMetrics] = field(default_factory=list)
    
    def add_table(self, metrics: TableMetrics):
        self.table_metrics.append(metrics)
        self.tables_processed += 1
        self.total_rows += metrics.rows_loaded
        self.duration_seconds += metrics.duration_seconds
        if not metrics.success:
            self.success = False
    
    def to_dict(self) -> Dict:
        return {
            "stage_name": self.stage_name,
            "tables_processed": self.tables_processed,
            "total_rows": self.total_rows,
            "duration_seconds": round(self.duration_seconds, 2),
            "success": self.success,
            "tables": [t.to_dict() for t in self.table_metrics]
        }


@dataclass
class ETLRunMetrics:
    """
    Complete metrics for a single ETL run.
    
    Tracks everything about a pipeline execution for a single game or batch.
    
    Attributes:
        run_id: Unique identifier for this run
        game_id: Game being processed (None for batch runs)
        game_ids: List of games (for batch runs)
        status: Current run status
        started_at: When the run started
        completed_at: When the run completed
        duration_seconds: Total run time
        stages: Metrics per ETL stage
        errors: List of error messages
        warnings: List of warning messages
    """
    run_id: str = ""
    game_id: Optional[int] = None
    game_ids: List[int] = field(default_factory=list)
    status: str = RunStatus.PENDING.value
    started_at: str = ""
    completed_at: str = ""
    duration_seconds: float = 0.0
    
    # Stage metrics
    rows_staged: int = 0
    rows_transformed: int = 0
    rows_loaded: int = 0
    
    # Detailed stage metrics
    stages: Dict[str, StageMetrics] = field(default_factory=dict)
    
    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Source file info
    source_file: str = ""
    source_checksum: str = ""
    
    def __post_init__(self):
        if not self.run_id:
            self.run_id = self._generate_run_id()
        if not self.started_at:
            self.started_at = datetime.utcnow().isoformat()
    
    def _generate_run_id(self) -> str:
        """Generate unique run ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        game_part = str(self.game_id) if self.game_id else "batch"
        return f"{game_part}_{timestamp}"
    
    def start(self):
        """Mark run as started."""
        self.status = RunStatus.RUNNING.value
        self.started_at = datetime.utcnow().isoformat()
        logger.info(f"ETL run started: {self.run_id}")
    
    def complete(self, success: bool = True):
        """Mark run as completed."""
        self.completed_at = datetime.utcnow().isoformat()
        
        if self.started_at:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            self.duration_seconds = (end - start).total_seconds()
        
        if success and not self.errors:
            self.status = RunStatus.SUCCESS.value
        elif self.errors and self.rows_loaded > 0:
            self.status = RunStatus.PARTIAL.value
        else:
            self.status = RunStatus.FAILED.value
        
        logger.info(
            f"ETL run completed: {self.run_id} - {self.status} "
            f"({self.duration_seconds:.1f}s, {self.rows_loaded} rows)"
        )
    
    def fail(self, error: str):
        """Mark run as failed with error."""
        self.errors.append(error)
        self.complete(success=False)
    
    def add_error(self, error: str):
        """Add an error without failing the run."""
        self.errors.append(error)
        logger.error(f"[{self.run_id}] {error}")
    
    def add_warning(self, warning: str):
        """Add a warning."""
        self.warnings.append(warning)
        logger.warning(f"[{self.run_id}] {warning}")
    
    def add_stage_metrics(self, stage_name: str, metrics: StageMetrics):
        """Add metrics for a stage."""
        self.stages[stage_name] = metrics
        
        # Update totals
        if stage_name == "stage":
            self.rows_staged = metrics.total_rows
        elif stage_name == "intermediate":
            self.rows_transformed = metrics.total_rows
        elif stage_name == "datamart":
            self.rows_loaded = metrics.total_rows
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "run_id": self.run_id,
            "game_id": self.game_id,
            "game_ids": self.game_ids,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_seconds": round(self.duration_seconds, 2),
            "rows": {
                "staged": self.rows_staged,
                "transformed": self.rows_transformed,
                "loaded": self.rows_loaded
            },
            "stages": {k: v.to_dict() for k, v in self.stages.items()},
            "errors": self.errors,
            "warnings": self.warnings,
            "source_file": self.source_file,
            "source_checksum": self.source_checksum
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ETLMetricsCollector:
    """
    Collects and persists ETL metrics.
    
    Stores metrics in both JSON files (detailed) and CSV (for analysis).
    
    Attributes:
        metrics_dir: Directory to store metrics files
        current_run: Currently active run metrics
    """
    
    def __init__(self, metrics_dir: str = "logs/metrics"):
        """
        Initialize metrics collector.
        
        Args:
            metrics_dir: Directory to store metrics files
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.current_run: Optional[ETLRunMetrics] = None
        
        # CSV file for run history
        self.history_file = self.metrics_dir / "etl_run_history.csv"
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Create history CSV file with headers if it doesn't exist."""
        if not self.history_file.exists():
            with open(self.history_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "run_id", "game_id", "status", "started_at", "completed_at",
                    "duration_seconds", "rows_staged", "rows_transformed",
                    "rows_loaded", "error_count", "warning_count"
                ])
    
    @contextmanager
    def track_run(self, game_id: int = None, game_ids: List[int] = None,
                  source_file: str = None):
        """
        Context manager for tracking an ETL run.
        
        Usage:
            with collector.track_run(game_id=18969) as metrics:
                # Do ETL work
                metrics.rows_staged = 1500
        
        Args:
            game_id: Single game ID
            game_ids: List of game IDs (for batch)
            source_file: Path to source tracking file
        
        Yields:
            ETLRunMetrics instance
        """
        metrics = ETLRunMetrics(
            game_id=game_id,
            game_ids=game_ids or [],
            source_file=source_file or ""
        )
        
        if source_file:
            metrics.source_checksum = self._compute_file_checksum(source_file)
        
        metrics.start()
        self.current_run = metrics
        
        try:
            yield metrics
            metrics.complete(success=True)
        except Exception as e:
            metrics.fail(str(e))
            raise
        finally:
            self.save_run(metrics)
            self.current_run = None
    
    def _compute_file_checksum(self, file_path: str) -> str:
        """Compute MD5 checksum of a file."""
        try:
            path = Path(file_path)
            if path.exists():
                with open(path, 'rb') as f:
                    return hashlib.md5(f.read()).hexdigest()
        except Exception:
            pass
        return ""
    
    def save_run(self, metrics: ETLRunMetrics):
        """
        Save run metrics to files.
        
        Args:
            metrics: The run metrics to save
        """
        # Save detailed JSON
        run_file = self.metrics_dir / f"run_{metrics.run_id}.json"
        with open(run_file, 'w') as f:
            f.write(metrics.to_json())
        
        # Append to history CSV
        with open(self.history_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                metrics.run_id,
                metrics.game_id,
                metrics.status,
                metrics.started_at,
                metrics.completed_at,
                round(metrics.duration_seconds, 2),
                metrics.rows_staged,
                metrics.rows_transformed,
                metrics.rows_loaded,
                len(metrics.errors),
                len(metrics.warnings)
            ])
        
        logger.debug(f"Saved metrics for run {metrics.run_id}")
    
    def get_recent_runs(self, limit: int = 10) -> List[Dict]:
        """
        Get recent ETL runs from history.
        
        Args:
            limit: Maximum number of runs to return
        
        Returns:
            List of run dictionaries (newest first)
        """
        runs = []
        
        if not self.history_file.exists():
            return runs
        
        with open(self.history_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                runs.append(row)
        
        # Sort by started_at descending
        runs.sort(key=lambda x: x.get("started_at", ""), reverse=True)
        
        return runs[:limit]
    
    def get_run_details(self, run_id: str) -> Optional[Dict]:
        """
        Get detailed metrics for a specific run.
        
        Args:
            run_id: The run ID to look up
        
        Returns:
            Run details dict or None if not found
        """
        run_file = self.metrics_dir / f"run_{run_id}.json"
        
        if run_file.exists():
            with open(run_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def get_stats(self, days: int = 7) -> Dict:
        """
        Get aggregate statistics for recent runs.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dict with aggregate statistics
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        runs = []
        for run in self.get_recent_runs(limit=1000):
            if run.get("started_at", "") >= cutoff_str:
                runs.append(run)
        
        if not runs:
            return {
                "period_days": days,
                "total_runs": 0,
                "success_rate": 0,
                "avg_duration_seconds": 0,
                "total_rows_loaded": 0
            }
        
        success_count = sum(1 for r in runs if r.get("status") == "success")
        durations = [float(r.get("duration_seconds", 0)) for r in runs]
        rows = [int(r.get("rows_loaded", 0)) for r in runs]
        
        return {
            "period_days": days,
            "total_runs": len(runs),
            "success_count": success_count,
            "failure_count": len(runs) - success_count,
            "success_rate": round(success_count / len(runs) * 100, 1),
            "avg_duration_seconds": round(sum(durations) / len(durations), 2),
            "min_duration_seconds": round(min(durations), 2),
            "max_duration_seconds": round(max(durations), 2),
            "total_rows_loaded": sum(rows),
            "avg_rows_per_run": round(sum(rows) / len(runs))
        }
    
    def cleanup_old_runs(self, days: int = 30):
        """
        Delete run files older than specified days.
        
        Args:
            days: Delete runs older than this many days
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = 0
        
        for run_file in self.metrics_dir.glob("run_*.json"):
            try:
                with open(run_file, 'r') as f:
                    data = json.load(f)
                
                started = data.get("started_at", "")
                if started and datetime.fromisoformat(started) < cutoff:
                    run_file.unlink()
                    deleted += 1
            except Exception:
                continue
        
        logger.info(f"Cleaned up {deleted} old run files")


# Global collector instance
_collector: Optional[ETLMetricsCollector] = None


def get_metrics_collector() -> ETLMetricsCollector:
    """Get or create the global metrics collector."""
    global _collector
    if _collector is None:
        _collector = ETLMetricsCollector()
    return _collector


def track_table_load(table_name: str, rows_read: int, rows_loaded: int,
                     duration_seconds: float, success: bool = True,
                     error_message: str = "") -> TableMetrics:
    """
    Create table metrics and optionally add to current run.
    
    Args:
        table_name: Name of the table
        rows_read: Rows read from source
        rows_loaded: Rows successfully loaded
        duration_seconds: Time taken
        success: Whether load succeeded
        error_message: Error message if failed
    
    Returns:
        TableMetrics instance
    """
    metrics = TableMetrics(
        table_name=table_name,
        rows_read=rows_read,
        rows_loaded=rows_loaded,
        rows_skipped=rows_read - rows_loaded,
        duration_seconds=duration_seconds,
        started_at=datetime.utcnow().isoformat(),
        completed_at=datetime.utcnow().isoformat(),
        success=success,
        error_message=error_message
    )
    
    collector = get_metrics_collector()
    if collector.current_run:
        # Add to current stage if tracking
        pass  # Could enhance to auto-detect stage
    
    return metrics
