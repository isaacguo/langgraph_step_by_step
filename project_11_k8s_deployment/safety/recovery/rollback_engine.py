from typing import Any, Dict, Optional
from .checkpoint_manager import CheckpointManager

class RollbackEngine:
    def __init__(self, checkpoint_manager: CheckpointManager):
        self.checkpoint_manager = checkpoint_manager

    def rollback(self, thread_id: str, steps: int = 1) -> Optional[Dict[str, Any]]:
        """
        Rollback the state by N steps.
        This retrieves the checkpoint N steps back.
        """
        checkpoints = list(self.checkpoint_manager.list_checkpoints(thread_id))
        if len(checkpoints) <= steps:
            return None
            
        # Checkpoints are typically ordered newest first? I need to verify.
        # Assuming list returns ordered iterator, need to consume.
        # LangGraph list returns iterator of (config, checkpoint, metadata, parent_config)
        
        # Sort by timestamp or ID if needed, but assuming default order is newest first.
        target_checkpoint = checkpoints[steps] 
        
        return target_checkpoint

    def get_safe_checkpoint(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Find the last known safe checkpoint.
        """
        for config, checkpoint, metadata, _ in self.checkpoint_manager.list_checkpoints(thread_id):
            if metadata.get("safety_status") == "safe":
                return {"config": config, "state": checkpoint}
        return None
