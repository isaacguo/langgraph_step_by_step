import traceback
from typing import Dict, Any, Type
import logging

logger = logging.getLogger(__name__)

class ErrorContainment:
    def __init__(self):
        self.critical_errors = [MemoryError, SystemError, SyntaxError]

    def contain(self, error: Exception, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Analyze and contain the error.
        """
        error_type = type(error).__name__
        trace = traceback.format_exc()
        
        logger.error(f"Containing error {error_type}: {str(error)}")
        
        is_critical = any(isinstance(error, t) for t in self.critical_errors)
        
        return {
            "contained": True,
            "error_type": error_type,
            "message": str(error),
            "is_critical": is_critical,
            "recovery_strategy": "restart_process" if is_critical else "retry_operation",
            "context_snapshot": context
        }
