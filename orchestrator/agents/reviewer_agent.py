"""
Reviewer Agent
"""

from orchestrator.models.task_models import Task, OrchestrationContext, Stage, TaskStatus
from orchestrator.agents.base_agent import BaseAgent

class ReviewerAgent(BaseAgent):
    """Reviews code for quality and security."""
    
    def get_stage(self) -> Stage:
        return Stage.REVIEW
    
    def execute(self, context: OrchestrationContext, task: Task) -> Task:
        self.logger.info("Reviewing code...")
        
        # Check previous stages
        for t in context.tasks.values():
            if t.stage in [Stage.CODE, Stage.TEST] and t.status != TaskStatus.SUCCESS:
                task.status = TaskStatus.FAILED
                task.errors.append(f"Previous stage {t.stage.value} failed")
                return task
        
        # Simulate review
        response = {
            "rating": "A",
            "summary": "Code looks good",
            "issues": [
                {"severity": "low", "file": "main.py", "line": 10, 
                 "description": "Consider adding type hints", 
                 "recommendation": "Add type hints"}
            ],
            "security_score": 8,
            "performance_score": 9,
            "maintainability_score": 8,
            "approved": True,
            "feedback": "Good code quality. Some minor improvements suggested."
        }
        
        task.output_data = response
        task.status = TaskStatus.APPROVED
        task.artifacts.append("review_report.md")
        
        return task