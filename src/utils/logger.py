"""
=============================================================================
LOGGING UTILITY
=============================================================================
File: src/utils/logger.py

PURPOSE:
    Centralized logging with console and file output.
    Color-coded by severity level.

USAGE:
    from src.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Processing started")
=============================================================================
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
import sys

class ColorFormatter(logging.Formatter):
    """Formatter with ANSI colors."""
    
    COLORS = {
        logging.DEBUG: '\033[95m',     # Magenta
        logging.INFO: '\033[94m',      # Blue
        logging.WARNING: '\033[93m',   # Yellow
        logging.ERROR: '\033[91m',     # Red
        logging.CRITICAL: '\033[1;91m' # Bold Red
    }
    RESET = '\033[0m'
    
    def __init__(self, use_colors=True):
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")
        self.use_colors = use_colors
    
    def format(self, record):
        msg = super().format(record)
        if self.use_colors:
            color = self.COLORS.get(record.levelno, '')
            msg = f"{color}{msg}{self.RESET}"
        return msg

_loggers = set()

def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Get configured logger."""
    logger = logging.getLogger(name)
    
    if name in _loggers:
        return logger
    
    _loggers.add(name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.propagate = False
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(ColorFormatter(use_colors=True))
    logger.addHandler(console)
    
    # File handler
    log_dir = Path.cwd() / "logs"
    log_dir.mkdir(exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_dir / f"hockey_analytics_{datetime.now():%Y-%m-%d}.log",
        maxBytes=10*1024*1024,
        backupCount=5
    )
    file_handler.setFormatter(ColorFormatter(use_colors=False))
    logger.addHandler(file_handler)
    
    return logger
