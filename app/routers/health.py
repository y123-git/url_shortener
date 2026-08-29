"""
Health Check Router
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import logging

from app.database import engine
from app.config import settings
from app.utils.cache import cache

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    logger.debug("Health check requested")
    
    # Check database
    db_healthy = False
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
            db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis only when the app is configured to require it.
    redis_healthy = True
    if settings.ENVIRONMENT.lower() not in {"development", "local", "test"}:
        try:
            redis_healthy = cache.redis.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            redis_healthy = False
    
    status = "healthy" if db_healthy and redis_healthy else "unhealthy"
    
    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if db_healthy else "disconnected",
        "redis": "connected" if redis_healthy else "disconnected",
        "version": "1.0.0"
    }

@router.get("/api-info")
async def api_info():
    """API metadata endpoint."""
    return {
        "service": "URL Shortener API",
        "version": "1.0.0",
        "description": "Production-grade URL shortener with analytics and orchestration",
        "docs": "/docs",
        "health": "/health"
    }