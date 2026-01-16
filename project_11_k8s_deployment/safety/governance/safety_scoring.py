from typing import Dict, Any, List

class SafetyScorer:
    def calculate_score(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate safety score based on various metrics.
        Returns a score between 0.0 (unsafe) and 1.0 (safe).
        """
        score = 1.0
        
        # Penalize for recent violations
        score -= metrics.get("violations_count", 0) * 0.1
        
        # Penalize for high uncertainty
        if metrics.get("uncertainty", 0) > 0.5:
            score -= 0.2
            
        return max(0.0, score)
