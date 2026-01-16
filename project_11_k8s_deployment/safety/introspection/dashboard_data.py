from typing import Dict, Any, List

class DashboardDataAggregator:
    def get_overview(self) -> Dict[str, Any]:
        """
        Get aggregated data for dashboard overview.
        """
        return {
            "total_requests": 100, # Placeholder: fetch from metrics
            "safety_incidents": 5,
            "average_latency": 0.5,
            "safety_score": 0.95
        }

    def get_recent_activity(self) -> List[Dict[str, Any]]:
        return [
            {"time": "10:00", "event": "Request processed", "status": "success"},
            {"time": "10:01", "event": "Safety check failed", "status": "blocked"}
        ]
