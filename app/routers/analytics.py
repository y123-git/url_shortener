"""
Analytics Router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import AnalyticsCRUD, URLCRUD

router = APIRouter()


@router.get("/{short_code}")
async def get_analytics(short_code: str, db: Session = Depends(get_db)):
    """Return analytics stats for a short code."""
    # Ensure the short URL exists
    url = URLCRUD.get(db, short_code)
    if not url:
        raise HTTPException(status_code=404, detail=f"Short URL '{short_code}' not found")

    stats = AnalyticsCRUD.get_stats(db, short_code)

    return {"short_code": short_code, **stats}
