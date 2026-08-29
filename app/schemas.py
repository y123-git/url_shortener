"""
Pydantic Schemas
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class ShortenRequest(BaseModel):
    """Request to shorten a URL."""
    original_url: HttpUrl = Field(..., description="URL to shorten")
    custom_code: Optional[str] = Field(None, max_length=10, description="Custom short code")
    ttl_seconds: Optional[int] = Field(None, gt=0, le=31536000, description="Time to live in seconds")
    scenario_type: Optional[str] = Field(None, description="Scenario type: greenfield, brownfield, ambiguous, or shorten")

class ShortenResponse(BaseModel):
    """Response with shortened URL."""
    short_url: str
    short_code: str
    expires_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "short_url": "http://localhost:8000/abc123",
                "short_code": "abc123",
                "expires_at": "2026-12-31T23:59:59"
            }
        }

class AnalyticsResponse(BaseModel):
    """Analytics response."""
    short_code: str
    original_url: str
    click_count: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    recent_clicks: Optional[list] = []

class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    status_code: int