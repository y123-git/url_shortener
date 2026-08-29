"""
CRUD Operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional, List

from .models import URL, Analytics
from .utils.shortener import URLShortener

class URLCRUD:
    """CRUD operations for URLs."""
    
    @staticmethod
    def create(db: Session, original_url: str, code: str, 
               user_id: Optional[str] = None, 
               expires_at: Optional[datetime] = None) -> URL:
        """Create a new shortened URL."""
        url_entry = URL(
            id=code,
            original_url=original_url,
            user_id=user_id,
            expires_at=expires_at
        )
        db.add(url_entry)
        db.commit()
        db.refresh(url_entry)
        return url_entry
    
    @staticmethod
    def get(db: Session, code: str) -> Optional[URL]:
        """Get URL by short code."""
        return db.query(URL).filter(URL.id == code).first()
    
    @staticmethod
    def exists(db: Session, code: str) -> bool:
        """Check if short code exists."""
        return db.query(URL).filter(URL.id == code).first() is not None
    
    @staticmethod
    def increment_click(db: Session, code: str) -> int:
        """Increment click count."""
        url_entry = URLCRUD.get(db, code)
        if url_entry:
            url_entry.click_count += 1
            db.commit()
            return url_entry.click_count
        return 0
    
    @staticmethod
    def get_user_urls(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[URL]:
        """Get URLs for a user."""
        return db.query(URL).filter(URL.user_id == user_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete(db: Session, code: str) -> bool:
        """Delete a short URL."""
        url_entry = URLCRUD.get(db, code)
        if url_entry:
            db.delete(url_entry)
            db.commit()
            return True
        return False

class AnalyticsCRUD:
    """CRUD operations for analytics."""
    
    @staticmethod
    def create(db: Session, short_code: str, referrer: Optional[str] = None,
               user_agent: Optional[str] = None, ip_address: Optional[str] = None) -> Analytics:
        """Create analytics entry."""
        analytics = Analytics(
            short_code=short_code,
            referrer=referrer,
            user_agent=user_agent,
            ip_address=ip_address
        )
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
        return analytics
    
    @staticmethod
    def get_stats(db: Session, short_code: str) -> dict:
        """Get analytics stats for a URL."""
        total = db.query(Analytics).filter(Analytics.short_code == short_code).count()
        
        # Recent clicks (last 10)
        recent = db.query(Analytics).filter(Analytics.short_code == short_code)\
            .order_by(desc(Analytics.clicked_at)).limit(10).all()
        
        return {
            "total_clicks": total,
            "recent_clicks": [
                {
                    "clicked_at": a.clicked_at.isoformat(),
                    "referrer": a.referrer,
                    "user_agent": a.user_agent,
                    "country": a.country,
                    "city": a.city
                }
                for a in recent
            ]
        }