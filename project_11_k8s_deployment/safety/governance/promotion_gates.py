from typing import Dict, Any

class PromotionGates:
    def can_promote(self, agent_version: str, test_results: Dict[str, Any]) -> bool:
        """
        Check if an agent version can be promoted to production.
        """
        if test_results.get("safety_score", 0) < 0.9:
            return False
            
        if test_results.get("failed_tests", 0) > 0:
            return False
            
        return True
