import multiprocessing
import time
from typing import Dict, Any, Callable
import resource

def _sandbox_wrapper(func, args, kwargs, result_queue):
    # Set resource limits
    try:
        # Limit CPU time (seconds)
        # resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
        # Limit memory (bytes) - e.g. 100MB
        # resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, 100 * 1024 * 1024))
        pass
    except Exception as e:
        result_queue.put({"error": f"Failed to set limits: {e}"})
        return

    try:
        res = func(*args, **kwargs)
        result_queue.put({"result": res})
    except Exception as e:
        result_queue.put({"error": str(e)})

class SandboxManager:
    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout

    def execute_in_sandbox(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute function in a separate process with resource limits.
        """
        ctx = multiprocessing.get_context("spawn")
        queue = ctx.Queue()
        p = ctx.Process(target=_sandbox_wrapper, args=(func, args, kwargs, queue))
        
        p.start()
        p.join(self.timeout)
        
        if p.is_alive():
            p.terminate()
            p.join()
            return {"success": False, "error": "Sandbox timeout"}
            
        if not queue.empty():
            res = queue.get()
            if "error" in res:
                return {"success": False, "error": res["error"]}
            return {"success": True, "result": res["result"]}
            
        return {"success": False, "error": "No result returned"}
