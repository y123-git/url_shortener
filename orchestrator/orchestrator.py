"""
Main Orchestrator
"""

from typing import Optional
import logging
from datetime import datetime

from orchestrator.models.task_models import (
    OrchestrationContext, Task, TaskStatus, Stage, Requirement
)
from orchestrator.agents import (
    AnalyzerAgent, DesignerAgent, CoderAgent, 
    TesterAgent, ReviewerAgent, DeployAgent
)
from orchestrator.core.state_manager import StateManager
from orchestrator.core.dependency_graph import DependencyGraph
from orchestrator.core.validators import GateValidator

logger = logging.getLogger(__name__)

class Orchestrator:
    """Main orchestrator that coordinates SDLC execution."""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.gate_validator = GateValidator()
        self.dependency_graph = DependencyGraph()
        
        # Initialize agents
        self.agents = {
            Stage.ANALYZE: AnalyzerAgent(),
            Stage.DESIGN: DesignerAgent(),
            Stage.CODE: CoderAgent(),
            Stage.TEST: TesterAgent(),
            Stage.REVIEW: ReviewerAgent(),
            Stage.DEPLOY: DeployAgent(),
        }
        
        self.context: Optional[OrchestrationContext] = None
    
    def orchestrate(self, requirement: str, is_greenfield: bool = True,
                   codebase_path: Optional[str] = None) -> OrchestrationContext:
        """Main orchestration entry point."""
        
        logger.info(f"Starting orchestration for: {requirement[:50]}...")
        
        # Initialize context
        self.context = OrchestrationContext(
            requirement=Requirement(description=requirement),
            is_greenfield=is_greenfield,
            codebase_path=codebase_path
        )
        
        # Create initial tasks
        self.context.tasks = self._create_tasks()
        
        # Run orchestration loop
        while not self._is_complete():
            next_task = self._get_next_task()
            if not next_task:
                break
            
            self._execute_task(next_task)
        
        # Finalize
        self.context.current_stage = Stage.DONE
        self.state_manager.save_state(self.context)
        
        logger.info("Orchestration complete!")
        return self.context
    
    def _create_tasks(self) -> dict:
        """Create initial tasks."""
        tasks = {}
        
        for stage in [Stage.ANALYZE, Stage.DESIGN, Stage.CODE, 
                      Stage.TEST, Stage.REVIEW, Stage.DEPLOY]:
            task = Task(
                stage=stage,
                input_data={
                    "requirement": self.context.requirement.description,
                    "is_greenfield": self.context.is_greenfield
                },
                human_approval_required=stage in [Stage.DESIGN, Stage.REVIEW, Stage.DEPLOY]
            )
            tasks[task.id] = task
        
        return tasks
    
    def _get_next_task(self) -> Optional[Task]:
        """Get the next task to execute."""
        for task in self.context.tasks.values():
            if task.status == TaskStatus.PENDING:
                # Check dependencies
                deps = self.dependency_graph.get_dependencies(task.stage)
                deps_complete = all(
                    any(t.stage == dep and t.status in [TaskStatus.SUCCESS, TaskStatus.APPROVED]
                        for t in self.context.tasks.values())
                    for dep in deps
                )
                
                if deps_complete and self.gate_validator.validate_entry(self.context, task.stage):
                    task.status = TaskStatus.RUNNING
                    task.started_at = datetime.utcnow()
                    return task
        
        return None
    
    def _execute_task(self, task: Task):
        """Execute a task."""
        logger.info(f"Executing task: {task.stage.value}")
        
        agent = self.agents.get(task.stage)
        if not agent:
            task.status = TaskStatus.FAILED
            task.errors.append(f"No agent found for stage {task.stage.value}")
            return
        
        try:
            task = agent.execute(self.context, task)
            
            # Validate exit gate
            if not self.gate_validator.validate_exit(self.context, task.stage, task):
                task.status = TaskStatus.FAILED
                task.errors.append("Exit gate validation failed")
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            task = agent.handle_error(self.context, task, e)
        
        task.completed_at = datetime.utcnow()
        self.context.tasks[task.id] = task
    
    def _is_complete(self) -> bool:
        """Check if orchestration is complete."""
        # All tasks done or failed
        all_done = all(
            t.status in [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.APPROVED]
            for t in self.context.tasks.values()
        )
        
        if all_done:
            # Check if any failed
            has_failed = any(t.status == TaskStatus.FAILED for t in self.context.tasks.values())
            if not has_failed:
                self.context.current_stage = Stage.DONE
                return True
        
        return False