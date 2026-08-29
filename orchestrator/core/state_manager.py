"""
State Manager for Orchestrator
"""

import json
import os
from typing import Optional
from datetime import datetime
from orchestrator.models.task_models import OrchestrationContext, Task, TaskStatus

class StateManager:
    """Manages orchestrator state."""
    
    def __init__(self, storage_dir: str = "./orchestrator_state"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save_state(self, context: OrchestrationContext) -> str:
        """Save orchestrator state."""
        state_file = f"{self.storage_dir}/state_{datetime.utcnow().timestamp()}.json"
        
        # Convert to serializable dict
        state = {
            "requirement": {
                "id": context.requirement.id,
                "description": context.requirement.description,
                "normalized": context.requirement.normalized,
                "ambiguities": context.requirement.ambiguities,
                "priority": context.requirement.priority,
                "acceptance_criteria": context.requirement.acceptance_criteria,
            },
            "tasks": {
                task_id: {
                    "stage": task.stage.value,
                    "status": task.status.value,
                    "output_data": task.output_data,
                    "artifacts": task.artifacts,
                    "errors": task.errors,
                }
                for task_id, task in context.tasks.items()
            },
            "current_stage": context.current_stage.value if context.current_stage else None,
            "is_greenfield": context.is_greenfield,
            "metadata": context.metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2, default=str)
        
        return state_file
    
    def load_state(self, state_file: str) -> Optional[OrchestrationContext]:
        """Load orchestrator state."""
        # Implementation for loading state
        pass