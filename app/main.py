"""
URL Shortener Service - Main Application
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
import logging
import os
from pathlib import Path

from app.config import settings
from app.database import Base, engine
from app.routers import shorten, redirect, analytics, health
from app.middleware.rate_limit import RateLimitMiddleware
from app.jobs import add_job, list_jobs, get_job

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create tables
logger.info("Creating database tables...")
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="URL Shortener API",
    description="Production-grade URL shortener with analytics and agentic orchestration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure in production
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(shorten.router, tags=["URL Shortening"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

@app.get("/", include_in_schema=False)
async def root(request: Request):
    """Serve the browser UI on the root route or JSON metadata."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        web_ui_path = Path(__file__).resolve().parent.parent / "web_ui.html"
        return FileResponse(str(web_ui_path))
    return {
        "service": "URL Shortener API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/scenarios")
async def scenarios():
    """Return the available scenario options for the browser UI."""
    return {
        "scenarios": [
            {
                "type": "greenfield",
                "name": "GREENFIELD SCENARIO",
                "description": "Build a URL shortener from scratch with full SDLC automation.",
                "estimated_time": "2-3 minutes",
                "use_cases": ["New service development", "Clean implementation"],
                "outputs": ["Complete codebase", "Tests", "Documentation"]
            },
            {
                "type": "brownfield",
                "name": "BROWNFIELD SCENARIO",
                "description": "Enhance an existing codebase with authentication and analytics.",
                "estimated_time": "3-4 minutes",
                "use_cases": ["Legacy modernization", "Feature additions"],
                "outputs": ["Modified code", "Migrations", "Tests"]
            },
            {
                "type": "ambiguous",
                "name": "AMBIGUOUS SCENARIO",
                "description": "Clarify vague requirements and generate a solution plan.",
                "estimated_time": "4-5 minutes",
                "use_cases": ["Unclear requirements", "Architecture decisions"],
                "outputs": ["Clarified requirements", "Solution trade-offs", "Implementation plan"]
            }
        ]
    }

@app.get("/jobs")
async def jobs():
    """Return stored jobs for the browser metrics and recent-jobs panel."""
    return list_jobs()

@app.get("/jobs/{job_id}")
async def get_job_by_id(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/jobs/{job_id}/logs")
async def get_job_logs(job_id: str, limit: int = 50):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    logs = job.get("logs", [])
    return {"logs": logs[-limit:] if limit else logs}

app.include_router(redirect.router, tags=["Redirects"])

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("=" * 50)
    logger.info("URL Shortener Service Starting...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info(f"Redis: {settings.REDIS_URL}")
    logger.info(f"Base URL: {settings.BASE_URL}")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("URL Shortener Service Shutting Down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )