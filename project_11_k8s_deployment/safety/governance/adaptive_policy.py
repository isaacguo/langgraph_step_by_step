from typing import Dict, Any, List

class AdaptivePolicy:
    def __init__(self):
        self.strictness_level = 1.0 # 1.0 = Normal, >1.0 = Strict, <1.0 = Relaxed

    def adjust_policy(self, recent_incidents: int):
        """
        Adjust policy strictness based on recent incidents.
        """
        if recent_incidents > 5:
            self.strictness_level = 1.5
        elif recent_incidents == 0:
            self.strictness_level = max(0.8, self.strictness_level - 0.1)

    def get_threshold_multiplier(self) -> float:
        return self.strictness_level
