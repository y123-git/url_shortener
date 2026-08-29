"""
Dependency Graph for Task Sequencing
"""

from typing import List, Dict, Set
from orchestrator.models.task_models import Stage

class DependencyGraph:
    """Manages task dependencies."""
    
    def __init__(self):
        self._dependencies = {
            Stage.ANALYZE: [],
            Stage.DESIGN: [Stage.ANALYZE],
            Stage.CODE: [Stage.DESIGN],
            Stage.TEST: [Stage.CODE],
            Stage.REVIEW: [Stage.TEST],
            Stage.DEPLOY: [Stage.REVIEW],
        }
    
    def get_dependencies(self, stage: Stage) -> List[Stage]:
        """Get dependencies for a stage."""
        return self._dependencies.get(stage, [])
    
    def get_all_dependencies(self, stage: Stage) -> Set[Stage]:
        """Get all transitive dependencies."""
        deps = set()
        direct = self.get_dependencies(stage)
        
        for dep in direct:
            deps.add(dep)
            deps.update(self.get_all_dependencies(dep))
        
        return deps
    
    def get_execution_order(self) -> List[Stage]:
        """Get topological execution order."""
        return [stage for stage in Stage if stage not in [Stage.DONE, Stage.FAILED]]