"""
URL Shortening Router
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.crud import URLCRUD
from app.schemas import ShortenRequest, ShortenResponse
from app.utils.shortener import URLShortener
from app.utils.cache import cache
from app.utils.validators import validate_custom_code, is_blocked_domain
from app.config import settings
from app.jobs import add_job, add_log

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/shorten", response_model=ShortenResponse)
async def shorten_url(
    request: Request,
    req: ShortenRequest,
    db: Session = Depends(get_db)
):
    """
    Shorten a URL.
    
    - **original_url**: URL to shorten (must be valid)
    - **custom_code**: Optional custom short code (3-10 characters)
    - **ttl_seconds**: Optional time-to-live in seconds
    """
    logger.info(f"Shortening URL: {req.original_url}")
    
    # Validate URL
    if is_blocked_domain(str(req.original_url)):
        raise HTTPException(400, "Domain is blocked")
    
    # Handle custom code
    if req.custom_code:
        if not validate_custom_code(req.custom_code):
            raise HTTPException(400, "Invalid custom code format")
        if URLCRUD.exists(db, req.custom_code):
            raise HTTPException(400, f"Custom code '{req.custom_code}' already taken")
        short_code = req.custom_code
    else:
        short_code = URLShortener.generate_unique_code(db, str(req.original_url))
    
    # Calculate expiration
    expires_at = None
    if req.ttl_seconds:
        expires_at = datetime.utcnow() + timedelta(seconds=req.ttl_seconds)
    
    # Save to database
    url_entry = URLCRUD.create(
        db=db,
        original_url=str(req.original_url),
        code=short_code,
        expires_at=expires_at
    )
    
    # Cache in Redis
    cache.set(short_code, str(req.original_url))

    # Track a job for browser metrics and recent activity.
    # Use the scenario_type from request, default to "shorten" if not provided.
    scenario = str(req.scenario_type or "shorten").strip().lower()
    job = add_job(
        scenario_type=scenario,
        status="completed",
        progress=100,
        result={
            "original_url": str(req.original_url),
            "short_code": short_code,
            "short_url": f"{settings.BASE_URL}/{short_code}",
            "ttl_seconds": req.ttl_seconds,
            "scenario_type": scenario,
        },
        logs=[
            f"Shortened {req.original_url} -> {settings.BASE_URL}/{short_code}",
            f"Generated short code: {short_code}",
        ],
    )
    add_log(job["job_id"], f"Shorten completed for {short_code}")

    # Build response
    short_url = f"{settings.BASE_URL}/{short_code}"

    return ShortenResponse(
        short_url=short_url,
        short_code=short_code,
        expires_at=expires_at
    )