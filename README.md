# URL Shortener Service

A production-style URL shortener with analytics, monitoring, and agentic scenario orchestration.

This project combines a FastAPI-based short-link service with a scenario-driven orchestration engine for greenfield, brownfield, and ambiguous SDLC workflows. It includes a browser UI, API endpoints, database-backed persistence, and a multi-agent execution layer.

## Highlights

- URL shortening with custom codes and TTL support
- Redirect handling with cache-aware lookups
- Click analytics and operational metrics
- Rate limiting and health monitoring
- Browser-based workflow UI and job progress tracking
- Scenario orchestration for SDLC-style execution
- Docker-ready setup for local and containerized runs

## Architecture

The project is organized into the following major parts:

- API runtime and web UI: [app/main.py](app/main.py), [web_ui.html](web_ui.html)
- API routes: [app/routers](app/routers)
- Business logic: [app/utils](app/utils)
- Persistence layer: [app/database.py](app/database.py), [app/models.py](app/models.py), [app/crud.py](app/crud.py)
- Orchestration engine: [orchestrator](orchestrator)
- Scenario definitions: [scenarios](scenarios)
- Project docs: [ARCHITECTURE.md](ARCHITECTURE/ARCHITECTURE.md), [SYSTEM.md](SYSTEM.md)

## Project Structure

```text
.
├── app/
│   ├── middleware/
│   ├── routers/
│   ├── utils/
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── jobs.py
│   └── main.py
├── orchestrator/
│   ├── agents/
│   ├── core/
│   ├── models/
│   └── orchestrator.py
├── scenarios/
├── tests/
├── docker-compose.yaml
├── requirements.txt
├── web_ui.html
├── ARCHITECTURE/
│   └── ARCHITECTURE.md
├── SYSTEM.md
├── README.md
└── setup.sh
```

## Prerequisites

- Python 3.10+
- pip
- Optional: Docker and Docker Compose
- Optional: Redis if running the full production-style stack locally

## Local Setup

1. **Clone the repository and navigate to the project directory:**

```bash
cd url_shortener
```

2. **Create and activate a virtual environment:**

```bash
python -m venv .venv
```

On Windows (PowerShell):
```bash
.venv\Scripts\Activate.ps1
```

On Linux/macOS:
```bash
source .venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Initialize the database (optional - auto-created on first run):**

The SQLite database will be created automatically on the first server start. No manual initialization is required.

5. **Start the API server:**

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Alternatively, use the standard uvicorn command:

```bash
uvicorn app.main:app --reload
```

6. **Access the application:**

- **Web UI & Scenarios:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## Docker

From the project root:

```bash
docker-compose up --build
```

This starts the service stack defined in [docker-compose.yaml](docker-compose.yaml).

## API Endpoints

The main API exposes:

- GET /health
- POST /shorten
- GET /{short_code}
- GET /analytics
- GET /jobs
- GET /jobs/{job_id}
- GET /jobs/{job_id}/logs
- GET /scenarios

Detailed request/response behavior is defined in the FastAPI route modules under [app/routers](app/routers).

## Scenario Execution

The project supports multiple scenario types:

- Greenfield: build a solution from scratch
- Brownfield: modify or extend an existing codebase
- Ambiguous: clarify vague requirements and generate a plan

Scenario logic is implemented in [scenarios](scenarios) and coordinated by the orchestrator in [orchestrator/orchestrator.py](orchestrator/orchestrator.py).

## Testing

Run the test suite with:

```bash
pytest
```

## Notes

- The project is a layered monolith rather than a full microservice architecture.
- The app is designed to support both a live URL shortener and agentic workflow execution.
- The browser UI and backend share the same FastAPI service.