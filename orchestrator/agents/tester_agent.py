"""
Tester Agent
"""

import json
import os
from orchestrator.models.task_models import Task, OrchestrationContext, Stage, TaskStatus
from orchestrator.agents.base_agent import BaseAgent

class TesterAgent(BaseAgent):
    """Generates tests."""
    
    def get_stage(self) -> Stage:
        return Stage.TEST
    
    def execute(self, context: OrchestrationContext, task: Task) -> Task:
        self.logger.info("Generating tests...")
        
        # Find code output
        code = None
        for t in context.tasks.values():
            if t.stage == Stage.CODE and t.status == TaskStatus.SUCCESS:
                code = t.output_data
                break
        
        if not code:
            task.status = TaskStatus.FAILED
            task.errors.append("No code output found")
            return task
        
        # Simulate test generation
        test_files = {
            "test_main.py": "import pytest\nfrom fastapi.testclient import TestClient\nfrom main import app\n\ndef test_root():\n    client = TestClient(app)\n    response = client.get('/')\n    assert response.status_code == 200"
        }
        
        task.output_data = {
            "files": [{"path": k, "content": v} for k, v in test_files.items()],
            "test_results": {
                "total": 10,
                "passing": 9,
                "failing": 1,
                "coverage": 0.85
            }
        }
        
        # Save tests
        os.makedirs(f"{context.artifacts_dir}/tests", exist_ok=True)
        for path, content in test_files.items():
            filepath = f"{context.artifacts_dir}/tests/{path}"
            with open(filepath, "w") as f:
                f.write(content)
            task.artifacts.append(f"tests/{path}")
        
        task.status = TaskStatus.SUCCESS
        return task