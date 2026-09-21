# Engineer Guide

This document reflects the current implementation in the URL shortener codebase as it exists in this repository. It is meant to describe what the application actually does today, not the original generic SDLC template.

## 1. Project purpose

The service is a FastAPI-based URL shortener with:

- URL shortening with optional custom codes
- Redirect support for shortened URLs
- TTL-based expiry support
- Click tracking and basic analytics
- Redis-backed caching with in-memory fallback
- Request rate limiting
- Background analytics processing for redirect events
- A parallel orchestration/scenario layer for SDLC-style execution
- A browser-facing web UI served from the same FastAPI app

## 2. Current architecture

### Application runtime

The main app is initialized in `app/main.py`:

- `FastAPI` application is created with title, version, docs, and OpenAPI config
- CORS and trusted-host middleware are enabled
- `RateLimitMiddleware` is attached
- Routers for health, shortening, redirects, and analytics are mounted
- Root route serves the browser UI when the request accepts HTML
- Job and scenario metadata endpoints are exposed

### Key runtime modules

- `app/main.py` — application bootstrap and HTTP routes
- `app/config.py` — environment-based settings
- `app/database.py` — SQLAlchemy engine and session factory
- `app/models.py` — `URL` and `Analytics` ORM models
- `app/crud.py` — database CRUD helpers for URLs and analytics
- `app/schemas.py` — Pydantic request/response schemas
- `app/jobs.py` — in-memory job tracking for browser metrics
- `app/background_jobs.py` — thread-based background analytics logging
- `app/utils/cache.py` — Redis cache manager with in-memory fallback
- `app/utils/shortener.py` — code generation logic
- `app/middleware/rate_limit.py` — per-IP rate limiting middleware

### Storage model

The default database is SQLite, configured in `app/config.py` as:

- `sqlite:///./url_shortener.db` in normal runtime
- `sqlite://` in pytest environments

The SQLAlchemy models are:

- `URL`
  - `id` — short code / primary key
  - `original_url`
  - `created_at`
  - `expires_at`
  - `click_count`
  - `user_id`
  - `custom_code`
- `Analytics`
  - `short_code`
  - `clicked_at`
  - `referrer`
  - `user_agent`
  - `ip_address`
  - `country`
  - `city`

## 3. Request flow

### Shorten URL

Route: `POST /shorten`

In `app/routers/shorten.py`:

1. Validates the incoming URL.
2. Rejects blocked domains.
3. Validates a custom code if one is supplied.
4. Ensures the custom code is not already taken.
5. Generates a unique short code when no custom code is provided.
6. Stores the mapping in the database.
7. Stores the shortened mapping in the Redis cache.
8. Creates a job record for UI metrics.
9. Returns a `ShortenResponse` with the short URL and expiry value.

The short code generation logic is handled in `app/utils/shortener.py` and tries multiple strategies to avoid collisions.

### Redirect flow

Route: `GET /{short_code}`

In `app/routers/redirect.py`:

1. Tries the Redis cache first.
2. Falls back to the SQLite database if the cache misses.
3. Returns HTTP 404 if the short code does not exist.
4. Returns HTTP 410 if the URL has expired.
5. Redirects with a `301` response to the original URL.
6. Tracks analytics asynchronously in a background thread so the redirect is not blocked.

### Analytics flow

Route: `GET /analytics/{short_code}`

In `app/routers/analytics.py`:

- Verifies the short code exists
- Reads aggregate analytics using `AnalyticsCRUD.get_stats()`
- Returns total clicks and recent click metadata

### Health and metadata

- `GET /health` checks database connectivity and, in non-development environments, Redis availability
- `GET /api-info` exposes service metadata
- `GET /jobs`, `GET /jobs/{job_id}`, and `GET /jobs/{job_id}/logs` return in-memory job metadata for the web UI
- `GET /scenarios` returns the scenario catalog used by the browser UI

## 4. Caching and rate limiting

### Cache behavior

`app/utils/cache.py` provides a `CacheManager` with:

- Redis as the primary cache
- in-memory fallback storage when Redis is unavailable
- JSON helpers for object caching
- simple increment support for counters

This is used for:

- redirect lookups
- short URL resolution
- rate limit counters

### Rate limiting

`app/middleware/rate_limit.py` implements a request throttle using the client IP address:

- key format: `rate_limit:{client_ip}`
- window: configured by `RATE_LIMIT_WINDOW`
- max requests: configured by `RATE_LIMIT`
- returns HTTP 429 when the limit is exceeded

## 5. Orchestration engine

The repository contains a separate orchestration layer under `orchestrator/`.

### Orchestrator overview

`orchestrator/orchestrator.py` defines a `Orchestrator` class that coordinates an SDLC-like sequence of tasks:

- `ANALYZE`
- `DESIGN`
- `CODE`
- `TEST`
- `REVIEW`
- `DEPLOY`
- `DONE`

Each stage is represented by `Task` objects defined in `orchestrator/models/task_models.py`.

### Agent model

The orchestrator can run different agents for each stage:

- `AnalyzerAgent`
- `DesignerAgent`
- `CoderAgent`
- `TesterAgent`
- `ReviewerAgent`
- `DeployAgent`

The task state includes:

- pending/running/success/failed status
- dependency tracking
- artifacts
- approval requirements
- error metadata

### Scenario layer

The project includes scenario runners under `scenarios/`:

- `brownfield_auth_analytics.py`
- `ambiguous_optimization.py`
- `run_all_scenarios.py`

These simulate greenfield, brownfield, and ambiguous requirements for the orchestration system, while the main app itself still serves the actual URL shortener product.

## 6. Configuration

The environment settings are defined in `app/config.py` and include:

- `ENVIRONMENT`
- `LOG_LEVEL`
- `BASE_URL`
- `SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `ALLOWED_ORIGINS`
- `CACHE_TTL`
- `MAX_URL_LENGTH`
- `RATE_LIMIT`
- `RATE_LIMIT_WINDOW`

## 7. Default local run

From the project root:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Then access:

- App root: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## 8. Validation and testing

The project includes tests under `tests/`.

Run the suite with:

```bash
pytest
```

The current codebase includes a mix of product behavior checks and orchestrator/scenario validation.

## 9. Practical implementation notes

The current codebase is best understood as a layered monolith with two concerns:

1. A real URL shortening service for end users
2. An agentic orchestration framework used to simulate SDLC execution

Important specifics from the implementation:

- The app is not a fully distributed microservice architecture.
- SQLite is the default persistence layer.
- Redis is used opportunistically for caching and throttling rather than as a strict dependency.
- Redirect analytics are processed in the background to avoid slowing user redirects.
- The browser UI and API share the same FastAPI application.
- Scenario orchestration is a simulation layer and not the main runtime product path.

## 10. Summary

The repository’s real implementation is a FastAPI URL shortener with analytics, caching, and operational monitoring, wrapped around an orchestration framework that models SDLC stages. The app is functional as a short-link service today, and the orchestration layer is layered on top as an agentic workflow experiment rather than as the main product flow.
