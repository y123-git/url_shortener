"""Background worker helpers for non-blocking analytics updates."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from app.crud import AnalyticsCRUD, URLCRUD
from app.database import SessionLocal

logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="redirect-analytics")


def track_redirect_analytics(
    short_code: str,
    referrer: Optional[str] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Persist click analytics without blocking the redirect response."""
    def _work() -> None:
        db = SessionLocal()
        try:
            URLCRUD.increment_click(db, short_code)
            AnalyticsCRUD.create(
                db=db,
                short_code=short_code,
                referrer=referrer,
                user_agent=user_agent,
                ip_address=ip_address,
            )
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Background analytics update failed for %s", short_code)
        finally:
            db.close()

    executor.submit(_work)
