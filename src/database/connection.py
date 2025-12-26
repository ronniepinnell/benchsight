"""
=============================================================================
DATABASE CONNECTION MANAGER
=============================================================================
File: src/database/connection.py

PURPOSE:
    Establish and manage database connections using SQLAlchemy.
    Supports both SQLite (local development) and PostgreSQL (production).

CONFIGURATION:
    Database type determined by environment variable or config:
    - DB_TYPE=sqlite (default for development)
    - DB_TYPE=postgres (for production)

=============================================================================
"""

import os
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Global engine instance (singleton)
_engine: Optional[Engine] = None

# Database configuration from environment
DB_TYPE = os.environ.get('DB_TYPE', 'sqlite')
PG_HOST = os.environ.get('PG_HOST', 'localhost')
PG_PORT = os.environ.get('PG_PORT', '5432')
PG_DATABASE = os.environ.get('PG_DATABASE', 'hockey_analytics')
PG_USER = os.environ.get('PG_USER', 'postgres')
PG_PASSWORD = os.environ.get('PG_PASSWORD', '')
SQLITE_PATH = os.environ.get('SQLITE_PATH', None)


def get_engine(db_type: str = None, db_path: Path = None, **pg_kwargs) -> Engine:
    """
    Get or create SQLAlchemy engine.
    
    Args:
        db_type: 'sqlite' or 'postgres'. Defaults to DB_TYPE env var.
        db_path: Path to SQLite file (sqlite only).
        **pg_kwargs: PostgreSQL overrides (host, port, database, user, password).
    
    Returns:
        SQLAlchemy Engine.
    """
    global _engine
    
    use_db_type = db_type or DB_TYPE
    
    # Reuse existing engine if no overrides
    if _engine is not None and db_type is None and db_path is None and not pg_kwargs:
        return _engine
    
    # Build connection string
    if use_db_type == 'postgres':
        connection_string = _build_postgres_connection_string(**pg_kwargs)
    else:
        connection_string = _build_sqlite_connection_string(db_path)
    
    # Create engine
    _engine = create_engine(connection_string, echo=False, pool_pre_ping=True)
    logger.info(f"Database engine created: {use_db_type}")
    
    return _engine


def _build_postgres_connection_string(**kwargs) -> str:
    """Build PostgreSQL connection string."""
    host = kwargs.get('host', PG_HOST)
    port = kwargs.get('port', PG_PORT)
    database = kwargs.get('database', PG_DATABASE)
    user = kwargs.get('user', PG_USER)
    password = kwargs.get('password', PG_PASSWORD)
    
    if password:
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return f"postgresql://{user}@{host}:{port}/{database}"


def _build_sqlite_connection_string(db_path: Path = None) -> str:
    """Build SQLite connection string."""
    if db_path is None:
        if SQLITE_PATH:
            db_path = Path(SQLITE_PATH)
        else:
            db_path = Path(__file__).parent.parent.parent / 'data' / 'hockey_analytics.db'
    
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f'sqlite:///{db_path}'


@contextmanager
def get_connection():
    """
    Get database connection as context manager.
    Auto-commits on success, rollback on failure.
    """
    engine = get_engine()
    connection = engine.connect()
    
    try:
        yield connection
        connection.commit()
    except Exception as e:
        connection.rollback()
        logger.error(f"Database error, rolled back: {e}")
        raise
    finally:
        connection.close()


def execute_sql(sql: str, params: dict = None) -> None:
    """Execute a SQL statement."""
    with get_connection() as conn:
        conn.execute(text(sql), params or {})


def execute_sql_file(file_path: Path) -> None:
    """Execute a SQL file with multiple statements."""
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    statements = sql_content.split(';')
    
    with get_connection() as conn:
        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue
            
            lines = [l.strip() for l in statement.split('\n') if l.strip()]
            if all(l.startswith('--') for l in lines):
                continue
            
            try:
                conn.execute(text(statement))
            except Exception as e:
                if 'does not exist' not in str(e).lower():
                    logger.warning(f"SQL warning: {e}")


def close_engine() -> None:
    """Close database engine."""
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
        logger.info("Database engine closed")


def get_db_type() -> str:
    """Get current database type."""
    return DB_TYPE


def test_connection() -> bool:
    """Test database connectivity."""
    try:
        with get_connection() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False
