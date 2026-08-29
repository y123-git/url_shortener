"""
Coder Agent
"""

import json
import os
from orchestrator.models.task_models import Task, OrchestrationContext, Stage, TaskStatus
from orchestrator.agents.base_agent import BaseAgent

class CoderAgent(BaseAgent):
    """Generates production-quality code."""
    
    def get_stage(self) -> Stage:
        return Stage.CODE
    
    def execute(self, context: OrchestrationContext, task: Task) -> Task:
        self.logger.info("Generating code...")
        
        # Find design output
        design = None
        for t in context.tasks.values():
            if t.stage == Stage.DESIGN and t.status == TaskStatus.SUCCESS:
                design = t.output_data
                break
        
        if not design:
            task.status = TaskStatus.FAILED
            task.errors.append("No design output found")
            return task
        
        # Simulate code generation
        code_files = {
            "main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef root():\n    return {'message': 'Hello World'}",
            "models.py": "from sqlalchemy import Column, String\nfrom database import Base\n\nclass URL(Base):\n    __tablename__ = 'urls'\n    id = Column(String, primary_key=True)",
            "requirements.txt": "fastapi==0.104.1\nuvicorn==0.24.0\nsqlalchemy==2.0.23"
        }
        
        task.output_data = {"files": [{"path": k, "content": v} for k, v in code_files.items()]}
        task.status = TaskStatus.SUCCESS
        
        # Save code artifacts
        os.makedirs(f"{context.artifacts_dir}/code", exist_ok=True)
        for path, content in code_files.items():
            filepath = f"{context.artifacts_dir}/code/{path}"
            with open(filepath, "w") as f:
                f.write(content)
            task.artifacts.append(f"code/{path}")
        
        return task