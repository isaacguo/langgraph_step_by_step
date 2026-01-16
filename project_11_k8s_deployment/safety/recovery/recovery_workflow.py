from typing import Dict, Any, List
from .rollback_engine import RollbackEngine

class RecoveryWorkflow:
    def __init__(self, rollback_engine: RollbackEngine):
        self.rollback_engine = rollback_engine

    def execute_recovery(self, thread_id: str, error_type: str) -> Dict[str, Any]:
        """
        Execute recovery strategy based on error type.
        """
        if error_type == "safety_violation":
            # Strategy: Rollback to last safe state
            safe_state = self.rollback_engine.get_safe_checkpoint(thread_id)
            if safe_state:
                return {
                    "status": "recovered",
                    "action": "rollback",
                    "target_config": safe_state["config"],
                    "message": "Rolled back to last safe state"
                }
            else:
                return {
                    "status": "failed",
                    "message": "No safe state found"
                }
                
        elif error_type == "transient_error":
            # Strategy: Retry (just return current state with retry flag)
            return {
                "status": "retry",
                "message": "Suggest retry"
            }
            
        return {"status": "unknown_error"}
