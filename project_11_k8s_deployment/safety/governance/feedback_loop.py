from typing import Dict, Any
from .adaptive_policy import AdaptivePolicy

class FeedbackLoop:
    def __init__(self, policy: AdaptivePolicy):
        self.policy = policy

    def process_feedback(self, incident_report: Dict[str, Any]):
        """
        Process feedback and adjust policy.
        """
        severity = incident_report.get("severity", "low")
        weight = 1 if severity == "low" else 5
        self.policy.adjust_policy(weight)
