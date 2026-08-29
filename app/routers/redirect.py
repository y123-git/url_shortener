"""
Redirect Router
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.database import get_db
from app.crud import URLCRUD
from app.utils.cache import cache
from app.config import settings
from app.background_jobs import track_redirect_analytics

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{short_code}")
async def redirect_to_url(
    request: Request,
    short_code: str,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Redirect to the original URL.
    
    - **short_code**: Short code to redirect
    """
    logger.info(f"Redirecting: {short_code}")
    
    # Check Redis cache first (fast path)
    cached_url = cache.get(short_code)
    if cached_url:
        logger.info(f"Cache hit for {short_code}")
        track_redirect_analytics(
            short_code=short_code,
            referrer=request.headers.get("referer"),
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None,
        )
        return RedirectResponse(url=cached_url, status_code=301)
    
    # Check database
    url_entry = URLCRUD.get(db, short_code)
    if not url_entry:
        raise HTTPException(404, f"Short URL '{short_code}' not found")
    
    # Check if expired
    if url_entry.expires_at and url_entry.expires_at < datetime.utcnow():
        raise HTTPException(410, f"Short URL '{short_code}' has expired")
    
    # Cache for future (1 hour TTL)
    cache.set(short_code, url_entry.original_url)

    # Track analytics in the background so the redirect completes immediately.
    track_redirect_analytics(
        short_code=short_code,
        referrer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"Redirecting to: {url_entry.original_url}")
    
    return RedirectResponse(url=url_entry.original_url, status_code=301)