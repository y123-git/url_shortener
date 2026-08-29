# Agent Architecture & LLM Integration Guide

## Overview

The **Agentic URL Shortener** uses a **multi-agent orchestration system** to automate SDLC workflows across six distinct stages: Analysis, Design, Coding, Testing, Review, and Deployment. Each agent is designed to handle specialized tasks, and in production, agents should integrate with Large Language Models (LLMs) to generate intelligent, context-aware outputs.

---

## LLM Recommendations

### For Production Use

**Recommended LLMs by Stage:**

| Stage | Recommended LLM | Rationale |
|-------|-----------------|-----------|
| **ANALYZE** | Claude 3.5 Sonnet or GPT-4 | Excels at requirements clarification, ambiguity detection, and scope definition. Strong reasoning capabilities. |
| **DESIGN** | Claude 3.5 Sonnet or GPT-4 | Architecture design requires deep technical reasoning and knowledge. Can generate component diagrams and API designs. |
| **CODE** | Claude 3.5 Sonnet, GPT-4, or Llama 3 (70B) | Code generation is the core strength of modern LLMs. High-quality, idiomatic code output. |
| **TEST** | GPT-4 or Claude 3.5 Sonnet | Test case generation requires understanding of edge cases, coverage analysis, and quality metrics. |
| **REVIEW** | Claude 3.5 Sonnet or GPT-4 | Code review requires nuanced analysis of security, performance, maintainability, and best practices. |
| **DEPLOY** | GPT-4 or Claude 3.5 Sonnet | Deployment requires orchestration logic, cloud API knowledge, and infrastructure understanding. |

### Current Implementation

All agents currently **simulate outputs** with hardcoded responses. Production usage requires:

1. **API Integration:** Replace simulated logic with API calls to chosen LLM
2. **Prompt Engineering:** Design stage-specific system and user prompts
3. **Context Management:** Pass orchestration context and previous stage outputs as part of prompts
4. **Error Handling:** Implement retry logic, token limit handling, and graceful degradation
5. **Cost Optimization:** Implement caching, prompt compression, and selective LLM usage

### Example Production Integration Pattern

```python
# Current (simulated)
normalized = f"Normalized: {requirement_text}"

# Production (with LLM)
response = llm_client.chat.completions.create(
    model="claude-3-5-sonnet-20241022",
    system="You are an expert requirements analyst...",
    messages=[{"role": "user", "content": requirement_text}],
    temperature=0.7
)
normalized = response.content[0].text
```

---

## Agent Architecture

### **BaseAgent** (`base_agent.py`)

**Base class for all SDLC agents.**

**Key Methods:**
- `execute()` - Abstract method; implemented by each agent to perform its stage-specific work
- `get_stage()` - Returns the SDLC stage this agent handles
- `validate_input()` - Validates inputs before execution
- `handle_error()` - Handles execution failures with logging and error tracking

**Inheritance Pattern:**
All agents (`AnalyzerAgent`, `DesignerAgent`, `CoderAgent`, etc.) inherit from `BaseAgent` and implement the abstract methods.

---

## Agent Roles & Functions

### **1. Analyzer Agent** (`analyzer_agent.py`)

**Stage:** `ANALYZE`

**Purpose:** Clarify and analyze requirements, identify ambiguities, and normalize scope.

**Current Behavior (Simulated):**
- Normalizes requirement text
- Identifies common ambiguities (traffic expectations, uptime SLAs, etc.)
- Proposes clarifications for each ambiguity
- Defines scope (in-scope vs. out-of-scope features)
- Estimates risk level and complexity
- Lists key components

**Output:**
```json
{
  "normalized_requirement": "...",
  "ambiguities": [
    {"issue": "What is the expected traffic?", "suggested": "Assume 1000 req/s"},
    {"issue": "What is the uptime requirement?", "suggested": "Assume 99.9%"}
  ],
  "scope": {
    "in_scope": ["URL shortening", "Redirect", "Analytics"],
    "out_of_scope": ["Authentication", "User management"]
  },
  "risk_level": "low",
  "complexity_estimate": 5,
  "components": ["api", "database", "cache", "analytics"]
}
```

**Production LLM Usage:**
- Use Claude/GPT-4 for reasoning-heavy ambiguity detection
- Prompt: "You are an expert software architect. Analyze this requirement and identify potential ambiguities, ask clarifying questions, and propose reasonable assumptions."

---

### **2. Designer Agent** (`designer_agent.py`)

**Stage:** `DESIGN`

**Purpose:** Design system architecture, API contracts, and data models.

**Current Behavior (Simulated):**
- Creates architecture overview (e.g., "FastAPI with PostgreSQL and Redis")
- Designs component hierarchy with responsibilities and dependencies
- Defines REST API endpoints with request/response schemas
- Specifies data entities and relationships
- Recommends technology stack

**Output:**
```json
{
  "architecture_overview": "FastAPI-based URL shortener with PostgreSQL and Redis",
  "components": [
    {"name": "API Gateway", "responsibility": "Handle HTTP requests", "dependencies": []},
    {"name": "URL Service", "responsibility": "Business logic", "dependencies": ["Database"]},
    {"name": "Cache", "responsibility": "Caching redirects", "dependencies": []}
  ],
  "api_design": {
    "endpoints": [
      {"path": "/shorten", "method": "POST", "request": {...}, "response": {...}},
      {"path": "/{code}", "method": "GET", "response": {...}}
    ]
  },
  "data_model": {
    "entities": [{"name": "URL", "fields": ["id", "original_url", "created_at", ...]}]
  },
  "tech_stack": {"backend": "FastAPI", "database": "PostgreSQL", "cache": "Redis"}
}
```

**Production LLM Usage:**
- Use Claude/GPT-4 for architectural reasoning
- Provide context from analysis stage
- Prompt: "Design the architecture for this system based on the following requirements and constraints..."

---

### **3. Coder Agent** (`coder_agent.py`)

**Stage:** `CODE`

**Purpose:** Generate production-quality code files based on design.

**Current Behavior (Simulated):**
- Generates code files (main.py, models.py, requirements.txt, etc.)
- Writes code to artifact directory
- Follows the design specification
- Creates both application code and configuration files

**Output:**
```json
{
  "files": [
    {"path": "main.py", "content": "from fastapi import FastAPI\n..."},
    {"path": "models.py", "content": "from sqlalchemy import Column\n..."},
    {"path": "requirements.txt", "content": "fastapi==0.104.1\n..."}
  ]
}
```

**Production LLM Usage:**
- Use Claude/GPT-4 or Llama 3 (70B) for code generation
- Provide design specification and prior stage outputs
- Prompt: "Generate production-quality Python code for the following components based on this design..."
- Include linting and formatting standards

---

### **4. Tester Agent** (`tester_agent.py`)

**Stage:** `TEST`

**Purpose:** Generate comprehensive test cases and validate code quality.

**Current Behavior (Simulated):**
- Generates unit tests, integration tests, and edge case tests
- Creates test files (test_main.py, test_models.py, etc.)
- Defines test metrics and coverage targets
- Simulates test execution results

**Output:**
```json
{
  "test_suites": [...],
  "coverage": 85,
  "results": {"passed": 42, "failed": 0, "skipped": 2},
  "quality_metrics": {
    "maintainability_index": 88,
    "cyclomatic_complexity": 3.2
  }
}
```

**Production LLM Usage:**
- Use GPT-4 or Claude for test case generation
- Prompt: "Generate comprehensive test cases for the following code, including unit tests, integration tests, and edge cases..."

---

### **5. Reviewer Agent** (`reviewer_agent.py`)

**Stage:** `REVIEW`

**Purpose:** Review code quality, security, and performance; provide feedback and approval.

**Current Behavior (Simulated):**
- Rates code quality (A-F scale)
- Identifies issues by severity (low, medium, high)
- Scores security, performance, and maintainability
- Provides structured feedback
- Approves or rejects based on quality gates

**Output:**
```json
{
  "rating": "A",
  "summary": "Code looks good",
  "issues": [
    {
      "severity": "low",
      "file": "main.py",
      "line": 10,
      "description": "Consider adding type hints",
      "recommendation": "Add type hints"
    }
  ],
  "security_score": 8,
  "performance_score": 9,
  "maintainability_score": 8,
  "approved": true,
  "feedback": "Good code quality. Some minor improvements suggested."
}
```

**Production LLM Usage:**
- Use Claude/GPT-4 for nuanced code analysis
- Prompt: "Review this code for security, performance, and maintainability. Identify issues, suggest improvements, and rate quality..."

---

### **6. Deploy Agent** (`deploy_agent.py`)

**Stage:** `DEPLOY`

**Purpose:** Generate deployment artifacts, infrastructure configs, and deployment automation.

**Current Behavior (Simulated):**
- Creates Dockerfile and docker-compose configurations
- Generates deployment manifests (Kubernetes, Docker Compose)
- Defines deployment steps and rollback procedures
- Specifies monitoring and observability setup
- Provides deployment validation checks

**Output:**
```json
{
  "deployment_artifacts": {
    "Dockerfile": "FROM python:3.10\n...",
    "docker-compose.yml": "version: '3'\nservices:\n..."
  },
  "deployment_strategy": "blue-green",
  "monitoring": {
    "metrics": ["latency", "error_rate", "throughput"],
    "alerts": ["high_error_rate"]
  },
  "rollback_procedure": "Stop new containers and revert to previous image"
}
```

**Production LLM Usage:**
- Use GPT-4 or Claude for infrastructure and DevOps knowledge
- Prompt: "Generate deployment configuration for this application including Dockerfile, docker-compose, and deployment strategies..."

---

## Orchestration Flow

```
START
  ↓
[ANALYZE] - Clarify requirements, identify ambiguities
  ↓ (Success)
[DESIGN] - Design architecture and API contracts (Human Approval Gate)
  ↓ (Approved)
[CODE] - Generate production code
  ↓ (Success)
[TEST] - Generate and run test suites
  ↓ (Success)
[REVIEW] - Review code quality and security (Human Approval Gate)
  ↓ (Approved)
[DEPLOY] - Generate deployment artifacts (Human Approval Gate)
  ↓ (Approved)
END - Orchestration Complete
  ↓
(Rejection at any gate → Rollback & Retry Loop)
```

---

## State Management

**StateManager** (`orchestrator/core/state_manager.py`):
- Persists orchestration context to disk/database
- Tracks task status, outputs, and artifacts
- Enables resumption after failures or interruptions

**DependencyGraph** (`orchestrator/core/dependency_graph.py`):
- Defines task dependencies
- Enforces stage ordering
- Validates completion of prerequisite stages

**GateValidator** (`orchestrator/core/validators.py`):
- Implements human approval gates at DESIGN, REVIEW, and DEPLOY stages
- Enforces quality gates and exit criteria
- Manages rollback on rejection

---

## Integration Checklist for Production

- [ ] Configure LLM API keys (Claude, GPT-4, etc.)
- [ ] Replace simulated logic with LLM API calls in each agent
- [ ] Design stage-specific prompts and system messages
- [ ] Implement error handling and retry logic
- [ ] Add token usage tracking and cost monitoring
- [ ] Test end-to-end orchestration with real LLM calls
- [ ] Implement logging and debugging for LLM interactions
- [ ] Set up fallback agents and graceful degradation
- [ ] Document prompt engineering decisions and LLM selection rationale
- [ ] Monitor LLM performance and iterate on prompts based on real-world results

---

## References

- **Orchestrator Core:** [orchestrator/orchestrator.py](orchestrator/orchestrator.py)
- **Agent Base Class:** [orchestrator/agents/base_agent.py](orchestrator/agents/base_agent.py)
- **State Management:** [orchestrator/core/state_manager.py](orchestrator/core/state_manager.py)
- **Models & Context:** [orchestrator/models/task_models.py](orchestrator/models/task_models.py)
