# Engineer Guide

This document reflects the current implementation in the URL shortener codebase as it exists in this repository. It is meant to describe what the application actually does today.

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

## 2. Project structure

```
url_shortener/
├── app/                           # FastAPI application layer
│   ├── __init__.py
│   ├── main.py                    # FastAPI app bootstrap and route mounting
│   ├── config.py                  # Environment-based configuration
│   ├── database.py                # SQLAlchemy engine and session factory
│   ├── models.py                  # ORM models (URL, Analytics)
│   ├── crud.py                    # Database CRUD helpers
│   ├── schemas.py                 # Pydantic request/response schemas
│   ├── jobs.py                    # In-memory job tracking
│   ├── background_jobs.py         # Background analytics processing thread
│   ├── routers/                   # API route handlers
│   │   ├── __init__.py
│   │   ├── health.py              # GET /health endpoint
│   │   ├── shorten.py             # POST /shorten endpoint
│   │   ├── redirect.py            # GET /{short_code} redirect logic
│   │   └── analytics.py           # GET /analytics/{short_code} endpoint
│   ├── utils/                     # Utility modules
│   │   ├── __init__.py
│   │   ├── cache.py               # Redis/in-memory cache manager
│   │   ├── shortener.py           # Short code generation logic
│   │   └── validators.py          # Input validation helpers
│   ├── middleware/                # HTTP middleware
│   │   ├── __init__.py
│   │   └── rate_limit.py          # Per-IP rate limiting middleware
│   └── __pycache__/
│
├── orchestrator/                  # SDLC orchestration layer
│   ├── __init__.py
│   ├── orchestrator.py            # Main orchestrator class
│   ├── agents/                    # Stage-specific agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Base agent abstract class
│   │   ├── analyzer_agent.py      # ANALYZE stage agent
│   │   ├── designer_agent.py      # DESIGN stage agent
│   │   ├── coder_agent.py         # CODE stage agent
│   │   ├── tester_agent.py        # TEST stage agent
│   │   ├── reviewer_agent.py      # REVIEW stage agent
│   │   ├── deploy_agent.py        # DEPLOY stage agent
│   │   └── __init__.py
│   ├── core/                      # Core orchestrator utilities
│   │   ├── __init__.py
│   │   ├── state_manager.py       # Checkpoint and rollback management
│   │   ├── dependency_graph.py    # Task dependency tracking
│   │   ├── validators.py          # Orchestration validators
│   │   └── __init__.py
│   └── models/                    # Data models
│       └── task_models.py         # Task and Stage definitions
│
├── scenarios/                     # SDLC scenario runners
│   ├── __init__.py
│   ├── brownfield_auth_analytics.py   # Brownfield scenario
│   ├── ambiguous_optimization.py      # Ambiguous requirements scenario
│   └── run_all_scenarios.py           # Main scenario orchestrator
│
├── tests/                         # Test suite
│   ├── __pycache__/
│   ├── test_main.py               # Main app and routing tests
│   ├── test_shorten.py            # URL shortening logic tests
│   ├── test_redirect.py           # Redirect and caching tests
│   └── test_analytics.py          # Analytics endpoint tests
│
├── docker/                        # Docker configuration
│   ├── Dockerfile.dockerfile      # Production Dockerfile
│   ├── Dockerfile.dev.dockerfile  # Development Dockerfile
│   └── entrypoint.sh              # Container entrypoint script
│
├── .github/                       # GitHub configuration
│   ├── copilot-instructions.md    # Copilot agent instructions
│   └── instructions/              # GitHub workflow instructions
│
├── ARCHITECTURE/                  # Architecture documentation directory
├── scenario_outputs/              # Generated scenario output files
├── .pytest_cache/                 # Pytest cache
├── .venv/                         # Python virtual environment
├── .env.example.txt               # Example environment variables
├── .gitignore                     # Git ignore rules
├── docker-compose.yaml            # Docker Compose configuration
├── requirements.txt               # Python dependencies
├── setup.sh                       # Setup script
├── web_ui.html                    # Browser web UI
├── url_shortener.db               # SQLite database
├── ENGINEERING.md                 # This file - engineer documentation
├── ENGINEER.md                    # Additional engineer documentation
├── SYSTEM.md                      # System architecture documentation
├── AGENTS.md                      # Agent documentation
├── README.md                      # Project README
├── quick_start.txt                # Quick start guide
└── ARCHITECTURE/                  # Additional architecture docs
```

## 3. Core application layer

### Application runtime

The main app is initialized in `app/main.py`:

- FastAPI application is created with title, version, docs, and OpenAPI config
- CORS and trusted-host middleware are enabled
- RateLimitMiddleware is attached
- Routers for health, shortening, redirects, and analytics are mounted
- Root route serves the browser UI when the request accepts HTML
- Job and scenario metadata endpoints are exposed

### Key runtime modules

- `app/main.py` — application bootstrap and HTTP routes
- `app/config.py` — environment-based settings management
- `app/database.py` — SQLAlchemy engine and session factory
- `app/models.py` — `URL` and `Analytics` ORM models
- `app/crud.py` — database CRUD helper functions
- `app/schemas.py` — Pydantic request/response schemas
- `app/jobs.py` — in-memory job tracking for browser metrics
- `app/background_jobs.py` — thread-based background analytics processing

### API routers

- `app/routers/health.py` — Service health checks
- `app/routers/shorten.py` — URL shortening endpoint
- `app/routers/redirect.py` — Short code redirect logic
- `app/routers/analytics.py` — Analytics queries

### Utilities and middleware

- `app/utils/cache.py` — Redis/in-memory cache abstraction
- `app/utils/shortener.py` — Short code generation algorithms
- `app/utils/validators.py` — Input validation helpers
- `app/middleware/rate_limit.py` — Per-IP rate limiting

### Storage model

The default database is SQLite, configured in `app/config.py`:

- `sqlite:///./url_shortener.db` in normal runtime
- `sqlite://` in pytest environments

**URL Model:**
- `id` — short code (primary key)
- `original_url` — the full URL being shortened
- `created_at` — timestamp of creation
- `expires_at` — optional expiration timestamp
- `click_count` — number of redirect clicks
- `user_id` — optional user identifier
- `custom_code` — optional custom short code

**Analytics Model:**
- `short_code` — reference to shortened URL
- `clicked_at` — timestamp of click
- `referrer` — HTTP referrer
- `user_agent` — browser user agent
- `ip_address` — client IP address
- `country` — geolocation country
- `city` — geolocation city

## 4. Request flow

### Shorten URL

**Route:** `POST /shorten`

Handler in `app/routers/shorten.py`:

1. Validates the incoming URL
2. Rejects blocked domains
3. Validates a custom code if supplied
4. Ensures custom code is not already taken
5. Generates unique short code when no custom code provided
6. Stores mapping in database
7. Caches shortened mapping in Redis
8. Creates job record for UI metrics
9. Returns `ShortenResponse` with short URL and expiry

Short code generation logic in `app/utils/shortener.py` tries multiple strategies to avoid collisions.

### Redirect flow

**Route:** `GET /{short_code}`

Handler in `app/routers/redirect.py`:

1. Tries Redis cache first
2. Falls back to SQLite database on cache miss
3. Returns HTTP 404 if short code doesn't exist
4. Returns HTTP 410 if URL has expired
5. Redirects with HTTP 301 to original URL
6. Tracks analytics asynchronously in background thread

### Analytics flow

**Route:** `GET /analytics/{short_code}`

Handler in `app/routers/analytics.py`:

- Verifies short code exists
- Reads aggregate analytics using `AnalyticsCRUD.get_stats()`
- Returns total clicks and recent click metadata

### Health and metadata

- `GET /health` — checks database connectivity and Redis availability (in non-dev)
- `GET /api-info` — exposes service metadata
- `GET /jobs` — returns in-memory job list for web UI
- `GET /jobs/{job_id}` — returns specific job details
- `GET /jobs/{job_id}/logs` — returns job execution logs
- `GET /scenarios` — returns scenario catalog for browser UI

## 5. Caching and rate limiting

### Cache behavior

`app/utils/cache.py` provides a `CacheManager` with:

- Redis as primary cache (if available)
- In-memory fallback when Redis unavailable
- JSON serialization helpers for object caching
- Simple increment support for counters

Used for:
- Redirect lookups (short code → URL)
- Short URL resolution
- Rate limit counters

### Rate limiting

`app/middleware/rate_limit.py` implements per-IP throttling:

- Key format: `rate_limit:{client_ip}`
- Window size: configured by `RATE_LIMIT_WINDOW`
- Max requests: configured by `RATE_LIMIT`
- Returns HTTP 429 when limit exceeded

## 6. Orchestration engine

The repository contains a separate orchestration layer under `orchestrator/`.

### Orchestrator overview

`orchestrator/orchestrator.py` defines an `Orchestrator` class that coordinates SDLC stages:

- `ANALYZE` — Requirements and feasibility analysis
- `DESIGN` — Architecture and design phase
- `CODE` — Implementation phase
- `TEST` — Testing and validation
- `REVIEW` — Code review and quality gates
- `DEPLOY` — Deployment planning
- `DONE` — Workflow completion

Each stage is represented by `Task` objects defined in `orchestrator/models/task_models.py`.

### Agent model

The orchestrator runs different agents for each stage:

- `AnalyzerAgent` — Analyzes requirements and identifies ambiguities
- `DesignerAgent` — Creates architecture and design
- `CoderAgent` — Generates code from design
- `TesterAgent` — Creates and runs tests
- `ReviewerAgent` — Reviews code quality and security
- `DeployAgent` — Plans deployment strategy

Task state includes:
- pending/running/success/failed status
- Dependency tracking
- Generated artifacts
- Approval requirements
- Error metadata

### State management

`orchestrator/core/state_manager.py` persists orchestration state:

- Saves checkpoints at each stage
- Enables resumption after failures
- Supports rollback on rejection
- Provides audit trails
- Tracks execution metadata

### Dependency management

`orchestrator/core/dependency_graph.py` manages task dependencies:

- Tracks which tasks depend on which stages
- Ensures proper execution order
- Prevents circular dependencies
- Enables parallel execution when possible

### Scenario layer

`scenarios/` directory contains scenario runners:

- `brownfield_auth_analytics.py` — Brownfield integration scenario
- `ambiguous_optimization.py` — Handles ambiguous requirements
- `run_all_scenarios.py` — Orchestrates all scenario execution

These simulate SDLC execution while the main app serves as the actual URL shortener product.

## 7. Configuration

Environment settings defined in `app/config.py`:

- `ENVIRONMENT` — development/production
- `LOG_LEVEL` — logging verbosity
- `BASE_URL` — service base URL
- `SECRET_KEY` — session/JWT secret
- `DATABASE_URL` — database connection string
- `REDIS_URL` — Redis connection string
- `ALLOWED_ORIGINS` — CORS allowed origins
- `CACHE_TTL` — cache time-to-live seconds
- `MAX_URL_LENGTH` — maximum URL length
- `RATE_LIMIT` — requests per window
- `RATE_LIMIT_WINDOW` — rate limit window seconds

## 8. Testing

Test suite under `tests/`:

- `test_main.py` — Main app and routing tests
- `test_shorten.py` — URL shortening logic tests
- `test_redirect.py` — Redirect and caching tests
- `test_analytics.py` — Analytics endpoint tests

Run with:

```bash
pytest
```

## 9. Deployment options

### Local development

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows
source .venv/bin/activate            # Linux/Mac
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Access at `http://127.0.0.1:8000`

### Docker development

```bash
docker-compose up -d
```

### Docker production

```bash
docker build -f docker/Dockerfile.dockerfile -t url-shortener:latest .
docker run -p 8000:8000 url-shortener:latest
```

## 10. Architecture notes

The codebase is a layered monolith with two primary concerns:

1. **Real URL shortening service** for end users
2. **Agentic orchestration framework** for SDLC simulation

Key characteristics:

- Not a fully distributed microservice architecture
- SQLite is the default persistence layer
- Redis is opportunistic (optional) for caching and throttling
- Analytics processing happens asynchronously in background thread
- Browser UI and API share the same FastAPI application
- Scenario orchestration is a simulation layer, not the main product path
- Orchestration framework demonstrates multi-stage task execution with human approval gates

## 11. Development workflow

### Adding a new route

1. Create handler in `app/routers/{feature}.py`
2. Import and mount in `app/main.py`
3. Add tests in `tests/test_{feature}.py`
4. Update configuration if needed in `app/config.py`

### Adding orchestration scenarios

1. Create scenario file in `scenarios/{scenario_name}.py`
2. Implement `Scenario` class with execution logic
3. Register in `scenarios/run_all_scenarios.py`
4. Output artifacts go to `scenario_outputs/{project_name}/`

### Configuration changes

1. Add environment variable to `.env.example.txt`
2. Update settings class in `app/config.py`
3. Document in this file

## 12. Summary

The repository implements a functional FastAPI URL shortener with analytics, caching, and rate limiting, layered with an SDLC-style orchestration framework that simulates agentic AI workflows. The core product is a working URL shortener service, and the orchestration layer demonstrates multi-stage task execution with human approval gates and checkpoint management.
