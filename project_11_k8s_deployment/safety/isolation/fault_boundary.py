import concurrent.futures
from typing import Callable, Any, Dict
import logging

logger = logging.getLogger(__name__)

class FaultBoundary:
    """
    Executes code within a fault isolation boundary.
    """
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    def execute_safe(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute function in a separate thread/process to isolate faults.
        """
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                result = future.result(timeout=self.timeout)
                return {"success": True, "result": result}
        except concurrent.futures.TimeoutError:
            logger.error(f"Execution timed out after {self.timeout}s")
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            logger.error(f"Execution failed: {str(e)}")
            return {"success": False, "error": str(e)}
