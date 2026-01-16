from typing import Dict, Any
from .logger import logger

class TelemetryCollector:
    def __init__(self):
        self.log = logger.bind(component="telemetry")

    def collect(self, event_type: str, data: Dict[str, Any]):
        """
        Collect telemetry data using structured logging.
        """
        self.log.info(event_type, **data)
