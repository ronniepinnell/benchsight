"""
=============================================================================
ETL LOGGER
=============================================================================
File: src/core/modules/logger.py
Version: 19.12
Created: January 9, 2026

Centralized logging for the BenchSight ETL pipeline.
Provides consistent logging with issue tracking.
=============================================================================
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Setup module logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ETLLogger:
    """
    ETL-specific logger with issue tracking and report generation.
    
    Usage:
        log = ETLLogger()
        log.info("Processing started")
        log.warn("Missing data in column X")
        log.error("Failed to load file")
        log.section("PHASE 1")
        log.save("output/etl_log.txt")
    """
    
    def __init__(self, name: str = "ETL"):
        self.name = name
        self.messages: List[str] = []
        self.issues: List[str] = []
        self.start_time = datetime.now()
        self._current_section = None
    
    def info(self, msg: str):
        """Log an info message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] INFO: {msg}"
        self.messages.append(formatted)
        logger.info(msg)
    
    def warn(self, msg: str):
        """Log a warning message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] WARN: {msg}"
        self.messages.append(formatted)
        self.issues.append(f"WARNING: {msg}")
        logger.warning(msg)
    
    def error(self, msg: str):
        """Log an error message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] ERROR: {msg}"
        self.messages.append(formatted)
        self.issues.append(f"ERROR: {msg}")
        logger.error(msg)
    
    def issue(self, msg: str):
        """Log an issue (tracked separately for summary)."""
        self.issues.append(msg)
        self.info(f"ISSUE: {msg}")
    
    def section(self, title: str):
        """Log a section header."""
        self._current_section = title
        separator = "=" * 60
        self.messages.append("")
        self.messages.append(separator)
        self.messages.append(title)
        self.messages.append(separator)
        print()
        print(separator)
        print(title)
        print(separator)
    
    def phase(self, num: int, name: str):
        """Log a phase header."""
        self.section(f"PHASE {num}: {name}")
    
    def success(self, msg: str):
        """Log a success message with checkmark."""
        self.info(f"✓ {msg}")
    
    def table_created(self, name: str, rows: int, cols: int):
        """Log table creation."""
        self.info(f"  ✓ {name}: {rows} rows, {cols} cols")
    
    def get_summary(self) -> dict:
        """Get a summary of the ETL run."""
        elapsed = datetime.now() - self.start_time
        return {
            'name': self.name,
            'start_time': self.start_time.isoformat(),
            'elapsed_seconds': elapsed.total_seconds(),
            'message_count': len(self.messages),
            'issue_count': len(self.issues),
            'issues': self.issues,
        }
    
    def save(self, path: Path):
        """Save the log to a file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            f.write(f"{'=' * 60}\n")
            f.write(f"ETL LOG: {self.name}\n")
            f.write(f"Started: {self.start_time.isoformat()}\n")
            f.write(f"{'=' * 60}\n\n")
            
            for msg in self.messages:
                f.write(msg + '\n')
            
            if self.issues:
                f.write(f"\n{'=' * 60}\n")
                f.write("ISSUES FOUND\n")
                f.write(f"{'=' * 60}\n")
                for issue in self.issues:
                    f.write(f"  • {issue}\n")
            
            elapsed = datetime.now() - self.start_time
            f.write(f"\n{'=' * 60}\n")
            f.write(f"COMPLETED in {elapsed.total_seconds():.1f} seconds\n")
            f.write(f"{'=' * 60}\n")
        
        self.info(f"Log saved to {path}")


# Global logger instance
_global_logger: Optional[ETLLogger] = None


def get_logger() -> ETLLogger:
    """Get the global ETL logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = ETLLogger()
    return _global_logger


def reset_logger():
    """Reset the global logger (for testing)."""
    global _global_logger
    _global_logger = None
