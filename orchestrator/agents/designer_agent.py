"""
Designer Agent
"""

import json
from orchestrator.models.task_models import Task, OrchestrationContext, Stage, TaskStatus
from orchestrator.agents.base_agent import BaseAgent

class DesignerAgent(BaseAgent):
    """Designs architecture, APIs, data models."""
    
    def get_stage(self) -> Stage:
        return Stage.DESIGN
    
    def execute(self, context: OrchestrationContext, task: Task) -> Task:
        self.logger.info("Designing system architecture...")
        
        # Get analysis output
        analysis = None
        for t in context.tasks.values():
            if t.stage == Stage.ANALYZE and t.status == TaskStatus.SUCCESS:
                analysis = t.output_data
                break
        
        if not analysis:
            task.status = TaskStatus.FAILED
            task.errors.append("No analysis output found")
            return task
        
        # Simulate design (in production, use LLM)
        response = {
            "architecture_overview": "FastAPI-based URL shortener with PostgreSQL and Redis",
            "components": [
                {"name": "API Gateway", "responsibility": "Handle HTTP requests", "dependencies": []},
                {"name": "URL Service", "responsibility": "Business logic", "dependencies": ["Database"]},
                {"name": "Cache", "responsibility": "Caching redirects", "dependencies": []}
            ],
            "api_design": {
                "endpoints": [
                    {"path": "/shorten", "method": "POST", "request": {"url": "string"}, "response": {"short_code": "string"}},
                    {"path": "/{code}", "method": "GET", "response": {"redirect": "string"}}
                ]
            },
            "data_model": {
                "entities": [
                    {"name": "URL", "fields": ["id", "original_url", "created_at", "expires_at", "click_count"]}
                ]
            },
            "tech_stack": {
                "backend": "FastAPI",
                "database": "PostgreSQL",
                "cache": "Redis"
            },
            "key_decisions": [
                {"decision": "Use FastAPI", "rationale": "Fast and modern", "alternatives": ["Django", "Flask"]}
            ]
        }
        
        task.output_data = response
        task.status = TaskStatus.APPROVAL_NEEDED
        task.human_approval_required = True
        task.artifacts.append("design.json")
        
        return task