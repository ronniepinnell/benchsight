"""
BenchSight ETL API Module

Provides REST API endpoints for triggering ETL operations from web interfaces.
"""

from src.api.server import app, get_orchestrator

__all__ = ['app', 'get_orchestrator']
