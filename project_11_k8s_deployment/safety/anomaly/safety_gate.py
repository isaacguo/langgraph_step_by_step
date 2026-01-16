from typing import Dict, Any, List
from app.config import settings

class SafetyGate:
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold

    def evaluate(self, safety_score: float, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate if the operation should pass the safety gate.
        """
        passed = safety_score >= self.threshold
        
        # Override based on context
        if context.get("emergency_mode", False):
            # Lower threshold in emergency? Or Higher?
            # Let's say we require strictly higher in emergency unless authorized override
            pass
            
        return {
            "passed": passed,
            "score": safety_score,
            "threshold": self.threshold,
            "decision": "proceed" if passed else "block"
        }
