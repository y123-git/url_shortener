"""
Deploy Agent
"""

import json
import os
from orchestrator.models.task_models import Task, OrchestrationContext, Stage, TaskStatus
from orchestrator.agents.base_agent import BaseAgent

class DeployAgent(BaseAgent):
    """Prepares deployment artifacts."""
    
    def get_stage(self) -> Stage:
        return Stage.DEPLOY
    
    def execute(self, context: OrchestrationContext, task: Task) -> Task:
        self.logger.info("Preparing deployment...")
        
        # Check all previous stages
        for t in context.tasks.values():
            if t.stage not in [Stage.DEPLOY, Stage.DONE] and t.status != TaskStatus.SUCCESS:
                task.status = TaskStatus.FAILED
                task.errors.append(f"Previous stage {t.stage.value} failed")
                return task
        
        # Simulate deployment artifacts
        deploy_files = {
            "Dockerfile": "FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD ['uvicorn', 'main:app', '--host', '0.0.0.0']",
            "docker-compose.yml": "version: '3.8'\nservices:\n  app:\n    build: .\n    ports:\n      - '8000:8000'",
            "README.md": "# URL Shortener\n\nA production-grade URL shortener service."
        }
        
        task.output_data = {"files": [{"path": k, "content": v} for k, v in deploy_files.items()]}
        
        # Save deployment artifacts
        os.makedirs(f"{context.artifacts_dir}/deploy", exist_ok=True)
        for path, content in deploy_files.items():
            filepath = f"{context.artifacts_dir}/deploy/{path}"
            with open(filepath, "w") as f:
                f.write(content)
            task.artifacts.append(f"deploy/{path}")
        
        task.status = TaskStatus.APPROVAL_NEEDED
        task.human_approval_required = True
        
        return task