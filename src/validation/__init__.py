"""
BenchSight Validation Module
Provides comprehensive validation for ETL:
- TableVerifier: Post-ETL output validation
- PreETLValidator: Pre-ETL raw data validation and cleaning
"""

from .table_verifier import TableVerifier, VerificationResult, CheckResult, CheckLevel
from .pre_etl_check import (
    PreETLValidator,
    ValidationResult,
    CleanResult,
    validate_game,
    validate_all_games,
    clean_game,
)

__all__ = [
    # Post-ETL validation
    'TableVerifier',
    'VerificationResult',
    'CheckResult',
    'CheckLevel',
    # Pre-ETL validation and cleaning
    'PreETLValidator',
    'ValidationResult',
    'CleanResult',
    'validate_game',
    'validate_all_games',
    'clean_game',
]
