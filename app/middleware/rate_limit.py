"""
Rate Limiting Middleware
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import time
import logging

from app.utils.cache import cache
from app.config import settings

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Create rate limit key
        key = f"rate_limit:{client_ip}"
        
        try:
            # Get current count
            current = cache.redis.get(key)
            
            if current is None:
                # First request
                cache.redis.setex(key, settings.RATE_LIMIT_WINDOW, 1)
            else:
                count = int(current)
                if count >= settings.RATE_LIMIT:
                    # Rate limit exceeded
                    logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "detail": f"Maximum {settings.RATE_LIMIT} requests per {settings.RATE_LIMIT_WINDOW} seconds",
                            "retry_after": settings.RATE_LIMIT_WINDOW
                        }
                    )
                # Increment counter
                cache.redis.incr(key)
        except Exception as e:
            logger.error(f"Rate limit error: {e}")
            # Allow request if rate limiting fails
        
        # Process request
        response = await call_next(request)
        return response