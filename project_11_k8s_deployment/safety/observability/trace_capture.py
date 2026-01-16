from typing import Dict, Any, List
import uuid
import time
from .logger import logger

class TraceCapture:
    def __init__(self):
        self.traces = {}

    def start_trace(self, trace_id: str = None) -> str:
        if not trace_id:
            trace_id = str(uuid.uuid4())
        
        self.traces[trace_id] = {
            "start_time": time.time(),
            "spans": []
        }
        return trace_id

    def add_span(self, trace_id: str, span_name: str, inputs: Dict[str, Any], outputs: Dict[str, Any]):
        if trace_id not in self.traces:
            return
        
        span = {
            "name": span_name,
            "timestamp": time.time(),
            "inputs": inputs,
            "outputs": outputs
        }
        self.traces[trace_id]["spans"].append(span)
        logger.info("Trace span added", trace_id=trace_id, span=span_name)

    def end_trace(self, trace_id: str) -> Dict[str, Any]:
        if trace_id not in self.traces:
            return {}
        
        trace = self.traces.pop(trace_id)
        trace["duration"] = time.time() - trace["start_time"]
        return trace
