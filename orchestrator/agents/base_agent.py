"""
Base Agent Class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from orchestrator.models.task_models import Task, OrchestrationContext, Stage, TaskStatus
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all SDLC agents."""
    
    def __init__(self):
        self.logger = logger
    
    @abstractmethod
    def execute(self, context: OrchestrationContext, task: Task) -> Task:
        """Execute the agent's specific task."""
        pass
    
    @abstractmethod
    def get_stage(self) -> Stage:
        """Return the stage this agent handles."""
        pass
    
    def validate_input(self, context: OrchestrationContext, task: Task) -> bool:
        """Validate input before execution."""
        return True
    
    def handle_error(self, context: OrchestrationContext, task: Task, error: Exception) -> Task:
        """Handle execution errors."""
        task.status = TaskStatus.FAILED
        task.errors.append(str(error))
        self.logger.error(f"Agent {self.get_stage().value} failed: {error}")
        return task