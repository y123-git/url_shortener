"""
Analyzer Agent
"""

import json
from orchestrator.models.task_models import Task, OrchestrationContext, Stage, TaskStatus, Requirement
from orchestrator.agents.base_agent import BaseAgent

class AnalyzerAgent(BaseAgent):
    """Analyzes requirements, identifies ambiguities, normalizes scope."""
    
    def get_stage(self) -> Stage:
        return Stage.ANALYZE
    
    def execute(self, context: OrchestrationContext, task: Task) -> Task:
        self.logger.info("Analyzing requirements...")
        
        requirement_text = task.input_data.get("requirement", "")
        
        # Simulate analysis (in production, use LLM)
        normalized = f"Normalized: {requirement_text}"
        ambiguities = [
            {"issue": "What is the expected traffic?", "suggested": "Assume 1000 req/s"},
            {"issue": "What is the uptime requirement?", "suggested": "Assume 99.9%"}
        ]
        
        # Update task output
        task.output_data = {
            "normalized_requirement": normalized,
            "ambiguities": ambiguities,
            "scope": {
                "in_scope": ["URL shortening", "Redirect", "Analytics"],
                "out_of_scope": ["Authentication", "User management"]
            },
            "risk_level": "low",
            "complexity_estimate": 5,
            "components": ["api", "database", "cache", "analytics"]
        }
        
        # Create normalized requirement
        context.requirement.normalized = normalized
        context.requirement.ambiguities = [a["issue"] for a in ambiguities]
        context.requirement.clarifications = {
            a["issue"]: a["suggested"] for a in ambiguities
        }
        
        task.status = TaskStatus.SUCCESS
        task.artifacts.append("analysis.json")
        
        return task