"""
Database Models
"""

from sqlalchemy import Column, String, DateTime, Integer, Index
from datetime import datetime
from .database import Base

class URL(Base):
    """URL model."""
    
    __tablename__ = "urls"
    
    id = Column(String(10), primary_key=True, index=True)
    original_url = Column(String(2048), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    click_count = Column(Integer, default=0)
    user_id = Column(String(50), nullable=True)
    custom_code = Column(String(50), nullable=True)
    
    __table_args__ = (
        Index('idx_short_code', 'id'),
        Index('idx_user_id', 'user_id'),
    )

class Analytics(Base):
    """Analytics model."""
    
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(10), index=True)
    clicked_at = Column(DateTime, default=datetime.utcnow)
    referrer = Column(String(2048), nullable=True)
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(45), nullable=True)
    country = Column(String(50), nullable=True)
    city = Column(String(50), nullable=True)
    
    __table_args__ = (
        Index('idx_analytics_short_code', 'short_code'),
        Index('idx_analytics_clicked_at', 'clicked_at'),
    )