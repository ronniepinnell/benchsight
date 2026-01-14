"""Configuration for BenchSight ETL API."""
import os
from pathlib import Path
from typing import Optional

# Project root (parent of api/)
PROJECT_ROOT = Path(__file__).parent.parent

# API Configuration
API_VERSION = "1.0.0"
API_TITLE = "BenchSight ETL API"
API_DESCRIPTION = "REST API for triggering ETL jobs"

# CORS Configuration
# Add production URLs from environment variable
CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS = [
    "http://localhost:3000",  # Dashboard (dev)
    "http://localhost:8080",  # Portal (dev)
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

# Add production URLs from environment variable (comma-separated)
if CORS_ORIGINS_ENV:
    CORS_ORIGINS.extend([origin.strip() for origin in CORS_ORIGINS_ENV.split(",")])

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# Job Configuration
MAX_CONCURRENT_JOBS = 1  # Only one ETL job at a time
JOB_TIMEOUT_SECONDS = 3600  # 1 hour timeout for ETL jobs

# Supabase Configuration (optional - can be set via environment)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
