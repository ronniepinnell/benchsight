"""
BenchSight Configuration Settings
"""

import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

# Database (PostgreSQL)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'benchsight',
    'user': 'benchsight_user',
    'password': 'your_password_here'
}

# ETL Settings
ETL_BATCH_SIZE = 1000
ETL_LOG_LEVEL = 'INFO'

# Stats Settings
DEFAULT_RATING = 4.0
LEAGUE_AVG_RATING = 4.0

# Video Settings
VIDEO_REWIND_SECONDS = 10

# Privacy Mode
PRIVACY_MODE_DEFAULT = False
