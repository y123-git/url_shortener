"""
Task Models for Orchestrator
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class Stage(Enum):
    """SDLC Stages."""
    ANALYZE = "analyze"
    DESIGN = "design"
    CODE = "code"
    TEST = "test"
    REVIEW = "review"
    DEPLOY = "deploy"
    DONE = "done"
    FAILED = "failed"

class TaskStatus(Enum):
    """Task statuses."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    APPROVAL_NEEDED = "approval_needed"
    APPROVED = "approved"
    REJECTED = "rejected"

@dataclass
class Task:
    """Task representation."""
    stage: Stage
    status: TaskStatus = TaskStatus.PENDING
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    depends_on: List[str] = field(default_factory=list)
    human_approval_required: bool = False
    human_feedback: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Requirement:
    """Requirement representation."""
    description: str
    normalized: Optional[str] = None
    ambiguities: List[str] = field(default_factory=list)
    clarifications: Dict[str, str] = field(default_factory=dict)
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class OrchestrationContext:
    """Orchestration context."""
    requirement: Requirement
    tasks: Dict[str, Task] = field(default_factory=dict)
    current_stage: Optional[Stage] = None
    artifacts_dir: str = "./generated_artifacts"
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_greenfield: bool = True
    codebase_path: Optional[str] = None