"""
Gate Validators for Orchestrator
"""

from typing import Dict, List
from orchestrator.models.task_models import OrchestrationContext, Task, TaskStatus, Stage

class GateValidator:
    """Validates entry/exit gates for each stage."""
    
    def validate_entry(self, context: OrchestrationContext, stage: Stage) -> bool:
        """Validate entry gate for a stage."""
        # Check all dependencies are complete
        if stage == Stage.ANALYZE:
            return context.requirement.description is not None
        
        elif stage == Stage.DESIGN:
            # Analysis must be complete
            analyze_tasks = [t for t in context.tasks.values() if t.stage == Stage.ANALYZE]
            return all(t.status == TaskStatus.SUCCESS for t in analyze_tasks)
        
        elif stage == Stage.CODE:
            # Design must be approved
            design_tasks = [t for t in context.tasks.values() if t.stage == Stage.DESIGN]
            return all(t.status in [TaskStatus.SUCCESS, TaskStatus.APPROVED] for t in design_tasks)
        
        elif stage == Stage.TEST:
            # Code must be complete
            code_tasks = [t for t in context.tasks.values() if t.stage == Stage.CODE]
            return all(t.status == TaskStatus.SUCCESS for t in code_tasks)
        
        elif stage == Stage.REVIEW:
            # Tests must pass
            test_tasks = [t for t in context.tasks.values() if t.stage == Stage.TEST]
            return all(t.status == TaskStatus.SUCCESS for t in test_tasks)
        
        elif stage == Stage.DEPLOY:
            # Review must be approved
            review_tasks = [t for t in context.tasks.values() if t.stage == Stage.REVIEW]
            return all(t.status in [TaskStatus.SUCCESS, TaskStatus.APPROVED] for t in review_tasks)
        
        return True
    
    def validate_exit(self, context: OrchestrationContext, stage: Stage, task: Task) -> bool:
        """Validate exit gate for a stage."""
        if task.status == TaskStatus.FAILED:
            return False
        
        if stage == Stage.ANALYZE:
            # Must have normalized requirement
            return context.requirement.normalized is not None
        
        elif stage == Stage.DESIGN:
            # Must have design artifacts
            return len(task.artifacts) > 0
        
        elif stage == Stage.CODE:
            # Must have code artifacts
            return len(task.artifacts) > 0
        
        elif stage == Stage.TEST:
            # Tests must pass (simulated)
            test_results = task.output_data.get("test_results", {})
            pass_rate = test_results.get("passing", 0) / max(test_results.get("total", 1), 1)
            return pass_rate >= 0.8  # 80% pass rate
        
        elif stage == Stage.REVIEW:
            # Review must be approved
            return task.status == TaskStatus.APPROVED
        
        elif stage == Stage.DEPLOY:
            # Deployment artifacts ready
            return len(task.artifacts) > 0
        
        return True