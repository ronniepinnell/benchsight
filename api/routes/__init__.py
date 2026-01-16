"""API routes."""
from .health import router as health_router
from .etl import router as etl_router
from .upload import router as upload_router
from .staging import router as staging_router
from .ml import router as ml_router

__all__ = ["health_router", "etl_router", "upload_router", "staging_router", "ml_router"]
